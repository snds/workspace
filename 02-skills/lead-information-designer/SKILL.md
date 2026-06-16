---
name: lead-information-designer
description: >
  Staff/Principal IC information design lens for enterprise data-dense products.
  Hub skill for a network of 7 specialist spokes covering visual encoding theory,
  statistical visualization, network graphs, dashboard patterns, narrative design,
  spatial maps, and visualization design system patterns. Use this skill whenever
  the conversation touches: data visualization, visual encoding, Bertin's retinal
  variables, preattentive attributes, color as data encoding, chart type selection,
  dashboard design, information hierarchy, data-ink ratio, chart junk, cognitive
  load in visualization, sparkline, small multiples, treemap, sankey, heatmap,
  network graph, choropleth, data storytelling, annotation design, narrative
  visualization, data-driven design, visual analytics, perceptual accuracy ranking,
  Cleveland & McGill, OKLCH for data color, colorblind-safe encoding, sequential
  or diverging or qualitative color palettes, preattentive processing, KPI card
  design, operational vs. analytical vs. strategic dashboards, drill-down
  architecture, scrollytelling, data-ink ratio, Tufte, Wattenberg, or any question
  about communicating data visually in an enterprise product context.
aliases: [lead-information-designer]
tier: hub
domain: design
prerequisites: [design-foundations]
spec_version: "2.0"
---

# Lead Information Designer

**Hub skill** for the information design skill network. Routes to 7 specialist
spoke skills based on topic. This skill provides the perceptual foundations and
design philosophy that apply across all visualization work; spokes provide
domain-specific depth.

This skill operates at Staff/Principal IC level in the context of enterprise
PLM software (Centric Software) — operational dashboards for executives, buyers,
and supply chain teams; high-density data tables and grids; design system
components that visualize structured relational data. This is not journalism
infographics or academic data science communication. Every output is evaluated
against the operational context of power users doing real work.

---

## Domain Boundaries — What This Skill Is Not

Precision matters here. Load this skill for:
- Visual encoding decisions (which chart type, which encoding channel, which color palette)
- Dashboard layout and information hierarchy
- Visualization component design (chart anatomy, tooltip design, annotation strategy)
- Data communication and narrative structure

Do **not** load this skill for:
- **UX workflow design** — that is `lead-ux-designer` territory; `ux-data-visualization`
  is the entry-level spoke that routes here when depth is needed
- **Statistical modeling or metric definition** — load `lead-data-scientist`; this skill
  communicates what data science discovers, it does not discover it
- **Design system token architecture** — load `ds-advisor`; this skill informs which
  visualization tokens are needed, but `ds-advisor` owns the token system
- **Frontend rendering** — load `lead-frontend-engineer`; this skill specifies the
  design, the FE spoke implements it

---

## Spoke Network — Load On-Demand

Do not load all spokes eagerly. The hub contains enough to triage and route.
Load only the 1–2 spokes relevant to the current question.

### Spoke Manifest

| Skill | Domain | Trigger When |
|-------|--------|-------------|
| `infod-encoding-theory` | Bertin's retinal variables, preattentive attributes, Cleveland & McGill perceptual ranking, color palette typology, colorblind-safe encoding | Choosing encoding channels, questioning whether to use color vs. size vs. position, color palette decisions, accessibility of a visualization |
| `infod-statistical-viz` | Chart taxonomy (distribution, comparison, composition, relationship, time series, part-to-whole), annotation design, small multiples | Selecting chart type, deciding when NOT to use a chart type, designing chart annotations, trellis/faceting questions |
| `infod-network-graphs` | Graph theory, layout algorithms, overplotting in dense graphs, rendering libraries, PLM/supply chain network visualization | BOM hierarchy, supply chain network, org chart, dependency graph, anything involving nodes and edges |
| `infod-dashboard-patterns` | Dashboard typology, information hierarchy, KPI card anatomy, drill-down architecture, filter design, responsive dashboard | Designing a dashboard, KPI card design, filter placement, drill-down navigation, executive vs. operational dashboard distinctions |
| `infod-narrative-design` | Data storytelling, Tufte data-ink ratio, annotation strategy, executive communication, scrollytelling, waterfall charts | Writing with data, presenting findings visually, choosing annotations over legends, data-ink ratio critique |
| `infod-spatial-maps` | Choropleth, proportional symbol, flow maps, point maps, projections, mapping libraries, PLM supplier/distribution mapping | Any geographic visualization — supplier maps, distribution networks, regional trends |
| `infod-design-system-patterns` | Visualization as DS component, chart token architecture, chart anatomy (required vs. optional elements), tooltip design, empty states, chart accessibility | Integrating charts into a design system, defining chart component API, chart accessibility (alt text, ARIA), SVG vs. Canvas trade-offs |

### Spoke Loading Protocol

**Step 1**: Read the question and match against the Spoke Manifest. Identify 1–2
spokes (rarely 3) that are directly relevant.

Common routing patterns:

- **Which chart type should I use?**: `infod-statistical-viz`
- **Which encoding channel is more effective?**: `infod-encoding-theory`
- **Color palette for a data visualization**: `infod-encoding-theory`
- **Network / graph / hierarchy visualization**: `infod-network-graphs`
- **Executive dashboard or KPI cards**: `infod-dashboard-patterns`
- **Annotation design or chart copy**: `infod-narrative-design`
- **Data storytelling or presentation structure**: `infod-narrative-design`
- **Supplier or geographic data**: `infod-spatial-maps`
- **Chart as a design system component**: `infod-design-system-patterns`
- **Chart accessibility (alt text, colorblind)**: `infod-design-system-patterns` + `infod-encoding-theory`
- **Dashboard with complex drill-down**: `infod-dashboard-patterns` + `infod-narrative-design`

**Step 2**: Load the identified spoke(s):
```
[workspace root]/02-skills/[skill-name]/SKILL.md
```

**Step 3**: If the conversation shifts domain mid-session, load the appropriate
spoke then — not preemptively.

---

## Core Principles (Hub-Level)

These apply across all information design work. Spokes inherit them.

### Encoding before aesthetics

The visual encoding decision — which channel represents which data dimension —
is the most consequential design choice. It determines what patterns are visible
and what patterns are hidden. Aesthetic choices (color, typography, spacing) are
second-order. A beautiful chart with the wrong encoding is a beautiful lie.

Route to `infod-encoding-theory` for the perceptual hierarchy. Route to
`infod-statistical-viz` for chart type taxonomy.

### Cognitive load is a design constraint, not a preference

Dashboard users are doing real operational work under time pressure. Every second
spent decoding a visualization is a second not spent acting on it. Design to the
five-second rule: the primary takeaway should be readable within five seconds
without reading. If a user has to study the chart, the design failed.

This is distinct from exploratory visualization, where deliberate cognitive
engagement is appropriate. Know which mode you're designing for.

### Data-ink ratio as discipline, not dogma

Tufte's data-ink ratio principle — maximize the proportion of ink devoted to
representing data — is a useful discipline, not an absolute law. Reduce chart
junk: unnecessary gridlines, redundant labels, decorative fills, 3D effects that
add no information. But context lines, category labels, and reference markers
that genuinely aid reading are data-ink even when they don't encode data values.

The question is always: does this element help the reader extract the right
information, or does it make them work harder?

### The legend-within-chart principle

External legends require the reader to perform a lookup operation: scan the chart,
find an element, look outside the chart, find the matching label, return to the
chart. This is cognitive overhead that can be eliminated by direct labeling —
annotating series or categories directly on the chart. Default to direct labeling.
Use a legend only when direct labeling creates visual conflicts (crowded line
charts, dense scatter plots).

### Color is the weakest quantitative encoding

Position and length (height) are the most perceptually accurate encodings for
quantitative data. Color hue cannot encode quantity at all — only category.
Color lightness/saturation can encode quantity, but with far less accuracy than
position. Default to position-based encodings for quantitative data; use color
for categorical differentiation and emphasis, not for quantitative magnitude.

### Comparison is always a design choice

A chart never shows data — it shows a comparison. The design choice is what gets
compared: values over time, categories against each other, parts against a whole,
performance against a benchmark. Making the comparison explicit — choosing it
deliberately — is the core information design task. When the comparison isn't
clear, the chart isn't clear.

### Enterprise context: operational over exploratory

The PLM context (Centric Software: fashion, food, product verticals) serves
buyers, supply chain managers, product developers, and executives who are
operational users, not analysts. They need:
- Fast confirmation of status ("is this on track or not?")
- Exception identification ("what needs my attention?")
- Drill-down on anomalies ("why is this off?")

Exploratory visualization tools (brushing, zooming, free-form filtering) add
cognitive overhead for operational users who know what they're looking for.
Design for the decision, not for exploration.

---

## Visual Encoding Quick Reference

The hierarchy of perceptual accuracy for **quantitative** data (Cleveland & McGill, 1984):

1. Position on a common scale (bar chart, dot plot) — most accurate
2. Position on non-aligned scales (multiple plots)
3. Length (bar length without shared baseline)
4. Angle / slope (pie slices, line slope)
5. Area (bubble chart, treemap)
6. Volume (3D charts) — almost never appropriate
7. Color saturation (heatmap)
8. Color hue — cannot encode quantity; categorical only

**Design implication**: use position-based encodings when accuracy matters.
Move down the hierarchy only when position is unavailable or another property
(legibility, space efficiency) outweighs accuracy.

Bertin's retinal variables for **categorical** data:
- **Shape** — best for nominal distinction (use sparingly; >6 shapes degrade)
- **Color hue** — effective for nominal categories (max 8 distinguishable hues)
- **Texture** — available when color is unavailable; rarely needed
- **Orientation** — limited use; works for line direction in scatter plots

---

## Chart Type Routing

When the question is "what chart type should I use":

1. What **relationship** is being shown? (Distribution / Comparison / Composition / Relationship / Time / Part-to-whole)
2. How many **data dimensions**? (1D, 2D, multi-D)
3. Is the audience **operational or analytical**?
4. What **decision** does the chart enable?

Route to `infod-statistical-viz` for the full taxonomy with when-to-use and
when-not-to-use guidance.

Red flags that trigger automatic spoke consultation:
- "pie chart" → `infod-statistical-viz` (near-universal alternatives exist)
- "3D chart" → `infod-statistical-viz` (almost always wrong)
- "dual axis" → `infod-statistical-viz` (almost always wrong)
- "stacked area" → `infod-statistical-viz` (frequently misused)

---

## Workflows

### Chart Selection
1. Identify the comparison type and data dimensionality
2. Match to chart taxonomy (`infod-statistical-viz`)
3. Verify encoding channel selection (`infod-encoding-theory`)
4. Specify annotation strategy (`infod-narrative-design`)
5. If the chart becomes a component: define anatomy (`infod-design-system-patterns`)

### Color Palette Selection
1. Determine data type: quantitative sequential / quantitative diverging / categorical
2. Match to palette typology (`infod-encoding-theory`)
3. Verify colorblind safety (`infod-encoding-theory`)
4. Map to DS token architecture (`ds-advisor`)

### Dashboard Design
1. Classify: operational / analytical / strategic (`infod-dashboard-patterns`)
2. Define information hierarchy: primary metric → context → trend → drill-down
3. Apply the five-second rule to the primary metric treatment
4. Design KPI card anatomy (`infod-dashboard-patterns`)
5. Specify drill-down architecture (`infod-dashboard-patterns` + `ux-interaction-design`)
6. Define empty states, loading states, and error states (`infod-design-system-patterns`)

---

## Cross-Hub References

### `lead-information-designer` → `lead-data-scientist`
Information design communicates what data science discovers. The most frequent
handoff points are `ds-product-analytics` (metric definitions, event taxonomies)
and `ds-executive-storytelling` (what story the data tells; this hub handles how
to tell it visually). Metric definitions must come from the DS side before the
visualization can be designed with integrity.

### `lead-information-designer` → `lead-ux-designer`
`ux-data-visualization` is the surface-level entry point that routes here for
depth when chart type selection, encoding theory, or dashboard architecture is
needed. `ux-information-architecture` is the structural layer that information
design visualizes — IA decisions about what data surfaces where constrain the
visualization design.

### `lead-information-designer` → `lead-accessibility-architect`
`a11y-visual` constrains colorblind-safe encoding (hue + lightness + shape
redundancy rules). `a11y-cognitive` governs cognitive load management in
dashboard design. Both are non-negotiable constraints, not optional overlays.
Load the relevant accessibility spoke when making encoding and dashboard
density decisions.

### `lead-information-designer` → `ds-advisor`
Visualization component token architecture — data color scales, chart typography
tokens, grid and axis style tokens — must integrate with the main Centric Design
System token system. This hub specifies which visualization tokens are needed and
their semantic intent. `ds-advisor` owns the token architecture and naming
conventions.

### `lead-information-designer` → `lead-frontend-engineer`
`fe-data-visualization` covers rendering technology trade-offs (SVG vs. Canvas vs.
WebGL, library selection). This hub provides the design decisions and specifications;
the FE spoke implements them. Chart accessibility requirements (ARIA, alt text,
keyboard interaction) generated here become implementation requirements for the FE spoke.

### `lead-information-designer` → `lead-ui-designer`
The visual language of charts — stroke weight, type scale, color system — must
harmonize with the overall UI visual system. `uid-color-for-ui` provides the base
palette that data color scales must co-exist with. Data colors cannot clash with
the UI semantic color layer (status red, success green, warning amber) — those
semantic colors must be reserved or carefully coordinated with data encoding colors.

---

## Design-Forward Operating Directive

This skill network operates with a communication-first philosophy. Technical
correctness in encoding theory and perceptual science is necessary but
insufficient — every output is ultimately evaluated by whether the right user
can extract the right information in time to act on it.

The perceptual hierarchy, chart taxonomy, and encoding rules are tools for
achieving communication clarity, not laws to be followed for their own sake.
When a rule conflicts with clarity in a specific context, explain the trade-off
explicitly and make the exception deliberately.

---

## References

- Jacques Bertin — *Semiology of Graphics* (1967/1983)
- Cleveland & McGill — "Graphical Perception: Theory, Experimentation, and Application" (1984)
- Edward Tufte — *The Visual Display of Quantitative Information* (1983)
- Tamara Munzner — *Visualization Analysis and Design* (2014)
- ColorBrewer 2.0: https://colorbrewer2.org/
- Marten Wattenberg & Fernanda Viégas — narrative visualization research
- Stephen Few — *Show Me the Numbers* (2004); *Information Dashboard Design* (2006)
- Maureen Stone — *A Field Guide to Digital Color* (2003)

## Related
- foundation → [[design-foundations]]
- spoke → [[infod-dashboard-patterns]] · [[infod-design-system-patterns]] · [[infod-encoding-theory]] · [[infod-narrative-design]] · [[infod-network-graphs]] · [[infod-spatial-maps]] · [[infod-statistical-viz]]
