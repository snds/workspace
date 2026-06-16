---
name: ux-data-visualization
description: >
  Chart selection, dashboard design, data density decisions, table design, and visual
  data encoding for enterprise SaaS products. Use this skill when working on: choosing
  the right chart type for a data relationship, dashboard layout and hierarchy, KPI
  widget design, cross-filter interaction design, table column hierarchy and numeric
  alignment, null/empty cell treatment, row density modes, sparklines and inline data
  context, color palette selection for data (sequential, diverging, categorical), small
  multiples vs. complex multi-series charts, Sankey/flow diagrams, responsive dashboard
  patterns, and any question about how to visually represent data in an enterprise
  interface. Also trigger on: "what chart should I use for X", "how do I design this
  dashboard", "how do I show trend in a table", "what's the right color scale for X",
  "this chart is unreadable — how do I fix it", or any question about data-to-visual
  encoding decisions. Assumes the designer understands Tufte-level data-ink ratio basics.
---

# UX — Data Visualization

Spoke skill in the `lead-ux-designer` network. Owns the design decision layer for
data visualization: chart type selection, visual encoding choices, dashboard architecture,
and table design for data-dense enterprise interfaces.

Does not own: rendering and implementation (→ `fe-data-visualization`), analytical
methodology (→ `ds-executive-storytelling`), instrumentation of dashboard interactions
(→ `ds-product-analytics`), API shape to support the chart (→ `be-api-design`).
Those constraints inform design decisions here but are decided elsewhere.

---

## Chart Selection Framework

The chart type is not an aesthetic choice — it is a claim about the relationship in
the data. Choosing the wrong chart type misrepresents the data. Use this framework:
match the relationship you're communicating to the encoding that makes it clearest.

### What relationship does the data express?

| Relationship | Primary encoding | Best chart(s) | Never use |
|-------------|-----------------|---------------|-----------|
| **Change over continuous time** | Position on shared axis | Line chart, area chart | Bar chart for continuous time series |
| **Comparison between discrete items** | Position on shared axis | Horizontal bar chart, dot plot | Pie chart if >3 items |
| **Part-to-whole** | Arc length / area proportion | Stacked bar, treemap, waffle | Pie chart for >3 segments or when precision matters |
| **Distribution** | Position + density | Histogram, box plot, violin plot | Bar chart of averages (hides spread) |
| **Correlation / relationship** | Position on two axes | Scatter plot, bubble chart, slope chart | Heatmap if both axes aren't categorical |
| **Ranking** | Position on common scale | Horizontal bar (for long labels), dot plot | Vertical bar when labels are long |
| **Flow between states** | Edge width proportional to volume | Sankey, alluvial diagram | Only when the flow metaphor is literally true |
| **Composition change over time** | Position on stacked area or 100% bar | Stacked bar (grouped for absolute, 100% for proportion) | Pie chart per time period |
| **Geographic distribution** | Map projection | Choropleth, proportional symbol map | Map when geography is irrelevant to the insight |
| **Network relationships** | Node and edge | Node-link graph | Node-link when the count is the insight, not the connections |

### Critical failure modes by chart type

**Pie charts**: the human visual system is poor at comparing arc lengths. Pie charts
work only when: (a) there are ≤3 segments, (b) the point is a rough proportion ("about
three-quarters"), and (c) precision is not required. Enterprise analytics almost never
satisfies all three. Use a bar chart.

**Bar charts for continuous time**: a bar chart for daily data over 12 months encodes
the wrong metaphor — bars imply discrete categories, not continuous change. Use a line
chart. Use bars only when each time period is genuinely a discrete event (monthly totals
with no meaningful interpolation between them).

**Heatmaps for non-categorical axes**: heatmaps work when both axes are categorical.
Using a heatmap with a continuous axis (time on X, metric on Y) conflates category
with gradient and makes the chart harder to read than a line chart.

**Multi-series line charts with >6 series**: beyond 5–6 series, color differentiation
fails and the chart becomes unreadable. Use small multiples instead.

**Dual-axis charts**: two Y-axes sharing an X-axis create the appearance of a
relationship between two metrics that may not have one. The cross-point of two lines
on a dual-axis chart changes with axis scaling — it is arbitrary. Only use dual-axis
charts when you can guarantee the axes are rationally related (e.g., two related units
of the same measurement).

---

## Data Density in Enterprise UIs

Enterprise users are not overwhelmed by density. They are overwhelmed by inconsistency
and poor hierarchy within density. This distinction matters: the solution to an
overwhelming enterprise dashboard is not less data — it is better structure.

### The data-ink ratio (Tufte)

Every non-data element in a chart consumes cognitive resources without contributing
information. Remove:
- Gridlines that don't aid reading (keep major gridlines, remove minor gridlines)
- Tick marks on axes where gridlines already mark positions
- Decorative fills and gradients on bars (solid fill reads better)
- Legends when the chart can be directly labeled
- Borders and drop shadows on charts (unless elevation is architecturally meaningful)
- Background fills on chart areas (the default in most charting libraries — remove it)

Don't interpret this as "use no gridlines." Gridlines that help users read specific
values are data-ink. The question is: does this element help the user read the chart?
If not, remove it.

### Small multiples over complex multi-series charts

When you need to compare the same metric across multiple segments, 9 small identical
charts are almost always easier to read than 1 chart with 9 series.

Small multiples work because: (a) the shared axis scale enables direct comparison;
(b) each chart is simple enough to read in 2–3 seconds; (c) patterns across the set
are visible without needing to track 9 colored lines through an overlapping hairball.

Small multiples require a consistent scale across all facets. If facets use different
axis scales, the visual comparison is meaningless.

### Sparklines for inline data context

A sparkline is a small, word-sized chart embedded in a table row or next to a metric.
Its purpose is to communicate trend without leaving the data context. Rules:
- Sparklines in the same column must share a Y-axis scale (otherwise the visual
  comparison across rows is misleading — a flat line at different absolute values
  should not look identical)
- Sparklines do not need axis labels, tick marks, or gridlines — they are for trend,
  not precise reading
- Width should be enough to show the shape clearly: 60–120px at compact density
- Paired with a value that gives the precise reading: the sparkline shows trend,
  the number shows current value

---

## Table Design for Complex Data

Tables are the dominant UI pattern in enterprise SaaS. They are also the most
commonly broken. Most table design failures are decisions that were never made.

### Column hierarchy

Left-to-right order is an implicit claim about what matters. Default column order:
1. **Primary identifier** (name, SKU, ID) — left-anchored, often sticky/frozen
2. **Secondary classifiers** (type, category, status) — next to the identifier
3. **Metric columns** (counts, values, percentages) — right or center-aligned
4. **Contextual dates** (created, modified, due) — secondary to metrics
5. **Actions** (edit, delete, row-level actions) — rightmost, never leftmost

Column order that puts a metric column next to the identifier before classifiers
makes classification harder. Column order is a design decision — don't accept the
default API response order as the column order.

### Numeric alignment

Right-align all numeric values. This enables vertical comparison of decimal positions.
Inconsistent decimal places in a column make vertical comparison impossible — if one
row shows "1.2" and another shows "1.23" and another shows "1", align them to the same
decimal precision (1.20, 1.23, 1.00).

Right-align: all integers, all decimals, all currencies, all percentages.
Left-align: all text (names, labels, descriptions, status strings).
Center: binary values (checkboxes, boolean badges), icons.

### Null/empty cell treatment

Three distinct states require three distinct visual treatments:
- **No data**: the system has no record for this value — use an em dash (—) or "N/A"
- **Zero**: the system has a record and the value is zero — show "0" with the same
  formatting as other values. Do not use a dash — it conflates zero with no data.
- **Not applicable**: the field doesn't apply to this record type — a dedicated
  visual treatment (lighter text, italics, or "—" with a tooltip explaining inapplicability)

Collapsing these three into one treatment ("—" for all) is a data quality failure
that forces users to guess which condition applies.

### Row density modes

Enterprise tools should offer density control because users' tasks vary: a user
scanning for an item in a 500-row table wants compact mode; a user reviewing the
details of a single record wants comfortable mode.

| Mode | Row height | Use case |
|------|-----------|---------|
| Compact | ~32px | Scanning large datasets; power-user workflows; minimal content per row |
| Default | ~40px | Standard use; short text values; status indicators |
| Comfortable | ~48px+ | Multi-line cell content; embedded sparklines; image thumbnails |

### Sorting, filtering, grouping

Each has an interaction model that must be consistent across every table in the product.

**Sorting**: click column header to sort ascending, click again for descending, click
again to clear sort. Sort direction must be visually clear. Multi-column sort requires
a sort priority indicator (1st sort, 2nd sort). Sort state must persist when the user
navigates away and returns (or be reset explicitly with a visible affordance).

**Filtering**: the filter panel location, filter chip design, and "clear all filters"
mechanism must be consistent. Filters applied in the current session vs. saved filters
are different states — design them differently.

**Grouping**: grouping by a column creates a collapsed tree. The group header row
must show aggregate values for metrics (not leave them blank). Expand/collapse state
must persist across pagination.

### Frozen headers and columns

Tables that exceed viewport width require frozen columns. The primary identifier
column must freeze at minimum — users should always see which record a row belongs
to when scrolling right.

Technical constraint: CSS `position: sticky` has specific behavior in overflow
containers. Coordinate with `fe-component-architecture` before specifying multi-
column freeze behavior — the implementation has constraints that affect design.

---

## Dashboard Design

### Dashboard hierarchy

A dashboard that surfaces everything equally surfaces nothing. Required hierarchy:

**Level 1 (above the fold)**: Primary KPIs — 3–5 numbers the user must assess on
every visit. These should be scannable in 5 seconds. Each KPI widget: label + value
+ context (trend, vs. target, or vs. prior period). Context is not optional.

**Level 2 (first scroll)**: Secondary metrics, charts that explain the KPIs, segment
breakdowns. These are consulted when a KPI shows an unexpected value.

**Level 3 (drill-down)**: Detail tables, full data sets, configuration. Reached via
interaction from Level 1 or 2 — not immediately visible.

A dashboard with 15 equal-weight charts has no hierarchy. The user must scan all 15
to determine what's important. This is a design failure.

### Widget design specification

Every metric widget must contain:
- **Label**: what metric is this? Specific ("Q3 Orders") not generic ("Orders")
- **Primary value**: the current number, formatted consistently across all widgets
- **Context**: at minimum one of — trend arrow + percentage change, progress toward
  target, comparison to prior period. Never a bare number with no context.
- **Time context**: what period does this cover? "Today," "Last 30 days," "YTD" must
  be explicitly stated on each widget — don't assume the user remembers the global filter.

### Cross-filter interactions

When selecting a value in one chart filters the data in other charts, this is a
cross-filter interaction. The behavior must be:
1. **Explicitly declared in design**: which charts cross-filter which? Not all charts
   should filter all others — declare the filter graph explicitly.
2. **Visually confirmed**: when a filter is active, the filtered state must be obvious —
   the selected segment should be highlighted in the source chart; other charts should
   show the filtered state with a visual indicator.
3. **Clearable**: the user must be able to remove the cross-filter without hunting for it.
   A persistent "filters active" banner with a "clear all" option is the minimum.

### Empty dashboard states

Three distinct empty states require distinct designs:

**New user, no data**: the user has never used the product and there is nothing to show.
Explain what this dashboard shows, what generates data, and what to do first.

**Filtered to zero**: the user's current filter combination matches no data. Show the
filter state clearly, explain that no data matches, and offer to clear the filters.
Do not show the same "no data" state as the new user experience.

**No data in time range**: data exists but not in the selected period. Show the time
range, indicate that no data exists for it, and suggest adjacent ranges where data exists.

---

## Color in Data Visualization

Color is the most overloaded visual channel in data visualization. Use it intentionally.

### Palette taxonomy

**Sequential**: ordered data from low to high (heat, density, quantity). Single hue
progressing from light to dark. Build in a perceptually uniform color space (OKLCH)
so equal lightness steps produce equal perceived differences. Example: light blue → 
dark blue for "low to high utilization."

**Diverging**: data with a meaningful neutral midpoint (above/below target, positive/
negative change). Two hues diverging from a neutral midpoint. The midpoint should be
visually neutral (gray or near-white). Example: red → gray → green for below/at/above
target — but see colorblind note below.

**Categorical**: nominal groups with no inherent order. Maximum 7 distinguishable
colors. Above 7, color alone cannot reliably distinguish categories — use direct
labeling or small multiples instead.

### Colorblind-safe encoding

~8% of users (predominantly men) have red-green color deficiency. Never use red and
green as the only differentiator for important information. Options:
- Pair color with shape, pattern, or icon (a triangle for "alert" works regardless of color)
- Use orange instead of red for "warning" (distinguishable for deuteranopes)
- Use blue/orange diverging palettes instead of red/green
- Test every categorical palette against deuteranopia and protanopia simulation
  (Figma plugins: Stark, Color Blind)

This is not optional in enterprise SaaS with diverse user populations.

### Color as encoding, not decoration

A chart's background color, grid color, and axis color do not encode data — keep them
neutral. Reserve color for the data marks themselves. When multiple charts coexist
on a dashboard, consistent use of the same color for the same category across charts
reduces the cognitive load of decoding each chart independently.

---

## Cross-Links

- `fe-data-visualization` — rendering and performance constraints; library selection
- `ds-executive-storytelling` — what data story to tell and why; analytical methodology
- `be-api-design` — API response shape; aggregate vs. raw data; date bucketing constraints
- `ds-product-analytics` — instrumentation of dashboard interactions; what to measure
- `ux-interaction-design` — cross-filter interactions as an interaction pattern; drill-down flows
- `lead-information-designer` — for encoding theory depth (Bertin's retinal variables, Cleveland & McGill hierarchy), full chart taxonomy, dashboard architecture (KPI card anatomy, drill-down patterns), and narrative design; this spoke is the entry-level design-decision layer; route here for perceptual theory and discipline depth

---

## References

- Edward Tufte — The Visual Display of Quantitative Information
- Claus Wilke — Fundamentals of Data Visualization (open access): https://clauswilke.com/dataviz/
- Datawrapper Academy — Chart type selection: https://academy.datawrapper.de/
- Observable — Data visualization patterns: https://observablehq.com/
- Carbon Design System — Data visualization guidelines: https://carbondesignsystem.com/data-visualization/
