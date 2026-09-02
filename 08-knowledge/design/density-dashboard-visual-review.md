---
title: Dashboard density visual review
status: living
updated: 2026-08-05
related: [centric-ui-density-adoption, density-dashboard-content-sized-grid, density-row-height-explained]
---

# Dashboard density visual review (2026-08-05)

Live app was behind Keycloak (`/login`), so the initial review used a harness that
mirrored pre-fix construction next to an idealized token-consuming variant.

Assets: `08-knowledge/design/assets/density-dashboard-review/`

## Status after safe wiring (same day)

**Done (no `ROW_HEIGHT` change):** page header, grid outer pad (L/R **and** T/B via
`p-(--density-page-inset)`), KPI / attention / activity / quick-action interiors, list
widget headers, strip gaps, thumbs & QA icons now consume `--density-*`.

**Also done (2026-08-05 later):** header↔grid rhythm — header `pb-0`, grid owns
vertical inset (matches side inset). KPI / QA default `h` **3** again
(`dashboard-layout-v8`) after v7’s `h=4` left sparse empty chrome; cards use
`gap-(--density-chrome-gap)`, value `text-2xl`, and drop `mt-auto` footer stretch.
`ROW_HEIGHT` still frozen at 40.

**Also done:** `GRID_MARGIN` is density-aware via `DENSITY_GRID_MARGIN_PX`
(`[12,16]` / `[16,24]` / `[24,32]`). Widget interiors use
`px-(--density-field-gap)` to match `DashboardHeader` L/R inset (vertical still
control-px-input / head-pad-y / cell-pad-y) + shared `rounded-md`. QA icon wells
aligned to `rounded-md`.

**Still frozen (address separately):** `DashboardGrid` `ROW_HEIGHT = 40`. Widget
row tracks stay mode-invariant, so spacious can still feel scrollier inside
fixed panels rather than growing the canvas. **Fill-height (2026-08-05):**
`recent-activity` default `h` matches `attention-list` (`9`) + storage
`dashboard-layout-v6` so the side-by-side card shells stretch. **Intended
direction:** content-sized grid (not density-bound `ROW_HEIGHT`) —
`density-dashboard-content-sized-grid.md`.

**Figma (2026-08-05):** DS file `o6o1ZuGHxDow2vHLuYXT6X` has no dedicated dashboard
home frame to retarget. Layout → Page Layout `content` already binds T/B/L/R to
`container/lg` (page-inset analogue). No variable named `page-inset`. Code decision
documented here + `centric-ui-density-adoption.md`.

## Original verdict (pre-fix)

Density **did** change chrome (header 56→64→72, nav 32→36→40, activity `py`
6→12→16, radius-md 8→12→16). On the **home dashboard canvas** the change felt
subtle because **most surface area was frozen in Tailwind literals + a fixed
react-grid-layout footprint**. Radius read louder than spacing.

## Pre-fix measurements

| Surface | Compact | Normal | Spacious | Then |
|---|---|---|---|---|
| App header h | 56 | 64 | 72 | yes |
| Sidebar nav h | 32 | 36 | 40 | yes |
| Page header pad | 32/24 | 32/24 | 32/24 | **was no** → now field-gap / chrome-gap |
| KPI card pad | 16 | 16 | 16 | **was no** → now cell-pad-y / px-input |
| Attention row pad | 16 | 16 | 16 | **was no** → now cell-pad-y / px-input |
| Activity row py | 6 | 12 | 16 | yes |
| Quick-action pad | 20 | 20 | 20 | **was no** → now cell-pad-y / px-input |
| Quick-action icon | 44 | 44 | 44 | **was no** → now control-h-lg |
| Attention thumb | 40 | 40 | 40 | **was no** → now control-h-lg |
| KPI strip track | 168 | 168 | 168 | **still no** (`ROW_HEIGHT=40`) |
| Full grid stack h | 984 | 984 | 984 | **still no** |

Idealized full token binding (incl. row height): KPI strip **144 → 196 → 248**;
full grid **792 → 1100 → 1408**.

## Remaining construction notes

1. **`ROW_HEIGHT` / content sizing** — frozen unit remains; product direction is
   content-sized view (see `density-dashboard-content-sized-grid.md`). Side-by-side
   fill already fixed (`recent-activity` h=9, `v6`). (`GRID_MARGIN` tracks density.)
2. **Partial wiring paradox** — list row pads grow inside fixed panel heights until
   shells are content-sized (or temporarily density-aware).
3. **Control ladder** — still ±4px (32/36/40); layout consumers do the drama.
4. **Sidebar** — fixed `h` + `py` still means sidebar-item-py barely affects rhythm.
5. **Shell radius optics** — taller attention/activity panels can *look* softer than
   KPI/QA at the same `rounded-md` / `--radius-md`; don’t split shell steps.
   Edit-mode dashed wrappers also use `rounded-md` (not `rounded-xl`).
