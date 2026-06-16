---
name: infod-narrative-design
description: >
  Data narrative and storytelling design: Wattenberg/Viégas narrative visualization
  framework, scrollytelling, annotation strategy, Tufte's data-ink ratio, chart junk
  critique, story structure for data, executive communication patterns (waterfall,
  before/after, benchmark comparison), and the annotation-replaces-legend principle.
  Use this spoke when structuring a data story, designing annotation layers, evaluating
  data-ink ratio, designing executive charts, or deciding whether scrollytelling is
  appropriate for a given context.
hub: lead-information-designer
---

# Narrative Design

Specialist spoke for data storytelling, editorial annotation, and data-ink discipline.
Part of the `lead-information-designer` skill network.

---

## Domain Boundary

This spoke owns **how data is communicated as a story** — structure, annotation,
editorial framing, and the visual reduction that makes meaning visible.

- **Which chart type to use** → `infod-statistical-viz`
- **Dashboard layout and hierarchy** → `infod-dashboard-patterns`
- **Encoding channels and color** → `infod-encoding-theory`
- **Executive-facing product design** → this spoke + `infod-dashboard-patterns`

---

## Narrative Visualization Framework

Wattenberg and Viégas (with Segel, 2010) identified a spectrum of narrative
visualization structures from author-driven (linear, fixed) to reader-driven
(open exploration). Enterprise visualization sits mostly in the middle.

### The Author/Reader Spectrum

```
Author-driven ←──────────────────────────────→ Reader-driven
(fixed story;      (guided story;                (open exploration;
 no interaction)    some interaction)              full control)

  Magazine         Martini Glass              Interactive Dashboard
  infographic      Slideshow                  Data Tool
                   Drill-down Story
```

### The Three Narrative Structures

**Martini Glass**
- Linear story (stem) → open exploration (glass)
- The reader follows a guided narrative, then is released into an interactive tool
- Use for: product feature introductions, onboarding flows with data, executive
  presentations that end with an exploration interface
- Structure: 3–7 authored screens/states → interaction enabled → user explores

**Interactive Slideshow**
- A sequence of authored states, each a chart + annotation combination
- The reader clicks through; each slide advances a sub-argument
- Use for: quarterly business reviews, executive briefings, investor decks
  that become a web page
- Structure: Situation → Complication → Data Evidence → Resolution → Call to Action

**Drill-Down Story**
- Overview → detail; the narrative is in the structure of the hierarchy
- Each level reveals more detail, supporting the headline claim
- Use for: enterprise dashboards with drill-down; investigation workflows
- The annotation at each level advances the interpretation

### When Scrollytelling is Wrong for Enterprise SaaS

Scrollytelling (scroll-driven animation with figure/text sync) is appropriate
for longform journalism and data reports. It is **almost always wrong** for
enterprise SaaS dashboards:

- Operational users need fast access to current state; scroll-driven reveals
  create latency before the data is visible
- Enterprise users return to dashboards repeatedly; scrollytelling rewards
  first-time readers, not power users
- Mobile enterprise use is already constrained; scrollytelling degrades further
- Implementation cost is high; maintenance cost is higher

**When scrollytelling is appropriate in enterprise:** onboarding walkthrough of
a new feature; an annual/seasonal report that is read once; a data story embedded
in a marketing or communication context.

For engineering implementation when scrollytelling is warranted: use Intersection
Observer API to trigger figure transitions as the prose scrolls; maintain figure
state while prose is in the corresponding scroll zone.

---

## Annotation Strategy

Annotations are the editorial layer. They are not decoration — they are the
designer's explicit statement about what the chart means. They replace the work
that a caption would do in a magazine, directly within the chart.

### Three Annotation Types

**Data callout (point annotation)**
- Points to a specific data element: a peak, a threshold crossing, an outlier
- Contains: the data value + a brief interpretation
- Format: short leader line + small bold label
- Example: "March peak: $4.2M — highest since 2019 due to spring launch"
- Rule: only annotate data points that are part of the story. Annotating
  every point is labeling, not annotation.

**Contextual annotation (encoding explanation)**
- Explains an encoding choice that the reader might not decode automatically
- Example: "Bubble size = order quantity" near the legend-less bubble chart
- Placed near the first instance of the encoding, in muted type
- Often replaces the legend

**Editorial annotation (interpretive)**
- States the takeaway: what does this data mean for the reader?
- Example: "EMEA accounts for 67% of margin decline" as a callout box
- Can be placed in the chart subtitle, a callout card, or as an annotation overlay
- This is the designer's judgment, rendered visible — it requires that the
  designer actually understands the data

### The Annotation Replaces the Legend Principle

A legend requires a lookup: find element → look at legend → decode meaning → return.
An annotation eliminates the lookup by putting the meaning at the element.

**Default behavior**: Direct label series, categories, and data callouts.
**Use a legend when**: direct labeling creates visual conflicts (e.g., tightly
clustered multi-series line chart where end labels overlap).

When a legend is unavoidable:
- Place it immediately adjacent to the relevant chart element, not in a corner
- Reduce the visual weight of the legend (small type, muted color)
- Never make the legend the largest text element in the chart

---

## Data-Ink Ratio

Tufte (1983) defines data-ink ratio as:

```
Data-ink ratio = data ink / total ink used to print the graphic
```

The principle: maximize the proportion of ink (or pixels) devoted to
representing data. Minimize "chartjunk" — ink that does not encode data.

### Chartjunk Categories (with Critique)

**Non-data gridlines**
- Heavy gridlines that compete with data marks for visual attention
- Fix: reduce opacity to ~15–20%; use dotted lines; or remove entirely where
  direct labels make them redundant

**Redundant labels**
- Labeling every bar when the axis is sufficient; repeating the chart title in
  the subtitle
- Fix: label selectively (the highest, the lowest, the annotated outlier)

**Decorative fills**
- Patterned fills, gradients, and drop shadows on chart marks
- Fix: flat solid colors; no drop shadows on chart marks

**3D effects**
- 3D bars, 3D pies, perspective — introduce visual distortion and add no information
- Fix: use 2D equivalents without exception

**Superfluous borders and frames**
- Bounding boxes around chart areas; redundant tick marks with gridlines present
- Fix: remove chart frame; use axis lines only where necessary

**Moiré vibration**
- Hatching, cross-hatching, and dense repetitive patterns in fills
- Fix: use solid color fills; use color or lightness for distinction

### When Decoration Is Justified

The data-ink ratio principle is not an absolute law. Two legitimate exceptions:

**Engagement and memorability**: There is evidence (Bateman et al., 2010) that
"embellished" charts — those with relevant imagery — are remembered better than
bare charts. In consumer-facing or non-expert contexts, a modest amount of visual
interest is justified if it aids retention.

**Brand identity in published reports**: Marketing and executive reports where
brand consistency matters can support a styled visual language that diverges
from bare minimalism, as long as the data is still accurately readable.

**The test**: Does the decorative element impede reading the data? If yes, remove
it. If no, the judgment call depends on context.

---

## Story Structure for Data

### Situation-Complication-Resolution (SCR)

The McKinsey SCR framework applies directly to data narratives:

- **Situation**: What is the context? "We have 12% YoY revenue growth."
- **Complication**: What is the problem or tension? "But margin declined 3 pts."
- **Resolution**: What do we do? "The margin decline is concentrated in EMEA
  fashion, driven by logistics costs. See recommendation."

Applied to a dashboard or report, the structure becomes:
- Primary metric shows the situation
- Context line shows the complication (vs. target, vs. prior period)
- Annotation names the cause; drill-down shows the resolution path

### The One-Chart Story

When a presentation or report has one central claim, one chart should carry it.

Design principle: write the headline first ("Margin declining in EMEA, accelerating
in APAC"), then design the chart that makes that headline obvious without reading it.
If the chart doesn't make the headline visible, change the chart or the headline.

### Multi-Chart Narrative Sequencing

For presentations or report pages with multiple charts:

1. **Overview → detail**: Start with the summary metric, then show the breakdown
2. **Problem → cause → solution**: Each chart advances one element of the argument
3. **Comparison before detail**: Show the comparison (plan vs. actual) before the
   breakdown of what drove it
4. **End with the ask**: The final chart supports the recommendation

Rule: every chart in a sequence should advance the narrative. If a chart could be
removed without losing the thread of the argument, remove it.

---

## Executive Communication Patterns

### The Waterfall Chart as Narrative Device

The waterfall chart shows how a starting value reaches an ending value through
a series of positive and negative contributions. It is the canonical chart for:
- Revenue bridge: "How did we go from $10M plan to $8.7M actual?"
- Margin walk: "Where was margin gained and lost?"
- Headcount change: "How did we get from 200 to 215 employees?"

**Design requirements:**
- Starting bar: absolute value, anchored at zero
- Intermediate bars: floating (start from the previous endpoint, not zero)
- Final bar: absolute value, anchored at zero; visually distinct (bold or different pattern)
- Color: positive contributions = one color; negative = another (colorblind-safe pair)
- Label: each bar labeled with the delta value and optionally the end value
- Always sort: by magnitude (largest contributor first) unless a chronological
  order tells a better story

**Anti-pattern**: using a standard bar chart to show contributions — the lack
of floating anchors destroys the addition/subtraction structure.

### Before/After Comparison

- Two columns: "Before" state and "After" state, for the same set of metrics
- Use a slope chart (two-period line chart) when the metric count is moderate (5–10)
- Use a table with directional indicators when the metric count is high (>10)
- Never: two separate pie charts for before/after — proportions across charts
  cannot be accurately compared

### Benchmark Comparison

- Shows how a value compares to a reference: industry benchmark, competitor,
  historical average, plan
- Design: the benchmark value should be visually secondary (reference line or bar
  in light gray) while the actual value is visually primary
- Label the benchmark explicitly: "Industry average: 72%"
- Never show a benchmark without explaining what it represents and its source

---

## Cross-Links

- **`infod-encoding-theory`** — preattentive attributes as annotation-like
  emphasis tools; color in annotation callouts must follow encoding theory rules
- **`infod-statistical-viz`** — annotation strategy by chart type; the waterfall
  chart taxonomy; when to use a slope chart vs. a bar chart for comparison
- **`infod-dashboard-patterns`** — editorial annotation in dashboard context;
  the executive dashboard as a narrative structure
- **`infod-design-system-patterns`** — annotation layer as a DS component;
  chart title and subtitle typographic spec
- **`lead-data-scientist`** — the data story must accurately represent what the
  data says; `ds-executive-storytelling` defines what the story is; this spoke
  designs how to tell it visually
- **`ux-interaction-design`** — scrollytelling intersection observer implementation
  when it is warranted

---

## References

- Edward Tufte — *The Visual Display of Quantitative Information* (1983)
- Edward Tufte — *Envisioning Information* (1990)
- Segel & Heer — "Narrative Visualization: Telling Stories with Data" (2010)
- Wattenberg & Viégas — narrative visualization research body
- Barbara Minto — *The Pyramid Principle* (SCR framework origin)
- Bateman et al. — "Useful Junk? The Effects of Visual Embellishment on
  Comprehension and Memorability of Charts" (CHI 2010)
- Cole Nussbaumer Knaflic — *Storytelling with Data* (2015)
