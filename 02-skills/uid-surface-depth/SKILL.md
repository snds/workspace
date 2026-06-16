---
name: uid-surface-depth
description: >
  Elevation, layering, shadow design, blur and frosted glass aesthetics, material
  design systems, and dark mode depth. Use this skill when the conversation
  touches: surface design, elevation systems, shadow design (realistic vs. designed
  shadows, colored shadows), backdrop-filter and glassmorphism (when it's appropriate
  and when it's not), neumorphism problems, dark mode elevation through lightness,
  modal and overlay depth, the surface layer stack in enterprise UI, or "how do
  we express depth without looking dated or decorative?" This spoke is part of
  the lead-ui-designer hub skill network.
aliases: [uid-surface-depth]
tier: spoke
domain: design
hub: lead-ui-designer
prerequisites: [lead-ui-designer]
spec_version: "2.0"
---

# UID: Surface Depth

Specialist spoke for elevation, layering, shadow design, and material aesthetics.
Part of the `lead-ui-designer` hub skill network.

---

## Domain Boundary

This spoke owns **depth as a visual design system**: how elevation is designed,
how surfaces behave at different levels, how depth communicates hierarchy, and
the aesthetics of material choices (flat, shadow-based, glassmorphic).

- **Surface color token architecture** → `ds-advisor`
- **Dark mode surface color construction in OKLCH** → `uid-color-for-ui`
- **GPU cost of backdrop-filter** → `lead-frontend-engineer` / `fe-performance`
- **Accessibility contrast on elevated surfaces** → `lead-accessibility-architect`

---

## Elevation as Information Hierarchy

Elevation is not decoration — it is a semantic signal. In UI design, elevation
communicates:

**What is "above" what in the interface**: A modal is above the page content.
A dropdown is above the card it opens from. A sticky header is above scrolling
content. These relationships communicate context and priority.

**What requires attention vs. what is background**: Higher elevation draws
the eye. A dialog at elevation-5 is more immediately visible than a card at
elevation-2. The elevation stack should match the attention hierarchy.

**What is interactive vs. ambient**: In many design systems, interactive
elements (buttons, inputs) have slightly higher elevation than static surfaces —
a subtle signal that they respond to interaction.

### The Rule: Elevation Must Be Systematic

Ad-hoc shadow decisions — "this card needed a shadow so I added `box-shadow: 0 2px 8px rgba(0,0,0,0.1)`"
— create elevation systems that are incoherent. Every shadow has an implied
position in a stack. When shadows are inconsistent, users can't read the
depth relationship between elements, and the UI feels visually noisy.

**Every element should belong to a named elevation level.** The shadow
(or surface lightness, in dark mode) for that level should come from a token,
not be hand-rolled.

---

## Shadow Design

### Realistic vs. Designed Shadows

**Realistic shadows** simulate a physical light source. One light source, one
direction (typically top-left for most Western UI), with umbra and penumbra.
Umbra: the hard shadow core. Penumbra: the soft, diffused outer edge.

```css
/* Realistic shadow — single light source */
box-shadow:
  0 1px 2px rgba(0,0,0,0.06),     /* umbra */
  0 2px 8px rgba(0,0,0,0.08);     /* penumbra */
```

**Designed shadows** prioritize visual hierarchy signal over physical realism.
A subtle tonal shift (light border on top, darker underside) can substitute for
a full shadow on minimalist designs. Colored shadows (tinted with the surface
color) look more designed and less generic than pure black rgba shadows.

**Enterprise recommendation**: Use designed, physically plausible shadows rather
than purely realistic ones. Photorealistic shadows (with complex light rigs) are
typically too decorative for enterprise data UIs. Designed shadows provide
hierarchy signal without visual noise.

### Shadow Scale (Light Mode)

Each elevation level has a defined shadow. Values are guidelines — adjust for
your specific palette and brand personality.

| Level | Description | Shadow |
|---|---|---|
| **0 (flat)** | No elevation — base surface | No shadow; use color/border differentiation |
| **1 (card)** | Cards, list items, form containers | `0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.06)` |
| **2 (raised)** | Sticky headers, action bars | `0 2px 6px rgba(0,0,0,0.08), 0 1px 3px rgba(0,0,0,0.06)` |
| **3 (overlay)** | Popovers, dropdowns, tooltips | `0 4px 12px rgba(0,0,0,0.10), 0 2px 4px rgba(0,0,0,0.06)` |
| **4 (modal)** | Dialogs, drawers, sheet panels | `0 8px 24px rgba(0,0,0,0.12), 0 4px 8px rgba(0,0,0,0.08)` |
| **5 (global)** | Notifications, command palette | `0 16px 40px rgba(0,0,0,0.14), 0 8px 16px rgba(0,0,0,0.08)` |

**Colored shadows**: Replace `rgba(0,0,0,...)` with `rgba(h, s, l, ...)` using
a tinted version of the surface color or brand color. The effect is subtle but
makes shadows look designed rather than default.

```css
/* Colored shadow — tinted with brand blue */
box-shadow:
  0 4px 12px oklch(52% 0.14 245 / 0.12),
  0 2px 4px oklch(52% 0.14 245 / 0.08);
```

### Failure Modes in Shadow Design

- **Shadow on flat backgrounds with no context**: A card shadow that doesn't
  contrast with its background — happens when the page background is already
  white and the card is also white. Fix: add a subtle surface color difference
  between page and card, or reduce shadow opacity.
- **All elements at the same shadow elevation**: When cards, modals, and dropdowns
  use the same shadow, depth relationships are incoherent.
- **Shadows on text or icons**: Shadows on non-surface elements (text-shadow on
  body text, drop-shadow on functional icons) are decorative noise. Reserve for
  display type where it contributes to legibility.

---

## Blur and Frosted Glass

`backdrop-filter: blur()` creates a frosted glass effect — the content behind
the surface is blurred while the surface itself is translucent.

### When Blur Is Appropriate

Blur signals: "I am transparent and aware of the content behind me." This is
appropriate when:
- **Overlapping layers need to maintain visual connection to the content below**:
  A modal that blurs the page behind it keeps the user contextually aware that
  the page is still there.
- **Navigation bars that float above scrolling content**: A translucent nav bar
  with blur is a visual signal that the content is scrolling under a persistent
  surface.
- **Sidesheets, command palettes**: The partial transparency communicates
  "context is preserved; you haven't navigated away."

### When Blur Is Decoration (Avoid)

Blur that serves no contextual purpose is visual noise that carries GPU cost.
Avoid blur when:
- The surface doesn't overlap meaningful content (there's nothing to see through)
- The surface is opaque in most states (full-opacity backgrounds with blur
  only visible in edge cases)
- The effect is applied globally "for aesthetics" rather than to signal layering

**Performance note**: `backdrop-filter` forces the browser to create a compositor
layer for the blurred surface AND for every element that appears behind it.
On GPU-constrained devices (low-end laptops, older hardware common in enterprise),
this has measurable frame rate impact. Don't use casually. See `fe-performance`.

### Glassmorphism Assessment

Glassmorphism (translucent containers with backdrop blur, light borders, and
subtle shadows) was visually compelling when novel (~2020–2022) but is now
a recognizable aesthetic trend. In enterprise UI:
- Use sparingly: command palettes, notification toasts, floating action panels
- Avoid as the primary surface treatment: too decorative for data-dense contexts
- Ensure sufficient contrast: translucency makes APCA compliance harder to
  guarantee — always check text contrast on glassmorphic surfaces against the
  worst-case content behind them

---

## Material Aesthetics

A brief catalog of material design approaches, with enterprise suitability.

### Flat Design

**Characteristics**: No shadows, no gradients. Color differentiation and spacing
alone create hierarchy. Pure color backgrounds.

**Enterprise suitability**: High, with caveats. Flat design requires stronger
color hierarchy and spacing discipline to maintain elevation clarity. When done
well, it's clean and fast to render. When done poorly, it looks undifferentiated
and hard to scan.

**When**: Products that prioritize data density over expressive depth. Technical
tools, admin dashboards.

### Elevation Model (Material Design)

**Characteristics**: Each elevation level has a defined shadow (light mode) or
surface lightness increase (dark mode). The elevation stack is a designed system.
Material Design 3 uses `surfaceContainerLowest` through `surfaceContainerHighest`
as the elevation tiers.

**Enterprise suitability**: Very high. The elevation model is systematic, predictable,
and accessible. It communicates hierarchy without decoration. This is the most
widely understood and implemented model for enterprise UI.

**When**: Default recommendation for enterprise SaaS.

### Neumorphism

**Characteristics**: UI elements appear extruded from the background using
dual light/shadow simulation (light shadow on top-left, dark shadow on
bottom-right). Everything appears to be the same material.

**Enterprise suitability**: Very low. Critical problems:
- Extremely poor accessibility: contrast between element and background is
  intentionally subtle, often below WCAG AA
- High cognitive load: all elements look similar; hierarchy is nearly invisible
- Interactive vs. non-interactive states are indistinguishable
- Fails completely in dark mode

**When**: Never in enterprise. Only as a stylistic experiment in personal/portfolio
work where accessibility is not a requirement.

### Apple HIG: Blur + Vibrancy

**Characteristics**: Translucent layers with `backdrop-filter` plus vibrancy
effects (colors that adapt to underlying content). System-native on macOS/iOS.

**Enterprise suitability**: Medium. Appropriate for native macOS/iOS apps following
HIG conventions. In web-based enterprise products, blur-only (without OS-native
vibrancy) produces a similar but simpler effect. Use selectively.

---

## Dark Mode Elevation

In dark mode, the shadow-based elevation model from light mode breaks down:
- Shadows become invisible on dark surfaces (dark shadow on dark background = invisible)
- Heavy shadow use in dark mode looks artificial — there's no ambient light to cast realistic shadows

**The Solution: Lightness as Elevation**

In dark mode, elevation is expressed through **surface lightness increase** in
OKLCH. Higher elevation = lighter surface.

| Elevation Level | Light Mode | Dark Mode |
|---|---|---|
| Base surface | White / very light gray | L ≈ 14–16% |
| Cards / panels | White (same as base, bordered) | L ≈ 18–20% |
| Raised components | Light gray | L ≈ 22–24% |
| Overlays / dropdowns | White with shadow | L ≈ 26–28% |
| Modals | White with heavy shadow | L ≈ 30–32% |
| Toasts / global | White with max shadow | L ≈ 34–36% |

Each step is approximately +4–5 L in OKLCH. This is subtle at individual steps
but produces clear visual hierarchy across the full stack.

**Shadows in dark mode**: Not eliminated entirely, but significantly reduced in
opacity and size. A modal in dark mode might have:
```css
box-shadow:
  0 8px 24px rgba(0, 0, 0, 0.3),   /* more opacity needed — dark bg mutes the contrast */
  0 4px 8px rgba(0, 0, 0, 0.2);
```

**Do not use higher opacity to compensate**: Very high opacity shadows
(`rgba(0,0,0,0.6+)`) look heavy and unrefined. If shadows aren't reading, use
a combination of subtle shadow + surface lightness difference.

---

## The Enterprise UI Layering Stack

A complete elevation model for enterprise SaaS products:

```
Layer 0: App background     — base surface; everything else sits on this
Layer 1: Content cards      — primary content containers, data tables, panels
Layer 2: Sticky chrome      — sticky headers, persistent toolbars, sidebars (when elevated)
Layer 3: Inline overlays    — popovers, select menus, date pickers, context menus
Layer 4: Modal context      — dialogs, confirm sheets, full-screen modals
Layer 5: Global persistent  — toasts, progress indicators, command palette
```

Each layer has:
- A defined surface color (token)
- A defined shadow (token)
- A defined `z-index` range

This eliminates ad-hoc z-index choices and ensures consistent depth relationships
across the entire product.

---

## Depth Without Decoration

Before reaching for shadows or blur, exhaust these options:
1. **Color differentiation**: Page background ≠ card color; even 2–3% L difference in OKLCH reads as a surface change
2. **Border**: A 1px border at L+15% creates separation without any depth illusion
3. **Spacing**: Generous margin around an element creates the perception of it floating without a shadow
4. **Typography**: Higher-weight type in a contained area signals "this is a structured element"

Only after these options are insufficient should shadows and blur be added.
This approach reduces visual complexity in data-dense contexts where shadows
would add noise rather than hierarchy.

---

## Cross-Links

- `uid-color-for-ui` — dark mode surface color construction; OKLCH lightness for elevation
- `ds-advisor` — elevation stack becomes elevation tokens (surface color, shadow, border-radius per level)
- `gd-visual-communication` — figure/ground principles for depth perception
- `lead-frontend-engineer` / `fe-performance` — backdrop-filter GPU cost; compositor layer implications
- `uid-spatial-composition` — z-axis and layering overview at the composition level
- `uid-visual-critique` — evaluating whether depth hierarchy is working

## Related
- hub → [[lead-ui-designer]]
