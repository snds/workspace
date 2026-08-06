---
title: Content-sized home dashboard grid
status: living
updated: 2026-08-05
related:
  - density-row-height-explained
  - density-dashboard-visual-review
  - centric-ui-density-adoption
  - density-dashboard-page-inset-vertical
---

# Content-sized home dashboard grid

## Decision (2026-08-05)

**Dual layout** is the product path:

| Mode | Renderer | Height |
|------|----------|--------|
| **View** (default) | CSS grid from saved `x/y/w` (`centric-ui` `DashboardViewGrid.tsx`) | **Hug** widgets → content height; **Fill** widgets → stretch with row peers (`items-stretch` + soft min from last `h`) |
| **Edit** | react-grid-layout (`DashboardGrid.tsx` edit path) | Frozen `ROW_HEIGHT = 40`; drag/resize/snap; density gutters |

Registry field `sizing: "hug" | "fill"` on each widget (`kpi-strip` / `quick-actions` = hug; `attention-list` / `recent-activity` = fill).

Storage key: `dashboard-layout-v10`. Persisted shape still `{ x, y, w, h, … }` — `h` is the edit-unit / soft min for fill; view hug ignores pixel `h`.

On **Enter edit**, view shells are measured (`[data-dashboard-widget]`) and quantized to RGL `h` so handles match on-screen size. On exit, view re-hugs from content (expected mild reflow).

Shell mode context: `DashboardShellMode` (`view` | `edit`) so hug widgets drop `h-full` in view.

## Why not RGL-only

`h × ROW_HEIGHT + (h − 1) × marginY` forces absolute cell height. Short content + `h-full` = empty bottoms (KPI / Quick Actions). Density gutters alone cannot fix that.

## Not in this pass

- Density-bound `ROW_HEIGHT`
- Masonry / overlapping widgets
- Server-persisted layouts
- Proto (no RGL dashboard)

## Prior interim note

Earlier: keep frozen `ROW_HEIGHT` and density-only chrome. Superseded by dual layout above.
