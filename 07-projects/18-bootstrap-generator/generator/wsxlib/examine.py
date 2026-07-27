"""`wsx examine` — read an existing workspace and report what augmentation it needs.

**Read-only.** It changes nothing. Its job is to let a person who ALREADY has a
workspace be *augmented additively* instead of re-interviewed from scratch. It answers
three questions the brain needs before it opens its mouth:

  1. Which interview movements (M0–M5) are already answered in profile.yaml — so we ask
     ONLY the pertinent ones and never re-ask what's already there.
  2. What canonical scaffold is missing — the non-destructive fix is `wsx upgrade`.
  3. Where connections are broken (orphans, dangling typed edges) — so augmentation can
     repair them rather than pile new content on a frayed graph.

The apply step is never done here: it's `wsx upgrade` (add missing scaffold, regenerate
the derived layer, run migrations — all non-destructive) plus targeted `wsx profile set`
for the newly-answered questions. Everything pre-existing is preserved.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from . import core, health, scaffold

# Each interview movement → the profile fields it populates. `optional` fields don't
# count against "pertinent" (personal interests and banned-list may be deliberately empty).
# kind: scalar | list | map.
MOVEMENTS = [
    ("M0", "Surfaces & infrastructure", [
        ("surfaces.primary", "scalar", False), ("surfaces.agents", "list", False),
        ("surfaces.machines", "list", True), ("models.tier", "scalar", True),
        ("context", "scalar", False)]),
    ("M1", "Work context", [
        ("contexts.work.role", "scalar", False), ("contexts.work.summary", "scalar", True)]),
    ("M2", "Professional craft", [
        ("contexts.professional.crafts", "list", False), ("expertise", "map", True)]),
    ("M3", "Personal context (walled)", [
        ("contexts.personal.interests", "list", True)]),
    ("M4", "Operating preferences", [
        ("preferences.tone", "scalar", False), ("preferences.audience", "scalar", True),
        ("preferences.verbosity", "scalar", True), ("preferences.banned", "list", True)]),
    ("M5", "Lifecycle & privacy", [
        ("lifecycle.separation", "scalar", False), ("lifecycle.automation", "scalar", True),
        ("privacy.personal_local_only", "scalar", True)]),
]


def _get(prof: dict, dotted: str):
    cur = prof
    for p in dotted.split("."):
        if isinstance(cur, dict) and p in cur:
            cur = cur[p]
        else:
            return None
    return cur


def _filled(val, kind: str) -> bool:
    if val is None:
        return False
    if kind == "scalar":
        return str(val).strip() != ""
    if kind in ("list", "map"):
        return len(val) > 0 if hasattr(val, "__len__") else bool(val)
    return bool(val)


def _movement_status(prof: dict) -> list:
    out = []
    for mid, label, fields in MOVEMENTS:
        req = [f for f in fields if not f[2]]
        req_filled = [f for f in req if _filled(_get(prof, f[0]), f[1])]
        missing_req = [f[0] for f in req if f not in req_filled]
        opt_missing = [f[0] for f in fields if f[2] and not _filled(_get(prof, f[0]), f[1])]
        if not req:
            status = "complete" if any(_filled(_get(prof, f[0]), f[1]) for f in fields) else "optional-empty"
        elif not missing_req:
            status = "complete"
        elif len(req_filled) == 0:
            status = "unanswered"
        else:
            status = "partial"
        out.append({"id": mid, "label": label, "status": status,
                    "missing_required": missing_req, "missing_optional": opt_missing,
                    "pertinent": status in ("unanswered", "partial")})
    return out


def _missing_scaffold(root: Path) -> list:
    # dict.fromkeys de-dupes while preserving order (some extras also live in TEMPLATES).
    expected = dict.fromkeys(list(scaffold.TEMPLATES.keys()) + [
        "HOME.md", "skills/_INDEX.md", "projects/_INDEX.md", "knowledge/README.md"])
    return [rel for rel in expected if not (root / rel).exists()]


def _inventory(root: Path) -> dict:
    hubs, spokes = 0, 0
    for _name, sk in core.iter_skills(root):
        fm, _ = core.parse_frontmatter(sk)
        if fm.get("kind") == "hub":
            hubs += 1
        else:
            spokes += 1
    pdir = root / "projects"
    projects = [d.name for d in pdir.iterdir()
                if pdir.is_dir() and d.is_dir() and not d.name.startswith((".", "_"))] if pdir.is_dir() else []
    return {"hubs": hubs, "spokes": spokes, "projects": projects}


def _connections(root: Path) -> dict:
    """Reuse health's graph helpers quietly (no printing) for a repair-oriented summary."""
    notes = list(health._iter_notes(root))
    by_name = health._basename_index(notes)
    inbound = {p.resolve(): 0 for p in notes}
    dangling = []
    for p in notes:
        for t in health._outbound(p, root, by_name):
            if t in inbound:
                inbound[t] += 1
        try:
            text = p.read_text(encoding="utf-8")
        except OSError:
            continue
        for name in health._relations_targets(text):
            if name not in by_name:
                dangling.append(f"{p.relative_to(root)} → [[{name}]]")
    orphans = [str(p.relative_to(root)) for p in notes
               if p.name not in health._EXEMPT_NAMES and not p.stem.startswith("_")
               and inbound.get(p.resolve(), 0) == 0]
    return {"orphans": orphans, "dangling": dangling, "notes": len(notes)}


# ------------------------------------------------------------ foreign vaults ---
# The wsx concepts, and the folder names a FOREIGN (non-wsx) workspace tends to use for
# them — including numbered-prefix variants (this project grew out of exactly such a
# workspace: 06-context, 01-frameworks, 03-skills, 08-knowledge, 07-projects).
_CONCEPTS = {
    "context": "who you are, projects, session log, decisions",
    "frameworks": "operating principles above any single skill",
    "skills": "reusable expertise (hubs + spokes)",
    "knowledge": "durable domain insight that outlives a session",
    "projects": "per-project documentation & context",
    "preferences": "how you want work approached and judged",
}


def _strip_num(name: str) -> str:
    return re.sub(r"^\d+[-_]?", "", name).lower()


def _find_concept_dir(root: Path, concept: str) -> Path | None:
    """Find a foreign dir that plays the role of `concept` (by name, numbered or not)."""
    try:
        for d in sorted(root.iterdir()):
            if d.is_dir() and (_strip_num(d.name) == concept or concept in d.name.lower()):
                return d
    except OSError:
        return None
    return None


def _looks_like_workspace(root: Path) -> bool:
    """A directory worth examining as a foreign workspace: an Obsidian vault, an AI-wired
    repo, or just a structured pile of markdown with some concept folders."""
    if (root / ".obsidian").is_dir():
        return True
    if any((root / f).exists() for f in ("AGENTS.md", "CLAUDE.md", "README.md")):
        if any(_find_concept_dir(root, c) for c in _CONCEPTS):
            return True
    return sum(1 for c in _CONCEPTS if _find_concept_dir(root, c)) >= 3


def _md_count(d: Path) -> int:
    try:
        return sum(1 for _ in d.rglob("*.md"))
    except OSError:
        return 0


def examine_foreign(root: Path, as_json: bool = False) -> int:
    """Read-only coverage map of a NON-wsx workspace. Never restructures — a mature
    foreign vault (like the one this generator grew out of) usually EXCEEDS the wsx
    model, and imposing the wsx scaffold on it would be a downgrade, not an upgrade."""
    present, missing = {}, []
    for concept, what in _CONCEPTS.items():
        d = _find_concept_dir(root, concept)
        if d:
            present[concept] = {"dir": d.name, "md_files": _md_count(d), "what": what}
        else:
            missing.append(concept)

    ai_wired = [f for f in ("AGENTS.md", "CLAUDE.md") if (root / f).exists()]
    cursor = (root / ".cursor").is_dir()
    obsidian = (root / ".obsidian").is_dir()
    is_git = (root / ".git").exists()
    total_md = _md_count(root)
    coverage = len(present)

    report = {"mode": "foreign", "path": str(root), "coverage": f"{coverage}/{len(_CONCEPTS)}",
              "present": present, "missing": missing, "ai_wired": ai_wired,
              "cursor": cursor, "obsidian": obsidian, "git": is_git, "total_md": total_md}
    if as_json:
        print(json.dumps(report, indent=2))
        return 0

    print(f"wsx examine — FOREIGN workspace readout for {root}\n")
    print("  This is not a wsx-generated workspace, so wsx examines it as a peer: it maps your")
    print("  layout onto the wsx concepts and reports coverage. It changes NOTHING, and it will")
    print("  not impose the wsx scaffold — a mature workspace like this usually exceeds it.\n")

    print(f"Concept coverage: {coverage}/{len(_CONCEPTS)}")
    for concept, what in _CONCEPTS.items():
        if concept in present:
            p = present[concept]
            print(f"  ✓ {concept:12} → {p['dir']}/  ({p['md_files']} md)  — {what}")
        else:
            print(f"  ✗ {concept:12} → (none found)  — {what}")

    print("\nAI wiring:")
    print(f"  {'✓' if ai_wired else '·'} instruction files: {', '.join(ai_wired) or '(none)'}")
    print(f"  {'✓' if cursor else '·'} .cursor/   {'✓' if obsidian else '·'} .obsidian (vault)   "
          f"{'✓' if is_git else '·'} git repo")
    print(f"  {total_md} markdown files total.")

    print("\nVerdict:")
    if coverage == len(_CONCEPTS):
        print("  This workspace already implements every wsx concept — and, being hand-built,")
        print("  very likely exceeds the wsx scaffold (richer frameworks, a real skill network,")
        print("  a memory system). wsx has nothing structural to add; running `wsx upgrade` here")
        print("  would try to impose a SIMPLER layout, which would be a downgrade. Don't.")
        print("  If you want wsx tooling on it, the right path is a thin adapter that maps these")
        print("  existing folders to the wsx concepts — a future capability, not today's upgrade.")
    elif coverage >= 3:
        print(f"  Partial match ({coverage}/{len(_CONCEPTS)}). Missing concepts: {', '.join(missing)}.")
        print("  These could be adopted as NEW folders without touching what exists — but confirm")
        print("  first; a foreign workspace may cover them under a different name wsx didn't detect.")
    else:
        print("  Little overlap with the wsx model. This may be a plain notes folder rather than a")
        print("  structured workspace; consider `wsx init` for a fresh vault and migrate content in.")
    return 0


def run(start: str, as_json: bool = False) -> int:
    """Dispatch: a wsx workspace gets the profile/scaffold readout; a foreign but
    workspace-like directory gets the concept-coverage map; anything else is refused."""
    s = Path(start or ".").resolve()
    root = core.find_workspace_root(str(s))
    if root:
        return examine(root, as_json)
    if _looks_like_workspace(s):
        return examine_foreign(s, as_json)
    raise SystemExit(f"error: {s} is neither a wsx workspace nor a recognizable "
                     "workspace layout. Point me at one, or `wsx init` a new one.")


def examine(root: Path, as_json: bool = False) -> int:
    man = core.load_manifest(root)
    prof = core.load_profile(root)
    is_wsx = man.get("generator") == "wsx"
    movements = _movement_status(prof)
    missing = _missing_scaffold(root)
    inv = _inventory(root)
    conn = _connections(root)
    pertinent = [m["id"] for m in movements if m["pertinent"]]

    report = {"is_wsx_workspace": is_wsx, "name": prof.get("identity", {}).get("name", ""),
              "movements": movements, "pertinent_movements": pertinent,
              "missing_scaffold": missing, "inventory": inv, "connections": conn}

    if as_json:
        print(json.dumps(report, indent=2))
        return 0

    print(f"wsx examine — augmentation readout for {root}\n")
    if not is_wsx:
        print("  ⚠ this doesn't look like a wsx-generated workspace (no generator marker in")
        print("    manifest.json). You can still `wsx upgrade` to bring it up to the scaffold,")
        print("    or `wsx init` a fresh one and migrate content in.\n")

    print("Interview coverage (ask only what's still pertinent):")
    for m in movements:
        mark = {"complete": "✓", "partial": "◐", "unanswered": "✗",
                "optional-empty": "·"}[m["status"]]
        extra = f"  missing: {', '.join(m['missing_required'])}" if m["missing_required"] else ""
        print(f"  {mark} {m['id']} {m['label']} — {m['status']}{extra}")
    if pertinent:
        print(f"\n  → Re-run the interview for ONLY: {', '.join(pertinent)}. Everything else is set.")
    else:
        print("\n  → Profile is complete — no interview needed; just augment structure/skills.")

    print(f"\nInventory: {inv['hubs']} hub(s), {inv['spokes']} spoke(s), "
          f"{len(inv['projects'])} project(s). (Don't re-propose what already exists.)")

    print("\nStructure:")
    if missing:
        print(f"  ✗ {len(missing)} missing scaffold file(s) — `wsx upgrade` adds them (non-destructive):")
        for rel in missing[:12]:
            print(f"      · {rel}")
        if len(missing) > 12:
            print(f"      …and {len(missing) - 12} more")
    else:
        print("  ✓ scaffold complete.")

    print("\nConnections (repair before piling on new content):")
    if conn["dangling"]:
        print(f"  ✗ {len(conn['dangling'])} dangling typed edge(s) — `wsx health` details them.")
    if conn["orphans"]:
        print(f"  ⚠ {len(conn['orphans'])} orphan note(s) — link or archive (`wsx health`).")
    if not conn["dangling"] and not conn["orphans"]:
        print("  ✓ graph is connected.")

    print("\nNext: augment ADDITIVELY — `wsx upgrade` (adds missing scaffold + repairs the derived")
    print("layer, non-destructively), then `wsx profile set …` for the pertinent movements above,")
    print("then `wsx emit all`. Nothing pre-existing is removed.")
    return 0
