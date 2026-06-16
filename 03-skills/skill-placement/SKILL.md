---
name: skill-placement
description: >
  Skill authoring + placement workflow. Trigger automatically at the start of any
  skill-creation task, before generating skill content, and when Sean says "create
  a skill", "generate skill", "make a skill", or similar. Establishes where the
  skill goes, the frontmatter v2 contract, cross-link reciprocity, and registry
  regeneration — so every new skill is wired into the graph correctly.
aliases: [skill-placement]
triggers: [create a skill, generate skill, make a skill, new skill, skill placement]
tier: cross-cutting
domain: workspace
surfaces: ["*"]
spec_version: "2.0"
---

# Skill Placement Workflow

Every skill created with Sean follows this workflow. **The git checkout is the source of truth** —
skills live in `03-skills/<name>/SKILL.md` and are wired into the graph via frontmatter. No Google
Drive, no `/mnt/skills` copy, no manual sync. See [[skill-frontmatter]] and
[[08-workspace-contribution-framework]] (the `03-skills/` layer rules).

## Before generating any skill content

1. **Decide placement.** Is this a new capability, or should an existing skill be extended? Extend when
   the need is within an existing skill's domain (don't duplicate). New skill only for a new concern.
2. **Decide tier + edges.** `foundation` (a domain's shared principle, only if 3+ hubs re-derive it) /
   `hub` (a discipline lead) / `spoke` (a specialty, under a `hub:`) / `cross-cutting` (a lens applied
   sideways). A spoke names its `hub` in `prerequisites`; a hub names its `foundation`.
3. **Author from the template** `00-bootstrap/templates/skill.md`: frontmatter v2
   (`name` = dir name · `aliases` · `triggers` · `tier` · `domain` · `hub`/`prerequisites` · `related`
   · `governed_by` · `surfaces` · `spec_version`) and a typed `## Related` block.

## After authoring

4. **Cross-link reciprocally.** Every `## Related` edge must be mirrored on the other skill
   (`foundation→` ⟺ `applies-in←`; `peer↔` both ways).
5. **Regenerate the graph:** `python3 09-tools/build-registry.py` (fails on cycles/dangling).
6. **Validate:** `python3 09-tools/validate-links.py` — no dangling/non-reciprocal links.
7. **Commit** the new `SKILL.md` + the regenerated `03-skills/skills.registry.json` together.

## Hard rules
- Never rename a `SKILL.md` file/dir later (breaks loader paths + wikilinks) — add `aliases`.
- Never hand-edit `skills.registry.json` — it is generated.

## Related
- peer ↔ [[workspace-bootstrap]]
