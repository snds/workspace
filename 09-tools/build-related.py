#!/usr/bin/env python3
"""
build-related.py — generate reciprocal `## Related` blocks from the skill graph.

The frontmatter is the single source of truth for the graph (`hub`, `prerequisites`,
`governed_by`, `tier`). This tool derives the human/Obsidian-facing `## Related` block
in each SKILL.md from that graph, so the navigational cross-links are always reciprocal
by construction and never drift from the frontmatter.

Structural relations are GENERATED (foundation/hub/spoke/applies-in/governed-by/governs);
hand-authored `peer ↔` lines and all prose above `## Related` are PRESERVED.

Reads `02-skills/skills.registry.json` (run build-registry.py first). Stdlib-only.

Usage:
  python3 09-tools/build-related.py            # rewrite Related blocks
  python3 09-tools/build-related.py --check    # CI: fail if any block is stale
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SK = ROOT / "02-skills"
REG = SK / "skills.registry.json"


def wl(name):
    return f"[[{name}]]"


def build_blocks(reg):
    skills = reg["skills"]
    tier = {n: s.get("tier") for n, s in skills.items()}

    # inverse maps
    spokes_of = {}          # hub -> [spokes]
    appliers_of = {}        # foundation -> [skills that prereq it]
    governed_of = {}        # governor -> [skills that name it in governed_by]
    for n, s in skills.items():
        h = s.get("hub")
        if h and h in skills and h != n:
            spokes_of.setdefault(h, []).append(n)
        for p in s.get("prerequisites") or []:
            if p in skills and tier.get(p) == "foundation":
                appliers_of.setdefault(p, []).append(n)
        for g in s.get("governed_by") or []:
            if g in skills:
                governed_of.setdefault(g, []).append(n)

    blocks = {}
    for n, s in skills.items():
        lines = []
        # foundation → (prerequisites that are foundations, excluding own hub)
        founds = [p for p in (s.get("prerequisites") or [])
                  if p in skills and tier.get(p) == "foundation"]
        if founds:
            lines.append("- foundation → " + " · ".join(wl(f) for f in sorted(set(founds))))
        # hub → (the hub field)
        h = s.get("hub")
        if h and h in skills:
            lines.append(f"- hub → {wl(h)}")
        # spoke → (if this is a hub/foundation with members)
        if n in spokes_of:
            lines.append("- spoke → " + " · ".join(wl(x) for x in sorted(spokes_of[n])))
        # applies-in ← (if this is a foundation)
        if n in appliers_of:
            lines.append("- applies-in ← " + " · ".join(wl(x) for x in sorted(appliers_of[n])))
        # governed-by →
        gb = [g for g in (s.get("governed_by") or []) if g in skills]
        if gb:
            lines.append("- governed-by → " + " · ".join(wl(x) for x in sorted(set(gb))))
        # governs → (if others name this in governed_by)
        if n in governed_of:
            lines.append("- governs → " + " · ".join(wl(x) for x in sorted(governed_of[n])))
        blocks[n] = lines
    return blocks


PEER_RE = re.compile(r"^\s*-\s*peer\s*(↔|<->)", re.IGNORECASE)


def apply_block(path, gen_lines):
    """Return new file text with a refreshed `## Related` block, preserving prose + peer lines."""
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    # find existing Related section
    rel_idx = next((i for i, l in enumerate(lines) if re.match(r"^##\s+Related\s*$", l)), None)
    preserved_peers = []
    if rel_idx is not None:
        # collect peer lines from the existing block, drop the rest
        j = rel_idx + 1
        while j < len(lines) and not re.match(r"^##\s+\S", lines[j]):
            if PEER_RE.match(lines[j]):
                preserved_peers.append(lines[j].strip())
            j += 1
        head = lines[:rel_idx]
        tail = lines[j:]  # anything after the Related section (rare)
    else:
        head = lines
        tail = []

    all_lines = gen_lines + preserved_peers
    if not all_lines:
        # no structural or peer links → leave file without a Related block
        new = "\n".join(head).rstrip() + ("\n".join([""] + tail) if tail else "")
        return new.rstrip() + "\n", (rel_idx is not None and not all_lines)

    block = ["## Related"] + all_lines
    body = "\n".join(head).rstrip() + "\n\n" + "\n".join(block) + "\n"
    if tail:
        body += "\n" + "\n".join(tail).strip() + "\n"
    return body, False


def main():
    check = "--check" in sys.argv[1:]
    reg = json.loads(REG.read_text(encoding="utf-8"))
    blocks = build_blocks(reg)
    stale = []
    changed = 0
    for name, s in reg["skills"].items():
        p = ROOT / s["path"]
        if not p.exists():
            continue
        new_text, _ = apply_block(p, blocks.get(name, []))
        if new_text != p.read_text(encoding="utf-8"):
            if check:
                stale.append(name)
            else:
                p.write_text(new_text, encoding="utf-8")
                changed += 1
    if check:
        if stale:
            print(f"✗ {len(stale)} Related blocks are stale — run: python3 09-tools/build-related.py",
                  file=sys.stderr)
            for n in stale[:10]:
                print(f"    {n}", file=sys.stderr)
            return 1
        print("✓ Related blocks up to date")
        return 0
    print(f"✓ refreshed Related blocks — {changed} files updated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
