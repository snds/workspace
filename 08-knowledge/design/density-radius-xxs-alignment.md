---
title: Density + radius/xxs cross-surface alignment
status: living
updated: 2026-08-06
related: [token-spec-page, cross-surface-token-parity, figma-shadow-modes]
---

# Density + `radius/xxs` alignment

Proto is SSOT. Figma Radii + centric-ui now share the same density-modeled ladder.

## Radius ladder (px)

| Token | Compact | Normal | Spacious |
|---|---|---|---|
| `xxs` | 2 | 2 | 4 |
| `xs` | 2 | 4 | 8 |
| `sm` | 4 | 8 | 12 |
| `md` | 8 | 12 | 16 |
| `lg` | 12 | 16 | 20 |
| `xl` | 16 | 20 | 24 |
| `2xl` | 16 | 20 | 24 |
| `3xl` | 24 | 28 | 32 |
| `4xl` | 32 | 40 | 48 |
| `none` | 0 | 0 | 0 |
| `full` | 9999 / `rounded-full` | same | same |

Compact may collapse `xxs`/`xs` both at 2. `full` stays ALIGNED (Figma 9999 vs Tailwind `rounded-full`).

## Surfaces

| Surface | Mechanism |
|---|---|
| Figma | `Foundations / Semantics / Radii` ladder + Density `control-radius/*` **literals** + `focus-ring-radius/*`; pin Density for control chrome |
| Proto | `data-density` + `src/styles/density.css` |
| centric-ui | `data-density` + `app/density.css` + `app/lib/density.ts`; header DensityToggle; Storybook density toolbar |

## Nested / focus-ring radii (2026-08-06)

Formula ([nested containers](https://medium.com/design-bootcamp/getting-your-border-radius-right-a-simple-trick-for-smooth-nested-containers-f6e0025e8c53)):

**`outerRadius = innerRadius + gap`**

Focus rings in this DS sit **3px** outside the control (`strokeWeight` 3 → `[ring]` inset −3). Binding the ring to the **same** token as the body pinches corners (visible on stickersheet Buttons).

### Do nested ideals land on the radius ladder?

**No — systematically miss by 1px.** Offset is 3; ladder steps are 4.

| Density | Inner (`control-radius/sm`) | Ideal ring | Nearest ladder | Δ |
|---|---|---|---|---|
| Compact | 4 | **7** | `radius/md` 8 | +1 |
| Normal | 8 | **11** | `radius/md` 12 | +1 |
| Spacious | 12 | **15** | `radius/lg` 16 | +1 |

| Density | Inner (`control-radius/md`) | Ideal ring | Nearest ladder | Δ |
|---|---|---|---|---|
| Compact | 8 | **11** | `radius/md` 12 | +1 |
| Normal | 12 | **15** | `radius/lg` 16 | +1 |
| Spacious | 16 | **19** | `radius/xl` 20 | +1 |

**Pills (`radius/full`)** — Switch / Badge / Slider thumb: keep `full` on both body and ring; nested formula is a no-op.

### Figma approach (no parametric variables)

Figma cannot express `radius + offset`. Precompute **body + ring** in **Density** so a single Density mode pin drives nesting (do not rely on Radii mode for control chrome):

| Token | Compact | Normal | Spacious | Notes |
|---|---|---|---|---|
| `control-radius/sm` | 4 | 8 | 12 | **Literals** (was alias→`radius/sm`; dual-pin bug) |
| `control-radius/md` | 8 | 12 | 16 | **Literals** (was alias→`radius/md`) |
| `focus-ring-offset` | 3 | 3 | 3 | |
| `focus-ring-radius/sm` | 7 | 11 | 15 | = control-sm + 3 |
| `focus-ring-radius/md` | 11 | 15 | 19 | = control-md + 3 |

IDs: `control-radius/sm` `VariableID:285:41` · `control-radius/md` `VariableID:285:42` · `focus-ring-radius/sm` `VariableID:432:26` · `focus-ring-radius/md` `VariableID:432:27`

Component mode variables:

- `Button / Size` `radius` → `control-radius/*`; `radiusRing` (`VariableID:432:28`) → `focus-ring-radius/*`
- `Select / Size` same pattern (`radiusRing` `VariableID:432:29`)
- `Badge / Shape` (`VariableID:142:29` / `434:1702`): Pill → `radius/full` body+ring; Rounded body → `control-radius/sm`, ring → `focus-ring-radius/sm`
- Input/Textarea masters bind body→`control-radius/md`, ring→`focus-ring-radius/md`
- Checkbox masters bind body→`control-radius/sm`, ring→`focus-ring-radius/sm` (was `radius/sm`)

`Foundations / Semantics / Radii` remains the general ladder SSOT (cards, etc.). Control chrome must use Density `control-radius` + `focus-ring-radius` so Compact/Spacious work without also pinning Radii.

Snap-to-next-rung remains an ACCEPTABLE fallback (±1px) if we ever refuse new floats.

**Badge / Shape** (2026-08-06): Pill keeps `radius/full` on body+ring. Rounded uses Density control + focus-ring tokens (confirmed Compact/Normal/Spacious nest = +3). Tabs/Nav bodies → `control-radius/sm`.

### Focus ring color (2026-08-06)

`Button / Variant` `ring/default` and `Badge / Variant` `ring/default` drive Focus
`[ring]` strokes. **Default = `chrome/ring`.** Exceptions only:

| Keep colored | Token |
|---|---|
| Variant `destructive` / `danger` | `status/destructive` |
| Component State=`Error` (ring bound directly) | `status/destructive` |

Status / negative chrome (`info`, `success`, `warning`, `caution`, ghosts, `pagination`)
use **`chrome/ring`** — not hue-matched rings. Remapped 11 Button modes accordingly;
Badge table was already correct.

`[state-layer]` must use the **same** corner token as its host control (same radius, not nested-outer — overlays are inset/fill, not offset rings).

Pagination Hover used a Button instance at Size=`lg` → state-layer `Button/Size.radius` = `control-radius/md` (12) while the instance corners were overridden to `Pagination/Control.radius` = `control-radius/sm` (8). **Fix:** set Pagination Button instances to Size=`sm` and bind width/height to `Pagination/Control.height` (keeps 40px square). Hover overlay now matches (8=8). Added `_Pagination/Item` **State=Focus** with nested ring.

Also: Tabs Hover body+layer → `control-radius/sm`. *(Error/Focus rings briefly added on Input Error, Toggle, Radio, OTP, etc. were **reverted 2026-08-06** — those variants already define focus without a separate `[ring]`.)*

### Control density audit (2026-08-06)

Dead alias `VariableID:64:2862` (deleted radius; Focus variants already on `control-radius/sm`) rebound on `_Radio/Item`, `_NavMenu/Trigger`, `_Menu/Item` rows, Slider/`_Slider/Thumb` value chips → **`control-radius/sm`**.

Also at component/mode level:
- `Button / Size` `paddingX` → `padding-x/sm|md`; `gap` → `gap/sm` (was raw 10/6)
- `Badge / Size` `padding-y` Small → `space/0-5`
- Input/Textarea pad-X → `padding-x/input`
- `_OTP/Slot` w/h → `control-height/lg`
- `_Dialog/Close` / `_Sheet/Close` w/h → `control-height/md`
- `_Select/Item` / `_Radio/Item` minH → `control-height/sm`; Nav/Menubar triggers minH → `control-height/md`
- Slider tracks `radius/sm` → `radius/full`

Left intentional: Badge HUG+pad (no fixed height); Slider root 24px track well; Switch/`Avatar` size collections still literal geometry.

### Figma-only construction tokens (`[figma-only][sync:ignore]`)

Prefix in the variable **description** so token sync skips them. Not product CSS tokens — Figma cannot express `calc()` / sibling-relative overlay position.

| Token | Why Figma-only |
|---|---|
| `focus-ring-offset` | Nest gap companion; code prefers `--focus-ring-offset` + calc |
| `focus-ring-radius/sm\|md` | Precomputed `control-radius + offset` |
| `Button/Select/Badge … radiusRing` | Component-mode aliases → focus-ring-radius |
| `Day/top-*` / `Day/bottom-*` (`Calendar / Radii`) | Per-corner range masks |
| `toggle-group/inset` (`VariableID:463:26`) | Shell↔item pad/gap = **2** (nest companion) |
| `toggle-group/item-radius` (`VariableID:463:25`) | = `control-radius/md − 2` → **6/10/14** (C/N/S) |
| `Toggle Group / Item` `Item/*` corners | Position masks (`standalone` / `h-*` / `v-*`) |
| `popover/offset-y` (`VariableID:456:25`) | Spacer height = `control-height/md + 4` → **36 / 40 / 44**. Absolute `[popover-anchor]` + `[popover-offset]` + in-flow Popover (Date Picker, Combobox, Nav Menu; Menubar also uses `[popover-pad-clear]`=`space-1`). Code: `top:100%` + margin |

### Field-anchored overlay radii (2026-08-06)

Standing rule (also in [[figma-ds-surface-authoring]] §B.0 / B.10a): **when in doubt, Density-bind** spacing/padding/radii/sizing. Panels that sit with a parent field/control must share that trigger’s `control-radius/*` rung — usually **`md`** for Input/Select default.

| Overlay | Binding |
|---|---|
| Popover, `_Select/Content` | Already `control-radius/md` |
| Calendar Single/Range, Command, Dropdown Menu, Context Menu | Was `sm` → **`control-radius/md`** |
| Tooltip | Stays `sm` (small chrome, not a field twin) |
| Dialog / Drawer | Radii ladder (`radius/xl`, …) — not field-paired |

### Calendar / `_Calendar/Day` (2026-08-06)

Days were FIXED 34 + `minHeight` 34 + pad-Y only — not density-square. Now:
- Cleared all min/max W/H on Day + Calendar tree
- Day **width = height = `control-height/md`** (C/N/S → 32/36/40, always square)
- Day padding all sides → `padding-y/xs`
- Calendar shell → `padding-x/md` + `padding-y/xl`; header/grid → `padding-y/xs` / `gap/xs`
- Weekday cells width → `control-height/md` (column align), height HUG + `padding-y/xs`

### Toggle Group nested radii + field height (2026-08-06)

Was: shell + items both `control-radius/sm`, shell hugged ~32 (not field-tall) → pinched nest next to Input/Button.

| Part | Binding |
|---|---|
| Shell corners | `control-radius/md` (`VariableID:285:42`) |
| Shell height (Horizontal) | `control-height/md` (`VariableID:285:28`) → 32/36/40 |
| Shell pad + item gap | `toggle-group/inset` = 2 |
| Item corners | `Toggle Group / Item` modes → `Item/*` (`VariableID:465:26–29`) |
| Nested end-cap radius | `toggle-group/item-radius` = md−2 → 6/10/14 |
| Mid / shared edges | `radius/none` |
| Standalone Toggle | mode `standalone` → still `control-radius/sm` (unchanged look) |

Horizontal items `FILL` height (inner = md−4). Vertical items height → `control-height/md`; corner modes `v-first|middle|last`. Stickersheet 12 instances reset; Density C/N/S rows verified.

### Code approach

Prefer live calc (true parametric):

```css
--focus-ring-offset: 3px;
--radius-focus-sm: calc(var(--radius-sm) + var(--focus-ring-offset));
--radius-focus-md: calc(var(--radius-md) + var(--focus-ring-offset));
```

Or for nested cards generally: `calc(var(--radius-lg) - var(--spacing-2))` on the inner. Ship Figma precomputed values as the documented SSOT until code gains the calc twins.

### Applies beyond focus rings

Same rule for card-in-card, input-in-field, icon wells in padded frames — whenever two rounded boxes share an inset gap.
- Data-table `ROW_DENSITY` bridge when tables should follow app density.
- ~~`--header-h` (48px) vs `--density-header-h` not yet unified in centric.~~ **Done 2026-08-05:** centric `--header-h: var(--density-header-h)` (56/64/72). Figma `header/height` already matched Proto.
- ~~CDS drop shadows still CODE→FIGMA GAP.~~ **Done 2026-08-05:** Figma `Foundations / Semantics / Shadows` (Drop 1–3) + single effect style `shadow/cds-drop`; Colors `shadow/drop-*` Light/Dark; Proto live `--shadow-cds-drop-*` in `@theme` + `.dark`.
- ~~Form/select Compact radius too soft.~~ **Done 2026-08-05:** SchemaForm widgets were overriding control `rounded-sm` with `rounded-md` — see [[centric-ui-density-adoption]] audit.
