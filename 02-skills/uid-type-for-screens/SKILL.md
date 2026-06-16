---
name: uid-type-for-screens
description: >
  Typography for digital interfaces — screen rendering realities, optical sizing,
  type hierarchy for UI, font selection for screens, variable font usage in UI,
  and type scale implementation. Use this skill when the conversation touches:
  screen typography decisions, type scale design for UI, font rendering on screens,
  font selection for enterprise UI (legibility, tabular figures, disambiguation),
  line height in UI components, letter spacing for labels vs. display text,
  variable font usage (opsz, wght axes), responsive type scales, web font
  performance, or "why does this font look wrong on screen?" This spoke is part
  of the lead-ui-designer hub skill network.
---

# UID: Type for Screens

Specialist spoke for typography in digital interfaces. Part of the
`lead-ui-designer` hub skill network.

---

## Domain Boundary

This spoke owns **typographic decisions for screens**: what types to use, why,
how to build a scale, how screen rendering affects choices, and how to implement
type hierarchy in UI contexts.

- **Deep glyph construction, spacing metrics, OpenType features** → `lead-type-designer`
- **Classical typographic theory (measure, leading, modular scales)** → `gd-typography`
- **Type token architecture in Figma/code** → `ds-advisor`
- **Accessibility minimum sizes, contrast for type** → `lead-accessibility-architect` / `a11y-visual`

---

## Screen Rendering Fundamentals

Before any type decisions, understand the physical context. Typography that looks
correct in print or at large sizes often looks wrong on screen because the
rendering environment is fundamentally different.

### Subpixel Rendering and Hinting

**What it is**: ClearType (Windows) and similar systems render the sub-red-green-
blue components of each pixel independently to achieve higher apparent horizontal
resolution. This is why text can look sharper than the pixel grid alone would allow.

**Design implication**: Fonts designed with hinting instructions (vertical and
horizontal stem snap, zone hints) render more crisply at small sizes. Fonts
ported directly from print without screen-specific hinting may look blurry below
18–20px on standard-density displays.

**On HiDPI/Retina displays**: Subpixel rendering is largely irrelevant at 2x+
density because actual pixels are small enough that anti-aliasing alone is
sufficient. This is why many modern fonts (designed for HiDPI) have minimal
hinting and look beautiful on Retina but mediocre on a 1080p monitor.

**Practical decision**: When selecting a UI font, test on a standard 1080p
display, not just on your Retina MacBook. Enterprise users on Windows at 96dpi
is still a significant use case.

### Anti-Aliasing

**`-webkit-font-smoothing: antialiased`** on macOS renders text thinner and
lighter than the default subpixel rendering. It looks "cleaner" but can reduce
readability at small sizes and for users with vision differences. Use deliberately,
not as a blanket reset.

**On Windows**: `font-smooth` has no equivalent with consistent behavior. Windows
ClearType is the rendering engine, and it's not CSS-controllable.

**Design implication**: A type system that looks perfect with `antialiased` on
macOS may need different weight selections to maintain the same visual weight on
Windows without it.

### Pixel Density

| Display Class | DPI | Context | Type Minimum |
|---|---|---|---|
| Standard desktop | ~96dpi (1x) | Windows enterprise, secondary monitors | 14px comfortable; 12px minimum with good font |
| HiDPI desktop | ~144dpi (1.5x) | Mid-range Windows, some monitors | 12px comfortable |
| Retina / 2x | ~192dpi | MacBook, many modern displays | 11px possible but still use 12px min |
| Mobile 3x | ~460+ dpi | iPhone Pro, flagship Android | 11px minimum (but OS accessibility overrides apply) |

**Enterprise design reality**: Assume your users are on Windows at 96dpi on a
second monitor that is not HiDPI. Design for that. Don't design exclusively for
the Retina display on your Mac.

---

## Type Hierarchy for UI

UI typography serves functional roles. Each level has constraints, not just sizes.

### The Functional Roles

| Level | CSS class example | Size range | Weight | Use |
|---|---|---|---|---|
| **Display** | `.type-display` | 36–56px | 600–700 | Hero text, empty state illustrations, onboarding headers |
| **Headline** | `.type-headline-lg/md/sm` | 24–32px | 600–700 | Page titles, modal headers, section titles |
| **Title** | `.type-title-lg/md/sm` | 18–22px | 500–600 | Card titles, table section headers, sub-page titles |
| **Body** | `.type-body-lg/md/sm` | 14–16px | 400 | Main content text, descriptions, labels with text |
| **Label** | `.type-label-lg/md/sm` | 12–14px | 500 | Form labels, table column headers, navigation items, button text |
| **Caption** | `.type-caption` | 11–12px | 400 | Timestamps, footnotes, helper text, metadata |
| **Code** | `.type-code` | 13–14px | 400 | Inline code, code blocks — always monospace |

**Rule**: Every instance of the same text level should use the same style.
Drift in body text size (14px in one place, 15px in another) signals that the
scale wasn't used consistently. Use the scale; don't freestyle.

### Line Height in UI

Line height is not just readability — it defines structural dimensions:
- **Touch target size**: A label with 24px line height becomes a 24px touch target. Too small.
- **Table row height**: Line height × 1 + vertical padding = row height. Inconsistent
  line heights create inconsistent row heights across a data table.
- **Vertical rhythm**: All spacing in a layout looks more coherent when text
  line heights are multiples of the base unit (8px or 4px).

**Reference values**:
- Display text (36px+): line-height 1.1–1.2 (tight — optical correction for large text)
- Headlines (24–32px): line-height 1.2–1.3
- Body text (14–16px): line-height 1.5–1.6 (generous for readability)
- Label text (12–14px): line-height 1.4–1.5
- Caption (11–12px): line-height 1.4

**Failure mode**: Setting `line-height: 1` on labels to "save space" — text
becomes illegible for multi-line labels and creates vertical rhythm breaks.

### Letter Spacing in UI

Letter spacing (tracking) is functional, not decorative:

| Context | Value | Reason |
|---|---|---|
| Large display text (36px+) | −0.02em to −0.05em | Optical correction — wide spacing at large sizes looks too loose |
| Headlines (20–32px) | −0.01em to −0.02em | Slight tightening for cohesion |
| Body text (14–16px) | 0 (default) | Fonts are designed for body tracking; don't adjust |
| Labels (12–14px) | 0 to +0.01em | Very slight widening if needed for legibility |
| Small uppercase labels (11–13px) | +0.05em to +0.10em | Uppercase at small sizes needs extra tracking for legibility |

**Failure mode**: Applying decorative letter-spacing to body text because "it
looks refined." This typically reduces readability. Tracking is a tool, not an
aesthetic default.

---

## Font Selection for UI

Choosing the right typeface for a UI is a functional decision, not just an
aesthetic one. Evaluate on these criteria:

### X-Height

Fonts with a tall x-height (the ratio of lowercase to uppercase letter height)
are more legible at small sizes. At 12px, a font with a 70% x-height (like Inter)
reads more clearly than one with a 60% x-height (like Garamond).

**Enterprise recommendation**: x-height ≥ 68% for body text fonts. Inter,
Source Sans, IBM Plex Sans, and similar system-aligned fonts score well here.

### Tabular Figures

In data tables and numeric display, figures must be **tabular** (monospaced
width) so that numbers align in columns. Most modern UI fonts offer this as an
OpenType feature: `font-variant-numeric: tabular-nums` or
`font-feature-settings: "tnum"`.

**Test**: Type a column of numbers in your chosen font. If the decimal points
and thousands separators do not vertically align, the font lacks tabular figures
or they're not enabled.

**Failure mode**: Using proportional figures in data tables — numbers don't align
and the table looks like it's vibrating when the user reads down a column.

### Character Disambiguation

At small sizes, certain character pairs are often confused:
- **0 and O** (zero vs. capital O) — critical in IDs, codes, reference numbers
- **l, I, and 1** (lowercase L, capital I, one) — critical in passwords, codes
- **Q and O** — in logos/labels at small sizes

Inter, for example, has a disambiguated zero by default. Many serif fonts and
some display fonts are poor at this.

**Test**: Type `0OlI1` in your font at 14px. Can you immediately distinguish all
five characters?

### Language Support

Enterprise SaaS with global users requires extended Latin at minimum (covering
French, German, Spanish, Portuguese, Dutch, Czech, Polish, etc.). If serving
Southeast Asian or East Asian markets, verify font coverage before selection.

**Check**: Does the font support all characters needed for your user base?
Missing glyphs produce the tofu square □ — always visible, always a failure.

### Common UI Font Recommendations (Enterprise SaaS)

| Font | Notes |
|---|---|
| **Inter** | Most common enterprise UI font. Excellent x-height, tabular figures, good disambiguation at all weights. Free. |
| **IBM Plex Sans** | Slightly more distinctive character. Good technical feel. Free. |
| **Source Sans 3** | Clean, very legible at small sizes. Good technical/neutral feel. Free. |
| **Geist Sans** (Vercel) | Modern geometric; good at small sizes. Free. |
| **DM Sans** | Geometric; feels slightly more consumer-facing. Good x-height. Free. |

**Paid options**: Söhne, Aktiv Grotesk, Neue Haas Grotesk — all good enterprise
choices with better hinting and character coverage than free alternatives, at cost.

---

## Variable Fonts in UI

Variable fonts offer significant advantages for UI:

### The `opsz` Axis (Optical Size)

When available, `font-optical-sizing: auto` or explicit `font-variation-settings: 'opsz' 14`
tells the font to use its optical size variant designed for the target size.
At small sizes, letterforms are opened up and stroke contrast is reduced for
legibility. At large display sizes, they can be more refined.

**Use it**: If your chosen font has an `opsz` axis, enable it. It's the equivalent
of having a separate display face and a text face in a single font file.

### The `wght` Axis

Variable weight allows precise weight selection rather than jumping between 400
and 700. This enables:
- `font-weight: 450` for labels that need slightly more presence than regular but
  shouldn't feel bold
- `font-weight: 550` for medium-emphasis titles that aren't as heavy as 600

**CSS implementation**:
```css
/* Variable font weight axis */
.type-label { font-weight: 500; }       /* works with variable fonts */
.type-headline { font-weight: 640; }    /* intermediate value, only works with variable font */
```

**Failure mode**: Loading Inter with `font-weight: 500` but not specifying the
variable font axes — it falls back to the nearest named weight (Regular or Medium)
without the intermediate value.

### Web Font Performance

Variable fonts reduce HTTP requests (one file vs. 6–8 static weight files) but
the file itself is larger. Trade-offs:

- **Use `font-display: swap`**: Shows fallback text immediately while the font
  loads. Prevents invisible text during load.
- **Preload critical fonts**: `<link rel="preload" as="font">` for the 1–2 font
  files used in the critical rendering path (the body weight, usually).
- **WOFF2 only**: WOFF and TTF are legacy formats. Modern browsers support WOFF2.
  Only include WOFF2 in new builds.
- **Subset if possible**: If your product is Latin-only, subsetting the font to
  Latin + Extended Latin can reduce file size by 30–50%.

```css
@font-face {
  font-family: 'Inter';
  src: url('/fonts/Inter.var.woff2') format('woff2-variations');
  font-weight: 100 900;
  font-display: swap;
  font-style: normal;
}
```

---

## Type Scale Implementation

### Modular Scale Adapted for Screens

Classical modular scales (1.25 Major Third, 1.333 Perfect Fourth) produce
mathematically harmonious scales but often need adjustment for UI:

- **Perfect Fourth scale (×1.333)** from 16px base:
  12, 14, 16, 21, 28, 37px → gaps too large for the middle range
- **Custom UI scale** from 12px, +2px steps through the label/body range,
  larger jumps at headline:
  12, 14, 16, 18, 20, 24, 28, 32, 40, 48px → more usable steps in the functional range

**Rule**: UI type scales prioritize functional steps over mathematical purity.
The 12–24px range where most UI text lives needs more steps, not fewer.

### Responsive Type Scale with CSS clamp()

```css
/* Title: 20px at mobile, scales to 24px at desktop */
.type-title {
  font-size: clamp(1.25rem, 1.1rem + 0.5vw, 1.5rem);
}

/* Body: fixed — don't scale body text with viewport */
.type-body {
  font-size: 1rem; /* 16px — don't scale */
}
```

**Rule**: Scale display and headline text responsively. Keep body and label text
at fixed sizes — responsive body text introduces readability variables that are
hard to control and rarely provide meaningful improvement.

---

## Failure Modes Summary

| Failure Mode | Description | Fix |
|---|---|---|
| Ignoring 1x rendering | Designed exclusively on Retina; looks poor on standard displays | Test on Windows at 96dpi before finalizing |
| No tabular figures | Numbers misalign in data tables | Enable `font-variant-numeric: tabular-nums` or choose a font with tabular figures |
| Line height ≤1 on labels | Text becomes unreadable and layout has no rhythm | Set minimum line-height 1.4 on all text |
| Decorative tracking on body | Letter-spacing applied for aesthetics, reduces readability | Reserve tracking for large display text (negative) and small uppercase labels (positive) |
| Too few scale steps in the 12–20px range | UI text doesn't have enough hierarchy options | Expand the scale with 2px steps through the functional range |
| Missing fallback font | FOIT (Flash of Invisible Text) during font load | Use `font-display: swap` and a well-matched system font fallback |
| Fixed display text | Headline sizes don't adapt to smaller viewports | Use `clamp()` for display and headline sizes |

---

## Cross-Links

- `gd-typography` — classical typographic theory: modular scales, measure, leading, hierarchy
- `lead-type-designer` — deep glyph construction, OpenType features, spacing metrics
- `ds-advisor` — type hierarchy decisions become type token values
- `lead-accessibility-architect` / `a11y-visual` — minimum text sizes, legibility for accessibility
- `uid-visual-system` — type system as part of the complete visual language
- `uid-color-for-ui` — color contrast for text must be re-evaluated against all surface colors
