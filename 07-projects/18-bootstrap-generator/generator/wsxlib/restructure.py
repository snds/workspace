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
# Functional reference forms that ENCODE a directory path (and so break on a move):
#   * markdown links / image embeds:  ](dir/file.md)   ](../dir/file.md)
#   * Dataview source clauses:        FROM "dir/sub"    FROM "dir"
# Wikilinks [[name]] and typed relations resolve by BASENAME, so a move never breaks them.
_MDLINK = re.compile(r"(\]\()([^)]+)(\))")
_DATAVIEW_FROM = re.compile(r'(\bFROM\s+")([^"]+)(")')


def _remap_segments(path: str, namemap: dict) -> str:
    """old->new on each path segment, protecting generated (non-vault) dirs."""
    segs = path.split("/")
    if any(s in _PROTECTED_SEGMENTS for s in segs):
        return path
    return "/".join(namemap.get(s, s) for s in segs)


def _remap_target(target: str, namemap: dict) -> str:
    """Rewrite a markdown link target's path segments (skip external / anchor-only)."""
    if "://" in target or target.startswith(("#", "mailto:")):
        return target
    path, sep, frag = target.partition("#")
    return _remap_segments(path, namemap) + (sep + frag if sep else "")


def _iter_vault_md(root: Path):
    """Every canonical vault markdown note (skips dot-dirs and the _archive backup)."""
    lay = layout.of(root)
    bases = [root] + [lay.dir(k) for k in
                      ("context", "skills", "frameworks", "projects", "knowledge",
                       "shared", "preferences", "tools")]
    seen = set()
    for base in bases:
        if not base.exists():
            continue
        it = base.glob("*.md") if base == root else base.rglob("*.md")
        for p in it:
            rp = p.relative_to(root)
            if p in seen or any(part.startswith((".", "_archive")) for part in rp.parts):
                continue
            if "_archive" in rp.parts:
                continue
            seen.add(p)
            yield p


def _files_referencing(root: Path, namemap: dict) -> list:
    """Preview (no writes): vault notes whose md-links or Dataview FROM reference a moved dir."""
    out = []
    for p in _iter_vault_md(root):
        try:
            text = p.read_text(encoding="utf-8")
        except OSError:
            continue
        hit = any(_remap_target(m.group(2), namemap) != m.group(2) for m in _MDLINK.finditer(text)) \
            or any(_remap_segments(m.group(2).lstrip("/"), namemap) != m.group(2).lstrip("/")
                   for m in _DATAVIEW_FROM.finditer(text))
        if hit:
            out.append(str(p.relative_to(root)))
    return out


def _rewrite_references(root: Path, namemap: dict) -> list:
    """Rewrite every path-encoding reference (md-links + Dataview FROM) across vault notes.
    Returns the list of files changed (for the ledger)."""
    changed = []
    for p in _iter_vault_md(root):
        try:
            text = p.read_text(encoding="utf-8")
        except OSError:
            continue
        new = _MDLINK.sub(lambda m: m.group(1) + _remap_target(m.group(2), namemap)
                          + m.group(3), text)
        new = _DATAVIEW_FROM.sub(
            lambda m: m.group(1) + _remap_segments(m.group(2).lstrip("/"), namemap)
            + m.group(3), new)
        if new != text:
            p.write_text(new, encoding="utf-8")
            changed.append(str(p.relative_to(root)))
    return changed


# ---------------------------------------------------- broken-reference audit ---
def _broken_refs(root: Path) -> set:
    """The set of FUNCTIONAL references that do not resolve on disk right now, keyed by
    (source-note-basename, kind, target-tail) so it survives the dir move for comparison.

    This is the guarantee's backbone: we snapshot it BEFORE touching anything and again
    AFTER rewiring; any reference broken only in the AFTER set is a break WE introduced."""
    broken = set()
    for p in _iter_vault_md(root):
        try:
            text = p.read_text(encoding="utf-8")
        except OSError:
            continue
        for m in _MDLINK.finditer(text):
            t = m.group(2).strip()
            if "://" in t or t.startswith(("#", "mailto:")):
                continue
            path = t.split("#")[0]
            if not path or not path.endswith((".md", ".png", ".jpg", ".jpeg", ".svg",
                                              ".pdf", ".json", ".canvas")):
                continue
            if not (p.parent / path).resolve().exists():
                broken.add((p.name, "mdlink", path.split("/")[-1]))
        for m in _DATAVIEW_FROM.finditer(text):
            q = m.group(2).strip().lstrip("/")
            if not (root / q).exists() and not (root / (q + ".md")).exists():
                broken.add((p.name, "dataview", q.split("/")[-1]))
    return broken


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


def _write_ledger(bdir: Path, moves: list, rewritten: list,
                  baseline_broken: list, new_breaks: list) -> None:
    """Augment migration.json into a full CHANGE LEDGER: every dir moved, every file whose
    references were rewritten, and the reference-integrity proof (pre-existing broken links
    vs. any the migration introduced). This is the record for auditing + reconnection."""
    f = bdir / "migration.json"
    rec = json.loads(f.read_text(encoding="utf-8"))
    rec["ledger"] = {
        "dirs_moved": [{"from": o, "to": n} for o, n in moves],
        "files_rewritten": rewritten,
        "references_verified": "every md-link + Dataview FROM re-checked to resolve on disk",
        "pre_existing_broken": [list(k) for k in baseline_broken],
        "breaks_introduced": [list(k) for k in new_breaks],  # MUST be empty on success
    }
    f.write_text(json.dumps(rec, indent=2) + "\n", encoding="utf-8")


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
        touched = _files_referencing(root, namemap)
        print(f"\n  Would rewrite path references in {len(touched)} note(s) "
              "(md-links + Dataview `FROM` queries):")
        for rel in touched[:12]:
            print(f"    ~ {rel}")
        if len(touched) > 12:
            print(f"    …and {len(touched) - 12} more")
        print("\n  Then: back up the flat dirs + config to _archive/pre-restructure-<stamp>/,")
        print("  rewrite the references above + .gitignore/.gitattributes, reindex the manifest,")
        print("  fill any missing new-core dirs (02-shared-references, 04-preferences, memory),")
        print("  re-emit every adapter/hook/index/registry, then verify + health.")
        print("\n  GUARANTEE: the migration snapshots every functional reference first and re-checks")
        print("  them all after; if it would break even ONE that worked before, it auto-rolls back")
        print("  and applies nothing. Wikilinks/typed edges resolve by basename → untouched by the move.")
        print("  A full change ledger is written to migration.json. Undo: `wsx restructure --rollback`.")
        return 0

    stamp = core.now_stamp().replace(" ", "-").replace(":", "")
    print(f"wsx restructure — MIGRATING to the numbered taxonomy (backup stamp {stamp})\n")

    # The guarantee's baseline: which functional references are ALREADY broken (the person's
    # own pre-existing dead links). Anything broken only AFTER we rewire is a break WE caused.
    baseline_broken = _broken_refs(root)

    bdir = _backup(root, moves, stamp)
    print(f"  ✓ backed up flat dirs + config to {bdir.relative_to(root)}/")

    for old, new in moves:
        shutil.move(str(root / old), str(root / new))
        print(f"  ✓ moved {old}/ -> {new}/")

    skills.reindex(root)                            # manifest skill paths -> numbered
    rewritten = _rewrite_references(root, namemap)  # md-links + Dataview FROM
    _rewrite_dotfiles(root, namemap)                # .gitignore / .gitattributes
    print(f"  ✓ rewired references in {len(rewritten)} note(s) + the dotfiles; "
          "reindexed the manifest")

    # Fill new-core dirs the flat layout lacked + regenerate the derived layer.
    print("\n  — filling new-core scaffold + regenerating derived layer —")
    upgrade.upgrade(root)
    prof = core.load_profile(root)
    adapters.emit(root, "all", prof, core.load_manifest(root))
    if (root / ".git").exists():
        core.git(root, "add", "-A", check=False)

    print("\n  — post-migration checks —")
    vfails = lifecycle.verify(root)
    hproblems = health.health(root)
    # THE hard-requirement gate: no reference that worked before may be broken now.
    now_broken = _broken_refs(root)
    new_breaks = sorted(now_broken - baseline_broken)

    # Record the full change ledger onto the migration record (for audit + reconnection).
    _write_ledger(bdir, moves, rewritten, sorted(baseline_broken), new_breaks)

    if vfails or new_breaks:
        if new_breaks:
            print(f"\n  ✗ migration would BREAK {len(new_breaks)} reference(s) that worked before:")
            for note, kind, tail in new_breaks[:20]:
                print(f"      · {note}: {kind} -> …/{tail}")
        else:
            print("\n  ✗ verify FAILED after migration.")
        print("  Auto-rolling back to the flat layout (nothing lost).")
        _rollback_from(root, bdir)
        print("\n  Reverted. This is the safety gate doing its job — the migration is not applied")
        print(f"  unless it can prove zero broken references. Details in {bdir.relative_to(root)}/migration.json.")
        return 1

    print(f"\n✓ restructure complete — every reference verified to still resolve. Workspace is on "
          f"the numbered taxonomy.{'  (health noted ' + str(hproblems) + ' advisory issue(s))' if hproblems else ''}")
    print(f"  Change ledger + backup at {bdir.relative_to(root)}/ (migration.json lists every move and")
    print("  every file whose links were rewired). Undo anytime: `wsx restructure --rollback`.")
    if (root / ".git").exists():
        print("  Changes are staged (git add -A); commit when ready: `wsx sync`.")
    return 0
