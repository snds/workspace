#!/usr/bin/env python3
"""
check-terminology.py — enforce recorded terminology rules mechanically.

Some feedback in `06-context/memory/` is a *rule about words* — and a rule nothing checks
gets broken again. This turns those entries into a deterministic gate, the same
"guaranteed, not advisory" move the frameworks apply everywhere else.

Design constraints that keep it useful rather than noisy:
  * HIGH PRECISION over recall. A checker that cries wolf gets ignored, which is worse
    than no checker. Each rule flags only unambiguous misuse and carries an explicit
    allowlist of legitimate uses (including domain vocabulary, per each rule's caveat).
  * HISTORY IS NOT REWRITTEN. Session logs, archives, and the memory entry that *defines*
    a rule are exempt — they legitimately quote the wrong word.
  * SOURCED. Every rule points at the memory file it came from, so the fix is one hop away.

Usage:
  python3 09-tools/check-terminology.py             # report; exit 1 on any violation
  python3 09-tools/check-terminology.py --list      # show the active rules and exit
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

SCAN_SUFFIXES = {".md", ".py", ".json", ".yaml", ".yml", ".sh", ".mdc"}
# Historical record + rule definitions legitimately contain the banned word.
# `05-artifacts/` is exempt because artifacts are IMMUTABLE dated snapshots — the
# workspace rule is "never overwrite an artifact, increment the version", so editing
# one to satisfy a linter would break a stronger rule.
SKIP_PARTS = {"_archive", ".git", ".obsidian", "node_modules", "dist", "build",
              "__pycache__", ".venv", "sessions", "05-artifacts"}
SKIP_NAMES = {"session-log.md", "session-log-archive.md", "audit-log.md",
              "check-terminology.py",
              "MEMORY.md"}  # the memory INDEX names each rule by its own term
SKIP_STEM_PREFIX = ("feedback-",)  # a rule's own memory entry defines the term

RULES = [
    {
        "id": "vendor-as-verb",
        # Verb/adjective forms are the misuse: "vendored", "vendoring", "vendor_cli".
        # The NOUN forms ("vendor-neutral", "vendor formats", supply-chain "vendors")
        # are legitimate and deliberately not matched.
        "pattern": re.compile(r"\bvendor(?:ed|ing)\b|\bvendor_[a-z]", re.IGNORECASE),
        "allow": re.compile(
            r"vendor-provided|vendor-neutral|vendor-specific|cloud-vendor", re.IGNORECASE),
        "message": ('"vendor/vendored" is reserved for PAID external services/work. Our own '
                    'code copied between repos is: adopt · copy in · reuse · port · mirror. '
                    'An open-source dependency is a dependency. A local shim is a shim.'),
        "source": "06-context/memory/feedback-vendor-terminology.md",
    },
]


def _files():
    for p in ROOT.rglob("*"):
        if not p.is_file() or p.suffix not in SCAN_SUFFIXES:
            continue
        rel = p.relative_to(ROOT)
        if any(part in SKIP_PARTS for part in rel.parts):
            continue
        if p.name in SKIP_NAMES or p.stem.startswith(SKIP_STEM_PREFIX):
            continue
        yield p, rel


def main():
    if "--list" in sys.argv:
        print("terminology rules in force:\n")
        for r in RULES:
            print(f"  {r['id']}\n    {r['message']}\n    source: {r['source']}\n")
        return 0

    violations = []
    scanned = 0
    for p, rel in _files():
        try:
            text = p.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        scanned += 1
        for i, line in enumerate(text.splitlines(), 1):
            for rule in RULES:
                if not rule["pattern"].search(line):
                    continue
                if rule["allow"].search(line):
                    continue
                violations.append((rel, i, line.strip()[:100], rule))

    print("check-terminology — recorded word rules, mechanically enforced\n")
    if not violations:
        print(f"  ✓ no violations across {scanned} file(s), {len(RULES)} rule(s) in force.")
        return 0

    by_rule = {}
    for rel, ln, snippet, rule in violations:
        by_rule.setdefault(rule["id"], (rule, []))[1].append((rel, ln, snippet))

    for rid, (rule, hits) in by_rule.items():
        print(f"  ✗ {rid} — {len(hits)} violation(s)")
        print(f"    {rule['message']}")
        print(f"    rule: {rule['source']}\n")
        for rel, ln, snippet in hits[:25]:
            print(f"      · {rel}:{ln}")
            print(f"          {snippet}")
        if len(hits) > 25:
            print(f"      …and {len(hits) - 25} more")
        print()

    print(f"{len(violations)} violation(s) across {scanned} scanned file(s).")
    return 1


if __name__ == "__main__":
    sys.exit(main())
