---
title: What ROW_HEIGHT controls on the home dashboard
status: living
updated: 2026-08-05
related: [density-dashboard-visual-review, density-dashboard-content-sized-grid, centric-ui-density-adoption]
---

# What `ROW_HEIGHT` controls

`ROW_HEIGHT = 40` in `DashboardGrid.tsx` (edit mode) is the react-grid-layout row unit. Widget shell height in **edit** is `h × ROW_HEIGHT + (h − 1) × marginY` (normal `marginY = 24`).

**View mode** no longer uses this for hug widgets — see dual layout in `density-dashboard-content-sized-grid.md`. Fill widgets may still use quantized `h` as a soft min height.
