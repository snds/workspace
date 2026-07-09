#!/usr/bin/env python3
"""
validate-workspace.py — governance integrity checks for the workspace.

Checks:
  1. ARCHIVE PROVENANCE — every file under `_archive/` (except the log itself) is referenced in
     `_archive/ARCHIVE-LOG.md`. Enforces the "never delete; archive with provenance" rule.   [error]
  2. MEMORY COVERAGE    — every memory file in `06-context/memory/` (except `_template.md` and
     `MEMORY.md`) is listed in `MEMORY.md`, so the session-start index stays complete.        [error]
  3. KNOWLEDGE COVERAGE — every entry under `08-knowledge/` (except `_README.md`, `_INDEX.md`,
     and `_archive/`) is listed in `_INDEX.md`, so trigger routing and session-start surfacing
     never silently miss an entry (added 2026-07-08 after unindexed entries were found).      [error]

Stdlib-only. See 01-frameworks/08-workspace-contribution-framework.md (Archive + Memory protocols).

Usage:
  python3 09-tools/validate-workspace.py
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARCHIVE = ROOT / "_archive"
ARCHIVE_LOG = ARCHIVE / "ARCHIVE-LOG.md"
MEMORY_DIR = ROOT / "06-context" / "memory"
MEMORY_INDEX = MEMORY_DIR / "MEMORY.md"
KNOWLEDGE_DIR = ROOT / "08-knowledge"
KNOWLEDGE_INDEX = KNOWLEDGE_DIR / "_INDEX.md"


def check_archive(errors):
    if not ARCHIVE.exists():
        return
    log_text = ARCHIVE_LOG.read_text(encoding="utf-8") if ARCHIVE_LOG.exists() else ""
    if not log_text:
        errors.append("_archive/ exists but ARCHIVE-LOG.md is missing")
        return
    for f in sorted(ARCHIVE.rglob("*")):
        if f.is_dir() or f == ARCHIVE_LOG:
            continue
        if f.name.startswith("."):
            continue
        # a file is "covered" if its name or relative path appears in the ledger
        rel = f.relative_to(ROOT).as_posix()
        if f.name not in log_text and rel not in log_text:
            errors.append(f"archived file has no ARCHIVE-LOG entry: {rel}")


def check_memory(errors):
    if not MEMORY_DIR.exists():
        return
    if not MEMORY_INDEX.exists():
        errors.append("06-context/memory/ exists but MEMORY.md index is missing")
        return
    index_text = MEMORY_INDEX.read_text(encoding="utf-8")
    for f in sorted(MEMORY_DIR.glob("*.md")):
        if f.name in ("MEMORY.md", "_template.md"):
            continue
        stem = f.stem
        if stem not in index_text and f.name not in index_text:
            errors.append(f"memory not listed in MEMORY.md: 06-context/memory/{f.name}")


def check_knowledge(errors):
    if not KNOWLEDGE_DIR.exists():
        return
    if not KNOWLEDGE_INDEX.exists():
        errors.append("08-knowledge/ exists but _INDEX.md is missing")
        return
    index_text = KNOWLEDGE_INDEX.read_text(encoding="utf-8")
    for f in sorted(KNOWLEDGE_DIR.rglob("*.md")):
        if f.name in ("_INDEX.md", "_README.md") or f.name.startswith("."):
            continue
        rel_parts = f.relative_to(KNOWLEDGE_DIR).parts
        if "_archive" in rel_parts:
            continue
        if f.stem not in index_text and f.name not in index_text:
            errors.append(f"knowledge entry not listed in _INDEX.md: {f.relative_to(ROOT).as_posix()}")


def main():
    errors = []
    check_archive(errors)
    check_memory(errors)
    check_knowledge(errors)
    for e in errors:
        print(f"  ✗ {e}", file=sys.stderr)
    if errors:
        print(f"workspace integrity FAILED — {len(errors)} errors", file=sys.stderr)
        return 1
    print("✓ workspace integrity ok — archive provenance + memory index + knowledge index complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())
