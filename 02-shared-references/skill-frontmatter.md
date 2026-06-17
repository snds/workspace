---
title: Skill Frontmatter Spec (v2)
spec_version: "2.1"
status: canonical
---

# Skill Frontmatter Spec — v2

> **v2.1** adds the optional `requires:` field (external-tool capability dependencies). Backward
> compatible — skills without it are unaffected.

Every `03-skills/<name>/SKILL.md` opens with a YAML frontmatter block. These keys are
the **single source of truth** for the skill graph: `09-tools/build-registry.py` reads
them to generate `03-skills/skills.registry.json`, and any agent reads them (directly or via the
registry) to decide what to load and in what order. See [[workspace-ontology]] for the
vocabulary and [[AGENTS]] → "Skill loading precedence" for the algorithm.

v2 is a **backward-compatible superset** of v1: `name` + `description` still suffice. The
added keys are optional but make the graph explicit instead of buried in prose. A skill
without them still loads (the agent falls back to matching `description`) — it just isn't
ordered or cross-linked until migrated.

## Fields

| Key | Type | Required | Meaning |
|---|---|---|---|
| `name` | string | always | Identity. **Must equal the directory name.** Kebab-case. |
| `description` | string | always | Routing prose. The zero-cost matching surface (already in the system prompt). Keep the trigger language rich. |
| `aliases` | list | recommended | Obsidian wikilink targets. Set to `[<dir-name>]` so `[[name]]` resolves despite every file being `SKILL.md`. |
| `triggers` | list | hubs + foundations | Lowercased keyword/phrase list — the deterministic half of `description`. Drives machine routing. |
| `tier` | enum | migrated skills | `foundation` \| `hub` \| `spoke` \| `cross-cutting`. The load-order class. |
| `domain` | string | optional | `design` \| `engineering` \| `product` \| `data` \| `game` \| … Facet for grouping + dedupe. |
| `hub` | string | spokes | The hub this spoke belongs to (creates a spoke→hub load edge). |
| `prerequisites` | list | where order matters | **Hard** "load before me" edges. Keep to 0–2; the resolver walks the chain transitively (so a spoke names only its hub; the hub names the foundation). |
| `related` | list | optional | **Soft** cross-references. Surfaced as suggestions, never auto-loaded. |
| `governed_by` | list | design/eng spokes | Cross-cutting lenses (e.g. `a11y-visual`, `visual-qa-ui-design`) applied *after* this skill produces output. |
| `governs` | list | cross-cutting skills | Inverse of `governed_by`. |
| `surfaces` | list | optional | Where the skill is valid. Default `["*"]`. Use e.g. `["claude-code","mcp"]` for tool-specific skills. |
| `requires` | list | tool-dependent skills | Capability ids ([[capability-registry]]) for external tools (MCP servers / CLIs) the skill needs. The agent **preflights** these before use — see "Capability requirements" below. |
| `spec_version` | string | optional | Frontmatter contract version. Stamp `"2.0"` (or `"2.1"` if using `requires`). |
| `pinned_version` | string | rare | Keep as-is on framework skills (`fw-*`). Orthogonal to loading. |

## Load-precedence rule

`tier` ranks load order: `foundation` (0) → `hub` (1) → `spoke` (2) → `cross-cutting` (3).
`prerequisites` and the implicit spoke→`hub` edge are the only **hard** edges. The transitive
chain `spoke → hub → foundation` is what guarantees principles load before specialty work —
**without restating the foundation on every spoke.**

## Capability requirements (`requires`)

A skill that depends on an external tool — an MCP server or a CLI — declares it by **capability
id**, not by hard-coding detection or install steps:

```yaml
requires: [figma-mcp]      # ids defined in 02-shared-references/capability-registry.md
```

The id resolves in [[capability-registry]], which holds the **detection probe**, **per-surface
install command**, and **fallback** for that capability. Before invoking the tool, the agent
**preflights** the capability (see [[AGENTS]] → "Capability preflight") and, if it's absent on the
current surface, follows the registry's fallback (`degrade` / `block` / `route`) instead of failing
opaquely. Reciprocity is enforced: the capability's `powers` list must name the skill, and vice
versa (`09-tools/validate-capabilities.py`).

This keeps skills portable — the same `requires: [figma-mcp]` works on Claude Code, Cursor, or any
MCP client, because *how* to detect/install lives in one surface-agnostic place.

## Examples

**Foundation** (`design-foundations/SKILL.md`):
```yaml
---
name: design-foundations
description: >
  Context-free visual + UX first principles — perception, hierarchy, contrast,
  color, type, composition. Load before any specialty design hub or spoke.
aliases: [design-foundations]
triggers: [design, ui, ux, visual, layout, color, type, composition, critique]
tier: foundation
domain: design
surfaces: ["*"]
spec_version: "2.0"
---
```

**Hub** (`lead-ui-designer/SKILL.md`):
```yaml
---
name: lead-ui-designer
description: >        # unchanged — full routing prose stays
  Staff/Principal IC visual designer for digital interfaces. Hub for 7 spokes …
aliases: [lead-ui-designer]
triggers: [ui design, visual design, color palette, type hierarchy, dark mode, elevation]
tier: hub
domain: design
prerequisites: [design-foundations]
related: [lead-ux-designer, ds-advisor, lead-graphic-designer]
spec_version: "2.0"
---
```

**Spoke** (`uid-color-for-ui/SKILL.md`):
```yaml
---
name: uid-color-for-ui
description: >        # unchanged
  Color design decisions for digital UI — palettes, dark mode, semantic roles …
aliases: [uid-color-for-ui]
triggers: [ui color palette, dark mode color, oklch, semantic color, colorblind-safe]
tier: spoke
domain: design
hub: lead-ui-designer
prerequisites: [lead-ui-designer]   # hub already requires design-foundations — don't restate it
related: [ds-advisor, uid-surface-depth]
governed_by: [a11y-visual]
spec_version: "2.0"
---
```

The chain resolves transitively: `uid-color-for-ui` → `lead-ui-designer` → `design-foundations`.

## The `## Related` block (body convention)

Below the frontmatter, each skill ends with one canonical `## Related` block using **typed**
wikilinks (basenames, resolved via `aliases`). This is the human/Obsidian-facing mirror of the
frontmatter edges and the only cross-link format permitted:

```markdown
## Related
- foundation → [[found-color]]
- hub → [[lead-ui-designer]]
- applies-in ← [[gd-color-theory]] · [[infod-encoding-theory]]
- governed-by → [[a11y-visual]]
- peer ↔ [[uid-surface-depth]]
```

Relation vocabulary: `foundation` · `hub` · `spoke` · `applies-in` · `governed-by` · `peer` ·
`encodes-into`. **Reciprocity is mandatory** (A `foundation→` B ⟹ B `applies-in←` A) and is
checked by `.github/workflows/link-validator.yml`. Only `foundation →` carries load precedence;
the rest are navigational.

## Rules

- **Never rename a `SKILL.md` file or its directory** without re-pointing every loader path and
  wikilink — 200+ files hardcode `03-skills/<name>/SKILL.md`. Add `aliases` instead.
- After editing frontmatter, run `python3 09-tools/build-registry.py` (or let CI catch the drift).
- `prerequisites` is a DAG: no cycles. The generator hard-fails on a cycle or a dangling reference.
