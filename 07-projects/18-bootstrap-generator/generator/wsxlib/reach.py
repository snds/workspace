"""`wsx reach` — well-formed ≠ reachable (Wave 3 lite harness).

Reports whether a cold agent can find, follow, and prove — not whether files parse.
Layer-0 adapters, trigger-routable skills, knowledge routes, named detectors.
Spokes without triggers are reported, not a blanket fail.
"""
from __future__ import annotations

from pathlib import Path

from . import core, layout


_LAYER0 = ("AGENTS.md", "HOME.md", "llms.txt")
_CROSS = ("close-out", "plan-ahead", "self-improve")


def report(root: Path) -> dict:
    lay = layout.of(root)
    skills = list(core.iter_skills(root))
    hubs, spokes, silent_hubs, silent_spokes = [], [], [], []
    for name, sk in skills:
        fm, _ = core.parse_frontmatter(sk)
        trg = core.skill_triggers(fm)
        kind = str(fm.get("kind") or "spoke")
        row = {"name": name, "path": str(sk.relative_to(root)), "triggers": trg}
        if core.is_command_skill(fm) or kind == "hub":
            hubs.append(row)
            if not trg:
                silent_hubs.append(name)
        else:
            spokes.append(row)
            if not trg:
                silent_spokes.append(name)
    kdir = lay.dir("knowledge")
    knowledge, unrouted_k = [], []
    skip = {"readme.md", "_index.md", "_template.md", "_readme.md"}
    if kdir.is_dir():
        for p in sorted(kdir.rglob("*.md")):
            if any(part.startswith(".") for part in p.relative_to(root).parts):
                continue
            if p.name.lower() in skip or p.stem.startswith("_"):
                continue
            knowledge.append(str(p.relative_to(root)))
            if not core.entry_triggers(p):
                unrouted_k.append(str(p.relative_to(root)))
    layer0 = {rel: (root / rel).exists() for rel in _LAYER0}
    present_cross = [n for n, _ in skills if n in _CROSS]
    missing_cross = [n for n in _CROSS if n not in present_cross]
    emitted = all(layer0.values())
    return {
        "layer0": layer0,
        "emitted": emitted,
        "hubs": len(hubs),
        "spokes": len(spokes),
        "silent_hubs": silent_hubs,
        "silent_spokes": silent_spokes,
        "knowledge": len(knowledge),
        "unrouted_knowledge": unrouted_k,
        "cross_cutting": present_cross,
        "missing_cross": missing_cross,
    }


def run(root: Path) -> int:
    d = report(root)
    fails = 0
    print("wsx reach — well-formed ≠ reachable\n")
    print("  Layer-0 (a cold agent’s first files):")
    for rel, ok in d["layer0"].items():
        mark = "✓" if ok else "·"
        print(f"    {mark} {rel}")
    if not d["emitted"]:
        print("    (emit not run yet — `wsx emit all` writes AGENTS.md / llms.txt)")
    print(f"\n  Skills: {d['hubs']} hub(s), {d['spokes']} spoke(s)")
    if d["silent_hubs"]:
        print(f"    ✗ silent hub(s) — never load: {', '.join(d['silent_hubs'])}")
        fails += 1
    else:
        print("    ✓ every hub declares triggers")
    if d["silent_spokes"]:
        print(f"    ⚠ {len(d['silent_spokes'])} spoke(s) with empty triggers "
              "(report only — a hub may route them):")
        for n in d["silent_spokes"][:8]:
            print(f"      · {n}")
        if len(d["silent_spokes"]) > 8:
            print(f"      …and {len(d['silent_spokes']) - 8} more")
    print(f"\n  Knowledge: {d['knowledge']} note(s)")
    if d["unrouted_knowledge"]:
        print(f"    ✗ {len(d['unrouted_knowledge'])} without Triggers: (not a route)")
        fails += 1
        for rel in d["unrouted_knowledge"][:6]:
            print(f"      · {rel}")
    else:
        print("    ✓ every knowledge entry is trigger-routable (or none yet)")
    print("\n  Named cross-cutting skills:")
    for n in d["cross_cutting"]:
        print(f"    ✓ {n}")
    for n in d["missing_cross"]:
        print(f"    ✗ missing {n}/SKILL.md — `wsx upgrade` adds the portable skeleton")
        fails += 1
    print()
    if fails:
        print(f"reach found {fails} reachability failure(s) (well-formed files can still be unreachable).")
    else:
        print("✓ reach: hubs load, knowledge routes, close-out/plan-ahead/self-improve present.")
        if not d["emitted"]:
            print("  (Layer-0 adapters appear after `wsx emit all`.)")
    return fails
