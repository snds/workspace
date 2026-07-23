"""Skill operations — the mechanical hand for the Resolver's GENERATE path.

The brain decides *what* skill to make (name, hub, triggers, when-to-use); `wsx
skill add` is how it actually creates the file and registers it in the manifest,
so the brain never hand-writes structural files. `reindex` rebuilds the manifest
skill index from disk (e.g. after the brain enriches a SKILL.md body).
"""
from __future__ import annotations

from pathlib import Path

from . import core, moc, yamlio


def _title(name: str) -> str:
    return name.replace("-", " ").replace("_", " ").title()


def _record(root: Path, name: str) -> dict:
    sk = root / "skills" / name / "SKILL.md"
    fm, _ = core.parse_frontmatter(sk)
    rec = {
        "path": f"skills/{name}/SKILL.md",
        "hub": fm.get("hub", ""),
        "kind": fm.get("kind", "spoke"),
        "level": fm.get("level", "intermediate"),
        "triggers": core.skill_triggers(fm),
        "source": fm.get("source", "generated"),
        "hash": core.sha256_file(sk),
    }
    if fm.get("seniority"):
        rec["seniority"] = fm["seniority"]
    return rec


LEVELS = ("hobbyist", "intermediate", "advanced", "expert")


# The heart of expertise calibration: the same skill is written at a different
# ALTITUDE depending on the person's level IN THIS DOMAIN. A hobbyist skill teaches
# fundamentals; an expert skill assumes fluency and captures the person's own
# judgment. Returns (altitude_note, how_prompt, extra_sections) for the skeleton.
def _altitude(level: str, seniority: str = "") -> tuple:
    sen = f", {seniority}-level" if seniority else ""
    frames = {
        "hobbyist": (
            f"Written for a **hobbyist**{sen} — someone learning this domain for love of it. "
            "TEACH: define the jargon, explain the *why*, scaffold each step. Assume enthusiasm, "
            "not fluency; never assume prior knowledge.",
            "the fundamentals done right — define the key terms, explain the reasoning, and give "
            "a beginner-safe procedure. Call out the classic beginner mistakes by name.",
            [("Foundations to learn",
              "the handful of underlying concepts worth building up first — each with a one-line "
              "'why it matters' and a pointer to where to go deeper")],
        ),
        "intermediate": (
            f"Written for an **intermediate**{sen} practitioner — has the basics, building fluency.",
            "the reusable procedure and the judgment that separates competent from good; assume "
            "the basics are known and focus on doing it well.",
            [],
        ),
        "advanced": (
            f"Written for an **advanced**{sen} practitioner — fluent, sharpening edge and nuance.",
            "the non-obvious techniques and refinements; skip the basics entirely and focus on the "
            "trade-offs, corner cases, and quality bar that lift advanced work.",
            [("Trade-offs & when to break the rules",
              "the situational calls where the textbook answer is wrong, and how this person decides")],
        ),
        "expert": (
            f"Written for an **expert**{sen} with deep fluency and their own opinions. Do NOT "
            "re-explain fundamentals — capture THEIR judgment: the hard-won calls, the edge cases, "
            "where even good practitioners slip. Peer-level and terse.",
            "this person's own judgment and signature method — the non-obvious calls, the edge cases, "
            "the things true at their level that aren't in any textbook. Terse; assume deep fluency.",
            [("Judgment calls & edge cases",
              "the hard decisions only experience settles — what this person weighs, and how")],
        ),
    }
    note, how, extras = frames.get(level, frames["intermediate"])
    if level == "expert" and seniority:
        extras = extras + [("Setting the bar & leading",
                            "how they review others' work, raise the standard, and lead in this "
                            "domain — the skill should help them operate at that altitude")]
    return note, how, extras


def _extra_sections_md(extras: list) -> str:
    out = ""
    for heading, prompt in extras:
        out += f"## {heading}\n\n_({prompt})_\n\n"
    return out


# The brain (Claude) authors the prose; `wsx skill add` lays down the *structure*
# it fills — a sectioned skeleton, not a flat stub. Every `_(...)` italic line is a
# writing prompt the brain replaces. Front matter stays the single source of truth
# for name/description/triggers; the body is where the reusable know-how goes.
def _skeleton_spoke(title: str, desc: str, hub: str, level: str, seniority: str) -> str:
    note, how, extras = _altitude(level, seniority)
    return (
        f"# {title}\n\n"
        "> **Skill skeleton — the brain replaces every _(…)_ prompt with real prose,\n"
        "> then runs `wsx skill reindex`. Front matter is the source of truth for\n"
        "> the name, description, and triggers; the body is the know-how.**\n>\n"
        f"> **Altitude — {level}:** {note}\n\n"
        "## When to use this\n\n"
        f"{desc}\n\n"
        "Reach for this skill when… _(name the concrete moments/tasks that should\n"
        "load it — be specific to how this person actually works)_\n\n"
        "**Not** for: _(what this skill deliberately does NOT cover — and where to go instead)_\n\n"
        "## How to do it well\n\n"
        f"_(the heart of the skill — write {how})_\n\n"
        "1. …\n2. …\n3. …\n\n"
        "## Worked example\n\n"
        "_(one concrete, end-to-end example in this person's real domain — inputs,\n"
        "the decision, the output)_\n\n"
        f"{_extra_sections_md(extras)}"
        "## Anti-patterns to avoid\n\n"
        "- _(the specific mistakes this person has learned to stop making)_\n\n"
        "## Related\n\n"
        # Real relative links → the Obsidian graph draws edges (a code span would not).
        f"- **Hub:** [{hub}](../{hub}/SKILL.md)\n"
        "- **All skills:** [index](../_INDEX.md)\n"
        "- **See also:** _(sibling spokes this composes with — run `wsx skill list`)_\n"
    )


def _skeleton_hub(title: str, desc: str, name: str, level: str, seniority: str) -> str:
    note, _how, _extras = _altitude(level, seniority)
    return (
        f"# {title}\n\n"
        "> **Hub skeleton — the brain replaces every _(…)_ prompt with real prose,\n"
        "> then runs `wsx skill reindex`. A hub orchestrates focused spokes; keep the\n"
        "> deep how-to in the spokes and the routing + shared standards here.**\n>\n"
        f"> **Altitude — {level}:** {note}\n\n"
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
        "- **All skills:** [index](../_INDEX.md)\n"
        "- **Spokes:** run `wsx skill list` to see this hub's members.\n"
    )


def add(root: Path, name: str, desc: str, triggers, hub: str,
        source: str = "generated", title: str = "", kind: str = "spoke",
        level: str = "intermediate", seniority: str = "") -> int:
    sk = root / "skills" / name / "SKILL.md"
    if sk.exists():
        raise SystemExit(f"error: skill '{name}' already exists ({sk.relative_to(root)})")
    if level not in LEVELS:
        level = "intermediate"
    trg = ([t.strip() for t in triggers.split(",") if t.strip()]
           if isinstance(triggers, str) else list(triggers or []))
    disp = title or _title(name)
    fm = {
        "name": name,
        "description": desc,
        "triggers": trg,
        "hub": hub or name,
        "kind": kind,
        "level": level,
        "source": source,
    }
    if seniority:
        fm["seniority"] = seniority
    if kind == "hub":
        fm["role"] = "orchestrator"
    body = (_skeleton_hub(disp, desc, name, level, seniority) if kind == "hub"
            else _skeleton_spoke(disp, desc, fm["hub"], level, seniority))
    sk.parent.mkdir(parents=True, exist_ok=True)
    sk.write_text(f"---\n{yamlio.dumps(fm)}\n---\n\n{body}", encoding="utf-8")

    man = core.load_manifest(root)
    man.setdefault("skills", {})[name] = _record(root, name)
    core.save_manifest(root, man)
    moc.write_mocs(root)  # relink HOME + skills index so the new skill joins the graph
    sen = f"/{seniority}" if seniority else ""
    print(f"✓ {kind} '{name}' created  [hub: {fm['hub']}]  ({source}, {level}{sen}, {len(trg)} trigger(s))")
    print(f"  skeleton written at {level} altitude — enrich the body, then: wsx skill reindex")
    return 0


def reindex(root: Path) -> int:
    man = core.load_manifest(root)
    prior = man.get("skills", {})
    rebuilt = {}
    for name, _ in core.iter_skills(root):
        old = prior.get(name, {})
        # Pulled/patched records are owned by `wsx resolve` (pin, registry, url,
        # read_only, pulled_at, the brain-assigned hub/triggers) — none of which live
        # in the upstream file's front matter. Rebuilding from disk would strip them,
        # so preserve the resolver's record verbatim; only generated skills reindex.
        if old.get("source") in ("pulled", "pulled+patched"):
            rebuilt[name] = old
        else:
            rebuilt[name] = _record(root, name)
    man["skills"] = rebuilt
    core.save_manifest(root, man)
    moc.write_mocs(root)  # keep HOME + skills index in sync with disk
    print(f"✓ reindexed {len(rebuilt)} skill(s) into manifest.json")
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
