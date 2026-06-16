#!/usr/bin/env python3
"""
validate-links.py — validate the typed `## Related` wikilink graph across skills.

Checks, on every `02-skills/<name>/SKILL.md` that has a `## Related` section:
  1. DANGLING   — every `[[target]]` resolves to an existing skill (by dir name or alias). [error]
  2. RECIPROCITY — typed relations are mutual per the vocabulary below.                     [error]
  3. FOUNDATION  — design/engineering spokes declare a `foundation →` link.                 [warning]

It only inspects the canonical typed `## Related` format (see
01-shared-references/skill-frontmatter.md). Skills not yet migrated have no such block and are
skipped — so this passes today and tightens automatically as skills are migrated. Stdlib-only.

Reciprocal pairs:
  foundation  <-> applies-in
  hub         <-> spoke
  peer        <-> peer
  governed-by <-> governs
(`encodes-into` is navigational; not reciprocity-checked.)

Usage:
  python3 09-tools/validate-links.py            # report; exit 1 on any error
  python3 09-tools/validate-links.py --strict   # also fail on warnings
"""

import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
WORKSPACE_ROOT = SCRIPT_DIR.parent
SKILLS_DIR = WORKSPACE_ROOT / "02-skills"

WIKILINK = re.compile(r"\[\[([^\]|]+?)(?:\|[^\]]+)?\]\]")
RELATION = re.compile(r"^\s*-\s*([a-z-]+)\s*(?:→|->|←|<-|↔|<->)\s*(.+)$")
RECIPROCAL = {
    "foundation": "applies-in",
    "applies-in": "foundation",
    "hub": "spoke",
    "spoke": "hub",
    "peer": "peer",
    "governed-by": "governs",
    "governs": "governed-by",
}
DESIGN_ENG_PREFIXES = ("uid-", "gd-", "ux-", "fe-", "be-", "type-", "motion-",
                       "infod-", "ia-", "3d-")


def aliases_for(skill_dir, text):
    """A skill is addressable by its dir name and any frontmatter aliases."""
    names = {skill_dir.name}
    m = re.search(r"^aliases:\s*\[(.*?)\]", text, re.MULTILINE)
    if m:
        names.update(a.strip().strip("\"'") for a in m.group(1).split(",") if a.strip())
    return names


def related_block(text):
    """Return the lines of the `## Related` section, or [] if absent."""
    lines = text.splitlines()
    out, capturing = [], False
    for ln in lines:
        if re.match(r"^##\s+Related\s*$", ln):
            capturing = True
            continue
        if capturing and re.match(r"^##\s+\S", ln):
            break
        if capturing:
            out.append(ln)
    return out


def parse_relations(block_lines):
    """Yield (relation, target) for each typed wikilink in a Related block."""
    for ln in block_lines:
        m = RELATION.match(ln)
        if not m:
            continue
        rel = m.group(1)
        for target in WIKILINK.findall(m.group(2)):
            yield rel, target.strip()


def main():
    strict = "--strict" in sys.argv[1:]
    errors, warnings = [], []

    skills = {}          # name -> {"aliases": set, "rels": [(rel, target)]}
    alias_to_name = {}
    for skill_md in sorted(SKILLS_DIR.glob("*/SKILL.md")):
        text = skill_md.read_text(encoding="utf-8", errors="replace")
        names = aliases_for(skill_md.parent, text)
        rels = list(parse_relations(related_block(text)))
        skills[skill_md.parent.name] = {"aliases": names, "rels": rels, "dir": skill_md.parent.name}
        for a in names:
            alias_to_name[a] = skill_md.parent.name

    # 1 + 2: dangling + reciprocity
    for name, rec in skills.items():
        for rel, target in rec["rels"]:
            tgt_name = alias_to_name.get(target)
            if tgt_name is None:
                errors.append(f"{name}: `{rel} → [[{target}]]` is dangling (no such skill)")
                continue
            inverse = RECIPROCAL.get(rel)
            if inverse:
                back = skills[tgt_name]["rels"]
                if not any(r == inverse and alias_to_name.get(t) == name for r, t in back):
                    errors.append(
                        f"{name}: `{rel} → [[{target}]]` not reciprocated "
                        f"({target} should declare `{inverse} → [[{name}]]`)")

    # 3: design/eng spokes should reach a foundation — directly (`foundation →`) or via their
    #    hub (`hub →`, since hubs carry the foundation prerequisite). Warn only if neither exists.
    for name, rec in skills.items():
        if name.startswith(DESIGN_ENG_PREFIXES) and rec["rels"]:
            rels = {rel for rel, _ in rec["rels"]}
            if "foundation" not in rels and "hub" not in rels:
                warnings.append(f"{name}: design/eng spoke reaches no foundation (no `foundation →` or `hub →`)")

    for w in warnings:
        print(f"  ⚠ {w}", file=sys.stderr)
    for e in errors:
        print(f"  ✗ {e}", file=sys.stderr)

    if errors or (strict and warnings):
        print(f"link validation FAILED — {len(errors)} errors, {len(warnings)} warnings", file=sys.stderr)
        return 1
    print(f"✓ links valid — {len(skills)} skills scanned, {len(warnings)} warnings")
    return 0


if __name__ == "__main__":
    sys.exit(main())
