#!/usr/bin/env python3
"""Copy Cursor-local canvases into git-tracked vault folders.

Cursor only compiles `.canvas.tsx` from
`~/.cursor/projects/<slug>/canvases/`. That path is machine-local and is not
the workspace git tree. This tool copies the source files into the vault so
durable canvas content travels with `snds/workspace`.

Live Cursor files stay where they are (the IDE will not see vault copies).
Session-end runs this on Cursor. Stdlib-only.

`--check` exits 1 on vault drift **or** an unmapped named project slug.
Explicit skips (employer, Legion, ephemeral Cursor windows, file-prefix
denylist) are reported and do not fail. Missing `~/.cursor/projects` is a
clean pass (CI cannot see that folder — A10).

Usage:
  python3 09-tools/cursor-externalize.py           # copy if dest missing or differs
  python3 09-tools/cursor-externalize.py --check   # report only; exit 1 if drift/unmapped
  python3 09-tools/cursor-externalize.py --self-test
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

# Never copy these into snds/workspace even when the slug maps to workspace-brain
# (parent `~/Projects` folder mixed personal + Centric canvases).
SKIP_FILE_PREFIXES: tuple[str, ...] = (
    "flavours-",
    "guided-setup-",
)

# Cursor project folder name → vault dest. None = skip (belongs in that repo).
# Include both Personal-MBP (`snds`) and Work-MBP (`sean-sands`) slugs.
PROJECT_DEFAULT: dict[str, str | None] = {
    "Users-snds-Projects-Workspace": "07-projects/19-workspace-brain/canvases",
    "Users-snds-Projects": "07-projects/19-workspace-brain/canvases",
    "Users-sean-sands-Projects-workspace": "07-projects/19-workspace-brain/canvases",
    "Users-sean-sands-projects": "07-projects/19-workspace-brain/canvases",
    "Users-snds-Projects-MediaSentinel": "07-projects/01-mediaservices/canvases",
    "Users-sean-sands-Projects-MediaSentinel": "07-projects/01-mediaservices/canvases",
    "Users-snds-Projects-lcars-generative-interface": "07-projects/20-lcars-generative-interface/canvases",
    "Users-sean-sands-Projects-lcars-generative-interface": "07-projects/20-lcars-generative-interface/canvases",
    "Users-snds-Projects-Legion": None,
    "Users-sean-sands-Projects-Legion": None,
}


def is_employer_slug(slug: str) -> bool:
    low = slug.lower()
    return "cpes-software" in low or "centric-ui" in low


def is_ephemeral_slug(slug: str) -> bool:
    return slug.isdigit() or slug.startswith("var-folders-") or slug == "empty-window"


def route(slug: str, name: str) -> Path | None:
    """Vault dest dir, or None when this file must not enter snds/workspace."""
    for prefix in SKIP_FILE_PREFIXES:
        if name.startswith(prefix):
            return None
    if is_employer_slug(slug):
        return None
    for prefix, dest in FILE_PREFIX_ROUTES:
        if name.startswith(prefix):
            return ROOT / dest
    dest = PROJECT_DEFAULT.get(slug)
    if dest is None:
        return None
    return ROOT / dest


def classify(slug: str, name: str) -> str:
    """copy | skip-file | skip-employer | skip-project | skip-ephemeral | unmapped."""
    for prefix in SKIP_FILE_PREFIXES:
        if name.startswith(prefix):
            return "skip-file"
    if is_employer_slug(slug):
        return "skip-employer"
    if is_ephemeral_slug(slug) and slug not in PROJECT_DEFAULT:
        return "skip-ephemeral"
    for prefix, _dest in FILE_PREFIX_ROUTES:
        if name.startswith(prefix):
            return "copy"
    if slug in PROJECT_DEFAULT:
        return "copy" if PROJECT_DEFAULT[slug] else "skip-project"
    return "unmapped"


def iter_live() -> list[tuple[Path, str, str]]:
    """Return (src, slug, name) for every live `.canvas.tsx`."""
    if not CURSOR_PROJECTS.is_dir():
        return []
    out: list[tuple[Path, str, str]] = []
    for proj in sorted(CURSOR_PROJECTS.iterdir()):
        canvases = proj / "canvases"
        if not canvases.is_dir():
            continue
        slug = proj.name
        for src in sorted(canvases.glob("*.canvas.tsx")):
            out.append((src, slug, src.name))
    return out


def sync(check: bool) -> int:
    planned: list[tuple[Path, Path, str]] = []
    skipped: list[tuple[str, str, str]] = []
    unmapped: list[tuple[str, str]] = []
    for src, slug, name in iter_live():
        kind = classify(slug, name)
        if kind == "copy":
            dest_dir = route(slug, name)
            if dest_dir is None:
                skipped.append((kind, slug, name))
                continue
            planned.append((src, dest_dir / name, slug))
        elif kind == "unmapped":
            unmapped.append((slug, name))
        else:
            skipped.append((kind, slug, name))

    copied, stale = 0, []
    for src, dest, slug in planned:
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.is_file() and filecmp.cmp(src, dest, shallow=False):
            continue
        stale.append((slug, src.name, dest.relative_to(ROOT).as_posix()))
        if check:
            continue
        shutil.copy2(src, dest)
        copied += 1

    def report() -> None:
        for slug, name, dest in stale:
            print(f"drift: {slug}/{name} → {dest}")
        for kind, slug, name in skipped:
            print(f"skip ({kind}): {slug}/{name}")
        for slug, name in unmapped:
            print(f"unmapped: {slug}/{name}")

    if check:
        report()
        if stale:
            print(f"cursor-externalize: {len(stale)} canvas(es) not in vault")
            return 1
        if unmapped:
            print(f"cursor-externalize: {len(unmapped)} unmapped canvas(es) — add a slug or skip")
            return 1
        print("cursor-externalize: vault copies match Cursor live files")
        if skipped:
            print(f"  ({len(skipped)} skipped)")
        return 0

    report()
    print(f"cursor-externalize: copied {copied}, already current {len(planned) - copied}")
    if unmapped:
        print(f"cursor-externalize: {len(unmapped)} unmapped canvas(es) — add a slug or skip")
        return 1
    return 0


def self_test() -> int:
    cases = [
        ("Users-sean-sands-Projects-workspace", "foo.canvas.tsx", "copy"),
        ("Users-sean-sands-projects", "agent-load-miss-review.canvas.tsx", "copy"),
        ("Users-sean-sands-projects", "flavours-claims-concepts.canvas.tsx", "skip-file"),
        ("Users-sean-sands-projects", "guided-setup-concepts.canvas.tsx", "skip-file"),
        ("Users-sean-sands-Projects-cpes-software-cds", "enterprise-charting-pm-brief.canvas.tsx", "skip-employer"),
        ("Users-sean-sands-Projects-Legion", "x.canvas.tsx", "skip-project"),
        ("1778171112680", "tmp.canvas.tsx", "skip-ephemeral"),
        ("Users-unknown-Named-Repo", "x.canvas.tsx", "unmapped"),
        ("Users-snds-Projects-Workspace", "lcars-replication-gap.canvas.tsx", "copy"),
    ]
    errors = 0
    for slug, name, expect in cases:
        got = classify(slug, name)
        if got != expect:
            print(f"FAIL classify({slug}, {name}) = {got}, want {expect}")
            errors += 1
        if expect == "copy" and route(slug, name) is None:
            print(f"FAIL route({slug}, {name}) is None, want a dest")
            errors += 1
        if expect != "copy" and route(slug, name) is not None:
            print(f"FAIL route({slug}, {name}) should be None")
            errors += 1
    if errors:
        print(f"cursor-externalize --self-test: {errors} error(s)")
        return 1
    print("cursor-externalize --self-test: ok")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true", help="report drift/unmapped; exit 1 if copies are missing, differ, or unmapped")
    ap.add_argument("--self-test", action="store_true", help="route/classify fixtures; no disk writes")
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    return sync(check=args.check)


if __name__ == "__main__":
    sys.exit(main())
