---
name: uid-spatial-composition
description: >
  Layout composition for screens — spacing as meaning, visual relationships,
  grid application, negative space, compositional hierarchy, and responsive
  layout logic. Use this skill when the conversation touches: UI layout decisions,
  spacing choices, visual hierarchy in layout, compositional problems ("the page
  feels off"), 8px grid and base unit systems, optical vs. mathematical spacing,
  negative space in UI, visual weight distribution, responsive layout adaptation,
  z-axis and layering in 2D interfaces, or density design in enterprise UIs.
  This spoke is part of the lead-ui-designer hub skill network.
aliases: [uid-spatial-composition]
tier: spoke
domain: design
hub: lead-ui-designer
prerequisites: [lead-ui-designer]
spec_version: "2.0"
---

# UID: Spatial Composition

Specialist spoke for layout composition and spatial hierarchy in digital
interfaces. Part of the `lead-ui-designer` hub skill network.

---

## Domain Boundary

This spoke owns **spatial decisions as aesthetic choices** — why the spacing
is what it is, what it communicates, and how it creates or breaks hierarchy.

- **How spatial decisions become spacing tokens** → `ds-advisor`
- **Grid and layout foundational theory (print origins)** → `gd-grid-and-layout`
- **Interactive layout patterns (interaction design)** → `lead-ux-designer` / `ux-interaction-design`
- **Surface design (elevation and z-axis depth)** → `uid-surface-depth`

---

## Spatial Relationships as Communication

Every spacing decision is a communication decision. There is no "neutral" spacing.

**Proximity signals relationship**: Elements close together are perceived as
related. Elements with space between them are perceived as separate or belonging
to different groups. This is Gestalt proximity — it operates automatically,
before users consciously process the layout.

**Implication**: Grouping related elements closely is not optional for clarity —
it's how the eye reads relationships. A form where label and input are 16px
apart and input and next label are also 16px apart looks like an undifferentiated
list, not a structured form.

**Distance signals separation**: The gap between sections, between components,
between structural elements is a semantic signal. Larger gaps mean "these are
separate topics." If everything has the same gap, nothing is grouped — everything
is equally related to everything else, which means nothing is.

**Alignment signals order**: Elements that share an alignment axis belong to
the same visual group. Left-aligned text creates a reading axis. Misaligned
elements break the flow and the implied grouping.

---

## The 8px Base Unit System

All spacing in a well-designed UI system is a multiple of 4px or 8px. This is
not arbitrary — it is derived from baseline grid theory (see `gd-grid-and-layout`)
and creates visual harmony through a shared increment.

### Why This Works

- **Visual harmony**: When all spacing is a multiple of the same unit, the eye
  perceives rhythm even if it cannot consciously identify the unit
- **Predictable relationships**: 8px, 16px, 24px, 32px form a progression where
  each step has a clear semantic size difference
- **Pixel-perfect at standard and 2x density**: At 1x, every 4px increment falls
  on a pixel boundary. At 2x, every 2px increment does. No sub-pixel rounding.

### Standard Scale

```
4px   — micro: icon internal padding, tight chip gaps
8px   — xs: element internal padding (tight), icon-to-label gaps
12px  — sm: element internal padding (default), grouped field gaps
16px  — md: component padding, section element gaps
24px  — lg: component-to-component gaps, card padding
32px  — xl: section separations within a page
48px  — 2xl: major section breaks
64px  — 3xl: page-level structural divisions
```

The scale names should be semantic, not numeric. `gap-lg` communicates intent;
`gap-24` does not. But the underlying values must be multiples of 4px.

### Failure Mode: Breaking the Grid Accidentally

Common sources of off-grid spacing:
- Default browser styles (margins, paddings on headings, paragraphs)
- "It looks better at 14px" decisions made without checking the grid impact
- Icon sizes that aren't 4px-divisible (17px icon requires -1.5px compensation)

**Fix**: Reset browser defaults explicitly. Choose icon sizes from the 4px grid
(16px, 20px, 24px, 32px). When an optical correction is needed, apply it at the
4px level (add 4px padding rather than shifting by 3px).

---

## Optical vs. Mathematical Spacing

Equal mathematical gaps don't always look equal. The eye has systematic biases
that must be accounted for.

### Top-Heavy Bias

Text sits in its bounding box with optical weight toward the bottom. A container
where top and bottom padding are mathematically equal will look like the text
sinks. Fix: add slightly more bottom padding, or use the visual center rather
than the mathematical center.

**Rule**: For buttons, tags, chips, and other text-in-container elements:
- If padding is `12px top / 12px bottom`, increase bottom to `14px` for optical centering
- OR use `padding-top: 11px; padding-bottom: 13px` for a 24px visual height

This is subtle but perceptible — especially in navigation, where a row of
buttons with sinking text looks amateurish.

### Shape Affects Weight Perception

- **Circles** appear smaller than squares of the same bounding box size —
  because the corners of the square add visual mass that the circle lacks
- **Tall rectangles** (portrait icons) feel narrower than wide rectangles of
  the same area
- **Dense content** (icon with many internal lines) appears heavier than sparse
  content (simple arrow icon) at the same size

**Implication**: Icon padding must account for shape. A circular icon at 24px
needs slightly more surrounding padding than a square icon at 24px to feel the
same visual weight in a row of mixed icons.

### Counter Optical Centering

For elements that must be visually centered (not mathematically): optical center
is slightly above the mathematical center. This is because the eye reads the
lower visual field as heavier.

In practice: when centering an icon inside a container, the icon placed at true
mathematical center will look slightly below center. Move it up by 1–2px.

---

## Negative Space in UI

White space is not wasted space. It is an active compositional element.

### Generous Spacing Signals Quality

Products with tight spacing signal "we don't have room for everything we want
to say" — even when that's not the intent. Generous spacing signals "we're
confident in this content, and we're giving it room to breathe."

In enterprise UI, there's pressure to maximize information density. But there's
a difference between **purposeful density** (data that needs to be dense) and
**incidental density** (everything crammed because no one made space decisions
explicitly).

**Decision framework**:
- Data tables, lists, select menus → density is functional; use tighter spacing
- Cards, panels, forms, settings → generous spacing signals quality
- Navigation, toolbars, headers → compact but not cramped

### Micro White Space vs. Macro White Space

**Micro white space**: Space between letters, lines, list items, form fields.
Controls readability and scanning within a component.

**Macro white space**: Space between sections, between components, page margins.
Controls structure and section separation.

Both need intentional control. Products that attend to one but not the other
feel "almost right but something's off."

---

## Visual Weight Distribution in UI Layouts

Heavy elements — large, dark, saturated, complex — draw the eye first. This is
not a preference; it is a perceptual fact. Use it intentionally.

### Creating Intentional Hierarchy

1. **Identify the most important element** on the screen. This element should
   have the highest visual weight — larger size, heavier type weight, or accent
   color. Everything else should have less.

2. **One primary focal point per screen** (with exceptions for dashboards with
   explicit multi-column design intent). If two elements compete equally for
   attention, neither is primary — hierarchy is broken.

3. **Secondary and tertiary elements should have visually subordinate weight**:
   lighter color, smaller size, less visual complexity.

**Blur test**: Squint at the screen. The first thing that resolves should be the
primary element. If a navigation bar, a decorative illustration, or a status
badge resolves first — the hierarchy is wrong.

### Visual Weight Offenders in Enterprise UI

- **Navigation sidebars** that are visually heavier than the content area. Fix:
  lower contrast background, lighter text weights.
- **Toolbar buttons** that compete visually with content. Fix: low-emphasis
  icon buttons (no fill, lower contrast) vs. primary action button (high emphasis).
- **Empty state illustrations** that are the most visually interesting thing on
  the screen. Fine when the screen is empty; ensure they don't compete when
  content is present.

---

## Compositional Hierarchy

Every screen should have three legible zones readable in the first 5 seconds.

### Zone Structure

| Zone | Visual Characteristics | Typical Content |
|---|---|---|
| **Primary** | Highest contrast, largest size, most visual weight | The main action or key information |
| **Secondary** | Medium contrast, standard size | Supporting context, secondary actions |
| **Tertiary** | Low contrast, small size | Metadata, timestamps, helper text, tertiary actions |

If a screen has two primary zones competing, neither is primary. Reconsider which
truly needs maximum emphasis, and subordinate the other.

### Compositional Patterns for Enterprise

**F-pattern reading**: Content-dense pages are scanned in an F-pattern
(left to right on the first row, shorter scan on the second, then down the left
edge). Place critical information on the first row and left edge.

**Z-pattern reading**: Simple layouts with few elements are read in a Z-pattern
(top-left → top-right → diagonal → bottom-left → bottom-right). Use for
landing pages, empty states, simple forms.

**Dashboard grids**: Don't apply F or Z patterns — dashboards require the user
to orient themselves. Strong visual hierarchy in card headers, consistent card
structures, and clear section labels matter more than positional reading patterns.

---

## Responsive Layout Logic

### Content-Aware vs. Container-Aware Reflow

**Content-aware reflow**: Layout adapts based on the content's natural breakpoints.
A three-column layout that doesn't have enough content to justify three columns
at narrow widths drops to two, then one.

**Container-aware reflow**: Components respond to their container, not the
viewport. A card in a 400px container behaves differently than the same card in
an 800px container. CSS container queries (`@container`) enable this.

**Enterprise implication**: Sidebar layouts and split-panel designs require
container-aware thinking — the content column width is not the viewport width.

### Adapting Compositions Across Breakpoints

**Rule**: At each breakpoint, re-evaluate the hierarchy, not just the dimensions.
Shrinking a 3-column desktop layout to a 1-column mobile layout is not
"responsive design" — it's resizing. Responsive design asks: what's most
important at this size? What can be hidden or deferred?

- **Desktop**: Full layout with secondary and tertiary zones visible
- **Tablet**: Primary and secondary zones; tertiary collapses to progressive disclosure
- **Mobile**: Primary zone dominant; secondary accessible; tertiary on-demand

---

## Z-Axis and Layering

In a 2D interface, depth is implied through overlap, shadow, and blur.
The z-axis is a design system, not an incidental technical detail.

### The Implied Layer Stack

Every surface in a UI should belong to one of these conceptual layers:

1. **Base**: The application background surface. Lowest level.
2. **Content**: Cards, panels, content areas. "On" the base.
3. **Raised**: Sticky headers, action bars — elevated above content but part of the layout.
4. **Overlay**: Popovers, tooltips, dropdowns — floating above the layout.
5. **Modal**: Dialogs, slideovers, drawers — consuming the full context.
6. **Toast**: Notifications, global status — above everything, temporary.

Each layer should have a defined shadow/surface treatment. See `uid-surface-depth`
for the full elevation design system.

**Failure mode**: Ad-hoc z-index values (999, 9999, 99999) that signal no
intentional layering model was designed. The result: z-index conflicts, elements
appearing under the wrong surface.

---

## Density Design in Enterprise

Enterprise UIs must balance two competing needs:
- Enough density to display the data users need without excessive scrolling
- Enough breathing room to support scanability and reduce cognitive load

### Density Tiers

| Tier | Spacing | Use case |
|---|---|---|
| **Comfortable** | Standard scale (16px padding, 8px gaps) | Settings, forms, onboarding |
| **Default** | Slightly compressed (12px padding, 6–8px gaps) | Standard data tables, lists |
| **Compact** | Tight (8px padding, 4px gaps) | Power-user data views, log tables |
| **Ultra-dense** | Minimal (4px padding, 2–4px gaps) | Terminal-like interfaces, raw data grids |

User-controllable density (a density toggle: comfortable/default/compact) is a
high-value feature for enterprise and requires spacing tokens to be designed
as a density system, not individual values.

---

## Failure Modes Summary

| Failure Mode | Description | Fix |
|---|---|---|
| Uniform spacing everywhere | Everything has the same gap; no visual grouping | Vary gaps semantically: tight within groups, generous between groups |
| Off-grid spacing | Pixel values that break the 4px grid | Audit for non-grid values; correct or document exceptions |
| Mathematical vs. optical centering | Centered-by-numbers that looks sunk | Add optical correction: more bottom padding, icon shifted up 1–2px |
| Competing primary elements | Two elements both demand first attention | Choose one primary; reduce the other's visual weight |
| Decoration as density | Unnecessary visual elements adding "richness" | Ask: does this element carry information? Remove if not |
| No responsive hierarchy decision | Shrinking desktop to mobile rather than re-prioritizing | At each breakpoint, re-evaluate hierarchy, not just dimensions |
| Ad-hoc z-index | z-index: 9999 everywhere | Define a named layer stack; assign semantic z-index values |

---

## Cross-Links

- `gd-grid-and-layout` — foundational grid theory: baseline grids, modular grids, Swiss layout
- `ds-advisor` — spatial decisions become spacing tokens; the spatial system IS the spacing token system
- `uid-surface-depth` — z-axis and elevation design
- `uid-visual-critique` — blur test and hierarchy evaluation frameworks
- `lead-ux-designer` / `ux-interaction-design` — interactive layout patterns (tabs, drawers, accordions)
- `uid-visual-system` — spacing as part of the complete visual language
