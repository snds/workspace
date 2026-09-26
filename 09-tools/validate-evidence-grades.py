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

`--status` (H8) is the report-to-register lane. A versioned report is a dated snapshot and is
never edited to say what happened next; the current state of its recommendations lives in a
findings register (a remediation spec's `## Findings` table, see intent-spec). The lane walks
git-tracked report roots only and flags a versioned report whose frontmatter `status:` pairs a
closure word (applied, resolved, closed, …) with an ID range or list while no tracked findings
row cites the report in `origin` or `closed_by`. Resolution runs one way: register → report.
It is report-only against a census ceiling: it fails only when the count rises above it.

Usage:
  python3 09-tools/validate-evidence-grades.py
  python3 09-tools/validate-evidence-grades.py --strict     # also enforce pre-registration
  python3 09-tools/validate-evidence-grades.py --status     # report → findings-register census
  python3 09-tools/validate-evidence-grades.py --self-test

Exit: 0 clean · 1 a report claims a grade it cannot support (or --status rose above the ceiling).
"""

from __future__ import annotations

import argparse
import re
import subprocess
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


# --status: the census ceiling may only go down (raise it only with a deliberate diff).
STATUS_CEILING = 0
VERSIONED_RE = re.compile(r"^(?P<slug>.+?)_v\d+\.\d+_\d{4}-\d{2}-\d{2}\.md$")
CLOSURE_WORD_RE = re.compile(r"\b(applied|resolved|closed|fixed|landed|done|completed?)\b", re.I)
ID_SPAN_RE = re.compile(r"\b[A-Z]{0,3}\d+\s*[–-]\s*[A-Z]{0,3}\d+\b|\b[A-Z]+\d+(?:\s*[,/]\s*[A-Z]+\d+)+")
ISO_DATE_RE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")


def _tracked(root: Path, *pathspecs: str) -> list[str]:
    r = subprocess.run(["git", "ls-files", "-z", "--", *pathspecs], cwd=str(root), capture_output=True,
                       text=True, timeout=30)
    return [p for p in r.stdout.split("\0") if p] if r.returncode == 0 else []


def _frontmatter_status(text: str) -> str:
    if not text.startswith("---"):
        return ""
    end = text.find("\n---", 3)
    for line in text[3:end if end > 0 else 0].splitlines():
        if line.lower().startswith("status:"):
            return line.split(":", 1)[1].strip()
    return ""


def status_claims(status: str) -> bool:
    """True when a status pairs a closure word with an ID range or list (dates are not ranges)."""
    bare = ISO_DATE_RE.sub(" ", status)
    return bool(CLOSURE_WORD_RE.search(bare) and ID_SPAN_RE.search(bare))


def _register_cells(text: str) -> list[str]:
    """origin and closed_by cells of the `## Findings` table in one document."""
    m = re.search(r"^##\s+Findings\s*$", text, re.M | re.I)
    if not m:
        return []
    header: list[str] | None = None
    cells: list[str] = []
    for line in text[m.end():].splitlines():
        line = line.strip()
        if line.startswith("## "):
            break
        if not line.startswith("|"):
            if header:
                break
            continue
        row = [c.strip() for c in re.split(r"(?<!\\)\|", line.strip("|"))]
        if all(set(c) <= set("-: ") for c in row):
            continue
        if header is None:
            header = [re.sub(r"[^a-z0-9]+", "_", c.lower()).strip("_") for c in row]
            continue
        for key in ("origin", "closed_by"):
            if key in header and header.index(key) < len(row):
                cells.append(row[header.index(key)])
    return cells


def status_census(root: Path = ROOT) -> list[str]:
    """Versioned, tracked reports whose status claims closure that no tracked findings row cites."""
    reports = [p for p in _tracked(root, *REPORT_ROOTS)
               if p.endswith(".md") and VERSIONED_RE.match(p.rsplit("/", 1)[-1])
               and not any(part in SKIP_PARTS for part in p.split("/"))]
    cells: list[str] = []
    for p in _tracked(root, "*.md"):
        try:
            text = (root / p).read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if "## Findings" in text:
            cells += _register_cells(text)
    cited = " ".join(cells)
    flagged = []
    for p in reports:
        try:
            status = _frontmatter_status((root / p).read_text(encoding="utf-8", errors="replace"))
        except OSError:
            continue
        slug = VERSIONED_RE.match(p.rsplit("/", 1)[-1]).group("slug")
        if status_claims(status) and not re.search(rf"(?<![\w-]){re.escape(slug)}(?=#|_v\d|[^\w-]|$)", cited):
            flagged.append(f"{p}: status claims closure ({status[:70]}) but no tracked findings row cites "
                           f"`{slug}` in origin or closed_by")
    return flagged


def run_status(root: Path = ROOT, ceiling: int = STATUS_CEILING) -> int:
    flagged = status_census(root)
    for f in flagged:
        print(f"  · {f}")
    over = len(flagged) > ceiling
    print(f"{'✗' if over else '✓'} report status census — {len(flagged)} uncited closure claim(s) "
          f"(ceiling {ceiling}); register → report, never the reverse")
    return 1 if over else 0


def _status_self_test() -> list[str]:
    """Replay the real shape: a report whose status says applied while one rec waited, uncited."""
    import contextlib
    import io
    import os
    import tempfile
    bad: list[str] = []
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update({"GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull})
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)

        def git(*args):
            subprocess.run(["git", *args], cwd=td, env=env, capture_output=True, timeout=30, check=True)

        git("init", "-q", "-b", "main")
        rep = root / "07-projects" / "01-x" / "reports" / "auto-review_v1.0_2026-01-01.md"
        rep.parent.mkdir(parents=True)
        rep.write_text("---\nstatus: first wave applied 2026-01-01 — A1, A2 wired; A8 deferred\n---\n# r\n")
        untracked = root / "05-artifacts" / "active" / "emp_review_v1.0_2026-01-01.md"
        untracked.parent.mkdir(parents=True)
        untracked.write_text("---\nstatus: applied — recs 1–9\n---\n")
        git("add", str(rep.relative_to(root)))
        flagged = status_census(root)
        if len(flagged) != 1 or "auto-review" not in flagged[0]:
            bad.append(f"status: an uncited applied+IDs report is flagged once, an untracked one never ({flagged})")
        with contextlib.redirect_stdout(io.StringIO()):
            ceiling_ok = run_status(root, ceiling=0) == 1 and run_status(root, ceiling=1) == 0
        if not ceiling_ok:
            bad.append("status: the ceiling decides the exit")
        spec = root / "07-projects" / "01-x" / "docs" / "INTENT-remediation.md"
        spec.parent.mkdir(parents=True)
        spec.write_text("---\nkind: remediation\n---\n## Findings\n\n| id | status | origin | closed_by |\n"
                        "|---|---|---|---|\n| F-001 | RESOLVED | auto-review#A8 | probe_v1.0 |\n")
        if len(status_census(root)) != 1:
            bad.append("status: an untracked register row must not clear the flag")
        git("add", str(spec.relative_to(root)))
        if status_census(root):
            bad.append(f"status: a tracked citing RESOLVED row clears the flag ({status_census(root)})")
        if status_claims("applied 2026-09-11") or not status_claims("applied — recs R1–R16"):
            bad.append("status: dates are not ranges; R1–R16 is")
    return bad


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

    failures += _status_self_test()
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
    ap.add_argument("--status", action="store_true",
                    help="report → findings-register census over tracked versioned reports (H8)")
    args = ap.parse_args()

    if args.self_test:
        return self_test()
    if args.status:
        return run_status()

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
