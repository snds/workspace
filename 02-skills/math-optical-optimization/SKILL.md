---
name: math-optical-optimization
description: >
  Perceptual optimization, psychophysical modeling, and variational methods for
  visual correctness and optical compensation. Use this skill whenever the
  conversation requires: overshoot calculation (why round shapes extend beyond
  flat boundaries), optical weight balancing across stroke orientations, stroke
  contrast modeling, counter area optimization for legibility, spatial frequency
  analysis of shapes at varying sizes, Weber-Fechner / Stevens power law applied
  to stroke weight perception, APCA / WCAG luminance contrast modeling, perceptual
  uniformity in weight/grade axes, least-squares and gradient descent for
  parameter fitting, energy minimization for curve smoothness (minimum curvature
  variation), Laplacian smoothing of point sets, perceptual hashing for shape
  similarity, area moment analysis for visual center-of-mass, or any formal
  mathematical treatment of making shapes "look right" — the quantitative bridge
  between geometry and human visual perception. This skill provides the
  optimization theory — not the curve math (math-bezier-spline-theory) or the
  shape topology (math-computational-geometry).
aliases: [math-optical-optimization]
spec_version: "2.0"
---

# Optical Optimization Mathematics

Doctoral-level perceptual optimization and psychophysical modeling for visual
correctness. Part of the precision vector & parametric design skill network.

---

## Domain Boundary

This skill owns **the mathematics of visual perception applied to shape
correction** — quantitative models of how humans perceive weight, size, balance,
and legibility, and optimization methods to achieve perceptual targets.

- **Curve construction math** → `math-bezier-spline-theory`
- **Shape topology & booleans** → `math-computational-geometry`
- **Multi-axis interpolation** → `math-interpolation-designspace`
- **Icon design decisions** → `lead-icon-artist`

---

## Psychophysical Foundations

### Weber-Fechner Law

Human perception of stimulus change follows a logarithmic relationship:

ΔS = k · ln(I/I₀)

Where:
- ΔS = perceived change in sensation
- I = stimulus intensity
- I₀ = reference intensity
- k = constant (modality-dependent)

**Design application**: Perceived weight differences between font weights should
be perceptually uniform. If weight axis values are linearly spaced (100, 200,
300...), the perceived differences are **not** uniform because perception is
logarithmic. This is why:
- The jump from wght=100 to wght=200 looks dramatic
- The jump from wght=600 to wght=700 looks subtle
- Perceptually uniform spacing requires geometric (not arithmetic) progression
  of stroke widths

### Stevens' Power Law (Refined Model)

S = k · Iⁿ

Where n is the exponent for the modality. For visual area perception, n ≈ 0.7,
meaning:
- A shape that is 2× the area appears only ~1.62× as large
- To appear 2× as large, a shape must be ~2.7× the area

**Design application**: When scaling icons for optical size (opsz axis), the
geometric scale factor and the perceived scale factor diverge. An icon at
opsz=48 is 2.4× the linear dimension of opsz=20, but the area is 5.76×,
which appears only ~3.7× as large perceptually.

---

## Overshoot Theory

### The Problem

Circles appear smaller than squares of the same geometric dimension because
the human visual system weights shapes by their area near the alignment
boundary, not by their extrema. The visual system performs a local averaging
operation near the edge.

### Quantitative Model

For a circle inscribed in a square of side s:

- Square area = s²
- Circle area = πs²/4 ≈ 0.785s²
- Area near the boundary (within δ of each edge):
  - Square: ~4sδ (uniform along all four edges)
  - Circle: ~4sδ · (2/π) ≈ 2.55sδ (reduced at tangent points)

The circle "occupies" less visual space near the alignment edge, so it appears
smaller. The overshoot compensates by pushing the extrema beyond the boundary.

### Overshoot Formula

For a glyph of height h and a circular element that should appear to match
height h:

overshoot = h · (1 − (A_circle / A_square)^(1/n))

Where n is the Stevens exponent for length perception (≈0.7–0.8 depending on
the study).

**Practical values** (empirically validated in type design):
- Circles: ~1.5–2% overshoot (~0.5 units on a 24-unit grid)
- Triangles/pointed shapes: ~2.5–3% overshoot (~0.7 units)
- Diamonds: ~2% overshoot

At the CentricSymbols scale (24×24 grid):
- Circle overshoot ≈ 0.36–0.48 units → round to 0.5 units
- Triangle overshoot ≈ 0.6–0.72 units → round to 0.75 or 1.0 units

### Overshoot Across Axes

The overshoot amount should vary with the `wght` axis:
- Thin weights (100): larger overshoot (thinner strokes reduce visual mass
  more at extrema)
- Bold weights (700): smaller overshoot (heavier strokes provide more visual
  anchoring at extrema)

Approximate relationship: overshoot ∝ 1/√(stroke_width)

---

## Stroke Weight Perception

### Orientation-Dependent Weight

Horizontal, vertical, and diagonal strokes of identical geometric width appear
to have different visual weights:

| Orientation | Perceived Weight (relative) | Compensation |
|-------------|---------------------------|-------------|
| Vertical | 1.00 (reference) | None |
| Horizontal | ~1.05–1.08 | Thin by 2–5% |
| Diagonal (45°) | ~0.92–0.95 | Thicken by 5–8% |
| Diagonal (steep) | ~0.96–0.98 | Thicken by 2–4% |

### Physical Basis

The retina has higher resolution along the horizontal axis (more cone density),
so horizontal strokes activate more photoreceptors per unit length, increasing
perceived weight. Diagonal strokes traverse more inter-receptor gaps, reducing
perceived weight.

### Compensation Model

For a baseline stroke width w (vertical reference):

w_h = w / (1 + α_h)     where α_h ≈ 0.03–0.05
w_d = w · (1 + α_d)     where α_d ≈ 0.05–0.08

These compensations apply to the glyph outline positions. In the skeleton-and-
meat model, they translate to direction-dependent radius:

r(θ) = r₀ · (1 + α · cos(2θ))

Where θ is the stroke angle and α encodes the compensation magnitude.

---

## Counter Area Optimization

### Legibility Model

At small sizes (opsz=20), legibility is dominated by counter (negative space)
visibility. A counter that is geometrically present but below the visual
resolution threshold is functionally invisible.

### Minimum Counter Area

For a rendered size of p pixels, the minimum perceptible counter:

A_min = (k / p²) · A_glyph

Where k is a constant determined by display PPI and viewing distance. For
typical screen conditions (96–220 PPI, 40–60cm viewing):

At 20px rendered height:
- Minimum counter width ≈ 2px (geometric) → 2 grid units at opsz=20
- Minimum counter area ≈ 4px² → 4 grid units²

### Counter Opening Optimization

For the opsz axis, the pipeline should verify:

```
For each counter in the glyph at opsz=20:
  Compute: minimum inscribed circle radius r_min
  If r_min < threshold (≈1 grid unit):
    Flag for manual review or automatic widening
```

The widening operation must preserve node count (topology) — it moves nodes
outward, it doesn't add or remove them.

### Area Moment Analysis (Visual Center of Mass)

The visual center of a glyph is its area centroid:

x̄ = (1/A) ∫∫ x dA
ȳ = (1/A) ∫∫ y dA

For glyph outlines (boundary integral via Green's theorem):

x̄ = (1/6A) Σᵢ (xᵢ + xᵢ₊₁)(xᵢyᵢ₊₁ − xᵢ₊₁yᵢ)
ȳ = (1/6A) Σᵢ (yᵢ + yᵢ₊₁)(xᵢyᵢ₊₁ − xᵢ₊₁yᵢ)

**Design application**: The visual center should be at the optical center of the
icon grid (slightly above geometric center). If the centroid deviates
significantly, the icon appears top-heavy or bottom-heavy.

**Visual weight audit (mathematical)**: Compute the centroid for every icon in
the set. The standard deviation of centroid positions across the set is a
quantitative measure of visual weight consistency.

---

## Curve Smoothness Optimization

### Minimum Curvature Variation Energy

A "smooth" curve minimizes abrupt changes in curvature. The smoothness energy
functional:

E_smooth = ∫ (dκ/ds)² ds

Where κ is curvature and s is arc length. This is the **minimum variation curve**
(MVC) energy, a standard in CAGD (Computer-Aided Geometric Design).

### Euler Spiral Connection

The curve that minimizes E_smooth with fixed endpoint positions and tangents is
the **Euler spiral** (clothoid), where curvature varies linearly with arc length:

κ(s) = κ₀ + (κ₁ − κ₀) · s/L

Euler spirals are used in:
- Transition curves between straight and circular sections (highway design)
- Type design for "perfect" smooth transitions (some foundries use them)
- Evaluating the smoothness quality of Bezier approximations

### Practical Smoothness Metric

For a Bezier spline with N segments, compute curvature at M sample points.
The smoothness score:

S = (1/M) Σⱼ (κⱼ₊₁ − κⱼ)²

Lower S = smoother curve. Compare across candidate designs to select the
smoothest representation with the fewest nodes.

### Laplacian Smoothing of Node Positions

For a set of nodes **Pᵢ** along a curve, one iteration of Laplacian smoothing:

**Pᵢ'** = **Pᵢ** + λ · (**L**(**Pᵢ**))

Where **L**(**Pᵢ**) = ½(**Pᵢ₋₁** + **Pᵢ₊₁**) − **Pᵢ** (the discrete Laplacian)

And λ ∈ (0, 1) is the smoothing factor.

**Caution**: Laplacian smoothing shrinks shapes (it's a diffusion process).
Use Taubin smoothing (alternate λ and negative μ steps) to smooth without
shrinkage.

**Design application**: Smoothing can clean up noisy node positions after
automated operations (boolean cleanup, node reduction), but must be applied
identically across all masters to preserve interpolation parity.

---

## Perceptual Uniformity in Axis Design

### Weight Axis Spacing

For the `wght` axis to produce perceptually uniform weight steps, the stroke
width should follow a geometric progression:

w(n) = w₀ · rⁿ

Where:
- w₀ = stroke width at minimum weight (wght=100)
- r = common ratio (determined by min/max weight range)
- n = step index (0 at wght=100, N at wght=700)

For CentricSymbols with wght ∈ [100, 700]:
- If w(100) = 1.0 and w(700) = 3.5 (units)
- r = (3.5/1.0)^(1/6) ≈ 1.232 per 100-unit step
- Intermediate: w(200)≈1.23, w(300)≈1.52, w(400)≈1.87, w(500)≈2.31, w(600)≈2.84

### Grade Axis as Iso-Width Perturbation

The `GRAD` axis modifies visual weight without changing advance width. This is
a constrained optimization:

**Minimize**: |w_new − w_target|²  (achieve target weight)
**Subject to**: advance_width remains constant

Geometrically: increase inner stroke expansion while decreasing outer stroke
expansion by the same amount. The constraint makes GRAD a differential quantity
(a perturbation around the nominal weight).

The GRAD axis value is conventionally expressed as the change in stem weight
in UPM units. At GRAD=0, stems are nominal. At GRAD=200, stems are 200 units
heavier (without advance width change).

### Optical Size Axis Scaling

The relationship between rendered pixel size and detail density is nonlinear.
A model for the maximum detail frequency f_max at rendered size p:

f_max(p) = (p / 2) · (1 − margin)

Where margin accounts for anti-aliasing blur (~0.5px). At p=20: f_max ≈ 9.75
cycles across the glyph — meaning features finer than ~2px spacing are
unresolvable.

This provides a quantitative basis for the opsz=20 simplification rule: remove
any feature whose spatial frequency exceeds f_max(20).

---

## Optimization Methods

### Least-Squares Fitting for Parameter Estimation

Many optical corrections involve fitting a model to empirical data (measured
perceived weights, overshoot amounts validated by designers):

**Problem**: Find parameters **θ** that minimize:

E(**θ**) = Σⱼ (model(xⱼ; **θ**) − yⱼ)²

**Methods**:
- **Linear least squares**: when model is linear in θ → solve A^T A θ = A^T y
- **Gauss-Newton**: when model is nonlinear → iterative linearization
- **Levenberg-Marquardt**: Gauss-Newton with regularization → robust convergence

### Gradient Descent for Continuous Optimization

For smooth objective functions (e.g., minimizing curvature variation energy):

**θ**ₙ₊₁ = **θ**ₙ − η · ∇E(**θ**ₙ)

With step size η chosen by line search or adaptive methods (Adam, L-BFGS).

**Design application**: Optimizing node positions to simultaneously minimize:
- Curvature variation (smoothness)
- Deviation from target shape (fidelity)
- Node count (simplicity)

This is a multi-objective optimization — the Pareto front represents the
tradeoff between smoothness and fidelity at each node count.

### Constrained Optimization for Grid Alignment

Icon font nodes must lie on integer grid coordinates. This makes optimization
a **mixed-integer programming** problem:

**Minimize**: E(shape quality)
**Subject to**: all coordinates ∈ ℤ (integer grid)

**Practical approach**: optimize in continuous space, then snap to grid, then
evaluate quality. If snapping degrades quality beyond threshold, try adjacent
grid points (enumerate the ≤ 4 nearest integer positions for each node).

---

## Contrast and Legibility Mathematics

### APCA (Accessible Perceptual Contrast Algorithm)

APCA models perceived contrast between foreground and background as:

L_c = (Y_bg^0.56 − Y_fg^0.57) × 1.14    (dark text on light bg)
L_c = (Y_bg^0.65 − Y_fg^0.62) × 1.14    (light text on dark bg)

Where Y is the relative luminance computed from sRGB:

Y = 0.2126·R_lin + 0.7152·G_lin + 0.0722·B_lin

And R_lin = (R_srgb/255)^2.4 (simplified gamma)

**Design application**: Icon stroke weight at small sizes must produce sufficient
APCA contrast. Thinner strokes at opsz=20 risk falling below the Lc 45
threshold for body text equivalents. The minimum stroke width for a given
background luminance can be computed from the APCA model.

### Spatial Frequency and MTF

The Modulation Transfer Function (MTF) of the human visual system determines
how well fine details are perceived:

MTF(f) ≈ exp(−(f/f₀)²)

Where f is spatial frequency (cycles per degree of visual angle) and f₀ ≈ 8
cpd is the peak sensitivity. Above ~30 cpd, sensitivity drops to near zero.

For a 20px icon at 96 PPI viewed at 50cm:
- 1 pixel = 0.264mm → ~1.8 arcmin → ~0.03°
- Nyquist frequency: 1/(2·0.03°) ≈ 17 cpd
- Effective MTF at Nyquist: MTF(17) ≈ 0.12 → only 12% contrast transmitted

This means a 1px feature at 20px is barely visible. Minimum perceptible
feature: ~2px (8.5 cpd, MTF ≈ 0.62 → 62% contrast transmitted).

---

## Perceptual Hashing for Icon Similarity

### Purpose

Quantitatively detect when two icons are visually too similar (confusion risk
in the icon set) or when a weight variant has diverged too far from its base.

### Method: Radial Moment Descriptor

1. Rasterize the glyph at a fixed size (e.g., 32×32)
2. Compute the centroid (center of mass)
3. Divide the surrounding area into N angular bins × M radial bins
4. Compute the fill ratio in each bin
5. The resulting N×M matrix is the descriptor

**Distance metric**: cosine similarity between descriptors. Similarity > 0.95
suggests potential confusion; similarity < 0.7 between weight variants suggests
the weight axis may be altering the icon's identity.

### Zernike Moments (Higher Precision)

Zernike polynomials form an orthogonal basis on the unit disk. Project the
glyph image onto Zernike moments for rotation-invariant shape descriptors
with controllable frequency resolution.

**Design application**: Zernike moments can detect systematic shape differences
between masters (e.g., "the thin master's circles are slightly squashed") that
might be invisible in spot checks but produce interpolation artifacts.


---

## Design-Forward Operating Directive

This skill sits at the intersection of mathematics and human perception — it
is inherently design-forward. But the risk is in the opposite direction: over-
relying on mathematical models and losing sight of the fact that perception is
variable, contextual, and ultimately subjective.

### Principles

1. **Models are starting points, not verdicts.** Weber-Fechner, Stevens' power
   law, and APCA are excellent predictive models — but they describe average
   perception under controlled conditions. Real users view icons in variable
   lighting, on diverse displays, in peripheral vision, while distracted.
   Present model outputs as informed recommendations, not prescriptions.

2. **Optical correction is an art practiced with mathematical tools.** The
   overshoot formula gives a starting value; the designer's eye determines
   the final value. When the formula says 0.48 units and the designer says
   0.5, the designer is probably right — they're integrating context the
   formula can't capture (surrounding icons, UI density, brand voice).

3. **Perceptual uniformity is a design goal, not a mathematical constraint.**
   The weight axis should *feel* even across its range. If the logarithmic
   spacing model produces weights that *feel* uneven to the designer, the
   model needs adjustment — not the designer's perception. Iterate between
   mathematical prediction and visual validation.

4. **Quantify what designers sense intuitively.** The greatest value of this
   skill is giving designers rigorous language for what they already know:
   "that icon feels heavier" becomes "its area centroid is 1.2 units lower
   than the set average." "That weight step feels bigger" becomes "the stroke
   width ratio is 1.35 instead of the target 1.23." This validates design
   intuition and makes it communicable.

5. **Aesthetics emerge from structure.** The most beautiful icons are ones
   where optical corrections are invisible — where the geometry quietly
   compensates for perceptual bias so the viewer sees only clarity, balance,
   and intentional form. The math should disappear into the design.
