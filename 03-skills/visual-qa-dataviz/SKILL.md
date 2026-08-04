---
name: visual-qa-dataviz
description: >-
  Visual QA judgment lens for charts, tables, dashboards, and statistical graphics.
  Use with /qa --lens dataviz. Covers encoding integrity, legend/scale honesty,
  colorblind-safe series, chartjunk, and table scanability.
aliases: [visual-qa-dataviz]
triggers: [dataviz qa, chart audit, dashboard qa, encoding integrity]
tier: spoke
domain: quality
hub: lead-visual-qa
prerequisites: [lead-visual-qa]
related: [infod-encoding-theory, fe-data-visualization, ux-data-visualization, qa]
rigor_role: multi-voice
surfaces: ["*"]
spec_version: "2.2"
---

# Visual QA — Data Visualization

Judgment lens (critique). For measured color/contrast use [[visual-qa-toolkit]].

## Checks

- Encoding matches data type (position > length > angle > area > color hue for quantity)
- Scales/baselines honest; truncated axes disclosed
- Series distinguishable under deuteranomaly; not color-only
- Legends/tooltips match ink; no chartjunk competing with signal
- Dense tables: alignment, scan columns, status not color-only

## Related
- hub → [[lead-visual-qa]]
- peer ↔ [[infod-encoding-theory]] · [[fe-data-visualization]] · [[ux-data-visualization]] · [[qa]]
