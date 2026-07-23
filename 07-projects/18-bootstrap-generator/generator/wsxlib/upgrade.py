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

import re
from pathlib import Path

from . import core, moc, scaffold


# --------------------------------------------------------------- migrations ---
# "Non-destructive" must not mean "leaves known-broken content in place". A migration
# repairs a SPECIFIC, generator-authored line that we know is wrong, surgically —
# everything the person wrote themselves is untouched. Each is idempotent.

def _migrate_critical_facts(root: Path, dry_run: bool):
    """Old CRITICAL_FACTS.md baked `primary assistant: <value>` in at init time, so it
    silently contradicted profile.yaml the moment the interview set the real surface.
    Replace that one line with the pointer form (no duplicated volatile state)."""
    f = root / "context" / "CRITICAL_FACTS.md"
    if not f.exists():
        return None
    text = f.read_text(encoding="utf-8")
    pat = re.compile(r"^- \*\*Who:\*\*.*primary assistant:.*$", re.MULTILINE)
    if not pat.search(text):
        return None
    name = str(core.load_profile(root).get("identity", {}).get("name", "you"))
    new = (f"- **Who:** {name}. Current surfaces, model tier, and preferences live in\n"
           "  [profile](profile.md) (regenerated from `profile.yaml` — always trust those two\n"
           "  over anything restated elsewhere).")
    if not dry_run:
        f.write_text(pat.sub(new, text, count=1), encoding="utf-8")
    return ("context/CRITICAL_FACTS.md",
            "stale `primary assistant:` line contradicted profile.yaml → replaced with a pointer")


def _migrate_separation(root: Path, dry_run: bool):
    """Same class of bug on the Separation line (baked value, never refreshed)."""
    f = root / "context" / "CRITICAL_FACTS.md"
    if not f.exists():
        return None
    text = f.read_text(encoding="utf-8")
    pat = re.compile(r"^- \*\*Separation:\*\* (?!personal context is local/walled unless you opted in)"
                     r".*$", re.MULTILINE)
    if not pat.search(text):
        return None
    new = ("- **Separation:** personal context is local/walled unless you opted in "
           "(see [profile](profile.md)).")
    if not dry_run:
        f.write_text(pat.sub(new, text, count=1), encoding="utf-8")
    return ("context/CRITICAL_FACTS.md",
            "baked `Separation:` value → replaced with a pointer to the profile")


MIGRATIONS = [_migrate_critical_facts, _migrate_separation]


def _bootstrap_git(root: Path, dry_run: bool):
    """A repo with ZERO commits is the silent failure mode from `wsx init` on a machine
    with no git identity: files exist, nothing is versioned, nothing can sync. Land the
    first commit if we can; if git has no identity, say exactly what's needed."""
    if not (root / ".git").exists():
        return None
    r = core.git(root, "rev-list", "--count", "HEAD", check=False, capture=True)
    if r.returncode == 0 and (r.stdout or "").strip().isdigit() and int(r.stdout.strip()) > 0:
        return None  # history exists — nothing to do
    if dry_run:
        return ("git", "repository has NO commits — would create the first one")
    core.git(root, "add", "-A", check=False)
    core.git(root, "commit", "-q", "-m", "wsx: initial commit of the workspace", check=False)
    ok, hint = scaffold._commit_ok(root)
    if ok:
        return ("git", "repository had NO commits — created the first one (your work is now versioned)")
    return ("git", "repository has NO commits and git has no identity configured. "
                   "Ask the person for their name + email, then run:\n"
                   f"{hint}\n      then: git -C \"{root}\" add -A && "
                   "git -C . commit -m \"wsx: initial commit\"")

# Generated files that upgrade always (re)writes — safe because they are derived
# from disk, never hand-authored.
_REGENERATED = ["HOME.md", "skills/_INDEX.md", "projects/_INDEX.md",
                "context/profile.md"]  # mirror of profile.yaml — must never be stale


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

    # Refresh the vendored CLI so an older workspace becomes self-sufficient too
    # (and picks up new commands like `health`). Always safe: it's generated code.
    vendored = []
    if not dry_run:
        moc.write_mocs(root)
        vendored = scaffold.vendor_cli(root)

    # Repair known-broken generated content + land a first commit if there is none.
    repairs = [r for r in (m(root, dry_run) for m in MIGRATIONS) if r]
    git_note = _bootstrap_git(root, dry_run)

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
    print(f"\n  {reverb} the vendored CLI so this workspace can drive itself:")
    print(f"    ~ wsx.py + .wsx/wsxlib/  ({len(vendored) or 'refreshed'} file(s))"
          if not dry_run else "    ~ wsx.py + .wsx/wsxlib/")
    print("      → run it here:  python3 wsx.py doctor")
    rverb = "would repair" if dry_run else "repaired"
    if repairs:
        print(f"\n  {rverb} known-stale generated content (your own writing untouched):")
        for rel, why in repairs:
            print(f"    ✎ {rel} — {why}")
    if git_note:
        print(f"\n  git:\n    • {git_note[1]}")

    print(f"\n  kept {len(kept)} existing file(s) untouched (non-destructive).")
    if dry_run:
        print("\n  → run `wsx upgrade` (no --dry-run) to apply.")
    else:
        print("\n  next: `wsx lint` and `wsx emit all` to refresh the AI adapters.")
    return 0
