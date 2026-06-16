---
name: type-variable-text
description: >
  Variable font axes for text typefaces — wght, wdth, ital, slnt, opsz, GRAD
  custom axes and their correct application in design systems and CSS. Use this
  skill whenever the conversation involves: variable font axis decisions for
  text faces, the opsz (optical size) axis in UI typography, font-variation-settings
  in CSS, font-optical-sizing: auto, designing the opsz axis for a text typeface,
  GRAD (grade) axis for dark mode compensation, how many variable font masters
  are needed, variable font token architecture in a design system, whether to
  use a variable font vs. multiple static fonts, performance trade-offs, or any
  question about variable font technology applied to text typefaces. Spoke of
  `lead-type-designer`. For icon font variable axes (FILL, wght for icons,
  GRAD for icons, opsz for icon simplification), use `variable-icon-font-architect`.
aliases: [type-variable-text]
tier: spoke
domain: design
hub: lead-type-designer
prerequisites: [lead-type-designer]
spec_version: "2.0"
---

# Type Variable Fonts for Text

Specialist lens for variable font axes and their application in text typeface
design. Part of the `lead-type-designer` skill network.

---

## Domain Boundary

This skill covers **variable font axes for TEXT typefaces** — linguistic,
readability-driven fonts for body, heading, label, and caption contexts.

| This skill covers | `variable-icon-font-architect` covers |
|---|---|
| wght axis for body and display text | wght axis for icon stroke weight |
| opsz axis for text legibility at small type sizes | opsz axis for icon simplification |
| GRAD axis for text density in dark mode | GRAD axis for icon optical weight |
| ital/slnt for text italic variants | FILL axis for icon outlined/filled states |
| Variable font DS token architecture for type | Icon font variable font pipeline |

The underlying axis mechanics are the same — route to
`variable-icon-font-architect`/`math-interpolation-designspace` for the
formal interpolation mathematics.

---

## Standard Variable Axes for Text Type

### wght — Weight (Registered Axis)

**Tag**: `wght` | **Range**: 100–900 | **CSS**: `font-weight`

The weight axis provides continuous variation from Thin (100) to Black (900)
without loading multiple static font files.

**Design considerations**:
- Intermediate weights are interpolated from masters; typically 2–3 masters
  (Light, Regular, Bold or Thin, Regular, Black) plus optional Extralight and
  Extrabold if the design requires discontinuous curve geometry
- At very heavy weights, counters must be explicitly managed — the interpolation
  math alone cannot preserve legible counters in a Black without master-level
  counter design
- The weight axis is the most widely supported and the most valuable single axis
  for a text typeface

**DS token mapping**: `font-weight: 400` in CSS maps directly to the wght axis.
The DS does not need to expose wght as a separate variable — `font-weight` is
the standard API.

**CSS**:
```css
/* Standard API — prefer this */
.text { font-weight: 600; }

/* Low-level override (only needed for non-standard values) */
.text { font-variation-settings: 'wght' 625; }
```

---

### wdth — Width (Registered Axis)

**Tag**: `wdth` | **Range**: 50–200 (percentage of normal width) | **CSS**: `font-stretch`

Width variation from condensed to extended without loading multiple width variants.

**Text type uses**:
- Condensed variants for space-constrained contexts (narrow columns, sidebar labels,
  data-dense tables)
- Extended variants for large display type where horizontal spread aids legibility
- Responsive width: same font at wider width for wide viewports, narrower for mobile

**Design consideration**: Width variation requires proportional changes to letterforms,
not just horizontal scaling. Mechanical horizontal scaling distorts letterforms — a
genuine wdth axis requires redesigned letter proportions at each width extreme.

**DS token mapping**: `font-stretch` or `font-variation-settings: 'wdth' 85` for
condensed label styles.

---

### ital — Italic (Registered Axis)

**Tag**: `ital` | **Range**: 0 (roman) to 1 (italic) | **CSS**: `font-style: italic`

Controls the shift between roman and italic letterforms.

**Important distinction — ital vs. slnt**:
- **ital=1** activates **genuinely different letterforms** — the italic forms of
  'a', 'g', 'f' differ from the roman forms (single-story 'a', open-tail 'g', etc.)
- **slnt** (slant) applies a geometric slant to the roman letterforms without
  changing the letterforms themselves — producing an oblique, not a true italic

A true italic is a separate design tradition from the roman; a high-quality text
typeface has a true italic. An oblique is simply the roman slanted.

**When ital=0.5 is meaningful**: Some contemporary variable designs support
intermediate italic values — a "slanted roman" or a soft italic. This is rare
and should be used deliberately.

**CSS**:
```css
em, i { font-style: italic; }  /* Standard; maps to ital=1 */
```

---

### slnt — Slant (Registered Axis)

**Tag**: `slnt` | **Range**: −90 to +90 degrees | **CSS**: `font-style: oblique [angle]`

Geometric slant applied to the roman letterforms. Negative values = forward-leaning
(normal oblique direction for Latin).

**Text type uses**:
- When a font has no true italic design, slant provides oblique emphasis
- Variable slant allows fine-tuning of oblique angle for specific optical sizes or
  contexts
- Some contemporary designs use slant as a continuous design variable for expression

**CSS**:
```css
.oblique { font-style: oblique -12deg; }
/* or */
.oblique { font-variation-settings: 'slnt' -12; }
```

---

### opsz — Optical Size (Registered Axis)

**Tag**: `opsz` | **Range**: typically 6–144 | **CSS**: `font-optical-sizing: auto`

The optical size axis is the **most powerful axis for UI and editorial typography**.
It provides optical-size-specific masters within a single font file.

### What Optical Size Means

At small type sizes (8–12px), letterforms need:
- **Larger x-height** relative to cap height (lowercase letters need more visual mass to be legible)
- **Wider letterforms** (condensed proportions at tiny sizes are hard to distinguish)
- **Heavier hairlines** (thin strokes disappear at small sizes)
- **More open apertures** (partially closed counters blur shut at small sizes)
- **More generous spacing** (letters need breathing room at small sizes to avoid blurring together)

At large display sizes (40px+), letterforms can be:
- **More refined and elegant** (detailed forms are visible)
- **More tightly proportioned** (high-quality display spacing)
- **Lower contrast hairlines** if desired for refinement
- **More tightly spaced** (display spacing conventions)

The opsz axis transitions between these two design spaces continuously.

### opsz in UI Design Systems — Critical

The opsz axis is the answer to the problem: "Our heading font looks great at
64px but too heavy/clunky at 12px caption size."

```css
/* font-optical-sizing: auto — browser selects opsz based on font-size */
body {
  font-optical-sizing: auto;  /* Enable automatic optical sizing */
}

/* Manual override for specific size contexts */
.caption {
  font-size: 11px;
  font-variation-settings: 'opsz' 11;  /* Explicitly request the 11pt optical size master */
}

.hero-heading {
  font-size: 72px;
  font-variation-settings: 'opsz' 72;  /* Request the display-scale master */
}
```

**`font-optical-sizing: auto` behavior**: When set, the browser passes the
computed font-size as the opsz value. This is the correct default — the browser
knows the rendered size. Override only when you want a different optical size
than the rendered size (uncommon but valid for creative effects).

### opsz in Design System Token Architecture

A DS that uses a type scale (12px caption, 14px body, 16px body-lg, 20px subtitle,
24px heading, 32px heading-xl, 48px display) should:

1. Enable `font-optical-sizing: auto` globally
2. Verify that the chosen variable font actually has a meaningful opsz axis (not
   all variable fonts with an opsz range do meaningful optical work)
3. For each type scale token, optionally specify a manual opsz if the automatic
   value produces undesired results

Route to `ds-advisor` for token architecture decisions.

---

### GRAD — Grade (Custom Axis, Registered)

**Tag**: `GRAD` | **Range**: typically −200 to +200 | **CSS**: `font-variation-settings: 'GRAD' [value]`

Grade changes the visual weight of the type without changing the advance widths
(the space each glyph occupies). Unlike wght, a grade change does not cause text
reflow.

**Text type applications**:

**Dark mode**: On a dark background, the same font at the same size appears
heavier than on a light background. Light backgrounds have more "bleed" around
dark letters; dark backgrounds have less. The GRAD axis compensates:
- Light mode: `GRAD 0` (default)
- Dark mode: `GRAD -25` (slightly lighter grade to match visual weight of light mode)

**Display density**: GRAD can compensate for different display types (high-density
retina vs. standard 1x) that render the same font at different apparent weights.

```css
@media (prefers-color-scheme: dark) {
  :root {
    font-variation-settings: 'GRAD' -25;
  }
}
```

---

## Variable Font Masters for Text Type

### How Many Masters?

| Design goal | Masters needed |
|---|---|
| Weight range only (Thin–Black) | 2 masters (extremes); 3 if an interior master is needed for correct interpolation |
| Weight + optical size | 4 masters: (Regular weight, text opsz), (Regular weight, display opsz), (Bold, text opsz), (Bold, display opsz) — the designspace corners |
| Full wght × opsz grid | 4–6 masters depending on design discontinuities |
| Adding GRAD | GRAD can be derived from wght via delta math; may not need separate masters |
| Adding ital | Typically doubles the master count (all existing masters × roman + italic) |

**Master placement principle**: Masters should be placed at design extremes that
accurately represent the design intent, not at arbitrary axis boundaries. A Regular
weight is usually a better axis anchor than a theoretically correct "median."

Route to `variable-icon-font-architect`/`math-interpolation-designspace` for the
formal designspace optimization mathematics.

### Interpolation Compatibility for Text Type

Same rules as icon fonts — all masters must have:
- Identical glyph counts
- Identical node counts per glyph
- Identical path directions (CW/CCW)
- Identical start point indices

For text type, the challenge is often the transition between roman letter
constructions and italic letter constructions — 'a', 'g', 'f' have different
construction geometry in italic and roman. Solutions:
- Compatible construction approach: build both versions with the same node count
  but positioned to create the appropriate forms at each end
- Layer-based approach (Glyphs): separate italic layer with compatible geometry

---

## Performance Trade-offs

### Variable Font vs. Multiple Static Fonts

| Scenario | Recommendation |
|---|---|
| 1–2 weights needed | Static fonts may be smaller; variable font adds overhead for unused axes |
| 3+ weights needed | Variable font is typically smaller than 3+ separate WOFF2 files |
| opsz axis needed | Variable font essential; no other way to deliver optical-size-specific rendering |
| GRAD for dark mode | Variable font essential |
| Full typographic range (heading to caption) | Variable font essential for opsz; also covers weight in one file |

### Subsetting

Variable fonts should still be subsetted to used character ranges:
- Latin only: subset out CJK, Devanagari, Arabic if not used — large fonts contain these
- `pyftsubset` or online tools for subsetting WOFF2

---

## Anti-Patterns and Failure Modes

| Anti-pattern | Symptom | Fix |
|---|---|---|
| Using a variable font without opsz for mixed-size type scales | Caption and display sizes use the same optical construction; small sizes look clunky | Choose a font with meaningful opsz axis, or accept the limitation |
| `font-optical-sizing: none` on body | Browser doesn't apply automatic opsz; type loses its optical-size optimization | Remove the override; use `font-optical-sizing: auto` |
| GRAD for weight variation | Text reflows as text reflow occurs if using wght instead of GRAD | Use GRAD specifically when no-reflow weight compensation is required |
| Master count explosion | Variable font file enormous; compile times long | Minimize masters; derive grades from wght deltas; evaluate which axes genuinely need masters |
| `font-variation-settings` overrides `font-weight` | Named-instance weight values ignored; DS tokens break | Either use `font-weight` (maps to wght automatically) or use `font-variation-settings` for all variation — not both |
| No `font-optical-sizing: auto` in DS base styles | opsz not applied anywhere; investment in opsz axis wasted | Add to `:root` or `body` in the DS base stylesheet |

---

## Cross-Links

- `variable-icon-font-architect`/`math-interpolation-designspace` — interpolation physics, delta algebra, avar remapping, master placement optimization are the same for text and icon fonts
- `variable-icon-font-architect`/`fonttools-ufo-internals` — Python build pipeline for variable fonts
- `type-letterform-construction` — construction decisions propagate through the variable axis; text-size construction for the text opsz master vs. display construction for the display opsz master
- `type-spacing-metrics` — spacing must be coordinated across variable axes; opsz should include spacing adjustments
- `ds-advisor` — variable font axis token architecture: `font-weight` for wght, responsive opsz tokens, GRAD for dark mode; how to expose axes through the DS layer
- `lead-ui-designer`/`uid-type-for-screens` — opsz axis in responsive UI typography; GRAD for dark mode type density compensation; `font-optical-sizing: auto` as a base stylesheet requirement
