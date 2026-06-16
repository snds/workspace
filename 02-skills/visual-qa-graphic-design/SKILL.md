---
name: visual-qa-graphic-design
description: >
  Graphic design visual QA specialist. Use this skill for reviewing: typography,
  type hierarchy, typeface selection, typographic rhythm, lettering, wordmarks,
  logomarks, iconography (as graphic design objects — visual weight, optical
  size, set consistency, metaphor clarity), brand identity systems, layout and
  composition, grid systems, editorial design, poster design, print and digital
  collateral, motion graphics identity, color palette and palette application,
  visual system coherence, illustration style consistency, infographic clarity,
  packaging design, wayfinding and signage, cover art, advertising creative.
  Also trigger when evaluating any visual artifact primarily through the lens
  of graphic craft, visual communication, and aesthetic quality — not UX flow
  or interactive behavior. Sub-specialties: typography QA, iconography QA
  (graphic design lens), brand identity QA, editorial layout QA, illustration QA.
  Spoke of lead-visual-qa.
---

# Visual QA — Graphic Design

Graphic design quality assurance specialist. Evaluates visual artifacts through
the lens of graphic craft: composition, typography, color, brand language, and
visual communication effectiveness. Spoke of `lead-visual-qa`.

---

## Domain Boundary

This skill owns the **graphic design evaluation lens**.

- **Interactive behavior, flows, navigation** → `visual-qa-ux-design`
- **Screen components, spacing systems, platform conventions** → `visual-qa-ui-design`
- **Type legibility for users with impairments** → `visual-qa-accessibility`
- **3D render quality, game environments** → `visual-qa-game-design` or `visual-qa-architecture`

When an artifact involves typography in a UI context, apply *this* skill's type
knowledge alongside `visual-qa-ui-design`'s spacing and component framework.

---

## Typography QA

Typography is a sub-specialty of graphic design QA. Typography failures are
among the most common and most impactful visual quality issues.

### Type Hierarchy

A well-structured hierarchy creates an immediate reading path. Evaluate:

| Level | Descriptor | Common Issues |
|-------|-----------|---------------|
| **H1 / Display** | Primary visual statement | Too similar in weight to H2; competing with imagery; overscaled for context |
| **H2 / Section** | Wayfinding and chunking | Insufficient contrast from body; too frequent — dilutes meaning |
| **H3 / Subsection** | Internal structure | Visually indistinguishable from H2; treated as a stylistic flourish rather than structural element |
| **Body** | Content carrier | Insufficient leading; too long a measure (>75 chars/line); too small for reading distance |
| **Caption / Micro** | Supporting context | Too small to be legible at target size; incorrect color contrast ratio |
| **Label / Tag** | Utility text | Confused with body text due to insufficient weight/style differentiation |

### Typographic Rhythm

Rhythm is the vertical cadence of text and space. Evaluate:

- **Leading (line-height)**: Body text should use 1.4–1.6× type size. Tighter than 1.3× compresses and creates
  fatigue. Looser than 1.8× fragments cohesion.
- **Paragraph spacing**: Should be at minimum equal to the leading value (1 line gap). Insufficient paragraph
  breaks make text feel unbroken and overwhelming.
- **Heading-to-body ratio**: Spacing between a heading and its following body text should be ≤ the spacing
  between the body text and the *next* heading — this "binds" content to its section header.
- **Optical margin alignment**: Pull-quotes and drop-caps should hang punctuation outside the text column
  to preserve visual margin alignment.

### Kerning and Letter-Spacing

- **Kerning** (spacing between individual character pairs) is font-level by default; flag when specific
  pairs create visual "holes" or "collisions" at display sizes
- **Tracking** (uniform letter-spacing adjustment): Display/heading type often benefits from slight negative
  tracking (−10 to −20/1000em). All-caps settings require positive tracking (+50 to +100/1000em). Body text
  should never have tracking applied.
- **Word spacing**: Justified type can create "rivers" of white space — flag when rivers are visible
  more than 2–3 lines deep in a block

### Type Choice and Brand Alignment

- Does the typeface personality match the context? (Industrial vs. humanist vs. geometric vs. display)
- Is the typeface appropriate for the medium? (Web-safe, variable font support, print rendering)
- Are typeface pairings creating harmony or tension? (Two geometric sans-serifs of similar weight = mud; serif + sans-serif = classic contrast)
- Does the type choice match precedent set by the reference material?

### Iconography (Graphic Design Lens)

When iconography is being reviewed as a graphic design artifact (not a functional UI element):

**Visual Weight Consistency**
- All icons in a set should reduce to approximately equal visual mass at the same size
- Blur test: apply 4px Gaussian blur to the icon set at target size — each icon should resolve
  to a similar gray value. Outliers are weight imbalances.
- Solid fills read heavier than equivalent stroked outlines — compensate with larger counter space
  or lighter stroke weight

**Optical Size Correctness**
- Icons displayed smaller than designed require optical size compensation: wider strokes, simplified
  geometry, opened counters
- A 24px icon displayed at 16px without optical compensation will appear muddy and hard to read
- At any target size: can the icon's metaphor be identified without effort?

**Set Coherence**
- Consistent perspective: all icons use the same viewing angle (typically front-facing or slight isometric)
- Consistent dimensionality: all flat, all with implied depth, or all truly 3D — never mixed
- Consistent stroke language: stroke weight, cap style, corner radius, and join type should be
  uniform across the set
- Consistent detail density: icons representing "simple" concepts should not have more detail than
  icons representing "complex" ones

**Metaphor Clarity**
- Is the core metaphor immediately recognizable at the target display size?
- Is there any risk of misinterpretation (e.g., a "globe" that reads as a "circle")?
- Does the icon work without a label at the target size, or does it require one?

---

## Composition and Layout QA

### Visual Balance

| Balance Type | Description | Failure Pattern |
|--------------|-------------|-----------------|
| **Symmetric** | Equal visual weight on both sides of a central axis | Off-center focal element that doesn't compensate; color imbalance between halves |
| **Asymmetric** | Unequal elements that balance through visual weight | Too much weight in one corner with nothing to counterbalance; orphaned elements |
| **Radial** | Elements arranged around a center point | Center not optically placed; radial elements at inconsistent visual weight |
| **Mosaic** | Uniform density without clear focal point | No entry point for the eye; everything equally important = nothing important |

### Rule of Thirds and Golden Ratio

These are starting points, not rules. Evaluate whether the composition has:
- A clear **focal point** (primary) — where does the eye go first?
- A clear **secondary element** — where does it go next?
- A **resting zone** — negative space that allows the composition to breathe

If a composition has been built on a grid or ratio system, evaluate whether that
structure is serving the content or constraining it.

### Negative Space

- Negative space should be intentional, not incidental
- Crowded compositions (too little negative space) feel anxious and low-quality
- Too much negative space without visual anchoring feels unfinished
- The negative space around a logo or focal element contributes to its perceived quality

---

## Color QA (Graphic Design Lens)

### Palette Adherence

- Are only the approved palette colors used?
- Are tints/shades derived from the palette (percentage tints of brand colors) vs. arbitrary values?
- Are neutrals (grays, off-whites, blacks) taken from the brand neutral scale or mixed independently?

### Color Harmony

| Harmony Type | Description | Common Issue |
|--------------|-------------|--------------|
| **Complementary** | Opposite on color wheel | High vibration at full saturation — needs one dominant, one accent |
| **Analogous** | Adjacent on color wheel | Can feel muddy or monochrome if values are too similar |
| **Triadic** | Three equally spaced hues | Easy to feel busy — one should dominate at 70%+ |
| **Split-complementary** | Base + two adjacent to complement | More stable than pure complementary |
| **Monochromatic** | Single hue, varying value/saturation | Requires strong value contrast to avoid flatness |

### Color Semantics

- Does color usage align with intended semantics? (Red = danger/error, Green = success, not reversed)
- Is the same color used consistently for the same meaning across all artifacts?
- Are status colors distinct enough from brand colors to avoid confusion?

---

## Brand Identity QA

### Logo Usage

- Clear space violation: minimum clear space around logo respected?
- Color variant misuse: logo on background that doesn't meet contrast requirement?
- Proportion distortion: logo stretched or compressed?
- Unauthorized modification: elements added, removed, or repositioned?
- Minimum size: logo rendered below the minimum legible size?

### Brand Voice → Visual Expression

- Does the visual tone match the stated brand personality attributes?
- Is the visual treatment consistent with other brand touchpoints (or is this an outlier)?
- Does the imagery, illustration style, and color usage reinforce the brand values?

---

## QA Checklist — Graphic Design

**Typography:**
- [ ] Hierarchy is readable as a visual sequence (H1 → H2 → body → support)
- [ ] Leading is appropriate for body text (1.4–1.6×)
- [ ] No unintentional rivers in justified blocks
- [ ] Tracking is appropriate for weight and case
- [ ] Type-pairing creates harmony rather than visual noise
- [ ] Typeface personality matches the content's voice and medium

**Iconography:**
- [ ] Visual weight is consistent across the set at target size
- [ ] Each icon's metaphor is immediately readable without a label (at target size)
- [ ] Stroke language (weight, cap, join, radius) is uniform across the set
- [ ] Optical compensation applied for small display sizes
- [ ] Icons pass the blur test (equal gray value at 4px blur)

**Layout:**
- [ ] Composition has a clear entry point and reading path
- [ ] Visual balance is intentional (symmetric, asymmetric, or radial — not accidental)
- [ ] Negative space is deliberate and consistent
- [ ] Focal hierarchy is maintained (primary → secondary → tertiary)

**Color:**
- [ ] Only approved palette colors used
- [ ] Color harmony type is consistent and intentional
- [ ] Color semantics are correct and consistent
- [ ] No unintended visual vibration from adjacent complementary colors

**Brand:**
- [ ] Logo usage follows clear space and proportion rules
- [ ] Visual treatment matches brand personality
- [ ] All touchpoints being evaluated are internally consistent
