#!/usr/bin/env python3
"""Read a pull request's state and CI, and merge it after Sean's review. Vetted script.

Why it exists: on an employer repo, `gh` needs the device's default account, and the walls never
let an agent change GH_CONFIG_DIR by hand (R6). Like prune-our-branches, this script is the one
registered way to make those calls: every `gh` call runs through `vetted_context().run()` (an intent
line, the lifted env, one receipt per action in ~/.config/snds-workspace/control/receipts.jsonl), only
in the argv shapes registered in 02-shared-references/vetted-scripts.json, and only where the action
policy allows it (via=vetted).

Actions (one per subcommand):
  status    the PR's state, mergeability, review decision, branches, and check rollup   (content-read)
  checks    every check with its state and link                                        (content-read)
  logs      the failed steps' log of one workflow run (`gh run view <id> --log-failed`) (content-read)
  comments  PR comments and review summaries                                           (content-read)
  review-comments  inline review comments on the diff (CodeQL posts its findings here)  (content-read)
  alerts    open code-scanning alerts on the PR's merge ref (rule, file, line, message) (content-read)
  merge     merge it — refused unless all of these hold:                                (merge)
              - Sean approved it in his own words, passed as --approved "…" (recorded in the receipt);
              - the PR is open, not a draft, and GitHub calls it mergeable (no conflicts, not blocked);
              - every check passed, was skipped, or is neutral (none failing, none still running);
              - its base is the repo's default branch and its head is not.
            Merge is human-only for every agent except through this script (action policy P29, Sean
            2026-10-12: "I would be the engineer that would be reviewing this").

Usage:
  python3 09-tools/pr-desk.py status   --repo /path/to/checkout --pr 87
  python3 09-tools/pr-desk.py checks   --repo /path/to/checkout --pr 87
  python3 09-tools/pr-desk.py logs     --repo /path/to/checkout --run 1234567890
  python3 09-tools/pr-desk.py comments --repo /path/to/checkout --pr 87
  python3 09-tools/pr-desk.py review-comments --repo /path/to/checkout --pr 87
  python3 09-tools/pr-desk.py alerts   --repo /path/to/checkout --pr 87
  python3 09-tools/pr-desk.py merge    --repo /path/to/checkout --pr 87 --method squash --approved "merge it"
  python3 09-tools/pr-desk.py --self-test
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable, List, Optional, Tuple

ROOT = Path(__file__).resolve().parent.parent
SCRIPT_ID = "pr-desk"
STATUS_FIELDS = "number,title,url,state,isDraft,mergeable,mergeStateStatus,reviewDecision,headRefName,baseRefName,statusCheckRollup"
CHECK_FIELDS = "name,state,bucket,link,workflow"
NETWORK_TIMEOUT_S = 120.0
METHODS = ("squash", "merge", "rebase")
# Check outcomes that don't block a merge (gh `bucket`, or a rollup conclusion/state).
PASSING = {"pass", "skipping", "success", "skipped", "neutral"}

_PINNED_API = ("vetted_context", "vetted_status", "repo_resolve", "detect_surface")


# --------------------------------------------------------------------------- resolver loading


def _pinned_resolver(home: Optional[Path] = None) -> Any:
    """profile_resolve from $HOME/.config/snds-workspace/lib/current, or None (then: unpinned)."""
    lib = (Path(home) if home is not None else Path.home()) / ".config" / "snds-workspace" / "lib" / "current"
    path = lib / "09-tools" / "profile_resolve.py"
    if not path.is_file():
        return None
    try:
        spec = importlib.util.spec_from_file_location("ws_pinned_profile_resolve", path)
        if spec is None or spec.loader is None:
            return None
        mod = importlib.util.module_from_spec(spec)
        sys.modules["ws_pinned_profile_resolve"] = mod
        spec.loader.exec_module(mod)
    except Exception:  # noqa: BLE001 - a broken pin is an unpinned pin
        return None
    return mod if all(hasattr(mod, n) for n in _PINNED_API) else None


def _vault_resolver() -> Any:
    try:
        tools = str(ROOT / "09-tools")
        if tools not in sys.path:
            sys.path.insert(0, tools)
        import profile_resolve  # noqa: PLC0415 - lazy by contract

        return profile_resolve
    except (ImportError, OSError, ValueError):
        return None


# --------------------------------------------------------------------------- argv (must match the registry)


def argv_for(action: str, *, pr: Optional[int] = None, run: Optional[str] = None, method: str = "squash") -> List[str]:
    if action == "status":
        return ["gh", "pr", "view", str(pr), "--json", STATUS_FIELDS]
    if action == "checks":
        return ["gh", "pr", "checks", str(pr), "--json", CHECK_FIELDS]
    if action == "logs":
        return ["gh", "run", "view", str(run), "--log-failed"]
    if action == "comments":
        return ["gh", "pr", "view", str(pr), "--json", "comments,reviews"]
    if action == "review-comments":
        return ["gh", "api", "--paginate", f"repos/{{owner}}/{{repo}}/pulls/{int(pr)}/comments"]
    if action == "alerts":
        return ["gh", "api", "--paginate", f"repos/{{owner}}/{{repo}}/code-scanning/alerts?ref=refs/pull/{int(pr)}/merge&state=open"]
    if action == "merge":
        return ["gh", "pr", "merge", str(pr), f"--{method}"]
    raise ValueError(f"unknown action {action!r}")


# --------------------------------------------------------------------------- the merge gate


def _rollup_outcome(c: dict) -> str:
    """One check from statusCheckRollup → pass | fail | pending (CheckRun or StatusContext)."""
    if c.get("__typename") == "StatusContext" or ("state" in c and "conclusion" not in c and "status" not in c):
        s = str(c.get("state") or "").lower()
        return "pass" if s in PASSING else "pending" if s in ("pending", "expected") else "fail"
    if str(c.get("status") or "").upper() not in ("COMPLETED", ""):
        return "pending"
    concl = str(c.get("conclusion") or "").lower()
    return "pass" if concl in PASSING else "fail"


def merge_blockers(status: dict, approved: str) -> List[str]:
    """Why this PR must not be merged now (empty = clear to merge). Reads `gh pr view --json STATUS_FIELDS`."""
    out: List[str] = []
    if not approved.strip():
        out.append("no approval: pass Sean's own words with --approved")
    if str(status.get("state") or "").upper() != "OPEN":
        out.append(f"the PR is {str(status.get('state') or 'unknown').lower()}, not open")
    if status.get("isDraft"):
        out.append("the PR is a draft")
    if str(status.get("mergeable") or "").upper() != "MERGEABLE":
        out.append(f"GitHub says mergeable={status.get('mergeable')} (conflicts, or not computed yet)")
    if str(status.get("mergeStateStatus") or "").upper() in ("BLOCKED", "DIRTY", "BEHIND", "DRAFT"):
        out.append(f"merge state is {status.get('mergeStateStatus')}")
    checks = status.get("statusCheckRollup") or []
    failing = [c.get("name") or c.get("context") or "?" for c in checks if _rollup_outcome(c) == "fail"]
    pending = [c.get("name") or c.get("context") or "?" for c in checks if _rollup_outcome(c) == "pending"]
    if failing:
        out.append(f"{len(failing)} check(s) failing: {', '.join(failing[:6])}")
    if pending:
        out.append(f"{len(pending)} check(s) still running: {', '.join(pending[:6])}")
    base, head = str(status.get("baseRefName") or ""), str(status.get("headRefName") or "")
    if not base or base == head:
        out.append("the head and base branches are the same (or unknown)")
    return out


def _default_branch(ctx: Any) -> Optional[str]:
    """The repo's default branch from origin/HEAD (a local, read-only git query)."""
    p = ctx.query(["git", "symbolic-ref", "--short", "refs/remotes/origin/HEAD"])
    name = (p.stdout or "").strip()
    return name.split("/", 1)[1] if p.returncode == 0 and "/" in name else None


# --------------------------------------------------------------------------- run


def _claude_chain(det: dict) -> bool:
    return det.get("family_for_walls") == "claude" or bool(det.get("agent_possible"))


def run(action: str, repo: Path, *, pr: Optional[int], run_id: Optional[str], method: str, approved: str,
        out: Callable[[str], None] = print, home: Optional[Path] = None, runner: Any = None, env: Optional[dict] = None,
        detection: Optional[dict] = None, pinned: Any = "auto", resolver: Any = "auto",
        script: Optional[Path] = None) -> int:
    pin = _pinned_resolver(home) if pinned == "auto" else pinned
    mod = resolver if resolver != "auto" else (pin or _vault_resolver())
    if mod is None:
        out("pr-desk: profile_resolve unavailable; nothing run")
        return 2
    script = script or Path(__file__).resolve()
    det = detection
    if det is None:
        try:
            det = mod.detect_surface()
        except Exception:  # noqa: BLE001 - undetermined detection is treated as a Claude chain
            det = {"family_for_walls": "claude", "agent_possible": True}
    repo = Path(repo).resolve()
    res = mod.repo_resolve(str(repo), home=home, detection=det)
    if _claude_chain(det) and not res.get("positively_personal"):
        # Checked before ANY gh call in this repo: an agent runs only the pinned bytes of this file.
        st = pin.vetted_status(SCRIPT_ID, script_path=script, home=home) if pin is not None else {"status": "unpinned", "notice": "no pinned lib"}
        if st.get("status") != "vetted":
            out(f"pr-desk: vetted-status {st.get('status')} — {st.get('notice') or 'not vetted'}; nothing run")
            return 4
    employer_gh = res.get("owner_class") == "employer"
    with mod.vetted_context(SCRIPT_ID, str(repo), script, home=home, detection=det, env=env, runner=runner,
                            assume_unpinned=pin is None, out=lambda s: None) as ctx:
        def call(act: str, argv: List[str], refs: List[str]) -> Tuple[int, str, str]:
            p = ctx.run(argv, act, refs=refs, needs_employer_gh=employer_gh, timeout=NETWORK_TIMEOUT_S)
            return p.returncode, p.stdout or "", p.stderr or ""

        if action == "merge":
            rc, so, se = call("status", argv_for("status", pr=pr), [f"pr-{pr}"])
            if rc != 0:
                out(f"pr-desk: could not read PR {pr}: {se.strip() or so.strip()}")
                return 1
            status = json.loads(so)
            why = merge_blockers(status, approved)
            dflt = _default_branch(ctx)
            if dflt and status.get("baseRefName") != dflt:
                why.append(f"base is {status.get('baseRefName')}, not the default branch {dflt}")
            if dflt and status.get("headRefName") == dflt:
                why.append("the head is the default branch")
            if why:
                out(f"pr-desk: not merging PR {pr}:")
                for w in why:
                    out(f"  - {w}")
                return 1
            # The approval travels in the receipt, trimmed to plain words (receipts carry no paths or URLs).
            words = " ".join(approved.replace("/", " ").replace(":", " ").split())[:80]
            rc, so, se = call("merge", argv_for("merge", pr=pr, method=method), [f"pr-{pr}", f"approved {words}"])
            out((so + se).strip() or (f"merged PR {pr}" if rc == 0 else f"merge failed ({rc})"))
            return 0 if rc == 0 else 1
        argv = argv_for(action, pr=pr, run=run_id)
        rc, so, se = call(action, argv, [f"run-{run_id}"] if action == "logs" else [f"pr-{pr}"])
        out(so.rstrip() if rc == 0 else f"pr-desk: {action} failed ({rc}): {se.strip()}")
        return 0 if rc == 0 else 1


# --------------------------------------------------------------------------- self-test


def self_test() -> int:
    fails: List[str] = []

    def ok(cond: bool, what: str) -> None:
        if not cond:
            fails.append(what)

    # 1. Every argv this script builds is a registered shape (the vault registry; the pin carries the same file).
    vault = _vault_resolver()
    if vault is None:
        print("pr-desk self-test FAIL: profile_resolve missing", file=sys.stderr)
        return 1
    reg = vault.load_table("vetted-scripts")
    row = next((r for r in reg.get("scripts") or [] if r.get("id") == SCRIPT_ID), None)
    ok(row is not None, "pr-desk is registered in vetted-scripts.json")
    if row:
        cases = [("status", {"pr": 87}), ("checks", {"pr": 87}), ("logs", {"run": "18311452763"}), ("comments", {"pr": 87}),
                 ("review-comments", {"pr": 87}), ("alerts", {"pr": 87})]
        cases += [("merge", {"pr": 87, "method": m}) for m in METHODS]
        for act, kw in cases:
            shapes = (row.get("argv") or {}).get(act) or []
            ok(any(vault.argv_matches_shape(argv_for(act, **kw), s) for s in shapes), f"{act} argv matches a registered shape")
            ok(act in (row.get("actions") or {}), f"{act} is a registered action")
        ok(row.get("actions", {}).get("merge") == "merge", "merge is registered as the merge class")
        ok(all(row["actions"][a] == "content-read" for a in ("status", "checks", "logs", "comments", "review-comments", "alerts")), "reads are content-read")
        ok(not vault.argv_matches_shape(["gh", "pr", "merge", "87", "--admin"], (row.get("argv") or {}).get("merge", [[]])[0]), "--admin is not a merge shape")
        ok(not any(vault.argv_matches_shape(["gh", "pr", "merge", "87", "--squash", "--admin"], s) for s in (row.get("argv") or {}).get("merge", [])), "no extra merge flags")

    # 2. The merge gate.
    green = {"state": "OPEN", "isDraft": False, "mergeable": "MERGEABLE", "mergeStateStatus": "CLEAN", "headRefName": "feat/x",
             "baseRefName": "main", "statusCheckRollup": [{"__typename": "CheckRun", "name": "ci", "status": "COMPLETED", "conclusion": "SUCCESS"},
                                                          {"__typename": "CheckRun", "name": "pages", "status": "COMPLETED", "conclusion": "SKIPPED"},
                                                          {"__typename": "StatusContext", "context": "deploy", "state": "SUCCESS"}]}
    ok(merge_blockers(green, "merge it") == [], "a green, open, mergeable PR with an approval is clear")
    ok(any("approval" in w for w in merge_blockers(green, "  ")), "no approval words: blocked")
    red = dict(green, statusCheckRollup=green["statusCheckRollup"] + [{"__typename": "CheckRun", "name": "lint", "status": "COMPLETED", "conclusion": "FAILURE"}])
    ok(any("failing: lint" in w for w in merge_blockers(red, "ok")), "a failing check blocks")
    running = dict(green, statusCheckRollup=[{"__typename": "CheckRun", "name": "test", "status": "IN_PROGRESS", "conclusion": ""}])
    ok(any("still running: test" in w for w in merge_blockers(running, "ok")), "a running check blocks")
    ok(any("draft" in w for w in merge_blockers(dict(green, isDraft=True), "ok")), "a draft blocks")
    ok(any("mergeable=CONFLICTING" in w for w in merge_blockers(dict(green, mergeable="CONFLICTING"), "ok")), "conflicts block")
    ok(any("BLOCKED" in w for w in merge_blockers(dict(green, mergeStateStatus="BLOCKED"), "ok")), "branch protection blocks")
    ok(any("merged" in w for w in merge_blockers(dict(green, state="MERGED"), "ok")), "an already merged PR is refused")
    ok(any("same" in w for w in merge_blockers(dict(green, headRefName="main"), "ok")), "head == base is refused")

    # 3. Unknown actions never build an argv.
    try:
        argv_for("close", pr=1)
        fails.append("an unknown action builds an argv")
    except ValueError:
        pass

    if fails:
        for f in fails:
            print(f"pr-desk self-test FAIL: {f}", file=sys.stderr)
        return 1
    print("pr-desk self-test ok")
    return 0


def _isolated_argv(argv: List[str], isolated: bool, exe: str, script: Path) -> Optional[List[str]]:
    """Re-exec under `python3 -I <absolute path>` (the floor accepts a vetted ancestor only that way)."""
    if isolated or "--self-test" in argv:
        return None
    return [exe, "-I", str(Path(script).resolve()), *argv]


def main() -> int:
    again = _isolated_argv(sys.argv[1:], bool(sys.flags.isolated), sys.executable, Path(__file__))
    if again is not None:
        os.execv(sys.executable, again)
    if "--self-test" in sys.argv[1:]:
        return self_test()
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("action", choices=("status", "checks", "logs", "comments", "review-comments", "alerts", "merge"))
    parser.add_argument("--repo", type=Path, required=True, help="the checkout (gh reads the repo from its origin)")
    parser.add_argument("--pr", type=int, help="pull request number")
    parser.add_argument("--run", dest="run_id", help="workflow run id (logs)")
    parser.add_argument("--method", choices=METHODS, default="squash", help="merge method (default squash)")
    parser.add_argument("--approved", default="", help="Sean's approval, in his words (merge)")
    args = parser.parse_args()
    if args.action == "logs" and not (args.run_id and args.run_id.isdigit()):
        parser.error("logs needs --run <numeric run id>")
    if args.action != "logs" and not args.pr:
        parser.error(f"{args.action} needs --pr <number>")
    return run(args.action, args.repo, pr=args.pr, run_id=args.run_id, method=args.method, approved=args.approved)


if __name__ == "__main__":
    raise SystemExit(main())
