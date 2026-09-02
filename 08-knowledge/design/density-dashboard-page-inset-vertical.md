---
title: Dashboard page-inset vertical + KPI hug
status: note
updated: 2026-08-05
related: [centric-ui-density-adoption, density-dashboard-visual-review]
---

# Dashboard vertical page inset + KPI cell hug (2026-08-05)

## Decision

1. **Grid owns page chrome on all four sides.** Outer scroll wrapper uses
   `px/pt/pb-page-inset` (theme aliases → `var(--density-page-inset, …)`). Measured
   RGL child stays unpadded.
   **Gotcha:** bare `p-(--density-*)` inside template literals can miss the Tailwind
   scanner; prefer static `cn(...)` + theme aliases (`p-card-pad`, `gap-field-gap`).
2. **Header** keeps `px/pt-page-inset` and `pb-0` so header + grid top inset don’t
   double-stack.
3. **KPI / quick-actions** use `dashboard-layout-v9` with RGL **`h: 4`** and
   `p-card-pad` / `gap-field-gap` (card-pad ladder bumped toward prior `p-5`).
   `ROW_HEIGHT` stays 40.

## Code surfaces

| Repo | Change |
|---|---|
| `centric-ui` | `DashboardGrid`, `DashboardHeader`, `KPICard`, `KPIStripWidget`, `QuickActionsWidget`, `layoutEngine` (`v8`), `widgetRegistry`, `density.css` comments |
| `saas-plm-prototype` | `density.css` comments only — **no** dashboard RGL / KPI strip to mirror |

## Figma

File `o6o1ZuGHxDow2vHLuYXT6X`: no dashboard home frame. Layout → Page Layout
`content` already uses `container/lg` on T/B/L/R. No `page-inset` variable.
No canvas edit required; code is source of truth for this rhythm.

## Risks

- Spacious/compact at `h=3` is tight (~cell height); `overflow-hidden` may clip a
  pixel or two if card-pad + control-h grow further — bump `h` or tighten again.
- Existing users on `dashboard-layout-v7` reset to defaults via key bump (intended).
- RGL width measurement: keep pad off `containerRef` (unchanged pattern).
