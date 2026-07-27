"""`skills.registry.json` — the machine index the trigger-router reads.

Generated from every skill's OWN front matter (name / description / triggers / hub /
kind / path). There is **no hardcoded routing table**: a skill routes on the triggers it
declares, so the automation is driven entirely by the person's own workspace content.
The neutral automation ported from a comprehensive workspace all reads this file.

Regenerated on `emit`, `skill add`, `skill reindex`, and `upgrade`, and by the
standalone `09-tools/build-registry.py` (so a workspace can rebuild it without wsx).
"""
from __future__ import annotations

import json
from pathlib import Path

from . import core, layout


def build(root: Path) -> Path:
    """Write <skills>/skills.registry.json from the front matter of every skill."""
    lay = layout.of(root)
    sk_dir = lay.dir("skills")
    sk_name = lay.name("skills")
    entries = []
    for name, sk in core.iter_skills(root):
        fm, _ = core.parse_frontmatter(sk)
        entries.append({
            "name": name,
            "path": f"{sk_name}/{name}/SKILL.md",
            "hub": str(fm.get("hub", "") or ""),
            "kind": fm.get("kind", "spoke"),
            "triggers": core.skill_triggers(fm),
            "description": str(fm.get("description", "")).strip(),
        })
    out = sk_dir / "skills.registry.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated": core.now_stamp(),
        "skills_dir": sk_name,
        "count": len(entries),
        "skills": sorted(entries, key=lambda e: e["name"]),
    }
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return out
