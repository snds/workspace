"""nightly.py --self-test (H1): fixpoint order, written paths, session scope, foreign
edits, timeouts, budget, the pre-commit lane with the X1 replay, and the timed SessionEnd
accelerator (dispatcher → nightly → commit → push to a local bare remote, <= 55 s).

Every case runs in a temp vault built from the REAL generators and synthetic skills."""

from __future__ import annotations

import json
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import nightly_fixture_lib as fx  # noqa: E402

REGISTRY = "03-skills/skills.registry.json"
ALPHA = "03-skills/alpha/SKILL.md"
BETA = "03-skills/beta/SKILL.md"
LANE_FIX_1 = "python3 09-tools/nightly.py --phases rebuild --scope staged --json"
LANE_FIX_2 = 'git add -- <paths listed under "written">'
FIXPOINT = ["build-registry.py", "build-related.py", "build-registry.py", "build-trigger-routes.py"]


def _nightly(vault: Path, env: dict, *args: str, timeout: float = 120):
    r = fx.py(vault / "09-tools" / "nightly.py", *args, cwd=vault, env=env, timeout=timeout)
    try:
        rep = json.loads(r.stdout) if "--json" in args else None
    except ValueError:
        rep = None
    return r, rep


def _ledger(vault: Path, sid: str, paths: list[str]) -> None:
    (vault / "06-context" / "sessions" / f"{sid}.touched").write_text(
        "".join(p + "\n" for p in paths), encoding="utf-8")


def _checks_pass(tree: Path, env: dict) -> bool:
    for gen, args in (("build-registry.py", ["--check"]), ("build-related.py", ["--check"]),
                      ("build-trigger-routes.py", ["--check"])):
        if fx.py(tree / "09-tools" / gen, *args, cwd=tree, env=env).returncode != 0:
            return False
    return True


def case_fixpoint_clean(c: fx.Checks, base: Path, tmp: Path, env: dict) -> None:
    v = fx.clone(base, tmp / "clean", env)
    r, rep = _nightly(v, env, "--phases", "rebuild", "--json")
    c.check(r.returncode == 0 and rep and rep["status"] == "ok", "clean rebuild exits 0, status ok",
            r.stderr[-300:])
    if not rep:
        return
    c.check([e["tool"] for e in rep["phases"]] == FIXPOINT, "fixpoint runs in order: "
            "registry → related → registry → trigger-routes")
    c.check(rep["phases"][2]["status"] == "noop", "second build-registry pass skipped when "
            "build-related wrote 0 files", rep["phases"][2]["status"])
    c.check(rep["written"] == [] and rep["fix"] is None, "clean tree: nothing written, no fix line")
    for key in ("phases", "failed", "commit", "written", "foreign", "scope", "budget_s",
                "elapsed_s", "skipped", "status", "fix"):
        c.check(key in rep, f"--json carries `{key}`")
    r2, _ = _nightly(v, env, "--check", "--phases", "rebuild")
    c.check(r2.returncode == 0, "--check on a clean tree exits 0")
    fx.add_edge(v)
    before = fx.git(v, "status", "--porcelain", env=env).stdout
    r3, _ = _nightly(v, env, "--check", "--phases", "rebuild")
    after = fx.git(v, "status", "--porcelain", env=env).stdout
    c.check(r3.returncode == 1, "--check exits 1 on drift", str(r3.returncode))
    c.check(before == after, "--check writes nothing")
    r4 = fx.py(v / "09-tools" / "nightly.py", "--dry-run", cwd=v, env=env)
    c.check(r4.returncode == 0 and "fixpoint pass" in r4.stdout, "--dry-run prints the plan")


def case_session_scope(c: fx.Checks, base: Path, tmp: Path, env: dict) -> None:
    v = fx.clone(base, tmp / "session", env)
    # Baseline: notes.md was already dirty when the session started.
    (v / "notes.md").write_text("older dirt\n", encoding="utf-8")
    bdir = v / ".workspace" / "state" / "sessions"
    bdir.mkdir(parents=True)
    (bdir / "S1.json").write_text(json.dumps({"schema_version": 1, "sid": "S1", "porcelain": [
        {"xy": " M", "path": "notes.md", "orig": None}]}) + "\n", encoding="utf-8")
    fx.add_edge(v)
    _ledger(v, "S1", [BETA])
    (v / "made-by-session.md").write_text("new\n", encoding="utf-8")  # clean at baseline
    r, rep = _nightly(v, env, "--phases", "rebuild", "--scope", "session:S1", "--json")
    c.check(r.returncode == 0 and rep and rep["status"] == "ok",
            "X1-style session case exits 0", (r.stderr or r.stdout)[-300:])
    if not rep:
        return
    per = {i: e["written"] for i, e in enumerate(rep["phases"])}
    c.check(per[0] == [REGISTRY], "step 1 (build-registry) wrote exactly the registry", str(per[0]))
    c.check(per[1] == [ALPHA, BETA], "step 2 (build-related) wrote exactly both Related blocks",
            str(per[1]))
    c.check(rep["phases"][2]["status"] == "ok" and per[2] == [REGISTRY],
            "step 3 re-ran build-registry because build-related wrote files", str(per[2]))
    c.check({REGISTRY, ALPHA, BETA} <= set(rep["written"]) and rep["foreign"] == [],
            "written covers x/SKILL.md, the rewritten Related block and the registry; none foreign")
    scope = set(rep.get("scope_paths") or [])
    c.check(BETA in scope and "made-by-session.md" in scope and "notes.md" not in scope,
            "session scope = ledger ∪ (dirty now, clean at baseline)", str(sorted(scope)))
    c.check(bool(rep["fix"]) and rep["fix"].startswith("git add -- ") and ALPHA in rep["fix"],
            "fix line stages exactly the written paths")


def case_foreign(c: fx.Checks, base: Path, tmp: Path, env: dict) -> None:
    v = fx.clone(base, tmp / "foreign", env)
    fx.add_edge(v)
    _ledger(v, "S2", [BETA])
    alpha = v / ALPHA
    alpha.write_text(alpha.read_text(encoding="utf-8").replace(
        "Fixture body for alpha.", "Fixture body for alpha. Another session's edit."),
        encoding="utf-8")
    r, rep = _nightly(v, env, "--phases", "rebuild", "--scope", "session:S2", "--json")
    c.check(r.returncode == 4 and rep and rep["status"] == "refused",
            "foreign unstaged edit on a written path gives exit 4", str(r.returncode))
    if rep:
        c.check(rep["foreign"] == [ALPHA], "the foreign path is listed", str(rep["foreign"]))
        c.check(rep["fix"] is None, "no fix line while foreign edits are present")


def case_foreign_input(c: fx.Checks, base: Path, tmp: Path, env: dict) -> None:
    """Another session's body edit on a SKILL.md the rebuild never rewrites still changes the
    registry hash: the whole heal is refused, nothing is written, and the input is named."""
    v = fx.clone(base, tmp / "foreign-input", env)
    alpha, beta = v / ALPHA, v / BETA
    alpha.write_text(alpha.read_text(encoding="utf-8").replace(
        "Fixture body for alpha.", "Fixture body for alpha. Another session's edit."), encoding="utf-8")
    beta.write_text(beta.read_text(encoding="utf-8").replace(
        "Fixture body for beta.", "Fixture body for beta. This session's edit."), encoding="utf-8")
    _ledger(v, "S6", [BETA])
    reg_before = (v / REGISTRY).read_bytes()
    r, rep = _nightly(v, env, "--phases", "rebuild", "--scope", "session:S6", "--json")
    c.check(r.returncode == 4 and rep and rep["status"] == "refused",
            "a foreign unstaged generator input refuses the whole heal (exit 4)", str(r.returncode))
    c.check((v / REGISTRY).read_bytes() == reg_before, "the refused heal writes nothing (registry untouched)")
    if rep:
        c.check(rep["written"] == [] and rep["foreign"] == [ALPHA] and rep.get("foreign_inputs") == [ALPHA],
                "the foreign input is named and nothing is listed as written",
                f"{rep['written']} {rep['foreign']} {rep.get('foreign_inputs')}")
        c.check(rep["fix"] is None, "no fix line while a foreign input is present")


def case_timeout(c: fx.Checks, base: Path, tmp: Path, env: dict) -> None:
    v = fx.clone(base, tmp / "timeout", env)
    (v / "09-tools" / "build-related.py").write_text("import time\ntime.sleep(30)\n",
                                                      encoding="utf-8")
    fx.add_edge(v)
    head = fx.git(v, "rev-parse", "HEAD", env=env).stdout.strip()
    r, rep = _nightly(v, env, "--phases", "rebuild,commit", "--step-timeout", "1", "--json")
    c.check(r.returncode == 3 and rep and rep["status"] == "skipped",
            "step timeout gives SKIPPED and exit 3 (never green)", str(r.returncode))
    if rep:
        st = [e["status"] for e in rep["phases"]]
        c.check(st[1] == "SKIPPED" and st[2] == "SKIPPED" and st[3] == "SKIPPED",
                "the timed-out step and the rest of the fixpoint are SKIPPED", str(st))
        c.check(rep["commit"].startswith("refused"), "commit refused on a SKIPPED run",
                rep["commit"])
    c.check(fx.git(v, "rev-parse", "HEAD", env=env).stdout.strip() == head, "no commit was made")


def case_budget(c: fx.Checks, base: Path, tmp: Path, env: dict) -> None:
    v = fx.clone(base, tmp / "budget", env)
    (v / "09-tools" / "compact-sessions.py").write_text("import time\ntime.sleep(30)\n",
                                                         encoding="utf-8")
    t0 = time.monotonic()
    r, rep = _nightly(v, env, "--phases", "fold,rebuild", "--budget", "1.5", "--json")
    took = time.monotonic() - t0
    c.check(r.returncode == 3 and rep and rep["status"] == "skipped",
            "budget exhaustion gives exit 3", str(r.returncode))
    if rep:
        st = [(e["phase"], e["status"]) for e in rep["phases"]]
        c.check(all(s == "SKIPPED" for _p, s in st) and len(st) == 5,
                "budget exhaustion marks every remaining step SKIPPED", str(st))
        c.check(any(s["reason"] == "budget exhausted" for s in rep["skipped"]),
                "skipped[] names the budget as the reason")
    c.check(took < 15, "budget is honoured (run stops early)", f"{took:.1f}s")


def case_lane_x1_replay(c: fx.Checks, base: Path, tmp: Path, env: dict) -> None:
    hooks = fx.hook_dir(tmp / "lane")
    # A commit that touches no skill source passes the lane silently.
    q = fx.clone(base, tmp / "lane-quiet", env)
    fx.git(q, "config", "core.hooksPath", str(hooks), env=env)
    (q / "notes.md").write_text("unrelated\n", encoding="utf-8")
    fx.git(q, "add", "notes.md", env=env)
    rq = fx.git(q, "commit", "-q", "-m", "unrelated", env=env, check=False)
    c.check(rq.returncode == 0 and rq.stderr.strip() == "", "lane is silent for non-skill commits",
            rq.stderr[-200:])

    marker_sets = [("WS_SURFACE_FAMILY=claude", {"WS_SURFACE_FAMILY": "claude"}),
                   ("CURSOR_AGENT=1", {"CURSOR_AGENT": "1"}),
                   ("CODEX_THREAD_ID=x", {"CODEX_THREAD_ID": "x"}),
                   ("no markers", {})]
    refusals, trees = [], []
    for i, (label, extra) in enumerate(marker_sets):
        menv = dict(env, **extra)
        v = fx.clone(base, tmp / f"lane-{i}", env)
        fx.git(v, "config", "core.hooksPath", str(hooks), env=env)
        fx.add_edge(v)
        fx.git(v, "add", BETA, env=menv)
        rc = fx.git(v, "commit", "-q", "-m", "x1: beta governed_by alpha", env=menv, check=False)
        text = (rc.stdout + rc.stderr).strip()
        refusals.append(text)
        lines = text.splitlines()
        c.check(rc.returncode != 0, f"[{label}] lane refuses the stale commit")
        c.check(lines[-2:] == [LANE_FIX_1, LANE_FIX_2],
                f"[{label}] lane prints exactly the two fix lines", repr(lines[-2:]))
        rf, rep = _nightly(v, menv, "--phases", "rebuild", "--scope", "staged", "--json")
        ok = rf.returncode == 0 and rep and rep["status"] == "ok"
        c.check(ok, f"[{label}] fix line 1 (scoped rebuild) exits 0", rf.stderr[-200:])
        if not ok:
            continue
        fx.git(v, "add", "--", *rep["written"], env=menv)
        rc2 = fx.git(v, "commit", "-q", "-m", "x1: beta governed_by alpha", env=menv, check=False)
        c.check(rc2.returncode == 0, f"[{label}] commit passes the lane after the fix",
                rc2.stderr[-200:])
        trees.append(fx.git(v, "rev-parse", "HEAD^{tree}", env=env).stdout.strip())
        arch = fx.archive_tree(v, tmp / f"lane-{i}-archive", env)
        c.check(_checks_pass(arch, env), f"[{label}] build-registry/related/routes --check "
                "exit 0 on `git archive HEAD`")
    c.check(len(set(refusals)) == 1, "identical refusal text under every marker set")
    c.check(len(trees) == len(marker_sets) and len(set(trees)) == 1,
            "identical fixed tree under every marker set", str(trees))


def case_accelerator(c: fx.Checks, base: Path, tmp: Path, env: dict, root: Path) -> None:
    dispatcher = root / ".claude" / "hooks" / "dispatcher.py"
    if not dispatcher.is_file():
        c.check(False, "timed accelerator: dispatcher.py present", str(dispatcher))
        return
    bare = tmp / "accel-remote.git"
    fx.git(tmp, "init", "-q", "--bare", "-b", "main", str(bare), env=env)
    v = fx.clone(base, tmp / "accel", env)
    fx.git(v, "remote", "set-url", "origin", str(bare), env=env)
    fx.git(v, "push", "-q", "-u", "origin", "main", env=env)
    head0 = fx.git(v, "rev-parse", "HEAD", env=env).stdout.strip()
    fx.add_edge(v)
    _ledger(v, "S5", [BETA])
    pl = fx.payload("claude-code.session-end")
    pl["session_id"] = "S5"
    denv = dict(env, CLAUDE_PROJECT_DIR=str(v))
    t0 = time.monotonic()
    r = fx.py(dispatcher, "session-end", cwd=v, env=denv, stdin=json.dumps(pl), timeout=90)
    took = time.monotonic() - t0
    c.check(r.returncode == 0, "accelerator: dispatcher session-end exits 0", r.stderr[-300:])
    c.check(took <= 55.0, f"accelerator: heal + commit + push finish in <= 55 s ({took:.1f}s)",
            f"{took:.1f}s")
    head = fx.git(v, "rev-parse", "HEAD", env=env).stdout.strip()
    c.check(head != head0, "accelerator: a commit was made")
    files = set(fx.git(v, "show", "--name-only", "--format=", "HEAD", env=env).stdout.split())
    c.check({BETA, ALPHA, REGISTRY} <= files,
            "accelerator commit carries x/SKILL.md, the rewritten Related block and the registry",
            str(sorted(files)))
    remote = fx.git(v, "--git-dir", str(bare), "rev-parse", "main", env=env).stdout.strip()
    c.check(remote == head, "accelerator: pushed to the (local bare) remote")
    gate = v / ".workspace" / "state" / "last-gate.json"
    try:
        g = json.loads(gate.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        g = {}
    tree = fx.git(v, "rev-parse", "HEAD^{tree}", env=env).stdout.strip()
    c.check(g.get("head") == head and g.get("tree") == tree and
            g.get("nightly", {}).get("status") == "ok",
            "last-gate.json records the committed HEAD tree with status ok", str(g)[:200])
    arch = fx.archive_tree(v, tmp / "accel-archive", env)
    c.check(_checks_pass(arch, env), "accelerator: generators --check exit 0 on `git archive HEAD`")


def run(root: Path) -> int:
    c = fx.Checks("nightly self-test")
    tools = root / "09-tools"
    with tempfile.TemporaryDirectory(prefix="nightly-selftest-") as td:
        tmp = Path(td)
        home = tmp / "home"
        home.mkdir()
        stubs = fx.make_stubs(tmp)
        env = fx.hermetic_env(home, stubs)
        try:
            base = fx.build_vault(tmp / "base", tools, env)
        except Exception as exc:  # noqa: BLE001
            c.check(False, "fixture vault builds", str(exc))
            return c.result()
        for case in (case_fixpoint_clean, case_session_scope, case_foreign, case_foreign_input, case_timeout,
                     case_budget, case_lane_x1_replay):
            print(f"· {case.__name__}")
            try:
                case(c, base, tmp, env)
            except Exception as exc:  # noqa: BLE001
                c.check(False, f"{case.__name__} ran", repr(exc))
        print("· case_accelerator")
        try:
            case_accelerator(c, base, tmp, env, root)
        except Exception as exc:  # noqa: BLE001
            c.check(False, "case_accelerator ran", repr(exc))
        for name in ("launchctl", "gh", "osascript"):
            c.check(fx.stub_calls(stubs, name) == 0, f"stub `{name}` never called")
    return c.result()


if __name__ == "__main__":
    sys.exit(run(HERE.parents[2]))
