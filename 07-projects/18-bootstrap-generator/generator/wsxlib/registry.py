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


def _is_foreign_registry(f: Path) -> bool:
    """True if an existing registry was written by SOMETHING ELSE (a hand-built vault's own
    tool), not by wsx. wsx registries carry `generated`/`skills_dir`; a foreign one has other
    shapes (e.g. `registry_version`/`$schema`). We must never overwrite that."""
    if not f.exists():
        return False
    try:
        data = json.loads(f.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return True  # unparseable / not ours → treat as foreign, don't clobber
    if isinstance(data, dict) and ("generated" in data and "skills_dir" in data):
        return False  # our own format — safe to regenerate
    return True


def build(root: Path) -> Path:
    """Write <skills>/skills.registry.json from the front matter of every skill.

    If a FOREIGN registry (a hand-built vault's own, in a different format) is already there,
    we never overwrite it — we write ours alongside as `skills.registry.wsx.json` so both
    survive. Prevents the data-loss the upgrade-against-a-rich-vault test surfaced."""
    lay = layout.of(root)
    sk_dir = lay.dir("skills")
    sk_name = lay.name("skills")
    fname = "skills.registry.json"
    if _is_foreign_registry(sk_dir / "skills.registry.json"):
        fname = "skills.registry.wsx.json"  # don't clobber the person's own registry
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
    out = sk_dir / fname
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated": core.now_stamp(),
        "skills_dir": sk_name,
        "count": len(entries),
        "skills": sorted(entries, key=lambda e: e["name"]),
    }
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return out
