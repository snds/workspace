---
title: centric-ui density token adoption
status: living
updated: 2026-08-05
related: [density-radius-xxs-alignment, density-dashboard-visual-review]
---

# centric-ui density token adoption

## Why density felt “sidebar-only”

Radius ladder remaps (`--radius-*`) apply globally via Tailwind `rounded-*`.
Control **heights/paddings** only change where markup consumes `--density-*`.
Most of centric still used literal `h-8` / `h-9` / `px-2.5`, so Compact→Normal→Spacious
barely moved chrome outside corners — while sidebar item rounding was the most
obvious radius delta.

## Token roles (dashboard)

| Token | Use |
|---|---|
| `--density-page-inset` | Page header + grid **outer** L/R (and page vertical chrome). 1.5 / 2 / 2.5rem |
| `--density-card-pad` | Inset from **card shell** edge (headers, rows, KPI/QA). Compact **1** / Normal **1.25** / Spacious **1.5**rem (Normal matches prior dashboard `p-5`) |
| `--density-field-gap` | Gaps **between** widgets/cards in a strip (not card chrome) |
| `--density-menu-item-py` | List **row** vertical pad (tight stack; not cell-pad-y) |
| `--density-head-pad-y` | Widget title bar vertical pad |
| `--density-chrome-gap` | Small chrome gaps (header actions, etc.) — **not** list text stacks |
| `--text-xs` / `--text-sm` | Tailwind theme font sizes remapped per density (UI chrome). Display (`text-2xl`) untouched |

Prefer Tailwind theme aliases (with fallbacks) over bare `p-(--density-*)` on dashboard:

`p-card-pad` · `gap-field-gap` · `gap-chrome-gap` · `px-page-inset` / `pt-page-inset` / `pb-page-inset`

These emit e.g. `padding: var(--density-card-pad, 1.25rem)` so inset still works if density.css is late.

## Control radius contract

Form controls (Button / Input / SelectTrigger / Textarea / command input / header search)
use **`rounded-sm` → `--radius-sm`**:

| Mode | `--radius-sm` | Control height |
|---|---|---|
| Compact | **4px** | 32px (`--density-control-h`) |
| Normal | 8px | 36px |
| Spacious | 12px | 40px |

Surfaces (dialogs, popovers, select popup, cards) stay on `rounded-lg` / `rounded-md`
and still track the density ladder — they are not control-radius.

## Compact form/select radius bug (2026-08-05 audit)

**Symptom:** SchemaForm inputs/selects looked too soft at Compact vs Button.

**Root cause:** Not broken tokens. Workflow form widgets **overrode** the primitive
`rounded-sm` with **`rounded-md`** (8px at Compact) via `twMerge`, and Enum/Specialization
selects also forced `h-auto` + `py-2` / `px-3` (padding-era height) instead of density
control tokens. Textarea primitive used `rounded-lg` (12px Compact).

**Fixed in centric-ui (uncommitted unless Sean commits):**

| File | Change |
|---|---|
| `RegisteredInput.tsx` | Removed `className="rounded-md"` override |
| `EnumSelectWidget.tsx` | `TRIGGER_CLASS` → `rounded-sm` + density px; drop `h-auto`/`py-2` |
| `SpecializationSelectWidget.tsx` | Same + skeleton → `h-(--density-control-h)` |
| `textarea.tsx` | `rounded-lg` → `rounded-sm`; density input px |
| `Header.tsx` search | `rounded-md` → `rounded-sm` |
| `command.tsx` input | `rounded-md` → `rounded-sm` |
| `checkbox.tsx` | `rounded-[4px]` → `rounded-[var(--radius-check)]` |
| `ClientResolveSubform` / `RunWorkflowDialog` | Skeleton `h-9` → density control-h |

## Primitive status (centric-ui `app/components/ui/`)

| Component | Status | Notes |
|---|---|---|
| Button | **compatible** | `rounded-sm` + full `--density-control-*` ladder |
| Input | **compatible** | `rounded-sm` + control-h / control-px-input |
| SelectTrigger | **compatible** | `rounded-sm` + control-h; form widgets must not re-`rounded-md` |
| SelectContent | partial | Popup `rounded-lg` (surface — OK); items use menu-item-py |
| Textarea | **compatible** (after fix) | Was P0 `rounded-lg` |
| Checkbox | **compatible** | Frozen `--radius-check` (4px all modes) by design |
| Switch | n/a radius | `rounded-full`; fixed px sizes (glyph-scale) |
| Tabs | partial | List `rounded-lg`, trigger `rounded-md`; height density-wired |
| Badge | partial | pill=`rounded-4xl` (invariant); shape=rounded uses `rounded-sm`; heights literal |
| Command input | **compatible** (after fix) | Shell still `rounded-md` |
| Dialog / Popover / Sheet | **compatible** (pad) | Surface `rounded-lg`; pad → `--density-card-pad` |
| Card | **compatible** (pad) | Shell pad → `--density-card-pad` / sm → head-pad / control-px |
| AlertDialog | **compatible** (pad) | Same card-pad contract as Dialog |
| Sidebar | partial | Items `rounded-md` + density heights; intentional md rung |
| Skeleton | partial | Default `rounded-md`; consumers must pass density h |
| Alert | partial | `rounded-lg` surface |
| Dropdown menu | partial | Popup `rounded-lg`; items `rounded-md` + menu-item-py |
| Form / Label | n/a | Layout only |

## Remaining gaps (priority)

### P0 — done
- Form Input/Select/Textarea compact radius overrides.

### P1 — done (2026-08-05)
- **Surfaces:** Card / Dialog / Sheet / AlertDialog pad → `--density-card-pad`
  (footer negative margins track the same token).
- **Feature chrome:** literal `h-7`/`h-8`/`h-9` / `size-8` control overrides across
  views, BO catalog, filters, data-table filter search, toolbars → density control
  tokens. Where `size="sm"` already sets `--density-control-h-sm`, redundant `h-*`
  overrides were removed so the sm ladder can move with mode.
- **FieldEditor** inline editors: `rounded-md` → `rounded-sm` (control contract).
- **FilterMultiselectPopover:** density height + `rounded-sm`.
- Left alone on purpose: table image thumbs (`size-9`), schema relationship SVG
  diagram height, decorative empty-state icons, data-table **row** density axis.

### P2 — inconsistent adoption
- Sidebar / Tabs / menu items on `rounded-md` while controls are `rounded-sm` (often intentional rung).
- Badge heights frozen; chip radius via `--radius-chip` when chips migrate off Badge pill.
- Content-sized view-mode grid is a future direction; RGL `ROW_HEIGHT` stays for edit/slotting.
- Proto (`saas-plm-prototype`) may need the same form-override + feature-chrome pass later.

### Done — UI chrome type steps with density (reversed prior “invariant text” stance)
`app/density.css` remaps Tailwind `--text-xs` / `--text-sm` (+ line-heights) per
`[data-density]`. Glyph/icon `size-*` stay fixed; **type** breathes for UI chrome.

| Mode | `--text-xs` | `--text-sm` |
|---|---|---|
| Compact | 0.6875rem (11) | 0.75rem (12) |
| Normal | 0.75rem (12) | 0.875rem (14) — TW defaults |
| Spacious | 0.875rem (14) | 1rem (16) |

Display steps (`text-2xl` KPI values) stay fixed. Dashboard list rows (Attention /
Activity) share `text-sm` titles + `text-xs` meta so both step together.

## Adopted (2026-08-05)

| Surface | Tokens |
|---|---|
| Primitives (Button/Input/Select/Tabs/Sidebar/menus) | control-h / control-px / menu-item-py / sidebar-item-py |
| Dashboard page header | `px/pt-(--density-page-inset)` |
| Dashboard grid outer L/R | `px-(--density-page-inset)` on a wrapper **outside** the RGL width ref |
| Dashboard grid gutters | `DENSITY_GRID_MARGIN_PX` |
| KPI / QA cards | `p-(--density-card-pad)`; icon wells → control-h; stacks `gap-1`/`gap-3` |
| List headers | `px-(--density-card-pad) py-(--density-head-pad-y)` |
| List rows | `px-(--density-card-pad) py-(--density-menu-item-py)`; text stack `gap-0.5`/`gap-1`; title `text-sm font-semibold`, meta `text-xs` |
| Strip / QA track gaps | `--density-field-gap` |
| Card shells (dashboard widgets) | `rounded-md` → `--radius-md` |
| SchemaForm controls | `rounded-sm` (restored; see audit above) |
| Card / Dialog / Sheet / AlertDialog | `--density-card-pad` |
| Feature toolbars / filters / selects | `--density-control-h*` (no frozen `h-8`/`h-9`) |

## Pattern

Prefer Tailwind v4 `h-(--density-control-h)` / `px-(--density-card-pad)`.
Controls: **`rounded-sm`**, never `rounded-md` / `rounded-lg` on Input/Select/Button/Textarea.
Do not put CSS padding on the same node as RGL `useContainerWidth` — measure an inner full-width child.
