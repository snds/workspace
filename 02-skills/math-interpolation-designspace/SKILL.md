---
name: math-interpolation-designspace
description: >
  Multi-dimensional interpolation theory, designspace algebra, and variation
  mechanics for parametric multi-axis systems. Use this skill whenever the
  conversation requires: multilinear interpolation across n-dimensional axis
  space, delta computation and storage, designspace as vector space / manifold,
  master placement optimization (where to position masters for minimum
  interpolation error), extrapolation theory and bounds, compatibility as
  topological equivalence, interpolation of complex attributes (path position,
  curvature, area, metrics), avar table mapping (axis value remapping for
  nonlinear perception), instance generation from continuous axis coordinates,
  the algebra of variation deltas (addition, composition, decomposition), tensor
  product interpolation, scattered data interpolation (non-rectangular master
  grids), Delaunay triangulation of designspace, or any formal mathematical
  treatment of how masters combine to produce intermediate instances. This skill
  provides the interpolation theory — not the curve math
  (math-bezier-spline-theory) or the perceptual optimization
  (math-optical-optimization).
---

# Interpolation & Designspace Theory

Doctoral-level multi-dimensional interpolation mathematics and variation algebra
for parametric axis systems. Part of the precision vector & parametric design
skill network.

---

## Domain Boundary

This skill owns **the mathematics of combining masters to produce instances** —
the algebra, geometry, and topology of the designspace, and the interpolation
functions that map axis coordinates to glyph geometry.

- **Curve math (Bezier, spline)** → `math-bezier-spline-theory`
- **Shape topology & booleans** → `math-computational-geometry`
- **Perceptual/optical optimization** → `math-optical-optimization`
- **Pipeline implementation** → `lead-technical-digital-artist`

---

## The Designspace as a Mathematical Object

### Definition

A variable font's designspace is a bounded region D ⊂ ℝⁿ, where n is the
number of variation axes:

D = [a₁_min, a₁_max] × [a₂_min, a₂_max] × ... × [aₙ_min, aₙ_max]

Each point **x** = (x₁, x₂, ..., xₙ) ∈ D specifies an **instance** — a
concrete font with fixed axis values.

For CentricSymbols (4 axes):

D = [100, 700] × [0, 1] × [−25, 200] × [20, 48]
     wght         FILL     GRAD          opsz

This is a 4-dimensional hyperrectangle with 2⁴ = 16 corners.

### Masters as Samples

Masters are specific points in D where the glyph geometry is explicitly
defined. The font stores the glyph data at each master location. All other
points in D are computed by interpolation.

**Full factorial master set**: One master at every corner of D → 2ⁿ masters.
For 4 axes: 16 masters. This is often excessive — the art is in placing fewer
masters strategically.

### The Default Master

One master is designated the **default** — the instance rendered when no axis
values are specified. Its designspace coordinate is the **origin** of the
variation system.

In OpenType, the default is stored as the base glyph data. Other masters are
stored as **deltas** (differences from the default).

---

## Linear Interpolation in 1D

### Basic Linear Interpolation (lerp)

For a single axis a ∈ [a_min, a_max] with two masters M₀ (at a_min) and M₁
(at a_max):

Normalize: t = (a − a_min) / (a_max − a_min),  t ∈ [0, 1]

Interpolate: **G**(t) = (1 − t) · **M₀** + t · **M₁**

Where **G** is any numeric attribute (node coordinates, advance width, etc.)
and the interpolation applies component-wise.

### Delta Representation

Rather than storing two complete masters, store:

- Default master **M₀** (complete glyph data)
- Delta **Δ** = **M₁** − **M₀** (difference from default)

Then: **G**(t) = **M₀** + t · **Δ**

This is the representation used in OpenType `gvar` (TrueType) and `CFF2` tables.

### Intermediate Masters

When the interpolation between min and max is not linear (e.g., stroke width
should increase faster at low weights), an intermediate master at axis value
a_mid provides a piecewise-linear approximation:

```
For a ∈ [a_min, a_mid]:
  t = (a − a_min) / (a_mid − a_min)
  G(t) = (1−t)·M₀ + t·M_mid

For a ∈ [a_mid, a_max]:
  t = (a − a_mid) / (a_max − a_mid)
  G(t) = (1−t)·M_mid + t·M₁
```

This is a piecewise-linear spline in 1D. OpenType supports arbitrary numbers
of intermediate masters per axis.

---

## Multilinear Interpolation in nD

### Bilinear Interpolation (2 axes)

For two axes (a, b) with four corner masters M₀₀, M₁₀, M₀₁, M₁₁:

Normalize: s = (a − a_min)/(a_max − a_min),  t = (b − b_min)/(b_max − b_min)

**G**(s, t) = (1−s)(1−t)·M₀₀ + s(1−t)·M₁₀ + (1−s)t·M₀₁ + st·M₁₁

This is a **tensor product** of two 1D interpolations. The coefficients
(1−s)(1−t), s(1−t), (1−s)t, st are the 2D Bernstein basis functions of
degree 1 (bilinear).

### Trilinear and Beyond

For n axes with 2ⁿ corner masters, the general multilinear interpolation:

**G**(**x**) = Σ_{**v** ∈ {0,1}ⁿ} **M_v** · ∏ᵢ₌₁ⁿ [vᵢ·tᵢ + (1−vᵢ)(1−tᵢ)]

Where:
- **v** ranges over all 2ⁿ binary vectors (corners of the unit hypercube)
- tᵢ is the normalized coordinate for axis i
- **M_v** is the master at corner **v**

For CentricSymbols (4 axes, 16 corners): this is **quadrilinear interpolation**.
Each instance is a weighted sum of up to 16 masters.

### Computational Cost

Evaluating multilinear interpolation naively requires 2ⁿ multiplications per
attribute per glyph. Efficient evaluation uses the **recursive nesting**
approach:

1. Interpolate along axis 1 (reduces 2ⁿ masters to 2ⁿ⁻¹)
2. Interpolate along axis 2 (reduces to 2ⁿ⁻²)
3. Continue until a single value remains

This requires n · 2ⁿ⁻¹ lerp operations instead of 2ⁿ multiplications — a
significant saving for large n.

---

## Delta Algebra

### Delta Decomposition

The OpenType variation model decomposes the interpolation into a sum of deltas
from the default:

**G**(**x**) = **M_default** + Σₖ sₖ(**x**) · **Δₖ**

Where:
- **Δₖ** is the delta for variation region k
- sₖ(**x**) is the scalar function that activates delta k at position **x**

### Variation Regions and Scalars

Each delta is associated with a **variation region** — a hyperrectangular
subregion of the designspace defined by per-axis peak, start, and end values:

For axis i in region k:
```
       | 0                          if xᵢ < startᵢ or xᵢ > endᵢ
sᵢ,ₖ = | (xᵢ − startᵢ)/(peakᵢ − startᵢ)  if startᵢ ≤ xᵢ < peakᵢ
       | (endᵢ − xᵢ)/(endᵢ − peakᵢ)       if peakᵢ ≤ xᵢ ≤ endᵢ
       | 1                          if xᵢ = peakᵢ
```

The scalar for region k is the product: sₖ(**x**) = ∏ᵢ sᵢ,ₖ(**x**)

This is a **tensor-product hat function** (tent function) centered at the
peak, fading to zero at the region boundaries.

### Delta Composition

Multiple deltas can be active simultaneously. Their effects are additive:

**G**(**x**) = **M_default** + s₁(**x**)·**Δ₁** + s₂(**x**)·**Δ₂** + ... + sₖ(**x**)·**Δₖ**

**Critical property**: delta additivity means the order of delta application
doesn't matter (commutativity of addition). This simplifies implementation
but constrains the types of variations that can be expressed.

### Limitations of Linear Delta Model

The additive delta model cannot represent:
- **Multiplicative interactions**: where axis A's effect depends on axis B's value
  (e.g., "FILL behaves differently at bold weight")
- **Discontinuities**: abrupt changes at specific axis values
- **Path topology changes**: adding/removing nodes (prohibited by definition)

For CentricSymbols: if FILL behavior needs to differ between thin and bold
weights, this requires an explicit interaction master at (wght=bold, FILL=1)
rather than relying on the default's delta.

---

## Master Placement Optimization

### The Problem

Given n axes and a budget of K masters (K < 2ⁿ), where should masters be
placed to minimize interpolation error across the designspace?

### Error Metric

The interpolation error at any point **x** is:

ε(**x**) = |**G_true**(**x**) − **G_interp**(**x**)|

Where **G_true** is the "ideal" glyph (what a designer would draw at **x**)
and **G_interp** is the interpolated result.

The total error over the designspace:

E = ∫_D ε(**x**)² d**x**

### Corner Masters (Minimal Set)

With only corner masters (default + axis extremes), the interpolation is
multilinear. The error is largest at the **center** of the designspace (farthest
from any master) and at points where the true variation is nonlinear.

For n axes with only min/max masters per axis: 2n + 1 masters (default + 2
per axis). But this only captures independent axis effects — no interactions.

### Interaction Masters

To capture how axis A affects axis B, add a master at a corner of the A×B
subspace:

- Without interaction master: **G**(a_max, b_max) = **M_default** + **Δ_a** + **Δ_b**
- With interaction master: **G**(a_max, b_max) = **M_default** + **Δ_a** + **Δ_b** + **Δ_ab**

Where **Δ_ab** = **M_(a_max,b_max)** − **M_default** − **Δ_a** − **Δ_b** captures the
interaction (the "surprise" beyond what independent axis effects predict).

### Project-Specific: CentricSymbols Master Strategy

Given that GRAD and high opsz values are pipeline-derived:

**Essential masters** (explicitly authored or derived):
1. Default: (wght=400, FILL=0, opsz=24) — authored
2. opsz=20: authored as Figma variant
3. wght extremes: pipeline-derived from medial axis scaling
4. FILL=1: requires explicit design (counter collapse behavior)
5. Interaction (wght×FILL): may need explicit master if FILL behavior
   changes with weight

**The mathematical question**: Given the pipeline's ability to derive wght
variants automatically, does the derived bold master produce acceptable
FILL=1 behavior? If not, a (wght=700, FILL=1) interaction master is needed.

---

## The avar Table: Axis Value Remapping

### Purpose

The `avar` table provides a piecewise-linear remapping of axis values before
interpolation, allowing **nonlinear perceptual response** from a linear
interpolation engine.

### Mathematical Model

The avar mapping for axis i:

aᵢ_normalized = f(aᵢ_user)

Where f is a piecewise-linear function defined by a set of (input, output) pairs:

f(x) = yⱼ + (x − xⱼ) · (yⱼ₊₁ − yⱼ) / (xⱼ₊₁ − xⱼ)   for x ∈ [xⱼ, xⱼ₊₁]

### Application to Perceptual Uniformity

From `math-optical-optimization`, the perceived weight follows a logarithmic
law. To make linear wght axis values produce perceptually uniform weight steps:

Define avar mapping: input (user-facing linear values) → output (internal
values that produce correct geometric stroke widths).

If the stroke width should follow w(t) = w₀ · r^t (geometric progression):

avar maps: user_wght → log((user_wght − 100)/600 · (r⁶ − 1) + 1) / log(r⁶)

This remapping makes wght=400 sit at the perceptual midpoint between 100 and
700, even though it's the arithmetic midpoint.

### avar Version 2

The `avar` v2 table (recently added to OpenType) supports:
- **Multi-axis remapping**: output depends on multiple input axes
- **Expression of axis interactions** without additional masters

This is mathematically equivalent to a nonlinear coordinate transform on the
designspace before interpolation.

---

## Extrapolation

### Definition

Extrapolation evaluates the interpolation function at points **outside** the
master-defined region of D. OpenType allows extrapolation — axis values can
exceed the defined min/max.

### Linear Extrapolation

Beyond the master range, the linear trend continues:

**G**(t) = **M₀** + t · **Δ**    for t > 1 or t < 0

### Stability Bounds

Extrapolation amplifies errors. If the interpolation error at the boundary is
ε_boundary, the extrapolation error at distance d beyond the boundary is:

ε_extrap ≈ ε_boundary + d · |∇ε|

For practical purposes, extrapolation beyond ~20% of the axis range risks
visible artifacts (self-intersecting outlines, negative counter areas, path
inversions).

### Project-Specific: CentricSymbols Extrapolation Policy

GRAD is pipeline-derived and may use extrapolation from the wght axis.
Extrapolation bounds should be validated:

```
For each glyph at extrapolated GRAD values:
  Check: no self-intersecting contours
  Check: all counter areas > 0
  Check: advance width unchanged (GRAD constraint)
  Check: no path direction reversals
```

---

## Compatibility as Topological Equivalence

### Formal Definition

Two glyphs are **interpolation-compatible** if and only if they have the same
topological structure:

1. **Same number of contours** (connected components of the boundary)
2. **Same number of nodes per contour** (points on each boundary component)
3. **Same contour order** (bijection between contours across masters)
4. **Same node order within each contour** (bijection between nodes)
5. **Same path directions** (orientations preserved)

This is a requirement of **combinatorial equivalence** — the two outlines must
be homeomorphic as labeled graphs.

### Why Topology Must Be Preserved

Interpolation operates on corresponding nodes by index:

**G**(t).node[i] = (1−t) · **M₀**.node[i] + t · **M₁**.node[i]

If the nodes don't correspond (different count, different order, different
contour assignment), the interpolation produces meaningless geometry.

### Detecting Incompatibility

**Algorithm**:
```
For masters M_a, M_b:
  For each glyph g:
    If contour_count(g, M_a) ≠ contour_count(g, M_b): FAIL
    For each contour c:
      If node_count(c, M_a) ≠ node_count(c, M_b): FAIL
      If orientation(c, M_a) ≠ orientation(c, M_b): FAIL
    Check: start point alignment (rotation invariant comparison)
```

### Resolving Incompatibility

When masters have different node counts (e.g., after outline operations):

1. **Add nodes**: Insert nodes in the master with fewer, at positions that
   minimize shape change (subdivide at parameter t where the node exists in
   the other master)
2. **Remove nodes**: Use curve fitting to remove excess nodes while staying
   within tolerance
3. **Reorder nodes/contours**: Relabel to establish correct correspondence

The mathematical challenge: finding the **optimal correspondence** between two
different-count node sets. This is related to the **assignment problem** and
can be solved with the Hungarian algorithm on a distance matrix.

---

## Tensor Product vs. Scattered Interpolation

### Tensor Product (Standard OpenType)

OpenType's variation model is a tensor-product structure — axes are independent
and interpolation is performed axis-by-axis. This requires masters arranged
on a **grid** (potentially sparse, with some corners omitted).

### Scattered Data Interpolation

When masters are not on a grid (e.g., a designer creates masters at arbitrary
designspace locations), scattered interpolation methods are needed:

- **Delaunay triangulation**: Triangulate the master positions in designspace,
  use barycentric interpolation within each simplex
- **Radial basis functions (RBF)**: **G**(**x**) = Σₖ wₖ · φ(|**x** − **xₖ**|) where
  φ is a kernel function (e.g., thin-plate spline: φ(r) = r² log r)
- **Natural neighbor interpolation**: Weight masters by their Voronoi cell
  overlap with the query point

These are not natively supported by OpenType but can be used in the build
pipeline to generate the grid-aligned masters that OpenType requires.

### Application to CentricSymbols

If the pipeline generates weight variants algorithmically (medial axis scaling),
the generated masters may not land exactly on grid corners. The pipeline should:

1. Generate masters at algorithmically optimal positions
2. Use scattered interpolation to resample onto the OpenType-required grid
3. Verify interpolation quality at all grid points

---

## Information-Theoretic Perspective

### Redundancy in Masters

When all axes are independent (no interactions), 2n+1 masters (default + 2 per
axis) fully specify the variation. The remaining 2ⁿ − 2n − 1 potential corner
masters carry zero additional information.

**Test for independence**: Compute the interaction delta **Δ_ab** for each axis
pair. If |**Δ_ab**| < ε (within numerical noise), the axes are independent and
the interaction master is unnecessary.

### Optimal Master Budget

Given a target maximum interpolation error ε_max across D:

1. Start with default + axis extreme masters (2n+1)
2. For each axis pair (a,b): compute interaction delta magnitude max|**Δ_ab**|
3. If max|**Δ_ab**| > ε_max: add the interaction master
4. Continue to three-way interactions if needed (rare — most font variation
   is well-approximated by pairwise interactions)

For CentricSymbols with 4 axes:
- Minimum masters: 9 (default + 2×4)
- Potential pairwise interactions: C(4,2) = 6
- Maximum with all pairwise: 15
- Full factorial: 16

The pipeline should measure interaction magnitudes to determine which of the
6 potential pairwise masters are actually needed.

---

## Interpolation of Non-Geometric Attributes

### Metrics Interpolation

Advance width, sidebearings, and vertical metrics also interpolate:

advance_width(**x**) = aw_default + Σₖ sₖ(**x**) · Δaw_k

For CentricSymbols: all icons have uniform advance width (monospaced grid).
The GRAD axis must maintain this invariant — its advance width delta must be
exactly zero.

### Kerning Interpolation

If kerning pairs are defined, the kerning values interpolate:

kern(A,B)(**x**) = kern_default(A,B) + Σₖ sₖ(**x**) · Δkern_k(A,B)

For icon fonts: kerning is typically not used (all glyphs are independently
positioned), but the machinery exists if needed.

### COLR Layer Interpolation

COLRv1 paint attributes (opacity, color) can also be variable:

alpha(**x**) = alpha_default + Σₖ sₖ(**x**) · Δalpha_k

This enables opacity that changes with weight or fill — e.g., a background
element that fades as FILL increases from 0 to 1.

---

## Numerical Precision in Interpolation

### Delta Quantization

In `gvar` tables, deltas are stored as 16-bit integers (range ±32767 in FUnits).
For UPM=2048, this provides sub-unit precision.

For `CFF2`, deltas are stored as fixed-point numbers with configurable precision.

### Accumulation Error

When multiple deltas are active, their sum can accumulate rounding errors:

ε_total ≤ Σₖ |sₖ| · ε_quantization

For K active deltas with maximum scalar 1.0 and quantization error 0.5:
ε_total ≤ K · 0.5

For CentricSymbols (up to 16 corners in 4D): worst case ε ≈ 8 FUnits at
UPM=2048 → ~0.004 em → ~0.08px at 20px render → invisible.

### Interpolation vs. Rounding Order

**Correct**: interpolate in full precision, then round to grid
**Incorrect**: round each delta, then sum

The difference matters when multiple small deltas combine to produce a
significant shift that would round differently if computed in aggregate vs.
piecewise.


---

## Design-Forward Operating Directive

The designspace is where a single design becomes a family. Interpolation
quality determines whether the full axis range feels like intentional design
or like a machine stretching shapes. This skill must ensure that the
mathematical machinery of variation serves continuous visual quality across
every possible instance.

### Principles

1. **Every instance is a design.** The user doesn't see "the default plus
   deltas" — they see a specific icon at a specific weight, fill, grade, and
   optical size. That instance must look as if a designer drew it deliberately.
   If an interpolated instance looks mechanical, distorted, or unbalanced,
   the master placement or delta structure needs revision — regardless of
   whether the math is "correct."

2. **The designspace has an aesthetic topology.** Some regions of the
   designspace are more visually critical than others. The default instance
   matters most; bold+filled is common in UI; thin+small is a legibility
   stress test. Weight master placement and interaction decisions should
   prioritize visual quality in high-traffic regions of the designspace
   over rarely-used corners.

3. **Interpolation artifacts are visual bugs, not math problems.** When an
   interpolated instance shows counter collapse, stroke thinning, or
   asymmetric weight distribution, frame the diagnosis in visual terms first
   ("the left stroke thins disproportionately at wght=250"), then trace to
   the mathematical cause (nonlinear variation not captured by linear delta
   model). The fix is evaluated by whether the visual artifact is eliminated,
   not by whether the math is more sophisticated.

4. **avar remapping is a design tool.** The avar table isn't a technical
   correction — it's a design decision about how the axis feels to use.
   A well-tuned avar makes weight steps feel natural and uniform; a poorly
   tuned one makes the axis feel lurchy or front-loaded. Route to
   `math-optical-optimization` for perceptual uniformity models, then
   validate the avar mapping by generating instances at regular axis
   intervals and evaluating their visual progression.

5. **Master budget decisions are aesthetic tradeoffs.** When deciding whether
   an interaction master is needed (e.g., wght×FILL), the question is not
   "is the interaction delta statistically significant" but "does the
   interpolated instance at (bold, filled) look as good as if a designer drew
   it directly?" If yes, skip the master. If no, add it. The math determines
   where to look; the design eye determines what to do.
