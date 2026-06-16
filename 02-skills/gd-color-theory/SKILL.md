---
name: gd-color-theory
description: >
  Color as both science and language — the print tradition extended to all
  media. Use this skill whenever the conversation touches: CMYK, RGB, Pantone,
  HSL, OKLCH, color models, subtractive vs. additive color, color harmony,
  complementary color, analogous color, triadic schemes, color psychology,
  simultaneous contrast, Albers, Josef Albers interaction of color, perceptual
  color spaces, dot gain, paper stock effects on color, proof-to-press matching,
  the 60-30-10 rule, color accessibility, color vision deficiency, deuteranopia,
  WCAG color contrast, APCA, or design system color token architecture. This
  skill is the upstream rationale for all color decisions in brand, print, UI,
  and design systems.
aliases: [gd-color-theory]
tier: spoke
domain: design
hub: lead-graphic-designer
prerequisites: [lead-graphic-designer, found-color]
governed_by: [a11y-visual]
spec_version: "2.0"
---

# GD — Color Theory

Specialist lens for color as a design material — its physics, perception,
psychology, print behavior, and application logic. Part of the Lead Graphic
Designer skill network.


> **Foundations:** [[found-color]] — perceptual model, harmony, simultaneous contrast,
> proportion, and CVD mechanics live there. This spoke covers **print-specific** application.

---

## Domain Boundary

This skill owns **color theory and application decisions** — how color is
understood, specified, and used across print and digital media.

- **Screen color tokens and semantic color architecture** → `ds-advisor`
  (this skill is the upstream rationale)
- **UI color decisions** → `lead-ui-designer` / `uid-color-for-ui`
- **Color accessibility in interactive UI** → `lead-accessibility-architect` /
  `a11y-visual`
- **Color in data visualization** → `lead-information-designer`

---

## Color Models

Understanding which color model applies to which medium is prerequisite
knowledge. Using the wrong model causes predictable production failures.

### CMYK — Subtractive Color (Print)

**Physics:** Cyan, Magenta, Yellow, Key (Black) inks absorb light rather than
emit it. Layering inks subtracts more wavelengths from reflected light.
Full CMYK = near-black (not pure black, which requires the K channel).

**Gamut:** Narrower than sRGB. Many RGB colors (especially saturated blues,
greens, and oranges) cannot be reproduced in CMYK. This is the source of
color shift between screen proof and press output.

**When to use:** Any work destined for offset or digital printing. All print
files should be delivered in CMYK with specified ICC profile (see
`gd-print-production`).

**Common failure:** Designing in RGB, converting to CMYK at the end. The
conversion happens once — after which the color relationships between elements
may have shifted relative to each other. Design in CMYK from the start for
print-primary work.

### RGB — Additive Color (Screen)

**Physics:** Red, Green, Blue light sources add together. Full RGB = white.
Used for screens, projectors, and any light-emitting display.

**Gamut:** sRGB (the standard web/screen color space) covers approximately
35% of visible color. Display P3 (used in modern Apple/high-gamut displays)
covers approximately 45%. These are still gamut-limited — the eye can see
far more than any screen can produce.

**When to use:** Screen-only media. Never for print-primary work.

**sRGB is a device standard, not a perceptual standard:** Equal hex steps
do not produce equal perceived brightness changes. This is the central reason
why design system color scales built in sRGB hex values look "off" — the
steps are mathematically equal but perceptually uneven.

### Pantone — Standardized Ink (Spot Color)

**Physics:** A Pantone color is a specific proprietary ink formulation mixed
to a defined recipe. When printed as a spot color, it uses a dedicated ink
plate (rather than being built from CMYK components). This guarantees
color consistency across press runs, printers, and paper stocks.

**When to use:** Brand colors where consistency is paramount (corporate identity,
packaging, branded merchandise). Any situation where a CMYK build of the color
would drift unacceptably across paper stocks or press conditions.

**Pantone to CMYK builds:** Every Pantone color has a CMYK equivalent, but
the build is always a compromise — many Pantone colors (metallics, neons,
pastels, most saturated blues) cannot be accurately reproduced in CMYK. The
build value is an approximation. Always specify both the Pantone number and
the CMYK build in brand standards.

**Pantone Libraries:** Pantone Matching System (PMS) for coated/uncoated
stock; Pantone Solid Coated vs. Solid Uncoated variants of the same color
look dramatically different — uncoated paper absorbs ink and shifts the
hue cooler and darker.

### HSL/HSB — Designer-Facing Color Picker

**Not a production color space** — a human-facing representation of RGB that
separates Hue (0–360°), Saturation (0–100%), and Lightness/Brightness (0–100%).
This is the color picker interface in most design tools.

**Limitation:** HSL does not model perceptual uniformity. Moving from 50%
to 60% saturation does not produce a 10% perceived increase in saturation —
the relationship is nonlinear and varies by hue.

### OKLCH — Perceptual Color Space (Modern Standard)

**Physics:** OKLCH separates three axes that correspond to human color
perception: L (Lightness, 0–1), C (Chroma / saturation, 0–0.4+), H (Hue,
0–360°). Equal L steps produce equal perceived brightness changes. Equal C
steps produce equal perceived saturation changes.

**Why it matters for design systems:** Token scales built in sRGB hex
produce perceptually uneven steps. Token scales built in OKLCH produce
perceptually uniform steps — which means:
- A neutral gray scale (N100–N900) where each step looks evenly spaced
- Brand color tints/shades where the 200 variant looks "one step lighter"
  than the 300 variant (not slightly lighter or dramatically lighter)
- Status color palettes (success/warning/error) where all three feel
  equally "present" at the same token step

**DS implication:** Design system color scales should be designed in OKLCH,
then converted to sRGB/P3 for output. The conversion may require gamut mapping
(some OKLCH values exceed sRGB gamut) — the mapping strategy should reduce
chroma to preserve lightness relationships.

---

## Harmony, proportion, simultaneous contrast → foundations

Harmony systems, the 60-30-10 proportion law, and Albers' simultaneous contrast are **context-free
principle** — they live in [[found-color]] (loaded first via this spoke's foundation prerequisite).
Apply them here with print constraints in mind (ink limits, substrate shift, spot vs. process).

## Color Psychology

Color associations are real but culturally and contextually variable.
Over-generalizing produces confident misinformation.

**What is defensible:**
- **Warm colors (red, orange, yellow)** advance spatially (appear to come
  forward in the picture plane) and signal urgency, energy, or warmth
- **Cool colors (blue, green, violet)** recede spatially and signal calm,
  trust, or distance
- **Saturation** increases perceived energy and excitement; desaturated palettes
  read as sophisticated, calm, or muted
- **Value contrast** signals importance — the highest contrast element is
  perceived as most important

**What requires cultural context:**
- Red means danger in Western contexts, celebration in Chinese contexts,
  political identity in other contexts
- White means purity/simplicity in Western contexts, mourning in some East
  Asian contexts
- Green means environmental/eco in many Western markets but has specific
  political associations elsewhere

**The design principle:** Never assume a color's cultural meaning is universal.
When designing for global audiences, verify color associations for primary
target markets. Name the assumptions when documenting brand color choices.

---

## Color in Print

### Dot Gain

In offset printing, ink spreads as it contacts paper — the dots that make up
the halftone image expand, darkening the output. Standard dot gain:
- Coated paper: 10–15%
- Uncoated paper: 20–30%
- Newsprint: 30–40%

ICC profiles (ISO Coated v2, Fogra39, SWOP) encode expected dot gain
mathematically. Files prepared with the correct profile will appear lighter
on screen but print correctly.

**Failure mode:** Preparing files for coated paper and printing on uncoated —
the output will be noticeably darker and muddier than anticipated.

### Paper Stock Effects on Color

- **Coated paper** (gloss, silk, matte): ink sits on the surface; bright,
  saturated color; fine halftone dots hold; sharp edges
- **Uncoated paper**: ink absorbs into the fibers; colors shift cooler and
  darker; fine halftone dots bleed; softer edges; better for warmth and
  tactile quality
- **Paper whiteness/brightness** affects every color — a cream-colored
  uncoated stock will shift all colors warm

**The practical rule:** never approve a color proof on a different stock than
the intended print stock.

### Proof-to-Press Matching

Three levels of proof:
1. **Digital proof (contract proof)**: colorimetrically accurate print on
   an inkjet proofing device using the production ICC profile; the legal
   standard for color approval
2. **Press proof**: a short run on the actual press with the actual inks and
   paper; expensive but the most accurate prediction
3. **Soft proof (monitor proof)**: on a calibrated monitor with the production
   ICC profile applied; fast and cheap but dependent on monitor calibration

A signed contract proof is the designer's best protection against press-to-proof
color disputes.

---

## Color Accessibility

### Color Vision Deficiency Types

| Type | Mechanism | Prevalence |
|------|-----------|-----------|
| Deuteranopia / deuteranomaly | Reduced/absent M-cone sensitivity (green) | ~6% of males, ~0.4% of females |
| Protanopia / protanomaly | Reduced/absent L-cone sensitivity (red) | ~2% of males |
| Tritanopia / tritanomaly | Reduced/absent S-cone sensitivity (blue) | ~0.003% |
| Achromatopsia | No color vision | Very rare |

**Deuteranopia is the most common** — approximately 1 in 16 males cannot
reliably distinguish red from green. This makes red/green status color systems
(the most common UI pattern) a significant accessibility failure.

### Design Rules for Color Accessibility

1. **Never use color as the only differentiator.** Any information encoded by
   color must also be encoded by shape, pattern, position, text, or icon.
   "The error is shown in red" fails for users with red-green CVD.

2. **Test with simulation.** Figma's accessibility plugins and tools like
   Sim Daltonism simulate CVD. Use them.

3. **Verify contrast.** WCAG 2.1 AA requires 4.5:1 contrast for normal text,
   3:1 for large text. APCA (WCAG 3.0 draft) provides a more nuanced
   perceptual model. Use APCA for new work.

4. **Status colors need hue separation and value separation.** Success green,
   warning amber, and error red must be distinguishable in CVD simulation.
   Separate them by both hue AND lightness — don't rely on hue alone.

---

## Anti-Patterns

- **Designing in RGB for print.** Colors will shift at CMYK conversion; some
  cannot be reproduced. Design in CMYK from the start for print-primary work.
- **Specifying Pantone without CMYK builds.** Brand standards must include all
  four color specifications: Pantone, CMYK, RGB, and HEX.
- **Building color scales in hex/sRGB.** Perceptually uneven steps produce
  color scales that look "off" to trained eyes. Build in OKLCH.
- **Evaluating colors in isolation.** Simultaneous contrast means a color only
  behaves predictably in its actual context.
- **Color as the only differentiator.** Status, category, and emphasis must have
  a secondary differentiator beyond hue.
- **Assuming universal color psychology.** Red means different things in different
  cultural contexts. Always verify for global audiences.
- **Uncoated/coated mismatch.** Approving proofs on the wrong stock.

---

## Related
- foundation → [[found-color]]
- hub → [[lead-graphic-designer]]
- governed-by → [[a11y-visual]]
