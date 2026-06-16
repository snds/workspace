---
name: lead-type-designer
description: >
  Staff/Principal IC type designer for text typefaces. Hub skill for a network
  of 7 specialist spokes covering letterform construction, spacing and metrics,
  OpenType features for text, type classification and history, multi-script type
  design, professional typesetting, and variable font axes for text faces. Use
  this skill whenever the conversation touches: text typeface design, glyph
  construction for readability, sidebearings, kerning, spacing systems, OpenType
  text features (liga, tnum, lnum, smcp, opsz), variable font weight and optical
  size axes for text, serif or sans-serif type design, type classification
  systems (Vox-ATypI, Humanist/Garalde/Transitional/Didone), type history and
  cultural context, multilingual type design (Arabic, Devanagari, CJK, Hebrew),
  professional typesetting in InDesign or CSS, rag control, baseline grids,
  widows and orphans, micro-typography, headline type, body type, display type,
  type metrics (UPM, x-height, cap height, ascender, descender), or any
  question about making type for reading. Also trigger on: "letterform",
  "typography", "typesetting", "kerning", "tracking", "leading",
  "sidebearings", "type specimen", "type scale", "type system".
  DOMAIN BOUNDARY: This hub handles TEXT typeface design — linguistic,
  readability-driven, classical tradition. For ICON FONT work (pictographic
  glyphs, FILL axis, FontTools icon pipeline), use the `variable-icon-font-architect`
  spoke (which is part of this hub's network). Also trigger on "icon font",
  "variable axes for icons", "FILL axis", "icon interpolation".
aliases: [lead-type-designer]
tier: hub
domain: design
prerequisites: [design-foundations]
spec_version: "2.0"
---

# Lead Type Designer

**Hub skill** for the text typeface design skill network. Routes to 7 specialist
spoke skills based on topic. This hub provides foundational principles and
routing logic; spokes provide deep domain knowledge when needed.

---

## Domain Boundary

| This hub's spokes cover | `variable-icon-font-architect` spoke covers |
|---|---|
| Text typeface design | Icon font construction |
| Glyph construction for linguistic readability | Pictographic glyph design |
| Text weight axes (wght for body/display text) | FILL axis, GRAD axis for icons |
| opsz for text legibility at small type sizes | opsz for icon simplification |
| OpenType features for text (liga, tnum, smcp) | GSUB for icon ligature substitution |
| Classical letterform construction | Skeleton-and-meat icon strategy |
| Professional typesetting | Icon grid and keyline systems |
| Multi-script text type (Arabic, Devanagari, CJK) | Icon font build pipeline |

**`variable-icon-font-architect` is a spoke within this hub's network.** It is
itself a sub-hub with its own 10-spoke network covering icon design, vector
construction, pipeline engineering, and applied mathematics. When icon font
work is the topic, load `variable-icon-font-architect` from this hub — it
will route further into its own spokes.

The two domains share underlying mathematics (bezier construction, variable
font interpolation physics, OpenType table mechanics) but serve entirely
different design traditions. General variable font axis mathematics lives
in `variable-icon-font-architect`'s `math-interpolation-designspace` and
`math-bezier-spline-theory` spokes — those spokes serve both traditions.

---

## Spoke Network — Load On-Demand

This hub routes to 8 spoke skills (7 text-type spokes + 1 icon-font sub-hub).
**Do not load all spokes eagerly.** Load only the 1–2 spokes relevant to the
current question. The hub itself contains enough context to triage and route.

### Spoke Manifest

| Skill | Domain | Trigger When |
|-------|--------|-------------|
| `type-letterform-construction` | Bezier craft for text glyphs, optical corrections, overshoot, counter design, weight relationships across a type family | Drawing glyphs, evaluating letterform quality, stem weight decisions, node economy, overshoot values, construction of specific letters |
| `type-spacing-metrics` | Sidebearings, kerning, tracking, line-height, UPM and vertical metrics | Spacing a typeface, kerning pairs and groups, letter-spacing tokens, leading relationships, metrics alignment across a family |
| `type-opentype-text` | OpenType features for text: liga, tnum, lnum, smcp, onum, frac, opsz-linked features | Specifying OpenType features in a DS text style, enabling tnum for data, small caps implementation, ligature behavior in CSS |
| `type-classification-history` | Vox-ATypI classification, historical movements, type anatomy vocabulary, typeface pairing, selection criteria | Choosing a typeface for a project, pairing typefaces, understanding what a typeface communicates culturally, anatomy vocabulary |
| `type-multi-script` | Arabic, Hebrew, Devanagari, CJK, multilingual family design, script-specific construction | Designing or selecting type for non-Latin scripts, multilingual product typography, right-to-left layout, conjunct forms |
| `type-typesetting` | InDesign professional typesetting, CSS typesetting, rag control, baseline grid, widows/orphans, hierarchical typesetting | Setting body text professionally, InDesign paragraph composer, rag control, optical margin alignment, web typesetting CSS |
| `type-variable-text` | Variable font axes for text: wght, wdth, ital, slnt, opsz, GRAD; CSS implementation; DS token integration | Variable font axis decisions for text faces, opsz in UI contexts, font-variation-settings, DS variable font token architecture |
| `variable-icon-font-architect` | **Sub-hub** — icon font construction, FILL/wght/GRAD/opsz for pictographic glyphs, interpolation-safe geometry, FontTools pipeline, CentricSymbols; routes into its own 10-spoke network | Icon fonts, FILL axis, pictographic glyph design, icon interpolation, exploding glyphs, icon font pipeline, skeleton-and-meat strategy |

### Spoke Loading Protocol

**Step 1**: Match the question to the Spoke Manifest. Identify 1–2 directly
relevant spokes. Rarely 3.

Common routing patterns:

- **Drawing or evaluating a specific letterform**: `type-letterform-construction`
- **Spacing or kerning a typeface**: `type-spacing-metrics`
- **OpenType features in a design system**: `type-opentype-text` + `type-spacing-metrics`
- **Choosing or pairing typefaces**: `type-classification-history`
- **Multilingual or non-Latin type**: `type-multi-script`
- **Setting body text or layout**: `type-typesetting`
- **Variable font axes for text**: `type-variable-text`
- **Building a text type DS token system**: `type-spacing-metrics` + `type-opentype-text` + `type-variable-text`
- **Type history, semantics, cultural register**: `type-classification-history`
- **Screen rendering of text type**: `type-letterform-construction` + `type-variable-text` (opsz)
- **Icon fonts / FILL axis / icon pipeline / pictographic glyphs**: `variable-icon-font-architect`

**Step 2**: Load the identified spoke(s) from:
```
[workspace root]/02-skills/[skill-name]/SKILL.md
```

For `variable-icon-font-architect`: after loading its SKILL.md, follow its
own Spoke Manifest to load 1–2 of its 10 specialist spokes for the specific
sub-topic (icon design, vector construction, math, pipeline, etc.).

**Step 3**: If the conversation shifts domain mid-session, load the newly
relevant spoke then — not preemptively.

**Never load all spokes at once.** The full network (this hub + sub-hub) is
~120k+ tokens; a typical question needs 1–2 spokes.

---

## Core Principles

### Type design is the design of reading

Every decision — letterform construction, spacing, OpenType features, optical
sizing — exists in service of two goals:

- **Legibility**: Can this text be decoded? (recognition of individual letterforms)
- **Readability**: Can this text be read for extended periods without fatigue?

Display type prioritizes legibility at large sizes. Body text prioritizes
readability over sustained reading durations. Caption and label type must
optimize for legibility at the smallest sizes it will encounter. These
constraints are different and produce different design decisions.

### Every letterform decision is an optical decision

Mathematical regularity produces optical irregularity. Corrections must be
built in:

- Horizontal strokes appear heavier than vertical strokes of identical weight — horizontals must be thinned
- Round and pointed forms must overshoot the cap line and baseline to appear flush with flat-top forms
- Optically centered elements sit slightly above the mathematical center
- Even-width bars in letterforms like E and H appear uneven — the middle bar is optically centered above the mathematical midpoint

The geometry must be drawn wrong to look right. This is not a bug — it is
the craft.

### Text type and display type have different constraints

**Text type (6–16pt / 8–20px)**: Robust forms survive anti-aliasing and
screen rendering. Generous x-height. Open counters. Moderate contrast.
Reliable spacing. OpenType features for text (tnum, onum, liga).

**Display type (24pt+ / 32px+)**: Refined forms, delicate hairlines, tighter
spacing. High contrast. The subtlety that text sizes would lose is visible
and expected at large sizes.

**Variable font opsz axis** bridges these: a single typeface can serve both
by providing optical-size-specific masters. Route to `type-variable-text` for
opsz implementation details.

### Spacing is as important as form

The best-drawn letterform in a poorly-spaced font fails. Spacing determines
whether type reads as an even gray texture (correct) or as scattered dark and
light patches (incorrect). Sidebearings and kerning are design work, not
technical afterthought. Route to `type-spacing-metrics` for the full spacing
system.

### Type history is type grammar

Understanding the classification and historical context of a typeface is
understanding how and when to use it. A typeface carries its historical
register — Garamond reads as humanist, rational, literary; Helvetica reads
as universal, neutral, institutional; Bodoni reads as elegance, precision,
fashion. Using a typeface without understanding its register is designing
without vocabulary. Route to `type-classification-history` for this knowledge.

---

## Cross-Hub References

### `lead-type-designer` ↔ `variable-icon-font-architect` (sub-hub spoke)

`variable-icon-font-architect` is a spoke within this hub — and itself a
sub-hub with 10 specialist spokes. Text type and icon fonts share underlying
tools (Glyphs, FontTools, Python pipelines, bezier construction) but serve
entirely different design traditions.

- **Shared mathematics**: bezier construction craft, variable font interpolation
  physics, axis mechanics — these live in `variable-icon-font-architect`'s
  `math-interpolation-designspace` and `math-bezier-spline-theory` spokes and
  apply to both text type and icon fonts
- **Text-type-specific**: letterform rationale (readability, spacing, optical
  corrections for reading), spacing systems, OpenType text features, type
  classification — these live in this hub's 7 spokes
- **Icon-font-specific**: FILL axis behavior, pictographic glyph design, icon
  grid/keyline systems, skeleton-and-meat strategy, FontTools icon pipeline,
  GSUB ligature substitution for icons — these stay in `variable-icon-font-architect`
- Routing: icon font work → load `variable-icon-font-architect` from this hub

### `lead-type-designer` → `lead-graphic-designer`

Type design is the making of the tools that graphic design uses.

- `gd-typography` is downstream context — classical typographic principles
  inform how the fonts this hub produces will be used
- `gd-grid-and-layout` provides the grid that typesetting sits within
- `gd-visual-communication` — visual perception principles directly affect
  construction decisions in `type-letterform-construction`

### `lead-type-designer` → `ds-advisor` (significant)

The design system is where text type knowledge operationalizes:

- `type-spacing-metrics` → token values for `line-height`, `letter-spacing`
- `type-opentype-text` → OpenType features baked into text style tokens (tnum lnum for numeric styles)
- `type-variable-text` → variable font axis tokens (wght, opsz) across the DS
- `type-letterform-construction` → type scale decisions; optical size steps should
  reflect real perceptual differences, not arbitrary multipliers
- `type-typesetting` → the typographic system (scale + leading + tracking + measure)
  designed as a coordinated set, not independent tokens

### `lead-type-designer` → `lead-ui-designer` (significant)

- `type-letterform-construction` → font selection for screen: understanding
  construction predicts which faces render well at screen densities
- `type-spacing-metrics` → overriding letter-spacing tokens, predicting optical
  alignment in mixed-size settings
- `type-opentype-text` → enabling tnum/disambiguation variants in dense UI data contexts
- `type-variable-text` → opsz axis in responsive UI typography; GRAD axis for dark
  mode type density compensation

### `lead-type-designer` → `lead-ux-designer` (significant)

- `type-typesetting` → typographic hierarchy IS the visual expression of IA hierarchy
- `type-spacing-metrics` → optical spacing informs form layout (label-to-field
  relationships, list item spacing)
- `type-opentype-text` → tnum/disambiguation variants as functional accessibility decisions
- `type-classification-history` → type semantics inform communication register in
  research artifacts and stakeholder materials

### `lead-type-designer` → `lead-accessibility-architect`

- `type-opentype-text` → disambiguation variants (0/O/l/I/1 clarity) as accessibility
  decisions for low-vision and cognitive processing differences
- `type-spacing-metrics` → letter-spacing and line-height as cognitive accessibility
  considerations (dyslexia, reading disabilities benefit from wider tracking and generous leading)

---

## Design-Forward Operating Directive

This skill network operates at the intersection of craft, history, and systems
thinking. Technical precision — bezier construction, OpenType table correctness,
variable font compatibility — is necessary but insufficient.

The test of any type decision is reading. Set a paragraph at the intended size
and rendering context. Read it. Read it again. The eye is the final validator.

Every spoke in this network maintains this standard: mathematical and technical
rigor in service of the reading experience. Not the reverse.

---

## References

- Hochuli, Jost. *Detail in Typography* — foundational text on micro-typography and spacing
- Bringhurst, Robert. *The Elements of Typographic Style* — the canonical reference for typographic practice
- Cheng, Karen. *Designing Type* — letterform construction analysis
- Unger, Gerard. *Theory of Type Design* — design rationale and optical principles
- Vox-ATypI classification system
- OpenType specification (Microsoft/Adobe)
- Google Fonts Knowledge — practical design principles (fonts.google.com/knowledge)
- Variable fonts specification (OpenType 1.8+)

## Related
- foundation → [[design-foundations]]
