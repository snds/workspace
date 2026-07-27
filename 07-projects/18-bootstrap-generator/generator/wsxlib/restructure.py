"""`wsx restructure` — migrate a legacy FLAT workspace up to the numbered taxonomy.

This is the highest-risk operation the tool ships (it physically moves directories and
rewrites links), so it is defensive by construction:

  * **dry-run by DEFAULT** — you must pass `--apply` to write anything.
  * **full backup first** — the flat dirs + the config files that change are snapshotted
    to `_archive/pre-restructure-<stamp>/` before a single file moves; a `migration.json`
    records every move so `--rollback` can reverse it precisely.
  * **git-aware** — moves happen on disk and are then staged (`git add -A`), so git records
    them as renames and history follows.
  * **derived layer regenerated, not hand-patched** — after the move, the manifest is
    reindexed, missing new-core dirs are filled (`upgrade`), and every adapter/hook/index/
    registry is re-emitted, so they are correct by construction for the numbered layout.
  * **post-migration verify + health**, with an **automatic rollback** if verify fails.
  * **idempotent** — on an already-numbered workspace it is a no-op.

Only hand-authored markdown links and the two dotfiles (`.gitignore`, `.gitattributes`)
are rewritten in place; everything else is regenerated. Wikilinks resolve by basename, so
they survive the move untouched.
"""
from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

from . import adapters, core, health, layout, lifecycle, skills, upgrade

# Dirs never treated as vault content when rewriting link targets (they are generated
# tool output, and `.claude/skills/` must never be confused with the vault skills dir).
_PROTECTED_SEGMENTS = {".claude", ".cursor", ".wsx", ".obsidian", ".git", "adapters",
                       "_archive"}
# copytree noise we never need in a backup.
_BACKUP_IGNORE = shutil.ignore_patterns(".git", "node_modules", "dist", "build", "target",
                                        ".venv", "__pycache__")


def _planned_moves(root: Path) -> list:
    """(old_name, new_name) for every legacy flat dir that should become numbered.

    A move is planned only when the flat dir exists AND its numbered target does not — so a
    fresh numbered workspace yields no moves, and a hybrid (post-R1-upgrade) one moves only
    the still-flat pieces."""
    moves = []
    for key, flat in layout.LEGACY.items():
        if flat == layout.CANONICAL[key]:
            continue  # 'adapters' is the same name in both — never moved
        num = layout.CANONICAL[key]
        if (root / flat).is_dir() and not (root / num).exists():
            moves.append((flat, num))
    return moves


def _conflicts(root: Path) -> list:
    """Both the flat AND numbered form present — ambiguous; refuse rather than risk a clobber."""
    out = []
    for key, flat in layout.LEGACY.items():
        num = layout.CANONICAL[key]
        if flat != num and (root / flat).is_dir() and (root / num).is_dir():
            out.append((flat, num))
    return out


# --------------------------------------------------------------- link rewrite ---
_MDLINK = re.compile(r"(\]\()([^)]+)(\))")


def _remap_target(target: str, namemap: dict) -> str:
    """Rewrite a markdown link target's path segments old->new, protecting generated dirs."""
    if "://" in target or target.startswith(("#", "mailto:")):
        return target
    path, sep, frag = target.partition("#")
    segs = path.split("/")
    if any(s in _PROTECTED_SEGMENTS for s in segs):
        return target
    new = [namemap.get(s, s) for s in segs]
    return "/".join(new) + (sep + frag if sep else "")


def _rewrite_note_links(root: Path, namemap: dict) -> int:
    """Rewrite md-link targets across canonical vault notes + root. Wikilinks resolve by
    basename so they need no rewrite. Returns the number of files changed."""
    lay = layout.of(root)
    scan_dirs = [root] + [lay.dir(k) for k in
                          ("context", "skills", "frameworks", "projects", "knowledge",
                           "shared", "preferences", "tools")]
    seen, changed = set(), 0
    for base in scan_dirs:
        if not base.exists():
            continue
        md_iter = base.glob("*.md") if base == root else base.rglob("*.md")
        for p in md_iter:
            if p in seen or any(part.startswith(".") for part in p.relative_to(root).parts):
                continue
            seen.add(p)
            try:
                text = p.read_text(encoding="utf-8")
            except OSError:
                continue
            new = _MDLINK.sub(lambda m: m.group(1) + _remap_target(m.group(2), namemap)
                              + m.group(3), text)
            if new != text:
                p.write_text(new, encoding="utf-8")
                changed += 1
    return changed


def _rewrite_dotfiles(root: Path, namemap: dict) -> None:
    """Rewrite dir path segments in .gitignore / .gitattributes (simple, known formats)."""
    for fname in (".gitignore", ".gitattributes"):
        f = root / fname
        if not f.exists():
            continue
        text = f.read_text(encoding="utf-8")
        for old, new in namemap.items():
            text = re.sub(r"(?<![\w.\-/])" + re.escape(old) + r"/", new + "/", text)
        f.write_text(text, encoding="utf-8")


# -------------------------------------------------------------------- backup ---
def _backup_dir(root: Path, stamp: str) -> Path:
    return root / "_archive" / f"pre-restructure-{stamp}"


def _backup(root: Path, moves: list, stamp: str) -> Path:
    """Snapshot the flat dirs + changed config files so --rollback can fully restore."""
    bdir = _backup_dir(root, stamp)
    (bdir / "dirs").mkdir(parents=True, exist_ok=True)
    for old, _new in moves:
        shutil.copytree(root / old, bdir / "dirs" / old, ignore=_BACKUP_IGNORE)
    (bdir / "files").mkdir(parents=True, exist_ok=True)
    for fname in (".gitignore", ".gitattributes", "manifest.json", "HOME.md"):
        if (root / fname).exists():
            shutil.copy2(root / fname, bdir / "files" / fname)
    record = {"stamp": stamp, "moves": moves,
              "new_dirs_before": sorted(set(new for _o, new in moves)),
              "config_files": [f for f in (".gitignore", ".gitattributes", "manifest.json",
                                           "HOME.md") if (root / f).exists()]}
    (bdir / "migration.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    return bdir


# -------------------------------------------------------------------- rollback ---
def _latest_backup(root: Path) -> Path | None:
    adir = root / "_archive"
    if not adir.is_dir():
        return None
    cands = sorted(adir.glob("pre-restructure-*/migration.json"))
    return cands[-1].parent if cands else None


def _rollback_from(root: Path, bdir: Path) -> int:
    rec = json.loads((bdir / "migration.json").read_text(encoding="utf-8"))
    moves = rec.get("moves", [])
    print(f"wsx restructure --rollback — restoring pre-migration state from {bdir.name}\n")
    for old, new in moves:
        if (root / new).exists():
            shutil.rmtree(root / new)
        src = bdir / "dirs" / old
        if src.is_dir():
            shutil.copytree(src, root / old)
            print(f"  ~ restored {old}/ (removed {new}/)")
    for fname in rec.get("config_files", []):
        src = bdir / "files" / fname
        if src.exists():
            shutil.copy2(src, root / fname)
            print(f"  ~ restored {fname}")
    # Regenerate the (now flat) derived layer so adapters/indexes match again.
    prof, man = core.load_profile(root), core.load_manifest(root)
    skills.reindex(root)
    adapters.emit(root, "all", prof, core.load_manifest(root))
    if (root / ".git").exists():
        core.git(root, "add", "-A", check=False)
    print("\n  ✓ rolled back to the flat layout. Backup left in place; delete it when satisfied.")
    return 0


# ---------------------------------------------------------------------- main ---
def restructure(root: Path, apply: bool = False, rollback: bool = False) -> int:
    if rollback:
        bdir = _latest_backup(root)
        if not bdir:
            print("wsx restructure --rollback: no pre-restructure backup found under _archive/.")
            return 1
        return _rollback_from(root, bdir)

    conflicts = _conflicts(root)
    if conflicts:
        print("wsx restructure — REFUSED: both flat and numbered forms exist for:")
        for old, new in conflicts:
            print(f"    {old}/  AND  {new}/   — resolve by hand (merge one into the other) first.")
        return 1

    moves = _planned_moves(root)
    if not moves:
        print("wsx restructure — already on the numbered taxonomy (nothing to migrate). "
              "Run `wsx upgrade` to fill any missing new pieces.")
        return 0

    namemap = {old: new for old, new in moves}
    if not apply:
        print("wsx restructure — DRY RUN (nothing written). Pass --apply to migrate.\n")
        print("  Would move (git-aware, history preserved):")
        for old, new in moves:
            print(f"    {old}/  ->  {new}/")
        print("\n  Then: back up the flat dirs to _archive/pre-restructure-<stamp>/,")
        print("  rewrite hand-authored links + .gitignore/.gitattributes, reindex the manifest,")
        print("  fill any missing new-core dirs (02-shared-references, 04-preferences, memory),")
        print("  re-emit every adapter/hook/index/registry, then verify + health.")
        print("  A failed verify auto-rolls-back. Undo anytime with `wsx restructure --rollback`.")
        return 0

    stamp = core.now_stamp().replace(" ", "-").replace(":", "")
    print(f"wsx restructure — MIGRATING to the numbered taxonomy (backup stamp {stamp})\n")

    bdir = _backup(root, moves, stamp)
    print(f"  ✓ backed up flat dirs + config to {bdir.relative_to(root)}/")

    for old, new in moves:
        shutil.move(str(root / old), str(root / new))
        print(f"  ✓ moved {old}/ -> {new}/")

    skills.reindex(root)                          # manifest skill paths -> numbered
    nchanged = _rewrite_note_links(root, namemap)  # hand-authored md-link targets
    _rewrite_dotfiles(root, namemap)              # .gitignore / .gitattributes
    print(f"  ✓ rewired links in {nchanged} note(s) + the dotfiles; reindexed the manifest")

    # Fill new-core dirs the flat layout lacked + regenerate the derived layer.
    print("\n  — filling new-core scaffold + regenerating derived layer —")
    upgrade.upgrade(root)
    prof, man = core.load_profile(root), core.load_manifest(root)
    adapters.emit(root, "all", prof, core.load_manifest(root))
    if (root / ".git").exists():
        core.git(root, "add", "-A", check=False)

    print("\n  — post-migration checks —")
    vfails = lifecycle.verify(root)
    hproblems = health.health(root)
    if vfails:
        print("\n  ✗ verify FAILED after migration — auto-rolling back to the flat layout.")
        _rollback_from(root, bdir)
        print("\n  The migration was reverted. Nothing was lost; investigate the verify output above.")
        return 1

    print(f"\n✓ restructure complete — workspace is on the numbered taxonomy."
          f"{'  (health noted ' + str(hproblems) + ' issue(s) — advisory)' if hproblems else ''}")
    print(f"  Backup kept at {bdir.relative_to(root)}/ — delete it once you're satisfied, or "
          "`wsx restructure --rollback` to undo.")
    if (root / ".git").exists():
        print("  Changes are staged (git add -A); commit when ready: `wsx sync`.")
    return 0
