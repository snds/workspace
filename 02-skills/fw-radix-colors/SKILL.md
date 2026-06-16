---
name: fw-radix-colors
description: >
  Radix UI Colors — 12-step accessible color scale system, dark mode pairing, alpha
  variants, P3 wide-gamut support, custom palette generation, and integration with
  Tailwind CSS and design token architectures. Use this skill whenever the conversation
  involves Radix Colors scales, the 12-step color system, generating custom color ramps
  that follow Radix conventions, APCA contrast, color tokens for design systems,
  dark/light mode color pairing, or integrating Radix Colors with Tailwind or CSS
  Modules. Also trigger when discussing accessible color palettes, color scale
  generation, or mapping Radix Colors as primitives in a 3-tier token model. If the
  user mentions "Radix Colors", "@radix-ui/colors", color scales with 12 steps, or
  accessible color systems — use this skill.
pinned_version: "3.0.0"
pinned_date: "2026-03-26"
changelog_url: "https://github.com/radix-ui/colors/releases"
aliases: [fw-radix-colors]
tier: spoke
domain: engineering
hub: lead-frontend-engineer
prerequisites: [lead-frontend-engineer]
spec_version: "2.0"
---

# Radix UI Colors — Framework Skill

## Version Check (run on every load)

Before beginning any Radix Colors work:

1. **Web search** for `@radix-ui/colors latest release npm` or check the releases URL.
2. **Compare** against `pinned_version: 3.0.0`.
3. If newer, flag to the user with key changes. Proceed with current knowledge.
4. If current, proceed silently.

---

## The 12-Step Scale System

Every Radix color scale has 12 steps, each with a defined semantic purpose. This is the
foundation — memorize this mapping:

### Step purposes

| Steps | Role | Usage |
|---|---|---|
| **1–2** | App & component backgrounds | Page background, subtle card/section fills. Step 1 is slightly lighter than 2. |
| **3–5** | Interactive component states | Step 3: normal, Step 4: hover, Step 5: pressed/selected |
| **6–8** | Borders | Step 6: subtle (cards, sections), Step 7: interactive borders, Step 8: strong borders + focus rings |
| **9–10** | Solid backgrounds | Step 9: highest chroma (purest color), Step 10: hover state for step 9 |
| **11–12** | Text | Step 11: low-contrast text (Lc 60 APCA), Step 12: high-contrast text (Lc 90 APCA) |

### Semantic grouping structure

```
BACKGROUNDS (foundation layer)
├── Step 1 — App background
├── Step 2 — Subtle component background
│
UI STATES (interactive layer)
├── Step 3 — Normal state
├── Step 4 — Hover state
├── Step 5 — Active / selected state
│
BORDERS (structural layer)
├── Step 6 — Subtle border
├── Step 7 — Interactive border
├── Step 8 — Strong border / focus ring
│
SOLIDS (emphasis layer)
├── Step 9 — Solid background (highest chroma)
├── Step 10 — Solid hover
│
TEXT (content layer)
├── Step 11 — Low-contrast text
└── Step 12 — High-contrast text
```

---

## Available Scales

### Grays (5)
Gray, Mauve, Slate, Sage, Olive

### Colors (25)
Red, Ruby, Crimson, Pink, Plum, Purple, Violet, Iris, Indigo, Blue, Cyan, Teal, Jade,
Green, Grass, Lime, Mint, Yellow, Amber, Orange, Tomato, Brown, Bronze, Gold

Each scale includes: 12 solid steps, 12 alpha variants, light mode, dark mode.

---

## Dark Mode Pairing

Radix uses the same CSS variable names for light and dark modes. The values swap automatically
based on which theme class is active:

```css
/* Light mode */
:root, .light, .light-theme {
  --blue-1: #eaf6ff;
  --blue-9: #0050f0;
  --blue-12: #061a4d;
}

/* Dark mode — same variable names, different values */
.dark, .dark-theme {
  --blue-1: #0d1520;
  --blue-9: #3d8aff;
  --blue-12: #c2d6f5;
}
```

**One-class-name approach**: `bg-blue-3` works in both themes without `dark:` prefixes.

### Automatic gray pairing
Each accent color is paired with a complementary gray scale. This pairing is calculated
to feel visually coherent (warm grays with warm accents, cool with cool).

---

## Alpha Variants

Every color has alpha (transparent) counterparts designed to blend over colored backgrounds:

```
Solid:  --blue-5
Alpha:  --blueA5

Solid dark: --blueDark5
Alpha dark: --blueDarkA5
```

**Use cases**: Overlays, glass-morphism effects, components on non-white backgrounds,
badges on colored surfaces.

---

## P3 Wide-Gamut Support

Radix Colors generates Display-P3 color definitions alongside sRGB:

- **Why**: Alpha blending in P3 behaves differently than sRGB. Without P3-specific
  definitions, colors look desaturated on modern Apple displays.
- **Format**: `color(display-p3 r g b / alpha)`
- **Automatic**: Custom palette generator outputs both sRGB and P3 definitions.

---

## Contrast & Accessibility Guarantees

Radix uses APCA (Accessible Perceptual Contrast Algorithm) instead of WCAG 2.1 ratios:

| Combination | APCA target | Meaning |
|---|---|---|
| Step 11 text on Step 1–2 bg | Lc 60 | Low-contrast text (secondary info) |
| Step 12 text on Step 1–2 bg | Lc 90 | High-contrast text (body copy) |

**Rule**: Stay within the same color family for guaranteed contrast. Cross-family
combinations (red text on blue background) are not guaranteed.

---

## CSS Custom Property Naming

```
Base:       --{color}-{step}        →  --blue-4
Alpha:      --{color}A{step}        →  --blueA4
Dark:       --{color}Dark{step}     →  --blueDark4
Dark alpha: --{color}DarkA{step}    →  --blueDarkA4
```

---

## Generating Custom Scales

### Official tool
[radix-ui.com/colors](https://www.radix-ui.com/colors) — Input 1–2 reference colors,
generates all 12 steps following Radix conventions. Supports wide-gamut input.

### Community tools
- **KColor** ([kcolor.co](https://kcolor.co/blog/docs/generator/modes/radix/)) — Automated
  12-step generation matching Radix conventions
- **radix-theme-generator** — Programmatic/runtime theme generation

### Generation principles
When creating custom scales, follow these rules:

1. **Step 9 = highest chroma** — This is the purest expression of the color.
2. **Steps 1–2 = near-white/near-black** — Almost invisible tint of the hue.
3. **Steps 11–12 = readable on 1–2** — Must pass APCA Lc 60/90 respectively.
4. **Monotonic lightness curve** — Lightness should decrease consistently from step 1→12
   (light mode) or increase from step 1→12 (dark mode).
5. **Chroma peaks at step 9** — Chroma rises through 3–9, then may drop slightly at 10–12
   for readability.

### Generative function pattern

```javascript
function generateRadixScale(hue, saturation) {
  // Lightness curve (light mode): 98% → 15%
  const lightness = [
    0.98, 0.96, 0.93, 0.89, 0.83,  // Steps 1-5 (backgrounds/states)
    0.74, 0.64, 0.53,               // Steps 6-8 (borders)
    0.55, 0.50,                      // Steps 9-10 (solids)
    0.38, 0.25                       // Steps 11-12 (text)
  ];

  // Chroma curve: peaks at step 9
  const chroma = [
    0.01, 0.02, 0.04, 0.07, 0.10,
    0.13, 0.16, 0.19,
    saturation, saturation * 0.9,
    saturation * 0.7, saturation * 0.5
  ];

  return lightness.map((l, i) => ({
    step: i + 1,
    value: `oklch(${l} ${chroma[i]} ${hue})`
  }));
}
```

This is a simplified illustration. Real Radix scales use more sophisticated perceptual
adjustments, but this captures the shape of the curves.

---

## Tailwind CSS Integration

### Method 1: CSS variable auto-discovery (Tailwind v4)

```css
@import '@radix-ui/colors/gray.css';
@import '@radix-ui/colors/blue.css';
@import 'tailwindcss';
```

Tailwind v4 automatically picks up `--blue-1` through `--blue-12` as color utilities.

### Method 2: Community plugins

- **tailwindcss-radix-colors** — Full Radix Colors with alpha modifier support
- **windy-radix-palette** — All scales mapped to Tailwind config

### Advantage over default Tailwind colors
Same class name works for both themes (no `dark:` prefix needed when using Radix's
theme-switching approach).

---

## 3-Tier Token Model Mapping

Radix Colors slot perfectly as Tier 1 (Primitive) tokens:

```
Tier 1 — Primitive (Radix Colors)
  --color-blue-1 through --color-blue-12
  --color-gray-1 through --color-gray-12

Tier 2 — Semantic
  --color-surface-default:     var(--color-gray-1)
  --color-surface-subtle:      var(--color-gray-2)
  --color-interactive-default: var(--color-blue-3)
  --color-interactive-hover:   var(--color-blue-4)
  --color-interactive-active:  var(--color-blue-5)
  --color-border-subtle:       var(--color-gray-6)
  --color-border-default:      var(--color-gray-7)
  --color-border-strong:       var(--color-gray-8)
  --color-solid-default:       var(--color-blue-9)
  --color-solid-hover:         var(--color-blue-10)
  --color-text-secondary:      var(--color-gray-11)
  --color-text-primary:        var(--color-gray-12)

Tier 3 — Component
  --button-bg:    var(--color-solid-default)
  --button-hover: var(--color-solid-hover)
  --button-text:  var(--color-surface-default)
```

---

## npm Package

```bash
npm install @radix-ui/colors
```

### JavaScript API

```javascript
import { blue, blueDark, gray, grayDark } from '@radix-ui/colors';

// blue.blue1 through blue.blue12 (solid)
// blue.blueA1 through blue.blueA12 (alpha)
```

### CSS import

```javascript
import '@radix-ui/colors/blue.css';
import '@radix-ui/colors/blueDark.css';
```

---

## Reference Spokes

| Spoke | When to load |
|---|---|
| `references/scale-generation-algorithms.md` | Deep dive on perceptual uniformity, APCA calculations, P3 gamma correction |
| `references/palette-recipes.md` | Pre-built semantic palette mappings for common DS archetypes (brand, neutral, status) |

---

## Design-Engineer Integration

This skill is a spoke of `design-engineer` and `ds-generation-pipeline`.
Pair with:
- **fw-tailwind-css** — Consumes Radix Colors as @theme primitives
- **fw-shadcn** — Components referencing semantic tokens derived from Radix scales
- **fw-radix-primitives** — Behavior layer using these colors for state indication
