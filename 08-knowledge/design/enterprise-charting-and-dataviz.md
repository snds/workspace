---
tags: [design-system, charts, dataviz, enterprise-saas, plm, echarts, carbon-charts, recharts, filter]
created: 2026-09-09
updated: 2026-09-09
status: working
confidence: medium
sources:
  - "CDS packages/data-table chart feature (Recharts 2.15, chart-from-selection)"
  - "Workspace skills: lead-information-designer, infod-dashboard-patterns, infod-design-system-patterns, infod-encoding-theory, fe-data-visualization, visual-qa-dataviz"
  - "Apache ECharts, IBM Carbon Charts, Vega-Lite, Unovis, AG Charts, MUI X Charts, ApexCharts licensing (2026)"
related_skills: [ds-advisor, lead-information-designer, infod-design-system-patterns, infod-dashboard-patterns, fe-data-visualization]
related_projects: [02-centricPLM]
trigger_words:
  - chart
  - charting
  - data visualization
  - dataviz
  - echarts
  - recharts
  - carbon charts
  - crossfilter
  - brush
  - dashboard widget
  - KPI sparkline
  - status encoding
  - positive negative
  - success destructive
  - data color status
---

# Enterprise charting and data visualization — research brief (2026-09-09)

Opening research for Centric / CDS. Two product jobs, one design-system contract. **Do not pick a chart library first.** Spec the altitudes, the filter event, and the token family — then wrap an engine.

**Working recommendation:** one engine (Apache ECharts) behind a CDS facade, including the table-selection popover. Recharts is already in that popover because it was the cheap React default, not because ECharts cannot do a 320×208 overlay. Treat in-page charts as a **filter primitive** that writes the same filter model as a filter chip. **Fold Carbon Charts as a pattern source — never as a runtime dependency.** Carbon 1.x is in maintenance, EOL June 2027, 2.x unreleased; installing or forking it fails the dependency intake gate.

---

## The two jobs (do not collapse them)

**In situ (chart as filter).** A chart or widget sits on a list/detail page. Clicking a bar, a slice, a legend item, or a nested child (a stacked segment, a treemap cell, a brush range) filters the data table below. The chart is a **faceted control that happens to use marks**, not a dashboard decoration. The output must be the same thing a Filter Chip already represents: field + operator + values, visible, dismissible, combinable with other filters.

**Isolated (chart as insight).** A dashboard tile or a page-level viz that is not necessarily wired to a table on the same page. Still needs the same visual language, empty/loading/error states, and accessibility contract — but the interaction may stop at tooltip / highlight / drill-to-another-page rather than live table filtering.

A third, quieter job sits under both: **sparks inside KPI cards** — trend shape only, no axes, no library required.

These three altitudes share tokens and chrome. They do **not** share one React component tree.

| Altitude | Job | Interaction | Engine |
|---|---|---|---|
| **A · Spark** | Status at a glance on a KPI card | None (or click-the-card) | Inline SVG / CSS. No chart library. |
| **B · In-page filter widget** | Constrain the table (or sibling widgets) on this page | Click, legend, nested child, brush → `FilterIntent` | Product engine (ECharts) behind a CDS wrapper |
| **C · Dashboard / analytical** | Explore, compare, monitor — may or may not be data-linked | Tooltip, highlight, drill (panel / page), optional brush | Same engine as B; richer series types |

CDS today only has a **fourth** altitude that should stay small: **chart-from-selection** inside `@centric/data-table` (currently Recharts, dynamically imported, bar/line/pie/scatter). That is a power-user affordance on a cell range, not a second viz system. Keep the lazy-load fence. If ECharts is the product engine, swap the canvas inside that fence rather than keeping two libraries.

---

## What already exists (do not reinvent)

- **`@centric/data-table` chart feature** — Recharts `^2.15.4`, opt-in `./chart` export, `ChartCanvas` is the only file allowed to import Recharts, loaded via `import()`. Token placeholders `--chart-1`…`--chart-5` as HSL fallbacks. Shapes: bar, line, pie, scatter via `detectChartShape`.
- **TanStack Table** is the grid. Chart→table filtering should write table column filters (and/or a shared page filter store), not a parallel selection model.
- **Dashboard density / KPI strip work** already exists in centric-ui (`sizing: hug | fill`, KPI anatomy). Sparks belong there, not in the chart package.
- **Filter Chip** is landing in CDS. Chart selections must mint the same chips. If a bar click produces a filter the chip row cannot show, the interaction is unfinished.
- **Data color vs UI color** is still a gap. `--chart-1`…`5` are shadcn-style series slots, not a sequential / diverging / categorical / **status** token family. Status hues are reserved for **status-typed data** (see below). Using them on a nominal series (mills, seasons, regions) encodes false meaning.

---

## Status-typed encoding

Color in a chart is chosen by **what the data means**, not by chart type. CDS already has a status token family for UI (pills, alerts, buttons). Charts that plot status-typed content must use **that same family**, so a “success” bar, a success pill, and a success spark all read as one language.

The earlier blanket “never put `status/*` on a chart” was too coarse. The correct split:

| Encoding | The data is… | Color family | Status hues? |
|---|---|---|---|
| **Categorical (nominal)** | Unordered categories: mill, season, region, SKU | `data-color-categorical-1…8` | **Forbidden.** Green on “Italy” implies Italy is healthy. |
| **Sequential** | Magnitude with no good/bad: volume, count, intensity | `data-color-sequential-*` | **Forbidden.** |
| **Diverging, non-evaluative** | Two directions, no judgment: hot/cold | `data-color-diverging-*` (non-status hues) | **Forbidden.** |
| **Diverging, evaluative** | Signed outcome with polarity: vs plan, margin delta | Poles = `status/success` + `status/destructive`; midpoint = neutral | **Required at the poles.** |
| **Status (evaluative categories)** | The values *are* statuses: pass/fail, on-track/at-risk/blocked | `status/*` | **Required.** |

“Status-typed” is a **schema fact**, not a designer preference. A column, metric, or aggregate is status-typed when its documented meaning is evaluative — positive/negative, success/failure, healthy/at-risk, or any equivalent nomenclature. If the field is just a label that happens to include the word “red,” it is not status-typed.

### Canonical roles (bind to existing CDS tokens)

CDS docs name four contexts as **negative, positive, warning, info**. Tokens add **caution**. Charts use the same names. Do not invent a parallel “chart success green.”

| Role | Nomenclature we accept in data/docs | Token (mark fill) | Primitive | Soft pair (washes, small marks, stacked) | Text/line/spark on a surface |
|---|---|---|---|---|---|
| **Positive** | positive, success, pass, approved, complete, healthy, on track, on time, favorable | `status/success` / `--sem-success` | green-9 | `status/success/soft` (green-3) | `status/success/soft/foreground` (green-11) |
| **Negative** | negative, destructive, danger, error, fail, failed, rejected, blocked, overdue, critical, unfavorable | `status/destructive` / `--sem-destructive` | red-9 | `status/destructive/soft` (red-3) | `status/destructive/soft/foreground` (red-11) |
| **Warning** | warning, at risk, delayed, needs review, serious | `status/warning` / `--sem-warning` | orange-9 | `status/warning/soft` (orange-3) | `status/warning/soft/foreground` (orange-11) |
| **Caution** | caution, watch, minor, approaching threshold | `status/caution` / `--sem-caution` | yellow-9 | `status/caution/soft` (yellow-3) | `status/caution/soft/foreground` (yellow-11) |
| **Info** | info, informational, draft, not started, unknown, no status | `status/info` / `--sem-info` | cyan-9 (**not** brand blue) | `status/info/soft` (cyan-3) | `status/info/soft/foreground` (cyan-11) |
| **Neutral** | no evaluation, mixed, N/A, withheld | `chrome` / muted neutrals | zinc | — | `text-secondary` |

`info` is cyan so it cannot be mistaken for brand (`action/primary` / centric-blue). A chart of “informational vs action required” must not paint info as brand blue.

**Fill vs stroke** follows [[brand-text-vs-fill]] and the status soft-foreground rule: solid step-9 is a **fill** (bars, area, donut slices, KPI spark when the card is status-colored). Lines, markers, and labels on a plot use **step 11** (`*-soft/foreground`). Step-9 as text on the plot fails contrast (already measured on the status solids).

### Polarity on signed metrics

A number is not automatically “positive = green.” Polarity is part of the metric definition.

| Polarity | Example | + direction maps to | − direction maps to |
|---|---|---|---|
| `higher-is-better` | On-time %, margin vs plan, yield | `status/success` | `status/destructive` |
| `lower-is-better` | Defect rate, days late, cost overrun | `status/destructive` | `status/success` |
| `none` | Units produced, temperature | Sequential / categorical — **no status** | — |

Zero or the plan line is the **neutral midpoint**, not a status. Do not color the axis or the plan annotation with success/destructive.

### Contract on every chart

```
colorEncoding: "categorical" | "sequential" | "diverging" | "status"
statusRoleMap?: Record<categoryValue, StatusRole>
polarity?: "higher-is-better" | "lower-is-better" | "none"
```

- `colorEncoding` is required. Defaulting to categorical when the column is a status enum is a **spec bug**, not a theme choice.
- For status categories, `statusRoleMap` is required and exhaustive. Unmapped values render **neutral** plus a visible “unmapped status” in the table view — they do not pick the next categorical hue.
- For evaluative diverging, `polarity` is required. Missing polarity → refuse to apply status hues (sequential fallback is also wrong; show the chart uncolored / single-series until polarity is declared).
- Chart-from-selection: if the selected column is a status field, the popover uses this encoding. Today `ChartCanvas` always paints `--chart-1…5`. That is a known gap.

### Redundancy (non-negotiable)

Status color is never the only signal — same rule as Status Pill and the colors foundation. Pair with **label, icon, and/or pattern**. Test deuteranopia: success vs destructive must still separate. Texture on bars (solid vs hatch) is the Carbon fold for this family.

### Worked examples

| Chart | Encoding | Color |
|---|---|---|
| Styles by mill (names) | categorical | `data-color-categorical-*` |
| Styles by workflow status (Approved / At risk / Blocked) | **status** | success / warning / destructive, mapped by value |
| Volume over time | sequential or single-series brand-neutral | not status |
| Margin vs plan (higher is better) | **evaluative diverging** | + → success, − → destructive, 0 → neutral |
| Defect rate vs target (lower is better) | **evaluative diverging** + `lower-is-better` | above target → destructive, below → success |
| Mixed: status stacked inside a mill bar | mill = categorical **axis**; stack segments = **status** | Two encodings at once is legal; the *stack* is status-typed, the *axis* is not |

### Anti-patterns

- Painting a mill or season with `status/success` because that mill is “doing well.” Annotate or filter; do not steal the status hue for a nominal category.
- Using `action/primary` (brand blue) for “good” or for info.
- Using rainbow categorical for a status enum (`chart-1` = Approved, `chart-2` = Blocked).
- Mapping “positive” to green without declaring polarity on a signed metric.
- Coloring only some statuses and leaving others on `chart-3`.
- Status fill on a line chart using step-9 (use step 11).

---

## Table-selection popovers are not a Recharts-only job

ECharts can render the existing popover. The current split is already the right architecture:

| Piece | Owns | Engine-specific? |
|---|---|---|
| `ChartFromSelectionButton` | When the button appears (multi-cell + a numeric column) | No |
| `ChartPopover` | Base UI popover, shape switcher, mapping the selection rect → `{ label, value }[]` | No |
| `detectChartShape` | Guess bar/line/pie/scatter from the range | No |
| `ChartCanvas` | The only file allowed to import Recharts | **Yes — this is the swap** |

Recharts `ResponsiveContainer` is the only thing the popover is actually leaning on. ECharts needs the equivalent: **do not `echarts.init` until the popover is open and has a non-zero box**, then `ResizeObserver` + `chart.resize()`, and `dispose()` on close. Hidden or `display:none` containers are the classic ECharts footgun; a portal popover that mounts at 320×208 is a normal case once you wait for layout.

**What a swap would take (small):**

1. Replace `ChartCanvas` with an ECharts adapter that maps the four shapes to `option` objects (bar / line / pie / scatter). Keep the same `ChartDataPoint` in.
2. Tree-shake the import (`echarts/core` + the four charts + the few components in use). Lazy-load it the same way Recharts is lazy-loaded today so the table barrel stays clean.
3. Register a Centric theme (CSS variables → `echarts.registerTheme`) so the popover and page-level widgets share series color, axis, and grid.
4. Init after open; resize; dispose. Prefer SVG renderer in the popover if 208px canvas looks soft; Canvas remains the page-level default.
5. Drop the `recharts` dependency from `@centric/data-table` once the adapter is in. Two engines is the thing to avoid, not the popover itself.

The popover does not need brush, dataZoom, or a11y-table-view on day one. Those belong on altitude B/C widgets. The popover is a quick read of a cell range.

**Do not** keep Recharts "because the popover is small." That is two theme pipelines and two a11y gaps for a 200px chart. Recharts stays only if we defer the ECharts decision entirely.

---

## Carbon Charts: fold patterns, never take the package

The EOL clock is the answer. Carbon Charts 1.x entered maintenance 2025-06-30 and is scheduled EOL 2027-06-30; 2.x is unreleased. Adding `@carbon/charts` (or a fork) fails the [[sec-supply-chain]] intake gate: *is it maintained? recent releases, succession, not heading into a documented sunset.* Forking it means **we** become the maintainers of IBM's D3 internals and visual language — that is not "avoiding a dependency," it is absorbing an abandoned one.

Apache 2.0 would let us copy source. That is still the wrong move: IBM look, D3 stack we do not otherwise use, trademark on "Carbon," and a second renderer beside ECharts.

**Fold (do this):**

- Data color as its own token family, tested for 3:1 non-text contrast and color vision. Categorical series never alias to `status/*`. Status-typed data **must** bind to `status/*` (see Status-typed encoding).
- Chart types grouped by **job** (comparison, trend, part-to-whole…), not 26 sibling components.
- Accessibility contract we implement on the ECharts wrapper: keyboard across marks and legend, pattern or label redundancy, a **visually hidden or toggleable data table** as the text alternative, title as the accessible name.
- Primitive states on marks: hover, selected, muted, disabled.

**Do not lift or integrate:**

- `npm install @carbon/charts` / `@carbon/charts-react` / Vue wrappers.
- A fork "to keep it alive past 2027."
- IBM Figma kits as production components (reference screenshots in research only).
- Carbon's D3 mark internals, palettes as hex, or their chart option API.

If a specific Carbon a11y technique is worth copying (e.g. how they expose the data table), re-author it against ECharts + CDS tokens. The test: if IBM deleted the GitHub repo tomorrow, our charts still compile.

### Exact take list (rules and contracts, re-authored — not IBM hex, D3, or npm)

Nothing below is a package. Each item is a spec we write in CDS tokens and implement on the ECharts wrapper.

**1. System model**

| Take | Spec it as |
|---|---|
| Three-level hierarchy: elements → primitives (marks with states) → chart types as patterns | DS IA, not 26 sibling components |
| Chart types grouped by **job**: comparison, trend, part-to-whole, correlation, connection, geospatial | Catalog headings. Ship two comparison/trend widgets in v1; do not import Carbon's 26 types |

**2. Data-color token families** (author in Radix/Centric, not IBM purple-cyan)

| Take | Spec it as |
|---|---|
| Categorical sequence applied in a **fixed order** so neighbors contrast | `data-color-categorical-1…8` (cap at 8). Never `status/*` or `action/primary` **unless the series is status-typed** |
| **Pairing palettes** sized to a known category count (a 3-series chart uses a 3-color pairing, not the first 3 of a 14-hue rainbow) | Token sets or a pairing table: 1-, 2-, 3-, 4-, 5-color options |
| Sequential / monochromatic: in **light** theme darkest = largest; in **dark** theme lightest = largest | `data-color-sequential-*` with theme-aware polarity |
| Diverging, **non-evaluative** (hot/cold, two directions with no good/bad) | `data-color-diverging-*`; midpoint neutral; **not** status red/green |
| Diverging, **evaluative** (vs plan, signed outcome with polarity) | Poles bind to `status/success` and `status/destructive`; midpoint still neutral |
| **Status / alert family** | Already `status/*`. Use as a mark scale **only** when the data is status-typed |
| Never substitute a gradient for a sequential scale | Ban in the chart token spec |
| Marks vs adjacent plot: **3:1 non-text contrast** (WCAG 1.4.11) | QA gate, not a token name |

**3. Anatomy rules Carbon is explicit about** (most of this is already in [[infod-design-system-patterns]]; these are the Carbon-specific additions)

| Take | Spec it as |
|---|---|
| Title states the **insight**, not the topic | Already required by the data/charts playbook |
| **Direct labels over legends**; legend only when labels collide | Wrapper default: labels on; legend opt-in |
| Tooltip **repeats** the axis values for the hovered mark (and all series at that x on a multi-line) | Tooltip content contract |
| Prefer **muted, not hidden**, when isolating a series (denominator stays visible) | Mark states: hover / selected / muted / disabled |
| Circular: slice **&lt; 3°** gets a callout; slice **&lt; 1°** is **not drawn** and is **not** in tooltip/keyboard — it exists only in the data table | Pie/donut rules + why the table view is required |
| Donut hole may hold a **single KPI / total**; not a second chart | Optional; only if we ship donut |
| Legend: default bottom; **max ~30% of chart height**; overflow scrolls or “view more” | Legend layout tokens |
| Legend hover mutes other series; legend **click isolates** (Carbon uses a checkmark selected state) | For altitude B, click = FilterIntent, not “hide series.” Do not copy hide-on-click onto list-page filter widgets |

**4. Accessibility contract** (the reason Carbon is on the mood board)

| Take | Spec it as |
|---|---|
| Color is never the only encoding — **texture / pattern / label / shape** as well | Pattern fills or direct labels on categorical marks; test deuteranopia |
| Keyboard reaches **title → legend → marks**; tooltip on focus, not hover-only | Wrapper, not ECharts default |
| Accessible name on the graphic (`svgAriaLabel` in Carbon) | `aria-label` / `aria-labelledby` pointing at the title |
| **Tabular representation** of the chart data as a first-class action (Carbon: toolbar → modal). Tiny slices that are not drawn **only** exist here | Chart chrome: “View as table” using `@centric/data-table` or a compact table, not Carbon’s modal |
| Loading is a chart state (`data.loading`), distinct from empty and error | Empty vs broken (already a workspace rule) |

**5. Optional chrome — take the slots, not the widgets**

| Take | Spec it as |
|---|---|
| Toolbar slot for chart actions (table view, export, overflow) | Compose existing Button / IconButton. Do not lift Carbon Toolbar |
| Export PNG / CSV | Later; not v1 for filter widgets |
| Zoom bar / canvas zoom | Later; altitude C only. ECharts `dataZoom` already does this |

**Do not take:** `@carbon/charts` (any framework wrapper), a fork, IBM hex palettes, IBM theme names (white/g10/g90/g100), CSS `prefix`, D3 mark internals, option API (`color.pairing.option`, `tabularRepModal`, `getFillColor`), Figma kits as production components, radar / word cloud / solar / alluvial unless a PLM job appears, legend-click-hides-series on list pages (that fights FilterIntent).

---

## Design-system implementations worth stealing

Enterprise design systems that treat visualization as a first-class layer (not a Storybook afterthought) share the same split: **tokens + anatomy + a small catalog of chart types as patterns**, with the engine behind a facade.

### IBM Carbon Charts — the reference system (not a default runtime)

[Carbon Charts](https://charts.carbondesignsystem.com/) is Apache 2.0, with wrappers for React, Vue, Angular, Svelte, and vanilla. ~26 chart types grouped by job (comparisons, trends, part-to-whole, correlations, connections, geospatial). Accessibility is the reason to study it:

- Data color palettes designed separately from brand UI color, with WCAG 1.4.11 non-text contrast (3:1) as a hard constraint.
- Color is never the only encoding: pattern fills, direct labels, a **data-table alternative view** for screen readers.
- Keyboard navigation across marks and legend.
- Three-level hierarchy that maps cleanly onto a DS: **elements** (color, type, texture) → **primitives** (point, line, area — interactive, with states) → **chart types as patterns** (the catalog).

**Do not install it.** Version 1.x entered maintenance 2025-06-30 and is scheduled EOL 2027-06-30; v2.x is unreleased. Multi-framework wrappers are real, but the visual language is IBM's, and theming to Centric tokens will fight the D3-based internals. Fold the model (see above). Do not audit the runtime as a candidate engine.

### Other systems (what to take)

| System | Take | Leave |
|---|---|---|
| **Carbon Charts** | Tokenized data color; a11y (pattern, table view, keyboard); chart-type-as-pattern | Runtime (maintenance clock, IBM look) |
| **Ant Design Charts / AntV G2** | Grammar-of-graphics thinking; G6 if we ever do BOM/supply-chain **networks** | Alibaba visual defaults; React-first docs |
| **Unovis** (F5, Apache 2.0) | CSS-variable theming; React + Vue + Angular + Svelte + Solid from one core | Smaller catalog; younger than ECharts |
| **Elastic Charts** | Kibana-grade time series, brush, annotation | **Elastic License 2.0 + SSPL** — procurement risk; not "Apache-open" |
| **shadcn Chart** | CSS variables `--chart-1`…`n` mapped into Recharts | Recharts ceiling; React-only; no brush-to-filter |
| **MUI X Charts** | Community bar/line/pie are MIT | Pro/Premium paywall for the charts you actually want |
| **Polaris / Primer / Fluent** | Almost nothing — viz is not a first-class DS layer there | — |

Atlassian, Shopify, and GitHub do **not** ship a viz system at Carbon's altitude. For a PLM DS, Carbon + AntV (networks) + Unovis (CSS vars) are the three to keep on the mood board.

---

## Open-source engines — fully free for advanced use

Constraint from this brief: **no payment required for the more advanced functions.** That eliminates Highcharts, amCharts (without the attribution badge), FusionCharts, ApexCharts above the $2M-revenue threshold, AG Charts **Enterprise** (zoom, navigator, sync, sankey, maps, financial), and MUI X Charts **Pro**. AG Charts Community and MUI X Charts Community remain legal; they are the wrong ceiling.

| Engine | License | Framework | Renderer | Why it is on the list | Why it is not the default |
|---|---|---|---|---|---|
| **Apache ECharts 6** | Apache 2.0 | Agnostic (`echarts-for-react`, `vue-echarts`, `ngx-echarts`) | Canvas (SVG optional) | Widest catalog with no paid tier; brush, dataZoom, legend select, large-data headroom; theme JSON maps to tokens | Config-object API is not React-idiomatic; a11y is partial — CDS wrapper must own keyboard, table-alt, captions |
| **Vega-Lite** | BSD-3 | Agnostic (JSON spec) | SVG / Canvas | Best **interaction model** in the field: a selection *is* a query. Canonical [brush → table](https://vega.github.io/vega-lite/examples/brush_table.html) and [crossfilter](https://vega.github.io/vega-lite/examples/interactive_layered_crossfilter.html) examples | Productizing a JSON grammar as a DS component is awkward; styling to Centric chrome is extra work |
| **Unovis** | Apache 2.0 | React, Vue, Angular, Svelte, Solid, vanilla | SVG | CSS variables as the theme API — closest to token-native; networks + maps in the same kit | Smaller, younger; fewer exotic types |
| **AntV G2 / G6** | MIT | Strongest in React; G6 for graphs | Canvas / SVG / WebGL | G6 is the serious BOM / supplier-network option | Two libraries; Chinese-docs gravity; not a DS wrapper |
| **Observable Plot** | ISC (D3 family) | Agnostic | SVG | Tiny, honest grammar; good for custom one-offs | Not a dashboard kit; you build chrome |
| **visx** (Airbnb) | MIT | React | SVG | Headless D3 primitives — maximum DS control | React-only; you assemble every chart |
| **Nivo** | MIT | React | SVG / Canvas | Pretty defaults, modular | React-only; bundle; customization thinner than visx |
| **Recharts** | MIT | React | SVG | Already in CDS; fine for ≤ a few thousand points | Hits a ceiling (brush, canvas, exotic types, Vue); do not grow the product system on it |
| **Perspective** (J.P. Morgan) | Apache 2.0 | Web component | WASM + charts | Streaming / Arrow-scale pivot + chart in one | Overkill for page-level widgets; visual language is its own product |
| **D3** | ISC | Agnostic | You choose | No ceiling | Not a library you "adopt" — a toolkit you staff |

**Default engine: ECharts, behind a CDS facade.** It is the only option that is simultaneously (1) unconditionally free at the high end, (2) framework-agnostic enough for Vue-primary PLM + React CDS, (3) catalog-deep enough that we will not outgrow it in two years, and (4) event-rich enough to emit filter intents (click, legend, brush, dataZoom).

**Interaction model to copy, not to ship: Vega-Lite selections.** A brush is a parameterized query. Highlight vs filter vs scale-domain (overview+detail) are three different uses of the same selection. CDS should name those three explicitly.

**Theming path:** ECharts `registerTheme` from CSS custom properties (`data-color-categorical-*`, `chart-grid-color`, `chart-axis-label-color`). Unovis is the fallback if CSS-variable theming turns out cheaper than ECharts theme JSON. Decision can wait until a spike.

---

## The filter contract (this is the actual product design)

Do not let the chart library own application state. The chart **emits**; the page **filters**.

```
FilterIntent {
  source: "chart" | "chip" | "toolbar" | "url"
  field: string          // the column / facet, e.g. "status" or "season"
  operator: "eq" | "in" | "range" | "contains"
  values: unknown[]      // categorical click → ["At Risk"]; brush → [min, max]
  label: string          // human chip text, e.g. "Status: At Risk"
  chartId?: string       // which widget minted this
}
```

**Behaviors to spec before any engine spike:**

1. **Click a mark** (bar, slice, treemap cell, stacked child) → `in` / `eq` on that category. Chip appears. Table filters. Chart **highlights** the selected mark and mutes the others (do not hide them — hiding destroys the denominator).
2. **Click a legend item** → same as mark click for that series. Second click clears, or uses the chip dismiss.
3. **Brush / range** (histogram, time axis, scatter) → `range` intent. Show as a chip with an editable range, not only as a visual brush — brushes are invisible to anyone who did not draw them.
4. **Nested child** (stacked bar segment, sunburst ring, treemap cell) → filter on the child's dimension, not the parent's. The chip must say which level fired.
5. **Cross-widget** (dashboard): one store, all widgets' query keys include it. Refetch in parallel; overlay loading, do not skeleton-replace (see [[fe-data-visualization]]).
6. **URL-serializable.** A filtered list page is a shareable view. Brush extents belong in the query string the same way column filters do.
7. **Empty vs broken.** Zero matches after a chart click is a valid empty table, not a chart error. A failed aggregation is a chart error. Do not collapse those (see [[silent-degradation-in-fenced-layers]]).

**Highlight vs filter** is a product choice, not a library default. Tableau/Power BI ship both ("filter others" vs "highlight"). For PLM list pages, **filter** is the primary (the table is the work). For analytical dashboards, **highlight** is often better (the other charts keep their denominators). Spec it per altitude, not globally.

---

## Encoding and accessibility (non-negotiable, library-independent)

From [[infod-encoding-theory]] and [[visual-qa-dataviz]], restated for this brief:

- Position and length before area before hue. Pie/donut only for ≤5 parts of one whole; never compare two pies.
- Categorical hue: max 8, colorblind-tested, **not** UI status colors.
- Sequential / diverging scales are a separate token family. Diverging midpoint is neutral, not brand blue.
- Truncated bar baselines are a blocker. Dual y-axes are a major. Missing data is not zero.
- Every product chart has a title (takeaway, not topic — [[03-data-and-charts]]), axis units in plain English, and a text alternative (visually hidden table or ARIA). Tooltips are additive, never the only access.
- Keyboard: marks and legend are focusable; tooltip on focus, not hover-only; WCAG 1.4.13 (hoverable, dismissible, persistent).
- Lazy-load the engine. A 180kb chart library on the dashboard route is fine; on the table barrel it is not. CDS already does this correctly for Recharts — copy that fence.

---

## What not to do

- **Do not run two chart engines.** If ECharts is the product engine, the selection popover uses it too. Recharts is not required for that overlay.
- **Do not buy Highcharts "for a11y."** The VPAT is real; the license is the problem this brief forbade. Own a11y in the wrapper (Carbon's pattern: table view + keyboard + pattern fills).
- **Do not adopt AG Charts because we once used AG Grid.** Integrated charts couple the grid vendor to the viz vendor. CDS already left AG Grid.
- **Do not put categorical series color on `status/*` or `action/primary`.** Status-typed data is the exception — it **must** use `status/*` (see Status-typed encoding). `action/primary` is still never a series color.
- **Do not ship a 20-type catalog in v1.** Ship altitude A (sparks) + two altitude-B widgets (categorical bar-as-filter, time histogram-as-filter) wired to the table. Catalog depth is why ECharts is the engine, not why it is the API.
- **Do not let Carbon Charts' maintenance clock become a surprise.** If a spike prefers Carbon for Vue parity + a11y, that is a dated bet (EOL 2027-06) and needs an exit.

---

## Open questions (research continues here)

1. **Vue vs React gravity.** Production PLM is Vue-primary; CDS / centric-ui is React. ECharts wrappers exist on both. Confirm whether the first consumer is CDS (React) or C8 (Vue) — that picks the first wrapper, not the engine.
2. **Server vs client aggregation.** A chart-as-filter on a 90-table PLM surface cannot chart every row in the browser. The widget charts **aggregates**; the table stays server-filtered. Who owns the aggregate API?
3. **BOM / network viz.** If supplier or BOM graphs are in scope, that is G6 / Unovis network, not ECharts. Keep it a separate package.
4. **Figma.** There is no Centric chart library in Figma yet. Spec tokens + chrome + two widgets before drawing 26 chart types. Carbon's Figma kits are a reference, not a copy source (trademark + visual language).
5. **Accessibility VPAT.** If procurement later requires a vendor VPAT, revisit Highcharts as an *exception* with a written license path — do not quietly swap engines under the facade without a contract.

---

## Related

- [[enterprise-charting-pm-brief]] — product-management rewrite (plain language)
- [[centric-plm-design-system]] — scale, multi-framework, table-first UI
- [[enterprise-saas-design-patterns]] — filter chips, saved views, density
- [[density-dashboard-visual-review]] / [[density-dashboard-content-sized-grid]] — KPI / widget shells already in flight
- [[radix-derived-color-system]] — do not collide **categorical** data-color with status/action; status-typed marks bind to `status/*`; info is cyan, not brand blue
- [[brand-text-vs-fill]] — status solids are fills (step 9); lines/labels use `*-soft/foreground` (step 11)
- [[silent-degradation-in-fenced-layers]] — empty vs broken on chart widgets
