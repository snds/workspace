---
name: found-color
description: >
  Context-free principles of color — perception, perceptual uniformity (OKLCH),
  harmony systems, simultaneous contrast, color-vision deficiency mechanics, and
  proportion. The shared root beneath gd-color-theory (print), uid-color-for-ui
  (screen), infod-encoding-theory (data), and motion/3d color. Load BEFORE any
  medium-specific color spoke. Triggers: color harmony, OKLCH, perceptual color,
  simultaneous contrast, Albers, color blindness, 60-30-10, color proportion.
aliases: [found-color]
triggers: [color harmony, oklch, perceptual color, simultaneous contrast, albers, color blindness, color vision deficiency, 60-30-10, color proportion]
tier: foundation
hub: design-foundations
domain: design
surfaces: ["*"]
spec_version: "2.0"
---

# Foundations — Color

Context-free color principle. Medium-specific application (CMYK/Pantone for print, surface lightness and
token values for screen, encoding channels for data) lives downstream — see **Applied in** below. If a
statement here is not true for print **and** screen **and** data **and** motion, it is in the wrong file.

## Perceptual model
- **Additive (light) vs. subtractive (pigment)** are the two physical mixing models; everything visual is
  one or the other. They predict *what mixes to what*, not *what looks related* — that's harmony + perception.
- **Perceptual uniformity (OKLCH / Oklab).** Equal numeric steps in HSL are *not* equal perceptual steps;
  OKLCH's lightness/chroma/hue are tuned so equal steps look equal. Reason about palettes in a perceptual
  space, then export to whatever the medium needs (hex, CMYK, tokens).

## Harmony systems
Relationships on the hue wheel that read as intentional: **complementary** (opposite — maximum tension),
**analogous** (adjacent — calm), **triadic** (evenly spaced — vivid balance), **split-complementary**
(softer tension), **tetradic** (two complementary pairs — hardest to balance). Harmony sets *relationships*;
proportion and context decide whether it works.

## Simultaneous contrast (Albers, Bezold)
**No color is seen in isolation.** The same color shifts in hue, value, and chroma depending on what
surrounds it — Albers' central lesson. The Bezold effect: changing one color in a composition shifts the
apparent character of all the others. Consequence: **always evaluate color against its real neighbors**,
never on a neutral swatch.

## Proportion — the 60-30-10 law
Visual rest comes from unequal distribution: ~60% dominant, ~30% secondary, ~10% accent. Equal proportions
fight; the accent only reads as an accent because it's scarce. A law of *proportion*, true in any medium.

## Color-vision deficiency (mechanics)
~8% of men, ~0.5% of women. **Deuteranopia/deuteranomaly** (green) is most common; **protanopia** (red),
**tritanopia** (blue-yellow) rarer. Mechanism: one cone type is absent or shifted, collapsing red↔green (or
blue↔yellow) discrimination. Principle: **never encode meaning by hue alone** — pair with value, shape,
position, or label. (Specific contrast *thresholds* and the audit gate are governance — see [[a11y-visual]].)

## Applied in
- [[gd-color-theory]] — print: CMYK, Pantone, dot gain, ICC, proof-to-press.
- [[uid-color-for-ui]] — screen: the four UI color roles, dark-mode surface lightness, token reference values.

## Related
- hub → [[design-foundations]]
- applies-in ← [[gd-color-theory]] · [[uid-color-for-ui]]
- peer ↔ [[found-hierarchy]]
