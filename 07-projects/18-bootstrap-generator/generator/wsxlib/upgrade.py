"""`wsx upgrade` — a corrective pass over an ALREADY-generated workspace.

People generated workspaces before newer scaffold pieces existed (a `projects/`
tree, the connective MOC/index layer, `frameworks/skill-authoring.md`, the
multi-device `.gitattributes`/session-fragment setup). This brings an existing
workspace up to the current shape — **non-destructively**:

  * MISSING scaffold files are created (projects/README.md, sessions/README.md, …).
  * The GENERATED MOC layer (HOME.md, skills/_INDEX.md, projects/_INDEX.md) is
    always regenerated — this is what reconnects a previously-islanded graph.
  * Hand-editable files that already exist are left EXACTLY as they are (never
    clobbered). Your prose, skills, and edits are safe.

Applies immediately (the user's chosen default); pass `--dry-run` to preview the
plan without writing anything.
"""
from __future__ import annotations

from pathlib import Path

from . import core, moc, scaffold

# Generated files that upgrade always (re)writes — safe because they are derived
# from disk, never hand-authored.
_REGENERATED = ["HOME.md", "skills/_INDEX.md", "projects/_INDEX.md"]


def upgrade(root: Path, dry_run: bool = False) -> int:
    prof = core.load_profile(root)
    ctx = dict(prof)
    ctx["date"] = core.today()

    added, kept = [], []
    for rel, content in scaffold.TEMPLATES.items():
        target = root / rel
        if target.exists():
            kept.append(rel)
            continue
        added.append(rel)
        if not dry_run:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(core.render(content, ctx), encoding="utf-8")

    if not dry_run:
        moc.write_mocs(root)

    verb = "would add" if dry_run else "added"
    print(f"wsx upgrade — corrective pass{'  (dry-run — nothing written)' if dry_run else ''}\n")
    if added:
        print(f"  {verb} {len(added)} missing scaffold file(s):")
        for rel in added:
            print(f"    + {rel}")
    else:
        print("  scaffold complete — no missing files.")
    reverb = "would regenerate" if dry_run else "regenerated"
    print(f"\n  {reverb} the connective MOC layer (reconnects the Obsidian graph):")
    for rel in _REGENERATED:
        print(f"    ~ {rel}")
    print(f"\n  kept {len(kept)} existing file(s) untouched (non-destructive).")
    if dry_run:
        print("\n  → run `wsx upgrade` (no --dry-run) to apply.")
    else:
        print("\n  next: `wsx lint` and `wsx emit all` to refresh the AI adapters.")
    return 0
