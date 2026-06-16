---
name: infod-network-graphs
description: >
  Network and graph visualization: graph theory basics for visualization,
  layout algorithm selection, overplotting strategies for dense graphs,
  rendering libraries, and enterprise PLM use cases (BOM hierarchy, supply
  chain networks, org charts, component dependencies). Use this spoke when
  the visualization involves nodes and edges, hierarchical relationships,
  dependency structures, supply chain networks, or any graph-structured data.
hub: lead-information-designer
---

# Network Graphs

Specialist spoke for graph and network visualization. Part of the
`lead-information-designer` skill network.

---

## Domain Boundary

This spoke owns **graph and network visualization decisions** — structure,
layout, rendering, and enterprise application.

- **Hierarchical tree without edge complexity** → `infod-statistical-viz`
  (treemap) or `infod-dashboard-patterns` (org chart as dashboard element)
- **Geographic networks (supply chain with location)** → `infod-spatial-maps`
  (flow maps) in combination with this spoke
- **Rendering implementation** → `fe-data-visualization`

---

## Graph Theory Basics for Visualization

Understanding graph structure determines which visualization approach is appropriate.

### Core Vocabulary

| Term | Definition | Visualization Implication |
|------|-----------|--------------------------|
| **Node (vertex)** | An entity in the graph | Visualized as a dot, circle, icon, or label |
| **Edge (link)** | A relationship between two nodes | Visualized as a line, arc, or arrow |
| **Directed graph (digraph)** | Edges have direction (A → B ≠ B → A) | Requires arrowheads; layout algorithms differ |
| **Undirected graph** | Edges are symmetric | No arrowheads; community structure often more important |
| **Weighted graph** | Edges have a magnitude | Edge width, color saturation, or opacity encodes weight |
| **Density** | Edges / possible edges; 0 = no connections, 1 = fully connected | High-density graphs require aggregation strategies |
| **Connected components** | Isolated clusters with no edges between them | Each component may need separate layout treatment |

### Centrality Measures — When to Compute and Show Them

Centrality measures tell you how "important" a node is within the network.
Each measures a different kind of importance. Showing centrality as a node
size or color encoding can reveal structure that layout alone cannot.

| Measure | What It Answers | Visual Encoding | PLM Use Case |
|---------|----------------|-----------------|--------------|
| **Degree centrality** | How many direct connections does this node have? | Node size | High-degree supplier = single point of failure risk |
| **Betweenness centrality** | How often does this node sit on the shortest path between others? | Node color intensity | Critical intermediary in supply chain |
| **Closeness centrality** | How quickly can this node reach all others? | Node size | Fastest-to-market distribution node |
| **Eigenvector centrality** | Is this node connected to other well-connected nodes? | Node size (PageRank variant) | Influential stakeholder in approval chains |

**Show centrality when:** there is a business question about which nodes matter
most. Do not show it by default — it adds cognitive load without payoff if the
question is simply "what is connected to what."

---

## Layout Algorithms

Layout is the most important design decision for a network graph. The same data
looks completely different under different layout algorithms. Match the algorithm
to the graph's dominant structure.

### Force-Directed (Fruchterman-Reingold)

**What it does**: Treats edges as springs (attraction) and nodes as repelling
charges. The simulation reaches an equilibrium where connected nodes cluster.

**Use when:**
- No inherent hierarchy in the data (undirected networks, community structure)
- The clustering pattern is the message — groups with dense internal connections
  will visually cluster
- n < 300 nodes (force simulations become slow and visually noisy at larger sizes)

**Limitations:**
- Non-deterministic: the same data renders differently each run unless the seed
  is fixed — important for reproducibility in product dashboards
- Edge crossing is not minimized; hairball effect at moderate density (>0.1)
- Layout has no semantic meaning — proximity encodes similarity, but axes mean nothing

**Parameter controls**: spring length (target edge length), spring constant
(edge attraction strength), charge (node repulsion). Increasing spring length
spreads the graph; increasing charge separates clusters.

### Hierarchical (Sugiyama / DOT)

**What it does**: Arranges nodes in layers (ranks), minimizes edge crossings,
draws edges as directed downward (top-to-bottom or left-to-right).

**Use when:**
- The data has a directed hierarchy: BOM, org chart, approval workflow,
  dependency DAG
- Direction matters — reading the graph top-to-bottom encodes the flow direction
- n < 1,000 nodes (Sugiyama has polynomial complexity)

**Limitations:**
- Only correct for directed acyclic graphs (DAGs); cycles require special handling
- Long chains of single-child nodes create tall, thin layouts; collapse chains
  where possible

**Enterprise PLM application**: BOM hierarchy (top-level product → assemblies →
sub-assemblies → components) is a natural hierarchical layout candidate.

### Circular Layout

**What it does**: Places all nodes on a circle; edges are chords.

**Use when:**
- The focus is on edge patterns between a fixed set of peers (not hierarchy)
- The nodes are pre-grouped and the groups should be arranged in arcs
- Adjacency matrix + chord diagram for large dense graphs

**Limitations:**
- Proximity has no meaning; hard to read for unfamiliar audiences
- Edge crossings are not minimized

### Geographic Layout

**What it does**: Places nodes at their geographic coordinates; edges are drawn
as great-circle arcs or straight lines.

**Use when:**
- Location is meaningful — supply chain with physical suppliers and factories
- Route visualization, distribution network, origin-destination flows

**Route to:** `infod-spatial-maps` for the geographic encoding layer. This spoke
handles the node/edge representation decisions; `infod-spatial-maps` handles the
map projection and geographic encoding.

### Matrix Layout (Adjacency Matrix)

**What it does**: Nodes become both row and column labels of a matrix; a cell is
filled when an edge exists between the row node and column node.

**Use when:**
- The graph is dense (many edges); force-directed becomes a hairball
- n > 200 nodes (matrix scales linearly in each dimension)
- Showing symmetric or asymmetric relationships between all node pairs

**Limitations:**
- Does not show topology (clustering, path structure) as intuitively as node-link
- Harder to read for non-expert audiences

---

## Overplotting Solutions for Dense Networks

Dense graphs (>200 nodes, high edge density) become unreadable in standard
force-directed layouts. Use a graduated intervention strategy.

### Tier 1: Filtering

- Show only nodes and edges above a centrality or weight threshold
- Interactive slider or preset filters ("show only suppliers with >3 connections")
- **Always show the filter state** — what is excluded must be disclosed

### Tier 2: Aggregation

- Collapse low-interest clusters into single aggregate nodes
- Show a "group" node representing N members with summary statistics
- Let the user expand on click

### Tier 3: Bundled Edges (Edge Bundling)

- Route edges through shared pathways to reduce visual clutter
- Hierarchical edge bundling (Holten, 2006): edges that share a hierarchical
  path are bundled together
- Trade-off: bundling reduces individual edge visibility; good for traffic
  pattern overview, bad for tracing specific connections

### Tier 4: Focus + Context (Fisheye)

- Magnify the neighborhood of the selected node; compress the rest
- Graphical fisheye distortion or ego-network extraction (show selected node
  + 1 or 2 hops)
- Ego-network extraction is more reliable for enterprise dashboards than
  fisheye distortion (distortion is disorienting in operational contexts)

### Tier 5: Matrix View Fallback

When node count exceeds ~200 and the structure cannot be simplified by filtering
or aggregation, switch to a matrix (adjacency matrix) representation. The matrix
is always readable regardless of density; it sacrifices topological intuition
for visual clarity.

**Decision rule:**
- n < 50, sparse: force-directed
- n < 200, hierarchical: Sugiyama
- n > 200 or density > 0.15: matrix, bundling, or filtered ego-network

---

## Visualization Libraries

### D3.js

- Full control over layout, rendering, interaction, and animation
- Requires significant implementation time
- Use when: custom layouts, unusual encodings, tight DS integration required
- Force simulation: `d3-force`; Sugiyama: external (d3-dag or Elk.js + D3)
- Cost: 3–5x development time vs. higher-level libraries

### Cytoscape.js

- Purpose-built for graph visualization with extensive layout plugin support
- Layouts: force-directed, hierarchical (dagre), circular, grid, breadthfirst
- Good for: interactive exploration, click-to-expand, highlighting ego-networks
- Cost: faster to implement than D3; less pixel-perfect control

### Gephi

- Desktop application for graph exploration and analysis
- Not a product/dashboard library — it is an analyst tool
- Use for: initial data exploration, centrality analysis, cluster discovery
  before deciding which subset of the graph to visualize in the product

### NetworkX + Matplotlib / Plotly (Python)

- For data science exploration, report generation, Jupyter notebooks
- Not for interactive product dashboards
- Use for: exploratory analysis, centrality computation, generating static
  images for presentations

### Elk.js

- Eclipse Layout Kernel — highly configurable hierarchical layout engine
- Excellent for BOM and workflow DAGs
- Used by: VS Code (dependency graph), draw.io, many diagramming tools
- Can be integrated with D3 or React for product-quality rendering

---

## Enterprise PLM Use Cases

### BOM Hierarchy (Bill of Materials)

- Data structure: directed tree (with shared sub-components creating a DAG)
- Layout: hierarchical (Sugiyama/Elk.js)
- Node encoding: product type (shape or icon), quantity (size or label),
  status (color — colorblind-safe)
- Edge encoding: quantity (edge label or width)
- Challenge: shared sub-components appear at multiple levels — use DAG layout,
  not strict tree; highlight shared nodes

### Supply Chain Network

- Data structure: directed graph with geographic positions
- Layout: geographic (node positions from supplier/factory coordinates) +
  force-directed adjustment to reduce overlap
- Node encoding: type (supplier/factory/warehouse — shape), volume (size),
  status (color + icon)
- Edge encoding: flow volume (width), lead time (color or label), mode (line style)
- Challenge: route to `infod-spatial-maps` for the geographic layer

### Component Dependency Graph

- Data structure: directed acyclic graph (DAG) — circular dependencies are bugs
- Layout: hierarchical
- Use case: data model dependencies, microservice dependency, API dependency map
- Highlight: cycles (errors), orphaned nodes, critical path

### Approval Workflow / Process Map

- Data structure: directed graph with possible cycles (for rejection/rework loops)
- Layout: hierarchical left-to-right or top-to-bottom
- Cycles: render as back-edges with a different visual treatment (dashed, curved)

---

## Cross-Links

- **`infod-encoding-theory`** — node size (area encoding) requires perceptual
  scaling; edge color uses sequential or categorical palette rules
- **`infod-statistical-viz`** — treemap and nested bar charts as alternatives
  to node-link diagrams for hierarchical composition
- **`infod-spatial-maps`** — supply chain networks with geographic positions;
  geographic layout uses map projection, edges become flow lines
- **`infod-dashboard-patterns`** — embedding a network overview in a dashboard
  with drill-down to ego-network; filter state management
- **`infod-design-system-patterns`** — graph component as DS component;
  tooltip design for nodes and edges; empty/loading/error states
- **`fe-data-visualization`** — library selection (D3, Cytoscape, Elk.js),
  SVG vs. Canvas at large node counts, WebGL for >10k nodes
- **`lead-data-scientist`** — centrality metrics and community detection
  algorithms should be computed server-side; the DS spoke owns the math

---

## References

- Tamara Munzner — *Visualization Analysis and Design*, Chapter 9 (Networks) (2014)
- Thomas M.J. Fruchterman and Edward M. Reingold — "Graph Drawing by Force-Directed Placement" (1991)
- Kozo Sugiyama — Hierarchical graph drawing (the Sugiyama framework)
- Danny Holten — "Hierarchical Edge Bundles" (2006)
- Cytoscape.js: https://js.cytoscape.org/
- Elk.js: https://eclipse.dev/elk/
- NetworkX documentation: https://networkx.org/
