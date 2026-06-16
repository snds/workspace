---
name: type-spacing-metrics
description: >
  Sidebearings, kerning, tracking, leading, and the vertical metrics system for
  text typefaces. Use this skill whenever the conversation involves: spacing a
  typeface, sidebearing values and logic, kerning pairs and kerning groups,
  the spacing string test, letter-spacing tokens for a design system, leading
  (line-height) relationships, tracking at different sizes, UPM and vertical
  metrics (x-height, cap height, ascender, descender), aligning multiple fonts
  on a common baseline, optical spacing overrides, or any question about the
  spatial layer of typography. Spoke of `lead-type-designer`. For icon font
  advance widths and padding, use `variable-icon-font-architect`.
aliases: [type-spacing-metrics]
tier: spoke
domain: design
hub: lead-type-designer
prerequisites: [lead-type-designer]
spec_version: "2.0"
---

# Type Spacing and Metrics

Specialist lens for the spacing system of text typefaces — sidebearings, kerning,
tracking, leading, and vertical metrics. Part of the `lead-type-designer` network.

---

## Domain Boundary

This skill owns **the spatial layer of text typography** — the blank space that
makes letterforms readable as words, lines, and blocks of text.

- **Letterform construction** → `type-letterform-construction`
- **Icon font advance widths** → `variable-icon-font-architect`
- **Design system token values** → `ds-advisor` (this skill provides the knowledge; ds-advisor handles the token architecture)
- **Screen-specific spacing decisions** → `lead-ui-designer`/`uid-type-for-screens`
- **Classical typographic principles** → `lead-graphic-designer`/`gd-typography`

---

## Sidebearings — The Foundation

### What Sidebearings Are

Every glyph has a left sidebearing (LSB) and right sidebearing (RSB) — the
blank space between the glyph's bounding box and its advance width boundary.
Sidebearings are not padding; they are **as much a part of the design as the
letterform itself**. Consistent sidebearings create even typographic texture.

### Sidebearing Logic by Letter Shape

| Letter group | LSB/RSB logic |
|---|---|
| Vertical stems (H, I, N, n, h) | Equal left and right; these are the reference spacing letters |
| Round forms (O, C, o, c) | Slightly less sidebearing than vertical stems of the same weight; the curvature provides optical space |
| Diagonal forms (A, V, W, v, w) | Asymmetric; the side with the acute angle has less sidebearing |
| Mixed (b, d, p, q) | One vertical side, one round side; apply vertical logic on straight side, round logic on curved side |
| Wide letters (M, W, m) | May need slightly wider sidebearings due to visual mass |
| Narrow letters (I, l, i) | May need slightly narrower sidebearings; too wide creates isolation |

### The Spacing String Test

The canonical test for normalizing spacing across all glyphs:

```
HHxHH HxH HxH
nnonn non
```

Replace 'x' with each letter being tested. In the H/H context, 'x' must look as
if it belongs in the rhythm of H's without disrupting the even texture. The 'n'
context does the same for lowercase. If 'x' looks too tight or too loose relative
to HH, adjust its sidebearings.

**Why H and n**: H has the simplest spacing (two vertical stems with equal
sidebearings) and n is its lowercase equivalent. Using them as the reference
frame reveals any spacing irregularity.

### Spacing Across the Weight Range

Heavier weights need **proportionally** tighter sidebearings:
- Light weights have more sidebearing relative to stroke weight
- Bold weights have less sidebearing relative to stroke weight
- The spacing must change across the weight axis — mechanically interpolating
  sidebearings from light to bold often requires manual refinement at intermediate
  weights

---

## Kerning

### When to Kern

Kerning corrects spacing between specific letter pairs that sidebearings alone
cannot fix. It is needed when:

- Diagonal + vertical combinations create large optical gaps (AV, AT, VA, WA)
- Overhanging letters create collisions (T followed by a, e, o, etc.)
- Certain pairs create trapped white space that breaks text rhythm

### Classic Kerning Pairs

**Negative kerning required (pairs that need moving closer)**:
- AV, AW, AT, AC, AG, AO, AQ
- VA, WA, TA
- Te, To, Ta, Ti, Tr, Ts, Tu, Ty
- LT, LV, LW, LY
- Fa, Fe, Fi, Fo, Fr, Fu
- PA, pu, pi, py, ph, pe
- Quotation marks + any capital (opening quote before H, T, A, etc.)

**Positive kerning required (pairs that need moving apart)**:
- rn (can read as m) — add space between r and n in text faces
- fi (before ligature is available) — prevent f descender colliding with i dot

### Kerning Groups

Instead of kerning every pair individually (which would require thousands of
pairs for a complete Latin character set), assign letters to groups based on
their **side shapes**:

| Group type | Members |
|---|---|
| Left-round | b, d, p, q, þ, ð |
| Left-diagonal | A, V, W, Á, À, Â, Ã, Ä, Å |
| Right-round | a, c, d, e, g, o, q, œ, ø |
| Right-diagonal | v, w, x, y |
| Left-vertical (capitals) | H, I, K, L, M, N, R, U |

Kerning one pair in a group applies to all members: kern AV, and AW, ÁV, ÀW,
etc. are all handled. Well-designed kerning groups reduce thousands of pairs to
hundreds.

### Metric Kerning vs. Optical Kerning

- **Metric kerning**: Uses the font's built-in kerning pairs (kern table or GPOS)
- **Optical kerning**: Application-level algorithm that ignores the font's kerning
  and applies spacing based on glyph shapes — useful as a fallback when metric
  kerning is absent or poor; less reliable for specialized or display type

**Best practice**: Ship the font with thorough metric kerning. Rely on optical
kerning only as a degraded fallback.

---

## Tracking (Letter-Spacing)

Tracking is a typographic adjustment applied at the text block or style level —
not a property of the font itself (unlike sidebearings and kerning).

### Size-Based Tracking Principles

| Type size | Tracking guidance | Rationale |
|---|---|---|
| Display (40px+) | Tight: −0.02em to −0.05em | Creates cohesion; text set for display often has sidebearings designed for text size |
| Heading (24–40px) | Slight negative to zero: −0.01em to 0 | Context-dependent |
| Body text (14–20px) | Zero or near-zero: 0 to +0.01em | Default sidebearings are designed for this range |
| Caption/label (10–13px) | Slightly wide: 0 to +0.02em | Restores legibility lost at small sizes |
| All-caps labels | Wide: +0.05em to +0.12em | Critical — uppercase strings read as tight even with correct sidebearings; the absence of ascenders and descenders requires added inter-letter space |
| Small caps | Wide: +0.03em to +0.08em | Similar to all-caps; small caps need more tracking than lowercase |

### The All-Caps Tracking Rule

Uppercase-only text **always** needs positive tracking. The reason: lowercase
letterforms have ascenders and descenders that create spacing variety and rhythm;
uppercase letterforms are all the same height, which makes the word space appear
compressed. This is not an aesthetic choice — it is a legibility correction.

**Anti-pattern**: Uppercase UI labels (navigation, buttons, tags) without added
tracking. The text reads as compressed and is harder to parse quickly.

---

## Leading (Line-Height)

Leading determines the vertical rhythm of a text block. Correct leading makes text
scannable and comfortable to read; incorrect leading makes it dense or fragmented.

### Leading Relationships

| Context | Leading guidance |
|---|---|
| Body text | 1.4–1.6× type size; shorter measure (line length) needs less leading |
| Long-form editorial | 1.5–1.7× for generous reading comfort |
| Tight display | 1.0–1.2× for coherent headline blocks |
| Single-line labels/captions | 1.2–1.4× minimum for visual breathing room |
| Code/monospace | 1.5–1.7× for character differentiation |

### The Measure Relationship

**Leading and measure (line length) must be calibrated together.**
- Longer measure → needs more leading (the eye must travel farther to find the next line)
- Shorter measure → can use tighter leading
- Rule of thumb: optimal measure for body text is 55–75 characters per line
- Below 45 characters: single column may not need generous leading
- Above 80 characters: increase leading to help the eye return to the left margin

### Leading as Design Token

In CSS and design systems, leading maps to `line-height`. This property should
be expressed as a **unitless multiplier** (e.g., `1.5`, not `24px`) so that it
scales correctly when type size changes. Route to `ds-advisor` for token
architecture decisions.

---

## Vertical Metrics System

### UPM (Units Per Em)

The coordinate space of the font. All values (sidebearings, kerning, ascender,
descender) are expressed in UPM units.

- Common UPM values: 1000 (PostScript/OpenType tradition), 2048 (TrueType tradition)
- Higher UPM = more granularity for fine spacing values
- Within a type family, all fonts must use the same UPM

### Key Vertical Metrics

| Metric | Definition | Typical value (1000 UPM) |
|---|---|---|
| Baseline | Zero line — all other metrics relative to this | 0 |
| x-height | Top of lowercase x | 480–540u (text), 530–560u (screen-optimized) |
| Cap height | Top of uppercase H | 660–720u |
| Ascender | Highest extent of b, d, f, h, k, l | 700–760u |
| Descender | Lowest extent of g, j, p, q, y | −200 to −240u |
| OS/2 metrics | Values in the OS/2 table controlling line box | Set to match or exceed actual extents |

### Multi-Font Alignment

When two fonts are used at the same size in a line (e.g., a sans-serif body font
and a monospace code font), their baselines align but their visual metrics
(x-height, cap height) may differ dramatically. This creates optically mismatched
type even at the same point size. Solutions:

- Size adjustment: scale the secondary font slightly (up or down) to match x-heights
- Metric alignment: when designing a companion family, align x-heights intentionally
- Token guidance: document the size relationship in the DS (`font-size-code: 0.9em` relative to body)

---

## Anti-Patterns and Failure Modes

| Anti-pattern | Symptom | Fix |
|---|---|---|
| Equal sidebearings on all letters | Rounds look too loose, diagonals create optical gaps | Apply the spacing logic by letter group |
| No kerning pairs | AV, AT, LY, Te create obvious gaps | Add kerning groups and the classic pairs |
| Zero tracking on all-caps UI labels | Button text reads as compressed and hard to parse | Add +0.05em to +0.10em tracking on uppercase labels |
| Tracking applied at text size without size scaling | Body text looks spread out; labels look cramped | Set tracking values per size context, not globally |
| Fixed-unit leading (e.g., 24px) | Leading breaks when type size changes | Use unitless line-height multipliers |
| Optical kerning as primary kerning | Inconsistent results in display, script, and specialty type | Build metric kerning; use optical only as fallback |
| Mismatched vertical metrics in companion fonts | Code font appears too large or too small next to body | Calibrate companion font size relative to x-height |

---

## Cross-Links

- `type-letterform-construction` — sidebearings and letterform construction are deeply interdependent; spacing follows from form, but form decisions must anticipate spacing needs
- `type-opentype-text` — kerning is implemented via GPOS table; tabular figures (tnum) are a spacing-driven feature that prevents column misalignment
- `type-variable-text` — spacing must be coordinated across the variable weight axis; opsz axis should include spacing adjustments (larger optical sizes need tighter spacing)
- `ds-advisor` — letter-spacing and line-height as design tokens; the mathematical relationship between type size and optimal leading is the basis for line-height tokens; documenting tracking values per size tier
- `lead-graphic-designer`/`gd-typography` — classical typographic spacing principles
- `lead-ui-designer`/`uid-type-for-screens` — screen-specific spacing decisions; when to override letter-spacing tokens
- `lead-ux-designer`/`ux-interaction-design` — optical spacing informs form layout; label-to-field relationships; list item spacing as readability and interaction decisions
- `lead-accessibility-architect`/`a11y-cognitive` — generous letter-spacing and line-height benefit users with dyslexia and reading disabilities

## Related
- hub → [[lead-type-designer]]
