---
name: lead-vector-designer
description: >
  Precision vector path construction and bezier curve craft. Use this skill
  whenever the conversation touches: bezier curve construction, pen tool technique,
  node placement strategy, boolean operations (union, subtract, intersect, exclude),
  stroke-to-outline mechanics, path direction (CW/CCW), SVG path data (d attribute)
  authoring or reading, geometric construction from primitives, Figma vector editing,
  anchor point types (smooth vs. corner), handle symmetry, tangent continuity,
  grid-aligned vector drawing, or any question about *how to construct paths
  correctly* for interpolation-safe output. This skill covers the craft of
  drawing — not what to draw (lead-icon-artist) or how to compile it
  (lead-technical-digital-artist).
---

# Lead Vector Designer

Specialist lens for precision vector path construction. Part of the precision
vector & parametric design skill network.

---

## Domain Boundary

This skill owns **path construction craft** — the mechanics of drawing vectors
that will survive destructive conversion and interpolate cleanly across masters.

- **What to draw** → `lead-icon-artist`
- **How to process/compile** → `lead-technical-digital-artist`
- **Interpolation physics & axis mechanics** → `variable-icon-font-architect` (hub)

---

## Core Competencies

### Bezier Curve Mechanics

- **Anchor types**: smooth (handles colinear, tangent-continuous) vs. corner
  (independent handles, allows discontinuity)
- **Handle symmetry**: mirrored (equal length) vs. asymmetric (unequal length,
  same angle) vs. disconnected (corner)
- **Minimum nodes principle**: use the fewest nodes that accurately describe the
  shape. Every unnecessary node is a potential interpolation hazard.
- **Curvature continuity**: G0 (positional), G1 (tangent), G2 (curvature) —
  icon fonts typically require G1 minimum at smooth transitions

### Node Placement Strategy for Icon Fonts

#### Cardinal Point Rule

Place nodes at the geometric extrema of every curve — the topmost, bottommost,
leftmost, and rightmost points. This is mandatory for:

- Font compilers (they expect extrema nodes for hinting)
- Clean bounding box calculation
- Predictable interpolation between masters

#### Grid Alignment

- All nodes snap to the icon grid (24×24 for CentricSymbols default master)
- Off-grid nodes cause sub-pixel rendering artifacts at small sizes
- Handles may extend off-grid, but anchors should not

#### Interpolation-Safe Placement

- Matching masters must have nodes in corresponding positions
- When a shape changes across masters (e.g., rounded corner radius changes with
  weight), the *number* of nodes stays fixed — only positions move
- Avoid nodes that would need to "jump" past each other between masters

### Boolean Operations

#### Operation Types

| Operation | Result | Use Case |
|-----------|--------|----------|
| Union | Merge overlapping shapes | Building compound shapes from primitives |
| Subtract | Cut one shape from another | Creating counters, notches, cutouts |
| Intersect | Keep only overlap | Masking, clipping |
| Exclude | Keep non-overlapping areas | Toggle/swap regions |

#### Boolean Hygiene for Font Export

Booleans must be **flattened** before export — font compilers don't understand
boolean operations, only filled contours with winding rules.

Post-flatten checklist:
1. Verify no overlapping paths remain
2. Check path directions: outer paths CW, inner counters CCW (or vice versa,
   but consistent across all glyphs)
3. Remove any zero-length segments or coincident nodes
4. Confirm node count hasn't changed unexpectedly

### Stroke Mechanics

#### Project-Specific: CentricSymbols Stroke Rules

- **Inside stroke on closed paths** — stroke expands inward from the path edge
- **Center stroke on open paths** — stroke expands symmetrically from the path
- **Round join** — always; miter and bevel are prohibited
- **Butt cap (None)** — no cap extension beyond endpoints

#### Stroke-to-Outline Conversion

This is the most node-count-sensitive operation in the pipeline:

1. Each stroke endpoint generates cap geometry (butt = 2 nodes per end)
2. Each corner generates join geometry (round = arc approximation, typically
   4–8 nodes depending on angle)
3. Sharp angles may generate extra nodes for round joins
4. **Verify node count after every conversion** — this is where parity breaks

#### Predictable Conversion Patterns

| Path Element | Stroke Nodes Generated |
|-------------|----------------------|
| Straight segment | 2 per side (4 total for a line) |
| 90° corner (round join) | ~4 arc nodes |
| Open endpoint (butt cap) | 2 nodes |
| Closed path junction | Joins merge, no cap nodes |

### SVG Path Data (d Attribute)

Reading and writing raw SVG path commands is essential for debugging export
issues and writing FontTools glyph definitions.

#### Command Reference

| Command | Parameters | Meaning |
|---------|-----------|---------|
| M/m | x y | Move to |
| L/l | x y | Line to |
| H/h | x | Horizontal line |
| V/v | y | Vertical line |
| C/c | x1 y1 x2 y2 x y | Cubic bezier |
| S/s | x2 y2 x y | Smooth cubic (mirrored handle) |
| Q/q | x1 y1 x y | Quadratic bezier |
| Z/z | — | Close path |

- Uppercase = absolute coordinates
- Lowercase = relative to current point
- Font glyphs use cubic beziers (C/S), not quadratic (Q)
- TrueType uses quadratic; CFF/CFF2 (OpenType) uses cubic

### Geometric Construction Patterns

Common icon primitives and their node-efficient constructions:

- **Circle**: 4 nodes at cardinal extrema, 8 handles (cubic approximation)
- **Rounded rectangle**: 4 corner arcs (2 nodes each = 8) + 4 straight segments
  (0 additional if tangent to arcs) = 8 nodes minimum
- **Arrow/chevron**: construct from stroked open path, not from polygons —
  preserves weight axis behavior
- **Ring/donut**: 2 concentric circles (8 nodes each), opposite winding directions

---

## Figma-Specific Vector Workflow

### Pen Tool Discipline

- Start closed paths at a consistent position (e.g., top-left extrema)
- Draw in a consistent direction (CW for outer, CCW for inner)
- Use Figma's node type toggles (smooth ↔ corner) to control handle behavior
- Hold Alt/Option to break handle symmetry without converting to corner

### Flatten & Outline Workflow

1. Select the complete icon frame contents
2. **Outline Stroke** (Ctrl/Cmd+Shift+O on strokes)
3. **Flatten** (Ctrl/Cmd+E to resolve all booleans)
4. Inspect result: check for stray points, overlapping segments, path direction
5. Compare node count against other masters

### Common Pitfalls in Figma

- **Auto-added nodes**: Figma may add nodes when flattening complex booleans —
  always verify count post-flatten
- **Path direction reversal**: Flatten can reverse inner path directions —
  check winding after every flatten
- **Compound paths splitting**: A single visual shape may become multiple
  separate paths after flatten — verify contour count
- **Sub-pixel nodes**: Figma allows fractional coordinates; snap to integers
  before export for font grid alignment

---

## Quality Checklist

Before handing any glyph to the pipeline:

- [ ] All anchors on-grid (integer coordinates on 24×24 or equivalent)
- [ ] Extrema nodes present at all curve extremes
- [ ] Minimum viable node count (no redundant points)
- [ ] Path directions consistent (outer CW, inner CCW — or project convention)
- [ ] Start points at consistent positions across masters
- [ ] No overlapping paths (all booleans flattened)
- [ ] No zero-length segments or coincident nodes
- [ ] Node count matches across all masters for this glyph
- [ ] Stroke rules applied (inside/closed, center/open, round join, butt cap)


---

## Design-Forward Operating Directive

This skill does not operate in isolation. Every path construction decision is
ultimately a **design decision** — evaluated by how the result looks, feels, and
communicates at rendered size, not by whether the geometry is technically sound
in the abstract.

### Principles

1. **Visual intent governs path strategy.** Node placement, handle angles, and
   boolean sequencing are not neutral technical choices — they shape the curve's
   character. A mathematically minimal node count that produces a stiff or
   lifeless curve is worse than one extra node that captures the designer's
   intended rhythm.

2. **Craft serves legibility and consistency.** The goal of clean vector
   construction is not cleanliness for its own sake — it's to produce icons
   that read clearly at 20px, interpolate gracefully across axes, and feel
   like they belong to the same visual family.

3. **Leverage the math spokes.** When facing a construction problem (offset
   curve artifacts, node reduction tradeoffs, boolean cleanup noise), route
   to the appropriate math skill (`math-bezier-spline-theory`,
   `math-computational-geometry`) for rigorous analysis — then translate the
   mathematical recommendation back into a visual evaluation. "Does it look
   right?" is the final gate.

4. **Surface aesthetic tradeoffs explicitly.** When technical constraints
   conflict with visual quality (e.g., grid snapping distorts a curve, node
   parity forces suboptimal placement), name both sides of the tradeoff and
   recommend the option that best preserves design intent.

5. **Evaluate at final output, not at authoring zoom.** Paths are authored at
   high magnification but consumed at 20–48px. Always ground construction
   decisions in how the icon will render at its smallest target size.
