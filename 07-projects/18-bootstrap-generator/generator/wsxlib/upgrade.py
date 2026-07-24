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


def _migrate_drop_encrypt(root: Path, dry_run: bool):
    """Remove the `privacy.encrypt` field. It was never implemented — the interview
    even ASKED for it and said wsx would handle it — so anyone who answered "yes" has
    been carrying a false guarantee. Strip it and say so plainly; at-rest protection is
    the OS's job (FileVault/BitLocker/LUKS), not this tool's."""
    prof = core.load_profile(root)
    priv = prof.get("privacy")
    if not isinstance(priv, dict) or "encrypt" not in priv:
        return None
    was_on = bool(priv.get("encrypt"))
    if not dry_run:
        priv.pop("encrypt", None)
        core.save_profile(root, prof)
    why = ("removed `privacy.encrypt` — wsx never implemented vault encryption, so this "
           "field promised protection it did not provide")
    if was_on:
        why += (". IT WAS SET TO TRUE: your personal notes were NEVER encrypted — only "
                "gitignored. Turn on full-disk encryption (FileVault/BitLocker) if you "
                "want at-rest protection")
    return ("context/profile.yaml", why)


def _reconcile_remote(root: Path, dry_run: bool):
    """profile.transport.remote is only a recorded string; `wsx remote` is what actually
    configures git. If the profile declares one and git has none, the person believes
    their work is backed up while nothing can push. Wire it — that's plainly intended."""
    if not (root / ".git").exists():
        return None
    declared = str(core.load_profile(root).get("transport", {}).get("remote", "") or "").strip()
    if not declared:
        return None
    r = core.git(root, "remote", "get-url", "origin", check=False, capture=True)
    if (r.stdout or "").strip():
        return None  # already configured
    if not dry_run:
        core.git(root, "remote", "add", "origin", declared, check=False)
    return ("git remote",
            f"profile declared {declared} but git had none configured → wired it "
            "(run `wsx sync` to push)")


MIGRATIONS = [_migrate_critical_facts, _migrate_separation,
              _migrate_drop_encrypt, _reconcile_remote]


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
    return ("git", "repository has NO commits because git has no author identity. "
                   "Ask the person what name + email to sign their commits with, then run:\n"
                   '      wsx identity --name "<their name>" --email "<their email>"\n'
                   "      (workspace-only by default; it makes the first commit for you)")

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
