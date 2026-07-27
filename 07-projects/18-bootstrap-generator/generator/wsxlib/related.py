"""build-related — weave a generated `## Related` block into each skill.

Derives the graph from each skill's OWN `hub` front matter — no hardcoded relationships.
A spoke links to its hub and its sibling spokes; a hub links to its spokes. The block is
delimited by HTML-comment markers, so re-running only ever rewrites its own region and
never touches the hand-authored body (idempotent, safe).

Opt-in: this EDITS skill files, so it is not part of the automatic derived-layer rebuild.
Run it via `09-tools/build-related.py` when you want the cross-links refreshed.
"""
from __future__ import annotations

import re
from pathlib import Path

from . import core, layout

_START = "<!-- wsx:related:start -->"
_END = "<!-- wsx:related:end -->"
_BLOCK = re.compile(re.escape(_START) + r".*?" + re.escape(_END), re.DOTALL)


def _rows(root: Path) -> list:
    rows = []
    for name, sk in core.iter_skills(root):
        fm, _ = core.parse_frontmatter(sk)
        rows.append({"name": name, "path": sk,
                     "hub": str(fm.get("hub", "") or name),
                     "kind": fm.get("kind", "spoke")})
    return rows


def _link(name: str) -> str:
    """A PATH-based markdown link to a sibling skill, relative to the current skill's dir.

    Every skill file is `SKILL.md`, so a `[[name]]` wikilink is ambiguous and does NOT
    resolve in Obsidian (there is no `name.md`). A relative path link both resolves AND
    draws the graph edge — the same reason the MOC layer uses path links for skills."""
    return f"[{name}](../{name}/SKILL.md)"


def _related_block(row: dict, rows: list) -> str:
    hub = row["hub"]
    members = [r for r in rows if r["hub"] == hub and r["name"] != row["name"]]
    lines = [_START, "## Related", ""]
    if row["kind"] == "hub":
        spokes = [r for r in members if r["kind"] != "hub"]
        if spokes:
            lines.append("Spokes in this hub:")
            for s in sorted(spokes, key=lambda r: r["name"]):
                lines.append(f"- {_link(s['name'])}")
        else:
            lines.append("_(no spokes yet under this hub.)_")
    else:
        hub_row = next((r for r in rows if r["name"] == hub and r["kind"] == "hub"), None)
        if hub_row:
            lines.append(f"Hub: {_link(hub)}")
        sibs = [r for r in members if r["kind"] != "hub"]
        if sibs:
            lines.append("")
            lines.append("Sibling spokes:")
            for s in sorted(sibs, key=lambda r: r["name"]):
                lines.append(f"- {_link(s['name'])}")
    lines.append(_END)
    return "\n".join(lines)


def build(root: Path) -> list:
    """Refresh the `## Related` block in every skill. Returns the files changed."""
    rows = _rows(root)
    changed = []
    for row in rows:
        sk = row["path"]
        text = sk.read_text(encoding="utf-8")
        block = _related_block(row, rows)
        if _BLOCK.search(text):
            new = _BLOCK.sub(lambda _m: block, text)
        else:
            new = text.rstrip() + "\n\n" + block + "\n"
        if new != text:
            sk.write_text(new, encoding="utf-8")
            changed.append(sk.relative_to(root))
    return changed


def run(root: Path) -> int:
    changed = build(root)
    lay = layout.of(root)
    n = sum(1 for _ in core.iter_skills(root))
    if not n:
        print("build-related: no skills yet — nothing to link.")
        return 0
    print(f"build-related: refreshed `## Related` in {len(changed)} of {n} skill(s) "
          f"under {lay.name('skills')}/.")
    for c in changed:
        print(f"  ~ {c}")
    return 0
