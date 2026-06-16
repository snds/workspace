---
name: infod-design-system-patterns
description: >
  Visualization as a design system component: chart token architecture (data color
  scale tokens, chart typography, grid/axis tokens), chart anatomy (required vs.
  optional elements), tooltip design, empty states for data components, and chart
  accessibility (alt text patterns, ARIA, keyboard access, SVG vs. Canvas trade-offs).
  Use this spoke when integrating charts into a design system, defining chart component
  tokens, specifying chart accessibility requirements, designing chart tooltips, or
  addressing SVG vs. Canvas rendering decisions for chart components.
hub: lead-information-designer
---

# Design System Patterns for Visualization

Specialist spoke for visualization components within a design system. Part of the
`lead-information-designer` skill network.

---

## Domain Boundary

This spoke owns the **design system integration layer** for visualization — how
charts become consistent, accessible, tokenized components.

- **Token architecture for the main DS** → `ds-advisor`
- **Chart type selection and encoding** → `infod-statistical-viz` + `infod-encoding-theory`
- **Frontend rendering implementation** → `fe-data-visualization` + `fe-component-architecture`
- **Accessibility implementation (ARIA, keyboard)** → `fe-accessibility`

---

## The Tension: Chart Freedom vs. DS Consistency

Charts are inherently more diverse than UI components. A button has 6–8 states.
A chart system can contain 20+ chart types, each with different mark geometries,
encoding configurations, and interaction models.

The design system's role is not to specify every chart — it is to establish:
1. The visual language shared by all charts (color, type, spacing)
2. The component API for commonly-used chart types
3. The accessibility contract that all charts must meet

**What becomes tokens (shared, constrained):**
- Data color palettes (sequential, diverging, categorical sequences)
- Chart typography (axis label scale, title scale, annotation scale)
- Grid and axis line style (color, weight, dash pattern)
- Spacing units within chart chrome (title margin, axis label margin)

**What must remain flexible (not tokenized at the chart level):**
- Mark type (a bar vs. a line vs. a dot)
- Encoding assignment (which data dimension maps to which channel)
- Annotation content (editorial decisions cannot be standardized)
- Scale range (data-driven; cannot be a design token)

---

## Chart Token Architecture

### Data Color Scale Tokens

Data color tokens are a separate token system from the UI semantic colors. They
must co-exist with the UI color system without colliding with semantic meanings.

**Categorical scale** (for nominal data: categories, series, groups):

```
data-color-categorical-1  (primary series)
data-color-categorical-2
data-color-categorical-3
data-color-categorical-4
data-color-categorical-5
data-color-categorical-6
data-color-categorical-7
data-color-categorical-8  (max 8 for reliable distinction)
```

Rules:
- 8 colors is the maximum for categorical series with reliable visual distinction
- Must be perceptually equidistant in hue and lightness
- Must be colorblind-safe: test all 8 against deuteranopia and protanopia simulation
- Must not use the UI semantic colors (error red, warning amber, success green) —
  those colors have semantic meaning in the UI; reusing them for categorical data
  would create false meaning
- Defined in OKLCH for perceptual uniformity; exported as hex for implementation

**Sequential scale** (for quantitative data: intensity, magnitude, quantity):

```
data-color-sequential-1   (lightest — low value)
data-color-sequential-2
data-color-sequential-3
data-color-sequential-4
data-color-sequential-5   (darkest — high value)
```

Rules:
- Monotonically increasing lightness (light to dark)
- A single hue family or a hue + lightness combination (blue-green sequential)
- 5 steps is sufficient for most data classification; 7 for fine-grained choropleth
- Must be distinguishable in grayscale (photocopy-safe)

**Diverging scale** (for data with a meaningful midpoint: variance from plan,
positive/negative change):

```
data-color-diverging-negative-2  (strongly negative)
data-color-diverging-negative-1  (mildly negative)
data-color-diverging-neutral      (midpoint — white or light gray)
data-color-diverging-positive-1  (mildly positive)
data-color-diverging-positive-2  (strongly positive)
```

Rules:
- Two hues diverging from a neutral midpoint
- Equal visual weight at equal distance from the midpoint
- Do not use UI semantic red/green for diverging — the association with
  error/success will override the data interpretation

**Coordinate with `ds-advisor`** for naming conventions, Figma variable
structure, and integration with the main token system.

### Chart Typography Tokens

```
chart-title-size          (relative to base: typically 1rem or 14px)
chart-title-weight        (bold or medium)
chart-subtitle-size       (0.875rem; muted color)
chart-axis-label-size     (0.75rem)
chart-axis-label-color    (text-secondary — from main DS token)
chart-annotation-size     (0.75rem)
chart-legend-label-size   (0.75rem)
chart-data-label-size     (0.75rem; on-mark labels)
chart-tooltip-title-size  (0.875rem; bold)
chart-tooltip-body-size   (0.875rem)
```

### Grid and Axis Tokens

```
chart-grid-color          (neutral-100 or equivalent from main DS)
chart-grid-weight         (1px)
chart-axis-line-color     (neutral-200)
chart-axis-line-weight    (1px)
chart-tick-color          (neutral-200)
chart-tick-length         (4px horizontal ticks)
chart-plot-background     (transparent or surface-base from main DS)
```

---

## Chart Component Anatomy

Every chart component has structural layers. Some are required for accessibility
and usability; others are optional based on context.

```
┌─────────────────────────────────────────────────────────────┐
│  [TITLE — required]                    [MENU/ACTIONS]        │
│  [SUBTITLE — optional; brief description or context]        │
├─────────────────────────────────────────────────────────────┤
│  [Y AXIS LABEL]  │                                          │
│                  │  [CHART PLOT AREA]                       │
│  [Y AXIS TICKS]  │                                          │
│  [Y AXIS LABELS] │                                          │
│                  │                                          │
│                  ├──────────────────────────────────────────│
│                  │  [X AXIS TICKS]                          │
│                  │  [X AXIS LABELS]                         │
│                  │  [X AXIS LABEL]                          │
├─────────────────────────────────────────────────────────────┤
│  [LEGEND — optional; prefer direct labels]                  │
│  [ANNOTATION LAYER — optional; editorial callouts]          │
│  [SOURCE ATTRIBUTION — required when data source matters]   │
└─────────────────────────────────────────────────────────────┘
```

### Required Elements (Accessibility and Usability)

| Element | Requirement |
|---------|-------------|
| **Title** | Every chart must have a title; it identifies the chart for screen readers and for users scanning a page |
| **Axis labels** | Required on any axis that is not self-evident; "Revenue ($M)" not just the tick marks |
| **Source attribution** | Required when the data source is external or when credibility is a question |
| **Alt text** | Required for any chart rendered as an image or SVG; see accessibility section |
| **Accessible color redundancy** | Any encoding that uses color must also use shape, label, or pattern for colorblind access |

### Optional Elements (Context-Dependent)

| Element | Include When |
|---------|-------------|
| **Subtitle** | When the title alone leaves the context unclear; brief (≤2 lines) |
| **Legend** | When direct labeling creates visual conflicts; kept minimal and adjacent to the chart |
| **Tooltip** | Any interactive chart; required for data callout without permanent labels |
| **Annotation layer** | When editorial interpretation adds value beyond axis reading |
| **Download/export action** | When users will need the data outside the dashboard |
| **Gridlines** | For charts where value estimation from position is important; suppress for sparklines |

---

## Tooltip Design

Tooltips are the primary interaction layer for most chart types.

### Position Strategy

**Follow-cursor**: tooltip follows the pointer or touch position; appropriate for
scatter plots and maps where the user explores freely.

**Fixed position (snapped)**: tooltip snaps to a fixed position relative to the
hovered element (above/below a bar, next to a data point); appropriate for bar
charts and line charts where the target is predictable.

**Floating panel**: large tooltip anchored to a side; appropriate when rich
content (multiple metrics, comparison, mini-charts) is needed.

### Content by Chart Type

| Chart Type | Tooltip Content |
|-----------|----------------|
| Bar chart | Category label + value + percentage of total (if composition) |
| Line chart | Date + series name + value; all visible series at the cursor's x-position |
| Scatter plot | x-label + x-value, y-label + y-value; optional: point name/ID |
| Choropleth | Region name + metric label + value + rank (optional) |
| Network graph | Node: name + centrality metrics; Edge: source + target + weight |
| Treemap | Category path + value + % of parent |

**Single value vs. series comparison**: Line charts with multiple series should
show all series values at the hovered x-position (series comparison tooltip),
not just the hovered series — this is the primary use case.

### Accessible Tooltip Design

- Tooltips must not be the only means of accessing information — the chart
  should be readable without interaction
- Keyboard-accessible: tooltips must appear on focus (not just hover); use
  CSS `:focus-visible` to trigger tooltip states
- Do not hide data inside tooltips that should be visible by default for
  critical metrics
- WCAG 2.1.1 (1.4.13): tooltip content must persist when the user moves
  the cursor to the tooltip (not auto-dismiss)
- Contrast: tooltip background must meet 4.5:1 against tooltip text

---

## Empty States for Data Components

Data components have four distinct empty states, each with different causes and
messages. Treating all four as the same state is a design failure.

### No Data (Genuinely Empty)

**Cause**: The filtered dataset has no records; the user selected criteria that
return nothing.

**Message**: "No [items] match your filters." + action to clear filters.

**Design**: Illustration optional; clear explanation required; filter reset CTA.
Do not show: axis, gridlines, or chart chrome. The chart shell should not persist
when there is no data — it implies data is coming.

### Loading

**Cause**: Data is being fetched; the chart will populate shortly.

**Message**: Skeleton screen matching the expected chart layout.

**Design**: Skeleton bars (for bar charts), skeleton lines (for line charts),
pulsing animation. Do not use a centered spinner in a chart — it gives no
information about what's loading.

Timing: if data loads in <300ms, suppress the skeleton (flash of skeleton is
more disruptive than no skeleton for fast responses). Use a minimum display
time for the skeleton if it does appear, to prevent jarring flicker.

### Error

**Cause**: The data request failed; a technical error occurred.

**Message**: "Couldn't load [chart name]." + retry action + optional error detail.

**Design**: Error icon + message + retry button. Do not show technical error
details to end users; log them.

### Filtered to Empty

**Cause**: The user applied filters that returned no results; the dataset exists
but no rows match.

**Message**: "No results for [active filter summary]." + "Clear filters" action.

**Design**: Distinct from "No Data" — the key difference is that the user caused
this state through filter action, and the solution is to change the filters.
Show the active filter context prominently.

---

## Accessibility in Visualization Components

### Alt Text for Charts

The standard pattern for chart alt text:

```
A [chart type] showing [relationship or trend] in [subject],
[time period if applicable]. [Key finding in one sentence.]
```

Examples:
- "A bar chart showing quarterly revenue by product category in FY2025.
  Accessories leads all categories at $4.2M, up 12% year-over-year."
- "A line chart showing on-time delivery rate from January to March 2025.
  The rate declined from 94% to 87% over the period, with a sharp drop in February."

**Anti-pattern**: "Chart showing data" — this is an alt text failure; it gives
screen reader users no information about the chart's content.

**Implementation**: `alt` attribute on `<img>` charts; `<title>` element as first
child of `<svg>` for inline SVG charts; `aria-label` or `aria-labelledby` on
the chart container for canvas-rendered charts.

### Table as Accessible Alternative

For complex charts (scatter plots, network graphs), provide the underlying data
as a visually-hidden table that screen readers can access:

```html
<figure>
  <canvas aria-label="Scatter plot of margin vs. volume by category">
    <!-- canvas rendering -->
  </canvas>
  <figcaption class="sr-only">
    <table>
      <!-- data table with same data as chart -->
    </table>
  </figcaption>
</figure>
```

### ARIA Live Regions for Real-Time Updates

When a chart updates automatically (operational dashboard with data refresh):

- Announce updates with `aria-live="polite"` on a visually-hidden region
- Do not announce every data point — announce the summary ("Dashboard updated.
  On-time delivery: 91%, down 2 points from last refresh.")
- `aria-live="assertive"` only for threshold violations that require immediate action

### Color + Shape Redundancy Rule

Any chart encoding that uses color to distinguish categories MUST also use
a second encoding channel:
- Shape (circle vs. square vs. triangle for scatter plot series)
- Pattern (solid vs. dashed vs. dotted for line series)
- Direct label (text label on each mark removes color dependency)

This satisfies WCAG 1.4.1 (Use of Color) and supports deuteranopia users.

Cross-link to `a11y-visual` for full WCAG color requirements and APCA
contrast guidance.

---

## SVG vs. Canvas Trade-Offs

### SVG

- **Accessible**: each element is a DOM node; `<title>` and `<desc>` are supported
- **Styleable**: CSS, DS tokens, Figma-inspectable
- **Performant limit**: degrades at ~5,000 DOM nodes; full charts with many marks
  should not use SVG at high data densities
- **Best for**: bar charts, line charts, small-n scatter plots, most standard charts
  in enterprise DS context

### Canvas

- **Fast**: 2D canvas handles 50,000+ marks without layout thrashing
- **Not accessible**: no DOM nodes; requires ARIA overlay for accessibility
- **Not styleable by CSS**: colors and fonts must be drawn programmatically
- **Best for**: large scatter plots, real-time animated charts, heatmaps at scale

**Accessibility requirement for Canvas**: an ARIA overlay describing the chart
plus a visually-hidden data table providing the same data in text form.

### WebGL (via deck.gl, regl, or Three.js)

- **Very fast**: GPU-accelerated; handles millions of points
- **Not accessible without ARIA overlay**
- **Use when**: n > 50,000 marks; geographic point clouds; real-time 3D visualization
- **Never for standard business charts** — the implementation cost is not justified

**Decision:**
- Standard chart, n < 5,000 marks: SVG
- Heatmap or scatter, n 5,000–50,000: Canvas
- Geographic point cloud or n > 50,000: WebGL (deck.gl)

---

## Cross-Links

- **`infod-encoding-theory`** — data color scale tokens must be defined in OKLCH;
  colorblind-safe categorical palette rules; preattentive emphasis for status encoding
- **`infod-statistical-viz`** — chart anatomy varies by chart type; axis requirements
  differ between bar, line, scatter; empty state message depends on chart type
- **`infod-dashboard-patterns`** — KPI card as a chart component; dashboard loading
  state patterns; filter state persistence
- **`infod-narrative-design`** — annotation layer design; chart title as editorial;
  subtitle as narrative context
- **`ds-advisor`** — data color scale tokens integrate with the main DS token system;
  naming conventions; Figma variable structure; token tier (global → alias → component)
- **`fe-data-visualization`** — SVG/Canvas/WebGL rendering implementation; library
  selection; performance optimization at large data scales
- **`fe-component-architecture`** — chart component API surface; variant/state coverage;
  prop interface design for chart components
- **`a11y-visual`** — WCAG 1.4.1 (Use of Color), 1.4.3 (Contrast), 1.4.11 (Non-text
  Contrast); colorblind simulation tools; APCA contrast for data-on-background
- **`fe-accessibility`** — ARIA implementation for chart components; focus management
  for interactive charts; keyboard interaction patterns

---

## References

- WCAG 2.2 — 1.4.1 Use of Color; 1.4.3 Contrast; 1.4.13 Content on Hover or Focus
- Léonie Watson — "Accessible SVG" patterns: https://www.sitepoint.com/tips-accessible-svg/
- Amy Cesal — Writing alt text for data visualizations:
  https://medium.com/nightingale/writing-alt-text-for-data-visualization-2a218ef43f81
- ARIA Authoring Practices Guide — Chart and data visualization patterns
- deck.gl — accessibility layer docs: https://deck.gl/docs/developer-guide/accessibility
- Figma — variable token documentation for design systems
