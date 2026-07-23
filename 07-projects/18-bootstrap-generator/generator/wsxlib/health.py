"""`wsx health` — graph hygiene for the vault (the input-time twin of `wsx lint`).

`lint` validates skills + manifest. `health` looks at the vault AS A GRAPH and reports
the rot that accumulates over time:

  * orphan nodes      — notes nothing links to (unreachable; the graph's dead ends)
  * stale claims      — notes tagged `#stale`, or `as of YYYY-MM` dates past a horizon
  * dangling edges    — `relations:` typed edges pointing at notes that don't exist

Advisory by design: orphans and aging notes are surfaced but don't fail the command.
Dangling typed edges and `#stale` tags are real integrity issues and set the exit code,
so a scheduled run can gate on them. Zero-dependency (stdlib only).
"""
from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path

# Notes that are intentionally not link targets (roots, indexes, templates, boilerplate).
_EXEMPT_NAMES = {"HOME.md", "README.md", "_INDEX.md", "_TEMPLATE.md",
                 "CRITICAL_FACTS.md", "index.md",
                 "AGENTS.md", "CLAUDE.md",  # generated adapters, not vault notes
                 "personal.md"}  # walled — intentionally unlinked when private
_SKIP_DIRS = {".git", ".obsidian", "adapters", ".claude", ".cursor"}

_WIKILINK = re.compile(r"\[\[([^\]|#]+)")
_MDLINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
_ASOF = re.compile(r"as of (\d{4})-(\d{2})", re.IGNORECASE)
_STALE = re.compile(r"(^|\s)#stale(\s|$)")
_STALE_MONTHS = 12  # a dated claim older than this is flagged "aging"


def _iter_notes(root: Path):
    for p in root.rglob("*.md"):
        if any(part in _SKIP_DIRS for part in p.relative_to(root).parts):
            continue
        yield p


def _basename_index(notes: list) -> dict:
    """basename (no ext, lowercased) -> list of note paths (Obsidian resolves by name)."""
    idx: dict[str, list] = {}
    for p in notes:
        idx.setdefault(p.stem.lower(), []).append(p)
    return idx


def _outbound(note: Path, root: Path, by_name: dict) -> set:
    """Resolve every link in `note` to a set of target note paths that exist."""
    try:
        text = note.read_text(encoding="utf-8")
    except OSError:
        return set()
    targets: set = set()
    for m in _WIKILINK.finditer(text):
        name = m.group(1).strip().split("/")[-1].lower()
        for t in by_name.get(name, []):
            targets.add(t)
    for m in _MDLINK.finditer(text):
        href = m.group(1).strip()
        if "://" in href or href.startswith("#") or not href.endswith(".md"):
            continue
        cand = (note.parent / href.split("#")[0]).resolve()
        if cand.exists():
            targets.add(cand)
    targets.discard(note.resolve())  # ignore self-links
    return targets


def _relations_targets(text: str) -> list:
    """Pull `[[x]]` targets out of a `relations:` front-matter block (best-effort)."""
    if not text.startswith("---"):
        return []
    end = text.find("\n---", 3)
    if end == -1:
        return []
    fm = text[3:end]
    m = re.search(r"^relations:\s*(.*?)(?=^\S|\Z)", fm, re.MULTILINE | re.DOTALL)
    if not m:
        return []
    return [t.strip().split("/")[-1].lower() for t in _WIKILINK.findall(m.group(1))]


def health(root: Path) -> int:
    notes = list(_iter_notes(root))
    by_name = _basename_index(notes)
    resolved = {p.resolve(): p for p in notes}

    inbound = {p.resolve(): 0 for p in notes}
    dangling = []  # (note, relation-target-name)
    for p in notes:
        for t in _outbound(p, root, by_name):
            if t in inbound:
                inbound[t] += 1
        try:
            text = p.read_text(encoding="utf-8")
        except OSError:
            continue
        for name in _relations_targets(text):
            if name not in by_name:
                dangling.append((p, name))

    orphans, stale_tagged, aging = [], [], []
    now = datetime.now(timezone.utc)
    for p in notes:
        if p.name in _EXEMPT_NAMES or p.stem.startswith("_"):
            continue
        if inbound.get(p.resolve(), 0) == 0:
            orphans.append(p)
        try:
            text = p.read_text(encoding="utf-8")
        except OSError:
            continue
        if _STALE.search(text):
            stale_tagged.append(p)
        for ym in _ASOF.finditer(text):
            y, mo = int(ym.group(1)), int(ym.group(2))
            months = (now.year - y) * 12 + (now.month - mo)
            if months >= _STALE_MONTHS:
                aging.append((p, f"{y:04d}-{mo:02d}", months))
                break

    def rel(p):
        return str(p.relative_to(root))

    print("wsx health — vault graph hygiene\n")
    # advisories (don't affect exit)
    if orphans:
        print(f"  ⚠ {len(orphans)} orphan note(s) — nothing links to them (add a link, or archive):")
        for p in orphans[:20]:
            print(f"      · {rel(p)}")
        if len(orphans) > 20:
            print(f"      …and {len(orphans) - 20} more")
    else:
        print("  ✓ no orphan notes — every note is reachable.")
    if aging:
        print(f"  ⚠ {len(aging)} aging claim(s) — `as of` date older than {_STALE_MONTHS}mo "
              "(re-verify or mark #stale):")
        for p, when, months in aging[:20]:
            print(f"      · {rel(p)}  (as of {when}, ~{months}mo old)")
    else:
        print("  ✓ no aging dated claims past the horizon.")

    # integrity issues (set the exit code)
    problems = 0
    if stale_tagged:
        problems += len(stale_tagged)
        print(f"  ✗ {len(stale_tagged)} note(s) tagged #stale — re-check or archive:")
        for p in stale_tagged[:20]:
            print(f"      · {rel(p)}")
    if dangling:
        problems += len(dangling)
        print(f"  ✗ {len(dangling)} dangling typed edge(s) — `relations:` points at a missing note:")
        for p, name in dangling[:20]:
            print(f"      · {rel(p)} → [[{name}]] (no such note)")
    if not problems:
        print("  ✓ no #stale tags and no dangling typed edges.")

    print(f"\n{'✓ health clean' if problems == 0 else f'health found {problems} integrity issue(s)'} "
          f"across {len(notes)} note(s).")
    return problems
