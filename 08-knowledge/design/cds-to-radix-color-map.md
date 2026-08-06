---
tags: [design-system, centric, cds, tokens, radix, migration, figma]
created: 2026-07-31
updated: 2026-07-31
status: reference
confidence: high
sources: [Figma file o6o1ZuGHxDow2vHLuYXT6X, session 2026-07-31-work-figma-density]
related_skills: [ds-advisor, design-engineer, fe-design-tokens]
related_projects: [centric-ui]
---

# CDS palette → Radix primitive map (retired from Figma library)

Catalog of the 42 `cds/*` semantic-color bridge tokens removed from
`Centric SaaS PLM — Design System` (`o6o1ZuGHxDow2vHLuYXT6X`) on **2026-07-31**.

These were catch-alls from a CDS → Radix/shadcn migration. They lived in
`Foundations / Semantics / Colors` (Light/Dark modes) and aliased Radix
primitives — **not** true intent tokens. Removed wholesale from Figma after
confirming **zero consumers** (no node bindings, no variable aliases).

The migration that still needs to happen is in **`centric-ui`** (employer repo):
replace remaining CDS color references with semantic intent tokens
(`action/primary`, `status/destructive`, …) or Radix primitives directly.

Hue remaps that are not 1:1 name matches:
- CDS `black` / `gray` → Radix **Zinc**
- CDS `pink` → Radix **Rose**
- CDS `purple` → Radix **Violet**

Legacy Figma names before slash-group rename: `cds-{hue}-{step}`
(e.g. `cds-blue-500`). Slash form at deletion: `cds/{hue}/{step}`.

## Mapping table

| CDS token | Light → Radix | Dark → Radix |
|-----------|---------------|--------------|
| `cds/black/50` | Zinc/Light/9 | Zinc/Dark/9 |
| `cds/black/100` | Zinc/Light/9 | Zinc/Dark/9 |
| `cds/black/200` | Zinc/Light/10 | Zinc/Dark/10 |
| `cds/black/300` | Zinc/Light/11 | Zinc/Dark/11 |
| `cds/black/400` | Zinc/Light/12 | Zinc/Dark/12 |
| `cds/black/500` | Zinc/Light/12 | Zinc/Dark/12 |
| `cds/gray/50` | Zinc/Light/1 | Zinc/Dark/1 |
| `cds/gray/100` | Zinc/Light/3 | Zinc/Dark/3 |
| `cds/gray/200` | Zinc/Light/4 | Zinc/Dark/4 |
| `cds/gray/300` | Zinc/Light/5 | Zinc/Dark/5 |
| `cds/gray/400` | Zinc/Light/6 | Zinc/Dark/6 |
| `cds/gray/500` | Zinc/Light/7 | Zinc/Dark/7 |
| `cds/gray/600` | Zinc/Light/8 | Zinc/Dark/8 |
| `cds/gray/800` | Zinc/Light/9 | Zinc/Dark/9 |
| `cds/gray/900` | Zinc/Light/10 | Zinc/Dark/10 |
| `cds/gray/1000` | Zinc/Light/11 | Zinc/Dark/11 |
| `cds/blue/50` | Blue/Light/3 | Blue/Dark/3 |
| `cds/blue/100` | Blue/Light/4 | Blue/Dark/4 |
| `cds/blue/500` | Blue/Light/9 | Blue/Dark/9 |
| `cds/blue/600` | Blue/Light/10 | Blue/Dark/10 |
| `cds/blue/700` | Blue/Light/11 | Blue/Dark/11 |
| `cds/cyan/50` | Cyan/Light/3 | Cyan/Dark/3 |
| `cds/cyan/500` | Cyan/Light/9 | Cyan/Dark/9 |
| `cds/cyan/600` | Cyan/Light/10 | Cyan/Dark/10 |
| `cds/green/50` | Green/Light/3 | Green/Dark/3 |
| `cds/green/500` | Green/Light/9 | Green/Dark/9 |
| `cds/green/600` | Green/Light/10 | Green/Dark/10 |
| `cds/orange/50` | Orange/Light/3 | Orange/Dark/3 |
| `cds/orange/500` | Orange/Light/9 | Orange/Dark/9 |
| `cds/orange/600` | Orange/Light/10 | Orange/Dark/10 |
| `cds/pink/50` | Rose/Light/3 | Rose/Dark/3 |
| `cds/pink/100` | Rose/Light/4 | Rose/Dark/4 |
| `cds/pink/300` | Rose/Light/7 | Rose/Dark/7 |
| `cds/pink/500` | Rose/Light/9 | Rose/Dark/9 |
| `cds/purple/50` | Violet/Light/3 | Violet/Dark/3 |
| `cds/purple/500` | Violet/Light/9 | Violet/Dark/9 |
| `cds/red/50` | Red/Light/3 | Red/Dark/3 |
| `cds/red/500` | Red/Light/9 | Red/Dark/9 |
| `cds/red/600` | Red/Light/10 | Red/Dark/10 |
| `cds/yellow/50` | Yellow/Light/3 | Yellow/Dark/3 |
| `cds/yellow/500` | Yellow/Light/9 | Yellow/Dark/9 |
| `cds/yellow/600` | Yellow/Light/10 | Yellow/Dark/10 |

Primitive path prefix in Figma: `Color/{Hue}/{Light|Dark}/{step}`
(e.g. `Color/Blue/Light/9`).

## Notes for the centric-ui migration

- Prefer **semantic intent** tokens over either CDS steps or raw Radix steps in
  product UI (`action/primary`, `status/destructive/soft`, `chrome/border`, …).
- Use this table only where a CDS step must be preserved temporarily — map to
  the listed Radix step, then replace with intent ASAP.
- Incomplete CDS scales (e.g. no `gray/700`, sparse `blue` steps) reflect the
  old bridge, not a full palette — do not recreate them in Figma.

## Related

- [[centric-plm-design-system]] — density + semantic naming conventions
- [[figma-ds-surface-authoring]] — Figma library authoring rules
