#!/usr/bin/env python3
"""A9 — a report may not stamp VERIFIED without saying what verified it.

The vault has an evidence-grade vocabulary (`VERIFIED` · `USER_REPORTED` · `INFERRED` ·
`INACCESSIBLE` · `NOT_EXPOSED` · `NOT_APPLICABLE`). It is a good convention and it is
exactly the convention that decays first: the grades keep appearing, the method that
earned them stops being written down, and the report reads as evidence while being
narrative. [[experiment-validity-baseline]]: an analysis with no pre-committed decision
rule produces a narrative, not evidence.

Two mechanical requirements for any REPORT that leans on the vocabulary:

  1. Declare the legend (or link the standard). A grade whose meaning is not on the page
     is a word, not a grade.
  2. Name a detector — a `09-tools/*.py`, a `vqa` command, a test runner, a `--check`, or
     an explicit "measured by". Something a reader can re-run.

And for a report that carries a quantitative claim, the pre-registration fields from
[[experiment-validity-baseline]] are required: primary metric, randomization unit,
expected direction, minimum effect, duration, stopping rule. That check is advisory
(`--strict` to enforce) because prose is not reliably classifiable and a lint that cries
wolf is a lint people route around.

Skills are exempt: `03-skills/` DEFINES this vocabulary, so using the words there is the
point rather than a claim.

Usage:
  python3 09-tools/validate-evidence-grades.py
  python3 09-tools/validate-evidence-grades.py --strict     # also enforce pre-registration
  python3 09-tools/validate-evidence-grades.py --self-test

Exit: 0 clean · 1 a report claims a grade it cannot support.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Where reports live. Everything else (skills, frameworks, adapters) is vocabulary, not claim.
REPORT_ROOTS = ["05-artifacts", "07-projects", "08-knowledge", "06-context/memory"]
SKIP_PARTS = {"_archive", ".git", "node_modules", "__pycache__", ".obsidian"}

GRADE_RE = re.compile(
    r"`(VERIFIED|USER_REPORTED|INFERRED|INACCESSIBLE|NOT_EXPOSED|NOT_APPLICABLE)`"
)
# Below this, the words are being used in passing, not as a report's evidence spine.
GRADE_THRESHOLD = 3

LEGEND_RE = re.compile(r"evidence[- ]grade legend|05-validation-harness|evidence grade[s]? legend", re.I)
DETECTOR_RE = re.compile(
    r"09-tools/[\w-]+\.py|\bvqa \w+|\bpytest\b|npm (?:run )?test|--check\b|measured by|"
    r"\bproofboard\b",
    re.I,
)
# A comparative number that implies a decision — the shape that needs pre-registration.
QUANT_RE = re.compile(r"\b\d+(?:\.\d+)?%|\b\d+/\d+\b|\bp\s*[<=]\s*0?\.\d+|\bn\s*=\s*\d+")
# Pre-registration is an EXPERIMENT requirement. An audit report full of percentages is
# not an experiment, and demanding a randomization unit of it is how a lint earns its way
# onto everybody's ignore list. Gate strict mode on experiment-shaped language — and on
# TWO DISTINCT signals, because one bare "experiment" is usually a trigger word in a
# routing table, which is exactly how this misfired on process-rigor-gaps (2026-09-15).
EXPERIMENT_RE = re.compile(
    r"(\bexperiment\b|\bA/B\b|\bab test\b|\bvariant group\b|\bcohort\b|\bcontrol group\b|"
    r"\bstatistical(?:ly)? significan\w*|\bhypothes[ei]s\b)",
    re.I,
)
PREREG_FIELDS = [
    ("primary metric", r"primary metric"),
    ("randomization unit", r"randomi[sz]ation unit|unit of randomi"),
    ("expected direction", r"expected direction"),
    ("minimum effect", r"minimum effect|minimum detectable|smallest effect"),
    ("duration", r"\bduration\b"),
    ("stopping rule", r"stopping rule"),
]


def report_files(root: Path = ROOT):
    for rel in REPORT_ROOTS:
        base = root / rel
        if not base.exists():
            continue
        for path in sorted(base.rglob("*.md")):
            if any(part in SKIP_PARTS for part in path.relative_to(root).parts):
                continue
            yield path


def audit_text(text: str, strict: bool = False) -> list[str]:
    """Return the failures for one document's text. Pure — the self-test drives this."""
    grades = GRADE_RE.findall(text)
    if len(grades) < GRADE_THRESHOLD:
        return []
    fails = []
    if not LEGEND_RE.search(text):
        fails.append(
            f"uses {len(grades)} evidence grades but never declares the legend "
            f"(state it, or link 02-shared-references/delivery-playbooks/05-validation-harness.md)"
        )
    if not DETECTOR_RE.search(text):
        fails.append(
            "claims evidence grades but names no detector — a reader cannot re-run "
            "anything, so VERIFIED is an assertion"
        )
    if strict and "VERIFIED" in grades and QUANT_RE.search(text) and len(set(m.lower() for m in EXPERIMENT_RE.findall(text))) >= 2:
        missing = [name for name, pat in PREREG_FIELDS if not re.search(pat, text, re.I)]
        if len(missing) == len(PREREG_FIELDS):
            fails.append(
                "quantitative claim marked VERIFIED with no pre-registration "
                f"({', '.join(name for name, _ in PREREG_FIELDS)}) — see experiment-validity-baseline"
            )
    return fails


def self_test() -> int:
    """Prove each rule can fail, and that the exemptions actually exempt."""
    failures = []

    def expect(name, cond):
        if not cond:
            failures.append(name)

    grades = " ".join(["`VERIFIED`"] * 4)
    legend = "**Evidence-grade legend:** `VERIFIED` · `INFERRED`"
    detector = "measured by `09-tools/workspace-harness.py --check`"

    expect("clean report passes", not audit_text(f"{legend}\n{detector}\n{grades}"))
    expect("missing legend fails",
           any("legend" in f for f in audit_text(f"{detector}\n{grades}")))
    expect("missing detector fails",
           any("detector" in f for f in audit_text(f"{legend}\n{grades}")))
    expect("below threshold is ignored", not audit_text("`VERIFIED` once, in passing"))
    expect("no grades at all is ignored", not audit_text("an ordinary document with prose"))

    quant = (f"{legend}\n{detector}\n{grades}\n"
             "the experiment showed conversion rose 14% in the variant group")
    expect("strict flags an unregistered quantitative claim", audit_text(quant, strict=True))
    expect("non-strict stays quiet on the same text", not audit_text(quant))
    registered = quant + ("\nprimary metric: activation. randomization unit: account. "
                          "expected direction: up. minimum effect: 2pp. duration: 3 weeks. "
                          "stopping rule: fixed horizon.")
    expect("strict accepts a pre-registered claim", not audit_text(registered, strict=True))
    audit_only = f"{legend}\n{detector}\n{grades}\n41 of 48 routes resolved (85%)"
    expect("strict ignores an audit report that is not an experiment",
           not audit_text(audit_only, strict=True))
    one_word = f"{legend}\n{detector}\n{grades}\n85% — row triggers on `experiment`"
    expect("strict ignores a lone experiment-word in a routing table",
           not audit_text(one_word, strict=True))

    for name in failures:
        print(f"  ✗ {name}")
    if failures:
        print(f"FAIL validate-evidence-grades self-test — {len(failures)} assertion(s)")
        return 1
    print("OK validate-evidence-grades self-test")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--strict", action="store_true",
                    help="also require pre-registration fields on quantitative VERIFIED claims")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        return self_test()

    errors, scanned = [], 0
    for path in report_files():
        text = path.read_text(encoding="utf-8", errors="replace")
        if not GRADE_RE.search(text):
            continue
        scanned += 1
        for fail in audit_text(text, strict=args.strict):
            errors.append(f"{path.relative_to(ROOT)}: {fail}")

    for e in errors:
        print(f"  ✗ {e}")
    if errors:
        print(f"evidence grades FAILED — {len(errors)} claim(s) without support "
              f"across {scanned} graded report(s)")
        return 1
    print(f"✓ evidence grades ok — {scanned} graded report(s), every grade has a legend "
          f"and a named detector")
    return 0


if __name__ == "__main__":
    sys.exit(main())
