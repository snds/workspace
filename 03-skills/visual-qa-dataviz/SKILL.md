---
name: visual-qa-dataviz
description: >-
  Data-visualization QA lens — judgment on whether a rendered chart, table, or dashboard tile
  encodes its data honestly and legibly. Use when reviewing built or designed data surfaces:
  "review this chart", "does this graph read", "is this axis misleading", "the series are
  indistinguishable", "audit this data table", "is this dashboard readable", "review the KPI
  tile", "these bars look wrong", "critique this visualization". Covers encoding fit (mark vs
  data type and task), axis honesty (truncated/dual axes, aspect ratio), series
  differentiation and color independence, labeling and legend strategy, chart junk and
  data-ink, number formatting/units/precision, missing-vs-zero, data-table craft (numeral
  alignment, density, header behavior, sortability affordance, totals), state coverage
  (loading/empty/partial/error/too-much-data), and dark-theme series contrast. Spoke of
  lead-visual-qa. Do NOT use for: choosing a chart type for an unbuilt need
  (ux-data-visualization), encoding theory and perceptual grounding (infod-encoding-theory),
  charting-library or virtualization implementation (fe-data-visualization), statistical
  validity of the underlying analysis (infod-statistical-viz, ds-* skills), or dashboard
  information architecture (infod-dashboard-patterns).
aliases: [visual-qa-dataviz]
triggers: [chart review, chart audit, dataviz qa, graph review, data table review, dashboard review, misleading axis, series contrast, legend review, kpi tile review]
tier: cross-cutting
domain: quality
hub: lead-visual-qa
surfaces: ["*"]
spec_version: "2.0"
---

# Visual QA — Data Visualization

The judgment lens for data surfaces already rendered: charts, tables, KPI tiles, dashboards.
It asks two questions in order — **is the encoding honest?** then **is it legible?** A chart
can be beautiful, on-brand, and pixel-perfect while still lying about the data; that failure is
this lens's first responsibility.

## Domain boundary

| Question | Owner |
|---|---|
| What chart should this be, for this user need? | [[ux-data-visualization]] |
| Why does this encoding work perceptually (position > length > area > hue) | [[infod-encoding-theory]] |
| How do I build it (library choice, virtualization, cross-filter) | [[fe-data-visualization]] |
| Is the statistic itself sound (sampling, aggregation, confidence) | [[infod-statistical-viz]] |
| How should the dashboard be organized and prioritized | [[infod-dashboard-patterns]] |
| Does this rendered chart/table read correctly and honestly | **this lens** |

Overlaps are common with [[visual-qa-ui-design]] (the tile is also a component) and
[[visual-qa-accessibility]] (series color independence is also a WCAG 1.4.1 concern). File the
finding in both when it fails both; do not silently defer.

## Measurement companions

This lens judges; measure wherever a number is available rather than asserting.

| Claim | Measure with |
|---|---|
| Series / gridline / label contrast against the plot background | [[visual-qa-toolkit]] `qa_contrast` (also non-text 3:1 for meaningful marks) |
| Series collapse under deuteranopia / protanopia / tritanopia | [[visual-qa-toolkit]] `qa_color_vision` |
| Palette drift from the DS chart tokens | [[visual-qa-toolkit]] `qa_color_extraction` (Δe against the palette export) |
| Table column/row alignment and density against the spacing scale | [[visual-qa-toolkit]] `qa_alignment` · `qa_spacing` |
| Label sizes against the type scale | [[visual-qa-toolkit]] `qa_typography` |
| Table semantics (`th`, `caption`, header association), sortable-control names | [[a11y-audit-toolkit]] |

State the pixels judged at. Fine axis labels and 1px gridlines cannot be evaluated from a
downsampled screenshot — capture natively first ([[native-visual-eval]]).

## Encoding honesty

| Failure | Why it matters | Verdict |
|---|---|---|
| Truncated y-axis on a bar chart | Bar *length* is the encoding; cutting the baseline multiplies apparent differences | blocker |
| Truncated axis on a line chart without saying so | Legitimate for trends, deceptive if unlabeled | major unless annotated |
| Dual y-axes | Any correlation can be manufactured by rescaling; two panels or an indexed series is almost always better | major |
| Area/bubble encoding by radius instead of area | Overstates magnitude quadratically | blocker |
| 3-D perspective, donut thickness, or shadow on a quantitative mark | Distorts the comparison the mark exists to make | major |
| Pie/donut with more than ~5 slices, or comparing across pies | Angle comparison is weak; cross-pie comparison is guesswork | major |
| Inconsistent bin widths, irregular time steps drawn evenly | Implies a uniformity the data lacks | blocker |
| Missing data drawn as zero, or interpolated across a gap | Invents observations | blocker |
| Unsorted categorical bars where rank is the question | Forces the reader to do the sorting | minor |
| Aggregation not stated (sum vs average vs median, timezone, currency) | The reader cannot know what they're looking at | major |
| Axis direction or color scale inverted from convention (e.g. red = good) | Reads backwards at a glance | major |

## Legibility and craft

- **Series differentiation** — hue alone fails for CVD users and in grayscale printouts. Line
  charts need dash/marker/width or direct labels; areas need pattern or ordering; categorical
  palettes should stay within the DS's chart token set and cap out at the number of hues that
  remain distinguishable (usually 6-8).
- **Direct labeling beats legends.** A legend forces a lookup for every glance. Label the last
  point of a line, the largest slice, the highlighted series. Keep the legend only when marks
  genuinely cannot carry a label.
- **Chart junk and data-ink** — gridlines should recede (never darker than the marks), ticks
  should be sparse and rounded, borders and drop shadows on plot areas add nothing. Remove
  anything that is not data, scale, or a label a reader needs.
- **Aspect ratio and banking** — a trend's apparent slope is set by the aspect ratio. Wildly
  wide or tall panels editorialize; aim for slopes that average near 45° for the comparison
  that matters, and keep small multiples on identical scales and ratios.
- **Overplotting** — dense scatter/line data needs transparency, binning, sampling, or
  aggregation. A solid mass of marks is not a visualization.
- **Number formatting** — consistent precision (not 3 decimals on one row and 0 on the next),
  thousands separators, units in the axis title rather than every tick, currency and percentage
  symbols placed per locale, abbreviations legible (`1.2M`, not `1200000`), and no false
  precision on estimates.
- **Annotation and context** — a value with no comparison (target, prior period, benchmark)
  answers nothing. Anomalies, deploys, and outages that explain a spike belong on the chart.
- **Dark theme** — chart palettes tuned on white commonly fail on dark surfaces (saturated
  fills glow, light strokes vanish). Judge both themes; they are two artifacts.
- **Interaction is not a channel of last resort** — if a value is only available in a tooltip,
  it does not exist for keyboard users, on touch, in a screenshot, or in an export.

## Data tables

Tables are data visualization; they fail in their own ways.

- **Numerals right-aligned** with tabular figures, decimal points aligned, units in the header;
  text left-aligned. Centered numeric columns are a defect.
- **Column order follows the reading task** (identifier → status → the numbers being compared →
  actions), and the primary identifier column stays visible when scrolling horizontally.
- **Density is deliberate** — enterprise power users want compact rows; compact must still meet
  target size (24×24 CSS px minimum) for row actions and checkboxes.
- **Header behavior** — sticky headers on long tables, sortable columns showing current sort
  direction and being operable by keyboard, and no sort affordance on columns that are not
  sortable.
- **Totals and aggregates** are visually distinct from data rows and state what they aggregate.
- **Empty, loading, partial, and error states** exist and are not a blank rectangle: skeletons
  match the eventual row height (no layout shift), empty states say what would appear here and
  how to get it, and partial failure marks the failed cells rather than blanking the table.
- **Truncation is recoverable** — an ellipsis with no tooltip, expansion, or full value
  elsewhere loses data; wrapping in a dense grid destroys scanability. Pick one deliberately.
- **Row-level meaning is not color-only** — a red row must also carry an icon, label, or status
  column.

## QA checklist — data visualization

**Honesty**
- [ ] Quantitative marks start at a true baseline, or the truncation is explicit
- [ ] No dual axes, 3-D effects, or radius-encoded area
- [ ] Missing data is shown as missing, not zero or interpolated
- [ ] Aggregation, units, timezone, and time grain are stated
- [ ] Scale/color direction matches convention for the domain

**Encoding fit**
- [ ] The mark matches the data type and the comparison task
- [ ] Categorical order serves the question (ranked when rank matters)
- [ ] Small multiples share scale, ratio, and color mapping

**Legibility**
- [ ] Series distinguishable without hue (dash, marker, pattern, or direct label)
- [ ] Series and label contrast measured, not eyeballed; non-text marks ≥ 3:1
- [ ] Gridlines and ticks recede; no chart junk
- [ ] Labels legible at native resolution; no collision or clipped rotation
- [ ] Number formatting consistent, with units and sane precision
- [ ] Judged in both light and dark themes

**Table craft**
- [ ] Numerals right-aligned, tabular figures, decimals aligned
- [ ] Sticky header; sort state visible and keyboard-operable
- [ ] Row actions and checkboxes meet target size at the chosen density
- [ ] Loading / empty / partial / error states present and shift-free
- [ ] Truncated content is recoverable
- [ ] Status is not conveyed by color alone

## Report shape

Return the shared `/qa` format (findings · severity · evidence · fix · owner · summary · next).
Route fixes: encoding and labeling changes to [[ux-data-visualization]] or
[[infod-encoding-theory]] for the rationale, implementation to [[fe-data-visualization]], chart
token gaps to [[ds-advisor]], and accessibility failures to [[visual-qa-accessibility]] plus
[[a11y-audit-toolkit]] for the structural half.

## Related
- hub → [[lead-visual-qa]]
- peer ↔ [[infod-encoding-theory]]
