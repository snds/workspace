#!/usr/bin/env python3
"""
validate-capabilities.py — enforce the capability-dependency contract.

The canonical capability data lives in a fenced ```json block inside
`02-shared-references/capability-registry.md`. Skills declare `requires: [<id>]`
in frontmatter (carried into `03-skills/skills.registry.json` by build-registry.py).

This gate checks, with no third-party deps:
  - each capability entry is well-formed (kind/detect/install/fallback/powers);
  - `fallback` is degrade|block|route; a `route` names a real `fallback_skill`;
  - every `powers` target is a real skill;
  - every skill `requires:` id resolves to a capability;
  - reciprocity: skill requires C  <=>  C.powers lists skill;
  - every capability id is documented in prose (outside the JSON block).

Usage:
  python3 09-tools/validate-capabilities.py            # report
  python3 09-tools/validate-capabilities.py --check     # same; nonzero exit on any error
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REG_MD = ROOT / "02-shared-references" / "capability-registry.md"
SKILLS_REG = ROOT / "03-skills" / "skills.registry.json"

VALID_KINDS = {"mcp", "cli", "env"}
VALID_FALLBACKS = {"degrade", "block", "route"}
REQUIRED_FIELDS = {"kind", "provides", "detect", "install", "fallback", "powers"}

JSON_BLOCK = re.compile(r"```json\s*\n(.*?)\n```", re.DOTALL)


def load_capabilities():
    text = REG_MD.read_text(encoding="utf-8")
    m = JSON_BLOCK.search(text)
    if not m:
        raise SystemExit(f"✗ no ```json block found in {REG_MD}")
    data = json.loads(m.group(1))
    prose = text[: m.start()] + text[m.end():]
    return data.get("capabilities", {}), prose


def main():
    errors, warnings = [], []
    caps, prose = load_capabilities()
    reg = json.loads(SKILLS_REG.read_text(encoding="utf-8"))
    skills = reg["skills"]

    # 1. capability shape
    for cid, c in caps.items():
        missing = REQUIRED_FIELDS - set(c)
        if missing:
            errors.append(f"capability '{cid}' missing field(s): {', '.join(sorted(missing))}")
            continue
        if c["kind"] not in VALID_KINDS:
            errors.append(f"capability '{cid}': kind '{c['kind']}' not in {sorted(VALID_KINDS)}")
        if c["fallback"] not in VALID_FALLBACKS:
            errors.append(f"capability '{cid}': fallback '{c['fallback']}' not in {sorted(VALID_FALLBACKS)}")
        if c["fallback"] == "route":
            fs = c.get("fallback_skill")
            if not fs:
                errors.append(f"capability '{cid}': fallback=route but no fallback_skill")
            elif fs not in skills:
                errors.append(f"capability '{cid}': fallback_skill '{fs}' is not a known skill")
        for p in c.get("powers", []):
            if p not in skills:
                errors.append(f"capability '{cid}': powers '{p}' is not a known skill")
        if cid not in prose:
            warnings.append(f"capability '{cid}' is not documented in prose (only in the JSON block)")

    # 2. skill requires -> capability, with reciprocity
    for name, s in skills.items():
        for rid in s.get("requires", []) or []:
            if rid not in caps:
                errors.append(f"skill '{name}' requires '{rid}', which is not in the capability registry")
            elif name not in caps[rid].get("powers", []):
                errors.append(
                    f"reciprocity: skill '{name}' requires '{rid}' but '{rid}'.powers does not list '{name}'"
                )

    # 3. reciprocity the other way: powers -> that skill must declare requires
    for cid, c in caps.items():
        for p in c.get("powers", []):
            if p in skills and cid not in (skills[p].get("requires", []) or []):
                errors.append(
                    f"reciprocity: '{cid}'.powers lists '{p}' but skill '{p}' does not require '{cid}'"
                )

    for w in warnings:
        print(f"  ⚠ {w}", file=sys.stderr)
    if errors:
        print(f"✗ capability contract: {len(errors)} error(s)", file=sys.stderr)
        for e in errors:
            print(f"    {e}", file=sys.stderr)
        return 1
    print(f"✓ capabilities ok — {len(caps)} capabilities, "
          f"{sum(len(s.get('requires', []) or []) for s in skills.values())} skill requirement(s) wired")
    return 0


if __name__ == "__main__":
    sys.exit(main())
