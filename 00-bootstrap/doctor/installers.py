#!/usr/bin/env python3
"""installers.py — explicit, human-run installers with uninstall paths (H24).

  installers.py install NAME[=ARG] [--sha SHA] [--surface S] [--probe]
  installers.py uninstall NAME[=ARG] [--surface S] [--probe]
  installers.py --self-test

`workspace-doctor.sh --install-<name>[=ARG]` / `--uninstall-<name>[=ARG]` exec this with
inherited stdio; the shell reads only the exit code. The unattended doctor never installs.

Names: pin, shims, git-hooks (H18: the global git lanes include from dist/git/lanes plus one
managed include block in ~/.gitconfig), identity, claude-overlay, sandbox-roots, plugin,
projects-pointer (~/Projects/AGENTS.md from dist/projects-AGENTS.md), launchd.
The Codex beacon (~/.codex/AGENTS.md) is a whole-file output of `shims=codex`.

Common contract (every name, both actions):
  1. refuse (exit 4, `installer refused: <reasons>`) unless fds 0 and 1 are TTYs and the
     agent verdict is human+determined. Undetermined, an ImportError of profile_resolve
     or any agent-possible env is a refusal. On the real home the real verdict is always
     consulted and an injected verdict can only tighten (pin_lib's real-home guard).
  2. print a unified diff per target; 3. prompt `Apply? [y/N]`;
  4. back up each existing target to `<target>.ws-bak.<UTC>`;
  5. write atomically and append control/install-log.jsonl;
  6. uninstall restores the backup named by the most recent install-log entry for each
     target byte-for-byte, or removes a file the installer created.

Exit codes: 0 applied · 1 declined or failed · 2 usage · 3 nothing to do / source absent ·
4 refused (precondition, agent, no TTY, foreign edits).

API: run(name, action, *, home, repo, agent_check=None, isatty=None, confirm=None,
now=None, which=None, **seams) -> int. The extra keyword seams (sha, surface, probe,
render_list, app_exists) are optional and default to the CLI behaviour.
"""
from __future__ import annotations

import datetime as dt
import difflib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
VAULT_ROOT = HERE.parents[1]
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import merge_settings  # noqa: E402 — sibling module, same directory
import pin_lib  # noqa: E402

NAMES = ("pin", "shims", "git-hooks", "identity", "claude-overlay", "sandbox-roots",
         "plugin", "projects-pointer", "launchd")
ACTIONS = ("install", "uninstall")
# Cursor scripts retired in wave 0 (T1 archives the dist copies). Installed copies are
# removed, with a backup, by `--uninstall-shims=cursor`.
RETIRED_CURSOR_SCRIPTS = ("cursor-prompt-route.sh", "cursor-reassert.sh",
                          "cursor-sessionend.sh", "cursor-subagent-stop.sh")
LAUNCHD_LABEL = "design.snds.workspace-doctor"
OVERLAY_OUTPUT_ID = "claude-user-fragment"
# The overlay goes into the file this surfaces.json layer installs. Every non-Claude host in
# its loaded_by list that is installed here needs a clean probe record first.
OVERLAY_LAYER_ID = "claude-user"
CLAUDE_FAMILY = "claude"
SURFACE_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
PROBES_DIR = "02-shared-references/probes"
HOOK_SCRIPT_RE = re.compile(r"(?:\$HOME|~)/\.claude/hooks/([A-Za-z0-9._-]+\.sh)")
RENDER_TIMEOUT = 30


class InstallerError(Exception):
    """Aborted without writing (exit 1)."""


class MissingSource(Exception):
    """Nothing to install: the source is absent in this wave (exit 3)."""


RefusedError = pin_lib.RefusedError


# --------------------------------------------------------------------------- context

class Ctx:
    def __init__(self, name, arg, action, *, home, repo, agent_check, confirm, now, which,
                 sha, surface, probe, render_list, app_exists):
        self.name, self.arg, self.action = name, arg, action
        self.home, self.repo = Path(home), Path(repo)
        self.agent_check = agent_check
        self.confirm = confirm or _default_confirm
        self.now = now
        self.which = which or shutil.which
        self.sha = sha
        self.surface = surface
        self.probe = bool(probe)
        self.render_list = render_list
        self.app_exists = app_exists or (lambda p: Path(p).exists())
        self.real = pin_lib.is_real_home(self.home)

    def utc(self) -> dt.datetime:
        n = self.now() if callable(self.now) else self.now
        return n or dt.datetime.now(dt.timezone.utc)

    def stamp(self) -> str:
        return self.utc().strftime("%Y%m%dT%H%M%SZ")

    def ts(self) -> str:
        return self.utc().strftime("%Y-%m-%dT%H:%M:%SZ")

    def paths(self) -> dict:
        return pin_lib.ws_paths(self.home)

    def pr(self):
        return pin_lib._PR_LOADER()

    def label(self) -> str:
        arg = self.arg or (self.sha if self.name == "pin" else None) or (
            self.surface if self.name == "shims" else None)
        lab = f"--install-{self.name}" + (f"={arg}" if arg else "")
        return lab + (" --probe" if self.probe else "")

    def expand(self, p: str):
        """install_path → absolute path under `home`; None for repo-relative (tracked)."""
        if not p:
            return None
        for pre in ("~/", "$HOME/", "${HOME}/"):
            if p.startswith(pre):
                return self.home / p[len(pre):]
        return Path(p) if os.path.isabs(p) else None


def _default_confirm(prompt: str) -> str:
    try:
        return input(prompt)
    except EOFError:
        return ""


def _real_isatty() -> dict:
    return {"stdin": os.isatty(0), "stdout": os.isatty(1)}


# --------------------------------------------------------------------------- preflight

def preflight(home, *, agent_check=None, isatty=None) -> list:
    """Every refusal reason for an installer run (empty = allowed)."""
    reasons = []
    real = pin_lib.is_real_home(home)
    tty = dict(isatty) if isinstance(isatty, dict) else _real_isatty()
    if real:
        rt = _real_isatty()
        tty = {k: bool(tty.get(k)) and rt[k] for k in ("stdin", "stdout")}
    for fd in ("stdin", "stdout"):
        if not tty.get(fd):
            reasons.append(f"no TTY on {fd}")
    try:
        pr = pin_lib._PR_LOADER()
    except Exception as e:  # noqa: BLE001 — ImportError or any error refuses
        pr = None
        reasons.append(f"profile_resolve unavailable ({type(e).__name__})")
    if real or agent_check is None:
        if pr is not None:
            try:
                reasons += pin_lib.verdict_reasons(pr.agent_check(), "real")
            except Exception as e:  # noqa: BLE001
                reasons.append(f"real verdict error ({type(e).__name__})")
    if agent_check is not None:
        try:
            reasons += pin_lib.verdict_reasons(pin_lib._call_verdict(agent_check), "injected")
        except Exception as e:  # noqa: BLE001
            reasons.append(f"injected verdict error ({type(e).__name__})")
    out = []
    for r in reasons:
        if r not in out:
            out.append(r)
    return out


# --------------------------------------------------------------------------- state + diff

def _state(path: Path):
    if os.path.islink(path):
        return ("link", os.readlink(path))
    if path.is_file():
        return ("file", path.read_bytes(), path.stat().st_mode & 0o777)
    return None


def _state_sha(st):
    if st is None:
        return None
    if st[0] == "link":
        return pin_lib.sha256_bytes(("link:" + st[1]).encode("utf-8"))
    return pin_lib.sha256_bytes(st[1])


def _same(a, b) -> bool:
    if a is None or b is None:
        return a is b
    if a[0] != b[0]:
        return False
    if a[0] == "link":
        return a[1] == b[1]
    return a[1] == b[1] and a[2] == b[2]


def _text(st):
    if st is None:
        return []
    if st[0] == "link":
        return [f"-> {st[1]}\n"]
    try:
        return st[1].decode("utf-8").splitlines(True)
    except UnicodeDecodeError:
        return None


def _print_diff(path: Path, old, new) -> None:
    a, b = _text(old), _text(new)
    if a is None or b is None:
        print(f"--- {path}\n+++ {path}\n(binary content differs)")
        return
    lines = list(difflib.unified_diff(a, b, fromfile=str(path) if old else "/dev/null",
                                      tofile=str(path) if new else "/dev/null"))
    if old and new and old[0] == "file" and new[0] == "file" and old[1] == new[1]:
        lines = [f"--- {path}\n", f"+++ {path}\n", f"mode {oct(old[2])} -> {oct(new[2])}\n"]
    sys.stdout.write("".join(lines) if lines else f"(no textual change: {path})\n")
    if lines and not lines[-1].endswith("\n"):
        sys.stdout.write("\n")


def _write_state(path: Path, st) -> None:
    if st is None:
        pin_lib.fs("remove", path)
        return
    pin_lib.fs("mkdir", path.parent, 0o755)
    if st[0] == "link":
        pin_lib.fs("symlink", path, st[1])
    else:
        pin_lib.fs("write", path, st[1], st[2])


def _backup(ctx: Ctx, path: Path, st):
    if st is None:
        return None
    bak = Path(f"{path}.ws-bak.{ctx.stamp()}")
    n = 1
    while os.path.lexists(bak):
        bak = Path(f"{path}.ws-bak.{ctx.stamp()}.{n}")
        n += 1
    _write_state(bak, st)
    return bak


# --------------------------------------------------------------------------- log

def _log_path(ctx: Ctx) -> Path:
    return ctx.paths()["control"] / "install-log.jsonl"


def _pinned_sha(ctx: Ctx):
    try:
        cur = pin_lib.current(home=ctx.home)
        return cur.get("sha") if cur.get("pinned") else None
    except Exception:  # noqa: BLE001 — informational field
        return None


def _log(ctx: Ctx, installer: str, action: str, target: Path, backup, before, after) -> None:
    p = ctx.paths()
    pin_lib.fs("mkdir", p["base"], 0o755)
    pin_lib.fs("mkdir", p["control"], 0o700)
    rec = {"ts": ctx.ts(), "installer": installer, "action": action, "target": str(target),
           "backup": str(backup) if backup else None, "sha_before": _state_sha(before),
           "sha_after": _state_sha(after), "pinned_sha": _pinned_sha(ctx)}
    pin_lib.fs("append", _log_path(ctx), (json.dumps(rec) + "\n").encode("utf-8"))


def read_log(ctx: Ctx) -> list:
    try:
        lines = _log_path(ctx).read_text(encoding="utf-8").splitlines()
    except OSError:
        return []
    out = []
    for ln in lines:
        try:
            rec = json.loads(ln)
        except ValueError:
            continue
        if isinstance(rec, dict) and rec.get("target"):
            out.append(rec)
    return out


# --------------------------------------------------------------------------- apply

def _confirmed(ctx: Ctx) -> bool:
    ans = ctx.confirm("Apply? [y/N] ")
    return str(ans or "").strip().lower() in ("y", "yes")


def _apply(ctx: Ctx, targets: list, *, after=None) -> int:
    """targets: [(path, desired_state)]. Diff, confirm, back up, write, log."""
    changes = []
    for path, want in targets:
        cur = _state(path)
        if not _same(cur, want):
            changes.append((path, cur, want))
    if not changes:
        print(f"nothing to do: {ctx.label()} is already installed")
        return 3
    for path, cur, want in changes:
        _print_diff(path, cur, want)
    if not _confirmed(ctx):
        print("not applied")
        return 1
    for path, cur, want in changes:
        bak = _backup(ctx, path, cur)
        _write_state(path, want)
        _log(ctx, ctx.label(), "install", path, bak, cur, want)
        print(f"installed: {path}" + (f" (backup {bak})" if bak else ""))
    if after:
        after()
    return 0


def _label_matches(label: str, ctx: Ctx) -> bool:
    base = f"--install-{ctx.name}"
    if not (label == base or label.startswith(base + "=") or label.startswith(base + " ")):
        return False
    arg = ctx.arg or (ctx.surface if ctx.name == "shims" else None)
    if arg and not label.startswith(f"{base}={arg}"):
        return False
    if ctx.probe and not label.endswith(" --probe"):
        return False
    return True


def _uninstall(ctx: Ctx, *, extra=(), before=None, after=None) -> int:
    """Replay the log per target (install pushes, uninstall pops). The installs of this
    installer on top of a target's stack are undone together: the target returns to the
    backup named by the lowest of them, byte-for-byte, or is removed if that install
    created it. A target whose top install belongs to another installer is refused."""
    stacks, order = {}, []
    for rec in read_log(ctx):
        t = rec["target"]
        st = stacks.setdefault(t, [])
        if rec.get("action") == "install":
            st.append(rec)
            if _label_matches(rec.get("installer", ""), ctx) and t not in order:
                order.append(t)
        elif st:
            st.pop()
    plan = []
    for t in order:
        st = stacks[t]
        if not st:
            continue
        if not _label_matches(st[-1].get("installer", ""), ctx):
            if any(_label_matches(r.get("installer", ""), ctx) for r in st):
                raise RefusedError(f"{t} was last changed by {st[-1].get('installer')}; "
                                   "uninstall that first")
            continue
        run_ = []
        while st and _label_matches(st[-1].get("installer", ""), ctx):
            run_.append(st.pop())
        path = Path(t)
        cur = _state(path)
        if _state_sha(cur) != run_[0].get("sha_after"):
            raise RefusedError(f"foreign edits since install: {t}")
        low = run_[-1]
        want = None
        if low.get("backup"):
            want = _state(Path(low["backup"]))
            if want is None:
                raise InstallerError(f"backup missing: {low['backup']}")
        plan.append((path, cur, want, low.get("backup"), len(run_)))
    for path in extra:
        cur = _state(path)
        if cur is not None and str(path) not in order:
            plan.append((path, cur, None, "__take__", 1))
    if not plan:
        print(f"nothing to do: no recorded install for {ctx.label()}")
        return 3
    for path, cur, want, _b, _n in plan:
        _print_diff(path, cur, want)
    if not _confirmed(ctx):
        print("not applied")
        return 1
    if before:
        before()
    label = ctx.label().replace("--install-", "--uninstall-", 1)
    for path, cur, want, bak, n in plan:
        if bak == "__take__":
            bak = _backup(ctx, path, cur)
        _write_state(path, want)
        for _ in range(n):
            _log(ctx, label, "uninstall", path, bak, cur, want)
        print(("restored: " if want is not None else "removed: ") + str(path))
    if after:
        after()
    return 0


# --------------------------------------------------------------------------- sources

def _src(ctx: Ctx, rel: str) -> Path:
    p = ctx.repo / rel
    if not p.is_file():
        raise MissingSource(f"source absent: {rel}")
    return p


def _render_outputs(ctx: Ctx) -> list:
    if ctx.render_list is not None:
        data = ctx.render_list() if callable(ctx.render_list) else ctx.render_list
    else:
        rs = ctx.repo / "00-bootstrap" / "doctor" / "render_shims.py"
        if not rs.is_file():
            raise MissingSource("render_shims.py absent (the output list arrives with H16)")
        try:
            p = subprocess.run([sys.executable, str(rs), "--list", "--json"], capture_output=True,
                               text=True, timeout=RENDER_TIMEOUT)
            data = json.loads(p.stdout) if p.returncode == 0 else None
        except (OSError, subprocess.SubprocessError, ValueError):
            data = None
        if data is None:
            raise MissingSource("render_shims.py --list failed")
    outs = data.get("outputs") if isinstance(data, dict) else data
    return [o for o in outs or [] if isinstance(o, dict)]


def _json_load(path: Path, *, missing=None):
    if not path.exists():
        return missing
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise InstallerError(f"unparseable {path}: {e} (fix by hand; never clobbered)") from e


def _file_state(data: bytes, mode: int):
    return ("file", data, mode)


def _render_target(ctx: Ctx, out: dict, *, keys=None):
    """(install path, desired state) for one render_shims output, or None if tracked."""
    mode = out.get("install_mode")
    dst = ctx.expand(out.get("install_path") or "")
    if mode == "tracked" or dst is None:
        return None
    src = _src(ctx, out.get("path") or "")
    old = _state(dst)
    if mode == "whole-file":
        data = src.read_bytes()
        if src.suffix == ".json":
            obj, changed = merge_settings.expand_home_strings(json.loads(data), ctx.home)
            if changed:
                data = merge_settings.dump(obj).encode("utf-8")
        return dst, _file_state(data, 0o755 if os.access(src, os.X_OK) else 0o644)
    if mode == "claude-settings-keys":
        frag = merge_settings.expand_env_home(json.loads(src.read_text(encoding="utf-8")), ctx.home)
        tgt = _json_load(dst, missing={})
        if not isinstance(tgt, dict):
            raise InstallerError(f"{dst} is not a JSON object (fix by hand)")
        try:
            new = merge_settings.replace_managed(tgt, frag, keys or out.get("keys")
                                                 or out.get("owned_keys") or ["hooks"])
        except ValueError as e:
            raise InstallerError(f"{dst}: {e} (fix by hand)") from e
        return dst, _file_state(merge_settings.dump(new).encode("utf-8"),
                                old[2] if old and old[0] == "file" else 0o600)
    if mode == "merge-hook-entries":
        frag, _ = merge_settings.expand_home_strings(json.loads(src.read_text(encoding="utf-8")),
                                                     ctx.home)
        tgt = _json_load(dst, missing={})
        try:
            new = merge_settings.merge_hook_entries(tgt, frag)
        except ValueError as e:
            raise InstallerError(f"{dst}: {e} (fix by hand)") from e
        return dst, _file_state(merge_settings.dump(new).encode("utf-8"),
                                old[2] if old and old[0] == "file" else 0o644)
    if mode == "managed-block":
        block = src.read_text(encoding="utf-8")
        lines = [ln for ln in block.splitlines() if ln.strip()]
        if len(lines) < 2:
            raise InstallerError(f"{src}: a managed block needs BEGIN and END marker lines")
        begin, end = lines[0], lines[-1]
        cur = old[1].decode("utf-8") if old and old[0] == "file" else ""
        body = block if block.endswith("\n") else block + "\n"
        # Quoted `~/` paths are rendered to this machine's home (codex does not expand `~`).
        home_s = str(ctx.home).replace("\\", "\\\\").replace('"', '\\"')
        body = re.sub(r'(["\'])~/', lambda m: m.group(1) + home_s + "/", body)
        rx = re.compile(re.escape(begin) + r".*?" + re.escape(end) + r"\n?", re.S)
        if dst.suffix == ".toml":
            cur, body = _splice_toml_tables(dst, rx.sub("", cur, count=1), body, begin, end)
            rx = re.compile(r"(?!)")  # the old block is already out of `cur`
        if rx.search(cur):
            new_text = rx.sub(lambda _m: body, cur, count=1)
        else:
            new_text = cur + ("" if not cur or cur.endswith("\n") else "\n") + body
        if dst.suffix == ".toml":
            try:
                import tomllib  # noqa: PLC0415 - optional (python 3.11+)
            except ImportError:
                tomllib = None
            if tomllib is not None:
                try:
                    tomllib.loads(new_text)
                except tomllib.TOMLDecodeError as e:
                    raise InstallerError(f"{dst}: the managed block would make invalid TOML ({e}); a table it "
                                         "declares is already defined outside the block (fix by hand)") from e
        return dst, _file_state(new_text.encode("utf-8"),
                                old[2] if old and old[0] == "file" else 0o644)
    raise InstallerError(f"unknown install_mode {mode!r} for output {out.get('id')}")


SPLICE_TAG = "# snds-workspace"
_TOML_HEADER_RE = re.compile(r"^\s*\[([^\[\]]+)\]\s*(?:#.*)?$")
_TOML_KEY_RE = re.compile(r"^\s*([A-Za-z0-9_.\"'-]+)\s*=")


def _splice_toml_tables(dst: Path, cur: str, body: str, begin: str, end: str) -> tuple:
    """TOML forbids declaring a table twice. When a table the managed block declares already
    exists outside the block (a host app may write one, e.g. Codex's [shell_environment_policy.set]),
    that table's key lines go inside the existing table, each tagged SPLICE_TAG, and the rest stays
    in the block. Lines spliced by an earlier install are removed first, so a reinstall is idempotent;
    uninstall restores the pre-install backup byte for byte. A key the existing table already
    defines is a conflict for the user, never an overwrite. Returns (cur, body)."""
    lines = [ln for ln in cur.splitlines(keepends=True) if not ln.rstrip("\n").endswith(SPLICE_TAG)]
    headers = {}
    for i, ln in enumerate(lines):
        m = _TOML_HEADER_RE.match(ln.rstrip("\n"))
        if m:
            headers.setdefault(m.group(1).strip(), i)
    sections, keep = [], []            # block sections: (table, [key lines])
    inner = body.splitlines(keepends=True)
    try:
        b0 = next(i for i, ln in enumerate(inner) if ln.rstrip("\n") == begin)
        b1 = next(i for i, ln in enumerate(inner) if ln.rstrip("\n") == end)
    except StopIteration:
        return "".join(lines), body
    table = None
    for ln in inner[b0 + 1:b1]:
        m = _TOML_HEADER_RE.match(ln.rstrip("\n"))
        if m:
            table = m.group(1).strip()
            sections.append((table, []))
        elif table is not None and ln.strip() and not ln.lstrip().startswith("#"):
            sections[-1][1].append(ln if ln.endswith("\n") else ln + "\n")
    inserts = {}
    for table, keys in sections:
        if table not in headers:
            continue
        start = headers[table] + 1
        stop = next((j for j in range(start, len(lines)) if _TOML_HEADER_RE.match(lines[j].rstrip("\n"))), len(lines))
        existing = {m.group(1) for ln in lines[start:stop] for m in [_TOML_KEY_RE.match(ln)] if m}
        clash = [k for ln in keys for m in [_TOML_KEY_RE.match(ln)] if m and m.group(1) in existing for k in [m.group(1)]]
        if clash:
            raise InstallerError(f"{dst}: [{table}] already sets {', '.join(sorted(set(clash)))} outside the managed "
                                 "block; remove it there or rename it, then re-run (fix by hand)")
        inserts[start] = [ln.rstrip("\n") + "  " + SPLICE_TAG + "\n" for ln in keys]
    if not inserts:
        return "".join(lines), body
    for at in sorted(inserts, reverse=True):
        lines[at:at] = inserts[at]
    spliced = {t for t, _k in sections if t in headers}
    out, skip = [], False
    for ln in inner:
        m = _TOML_HEADER_RE.match(ln.rstrip("\n"))
        if m:
            skip = m.group(1).strip() in spliced
            if skip:
                continue
        elif ln.rstrip("\n") == end:
            skip = False
        if skip and ln.strip():
            continue
        out.append(ln)
    return "".join(lines), "".join(out)


def _script_deps(ctx: Ctx, state) -> list:
    """Hook scripts a rendered registry calls under ~/.claude/hooks (non-HEAL ones)."""
    if not state or state[0] != "file":
        return []
    out = []
    for name in sorted(set(HOOK_SCRIPT_RE.findall(state[1].decode("utf-8", "replace")))):
        if name.startswith("workspace-"):
            continue  # HEAL class: the doctor keeps these current
        src = ctx.repo / "00-bootstrap" / "dist" / name
        if src.is_file():
            out.append((ctx.home / ".claude" / "hooks" / name, _file_state(src.read_bytes(), 0o755)))
    return out


# --------------------------------------------------------------------------- installers

def _pin_is_installed(ctx: Ctx) -> bool:
    p = ctx.paths()
    return p["lib_current"].exists() and os.access(p["bin"] / "ws-hook", os.X_OK)


def _settings_reference_ws_hook(ctx: Ctx) -> bool:
    sj = ctx.home / ".claude" / "settings.json"
    if not sj.exists():
        return False
    try:
        obj = json.loads(sj.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return "bin/ws-hook" in sj.read_text(encoding="utf-8", errors="replace")
    blob = json.dumps({"env": obj.get("env"), "hooks": obj.get("hooks")}) if isinstance(obj, dict) else ""
    return "bin/ws-hook" in blob


def do_pin(ctx: Ctx) -> int:
    p = ctx.paths()
    targets = [p["lib_current"], p["bin"] / "ws-hook", p["bin"] / "ws", p["root_file"]]
    if ctx.action == "uninstall":
        if _settings_reference_ws_hook(ctx):
            raise RefusedError("~/.claude/settings.json still references bin/ws-hook "
                               "(run --uninstall-claude-overlay first)")
        return _uninstall(ctx)
    sha = ctx.arg or ctx.sha or "HEAD"
    try:
        full = pin_lib._git(ctx.repo, "rev-parse", "--verify", f"{sha}^{{commit}}").strip()
        top = pin_lib._git(ctx.repo, "rev-parse", "--show-toplevel").strip()
    except pin_lib.PinError as e:
        raise MissingSource(str(e)) from e
    want = {p["lib_current"]: ("link", full),
            p["root_file"]: _file_state((top + "\n").encode("utf-8"), 0o644)}
    for name in pin_lib.WRAPPERS:
        try:
            data = pin_lib._git(ctx.repo, "show", f"{full}:00-bootstrap/dist/{name}", text=False)
        except pin_lib.PinError:
            continue
        want[p["bin"] / name] = _file_state(data, 0o755)
    before = {t: _state(t) for t in targets}
    changes = [t for t in want if not _same(before[t], want[t])]
    lib_ready = (p["lib_current"].parent / full / "PIN.json").is_file()
    if not changes and lib_ready:
        print(f"nothing to do: pinned at {full}")
        return 3
    for t in changes:
        _print_diff(t, before[t], want[t])
    if not lib_ready:
        print(f"+ lib/{full}/ (git archive of {len(pin_lib.PINNED_PATHS)} pinned paths, read-only)")
    if not _confirmed(ctx):
        print("not applied")
        return 1
    baks = {t: _backup(ctx, t, before[t]) for t in changes}
    res = pin_lib.pin(full, repo=ctx.repo, home=ctx.home, confirm_real_home=True,
                      agent_check=ctx.agent_check)
    for t in targets:
        after = _state(t)
        if not _same(before[t], after):
            _log(ctx, ctx.label(), "install", t, baks.get(t), before[t], after)
    print(f"pinned {res['sha']} ({len(res['paths'])} paths; absent: {len(res['absent'])})")
    return 0


def do_shims(ctx: Ctx) -> int:
    surface = ctx.arg or ctx.surface
    if ctx.action == "uninstall":
        extra = ()
        if surface in (None, "cursor") and not ctx.probe:
            extra = [ctx.home / ".claude" / "hooks" / n for n in RETIRED_CURSOR_SCRIPTS]
        return _uninstall(ctx, extra=extra)
    outs = [o for o in _render_outputs(ctx)
            if (surface is None or o.get("surface") == surface)
            and bool(o.get("probe")) == ctx.probe]
    targets = []
    for o in outs:
        t = _render_target(ctx, o)
        if t is None:
            continue
        targets.append(t)
        targets += _script_deps(ctx, t[1])
    if not targets:
        raise MissingSource(f"no installable outputs for surface={surface or 'all'}"
                            f"{' (probe)' if ctx.probe else ''}")
    if not _pin_is_installed(ctx):
        print("pin missing: installing it first")
        sub = Ctx("pin", None, "install", home=ctx.home, repo=ctx.repo,
                  agent_check=ctx.agent_check, confirm=ctx.confirm, now=ctx.now,
                  which=ctx.which, sha=None, surface=None, probe=False,
                  render_list=ctx.render_list, app_exists=ctx.app_exists)
        rc = do_pin(sub)
        if rc not in (0, 3):
            return rc
    seen, uniq = set(), []
    for path, st in targets:
        if str(path) not in seen:
            seen.add(str(path))
            uniq.append((path, st))
    return _apply(ctx, uniq)


def do_plugin(ctx: Ctx) -> int:
    if ctx.action == "uninstall":
        return _uninstall(ctx)
    targets = []
    for o in _render_outputs(ctx):
        if o.get("layer") != "snds-plugin" or o.get("probe"):
            continue
        t = _render_target(ctx, o)
        if t is None:
            continue
        plugin_dir = t[0].parent.parent
        if not plugin_dir.is_dir():
            raise MissingSource(f"plugin not built at {plugin_dir} "
                                "(run python3 09-tools/build-local-skill-plugin.py first)")
        targets.append(t)
    if not targets:
        raise MissingSource("no snds-plugin output in the render list")
    return _apply(ctx, targets)


def _launchctl(ctx: Ctx, verb: str, plist: Path) -> None:
    """Only for the real home: a temp HOME never reaches launchctl."""
    if not ctx.real or not ctx.which("launchctl"):
        return
    subprocess.run(["launchctl", verb, str(plist)], capture_output=True, timeout=15)


def do_launchd(ctx: Ctx) -> int:
    plist = ctx.home / "Library" / "LaunchAgents" / f"{LAUNCHD_LABEL}.plist"
    if ctx.action == "uninstall":
        return _uninstall(ctx, before=lambda: _launchctl(ctx, "unload", plist),
                          after=lambda: plist.exists() and _launchctl(ctx, "load", plist))
    src = _src(ctx, "00-bootstrap/dist/launchd.plist")

    def reload():
        _launchctl(ctx, "unload", plist)
        _launchctl(ctx, "load", plist)
    return _apply(ctx, [(plist, _file_state(src.read_bytes(), 0o644))], after=reload)


def do_identity(ctx: Ctx) -> int:
    if ctx.action == "uninstall":
        return _uninstall(ctx)
    rs = ctx.repo / "00-bootstrap" / "doctor" / "render_shims.py"
    if not rs.is_file():
        raise MissingSource("identity emitter absent (arrives with H17)")
    try:
        dev = ctx.pr().current_device().get("id")
    except Exception as e:  # noqa: BLE001
        raise MissingSource(f"device unresolved ({type(e).__name__})") from e
    try:
        p = subprocess.run([sys.executable, str(rs), "--emit", "identity-inc", "--device", str(dev)],
                           capture_output=True, timeout=RENDER_TIMEOUT)
    except (OSError, subprocess.SubprocessError) as e:
        raise MissingSource(f"identity emitter failed ({type(e).__name__})") from e
    if p.returncode != 0 or not p.stdout:
        raise MissingSource("identity emitter not available (arrives with H17)")
    return _apply(ctx, [(ctx.paths()["base"] / "git" / "identity.inc", _file_state(p.stdout, 0o644))])


def _probe_file(ctx: Ctx, surface: str, device: str) -> Path:
    return ctx.repo / PROBES_DIR / f"{surface}@{device}.json"


def _install_known(ctx: Ctx, row) -> bool | None:
    """Whether a surface is installed here, from its install_probe in surfaces.json.

    True or False when the probe gives an answer. None when it cannot: no probe, an item of
    an unknown kind, a relative path, or a check that raised. Callers treat None as
    installed (fail closed).
    """
    probe = row.get("install_probe") if isinstance(row, dict) else None
    items = probe.get("any_of") if isinstance(probe, dict) else None
    if not isinstance(items, list) or not items:
        return None
    unknown = False
    for item in items:
        checked = False
        try:
            cmd = item.get("cmd") if isinstance(item, dict) else None
            if isinstance(cmd, str) and cmd:
                checked = True
                if ctx.which(cmd):
                    return True
            path = item.get("path") if isinstance(item, dict) else None
            if isinstance(path, str) and path:
                full = ctx.expand(path)
                if full is None:
                    unknown = True
                else:
                    checked = True
                    if ctx.app_exists(str(full)):
                        return True
        except Exception:  # noqa: BLE001 - a check that fails gives no answer
            unknown = True
            continue
        if not checked:
            unknown = True
    return None if unknown else False


def overlay_probe_surfaces(ctx: Ctx) -> tuple:
    """(surfaces that need a probe record, refusal reasons) for the Claude overlay.

    The list comes from surfaces.json: every surface in the loaded_by list of the
    claude-user layer that is not in the Claude family and is installed on this device.
    A surface stays in the list when the table has no row for it or its install state
    cannot be determined. A missing or malformed table is a refusal.
    """
    try:
        table = ctx.pr().load_table("surfaces")
    except Exception as e:  # noqa: BLE001
        return [], [f"surfaces table unavailable ({type(e).__name__}); cannot tell which "
                    "hosts load the Claude overlay"]
    if not isinstance(table, dict):
        return [], ["surfaces table is not an object; cannot tell which hosts load the Claude overlay"]
    layer = next((ly for ly in table.get("layers") or []
                  if isinstance(ly, dict) and ly.get("id") == OVERLAY_LAYER_ID), None)
    loaded_by = layer.get("loaded_by") if layer else None
    if not isinstance(loaded_by, list):
        return [], [f"surfaces table has no {OVERLAY_LAYER_ID} layer with a loaded_by list; "
                    "cannot tell which hosts load the Claude overlay"]
    rows = {r.get("id"): r for r in table.get("surfaces") or [] if isinstance(r, dict)}
    needed, reasons = [], []
    for sid in loaded_by:
        if not isinstance(sid, str) or not SURFACE_ID_RE.match(sid):
            reasons.append(f"surfaces table: {OVERLAY_LAYER_ID} loaded_by has an invalid surface id "
                           f"{sid!r}")
            continue
        if sid in needed:
            continue
        row = rows.get(sid)
        if row is not None and row.get("family") == CLAUDE_FAMILY:
            continue
        if row is not None and _install_known(ctx, row) is False:
            continue
        needed.append(sid)
    return needed, reasons


def _git_floor_refusals(ctx: Ctx, dev: str) -> list:
    """The floor is a config-based git hook; git older than 2.54 ignores `hook.*` config silently,
    so the overlay would install with no floor and no error. Require this device's git record
    (profile_resolve.py gitcaps --record) to show config_hooks true."""
    f = _probe_file(ctx, "git", dev)
    if not f.is_file():
        return [f"git capability record missing: {PROBES_DIR}/git@{dev}.json "
                "(run python3 09-tools/profile_resolve.py gitcaps --record)"]
    try:
        rec = json.loads(f.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return [f"git capability record unreadable: git@{dev}"]
    if not isinstance(rec, dict) or rec.get("config_hooks") is not True:
        ver = rec.get("git_version") if isinstance(rec, dict) else None
        return [f"git@{dev} shows no config-based hooks (git {ver or 'unknown'}; the floor needs git >= 2.54 "
                "on PATH, then re-record gitcaps)"]
    return []


def overlay_refusals(ctx: Ctx) -> list:
    reasons = []
    p = ctx.paths()
    if not os.access(p["bin"] / "ws-hook", os.X_OK):
        reasons.append("bin/ws-hook missing or not executable (run --install-pin)")
    if not p["lib_current"].exists():
        reasons.append("lib/current missing (run --install-pin)")
    try:
        dev = ctx.pr().current_device().get("id") or "unknown"
    except Exception as e:  # noqa: BLE001
        dev = "unknown"
        reasons.append(f"device unresolved ({type(e).__name__})")
    reasons += _git_floor_refusals(ctx, dev)
    needed, table_reasons = overlay_probe_surfaces(ctx)
    reasons += table_reasons
    claude_env = _claude_settings_env_names(ctx)
    for s in needed:
        f = _probe_file(ctx, s, dev)
        if not f.is_file():
            reasons.append(f"probe record missing: {PROBES_DIR}/{s}@{dev}.json")
            continue
        try:
            rec = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            reasons.append(f"probe record unreadable: {s}@{dev}")
            continue
        # Every env probe the record keeps (one per `via`), plus the legacy single `env_probe`.
        envps = []
        if isinstance(rec, dict):
            envps = [e for e in [rec.get("env_probe"), *(rec.get("env_probes") or {}).values()] if isinstance(e, dict)]
        if any((e.get("env_presence") or {}).get("WS_CLAUDE_OVERLAY") is True for e in envps):
            reasons.append(f"probe {s}@{dev} shows env import of the Claude overlay "
                           "(WS_CLAUDE_OVERLAY present)")
            continue
        # On a device without the overlay, WS_CLAUDE_OVERLAY is absent everywhere, so its absence
        # proves nothing. Any name from Claude's own settings env in another host's shell does.
        names = set().union(*[set(e.get("env_marker_names") or []) for e in envps]) if envps else set()
        leaked = sorted(names & claude_env)
        if leaked:
            reasons.append(f"probe {s}@{dev} shows env import of Claude settings env ({', '.join(leaked)}); "
                           "the overlay would reach that host (D4: needs the Claude-only env-file channel)")
    return reasons


def _claude_settings_env_names(ctx: Ctx) -> set:
    """Env names Claude Code applies from settings: the user layer and this repo's project layer."""
    names: set = set()
    for f in (ctx.home / ".claude" / "settings.json", ctx.repo / ".claude" / "settings.json"):
        try:
            env = json.loads(f.read_text(encoding="utf-8")).get("env") or {}
        except (OSError, ValueError, AttributeError):
            continue
        if isinstance(env, dict):
            names |= {k for k in env if isinstance(k, str)}
    return names


EMPLOYER_NOIDENT_NAME = "claude-employer-noident.inc"
EMPLOYER_NOIDENT_INC = (
    "# Claude overlay (snds-workspace): included for every employer remote form AFTER the personal\n"
    "# includes, so an employer repo that also has a personal remote gets no identity at all.\n"
    "[user]\n\tuseConfigOnly = true\n\tname =\n\temail =\n"
)


def do_claude_overlay(ctx: Ctx) -> int:
    if ctx.action == "uninstall":
        return _uninstall(ctx)
    reasons = overlay_refusals(ctx)
    if reasons:
        raise RefusedError("; ".join(reasons))
    outs = [o for o in _render_outputs(ctx) if o.get("id") == OVERLAY_OUTPUT_ID]
    if not outs:
        raise MissingSource(f"render list has no {OVERLAY_OUTPUT_ID} output")
    out = dict(outs[0])
    out["install_mode"] = "claude-settings-keys"
    targets = [_render_target(ctx, out, keys=["env", "hooks"])]
    base = ctx.paths()["base"]
    for sub, mode in (("git", 0o644), ("gh-claude", 0o600)):
        d = ctx.repo / "00-bootstrap" / "dist" / sub
        if d.is_dir():
            for f in sorted(d.iterdir()):
                if f.is_file():
                    targets.append((base / sub / f.name, _file_state(f.read_bytes(), mode)))
    targets.append((base / "git" / EMPLOYER_NOIDENT_NAME, _file_state(EMPLOYER_NOIDENT_INC.encode("utf-8"), 0o644)))
    return _apply(ctx, targets)


def do_sandbox_roots(ctx: Ctx) -> int:
    if ctx.action == "uninstall":
        return _uninstall(ctx)
    try:
        table = ctx.pr().load_table("surfaces")
    except Exception as e:  # noqa: BLE001
        raise MissingSource(f"surfaces table unavailable ({type(e).__name__})") from e
    rows = [r for r in (table.get("surfaces") or []) if isinstance(r, dict) and r.get("sandbox")]
    if not rows:
        raise MissingSource("no surface declares a sandbox")
    tel = ctx.paths()["telemetry"]
    targets = []
    for r in rows:
        sb = r["sandbox"]
        key = sb.get("write_root_key") or "write roots"
        cfg = ctx.expand(sb.get("config_path") or "")
        if cfg is None or sb.get("config_path_verified") is not True:
            print(f"{r.get('id')}: sandbox config path unverified; nothing installed. By hand, "
                  f"add {tel} to `{key}` in that host's sandbox settings.")
            continue
        frag_outs = [o for o in _render_outputs(ctx)
                     if o.get("surface") == r.get("id") and "sandbox" in str(o.get("id"))]
        if not frag_outs:
            continue
        frag, _ = merge_settings.expand_home_strings(
            json.loads(_src(ctx, frag_outs[0].get("path") or "").read_text(encoding="utf-8")),
            ctx.home)
        tgt = _json_load(cfg, missing={})
        new = merge_settings.merge(json.loads(json.dumps(tgt)), frag)
        old = _state(cfg)
        targets.append((cfg, _file_state(merge_settings.dump(new).encode("utf-8"),
                                         old[2] if old and old[0] == "file" else 0o644)))
    if not targets:
        return 3
    return _apply(ctx, targets)


PROJECTS_POINTER_SRC = "00-bootstrap/dist/projects-AGENTS.md"


def do_projects_pointer(ctx: Ctx) -> int:
    """H6: the machine-local ~/Projects/AGENTS.md pointer (rendered by render_shims.py from
    beacons.json; each family's rule plus the neutral `ws` commands). Whole file, never merged."""
    if ctx.action == "uninstall":
        return _uninstall(ctx)
    src = _src(ctx, PROJECTS_POINTER_SRC)
    return _apply(ctx, [(ctx.home / "Projects" / "AGENTS.md", _file_state(src.read_bytes(), 0o644))])


def do_no_source(ctx: Ctx) -> int:
    if ctx.action == "uninstall":
        return _uninstall(ctx)
    raise MissingSource(f"{ctx.name}: no wave-0 source")


# H18: the global git lanes. One rendered include under ~/.config/snds-workspace and one managed
# include block in ~/.gitconfig; the lanes exec the PINNED git_lanes.py. Constants mirror
# 09-tools/git_lanes.py (the self-test asserts they agree).
GIT_LANES_DIST = "00-bootstrap/dist/git/lanes/ws-lanes.inc"
GIT_LANES_INC = ".config/snds-workspace/git/lanes/ws-lanes.inc"          # under HOME
GIT_LANES_PINNED = "09-tools/git_lanes.py"                               # under lib/current
GIT_LANES_BEGIN = "# BEGIN snds-workspace git lanes (installers.py git-hooks; do not edit)"
GIT_LANES_END = "# END snds-workspace git lanes"


def _in_git_repo(path: Path):
    """The work tree (or git dir) containing `path`, or None: a lane include must never live in a
    repo, where a commit, checkout or agent edit could change what every repo on the device runs."""
    cur = path.parent
    for _ in range(64):
        try:
            if (cur / ".git").exists() or (cur / "HEAD").is_file() and (cur / "objects").is_dir():
                return cur
        except OSError:
            return None
        if cur.parent == cur:
            return None
        cur = cur.parent
    return None


def git_hooks_refusals(ctx: Ctx) -> list:
    reasons = []
    p = ctx.paths()
    if not (p["lib_current"] / GIT_LANES_PINNED).is_file():
        reasons.append(f"the pinned lib has no {GIT_LANES_PINNED} (it must be in pin_lib.PINNED_PATHS; "
                       "then run workspace-doctor.sh --install-pin), so the lanes would silently allow everything")
    try:
        dev = ctx.pr().current_device().get("id") or "unknown"
    except Exception as e:  # noqa: BLE001
        dev = "unknown"
        reasons.append(f"device unresolved ({type(e).__name__})")
    reasons += [r.replace("the floor needs", "the git lanes need") for r in _git_floor_refusals(ctx, dev)]
    inc = ctx.home / GIT_LANES_INC
    repo = _in_git_repo(inc)
    if repo is not None:
        reasons.append(f"the lane include {inc} would lie inside the git repository {repo}")
    gc = ctx.home / ".gitconfig"
    if os.path.islink(gc):
        reasons.append(f"{gc} is a symlink (a dotfiles checkout?); the installer never rewrites a link — add "
                       f"the include block from {GIT_LANES_DIST}'s header by hand, or replace the link with a file")
    if os.environ.get("GIT_CONFIG_GLOBAL") and ctx.real:
        reasons.append("GIT_CONFIG_GLOBAL is set in this shell, so git would not read ~/.gitconfig; unset it first")
    return reasons


def gitconfig_with_lanes(cur: str, home: Path) -> str:
    block = f"{GIT_LANES_BEGIN}\n[include]\n\tpath = ~/{GIT_LANES_INC}\n{GIT_LANES_END}\n"
    rx = re.compile(re.escape(GIT_LANES_BEGIN) + r".*?" + re.escape(GIT_LANES_END) + r"\n?", re.S)
    if rx.search(cur):
        return rx.sub(lambda _m: block, cur, count=1)
    return cur + ("" if not cur or cur.endswith("\n") else "\n") + block


def do_git_hooks(ctx: Ctx) -> int:
    """--install-git-hooks: the include file plus one managed include block in ~/.gitconfig.
    Refuses unless the pinned lib carries git_lanes.py and this device's git record shows config
    hooks (git >= 2.54). Uninstall restores ~/.gitconfig byte-for-byte (or removes it if the
    installer created it) and removes the include."""
    if ctx.action == "uninstall":
        return _uninstall(ctx)
    src = _src(ctx, GIT_LANES_DIST)
    reasons = git_hooks_refusals(ctx)
    if reasons:
        raise RefusedError("; ".join(reasons))
    inc = ctx.home / GIT_LANES_INC
    gc = ctx.home / ".gitconfig"
    old = _state(gc)
    try:
        cur = old[1].decode("utf-8") if old else ""
    except UnicodeDecodeError as e:
        raise InstallerError(f"{gc} is not UTF-8 (fix by hand)") from e
    new = gitconfig_with_lanes(cur, ctx.home)
    return _apply(ctx, [(inc, _file_state(src.read_bytes(), 0o644)),
                        (gc, _file_state(new.encode("utf-8"), old[2] if old else 0o644))])


HANDLERS = {
    "pin": do_pin, "shims": do_shims, "git-hooks": do_git_hooks, "identity": do_identity,
    "claude-overlay": do_claude_overlay, "sandbox-roots": do_sandbox_roots,
    "plugin": do_plugin, "projects-pointer": do_projects_pointer, "launchd": do_launchd,
}


# --------------------------------------------------------------------------- run

def run(name, action, *, home, repo, agent_check=None, isatty=None, confirm=None, now=None,
        which=None, sha=None, surface=None, probe=False, render_list=None,
        app_exists=None) -> int:
    base, _, arg = str(name).partition("=")
    if base not in NAMES or action not in ACTIONS or (arg and base not in ("pin", "shims")):
        print(f"usage: installers.py install|uninstall NAME[=ARG]; NAME in {', '.join(NAMES)}",
              file=sys.stderr)
        return 2
    reasons = preflight(home, agent_check=agent_check, isatty=isatty)
    if pin_lib.is_real_home(home) and not reasons:
        reasons = pin_lib.check_writer(home, confirm_real_home=True, agent_check=agent_check)
    if reasons:
        print(f"installer refused: {'; '.join(reasons)}", file=sys.stderr)
        return 4
    ctx = Ctx(base, arg or None, action, home=home, repo=repo, agent_check=agent_check,
              confirm=confirm, now=now, which=which, sha=sha, surface=surface, probe=probe,
              render_list=render_list, app_exists=app_exists)
    guard = pin_lib.armed(home) if ctx.real else pin_lib._null()
    try:
        with guard:
            return HANDLERS[base](ctx)
    except RefusedError as e:
        print(f"installer refused: {e}", file=sys.stderr)
        return 4
    except MissingSource as e:
        print(f"nothing to install: {e}", file=sys.stderr)
        return 3
    except (InstallerError, pin_lib.PinError) as e:
        print(f"installer aborted: {e}", file=sys.stderr)
        return 1


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv[:1] == ["--self-test"]:
        return self_test()
    if len(argv) < 2 or argv[0] not in ACTIONS:
        print(__doc__.split("\n\n")[1], file=sys.stderr)
        return 2
    action, name, rest = argv[0], argv[1], argv[2:]
    sha = surface = None
    probe = False
    it = iter(rest)
    for a in it:
        if a == "--probe":
            probe = True
        elif a in ("--sha", "--surface"):
            v = next(it, None)
            if v is None:
                return 2
            if a == "--sha":
                sha = v
            else:
                surface = v
        elif a.startswith("--sha="):
            sha = a.split("=", 1)[1]
        elif a.startswith("--surface="):
            surface = a.split("=", 1)[1]
        else:
            print(f"unknown argument {a}", file=sys.stderr)
            return 2
    return run(name, action, home=Path.home(), repo=VAULT_ROOT, sha=sha, surface=surface,
               probe=probe)


# --------------------------------------------------------------------------- self-test

FIXTURES = VAULT_ROOT / "09-tools" / "fixtures" / "installer"
HUMAN, AGENT, UNDETERMINED = pin_lib.HUMAN, pin_lib.AGENT, pin_lib.UNDETERMINED
TTY = {"stdin": True, "stdout": True}
FIXED_NOW = dt.datetime(2026, 9, 22, 20, 0, 0, tzinfo=dt.timezone.utc)
_KEEP = object()


def CURSOR_ONLY(name):  # noqa: N802 - a `which` stand-in: only the cursor command exists
    return "/x/cursor" if name == "cursor" else None


def overlay_table(*, grok_probe=_KEEP, extra_loaded_by=()) -> dict:
    """A small surfaces table with the claude-user layer, shaped like the tracked one."""
    rows = [
        {"id": "claude-code", "family": "claude", "install_probe": {"any_of": [{"cmd": "claude"}]}},
        {"id": "cursor", "family": "cursor",
         "install_probe": {"any_of": [{"cmd": "cursor"}, {"path": "/Applications/Cursor.app"}]}},
        {"id": "copilot-vscode", "family": "copilot",
         "install_probe": {"any_of": [{"cmd": "code"}, {"path": "/Applications/Visual Studio Code.app"}]}},
        {"id": "grok-build", "family": "unknown-agent",
         "install_probe": {"any_of": [{"cmd": "grok"}]} if grok_probe is _KEEP else grok_probe},
    ]
    loaded_by = ["claude-code", "cursor", "copilot-vscode", "grok-build", *extra_loaded_by]
    return {"schema_version": 1, "surfaces": rows,
            "layers": [{"id": OVERLAY_LAYER_ID, "loaded_by": loaded_by},
                       {"id": "cursor-user", "loaded_by": ["cursor", "cursor-cli"]}]}


def self_test() -> int:
    import contextlib
    import io
    import tempfile
    import unittest

    real_home = pin_lib.passwd_home()

    def build_repo(td: Path) -> Path:
        files = {}
        src = FIXTURES / "repo"
        for f in sorted(src.rglob("*")):
            if f.is_file():
                files[str(f.relative_to(src))] = f.read_bytes()
        # The overlay must yield exactly the TRACKED dist keys, so the real fragment is read
        # (read-only) from this checkout instead of a fixture copy.
        frag = VAULT_ROOT / "00-bootstrap" / "dist" / "settings-user-fragment.json"
        files["00-bootstrap/dist/settings-user-fragment.json"] = frag.read_bytes()
        repo = pin_lib.make_repo(td, files)
        for rel in ("00-bootstrap/dist/ws-hook", "00-bootstrap/dist/ws",
                    "00-bootstrap/dist/cursor-sessionstart.sh"):
            os.chmod(repo / rel, 0o755)
        return repo

    class Base(unittest.TestCase):
        def setUp(self):
            self._saved = (pin_lib._PR_LOADER, pin_lib._fs, os.environ.get("PATH"))
            self.verdict_fake = pin_lib.fake_profile_resolve(AGENT)
            self.surfaces = {"surfaces": []}
            self.verdict_fake.load_table = lambda name, **_kw: self.surfaces
            pin_lib._PR_LOADER = lambda: self.verdict_fake
            self.spy = pin_lib.FsSpy(pin_lib._fs_impl)
            pin_lib._fs = self.spy
            self.td = Path(tempfile.mkdtemp(prefix="installers-"))
            self.home = self.td / "home"
            self.home.mkdir()
            self.repo = build_repo(self.td)
            self.render = json.loads((FIXTURES / "render-list.json").read_text(encoding="utf-8"))
            self.stubs = self.td / "stubs"
            self.stubs.mkdir()
            self.stub_log = self.td / "stub-calls.log"
            for name in ("launchctl", "gh", "osascript"):
                s = self.stubs / name
                s.write_text(f"#!/bin/sh\necho {name} \"$@\" >> '{self.stub_log}'\nexit 0\n")
                os.chmod(s, 0o755)
            os.environ["PATH"] = f"{self.stubs}{os.pathsep}{self._saved[2] or ''}"

        def tearDown(self):
            pin_lib._PR_LOADER, pin_lib._fs = self._saved[0], self._saved[1]
            if self._saved[2] is not None:
                os.environ["PATH"] = self._saved[2]
            for op, p in self.spy.calls:
                self.assertTrue(p.startswith(str(self.td)) or
                                os.path.realpath(p).startswith(os.path.realpath(str(self.td))),
                                f"write outside the test dir: {op} {p}")
            for d, _dirs, _files in os.walk(self.td):
                os.chmod(d, 0o755)
            shutil.rmtree(self.td, ignore_errors=True)

        def run_inst(self, name, action="install", *, verdict=HUMAN, tty=TTY, answer="y", **kw):
            out, err = io.StringIO(), io.StringIO()
            kw.setdefault("render_list", self.render)
            kw.setdefault("which", lambda _n: None)
            kw.setdefault("app_exists", lambda _p: False)
            kw.setdefault("home", self.home)
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                rc = run(name, action, repo=self.repo,
                         agent_check=(lambda v=verdict: dict(v)) if verdict is not None else None,
                         isatty=tty, confirm=lambda _p: answer, now=lambda: FIXED_NOW, **kw)
            return rc, out.getvalue(), err.getvalue()

        def stub_calls(self):
            return self.stub_log.read_text() if self.stub_log.exists() else ""

        def plugin_target(self):
            return self.home / ".claude" / "local-plugins" / "snds-local" / "snds" / "hooks" / "hooks.json"

        def install_pin(self):
            rc, out, err = self.run_inst("pin")
            self.assertIn(rc, (0, 3), out + err)

        def log(self):
            p = self.home / ".config" / "snds-workspace" / "control" / "install-log.jsonl"
            return [json.loads(x) for x in p.read_text().splitlines()] if p.exists() else []

    class TestInstaller(Base):
        def test_refusal_matrix(self):
            cases = [
                ("agent", dict(verdict=AGENT), "injected verdict: agent"),
                ("undetermined", dict(verdict=UNDETERMINED), "injected verdict: undetermined"),
                ("stdin", dict(tty={"stdin": False, "stdout": True}), "no TTY on stdin"),
                ("stdout", dict(tty={"stdin": True, "stdout": False}), "no TTY on stdout"),
            ]
            for name in NAMES:
                for action in ACTIONS:
                    for label, kw, needle in cases:
                        rc, _o, err = self.run_inst(name, action, **kw)
                        self.assertEqual(rc, 4, f"{name} {action} {label}")
                        self.assertIn("installer refused:", err)
                        self.assertIn(needle, err, f"{name} {action} {label}")

                    def boom():
                        raise ImportError("profile_resolve")
                    pin_lib._PR_LOADER = boom
                    rc, _o, err = self.run_inst(name, action)
                    pin_lib._PR_LOADER = lambda: self.verdict_fake
                    self.assertEqual(rc, 4)
                    self.assertIn("profile_resolve unavailable (ImportError)", err)
            self.assertEqual(self.spy.calls, [])
            self.assertEqual(list(self.home.iterdir()), [])

        def test_real_home_consults_real_verdict(self):
            n = len(self.spy.calls)
            for name in NAMES:
                rc, _o, err = self.run_inst(name, verdict=None, home=real_home)
                self.assertEqual(rc, 4, name)
                self.assertIn("real verdict: agent", err)
            self.assertEqual(len(self.spy.calls), n)

        def test_temp_home_without_injected_verdict_consults_the_real_one(self):
            # pin_lib._PR_LOADER is the agent fake (setUp): no injected verdict must still refuse.
            reasons = preflight(self.home, agent_check=None, isatty=TTY)
            self.assertTrue(any(r.startswith("real verdict: agent") for r in reasons), reasons)

        def test_is_real_home_fails_closed(self):
            saved = pin_lib.passwd_home

            def boom():
                raise KeyError("no passwd entry")
            pin_lib.passwd_home = boom
            try:
                self.assertTrue(pin_lib.is_real_home(self.home))
            finally:
                pin_lib.passwd_home = saved

        def test_allow_path_backup_log_and_byte_exact_uninstall(self):
            tgt = self.plugin_target()
            tgt.parent.mkdir(parents=True)
            original = b'{"hooks": {"hand": "edited"}}\n'
            tgt.write_bytes(original)
            os.chmod(tgt, 0o640)
            rc, out, err = self.run_inst("plugin")
            self.assertEqual(rc, 0, out + err)
            self.assertIn(f"--- {tgt}", out)
            self.assertIn(f"+++ {tgt}", out)
            bak = Path(f"{tgt}.ws-bak.20260922T200000Z")
            self.assertEqual(bak.read_bytes(), original)
            self.assertEqual(tgt.read_bytes(), (self.repo / "00-bootstrap/dist/plugin-hooks.json").read_bytes())
            log = self.log()
            self.assertEqual(len(log), 1)
            self.assertEqual(sorted(log[0]), ["action", "backup", "installer", "pinned_sha",
                                              "sha_after", "sha_before", "target", "ts"])
            self.assertEqual((log[0]["installer"], log[0]["action"], log[0]["backup"]),
                             ("--install-plugin", "install", str(bak)))
            self.assertEqual(self.run_inst("plugin")[0], 3)            # idempotent
            rc, out, err = self.run_inst("plugin", "uninstall")
            self.assertEqual(rc, 0, out + err)
            self.assertEqual(tgt.read_bytes(), original)
            self.assertEqual(tgt.stat().st_mode & 0o777, 0o640)
            self.assertEqual(self.log()[-1]["action"], "uninstall")
            self.assertEqual(self.run_inst("plugin", "uninstall")[0], 3)

        def test_projects_pointer_install_and_uninstall(self):
            src = self.repo / PROJECTS_POINTER_SRC
            src.write_text("# ~/Projects pointer fixture\n")
            tgt = self.home / "Projects" / "AGENTS.md"
            rc, out, err = self.run_inst("projects-pointer")
            self.assertEqual(rc, 0, out + err)
            self.assertEqual(tgt.read_bytes(), src.read_bytes())
            self.assertEqual(self.run_inst("projects-pointer")[0], 3)       # idempotent
            rc, out, err = self.run_inst("projects-pointer", "uninstall")
            self.assertEqual(rc, 0, out + err)
            self.assertFalse(tgt.exists())

        def test_codex_beacon_installs_through_shims_codex(self):
            src = self.repo / "00-bootstrap/dist/codex-AGENTS.md"
            src.write_text("<!-- WORKSPACE-BEACON v3 · codex -->\nfixture\n")
            render = {"outputs": [{"id": "beacon-codex", "path": "00-bootstrap/dist/codex-AGENTS.md",
                                   "install_path": "~/.codex/AGENTS.md", "install_mode": "whole-file",
                                   "surface": "codex", "probe": False, "keys": ["whole-file"]}]}
            self.install_pin()
            tgt = self.home / ".codex" / "AGENTS.md"
            tgt.parent.mkdir(parents=True, exist_ok=True)
            tgt.write_text("old beacon\n")
            rc, out, err = self.run_inst("shims=codex", render_list=render)
            self.assertEqual(rc, 0, out + err)
            self.assertEqual(tgt.read_bytes(), src.read_bytes())
            rc, out, err = self.run_inst("shims=codex", "uninstall", render_list=render)
            self.assertEqual(rc, 0, out + err)
            self.assertEqual(tgt.read_text(), "old beacon\n")

        def test_declined_writes_nothing(self):
            self.plugin_target().parent.mkdir(parents=True)
            rc, out, _e = self.run_inst("plugin", answer="n")
            self.assertEqual(rc, 1)
            self.assertIn("not applied", out)
            self.assertEqual(self.spy.calls, [])

        def test_foreign_edit_refuses_uninstall(self):
            self.plugin_target().parent.mkdir(parents=True)
            self.assertEqual(self.run_inst("plugin")[0], 0)
            self.plugin_target().write_text("{}\n")
            rc, _o, err = self.run_inst("plugin", "uninstall")
            self.assertEqual(rc, 4)
            self.assertIn("foreign edits", err)

        def test_launchd_created_then_removed_and_no_stub_called(self):
            plist = self.home / "Library" / "LaunchAgents" / f"{LAUNCHD_LABEL}.plist"
            rc, out, err = self.run_inst("launchd", which=shutil.which)
            self.assertEqual(rc, 0, out + err)
            self.assertEqual(plist.read_bytes(), (self.repo / "00-bootstrap/dist/launchd.plist").read_bytes())
            self.assertIsNone(self.log()[0]["backup"])
            rc, out, err = self.run_inst("launchd", "uninstall", which=shutil.which)
            self.assertEqual(rc, 0, out + err)
            self.assertFalse(plist.exists())
            self.assertEqual(self.stub_calls(), "")

        def test_pin_install_and_uninstall_guard(self):
            self.install_pin()
            base = self.home / ".config" / "snds-workspace"
            self.assertTrue(os.access(base / "bin" / "ws-hook", os.X_OK))
            self.assertEqual(self.run_inst("pin")[0], 3)
            sj = self.home / ".claude" / "settings.json"
            sj.parent.mkdir(parents=True)
            sj.write_text(json.dumps({"env": {"WS_HOOK": "~/.config/snds-workspace/bin/ws-hook"}}))
            rc, _o, err = self.run_inst("pin", "uninstall")
            self.assertEqual(rc, 4)
            self.assertIn("bin/ws-hook", err)
            sj.write_text("{}\n")
            rc, out, err = self.run_inst("pin", "uninstall")
            self.assertEqual(rc, 0, out + err)
            self.assertFalse(os.path.lexists(base / "lib" / "current"))
            self.assertFalse((base / "bin" / "ws-hook").exists())

        def test_shims_cursor_pin_first_probe_merge_and_retired_cleanup(self):
            hooks = self.home / ".cursor" / "hooks.json"
            hooks.parent.mkdir(parents=True)
            hooks.write_text('{"version": 1, "hooks": {"stop": [{"command": "mine"}]}}\n')
            original = hooks.read_bytes()
            retired = self.home / ".claude" / "hooks" / "cursor-reassert.sh"
            retired.parent.mkdir(parents=True)
            retired.write_text("#!/bin/sh\n")
            rc, out, err = self.run_inst("shims=cursor")
            self.assertEqual(rc, 0, out + err)
            self.assertIn("pin missing: installing it first", out)
            self.assertTrue((self.home / ".config/snds-workspace/lib/current").exists())
            self.assertEqual(hooks.read_bytes(),
                             (self.repo / "00-bootstrap/dist/cursor-hooks.json").read_bytes())
            script = self.home / ".claude" / "hooks" / "cursor-sessionstart.sh"
            self.assertTrue(os.access(script, os.X_OK))
            after_shims = hooks.read_bytes()
            rc, out, err = self.run_inst("shims=cursor", probe=True)
            self.assertEqual(rc, 0, out + err)
            merged = json.loads(hooks.read_text())
            cmds = [e["command"] for e in merged["hooks"]["sessionStart"]]
            self.assertEqual(len(cmds), 2)
            self.assertTrue(any("ws-hook" in c and "--probe" in c for c in cmds))
            rc, out, err = self.run_inst("shims=cursor", "uninstall", probe=True)
            self.assertEqual(rc, 0, out + err)
            self.assertEqual(hooks.read_bytes(), after_shims)
            rc, out, err = self.run_inst("shims=cursor", "uninstall")
            self.assertEqual(rc, 0, out + err)
            self.assertEqual(hooks.read_bytes(), original)
            self.assertFalse(script.exists())
            self.assertFalse(retired.exists())
            self.assertTrue(list(retired.parent.glob("cursor-reassert.sh.ws-bak.*")))

        def _seed_overlay_ready(self, probe_env=False, probe=True, config_hooks=True):
            self.install_pin()
            self.surfaces = overlay_table()
            self._seed_gitcaps(config_hooks)
            if probe:
                self._seed_probe("cursor", probe_env)

        def _seed_gitcaps(self, config_hooks=True, present=True):
            f = self.repo / PROBES_DIR / "git@dev-a.json"
            f.parent.mkdir(parents=True, exist_ok=True)
            if not present:
                f.unlink(missing_ok=True)
                return
            f.write_text(json.dumps({"schema_version": 1, "surface": "git", "device": "dev-a",
                                     "git_version": "2.54.0" if config_hooks else "2.50.1", "hasconfig": True,
                                     "config_hooks": config_hooks, "recorded_at": "2026-09-24"}))

        def _seed_probe(self, surface, env=False):
            d = self.repo / PROBES_DIR
            d.mkdir(parents=True, exist_ok=True)
            rec = json.loads((FIXTURES / "probe-cursor.json").read_text())
            rec["surface"] = surface
            rec["env_probe"]["env_presence"]["WS_CLAUDE_OVERLAY"] = env
            (d / f"{surface}@dev-a.json").write_text(json.dumps(rec))

        def overlay_ctx(self, which=lambda _n: None, app_exists=lambda _p: False):
            return Ctx("claude-overlay", None, "install", home=self.home, repo=self.repo,
                       agent_check=None, confirm=None, now=None, which=which, sha=None,
                       surface=None, probe=False, render_list=None, app_exists=app_exists)

        def test_codex_managed_block_expands_home_and_refuses_duplicate_tables(self):
            frag = VAULT_ROOT / "00-bootstrap" / "dist" / "codex-config-fragment.toml"
            (self.repo / "00-bootstrap/dist").mkdir(parents=True, exist_ok=True)
            shutil.copyfile(frag, self.repo / "00-bootstrap/dist/codex-config-fragment.toml")
            out = {"id": "codex-config-fragment", "path": "00-bootstrap/dist/codex-config-fragment.toml",
                   "install_path": "~/.codex/config.toml", "install_mode": "managed-block"}
            ctx = Ctx("shims", "codex", "install", home=self.home, repo=self.repo, agent_check=None,
                      confirm=lambda *_a: True, now=None, which=None, sha=None, surface="codex", probe=False,
                      render_list=None, app_exists=None)
            cfg = self.home / ".codex" / "config.toml"
            cfg.parent.mkdir(parents=True, exist_ok=True)
            cfg.write_text('model = "x"\n')
            _dst, state = _render_target(ctx, out)
            text = state[1].decode("utf-8")
            self.assertIn(f'"{self.home}/.config/snds-workspace/telemetry"', text)
            self.assertNotIn('"~/', text)
            cfg.write_text('[sandbox_workspace_write]\nwritable_roots = ["/tmp/x"]\n')
            try:
                import tomllib  # noqa: F401
            except ImportError:
                self.skipTest("tomllib needs python 3.11 (the duplicate-table refusal is best effort before)")
            with self.assertRaises(InstallerError) as cm:
                _render_target(ctx, out)
            self.assertIn("sandbox_workspace_write", str(cm.exception))
            self.assertIn("writable_roots", str(cm.exception))

        def test_codex_managed_block_splices_into_an_existing_table(self):
            # Work MBP 2026-09-24: the Codex app had written its own [shell_environment_policy.set].
            try:
                import tomllib
            except ImportError:
                self.skipTest("tomllib needs python 3.11")
            frag = VAULT_ROOT / "00-bootstrap" / "dist" / "codex-config-fragment.toml"
            (self.repo / "00-bootstrap/dist").mkdir(parents=True, exist_ok=True)
            shutil.copyfile(frag, self.repo / "00-bootstrap/dist/codex-config-fragment.toml")
            out = {"id": "codex-config-fragment", "path": "00-bootstrap/dist/codex-config-fragment.toml",
                   "install_path": "~/.codex/config.toml", "install_mode": "managed-block"}
            ctx = Ctx("shims", "codex", "install", home=self.home, repo=self.repo, agent_check=None,
                      confirm=lambda *_a: True, now=None, which=None, sha=None, surface="codex", probe=False,
                      render_list=None, app_exists=None)
            cfg = self.home / ".codex" / "config.toml"
            cfg.parent.mkdir(parents=True, exist_ok=True)
            user = 'model = "x"\n\n[shell_environment_policy.set]\nAPP_KEY = "app"\n\n[features]\nx = true\n'
            cfg.write_text(user)
            _dst, state = _render_target(ctx, out)
            text = state[1].decode("utf-8")
            doc = tomllib.loads(text)
            self.assertEqual(doc["shell_environment_policy"]["set"]["APP_KEY"], "app")      # user key kept
            self.assertIn("WS_SURFACE_FAMILY", doc["shell_environment_policy"]["set"])      # spliced in
            self.assertIn("writable_roots", doc["sandbox_workspace_write"])                  # rest stays in the block
            self.assertEqual(text.count("[shell_environment_policy.set]"), 1)
            self.assertTrue(any(ln.endswith(SPLICE_TAG) for ln in text.splitlines() if "WS_SURFACE_FAMILY" in ln))
            cfg.write_text(text)
            _dst, again = _render_target(ctx, out)                                          # reinstall: idempotent
            self.assertEqual(again[1].decode("utf-8"), text)
            cfg.write_text(user.replace('APP_KEY = "app"', 'WS_SURFACE_FAMILY = "mine"'))
            with self.assertRaises(InstallerError) as cm:                                   # a real clash refuses
                _render_target(ctx, out)
            self.assertIn("WS_SURFACE_FAMILY", str(cm.exception))

        def test_overlay_replace_end_to_end(self):
            self._seed_overlay_ready()
            sj = self.home / ".claude" / "settings.json"
            sj.parent.mkdir(parents=True, exist_ok=True)
            stale = (FIXTURES / "settings-v1-stale.json").read_bytes()
            sj.write_bytes(stale)
            rc, out, err = self.run_inst("claude-overlay", which=CURSOR_ONLY)
            self.assertEqual(rc, 0, out + err)
            got = json.loads(sj.read_text())
            frag = merge_settings.expand_env_home(json.loads(
                (self.repo / "00-bootstrap/dist/settings-user-fragment.json").read_text()), self.home)
            managed = {k: v for k, v in got["env"].items() if merge_settings.is_managed_env(k)}
            self.assertEqual(managed, frag["env"])
            self.assertEqual(got["env"]["EDITOR"], "vi")                 # user key kept
            cmds = [h["command"] for g in got["hooks"]["SessionStart"] for h in g["hooks"]]
            self.assertEqual(sum("workspace-sessionstart" in c for c in cmds), 1)
            self.assertIn("my-own-hook.sh", " ".join(cmds))               # user hook kept
            ni = self.home / ".config/snds-workspace/git" / EMPLOYER_NOIDENT_NAME
            self.assertEqual(ni.read_text(), EMPLOYER_NOIDENT_INC)          # the employer no-identity include
            self.assertIn("useConfigOnly = true", EMPLOYER_NOIDENT_INC)
            self.assertTrue((self.home / ".config/snds-workspace/git/claude-identity.inc").is_file())
            self.assertTrue((self.home / ".config/snds-workspace/gh-claude/config.yml").is_file())
            self.assertEqual(self.run_inst("claude-overlay", which=CURSOR_ONLY)[0], 3)
            rc, out, err = self.run_inst("claude-overlay", "uninstall")
            self.assertEqual(rc, 0, out + err)
            self.assertEqual(sj.read_bytes(), stale)

        def test_overlay_refusals(self):
            rc, _o, err = self.run_inst("claude-overlay")
            self.assertEqual(rc, 4)
            self.assertIn("bin/ws-hook", err)
            self._seed_overlay_ready(probe=False)
            rc, _o, err = self.run_inst("claude-overlay", which=CURSOR_ONLY)
            self.assertEqual(rc, 4)
            self.assertIn("probe record missing", err)
            self._seed_overlay_ready(probe_env=True)
            rc, _o, err = self.run_inst("claude-overlay", which=CURSOR_ONLY)
            self.assertEqual(rc, 4)
            self.assertIn("env import", err)
            self._seed_overlay_ready()
            rc, _o, err = self.run_inst("claude-overlay",
                                        which=lambda n: f"/x/{n}" if n in ("cursor", "code") else None)
            self.assertEqual(rc, 4)
            self.assertIn("copilot-vscode@dev-a", err)
            self.assertNotIn("cursor@dev-a", err)

        def test_overlay_refuses_claude_settings_env_import_before_first_install(self):
            # Personal MBP 2026-09-24: no overlay yet, so WS_CLAUDE_OVERLAY was absent everywhere, but
            # Codex desktop and Grok Build shells carried names from Claude's settings env.
            self._seed_overlay_ready()
            sj = self.home / ".claude" / "settings.json"
            sj.parent.mkdir(parents=True, exist_ok=True)
            sj.write_text(json.dumps({"env": {"CLAUDE_CODE_DISABLE_AUTO_MEMORY": "1"}}))
            rc, out, err = self.run_inst("claude-overlay", which=CURSOR_ONLY)
            self.assertEqual(rc, 0, out + err)                   # the seeded cursor shell carries none of it
            self.run_inst("claude-overlay", "uninstall")
            f = self.repo / PROBES_DIR / "cursor@dev-a.json"
            rec = json.loads(f.read_text())
            rec["env_probe"]["env_marker_names"] = ["CLAUDE_CODE_DISABLE_AUTO_MEMORY", "TERM_PROGRAM"]
            f.write_text(json.dumps(rec))
            rc, _o, err = self.run_inst("claude-overlay", which=CURSOR_ONLY)
            self.assertEqual(rc, 4)
            self.assertIn("env import of Claude settings env (CLAUDE_CODE_DISABLE_AUTO_MEMORY)", err)

        def test_overlay_reads_every_per_via_env_probe(self):
            self._seed_overlay_ready()
            f = self.repo / PROBES_DIR / "cursor@dev-a.json"
            rec = json.loads(f.read_text())
            clean = dict(rec["env_probe"])
            rec["env_probes"] = {"terminal": clean,
                                 "run_in_terminal": dict(clean, env_presence={"WS_CLAUDE_OVERLAY": True})}
            f.write_text(json.dumps(rec))                        # the latest env_probe is clean; an older via is not
            rc, _o, err = self.run_inst("claude-overlay", which=CURSOR_ONLY)
            self.assertEqual(rc, 4)
            self.assertIn("WS_CLAUDE_OVERLAY present", err)

        def test_overlay_refuses_git_without_config_hooks(self):
            self._seed_overlay_ready(config_hooks=False)
            rc, _o, err = self.run_inst("claude-overlay", which=CURSOR_ONLY)
            self.assertEqual(rc, 4)
            self.assertIn("no config-based hooks (git 2.50.1", err)
            self._seed_gitcaps(present=False)
            rc, _o, err = self.run_inst("claude-overlay", which=CURSOR_ONLY)
            self.assertEqual(rc, 4)
            self.assertIn("git capability record missing", err)
            self._seed_gitcaps(config_hooks=True)
            rc, out, err = self.run_inst("claude-overlay", which=CURSOR_ONLY)
            self.assertEqual(rc, 0, out + err)

        # T10 rerun L-09: the probe list comes from surfaces.json, not a hard-coded list.
        def test_overlay_probe_list_skips_an_uninstalled_cursor(self):
            self._seed_overlay_ready(probe=False)
            reasons = overlay_refusals(self.overlay_ctx())
            self.assertEqual(reasons, [])
            self.assertFalse(any("cursor@" in r for r in reasons), reasons)
            rc, out, err = self.run_inst("claude-overlay")          # no Cursor, no probe record
            self.assertEqual(rc, 0, out + err)

        def test_overlay_probe_list_requires_an_installed_non_claude_surface(self):
            self._seed_overlay_ready(probe=False)
            ctx = self.overlay_ctx(which=lambda n: f"/x/{n}" if n in ("grok", "claude") else None)
            reasons = overlay_refusals(ctx)
            self.assertIn(f"probe record missing: {PROBES_DIR}/grok-build@dev-a.json", reasons)
            self.assertFalse(any("claude-code@" in r for r in reasons), reasons)   # Claude family
            self.assertFalse(any("cursor@" in r or "copilot-vscode@" in r for r in reasons), reasons)
            self._seed_probe("grok-build", env=True)
            self.assertTrue(any("probe grok-build@dev-a shows env import" in r
                                for r in overlay_refusals(ctx)))
            self._seed_probe("grok-build")
            self.assertEqual(overlay_refusals(ctx), [])

        def test_overlay_probe_list_fails_closed_when_install_state_is_unknown(self):
            self._seed_overlay_ready(probe=False)
            missing = f"probe record missing: {PROBES_DIR}/grok-build@dev-a.json"
            unknown_probes = (None, {}, {"any_of": []}, {"any_of": [{"bundle": "x"}]},
                              {"any_of": [{"path": "Applications/Grok.app"}]})
            for probe in unknown_probes:
                self.surfaces = overlay_table(grok_probe=probe)
                self.assertIn(missing, overlay_refusals(self.overlay_ctx()), probe)

            def boom(_n):
                raise OSError("which failed")
            self.surfaces = overlay_table()
            reasons = overlay_refusals(self.overlay_ctx(which=boom))
            for s in ("cursor", "copilot-vscode", "grok-build"):
                self.assertIn(f"probe record missing: {PROBES_DIR}/{s}@dev-a.json", reasons)
            self.surfaces = overlay_table(extra_loaded_by=["new-host"])      # no surface row
            self.assertIn(f"probe record missing: {PROBES_DIR}/new-host@dev-a.json",
                          overlay_refusals(self.overlay_ctx()))
            for table in ({"surfaces": []}, {"layers": [{"id": "claude-user"}]}):
                self.surfaces = table
                self.assertTrue(any("cannot tell which hosts load the Claude overlay" in r
                                    for r in overlay_refusals(self.overlay_ctx())), table)

            def no_table(_name, **_kw):
                raise OSError("surfaces.json unreadable")
            self.verdict_fake.load_table = no_table
            self.assertTrue(any(r.startswith("surfaces table unavailable (OSError)")
                                for r in overlay_refusals(self.overlay_ctx())))

        def test_overlay_probe_list_on_the_tracked_table(self):
            """Today's behaviour on the tracked surfaces.json: Cursor and VS Code need a probe
            record when installed, and only then; Claude Code never does."""
            self.install_pin()
            self.surfaces = json.loads((VAULT_ROOT / "02-shared-references" / "surfaces.json")
                                       .read_text(encoding="utf-8"))
            both = self.overlay_ctx(which=lambda n: f"/x/{n}" if n in ("cursor", "code", "claude") else None)
            needed, reasons = overlay_probe_surfaces(both)
            self.assertEqual(reasons, [])
            self.assertIn("cursor", needed)
            self.assertIn("copilot-vscode", needed)
            self.assertNotIn("claude-code", needed)
            vscode_app = self.overlay_ctx(app_exists=lambda p: p == "/Applications/Visual Studio Code.app")
            needed, _r = overlay_probe_surfaces(vscode_app)
            self.assertIn("copilot-vscode", needed)
            self.assertNotIn("cursor", needed)
            needed, _r = overlay_probe_surfaces(self.overlay_ctx())
            self.assertNotIn("cursor", needed)
            self.assertNotIn("copilot-vscode", needed)

        def _seed_git_lanes(self, *, pinned=True, config_hooks=True):
            """The lanes' dist include in the fixture repo, a gitcaps record and (optionally) a lib/current
            that carries git_lanes.py (a hand-made lib dir: the fixture pin has no git_lanes.py)."""
            dist = self.repo / GIT_LANES_DIST
            dist.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(VAULT_ROOT / GIT_LANES_DIST, dist)
            self._seed_gitcaps(config_hooks)
            lib = self.home / ".config/snds-workspace/lib/lanes-fixture"
            (lib / "09-tools").mkdir(parents=True, exist_ok=True)
            if pinned:
                (lib / GIT_LANES_PINNED).write_text("# fixture pinned lane\n")
            cur = self.home / ".config/snds-workspace/lib/current"
            if os.path.lexists(cur):
                cur.unlink()
            cur.symlink_to("lanes-fixture")

        def test_git_hooks_constants_match_git_lanes(self):
            import importlib.util
            spec = importlib.util.spec_from_file_location("git_lanes_const", VAULT_ROOT / "09-tools/git_lanes.py")
            gl = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(gl)
            self.assertEqual((gl.DIST_INCLUDE_REL, gl.INSTALL_INCLUDE_REL, gl.GITCONFIG_BEGIN, gl.GITCONFIG_END),
                             (GIT_LANES_DIST, GIT_LANES_INC, GIT_LANES_BEGIN, GIT_LANES_END))
            self.assertEqual(gitconfig_with_lanes("", self.home), gl.gitconfig_block(self.home))
            self.assertTrue(gl.PINNED_SELF_REL.endswith(GIT_LANES_PINNED))

        def test_git_hooks_install_and_byte_exact_uninstall(self):
            self._seed_git_lanes()
            gc = self.home / ".gitconfig"
            original = b"[user]\n\tname = Someone\n[alias]\n\tst = status"          # no trailing newline
            gc.write_bytes(original)
            os.chmod(gc, 0o600)
            rc, out, err = self.run_inst("git-hooks")
            self.assertEqual(rc, 0, out + err)
            inc = self.home / GIT_LANES_INC
            self.assertEqual(inc.read_bytes(), (VAULT_ROOT / GIT_LANES_DIST).read_bytes())
            text = gc.read_text()
            self.assertTrue(text.startswith(original.decode() + "\n"), text)       # user content kept
            self.assertIn(f"\tpath = ~/{GIT_LANES_INC}\n", text)
            self.assertEqual(gc.stat().st_mode & 0o777, 0o600)
            self.assertEqual(self.run_inst("git-hooks")[0], 3)                     # idempotent
            rc, out, err = self.run_inst("git-hooks", "uninstall")
            self.assertEqual(rc, 0, out + err)
            self.assertEqual(gc.read_bytes(), original)
            self.assertFalse(inc.exists())
            gc.unlink()                                                            # no ~/.gitconfig at all
            self.assertEqual(self.run_inst("git-hooks")[0], 0)
            self.assertTrue(gc.is_file())
            self.assertEqual(self.run_inst("git-hooks", "uninstall")[0], 0)
            self.assertFalse(gc.exists())
            self.assertFalse(inc.exists())

        def test_git_hooks_foreign_edit_refuses_uninstall(self):
            self._seed_git_lanes()
            self.assertEqual(self.run_inst("git-hooks")[0], 0)
            gc = self.home / ".gitconfig"
            gc.write_text(gc.read_text() + "[core]\n\teditor = vi\n")
            rc, _o, err = self.run_inst("git-hooks", "uninstall")
            self.assertEqual(rc, 4)
            self.assertIn("foreign edits since install", err)

        def test_git_hooks_refusals(self):
            self._seed_git_lanes(pinned=False)
            rc, _o, err = self.run_inst("git-hooks")
            self.assertEqual(rc, 4)
            self.assertIn("pinned lib has no 09-tools/git_lanes.py", err)
            self._seed_git_lanes(config_hooks=False)
            rc, _o, err = self.run_inst("git-hooks")
            self.assertEqual(rc, 4)
            self.assertIn("no config-based hooks (git 2.50.1", err)
            self.assertIn("the git lanes need git >= 2.54", err)
            self._seed_git_lanes()
            self._seed_gitcaps(present=False)
            rc, _o, err = self.run_inst("git-hooks")
            self.assertEqual(rc, 4)
            self.assertIn("git capability record missing", err)
            self._seed_git_lanes()
            real = self.td / "dotfiles-gitconfig"
            real.write_text("[user]\n\tname = x\n")
            (self.home / ".gitconfig").symlink_to(real)
            rc, _o, err = self.run_inst("git-hooks")
            self.assertEqual(rc, 4)
            self.assertIn("is a symlink", err)
            (self.home / ".gitconfig").unlink()
            (self.home / ".config" / ".git").mkdir(parents=True)                     # ~/.config is a dotfiles repo
            rc, _o, err = self.run_inst("git-hooks")
            self.assertEqual(rc, 4)
            self.assertIn("would lie inside the git repository", err)
            self.assertEqual(real.read_text(), "[user]\n\tname = x\n")
            self.assertFalse((self.home / GIT_LANES_INC).exists())

        def test_missing_sources_exit_3(self):
            for name in ("git-hooks", "projects-pointer", "identity"):   # fixture repo has no pointer
                rc, _o, err = self.run_inst(name)
                self.assertEqual(rc, 3, name + err)
            self.assertEqual(self.run_inst("shims", render_list=None)[0], 3)   # no render_shims.py
            self.assertEqual(self.run_inst("plugin")[0], 3)                  # plugin not built
            self.assertEqual(self.run_inst("shims=nowhere")[0], 3)
            (self.repo / "00-bootstrap/dist/launchd.plist").unlink()
            self.assertEqual(self.run_inst("launchd")[0], 3)
            self.surfaces = {"surfaces": [{"id": "cursor", "sandbox": {
                "write_root_key": "additionalReadwritePaths", "config_path": None,
                "config_path_verified": False}}]}
            rc, out, _e = self.run_inst("sandbox-roots")
            self.assertEqual(rc, 3)
            self.assertIn("unverified", out)
            self.assertEqual(self.spy.calls, [])

        def test_usage(self):
            self.assertEqual(self.run_inst("nope")[0], 2)
            self.assertEqual(self.run_inst("plugin=x")[0], 2)
            self.assertEqual(self.run_inst("plugin", "reinstall")[0], 2)

    class TestOverlayReplace(unittest.TestCase):
        def test_floor_command_is_bound_to_the_install_home(self):
            cmd = 'H="$HOME"; W="$H/.config/snds-workspace/bin/ws-hook"; exec env HOME="$H" "$W"'
            got = merge_settings.expand_env_home({"env": {"GIT_CONFIG_VALUE_9": cmd, "X": "~/a", "Y": "plain"}},
                                                 "/Users/pat sample")
            self.assertEqual(got["env"]["GIT_CONFIG_VALUE_9"],
                             "H='/Users/pat sample'; W=\"$H/.config/snds-workspace/bin/ws-hook\"; exec env HOME=\"$H\" \"$W\"")
            self.assertEqual(got["env"]["X"], "/Users/pat sample/a")
            self.assertEqual(got["env"]["Y"], "plain")

        def test_stale_v1_env_yields_exactly_dist_keys(self):
            stale = json.loads((FIXTURES / "settings-v1-stale.json").read_text())
            self.assertIn("GIT_AUTHOR_EMAIL", stale["env"])
            frag = merge_settings.expand_env_home(json.loads(
                (VAULT_ROOT / "00-bootstrap/dist/settings-user-fragment.json").read_text()), "/h")
            new = merge_settings.replace_managed(stale, frag, ["env", "hooks"])
            managed = {k: v for k, v in new["env"].items() if merge_settings.is_managed_env(k)}
            self.assertEqual(managed, frag["env"])
            self.assertNotIn("GIT_AUTHOR_EMAIL", new["env"])

        def test_merge_settings_cli_legacy_and_replace(self):
            with tempfile.TemporaryDirectory() as td:
                t = Path(td) / "s.json"
                t.write_bytes((FIXTURES / "settings-v1-stale.json").read_bytes())
                frag = VAULT_ROOT / "00-bootstrap/dist/settings-user-fragment.json"
                ms = str(HERE / "merge_settings.py")
                env = dict(os.environ, HOME=td)
                r = subprocess.run([sys.executable, ms, "--replace-managed", "env", "--dry-run",
                                    str(frag), str(t)], capture_output=True, text=True, env=env, timeout=30)
                self.assertEqual(r.returncode, 0)
                self.assertIn("differs: env.GIT_AUTHOR_EMAIL", r.stdout)
                r = subprocess.run([sys.executable, ms, "--replace-managed", "env,hooks", "--no-backup",
                                    str(frag), str(t)], capture_output=True, env=env, timeout=30)
                self.assertEqual(r.returncode, 0)
                self.assertEqual(list(Path(td).glob("s.json.bak-*")), [])
                r = subprocess.run([sys.executable, ms, "--replace-managed", "env,hooks", "--no-backup",
                                    str(frag), str(t)], capture_output=True, env=env, timeout=30)
                self.assertEqual(r.returncode, 3)
                t.write_text("{}\n")
                r = subprocess.run([sys.executable, ms, str(frag), str(t)], capture_output=True,
                                   env=env, timeout=30)
                self.assertEqual(r.returncode, 0)                       # legacy merge
                self.assertEqual(len(list(Path(td).glob("s.json.bak-*"))), 1)
                r = subprocess.run([sys.executable, ms, str(frag), str(t)], capture_output=True,
                                   env=env, timeout=30)
                self.assertEqual(r.returncode, 3)                       # legacy no-op

    class TestDoctorModes(unittest.TestCase):
        """The unattended modes change no REPORT-class file and call no launchctl, gh or
        osascript on a temp HOME; --quick never runs scan."""

        def setUp(self):
            self.td = Path(tempfile.mkdtemp(prefix="doctor-"))
            self.home = self.td / "home"
            self.ws = self.td / "ws"
            dist = self.ws / "00-bootstrap" / "dist"
            (self.ws / "00-bootstrap" / "doctor").mkdir(parents=True)
            dist.mkdir(parents=True)
            (self.ws / "AGENTS.md").write_text("fixture\n")
            for f in ("workspace-doctor.sh", "merge_settings.py", "pin_lib.py", "installers.py"):
                shutil.copy2(HERE / f, self.ws / "00-bootstrap" / "doctor" / f)
            real_dist = VAULT_ROOT / "00-bootstrap" / "dist"
            for f in real_dist.iterdir():
                if f.is_file() and not f.name.startswith("beacon-repos"):
                    shutil.copy2(f, dist / f.name)
            (dist / "git").mkdir()
            shutil.copy2(real_dist / "git" / "claude-identity.inc", dist / "git" / "claude-identity.inc")
            (dist / "gh-claude").mkdir()
            for f in ("hosts.yml", "config.yml"):
                (dist / "gh-claude" / f).write_text("fixture: true\n")
            beacon_repo = self.td / "beacon-repo"
            beacon_repo.mkdir()
            (dist / "beacon-repos.txt").write_text(f"{beacon_repo}\n")
            # render_shims stand-in: --install-state, and --rewrite-audit exiting with the code in
            # <td>/rewrite-audit-exit (0 when absent).
            (self.ws / "00-bootstrap" / "doctor" / "render_shims.py").write_text(
                "import json, os, sys\n"
                "if '--rewrite-audit' in sys.argv:\n"
                "    m = os.path.join(os.environ['HOME'], '..', 'rewrite-audit-exit')\n"
                "    sys.exit(int(open(m).read()) if os.path.exists(m) else 0)\n"
                "print(json.dumps({'schema_version': 1, 'cmd': 'install-state', "
                "'surfaces': {'cursor': {'installed': True, 'via': 'cmd:cursor'}}}))\n")
            h = self.home
            (h / ".claude" / "hooks").mkdir(parents=True)
            (h / ".claude" / "workspace-brain-path").write_text(f"{self.ws}\n")
            seeds = {
                ".cursor/hooks.json": "{}\n",
                ".claude/hooks/cursor-sessionstart.sh": "stale\n",
                ".claude/hooks/cursor-reassert.sh": "retired copy\n",
                ".claude/settings.json": (FIXTURES / "settings-v1-stale.json").read_text(),
                ".config/snds-workspace/git/claude-identity.inc": "stale\n",
                ".config/snds-workspace/gh-claude/hosts.yml": "stale\n",
                ".claude/local-plugins/snds-local/snds/hooks/hooks.json": "{}\n",
                ".codex/AGENTS.md": "stale beacon\n",
                "Projects/AGENTS.md": "stale pointer\n",
                "Library/LaunchAgents/design.snds.workspace-doctor.plist": "stale\n",
                "Projects/.claude/hooks/dispatcher.py": "# fossil\n",
                ".config/snds-workspace/lib/fake/09-tools/profile_resolve.py": (
                    "import os, sys\n"
                    "p = os.path.join(os.environ['HOME'], '.config/snds-workspace/telemetry/scan-called')\n"
                    "open(p, 'a').write(' '.join(sys.argv[1:]) + '\\n')\n"),
            }
            for rel, text in seeds.items():
                p = h / rel
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(text)
            (h / ".config/snds-workspace/telemetry").mkdir(parents=True)
            os.symlink("fake", h / ".config/snds-workspace/lib/current")
            self.report = {rel: (h / rel).read_bytes() for rel in seeds}
            self.stubs = self.td / "stubs"
            self.stubs.mkdir()
            self.stub_log = self.td / "stub-calls.log"
            for name in ("launchctl", "gh", "osascript"):
                s = self.stubs / name
                s.write_text(f"#!/bin/sh\necho {name} \"$@\" >> '{self.stub_log}'\nexit 0\n")
                os.chmod(s, 0o755)

        def tearDown(self):
            shutil.rmtree(self.td, ignore_errors=True)

        def doctor(self, *args):
            env = {k: v for k, v in os.environ.items() if not k.startswith("WS_")}
            env.update(HOME=str(self.home), PATH=f"{self.stubs}{os.pathsep}{os.environ.get('PATH', '')}")
            return subprocess.run(["bash", str(self.ws / "00-bootstrap/doctor/workspace-doctor.sh"), *args],
                                  capture_output=True, text=True, env=env, timeout=120,
                                  stdin=subprocess.DEVNULL)

        def snapshot(self):
            snap = {}
            for p in sorted(self.home.rglob("*")):
                if p.is_file() and not p.is_symlink():
                    snap[str(p.relative_to(self.home))] = p.read_bytes()
            return snap

        def assert_report_unchanged(self):
            for rel, data in self.report.items():
                self.assertEqual((self.home / rel).read_bytes(), data, f"REPORT-class file changed: {rel}")

        def stub_calls(self):
            return self.stub_log.read_text() if self.stub_log.exists() else ""

        def heal_or_allowed(self, rel, telemetry_ok):
            heal = (".claude/hooks/workspace-", ".claude/CLAUDE.md", ".claude/workspace-brain-path",
                    ".claude/ws-state/")
            return rel.startswith(heal) or (telemetry_ok and rel.startswith(".config/snds-workspace/telemetry/"))

        def test_quick_quiet_reports_only_and_never_scans(self):
            before = self.snapshot()
            r = self.doctor("--quick", "--quiet")
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assert_report_unchanged()
            self.assertEqual(self.stub_calls(), "")
            self.assertFalse((self.home / ".config/snds-workspace/telemetry/scan-called").exists())
            self.assertFalse((self.home / ".config/snds-workspace/telemetry/install-state.json").exists())
            for rel in set(self.snapshot()) - set(before):
                self.assertTrue(self.heal_or_allowed(rel, False), f"unexpected write: {rel}")
            # HEAL class still heals
            self.assertEqual((self.home / ".claude/hooks/workspace-sessionstart.sh").read_bytes(),
                             (self.ws / "00-bootstrap/dist/workspace-sessionstart.sh").read_bytes())

        def test_quiet_reports_only_scans_pinned_and_writes_install_state(self):
            before = self.snapshot()
            r = self.doctor("--quiet")
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assert_report_unchanged()
            self.assertEqual(self.stub_calls(), "")
            self.assertEqual((self.home / ".config/snds-workspace/telemetry/scan-called").read_text(),
                             "scan --report\n")
            st = json.loads((self.home / ".config/snds-workspace/telemetry/install-state.json").read_text())
            self.assertEqual(sorted(st), ["device", "generated_at", "schema_version", "surfaces"])
            for rel in set(self.snapshot()) - set(before):
                self.assertTrue(self.heal_or_allowed(rel, True), f"unexpected write: {rel}")

        def test_quiet_without_pin_skips_scan(self):
            os.unlink(self.home / ".config/snds-workspace/lib/current")
            r = self.doctor("--quiet")
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertFalse((self.home / ".config/snds-workspace/telemetry/scan-called").exists())
            r = self.doctor()
            self.assertIn("nothing pinned", r.stdout)

        def test_default_reports_with_installer_names(self):
            r = self.doctor()
            self.assert_report_unchanged()
            self.assertEqual(self.stub_calls(), "")
            for flag in ("--install-shims=cursor", "--install-claude-overlay", "--install-plugin",
                         "--install-launchd", "--uninstall-shims=cursor", "--install-shims=codex",
                         "--install-projects-pointer"):
                self.assertIn(flag, r.stdout)

        def test_check_writes_nothing(self):
            before = self.snapshot()
            r = self.doctor("--check")
            self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
            self.assertEqual(self.snapshot(), before)
            self.assertNotIn("launchctl", self.stub_calls())
            self.assertNotIn("osascript", self.stub_calls())
            self.assertIn("overlay env", r.stdout)

        def test_check_audits_the_git_lanes(self):
            """H18: not installed is a NOTE naming the installer; installed and untouched is silent; a later
            global entry that disables a lane is DRIFT; --check still writes nothing."""
            tools = self.ws / "09-tools"
            tools.mkdir(exist_ok=True)
            shutil.copy2(VAULT_ROOT / "09-tools" / "git_lanes.py", tools / "git_lanes.py")
            dist = self.ws / GIT_LANES_DIST
            dist.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(VAULT_ROOT / GIT_LANES_DIST, dist)
            r = self.doctor("--check")
            self.assertIn("git lanes not installed — to install: workspace-doctor.sh --install-git-hooks", r.stdout)
            inc = self.home / GIT_LANES_INC
            inc.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(dist, inc)
            gc = self.home / ".gitconfig"
            gc.write_text(gitconfig_with_lanes("", self.home))
            r = self.doctor("--check")
            self.assertNotIn("git lanes", r.stdout, r.stdout)
            gc.write_text(gc.read_text() + '[hook "ws-lane-pre-push"]\n\tenabled = false\n')
            before = self.snapshot()
            r = self.doctor("--check")
            self.assertIn("DRIFT: git lanes shadowed, disabled or stale", r.stdout)
            self.assertIn("ws-lane-pre-push disabled", r.stdout)
            self.assertEqual(self.snapshot(), before)

        def test_check_maps_the_rewrite_audit_exit_code(self):
            """T10 rerun T-01: exit 1 is the H17-R9 NOTE, any other failure is 'unavailable', 0 is silent."""
            marker = self.td / "rewrite-audit-exit"
            seen = {}
            for code in ("0", "1", "2"):
                marker.write_text(code)
                seen[code] = self.doctor("--check").stdout
            self.assertNotIn("rewrites an employer URL", seen["0"])
            self.assertNotIn("rewrite audit unavailable", seen["0"])
            self.assertIn("NOTE: a git config file rewrites an employer URL", seen["1"])
            self.assertIn("NOTE: rewrite audit unavailable", seen["2"])
            self.assertNotIn("rewrites an employer URL", seen["2"])

        def test_check_notes_declared_home_and_brain(self):
            """T10 rerun L-05: devices.json says doctor --check verifies `home` (and `brain`)."""
            import socket
            (self.ws / "09-tools").mkdir()
            shutil.copy2(VAULT_ROOT / "09-tools" / "profile_resolve.py", self.ws / "09-tools" / "profile_resolve.py")
            dev = json.loads((VAULT_ROOT / "02-shared-references" / "devices.json").read_text(encoding="utf-8"))
            host = socket.gethostname().split(".", 1)[0]
            for row in dev["devices"]:
                row["hostnames"] = [host] if row["id"] == "work-mbp" else [f"not-{host}"]
                if row["id"] == "work-mbp":
                    row.update(home="/nonexistent/fixture-home", brain="Projects/elsewhere")
            (self.ws / "02-shared-references").mkdir()
            (self.ws / "02-shared-references" / "devices.json").write_text(json.dumps(dev), encoding="utf-8")
            r = self.doctor("--check")
            self.assertIn("devices.json declares home /nonexistent/fixture-home", r.stdout, r.stdout + r.stderr)
            self.assertIn("devices.json declares brain Projects/elsewhere", r.stdout, r.stdout + r.stderr)
            next(d for d in dev["devices"] if d["id"] == "work-mbp").update(
                home=str(self.home), brain=os.path.relpath(self.ws, self.home))
            (self.ws / "02-shared-references" / "devices.json").write_text(json.dumps(dev), encoding="utf-8")
            r = self.doctor("--check")
            self.assertNotIn("devices.json declares", r.stdout, r.stdout + r.stderr)

        def test_pointer_takes_the_on_disk_spelling(self):
            """T10 rerun L-05: on a case-insensitive volume the pointer keeps the on-disk spelling."""
            real = os.path.realpath(self.ws)
            if not os.path.isdir(real.upper()) or real.upper() == real:
                self.skipTest("case-sensitive volume: another spelling is another path")
            (self.home / ".claude" / "workspace-brain-path").write_text(real.upper() + "\n")
            r = self.doctor("--quick")
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertEqual((self.home / ".claude" / "workspace-brain-path").read_text().strip(), real)

        def test_current_overlay_is_not_reported_outdated(self):
            frag = merge_settings.expand_env_home(json.loads(
                (self.ws / "00-bootstrap/dist/settings-user-fragment.json").read_text()), self.home)
            (self.home / ".claude/settings.json").write_text(json.dumps({"env": frag["env"]}, indent=2) + "\n")
            r = self.doctor()
            self.assertNotIn("outdated Claude identity overlay", r.stdout + r.stderr)
            self.assertNotIn("missing the Claude identity env overlay", r.stdout + r.stderr)

        def test_quick_never_runs_installers(self):
            r = self.doctor("--quick", "--install-plugin")
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assert_report_unchanged()
            self.assertFalse((self.home / ".config/snds-workspace/control").exists())
            self.assertIn("installers never run under --quick", r.stdout)

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    for cls in (TestInstaller, TestOverlayReplace, TestDoctorModes):
        suite.addTests(loader.loadTestsFromTestCase(cls))
    res = unittest.TextTestRunner(verbosity=1).run(suite)
    return 0 if res.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
