#!/usr/bin/env python3
"""A4 — one entrypoint for the nightly maintenance recipe. Wrapper only; NOTHING schedules it.

`02-shared-references/nightly-maintenance-recipe.md` is the doctrine. This is the
executable form of it, so an agent runs one command instead of re-reading a markdown
list and hand-sequencing eight CLIs — which is the token cost the recipe was paying.

Deliberately NOT a `.sh`, despite the automation review naming `nightly.sh`: portable-first
is an AGENTS.md core rule and the fleet includes a Windows machine. Same stdlib-only Python
as every other tool here, so `python3 09-tools/nightly.py` works on all three machines.

Phases, in the order the recipe fixes:

  fold     compact-sessions.py — merge session fragments into the log (idempotent)
  rebuild  build-related -> build-registry -> build-trigger-routes. MUTATING, and the
           order is load-bearing: build-related rewrites Related blocks, build-registry
           hashes them, so registry-after-related or CI sees registry-drift.
  verify   workspace-harness.py — the whole gate chain, reachability, token budget.
           Read-only; it runs the generators in --check mode.
  watch    ds-source-watch.py --check — advisory. Never --fetch from here: network + judgment.
  commit   OPT-IN (--commit). Mechanical updates only.

Guardrails inherited from the recipe, enforced here:
  - Report, don't rewrite notes. No step makes an epistemic judgment. Resolving a #stale
    claim or archiving an orphan is /health plus a human.
  - Never invent skills. Minting is self-improve during an ordinary session, not a batch job.
  - Idempotent. Every phase is safe to re-run, and nothing deletes a note.

Usage:
  python3 09-tools/nightly.py                # fold, rebuild, verify, report
  python3 09-tools/nightly.py --dry-run      # print the plan, run nothing
  python3 09-tools/nightly.py --commit       # also commit mechanical updates
  python3 09-tools/nightly.py --json

Exit: 0 all phases clean · 1 a phase failed · 2 could not run.

To enable on a schedule, see the recipe's "How to enable". This file does not do it, and
adding a cron entry here would be enabling by stealth.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent

# (phase, script, args, mutating, advisory)
# advisory = a non-zero exit is reported but does not fail the run.
PHASES: list[tuple[str, str, list[str], bool, bool]] = [
    ("fold", "compact-sessions.py", [], True, False),
    ("rebuild", "build-related.py", [], True, False),
    ("rebuild", "build-registry.py", [], True, False),
    ("rebuild", "build-trigger-routes.py", [], True, False),
    ("verify", "workspace-harness.py", [], False, False),
    ("watch", "ds-source-watch.py", ["--check"], False, True),
]

SAFE_COMMIT_PATHS = [
    "03-skills/skills.registry.json",
    "02-shared-references/trigger-routes.md",
    "06-context/session-log.md",
    "06-context/session-log-archive.md",
    "06-context/sessions",
    "07-projects/19-workspace-brain/reports",
]


def run_step(script: str, args: list[str]) -> tuple[int, str, float]:
    target = TOOLS / script
    if not target.exists():
        return 127, f"missing: 09-tools/{script}", 0.0
    start = time.monotonic()
    proc = subprocess.run([sys.executable, str(target), *args],
                          capture_output=True, text=True, cwd=str(ROOT))
    out = (proc.stdout + proc.stderr).strip().splitlines()
    return proc.returncode, (out[-1] if out else ""), round(time.monotonic() - start, 2)


def commit_mechanical() -> tuple[int, str]:
    """Stage only the paths this run can legitimately have changed. Never `git add -A`.

    Nightly runs unattended by design, so an allowlist is the difference between
    committing a rebuilt index and committing whatever else was on disk.
    """
    present = [p for p in SAFE_COMMIT_PATHS if (ROOT / p).exists()]
    subprocess.run(["git", "add", "--", *present], cwd=str(ROOT), capture_output=True, text=True)
    staged = subprocess.run(["git", "diff", "--cached", "--name-only"],
                            cwd=str(ROOT), capture_output=True, text=True).stdout.split()
    if not staged:
        return 0, "nothing mechanical to commit"
    msg = ("Nightly maintenance: fold sessions, rebuild indexes.\n\n"
           "Mechanical only — generated indexes and folded session fragments.\n"
           "No note content was edited; epistemic findings are /health plus a human.\n")
    proc = subprocess.run(["git", "commit", "-m", msg], cwd=str(ROOT),
                          capture_output=True, text=True)
    return proc.returncode, f"committed {len(staged)} path(s)"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--commit", action="store_true", help="commit mechanical updates (opt-in)")
    ap.add_argument("--dry-run", action="store_true", help="print the plan, run nothing")
    ap.add_argument("--json", action="store_true", help="machine-readable report")
    args = ap.parse_args()

    if args.dry_run:
        print("nightly plan (nothing executed):")
        for phase, script, extra, mutating, advisory in PHASES:
            flags = " ".join(filter(None, ["MUTATES" if mutating else "read-only",
                                           "advisory" if advisory else ""]))
            print(f"  [{phase:<7}] python3 09-tools/{script} {' '.join(extra)}  ({flags})")
        print(f"  [commit ] {'yes (allowlisted paths)' if args.commit else 'skipped — pass --commit'}")
        return 0

    results, failed = [], 0
    for phase, script, extra, _mutating, advisory in PHASES:
        code, last, secs = run_step(script, extra)
        ok = code == 0
        if not ok and not advisory:
            failed += 1
        results.append({"phase": phase, "tool": script, "exit": code,
                        "status": "ok" if ok else ("advisory" if advisory else "FAIL"),
                        "seconds": secs, "last": last})
        if not args.json:
            mark = "✓" if ok else ("·" if advisory else "✗")
            print(f"  {mark} [{phase:<7}] {script:<28} {secs:>5.2f}s  {last[:64]}")

    commit_note = "skipped (pass --commit)"
    if args.commit and failed == 0:
        code, commit_note = commit_mechanical()
        if code != 0:
            failed += 1
    elif args.commit:
        commit_note = "skipped — a phase failed; refusing to commit on a red tree"

    if args.json:
        print(json.dumps({"phases": results, "failed": failed, "commit": commit_note}, indent=2))
    else:
        print(f"  · commit: {commit_note}")
        print(f"nightly: {'PASS' if failed == 0 else 'FAIL'} — {failed} failing phase(s)")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
