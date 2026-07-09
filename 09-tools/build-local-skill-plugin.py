#!/usr/bin/env python3
"""
build-local-skill-plugin.py — mirror curated 03-skills/ hubs into a LOCAL Claude
Code plugin so they surface as native `/snds:<name>` slash commands.

Why this exists
---------------
`03-skills/` (in the portable git checkout — the source of truth) defines Sean's
hub/spoke skill network. Those skills are available to the *model* but are NOT
installable local Claude Code plugins, so they never appear in the interactive `/`
autocomplete menu.

This script does that for local Claude Code: it COPIES a curated set of hub skills
out of the checkout's `03-skills/` into a self-contained plugin under
`~/.claude/local-plugins/` (kept outside the repo so the generated mirror isn't
committed back into the workspace as duplicate skill copies), then writes the
marketplace + plugin manifests. Re-run it after any refactor so the slash commands
reflect the current checkout.

After running, register it once per machine:

    claude plugin marketplace add ~/.claude/local-plugins/snds-local
    claude plugin install snds@snds-local
    # then restart Claude Code

Re-run this script any time you edit a hub's SKILL.md or change the HUBS list.
It rebuilds the plugin's skills/ dir from scratch, so removed hubs disappear.

Single source of truth stays `03-skills/`. This is a generated mirror.
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

# --- Config -----------------------------------------------------------------

# Curated operational hub skills (entry points), not the spokes. Edit this list
# to add/remove commands, then re-run. Names must match dir names in 03-skills/.
HUBS = [
    # Workspace / session ops
    "workspace-bootstrap",
    # Design systems + Figma
    "ds-advisor",
    "design-engineer",
    "ux-component-library",
    "figma-canvas-designer",
    "figma-plugin-dev",
    "variable-icon-font-architect",
    "visual-qa-toolkit",
    # Project hubs
    "legion-project",
    "lead-game-designer",
    "lead-art-director",
    "lead-game-developer",
    "omni-project",
    "material-symbols-project",
    # Discipline leads (most-used)
    "lead-ux-designer",
    "lead-ui-designer",
    "lead-frontend-engineer",
    "lead-product-manager",
]

MARKETPLACE_NAME = "snds-local"
PLUGIN_NAME = "snds"  # command prefix -> /snds:<skill>
PLUGIN_VERSION = "0.3.0"  # 0.3.0: ships the ws-bootstrap SessionStart hook (bootstrap layer L4)

# --- Paths ------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent           # .../09-tools
WORKSPACE_ROOT = SCRIPT_DIR.parent                      # workspace root
SRC_SKILLS = WORKSPACE_ROOT / "03-skills"

DEST_ROOT = Path.home() / ".claude" / "local-plugins" / MARKETPLACE_NAME
PLUGIN_DIR = DEST_ROOT / PLUGIN_NAME
SKILLS_DIR = PLUGIN_DIR / "skills"


def main() -> int:
    if not SRC_SKILLS.is_dir():
        print(f"ERROR: source skills dir not found: {SRC_SKILLS}", file=sys.stderr)
        return 1

    # Validate every hub before we touch anything.
    missing = [h for h in HUBS if not (SRC_SKILLS / h / "SKILL.md").is_file()]
    if missing:
        print("ERROR: these hubs have no SKILL.md in 03-skills/:", file=sys.stderr)
        for h in missing:
            print(f"  - {h}", file=sys.stderr)
        return 1

    # Clean rebuild of the skills dir so removed hubs disappear.
    if SKILLS_DIR.exists():
        shutil.rmtree(SKILLS_DIR)
    SKILLS_DIR.mkdir(parents=True, exist_ok=True)

    copied = []
    for h in HUBS:
        src = SRC_SKILLS / h
        dst = SKILLS_DIR / h
        # Copy the whole skill dir (SKILL.md + any supporting files/scripts).
        shutil.copytree(src, dst, ignore=shutil.ignore_patterns(".git", "__pycache__"))
        copied.append(h)

    # Plugin hooks — L4 of the bootstrap guarantee. Points at the WORKSPACE copy of
    # the SessionStart script (different failure surface from ~/.claude/hooks/);
    # dedup vs the user-scope registration is the script's own atomic marker.
    hooks_src = WORKSPACE_ROOT / "00-bootstrap" / "dist" / "plugin-hooks.json"
    if hooks_src.exists():
        hooks_dir = PLUGIN_DIR / "hooks"
        hooks_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(hooks_src, hooks_dir / "hooks.json")

    # Plugin manifest.
    plugin_manifest = {
        "name": PLUGIN_NAME,
        "description": "Sean's curated operational hub skills, mirrored from the "
        "Claude Workspace 03-skills/ network for native slash-command access.",
        "version": PLUGIN_VERSION,
        "keywords": ["design-systems", "figma", "workspace", "qa", "legion", "icon-fonts"],
    }
    (PLUGIN_DIR / ".claude-plugin").mkdir(parents=True, exist_ok=True)
    (PLUGIN_DIR / ".claude-plugin" / "plugin.json").write_text(
        json.dumps(plugin_manifest, indent=2) + "\n", encoding="utf-8"
    )

    # Marketplace manifest. Relative source resolves from the marketplace root.
    marketplace_manifest = {
        "$schema": "https://anthropic.com/claude-code/marketplace.schema.json",
        "name": MARKETPLACE_NAME,
        "description": "Local mirror of curated Claude Workspace hub skills.",
        "owner": {"name": "Sean Sands", "email": "hello@snds.design"},
        "plugins": [
            {
                "name": PLUGIN_NAME,
                "source": f"./{PLUGIN_NAME}",
                "description": "Curated operational hub skills "
                "(design systems, Figma, icon fonts, QA, Legion, Omni, workspace ops).",
            }
        ],
    }
    (DEST_ROOT / ".claude-plugin").mkdir(parents=True, exist_ok=True)
    (DEST_ROOT / ".claude-plugin" / "marketplace.json").write_text(
        json.dumps(marketplace_manifest, indent=2) + "\n", encoding="utf-8"
    )

    print(f"Built local plugin '{PLUGIN_NAME}' with {len(copied)} skills at:")
    print(f"  {DEST_ROOT}")
    print()
    print("Skills mirrored:")
    for h in copied:
        print(f"  /{PLUGIN_NAME}:{h}")
    print()
    print("Next steps (run once per machine, then restart Claude Code):")
    print(f"  claude plugin marketplace add {DEST_ROOT}")
    print(f"  claude plugin install {PLUGIN_NAME}@{MARKETPLACE_NAME}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
