---
name: infod-spatial-maps
description: >
  Spatial and geographic data visualization: choropleth maps (projections, class
  break methods, lie potential), proportional symbol maps, flow and origin-destination
  maps, point maps (clustering, density), map projections and their distortions, and
  web mapping libraries (Mapbox GL JS, Leaflet, D3 + topojson, deck.gl). PLM-specific
  use cases: supplier location maps, distribution networks, geographic trend overlays.
  Use this spoke when any data has a geographic dimension or when the question
  involves a map as the primary visualization.
hub: lead-information-designer
---

# Spatial Maps

Specialist spoke for geographic and spatial data visualization. Part of the
`lead-information-designer` skill network.

---

## Domain Boundary

This spoke owns **geographic visualization decisions** — when to use a map vs. a
chart, which map type, which projection, and which library.

- **Non-geographic networks with location data** → combine this spoke with
  `infod-network-graphs` (graph structure) + this spoke (geographic layer)
- **Color palette for choropleth** → `infod-encoding-theory` (sequential vs.
  diverging palette selection, ColorBrewer, OKLCH)
- **Map as a dashboard tile** → `infod-dashboard-patterns` for layout context

---

## When to Use a Map (and When Not To)

**Use a map when:**
- Geography is a variable the reader needs to reason about — "where" is part of
  the question
- The spatial distribution or pattern is the insight (clusters, corridors, gaps)
- The user has a mental model of the geographic space that aids interpretation

**Do not use a map when:**
- Geography is incidental — the insight is categorical (region A vs. region B)
  and a bar chart would communicate it more accurately
- The distribution is uniform — a map of uniform data shows the map, not the data
- The audience doesn't share the geographic mental model (e.g., international data
  with a US-only map literacy assumption)
- Precise comparison between regions is needed — bar charts are more accurate

A bar chart with regions on the x-axis is almost always more quantitatively
accurate than a choropleth map of the same data. Use the map when the "where"
visual insight adds value beyond the comparison.

---

## Choropleth Maps

A choropleth fills geographic regions (countries, states, zip codes) with a
color scale to encode a quantitative variable.

### Projections for Choropleth

**Albers USA** — Area-preserving composite for US-only data; shows Alaska and
Hawaii in insets at correct relative scale; the standard for US thematic maps.

**Albers (generalized)** — Equal-area conic; appropriate for mid-latitude regions
(Europe, continental US) where area preservation matters.

**Goode's Homolosine** — Interrupted equal-area for world maps; preserves area
at the cost of a visually "torn" ocean. Use for global thematic data where area
accuracy matters more than spatial continuity.

**Web Mercator (EPSG:3857)** — The default for web tile maps (Google Maps,
Mapbox streets layer). **Severely distorts area** at high latitudes (Greenland
appears as large as Africa). Never use for choropleth maps — the area distortion
visually over-weights high-latitude low-population regions.

**Equal Earth** — A compromise equal-area projection for world maps with a
visually pleasing silhouette. Good default for world-scale thematic maps.

**Rule**: For choropleth maps, always use an equal-area projection. Area-distorting
projections make high-latitude regions appear to contribute more than they do.

### Class Break Methods

Choropleth maps must classify continuous data into discrete buckets for color encoding.
The choice of classification method changes what the map shows.

**Natural Breaks (Jenks)**
- Minimizes within-class variance; maximizes between-class variance
- Classes follow the data's natural clusters
- Use when: the data has natural groupings; showing where genuine discontinuities exist
- Disadvantage: class boundaries change with each dataset; cannot be compared across time

**Equal Interval**
- Divides the data range into N equal-sized intervals
- Class boundaries are round, predictable numbers
- Use when: the audience will read the legend carefully; comparison across time is needed
- Disadvantage: if data is skewed, most data falls in 1–2 classes; poor visual differentiation

**Quantile**
- Each class contains the same number of geographic units
- Maximizes color variation and visual differentiation on the map
- Use when: you want to see relative ranking regardless of absolute values
- Lie potential: quantile maps misrepresent the magnitude of differences; a small
  difference near the class break is shown as the same color distance as a large
  difference in the middle of a class. Never use for communicating precise differences.

**Standard Deviation**
- Classes are defined by standard deviations from the mean
- Use when: showing divergence from average is the message (e.g., performance vs. mean)
- Pairs with a diverging color palette centered at the mean

**Manual Breaks**
- Manually specified thresholds with business meaning (e.g., on-time: ≥95%; warning: 85–94%; critical: <85%)
- Use when: the thresholds are operationally defined and the audience will use them as decision criteria
- Best for: operational maps with defined pass/fail or tier-based status encoding

**Rule**: Match the class break method to the question. Use jenks for exploratory;
manual breaks for operational; quantile only when relative rank is the question.

### Choropleth Lie Potential

**Area bias (MAUP — Modifiable Areal Unit Problem)**
- Large geographic areas (sparse rural regions) visually dominate the map even
  when their contribution is small
- Example: a choropleth of US sales data makes Montana look important because
  it's big, even if sales are negligible
- Mitigation: use cartogram (area scaled to value) or proportional symbol map
  instead of choropleth for population-normalized data

**MAUP — Scale effect**
- The same data aggregated at different geographic units (county vs. state vs.
  region) can show completely different patterns
- Always show the geographic level of aggregation in the map title or attribution

**Mitigation strategies:**
1. Use a proportional symbol map instead of choropleth when the areas are not
   meaningful representations of the variable
2. Use per-capita or normalized values (sales per store, units per region) rather
   than absolute values when region size correlates with the variable
3. Acknowledge the limitation in the chart annotation when using choropleth for
   non-normalized data

---

## Proportional Symbol Maps

Places circles (or other symbols) at geographic locations; circle area encodes a
quantitative variable.

**Use instead of choropleth when:**
- Point data (cities, stores, factories) rather than areal data (countries, states)
- Absolute values matter (not per-area rates)
- Multiple variables need encoding (circle size + color)

### Perceptual Size Scaling (Flannery Correction)

Human perception systematically underestimates area. A circle with 4× the area
appears only ~2–2.5× as large. To encode data with accurate perceived magnitude:

```
Corrected radius = k × value^0.5716
```

The Flannery (1971) exponent of 0.5716 (rather than 0.5 for pure area scaling)
compensates for perceptual underestimation. The constant k sets the reference
circle size.

**Without Flannery correction**: large values are systematically under-perceived,
flattening the apparent magnitude difference.

### Overlapping Circles

When many locations are clustered:
- Transparent fills (50–70% opacity) reveal overlap without hiding individual symbols
- Outline-only symbols (no fill) for dense clusters
- Shift to hexbin aggregation or convex hull clustering when too many overlap
- Show the count of aggregated points in cluster labels

---

## Flow Maps and Origin-Destination (OD) Maps

Flow maps show movement between locations: goods in transit, migration,
data packets, supply chain flows.

### Bundled vs. Unbundled Flow Lines

**Unbundled flow lines**: each origin-destination pair is one line; appropriate
for ≤20 distinct flows; shows individual routes clearly.

**Bundled flow lines**: lines that share a geographic direction are combined into
bundles; appropriate for 20–500 flows; reduces visual clutter; reveals main
corridors at the cost of individual route legibility.

**Aggregated OD matrix** (chord diagram): for dense OD data (>100 pairs), a
chord diagram encodes all OD flows as chords on a circle; loses geographic
context but shows volume relationships clearly.

### Direction Encoding

- Arrow heads on flow lines; scale arrowhead with flow volume
- For bilateral flows (A→B and B→A): use offset parallel lines; or encode
  net direction with a signed color (diverging)

### Threshold Filtering

Always filter low-volume flows by default; provide a control to adjust the
threshold. Showing all flows in a dense OD dataset produces a hairball.
Display the filter state clearly ("Showing flows > 100 units/week").

---

## Point Maps

For individual location data (stores, suppliers, factories, events).

### Overplotting Solutions

**Marker cluster**: group nearby points into a single cluster marker showing
count; expand on click. Standard pattern in Leaflet and Mapbox.

**Hexbin aggregation**: aggregate points into a hexagonal grid; color hexagons
by count or average metric. Better than marker clusters for showing density patterns.

**Kernel density estimation**: smooth density surface rendered as a heat-layer.
Shows where points concentrate; loses individual point identity.

**Sampling**: for very large datasets (>10k points), random sample or progressive
loading (load overview first, detail on zoom).

---

## Map Projections for Interactive Web Maps

| Projection | Distortion | Use For |
|-----------|-----------|---------|
| **Web Mercator** | Severe area distortion at high latitudes | Basemap tiles only; never for thematic data |
| **Equal Earth** | None (equal area) | World-scale thematic maps |
| **Albers USA** | None (equal area, US) | US-only thematic maps |
| **Robinson** | Compromise (not equal area) | Reference/overview world maps |
| **WGS84 geographic** (lat/lng as x/y) | Severe at poles | Small-area maps; not for global display |

**For interactive dashboards**: Use Web Mercator for the basemap (standard tile layers);
overlay thematic data using an equal-area transformation for choropleth polygons.

---

## Libraries

### Mapbox GL JS / MapboxGL

- GPU-accelerated vector tile rendering
- Supports custom layer types, 3D terrain, smooth zoom/pan
- Best for: high-quality product map experiences; interactive maps in dashboards;
  large point datasets (100k+) with deck.gl integration
- Cost: Mapbox pricing applies for tile usage; self-hosted tiles with open data
  are possible

### Leaflet

- Lightweight raster tile map library
- Wide plugin ecosystem (marker cluster, heat layer, draw tools)
- Best for: lighter-weight map experiences; when Mapbox budget is a concern;
  simple point or choropleth overlays
- Limitation: no GPU rendering; degrades with large point datasets

### D3.js + TopoJSON

- Full programmatic control over SVG map rendering
- TopoJSON: compact topology-preserving alternative to GeoJSON; smaller files
- Best for: custom projection maps, non-tile-based thematic maps,
  embedded SVG maps in articles or reports
- Cost: high implementation time; no built-in tiling or interactivity

### deck.gl

- WebGL-based, built for large-scale point data (millions of points)
- Layer types: ScatterplotLayer, HexagonLayer, HeatmapLayer, ArcLayer (OD flows),
  GeoJsonLayer (choropleth)
- Best for: supply chain visualization with many locations; large point datasets
  where Leaflet/Mapbox performance degrades
- Integration: works with Mapbox GL JS (deck.gl on top of Mapbox basemap)

**Decision guide:**
- Lightweight map, simple overlay: Leaflet
- Product-quality interactive map: Mapbox GL JS
- Custom projection, SVG: D3 + TopoJSON
- >50k points or custom GPU layers: deck.gl + Mapbox

---

## Enterprise PLM Use Cases

### Supplier Location Map

- Show factory/supplier locations as proportional symbols (circle area = order volume)
- Color encode by status: active, at-risk, on audit watch
- Filter by category, season, or sourcing region
- Click through to supplier scorecard
- Library: Mapbox GL JS + deck.gl ScatterplotLayer for volume

### Distribution Network Visualization

- Origin: factories / warehouses
- Destination: distribution centers / customer regions
- Flow lines: bundled by region; width = volume; color = on-time rate
- Status overlay: DC status (full/low/critical)
- Library: deck.gl ArcLayer for flows + Mapbox basemap

### Geographic Trend Overlays

- Choropleth of sales performance, margin, or delivery rate by country/region
- Equal Earth projection for global view; Albers USA for US-specific
- Class breaks: use manual thresholds tied to KPI targets (red/amber/green)
  rather than statistical methods — this is an operational map, not exploratory
- Library: Mapbox GL JS GeoJSON layer or D3 + TopoJSON for full SVG control

---

## Cross-Links

- **`infod-encoding-theory`** — sequential vs. diverging palette for choropleth;
  ColorBrewer palette selection; Flannery correction is an area perception problem
  (Cleveland & McGill encoding hierarchy)
- **`infod-network-graphs`** — supply chain networks with geographic positions;
  flow maps with origin-destination pairs; geographic layout algorithm
- **`infod-dashboard-patterns`** — embedding a map tile in a dashboard;
  geographic filter state; drill-down from map to detail table
- **`infod-statistical-viz`** — when a bar chart (categories = regions) is
  more appropriate than a choropleth map
- **`infod-design-system-patterns`** — map component anatomy; tooltip design
  for map markers; empty/loading states for map tiles
- **`fe-data-visualization`** — library selection and implementation (Mapbox,
  deck.gl, Leaflet); WebGL rendering for large point datasets

---

## References

- Cynthia Brewer — *Designed Maps: A Sourcebook for GIS Users* (2008)
- Mark Monmonier — *How to Lie with Maps* (1991)
- Flannery, J.J. — "The Relative Effectiveness of Some Common Graduated Point
  Symbols in the Presentation of Quantitative Data" (1971)
- ColorBrewer 2.0 — geographic projection filters: https://colorbrewer2.org/
- deck.gl documentation: https://deck.gl/
- Mapbox GL JS documentation: https://docs.mapbox.com/mapbox-gl-js/
