"""Skill operations — the mechanical hand for the Resolver's GENERATE path.

The brain decides *what* skill to make (name, hub, triggers, when-to-use); `wsx
skill add` is how it actually creates the file and registers it in the manifest,
so the brain never hand-writes structural files. `reindex` rebuilds the manifest
skill index from disk (e.g. after the brain enriches a SKILL.md body).
"""
from __future__ import annotations

from pathlib import Path

from . import core, yamlio


def _title(name: str) -> str:
    return name.replace("-", " ").replace("_", " ").title()


def _record(root: Path, name: str) -> dict:
    sk = root / "skills" / name / "SKILL.md"
    fm, _ = core.parse_frontmatter(sk)
    return {
        "path": f"skills/{name}/SKILL.md",
        "hub": fm.get("hub", ""),
        "triggers": core.skill_triggers(fm),
        "source": fm.get("source", "generated"),
        "hash": core.sha256_file(sk),
    }


def add(root: Path, name: str, desc: str, triggers, hub: str,
        source: str = "generated", title: str = "") -> int:
    sk = root / "skills" / name / "SKILL.md"
    if sk.exists():
        raise SystemExit(f"error: skill '{name}' already exists ({sk.relative_to(root)})")
    trg = ([t.strip() for t in triggers.split(",") if t.strip()]
           if isinstance(triggers, str) else list(triggers or []))
    fm = {
        "name": name,
        "description": desc,
        "triggers": trg,
        "hub": hub or name,
        "source": source,
    }
    body = (f"# {title or _title(name)}\n\n{desc}\n\n"
            "_Generated stub — the brain enriches this with when-to-use, the how-to,\n"
            "and examples. Run `wsx skill reindex` after editing the front matter._\n")
    sk.parent.mkdir(parents=True, exist_ok=True)
    sk.write_text(f"---\n{yamlio.dumps(fm)}\n---\n\n{body}", encoding="utf-8")

    man = core.load_manifest(root)
    man.setdefault("skills", {})[name] = _record(root, name)
    core.save_manifest(root, man)
    print(f"✓ skill '{name}' created  [hub: {fm['hub']}]  ({source}, {len(trg)} trigger(s))")
    return 0


def reindex(root: Path) -> int:
    man = core.load_manifest(root)
    man["skills"] = {name: _record(root, name) for name, _ in core.iter_skills(root)}
    core.save_manifest(root, man)
    print(f"✓ reindexed {len(man['skills'])} skill(s) into manifest.json")
    return 0


def list_skills(root: Path) -> int:
    man = core.load_manifest(root)
    skills = man.get("skills", {})
    if not skills:
        disk = list(core.iter_skills(root))
        if not disk:
            print('(no skills yet — create one: wsx skill add <name> --desc "…")')
            return 0
        print("(skills on disk but not indexed — run: wsx skill reindex)")
        for name, _ in disk:
            print(f"  {name}")
        return 0
    # group by hub for a readable tree
    by_hub: dict[str, list] = {}
    for name, rec in sorted(skills.items()):
        by_hub.setdefault(rec.get("hub", "") or name, []).append((name, rec))
    for hub, members in sorted(by_hub.items()):
        print(f"{hub}")
        for name, rec in members:
            trg = ", ".join(rec.get("triggers", []))
            tag = "" if rec.get("source") == "generated" else f" ({rec.get('source')})"
            print(f"  └─ {name}{tag}  — {trg}")
    return 0
