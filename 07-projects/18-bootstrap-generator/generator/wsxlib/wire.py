"""`wsx wire` — connect anything in the workspace that isn't wired in yet.

`moc`/`emit` regenerate the KNOWN taxonomy (context, skills, …). But a person can add an
*unanticipated* dir — `10-research/`, `recipes/`, whatever — and its notes become orphans,
unreachable from HOME, maybe even gitignored. `wire` is the discovery-driven pass that finds
those and connects them per a declarative **wiring-intent registry**, to every destination the
dir-kind implies. It generalizes `moc.write_mocs` + `emit` into "find what's loose, wire it."

Safe to run anytime · idempotent (a fully-wired vault → no-op) · runs off the copied-in `.wsx`
CLI, so a workspace self-wires with **no generator present**.

The intent registry (`INTENT`) is the heart: to teach the workspace to wire a new KIND of
directory, add a row — you don't touch the discovery logic.
"""
from __future__ import annotations

from pathlib import Path

from . import core, layout

# Never treated as vault content (generated tooling / vcs / editor state).
_NON_CONTENT = {"adapters", "_archive", ".git", ".claude", ".cursor", ".obsidian",
                ".wsx", "node_modules"}

# dir-kind → the destinations wire must connect it to. Known taxonomy kinds are already
# handled by moc/emit; the load-bearing row is "other" — how an UNANTICIPATED content dir
# gets wired. Add a row to teach wire a new kind; discovery logic stays untouched.
INTENT = {
    #  kind          home?  own _INDEX?  in skills registry?  keep git-trackable?
    "skills":     {"home": True, "index": True, "registry": True, "trackable": True},
    "knowledge":  {"home": True, "index": True, "registry": False, "trackable": True},
    "projects":   {"home": True, "index": True, "registry": False, "trackable": True},
    "context":    {"home": True, "index": False, "registry": False, "trackable": True},
    "frameworks": {"home": True, "index": False, "registry": False, "trackable": True},
    "shared":     {"home": True, "index": False, "registry": False, "trackable": True},
    "preferences":{"home": True, "index": False, "registry": False, "trackable": True},
    "tools":      {"home": True, "index": False, "registry": False, "trackable": True},
    "other":      {"home": True, "index": True, "registry": False, "trackable": True},
}


def _known_dirs(root: Path) -> set:
    """The dir NAMES the taxonomy already owns (numbered + legacy, as present)."""
    lay = layout.of(root)
    names = {lay.name(k) for k in layout.CANONICAL}
    names |= set(layout.LEGACY.values())
    return names


def _md_files(d: Path) -> list:
    return sorted(p for p in d.rglob("*.md")
                  if p.name != "_INDEX.md"
                  and not any(part.startswith(".") for part in p.relative_to(d).parts))


def discover_extras(root: Path) -> list:
    """UNANTICIPATED content dirs: top-level dirs with markdown that the taxonomy doesn't own
    and that aren't generated tooling. These are what `moc`/`emit` would otherwise miss."""
    known = _known_dirs(root)
    out = []
    for d in sorted(root.iterdir()):
        if not d.is_dir() or d.name.startswith(".") or d.name in _NON_CONTENT:
            continue
        if d.name in known:
            continue
        if _md_files(d):
            out.append(d)
    return out


# --------------------------------------------------------------------- checks ---
def _ensure_index(d: Path) -> bool:
    """Give an extra dir an _INDEX.md so its notes are reachable (not orphans). Regenerated
    idempotently from disk. Returns True if it changed."""
    idx = d / "_INDEX.md"
    files = _md_files(d)
    lines = [f"# {d.name} — index", "",
             "_Auto-wired by `wsx wire` so these notes are reachable. Back to [[HOME]]._", ""]
    for p in files:
        rel = p.relative_to(d).as_posix()
        lines.append(f"- [{p.stem}]({rel})")
    new = "\n".join(lines).rstrip() + "\n"
    old = idx.read_text(encoding="utf-8") if idx.exists() else ""
    if new != old:
        idx.write_text(new, encoding="utf-8")
        return True
    return False


def _ensure_trackable(root: Path, d: Path) -> bool:
    """If git would IGNORE this content dir, add a whitelist negation so it's tracked.
    Returns True if .gitignore changed."""
    if not (root / ".git").exists():
        return False
    r = core.git(root, "check-ignore", "-q", d.name, check=False)
    if r.returncode != 0:
        return False  # not ignored — nothing to do
    gi = root / ".gitignore"
    line = f"!{d.name}/"
    text = gi.read_text(encoding="utf-8") if gi.exists() else ""
    if line in text:
        return False
    text = text.rstrip() + f"\n\n# wsx wire: keep this content dir tracked (was gitignored)\n{line}\n"
    gi.write_text(text, encoding="utf-8")
    return True


# ----------------------------------------------------------------------- wire ---
def wire(root: Path) -> int:
    from . import adapter, adapters, moc, skills
    # REFERENCE MODE: on an adapter-mapped foreign vault, wire's job (regenerate the derived
    # layer + re-emit adapters) would overwrite hand-authored content. Do only the ADDITIVE,
    # non-colliding part — give any unanticipated dir an _INDEX so its notes are reachable —
    # and skip HOME/index/adapter regeneration.
    adapted = adapter.is_adapted(root)
    lay = layout.of(root)
    changed = {"indexed": [], "trackable": [], "extras": []}
    if adapted:
        extras = discover_extras(root)
        for d in extras:
            if _ensure_index(d):
                changed["indexed"].append(f"{d.name}/_INDEX.md")
            if _ensure_trackable(root, d):
                changed["trackable"].append(d.name)
        print(f"wsx wire — reference mode (adapter-mapped vault): additive wiring only\n")
        if extras:
            print(f"  indexed {len(changed['indexed'])} unanticipated dir(s); whitelisted "
                  f"{len(changed['trackable'])}. Your HOME/adapters are left untouched.")
        else:
            print("  nothing loose. (Your HOME, indexes, and adapters are hand-authored — wsx")
            print("  won't regenerate them in reference mode.)")
        return 0

    # 1. discovery — unanticipated content dirs → wire per the "other" intent.
    extras = discover_extras(root)
    intent = INTENT["other"]
    for d in extras:
        changed["extras"].append(d.name)
        if intent["index"] and _ensure_index(d):
            changed["indexed"].append(f"{d.name}/_INDEX.md")
        if intent["trackable"] and _ensure_trackable(root, d):
            changed["trackable"].append(d.name)

    # 2. un-indexed skills — folders on disk not in the manifest → reindex catches them.
    man = core.load_manifest(root)
    recorded = set(man.get("skills", {}) or {})
    on_disk = {name for name, _ in core.iter_skills(root)}
    reindexed = bool(on_disk - recorded) or bool(recorded - on_disk)
    if reindexed:
        skills.reindex(root)

    # 3. regenerate the whole derived layer (HOME now includes discovered extras via moc) +
    #    re-emit every adapter/hook so nothing references stale structure.
    moc.write_mocs(root)
    prof = core.load_profile(root)
    adapters.emit(root, "all", prof, core.load_manifest(root))

    # report
    print(f"wsx wire — connect everything loose in {root}\n")
    if extras:
        print(f"  discovered {len(extras)} unanticipated content dir(s): {', '.join(changed['extras'])}")
        for i in changed["indexed"]:
            print(f"    ~ indexed {i} (notes now reachable)")
        for t in changed["trackable"]:
            print(f"    ~ whitelisted {t}/ in .gitignore (was gitignored → now tracked)")
        print("    ~ linked from HOME ('Other areas') + re-emitted adapters/hooks")
    else:
        print("  no unanticipated dirs — the taxonomy owns everything.")
    if reindexed:
        print("  ~ reindexed skills (found folders not in the manifest)")
    print("\n  ✓ derived layer regenerated (HOME · indexes · registry · adapters · hooks · tools).")
    any_change = bool(extras or reindexed or changed["indexed"] or changed["trackable"])
    print("  re-run is a no-op." if not any_change
          else "  everything is now wired; a re-run will be a no-op.")
    return 0
