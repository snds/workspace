"""dispatcher.py --self-test (H1 dispatcher side, H19 wiring, D14 devices wiring).

Runs the REAL dispatcher as a subprocess against temp repos (CLAUDE_PROJECT_DIR points at
the temp repo), with contract-shaped fake ws_hook/profile_resolve modules written into
the temp repo's 09-tools/. T5 ships its own payload copies in ./payloads; after T9a the
integrated TestDispatcherDefer loads T1's golden payloads instead."""

from __future__ import annotations

import importlib.util
import json
import socket
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import nightly_fixture_lib as fx  # noqa: E402

LEGACY_MAP_NAME = "HOSTNAME" + "_MAP"  # built at runtime so this file never contains it


def _repo(path: Path, env: dict, *, fakes: bool = True) -> Path:
    path.mkdir(parents=True)
    (path / ".gitignore").write_text(fx.GITIGNORE, encoding="utf-8")
    (path / "README.md").write_text("fixture repo\n", encoding="utf-8")
    (path / "06-context" / "sessions").mkdir(parents=True)
    (path / "06-context" / "sessions" / ".keep").write_text("", encoding="utf-8")
    if fakes:
        fx.install_fakes(path)
    fx.git(path, "init", "-q", "-b", "main", env=env)
    fx.git(path, "add", "-A", env=env)
    fx.git(path, "commit", "-q", "-m", "fixture: base", env=env)
    return path


def _run(dispatcher: Path, repo: Path, env: dict, event: str | None, pl: dict | None = None,
         extra_env: dict | None = None):
    denv = dict(env, CLAUDE_PROJECT_DIR=str(repo), **(extra_env or {}))
    args = [event] if event else []
    return fx.py(dispatcher, *args, cwd=repo, env=denv, stdin=json.dumps(pl or {}), timeout=90)


def _detect_called(repo: Path) -> bool:
    return (repo / ".workspace" / "detect-called").is_file()


def case_defer(c: fx.Checks, d: Path, tmp: Path, env: dict) -> None:
    repo = _repo(tmp / "defer", env)
    # Claude Code payload: proceeds, and no detection (ancestry) walk runs.
    r = _run(d, repo, env, "pre-tool", fx.payload("claude-code.pre-tool"))
    c.check(r.returncode == 0 and "permissionDecision" in r.stdout,
            "Claude Code payload proceeds (the Figma gate fires)", r.stderr[-200:])
    c.check(not _detect_called(repo), "no detect_surface/ps walk when the payload says claude-code")
    for name in ("cursor.pre-tool", "cursor.session-start", "copilot-vscode.pre-tool",
                 "copilot-vscode.session-start"):
        event = "pre-tool" if name.endswith("pre-tool") else "session-start"
        r = _run(d, repo, env, event, fx.payload(name))
        c.check(r.returncode == 0 and r.stdout == "", f"{name} payload exits 0 silently",
                (r.stdout + r.stderr)[-200:])
    bare = {"tool_name": "mcp__figma__use_figma", "tool_input": {}}
    r = _run(d, repo, env, "pre-tool", dict(bare, session_id="unverified-env"),
             {"CODEX_THREAD_ID": "x"})
    c.check(r.returncode == 0 and "permissionDecision" in r.stdout,
            "an unverified env marker alone does not defer", r.stderr[-200:])
    r = _run(d, repo, env, "pre-tool", dict(bare, session_id="verified-env"), {"CURSOR_AGENT": "1"})
    c.check(r.returncode == 0 and r.stdout == "", "a verified env marker (CURSOR_AGENT=1) defers")
    # No resolver modules at all: fail open (today's behaviour), even for a Cursor payload.
    plain = _repo(tmp / "defer-nofakes", env, fakes=False)
    r = _run(d, plain, env, "pre-tool", fx.payload("cursor.pre-tool"))
    c.check(r.returncode == 0 and "permissionDecision" in r.stdout,
            "missing ws_hook/profile_resolve: proceeds (fail-open)", r.stderr[-200:])


def case_events(c: fx.Checks, d: Path, tmp: Path, env: dict) -> None:
    repo = _repo(tmp / "events", env)
    r = _run(d, repo, env, "no-such-event", {})
    c.check(r.returncode == 0 and "unknown event" in r.stderr, "an unknown event exits 0 with a note",
            f"rc={r.returncode} {r.stderr[-120:]}")
    r = _run(d, repo, env, None, {})
    c.check(r.returncode == 0, "no event argument exits 0", f"rc={r.returncode}")


def case_session_start(c: fx.Checks, d: Path, tmp: Path, env: dict) -> None:
    repo = _repo(tmp / "ws", env)
    sibling = tmp / "ws.intent-x"
    fx.git(repo, "worktree", "add", "-q", "-b", "intent/x", str(sibling), env=env)
    nested = repo / ".claude" / "worktrees" / "merged"
    fx.git(repo, "worktree", "add", "-q", "-b", "merged-nested", str(nested), env=env)
    pl = fx.payload("claude-code.session-start")
    r = _run(d, repo, env, "session-start", pl)
    c.check(r.returncode == 0 and "hookSpecificOutput" in r.stdout,
            "Claude Code session-start emits the context card", r.stderr[-200:])
    c.check(sibling.is_dir() and fx.git(repo, "rev-parse", "--verify", "-q", "intent/x", env=env,
                                        check=False).returncode == 0,
            "a sibling <root>.intent-x worktree with an empty branch is never removed")
    c.check(not nested.exists(), "a nested, fully merged worktree is still cleaned (control)")
    base = repo / ".workspace" / "state" / "sessions" / f"{pl['session_id']}.json"
    c.check(base.is_file(), "session-start writes the session baseline via ws_hook.write_baseline")
    # SessionEnd on intent/x makes no commit.
    (sibling / "wip.md").write_text("implementor work\n", encoding="utf-8")
    head = fx.git(sibling, "rev-parse", "HEAD", env=env).stdout.strip()
    r = _run(d, sibling, env, "session-end", fx.payload("claude-code.session-end"))
    c.check(r.returncode == 0 and "intent/" in r.stderr, "SessionEnd on intent/x prints a notice",
            r.stderr[-200:])
    c.check(fx.git(sibling, "rev-parse", "HEAD", env=env).stdout.strip() == head and
            (sibling / "wip.md").is_file() and
            "wip.md" in fx.git(sibling, "status", "--porcelain", env=env).stdout,
            "SessionEnd on intent/x makes no commit and leaves the work dirty")


def case_session_end_label(c: fx.Checks, d: Path, tmp: Path, env: dict) -> None:
    repo = _repo(tmp / "label", env)
    (repo / "README.md").write_text("edited\n", encoding="utf-8")
    pl = fx.payload("claude-code.session-end")
    (repo / "06-context" / "sessions" / f"{pl['session_id']}.touched").write_text(
        "README.md\n", encoding="utf-8")
    r = _run(d, repo, env, "session-end", pl)
    msg = fx.git(repo, "log", "-1", "--format=%s", env=env).stdout.strip()
    c.check(r.returncode == 0 and "Fixture Device A" in msg,
            "session-end label comes from devices.json (via profile_resolve)", msg)
    c.check(msg.endswith("(scoped)"), "nightly.py absent: fail-open fallback still commits scoped",
            msg)
    gate = repo / ".workspace" / "state" / "last-gate.json"
    try:
        g = json.loads(gate.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        g = {}
    head = fx.git(repo, "rev-parse", "HEAD", env=env).stdout.strip()
    c.check(g.get("head") == head and g.get("nightly", {}).get("status") == "skipped",
            "last-gate.json written for the commit (skipped: no nightly)", str(g)[:160])
    plain = _repo(tmp / "label-plain", env, fakes=False)
    (plain / "README.md").write_text("edited\n", encoding="utf-8")
    r = _run(d, plain, env, "session-end", pl)
    msg = fx.git(plain, "log", "-1", "--format=%s", env=env).stdout.strip()
    short = socket.gethostname().split(".")[0]
    c.check(r.returncode == 0 and f"from {short} @" in msg,
            "no resolver: label falls back to the raw short hostname", msg)


def case_no_legacy_map(c: fx.Checks, d: Path) -> None:
    setup = d.parents[2] / "00-bootstrap" / "setup" / "setup.py"
    for p in (d, setup):
        try:
            text = p.read_text(encoding="utf-8")
        except OSError:
            c.check(False, f"{p.name} readable")
            continue
        c.check(LEGACY_MAP_NAME not in text, f"no {LEGACY_MAP_NAME} remains in {p.name}")


def case_setup_labels(c: fx.Checks, d: Path, tmp: Path, env: dict) -> None:
    setup_path = d.parents[2] / "00-bootstrap" / "setup" / "setup.py"
    spec = importlib.util.spec_from_file_location("ws_setup_fixture", setup_path)
    if spec is None or spec.loader is None:
        c.check(False, "setup.py importable")
        return
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    root = tmp / "setup-root"
    fx.install_fakes(root)
    saved = list(sys.path)
    # Hermetic import path: drop any directory that already holds a real profile_resolve.
    clean = [p for p in saved if not (Path(p or ".") / "profile_resolve.py").is_file()]
    try:
        sys.path[:] = clean
        sys.modules.pop("profile_resolve", None)
        c.check(mod.detect_machine_label(root=root) == "Fixture Device A",
                "setup.py label comes from devices.json (via profile_resolve)")
        c.check(mod.hostname_known(root=root) is True, "setup.py hostname_known via current_device")
        sys.path[:] = clean
        sys.modules.pop("profile_resolve", None)
        empty = tmp / "setup-empty"
        (empty / "09-tools").mkdir(parents=True)
        short = socket.gethostname().split(".")[0]
        got = mod.detect_machine_label(root=empty)
        c.check(got == short, "setup.py falls back to the raw short hostname", got)
        c.check(mod.hostname_known(root=empty) is None, "setup.py: no resolver → hostname unknown")
    finally:
        sys.modules.pop("profile_resolve", None)
        sys.path[:] = saved


def run(dispatcher: Path) -> int:
    c = fx.Checks("dispatcher self-test")
    with tempfile.TemporaryDirectory(prefix="dispatcher-selftest-") as td:
        tmp = Path(td)
        home = tmp / "home"
        home.mkdir()
        stubs = fx.make_stubs(tmp)
        env = fx.hermetic_env(home, stubs)
        for name, fn in (("case_defer", case_defer), ("case_events", case_events),
                         ("case_session_start", case_session_start),
                         ("case_session_end_label", case_session_end_label),
                         ("case_setup_labels", case_setup_labels)):
            print(f"· {name}")
            try:
                fn(c, dispatcher, tmp, env)
            except Exception as exc:  # noqa: BLE001
                c.check(False, f"{name} ran", repr(exc))
        print("· case_no_legacy_map")
        case_no_legacy_map(c, dispatcher)
        for name in ("launchctl", "gh", "osascript"):
            c.check(fx.stub_calls(stubs, name) == 0, f"stub `{name}` never called")
    return c.result()


if __name__ == "__main__":
    sys.exit(run(HERE.parents[2] / ".claude" / "hooks" / "dispatcher.py"))
