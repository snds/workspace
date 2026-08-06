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
