"""Golden cases for H23 session closure and H25 fragment limits: TestClosure and `closure.py --self-test`.

One synthetic world per case group, built on the wall-guard world (temp HOME, fixture tables with
synthetic owners, real git repos, a checkout cache): acme-corp is the employer, pat-sample is
personal, dev-a is the work device and dev-b the personal one. The fixture workspace is made a real
git repository so the sweeper can commit. Nothing here reads the real ~/.config or ~/.claude.

run_cases(closure_module) returns [(name, ok, detail)].
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any, List

HERE = Path(__file__).resolve().parent
TOOLS = HERE.parents[1]
ROOT = TOOLS.parent
WG_CASES = TOOLS / "fixtures" / "wall_guard" / "cases.py"
FRAG = "06-context/sessions/2026-09-25-dev-b-ab12.md"
OLD = 3 * 86400


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@contextlib.contextmanager
def isolated_env(home: Path):
    """Temp HOME and no global or system git config, for this process and its git children."""
    saved = dict(os.environ)
    try:
        for k in list(os.environ):
            if k.startswith(("GIT_CONFIG", "WS_", "CLAUDE", "CURSOR", "CODEX")):
                os.environ.pop(k, None)
        os.environ.update({"HOME": str(home), "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
                           "GIT_TERMINAL_PROMPT": "0", "LANG": "C", "LC_ALL": "C"})
        yield
    finally:
        os.environ.clear()
        os.environ.update(saved)


def _git(cwd: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", *args],
                          cwd=str(cwd), capture_output=True, text=True, timeout=60)


def _w(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def world(pr, tmp: Path) -> dict:
    wg = _load("wg_cases_for_closure", WG_CASES)
    w = wg.build_world(pr, tmp)
    ws = w["root"]
    _w(ws / "06-context" / "session-log.md", "# Session Log\n\n## Session Entries\n\n### 2026-09-01 — seed\n")
    _w(ws / "06-context" / "sessions" / "README.md", "fragments\n")
    _w(ws / "03-skills" / "skills.registry.json", "{}\n")
    _w(ws / "notes" / "idea.md", "seed\n")
    _w(ws / "notes" / "live.md", "seed\n")
    _w(ws / "notes" / "other.md", "seed\n")
    _git(ws, "init", "-q", "-b", "main")
    _git(ws, "add", "-A")
    _git(ws, "commit", "-q", "-m", "seed")
    for key in ("PERS", "EMP"):
        _w(w[key] / "README.md", "seed\n")
        _git(w[key], "add", "-A")
        _git(w[key], "commit", "-q", "-m", "seed")
    w["tele"] = pr.ws_paths(home=w["home"])["telemetry"]
    os.environ["HOME"] = str(w["home"])     # restored by isolated_env
    return w


def ledger(w: dict, sid: str, recs: List[dict], *, age: float = 0.0) -> Path:
    f = w["tele"] / "sessions" / f"{sid}.touched"
    f.parent.mkdir(parents=True, exist_ok=True)
    with f.open("a", encoding="utf-8") as fh:
        for r in recs:
            fh.write(json.dumps(dict({"ts": "2026-09-25T00:00:00Z", "tool": "Write"}, **r)) + "\n")
    if age:
        t = time.time() - age
        os.utime(f, (t, t))
    return f


def rec(repo: Path, path, host: str) -> dict:
    return {"repo": str(repo), "path": path, "host": host}


class Spy:
    """Records every subprocess.run (argv, cwd) made while active; the calls still run."""

    def __init__(self) -> None:
        self.calls: List[tuple] = []
        self._orig = subprocess.run

    def __enter__(self):
        orig = self._orig

        def run(argv, *a, **kw):
            self.calls.append((list(argv) if isinstance(argv, (list, tuple)) else [str(argv)], str(kw.get("cwd") or "")))
            return orig(argv, *a, **kw)
        subprocess.run = run
        return self

    def __exit__(self, *exc):
        subprocess.run = self._orig

    def touched(self, repo: Path) -> List[list]:
        r = os.path.realpath(str(repo))
        out = []
        for argv, cwd in self.calls:
            if cwd and os.path.realpath(cwd) == r:
                out.append(argv)
            elif any(os.path.realpath(a) == r for a in argv if isinstance(a, str) and a.startswith("/")):
                out.append(argv)
        return out


def run_cases(c) -> list:
    results: List[tuple] = []

    def ok(name: str, cond: Any, detail: str = "") -> None:
        results.append((name, bool(cond), "" if cond else detail))

    pr = c._pr()
    with tempfile.TemporaryDirectory(prefix="closure-") as td:
        tmp = Path(os.path.realpath(td))
        with isolated_env(tmp / "home"):
            _plan_matrix(c, pr, tmp / "plan", ok)
            _fallback(c, pr, tmp / "fb", ok)
            _sweeper(c, pr, tmp / "sweep", ok)
            _sweeper_live(c, pr, tmp / "live", ok)
            _h25(c, pr, tmp / "h25", ok)
            _ledger_parity(c, pr, tmp / "parity", ok)
            _hook_wiring(c, pr, tmp / "hook", ok)
    return results


# --------------------------------------------------------------------------- plan matrix

def _plan_matrix(c, pr, tmp: Path, ok) -> None:
    w = world(pr, tmp)
    ws, home = w["root"], w["home"]
    # repo class x family: the action, the identity and what git may touch
    want = {
        ("workspace", "claude"): ("workspace", "pat"), ("workspace", "cursor"): ("workspace", "pat"),
        ("workspace", "codex"): ("workspace", "pat"),
        ("personal", "claude"): ("commit-push", "pat"), ("personal", "cursor"): ("commit-push", "pat"),
        ("personal", "codex"): ("commit-push", "pat"),
        ("employer", "claude"): ("handoff", None), ("employer", "cursor"): ("branch-pr", None),
        ("employer", "codex"): ("branch-pr", None),
        ("unknown", "claude"): ("handoff", None), ("unknown", "cursor"): ("branch-pr", None),
        ("unknown", "codex"): ("branch-pr", None),
    }
    repos = {"workspace": ws, "personal": w["PERS"], "employer": w["EMP"], "unknown": w["UNK_IN"]}
    hosts = {"claude": "claude-code", "cursor": "cursor", "codex": "codex"}
    for (cls, fam), (action, ident) in want.items():
        sid = f"m-{cls}-{fam}"
        path = "notes/idea.md" if cls == "workspace" else "README.md"
        ledger(w, sid, [rec(repos[cls], path, hosts[fam])])
        with Spy() as spy:
            p = c.plan(sid, home=home, root=ws, hostname="host-b")
        row = next((r for r in p["repos"] if r["repo"] == os.path.realpath(repos[cls])), None)
        good = row is not None and row["class"] == cls and row["action"] == action and p["family"] == fam
        if ident:
            good = good and row["identity"] == ident
        ok(f"plan {cls} x {fam} -> {action}", good, json.dumps(row))
        if cls == "workspace" and row:
            ok(f"plan workspace x {fam}: fold, rebuild, verify, commit, push",
               row["steps"] == ["fold", "rebuild", "verify", "commit", "push"], str(row["steps"]))
        if action == "branch-pr" and row:
            ok(f"plan {cls} x {fam}: a feature branch first; never the default branch",
               row["steps"][0] == "feature-branch" and any("never commit or push the default branch" in n
                                                           for n in row["notes"]), json.dumps(row))
        if fam == "claude" and cls in ("employer", "unknown"):
            ok(f"plan {cls} x claude: no git in that repo; commands are the vetted script only",
               not spy.touched(repos[cls]) and all(x.startswith("python3 09-tools/prune-our-branches.py")
                                                   for x in row["commands"]), str(spy.touched(repos[cls])))
            ok(f"plan {cls} x claude: H25 limits flagged", p["h25_fragment_limits"] is True)
    # the device matters: the employer repo from Cursor on the work device takes the employer identity
    ledger(w, "m-dev-a", [rec(w["EMP"], "README.md", "cursor")])
    p = c.plan("m-dev-a", home=home, root=ws, hostname="host-a")
    ok("plan employer x cursor on dev-a: the employer allowlist identity",
       p["repos"][0]["identity"] == "acme-id" and p["device"] == "dev-a", json.dumps(p["repos"][0]))
    text = c.format_plan(c.plan("m-employer-claude", home=home, root=ws, hostname="host-b"))
    ok("text plan names the action per repo and the H25 limits",
       "[employer] -> handoff" in text and "H25:" in text, text)
    mixed = "m-mixed"
    ledger(w, mixed, [rec(ws, "notes/idea.md", "cursor"), rec(ws, "notes/idea.md", "claude-code")])
    ok("a session seen from two families closes under the tighter walls",
       c.plan(mixed, home=home, root=ws, hostname="host-b")["family"] == "claude")


def _fallback(c, pr, tmp: Path, ok) -> None:
    w = world(pr, tmp)
    ws, home = w["root"], w["home"]
    for key in ("PERS", "EMP"):
        _w(w[key] / "README.md", "dirty\n")
    _w(ws / "notes" / "idea.md", "dirty\n")
    with Spy() as spy:
        p = c.plan("no-ledger", family="claude", home=home, root=ws, hostname="host-b")
    got = {r["class"] for r in p["repos"]}
    ok("fallback (no ledger, Claude): git status over the workspace and positively personal repos only",
       p["source"] == "fallback-git-status" and got == {"workspace", "personal"}, json.dumps(p["repos"]))
    ok("fallback (Claude) runs no git in the employer repo", not spy.touched(w["EMP"]), str(spy.touched(w["EMP"])))
    p = c.plan("no-ledger", family="cursor", home=home, root=ws, hostname="host-b")
    ok("fallback (Cursor) includes the dirty employer repo, closed by branch and PR",
       any(r["class"] == "employer" and r["action"] == "branch-pr" for r in p["repos"]), json.dumps(p["repos"]))


# --------------------------------------------------------------------------- sweeper

def _status(repo: Path) -> str:
    return _git(repo, "status", "--porcelain=v1", "--untracked-files=all").stdout


def _head(repo: Path) -> str:
    return _git(repo, "rev-parse", "HEAD").stdout.strip()


def _sweeper(c, pr, tmp: Path, ok) -> None:
    w = world(pr, tmp)
    ws, home = w["root"], w["home"]
    _w(ws / FRAG, "### 2026-09-25 — cursor work\n\nSessionID: 2026-09-25-dev-b-ab12\n--- SESSION BLOCK ---\n"
                  "Surface: Cursor\n--- END BLOCK ---\n")
    _w(ws / "03-skills" / "skills.registry.json", "{\"rebuilt\": true}\n")
    _w(ws / "notes" / "idea.md", "substantive edit\n")
    _w(ws / "notes" / "other.md", "someone else's edit\n")
    _w(w["PERS"] / "README.md", "personal leftover\n")
    pers_before, pers_head = _status(w["PERS"]), _head(w["PERS"])
    ledger(w, "cur-dead", [rec(ws, FRAG, "cursor"), rec(ws, "notes/idea.md", "cursor"), rec(ws, None, "cursor"),
                           rec(w["PERS"], "README.md", "cursor")], age=OLD)
    before = _head(ws)
    with Spy() as spy:
        res = c.sweep(home=home, root=ws, current_sid="claude-now", host="claude-code", hostname="host-b")
    files = _git(ws, "show", "--name-only", "--format=%ae", "HEAD").stdout.split()
    ok("a Cursor session's leftover fragment is swept by the next start on another surface (Claude)",
       _head(ws) != before and FRAG in files, json.dumps(res))
    ok("the sweep commits only mechanical paths: the fragment and the rebuild output",
       sorted(files[1:]) == sorted([FRAG, "03-skills/skills.registry.json"]), str(files))
    ok("the sweep commits under the resolved identity (Claude on dev-b: pat)",
       files[:1] == ["1717+pat-sample@users.noreply.github.com"], str(files[:1]))
    st = _status(ws)
    ok("substantive and unclaimed paths stay uncommitted",
       "notes/idea.md" in st and "notes/other.md" in st, st)
    ok("the sweep never touches another repo",
       _status(w["PERS"]) == pers_before and _head(w["PERS"]) == pers_head and not spy.touched(w["PERS"])
       and all(os.path.realpath(cwd) == os.path.realpath(ws) for argv, cwd in spy.calls if argv[:1] == ["git"]),
       str([x for x in spy.calls if x[0][:1] == ["git"]]))
    ok("the sweep never pushes", not any("push" in argv for argv, _ in spy.calls))
    n = res["notices"]
    ok("substantive leftovers become one notice with the closure command",
       len(n) == 1 and n[0]["files"] == 1 and n[0]["text"] ==
       "uncommitted work from cursor session cur-dead: 1 file — run: ws closure plan --session cur-dead", json.dumps(n))
    ok("the notice reaches the card reader", c.read_notices(home=home) == [n[0]["text"]], str(c.read_notices(home=home)))
    ss = _load("session_status_for_closure", TOOLS / "session-status.py")
    ok("session-status shows the closure notice", n[0]["text"] in ss.notices(), str(ss.notices()))
    again = c.sweep(home=home, root=ws, current_sid="claude-now", host="claude-code", hostname="host-b")
    ok("a second sweep commits nothing and keeps the notice",
       not again["committed"] and len(again["notices"]) == 1, json.dumps(again))
    # a dead session with only mechanical leftovers closes its ledger
    _w(ws / "06-context" / "sessions" / "2026-09-25-dev-b-cd34.md", "SessionID: 2026-09-25-dev-b-cd34\n")
    ledger(w, "cdx-dead", [rec(ws, "06-context/sessions/2026-09-25-dev-b-cd34.md", "codex")], age=OLD)
    res = c.sweep(home=home, root=ws, current_sid="claude-now", host="cursor", hostname="host-b")
    ok("a Codex leftover fragment is swept by a Cursor start and its ledger closes",
       any(x["sid"] == "cdx-dead" for x in res["committed"])
       and (w["tele"] / "sessions" / "cdx-dead.closed").is_file(), json.dumps(res))
    ok("a closed ledger still plans", [r["action"] for r in c.plan("cdx-dead", home=home, root=ws,
                                                                   hostname="host-b")["repos"]] == ["workspace"])
    ok("a ledger that reached another repo is not closed by the sweeper",
       (w["tele"] / "sessions" / "cur-dead.touched").is_file())
    # never blocks: a zero budget sweeps nothing and returns
    ledger(w, "late", [rec(ws, "notes/idea.md", "codex")], age=OLD)
    t0 = time.monotonic()
    res = c.sweep(home=home, root=ws, current_sid="x", host="codex", budget=0.0, hostname="host-b")
    ok("an exhausted budget skips instead of blocking", time.monotonic() - t0 < 5 and res["skipped"], json.dumps(res))


def _sweeper_live(c, pr, tmp: Path, ok) -> None:
    w = world(pr, tmp)
    ws, home = w["root"], w["home"]
    _w(ws / FRAG, "SessionID: 2026-09-25-dev-b-ab12\n")
    _w(ws / "03-skills" / "skills.registry.json", "{\"live rebuild\": true}\n")
    _w(ws / "notes" / "live.md", "live edit\n")
    ledger(w, "dead", [rec(ws, FRAG, "cursor"), rec(ws, "notes/live.md", "cursor")], age=OLD)
    ledger(w, "alive", [rec(ws, "notes/live.md", "claude-code"), rec(ws, None, "claude-code")])
    res = c.sweep(home=home, root=ws, current_sid="alive", host="claude-code", hostname="host-b")
    files = _git(ws, "show", "--name-only", "--format=", "HEAD").stdout.split()
    ok("with a live session in the workspace only the dead session's fragment is swept",
       files == [FRAG], str(files))
    st = _status(ws)
    ok("a live session's claimed path and a live rebuild output stay uncommitted",
       "notes/live.md" in st and "skills.registry.json" in st, st)
    ok("a path a live session claims is not the dead session's notice", not res["notices"], json.dumps(res))
    dres = c.sweep(home=home, root=ws, current_sid="alive", host="claude-code", dry_run=True, hostname="host-b")
    ok("dry-run reports and commits nothing", _head(ws) == _git(ws, "rev-parse", "HEAD").stdout.strip()
       and not any(x.get("sha") for x in dres["committed"]), json.dumps(dres))


# --------------------------------------------------------------------------- H25

EMP_FRAGMENT = ("### 2026-09-25 — widget fix\n\nSessionID: 2026-09-25-dev-b-ef56\n--- SESSION BLOCK ---\n"
                "Surface: Cursor\nSummary: fixed the acme-corp/widget date picker in src/picker.ts\n"
                "Decisions:\n  - kept the vault note short\nNext:\n  - review https://github.com/acme-corp/widget/pull/7\n"
                "--- END BLOCK ---\n")


def _h25(c, pr, tmp: Path, ok) -> None:
    w = world(pr, tmp)
    ws, home = w["root"], w["home"]
    rel = "06-context/sessions/2026-09-25-dev-b-ef56.md"
    _w(ws / rel, EMP_FRAGMENT)
    ledger(w, "emp-cur", [rec(ws, rel, "cursor"), rec(w["EMP"], "src/picker.ts", "cursor")], age=OLD)
    lim = c.limited_repos(c.ledger("emp-cur", home=home), "cursor", home=home, root=ws)
    text = c.limit_fragment(EMP_FRAGMENT, lim, family="cursor", public=True,
                            tokens=c.employer_tokens(lim, root=ws))
    low = text.casefold()
    ok("H25: an employer-touched fragment keeps no employer slug, repo name, path or URL",
       "acme" not in low and "widget" not in low and "picker" not in low, text)
    ok("H25: it holds one opaque id and a status per employer repo (public vault: no PR URL)",
       f"  - {c.opaque_id(lim[0])} — branch-pr" in text and "https://" not in text, text)
    ok("H25: unrelated lines survive (gate 2)", "kept the vault note short" in text and "SessionID:" in text, text)
    ok("H25: limits are idempotent",
       c.limit_fragment(text, lim, family="cursor", public=True, tokens=c.employer_tokens(lim, root=ws)) == text)
    priv = c.limit_fragment(EMP_FRAGMENT, [dict(lim[0], pr_url="https://github.com/acme-corp/widget/pull/7")],
                            family="cursor", public=False, tokens=c.employer_tokens(lim, root=ws))
    ok("H25: a private workspace keeps the slug and an allowed PR URL",
       "  - acme-corp/widget — branch-pr — https://github.com/acme-corp/widget/pull/7" in priv, priv)
    cl = c.limit_fragment(EMP_FRAGMENT, [dict(lim[0], pr_url="https://x/pull/1", status=None)], family="claude",
                          public=False, tokens=c.employer_tokens(lim, root=ws))
    ok("H25: a Claude session's employer repo reads handoff and never carries a PR URL",
       "— handoff" in cl and "https://x/pull/1" not in cl, cl)
    ok("H25: a personal-only session's fragment is untouched",
       c.limit_fragment(EMP_FRAGMENT, [], family="cursor", public=True, tokens=[]) == EMP_FRAGMENT)
    # the fragment writer (compact-sessions fold) and the sweeper both enforce it
    cs = _load("compact_sessions_for_closure", TOOLS / "compact-sessions.py")
    with contextlib.redirect_stdout(io.StringIO()):
        cs.compact(ws, quiet=True)
    log = (ws / "06-context" / "session-log.md").read_text(encoding="utf-8").casefold()
    ok("H25: compact-sessions folds the limited fragment", "widget" not in log and "emp-" in log
       and "kept the vault note short" in log, log[:600])
    _git(ws, "checkout", "-q", "--", "06-context/session-log.md")
    _w(ws / rel, EMP_FRAGMENT)
    c.sweep(home=home, root=ws, current_sid="now", host="codex", hostname="host-b")
    committed = _git(ws, "show", f"HEAD:{rel}").stdout.casefold()
    ok("H25: the sweeper limits the fragment before it commits it",
       committed and "widget" not in committed and "emp-" in committed, committed)


# --------------------------------------------------------------------------- ledger parity

def _ledger_parity(c, pr, tmp: Path, ok) -> None:
    w = world(pr, tmp)
    ws, home = w["root"], w["home"]
    wh = c._wh()
    for host, event in (("claude-code", "post-tool"), ("cursor", "post-edit"), ("codex", "post-tool")):
        payload = dict(wh.ledger_golden(host, event, ws), session_id=f"par-{host}")
        payload.pop("conversation_id", None)
        wh.record_touch(host, payload, home=home)
    shapes = set()
    for host in ("claude-code", "cursor", "codex"):
        g = c.group_repos(c.ledger(f"par-{host}", home=home))
        shapes.add(json.dumps({k: v["paths"] for k, v in g.items()}, sort_keys=True))
        p = c.plan(f"par-{host}", home=home, root=ws, hostname="host-b")
        ok(f"ledger parity: the {host} golden closes the workspace",
           [r["action"] for r in p["repos"]] == ["workspace"], json.dumps(p["repos"]))
    ok("ledger parity: Claude, Cursor and Codex goldens give one ledger shape",
       shapes == {json.dumps({os.path.realpath(ws): ["notes/touched.md"]}, sort_keys=True)}, str(shapes))


def _hook_wiring(c, pr, tmp: Path, ok) -> None:
    wh = c._wh()
    calls: List[dict] = []
    orig = c.sweep

    def fake(**kw):
        calls.append(kw)
        return {}
    c.sweep = fake
    try:
        payload = wh.ledger_golden("cursor", "post-edit", tmp)
        wh.run_sweep("cursor", dict(payload, conversation_id="cur-start"), home=tmp, budget=1.0)
    finally:
        c.sweep = orig
    ok("ws-hook sweep hands closure.sweep the session, host and a bounded budget",
       calls and calls[0]["current_sid"] == "cur-start" and calls[0]["host"] == "cursor"
       and calls[0]["budget"] <= 1.0, str(calls))
