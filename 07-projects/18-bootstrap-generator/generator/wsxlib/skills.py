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
        "kind": fm.get("kind", "spoke"),
        "triggers": core.skill_triggers(fm),
        "source": fm.get("source", "generated"),
        "hash": core.sha256_file(sk),
    }


# The brain (Claude) authors the prose; `wsx skill add` lays down the *structure*
# it fills — a sectioned skeleton, not a flat stub. Every `_(...)` italic line is a
# writing prompt the brain replaces. Front matter stays the single source of truth
# for name/description/triggers; the body is where the reusable know-how goes.
def _skeleton_spoke(title: str, desc: str, hub: str) -> str:
    return (
        f"# {title}\n\n"
        "> **Skill skeleton — the brain replaces every _(…)_ prompt with real prose,\n"
        "> then runs `wsx skill reindex`. Front matter is the source of truth for\n"
        "> the name, description, and triggers; the body is the know-how.**\n\n"
        "## When to use this\n\n"
        f"{desc}\n\n"
        "Reach for this skill when… _(name the concrete moments/tasks that should\n"
        "load it — be specific to how this person actually works)_\n\n"
        "**Not** for: _(what this skill deliberately does NOT cover — and where to go instead)_\n\n"
        "## How to do it well\n\n"
        "_(the heart of the skill: the actual procedure, judgment calls, and standards\n"
        "that make this person's work in this area good. Write the reusable know-how —\n"
        "not generic advice an untuned model already has.)_\n\n"
        "1. …\n2. …\n3. …\n\n"
        "## Worked example\n\n"
        "_(one concrete, end-to-end example in this person's real domain — inputs,\n"
        "the decision, the output)_\n\n"
        "## Anti-patterns to avoid\n\n"
        "- _(the specific mistakes this person has learned to stop making)_\n\n"
        "## Related\n\n"
        f"- **Hub:** `{hub}`\n"
        "- **See also:** _(sibling spokes this composes with — run `wsx skill list`)_\n"
    )


def _skeleton_hub(title: str, desc: str, name: str) -> str:
    return (
        f"# {title}\n\n"
        "> **Hub skeleton — the brain replaces every _(…)_ prompt with real prose,\n"
        "> then runs `wsx skill reindex`. A hub orchestrates focused spokes; keep the\n"
        "> deep how-to in the spokes and the routing + shared standards here.**\n\n"
        "## What this hub owns\n\n"
        f"{desc}\n\n"
        "Load this hub when the work touches _(this domain)_, then route to the spoke\n"
        "that matches the task.\n\n"
        "## Spokes in this hub\n\n"
        "_(list each spoke + one line on when to route to it. Create spokes with\n"
        f"`wsx skill add <spoke> --hub {name} --kind spoke --desc \"…\"`.)_\n\n"
        "- `…` — …\n\n"
        "## Operating standards (apply across every spoke)\n\n"
        "_(the cross-cutting judgment and quality bar for this whole domain — the\n"
        "things true no matter which spoke is active)_\n\n"
        "## Anti-patterns to avoid\n\n"
        "- _(domain-wide mistakes to steer every spoke away from)_\n\n"
        "## Related\n\n"
        "- **Spokes:** run `wsx skill list` to see this hub's members.\n"
    )


def add(root: Path, name: str, desc: str, triggers, hub: str,
        source: str = "generated", title: str = "", kind: str = "spoke") -> int:
    sk = root / "skills" / name / "SKILL.md"
    if sk.exists():
        raise SystemExit(f"error: skill '{name}' already exists ({sk.relative_to(root)})")
    trg = ([t.strip() for t in triggers.split(",") if t.strip()]
           if isinstance(triggers, str) else list(triggers or []))
    disp = title or _title(name)
    fm = {
        "name": name,
        "description": desc,
        "triggers": trg,
        "hub": hub or name,
        "kind": kind,
        "source": source,
    }
    if kind == "hub":
        fm["role"] = "orchestrator"
    body = (_skeleton_hub(disp, desc, name) if kind == "hub"
            else _skeleton_spoke(disp, desc, fm["hub"]))
    sk.parent.mkdir(parents=True, exist_ok=True)
    sk.write_text(f"---\n{yamlio.dumps(fm)}\n---\n\n{body}", encoding="utf-8")

    man = core.load_manifest(root)
    man.setdefault("skills", {})[name] = _record(root, name)
    core.save_manifest(root, man)
    print(f"✓ {kind} '{name}' created  [hub: {fm['hub']}]  ({source}, {len(trg)} trigger(s))")
    print("  skeleton written — enrich the body sections, then: wsx skill reindex")
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
            tags = []
            if rec.get("kind") == "hub":
                tags.append("hub")
            if rec.get("source") != "generated":
                tags.append(rec.get("source"))
            tag = f" [{', '.join(tags)}]" if tags else ""
            print(f"  └─ {name}{tag}  — {trg}")
    return 0
