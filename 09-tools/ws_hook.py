#!/usr/bin/env python3
"""ws_hook.py — neutral hook core for every host (H19).

One entry behind the byte-stable wrappers `00-bootstrap/dist/ws-hook` and `ws`. The installed
copy runs from the pinned lib (`~/.config/snds-workspace/lib/current/09-tools/ws_hook.py`) and
imports its sibling `profile_resolve.py`; tables resolve relative to that copy.

  ws_hook.py --host HOST --event EVENT [--probe] [--budget SECONDS]   stdin: host payload JSON
  ws_hook.py --host git --floor claude [GIT_HOOK_ARGS...]             stdin: pre-push ref lines
  ws_hook.py lane EVENT [GIT_HOOK_ARGS...]                            the H18/H11 git lanes (git_lanes.py)
  ws_hook.py host --skip-any H[,H...]                                 stdin: payload JSON (optional)
  ws_hook.py host --skip-unless H[,H...]                              stdin: payload JSON (optional)
  ws_hook.py host --skip-unless-layer LAYER                           stdin: payload JSON (optional)
  ws_hook.py env-file --host claude-code                              stdin: SessionStart payload JSON
  ws_hook.py sweep --host H [--budget SECONDS]                       stdin: session-start payload JSON
  ws_hook.py probe-env --host H [--via terminal|run_in_terminal] [--record]
  ws_hook.py probe-promote --host H [--device D]
  ws_hook.py --self-test
  ws_hook.py --self-test-shell

Hook paths fail open: a missing module or table, an exception or a timeout gives no decision
(exit 0, no stdout). `--event user-prompt` routes through the vault's 09-tools/prompt_route.py
(the one matcher, run as a subprocess from the root the pointer names; H7), rendered in the
host dialect. Event paths are exercised by fixtures until a registration runs them live. `host --skip-any` exits 3 only on verified evidence that the
acting host is in the set, 0 when a verified host is outside it, 2 otherwise. `host --skip-unless`
is its complement: 3 only on verified evidence that the acting host is outside the set, 0 when a
verified host is in it, 2 otherwise (an empty set is a usage error, 2). `host --skip-unless-layer
LAYER` is `--skip-unless` with the set read from surfaces.json: the `loaded_by` of that layer. An
unknown layer, a layer with no hosts or a missing table gives 2. The boot shim uses it with
`claude-project`, so the hosts it defers for are exactly the table's.

`env-file` (D-W1-4) delivers the Claude overlay through Claude Code's session env file: it copies
the validated exports of the installed ~/.config/snds-workspace/claude-overlay.env into the file
named by CLAUDE_ENV_FILE, as one delimited block. It never prints and always exits 0.

H23: `--event post-tool` appends the tool call's touches (repo root, repo-relative path or null
for a shell command, tool, ts, host) to ~/.config/snds-workspace/telemetry/sessions/<sid>.touched
without importing profile_resolve; it never prints. `sweep` (and the session-start event) runs the
pinned sibling closure.py sweeper within its budget: a dead session's mechanical workspace
leftovers are committed, substantive ones become a card notice. Both fail open.

Stdlib only; Python 3.9+.
"""

from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import getpass
import hashlib
import importlib.util
import io
import json
import os
import re
import shlex
import shutil
import socket
import stat
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path
from typing import Optional

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
EVENTS = ("session-start", "user-prompt", "pre-tool", "post-tool", "stop", "subagent-stop",
          "pre-compact", "session-end")
REDACT_RE = re.compile(r"^[A-Za-z0-9_.:+ ()-]{0,80}$")
# WS_OVERLAY_CHANNEL is set only by the env-file channel (D-W1-4), so a probe record shows which
# channel delivered the Claude overlay to that shell.
ENV_PRESENCE_KEYS = ("WS_CLAUDE_OVERLAY", "WS_SURFACE_FAMILY", "GIT_CONFIG_COUNT", "GH_CONFIG_DIR",
                     "CLAUDE_ENV_FILE", "WS_OVERLAY_CHANNEL")
PROBES_REL = "02-shared-references/probes"
PAYLOAD_FIXTURES_REL = "09-tools/fixtures/ws_hook/payloads"
BASELINE_FIXTURES_REL = "09-tools/fixtures/ws_hook/baseline-2ff02e7"
CLAIM_MAX_AGE_S = 14 * 86400
DEFAULT_BUDGET_S = 10.0
FLOOR_BUDGET_S = 10.0
GIT_TIMEOUT_S = 4
SWEEP_BUDGET_S = 4.0     # H23: the session-start sweeper's share of the start budget
# Wave 0: only the Claude dispatcher writes the session baseline (T5 wiring). Wave 1 decides
# whether the hook core writes it too, once the path is registered live.
BASELINE_IN_HOOK = False
SESSION_KEYS = ("session_id", "sessionId", "conversation_id")
TURN_KEYS = ("turn_id", "turnId", "prompt_id", "promptId", "generation_id", "generationId")
PROMPT_KEYS = ("prompt", "userPrompt")
BASELINE_SCRIPTS = {
    "workspace-sessionstart.sh": "84a0fd39a8023e892f17377a552a76c2e94e7dcb0417784483944d567b0d4c78",
    "workspace-reassert.sh": "0b26ed2a02aea604d04815da7105702722be009bd753df683f53df3dbbfe20f0",
    "workspace-audit.sh": "b2f739f668b492ed7787488d957970c771296d2bb7e2d301e051be8b9f2c13e6",
}
BASELINE_REV = "2ff02e7"

_PR = None          # test seam: a stand-in profile_resolve module
_UNSET_TABLE = object()


# --------------------------------------------------------------------------- imports + tables

IMPORT_BUDGET_S = 3.0
_PR_CACHE: dict = {}


def _import_budget() -> float:
    try:
        return max(0.2, float(os.environ.get("WS_HOOK_IMPORT_BUDGET", IMPORT_BUDGET_S)))
    except ValueError:
        return IMPORT_BUDGET_S


def _profile_resolve():
    """The sibling profile_resolve module, or None (callers then give no decision).

    Hook paths fail open: any failure at import (SyntaxError, RuntimeError, SystemExit, ...) and an
    import that outlasts the import budget both give None, once per process."""
    if _PR is not None:
        return _PR
    if "mod" in _PR_CACHE:
        return _PR_CACHE["mod"]
    box = {}

    def imp():
        try:
            if str(TOOLS) not in sys.path:
                sys.path.insert(0, str(TOOLS))
            import profile_resolve
            box["m"] = profile_resolve
        except BaseException:  # noqa: BLE001 - a broken pinned module must never block a host
            sys.modules.pop("profile_resolve", None)

    th = threading.Thread(target=imp, daemon=True)
    th.start()
    th.join(_import_budget())
    mod = None if th.is_alive() else box.get("m")
    _PR_CACHE["mod"] = mod
    return mod


def _surfaces():
    pr = _profile_resolve()
    if pr is None:
        return None
    try:
        t = pr.load_table("surfaces")
    except Exception:
        return None
    return t if isinstance(t, dict) else None


def _row(t, host):
    for s in (t or {}).get("surfaces") or []:
        if s.get("id") == host:
            return s
    return None


def _ws_paths(home=None):
    pr = _profile_resolve()
    if pr is None:
        return None
    try:
        return pr.ws_paths(home=home)
    except Exception:
        return None


def _telemetry(home=None):
    paths = _ws_paths(home)
    if not paths:
        return None
    tele = Path(paths["telemetry"])
    return tele if tele.is_dir() else None


def _safe(value) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]", "_", str(value))[:80]


# --------------------------------------------------------------------------- payload adapters

def payload_host_hint(payload: dict, *, table=None) -> Optional[str]:
    """Surface id whose declared payload keys are present (rank-1 evidence), else None."""
    if not isinstance(payload, dict) or not payload:
        return None
    t = table if table is not None else _surfaces()
    if not t:
        return None
    hits = []
    for s in t.get("surfaces") or []:
        for m in (s.get("markers") or {}).get("payload_keys_any") or []:
            key = m.get("key")
            if key not in payload:
                continue
            needle = m.get("contains")
            if needle is not None and needle not in str(payload.get(key) or ""):
                continue
            if s["id"] not in hits:
                hits.append(s["id"])
            break
    return hits[0] if len(hits) == 1 else None


def _event_id(raw: str, t) -> Optional[str]:
    if not raw:
        return None
    for fmt in ((t or {}).get("formats") or {}).values():
        for neutral, name in fmt.items():
            if name == raw:
                return neutral
    return raw if raw in EVENTS else None


def normalize(payload: dict, host: str, *, table=None) -> dict:
    p = payload if isinstance(payload, dict) else {}
    t = table if table is not None else _surfaces()
    event = _event_id(str(p.get("hook_event_name") or p.get("hookEventName") or ""), t)
    session = next((str(p[k]) for k in SESSION_KEYS if p.get(k)), "")
    turn = next((str(p[k]) for k in TURN_KEYS if p.get(k)), "")
    if not turn:
        prompt = next((str(p[k]) for k in PROMPT_KEYS if p.get(k)), "")
        if event == "user-prompt" and prompt:
            turn = hashlib.sha1(prompt.encode("utf-8")).hexdigest()[:12]
        elif event == "session-start":
            turn = "0"
    cwd = p.get("cwd") or ""
    if not cwd and isinstance(p.get("workspace_roots"), list) and p["workspace_roots"]:
        cwd = p["workspace_roots"][0]
    source = p.get("source") or ("startup" if event == "session-start" else "")
    return {"host": host, "event": event, "session": session, "turn": turn, "cwd": str(cwd),
            "source": str(source)}


# --------------------------------------------------------------------------- dialects

def render(dialect: str, event: str, text: str, *, table=None) -> str:
    """Context text in the host's dialect; nothing for an unverified or unknown dialect."""
    t = table if table is not None else _surfaces()
    d = ((t or {}).get("dialects") or {}).get(dialect)
    if not d or not d.get("verified") or not text:
        return ""
    ctx = d.get("context")
    if ctx == "hookSpecificOutput":
        name = (((t or {}).get("formats") or {}).get("claude-settings") or {}).get(event)
        if event not in ("session-start", "user-prompt") or not name:
            return ""
        return json.dumps({"hookSpecificOutput": {"hookEventName": name, "additionalContext": text}},
                          ensure_ascii=False)
    if ctx == "additional_context":
        if event != "session-start":
            return "{}"
        return json.dumps({"additional_context": text}, ensure_ascii=False)
    if ctx == "plain":
        return text
    return ""


def noop(dialect: str, *, table=None) -> str:
    t = table if table is not None else _surfaces()
    d = ((t or {}).get("dialects") or {}).get(dialect)
    return (d or {}).get("noop", "") if d else ""


# --------------------------------------------------------------------------- claims

def claim(session, event, turn, *, host, home=None) -> bool:
    """Atomic first-writer claim. False means a duplicate; True means proceed."""
    tele = _telemetry(home)
    if tele is None or not session:
        return True
    base = tele / "claims"
    key = f"{_safe(session)}.{_safe(event)}.{_safe(turn or '0')}"
    try:
        base.mkdir(exist_ok=True)
        (base / key).mkdir()
    except FileExistsError:
        return False
    except OSError:
        return True
    try:
        (base / key / "host").write_text(f"{host}\n", encoding="utf-8")
    except OSError:
        pass
    return True


def prune_claims(*, home=None, now=None) -> int:
    tele = _telemetry(home)
    if tele is None or not (tele / "claims").is_dir():
        return 0
    cutoff = (now if now is not None else time.time()) - CLAIM_MAX_AGE_S
    removed = 0
    for d in (tele / "claims").iterdir():
        try:
            if d.is_dir() and d.stat().st_mtime < cutoff:
                shutil.rmtree(d)
                removed += 1
        except OSError:
            continue
    return removed


# --------------------------------------------------------------------------- baseline

def _git(root: Path, *args) -> Optional[str]:
    try:
        r = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True,
                           timeout=GIT_TIMEOUT_S)
    except (OSError, subprocess.SubprocessError):
        return None
    return r.stdout if r.returncode == 0 else None


def _looks_like_workspace(root: Path) -> bool:
    pr = _profile_resolve()
    if pr is not None and hasattr(pr, "is_workspace_checkout"):
        try:
            return bool(pr.is_workspace_checkout(root))
        except Exception:
            return False
    return ((root / "AGENTS.md").is_file() and (root / ".git").exists()
            and (root / "02-shared-references" / "surfaces.json").is_file())


def parse_porcelain_z(text: str) -> list:
    tokens = text.split("\0")
    out, i = [], 0
    while i < len(tokens):
        tok = tokens[i]
        i += 1
        if len(tok) < 4:
            continue
        xy, path, orig = tok[:2], tok[3:], None
        if "R" in xy or "C" in xy:
            orig = tokens[i] if i < len(tokens) else None
            i += 1
        out.append({"xy": xy, "path": path, "orig": orig})
    return out


def write_baseline(payload: dict, root: Path, *, now=None) -> Optional[Path]:
    """Write .workspace/state/sessions/<sid>.json, only when root is the workspace."""
    try:
        root = Path(root)
        if not _looks_like_workspace(root):
            return None
        t = _surfaces()
        hint = payload_host_hint(payload, table=t)
        sid = _safe(normalize(payload, hint or "unknown", table=t)["session"])
        if not sid:
            return None
        head = (_git(root, "rev-parse", "HEAD") or "").strip() or None
        porcelain = parse_porcelain_z(_git(root, "status", "--porcelain=v1", "-z") or "")
        row = _row(t, hint) if hint else None
        stamp = (now or dt.datetime.now(dt.timezone.utc)).strftime("%Y-%m-%dT%H:%M:%SZ")
        rec = {"schema_version": 1, "sid": sid, "host": hint or "unknown",
               "family": (row or {}).get("family", "unknown"), "via": "payload" if hint else "none",
               "head": head, "porcelain": porcelain, "ts": stamp}
        out = root / ".workspace" / "state" / "sessions" / f"{sid}.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        tmp = out.with_name(out.name + ".tmp")
        tmp.write_text(json.dumps(rec, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        os.replace(tmp, out)
        return out
    except Exception:
        return None


# --------------------------------------------------------------------------- H23: the touch ledger

# telemetry/sessions/<sid>.touched, one JSON line per touch: {repo, path, tool, ts, host}. `path` is
# repo-relative for an edit and null for a shell command (closure falls back to git status there).
# The write path never imports profile_resolve and never prints: it runs after every tool call.
LEDGER_DIR = "sessions"
LEDGER_SUFFIX = ".touched"
LEDGER_BUDGET_S = 0.05
LEDGER_EDIT_TOOLS = ("Edit", "Write", "MultiEdit", "NotebookEdit", "Update")
LEDGER_SHELL_TOOLS = ("Bash", "Shell", "run_terminal_cmd")
LEDGER_PATH_KEYS = ("file_path", "notebook_path", "path")
_PATCH_RE = re.compile(r"^\*\*\* (?:Add File|Update File|Delete File|Move to): (.+)$")


def _home_base(home=None) -> Path:
    return (Path(home) if home is not None else Path.home()) / ".config" / "snds-workspace"


def ledger_path(sid: str, *, home=None) -> Path:
    return _home_base(home) / "telemetry" / LEDGER_DIR / f"{_safe(sid)}{LEDGER_SUFFIX}"


def _jsonish(v):
    if isinstance(v, str) and v.strip()[:1] == "{":
        try:
            return json.loads(v)
        except ValueError:
            return v
    return v


def _repo_top(p: Path) -> Optional[Path]:
    cur = p
    for _ in range(64):
        try:
            if (cur / ".git").exists():
                return cur
        except OSError:
            return None
        if cur.parent == cur:
            return None
        cur = cur.parent
    return None


def touch_records(payload: dict, host: str, *, now=None) -> list:
    """Ledger lines for one post-tool payload (Claude PostToolUse, Cursor afterFileEdit and
    afterShellExecution, Codex PostToolUse on Bash and apply_patch). [] for anything else."""
    p = payload if isinstance(payload, dict) else {}
    event = str(p.get("hook_event_name") or p.get("hookEventName") or "")
    tool = str(p.get("tool_name") or p.get("toolName") or "")
    tin = _jsonish(p.get("tool_input") if "tool_input" in p else p.get("toolInput"))
    tin = tin if isinstance(tin, dict) else {}
    cwd = p.get("cwd") or ""
    if not cwd and isinstance(p.get("workspace_roots"), list) and p["workspace_roots"]:
        cwd = p["workspace_roots"][0]
    paths, shell = [], False
    if event == "afterFileEdit":
        tool, paths = "Write", [p.get("file_path")]
    elif event == "afterShellExecution":
        tool, shell = "Shell", True
    elif tool in LEDGER_EDIT_TOOLS:
        paths = [next((tin[k] for k in LEDGER_PATH_KEYS if isinstance(tin.get(k), str) and tin[k]), None)]
    elif tool == "apply_patch":
        text = next((tin[k] for k in ("input", "patch", "command") if isinstance(tin.get(k), str)), "")
        paths = [m.group(1).strip() for m in (_PATCH_RE.match(ln.strip()) for ln in text.splitlines()) if m]
    elif tool in LEDGER_SHELL_TOOLS:
        shell = True
        wd = tin.get("workdir") or tin.get("cwd")
        cwd = wd if isinstance(wd, str) and wd else cwd
    else:
        return []
    base = Path(str(cwd)).expanduser() if cwd else None
    stamp = (now or dt.datetime.now(dt.timezone.utc)).strftime("%Y-%m-%dT%H:%M:%SZ")
    out = []
    if shell:
        top = _repo_top(base.resolve()) if base is not None and base.is_absolute() else None
        if top is not None:
            out.append({"repo": str(top), "path": None, "tool": tool, "ts": stamp, "host": host})
        return out
    for raw in dict.fromkeys(x for x in paths if isinstance(x, str) and x):
        f = Path(raw).expanduser()
        if not f.is_absolute():
            if base is None or not base.is_absolute():
                continue
            f = base / f
        f = Path(os.path.abspath(f))
        top = _repo_top(f.parent)
        if top is None:
            continue
        try:
            rel = f.relative_to(top).as_posix()
        except ValueError:
            continue
        out.append({"repo": str(top), "path": rel, "tool": tool, "ts": stamp, "host": host})
    return out


def _payload_table():
    """surfaces.json read directly (no profile_resolve import on the post-tool path)."""
    try:
        return json.loads((ROOT / "02-shared-references" / "surfaces.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def record_touch(host_arg: str, payload: dict, *, home=None, now=None) -> int:
    """Append this tool call's touches to the session ledger. Fails open, never prints, 0 always.

    Host filter: a payload that names another host (Cursor running the Claude user hooks) is left
    to that host's own registration. Nothing is written until telemetry/ exists (a human installs)."""
    try:
        p = payload if isinstance(payload, dict) else {}
        sid = next((str(p[k]) for k in SESSION_KEYS if p.get(k)), "")
        tele = _home_base(home) / "telemetry"
        if not sid or not tele.is_dir():
            return 0
        hint = payload_host_hint(p, table=_payload_table())
        if host_arg != "auto" and hint and hint != host_arg:
            return 0
        host = host_arg if host_arg != "auto" else (hint or "unknown")
        recs = touch_records(p, host, now=now)
        if not recs:
            return 0
        target = tele / LEDGER_DIR / f"{_safe(sid)}{LEDGER_SUFFIX}"
        target.parent.mkdir(exist_ok=True)
        data = "".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in recs).encode("utf-8")
        fd = os.open(str(target), os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o600)
        try:
            os.write(fd, data)
        finally:
            os.close(fd)
        return 0
    except Exception:
        return 0


def read_ledger(sid: str, *, home=None) -> list:
    try:
        text = ledger_path(sid, home=home).read_text(encoding="utf-8")
    except OSError:
        return []
    out = []
    for ln in text.splitlines():
        try:
            rec = json.loads(ln)
        except ValueError:
            continue
        if isinstance(rec, dict) and isinstance(rec.get("repo"), str):
            out.append(rec)
    return out


def run_sweep(host_arg: str, payload: dict, *, home=None, budget=None) -> int:
    """H23 sweeper at session start: the pinned sibling closure.py commits a dead session's
    mechanical workspace leftovers and records card notices. Budget-limited; fails open; silent."""
    p = payload if isinstance(payload, dict) else {}
    limit = max(0.2, float(budget)) if budget is not None else SWEEP_BUDGET_S

    def go():
        if str(TOOLS) not in sys.path:
            sys.path.insert(0, str(TOOLS))
        import closure  # noqa: PLC0415 - pinned sibling; absent in an older pin (then no sweep)
        sid = next((str(p[k]) for k in SESSION_KEYS if p.get(k)), "")
        closure.sweep(home=home, current_sid=sid, host=host_arg, budget=limit)

    _run_optional([go], limit)
    return 0


# --------------------------------------------------------------------------- detection glue

def _detect(hint=None, *, env=None) -> dict:
    pr = _profile_resolve()
    if pr is None:
        return {"acting_host": "unknown", "family_for_walls": "unknown", "via": "none",
                "verified": False, "determined": False, "conflict": False}
    try:
        det = pr.detect_surface(hint, env=env) if env is not None else pr.detect_surface(hint)
    except Exception:
        return {"acting_host": "unknown", "family_for_walls": "unknown", "via": "none",
                "verified": False, "determined": False, "conflict": False}
    return det if isinstance(det, dict) else {}


def layer_hosts(layer_id, *, table=_UNSET_TABLE) -> set:
    """The hosts that load a layer (its `loaded_by` in surfaces.json); empty when the table or the
    layer is missing."""
    t = _surfaces() if table is _UNSET_TABLE else table
    for lay in (t or {}).get("layers") or []:
        if isinstance(lay, dict) and lay.get("id") == layer_id:
            return {h for h in lay.get("loaded_by") or [] if isinstance(h, str) and h}
    return set()


def host_skip_any(hosts, payload, *, env=None, unless=False) -> int:
    """Exit code for `host --skip-any` (unless=False) or `host --skip-unless` (unless=True).

    3 on verified evidence that the acting host is in the set (unless: outside it), 0 on verified
    evidence of the opposite, 2 when no host is verified."""
    try:
        if unless and not hosts:
            return 2
        t = _surfaces()
        hint = payload_host_hint(payload, table=t) if (payload and t) else None
        if hint:
            acting = hint
        else:
            if _profile_resolve() is None:
                return 2
            det = _detect(None, env=env)
            if not det.get("determined") or not det.get("verified"):
                return 2
            acting = det.get("acting_host")
        if unless and (not acting or acting == "unknown"):
            return 2
        return 3 if (acting in hosts) != unless else 0
    except Exception:
        return 2


# --------------------------------------------------------------------------- probes

def _hostnames() -> list:
    names = set()
    try:
        full = socket.gethostname()
        names.update({full, full.split(".")[0]})
    except OSError:
        pass
    return [n for n in names if len(n) >= 4]


def _users() -> list:
    names = set()
    try:
        names.add(getpass.getuser())
    except Exception:
        pass
    home = os.path.basename(os.path.expanduser("~"))
    if home:
        names.add(home)
    return [n for n in names if len(n) >= 3]


def validate_record(rec, *, allow_env_values=(), hostnames=None, users=None) -> list:
    """Every string value matches the redaction regex; no host, user, path or foreign env value."""
    hostnames = _hostnames() if hostnames is None else hostnames
    users = _users() if users is None else users
    problems = []

    def walk(v, where):
        if isinstance(v, dict):
            for k, x in v.items():
                walk(k, f"{where}.<key>")
                walk(x, f"{where}.{k}")
        elif isinstance(v, list):
            for i, x in enumerate(v):
                walk(x, f"{where}[{i}]")
        elif isinstance(v, str):
            if not REDACT_RE.match(v):
                problems.append(f"{where}: value fails the redaction pattern")
                return
            low = v.lower()
            for h in hostnames:
                if h.lower() in low:
                    problems.append(f"{where}: value names this host")
            for u in users:
                if u.lower() in low:
                    problems.append(f"{where}: value names a user")

    walk(rec, "record")
    for section in (rec.get("env_probe") or {}, rec):
        values = section.get("env_values") if isinstance(section, dict) else None
        for k in (values or {}):
            if k not in allow_env_values:
                problems.append(f"env_values.{k}: not in probe_env_value_allowlist")
    return problems


def _redact(v):
    if isinstance(v, dict):
        return {k: _redact(x) for k, x in v.items() if isinstance(k, str) and REDACT_RE.match(k)}
    if isinstance(v, list):
        return [_redact(x) for x in v]
    if isinstance(v, str) and not REDACT_RE.match(v):
        return "redacted"
    return v


def _git_version() -> Optional[str]:
    try:
        r = subprocess.run(["git", "--version"], capture_output=True, text=True, timeout=GIT_TIMEOUT_S)
    except (OSError, subprocess.SubprocessError):
        return None
    m = re.search(r"(\d+\.\d+(?:\.\d+)?)", r.stdout or "")
    return m.group(1) if m else None


def _device_id() -> str:
    pr = _profile_resolve()
    try:
        return str(pr.current_device()["id"]) if pr is not None else "unknown"
    except Exception:
        return "unknown"


def _ancestry() -> list:
    pr = _profile_resolve()
    try:
        return [str(a.get("comm", "")) for a in pr.walk_ancestry()] if pr is not None else []
    except Exception:
        return []


def probe_record(kind, declared, event, payload, t, *, env=None, via=None, now=None) -> dict:
    env = dict(os.environ if env is None else env)
    hint = payload_host_hint(payload, table=t) if payload else None
    det = _detect(hint, env=env)
    prefixes = tuple((t or {}).get("probe_env_name_prefixes") or ())
    allow = list((t or {}).get("probe_env_value_allowlist") or ())
    stamp = (now or dt.datetime.now(dt.timezone.utc))
    rec = {
        "schema_version": 1, "kind": kind, "declared_host": declared, "event": event,
        "recorded_at": stamp.strftime("%Y-%m-%d"), "ts": stamp.strftime("%Y%m%dT%H%M%SZ"),
        "device": _device_id(),
        "payload_keys": sorted(k for k in (payload or {}) if isinstance(k, str)),
        "via": via,
        "env_marker_names": sorted(k for k in env if prefixes and k.startswith(prefixes)),
        "env_values": {k: env[k] for k in allow if k in env},
        "env_presence": {k: (k in env) for k in ENV_PRESENCE_KEYS},
        "ancestry_comm": _ancestry(),
        "detected": {k: det.get(k) for k in ("acting_host", "family_for_walls", "via", "verified", "conflict")},
        "git_version": _git_version(),
    }
    rec = _redact(rec)
    bad = validate_record(rec, allow_env_values=allow)
    if bad:
        # Scrub any value that names this host or user; never write it.
        hosts, users = _hostnames(), _users()

        def scrub(v):
            if isinstance(v, dict):
                return {k: scrub(x) for k, x in v.items()}
            if isinstance(v, list):
                return [scrub(x) for x in v]
            if isinstance(v, str) and any(n.lower() in v.lower() for n in hosts + users):
                return "redacted"
            return v
        rec = scrub(rec)
    return rec


def _write_probe_record(rec: dict, *, home=None) -> Optional[Path]:
    tele = _telemetry(home)
    if tele is None:
        return None
    try:
        d = tele / "probes"
        d.mkdir(exist_ok=True)
        fd, name = tempfile.mkstemp(prefix=f"{rec.get('ts', 'x')}-", suffix=".json", dir=str(d))
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, indent=2, ensure_ascii=False) + "\n")
        return Path(name)
    except OSError:
        return None


def _via_key(via) -> str:
    return str(via) if via else "agent-shell"


def _tracked_probe(host: str, device: str, existing: dict, hook_recs: list, env_rec, today: str) -> dict:
    hp = existing.get("hook_probe") or {"status": "not-installed", "events": {}}
    hp = {"status": hp.get("status", "not-installed"), "events": dict(hp.get("events") or {})}
    envp = existing.get("env_probe") or {"via": None, "env_marker_names": [], "env_values": {}, "env_presence": {}}
    ancestry = existing.get("ancestry_comm") or []
    detected = existing.get("detected") or {}
    mismatch = bool(existing.get("detection_mismatch"))
    git_version = existing.get("git_version")
    for rec in sorted(hook_recs, key=lambda r: r.get("ts", "")):
        hp["events"][rec.get("event") or "unknown"] = {
            "payload_keys": rec.get("payload_keys") or [],
            "env_marker_names": rec.get("env_marker_names") or [],
            "env_presence": rec.get("env_presence") or {}}
        hp["status"] = "recorded"
        ancestry = rec.get("ancestry_comm") or ancestry
        detected = rec.get("detected") or detected
        git_version = rec.get("git_version") or git_version
        mismatch = mismatch or (detected.get("acting_host") != host)
    # One env probe per `via` (terminal, run_in_terminal, agent shell): a later run of one kind must not
    # overwrite another kind's evidence. `env_probe` stays the latest, for readers of the older shape.
    probes = dict(existing.get("env_probes") or {})
    if not probes and existing.get("env_probe") and (existing["env_probe"].get("env_marker_names")
                                                    or existing["env_probe"].get("env_presence")):
        probes[_via_key(existing["env_probe"].get("via"))] = existing["env_probe"]
    if env_rec:
        envp = {"via": env_rec.get("via"), "env_marker_names": env_rec.get("env_marker_names") or [],
                "env_values": env_rec.get("env_values") or {}, "env_presence": env_rec.get("env_presence") or {}}
        probes[_via_key(env_rec.get("via"))] = envp
        # Payload-derived detection outranks env detection: an env-only run keeps a recorded hook probe's.
        if not hook_recs and hp["status"] != "recorded":
            ancestry = env_rec.get("ancestry_comm") or ancestry
            detected = env_rec.get("detected") or detected
            mismatch = mismatch or ((env_rec.get("detected") or {}).get("acting_host") != host)
        git_version = env_rec.get("git_version") or git_version
    return {"schema_version": 1, "surface": host, "device": device, "recorded_at": today,
            "declared_host": host, "hook_probe": hp, "env_probe": envp, "env_probes": probes, "ancestry_comm": ancestry,
            "detected": detected, "detection_mismatch": mismatch, "git_version": git_version}


def _vault_root(home=None, root=None) -> Optional[Path]:
    if root is not None:
        return Path(root)
    paths = _ws_paths(home)
    if not paths:
        return None
    try:
        text = Path(paths["root_file"]).read_text(encoding="utf-8").strip()
    except OSError:
        return None
    return Path(text) if text else None


def _write_tracked(root: Path, host: str, device: str, rec: dict) -> Path:
    out = root / PROBES_REL / f"{_safe(host)}@{_safe(device)}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_name(out.name + ".tmp")
    tmp.write_text(json.dumps(rec, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(tmp, out)
    return out


def _load_existing(root: Path, host: str, device: str) -> dict:
    path = root / PROBES_REL / f"{_safe(host)}@{_safe(device)}.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def probe_env(host, *, via=None, record=False, home=None, root=None, env=None, out=None) -> int:
    out = out or sys.stdout
    t = _surfaces()
    if t is None:
        print("ws_hook: surfaces table unavailable (profile_resolve missing?)", file=sys.stderr)
        return 2
    rec = probe_record("env", host, None, {}, t, env=env, via=via)
    print(json.dumps(rec, indent=2, ensure_ascii=False), file=out)
    if not record:
        return 0
    vroot = _vault_root(home, root)
    if vroot is None:
        print("ws_hook: no workspace root pointer; nothing recorded", file=sys.stderr)
        return 3
    device = rec.get("device") or "unknown"
    today = rec.get("recorded_at")
    tracked = _tracked_probe(host, device, _load_existing(vroot, host, device), [], rec, today)
    bad = validate_record(tracked, allow_env_values=t.get("probe_env_value_allowlist") or [])
    if bad:
        for b in bad:
            print(f"REJECT {b}", file=sys.stderr)
        return 1
    print(f"wrote {_write_tracked(vroot, host, device, tracked)}", file=sys.stderr)
    return 0


def probe_promote(host, *, device=None, home=None, root=None) -> int:
    t = _surfaces()
    if t is None:
        print("ws_hook: surfaces table unavailable", file=sys.stderr)
        return 2
    tele = _telemetry(home)
    recs = []
    for f in sorted((tele / "probes").glob("*.json")) if tele and (tele / "probes").is_dir() else []:
        try:
            rec = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if not isinstance(rec, dict):
            continue
        det = (rec.get("detected") or {}).get("acting_host")
        if rec.get("declared_host") == host or det == host:
            recs.append(rec)
    if not recs:
        print(f"nothing to promote for {host}")
        return 3
    device = device or recs[-1].get("device") or _device_id()
    allow = t.get("probe_env_value_allowlist") or []
    bad = []
    for rec in recs:
        bad += validate_record(rec, allow_env_values=allow)
    hook_recs = [r for r in recs if r.get("kind") == "hook"]
    env_recs = sorted((r for r in recs if r.get("kind") == "env"), key=lambda r: r.get("ts", ""))
    vroot = _vault_root(home, root)
    if vroot is None:
        print("ws_hook: no workspace root pointer", file=sys.stderr)
        return 2
    today = dt.date.today().isoformat()
    tracked = _tracked_probe(host, device, _load_existing(vroot, host, device), hook_recs,
                             env_recs[-1] if env_recs else None, today)
    bad += validate_record(tracked, allow_env_values=allow)
    if bad:
        for b in sorted(set(bad)):
            print(f"REJECT {b}", file=sys.stderr)
        return 1
    print(f"wrote {_write_tracked(vroot, host, device, tracked)}")
    return 0


# --------------------------------------------------------------------------- events

def _budget(row, event, budget) -> float:
    if budget is not None:
        return max(0.2, float(budget))
    limit = ((row or {}).get("timeouts_s") or {}).get(event)
    return max(1.0, float(limit) - 3.0) if limit else DEFAULT_BUDGET_S


def _card(host, row, budget, home=None) -> Optional[str]:
    vroot = _vault_root(home)
    if vroot is None:
        return None
    script = vroot / "09-tools" / "session-status.py"
    if not script.is_file():
        return None
    label = (row or {}).get("label") or host
    try:
        r = subprocess.run([sys.executable, str(script), "--surface", label, "--via", f"ws-hook/{host}"],
                           capture_output=True, text=True, timeout=budget, cwd=str(vroot))
    except (OSError, subprocess.SubprocessError):
        return None
    text = (r.stdout or "").strip()
    return text or None


def _route(host, payload, budget, home=None) -> Optional[str]:
    """H7: the one matcher, run from the vault checkout (never a fork, never imported into
    the pinned process). The raw payload goes in on stdin; prompt_route applies the host
    adapter and is_user_turn (X2). Nothing on any failure."""
    vroot = _vault_root(home)
    if vroot is None:
        return None
    script = vroot / "09-tools" / "prompt_route.py"
    if not script.is_file():
        return None
    try:
        r = subprocess.run([sys.executable, str(script), "--stdin", "--payload", "--host", host,
                            "--brain", str(vroot)], input=json.dumps(payload), capture_output=True,
                           text=True, timeout=budget, cwd=str(vroot))
    except (OSError, subprocess.SubprocessError, TypeError, ValueError):
        return None
    text = (r.stdout or "").strip() if r.returncode == 0 else ""
    return text or None


def _route_event(host, row, dialect, payload, n, t, budget, home, out, start) -> int:
    if not host or not claim(n["session"], "user-prompt", n["turn"] or "0", host=host, home=home):
        return 0
    limit = _budget(row, "user-prompt", budget)
    text = _route(host, payload, max(0.2, limit - (time.monotonic() - start)), home)
    rendered = render(dialect, "user-prompt", text, table=t) if text else ""
    if rendered:
        out.write(rendered + "\n")
        out.flush()
    return 0


def _run_optional(steps, remaining: float) -> None:
    threads = []
    for step in steps:
        th = threading.Thread(target=_quiet(step), daemon=True)
        th.start()
        threads.append(th)
    deadline = time.monotonic() + max(0.0, remaining)
    for th in threads:
        th.join(max(0.0, deadline - time.monotonic()))


def _quiet(fn):
    def run():
        try:
            fn()
        except Exception:
            pass
    return run


def handle_event(host_arg, event, payload, *, probe=False, budget=None, home=None, env=None,
                 optional_steps=None, out=None) -> int:
    """0, or the guard's exit code on a pre-tool deny (Codex and Windsurf block with 2). Output only
    when there is a decision."""
    out = out or sys.stdout
    start = time.monotonic()
    if event == "pre-tool" and not probe:
        return run_guard(host_arg, payload, env=env, home=home, out=out)
    if event == "post-tool" and not probe:
        return record_touch(host_arg, payload, home=home)
    try:
        t = _surfaces()
        if t is None:
            return 0
        hint = payload_host_hint(payload, table=t)
        host = hint if host_arg == "auto" else host_arg
        if host_arg == "auto" and not host:
            det = _detect(None, env=env)
            host = det.get("acting_host") if det.get("determined") and det.get("verified") else None
        row = _row(t, host) if host else None
        dialect = (row or {}).get("dialect") or "none"
        n = normalize(payload, host or "unknown", table=t)
        if probe:
            if claim(f"probe-{n['session']}" if n["session"] else "", event, n["turn"] or "0",
                     host=host or "unknown", home=home):
                _write_probe_record(probe_record("hook", host_arg, event, payload, t, env=env), home=home)
            text = noop(dialect, table=t)
            if text:
                out.write(text + "\n")
            return 0
        if event == "user-prompt":
            return _route_event(host, row, dialect, payload, n, t, budget, home, out, start)
        if event == "stop":
            return stop_notice(host or "unknown", dialect, n, home=home, out=out)
        if event != "session-start":
            return 0            # other events observe only
        if not claim(n["session"], event, n["turn"] or "0", host=host or "unknown", home=home):
            return 0
        limit = _budget(row, event, budget)
        card = _card(host, row, max(0.2, limit - (time.monotonic() - start)), home) if host else None
        text = render(dialect, event, card, table=t) if card else ""
        if text:
            out.write(text + "\n")
            out.flush()
        steps = optional_steps if optional_steps is not None else [lambda: prune_claims(home=home)]
        if optional_steps is None and host:
            rest = max(0.2, limit - (time.monotonic() - start))
            steps.append(lambda: run_sweep(host, payload, home=home, budget=min(SWEEP_BUDGET_S, rest)))
        if BASELINE_IN_HOOK and optional_steps is None:
            steps.append(lambda: write_baseline(payload, Path(n["cwd"] or ".")))
        _run_optional(steps, limit - (time.monotonic() - start))
        return 0
    except Exception:
        return 0


def _git_lanes():
    """The sibling git_lanes.py in the pinned lib, or None (callers then allow / stay silent)."""
    try:
        spec = importlib.util.spec_from_file_location("ws_hook_git_lanes", TOOLS / "git_lanes.py")
        if spec is None or spec.loader is None:
            return None
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    except BaseException:  # noqa: BLE001 - a broken lane module never blocks git or a host
        return None


def _lane_main(argv, *, err=None) -> int:
    """`ws_hook.py lane EVENT [HOOK_ARGS...]`: the git lanes through the one pinned entry (W2-0 item 2).
    git_lanes' hook path decides (exit 1 blocks); a missing or broken module, or any error, allows."""
    err = err or sys.stderr
    gl = _git_lanes()
    if gl is None:
        print("ws-lanes: git_lanes.py unavailable in the pinned lib; allowing", file=err)
        return 0
    try:
        return 1 if gl.main(["hook", *argv[1:]]) == 1 else 0
    except KeyboardInterrupt:
        raise
    except BaseException as exc:  # noqa: BLE001
        print(f"ws-lanes: {exc.__class__.__name__} in the lane; allowing", file=err)
        return 0


def _workspace_top(cwd: str, home=None) -> Optional[Path]:
    """The work tree holding cwd when it is the workspace (or one of its worktrees), else None."""
    vroot = _vault_root(home)
    if not vroot or not cwd:
        return None
    try:
        r = subprocess.run(["git", "-C", cwd, "rev-parse", "--show-toplevel"], capture_output=True, text=True,
                           timeout=GIT_TIMEOUT_S)
    except (OSError, subprocess.SubprocessError):
        return None
    top = Path(r.stdout.strip()) if r.returncode == 0 and r.stdout.strip() else None
    if top is None or not (top / "AGENTS.md").is_file():
        return None
    real, base = os.path.realpath(top), os.path.realpath(vroot)
    return top if real == base or real.startswith(base + os.sep) else None


def stop_notice(host, dialect, n, *, home=None, out=None, err=None) -> int:
    """H11: a vendor stop hook is a notice-only accelerator. At most one line (the last-gate notice for
    the workspace checkout the session is in), once per session per notice. Never a Cursor
    followup_message, never a Codex continue or decision: Cursor gets its `{}` no-op on stdout, Codex
    nothing, and the line goes to stderr; Claude gets it as a systemMessage. Always 0."""
    out = out or sys.stdout
    err = err or sys.stderr
    line = None
    try:
        top = _workspace_top(n.get("cwd") or os.getcwd(), home)
        gl = _git_lanes() if top is not None else None
        line = gl.gate_notice(top) if gl is not None else None
        if line and not claim(n.get("session") or "", "stop-gate", hashlib.sha1(line.encode()).hexdigest()[:12],
                              host=host, home=home):
            line = None
    except Exception:  # noqa: BLE001 - a stop hook never fails the host
        line = None
    if dialect == "claude":
        if line:
            out.write(json.dumps({"systemMessage": f"ws-gate: {line}"}, ensure_ascii=False) + "\n")
        return 0
    text = noop(dialect)
    if text:
        out.write(text + "\n")
    if line:
        err.write(f"ws-gate: {line}\n")
    return 0


def run_guard(host_arg, payload, *, env=None, home=None, out=None, err=None) -> int:
    """Pre-tool: the H15 wall guard (the sibling wall_guard.py in the pinned lib). Fails open."""
    out = out or sys.stdout
    err = err or sys.stderr
    try:
        if str(TOOLS) not in sys.path:
            sys.path.insert(0, str(TOOLS))
        import wall_guard  # noqa: PLC0415
        rc, text, why, _dec = wall_guard.run_hook(host_arg, payload, env=env, home=home)
    except BaseException:  # noqa: BLE001 - a missing or broken guard never blocks a host
        return 0
    if text:
        out.write(text + "\n")
        out.flush()
    if why:
        err.write(why + "\n")
    return rc


def run_floor(hook_args, stdin_lines, *, budget=FLOOR_BUDGET_S, err=None) -> int:
    err = err or sys.stderr
    n = len(hook_args)
    event = "pre-push" if n == 2 else ("commit-msg" if n == 1 else "pre-commit")
    pr = _profile_resolve()
    fn = getattr(pr, "floor_decide", None) if pr is not None else None
    if fn is None:
        print("ws-claude-wall: floor unavailable (floor_decide not in the pinned lib); allowing", file=err)
        return 0
    box = {}

    def run():
        try:
            box["v"] = fn(event, list(hook_args), list(stdin_lines))
        except Exception as exc:
            box["e"] = exc

    th = threading.Thread(target=run, daemon=True)
    th.start()
    th.join(budget)
    if th.is_alive():
        print(f"ws-claude-wall: floor timed out after {budget:g}s; allowing", file=err)
        return 0
    if "e" in box:
        print(f"ws-claude-wall: floor error ({type(box['e']).__name__}); allowing", file=err)
        return 0
    v = box.get("v") if isinstance(box.get("v"), dict) else {}
    if v.get("decision") == "block":
        print(f"ws-claude-wall: blocked [{v.get('rule') or 'unknown'}] {v.get('reason') or ''}".rstrip(), file=err)
        return 1
    if v.get("notice"):
        print(f"ws-claude-wall: {v['notice']}", file=err)
    return 0


def _read_payload(stdin=None) -> dict:
    s = stdin or sys.stdin
    try:
        if s.isatty():
            return {}
        data = s.read()
    except (OSError, ValueError, AttributeError):
        return {}
    try:
        p = json.loads(data) if data and data.strip() else {}
    except ValueError:
        return {}
    return p if isinstance(p, dict) else {}


def _read_lines(stdin=None) -> list:
    s = stdin or sys.stdin
    try:
        if s.isatty():
            return []
        return [ln.rstrip("\n") for ln in s.read().splitlines() if ln.strip()]
    except (OSError, ValueError, AttributeError):
        return []


# --------------------------------------------------------------------------- D-W1-4: the overlay env file

# Claude Code hands SessionStart hooks a file in CLAUDE_ENV_FILE and prepends its contents to every
# Bash tool command of that session. Other hosts never set it, so the overlay stays Claude-only even
# where another host imports Claude's settings env. Only the Bash tool reads the file: hooks, MCP
# servers and the terminal panel never get the overlay (H17-R13), and a session whose SessionStart
# hooks did not run gets none (H17-R7; the SessionEnd audit logs NOOVERLAY for the doctor).
OVERLAY_ENV_NAME = "claude-overlay.env"            # under ws_paths()["base"]; --install-claude-overlay
OVERLAY_BEGIN = "# BEGIN snds-workspace overlay"
OVERLAY_END = "# END snds-workspace overlay"
OVERLAY_TELEMETRY = "overlay-env.jsonl"
OVERLAY_SOURCE_MAX = 256 * 1024
OVERLAY_NAME_RE = re.compile(r"^(?:WS_[A-Z0-9_]+|GH_CONFIG_DIR|GIT_CONFIG_COUNT|GIT_CONFIG_(?:KEY|VALUE)_[0-9]+)$")
OVERLAY_LINE_RE = re.compile(r"^export ([A-Z][A-Z0-9_]*)='((?:[^'\x00-\x1f\x7f]|'\\'')*)'$")
OVERLAY_SID_RE = re.compile(r"^[A-Za-z0-9_.-]{1,128}$")
HOME_BIND = 'H="$HOME";'           # merge_settings.HOME_BIND: the floor command binds its install home


class _EnvFileSkip(Exception):
    """The env-file step does nothing; the message is the telemetry reason."""


def _sq(value: str) -> str:
    return "'" + value.replace("'", "'\\''") + "'"


def parse_overlay_env(text: str) -> list:
    """[(name, value)] from the installed overlay file. Blank and `#` lines are skipped; every other
    line must be `export NAME='value'` with NAME an overlay name, once. Anything else refuses."""
    pairs, seen = [], set()
    for i, ln in enumerate(text.splitlines(), 1):
        if not ln.strip() or ln.startswith("#"):
            continue
        m = OVERLAY_LINE_RE.match(ln)
        if not m:
            raise _EnvFileSkip(f"installed overlay line {i} is not a strict export line")
        name = m.group(1)
        if not OVERLAY_NAME_RE.match(name):
            raise _EnvFileSkip(f"installed overlay line {i} names a non-overlay variable")
        if name in seen:
            raise _EnvFileSkip(f"installed overlay line {i} repeats a name")
        seen.add(name)
        pairs.append((name, m.group(2).replace("'\\''", "'")))
    if not pairs:
        raise _EnvFileSkip("installed overlay file has no export lines")
    return pairs


def _expand_home(value: str, home: Path) -> str:
    """As merge_settings.expand_env_home: `~/` becomes the home (gh does not expand it), and the
    floor command's `H="$HOME";` binds this home, so a caller's HOME= cannot re-route the wrapper."""
    h = str(home)
    if value.startswith("~/"):
        return os.path.join(h, value[2:])
    if value.startswith(HOME_BIND):
        return f"H={shlex.quote(h)};" + value[len(HOME_BIND):]
    return value


def overlay_block(pairs: list, home: Path) -> str:
    lines = [OVERLAY_BEGIN,
             "# Written by ws-hook env-file (snds-workspace, D-W1-4) at every SessionStart; do not edit."]
    lines += [f"export {n}={_sq(_expand_home(v, home))}" for n, v in pairs]
    lines.append(OVERLAY_END)
    return "\n".join(lines) + "\n"


def splice_overlay_block(current: str, block: str) -> str:
    """current with every block of ours removed and `block` appended, so our exports come last.
    Foreign lines are kept as they are. An unterminated block of ours refuses."""
    out, inside = [], False
    for ln in current.splitlines(keepends=True):
        s = ln.rstrip("\n")
        if not inside and s == OVERLAY_BEGIN:
            inside = True
            continue
        if inside:
            if s == OVERLAY_END:
                inside = False
            continue
        out.append(ln)
    if inside:
        raise _EnvFileSkip("unterminated overlay block in the session env file")
    text = "".join(out)
    if text and not text.endswith("\n"):
        text += "\n"
    return text + block


def _session_env_target(target: str, home: Path) -> Path:
    p = Path(target)
    if not p.is_absolute():
        raise _EnvFileSkip("CLAUDE_ENV_FILE is not an absolute path")
    try:
        base = (home / ".claude" / "session-env").resolve(strict=True)
        parent = p.parent.resolve(strict=True)
    except (OSError, RuntimeError):
        raise _EnvFileSkip("CLAUDE_ENV_FILE is not under ~/.claude/session-env") from None
    if parent != base and base not in parent.parents:
        raise _EnvFileSkip("CLAUDE_ENV_FILE is not under ~/.claude/session-env")
    if p.is_symlink() or (p.exists() and not p.is_file()):
        raise _EnvFileSkip("CLAUDE_ENV_FILE is not a regular file")
    return parent / p.name


def _read_overlay_source(src: Path) -> list:
    try:
        st = os.lstat(src)
    except OSError:
        raise _EnvFileSkip("overlay env file not installed") from None
    if not stat.S_ISREG(st.st_mode):
        raise _EnvFileSkip("installed overlay env file is not a regular file")
    if st.st_mode & 0o022:
        raise _EnvFileSkip("installed overlay env file is group- or world-writable")
    if hasattr(os, "getuid") and st.st_uid != os.getuid():
        raise _EnvFileSkip("installed overlay env file is owned by another user")
    if st.st_size > OVERLAY_SOURCE_MAX:
        raise _EnvFileSkip("installed overlay env file is too large")
    try:
        text = src.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        raise _EnvFileSkip("installed overlay env file is unreadable") from None
    return parse_overlay_env(text)


def _overlay_telemetry(home: Path, rec: dict) -> None:
    tele = _telemetry(home)
    if tele is None:
        return
    try:
        with open(tele / OVERLAY_TELEMETRY, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, separators=(",", ":")) + "\n")
    except OSError:
        pass


def env_file(host_arg, payload, *, env=None, home=None, table=_UNSET_TABLE) -> str:
    """Write the overlay block into CLAUDE_ENV_FILE: "written", "noop" or "error". Never raises and
    never prints. Acts only for --host claude-code, a claude-code payload, a CLAUDE_ENV_FILE under
    ~/.claude/session-env and an installed overlay file whose every line validates. On success it
    leaves ~/.claude/ws-state/overlay.<session_id>, which the SessionEnd audit looks for."""
    env = os.environ if env is None else env
    home = Path(home) if home is not None else Path.home()
    p = payload if isinstance(payload, dict) else {}
    sid = p.get("session_id")
    sid = sid if isinstance(sid, str) and OVERLAY_SID_RE.match(sid) else None
    status, reason, n = "noop", "", 0
    try:
        if host_arg != "claude-code":
            raise _EnvFileSkip("host is not claude-code")
        target = env.get("CLAUDE_ENV_FILE") or ""
        if not target:
            raise _EnvFileSkip("CLAUDE_ENV_FILE unset")
        tpath = _session_env_target(target, home)
        t = _surfaces() if table is _UNSET_TABLE else table
        if not t:
            raise _EnvFileSkip("surfaces table unavailable")
        if payload_host_hint(p, table=t) != "claude-code":
            raise _EnvFileSkip("payload is not a claude-code payload")
        paths = _ws_paths(home)
        if not paths:
            raise _EnvFileSkip("profile_resolve unavailable")
        pairs = _read_overlay_source(Path(paths["base"]) / OVERLAY_ENV_NAME)
        try:
            cur = tpath.read_text(encoding="utf-8") if tpath.exists() else ""
            mode = (tpath.stat().st_mode & 0o777) if tpath.exists() else 0o600
        except (OSError, UnicodeDecodeError):
            raise _EnvFileSkip("session env file unreadable") from None
        new = splice_overlay_block(cur, overlay_block(pairs, home))
        fd, tmp = tempfile.mkstemp(prefix=".ws-overlay-", dir=str(tpath.parent))
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                fh.write(new)
            os.chmod(tmp, mode)
            os.replace(tmp, tpath)
        except BaseException:
            try:
                os.unlink(tmp)
            except OSError:
                pass
            raise
        status, n = "written", len(pairs)
        if sid:
            state = home / ".claude" / "ws-state"
            state.mkdir(parents=True, exist_ok=True)
            stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            (state / f"overlay.{sid}").write_text(f"{stamp} env-file {n}\n", encoding="utf-8")
    except _EnvFileSkip as exc:
        reason = str(exc)
    except Exception as exc:  # noqa: BLE001 - fails open: the host session always starts
        status, reason = "error", exc.__class__.__name__
    try:
        src = p.get("source")
        _overlay_telemetry(home, {
            "schema_version": 1, "ts": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "event": "env-file", "host": _safe(host_arg), "result": status, "reason": reason or None,
            "session": sid, "source": _safe(src) if src else None, "exports": n})
    except Exception:  # noqa: BLE001
        pass
    return status


def _env_file_main(argv) -> int:
    """`env-file --host H`: exit 0 and nothing on stdout (SessionStart stdout becomes model context),
    whatever happens."""
    try:
        host = argv[2] if len(argv) == 3 and argv[1] == "--host" else None
        env_file(host, _read_payload())
    except BaseException:  # noqa: BLE001
        pass
    return 0


# --------------------------------------------------------------------------- self-test fakes

class _FakePR:
    """Stand-in for profile_resolve (T2) inside this task's self-test."""

    def __init__(self, home: Path, *, detect=None, floor=None, root=ROOT):
        self.home = Path(home)
        self._detect = detect or {"acting_host": "unknown", "determined": False, "verified": False,
                                  "via": "none", "family_for_walls": "unknown", "conflict": False}
        self.root = root
        if floor is not None:
            self.floor_decide = floor
        self.calls = []

    def load_table(self, name, *, root=None):
        return json.loads((Path(root or self.root) / "02-shared-references" / f"{name}.json").read_text(encoding="utf-8"))

    def ws_paths(self, *, home=None):
        base = Path(home or self.home) / ".config" / "snds-workspace"
        return {"base": base, "root_file": base / "root", "bin": base / "bin",
                "lib_current": base / "lib" / "current", "control": base / "control",
                "telemetry": base / "telemetry"}

    def detect_surface(self, payload_hint=None, *, env=None, ancestry=None, isatty=None, root=None):
        self.calls.append(("detect", payload_hint))
        if payload_hint:
            return {"acting_host": payload_hint, "determined": True, "verified": True, "via": "payload",
                    "family_for_walls": "fixture", "conflict": False}
        return dict(self._detect)

    def current_device(self, **kw):
        return {"id": "dev-a", "label": "fixture device"}

    def walk_ancestry(self, **kw):
        return [{"pid": 2, "ppid": 1, "comm": "zsh", "args": ""},
                {"pid": 1, "ppid": 0, "comm": "Cursor Helper (Plugin)", "args": ""}]


def _with_pr(fake):
    class _Ctx:
        def __enter__(self):
            global _PR
            self.prev = _PR
            _PR = fake
            return fake

        def __exit__(self, *exc):
            global _PR
            _PR = self.prev
            return False
    return _Ctx()


def _golden(surface: str, event: str) -> dict:
    return json.loads((ROOT / PAYLOAD_FIXTURES_REL / f"{surface}.{event}.json").read_text(encoding="utf-8"))


GOLDEN_SURFACES = ("claude-code", "cursor", "codex", "copilot-vscode")
FAKE_PR_SOURCE = '''
import json, os, time
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
MODE = os.environ.get("WS_FAKE_FLOOR", "absent")
def load_table(name, *, root=None):
    return json.loads((ROOT / "02-shared-references" / f"{name}.json").read_text(encoding="utf-8"))
def ws_paths(*, home=None):
    base = Path(home or os.path.expanduser("~")) / ".config" / "snds-workspace"
    return {"base": base, "root_file": base / "root", "bin": base / "bin", "lib_current": base / "lib" / "current",
            "control": base / "control", "telemetry": base / "telemetry"}
def detect_surface(payload_hint=None, **kw):
    return {"acting_host": payload_hint or "unknown", "determined": bool(payload_hint),
            "verified": bool(payload_hint), "via": "payload" if payload_hint else "none"}
def current_device(**kw):
    return {"id": "dev-a"}
def walk_ancestry(**kw):
    return []
if MODE != "absent":
    def floor_decide(event, hook_args, stdin_lines, **kw):
        if MODE == "block":
            return {"decision": "block", "rule": "I1", "reason": f"fixture block at {event}"}
        if MODE == "raise":
            raise RuntimeError("fixture")
        if MODE == "sleep":
            time.sleep(5)
        return {"decision": "allow", "rule": None, "reason": ""}
'''


def _fixture_tree(tmp: Path, *, with_pr: bool) -> Path:
    tools = tmp / "tree" / "09-tools"
    tools.mkdir(parents=True)
    shutil.copy2(Path(__file__).resolve(), tools / "ws_hook.py")
    (tmp / "tree" / "02-shared-references").mkdir()
    shutil.copy2(ROOT / "02-shared-references" / "surfaces.json", tmp / "tree" / "02-shared-references" / "surfaces.json")
    if with_pr:
        (tools / "profile_resolve.py").write_text(FAKE_PR_SOURCE, encoding="utf-8")
    return tools / "ws_hook.py"


def _run_cli(script: Path, args, *, stdin="", home: Path, extra_env=None, timeout=30):
    env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(home), "LANG": "C"}
    env.update(extra_env or {})
    return subprocess.run([sys.executable, str(script), *args], input=stdin, capture_output=True, text=True,
                          env=env, timeout=timeout)


def _tree_snapshot(path: Path) -> list:
    return sorted(str(p.relative_to(path)) for p in path.rglob("*"))


def self_test_cases() -> list:
    results = []

    def ok(name, cond, detail=""):
        results.append((name, bool(cond), "" if cond else detail))

    table = json.loads((ROOT / "02-shared-references" / "surfaces.json").read_text(encoding="utf-8"))

    # 1. Goldens: declared keys only, hint resolves, normalize to equal events.
    for event in ("session-start", "user-prompt"):
        norm = {}
        for s in GOLDEN_SURFACES:
            p = _golden(s, event)
            declared = {m["key"] for m in (_row(table, s)["markers"]["payload_keys_any"])}
            foreign = {m["key"] for r in table["surfaces"] if r["id"] != s for m in r["markers"]["payload_keys_any"]}
            ok(f"golden {s}.{event} carries its declared keys only", declared <= set(p) and not (foreign & set(p)),
               f"declared={declared} foreign={foreign & set(p)}")
            hint = payload_host_hint(p, table=table)
            ok(f"golden {s}.{event} hints {s}", hint == s, f"hint={hint}")
            n = normalize(p, s, table=table)
            n.pop("host")
            norm[s] = n
        first = norm[GOLDEN_SURFACES[0]]
        ok(f"goldens normalize to equal {event} events", all(v == first for v in norm.values()), json.dumps(norm))
        ok(f"normalized {event} names the event", first["event"] == event, str(first))
    p = dict(_golden("cursor", "user-prompt"), generation_id="gen-7")
    ok("a payload turn id wins over the prompt hash", normalize(p, "cursor", table=table)["turn"] == "gen-7")

    # 2. Every dialect is valid.
    for name, d in table["dialects"].items():
        for event in ("session-start", "user-prompt"):
            text = render(name, event, "CARD", table=table)
            if not d.get("verified"):
                ok(f"dialect {name} unverified renders nothing", text == "", repr(text))
                continue
            if d["context"] == "plain":
                ok(f"dialect {name} {event} plain", text == "CARD", repr(text))
                continue
            try:
                obj = json.loads(text) if text else None
            except ValueError:
                obj = None
            if d["context"] == "hookSpecificOutput":
                good = obj and obj["hookSpecificOutput"]["additionalContext"] == "CARD" and \
                    obj["hookSpecificOutput"]["hookEventName"] == table["formats"]["claude-settings"][event]
            else:
                good = obj == ({"additional_context": "CARD"} if event == "session-start" else {})
            ok(f"dialect {name} {event} is valid JSON in shape", good, repr(text))
        nv = noop(name, table=table)
        ok(f"dialect {name} noop parses", nv == "" or json.loads(nv) == {}, repr(nv))

    with tempfile.TemporaryDirectory(prefix="ws-hook-st-") as tmpd:
        tmp = Path(tmpd)
        # Fake workspace root with a card script.
        vroot = tmp / "vault"
        (vroot / "09-tools").mkdir(parents=True)
        (vroot / "09-tools" / "session-status.py").write_text(
            "import sys\nprint('CARD for ' + sys.argv[2])\n", encoding="utf-8")
        # H7: the real matcher over the prompt_route fixture brain.
        shutil.copy2(TOOLS / "prompt_route.py", vroot / "09-tools" / "prompt_route.py")
        shutil.copytree(TOOLS / "fixtures" / "prompt_route" / "brain", vroot, dirs_exist_ok=True)
        (vroot / "AGENTS.md").write_text("# fixture brain\n", encoding="utf-8")

        def home_with(tele: bool, name: str) -> Path:
            home = tmp / name
            base = home / ".config" / "snds-workspace"
            base.mkdir(parents=True)
            (base / "root").write_text(str(vroot) + "\n", encoding="utf-8")
            if tele:
                (base / "telemetry").mkdir()
            return home

        # 3. Card + duplicate claim.
        home = home_with(True, "h-claim")
        fake = _FakePR(home)
        with _with_pr(fake):
            buf1, buf2 = io.StringIO(), io.StringIO()
            payload = _golden("claude-code", "session-start")
            handle_event("auto", "session-start", payload, home=home, out=buf1, optional_steps=[])
            handle_event("auto", "session-start", payload, home=home, out=buf2, optional_steps=[])
            try:
                obj = json.loads(buf1.getvalue())
                card_ok = obj["hookSpecificOutput"]["additionalContext"].startswith("CARD for ")
            except (ValueError, KeyError):
                card_ok = False
            ok("session-start emits the card in the host dialect", card_ok, buf1.getvalue())
            ok("a duplicate claim gives no output", buf2.getvalue() == "", buf2.getvalue())
            buf3 = io.StringIO()
            handle_event("auto", "session-start", dict(_golden("cursor", "session-start"), conversation_id="sess-cur"),
                         home=home, out=buf3, optional_steps=[])
            try:
                cur_ok = json.loads(buf3.getvalue())["additional_context"].startswith("CARD for ")
            except (ValueError, KeyError):
                cur_ok = False
            ok("cursor session-start uses the cursor dialect", cur_ok, buf3.getvalue())
            buf4 = io.StringIO()
            handle_event("auto", "session-start", dict(_golden("codex", "session-start"), session_id="sess-cdx"),
                         home=home, out=buf4, optional_steps=[])
            ok("codex session-start gets the card as plain text", buf4.getvalue().startswith("CARD for "),
               buf4.getvalue())
            # H7: user-prompt routes through the vault's prompt_route (the one matcher).
            buf5 = io.StringIO()
            handle_event("auto", "user-prompt", _golden("claude-code", "user-prompt"), home=home, out=buf5)
            ok("user-prompt with no trigger emits nothing", buf5.getvalue() == "", buf5.getvalue())
            routed = dict(_golden("claude-code", "user-prompt"), prompt="review the zero vector plan",
                          session_id="sess-route")
            buf6 = io.StringIO()
            handle_event("auto", "user-prompt", routed, home=home, out=buf6)
            try:
                ctx = json.loads(buf6.getvalue())["hookSpecificOutput"]
                route_ok = ctx["hookEventName"] == "UserPromptSubmit" and "zero-vector.md" in ctx["additionalContext"]
                longest_ok = "fixture-linear-algebra" not in ctx["additionalContext"]
            except (ValueError, KeyError):
                route_ok = longest_ok = False
            ok("user-prompt routes in the host dialect (claude-code)", route_ok, buf6.getvalue())
            ok("user-prompt keeps longest-match suppression", longest_ok, buf6.getvalue())
            buf7 = io.StringIO()
            handle_event("auto", "user-prompt", routed, home=home, out=buf7)
            ok("a duplicate user-prompt claim gives no output", buf7.getvalue() == "", buf7.getvalue())
            x2 = dict(routed, session_id="sess-x2",
                      prompt="<task-notification>\n<summary>review the zero vector plan</summary>\n</task-notification>")
            buf8 = io.StringIO()
            handle_event("auto", "user-prompt", x2, home=home, out=buf8)
            ok("X2: a task-notification turn is not routed", buf8.getvalue() == "", buf8.getvalue())
            buf9 = io.StringIO()
            handle_event("auto", "user-prompt", dict(_golden("cursor", "user-prompt"), conversation_id="sess-rc",
                                                     prompt="review the zero vector plan"), home=home, out=buf9)
            ok("cursor user-prompt cannot inject (renders {})", buf9.getvalue().strip() == "{}", buf9.getvalue())
            buf10 = io.StringIO()
            handle_event("auto", "user-prompt", dict(_golden("codex", "user-prompt"), session_id="sess-rx",
                                                     prompt="review the zero vector plan"), home=home, out=buf10)
            ok("codex user-prompt routes as plain text", buf10.getvalue().startswith("# Project trigger detected")
               and "zero-vector.md" in buf10.getvalue(), buf10.getvalue())
            # H7 golden: the documented Codex UserPromptSubmit payload -> exact routing stdout.
            gold = json.loads((ROOT / "09-tools" / "fixtures" / "ws_hook" / "goldens" /
                               "codex.user-prompt-route.json").read_text(encoding="utf-8"))
            buf10g = io.StringIO()
            handle_event("codex", "user-prompt", gold["payload"], home=home, out=buf10g)
            ok("golden codex.user-prompt-route: stdout matches", buf10g.getvalue() == gold["stdout"],
               repr(buf10g.getvalue()))
            (vroot / "09-tools" / "prompt_route.py").rename(vroot / "09-tools" / "prompt_route.off")
            buf11 = io.StringIO()
            handle_event("auto", "user-prompt", dict(routed, session_id="sess-noroute"), home=home, out=buf11)
            (vroot / "09-tools" / "prompt_route.off").rename(vroot / "09-tools" / "prompt_route.py")
            ok("user-prompt fails open without prompt_route", buf11.getvalue() == "", buf11.getvalue())

            # 4. Card still emitted when optional steps sleep past the budget.
            buf = io.StringIO()
            p2 = dict(payload, session_id="sess-budget")
            t0 = time.monotonic()
            handle_event("auto", "session-start", p2, home=home, out=buf, budget=1.0,
                         optional_steps=[lambda: time.sleep(4)])
            elapsed = time.monotonic() - t0
            ok("card still emitted when optional steps sleep past the budget",
               "CARD for" in buf.getvalue() and elapsed < 2.5, f"elapsed={elapsed:.2f} out={buf.getvalue()!r}")

            # 5. Probe mode: records and emits the dialect noop.
            buf = io.StringIO()
            handle_event("auto", "session-start", _golden("cursor", "session-start"), probe=True, home=home,
                         out=buf, env={"CURSOR_AGENT": "1", "TERM_PROGRAM": "vscode", "SECRET_THING": "x"})
            recs = list((home / ".config" / "snds-workspace" / "telemetry" / "probes").glob("*.json"))
            ok("probe emits the cursor noop", buf.getvalue().strip() == "{}", buf.getvalue())
            ok("probe writes one telemetry record", len(recs) == 1, str(recs))
            if recs:
                rec = json.loads(recs[0].read_text(encoding="utf-8"))
                ok("probe record keeps env names, not foreign values",
                   "CURSOR_AGENT" in rec["env_marker_names"] and "SECRET_THING" not in json.dumps(rec)
                   and rec["env_values"].get("CURSOR_AGENT") == "1", json.dumps(rec))

        # 5b. An env-only record keeps the payload-derived detection of a recorded hook probe.
        hook_det = {"acting_host": "claude-code", "via": "payload", "verified": True}
        prior = {"hook_probe": {"status": "recorded", "events": {"stop": {}}}, "detected": hook_det,
                 "ancestry_comm": ["claude"]}
        env_only = {"via": None, "detected": {"acting_host": "claude-code", "via": "env", "verified": False},
                    "ancestry_comm": ["zsh"], "env_presence": {"WS_CLAUDE_OVERLAY": True}}
        merged = _tracked_probe("claude-code", "d", prior, [], env_only, "2026-01-01")
        ok("env-only record keeps hook detection",
           merged["detected"] == hook_det and merged["ancestry_comm"] == ["claude"]
           and merged["env_probe"]["env_presence"]["WS_CLAUDE_OVERLAY"] is True, json.dumps(merged))
        term = dict(env_only, via="terminal", env_presence={"WS_CLAUDE_OVERLAY": False})
        both = _tracked_probe("claude-code", "d", merged, [], term, "2026-01-02")
        ok("env probes are kept per via",
           set(both["env_probes"]) == {"agent-shell", "terminal"}
           and both["env_probes"]["agent-shell"]["env_presence"]["WS_CLAUDE_OVERLAY"] is True
           and both["env_probe"]["via"] == "terminal", json.dumps(both["env_probes"]))
        legacy = _tracked_probe("claude-code", "d", {"env_probe": {"via": "run_in_terminal", "env_marker_names": ["X"],
                                                                   "env_presence": {}}}, [], term, "2026-01-02")
        ok("a legacy single env_probe is kept under its via",
           set(legacy["env_probes"]) == {"run_in_terminal", "terminal"}, json.dumps(legacy["env_probes"]))
        fresh = _tracked_probe("claude-code", "d", {}, [], env_only, "2026-01-01")
        ok("env-only record without a hook probe takes env detection",
           fresh["detected"]["via"] == "env", json.dumps(fresh))

        # 6. No writes when telemetry/ is absent.
        home = home_with(False, "h-notele")
        before = _tree_snapshot(home)
        with _with_pr(_FakePR(home)):
            handle_event("auto", "session-start", _golden("claude-code", "session-start"), home=home,
                         out=io.StringIO())
            handle_event("auto", "session-start", _golden("cursor", "session-start"), probe=True, home=home,
                         out=io.StringIO())
            ok("claim proceeds without telemetry/", claim("s", "session-start", "0", host="x", home=home))
        ok("no writes when telemetry/ is absent", _tree_snapshot(home) == before,
           f"{before} -> {_tree_snapshot(home)}")

        # 7. Baseline only in the workspace.
        home = home_with(True, "h-base")
        with _with_pr(_FakePR(home)):
            plain = tmp / "not-a-workspace"
            plain.mkdir()
            ok("baseline not written outside the workspace",
               write_baseline(_golden("claude-code", "session-start"), plain) is None
               and not (plain / ".workspace").exists())
        fake_ws = tmp / "fake-ws"
        (fake_ws / "02-shared-references").mkdir(parents=True)
        (fake_ws / "AGENTS.md").write_text("# fixture\n", encoding="utf-8")
        shutil.copy2(ROOT / "02-shared-references" / "surfaces.json", fake_ws / "02-shared-references" / "surfaces.json")
        genv = {k: v for k, v in os.environ.items() if not k.startswith("GIT_CONFIG")}
        genv.update({"HOME": str(home), "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull})
        subprocess.run(["git", "init", "-q"], cwd=fake_ws, env=genv, timeout=GIT_TIMEOUT_S * 5, capture_output=True)
        (fake_ws / "new.txt").write_text("x\n", encoding="utf-8")
        with _with_pr(_FakePR(home)):      # no is_workspace_checkout: exercises the fallback check
            path = write_baseline(_golden("claude-code", "session-start"), fake_ws)

        class _WsPR(_FakePR):
            def is_workspace_checkout(self, path, *, root=None):
                return Path(path).resolve() == fake_ws.resolve()
        with _with_pr(_WsPR(home)):
            ok("baseline honours profile_resolve.is_workspace_checkout",
               write_baseline(_golden("claude-code", "session-start"), plain) is None)
        good = False
        if path and path.is_file():
            rec = json.loads(path.read_text(encoding="utf-8"))
            good = rec["sid"] == "sess-0001" and any(e["path"] == "new.txt" for e in rec["porcelain"])
        ok("baseline written in the workspace with parsed porcelain", good, str(path))
        ok("porcelain -z parses renames with orig",
           parse_porcelain_z("R  new.md\0old.md\0 M x.py\0") ==
           [{"xy": "R ", "path": "new.md", "orig": "old.md"}, {"xy": " M", "path": "x.py", "orig": None}])

        # 8. probe-promote redaction.
        def promote_case(name, rec_patch, want_rc):
            h = home_with(True, f"h-promote-{name}")
            pdir = h / ".config" / "snds-workspace" / "telemetry" / "probes"
            if rec_patch is not None:
                pdir.mkdir()
                base = {"schema_version": 1, "kind": "hook", "declared_host": "auto", "event": "session-start",
                        "recorded_at": "2026-09-23", "ts": "20260923T000000Z", "device": "dev-a",
                        "payload_keys": ["cursor_version", "hook_event_name"], "via": None,
                        "env_marker_names": ["CURSOR_AGENT"], "env_values": {"CURSOR_AGENT": "1"},
                        "env_presence": {k: False for k in ENV_PRESENCE_KEYS}, "ancestry_comm": ["zsh"],
                        "detected": {"acting_host": "cursor", "family_for_walls": "cursor", "via": "payload",
                                     "verified": True, "conflict": False}, "git_version": "2.54.0"}
                base.update(rec_patch)
                (pdir / "r1.json").write_text(json.dumps(base), encoding="utf-8")
            vr = tmp / f"vr-{name}"
            vr.mkdir()
            with _with_pr(_FakePR(h)):
                import contextlib
                with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                    rc = probe_promote("cursor", home=h, root=vr)
            written = vr / PROBES_REL / "cursor@dev-a.json"
            ok(f"probe-promote {name} exits {want_rc}", rc == want_rc and written.exists() == (want_rc == 0),
               f"rc={rc} written={written.exists()}")
            return written

        w = promote_case("clean", {}, 0)
        if w.exists():
            data = json.loads(w.read_text(encoding="utf-8"))
            ok("promoted file passes validation and records the hook event",
               not validate_record(data, allow_env_values=table["probe_env_value_allowlist"], hostnames=[], users=[])
               and data["hook_probe"]["status"] == "recorded" and not data["detection_mismatch"], json.dumps(data))
        promote_case("path", {"ancestry_comm": ["/usr/bin/zsh"]}, 1)
        promote_case("at-sign", {"payload_keys": ["user@example"]}, 1)
        promote_case("foreign-env-value", {"env_values": {"CURSOR_AGENT": "1", "HOME_DIR": "x"}}, 1)
        promote_case("nothing", None, 3)

    # 9. host --skip-any.
    with tempfile.TemporaryDirectory(prefix="ws-hook-st-") as tmpd:
        home = Path(tmpd)
        cases = [
            ("verified cursor payload in the set", _golden("cursor", "session-start"), None, 3),
            ("claude payload not in the set", _golden("claude-code", "session-start"), None, 0),
            ("codex payload not in the set", _golden("codex", "session-start"), None, 0),
            ("no payload, verified env cursor", {}, {"acting_host": "cursor", "determined": True, "verified": True}, 3),
            ("no payload, verified env claude", {}, {"acting_host": "claude-code", "determined": True, "verified": True}, 0),
            ("no payload, unverified cursor", {}, {"acting_host": "cursor", "determined": True, "verified": False}, 2),
            ("undetermined", {}, {"acting_host": "unknown", "determined": False, "verified": False}, 2),
        ]
        for name, payload, det, want in cases:
            with _with_pr(_FakePR(home, detect=det)):
                rc = host_skip_any({"cursor"}, payload)
            ok(f"host --skip-any: {name} -> {want}", rc == want, f"rc={rc}")

        class _Boom(_FakePR):
            def detect_surface(self, *a, **kw):
                raise RuntimeError("boom")
        with _with_pr(_Boom(home)):
            ok("host --skip-any: detection error -> 2", host_skip_any({"cursor"}, {}) == 2)

        # --skip-unless: the complement. 3 only on verified evidence of a host outside the set.
        proj = {"claude-code", "cursor"}
        cases = [
            ("claude payload in the set", _golden("claude-code", "session-start"), None, proj, 0),
            ("cursor payload in the set", _golden("cursor", "session-start"), None, proj, 0),
            ("codex payload outside the set", _golden("codex", "session-start"), None, proj, 3),
            ("copilot-vscode payload outside the set", _golden("copilot-vscode", "session-start"), None, proj, 3),
            ("no payload, verified env claude", {}, {"acting_host": "claude-code", "determined": True, "verified": True}, proj, 0),
            ("no payload, verified env codex", {}, {"acting_host": "codex", "determined": True, "verified": True}, proj, 3),
            ("no payload, unverified codex", {}, {"acting_host": "codex", "determined": True, "verified": False}, proj, 2),
            ("verified but unknown host", {}, {"acting_host": "unknown", "determined": True, "verified": True}, proj, 2),
            ("undetermined", {}, {"acting_host": "unknown", "determined": False, "verified": False}, proj, 2),
            ("empty set", _golden("codex", "session-start"), None, set(), 2),
        ]
        for name, payload, det, hosts, want in cases:
            with _with_pr(_FakePR(home, detect=det)):
                rc = host_skip_any(hosts, payload, unless=True)
            ok(f"host --skip-unless: {name} -> {want}", rc == want, f"rc={rc}")
        with _with_pr(_Boom(home)):
            ok("host --skip-unless: detection error -> 2", host_skip_any(proj, {}, unless=True) == 2)

        # --skip-unless-layer: the set is a layer's loaded_by in surfaces.json, never a list in the shim.
        live = json.loads((ROOT / "02-shared-references" / "surfaces.json").read_text(encoding="utf-8"))
        want_proj = set(next(lay for lay in live["layers"] if lay["id"] == "claude-project")["loaded_by"])
        ok("layer_hosts(claude-project) is the table's loaded_by",
           layer_hosts("claude-project", table=live) == want_proj and "copilot-vscode" in want_proj
           and "codex" not in want_proj, f"{sorted(layer_hosts('claude-project', table=live))}")
        ok("layer_hosts: unknown layer -> empty", layer_hosts("no-such-layer", table=live) == set())
        ok("layer_hosts: no table -> empty", layer_hosts("claude-project", table=None) == set())
        with _with_pr(_FakePR(home)):
            ok("layer_hosts reads the table through profile_resolve", layer_hosts("claude-project") == want_proj)
        for surface, want in (("claude-code", 0), ("cursor", 0), ("copilot-vscode", 0), ("codex", 3)):
            with _with_pr(_FakePR(home)):
                rc = host_skip_any(layer_hosts("claude-project"), _golden(surface, "session-start"), unless=True)
            ok(f"host --skip-unless-layer claude-project: {surface} payload -> {want}", rc == want, f"rc={rc}")
        # The boot shim defers by the layer its own registrations defer to (Rule R defers_to).
        shim = (ROOT / "00-bootstrap" / "dist" / "workspace-sessionstart.sh").read_text(encoding="utf-8")
        named = set(re.findall(r"host --skip-unless-layer (\S+)", shim))
        regs = {r["id"]: r for r in live["registrations"]}
        targets = {regs[r["defers_to"]]["layer"] for r in live["registrations"]
                   if r.get("command") == "ws-user-sessionstart" and r.get("defers_to") in regs}
        ok("boot shim defers for the hosts of the layer its registrations defer to",
           bool(named) and named == targets, f"shim={sorted(named)} table={sorted(targets)}")
        ok("boot shim names no host list for the deferral", "host --skip-unless " not in shim)

        # 10. Floor adapter.
        seen = []

        def fl_block(event, args, lines):
            seen.append(event)
            return {"decision": "block", "rule": "I1", "reason": "fixture"}

        def fl_raise(event, args, lines):
            raise RuntimeError("fixture")

        def fl_sleep(event, args, lines):
            time.sleep(3)
            return {"decision": "block"}

        for name, fn, args, want in [("block maps to 1", fl_block, ["origin", "url"], 1),
                                     ("exception maps to 0", fl_raise, [], 0),
                                     ("timeout maps to 0", fl_sleep, ["msgfile"], 0)]:
            err = io.StringIO()
            with _with_pr(_FakePR(home, floor=fn)):
                rc = run_floor(args, ["refs/heads/x 1 refs/heads/x 0"], budget=0.5, err=err)
            ok(f"floor adapter: {name}", rc == want and err.getvalue().strip(), f"rc={rc} err={err.getvalue()!r}")
        ok("floor adapter: argc 2 is pre-push", seen == ["pre-push"], str(seen))
        err = io.StringIO()
        with _with_pr(_FakePR(home)):
            rc = run_floor([], [], err=err)
        ok("floor adapter: absent floor_decide maps to 0 with a notice", rc == 0 and "unavailable" in err.getvalue())
        argc_seen = []

        def fl_argc(event, args, lines):
            argc_seen.append(event)
            return {"decision": "allow"}
        with _with_pr(_FakePR(home, floor=fl_argc)):
            run_floor(["msg"], [], err=io.StringIO())
            run_floor([], [], err=io.StringIO())
        ok("floor adapter: argc 1 is commit-msg, 0 is pre-commit", argc_seen == ["commit-msg", "pre-commit"], str(argc_seen))

    # 11. Subprocess: missing profile_resolve fails open; CLI floor mapping; N1 wrapper under sh.
    with tempfile.TemporaryDirectory(prefix="ws-hook-st-") as tmpd:
        tmp = Path(tmpd)
        home = tmp / "home"
        home.mkdir()
        lone = _fixture_tree(tmp / "lone", with_pr=False)
        cur = json.dumps(_golden("cursor", "session-start"))
        r = _run_cli(lone, ["host", "--skip-any", "cursor"], stdin=cur, home=home)
        ok("missing profile_resolve: host --skip-any exits 2", r.returncode == 2, f"rc={r.returncode} {r.stderr}")
        cdx = json.dumps(_golden("codex", "session-start"))
        r = _run_cli(lone, ["host", "--skip-unless", "claude-code,cursor"], stdin=cdx, home=home)
        ok("missing profile_resolve: host --skip-unless exits 2", r.returncode == 2, f"rc={r.returncode} {r.stderr}")
        r = _run_cli(lone, ["host", "--skip-unless-layer", "claude-project"], stdin=cdx, home=home)
        ok("missing profile_resolve: host --skip-unless-layer exits 2", r.returncode == 2, f"rc={r.returncode} {r.stderr}")
        r = _run_cli(lone, ["--host", "auto", "--event", "session-start"], stdin=cur, home=home)
        ok("missing profile_resolve: event exits 0 silently", r.returncode == 0 and r.stdout == "", f"{r.returncode} {r.stdout!r}")
        r = _run_cli(lone, ["--host", "git", "--floor", "claude", "origin", "url"], stdin="", home=home)
        ok("missing profile_resolve: floor exits 0 with a notice", r.returncode == 0 and "allowing" in r.stderr, r.stderr)
        broken = {"raises": "raise RuntimeError('fixture')\n", "syntax": "def x(:\n",
                  "exits": "import sys\nsys.exit(7)\n", "hangs": "import time\ntime.sleep(30)\n"}
        for label, body in broken.items():
            bt = _fixture_tree(tmp / f"broken-{label}", with_pr=False)
            (bt.parent / "profile_resolve.py").write_text(body, encoding="utf-8")
            t0 = time.monotonic()
            try:
                rf = _run_cli(bt, ["--host", "git", "--floor", "claude", "origin", "url"], stdin="a b c d\n",
                              home=home, extra_env={"WS_HOOK_IMPORT_BUDGET": "1"}, timeout=12)
                re_ = _run_cli(bt, ["--host", "auto", "--event", "session-start"], stdin=cur, home=home,
                               extra_env={"WS_HOOK_IMPORT_BUDGET": "1"}, timeout=12)
            except subprocess.TimeoutExpired:
                rf = re_ = subprocess.CompletedProcess([], 124, "", "timed out (unbounded import)")
            took = time.monotonic() - t0
            ok(f"a pinned profile_resolve that {label} at import fails open (floor 0, event 0, bounded)",
               rf.returncode == 0 and re_.returncode == 0 and took < 15 and "Traceback" not in rf.stderr + re_.stderr,
               f"floor={rf.returncode} event={re_.returncode} took={took:.1f}s {rf.stderr[-160:]} {re_.stderr[-160:]}")
        full = _fixture_tree(tmp / "full", with_pr=True)
        r = _run_cli(full, ["host", "--skip-any", "cursor"], stdin=cur, home=home)
        ok("CLI host --skip-any with a cursor payload exits 3", r.returncode == 3, f"rc={r.returncode} {r.stderr}")
        for label, stdin, want in (("codex", cdx, 3), ("cursor", cur, 0),
                                   ("claude", json.dumps(_golden("claude-code", "session-start")), 0)):
            r = _run_cli(full, ["host", "--skip-unless", "claude-code,cursor"], stdin=stdin, home=home)
            ok(f"CLI host --skip-unless claude-code,cursor with a {label} payload exits {want}",
               r.returncode == want, f"rc={r.returncode} {r.stderr}")
        for label, stdin, want in (("codex", cdx, 3), ("cursor", cur, 0),
                                   ("claude", json.dumps(_golden("claude-code", "session-start")), 0),
                                   ("copilot-vscode", json.dumps(_golden("copilot-vscode", "session-start")), 0)):
            r = _run_cli(full, ["host", "--skip-unless-layer", "claude-project"], stdin=stdin, home=home)
            ok(f"CLI host --skip-unless-layer claude-project with a {label} payload exits {want}",
               r.returncode == want, f"rc={r.returncode} {r.stderr}")
        for label, args in (("both flags", ["--skip-any", "cursor", "--skip-unless", "cursor"]), ("no flag", []),
                            ("empty set", ["--skip-unless", ","]),
                            ("an unknown layer", ["--skip-unless-layer", "no-such-layer"]),
                            ("a layer and a list", ["--skip-unless-layer", "claude-project", "--skip-unless", "codex"])):
            r = _run_cli(full, ["host", *args], stdin=cdx, home=home)
            ok(f"CLI host with {label} exits 2", r.returncode == 2, f"rc={r.returncode} {r.stderr}")
        r = _run_cli(full, ["--host", "git", "--floor", "claude", "origin", "url"], stdin="a b c d\n", home=home,
                     extra_env={"WS_FAKE_FLOOR": "block"})
        ok("CLI floor block exits 1 with the rule on stderr", r.returncode == 1 and "I1" in r.stderr, f"{r.returncode} {r.stderr}")
        r = _run_cli(full, ["--host", "git", "--floor", "claude"], home=home, extra_env={"WS_FAKE_FLOOR": "raise"})
        ok("CLI floor exception exits 0", r.returncode == 0 and "allowing" in r.stderr, f"{r.returncode} {r.stderr}")
        r = _run_cli(full, ["--host", "auto", "--event", "session-start", "--probe"], stdin=cur, home=home)
        ok("CLI probe emits the cursor noop", r.returncode == 0 and r.stdout.strip() == "{}", f"{r.returncode} {r.stdout!r}")

        # N1: every rendered .claude/settings.json command, CLAUDE_PROJECT_DIR unset or dispatcher absent.
        settings = json.loads((ROOT / ".claude" / "settings.json").read_text(encoding="utf-8"))
        cmds = [h["command"] for groups in settings["hooks"].values() for g in groups for h in g["hooks"]]
        fake_proj = tmp / "proj"
        (fake_proj / ".claude" / "hooks").mkdir(parents=True)
        base_env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(home)}
        all_ok = bool(cmds)
        for c in cmds:
            r1 = subprocess.run(["sh", "-c", c], input="{}", capture_output=True, text=True, env=base_env, timeout=20)
            r2 = subprocess.run(["sh", "-c", c], input="{}", capture_output=True, text=True,
                                env=dict(base_env, CLAUDE_PROJECT_DIR=str(fake_proj)), timeout=20)
            all_ok = all_ok and r1.returncode == 0 and not r1.stdout and not r1.stderr
            all_ok = all_ok and r2.returncode == 0 and not r2.stdout and not r2.stderr
        ok("N1: CLAUDE_PROJECT_DIR unset or dispatcher absent exits 0 silently", all_ok, str(cmds[:1]))
        (fake_proj / ".claude" / "hooks" / "dispatcher.py").write_text(
            "import sys\nprint('ran ' + sys.argv[1])\n", encoding="utf-8")
        r3 = subprocess.run(["sh", "-c", cmds[0]], input="{}", capture_output=True, text=True,
                            env=dict(base_env, CLAUDE_PROJECT_DIR=str(fake_proj)), timeout=20)
        ok("N1: a present dispatcher still runs with its event", r3.returncode == 0 and r3.stdout.startswith("ran "),
           f"{r3.returncode} {r3.stdout!r} {r3.stderr!r}")
    results += env_file_cases(table)
    results += ledger_cases()
    return results


LEDGER_GOLDENS = (("claude-code", "post-tool", "edit"), ("claude-code", "post-tool-bash", "shell"),
                  ("cursor", "post-edit", "edit"), ("cursor", "post-shell", "shell"),
                  ("codex", "post-tool", "edit"), ("codex", "post-tool-bash", "shell"))


def _placed(obj, cwd: Path):
    if isinstance(obj, str):
        return obj.replace("fixture-cwd", str(cwd))
    if isinstance(obj, list):
        return [_placed(x, cwd) for x in obj]
    if isinstance(obj, dict):
        return {k: _placed(v, cwd) for k, v in obj.items()}
    return obj


def ledger_golden(surface: str, event: str, cwd: Path) -> dict:
    """A post-tool golden with its fixture cwd placed at a real directory (H23 tests)."""
    return _placed(_golden(surface, event), cwd)


def ledger_cases() -> list:
    """H23: one ledger shape from every host's post-tool golden; host filter; silent; fast."""
    results = []

    def ok(name, cond, detail=""):
        results.append((name, bool(cond), "" if cond else detail))

    with tempfile.TemporaryDirectory(prefix="ws-hook-ledger-") as tmpd:
        tmp = Path(os.path.realpath(tmpd))
        repo = tmp / "repo"
        (repo / ".git").mkdir(parents=True)
        (repo / "notes").mkdir()
        home = tmp / "home"
        (home / ".config" / "snds-workspace" / "telemetry").mkdir(parents=True)
        shapes = {}
        for surface, event, kind in LEDGER_GOLDENS:
            payload = dict(ledger_golden(surface, event, repo), session_id=f"s-{surface}-{event}")
            payload.pop("conversation_id", None)
            buf = io.StringIO()
            t0 = time.monotonic()
            with contextlib.redirect_stdout(buf):
                rc = handle_event(surface, "post-tool", payload, home=home)
            took = time.monotonic() - t0
            recs = read_ledger(f"s-{surface}-{event}", home=home)
            ok(f"ledger {surface}.{event}: rc 0, silent, under {LEDGER_BUDGET_S * 1000:.0f} ms",
               rc == 0 and buf.getvalue() == "" and took < LEDGER_BUDGET_S, f"rc={rc} out={buf.getvalue()!r} {took:.3f}s")
            shape = [(r["repo"], r["path"]) for r in recs]
            ok(f"ledger {surface}.{event} names the repo and host",
               len(recs) == 1 and recs[0]["host"] == surface and recs[0]["repo"] == str(repo)
               and set(recs[0]) == {"repo", "path", "tool", "ts", "host"}, json.dumps(recs))
            shapes.setdefault(kind, set()).add(tuple(shape))
        ok("ledger parity: every host's edit golden gives the same record",
           shapes.get("edit") == {((str(repo), "notes/touched.md"),)}, str(shapes.get("edit")))
        ok("ledger parity: every host's shell golden gives the repo with no path",
           shapes.get("shell") == {((str(repo), None),)}, str(shapes.get("shell")))
        cur = dict(ledger_golden("cursor", "post-edit", repo), conversation_id="s-filter")
        handle_event("claude-code", "post-tool", cur, home=home)
        ok("host filter: a Cursor payload on the Claude registration writes nothing",
           not ledger_path("s-filter", home=home).exists())
        handle_event("auto", "post-tool", cur, home=home)
        ok("--host auto takes the payload host", [r["host"] for r in read_ledger("s-filter", home=home)] == ["cursor"])
        outside = dict(ledger_golden("claude-code", "post-tool", tmp / "no-repo"), session_id="s-out")
        handle_event("claude-code", "post-tool", outside, home=home)
        ok("an edit outside any repo is not recorded", not ledger_path("s-out", home=home).exists())
        read = dict(ledger_golden("claude-code", "post-tool", repo), session_id="s-read", tool_name="Read")
        handle_event("claude-code", "post-tool", read, home=home)
        ok("a read tool is not recorded", not ledger_path("s-read", home=home).exists())
        bare = tmp / "bare-home"
        bare.mkdir()
        handle_event("claude-code", "post-tool", dict(ledger_golden("claude-code", "post-tool", repo)), home=bare)
        ok("no ledger without telemetry/ (nothing installed)", _tree_snapshot(bare) == [], str(_tree_snapshot(bare)))
        ok("a broken payload fails open", handle_event("codex", "post-tool", {"session_id": "x", "tool_input": 3},
                                                       home=home) == 0)
        full = _fixture_tree(tmp / "cli", with_pr=False)
        pl = json.dumps(dict(ledger_golden("codex", "post-tool", repo), session_id="s-cli"))
        r = _run_cli(full, ["--host", "codex", "--event", "post-tool"], stdin=pl, home=home)
        ok("CLI post-tool writes the ledger without profile_resolve and prints nothing",
           r.returncode == 0 and r.stdout == "" and r.stderr == ""
           and [x["path"] for x in read_ledger("s-cli", home=home)] == ["notes/touched.md"],
           f"{r.returncode} {r.stdout!r} {r.stderr!r}")
        start = json.dumps(dict(_golden("cursor", "session-start"), conversation_id="s-sweep"))
        r = _run_cli(full, ["sweep", "--host", "cursor", "--budget", "1"], stdin=start, home=home)
        ok("CLI sweep with no closure module in the pin fails open with the Cursor noop",
           r.returncode == 0 and r.stdout.strip() == "{}" and r.stderr == "", f"{r.returncode} {r.stdout!r} {r.stderr!r}")
        r = _run_cli(full, ["sweep", "--host", "claude-code"], stdin=start, home=home)
        ok("CLI sweep host filter: a Cursor payload on the Claude registration is silent",
           r.returncode == 0 and r.stdout == "" and r.stderr == "", f"{r.returncode} {r.stdout!r} {r.stderr!r}")
    return results


OVERLAY_SAMPLE = (
    "# fixture overlay (header comment)\n"
    f"{OVERLAY_BEGIN}\n"
    "export WS_CLAUDE_OVERLAY='v5'\n"
    "export WS_SURFACE_FAMILY='claude'\n"
    "export WS_OVERLAY_CHANNEL='env-file'\n"
    "export GH_CONFIG_DIR='~/.config/snds-workspace/gh-claude'\n"
    "export GIT_CONFIG_COUNT='2'\n"
    "export GIT_CONFIG_KEY_0='hook.ws-claude-wall.command'\n"
    "export GIT_CONFIG_VALUE_0='H=\"$HOME\"; W=\"$H/x\"; exec \"$W\"'\n"
    "export GIT_CONFIG_KEY_1='x.quote'\n"
    "export GIT_CONFIG_VALUE_1='it'\\''s'\n"
    f"{OVERLAY_END}\n"
)


def env_file_cases(table: dict) -> list:
    """D-W1-4: the env-file step. Happy path, idempotent re-run, foreign lines kept, and every no-op
    branch (each leaves the session env file untouched and names its reason in telemetry)."""
    results = []

    def ok(name, cond, detail=""):
        results.append((f"env-file: {name}", bool(cond), "" if cond else detail))

    with tempfile.TemporaryDirectory(prefix="ws-hook-envfile-") as tmpd:
        tmp = Path(tmpd).resolve()
        home = tmp / "home"
        base = home / ".config" / "snds-workspace"
        (base / "telemetry").mkdir(parents=True)
        sess = home / ".claude" / "session-env" / "sess-0001"
        sess.mkdir(parents=True)
        src = base / OVERLAY_ENV_NAME
        src.write_text(OVERLAY_SAMPLE, encoding="utf-8")
        os.chmod(src, 0o644)
        target = sess / "sessionstart-hook-1.sh"
        claude_p = _golden("claude-code", "session-start")
        tele = base / "telemetry" / OVERLAY_TELEMETRY

        def last_reason():
            try:
                return json.loads(tele.read_text(encoding="utf-8").splitlines()[-1]).get("reason")
            except (OSError, ValueError, IndexError):
                return None

        def run(env=None, payload=None, host="claude-code"):
            e = {"CLAUDE_ENV_FILE": str(target)} if env is None else env
            with _with_pr(_FakePR(home)):
                return env_file(host, claude_p if payload is None else payload, env=e, home=home, table=table)

        target.write_text("export FOREIGN_BEFORE=1\n", encoding="utf-8")
        st = run()
        text = target.read_text(encoding="utf-8")
        ok("happy path writes the block", st == "written" and text.count(OVERLAY_BEGIN) == 1
           and text.startswith("export FOREIGN_BEFORE=1\n") and text.endswith(OVERLAY_END + "\n"), f"{st} {text!r}")
        ok("~/ and the floor home bind are rendered to the home",
           f"export GH_CONFIG_DIR='{home}/.config/snds-workspace/gh-claude'" in text
           and f"export GIT_CONFIG_VALUE_0='H={shlex.quote(str(home))}; W=\"$H/x\"; exec \"$W\"'" in text
           and "~/" not in text, text)
        ok("a marker names the session", (home / ".claude" / "ws-state" / "overlay.sess-0001").is_file())
        r = subprocess.run(["bash", "-c", f". {shlex.quote(str(target))}; printf '%s|%s|%s' \"$WS_OVERLAY_CHANNEL\" "
                            "\"$GIT_CONFIG_VALUE_1\" \"$GIT_CONFIG_COUNT\""], capture_output=True, text=True, timeout=20)
        ok("the written file sources in bash with exact values", r.stdout == "env-file|it's|2", repr(r.stdout))
        with open(target, "a", encoding="utf-8") as fh:
            fh.write("export FOREIGN_AFTER=2\n")
        st = run()
        text = target.read_text(encoding="utf-8")
        ok("a re-run keeps one block and every foreign line",
           st == "written" and text.count(OVERLAY_BEGIN) == 1 and text.count(OVERLAY_END) == 1
           and "export FOREIGN_BEFORE=1\n" in text and "export FOREIGN_AFTER=2\n" in text
           and text.index("FOREIGN_AFTER") < text.index(OVERLAY_BEGIN), text)
        ok("telemetry records the write", json.loads(tele.read_text().splitlines()[-1]).get("result") == "written")

        before = target.read_bytes()

        def noop_case(name, needle, **kw):
            st = run(**kw)
            ok(f"{name} is a no-op", st == "noop" and target.read_bytes() == before and needle in (last_reason() or ""),
               f"{st} reason={last_reason()!r}")

        noop_case("CLAUDE_ENV_FILE unset", "unset", env={})
        outside = tmp / "elsewhere.sh"
        outside.write_text("", encoding="utf-8")
        noop_case("a path outside ~/.claude/session-env", "not under", env={"CLAUDE_ENV_FILE": str(outside)})
        ok("the outside file stays empty", outside.read_text() == "")
        noop_case("a relative path", "absolute", env={"CLAUDE_ENV_FILE": "session-env/x.sh"})
        noop_case("a codex payload", "not a claude-code payload", payload=_golden("codex", "session-start"))
        noop_case("an unverified payload", "not a claude-code payload", payload={"session_id": "sess-0001"})
        noop_case("another --host", "host is not claude-code", host="codex")
        for label, bad in (("a non-overlay name", "export PATH='/tmp'\n"),
                           ("a double-quoted value", 'export WS_X="$(id)"\n'),
                           ("a trailing command", "export WS_X='a'; id\n"),
                           ("a repeated name", "export WS_X='a'\nexport WS_X='b'\n")):
            src.write_text(OVERLAY_SAMPLE + bad, encoding="utf-8")
            noop_case(f"a bad installed line ({label})", "installed overlay line")
        src.write_text(OVERLAY_SAMPLE, encoding="utf-8")
        os.chmod(src, 0o666)
        noop_case("a world-writable installed file", "writable")
        os.chmod(src, 0o644)
        src.unlink()
        noop_case("no installed file", "not installed")
        src.write_text(OVERLAY_SAMPLE, encoding="utf-8")
        os.chmod(src, 0o644)
        target.write_text(f"export A=1\n{OVERLAY_BEGIN}\nexport WS_X='a'\n", encoding="utf-8")
        before = target.read_bytes()
        noop_case("an unterminated block of ours", "unterminated")

        # The CLI: nothing on stdout, exit 0, even with no payload or a broken argument list.
        script = _fixture_tree(tmp / "cli", with_pr=True)
        target.write_text("", encoding="utf-8")
        r = _run_cli(script, ["env-file", "--host", "claude-code"], stdin=json.dumps(claude_p), home=home,
                     extra_env={"CLAUDE_ENV_FILE": str(target)})
        ok("CLI writes the block silently", r.returncode == 0 and r.stdout == "" and r.stderr == ""
           and target.read_text().count(OVERLAY_BEGIN) == 1, f"{r.returncode} {r.stdout!r} {r.stderr!r}")
        r = _run_cli(script, ["env-file"], stdin="not json", home=home, extra_env={"CLAUDE_ENV_FILE": str(target)})
        ok("CLI usage error exits 0 silently", r.returncode == 0 and r.stdout == "" and r.stderr == "",
           f"{r.returncode} {r.stdout!r} {r.stderr!r}")
    return results


# --------------------------------------------------------------------------- shell goldens

def _baseline_script(name: str) -> bytes:
    want = BASELINE_SCRIPTS[name]
    try:
        r = subprocess.run(["git", "show", f"{BASELINE_REV}:00-bootstrap/dist/{name}"], cwd=ROOT,
                           capture_output=True, timeout=10)
        if r.returncode == 0 and hashlib.sha256(r.stdout).hexdigest() == want:
            return r.stdout
    except (OSError, subprocess.SubprocessError):
        pass
    data = (ROOT / BASELINE_FIXTURES_REL / name).read_bytes()
    if hashlib.sha256(data).hexdigest() != want:
        raise RuntimeError(f"baseline copy of {name} does not match {BASELINE_REV}")
    return data


def _shell_run(script: bytes, payload: str, *, tmp: Path, ws: Path, tag: str, pin_rc=None, pre_state=None,
               real_pin=False, home_files=None):
    """(rc, stdout, audit lines) of one shim run in a temp home.

    pin_rc installs a stand-in ws-hook that always exits pin_rc. real_pin installs the byte-stable
    dist wrapper with lib/current pointing at this tree, so the real host detection answers."""
    home = tmp / f"home-{tag}"
    (home / ".claude").mkdir(parents=True)
    (home / ".claude" / "workspace-brain-path").write_text(str(ws) + "\n", encoding="utf-8")
    for rel, text in (pre_state or {}).items():
        p = home / ".claude" / "ws-state" / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    if pin_rc is not None:
        b = home / ".config" / "snds-workspace" / "bin"
        b.mkdir(parents=True)
        (b / "ws-hook").write_text(f"#!/bin/sh\ncat >/dev/null\nexit {pin_rc}\n", encoding="utf-8")
        (b / "ws-hook").chmod(0o755)
    elif real_pin:
        cfg = home / ".config" / "snds-workspace"
        (cfg / "bin").mkdir(parents=True)
        (cfg / "lib").mkdir()
        shutil.copy2(ROOT / "00-bootstrap" / "dist" / "ws-hook", cfg / "bin" / "ws-hook")
        (cfg / "bin" / "ws-hook").chmod(0o755)
        (cfg / "lib" / "current").symlink_to(ROOT, target_is_directory=True)
    for rel, text in (home_files or {}).items():
        p = home / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    path = tmp / f"script-{tag}.sh"
    path.write_bytes(script)
    env = {"HOME": str(home), "PATH": os.environ.get("PATH", "/usr/bin:/bin"), "LANG": "C", "LC_ALL": "C",
           "TMPDIR": str(tmp), "GIT_CEILING_DIRECTORIES": str(tmp), "GIT_CONFIG_NOSYSTEM": "1",
           "GIT_CONFIG_GLOBAL": os.devnull}
    r = subprocess.run(["bash", str(path)], input=payload, capture_output=True, text=True, env=env,
                       cwd=str(tmp), timeout=60)
    log = home / ".claude" / "ws-state" / "audit.log"
    log_lines = [" ".join(ln.split(" ")[1:]) for ln in log.read_text(encoding="utf-8").splitlines()] if log.exists() else []
    return r.returncode, r.stdout, log_lines


def shell_golden_cases() -> list:
    results = []
    with tempfile.TemporaryDirectory(prefix="ws-hook-shell-") as tmpd:
        tmp = Path(tmpd).resolve()
        ws = tmp / "ws"
        (ws / "00-bootstrap" / "dist").mkdir(parents=True)
        (ws / ".claude" / "hooks").mkdir(parents=True)
        (ws / "AGENTS.md").write_text("# fixture workspace\n", encoding="utf-8")
        (ws / "00-bootstrap" / "dist" / "RULES.txt").write_text("- fixture rule one\n- fixture rule two\n", encoding="utf-8")
        (ws / ".claude" / "hooks" / "dispatcher.py").write_text("# fixture\n", encoding="utf-8")
        (ws / ".claude" / "settings.json").write_text('{"hooks": "dispatcher.py"}\n', encoding="utf-8")
        outside = tmp / "elsewhere"
        outside.mkdir()
        transcript_ok = tmp / "t-ok.jsonl"
        transcript_ok.write_text(json.dumps({"type": "user", "message": {"role": "user", "content": "hi"}}) + "\n" +
                                 json.dumps({"type": "assistant", "message": {"role": "assistant", "content": "[workspace: LOADED · x]"}}) + "\n" +
                                 json.dumps({"type": "user", "message": {"role": "user", "content": "more"}}) + "\n", encoding="utf-8")
        transcript_miss = tmp / "t-miss.jsonl"
        transcript_miss.write_text(json.dumps({"type": "assistant", "message": {"role": "assistant", "content": "no token"}}) + "\n",
                                   encoding="utf-8")

        def claude(event, source=None, cwd=ws, transcript=None, sid="sess-0001"):
            p = _golden("claude-code", "session-start" if event == "SessionStart" else "user-prompt")
            p.update({"session_id": sid, "cwd": str(cwd), "hook_event_name": event,
                      "transcript_path": str(transcript or (tmp / ".claude" / "projects" / "fx" / f"{sid}.jsonl"))})
            if source:
                p["source"] = source
            return p

        def shaped(surface, event_file, **upd):
            p = _golden(surface, event_file)
            p.update(upd)
            return p

        codex_p = shaped("codex", "session-start", cwd=str(outside))
        codex_in = shaped("codex", "session-start", cwd=str(ws))
        copilot_in = shaped("copilot-vscode", "session-start", cwd=str(ws))
        cursor_p = shaped("cursor", "session-start", workspace_roots=[str(outside)])
        cases = {
            "workspace-sessionstart.sh": [
                (f"claude {src} {where}", claude("SessionStart", src, cwd), None)
                for src in ("startup", "resume", "compact") for where, cwd in (("inside", ws), ("outside", outside))
            ] + [("codex outside", codex_p, None), ("cursor outside", cursor_p, None),
                 # No verdict (no pin, exit 0, exit 2) keeps the 2ff02e7 in-workspace deferral.
                 ("codex inside", codex_in, None), ("copilot-vscode inside", copilot_in, None)],
            "workspace-reassert.sh": [
                ("claude no boot marker inside", claude("UserPromptSubmit", cwd=ws), None),
                ("claude marker, ritual missing outside", claude("UserPromptSubmit", cwd=outside, transcript=transcript_miss),
                 {"boot.sess-0001": "", "count.sess-0001": "1\n"}),
                ("codex", shaped("codex", "user-prompt", session_id="sess-0001"), {"boot.sess-0001": ""}),
                ("cursor", shaped("cursor", "user-prompt", session_id="sess-0001"), None),
            ],
            "workspace-audit.sh": [
                ("claude transcript ok inside", claude("SessionEnd", cwd=ws, transcript=transcript_ok), None),
                ("claude no transcript outside", claude("SessionEnd", cwd=outside), None),
                ("codex", shaped("codex", "session-start", hook_event_name="SessionEnd"), None),
                ("cursor", shaped("cursor", "session-start", hook_event_name="sessionEnd", session_id="sess-0001"), None),
            ],
        }
        n = 0
        for name, variants in cases.items():
            try:
                old = _baseline_script(name)
            except (OSError, RuntimeError) as exc:
                results.append((f"{name}: 2ff02e7 baseline available", False, str(exc)))
                continue
            new = (ROOT / "00-bootstrap" / "dist" / name).read_bytes()
            for label, payload, pre in variants:
                text = json.dumps(payload)
                n += 1
                want = _shell_run(old, text, tmp=tmp, ws=ws, tag=f"{n}-old", pre_state=pre)
                is_cursor = label.startswith("cursor")
                pins = (None, 0, 2) if not is_cursor else (None, 2)
                for pin in pins:
                    n += 1
                    got = _shell_run(new, text, tmp=tmp, ws=ws, tag=f"{n}-new", pin_rc=pin, pre_state=pre)
                    results.append((f"{name} {label} pin={pin}: identical to {BASELINE_REV}", got == want,
                                    f"want={want!r} got={got!r}"))
                if is_cursor:
                    n += 1
                    got = _shell_run(new, text, tmp=tmp, ws=ws, tag=f"{n}-new", pin_rc=3, pre_state=pre)
                    results.append((f"{name} {label} pin=3: exits 0 with no output", got == (0, "", []),
                                    f"got={got!r}"))
                if want[1] == "" and not want[2] and name != "workspace-reassert.sh":
                    results.append((f"{name} {label}: baseline produced output to compare", False,
                                    "fixture produced no stdout and no log line"))

        # L-08, the one sanctioned departure from 2ff02e7 (every case above stays byte-identical).
        # Inside the workspace the boot shim defers to the project hook only for a host that loads
        # the claude-project layer (its loaded_by in surfaces.json). Codex does not, so a Codex host
        # verified by the real pinned ws-hook gets the card 2ff02e7 gives it outside the workspace,
        # not the pointer. Claude Code and Copilot in VS Code load the layer and stay byte-identical.
        name = "workspace-sessionstart.sh"
        try:
            old = _baseline_script(name)
        except (OSError, RuntimeError) as exc:
            results.append((f"{name}: {BASELINE_REV} baseline available for the real-pin goldens", False, str(exc)))
            return results
        new = (ROOT / "00-bootstrap" / "dist" / name).read_bytes()
        n += 1
        card = _shell_run(old, json.dumps(codex_p), tmp=tmp, ws=ws, tag=f"{n}-old")
        n += 1
        pointer = _shell_run(old, json.dumps(codex_in), tmp=tmp, ws=ws, tag=f"{n}-old")
        n += 1
        got = _shell_run(new, json.dumps(codex_in), tmp=tmp, ws=ws, tag=f"{n}-new", real_pin=True)
        results.append((f"{name} codex inside, real pin: the card {BASELINE_REV} gives codex outside, not the pointer",
                        got == card and card != pointer and "via:user-hook/" in card[1],
                        f"card={card!r} pointer={pointer!r} got={got!r}"))
        claude_in = claude("SessionStart", "startup", ws)
        n += 1
        want = _shell_run(old, json.dumps(claude_in), tmp=tmp, ws=ws, tag=f"{n}-old")
        n += 1
        got = _shell_run(new, json.dumps(claude_in), tmp=tmp, ws=ws, tag=f"{n}-new", real_pin=True)
        results.append((f"{name} claude inside, real pin: identical to {BASELINE_REV}",
                        got == want and "via:project-hook/" in want[1], f"want={want!r} got={got!r}"))
        n += 1
        want = _shell_run(old, json.dumps(copilot_in), tmp=tmp, ws=ws, tag=f"{n}-old")
        n += 1
        got = _shell_run(new, json.dumps(copilot_in), tmp=tmp, ws=ws, tag=f"{n}-new", real_pin=True)
        results.append((f"{name} copilot-vscode inside the workspace, real pin: identical to {BASELINE_REV}",
                        got == want and "via:project-hook/" in want[1], f"want={want!r} got={got!r}"))
        cursor_in = shaped("cursor", "session-start", workspace_roots=[str(ws)])
        n += 1
        got = _shell_run(new, json.dumps(cursor_in), tmp=tmp, ws=ws, tag=f"{n}-new", real_pin=True)
        results.append((f"{name} cursor inside, real pin: exits 0 with no output", got == (0, "", []), f"got={got!r}"))

        # D-W1-4, the audit's one addition: with the env-file channel installed, a verified Claude Code
        # session that ends without its overlay marker logs NOOVERLAY after its usual line. The cases
        # above (no channel installed) stay byte-identical to 2ff02e7.
        name = "workspace-audit.sh"
        new = (ROOT / "00-bootstrap" / "dist" / name).read_bytes()
        chan = {f".config/snds-workspace/{OVERLAY_ENV_NAME}": OVERLAY_SAMPLE}
        tp = tmp / ".claude" / "projects" / "fx" / "sess-0009.jsonl"
        tp.parent.mkdir(parents=True, exist_ok=True)
        tp.write_text(transcript_ok.read_text(encoding="utf-8"), encoding="utf-8")
        tp1 = tmp / ".claude" / "projects" / "fx" / "sess-0010.jsonl"
        tp1.write_text(transcript_miss.read_text(encoding="utf-8"), encoding="utf-8")
        ended = claude("SessionEnd", cwd=ws, transcript=tp, sid="sess-0009")
        stamped = lambda ts: "".join(json.dumps(dict(json.loads(ln), timestamp=ts)) + "\n"  # noqa: E731
                                     for ln in transcript_ok.read_text(encoding="utf-8").splitlines())
        tp_old = tmp / ".claude" / "projects" / "fx" / "sess-0012.jsonl"
        tp_old.write_text(stamped("2020-01-01T00:00:00.000Z"), encoding="utf-8")
        tp_new = tmp / ".claude" / "projects" / "fx" / "sess-0013.jsonl"
        tp_new.write_text(stamped("2099-01-01T00:00:00.000Z"), encoding="utf-8")
        audit_cases = [
            ("claude session started before the channel was installed: no NOOVERLAY",
             claude("SessionEnd", cwd=ws, transcript=tp_old, sid="sess-0012"), chan, None,
             ["OK   sess-0012 cwd=" + str(ws)]),
            ("claude session started after the channel was installed, no marker: NOOVERLAY",
             claude("SessionEnd", cwd=ws, transcript=tp_new, sid="sess-0013"), chan, None,
             ["OK   sess-0013 cwd=" + str(ws), "NOOVERLAY sess-0013"]),
            ("claude, channel installed, no marker: NOOVERLAY", ended, chan, None,
             ["OK   sess-0009 cwd=" + str(ws), "NOOVERLAY sess-0009"]),
            ("claude, channel installed, marker present: no NOOVERLAY", ended, chan, {"overlay.sess-0009": "x\n"},
             ["OK   sess-0009 cwd=" + str(ws)]),
            ("claude, channel not installed: no NOOVERLAY", ended, None, None, ["OK   sess-0009 cwd=" + str(ws)]),
            ("claude one-shot, channel installed: exempt", claude("SessionEnd", cwd=ws, transcript=tp1, sid="sess-0010"),
             chan, None, ["SKIP sess-0010 one-shot"]),
            ("codex with a transcript, channel installed: not Claude Code",
             shaped("codex", "session-start", hook_event_name="SessionEnd", session_id="sess-0011",
                    transcript_path=str(transcript_ok), cwd=str(ws)), chan, None, ["OK   sess-0011 cwd=" + str(ws)]),
        ]
        for label, payload, files, pre, want_log in audit_cases:
            n += 1
            got = _shell_run(new, json.dumps(payload), tmp=tmp, ws=ws, tag=f"{n}-audit", real_pin=True,
                             home_files=files, pre_state=pre)
            results.append((f"{name} {label}", got == (0, "", want_log), f"got={got!r}"))
    return results


# --------------------------------------------------------------------------- CLI

def _report(results, title) -> int:
    failed = [r for r in results if not r[1]]
    for name, ok_, detail in results:
        print(f"{'ok  ' if ok_ else 'FAIL'} {name}" + ("" if ok_ else f" — {detail}"))
    print(f"{title}: {len(results) - len(failed)}/{len(results)} passed")
    return 1 if failed else 0


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv[:1] == ["--self-test"]:
        return _report(self_test_cases(), "ws_hook self-test")
    if argv[:1] == ["--self-test-shell"]:
        return _report(shell_golden_cases(), "ws_hook self-test-shell")
    if argv[:1] == ["host"]:
        ap = argparse.ArgumentParser(prog="ws_hook.py host")
        mode = ap.add_mutually_exclusive_group(required=True)
        mode.add_argument("--skip-any")
        mode.add_argument("--skip-unless")
        mode.add_argument("--skip-unless-layer")
        try:
            a = ap.parse_args(argv[1:])
        except SystemExit:
            return 2
        payload = _read_payload()
        if a.skip_unless_layer is not None:
            try:
                hosts = layer_hosts(a.skip_unless_layer.strip())
            except Exception:
                return 2
            return host_skip_any(hosts, payload, unless=True)
        unless = a.skip_unless is not None
        spec = a.skip_unless if unless else a.skip_any
        hosts = {h.strip() for h in spec.split(",") if h.strip()}
        return host_skip_any(hosts, payload, unless=unless)
    if argv[:1] == ["env-file"]:
        return _env_file_main(argv)
    if argv[:1] == ["sweep"]:
        return _sweep_main(argv)
    if argv[:1] == ["probe-env"]:
        ap = argparse.ArgumentParser(prog="ws_hook.py probe-env")
        ap.add_argument("--host", required=True)
        ap.add_argument("--via", choices=["terminal", "run_in_terminal"])
        ap.add_argument("--record", action="store_true")
        try:
            a = ap.parse_args(argv[1:])
        except SystemExit:
            return 2
        return probe_env(a.host, via=a.via, record=a.record)
    if argv[:1] == ["probe-promote"]:
        ap = argparse.ArgumentParser(prog="ws_hook.py probe-promote")
        ap.add_argument("--host", required=True)
        ap.add_argument("--device")
        try:
            a = ap.parse_args(argv[1:])
        except SystemExit:
            return 2
        return probe_promote(a.host, device=a.device)
    if argv[:1] == ["lane"]:
        return _lane_main(argv)
    try:
        return _hook_main(argv)
    except KeyboardInterrupt:
        raise
    except BaseException as exc:  # noqa: BLE001 - hook paths (floor, events) always fail open
        print(f"ws_hook: {exc.__class__.__name__} in a hook path; allowing", file=sys.stderr)
        return 0


def _sweep_main(argv) -> int:
    """`ws_hook.py sweep --host H` (stdin: the session-start payload). Never prints; exit 0."""
    try:
        ap = argparse.ArgumentParser(prog="ws_hook.py sweep")
        ap.add_argument("--host", required=True)
        ap.add_argument("--budget", type=float)
        a = ap.parse_args(argv[1:])
        payload = _read_payload()
        t = _payload_table()
        hint = payload_host_hint(payload, table=t)
        host = a.host if a.host != "auto" else (hint or "unknown")
        if not (a.host != "auto" and hint and hint != a.host):   # host filter: the other host sweeps
            run_sweep(host, payload, budget=a.budget)
        text = noop((_row(t, host) or {}).get("dialect") or "none", table=t)
        if text:
            sys.stdout.write(text + "\n")
        return 0
    except BaseException:  # noqa: BLE001 - a session start is never blocked
        return 0


def _hook_main(argv) -> int:
    if "--floor" in argv:
        i = argv.index("--floor")
        if argv[:2] != ["--host", "git"] or i != 2 or argv[3:4] != ["claude"]:
            print("usage: ws_hook.py --host git --floor claude [GIT_HOOK_ARGS...]", file=sys.stderr)
            return 0
        hook_args = argv[4:]
        return run_floor(hook_args, _read_lines() if len(hook_args) == 2 else [])
    ap = argparse.ArgumentParser(prog="ws_hook.py")
    ap.add_argument("--host", required=True)
    ap.add_argument("--event", required=True, choices=EVENTS)
    ap.add_argument("--probe", action="store_true")
    ap.add_argument("--budget", type=float)
    try:
        a = ap.parse_args(argv)
    except SystemExit:
        return 0            # hook path: a usage error never blocks the host
    if a.event == "post-tool" and not a.probe:
        return record_touch(a.host, _read_payload())     # H23 hot path: no profile_resolve import
    t = _surfaces()
    if t is not None and a.host != "auto":
        row = _row(t, a.host)
        if row is None or not row.get("hookable"):
            print(f"ws_hook: --host {a.host} is not a hookable surface", file=sys.stderr)
            return 0
    return handle_event(a.host, a.event, _read_payload(), probe=a.probe, budget=a.budget)


if __name__ == "__main__":
    sys.exit(main())
