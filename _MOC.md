---
tags: [moc]
title: Workspace Map of Content
---

# 🗺️ Workspace — Map of Content

The layered index of the whole workspace. Start here in Obsidian. Machine entry point for agents is
[[llms]] → [[AGENTS]]; the routing map for *where things go* is [[workspace-ontology]].

## Layers (the skill graph)

Skills load **foundation → hub → spoke**, with cross-cutting lenses applied sideways. The lists below
are auto-generated from each skill's `tier` frontmatter (single source of truth = the frontmatter graph).

### Foundations — load first
> Context-free first principles per domain. A specialty skill always loads its foundation before itself.

```dataview
LIST rows.file.link
FROM "02-skills"
WHERE tier = "foundation"
GROUP BY domain
SORT domain ASC
```

### Discipline hubs
```dataview
LIST rows.file.link
FROM "02-skills"
WHERE tier = "hub"
GROUP BY domain
SORT domain ASC
```

### Cross-cutting lenses (accessibility, visual QA)
> Applied sideways/after at every layer — they `govern` output, they aren't ancestors.

```dataview
LIST rows.file.link
FROM "02-skills"
WHERE tier = "cross-cutting"
SORT file.name ASC
```

### Spokes missing a foundation path (migration backlog)
```dataview
LIST file.link
FROM "02-skills"
WHERE tier = "spoke" AND !hub
SORT file.name ASC
```

## Domain entry points
- **Design** → [[design-foundations]] → [[lead-ui-designer]] · [[lead-graphic-designer]] · [[lead-ux-designer]] · [[lead-type-designer]] · [[lead-motion-designer]] · [[lead-information-designer]] · [[lead-3d-designer]]
- **Engineering** → [[eng-foundations]] → [[lead-frontend-engineer]] · [[lead-backend-engineer]] · [[lead-devops-engineer]]
- **Product** → [[product-foundations]] → [[lead-product-manager]]
- **Data** → [[data-foundations]] → [[lead-data-scientist]]
- **Game** → [[game-foundations]] → [[lead-game-designer]] · [[lead-game-developer]] · [[lead-art-director]]

## Other maps
- [[_HOME]] — daily front door · [[_SKILLS]] — full skill list · [[_FRAMEWORKS]] — operating frameworks
- [[_CONTEXT]] — role/project/session/memory · [[_PROJECTS]] — projects · [[_CHEATSHEET]] — quick reference

## The system layer
- **Contract:** [[AGENTS]] (universal) · adapters [[CLAUDE]] · [[CURSOR]] · [[PERPLEXITY]]
- **Governance:** [[08-workspace-contribution-framework]] (how/when/where/what/why to edit) · [[workspace-ontology]] (routing map)
- **Generated graph:** `02-skills/skills.registry.json` ← `09-tools/build-registry.py` + `build-related.py`
- **Memory:** [[MEMORY]] · **Archive:** `_archive/ARCHIVE-LOG.md`
