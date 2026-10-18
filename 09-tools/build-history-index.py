#!/usr/bin/env python3
"""
build-history-index.py

Keeps each project's long-term tier linked ([[decision-memory-tiers]]). For every baton
(07-projects/<p>/SESSION-STATE.md, or a scoped one deeper in the project, such as
07-projects/<p>/docs/<thread>/SESSION-STATE.md) with a history/ folder beside it, it writes
history/README.md, the index: each month newest first, with its entries. It also makes sure
the links run both ways:

  - the baton points to history/README.md (once, in its history section);
  - each month file links back to the index and the baton.

Month files are written by the workspace app's batons.size fix or by hand; the index is
generated and never hand-edited. Idempotent: a second run changes nothing.

Usage:
    python3 09-tools/build-history-index.py
    python3 09-tools/build-history-index.py --check   # fail when anything would change
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent
PROJECTS = WORKSPACE / "07-projects"

# The baton's pointer, current and the one the first splits wrote (replaced in place).
POINTER = ("_Older entries are in [history/README.md](history/README.md), the long-term tier, "
           "by month; the app's Projects timeline joins them with this file._")
OLD_POINTERS = [
    "_Older entries are in [history/](history/), by month; the app's Projects timeline joins them with this file._",
]
# Neutral wording, the same the workspace app's batons.size fix writes, so neither rewrites the other.
NAV = "_[Index](README.md) · [The baton](../SESSION-STATE.md) · long-term tier_"
OLD_NAVS = ["_[Index](README.md) · [The baton](../SESSION-STATE.md) · long-term tier ([[decision-memory-tiers]])_"]
ENTRY = re.compile(r"^###\s+(\d{4}-\d{2}-\d{2})\b(.*)$")
MONTH = re.compile(r"^\d{4}-\d{2}\.md$")


def project_title(folder: Path) -> str:
    readme = folder / "README.md"
    if readme.is_file():
        text = readme.read_text(encoding="utf-8", errors="replace")
        m = re.search(r"^title:\s*(.+)$", text, re.MULTILINE)
        if m:
            return m.group(1).strip().strip('"')
        m = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
        if m:
            return m.group(1).strip()
    return folder.name


def entries(month_text: str) -> list[str]:
    """`date — title` for each `### date — …` entry, in file order."""
    out = []
    for line in month_text.splitlines():
        m = ENTRY.match(line)
        if m:
            rest = m.group(2).strip().lstrip("—–-:").strip()
            out.append(f"{m.group(1)} — {rest}" if rest else m.group(1))
    return out


def index_text(folder: Path, months: list[Path]) -> str:
    title = project_title(folder)
    lines = [
        f"# History — {title}",
        "",
        "_The long-term tier of [the baton](../SESSION-STATE.md): what it moved out once it passed "
        "12 KB. Generated; don't edit by hand. Newest month first._",
    ]
    for month in sorted(months, key=lambda p: p.stem, reverse=True):
        found = entries(month.read_text(encoding="utf-8", errors="replace"))
        lines += ["", f"## [{month.stem}]({month.name}) — {len(found)} {'entry' if len(found) == 1 else 'entries'}", ""]
        lines += [f"- {e}" for e in found] or ["- (no dated entries)"]
    return "\n".join(lines) + "\n"


def with_nav(text: str) -> str:
    """A month file with its back-links under the first heading (once)."""
    for old in OLD_NAVS:
        text = text.replace(old, NAV)
    if NAV in text:
        return text
    lines = text.split("\n")
    at = next((i for i, l in enumerate(lines) if l.startswith("# ")), -1)
    lines.insert(at + 1, "")
    lines.insert(at + 2, NAV)
    out = "\n".join(lines)
    return re.sub(r"\n{3,}", "\n\n", out)


def with_pointer(baton: str) -> str:
    """The baton's pointer to the index: the old wording replaced, or added under its history heading."""
    for old in OLD_POINTERS:
        baton = baton.replace(old, POINTER)
    if POINTER in baton:
        return baton
    m = re.search(r"^## .*[Hh]istory.*$", baton, re.MULTILINE)
    if m:
        return baton[: m.end()] + "\n\n" + POINTER + baton[m.end():]
    return baton.rstrip("\n") + "\n\n## History\n\n" + POINTER + "\n"


# Folders a baton search never enters: tool state, copies, dependencies and history itself.
SKIP = {".claude", ".git", "node_modules", "history", "_archive", ".smart-env"}


def baton_folders() -> list[Path]:
    """Every folder under 07-projects that holds a baton, project roots and scoped batons alike."""
    out = []
    for baton in PROJECTS.rglob("SESSION-STATE.md"):
        rel = baton.relative_to(PROJECTS).parts
        if not any(part in SKIP for part in rel[:-1]):
            out.append(baton.parent)
    return sorted(out)


def plan() -> dict[Path, str]:
    """Every file that would change, with its new text."""
    changes: dict[Path, str] = {}
    if not PROJECTS.is_dir():
        return changes
    for folder in baton_folders():
        hist = folder / "history"
        if not hist.is_dir():
            continue
        months = sorted(p for p in hist.iterdir() if p.is_file() and MONTH.match(p.name))
        if not months:
            continue
        for m in months:
            text = m.read_text(encoding="utf-8")
            new = with_nav(text)
            if new != text:
                changes[m] = new
        index = hist / "README.md"
        new_index = index_text(folder, months)
        if not index.is_file() or index.read_text(encoding="utf-8") != new_index:
            changes[index] = new_index
        baton = folder / "SESSION-STATE.md"
        if baton.is_file():
            text = baton.read_text(encoding="utf-8")
            new = with_pointer(text)
            if new != text:
                changes[baton] = new
    return changes


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--check", action="store_true", help="fail when anything would change")
    args = parser.parse_args()
    changes = plan()
    if args.check:
        if changes:
            for path in changes:
                print(f"stale: {path.relative_to(WORKSPACE)}", file=sys.stderr)
            print("run: python3 09-tools/build-history-index.py", file=sys.stderr)
            return 1
        print("history indexes: current")
        return 0
    for path, text in changes.items():
        path.write_text(text, encoding="utf-8")
        print(f"wrote {path.relative_to(WORKSPACE)}")
    if not changes:
        print("history indexes: current")
    return 0


if __name__ == "__main__":
    sys.exit(main())
