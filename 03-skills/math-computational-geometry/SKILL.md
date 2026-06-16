---
name: math-computational-geometry
description: >
  Computational geometry, topological analysis, and constructive solid geometry
  for 2D vector shape operations. Use this skill whenever the conversation
  requires: boolean operations (union, intersection, difference, XOR) as
  set-theoretic operations on planar regions, winding number computation,
  point-in-polygon algorithms, contour orientation detection (CW/CCW), even-odd
  vs. non-zero fill rules, Minkowski sum and offset (stroke expansion as
  Minkowski sum with disk), convex hull algorithms, medial axis transform
  (skeleton extraction), Voronoi diagrams for equidistant partitioning, sweep-line
  algorithms for intersection detection, polygon triangulation, shape
  decomposition into convex parts, topological validation (Euler characteristic,
  genus, manifold conditions), path winding and self-intersection detection, or
  any formal geometric/topological analysis of 2D vector regions. This skill
  provides the theoretical geometry — not the curve math
  (math-bezier-spline-theory) or the perceptual optimization
  (math-optical-optimization).
aliases: [math-computational-geometry]
spec_version: "2.0"
---

# Computational Geometry & Topology

Doctoral-level computational geometry and topological analysis for 2D vector
shape operations. Part of the precision vector & parametric design skill network.

---

## Domain Boundary

This skill owns **the mathematics of 2D regions and their operations** —
boolean algebra on shapes, topological classification, winding rules, and
geometric algorithms on polygonal/curved domains.

- **Curve math (Bezier, spline)** → `math-bezier-spline-theory`
- **Perceptual/optical optimization** → `math-optical-optimization`
- **Multi-axis interpolation** → `math-interpolation-designspace`
- **Path construction workflow** → `lead-vector-designer`

---

## Foundations: Planar Regions and Boundaries

### Oriented Contours

A glyph outline is a set of oriented closed contours (loops) in ℝ². Each
contour partitions the plane into an interior and exterior. The orientation
(direction of traversal) determines which side is "inside."

**Convention in OpenType (CFF/CFF2)**:
- **Counterclockwise (CCW)** contours define filled regions (positive area)
- **Clockwise (CW)** contours define holes (negative area, counters)

**Convention in TrueType**:
- Reversed: CW = filled, CCW = hole

The choice is arbitrary but must be consistent within a font. CentricSymbols
uses CFF2, so CCW = fill, CW = hole.

### Signed Area (Shoelace Formula)

For a polygon with vertices (x₁,y₁), ..., (xₙ,yₙ):

A = ½ |Σᵢ₌₁ⁿ (xᵢyᵢ₊₁ − xᵢ₊₁yᵢ)|

The **signed** area (without absolute value) reveals orientation:
- A > 0 → CCW (filled region)
- A < 0 → CW (hole)

For Bezier curves, the signed area uses the parametric integral:

A = ½ ∮ (x dy − y dx) = ½ ∫₀¹ (B_x(t)B'_y(t) − B_y(t)B'_x(t)) dt

This integral has a closed-form solution for cubic Beziers (it reduces to
polynomial integration).

### Orientation Detection Algorithm

```
For each contour:
  1. Compute signed area using shoelace formula (polygon) or parametric
     integral (Bezier curves)
  2. Sign determines orientation:
     Positive → CCW (fill in CFF2)
     Negative → CW (hole in CFF2)
  3. Compare against expected convention
  4. Reverse path if needed (swap node traversal order, flip handles)
```

**Design application**: This is the core algorithm for the "check path directions"
step in glyph validation. Mismatched orientations cause fill rule errors —
holes render as filled or fills render as empty.

---

## Winding Number Theory

### Definition

The winding number w(**p**, C) of a closed curve C around point **p** counts
how many times C wraps around **p** in the CCW direction:

w(**p**, C) = (1/2π) ∮_C dθ

Where θ is the angle from **p** to the current point on C.

### Computational Method

For a polygonal approximation (or piecewise curve):

```
w = 0
For each edge (v₁, v₂):
  If v₁.y ≤ p.y:
    If v₂.y > p.y:                    (upward crossing)
      If left_of(v₁, v₂, p) > 0:     (p is left of edge)
        w += 1
  Else:
    If v₂.y ≤ p.y:                    (downward crossing)
      If left_of(v₁, v₂, p) < 0:     (p is right of edge)
        w -= 1
Return w
```

Where `left_of(v₁, v₂, p)` = (v₂.x − v₁.x)(p.y − v₁.y) − (p.x − v₁.x)(v₂.y − v₁.y)

### Fill Rules

| Rule | Fill Condition | Behavior |
|------|---------------|----------|
| Non-zero | w(**p**) ≠ 0 | Standard for fonts — all winding counts fill |
| Even-odd | w(**p**) is odd | Alternating fill — used in some SVG contexts |

**OpenType fonts use non-zero winding rule exclusively.** This is why path
direction matters — two overlapping CCW contours produce w = 2 (filled under
non-zero), while one CCW and one CW produce w = 0 (unfilled = hole).

### Winding Number and Boolean Operations

Understanding winding numbers allows reasoning about boolean results:

| Region | w(A) | w(B) | A ∪ B | A ∩ B | A \ B |
|--------|------|------|-------|-------|-------|
| Outside both | 0 | 0 | unfilled | unfilled | unfilled |
| Inside A only | ≠0 | 0 | filled | unfilled | filled |
| Inside B only | 0 | ≠0 | filled | unfilled | unfilled |
| Inside both | ≠0 | ≠0 | filled | filled | unfilled |

---

## Boolean Operations on Planar Regions

### Theoretical Framework

Boolean operations on 2D regions are instances of **regularized set operations**
from constructive solid geometry (CSG), restricted to 2D:

- **Union**: A ∪* B = closure(interior(A ∪ B))
- **Intersection**: A ∩* B = closure(interior(A ∩ B))
- **Difference**: A \* B = closure(interior(A \ B))
- **Symmetric difference (XOR)**: A △* B = (A \* B) ∪* (B \* A)

The regularization (closure of interior) eliminates degenerate results like
isolated points or dangling edges.

### Sweep-Line Boolean Algorithm (Greiner-Hormann family)

The standard algorithm for polygon/curve booleans:

**Phase 1 — Intersection detection**:
1. Find all intersection points between contours of A and contours of B
2. For Bezier curves: use recursive subdivision (bisect both curves,
   check bounding box overlap, recurse until segments are nearly linear,
   then compute line-line intersection)
3. Insert intersection points into both contours (splitting curves at
   intersection parameters)

**Phase 2 — Classification**:
1. For each edge segment between intersections, determine if it lies:
   - Inside A, inside B, on boundary of A, on boundary of B
2. Classification uses point-in-polygon (winding number) tests on
   segment midpoints

**Phase 3 — Selection**:
Based on the desired operation, select edges:
- Union: edges outside the other shape + shared boundary edges
- Intersection: edges inside the other shape
- Difference A\B: edges of A outside B + edges of B inside A (reversed)

**Phase 4 — Contour assembly**:
1. Link selected edges into closed contours
2. Assign correct orientations (CCW for fills, CW for holes)
3. Validate: no self-intersections, correct nesting

### Robustness Issues

Boolean operations on Bezier curves are notoriously fragile:

- **Tangential intersections**: curves that touch but don't cross (t = single
  root with even multiplicity)
- **Coincident edges**: overlapping curve segments (infinite intersections)
- **Numerical precision**: intersection parameters near 0 or 1 (is the
  intersection at the endpoint or not?)
- **Degenerate inputs**: zero-area contours, self-intersecting paths

**Mitigation**: Use exact arithmetic (rational numbers) for classification
decisions, or use ε-tolerance with consistent tie-breaking rules.

**Design application**: These robustness issues explain why Figma's Flatten
operation sometimes produces unexpected results — and why post-flatten
validation (node count, path direction, contour count) is mandatory.

---

## Minkowski Sum and Stroke Expansion

### Stroke as Minkowski Sum

A stroked path with width 2r is geometrically the **Minkowski sum** of the
path skeleton with a disk of radius r:

**Stroke**(C, r) = C ⊕ D(r) = {**p** + **d** : **p** ∈ C, **d** ∈ D(r)}

Where D(r) is the closed disk of radius r centered at the origin.

### Properties

- The Minkowski sum of a convex set with any set is well-defined and produces
  no self-intersections if the original set has no self-intersections and
  curvature > 1/r everywhere
- For non-convex paths or paths with high curvature, the Minkowski sum can
  self-intersect → requires trimming
- **Inside stroke** (CentricSymbols closed paths): equivalent to Minkowski
  difference (erosion): C ⊖ D(r)
- **Center stroke** (CentricSymbols open paths): full Minkowski sum

### Relationship to Offset Curves

The boundary of the Minkowski sum is composed of:
- Offset curves at distance r (parallel to original path)
- Offset curves at distance −r (anti-parallel)
- Circular arcs at endpoints (cap geometry) or join geometry at corners

This connects to `math-bezier-spline-theory`'s offset curve treatment — the
offset curve (**C**(t) + r·**n̂**(t)) is one boundary component of the Minkowski sum.

---

## Medial Axis Transform

### Definition

The medial axis of a 2D region R is the locus of centers of maximal inscribed
disks — the set of all points inside R that have more than one closest point
on the boundary ∂R.

Equivalently: the medial axis is the set of points where the distance function
to the boundary is not differentiable (the "ridge" of the distance field).

### Relationship to Skeleton-and-Meat Strategy

The medial axis is the mathematical formalization of the "skeleton" concept in
icon font construction:

- **Skeleton** = medial axis of the filled glyph shape
- **Meat** = the radius function r(t) along the medial axis (the inscription radius)
- **wght axis** = varying r(t) along the medial axis while keeping the axis fixed

This means the weight axis, in its ideal mathematical form, is a **medial axis
transform with variable radius function**.

### Computation

For polygonal regions:
1. Compute Voronoi diagram of the boundary edges
2. The medial axis is the subset of Voronoi edges that lie inside the region
3. Prune branches (remove spurs from boundary noise)

For curved boundaries (Bezier):
- Approximate boundary as polyline, compute Voronoi
- Or: use the distance field approach (sample on grid, find ridges)

### Application to Weight Axis Derivation

If the pipeline needs to generate weight variants from a single master:

1. Extract the medial axis from the default weight outline
2. Compute the radius function r(t) at each point
3. Scale r(t) → r(t) · k for a new weight (k > 1 = bolder, k < 1 = thinner)
4. Reconstruct the outline from the scaled medial axis transform
5. The result has the same topology and node structure — only positions change

This is the mathematical basis for CentricSymbols' pipeline-derived weight
variants.

---

## Convex Hull and Bounding Structures

### Convex Hull of Control Points

The convex hull property of Bezier curves guarantees:

**B**(t) ∈ Conv(**P₀**, **P₁**, **P₂**, **P₃**) for all t ∈ [0,1]

This enables fast rejection tests:
- If the convex hulls of two curves don't overlap, they don't intersect
- If a point is outside the convex hull, it's outside the curve
- Bounding box (axis-aligned bounding rectangle) is a fast approximation of
  the convex hull

### Hierarchical Bounding

For intersection detection across many curves (e.g., boolean operations on
complex glyphs):

1. **BVH (Bounding Volume Hierarchy)**: recursively subdivide curves, build
   a tree of bounding boxes
2. **Sweep line**: sort curve segments by x-coordinate, process events
3. **Grid hashing**: partition the plane into cells, test only curves in
   adjacent cells

These are O(n log n) vs. naive O(n²) for n curve segments — critical for
complex glyphs with many contours.

---

## Topological Validation

### Euler Characteristic for 2D

For a planar subdivision with V vertices, E edges, F faces:

χ = V − E + F = 2 (for a connected planar graph with outer face)

For a glyph with:
- C outer contours (filled regions)
- H hole contours (counters)
- No self-intersections

Expected: C connected filled regions, each with some number of holes.

### Validation Checks

| Check | Method | Failure Mode |
|-------|--------|-------------|
| No self-intersection | Sweep line on all edges | Rendering artifacts |
| Correct orientation | Signed area per contour | Fill rule errors |
| Proper nesting | Point-in-polygon on contour samples | Holes outside fills |
| Connected components | Graph traversal on contour nesting | Orphaned contours |
| No coincident points | Distance check on all node pairs | Degenerate geometry |
| No zero-length edges | Segment length check | Numerical instability |

### Contour Nesting Tree

Build a tree structure of contour containment:

```
For each contour Cᵢ:
  For each other contour Cⱼ:
    Test if Cⱼ is inside Cᵢ (winding number of a point on Cⱼ w.r.t. Cᵢ)

Build tree:
  Root: virtual outer boundary
  Level 1: outermost contours (fills)
  Level 2: holes directly inside Level 1 contours
  Level 3: fills inside holes (islands in lakes)
  ...
```

**Validation rule**: contours at even depth (0, 2, 4...) should be CCW (fills),
contours at odd depth (1, 3, 5...) should be CW (holes) — for CFF2 convention.

---

## Shape Distance Metrics

### Hausdorff Distance

The Hausdorff distance between two shapes A, B:

d_H(A, B) = max(sup_{a∈A} inf_{b∈B} |a−b|,  sup_{b∈B} inf_{a∈A} |a−b|)

This is the maximum deviation between two shapes — the "worst case" distance.

**Design application**: Used to measure how much a shape changed after:
- Node reduction
- Curve fitting
- Boolean operation + cleanup
- Offset curve approximation

A Hausdorff distance < 0.5 UPM units means the change is sub-pixel at all
practical rendered sizes.

### Fréchet Distance

A more refined shape comparison that respects the parameterization (order of
traversal) of the curves. The Fréchet distance is the minimum leash length
needed for a person walking along curve A and a dog walking along curve B to
traverse both curves simultaneously.

**Design application**: Fréchet distance detects reordering errors (same shape
but traversed in a different order) that Hausdorff distance would miss.

---

## Algorithms for Font-Specific Problems

### Point-in-Glyph Test

Given a compiled glyph and a point **p**, determine if **p** is inside the
glyph (filled):

1. Cast a ray from **p** in any direction (typically +x)
2. Count crossings with all contour edges (using Bezier-ray intersection)
3. Apply winding rule: sum signed crossings
4. Non-zero sum → inside (filled)

This is used for hit-testing, kerning pair analysis, and COLR layer
composition validation.

### Contour Simplification (Visvalingam-Whyatt for Curves)

Adapted from polyline simplification for Bezier outlines:

1. For each node, compute the "visual importance" = area of the triangle
   formed by the node and its two neighbors
2. Remove the node with smallest importance
3. Refit the surrounding curves to absorb the removed node
4. Repeat until desired node count or maximum error threshold

**Constraint**: Must preserve node parity across masters — if a node is
removed in one master, the corresponding node must be removed in all masters.

### Overlap Removal

Post-boolean-operation cleanup to ensure no overlapping contours remain:

1. Detect all curve-curve intersections within the glyph
2. If intersections exist: re-run union on the glyph with itself
3. Validate: no intersections remain
4. This is a fixpoint operation — repeat until stable

Many font compilers (and validators like fontbakery) require overlap-free
outlines, even though renderers can handle overlaps via fill rules.


---

## Design-Forward Operating Directive

Shape operations are where design intent meets geometric reality. A boolean
union or path offset is not a neutral transformation — it either preserves or
destroys the visual qualities the designer intended. This skill must evaluate
every geometric operation through an aesthetic lens.

### Principles

1. **Topology serves visual structure.** Contour nesting, path direction, and
   winding numbers are not abstract properties — they determine what fills
   and what doesn't, what reads as solid and what reads as void. When
   validating topology, ask: "Does this produce the visual figure/ground
   relationship the designer intended?"

2. **Boolean cleanup is a design-critical operation.** Post-boolean geometry
   often contains artifacts: micro-segments, near-coincident nodes, reversed
   contours. These are not just technical debt — they produce rendering
   artifacts (hairline gaps, fill bleed, anti-aliasing noise) that degrade
   visual quality. Clean aggressively, validate visually.

3. **The medial axis is a design skeleton, not just a mathematical object.**
   When extracting or manipulating the medial axis for weight derivation,
   evaluate whether the resulting skeleton captures the icon's visual
   structure — its balance, its proportional emphasis, its rhythm. A
   mathematically correct medial axis that produces visually unbalanced
   weight variants has failed.

4. **Shape distance metrics inform design judgment.** Hausdorff and Fréchet
   distances quantify how much a shape changed — but the design question is
   whether the change is **visible** and whether it **matters**. A 2-unit
   Hausdorff distance on a decorative flourish may be invisible; the same
   distance on a thin counter at opsz=20 may destroy legibility. Always
   contextualize distance metrics against rendered size and visual criticality.

5. **Minkowski operations are stroke design operations.** Stroke expansion
   (Minkowski sum with a disk) defines the visual weight of every outlined
   icon. The mathematical properties of the Minkowski sum — self-intersection
   at high curvature, cap and join geometry — directly determine visual
   quality at corners, endpoints, and tight curves. Recommend solutions that
   produce the cleanest, most visually consistent stroke geometry.
