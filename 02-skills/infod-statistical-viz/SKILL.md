---
name: infod-statistical-viz
description: >
  Chart taxonomy and selection for statistical and business data: distribution,
  comparison, composition, relationship, time series, and part-to-whole charts.
  Covers when NOT to use specific chart types, annotation design (data callouts,
  reference lines, threshold markers), the legend-within-chart principle, and
  small multiples (trellis/faceting). Use this spoke when the question is which
  chart type to use for a specific data structure and audience, when a chart
  type is inappropriate or misleading, how to annotate a chart for clarity, or
  when to use small multiples vs. animation vs. interaction.
hub: lead-information-designer
aliases: [infod-statistical-viz]
tier: spoke
domain: design
prerequisites: [lead-information-designer]
spec_version: "2.0"
---

# Statistical Visualization

Specialist spoke for chart type taxonomy, selection criteria, and annotation
design. Part of the `lead-information-designer` skill network.

---

## Domain Boundary

This spoke owns **chart type decisions** — what to use, when, and why not.

- **Why a specific encoding channel works** → `infod-encoding-theory`
- **Dashboard layout with multiple charts** → `infod-dashboard-patterns`
- **Chart as a design system component** → `infod-design-system-patterns`
- **Narrative structure for multiple charts** → `infod-narrative-design`

---

## Chart Taxonomy

### Distribution — What does the data spread look like?

**Histogram**
- Shows frequency distribution of a single continuous variable in bins
- Reveals modality (unimodal, bimodal), skew, outliers
- Hides: individual data points, exact values between bin edges
- When to use: raw data distribution exploration; never for dashboards where
  the distribution is already understood
- Bin count matters: too few bins hides shape, too many creates noise
  (Sturges' rule: k = 1 + log₂(n) as a starting point)

**Density Plot (KDE)**
- Smoothed continuous estimate of distribution shape
- Shows: shape clearly; hides exact frequencies
- When to use: when comparing distributions of two groups overlaid;
  when the smoothed shape is more informative than bin counts
- When not: when readers need to count or read exact frequencies

**Box Plot**
- Shows: median, IQR (Q1–Q3), whiskers (typically 1.5×IQR), outliers
- Hides: distribution shape within the IQR (bimodal data looks unimodal in a box)
- When to use: comparing distributions across many groups (>5) where
  a density plot would overlap illegibly
- When not: for audiences unfamiliar with quartile notation; when
  sample sizes are small (n < 30); when distribution shape matters

**Violin Plot**
- Combines box plot structure with mirrored density estimate
- Shows: full distribution shape + summary statistics
- When to use: when you need both the shape and the summary; when n is large
- When not: for non-statistician audiences who find the shape confusing

**Strip Plot (Jitter)**
- Shows every individual data point as a dot, jittered horizontally to reduce overlap
- Shows: actual data, outliers, sample size
- When to use: small to medium n (≤200); when individual points matter
- When not: n > 300 (overplotting becomes unmanageable)

### Comparison — How do categories differ?

**Bar Chart (Categorical)**
- Vertical or horizontal bars on a common baseline
- The reference standard for comparing discrete category magnitudes
- Always start the value axis at zero (truncated bars misrepresent magnitude ratios)
- Horizontal bars preferred when category labels are long
- When not: continuous data (use line chart); >20 categories (use dot plot or table)

**Dot Plot (Cleveland)**
- A dot for each category value on a shared scale
- More space-efficient than bars; equally accurate (position on common scale)
- Better than bars for: ranked lists, large number of categories, when the
  zero baseline is far from the minimum value and zero-starting would compress
  the data range
- When not: unfamiliar audiences who expect bars

**Lollipop Chart**
- A line from zero to a dot; like a bar but with less visual mass
- Use when: many categories, bars feel heavy; calling individual values out
- Avoid when: differences are small (the thin line reduces readability)

**Slope Chart**
- Lines connecting values at two time points or two conditions per category
- Excellent for showing direction and magnitude of change between exactly two periods
- When not: more than two comparison periods (use line chart instead)

**Grouped Bar Chart**
- Bars grouped side-by-side for multiple series per category
- Effective for: comparing series values within each group
- When not: more than 4 groups (visual mass becomes unmanageable); use
  small multiples instead

### Composition — What makes up the whole?

**Stacked Bar Chart**
- Bars divided into segments representing sub-components
- Effective for: total comparison + rough sub-component inspection at the top-level
- Fundamental limitation: only the bottom segment has an accurate baseline;
  all others float and cannot be accurately compared across categories
- Lie potential: middle segments appear to change when the bottom segment changes,
  even if the middle segment value is constant
- Mitigation: use 100% stacked bar only when the proportion (not magnitude) is
  the message; limit to 3–4 segments maximum

**Treemap**
- Nested rectangles; area encodes value within a hierarchical structure
- Use for: displaying proportional composition of a hierarchy (e.g., category →
  sub-category spend); when the hierarchy structure is part of the message
- Limitation: area is a weak encoding (Cleveland & McGill rank 5); small segments
  are nearly impossible to compare
- When not: when precise comparison of individual segments is needed; prefer
  bar chart for comparison, treemap for overview/navigation

**Marimekko (Mosaic) Chart**
- Variable-width columns (encoding one variable) with stacked segments (encoding another)
- Two-dimensional composition encoding: proportion × count or proportion × proportion
- Lie potential: high; both the width and height encode data, and neither has a
  common baseline for either dimension
- Use sparingly: only when both dimensions genuinely need to be shown together
  and the audience can be briefed on how to read it

### Relationship — How do two or more variables co-vary?

**Scatterplot**
- x/y position for two quantitative variables
- The most powerful encoding for showing correlation, clusters, outliers
- Overplotting solutions for large n:
  - **Alpha transparency** (n < 1,000): reduce opacity so overlap is visible as density
  - **Jitter** (discrete data): add noise to reveal overlapping points
  - **Hex bins** (n > 1,000): aggregate into hexagonal cells, color by count
  - **Contour lines**: show density contours over individual points
  - **Sampling**: random or stratified sample when n > 50,000 and full set is not needed
- Always annotate outliers that matter; the reader cannot find them without guidance

**Bubble Chart**
- Scatterplot with a third variable encoded as circle area
- Perceptual limitation: area is systematically underestimated (Cleveland rank 5)
- Flannery correction: scale radius by value^0.5716 rather than value^0.5 to
  compensate for underestimation
- When not: when accurate comparison of the third variable is required; use a
  scatterplot matrix or small multiples instead

**Connected Scatter (Trajectory Plot)**
- Scatterplot with time-ordered points connected by lines, forming a path
- Shows the trajectory of a unit through a two-variable space over time
- When to use: when the direction and path of change matter, not just endpoints
- When not: more than 4–5 trajectories (overlapping paths become unreadable)

### Time Series — How does a value change over time?

**Line Chart**
- The standard for continuous time series
- Rule: connect points with a line only when the data represents a continuous
  process (not discrete events at those timestamps)
- Year labels: use full year on x-axis, not abbreviated
- When multiple series: direct label each line at its endpoint; avoid a legend
  when possible

**Area Chart**
- Line chart with the area below filled
- Use only when: cumulative or flow quantities where "under the curve" is
  meaningful (total revenue accrued, cumulative count)
- When not: overlapping multiple series (areas obscure each other; use lines)
- Pitfall: area charts are often misread as stacked; be explicit in the title

**Horizon Chart**
- A dense time series format for many series in limited vertical space
- Each series is divided into bands (positive/negative, near/far) and overlaid
  with color encoding distance from baseline
- High information density; requires audience briefing
- Use for: operational monitoring dashboards with 10–30 time series in
  limited vertical space; not for general audiences

**OHLC / Candlestick**
- Open, High, Low, Close encoding for financial time series
- Purpose-built for financial data; inappropriate outside that context

### Part-to-Whole — What percentage is each part?

**Pie Chart**
- Encodes proportion as angle; immediately familiar
- Works when: 2–3 slices; the dominant category's dominance is the message;
  the exact proportions don't matter (rough impression is sufficient)
- Fails when: >5 slices (angle differences become indistinguishable); any two
  slices need accurate comparison; proportions are similar in magnitude
- Rule: if you need a pie chart with more than 3 slices, use a bar chart instead
- Never: 3D pie charts, exploded pie charts

**Donut Chart**
- A pie with a center hole for labeling the total
- Same limitations as pie; the center label is the only improvement
- Acceptable for: a single dominant metric with context (e.g., "78% on-time
  delivery" as a donut in a KPI card)

**Waffle Chart (Unit Chart)**
- A grid of squares where filled squares represent proportions
- More readable than a pie for proportions near 25%, 50%, 75% because the grid
  provides reference structure
- Use for: simple proportions; when a human/unit representation is meaningful;
  when the audience includes non-analysts

**Small Multiples Rule for Part-to-Whole**
If you need to show part-to-whole across multiple categories (e.g., product mix
by region), use a small multiples bar chart rather than multiple pie charts.
Multiple pies cannot be compared across charts; multiple bar charts with a shared
scale can.

---

## When NOT to Use — Absolute Rules

| Chart Type | Never Use When |
|------------|---------------|
| **Pie chart** | >5 slices; any two slices need precise comparison |
| **3D chart** | Any quantitative data; always degrades accuracy |
| **Dual-axis chart** | The two series use different units — almost always creates a false correlation by axis scaling; use two separate charts instead |
| **Stacked area (multiple series)** | More than 2 series; accurate reading of individual series is needed |
| **Radar / Spider chart** | Any serious comparison; area and distance from center are both misleading; replace with parallel coordinates or small multiples bar |
| **Bubble chart** | Precise magnitude comparison; use scatterplot + separate bar chart |
| **Waterfall (negative)** | Don't confuse the Marimekko waterfall with the executive waterfall; see `infod-narrative-design` for the narrative waterfall |

---

## Annotation Design

Annotations are the text layer that makes a chart tell a specific story. They
are not decoration — they are the editorial layer that transforms data into
communication.

### Types of Annotations

**Data callout annotation**
- Points to a specific data element with a label or leader line
- Use to: identify the outlier, name the peak, label the threshold crossing
- Format: value + context ("Q3: $2.4M — first quarter exceeding plan")

**Reference line / threshold marker**
- Horizontal or vertical line marking a target, plan value, or threshold
- Label directly on the line ("Plan: $2.1M"); never in a legend
- Use light gray or a neutral secondary color; should recede behind data marks

**Contextual annotation**
- Explains the encoding choice: "(Size = order quantity)"
- Placed at the start of the relevant encoding; small, muted type
- Reduces the need for a legend

**Editorial annotation**
- Tells the reader what matters: "Margin decline concentrated in EMEA"
- Placed as a title element, subtitle, or callout box
- This is the information designer's judgment, made visible

### The Legend-Within-Chart Principle

Every legend is an instruction to perform a lookup operation. Direct labeling
eliminates the lookup. Default to direct labels on or near the data. Use a
legend only when direct labeling creates visual conflicts (crowded multi-series
line chart with crossing lines).

### Reference Lines vs. Gridlines

Gridlines are a background structure for reading values; they should be light
gray and visually recede. Reference lines are data (they encode a specific value
that matters); they should be visible but secondary to the data marks.

Never make gridlines as dark as data marks.

---

## Small Multiples (Trellis / Faceting)

Small multiples apply the same chart (same encoding, same scale) to multiple
subsets of data, displayed side-by-side or in a grid. This allows comparison
across subsets by position — the most perceptually accurate channel.

**When small multiples beat interaction:**
- The user needs to compare multiple subsets simultaneously (not sequentially)
- Animation would require memory of the previous state — unreliable for comparison
- The data fits within a reasonable grid (4×4 or smaller for legibility)

**When small multiples beat a single chart with grouping:**
- More than 4 series in one chart creates visual crowding
- The individual subset pattern matters as much as the comparison

**Requirements for valid small multiples:**
- Identical scales across all panels (same x-axis range, same y-axis range)
- Identical encoding (same mark type, same color mapping)
- Consistent panel size
- Clear, minimal panel labels (category name only; not repeated axis labels)

**When not to use small multiples:**
- When the comparison across subsets is the only question (a grouped bar chart
  or slope chart is more efficient)
- When panel count exceeds ~12 (grid becomes too small to read)

---

## Cross-Links

- **`infod-encoding-theory`** — perceptual accuracy of encoding channels is the
  foundation for chart type selection rationale
- **`infod-dashboard-patterns`** — chart type choices for KPI cards, trend
  sparklines, and drill-down charts within dashboards
- **`infod-narrative-design`** — annotation strategy and editorial framing;
  the waterfall chart as executive narrative device
- **`infod-design-system-patterns`** — chart component anatomy (title, subtitle,
  axis labels, legend, tooltip, empty state) for DS integration
- **`infod-network-graphs`** — node-link diagrams and hierarchy visualization;
  separate taxonomy from statistical charts
- **`infod-spatial-maps`** — choropleth and proportional symbol as composition
  and comparison charts applied geographically

---

## References

- Cleveland & McGill — "Graphical Perception: Theory, Experimentation, and Application" (1984)
- Heer & Bostock — "Crowdsourcing Graphical Perception" (2010; replication and extension)
- Stephen Few — *Show Me the Numbers* (2004)
- Edward Tufte — *The Visual Display of Quantitative Information* (1983)
- Claus Wilke — *Fundamentals of Data Visualization* (2019): https://clauswilke.com/dataviz/
- Alberto Cairo — *How Charts Lie* (2019)
