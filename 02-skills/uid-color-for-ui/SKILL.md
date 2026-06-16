---
name: uid-color-for-ui
description: >
  Color design decisions for digital UI — palette construction, semantic roles,
  dark mode design, colorblind-safe systems, perceptual uniformity, and color
  judgment in context. Use this skill whenever the conversation touches: UI color
  palette design, color for dark mode, OKLCH in UI, building a semantic color
  system, colorblind-safe palettes, color contrast in UI contexts, simultaneous
  contrast effects on UI elements, evaluating color decisions in a product,
  neutral color design for surfaces, or "does this color choice work?" This spoke
  owns the design decisions. Token architecture that encodes these decisions lives
  in ds-advisor. Part of the lead-ui-designer hub skill network.
---

# UID: Color for UI

Specialist spoke for color design in digital interfaces — the decisions, not
the token encoding. Part of the `lead-ui-designer` hub skill network.

---

## Domain Boundary

This spoke owns **color as design**: what colors to use, why, in what roles,
and how they behave in context. The downstream encoding of those decisions into
a token architecture belongs to `ds-advisor`.

**The design decision**: "This product's interactive color is a desaturated blue
at L=55 in OKLCH, which provides sufficient contrast on all surface levels in
both light and dark modes."

**The token encoding**: "That value becomes `--color-interactive-default: oklch(55% 0.12 245);`
under a semantic layer `color.interactive.default`." → `ds-advisor`

Both are needed. This spoke handles the first half.

---

## Color Roles in UI

Every color in a UI palette has a role. Undocumented color = uncontrolled color.
These four roles cover the full palette:

### Brand Color
- **Purpose**: Identity and recognition. This is what users associate with the product.
- **Usage**: Sparingly. Brand color as the primary interactive color is common but
  not mandatory. Brand color as a background color is rarely appropriate in enterprise.
- **Failure mode**: Using brand color everywhere because it's "on brand" — which
  dilutes its ability to draw attention when it actually matters.

### Semantic Color
- **Purpose**: Status communication. Success/warning/error/info. These have
  conventional meaning users have learned across products.
- **Usage**: Only for actual status. Do not use success green as a decorative
  accent. Do not use warning yellow for visual interest.
- **Failure mode**: Decorative use of semantic colors. When a user sees green,
  they expect success — decorative green breaks that signal.

### Neutral Color
- **Purpose**: Surfaces, text, borders, dividers. The majority of visual real
  estate in any enterprise UI is neutral.
- **Usage**: Multiple steps needed — base surface, elevated surface, card
  surface, border, secondary text, muted text, disabled. A neutral palette
  with fewer than 6–8 steps is usually too coarse.
- **Failure mode**: Purely gray neutrals with zero chroma. Achromatic grays
  look cold and lifeless on screens. Slightly chromatic neutrals (0.005–0.015
  chroma in OKLCH) feel more natural. The chroma can be warm (yellow), cool
  (blue), or brand-tinted.

### Accent / Interactive Color
- **Purpose**: Interactive elements (links, buttons, focus rings, checkboxes),
  focal points, and emphasis. The color that means "you can do something here."
- **Usage**: Consistent and disciplined. One interactive color per product
  (or a small family of 2–3 for different interaction types). More than that
  and users lose the signal.
- **Failure mode**: Multiple competing accent colors that each "compete" for
  attention, none of which is clearly "the interactive color."

---

## Building a UI Palette in OKLCH

OKLCH is the right color space for UI palette construction. Reasons:

- **Perceptually uniform lightness (L)**: Equal L-steps produce equal perceived
  brightness changes. This means a 10-step scale from L=10 to L=95 will have
  visually even steps — unlike HSL/HEX where the middle range compresses.
- **Predictable contrast behavior**: You can predict which color combinations
  will meet APCA/WCAG contrast thresholds before measuring them, because
  lightness is the primary contrast dimension and L in OKLCH is perceptually
  uniform.
- **Chroma (C) and hue (H) are independent of lightness**: You can lighten a
  color without shifting its hue (unlike HSL, where lightening often desaturates
  and shifts hue).
- **Works in both light and dark modes**: The same hue can be lightened or
  darkened with predictable results, making it practical to design a single
  palette that covers both modes.

### Construction Process

1. **Start with the main hue**: Choose the H value for your primary/interactive color.
2. **Set the chroma budget**: How saturated should this product feel? Enterprise:
   typically C=0.10–0.18 for interactive colors. Consumer: can go higher (C=0.20+).
3. **Build the scale**: 10–12 L steps from ~L=15 (darkest, dark mode interactive
   text) to ~L=95 (lightest, used for tinted backgrounds).
4. **Define semantic stops**: Which scale step is the default background, which
   is the interactive default, which is the hover, which is the text on a colored
   button?
5. **Build the neutral family**: Neutral hue should be slightly related to the
   primary hue or brand — pure achromatic (H irrelevant, C=0) is often too cold.
   Use C=0.005–0.012 for subtle warmth or coolness.
6. **Build semantic colors**: Success (green-ish hue), warning (yellow-orange),
   error (red), info (blue) — each at consistent chroma relative to the brand
   palette so they feel related.

### OKLCH Values for Common UI Roles (Enterprise SaaS Reference)

```
// Interactive / Brand (adjust H to your brand hue)
--color-interactive-default:  oklch(52% 0.14 245)   /* buttons, links */
--color-interactive-hover:    oklch(46% 0.14 245)   /* -6 L on hover */
--color-interactive-subtle:   oklch(94% 0.04 245)   /* tinted backgrounds */
--color-interactive-on-dark:  oklch(68% 0.12 245)   /* same hue, lighter, for dark mode interactive */

// Surfaces (light mode)
--color-surface-base:         oklch(98% 0.005 245)  /* app background */
--color-surface-raised:       oklch(100% 0 0)       /* cards, panels */
--color-surface-overlay:      oklch(96% 0.008 245)  /* hovered rows, selected states */

// Surfaces (dark mode)
--color-surface-base-dark:    oklch(16% 0.008 245)  /* NOT pure black */
--color-surface-raised-dark:  oklch(20% 0.010 245)  /* slight L increase = elevation */
--color-surface-overlay-dark: oklch(24% 0.012 245)  /* modal, elevated surface */
```

These are reference values — actual values depend on brand hue and contrast
requirements. Measure APCA on all text/surface combinations before finalizing.

---

## Light vs. Dark Mode Palette Design

### The Core Mistake: Inversion

Dark mode is not `#FFFFFF → #000000`. Inverting a light palette produces:
- Pure black backgrounds that look harsh and unnatural
- Colors that no longer have the right perceived weight in context
- Shadow-based elevation that becomes invisible or garish
- Status colors that may no longer meet contrast requirements

### Dark Mode Surface Design

Dark mode surfaces should use **near-black with subtle chroma**, not pure black:
- `#000000` (oklch 0%) → looks unnatural, high contrast is harsh
- `#111113` (oklch ~10%, slight blue-cool) → standard dark surface
- `#1A1A1F` (oklch ~16%, very slight blue tint) → warm-cool neutral, the
  most naturalistic dark surface on typical warm-white screens
- `#1C1916` (oklch ~16%, warm yellow tint) → warm dark surface, good for
  products with warm brand colors

The chroma is subtle (C=0.005–0.015) but perceptible. Its effect is that the
surface reads as a designed neutral rather than a defaulted black.

### Dark Mode Elevation

In dark mode, elevation is expressed through **surface lightness increase**, not
shadow deepening:
- Base surface: L=16%
- Cards / raised surfaces: L=20–21%
- Overlays / hovered containers: L=23–25%
- Modals / sidesheets: L=26–28%
- Popovers / dropdowns: L=30–32%

Each level is ~+4-5 L in OKLCH. This is the pattern Material Design 3 uses
formally (they call it "surface container" levels). See `uid-surface-depth` for
the full elevation system.

### Dark Mode Color Adaptation

Colors designed for light mode need adaptation, not just use:
- Interactive colors often need to be lightened (higher L) in dark mode to
  maintain contrast against dark surfaces. A blue that reads well on white
  at L=52% may need to be L=65–70% on a dark background.
- Semantic colors (success, warning, error) need similar adaptation.
- Do NOT simply increase brightness in HSL — use OKLCH L adjustment to
  maintain hue and chroma relationships.

### Dark Mode Contrast Check

Re-run all text/surface contrast checks in dark mode. Do not assume that passing
light mode guarantees dark mode passes. Common failures:
- Muted text that barely passed in light mode fails in dark mode
- Success green that was readable on white is too dark on a dark card
- Disabled state colors that disappear entirely

---

## Color in Enterprise Data-Dense UIs

### The Signal Problem

In a dense UI with many elements, color competes for attention. Every colored
element is saying "look at me." If 40% of cells in a data table are colored,
none of them are signals anymore — they're wallpaper.

**Rule**: In enterprise data views, color should appear only where it carries
semantic meaning (status, alert, categorical encoding). Decorative color in
data-dense UIs degrades the signal-to-noise ratio.

### Categorical Color Encoding

When color encodes categorical data (e.g., product lines, departments, status
types), the palette needs:
- **Perceptual distinctiveness**: Colors must be visually distinguishable from
  each other, not just numerically different
- **Consistent perceived weight**: All category colors should feel like equal
  "loudness" — no one category should visually dominate
- **8 categories maximum**: Beyond 8 categorical colors, users lose track of
  the legend. More than 8 → consider non-color encodings (shape, pattern, icon)

### Traffic Light Pitfall

Red/yellow/green status encoding is overused and problematic:
- Deuteranopia (red-green colorblindness) affects ~8% of males — red and green
  look the same
- Always pair color with shape/icon/text when encoding status
- Consider whether orange/amber reads clearly enough from green in your specific
  palette before using it

---

## Colorblind-Safe UI Palettes

### Which Types to Design For

| Type | Prevalence | Can't distinguish |
|---|---|---|
| Deuteranopia (green weakness) | ~5–6% male | Red and green |
| Protanopia (red weakness) | ~1–2% male | Red and green (red appears very dark) |
| Tritanopia (blue weakness) | ~0.01% | Blue and green; yellow and red |

Design for deuteranopia/protanopia first — they affect the most users and share
the red-green confusion.

### Safe Strategies

1. **Never use color as the only differentiator** — always pair with label,
   icon, or pattern
2. **Avoid red/green adjacency** for data with opposing meanings (success/fail,
   good/bad) — use blue/orange or purple/yellow as colorblind-safe alternatives
3. **Simulate** with deuteranopia filters in Figma (View > Color Blindness
   Simulation) to verify before declaring a palette complete
4. **Check status icon shapes**: success = check, warning = triangle, error =
   circle-x — shape + color together, always

---

## Simultaneous Contrast in UI

Adjacent UI elements change each other's perceived color. The same surface color
looks different when surrounded by a lighter vs. darker border. The same text
color appears darker on a light card vs. a slightly tinted row.

**Practical implications**:
- Tokens must be evaluated **in context** — on the actual surface they'll appear
  on — not against white or in isolation
- Semantic color swatches in documentation should show the color on the surfaces
  where it will actually appear
- A blue that passes APCA on a white surface may fail or look different on
  a slightly tinted card background

**Testing practice**: always evaluate color decisions in a representative
composition, not on a blank artboard. Use realistic states: hover, selected,
focused, disabled.

---

## Failure Modes Summary

| Failure Mode | Description | Fix |
|---|---|---|
| Palette inversion | Dark mode = light mode with inverted colors | Redesign dark mode surfaces from scratch using OKLCH |
| Pure black backgrounds | `#000000` in dark mode | Use near-black with subtle chroma: `oklch(16% 0.008 245)` |
| Decorative semantic colors | Success green used as brand accent | Restrict semantic colors to status contexts only |
| Color as only differentiator | Red = bad, green = good, no other signal | Always pair color with icon, label, or pattern |
| Swatch-based decisions | Colors approved in isolation, look wrong in context | Evaluate all colors on representative compositions |
| Achromatic neutrals | Pure gray scales that look cold | Add subtle chroma (C=0.005–0.015) to neutrals |
| Too many accent colors | 3–4 competing "interactive" colors | Reduce to 1 primary interactive color + at most 1–2 supporting |
| sRGB-biased palette | Scale looks uneven in perceived brightness | Rebuild in OKLCH with consistent L steps |

---

## Cross-Links

- `gd-color-theory` — foundational color science: harmony, perceptual uniformity, simultaneous contrast
- `ds-advisor` — color decisions become token architecture here; semantic token design
- `lead-accessibility-architect` / `a11y-visual` — contrast requirements, APCA measurement
- `uid-surface-depth` — dark mode elevation expressed through surface lightness
- `uid-visual-system` — color palette as part of the complete visual language
- `lead-frontend-engineer` / `fe-component-architecture` — OKLCH in CSS custom properties
- `lead-type-designer` / `type-letterform-construction` — how color interacts with type rendering at small sizes
