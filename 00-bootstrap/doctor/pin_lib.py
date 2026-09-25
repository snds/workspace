#!/usr/bin/env python3
"""pin_lib.py — the pinned lib under ~/.config/snds-workspace (H24).

Hooks never exec the live vault tree. A human-run installer `git archive`s the pinned
paths at one commit into lib/<sha>/ (read-only), writes PIN.json and vetted.lock.json,
flips lib/current atomically and copies the byte-stable wrappers into bin/.

  pin_lib.py pin [--sha SHA|HEAD] [--repo DIR] --home DIR [--json]
  pin_lib.py current --home DIR [--json]
  pin_lib.py lag --home DIR [--repo DIR] [--json]
  pin_lib.py --self-test

Exit codes: 0 ok · 1 fail · 2 usage/infrastructure error · 3 nothing pinned · 4 refused.

Real-home guard: every writer takes confirm_real_home=False and agent_check=None. A
`home` that is (or lies inside) the passwd home is written only when confirm_real_home
is True AND the vault profile_resolve.agent_check() says human+determined AND an
injected agent_check (if any) also says human — injection can only tighten. Any error
refuses. For a temporary home only the injected verdict applies (this is how tests run).
The CLI never passes confirm_real_home=True: only installers.py does, after its checks.
Every write goes through one primitive (`_fs`) that independently refuses any path under
the passwd home unless the guard armed it for this call.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import io
import json
import os
import pwd
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
VAULT_ROOT = HERE.parents[1]
VAULT_TOOLS = VAULT_ROOT / "09-tools"

# The one home of the pinned-path list (spec 3c). Absent paths are skipped and listed.
PINNED_PATHS = [
    "09-tools/ws_hook.py",
    "09-tools/profile_resolve.py",
    "09-tools/git_lanes.py",
    "02-shared-references/surfaces.json",
    "02-shared-references/devices.json",
    "02-shared-references/delivery-playbooks/context-remotes.json",
    "02-shared-references/delivery-playbooks/action-policy.json",
    "02-shared-references/vetted-scripts.json",
    "00-bootstrap/dist/ws-hook",
    "00-bootstrap/dist/ws",
]
WRAPPERS = ("ws-hook", "ws")
VETTED_TABLE = "02-shared-references/vetted-scripts.json"
GIT_TIMEOUT = 30


class RefusedError(Exception):
    """A write was refused by the real-home guard (CLI exit 4)."""


class PinError(Exception):
    """Infrastructure error: git failure, missing module, unreadable pin (CLI exit 2)."""


# --------------------------------------------------------------------------- guard

def _import_profile_resolve():
    """Vault consumer import (spec 3d): the vault's own 09-tools, lazily."""
    d = str(VAULT_TOOLS)
    if d not in sys.path:
        sys.path.insert(0, d)
    import profile_resolve  # noqa: PLC0415 — lazy by contract
    return profile_resolve


# Test seam: self-tests swap the loader for a fake (or one that raises ImportError).
_PR_LOADER = _import_profile_resolve


def passwd_home() -> Path:
    return Path(os.path.realpath(pwd.getpwuid(os.getuid()).pw_dir))


def _real(p) -> Path:
    return Path(os.path.realpath(os.path.expanduser(str(p))))


def _under(p: Path, root: Path) -> bool:
    return p == root or root in p.parents


def is_real_home(home) -> bool:
    """True when `home` is the passwd home or lies inside it (fail-closed on error)."""
    try:
        return _under(_real(home), passwd_home())
    except Exception:  # noqa: BLE001 — undeterminable is treated as real
        return True


def _call_verdict(agent_check):
    return agent_check() if callable(agent_check) else agent_check


def verdict_reasons(verdict, label: str) -> list:
    """Refusal reasons for one agent verdict ({human, determined, reasons})."""
    if not isinstance(verdict, dict):
        return [f"{label} verdict unusable"]
    if verdict.get("determined") is not True:
        return [f"{label} verdict: undetermined"]
    if verdict.get("human") is not True:
        why = ", ".join(str(r) for r in (verdict.get("reasons") or [])) or "agent evidence"
        return [f"{label} verdict: agent ({why})"]
    return []


def check_writer(home, *, confirm_real_home=False, agent_check=None) -> list:
    """Every reason the guard refuses a write under `home` (empty list = allowed)."""
    reasons = []
    if is_real_home(home):
        if confirm_real_home is not True:
            reasons.append("real home without confirm_real_home")
        try:
            reasons += verdict_reasons(_PR_LOADER().agent_check(), "vault")
        except Exception as e:  # noqa: BLE001 — ImportError or any error refuses
            reasons.append(f"profile_resolve unavailable ({type(e).__name__})")
    if agent_check is not None:
        try:
            reasons += verdict_reasons(_call_verdict(agent_check), "injected")
        except Exception as e:  # noqa: BLE001
            reasons.append(f"injected verdict error ({type(e).__name__})")
    return reasons


# --------------------------------------------------------------------------- write primitive

_ARMED: dict = {}  # home -> nesting depth


class armed:
    """Context manager: permit primitive writes under `home` for one guarded operation.
    Re-entrant: a nested arming (installers.run arms, then pin() arms again) must not disarm the
    outer one on exit, so each home carries a depth count."""

    def __init__(self, home):
        self.home = _real(home)

    def __enter__(self):
        _ARMED[self.home] = _ARMED.get(self.home, 0) + 1
        return self

    def __exit__(self, *exc):
        n = _ARMED.get(self.home, 0) - 1
        if n > 0:
            _ARMED[self.home] = n
        else:
            _ARMED.pop(self.home, None)
        return False


def _assert_writable(path) -> None:
    p = Path(os.path.realpath(os.path.dirname(os.path.abspath(str(path))))) / os.path.basename(str(path))
    if _under(p, passwd_home()) and not any(_under(p, a) for a in _ARMED):
        raise RefusedError(f"write under the real home is not armed: {p}")


def _fs_impl(op: str, path, *args):
    """The single write primitive. ops: mkdir, write, append, symlink, remove, rmtree,
    chmod, rename. Atomic where it matters (write, symlink)."""
    _assert_writable(path)
    path = str(path)
    if op == "mkdir":
        mode = args[0] if args else 0o755
        if not os.path.isdir(path):
            os.makedirs(path, exist_ok=True)
            os.chmod(path, mode)
    elif op == "write":
        data, mode = args[0], (args[1] if len(args) > 1 else 0o644)
        tmp = f"{path}.ws-tmp.{os.getpid()}"
        with open(tmp, "wb") as f:
            f.write(data)
        os.chmod(tmp, mode)
        os.replace(tmp, path)
    elif op == "append":
        with open(path, "ab") as f:
            f.write(args[0])
    elif op == "symlink":
        tmp = f"{path}.ws-tmp.{os.getpid()}"
        if os.path.lexists(tmp):
            os.unlink(tmp)
        os.symlink(args[0], tmp)
        os.replace(tmp, path)
    elif op == "remove":
        if os.path.lexists(path):
            os.unlink(path)
    elif op == "rmtree":
        if os.path.lexists(path):
            for d, _dirs, _files in os.walk(path):
                os.chmod(d, 0o755)
            shutil.rmtree(path)
    elif op == "chmod":
        os.chmod(path, args[0])
    elif op == "rename":
        _assert_writable(args[0])
        os.replace(path, str(args[0]))
    else:
        raise ValueError(f"unknown fs op {op}")


# Test seam: self-tests wrap this with a spy that fails on any real-home path.
_fs = _fs_impl


def fs(op, path, *args):
    return _fs(op, path, *args)


# --------------------------------------------------------------------------- helpers

def _git(repo, *args, text=True):
    try:
        p = subprocess.run(["git", "-C", str(repo), *args], capture_output=True,
                           text=text, timeout=GIT_TIMEOUT)
    except (OSError, subprocess.SubprocessError) as e:
        raise PinError(f"git {args[0]}: {e}") from e
    if p.returncode != 0:
        err = p.stderr if text else p.stderr.decode("utf-8", "replace")
        raise PinError(f"git {' '.join(args[:2])}: {err.strip()[:200]}")
    return p.stdout


def ws_paths(home) -> dict:
    """Machine paths from the one home, profile_resolve.ws_paths (spec 3d)."""
    try:
        pr = _PR_LOADER()
        raw = pr.ws_paths(home=Path(home))
    except Exception as e:  # noqa: BLE001
        raise PinError(f"profile_resolve.ws_paths unavailable ({type(e).__name__})") from e
    return {k: Path(v) for k, v in raw.items()}


def _utc(now=None) -> str:
    t = now or dt.datetime.now(dt.timezone.utc)
    return t.strftime("%Y-%m-%dT%H:%M:%SZ")


def _json_bytes(obj) -> bytes:
    return (json.dumps(obj, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _safe_member(name: str) -> bool:
    p = Path(name)
    return not p.is_absolute() and ".." not in p.parts


def _extract(tar_bytes: bytes, dest: Path) -> None:
    with tarfile.open(fileobj=io.BytesIO(tar_bytes), mode="r:") as tf:
        for m in tf.getmembers():
            if not _safe_member(m.name):
                raise PinError(f"unsafe archive member {m.name!r}")
            target = dest / m.name
            if m.isdir():
                fs("mkdir", target, 0o755)
            elif m.isfile():
                fs("mkdir", target.parent, 0o755)
                f = tf.extractfile(m)
                fs("write", target, f.read() if f else b"", 0o644)
            # symlinks and specials are never materialized in the pinned lib


def _seal(root: Path) -> None:
    """Files 0444, directories 0555 (bottom-up)."""
    for d, dirs, files in os.walk(root, topdown=False):
        for f in files:
            fs("chmod", Path(d) / f, 0o444)
        for sub in dirs:
            fs("chmod", Path(d) / sub, 0o555)
    fs("chmod", root, 0o555)


def _vetted_lock(repo, sha: str) -> dict:
    scripts = []
    try:
        table = json.loads(_git(repo, "show", f"{sha}:{VETTED_TABLE}"))
    except (PinError, ValueError):
        table = {}
    for s in table.get("scripts", []) if isinstance(table, dict) else []:
        path = s.get("path") if isinstance(s, dict) else None
        if not path:
            continue
        try:
            blob = _git(repo, "rev-parse", f"{sha}:{path}").strip()
        except PinError:
            blob = None
        scripts.append({"id": s.get("id"), "path": path, "blob": blob})
    return {"schema_version": 1, "pinned_sha": sha, "scripts": scripts}


# --------------------------------------------------------------------------- API

def pin(sha="HEAD", *, repo, home, confirm_real_home=False, agent_check=None) -> dict:
    reasons = check_writer(home, confirm_real_home=confirm_real_home, agent_check=agent_check)
    if reasons:
        raise RefusedError("; ".join(reasons))
    with armed(home) if is_real_home(home) else _null():
        return _pin(sha, repo=repo, home=home)


class _null:
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def _pin(sha, *, repo, home) -> dict:
    repo_root = _git(repo, "rev-parse", "--show-toplevel").strip()
    full = _git(repo, "rev-parse", "--verify", f"{sha}^{{commit}}").strip()
    listed = set(_git(repo, "ls-tree", "-r", "--name-only", full, "--", *PINNED_PATHS).splitlines())
    present = [p for p in PINNED_PATHS if p in listed]
    absent = [p for p in PINNED_PATHS if p not in listed]
    paths = ws_paths(home)
    base, lib = paths["base"], paths["lib_current"].parent
    fs("mkdir", base, 0o755)
    for d, mode in ((paths["bin"], 0o755), (lib, 0o755), (paths["control"], 0o700),
                    (paths["telemetry"], 0o755)):
        fs("mkdir", d, mode)
    dest = lib / full
    reused = (dest / "PIN.json").is_file()
    if not reused:
        tmp = lib / f".{full}.tmp.{os.getpid()}"
        fs("rmtree", tmp)
        fs("mkdir", tmp, 0o755)
        if present:
            _extract(_git(repo, "archive", "--format=tar", full, "--", *present, text=False), tmp)
        pin_doc = {"schema_version": 1, "sha": full, "pinned_at": _utc(),
                   "repo_root": repo_root, "paths": present}
        fs("write", tmp / "PIN.json", _json_bytes(pin_doc), 0o644)
        fs("write", tmp / "vetted.lock.json", _json_bytes(_vetted_lock(repo, full)), 0o644)
        _seal(tmp)
        if dest.exists():
            fs("rmtree", dest)
        fs("rename", tmp, dest)
    fs("symlink", paths["lib_current"], full)
    bin_updated = []
    for name in WRAPPERS:
        src = dest / "00-bootstrap" / "dist" / name
        if not src.is_file():
            continue
        data = src.read_bytes()
        tgt = paths["bin"] / name
        if not tgt.is_file() or tgt.read_bytes() != data:
            fs("write", tgt, data, 0o755)
            bin_updated.append(name)
        elif not os.access(tgt, os.X_OK):
            fs("chmod", tgt, 0o755)
    root_line = (repo_root + "\n").encode("utf-8")
    rf = paths["root_file"]
    if not rf.is_file() or rf.read_bytes() != root_line:
        fs("write", rf, root_line, 0o644)
    return {"schema_version": 1, "cmd": "pin", "sha": full, "lib": str(dest), "paths": present,
            "absent": absent, "reused": reused, "bin_updated": bin_updated}


def current(*, home) -> dict:
    paths = ws_paths(home)
    link = paths["lib_current"]
    if not link.exists():
        return {"schema_version": 1, "cmd": "current", "pinned": False}
    try:
        pin_doc = json.loads((link / "PIN.json").read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise PinError(f"unreadable PIN.json: {e}") from e
    try:
        lock = json.loads((link / "vetted.lock.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        lock = None
    return {"schema_version": 1, "cmd": "current", "pinned": True, "sha": pin_doc.get("sha"),
            "pin": pin_doc, "lock": lock}


def lag(*, home, repo) -> dict:
    cur = current(home=home)
    if not cur.get("pinned"):
        return {"schema_version": 1, "cmd": "lag", "pinned": False}
    pinned = cur["sha"]
    head = _git(repo, "rev-parse", "HEAD").strip()
    behind = int(_git(repo, "rev-list", "--count", f"{pinned}..{head}", "--", *PINNED_PATHS).strip() or 0)
    changed = [p for p in _git(repo, "diff", "--name-only", pinned, head, "--", *PINNED_PATHS).splitlines() if p]
    return {"schema_version": 1, "cmd": "lag", "pinned": True, "pinned_sha": pinned,
            "head_sha": head, "commits_behind_on_pinned_paths": behind, "changed_paths": changed}


# --------------------------------------------------------------------------- CLI

def _emit(obj: dict, as_json: bool) -> None:
    if as_json:
        print(json.dumps(obj, indent=2))
        return
    for k, v in obj.items():
        if k in ("schema_version", "cmd"):
            continue
        print(f"{k}: {v if not isinstance(v, (list, dict)) else json.dumps(v)}")


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv[:1] == ["--self-test"]:
        return self_test()
    ap = argparse.ArgumentParser(prog="pin_lib.py")
    sub = ap.add_subparsers(dest="cmd")
    p = sub.add_parser("pin")
    p.add_argument("--sha", default="HEAD")
    p.add_argument("--repo", default=str(VAULT_ROOT))
    p.add_argument("--home", required=True)
    p.add_argument("--json", action="store_true")
    c = sub.add_parser("current")
    c.add_argument("--home", required=True)
    c.add_argument("--json", action="store_true")
    lg = sub.add_parser("lag")
    lg.add_argument("--home", required=True)
    lg.add_argument("--repo", default=str(VAULT_ROOT))
    lg.add_argument("--json", action="store_true")
    try:
        a = ap.parse_args(argv)
    except SystemExit:
        return 2
    if not a.cmd:
        ap.print_usage(sys.stderr)
        return 2
    try:
        if a.cmd == "pin":
            _emit(pin(a.sha, repo=a.repo, home=a.home), a.json)
            return 0
        if a.cmd == "current":
            r = current(home=a.home)
        else:
            r = lag(home=a.home, repo=a.repo)
        _emit(r, a.json)
        return 0 if r.get("pinned") else 3
    except RefusedError as e:
        print(f"pin refused: {e}", file=sys.stderr)
        return 4
    except PinError as e:
        print(f"pin_lib: {e}", file=sys.stderr)
        return 2


# --------------------------------------------------------------------------- self-test

def fake_profile_resolve(verdict=None):
    """A stand-in for profile_resolve (T2) used by T3's own self-tests only."""
    import types

    def _ws_paths(*, home=None):
        b = Path(home) / ".config" / "snds-workspace"
        return {"base": b, "root_file": b / "root", "bin": b / "bin",
                "lib_current": b / "lib" / "current", "control": b / "control",
                "telemetry": b / "telemetry"}

    v = verdict if verdict is not None else {"human": False, "determined": True,
                                             "reasons": ["fake: agent"]}
    return types.SimpleNamespace(
        agent_check=lambda **_kw: dict(v),
        ws_paths=_ws_paths,
        current_device=lambda **_kw: {"id": "dev-a", "label": "Device A"},
        load_table=lambda name, **_kw: {},
    )


HUMAN = {"human": True, "determined": True, "reasons": []}
AGENT = {"human": False, "determined": True, "reasons": ["env:CURSOR_AGENT"]}
UNDETERMINED = {"human": False, "determined": False, "reasons": ["no evidence"]}


class FsSpy:
    """Wraps the write primitive: records every call and raises on any real-home path."""

    def __init__(self, inner):
        self.inner, self.calls = inner, []
        self.real = passwd_home()

    def __call__(self, op, path, *args):
        self.calls.append((op, str(path)))
        for p in [path] + ([args[0]] if op == "rename" else []):
            rp = Path(os.path.realpath(os.path.dirname(os.path.abspath(str(p)))))
            if _under(rp, self.real):
                raise AssertionError(f"write primitive reached the real home: {op} {p}")
        return self.inner(op, path, *args)


def hermetic_git_env() -> dict:
    """Fixture git never sees the runner's global/system config, hooks or overlay env."""
    env = {k: v for k, v in os.environ.items()
           if not k.startswith(("GIT_CONFIG", "GIT_AUTHOR_", "GIT_COMMITTER_", "GIT_DIR",
                                "GIT_WORK_TREE", "GIT_INDEX"))}
    env.update({"GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"})
    return env


def _fixture_git(*args) -> None:
    subprocess.run(["git", "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                    "-c", "commit.gpgsign=false", "-c", "core.hooksPath=/dev/null", *args],
                   check=True, timeout=GIT_TIMEOUT, env=hermetic_git_env(),
                   stdout=subprocess.DEVNULL)


def make_repo(td: Path, files: dict) -> Path:
    repo = td / "repo"
    repo.mkdir()
    _fixture_git("init", "-q", "-b", "main", str(repo))
    for rel, data in files.items():
        p = repo / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data if isinstance(data, bytes) else data.encode("utf-8"))
    commit_all(repo, "fixture")
    return repo


def commit_all(repo: Path, msg: str) -> None:
    _fixture_git("-C", str(repo), "add", "-A")
    _fixture_git("-C", str(repo), "commit", "-q", "-m", msg)


FIXTURE_FILES = {
    "09-tools/ws_hook.py": "print('fixture ws_hook')\n",
    "02-shared-references/surfaces.json": '{"schema_version": 1}\n',
    "02-shared-references/vetted-scripts.json": json.dumps(
        {"schema_version": 1, "scripts": [{"id": "prune-our-branches",
                                           "path": "09-tools/prune-our-branches.py"}]}) + "\n",
    "09-tools/prune-our-branches.py": "print('fixture prune')\n",
    "00-bootstrap/dist/ws-hook": "#!/bin/sh\nexit 0\n",
    "00-bootstrap/dist/ws": "#!/bin/sh\nexit 2\n",
    "README.md": "fixture\n",
}


def self_test() -> int:
    import tempfile
    import unittest

    class TestPinLib(unittest.TestCase):
        def setUp(self):
            global _PR_LOADER, _fs
            self._saved = (_PR_LOADER, _fs)
            _PR_LOADER = lambda: fake_profile_resolve()  # noqa: E731
            self.spy = FsSpy(_fs_impl)
            _fs = self.spy
            self.td = Path(tempfile.mkdtemp(prefix="pinlib-"))
            self.home = self.td / "home"
            self.home.mkdir()
            self.repo = make_repo(self.td, FIXTURE_FILES)

        def tearDown(self):
            global _PR_LOADER, _fs
            _PR_LOADER, _fs = self._saved
            for d, _dirs, _files in os.walk(self.td):
                os.chmod(d, 0o755)
            shutil.rmtree(self.td, ignore_errors=True)

        def base(self):
            return self.home / ".config" / "snds-workspace"

        def test_pin_layout_modes_and_records(self):
            r = pin(repo=self.repo, home=self.home, agent_check=lambda: HUMAN)
            b = self.base()
            self.assertTrue((b / "lib" / "current").is_symlink())
            cur = b / "lib" / "current"
            self.assertEqual((cur / "09-tools" / "ws_hook.py").read_text(), "print('fixture ws_hook')\n")
            self.assertIn("09-tools/profile_resolve.py", r["absent"])
            self.assertIn("02-shared-references/devices.json", r["absent"])
            self.assertEqual(oct((cur / "09-tools" / "ws_hook.py").stat().st_mode & 0o777), "0o444")
            self.assertEqual(oct((cur / "09-tools").stat().st_mode & 0o777), "0o555")
            self.assertEqual(oct((b / "control").stat().st_mode & 0o777), "0o700")
            self.assertEqual(oct((b / "telemetry").stat().st_mode & 0o777), "0o755")
            doc = json.loads((cur / "PIN.json").read_text())
            self.assertEqual(sorted(doc), ["paths", "pinned_at", "repo_root", "schema_version", "sha"])
            self.assertEqual(doc["sha"], r["sha"])
            lock = json.loads((cur / "vetted.lock.json").read_text())
            blob = _git(self.repo, "rev-parse", f"{r['sha']}:09-tools/prune-our-branches.py").strip()
            self.assertEqual(lock["scripts"][0]["blob"], blob)
            self.assertEqual((b / "bin" / "ws-hook").read_bytes(), b"#!/bin/sh\nexit 0\n")
            self.assertTrue(os.access(b / "bin" / "ws-hook", os.X_OK))
            self.assertEqual((b / "root").read_text().strip(),
                             _git(self.repo, "rev-parse", "--show-toplevel").strip())
            self.assertEqual(current(home=self.home)["sha"], r["sha"])

        def test_vault_edit_leaves_pinned_bytes(self):
            pin(repo=self.repo, home=self.home, agent_check=lambda: HUMAN)
            cur = self.base() / "lib" / "current" / "09-tools" / "ws_hook.py"
            before = cur.read_bytes()
            (self.repo / "09-tools" / "ws_hook.py").write_text("print('edited')\n")
            self.assertEqual(cur.read_bytes(), before)       # working-tree edit
            commit_all(self.repo, "edit")
            self.assertEqual(cur.read_bytes(), before)       # committed edit
            lg = lag(home=self.home, repo=self.repo)
            self.assertEqual(lg["commits_behind_on_pinned_paths"], 1)
            self.assertEqual(lg["changed_paths"], ["09-tools/ws_hook.py"])
            (self.repo / "README.md").write_text("other\n")
            commit_all(self.repo, "unpinned edit")
            self.assertEqual(lag(home=self.home, repo=self.repo)["commits_behind_on_pinned_paths"], 1)

        def test_repin_flips_current_and_skips_identical_wrappers(self):
            r1 = pin(repo=self.repo, home=self.home, agent_check=lambda: HUMAN)
            (self.repo / "09-tools" / "ws_hook.py").write_text("print('v2')\n")
            commit_all(self.repo, "v2")
            r2 = pin(repo=self.repo, home=self.home, agent_check=lambda: HUMAN)
            self.assertNotEqual(r1["sha"], r2["sha"])
            self.assertEqual(os.readlink(self.base() / "lib" / "current"), r2["sha"])
            self.assertEqual(r2["bin_updated"], [])
            self.assertTrue((self.base() / "lib" / r1["sha"] / "PIN.json").is_file())
            self.assertEqual(lag(home=self.home, repo=self.repo)["commits_behind_on_pinned_paths"], 0)

        def test_temp_home_injected_verdicts(self):
            for v in (AGENT, UNDETERMINED):
                with self.assertRaises(RefusedError):
                    pin(repo=self.repo, home=self.home, agent_check=lambda v=v: v)
            self.assertFalse(self.base().exists())

        def test_nothing_pinned(self):
            self.assertFalse(current(home=self.home)["pinned"])
            self.assertEqual(main(["current", "--home", str(self.home)]), 3)
            self.assertEqual(main(["lag", "--home", str(self.home), "--repo", str(self.repo)]), 3)

        # ---- real-home guard: the write spy must never be reached ----
        def _assert_real_home_refused(self, **kw):
            global _PR_LOADER
            real = passwd_home()
            n = len(self.spy.calls)
            with self.assertRaises(RefusedError) as cm:
                pin(repo=self.repo, home=real, **kw)
            self.assertEqual(len(self.spy.calls), n, "write primitive reached")
            return str(cm.exception)

        def test_nested_arming_survives_inner_exit(self):
            # installers.run arms the home, then pin() arms it again; the inner exit must not
            # disarm the outer guard (the 2026-09-24 re-pin logged nothing for this reason).
            g = globals()
            saved = g["passwd_home"]
            g["passwd_home"] = lambda: _real(self.home)
            try:
                target = self.base() / "control" / "probe.txt"
                with armed(self.home):
                    with armed(self.home):
                        fs("mkdir", self.base(), 0o755)
                    fs("mkdir", target.parent, 0o700)
                    fs("append", target, b"after inner exit\n")
                self.assertEqual(target.read_bytes(), b"after inner exit\n")
                with self.assertRaises(RefusedError):
                    fs("append", target, b"after outer exit\n")
                self.assertEqual(_ARMED, {})
            finally:
                g["passwd_home"] = saved

        def test_real_home_without_confirm(self):
            msg = self._assert_real_home_refused()
            self.assertIn("confirm_real_home", msg)

        def test_real_home_confirm_with_injected_agent(self):
            msg = self._assert_real_home_refused(confirm_real_home=True, agent_check=lambda: AGENT)
            self.assertIn("injected verdict: agent", msg)

        def test_real_home_confirm_profile_resolve_unimportable(self):
            global _PR_LOADER

            def boom():
                raise ImportError("no profile_resolve")
            _PR_LOADER = boom
            msg = self._assert_real_home_refused(confirm_real_home=True)
            self.assertIn("profile_resolve unavailable (ImportError)", msg)

        def test_real_home_cli_refuses(self):
            self.assertEqual(main(["pin", "--home", str(passwd_home()), "--repo", str(self.repo)]), 4)

        def test_primitive_guard_refuses_unarmed_real_home(self):
            # Only the pure check is exercised; no write op is ever issued at the real home.
            with self.assertRaises(RefusedError):
                _assert_writable(passwd_home() / ".never-written")
            _assert_writable(self.home / "ok")

        def test_is_real_home(self):
            self.assertTrue(is_real_home(passwd_home()))
            self.assertTrue(is_real_home(passwd_home() / ".config"))
            self.assertFalse(is_real_home(self.home))

    suite = unittest.TestLoader().loadTestsFromTestCase(TestPinLib)
    res = unittest.TextTestRunner(verbosity=1).run(suite)
    return 0 if res.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
