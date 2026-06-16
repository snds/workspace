---
name: type-letterform-construction
description: >
  Bezier craft and construction principles for text glyphs. Use this skill
  whenever the conversation involves: drawing specific letterforms, evaluating
  letterform quality, stem weight decisions, overshoot values, counter design,
  optical corrections built into construction, weight relationships across a
  type family, G2 curvature continuity, node placement for text glyphs,
  how construction decisions affect screen rendering, the difference between
  text type and display type construction, regularization and typographic
  texture, or any question about how to draw a letter correctly for a text face.
  Spoke of `lead-type-designer`. For icon glyph construction, use
  `variable-icon-font-architect`/`lead-vector-designer`.
aliases: [type-letterform-construction]
tier: spoke
domain: design
hub: lead-type-designer
prerequisites: [lead-type-designer]
spec_version: "2.0"
---

# Type Letterform Construction

Specialist lens for bezier craft and construction principles in text typeface
design. Part of the `lead-type-designer` skill network.

---

## Domain Boundary

This skill owns **letterform construction decisions for text typefaces** — how
to draw glyphs that read well at text sizes across a type family.

- **Icon glyph construction** → `variable-icon-font-architect`/`lead-vector-designer`
- **Spacing the resulting glyphs** → `type-spacing-metrics`
- **Screen rendering and font selection** → `lead-ui-designer`/`uid-type-for-screens`
- **Bezier mathematics** → `variable-icon-font-architect`/`math-bezier-spline-theory` (shared math)
- **Visual perception principles** → `variable-icon-font-architect`/`math-optical-optimization` (shared)

---

## Text Type vs. Display Type Construction

The single most important contextual distinction in letterform construction.

### Text Type Construction (6–20pt / 8–28px)

Text type must survive:
- Anti-aliasing at small sizes (screen rendering smears fine detail)
- Extended reading duration (fatigue from irregular texture)
- Variable rendering environments (retina vs. 1x, Windows ClearType vs. macOS subpixel)

Construction priorities:
- **Robust forms**: No hairlines thinner than ~40u at 1000 UPM; nothing too delicate to survive rasterization
- **Generous x-height**: Taller x-height improves legibility at small sizes by giving lowercase letters more visual mass
- **Open apertures**: The openings in letters like c, e, a, s should not be nearly closed — closed apertures blur together at text size
- **Moderate stroke contrast**: The ratio between thick and thin strokes should not be extreme; Bodoni-level contrast fails at text size
- **Even texture priority**: The overriding goal at text sizes is an even gray texture — each letter must contribute its share of ink without disrupting rhythm

### Display Type Construction (24pt+ / 32px+)

Display type can be:
- **Refined and delicate**: Hairlines can be very fine; details that would blur at text size are visible and expected at display
- **High contrast**: Dramatic thick/thin ratios (Bodoni, Didot-style) work at large sizes
- **Tightly spaced**: Display sizes benefit from tighter tracking
- **Optically sophisticated**: Subtle curvature refinements, very precise overshoot values, nuanced terminal shapes — all visible at large sizes

**Failure modes**:
- Text-type construction at display size → looks clunky, inelegant, "designed for small"
- Display-type construction at text size → hairlines disappear, contrast overwhelms, reads poorly

The **opsz variable axis** is the technical solution: one font file with masters optimized for text and display sizes. See `type-variable-text` for opsz implementation.

---

## Stem Weight and Stroke Contrast

### Optical Illusions in Stroke Weight

Mathematical equality produces optical inequality. These corrections are mandatory:

**Horizontal strokes appear heavier than vertical strokes of identical width.**
- Cause: Physiological — the eye's horizontal motion in reading sensitizes it to horizontal mass
- Correction: Horizontal strokes (crossbars of E, H, T, f; thin strokes in O) must be drawn thinner than vertical stems of the intended "same" weight
- Magnitude: Typically 10–20% thinner depending on typeface weight

**Counter-intuitive consequence**: In a 400-weight text face with 80u vertical stems, the horizontal crossbars may need to be 65–70u to appear the same weight.

### Stroke Contrast Systems

Different historical periods produced different contrast models:

| Contrast Model | Stress Axis | Examples | Use Context |
|---|---|---|---|
| Humanist | Diagonal (calligraphic) | Garamond, Jenson | Literary, humanist, warm |
| Garalde | Diagonal, moderate | Minion, Palatino | Book text, editorial |
| Transitional | Vertical, moderate | Baskerville, Times | Formal, authoritative |
| Didone | Vertical, extreme | Bodoni, Didot | Fashion, luxury, headline |
| Geometric sans | None (monolinear) | Futura, Avenir | Modern, geometric |
| Humanist sans | Slight diagonal | Gill Sans, Frutiger | Approachable, legible |

The stress axis and contrast ratio are primary construction decisions — they determine the historical register and appropriate use context of the typeface.

---

## Counter Design

The counter (enclosed or partially enclosed negative space) is **as important as
the positive letterform**. A typeface is a system of white and black in balance.

### Counter Sizing Principles

- Well-designed counters create **even gray texture** in text blocks
- At text sizes, counters must be large enough to remain open after rasterization
- Minimum counter width for text faces: approximately 40–50% of the total advance width in a letter like 'o'
- Counters that are too small close up at small sizes and read as dark spots
- Counters that are too large (very light weights) make the text feel thin and fragile

### Counter Shape Quality

The shape of the counter is a design decision, not a residue:

- **Humanist counters**: Slightly irregular, calligraphy-derived, warm
- **Geometric counters**: Circular, mathematically precise, cool
- **Transitional counters**: Between the two — not quite circular, not quite calligraphic

### The Double-Counter Problem (lowercase a)

Two-story 'a' has a complex counter system — the upper counter (above the bowl) and the lower counter (the bowl itself) must both be well-formed. The junction between the bowl and the stem is one of the most technically demanding details in text type design. The single-story 'a' (used in italic and some sans-serif designs) trades the complex junction for a simpler but potentially more ambiguous letterform.

---

## Overshoot

Curved forms (O, C, G, S, o, c, e) and pointed forms (A, V, W, M, v, w) must
extend slightly **beyond** the cap line and baseline to **appear** the same
height as flat-top/bottom forms (H, I, E, L, h, i, l).

### Why Overshoot Is Necessary

The optical illusion: a circle inscribed precisely within a square appears smaller
than the square. The eye reads the corners of the flat form as defining its maximum
extent; the curved form only touches the boundary at a single tangent point, which
reads as smaller.

### Overshoot Values for Text Type

| Form type | Typical overshoot | Notes |
|---|---|---|
| Caps O, C, G, S | 1–3% of cap height | At 700u cap height, 7–21u overshoot |
| Lowercase o, c, e | 1–2.5% of x-height | Proportional to x-height, not cap height |
| Pointed caps A, V, W | 1.5–3% of cap height | Points need more overshoot than rounds |
| Pointed lowercase v, w | 1–2% of x-height | Similar to caps but scaled |
| Figures (0, 6, 8, 9) | 1–2% of figure height | Figures often slightly shorter than caps |

**Anti-pattern**: Overshoot values that are too small make rounds look small;
values that are too large make rounds look oversized. Text-size testing is required
— overshoot that reads correctly at display size may need adjustment for text-size rendering.

---

## Optical Center

**Mathematical center is not optical center.**

- Elements positioned at mathematical center of a space appear to sit too low
- Optical center is approximately 55–60% from the bottom (i.e., slightly above the midpoint)
- Applies to: crossbars on A, H, f; middle arm of E, F; center crossbar of uppercase B (lower half should be larger than upper half)
- The uppercase B's lower bowl is always larger than the upper bowl — this is not a stylistic choice, it is an optical correction that makes both halves appear equal

---

## Bezier Craft for Text Glyphs

### Node Placement Principles

Text type bezier construction follows the same physical laws as icon construction,
but the priorities are shaped by readability requirements:

**Smooth curve entry/exit**: Handles must align with the curve's tangent at the
node — a handle that deviates from the tangent creates an inflection point at the
join, which creates visual texture in the outline.

**Tension balance**: The handles on either side of a smooth curve node should
have proportional lengths relative to the curve's total arc. Handles too long
produce overly flat curves; handles too short produce pinched curves.

**Node economy**: Minimum nodes required to produce a smooth curve. Excess nodes
introduce subtle kinks that appear as noise at high resolution and as rendering
artifacts at text size.

**Preferred node positions**: Place oncurve nodes at extrema (topmost, bottommost,
leftmost, rightmost points of a curve). This is required by many font compilers and
improves rendering correctness.

### G2 Curvature Continuity

G2 continuity (matching curvature, not just tangent direction) produces visually
smoother curves than G1 (matching tangent only). At text sizes, the difference
between G1 and G2 is subtle but contributes to the overall quality impression
of a typeface — a G2 typeface has a smoothness that G1 typefaces lack.

G2 curves require handles that satisfy the curvature matching condition at each
join — more complex to construct but the standard for premium text type.

**Practical implication**: When evaluating letterform quality, zoom in on the
junction between curved and straight elements (e.g., the shoulder of 'n',
the bowl entry of 'b', 'd', 'p', 'q'). A sharp curvature change at the junction
indicates G1 at best; a smooth transition indicates G2 construction.

---

## Weight Relationships Across a Type Family

### The Weight Ratio Problem

In a type family from Thin (100) to Black (900):

- **Thin weights**: The counters dominate; stroke is the residual
- **Regular weights (400)**: Stroke and counter are in balance
- **Bold weights (700)**: Stroke dominates; counters are squeezed but must remain open
- **Black (900)**: Strokes nearly touch; counters are minimum viable

The **stroke-to-counter ratio changes** across the weight range. Interpolating a
black from a regular by mechanically expanding strokes in all directions produces
incorrect letterforms — the counters collapse too quickly or the overall proportions
become distorted.

### Spacing Changes With Weight

Heavier weights need tighter sidebearings (relatively) because the letters have
more mass — the same numerical sidebearing that works for a Thin looks too wide on
a Black, and too narrow on the Thin. Route to `type-spacing-metrics` for the full
spacing system.

---

## Regularization — The Even Gray Test

The ultimate test for letterform construction quality in a text typeface:

**Set a paragraph of text in the typeface at the intended size. Step back. Squint.**

The paragraph should read as an even gray rectangle. Dark spots indicate too much
ink in one area (over-heavy stroke, too-small counter). Light spots indicate too
little ink (too-light stroke, too-large counter, poor spacing).

Letters must appear visually equal in weight even though they are geometrically
different. H and O have different shapes but must contribute the same amount of
visual mass per unit of advance width. This **regularization** is the designer's
primary craft judgment — it cannot be derived mathematically, only tested visually.

---

## Anti-Patterns and Failure Modes

| Anti-pattern | Symptom | Fix |
|---|---|---|
| Equal-weight horizontals and verticals | Crossbars appear too heavy, text reads dark | Thin horizontal strokes 10–20% relative to verticals |
| No overshoot on curved forms | Rounds appear smaller than flat forms | Add 1–3% overshoot at cap height and x-height |
| Mathematical centering of elements | Crossbars and middle arms appear low | Raise by 5–10% toward optical center |
| G1 curve junctions | Visible kink at curved-to-straight transitions | Rebuild junctions with G2 curvature matching |
| Excess nodes at non-extrema | Subtle kinks in curves, rendering artifacts | Consolidate to extrema placement |
| Display construction at text size | Fine hairlines disappear, high contrast overwhelms | Rebuild with text-appropriate contrast and robustness |
| Counter collapse across weight range | Bold weight illegible, black weight unusable | Redesign weight extrema with correct counter sizing |

---

## Cross-Links

- `variable-icon-font-architect`/`lead-vector-designer` — bezier construction craft is shared; path direction, node parity, boolean hygiene apply to both text and icon glyphs
- `variable-icon-font-architect`/`math-bezier-spline-theory` — the underlying parametric curve math
- `variable-icon-font-architect`/`math-optical-optimization` — perceptual models for weight compensation, overshoot calculation
- `type-spacing-metrics` — after construction, letterforms must be spaced; the two are deeply interdependent
- `type-variable-text` — construction decisions propagate through variable font interpolation; weight axis compatibility requires construction consistency
- `ds-advisor` — how construction quality informs type scale decisions; optical size steps in the type scale should reflect actual perceptual differences at the construction level
- `lead-ui-designer`/`uid-type-for-screens` — construction decisions (stem weight, counter size, aperture openness) predict which typefaces render well on screen
