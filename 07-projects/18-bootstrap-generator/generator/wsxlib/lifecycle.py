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
        print('    wsx init ~/Documents/Projects/Workspace --name "Your Name"')
        print("  …or just open this folder in your AI assistant and say:")
        print('    "set up my workspace"')
    return 0


# -------------------------------------------------------------------- lint ---
def lint(root: Path) -> int:
    """Validate skills + manifest; report trigger overlaps. Returns problem count."""
    problems = 0
    trigger_owners: dict[str, list] = {}
    skills = list(core.iter_skills(root))
    man = core.load_manifest(root)
    recs = man.get("skills", {})

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
        # composite skills must cite: if the manifest records references, the body
        # must carry the Sources block (the attribution the citations are for).
        rec = recs.get(name, {})
        if rec.get("references") and "wsx:sources" not in body and "Sources & further reading" not in body:
            print(f"  ⚠ {name}: composite skill has {len(rec['references'])} recorded "
                  "reference(s) but no Sources block — re-run `wsx resolve` to cite them")
            problems += 1
        for t in core.skill_triggers(fm):
            trigger_owners.setdefault(t, []).append(name)

    for trg, owners in sorted(trigger_owners.items()):
        if len(owners) > 1:
            print(f"  ⚠ trigger overlap: '{trg}' claimed by {', '.join(owners)} "
                  "— assign one canonical owner (see brain/resolver.md)")
            problems += 1

    # manifest sanity
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

    # 4. pinned content still matches its pin — pulled skills (byte-identical, read-only)
    #    and any cached composite references. Both must stay verifiable/re-fetchable.
    man = core.load_manifest(root)
    pins = []  # (label, path, pin)
    for name, rec in man.get("skills", {}).items():
        if rec.get("pin"):
            pins.append((name, rec.get("path", ""), rec["pin"]))
        for ref in rec.get("references", []):
            if ref.get("pin") and ref.get("cached"):
                pins.append((f"{name}:ref", ref["cached"], ref["pin"]))
    ok = 0
    for label, rel, pin in pins:
        f = root / rel
        if not f.exists():
            print(f"  ✗ {label}: pinned content missing on disk ({rel})")
            fails += 1
        elif core.sha256_file(f) != pin:
            print(f"  ✗ {label}: on-disk content diverged from its pin — pinned content "
                  "must stay byte-identical (patch via overlay, or re-run `wsx resolve --update`)")
            fails += 1
        else:
            ok += 1
    if pins:
        print(f"  ✓ {ok}/{len(pins)} pinned item(s) (pulled skills + cached refs) match their pin")

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
        print("note: no git remote configured — nothing to sync yet.")
        print("      run `wsx remote` for free hosting options (GitHub/GitLab/Codeberg),")
        print("      then `wsx remote <url>` to wire it.")
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


# ------------------------------------------------------------------ remote ---
_HOSTING = """where should this workspace live? (it's a git repo — pick a home so it
syncs across your machines and is backed up). Recommended, all free:

  • GitHub — a **private** repo (github.com/new → set Private). Most common; free
      private repos. Best if you already have an account.
  • GitLab (gitlab.com) — free private repos too; a good GitHub alternative.
  • Codeberg (codeberg.org) — free, community-run, no-tracking; nice for personal.
  • Local-only — no host at all; it just lives on this machine (you can add a
      remote later). Fine for a purely personal, single-machine setup.

Create an EMPTY repo (no README) on your chosen host, copy its URL, then run:
  wsx remote <url>        # e.g. wsx remote git@github.com:you/workspace.git
  wsx sync                # pushes your workspace up

Nothing is created for you — you own the account and the repo; wsx just wires it."""


def remote(root: Path, url: str = "") -> int:
    """Set (or show) the workspace's git remote, and record it in the profile.
    With no url, print the free-hosting recommendations."""
    if not url:
        if core.has_remote(root):
            r = core.git(root, "remote", "get-url", "origin", check=False, capture=True)
            print(f"remote 'origin' → {r.stdout.strip()}")
            print("change it with `wsx remote <url>`; push with `wsx sync`.")
        else:
            print(_HOSTING)
        return 0

    # add or update origin
    if core.has_remote(root):
        core.git(root, "remote", "set-url", "origin", url, check=False)
        verb = "updated"
    else:
        core.git(root, "remote", "add", "origin", url, check=False)
        verb = "set"

    # record intent in the profile so adapters/brain know where it lives
    prof = core.load_profile(root)
    prof.setdefault("transport", {})["type"] = "git"
    prof["transport"]["remote"] = url
    core.save_profile(root, prof)

    print(f"✓ remote 'origin' {verb} → {url}")
    print("  next: `wsx sync` to push your workspace up.")
    return 0


# resolve lives in resolver.py now (the mechanical half of the Resolver: fetch,
# pin, namespace, scaffold overlays, register). cli.cmd_resolve calls it directly.
