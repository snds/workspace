#!/usr/bin/env python3
"""Copy Cursor-local canvases into git-tracked vault folders.

Cursor only compiles `.canvas.tsx` from
`~/.cursor/projects/<slug>/canvases/`. That path is machine-local and is not
the workspace git tree. This tool copies the source files into the vault so
durable canvas content travels with `snds/workspace`.

Live Cursor files stay where they are (the IDE will not see vault copies).
Session-end runs this on Cursor. Stdlib-only.

Usage:
  python3 09-tools/cursor-externalize.py           # copy if dest missing or differs
  python3 09-tools/cursor-externalize.py --check   # report only; exit 1 if drift
"""
from __future__ import annotations

import argparse
import filecmp
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CURSOR_PROJECTS = Path.home() / ".cursor" / "projects"

# First matching prefix wins. Unmatched files use PROJECT_DEFAULT.
FILE_PREFIX_ROUTES: tuple[tuple[str, str], ...] = (
    ("lcars-", "07-projects/20-lcars-generative-interface/canvases"),
    ("looney-", "07-projects/01-mediaservices/canvases"),
    ("duplicate-scan-", "07-projects/01-mediaservices/canvases"),
    ("authoritative-delete-", "07-projects/01-mediaservices/canvases"),
)

# Cursor project folder name → vault dest. None = skip (belongs in that repo).
PROJECT_DEFAULT: dict[str, str | None] = {
    "Users-snds-Projects-Workspace": "07-projects/19-workspace-brain/canvases",
    "Users-snds-Projects": "07-projects/19-workspace-brain/canvases",
    "Users-snds-Projects-MediaSentinel": "07-projects/01-mediaservices/canvases",
    "Users-snds-Projects-lcars-generative-interface": "07-projects/20-lcars-generative-interface/canvases",
    "Users-snds-Projects-Legion": None,
}


def route(slug: str, name: str) -> Path | None:
    for prefix, dest in FILE_PREFIX_ROUTES:
        if name.startswith(prefix):
            return ROOT / dest
    dest = PROJECT_DEFAULT.get(slug)
    if dest is None:
        return None
    return ROOT / dest


def iter_sources() -> list[tuple[Path, Path, str]]:
    """Return (src, dest_file, slug) for every live canvas that maps into the vault."""
    if not CURSOR_PROJECTS.is_dir():
        return []
    out: list[tuple[Path, Path, str]] = []
    for proj in sorted(CURSOR_PROJECTS.iterdir()):
        canvases = proj / "canvases"
        if not canvases.is_dir():
            continue
        slug = proj.name
        for src in sorted(canvases.glob("*.canvas.tsx")):
            dest_dir = route(slug, src.name)
            if dest_dir is None:
                continue
            out.append((src, dest_dir / src.name, slug))
    return out


def skipped_legion() -> list[Path]:
    d = CURSOR_PROJECTS / "Users-snds-Projects-Legion" / "canvases"
    if not d.is_dir():
        return []
    return sorted(d.glob("*.canvas.tsx"))


def sync(check: bool) -> int:
    planned = iter_sources()
    copied, stale, skipped = 0, [], []
    for src, dest, slug in planned:
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.is_file() and filecmp.cmp(src, dest, shallow=False):
            continue
        stale.append((slug, src.name, dest.relative_to(ROOT).as_posix()))
        if check:
            continue
        shutil.copy2(src, dest)
        copied += 1

    for p in skipped_legion():
        skipped.append(p.name)

    if check:
        for slug, name, dest in stale:
            print(f"drift: {slug}/{name} → {dest}")
        if skipped:
            print("skip (Legion repo, not this vault): " + ", ".join(skipped))
        if stale:
            print(f"cursor-externalize: {len(stale)} canvas(es) not in vault")
            return 1
        print("cursor-externalize: vault copies match Cursor live files")
        if skipped:
            print(f"  ({len(skipped)} Legion canvas(es) left in Cursor local)")
        return 0

    for slug, name, dest in stale:
        print(f"copied: {slug}/{name} → {dest}")
    if skipped:
        print("skip (belongs in Legion git, not snds/workspace): " + ", ".join(skipped))
    print(f"cursor-externalize: copied {copied}, already current {len(planned) - copied}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true", help="report drift; exit 1 if copies are missing or differ")
    args = ap.parse_args()
    return sync(check=args.check)


if __name__ == "__main__":
    sys.exit(main())
