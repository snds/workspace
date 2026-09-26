"""Temp-HOME fixtures for the H11 gate lanes (git_lanes.py post-commit + pre-push, ws_hook stop notices).

Same world as lane_cases.py (its Lab: a synthetic pinned lib, the lanes installed by the REAL installer,
local bare remotes, synthetic owners only). The workspace-shaped checkout gets a stand-in nightly.py
that answers the H1 lane and the H11 verify: `--phases verify --from-diff ...` prints a nightly JSON
report, red while $HOME/gate-red exists, and appends one line per verify to $HOME/verify-calls (so tree
reuse is counted, not assumed). Nothing touches the real HOME or any real checkout.

Each case is (name, passed, detail); passed None is a SKIP (git < 2.54), never a pass. Used by
TestGateLanes in test-validators.py and by `git_lanes.py --self-test` (through lane_cases.run_all).
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
import re
import shutil
import sys
import tempfile
import time
from pathlib import Path

FX = Path(__file__).resolve().parent
ROOT = FX.parents[2]
TOOLS = ROOT / "09-tools"

GATE_NIGHTLY = ('import json, os, sys\n'
                'home = os.environ["HOME"]\n'
                'if "--lane" in sys.argv:\n'
                '    sys.exit(1 if os.path.exists(os.path.join(home, "heal-stale")) else 0)\n'
                'with open(os.path.join(home, "verify-calls"), "a") as fh:\n'
                '    fh.write(" ".join(sys.argv[1:]) + "\\n")\n'
                'red = os.path.exists(os.path.join(home, "gate-red"))\n'
                'print(json.dumps({"status": "fail" if red else "ok", "phases": [{"phase": "verify", '
                '"charged": ["build-registry.py"] if red else []}]}))\n'
                'sys.exit(1 if red else 0)\n')
SUFFIX_RE = re.compile(r"\[gate:[^\]]+\]")
CASES = [
    "post-commit: a workspace commit detaches the verify and last-gate.json records HEAD's tree (via post-commit)",
    "parity: the pre-push [gate:...] suffix is identical under the human, Claude, Cursor and Codex chains "
    "(a reused post-commit verdict)",
    "parity: a fresh pre-push verify gives the same suffix under every chain, and the tree is verified once",
    "tree-hash reuse: a tree already verified is never verified again (verify calls counted)",
    "report-only: a red verify never blocks a push by default; the line says report-only",
    "ws.pushgate block (installer =block): a red verify holds the push [GATE], the remote ref is unchanged, "
    "the hold is in the ring; a green tree pushes",
    "bypass: WS_GATE_BYPASS under an agent chain (Cursor) is refused, the push stays held and the refusal is a "
    "receipt; with no process table (undetermined) it is refused too",
    "bypass: with no agent in the ancestry (in-process ancestry) WS_GATE_BYPASS lets the held push through, "
    "recorded in receipts.jsonl and the ring",
    "kill switch: WS_PUSH_GATE=off pushes a red tree under block mode without running a verify",
    "ws.pushgate at repo scope never enables the hold (report-only, with a notice) and the audit names it",
    "stop hooks: at most one notice line per call, once per session; Cursor stdout stays the {} no-op (no "
    "followup_message), Codex stdout stays empty (no continue/decision), Claude gets one systemMessage; a "
    "session outside the workspace gets nothing",
    "post-commit: quiet while a rebase, cherry-pick, am or revert replays commits; `commit (amend)` is not one",
    "WS_GATE_NOWAIT (report-only, the SessionEnd push): an unverified tree pushes at once with a pending line; "
    "the detached verify still records that tree's verdict (via pre-push), exactly once",
    "WS_GATE_NOWAIT under ws.pushgate block is ignored: a red tree stays held",
]


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(str(path))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def _suffix(text: str) -> str:
    found = SUFFIX_RE.findall(text or "")
    return found[-1] if found else ""


def _calls(home: Path) -> int:
    p = home / "verify-calls"
    return len(p.read_text(encoding="utf-8").splitlines()) if p.exists() else 0


def _receipts(ws: Path) -> list:
    p = ws / ".workspace" / "state" / "receipts.jsonl"
    if not p.exists():
        return []
    return [json.loads(ln) for ln in p.read_text(encoding="utf-8").splitlines() if ln.strip()]


def _gate(ws: Path) -> dict:
    try:
        return json.loads((ws / ".workspace" / "state" / "last-gate.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def gate_cases() -> list:
    lc = _load(FX / "lane_cases.py", "gate_fx_lane_cases")
    if lc.git_version() < (2, 54):
        v = ".".join(map(str, lc.git_version()))
        return [(n, None, f"git {v} < 2.54 (config-based hooks)") for n in CASES]
    out = []
    td = tempfile.mkdtemp(prefix="ws-gate-")
    try:
        lab = lc.Lab(Path(os.path.realpath(td)))
        rc, log = lab.install()
        if rc != 0:
            return [(n, False, f"install rc={rc} {log[-300:]}") for n in CASES]
        ws, home = lab.ws, lab.home
        (ws / "09-tools" / "nightly.py").write_text(GATE_NIGHTLY, encoding="utf-8")
        (ws / ".gitignore").write_text(".workspace/\n", encoding="utf-8")
        setup = dict(lab.ident(lab.env, "pat"), GIT_CONFIG_GLOBAL="/dev/null")
        url = ["-c", f"url.file://{lab.bare_root}/.insteadOf=git@github.com:"]
        lab.g(setup, "add", "-A", cwd=ws)
        lab.g(setup, "commit", "-q", "-m", "base", cwd=ws)
        lab.g(setup, *url, "push", "-q", "-u", "origin", "main", cwd=ws)
        lab.g(lab.env, "config", "user.name", "Pat Sample", cwd=ws)
        lab.g(lab.env, "config", "user.email", lab.mail("pat"), cwd=ws)
        chains = {"human": lab.env, "claude": dict(lab.env, WS_SURFACE_FAMILY="claude"),
                  "cursor": dict(lab.env, CURSOR_AGENT="1"), "codex": dict(lab.env, CODEX_THREAD_ID="fx-thread")}
        off = dict(lab.env, WS_PUSH_GATE="off")
        n = [0]

        def commit(env, red: bool):
            n[0] += 1
            (home / "gate-red").write_text("1") if red else (home / "gate-red").unlink(missing_ok=True)
            (ws / f"change-{n[0]}.txt").write_text(f"{n[0]}\n", encoding="utf-8")
            lab.g(env, "add", f"change-{n[0]}.txt", cwd=ws)
            return lab.g(env, "commit", "-q", "-m", f"change {n[0]}", cwd=ws)

        def head():
            return lab.g(lab.env, "rev-parse", "HEAD", cwd=ws).stdout.strip()

        def tree():
            return lab.g(lab.env, "rev-parse", "HEAD^{tree}", cwd=ws).stdout.strip()

        def remote():
            return lab.ref("pat-sample/ws", "main")

        def prepush(env):
            ref = lab.tmp / "refs.txt"
            ref.write_text(f"refs/heads/main {head()} refs/heads/main {remote()}\n", encoding="utf-8")
            return lab.g(env, "hook", "run", f"--to-stdin={ref}", "pre-push", "--", "origin",
                         "git@github.com:pat-sample/ws.git", cwd=ws)

        # post-commit: detached verify, recorded for HEAD's tree
        r = commit(lab.env, red=True)
        t1 = tree()
        deadline = time.monotonic() + 60
        while time.monotonic() < deadline and _gate(ws).get("tree") != t1:
            time.sleep(0.25)
        g = _gate(ws)
        out.append((CASES[0], r.returncode == 0 and "verify started in the background" in r.stderr
                    and g.get("tree") == t1 and (g.get("gate") or {}).get("via") == "post-commit"
                    and (g.get("gate") or {}).get("status") == "red",
                    f"rc={r.returncode} {r.stderr[-200:]} gate={json.dumps(g.get('gate'))[:200]}"))

        # parity over a reused verdict
        calls0 = _calls(home)
        res = {name: prepush(env) for name, env in chains.items()}
        sfx = {name: _suffix(x.stderr) for name, x in res.items()}
        want = f"[gate:red:build-registry.py@{t1[:12]}]"
        out.append((CASES[1], all(x.returncode == 0 for x in res.values()) and set(sfx.values()) == {want},
                    f"suffixes={sfx} rc={[x.returncode for x in res.values()]}"))
        reuse_ok = _calls(home) == calls0

        # parity over a fresh verify (post-commit switched off for this commit)
        commit(off, red=False)
        t2 = tree()
        calls1 = _calls(home)
        res = {name: prepush(env) for name, env in chains.items()}
        sfx = {name: _suffix(x.stderr) for name, x in res.items()}
        out.append((CASES[2], set(sfx.values()) == {f"[gate:green@{t2[:12]}]"} and _calls(home) == calls1 + 1
                    and "(reused)" in res["codex"].stderr,
                    f"suffixes={sfx} calls={_calls(home) - calls1}"))
        out.append((CASES[3], reuse_ok and _calls(home) == calls1 + 1, f"calls0={calls0} calls1={calls1} "
                                                                      f"now={_calls(home)}"))

        # report-only: a red push goes through
        commit(off, red=True)
        before = remote()
        r = lab.g(chains["cursor"], "push", "origin", "main", cwd=ws)
        out.append((CASES[4], r.returncode == 0 and remote() == head() != before and "report-only" in r.stderr
                    and _suffix(r.stderr).startswith("[gate:red:build-registry.py@"),
                    f"rc={r.returncode} {r.stderr[-300:]}"))

        # NOWAIT (report-only): no record for the tree -> push at once, the verify detaches and records
        commit(off, red=True)
        t_nw, calls_nw = tree(), _calls(home)
        r = lab.g(dict(chains["claude"], WS_GATE_NOWAIT="1"), "push", "origin", "main", cwd=ws)
        deadline = time.monotonic() + 60
        while time.monotonic() < deadline and not any(
                x.get("tree") == t_nw and x.get("status") == "red" for x in _gate(ws).get("ring") or []):
            time.sleep(0.25)
        time.sleep(0.5)
        rec_nw = [x for x in _gate(ws).get("ring") or [] if x.get("tree") == t_nw]
        out.append((CASES[12], r.returncode == 0 and remote() == head() and "not awaited" in r.stderr
                    and _suffix(r.stderr) == f"[gate:pending@{t_nw[:12]}]" and len(rec_nw) == 1
                    and rec_nw[0].get("via") == "pre-push" and rec_nw[0].get("status") == "red"
                    and _calls(home) == calls_nw + 1,
                    f"rc={r.returncode} {r.stderr[-240:]} ring={rec_nw} calls={_calls(home) - calls_nw}"))

        # block mode through the real installer
        rc_b, log_b = lab.install("git-hooks=block")
        commit(off, red=True)
        held_head, before = head(), remote()
        r_nw = lab.g(dict(chains["claude"], WS_GATE_NOWAIT="1"), "push", "origin", "main", cwd=ws)
        out.append((CASES[13], r_nw.returncode != 0 and "[GATE]" in r_nw.stderr and "ignored" in r_nw.stderr
                    and remote() == before, f"rc={r_nw.returncode} {r_nw.stderr[-240:]}"))
        r = lab.g(chains["cursor"], "push", "origin", "main", cwd=ws)
        ring = _gate(ws).get("ring") or []
        held = r.returncode != 0 and "[GATE]" in r.stderr and remote() == before and any(
            x.get("event") == "held" and x.get("head") == held_head for x in ring)
        commit(off, red=False)
        r2 = lab.g(chains["cursor"], "push", "origin", "main", cwd=ws)
        out.append((CASES[5], rc_b == 0 and held and r2.returncode == 0 and remote() == head(),
                    f"install={rc_b} {log_b[-120:]} held={held} {r.stderr[-240:]} green={r2.returncode} "
                    f"{r2.stderr[-160:]}"))

        # bypass refused under an agent chain (and when undetermined)
        commit(off, red=True)
        before = remote()
        r = lab.g(dict(chains["cursor"], WS_GATE_BYPASS="fixture reason"), "push", "origin", "main", cwd=ws)
        rec = _receipts(ws)
        r_h = lab.g(dict(lab.env, WS_GATE_BYPASS="fixture reason"), "push", "origin", "main", cwd=ws)
        rec_h = _receipts(ws)
        out.append((CASES[6], r.returncode != 0 and "refused" in r.stderr and remote() == before and rec
                    and rec[-1]["action_class"] == "gate-bypass" and rec[-1]["verdict"]["result"] == "bypass-refused"
                    and rec[-1]["family"] == "cursor" and r_h.returncode != 0 and len(rec_h) == len(rec) + 1,
                    f"agent={r.returncode} {r.stderr[-200:]} undetermined={r_h.returncode} last={rec[-1:]}"))

        # bypass honoured with no agent in the ancestry (in-process: the fixture lib reads no process table)
        gl = _load(lab.lib / "09-tools" / "git_lanes.py", "gate_fx_git_lanes")
        gl._PR = None
        lines = [f"refs/heads/main {head()} refs/heads/main {remote()}"]
        base = gl._allow(family="human", lane="workspace")
        d = gl.gate_push(base, ws, lines, dict(lab.env, WS_GATE_BYPASS="fixture: CI is down"), {},
                         ancestry=[{"comm": "zsh"}, {"comm": "login"}], root=lab.lib)
        rec = _receipts(ws)
        ring = _gate(ws).get("ring") or []
        out.append((CASES[7], d["decision"] == "allow" and any("allowed by WS_GATE_BYPASS (recorded)" in x
                                                               for x in d["notices"])
                    and rec[-1]["verdict"] == {"result": "bypass", "reason": "fixture: CI is down"}
                    and ring[-1].get("event") == "bypass",
                    f"{json.dumps(d)[:300]} last={rec[-1:]}"))

        # kill switch
        calls2 = _calls(home)
        commit(off, red=True)
        r = lab.g(dict(chains["cursor"], WS_PUSH_GATE="off"), "push", "origin", "main", cwd=ws)
        out.append((CASES[8], r.returncode == 0 and remote() == head() and "gate off" in r.stderr
                    and _calls(home) == calls2, f"rc={r.returncode} calls={_calls(home) - calls2} {r.stderr[-200:]}"))

        # ws.pushgate at repo scope is ignored (report-only install), and audited
        lab.install("git-hooks")
        lab.g(lab.env, "config", "ws.pushgate", "block", cwd=ws)
        commit(off, red=True)
        r = lab.g(chains["cursor"], "push", "origin", "main", cwd=ws)
        a = gl.audit(repos=[str(ws)], home=home, env=lab.env, ancestry=[])
        f = " | ".join(a["findings"])
        lab.g(lab.env, "config", "--unset", "ws.pushgate", cwd=ws)
        out.append((CASES[9], r.returncode == 0 and "is ignored" in r.stderr and "report-only" in r.stderr
                    and "ws.pushgate set outside" in f, f"rc={r.returncode} {r.stderr[-200:]} audit={f[:200]}"))

        # stop hooks: one notice at most (HEAD is red and unpushed)
        commit(off, red=True)
        lab.g(off, "hook", "run", "post-commit", cwd=ws)          # gate off: nothing
        gl.verify_tree(ws, tree(), head(), f"{remote()}..{head()}", env=lab.env, via="fixture")
        wh = _load(TOOLS / "ws_hook.py", "gate_fx_ws_hook")
        results = {}
        for label, dialect, sess in (("cursor", "cursor", "S1"), ("cursor-again", "cursor", "S1"),
                                     ("codex", "codex", "S2"), ("claude", "claude", "S3")):
            o, e = io.StringIO(), io.StringIO()
            rc_s = wh.stop_notice(label, dialect, {"cwd": str(ws), "session": sess}, home=home, out=o, err=e)
            results[label] = (rc_s, o.getvalue(), e.getvalue())
        o, e = io.StringIO(), io.StringIO()
        emp = lab.clone("acme-corp/widget", "emp-stop", email_id="acme-id")
        wh.stop_notice("cursor", "cursor", {"cwd": str(emp), "session": "S5"}, home=home, out=o, err=e)
        outside = (o.getvalue(), e.getvalue())
        o2 = io.StringIO()
        with contextlib.redirect_stderr(io.StringIO()) as e2:
            rc_h = wh.handle_event("codex", "stop", {"session_id": "S6", "cwd": str(ws), "hook_event_name": "Stop"},
                                   home=home, out=o2)
        cur, again, cdx, cl = results["cursor"], results["cursor-again"], results["codex"], results["claude"]
        try:
            cl_obj = json.loads(cl[1])
        except ValueError:
            cl_obj = {}
        ok_stop = (all(x[0] == 0 for x in results.values())
                   and cur[1] == "{}\n" and len(cur[2].splitlines()) == 1 and "[gate:red:" in cur[2]
                   and again[1] == "{}\n" and again[2] == ""
                   and cdx[1] == "" and len(cdx[2].splitlines()) == 1
                   and set(cl_obj) == {"systemMessage"} and "[gate:red:" in cl_obj.get("systemMessage", "")
                   and len(cl[1].splitlines()) == 1 and cl[2] == ""
                   and outside == ("{}\n", "")
                   and rc_h == 0 and o2.getvalue() == "" and len(e2.getvalue().splitlines()) <= 1
                   and not any(k in (cur[1] + cdx[1] + cl[1]) for k in ("followup_message", '"continue"', '"decision"')))
        out.append((CASES[10], ok_stop, f"{results} outside={outside} handle={rc_h} {o2.getvalue()!r} "
                                        f"{e2.getvalue()!r}"))

        # post-commit sequencing
        gd = lab.tmp / "gitdir"
        (gd / "rebase-merge").mkdir(parents=True)
        seq = (gl._sequencing(gd, {}) and gl._sequencing(None, {"GIT_REFLOG_ACTION": "rebase (pick)"})
               and gl._sequencing(None, {"GIT_REFLOG_ACTION": "cherry-pick"})
               and not gl._sequencing(None, {"GIT_REFLOG_ACTION": "commit (amend)"})
               and not gl._sequencing(lab.tmp / "none", {}))
        out.append((CASES[11], seq, "sequencing detection"))
    finally:
        time.sleep(0.5)          # let a detached verify finish writing before the temp world goes
        for d, _dirs, _files in os.walk(td):
            try:
                os.chmod(d, 0o755)
            except OSError:
                pass
        shutil.rmtree(td, ignore_errors=True)
    return out


if __name__ == "__main__":
    fails = 0
    for name, passed, detail in gate_cases():
        mark = "SKIP" if passed is None else ("ok" if passed else "FAIL")
        fails += passed is False
        print(f"{mark:4} {name}\n     {detail}")
    sys.exit(1 if fails else 0)
