#!/usr/bin/env python3
"""Copy Cursor-local canvases into git-tracked folders.

Cursor only compiles `.canvas.tsx` from
`~/.cursor/projects/<slug>/canvases/`. That path is machine-local.

Personal canvases copy into this vault (`07-projects/…/canvases/`) and are
mirrored into the owning checkout's Cursor slug so this window can open them.

Employer (`cpes-software` / `c8`) canvases never enter `snds/workspace`. They
copy into that repo's `canvases/` directory. Mixed-parent prefixes (`flavours-`,
`guided-setup-`) move out of the `~/Projects` Cursor slug into the prototype
repo (and that repo's live Cursor folder). Session-end runs this on Cursor.
Stdlib-only.

`--check` exits 1 on vault drift, a missing live mirror when that slug exists,
an unmapped named slug, employer-repo drift (when the checkout exists), or a
company canvas still sitting in a mixed personal slug. Legion / ephemeral /
missing employer checkout skips do not fail. Missing `~/.cursor/projects` is a
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
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CURSOR_PROJECTS = Path.home() / ".cursor" / "projects"
EMPLOYER_ORGS = ("cpes-software", "c8")

# First matching prefix wins. Unmatched files use PROJECT_DEFAULT.
FILE_PREFIX_ROUTES: tuple[tuple[str, str], ...] = (
    ("lcars-", "07-projects/20-lcars-generative-interface/canvases"),
    ("looney-", "07-projects/01-mediaservices/canvases"),
    ("duplicate-scan-", "07-projects/01-mediaservices/canvases"),
    ("authoritative-delete-", "07-projects/01-mediaservices/canvases"),
)

# Mixed `~/Projects` Cursor window: these are Centric product canvases.
# Dest is relative to the platform Projects directory, never this vault.
EMPLOYER_FILE_PREFIXES: tuple[tuple[str, str], ...] = (
    ("flavours-", "cpes-software/saas-plm-prototype/canvases"),
    ("guided-setup-", "cpes-software/saas-plm-prototype/canvases"),
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

# Vault dest → Cursor slugs that should compile these files.
VAULT_LIVE_MIRROR: dict[str, tuple[str, ...]] = {
    "07-projects/19-workspace-brain/canvases": (
        "Users-sean-sands-Projects-workspace",
        "Users-snds-Projects-Workspace",
    ),
    "07-projects/20-lcars-generative-interface/canvases": (
        "Users-sean-sands-Projects-lcars-generative-interface",
        "Users-snds-Projects-lcars-generative-interface",
    ),
    "07-projects/01-mediaservices/canvases": (
        "Users-sean-sands-Projects-MediaSentinel",
        "Users-snds-Projects-MediaSentinel",
    ),
}


def projects_root() -> Path:
    for name in ("Projects", "projects"):
        path = Path.home() / name
        if path.is_dir():
            return path
    return Path.home() / "Projects"


def is_under(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def is_employer_slug(slug: str) -> bool:
    low = slug.lower()
    return "cpes-software" in low or "centric-ui" in low or "-c8-" in f"-{low}-" or low.endswith("-c8")


def is_ephemeral_slug(slug: str) -> bool:
    return slug.isdigit() or slug.startswith("var-folders-") or slug == "empty-window"


def is_workspace_default_slug(slug: str) -> bool:
    dest = PROJECT_DEFAULT.get(slug)
    return bool(dest and dest.endswith("19-workspace-brain/canvases"))


def employer_prefix_dest(name: str) -> str | None:
    for prefix, dest in EMPLOYER_FILE_PREFIXES:
        if name.startswith(prefix):
            return dest
    return None


def slug_after_projects(slug: str) -> str | None:
    low = slug.lower()
    key = "-projects-"
    i = low.find(key)
    if i < 0:
        return None
    return low[i + len(key) :]


def match_employer_repo(slug: str, projects: Path) -> Path | None:
    """Longest existing org/child under `projects` whose hyphen form prefixes the slug tail."""
    tail = slug_after_projects(slug)
    if not tail:
        return None
    candidates: list[tuple[int, Path]] = []
    for org in EMPLOYER_ORGS:
        org_dir = projects / org
        if not org_dir.is_dir():
            continue
        for child in org_dir.iterdir():
            if not child.is_dir() or child.name.startswith("."):
                continue
            frag = f"{org}-{child.name}".lower()
            if tail == frag or tail.startswith(f"{frag}-"):
                candidates.append((len(frag), child / "canvases"))
    if not candidates:
        return None
    candidates.sort(key=lambda item: item[0], reverse=True)
    dest = candidates[0][1]
    if is_under(dest, ROOT):
        raise RuntimeError(f"employer dest resolved inside workspace: {dest}")
    if not any(is_under(dest, projects / org) for org in EMPLOYER_ORGS):
        return None
    return dest


def employer_dest_dir(slug: str, name: str, projects: Path | None = None) -> Path | None:
    projects = projects if projects is not None else projects_root()
    prefix = employer_prefix_dest(name)
    if prefix:
        dest = projects / prefix
        if is_under(dest, ROOT):
            raise RuntimeError(f"employer dest resolved inside workspace: {dest}")
        return dest
    if is_employer_slug(slug):
        return match_employer_repo(slug, projects)
    return None


def companions(src: Path) -> list[Path]:
    files = [src]
    if src.name.endswith(".canvas.tsx"):
        data = src.with_name(src.name[: -len(".canvas.tsx")] + ".canvas.data.json")
        if data.is_file():
            files.append(data)
    return files


def route(slug: str, name: str) -> Path | None:
    """Vault dest dir, or None when this file must not enter snds/workspace."""
    if employer_prefix_dest(name) or is_employer_slug(slug):
        return None
    for prefix, dest in FILE_PREFIX_ROUTES:
        if name.startswith(prefix):
            return ROOT / dest
    dest = PROJECT_DEFAULT.get(slug)
    if dest is None:
        return None
    return ROOT / dest


def classify(slug: str, name: str) -> str:
    """copy | employer | skip-project | skip-ephemeral | unmapped."""
    if employer_prefix_dest(name) or is_employer_slug(slug):
        return "employer"
    if is_ephemeral_slug(slug) and slug not in PROJECT_DEFAULT:
        return "skip-ephemeral"
    for prefix, _dest in FILE_PREFIX_ROUTES:
        if name.startswith(prefix):
            return "copy"
    if slug in PROJECT_DEFAULT:
        return "copy" if PROJECT_DEFAULT[slug] else "skip-project"
    return "unmapped"


def live_mirror_targets(vault_file: Path) -> list[Path]:
    """Cursor compile paths that should match this vault canvas."""
    try:
        rel = vault_file.parent.relative_to(ROOT).as_posix()
    except ValueError:
        return []
    out: list[Path] = []
    for slug in VAULT_LIVE_MIRROR.get(rel, ()):
        proj = CURSOR_PROJECTS / slug
        if not proj.is_dir():
            continue
        dest = proj / "canvases" / vault_file.name
        if dest.resolve() == vault_file.resolve():
            continue
        out.append(dest)
    return out


def employer_live_targets(dest_dir: Path, src: Path) -> list[Path]:
    """Compile path on the owning employer Cursor slug (exact repo match, not worktrees)."""
    try:
        repo = dest_dir.parent.relative_to(projects_root()).as_posix()
    except ValueError:
        return []
    frag = repo.replace("/", "-").lower()
    out: list[Path] = []
    if not CURSOR_PROJECTS.is_dir():
        return []
    for proj in CURSOR_PROJECTS.iterdir():
        tail = slug_after_projects(proj.name)
        if tail != frag:
            continue
        live = proj / "canvases" / src.name
        if live.resolve() == src.resolve():
            continue
        out.append(live)
    return out


def iter_vault_canvases() -> list[Path]:
    dirs = {d for d in PROJECT_DEFAULT.values() if d} | {d for _p, d in FILE_PREFIX_ROUTES}
    files: list[Path] = []
    for dest in sorted(dirs):
        d = ROOT / dest
        if d.is_dir():
            files.extend(sorted(d.glob("*.canvas.tsx")))
    return files


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


def display_dest(dest: Path) -> str:
    try:
        return dest.relative_to(ROOT).as_posix()
    except ValueError:
        try:
            return dest.relative_to(projects_root()).as_posix()
        except ValueError:
            return str(dest)


def copy_if_stale(src: Path, dest: Path, check: bool) -> bool:
    """Copy src → dest. Return True if dest was missing or differed."""
    if dest.is_file() and filecmp.cmp(src, dest, shallow=False):
        return False
    if check:
        return True
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)
    return True


def sync(check: bool) -> int:
    vault_planned: list[tuple[Path, Path, str]] = []
    employer_planned: list[tuple[Path, Path, str]] = []
    skipped: list[tuple[str, str, str]] = []
    unmapped: list[tuple[str, str]] = []
    stray_mixed: list[tuple[str, str]] = []

    for src, slug, name in iter_live():
        kind = classify(slug, name)
        if kind == "copy":
            dest_dir = route(slug, name)
            if dest_dir is None:
                skipped.append((kind, slug, name))
                continue
            vault_planned.append((src, dest_dir / name, slug))
        elif kind == "employer":
            dest_dir = employer_dest_dir(slug, name)
            repo = dest_dir.parent if dest_dir is not None else None
            if dest_dir is None or repo is None or not repo.is_dir():
                skipped.append(("skip-employer-missing", slug, name))
                continue
            if is_under(dest_dir, ROOT):
                raise RuntimeError(f"employer dest inside workspace: {dest_dir}")
            employer_planned.append((src, dest_dir / name, slug))
            if is_workspace_default_slug(slug):
                stray_mixed.append((slug, name))
        elif kind == "unmapped":
            unmapped.append((slug, name))
        else:
            skipped.append((kind, slug, name))

    copied, stale = 0, []
    for src, dest, slug in vault_planned:
        if is_under(dest, ROOT) is False:
            raise RuntimeError(f"vault dest escaped workspace: {dest}")
        for piece in companions(src):
            piece_dest = dest.with_name(piece.name)
            if copy_if_stale(piece, piece_dest, check):
                stale.append((slug, piece.name, display_dest(piece_dest)))
                if not check:
                    copied += 1

    employer_copied, employer_stale = 0, []
    moved = 0
    for src, dest, slug in employer_planned:
        if is_under(dest, ROOT):
            raise RuntimeError(f"employer dest inside workspace: {dest}")
        for piece in companions(src):
            piece_dest = dest.with_name(piece.name)
            if copy_if_stale(piece, piece_dest, check):
                employer_stale.append((slug, piece.name, display_dest(piece_dest)))
                if not check:
                    employer_copied += 1
            for live in employer_live_targets(dest.parent, piece):
                if copy_if_stale(piece, live, check):
                    employer_stale.append((slug, piece.name, str(live)))
                    if not check:
                        employer_copied += 1
        if (
            not check
            and is_workspace_default_slug(slug)
            and dest.is_file()
            and filecmp.cmp(src, dest, shallow=False)
        ):
            for piece in companions(src):
                piece.unlink(missing_ok=True)
            moved += 1

    mirrored, live_stale = 0, []
    for vault_file in iter_vault_canvases():
        for live in live_mirror_targets(vault_file):
            if live.is_file() and filecmp.cmp(vault_file, live, shallow=False):
                continue
            rel = vault_file.relative_to(ROOT).as_posix()
            live_stale.append((rel, str(live)))
            if check:
                continue
            live.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(vault_file, live)
            mirrored += 1

    def report() -> None:
        for slug, name, dest in stale:
            print(f"drift: {slug}/{name} → {dest}")
        for slug, name, dest in employer_stale:
            print(f"employer-drift: {slug}/{name} → {dest}")
        for vault_rel, live in live_stale:
            print(f"live-miss: {vault_rel} → {live}")
        for slug, name in stray_mixed:
            print(f"stray-mixed: {slug}/{name}")
        for kind, slug, name in skipped:
            print(f"skip ({kind}): {slug}/{name}")
        for slug, name in unmapped:
            print(f"unmapped: {slug}/{name}")

    if check:
        report()
        if stale:
            print(f"cursor-externalize: {len(stale)} canvas(es) not in vault")
            return 1
        if employer_stale:
            print(f"cursor-externalize: {len(employer_stale)} employer canvas(es) not in repo canvases/")
            return 1
        if live_stale:
            print(f"cursor-externalize: {len(live_stale)} canvas(es) not in this checkout's live canvases/")
            return 1
        if stray_mixed:
            print(f"cursor-externalize: {len(stray_mixed)} company canvas(es) still in a mixed personal slug")
            return 1
        if unmapped:
            print(f"cursor-externalize: {len(unmapped)} unmapped canvas(es) — add a slug or skip")
            return 1
        print("cursor-externalize: vault copies match Cursor live files")
        if skipped:
            print(f"  ({len(skipped)} skipped)")
        return 0

    report()
    print(
        f"cursor-externalize: copied {copied} to vault, "
        f"copied {employer_copied} to employer canvases/, "
        f"moved {moved} off mixed personal slugs, "
        f"mirrored {mirrored} into live canvases/, "
        f"vault already current {max(0, len(vault_planned) - copied)}"
    )
    if unmapped:
        print(f"cursor-externalize: {len(unmapped)} unmapped canvas(es) — add a slug or skip")
        return 1
    return 0


def self_test() -> int:
    cases = [
        ("Users-sean-sands-Projects-workspace", "foo.canvas.tsx", "copy"),
        ("Users-sean-sands-projects", "agent-load-miss-review.canvas.tsx", "copy"),
        ("Users-sean-sands-projects", "flavours-claims-concepts.canvas.tsx", "employer"),
        ("Users-sean-sands-projects", "guided-setup-concepts.canvas.tsx", "employer"),
        ("Users-sean-sands-Projects-cpes-software-cds", "enterprise-charting-pm-brief.canvas.tsx", "employer"),
        ("Users-sean-sands-Projects-cpes-software-saas-plm-prototype", "workflow-diagramming-patterns.canvas.tsx", "employer"),
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
        vault = route(slug, name)
        if expect == "copy" and vault is None:
            print(f"FAIL route({slug}, {name}) is None, want a dest")
            errors += 1
        if expect != "copy" and vault is not None:
            print(f"FAIL route({slug}, {name}) should be None")
            errors += 1
        if expect == "copy" and vault is not None and not is_under(vault, ROOT):
            print(f"FAIL vault dest escaped ROOT: {vault}")
            errors += 1
        if expect == "employer" and vault is not None:
            print(f"FAIL employer file routed into vault: {vault}")
            errors += 1

    tmp = Path(tempfile.mkdtemp(prefix="cursor-ext-"))
    try:
        (tmp / "cpes-software" / "cds").mkdir(parents=True)
        (tmp / "cpes-software" / "cds-field").mkdir(parents=True)
        (tmp / "cpes-software" / "saas-plm-prototype").mkdir(parents=True)
        (tmp / "cpes-software" / "centric-ui").mkdir(parents=True)
        match_cases = [
            ("Users-sean-sands-Projects-cpes-software-cds", tmp / "cpes-software" / "cds" / "canvases"),
            ("Users-sean-sands-Projects-cpes-software-cds-field", tmp / "cpes-software" / "cds-field" / "canvases"),
            (
                "Users-sean-sands-Projects-cpes-software-saas-plm-prototype-pr49",
                tmp / "cpes-software" / "saas-plm-prototype" / "canvases",
            ),
            (
                "Users-sean-sands-Projects-cpes-software-centric-ui",
                tmp / "cpes-software" / "centric-ui" / "canvases",
            ),
        ]
        for slug, want in match_cases:
            got = match_employer_repo(slug, tmp)
            if got != want:
                print(f"FAIL match_employer_repo({slug}) = {got}, want {want}")
                errors += 1
            if got is not None and is_under(got, ROOT):
                print(f"FAIL employer match inside workspace: {got}")
                errors += 1
        prefix = employer_dest_dir(
            "Users-sean-sands-projects",
            "flavours-claims-concepts.canvas.tsx",
            tmp,
        )
        want_prefix = tmp / "cpes-software" / "saas-plm-prototype" / "canvases"
        if prefix != want_prefix:
            print(f"FAIL flavours dest = {prefix}, want {want_prefix}")
            errors += 1
        if prefix is not None and is_under(prefix, ROOT):
            print(f"FAIL flavours dest inside workspace: {prefix}")
            errors += 1
        if match_employer_repo("Users-sean-sands-Projects-workspace", tmp) is not None:
            print("FAIL workspace slug matched an employer repo")
            errors += 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

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
