"""Lifecycle + maintenance commands: lint, verify, session, sync, resolve, doctor."""
from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

from . import adapters, core, yamlio


# ------------------------------------------------------------------ doctor ---
def doctor() -> int:
    """Check the environment and tell the user exactly what to do next.

    Designed for the 'I ran it and nothing happened' moment: it explains where
    you are (generator vs. workspace) and the one command to run.
    """
    print("wsx doctor — checking your setup\n")
    print(f"  python3   : ✓ {sys.version.split()[0]}")
    git = shutil.which("git")
    if git:
        print(f"  git       : ✓ {git}")
    else:
        print("  git       : ✗ not found — install GitHub Desktop "
              "(https://github.com/apps/desktop) for sync + history")
    here = os.getcwd()
    print(f"  here      : {here}")
    root = core.find_workspace_root()
    if root:
        print(f"  workspace : ✓ {root}\n")
        print("  You're inside a workspace. Useful next:")
        print("    wsx verify            # check it's healthy")
        print("    wsx emit claude-code  # make it AI-ready")
    else:
        print("  workspace : — none here (this is the GENERATOR, not a workspace)\n")
        print("  The generator BUILDS a separate workspace folder. To create yours:")
        print('    wsx init ~/Documents/my-workspace --name "Your Name"')
        print("  …or just open this folder in your AI assistant and say:")
        print('    "set up my workspace"')
    return 0


# -------------------------------------------------------------------- lint ---
def lint(root: Path) -> int:
    """Validate skills + manifest; report trigger overlaps. Returns problem count."""
    problems = 0
    trigger_owners: dict[str, list] = {}
    skills = list(core.iter_skills(root))

    for name, sk in skills:
        fm, body = core.parse_frontmatter(sk)
        if not fm.get("name"):
            print(f"  ✗ {name}: missing 'name' in front matter")
            problems += 1
        if not str(fm.get("description", "")).strip():
            print(f"  ✗ {name}: missing 'description' in front matter")
            problems += 1
        # un-enriched skeleton: the brain must replace the `_(…)_` writing prompts
        # (and drop the skeleton banner) before shipping. Pulled skills are exempt —
        # they arrive finished from a registry, not from our skeleton.
        if fm.get("source", "generated") == "generated":
            prompts = body.count("_(")
            if "skeleton —" in body or prompts:
                detail = f"{prompts} unfilled prompt(s)" if prompts else "skeleton banner still present"
                print(f"  ⚠ {name}: un-enriched skeleton — {detail}; "
                      "fill the body, then `wsx skill reindex`")
                problems += 1
        for t in core.skill_triggers(fm):
            trigger_owners.setdefault(t, []).append(name)

    for trg, owners in sorted(trigger_owners.items()):
        if len(owners) > 1:
            print(f"  ⚠ trigger overlap: '{trg}' claimed by {', '.join(owners)} "
                  "— assign one canonical owner (see brain/resolver.md)")
            problems += 1

    # manifest sanity
    man = core.load_manifest(root)
    if man.get("schema_version") != "0.2":
        print(f"  ⚠ manifest schema_version is {man.get('schema_version')!r} (expected '0.2')")
        problems += 1

    if problems == 0:
        print(f"✓ lint clean — {len(skills)} skill(s), no trigger overlaps")
    else:
        print(f"lint found {problems} issue(s) across {len(skills)} skill(s)")
    return problems


# ------------------------------------------------------------------ verify ---
def verify(root: Path) -> int:
    """Dry-run: round-trip the profile and gather each emit target. Returns failure count."""
    fails = 0

    # 1. profile round-trips through the YAML subset
    prof = core.load_profile(root)
    try:
        reparsed = yamlio.loads(yamlio.dumps(prof))
        if reparsed != prof:
            print("  ✗ profile.yaml does not round-trip through the YAML subset")
            fails += 1
        else:
            print("  ✓ profile.yaml round-trips cleanly")
    except Exception as e:  # noqa: BLE001
        print(f"  ✗ profile.yaml failed to parse: {e}")
        fails += 1

    # 2. each adapter can gather without error (no files written)
    for target in ("claude-code", "agents-md", "cursor", "pack"):
        try:
            adapters.gather(root, prof)
            print(f"  ✓ {target}: ready to emit")
        except Exception as e:  # noqa: BLE001
            print(f"  ✗ {target}: gather failed — {e}")
            fails += 1

    # 3. required canonical files exist
    for rel in ("context/project-context.md", "context/session-log.md", "manifest.json"):
        if not (root / rel).exists():
            print(f"  ✗ missing canonical file: {rel}")
            fails += 1

    print("✓ verify passed" if fails == 0 else f"verify found {fails} failure(s)")
    return fails


# ----------------------------------------------------------------- session ---
def session(root: Path, sub: str) -> int:
    log = root / "context" / "session-log.md"
    if sub == "start":
        print(f"session started {core.now_stamp()} — context loaded from {root}")
        return 0
    if sub == "end":
        block = (
            f"\n--- SESSION BLOCK ---\n"
            f"Date: {core.today()}\n"
            f"Stamp: {core.now_stamp()}\n"
            f"Summary: (fill in)\n"
            f"--- END BLOCK ---\n"
        )
        with log.open("a", encoding="utf-8") as fh:
            fh.write(block)
        print(f"✓ session block appended to {log.relative_to(root)}")
        return 0
    if sub == "reconcile":
        print("note: reconcile merges Session Blocks from concurrent machines — "
              "not yet implemented (see SPEC). No changes made.")
        return 0
    raise SystemExit("error: session expects start|end|reconcile")


# -------------------------------------------------------------------- sync ---
def sync(root: Path) -> int:
    if not core.has_remote(root):
        print("note: no git remote configured — nothing to sync. "
              "Add one with GitHub Desktop or `git remote add origin <url>`.")
        return 0
    print("syncing via git…")
    pull = core.git(root, "pull", "--rebase", "--autostash", check=False, capture=True)
    if pull.returncode != 0:
        print(pull.stderr.strip())
        print("✗ pull failed — resolve manually, then `wsx sync` again")
        return 1
    push = core.git(root, "push", check=False, capture=True)
    if push.returncode != 0:
        print(push.stderr.strip())
        return 1
    print("✓ synced (pull --rebase + push)")
    return 0


# ----------------------------------------------------------------- resolve ---
def resolve(root: Path) -> int:
    """STUB (honest): the mechanical half of the Resolver (fetch + pin pulled skills).

    The brain's judgment (pull/adapt/generate, hub assignment, overlap reconciliation)
    lives in brain/resolver.md. This command will fetch + pin skills the brain selected.
    Not yet implemented — it currently reports the plan location and exits cleanly.
    """
    plan = root / "context" / "skill-plan.md"
    print("🚧 wsx resolve is a stub (see SPEC §4 + brain/resolver.md).")
    if plan.exists():
        print(f"   found a skill plan at {plan.relative_to(root)} — fetch/pin not yet wired.")
    else:
        print("   no skill-plan.md yet — the brain produces one (capability → source → hub → triggers)")
        print("   and shows it as a review gate before anything installs.")
    return 0
