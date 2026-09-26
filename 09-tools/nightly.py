#!/usr/bin/env python3
"""A4/H1 — one entrypoint for the nightly maintenance recipe and the regeneration sequencer.

`02-shared-references/nightly-maintenance-recipe.md` is the doctrine. This is the
executable form of it, so an agent runs one command instead of re-reading a markdown
list and hand-sequencing the generators. NOTHING schedules it.

Deliberately NOT a `.sh`: portable-first is an AGENTS.md core rule. Stdlib-only Python,
like every other tool here.

Phases (run in this order; default fold,rebuild,verify,watch):

  fold     compact-sessions.py — merge session fragments into the log (idempotent)
  rebuild  the generator FIXPOINT, in this exact order:
             1. build-registry
             2. build-related          (rewrites Related blocks from the registry)
             3. build-registry again   (skipped when step 2 wrote 0 files)
             4. build-trigger-routes
  verify   workspace-harness.py — the whole gate chain. Read-only. With --from-diff (H11) the
           verify step is close-out-dispatch.py --from-diff --run instead: only the QUALITY_CHAIN
           steps the diff selects (--range R, else the working tree against HEAD; --fast drops the
           slow ones). CHARGED failures fail it, a SKIPPED step gives exit 3, and the report lists
           the charged step names under the step's `charged`.
  watch    ds-source-watch.py --check — advisory. Never --fetch from here.
  commit   opt-in (`--phases ...,commit` or `--commit`). Stages exactly the paths this
           run WROTE, and refuses unless the run's status is ok.

Written paths are computed from sha256 snapshots, taken before and after every step, of
the registry, every 03-skills/**/SKILL.md, trigger-routes.md, trigger-routes-digest.md,
06-context/session-log*.md and 06-context/sessions/*.md. A written path is FOREIGN when it had unstaged edits before
the run and is outside `--scope`; foreign edits give exit 4 and are never staged. When a
generator INPUT (any 03-skills/**/SKILL.md, trigger-routes.json, knowledge-hints.json) outside
`--scope` has unstaged edits, the whole heal is refused before any step runs: exit 4, nothing
written or staged, and the inputs are listed under `foreign_inputs`.

Scopes: all (default; nothing is foreign) · staged (the index) · session:SID (the
dispatcher touch ledger 06-context/sessions/<SID>.touched, plus every path dirty now
that was clean in .workspace/state/sessions/<SID>.json) · range:R (git diff --name-only R).

Usage:
  python3 09-tools/nightly.py                          # fold, rebuild, verify, watch
  python3 09-tools/nightly.py --dry-run                # print the plan, run nothing
  python3 09-tools/nightly.py --phases rebuild --json  # the fixpoint, with written paths
  python3 09-tools/nightly.py --check --phases rebuild # generators in --check mode; writes nothing
  python3 09-tools/nightly.py --lane pre-commit        # stateless pre-commit lane (git hook)
  python3 09-tools/nightly.py --phases verify --from-diff --range @{u}..HEAD --fast --budget 20 --json
                                                       # the H11 gate the git lanes run
  python3 09-tools/nightly.py --self-test

Exit: 0 clean · 1 a FAIL (or drift under --check) · 2 could not run · 3 SKIPPED present
(timeout or budget; never green) · 4 refused (foreign edits on written paths).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
FIXTURES = TOOLS / "fixtures" / "nightly"

PHASE_ORDER = ["fold", "rebuild", "verify", "watch", "commit"]
DEFAULT_PHASES = ["fold", "rebuild", "verify", "watch"]
DEFAULT_STEP_TIMEOUT = 15.0
# workspace-harness runs the whole gate chain (~30 s on the live tree). Under a flat 15 s
# default the default run would always report verify SKIPPED, so verify keeps its own
# default. An explicit --step-timeout and --budget still cap it.
VERIFY_STEP_TIMEOUT = 180.0
GIT_TIMEOUT = 10.0

# One entry per step. `check_args` None = no --check form (the fixpoint's second pass).
# advisory = a non-zero exit is reported but does not fail the run.
PHASES: list[dict] = [
    {"phase": "fold", "tool": "compact-sessions.py", "args": [], "check_args": ["--check"],
     "mutating": True, "advisory": False},
    {"phase": "rebuild", "tool": "build-registry.py", "args": [], "check_args": ["--check"],
     "mutating": True, "advisory": False},
    {"phase": "rebuild", "tool": "build-related.py", "args": [], "check_args": ["--check"],
     "mutating": True, "advisory": False, "feeds_fixpoint": True},
    {"phase": "rebuild", "tool": "build-registry.py", "args": [], "check_args": None,
     "mutating": True, "advisory": False, "fixpoint": True},
    {"phase": "rebuild", "tool": "build-trigger-routes.py", "args": [], "check_args": ["--check"],
     "mutating": True, "advisory": False},
    {"phase": "verify", "tool": "workspace-harness.py", "args": [], "check_args": [],
     "mutating": False, "advisory": False, "default_timeout": VERIFY_STEP_TIMEOUT},
    {"phase": "watch", "tool": "ds-source-watch.py", "args": ["--check"], "check_args": ["--check"],
     "mutating": False, "advisory": True},
]

# Generator INPUTS: an unstaged edit on one of these outside --scope changes what the rebuild
# would write (the registry hashes every SKILL.md), so the whole heal is refused.
GENERATOR_INPUT_RE = re.compile(r"^03-skills/.+/SKILL\.md$")
GENERATOR_INPUTS = ("02-shared-references/trigger-routes.json",
                    "02-shared-references/knowledge-hints.json")


def foreign_generator_inputs(pre_unstaged: set[str], scope_paths: set[str] | None) -> list[str]:
    """Generator inputs with unstaged edits before the run and outside --scope."""
    if scope_paths is None:
        return []
    return sorted(p for p in pre_unstaged
                  if (GENERATOR_INPUT_RE.match(p) or p in GENERATOR_INPUTS) and p not in scope_paths)


# Staged paths that make the pre-commit lane run the rebuild check.
LANE_SOURCES = ("02-shared-references/trigger-routes.json",
                "02-shared-references/knowledge-hints.json")
LANE_EXPORT = ["03-skills", "02-shared-references/trigger-routes.json",
               "02-shared-references/trigger-routes.md",
               "02-shared-references/trigger-routes-digest.md",
               "02-shared-references/knowledge-hints.json",
               "09-tools/build-registry.py", "09-tools/build-related.py",
               "09-tools/build-trigger-routes.py"]
LANE_FIX_1 = "python3 09-tools/nightly.py --phases rebuild --scope staged --json"
LANE_FIX_2 = 'git add -- <paths listed under "written">'


# ---------- git + snapshots ----------


def _git(args: list[str], *, root: Path = ROOT, timeout: float = GIT_TIMEOUT):
    """Run git; None when git is missing, times out, or cannot start."""
    try:
        return subprocess.run(["git", *args], cwd=str(root), capture_output=True,
                              text=True, timeout=timeout)
    except (OSError, subprocess.TimeoutExpired):
        return None


def _z_paths(out: str) -> list[str]:
    return [p for p in out.split("\0") if p]


def snapshot(root: Path = ROOT) -> dict[str, str]:
    """sha256 of every path a nightly step may write (the declared written set)."""
    files: list[Path] = []
    files.append(root / "03-skills" / "skills.registry.json")
    skills = root / "03-skills"
    if skills.is_dir():
        files.extend(sorted(skills.glob("**/SKILL.md")))
    files.append(root / "02-shared-references" / "trigger-routes.md")
    files.append(root / "02-shared-references" / "trigger-routes-digest.md")
    ctx = root / "06-context"
    if ctx.is_dir():
        files.extend(sorted(ctx.glob("session-log*.md")))
        if (ctx / "sessions").is_dir():
            files.extend(sorted((ctx / "sessions").glob("*.md")))
    out: dict[str, str] = {}
    for f in files:
        try:
            if f.is_file():
                out[f.relative_to(root).as_posix()] = hashlib.sha256(f.read_bytes()).hexdigest()
        except OSError:
            continue
    return out


def written_between(before: dict[str, str], after: dict[str, str]) -> list[str]:
    return sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k))


def _porcelain(root: Path = ROOT) -> list[tuple[str, str]] | None:
    """[(XY, path)] from `git status --porcelain=v1 -z`; None when git fails."""
    r = _git(["status", "--porcelain=v1", "-z", "--untracked-files=all"], root=root)
    if r is None or r.returncode != 0:
        return None
    out: list[tuple[str, str]] = []
    parts = r.stdout.split("\0")
    i = 0
    while i < len(parts):
        rec = parts[i]
        i += 1
        if len(rec) < 4:
            continue
        if rec[0] in "RC":
            i += 1  # the rename/copy source follows as its own NUL field
        out.append((rec[:2], rec[3:]))
    return out


def unstaged_paths(root: Path = ROOT) -> set[str]:
    """Paths whose worktree differs from the index, plus untracked files."""
    return {p for xy, p in (_porcelain(root) or []) if xy == "??" or xy[1] != " "}


def _dirty_now(root: Path) -> set[str]:
    return {p for _xy, p in (_porcelain(root) or [])}


def _safe_sid(sid: str) -> str:
    # Same sanitisation as the dispatcher's touch ledger file name.
    return re.sub(r"[^A-Za-z0-9._-]", "-", sid)[:80]


def resolve_scope(scope: str, root: Path = ROOT) -> set[str] | None:
    """None means every path is in scope. Raises ValueError when it cannot be resolved."""
    if scope == "all":
        return None
    if scope == "staged":
        r = _git(["diff", "--cached", "--name-only", "-z"], root=root)
        if r is None or r.returncode != 0:
            raise ValueError("cannot read the index (git diff --cached failed)")
        return set(_z_paths(r.stdout))
    if scope.startswith("range:"):
        rng = scope[len("range:"):]
        if not rng:
            raise ValueError("range:R needs a revision range")
        r = _git(["diff", "--name-only", "-z", rng], root=root)
        if r is None or r.returncode != 0:
            raise ValueError(f"cannot diff range {rng!r}")
        return set(_z_paths(r.stdout))
    if scope.startswith("session:"):
        sid = scope[len("session:"):]
        if not sid:
            raise ValueError("session:SID needs a session id")
        paths: set[str] = set()
        ledger = root / "06-context" / "sessions" / f"{_safe_sid(sid)}.touched"
        try:
            if ledger.is_file():
                paths.update(ln.strip() for ln in ledger.read_text(encoding="utf-8").splitlines()
                             if ln.strip())
        except OSError:
            pass
        base_dir = root / ".workspace" / "state" / "sessions"
        for name in (f"{sid}.json", f"{_safe_sid(sid)}.json"):
            bf = base_dir / name
            if not bf.is_file():
                continue
            try:
                base = json.loads(bf.read_text(encoding="utf-8"))
                was_dirty = {e.get("path") for e in base.get("porcelain") or []
                             if isinstance(e, dict)}
            except (OSError, ValueError, AttributeError):
                break
            paths.update(p for p in _dirty_now(root) if p not in was_dirty)
            break
        return paths
    raise ValueError(f"unknown scope {scope!r} (all|staged|session:SID|range:R)")


# ---------- steps ----------


def run_step(script: str, args: list[str], timeout: float | None,
             tools: Path = TOOLS, root: Path = ROOT, sink: dict | None = None) -> tuple[int | None, str, float, bool]:
    """(exit, last line, seconds, timed_out). Exit None when it timed out. `sink` receives stdout."""
    target = tools / script
    if not target.exists():
        return 127, f"missing: 09-tools/{script}", 0.0, False
    start = time.monotonic()
    try:
        proc = subprocess.run([sys.executable, str(target), *args], capture_output=True,
                              text=True, cwd=str(root), timeout=timeout)
    except subprocess.TimeoutExpired:
        return None, f"timed out after {timeout:.1f}s", round(time.monotonic() - start, 2), True
    if sink is not None:
        sink["stdout"] = proc.stdout
    out = (proc.stdout + proc.stderr).strip().splitlines()
    return proc.returncode, (out[-1] if out else ""), round(time.monotonic() - start, 2), False


def diff_gate_args(args: argparse.Namespace, timeout: float | None) -> list[str]:
    """close-out-dispatch.py arguments for the --from-diff verify step (H11)."""
    out = ["--from-diff", "--run", "--json", "--via", args.via or "nightly"]
    if args.range:
        out += ["--range", args.range]
    if args.fast:
        out.append("--fast")
    if timeout is not None:
        out += ["--budget", f"{max(1.0, timeout - 2.0):.1f}"]
    return out


def gate_charged(stdout: str) -> list[str]:
    """The CHARGED step names from close-out-dispatch --from-diff --json output ([] when unparseable)."""
    try:
        obj = json.loads(stdout)
    except ValueError:
        return []
    rows = obj.get("results") if isinstance(obj, dict) else None
    return [str(r.get("step")) for r in rows or [] if isinstance(r, dict) and r.get("status") == "CHARGED"]


def commit_written(paths: list[str]) -> tuple[int, str]:
    """Stage exactly the paths this run wrote, then commit. Never `git add -A`."""
    if not paths:
        return 0, "nothing mechanical to commit"
    add = _git(["add", "-A", "--", *paths])
    if add is None or add.returncode != 0:
        return 1, "git add failed; nothing committed"
    staged = _git(["diff", "--cached", "--name-only"])
    if staged is None or not staged.stdout.split():
        return 0, "nothing mechanical to commit"
    msg = ("Nightly maintenance: fold sessions, rebuild indexes.\n\n"
           "Mechanical only — generated indexes and folded session fragments.\n"
           "No note content was edited; epistemic findings are /health plus a human.\n")
    proc = _git(["commit", "-m", msg], timeout=30)
    if proc is None or proc.returncode != 0:
        return 1, "git commit failed"
    return 0, f"committed {len(staged.stdout.split())} path(s)"


def _ordered_phases(raw: str, commit_flag: bool) -> list[str]:
    wanted = [p.strip() for p in raw.split(",") if p.strip()]
    bad = [p for p in wanted if p not in PHASE_ORDER]
    if bad:
        raise ValueError(f"unknown phase(s): {', '.join(bad)} (known: {', '.join(PHASE_ORDER)})")
    if commit_flag and "commit" not in wanted:
        wanted.append("commit")
    return [p for p in PHASE_ORDER if p in wanted]


def run(args: argparse.Namespace) -> tuple[int, dict]:
    started = time.monotonic()
    phases = _ordered_phases(args.phases, args.commit)
    scope_paths = resolve_scope(args.scope)
    pre_unstaged = set() if args.check else unstaged_paths()
    budget = args.budget
    foreign_inputs = [] if args.check else foreign_generator_inputs(pre_unstaged, scope_paths)
    if foreign_inputs and any(ph in phases for ph in ("fold", "rebuild")):
        results = [{"phase": st["phase"], "tool": st["tool"], "exit": None, "status": "SKIPPED",
                    "seconds": 0.0, "last": "refused: foreign unstaged generator inputs", "written": [],
                    "pass": False} for st in PHASES if st["phase"] in phases]
        return 4, {
            "schema_version": 1, "cmd": "nightly", "status": "refused", "phases": results, "failed": 0,
            "commit": "refused — foreign unstaged generator inputs; nothing written or staged",
            "written": [], "foreign": foreign_inputs, "foreign_inputs": foreign_inputs,
            "scope": args.scope, "scope_paths": None if scope_paths is None else sorted(scope_paths),
            "budget_s": budget, "elapsed_s": round(time.monotonic() - started, 2), "skipped": [],
            "check": False, "fix": None,
        }

    results: list[dict] = []
    skipped: list[dict] = []
    written_all: list[str] = []
    rebuild_blocked = False
    related_ok = False
    related_wrote = 0

    for step in PHASES:
        if step["phase"] not in phases:
            continue
        cmd_args = step["check_args"] if args.check else step["args"]
        entry = {"phase": step["phase"], "tool": step["tool"], "exit": None, "status": "",
                 "seconds": 0.0, "last": "", "written": [], "pass": False}
        results.append(entry)
        reason = ""
        if step.get("fixpoint") and (args.check or (related_ok and related_wrote == 0)):
            entry.update(status="noop", last="build-related wrote 0 files; second pass not needed")
            entry["pass"] = True
            continue
        if step["phase"] == "rebuild" and rebuild_blocked:
            reason = "upstream rebuild step did not pass"
        remaining = None if budget is None else budget - (time.monotonic() - started)
        if not reason and remaining is not None and remaining <= 0:
            reason = "budget exhausted"
        if reason:
            entry.update(status="SKIPPED", last=reason)
            skipped.append({"phase": step["phase"], "tool": step["tool"], "reason": reason})
            if step["phase"] == "rebuild":
                rebuild_blocked = True
            continue
        step_timeout = args.step_timeout
        if step_timeout is None:
            step_timeout = step.get("default_timeout", DEFAULT_STEP_TIMEOUT)
        by_budget = remaining is not None and remaining < step_timeout
        timeout = remaining if by_budget else step_timeout
        tool, sink = step["tool"], None
        if step["phase"] == "verify" and getattr(args, "from_diff", False):
            tool, cmd_args, sink = "close-out-dispatch.py", diff_gate_args(args, timeout), {}
            entry["tool"] = tool
        before = snapshot()
        code, last, secs, timed_out = run_step(tool, list(cmd_args or []), timeout, sink=sink)
        after = snapshot()
        wrote = written_between(before, after)
        entry.update(exit=code, seconds=secs, last=last, written=wrote)
        if sink is not None:
            entry["charged"] = gate_charged(sink.get("stdout") or "")
            if code == 2:
                # close-out-dispatch exit 2: a step SKIPPED or nothing ran. Never green, never red.
                entry.update(status="SKIPPED", last=f"diff gate skipped — {last}")
                skipped.append({"phase": step["phase"], "tool": tool, "reason": "a diff-selected step SKIPPED"})
                continue
        for p in wrote:
            if p not in written_all:
                written_all.append(p)
        if step.get("feeds_fixpoint"):
            related_wrote = len(wrote)
            related_ok = code == 0 and not timed_out
        if timed_out:
            why = "budget exhausted" if by_budget else f"step timeout {step_timeout:g}s"
            entry.update(status="SKIPPED", last=f"{why} — {last}")
            skipped.append({"phase": step["phase"], "tool": step["tool"], "reason": why})
        elif code == 0:
            entry.update(status="ok")
            entry["pass"] = True
        elif step["advisory"]:
            entry.update(status="advisory")
            entry["pass"] = True
        else:
            entry.update(status="FAIL")
        if step["phase"] == "rebuild" and entry["status"] in ("SKIPPED", "FAIL") and not args.check:
            rebuild_blocked = True

    failed = sum(1 for e in results if e["status"] == "FAIL")
    foreign = sorted(p for p in written_all
                     if p in pre_unstaged and scope_paths is not None and p not in scope_paths)
    if failed:
        status, rc = "fail", 1
    elif foreign:
        status, rc = "refused", 4
    elif skipped:
        status, rc = "skipped", 3
    else:
        status, rc = "ok", 0

    commit_note = "skipped (pass --commit or --phases ...,commit)"
    committed = False
    if "commit" in phases:
        if args.check:
            commit_note = "skipped — --check writes nothing"
        elif status != "ok":
            commit_note = f"refused — run status is {status}; never commit a non-green tree"
        else:
            code, commit_note = commit_written(written_all)
            committed = code == 0 and commit_note.startswith("committed")
            if code != 0:
                failed += 1
                status, rc = "fail", 1

    fix = None
    if status == "ok" and written_all and not committed and not args.check:
        fix = "git add -- " + " ".join(shlex.quote(p) for p in written_all)

    report = {
        "schema_version": 1, "cmd": "nightly", "status": status, "phases": results,
        "failed": failed, "commit": commit_note, "written": written_all, "foreign": foreign,
        "scope": args.scope,
        "scope_paths": None if scope_paths is None else sorted(scope_paths),
        "budget_s": budget, "elapsed_s": round(time.monotonic() - started, 2),
        "skipped": skipped, "check": bool(args.check), "fix": fix, "foreign_inputs": [],
    }
    return rc, report


# ---------- pre-commit lane ----------


def _lane_matches(path: str) -> bool:
    return (path.startswith("03-skills/") and path.endswith("/SKILL.md")) or path in LANE_SOURCES


def lane_pre_commit(root: Path = ROOT, timeout: float = DEFAULT_STEP_TIMEOUT) -> int:
    """Stateless pre-commit lane. Checks the generators against the INDEX being committed.

    Exit 0 silently unless a staged path is a skill source; exit 1 with exactly two fix
    lines on drift. Infrastructure errors fail open (exit 0 with a one-line notice): CI
    re-checks every push.
    """
    staged = _git(["diff", "--cached", "--name-only", "-z"], root=root)
    if staged is None or staged.returncode != 0:
        print("nightly lane: could not read the index; skipped (CI re-checks)", file=sys.stderr)
        return 0
    if not any(_lane_matches(p) for p in _z_paths(staged.stdout)):
        return 0
    listed = _git(["ls-files", "-z", "--", *LANE_EXPORT], root=root)
    if listed is None or listed.returncode != 0:
        print("nightly lane: could not list the index; skipped (CI re-checks)", file=sys.stderr)
        return 0
    drift: list[str] = []
    with tempfile.TemporaryDirectory(prefix="nightly-lane-") as td:
        prefix = str(Path(td) / "tree") + os.sep
        try:
            exp = subprocess.run(["git", "checkout-index", "-z", "--stdin", f"--prefix={prefix}"],
                                 cwd=str(root), input=listed.stdout, capture_output=True,
                                 text=True, timeout=GIT_TIMEOUT)
        except (OSError, subprocess.TimeoutExpired):
            exp = None
        if exp is None or exp.returncode != 0:
            print("nightly lane: could not export the index; skipped (CI re-checks)", file=sys.stderr)
            return 0
        tree = Path(prefix)
        tools = tree / "09-tools"
        tools.mkdir(parents=True, exist_ok=True)
        for gen in ("build-registry.py", "build-related.py", "build-trigger-routes.py"):
            if not (tools / gen).is_file() and (TOOLS / gen).is_file():
                shutil.copy2(TOOLS / gen, tools / gen)
        for gen in ("build-registry.py", "build-related.py", "build-trigger-routes.py"):
            code, _last, _secs, timed_out = run_step(gen, ["--check"], timeout, tools=tools, root=tree)
            if timed_out or code == 127:
                print(f"nightly lane: {gen} --check could not run; skipped (CI re-checks)",
                      file=sys.stderr)
                return 0
            if code != 0:
                drift.append(gen)
    if not drift:
        return 0
    print(f"nightly lane: generated files are stale for the staged skill sources "
          f"({', '.join(drift)}); commit refused. Fix:", file=sys.stderr)
    print(LANE_FIX_1, file=sys.stderr)
    print(LANE_FIX_2, file=sys.stderr)
    return 1


# ---------- entry ----------


def _print_human(report: dict) -> None:
    marks = {"ok": "✓", "advisory": "·", "noop": "=", "SKIPPED": "…", "FAIL": "✗"}
    for e in report["phases"]:
        mark = marks.get(e["status"], "?")
        wrote = f"  wrote {len(e['written'])}" if e["written"] else ""
        print(f"  {mark} [{e['phase']:<7}] {e['tool']:<26} {e['seconds']:>5.2f}s  "
              f"{e['status']:<8} {e['last'][:56]}{wrote}")
    print(f"  · commit: {report['commit']}")
    if report.get("foreign_inputs"):
        print("  ✗ refused: another session has unstaged edits on generator inputs (nothing written; "
              "resolve or commit them first):")
        for p in report["foreign_inputs"]:
            print(f"      {p}")
    elif report["foreign"]:
        print("  ✗ foreign unstaged edits on written paths (not staged; resolve first):")
        for p in report["foreign"]:
            print(f"      {p}")
    if report["fix"]:
        print(f"  fix: {report['fix']}")
    print(f"nightly: {report['status'].upper()} — {report['failed']} failing step(s), "
          f"{len(report['skipped'])} skipped, {len(report['written'])} written")


def _self_test() -> int:
    target = FIXTURES / "selftest_nightly.py"
    if not target.is_file():
        print(f"nightly self-test: missing {target.relative_to(ROOT)}", file=sys.stderr)
        return 1
    sys.path.insert(0, str(FIXTURES))
    try:
        import selftest_nightly  # noqa: PLC0415 — fixture module, loaded on demand
    except Exception as exc:  # noqa: BLE001
        print(f"nightly self-test: cannot load fixtures: {exc}", file=sys.stderr)
        return 1
    return int(selftest_nightly.run(ROOT))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--phases", default=",".join(DEFAULT_PHASES),
                    help="comma list of fold,rebuild,verify,watch,commit")
    ap.add_argument("--check", action="store_true",
                    help="run the generators in --check mode; write nothing; exit 1 on drift")
    ap.add_argument("--scope", default="all", help="all|staged|session:SID|range:R")
    ap.add_argument("--budget", type=float, default=None, help="total seconds for all steps")
    ap.add_argument("--step-timeout", type=float, default=None,
                    help=f"seconds per step (default {DEFAULT_STEP_TIMEOUT:g}; verify "
                         f"{VERIFY_STEP_TIMEOUT:g})")
    ap.add_argument("--commit", action="store_true", help="same as adding commit to --phases")
    ap.add_argument("--dry-run", action="store_true", help="print the plan, run nothing")
    ap.add_argument("--json", action="store_true", help="machine-readable report")
    ap.add_argument("--lane", choices=["pre-commit"], help="stateless git-hook lane")
    ap.add_argument("--from-diff", action="store_true",
                    help="verify runs close-out-dispatch --from-diff (the diff-selected gate), not the whole harness")
    ap.add_argument("--range", default=None, help="with --from-diff: the revision range to diff (A..B)")
    ap.add_argument("--fast", action="store_true", help="with --from-diff: drop the steps measured over 5 s")
    ap.add_argument("--via", default=None, help="with --from-diff: who invoked the gate (receipt field)")
    ap.add_argument("--self-test", action="store_true", help="run the fixtures")
    args = ap.parse_args(argv)

    if args.self_test:
        return _self_test()
    if args.lane == "pre-commit":
        return lane_pre_commit()
    if (args.range or args.fast or args.via) and not args.from_diff:
        print("nightly: --range, --fast and --via need --from-diff", file=sys.stderr)
        return 2
    try:
        phases = _ordered_phases(args.phases, args.commit)
    except ValueError as exc:
        print(f"nightly: {exc}", file=sys.stderr)
        return 2
    if args.dry_run:
        print("nightly plan (nothing executed):")
        for step in PHASES:
            if step["phase"] not in phases:
                continue
            extra = step["check_args"] if args.check else step["args"]
            tool = step["tool"]
            if step["phase"] == "verify" and args.from_diff:
                tool, extra = "close-out-dispatch.py", diff_gate_args(args, args.budget)
            if step.get("fixpoint"):
                note = "fixpoint pass; skipped when build-related wrote 0 files"
            else:
                note = " ".join(filter(None, [
                    "MUTATES" if step["mutating"] and not args.check else "read-only",
                    "advisory" if step["advisory"] else ""]))
            print(f"  [{step['phase']:<7}] python3 09-tools/{tool} "
                  f"{' '.join(extra or [])}  ({note})")
        print(f"  [commit ] {'yes (written paths only)' if 'commit' in phases else 'skipped'}")
        print(f"  scope: {args.scope}")
        return 0
    try:
        rc, report = run(args)
    except ValueError as exc:
        if args.json:
            print(json.dumps({"schema_version": 1, "cmd": "nightly", "status": "error",
                              "error": str(exc)}, indent=2))
        print(f"nightly: could not run — {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        _print_human(report)
    return rc


if __name__ == "__main__":
    sys.exit(main())
