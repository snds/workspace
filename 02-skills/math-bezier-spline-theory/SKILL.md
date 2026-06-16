---
name: math-bezier-spline-theory
description: >
  Parametric curve theory, Bezier mathematics, and spline algebra. Use this
  skill whenever the conversation requires: de Casteljau evaluation, Bernstein
  polynomial decomposition, cubic Bezier parameterization, curve subdivision
  (midpoint or arbitrary t), arc-length parameterization, curvature and torsion
  analysis, inflection point detection, G0/G1/G2/G3 continuity classification,
  offset curve computation (parallel curves for stroke expansion), circle-to-Bezier
  approximation error bounds, curve fitting and node reduction algorithms,
  hodograph analysis, rational Bezier curves, B-spline to Bezier conversion,
  quadratic-to-cubic promotion, or any formal mathematical treatment of
  parametric curves. This skill provides the theoretical foundation — not the
  Figma workflow (lead-vector-designer) or the FontTools implementation
  (lead-technical-digital-artist).
---

# Bezier & Spline Theory

Doctoral-level parametric curve mathematics. Part of the precision vector &
parametric design skill network.

---

## Domain Boundary

This skill owns **the mathematics of curves** — formal definitions, theorems,
algorithms, and error analysis for the parametric curves used in font glyphs.

- **Drawing curves in Figma** → `lead-vector-designer`
- **Compiling curves into fonts** → `lead-technical-digital-artist`
- **Shape topology & booleans** → `math-computational-geometry`
- **Interpolation across masters** → `math-interpolation-designspace`
- **Perceptual optimization** → `math-optical-optimization`

---

## Foundations

### The Cubic Bezier Curve

All CFF2/OpenType outline fonts use cubic Bezier curves. The fundamental
definition:

**B**(t) = (1−t)³**P₀** + 3(1−t)²t**P₁** + 3(1−t)t²**P₂** + t³**P₃**,  t ∈ [0,1]

Where:
- **P₀**, **P₃** are on-curve anchor points (endpoints)
- **P₁**, **P₂** are off-curve control points (handles)
- t is the parameter (not arc length — this distinction matters)

#### Bernstein Basis Form

The cubic Bezier is a weighted sum of Bernstein basis polynomials:

**B**(t) = Σᵢ₌₀³ Bᵢ,₃(t) **Pᵢ**

Where Bᵢ,₃(t) = C(3,i) tⁱ(1−t)³⁻ⁱ are the Bernstein basis functions:

| Basis | Expression | Role |
|-------|-----------|------|
| B₀,₃(t) | (1−t)³ | Influence of P₀ |
| B₁,₃(t) | 3t(1−t)² | Influence of P₁ |
| B₂,₃(t) | 3t²(1−t) | Influence of P₂ |
| B₃,₃(t) | t³ | Influence of P₃ |

**Partition of unity**: Σ Bᵢ,₃(t) = 1 for all t — the curve always lies within
the convex hull of its control points.

#### Matrix Form

**B**(t) = [1  t  t²  t³] · M · [P₀  P₁  P₂  P₃]ᵀ

Where M is the cubic Bezier basis matrix:

```
M = | 1   0   0   0 |
    |-3   3   0   0 |
    | 3  -6   3   0 |
    |-1   3  -3   1 |
```

This form is efficient for computation and enables matrix-based transformations
of the curve's shape.

### De Casteljau Algorithm

The numerically stable recursive evaluation algorithm:

Given control points **P₀**, **P₁**, **P₂**, **P₃** and parameter t:

```
Level 0: P₀⁰ = P₀,  P₁⁰ = P₁,  P₂⁰ = P₂,  P₃⁰ = P₃

Level 1: Pᵢ¹ = (1−t)Pᵢ⁰ + tPᵢ₊₁⁰     (i = 0,1,2)
         → P₀¹, P₁¹, P₂¹

Level 2: Pᵢ² = (1−t)Pᵢ¹ + tPᵢ₊₁¹     (i = 0,1)
         → P₀², P₁²

Level 3: P₀³ = (1−t)P₀² + tP₁²
         → B(t) = P₀³
```

**Why this matters for fonts**: De Casteljau is not just evaluation — the
intermediate points at each level define the control points of the two
sub-curves produced by subdivision at parameter t:

- Left sub-curve: **P₀⁰**, **P₀¹**, **P₀²**, **P₀³**
- Right sub-curve: **P₀³**, **P₁²**, **P₂¹**, **P₃⁰**

This is the mathematical foundation of curve splitting operations used in
font editing and node insertion.

---

## Derivatives and Differential Properties

### First Derivative (Velocity / Tangent)

**B'**(t) = 3[(1−t)²(**P₁** − **P₀**) + 2(1−t)t(**P₂** − **P₁**) + t²(**P₃** − **P₂**)]

The first derivative is itself a quadratic Bezier defined by the control
points (**P₁** − **P₀**), (**P₂** − **P₁**), (**P₃** − **P₂**). This derived curve
is called the **hodograph**.

**Design application**: The tangent direction at any point determines:
- Handle angle at smooth nodes (G1 continuity)
- Stroke expansion direction for offset curves
- Extrema detection (where B'ₓ(t) = 0 or B'ᵧ(t) = 0)

### Second Derivative (Acceleration / Curvature)

**B''**(t) = 6[(1−t)(**P₂** − 2**P₁** + **P₀**) + t(**P₃** − 2**P₂** + **P₁**)]

A linear function of t — the second derivative of a cubic is linear.

### Curvature κ(t)

The signed curvature at parameter t:

κ(t) = (B'ₓ B''ᵧ − B'ᵧ B''ₓ) / (B'ₓ² + B'ᵧ²)^(3/2)

**Design application**: Curvature determines:
- Smoothness quality (abrupt curvature changes look "kinked")
- Optical weight distribution along curves
- Where round joins need the most arc-approximation nodes

### Inflection Points

An inflection point occurs where curvature changes sign: κ(t) = 0.

For a cubic Bezier, the numerator of κ(t) is quadratic in t, so there are
**at most 2 inflection points** per cubic segment.

**Detection**: Solve B'ₓ(t)B''ᵧ(t) − B'ᵧ(t)B''ₓ(t) = 0 for t ∈ (0,1).

**Design application**: Inflection points are critical for:
- Node placement strategy — nodes should be placed at or near inflection points
  for maximum curve control with minimum nodes
- Offset curve computation — offset curves can self-intersect at inflection points
- Subdivision strategy — subdivide at inflection points to produce
  monotone-curvature segments (simpler to process)

---

## Extrema Detection

Font compilers require explicit nodes at curve extrema (topmost, bottommost,
leftmost, rightmost points). Mathematically, these are where the derivative
components vanish:

**X-extrema**: Solve B'ₓ(t) = 0 → quadratic in t, at most 2 solutions
**Y-extrema**: Solve B'ᵧ(t) = 0 → quadratic in t, at most 2 solutions

For the quadratic 3[(1−t)²a + 2(1−t)tb + t²c] = 0 where a, b, c are the
hodograph control values:

Using substitution and the quadratic formula:

t = (a − b ± √(b² − ac)) / (a − 2b + c)

Filter for t ∈ (0,1) — solutions outside this range are not on the curve segment.

**Algorithm for adding extrema nodes**:
1. Compute all t values where B'ₓ(t) = 0 or B'ᵧ(t) = 0
2. Filter to t ∈ (0,1)
3. Sort filtered t values
4. Subdivide the curve at each t (using de Casteljau) sequentially
5. Each subdivision introduces a new on-curve point at the extremum

---

## Curve Subdivision

### Subdivision at Arbitrary t

Using de Casteljau, subdivide at parameter t to produce two curves that are
mathematically identical to the original but with a new shared endpoint at **B**(t).

This is the core operation for:
- Inserting nodes (the new subdivision point becomes an on-curve node)
- Splitting curves at extrema
- Adaptive rendering
- Intersection algorithms (recursive subdivision)

### Midpoint Subdivision (t = 0.5)

Special case with simplified arithmetic (no floating point needed if control
points are integers):

Left: **P₀**, (**P₀**+**P₁**)/2, (**P₀**+2**P₁**+**P₂**)/4, (**P₀**+3**P₁**+3**P₂**+**P₃**)/8
Right: (**P₀**+3**P₁**+3**P₂**+**P₃**)/8, (**P₁**+2**P₂**+**P₃**)/4, (**P₂**+**P₃**)/2, **P₃**

**Design application**: Midpoint subdivision is used in recursive flattening
algorithms to convert curves to line segments for rasterization, and in
curve-curve intersection tests.

---

## Arc-Length Parameterization

The parameter t is **not** proportional to arc length. A curve can traverse
most of its length in a small t interval if control points are unevenly spaced.

### Arc Length Integral

The total arc length L of a cubic Bezier:

L = ∫₀¹ |**B'**(t)| dt = ∫₀¹ √(B'ₓ(t)² + B'ᵧ(t)²) dt

This integral has no closed-form solution for cubics. Numerical methods:

1. **Gaussian quadrature** — typically 5-point Gauss-Legendre is sufficient
   for font-quality accuracy
2. **Recursive subdivision** — subdivide until segments are nearly linear,
   sum chord lengths
3. **Lookup table** — precompute L(t) at N sample points, interpolate

### Re-parameterization by Arc Length

Given arc length s ∈ [0, L], find t such that the arc length from 0 to t
equals s. This requires inverting the arc-length function:

t = L⁻¹(s)

**Method**: Newton-Raphson iteration on f(t) = ∫₀ᵗ |**B'**(τ)| dτ − s = 0

f'(t) = |**B'**(t)|

tₙ₊₁ = tₙ − f(tₙ)/f'(tₙ)

**Design application**: Arc-length parameterization is essential for:
- Evenly spaced dashing along stroked paths
- Uniform point distribution for offset curve computation
- Even interpolation of decorative elements along a path

---

## Circle Approximation by Cubic Beziers

Circles cannot be exactly represented by polynomial Bezier curves (they are
rational/algebraic, not polynomial). The standard approximation uses 4 cubic
segments, one per quadrant.

### The κ = 4(√2 − 1)/3 Constant

For a unit quarter-circle from (1,0) to (0,1):

**P₀** = (1, 0)
**P₁** = (1, κ)
**P₂** = (κ, 1)
**P₃** = (0, 1)

Where κ = 4(√2 − 1)/3 ≈ 0.5522847498

### Error Analysis

The maximum radial error of this approximation:

ε_max = (1 − cos(π/8))·(4κ − 1) ≈ 0.00027

That's 0.027% of the radius — well within font rendering tolerance at any
practical size. The error occurs at t = 0.5 (the midpoint of each quarter arc).

**Design application**: This approximation defines the 4-node-per-quadrant (8 nodes
total) circle construction used in all icon fonts. Understanding the error bound
confirms why 8 nodes are sufficient and additional nodes would not improve
visual quality at any rendered size.

### Higher-Accuracy Approximations

For specialized cases (very large optical sizes, display contexts):

- **8 segments** (octant arcs): ε_max ≈ 1.5 × 10⁻⁵ (16 nodes total)
- **Rational Bezier** (exact): requires weights, not supported in CFF2

For CentricSymbols, the standard 4-segment approximation is always sufficient.

---

## Offset Curves (Parallel Curves)

The mathematical core of stroke expansion — converting a centered stroke path
into filled outlines.

### Definition

Given curve **C**(t) and offset distance d, the offset curve:

**C_d**(t) = **C**(t) + d · **n̂**(t)

Where **n̂**(t) is the unit normal:

**n̂**(t) = (−B'ᵧ(t), B'ₓ(t)) / |**B'**(t)|

### The Fundamental Problem

The offset of a cubic Bezier is **not** a cubic Bezier. It's a degree-10
algebraic curve (for cubics). This means exact offset curves cannot be
represented in the font format.

### Approximation Strategies

1. **Tiller-Hanson method**: Offset the control polygon, then adjust. Fast but
   inaccurate for high curvature.

2. **Subdivision + local offset**: Subdivide the curve into segments with low
   curvature variation, offset each locally, rejoin. This is what most font
   tools use.

3. **Variational approach**: Minimize the deviation between the true offset
   and a cubic approximation using least-squares fitting.

### Self-Intersection at Inflection Points

When the offset distance d exceeds the radius of curvature |1/κ(t)| at any
point, the offset curve **self-intersects**. This produces the "loops" that
must be trimmed in stroke-to-outline conversion.

**Detection**: Find all t where |κ(t)| > 1/d. At these points, the offset
curve crosses itself.

**Resolution**: Subdivide at the inflection points, compute offset segments
separately, trim the self-intersecting loops, and rejoin. This is why
stroke-to-outline operations can produce unexpected node counts.

---

## Curve Fitting and Node Reduction

### The Fitting Problem

Given a set of sample points {**Qⱼ**}, find control points **P₀**, **P₁**, **P₂**,
**P₃** that minimize the fitting error:

E = Σⱼ |**B**(tⱼ) − **Qⱼ**|²

This is a nonlinear least-squares problem because the parameter values tⱼ
are unknown.

### Philip Schneider's Algorithm

The standard algorithm used in font tools:

1. **Chord-length parameterization**: Assign tⱼ = Σₖ₌₁ʲ |Qₖ − Qₖ₋₁| / L_total
2. **Fit endpoints**: P₀ = Q₀, P₃ = Qₙ (forced interpolation)
3. **Solve for handles**: Set up the least-squares system for P₁, P₂ given the
   endpoint tangent constraints
4. **Iterate**: Re-parameterize using Newton-Raphson, re-fit, repeat until
   convergence or tolerance met
5. **Split if needed**: If error exceeds tolerance, subdivide the point set
   at the worst-error point, fit each half recursively

### Node Reduction

The inverse of fitting — given a multi-segment spline, reduce the number of
nodes while staying within a tolerance ε:

1. Merge adjacent segments into a single cubic
2. Measure maximum deviation
3. If deviation < ε, accept the merge; otherwise keep the original segments
4. Process greedily or optimally (dynamic programming for global optimum)

**Design application**: Node reduction is critical for:
- Simplifying outlines after boolean operations (which often produce excess nodes)
- Optimizing glyphs for file size
- Preparing masters for interpolation (fewer nodes = fewer potential
  compatibility issues)

**Constraint**: Node reduction must preserve parity across masters — you
cannot reduce nodes in one master without performing the identical reduction
in all other masters.

---

## Continuity Classification

### Geometric Continuity Grades

At the junction of two Bezier segments sharing endpoint **P**:

| Grade | Requirement | Visual Result |
|-------|------------|---------------|
| G⁻¹ | Gap between segments | Discontinuous (broken path) |
| G⁰ | Shared endpoint | Positional continuity (corner) |
| G¹ | Colinear handles, any length ratio | Tangent continuity (smooth) |
| G² | Matching curvature at junction | Curvature continuity (very smooth) |
| G³ | Matching curvature derivative | "Perfect" smoothness |

### Parametric vs. Geometric Continuity

- **C¹** (parametric): tangent vectors are equal → implies G¹ but also constrains speed
- **G¹** (geometric): tangent vectors are proportional → weaker but sufficient for visual smoothness

Font outlines use G¹ at smooth nodes (colinear handles, lengths may differ).
G² is achievable but not typically enforced — it matters more for industrial
design curves than icon outlines.

### Continuity Verification Algorithm

At junction point **P** = **B₁**(1) = **B₂**(0):

```
G⁰: |P₁_end − P₂_start| < ε                     (positional)

G¹: (P₁_end − P₁_handle_in) × (P₂_handle_out − P₂_start) = 0   (cross product = 0 → colinear)

G²: κ₁(1) = κ₂(0)                                 (curvature match)
```

---

## Quadratic-to-Cubic Promotion

TrueType fonts use quadratic Bezier curves; CFF/CFF2 uses cubic. When
converting:

Given quadratic control points **Q₀**, **Q₁**, **Q₂**:

**P₀** = **Q₀**
**P₁** = **Q₀** + (2/3)(**Q₁** − **Q₀**) = (1/3)**Q₀** + (2/3)**Q₁**
**P₂** = **Q₂** + (2/3)(**Q₁** − **Q₂**) = (2/3)**Q₁** + (1/3)**Q₂**
**P₃** = **Q₂**

This conversion is **exact** — a quadratic Bezier is a special case of cubic
where the two handles are constrained to specific positions. No approximation
error is introduced.

The reverse (cubic to quadratic) is **lossy** and requires approximation
algorithms — relevant when targeting TrueType output.

---

## Computational Considerations for Font Pipelines

### Integer Arithmetic

Font coordinates are typically integers (grid-aligned). Many Bezier operations
can be performed in integer arithmetic if subdivision is at dyadic rationals
(t = k/2ⁿ), avoiding floating-point error accumulation.

### Numerical Stability

- De Casteljau is numerically stable; direct polynomial evaluation is not
- For root-finding (extrema, inflections), use companion matrix eigenvalue
  methods for robust cubic/quadratic root finding rather than the quadratic
  formula (which suffers catastrophic cancellation when discriminant ≈ 0)
- When testing for colinearity (G¹), use cross-product magnitude with an
  angular tolerance, not exact zero comparison

### Precision Budget

At UPM 2048 with 24×24 source grid (scale factor ≈ 85.33):
- Source precision: 1 unit = 1/24 of em
- Target precision: 1 unit = 1/2048 of em
- Subdivision and fitting operations should preserve precision to ±0.5 UPM units
- At 20px rendered size: 1 UPM unit ≈ 0.01 pixels — well below visible threshold


---

## Design-Forward Operating Directive

This skill provides the deepest mathematical foundations in the system — but
mathematics here is never an end in itself. Every theorem, formula, and
algorithm exists to produce curves that **look beautiful and read clearly** at
their final rendered size.

### Principles

1. **Connect every formula to a visual outcome.** When presenting a curvature
   analysis, an offset curve approximation, or a node reduction strategy,
   always close the loop: "This matters because at 20px, the user will see..."
   Mathematics without visual grounding is incomplete in this context.

2. **Aesthetic smoothness outranks minimal node count.** The minimum-node
   representation is not automatically the best. If a curve fitting algorithm
   produces a 4-node result with visible curvature discontinuity, and a
   5-node result with G2 continuity, recommend the 5-node version — then
   explain the mathematical tradeoff (node parity cost vs. curvature quality).

3. **Error bounds are perceptual thresholds.** When computing approximation
   errors (circle-to-Bezier, offset curve, arc-length), translate the
   numerical error into rendered pixels at the relevant optical sizes. An
   error of 0.3 UPM units is meaningless to a designer; "invisible at all
   sizes above 12px" is actionable.

4. **Serve the design spokes proactively.** When `lead-vector-designer` faces
   a node placement dilemma, provide not just the mathematical analysis but a
   design-informed recommendation: "Place the node at the inflection point
   (t ≈ 0.38) because this gives maximum curvature control at the transition
   from the straight segment to the arc — the point where visual quality is
   most sensitive."

5. **Prefer elegant solutions.** When multiple mathematical approaches solve
   the same problem, prefer the one that produces cleaner geometry, more
   predictable interpolation behavior, and simpler downstream maintenance —
   even if it's not the theoretically optimal one. Engineering taste and
   design sensibility apply to mathematics too.
