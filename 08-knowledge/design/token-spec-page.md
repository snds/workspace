---
title: Token Spec page (Figma ↔ centric-ui ↔ prototype)
status: living
updated: 2026-08-05
figma_file: o6o1ZuGHxDow2vHLuYXT6X
figma_page: Token Spec
data: token-spec-figma-vs-code.json
related: [figma-shadow-modes, density-radius-xxs-alignment, cross-surface-token-parity]
---

## Authoring rule (Sean, 2026-08-05)

**Do not wholesale rebuild or wipe the Token Spec root frame.** Sean has hand-tuned
hug/fill / auto-layout on the frame (`409:12664` and descendants). Before any edit:

1. Re-read the target frame and its children (layoutMode, layoutSizing H/V, align, grow).
2. Be **additive** or surgically adjust existing nodes.
3. Never `remove()` the root content and regenerate; never force-resize hug frames to fixed heights.

Frame: https://www.figma.com/design/o6o1ZuGHxDow2vHLuYXT6X/Centric-SaaS-PLM---Design-System?node-id=409-12664

## Dogfood pass (2026-08-05)

Token Spec now consumes the DS (bindings + components), without regenerating the page:

| Check | Before | After |
|---|---|---|
| Bound solid fills | ~0 | **1166** (137 unbound — mostly intentional color-sample swatches) |
| Text with local text style | ~0 / 890 | **884 / 890** (Alert instance text keeps component styles) |
| Bound padding / gap / radius | ~0 | padding on many frames; **1112** gaps; **123** radii |
| Root layout | HUG / HUG | **preserved** HUG / HUG; section kids FILL×HUG |

Components swapped in place:

- Legend chips → **6× Badge** instances (`8:5505`) with `Badge / Variant` modes (success / info / warning / secondary)
- Intro callouts → **3× Alert** instances (`54:1028`, Success + Info×2); icons off (Material Symbols Outlined unavailable in plugin font load)

Chrome fills/text bound to Foundations semantics (`surface/*`, `chrome/border`, status softs, etc.). Color-row swatches left literal so resolved hex samples stay honest.

### Remaining gaps

- Unbound fills ≈ color swatches + a few outliers outside semantic RGB threshold
- Table row Separators not swapped to Separator component (layout risk)
- Stats / DEVIATE counts still reflect pre-code-remap snapshot (content regenerate separate from dogfood)
- Alert icons disabled until Outlined Material Symbols loads in plugin context

## Targets

| Column | Source |
|---|---|
| Figma | Foundations / Semantics in this file |
| centric-ui | `app/app.css` + `palette.generated.css` |
| prototype | `saas-plm-prototype` `src/styles/density.css` + `tailwind.css` |

## Align pass (2026-08-05)

- Figma Density **Compact/Normal/Spacious** now match prototype same-mode values for control heights, row padding, gaps, control radii, and newly added proto twins.
- New Figma density tokens: `padding-x/input`, `row/padding-y-head`, `header/height`, `menu-item/padding-y`, `sidebar-item/padding-y`, `tab/padding-y`, `row/height`.
- Figma Radii semantic scale is **density-modeled** (Compact/Normal/Spacious) to match Proto, including `radius/xxs`.
- Prototype gained `--density-control-px-sm` (Figma `padding-x/sm`) and `--radius-none`. Full circle stays Tailwind `rounded-full` (not a 9999px token).

### `radius/full` — ALIGNED

| Surface | Representation |
|---|---|
| Figma | `radius/full` = **9999px** (variables cannot bind a non-pixel circle) |
| centric-ui | Tailwind **`rounded-full`** → `calc(infinity * 1px)` |
| prototype | Same Tailwind **`rounded-full`** |

Status: **ALIGNED** — identical intent and visual outcome; implementation differs by surface.
Canonical rule: [[cross-surface-token-parity]].

### Spacing / radii notes (2026-08-05)

- **`space/px`**: Figma already had it (1px). Both codebases declare `--spacing-px: 1px` (Tailwind `*-px`).
- **`radius/xxs`**: Hairline rung — Compact/Normal **2px**, Spacious **4px**. Compact may collapse `xxs`/`xs` both at 2.
- **`radius/xs`**: Compact 2 / Normal 4 / Spacious 8.
- **Header height**: ALIGNED — Figma `header/height` (56/64/72) · Proto `--density-header-h` · centric `--header-h: var(--density-header-h)`.
- **CDS drop shadows**: ALIGNED — Figma collection `Foundations / Semantics / Shadows` (modes Drop 1–3) + Colors `shadow/drop-*` (Light/Dark) + single effect style `shadow/cds-drop`. Code: `--shadow-cds-drop-*` in centric + Proto `@theme`/`.dark`. See [[figma-shadow-modes]].

## Color pipelines

Each color row shows **Figma / centric-ui / prototype** reference chains (Light + Dark)
and resolved output. Status uses [[cross-surface-token-parity]]:

- **MATCH** — value + functionally equivalent pipeline (naming may differ)
- **ALIGNED** — same visual outcome; pipeline differs by surface
- **DEVIATE** — value/intent differs (selected/sidebar were the six; code now remapped to Figma overlay model on `feat/interaction-overlay-tokens` — regenerate snapshot to clear DEVIATE)

### Gut check (2026-08-05 evening) — live Figma + Token Spec update

Live probe (Figma MCP restored) confirmed Figma already aliases selected/accent
**foregrounds** through `action/primary-text` (Blue/11) — matches remapped code.
Washes remain Blue A overlays → **ALIGNED** (rgba vs `blueA-*` hex).

**Canvas Token Spec** (`409:12664`) surgically updated (no wipe):

- 12 row status labels DEVIATE → MATCH (foregrounds) / ALIGNED (washes)
- Notes rewritten; light-table chain cells refreshed to live chains
- Stats: Color MATCH **44** · ALIGNED **4** · DEVIATE **0**

Snapshot JSON: 44 MATCH · 4 ALIGNED · 0 DEVIATE · 26 FIGMA-ONLY.

### Stickersheet Inventory (2026-08-05)

New page **Stickersheet Inventory** (`426:60`):
https://www.figma.com/design/o6o1ZuGHxDow2vHLuYXT6X/Centric-SaaS-PLM---Design-System?node-id=426-60

- 6 shells: Light/Dark × Compact/Normal/Spacious (Colors + Density + Radii modes pinned)
- Review matrix: VARIANT axes × Size/Variant-as-modes; **icons ignored**
- ~61 component sections × 6 shells ≈ **1832 instances / shell** (~11k total)
- Button full State × Size × Variant modes; other sets + orphans included

See [[stickersheet-inventory-plan]].
