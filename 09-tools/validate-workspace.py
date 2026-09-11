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
  4. TOOL ADAPTERS      — native-filename pointers at AGENTS.md exist, mention close-out, and
     stay short (added 2026-09-11 so Gemini/Copilot/Warp/Aider/Windsurf/web packs cannot drift
     into a second contract).                                                                [error]

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

ADAPTER_MD = [
    "GEMINI.md",
    "WARP.md",
    "CONVENTIONS.md",
    "PERPLEXITY.md",
    ".github/copilot-instructions.md",
    ".windsurf/rules/workspace.md",
    "00-bootstrap/adapters/web-session.md",
]
ADAPTER_CONFIG = [
    ".gemini/settings.json",
    ".aider.conf.yml",
]
MAX_ADAPTER_LINES = 40
MAX_WEB_SESSION_LINES = 80


def check_archive(errors, archive=None, archive_log=None, root=None):
    archive = ARCHIVE if archive is None else archive
    archive_log = ARCHIVE_LOG if archive_log is None else archive_log
    root = ROOT if root is None else root
    if not archive.exists():
        return
    log_text = archive_log.read_text(encoding="utf-8") if archive_log.exists() else ""
    if not log_text:
        errors.append("_archive/ exists but ARCHIVE-LOG.md is missing")
        return
    for f in sorted(archive.rglob("*")):
        if f.is_dir() or f == archive_log:
            continue
        if f.name.startswith("."):
            continue
        # a file is "covered" if its name or relative path appears in the ledger
        rel = f.relative_to(root).as_posix()
        if f.name not in log_text and rel not in log_text:
            errors.append(f"archived file has no ARCHIVE-LOG entry: {rel}")


def check_memory(errors, memory_dir=None, memory_index=None):
    memory_dir = MEMORY_DIR if memory_dir is None else memory_dir
    memory_index = MEMORY_INDEX if memory_index is None else memory_index
    if not memory_dir.exists():
        return
    if not memory_index.exists():
        errors.append("06-context/memory/ exists but MEMORY.md index is missing")
        return
    index_text = memory_index.read_text(encoding="utf-8")
    for f in sorted(memory_dir.glob("*.md")):
        if f.name in ("MEMORY.md", "_template.md"):
            continue
        stem = f.stem
        if stem not in index_text and f.name not in index_text:
            errors.append(f"memory not listed in MEMORY.md: 06-context/memory/{f.name}")


def check_knowledge(errors, knowledge_dir=None, knowledge_index=None, root=None):
    knowledge_dir = KNOWLEDGE_DIR if knowledge_dir is None else knowledge_dir
    knowledge_index = KNOWLEDGE_INDEX if knowledge_index is None else knowledge_index
    root = ROOT if root is None else root
    if not knowledge_dir.exists():
        return
    if not knowledge_index.exists():
        errors.append("08-knowledge/ exists but _INDEX.md is missing")
        return
    index_text = knowledge_index.read_text(encoding="utf-8")
    for f in sorted(knowledge_dir.rglob("*.md")):
        if f.name in ("_INDEX.md", "_README.md") or f.name.startswith("."):
            continue
        rel_parts = f.relative_to(knowledge_dir).parts
        if "_archive" in rel_parts:
            continue
        if f.stem not in index_text and f.name not in index_text:
            errors.append(f"knowledge entry not listed in _INDEX.md: {f.relative_to(root).as_posix()}")


def check_adapters(errors, root=None, files=None, configs=None):
    """Native-filename adapters must exist, point at AGENTS.md, and stay thin."""
    root = ROOT if root is None else root
    files = ADAPTER_MD if files is None else files
    configs = ADAPTER_CONFIG if configs is None else configs
    for rel in files:
        path = root / rel
        if not path.is_file():
            errors.append(f"missing tool adapter: {rel}")
            continue
        text = path.read_text(encoding="utf-8")
        if "AGENTS.md" not in text:
            errors.append(f"adapter {rel} must mention AGENTS.md")
        if "close-out" not in text:
            errors.append(f"adapter {rel} must mention close-out")
        cap = MAX_WEB_SESSION_LINES if rel.endswith("web-session.md") else MAX_ADAPTER_LINES
        n = len(text.splitlines())
        if n > cap:
            errors.append(f"adapter {rel} is {n} lines (cap {cap}); keep it a pointer")
    for rel in configs:
        path = root / rel
        if not path.is_file():
            errors.append(f"missing tool adapter config: {rel}")
            continue
        if "AGENTS.md" not in path.read_text(encoding="utf-8"):
            errors.append(f"adapter config {rel} must name AGENTS.md")


def main():
    errors = []
    check_archive(errors)
    check_memory(errors)
    check_knowledge(errors)
    check_adapters(errors)
    for e in errors:
        print(f"  ✗ {e}", file=sys.stderr)
    if errors:
        print(f"workspace integrity FAILED — {len(errors)} errors", file=sys.stderr)
        return 1
    print("✓ workspace integrity ok — archive provenance + memory index + knowledge index + adapters complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())
