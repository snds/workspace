---
name: infod-encoding-theory
description: >
  Visual encoding theory for data visualization: Bertin's 7 retinal variables,
  preattentive processing, Cleveland & McGill perceptual accuracy ranking, color
  palette typology (sequential, diverging, qualitative), perceptual uniformity
  (OKLCH vs. HSL), and colorblind-safe encoding. Use this spoke when decisions
  involve which encoding channel to use for which data type, whether a color
  scale is perceptually uniform, which encoding channels support parallel
  preattentive processing, how to design colorblind-safe visualizations, or
  how to use preattentive attributes to direct attention in dashboards.
hub: lead-information-designer
aliases: [infod-encoding-theory]
tier: spoke
domain: design
prerequisites: [lead-information-designer, found-color]
spec_version: "2.0"
---

# Encoding Theory

Specialist spoke for visual encoding decisions — the foundational layer of
information design. Covers how the human visual system processes graphical
encodings and which encodings are most effective for which data types.

Part of the `lead-information-designer` skill network.

---

## Domain Boundary

This spoke owns the **theory of visual encoding**: which channel to use, why,
and what the perceptual science says about its effectiveness.

- **Which chart type to use** → `infod-statistical-viz`
- **How to apply encoding in a dashboard layout** → `infod-dashboard-patterns`
- **Encoding in a specific chart component** → `infod-design-system-patterns`

---

## Bertin's 7 Retinal Variables

Jacques Bertin (1967) identified 7 visual properties that can be varied to
encode data. He distinguished between **selective** (can isolate a group),
**associative** (can group similar), **ordered** (implies rank), and
**quantitative** (implies quantity) properties.

| Variable | Selective | Associative | Ordered | Quantitative | Best For |
|----------|-----------|-------------|---------|--------------|----------|
| **Position** | Yes | Yes | Yes | Yes | Quantitative, ordinal, nominal |
| **Size** | Yes | No | Yes | Yes | Quantitative (with perceptual correction) |
| **Shape** | Yes | Yes | No | No | Nominal only |
| **Value** (lightness) | Yes | Yes | Yes | Partial | Ordinal; quantitative in limited range |
| **Color hue** | Yes | Yes | No | No | Nominal only — cannot encode quantity |
| **Orientation** | Yes | Yes | No | No | Nominal; directional data |
| **Texture** | Yes | Yes | No | No | Nominal; fallback when color unavailable |

**Critical implication**: Color hue is purely nominal. When a designer uses a
rainbow color scale to encode quantitative data, they are using a nominal-only
channel for a quantitative task. The result is a chart that cannot be read
accurately without the legend.

### Effectiveness Ranking by Data Type

For **quantitative** data (numeric values, magnitudes):
1. Position (most accurate)
2. Length
3. Size (area, with perceptual scaling)
4. Value/lightness (in a narrow range)

For **ordinal** data (ranked categories, Likert scales):
1. Position
2. Value/lightness (sequential color scale)
3. Size

For **nominal** data (unranked categories):
1. Position (spatial separation)
2. Color hue (up to 8 distinguishable categories)
3. Shape (up to 6 easily distinguishable shapes)
4. Texture (fallback)

---

## Cleveland & McGill Perceptual Accuracy Ranking (1984)

Cleveland and McGill's foundational experiment established the relative accuracy
of graphical perception tasks — how well humans can extract quantitative
information from different visual encodings.

**Ranked from most to least accurate:**

1. **Position on a common scale** — bar chart, dot plot, scatter plot aligned to
   a shared axis; highest accuracy
2. **Position on non-aligned scales** — multiple plots sharing a scale but not
   aligned (e.g., small multiples with separate but equivalent axes)
3. **Length** — bar length independent of a zero baseline
4. **Direction / Angle** — line slope in a slope chart; angle in a pie slice
5. **Area** — bubble chart, treemap; systematically underestimated
6. **Volume** — 3D charts; severely inaccurate; almost never appropriate
7. **Color saturation** — heatmap cell intensity; rough ordinal distinctions only
8. **Color hue** — categorical only; not suitable for quantitative estimation

**Design implication from this ranking:**

- Use bar charts (position + length) when quantitative accuracy matters
- Use bubble charts (area) only when a rough magnitude impression is sufficient
- Avoid pie charts (angle) when precise comparison is needed — use bar charts
- Never use 3D charts for quantitative data; the depth distortion makes accurate
  reading impossible
- Heatmaps are appropriate when ordinal grouping is the goal (hot/warm/cool),
  not when precise values must be read

---

## Preattentive Processing

Some visual properties are processed **preattentively** — in parallel across
the visual field, before conscious attention is directed. They "pop out" without
searching. Others require **serial** processing — the eye must scan.

### Preattentive Attributes (parallel, ~150ms detection)

| Attribute | Effect | Design Use |
|-----------|--------|------------|
| **Color hue** | One different hue pops out in a field of others | Highlight an anomaly; categorize with max ~4 hues for clear pop |
| **Color saturation/value** | A brighter or darker element pops out | Mark a threshold violation; indicate status |
| **Size** | A larger element pops out | Emphasize the primary metric; signal magnitude difference |
| **Orientation** | A rotated element pops out | Indicate direction change; useful for scatter plots with direction data |
| **Shape** | A different shape pops out | Distinguish a special category from a uniform field |
| **Enclosure** | A visually grouped set pops out | Group related metrics in a dashboard; use a bounding box sparingly |
| **Motion** | A moving element pops out powerfully | Use sparingly; motion is cognitively demanding; never for ambient status |

### Serial Attributes (attentive, require scanning)

Length, area, angle, and color hue differences within a category all require
serial comparison — the viewer must look at each element in turn to compare.
This is not a failure; it is appropriate for exploratory charts where the user
is expected to investigate. It is inappropriate for dashboards where the
five-second rule applies.

### Application in Enterprise Dashboards

Design principle: **use at most one preattentive attribute per visualization
for emphasis**. Using two or more creates competition ("which pop-out should I
look at first?") and eliminates the pop-out effect for both.

Common patterns:
- A red KPI card in a field of green/neutral cards — status via color saturation
- A larger number in a KPI card hierarchy — primary metric via size
- An outlined element in a field of filled elements — exception via shape

---

## Color Palette Typology

### Sequential Palettes
Use for **quantitative data with a natural zero or low end**: population, revenue,
quantity on hand, days late. Values increase along one dimension.

- Lightness should increase monotonically from light (low) to dark (high)
- Appropriate for: choropleth maps, heatmaps, single-metric gradient tables

**Example sequences**: Blues, Greens, YlGnBu, Oranges (ColorBrewer)

Rule: Never use a sequential palette for categorical data. The implied ordering
will suggest a rank that doesn't exist.

### Diverging Palettes
Use for **quantitative data with a meaningful midpoint**: variance from plan,
temperature deviation, positive/negative margin, change scores (gain vs. loss).

- Two hues diverge from a neutral midpoint (white, light gray, or light beige)
- Lightness should be equal at equal distance from the midpoint
- The midpoint must have a real meaning (zero, plan, a threshold)

**Example diverging**: RdBu, PiYG, BrBG (ColorBrewer)

Anti-pattern: using a diverging scale when there is no meaningful midpoint. A
revenue chart with a blue-to-red diverging scale from $0 to $1M implies that
$500K is a benchmark — it is not.

### Qualitative Palettes
Use for **categorical (nominal) data**: product categories, regions, business
units, status types.

- Hues should be perceptually equidistant in appearance
- Maximum 8 categories with reliable visual distinction; more than 8 requires
  redundant encoding (shape, pattern) or grouping
- Do not use lightness variation within a qualitative palette — it implies ranking

**Example qualitative**: Set1, Set2, Paired (ColorBrewer)

### ColorBrewer Guidance

ColorBrewer (Brewer, 2003; colorbrewer2.org) is the standard reference for
cartographic and data color palettes. Every palette is tested for:
- Photocopy-safe (lightness-distinguishable in grayscale)
- Colorblind-safe variants are marked explicitly

Use the print-safe and colorblind-safe flags when selecting palettes for
enterprise products that will be screenshot-shared and accessible.

---

## Perceptual Uniformity: OKLCH vs. HSL

### The HSL Problem

HSL (hue, saturation, lightness) is a convenient color model for specifying
colors programmatically. It is **not perceptually uniform**. Two colors at the
same HSL lightness value appear dramatically different in perceived brightness:
yellow at L=50% appears far brighter than blue at L=50%. A color scale defined
in HSL with uniform lightness steps will produce uneven perceptual steps — some
transitions appear large, others small.

For data color scales, uneven perceptual steps are a design failure: the viewer
will perceive differences in the data where the data doesn't have them, and miss
differences where it does.

### OKLCH — Perceptually Uniform by Design

OKLCH (Lightness, Chroma, Hue — OK color space, 2020) is a perceptually uniform
polar color model. Equal steps in L produce equal perceived steps in brightness.
Equal steps in C produce equal perceived steps in saturation. This makes it the
correct model for constructing data color scales.

**Why OKLCH for data palettes:**
- Sequential scales with equal L steps produce even perceptual gradients
- Diverging scales can be constructed with guaranteed symmetry
- Colorblind simulation is more reliable (distance in OKLCH approximates
  perceptual distance in CVD-affected vision better than HSL)

**Practical use:** Define data color scale endpoints and midpoints in OKLCH.
Interpolate in OKLCH. Export to hex for implementation. Do not interpolate in
HSL — the perceptual warping will appear as a muddy band in the middle of the
gradient.

CSS Color Level 4 supports `oklch()` natively; modern browsers support it.
Tokens defined in OKLCH should be accompanied by hex fallbacks.

---

## Colorblind-Safe Encoding

Approximately 8% of males and 0.5% of females have some form of color vision
deficiency (CVD). The most common type is red-green deficiency (deuteranopia,
protanopia). Blue-yellow deficiency (tritanopia) is rare but must be considered.

### Rules for Colorblind-Safe Encoding

1. **Never use red and green as the only distinction** for meaningful categories.
   Red and green are indistinguishable to deuteranopes (the most common CVD type).
   This is the most common violation in enterprise dashboards (status indicators,
   gain/loss charts).

2. **Use hue + lightness + shape redundancy.** If two categories must be
   distinguishable, encode the distinction in at least two channels: hue AND
   lightness AND/OR shape. A red circle and a green circle fail. A dark-red
   circle and a light-green triangle pass (three redundant channels).

3. **Safe alternative to red/green:** Use blue/orange (diverging: OKL-safe),
   or teal/red with lightness separation. The ColorBrewer "colorblind safe"
   palettes are tested against deuteranopia simulation.

4. **Test with CVD simulation:** Tools — Figma's built-in accessibility view,
   Stark plugin, Adobe Color's accessibility checker, Coblis.

5. **Status indicators (good/warning/error):** Use color + icon + text label
   redundantly. Never color alone for status.

Cross-link to `a11y-visual` for full accessibility treatment including
APCA contrast ratio guidance for text-on-data-color backgrounds.

---

## Preattentive Emphasis Patterns for Enterprise Dashboards

### The Single Emphasis Rule
Choose **one** preattentive attribute per dashboard view for primary emphasis.
Use it consistently for the same semantic meaning (e.g., red saturation always
means "below threshold"). Using multiple pop-out attributes in one view for
different meanings destroys the hierarchy.

### Threshold / Status Pattern
Common in operational dashboards:

| Condition | Encoding | Avoid |
|-----------|----------|-------|
| On track | Neutral (no emphasis — noise reduction) | Green everywhere is noise |
| Warning | Amber + icon | Color alone |
| Below threshold | Red saturation increase + icon + text | Red/green without lightness diff |
| Exceptional performance | Positive accent hue + bold label | Too many accent states |

The design goal: **make the exception visible, not the rule.** If everything is
colored, nothing is emphasized.

### Annotation as Preattentive Guidance
A well-placed annotation (callout line + label) directs the reader's attention as
effectively as a preattentive attribute — with the added benefit of explaining
what to notice and why. Route to `infod-narrative-design` for annotation strategy.

---

## Cross-Links

- **`infod-statistical-viz`** — encoding theory determines which chart types are
  perceptually appropriate; consult when selecting chart type
- **`infod-dashboard-patterns`** — preattentive emphasis rules apply directly to
  dashboard KPI card design and status encoding
- **`infod-design-system-patterns`** — data color scale tokens must be defined in
  OKLCH and verified for colorblind safety before tokenization
- **`infod-spatial-maps`** — sequential and diverging palette selection is
  critical for choropleth maps; Flannery correction for proportional symbol size
- **`a11y-visual`** — colorblind-safe encoding, APCA contrast for data
  visualizations, accessible status indicators
- **`ds-advisor`** — token architecture for data color scale tokens that integrate
  with the main design system
- **`lead-data-scientist`** — metric semantics inform whether a sequential or
  diverging palette is appropriate (diverging requires a meaningful midpoint)

---

## References

- Jacques Bertin — *Semiology of Graphics* (1967/1983)
- Cleveland & McGill — "Graphical Perception: Theory, Experimentation, and Application" (1984)
- Cynthia Brewer — ColorBrewer 2.0: https://colorbrewer2.org/
- Björn Ottosson — OKLCH specification and rationale: https://bottosson.github.io/posts/oklab/
- CSS Color Level 4 — oklch() specification
- Ware, Colin — *Information Visualization: Perception for Design* (4th ed., 2020)

## Related
- foundation → [[found-color]]
- hub → [[lead-information-designer]]
