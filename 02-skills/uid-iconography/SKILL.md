---
name: uid-iconography
description: >
  Visual language for icons in a design system context — style definition, style
  coherence, metaphor and symbol design, icon size and context, color in icons,
  and icon as communication. Use this skill when the conversation touches: defining
  or auditing an icon set's visual language, icon style parameters (stroke weight,
  corner radius, fill vs. outline), metaphor selection for abstract concepts,
  failed icon metaphors, icon style consistency across a set, icon size system
  and how style adapts across sizes, color in icons (monochrome vs. duotone vs.
  multicolor), when icons need labels, or icon readability tests. This spoke covers
  the design side of iconography. Deep icon construction and keyline math live in
  lead-icon-artist. Part of the lead-ui-designer hub skill network.
aliases: [uid-iconography]
tier: spoke
domain: design
hub: lead-ui-designer
prerequisites: [lead-ui-designer]
spec_version: "2.0"
---

# UID: Iconography

Specialist spoke for icon visual language in design system contexts.
Part of the `lead-ui-designer` hub skill network.

---

## Domain Boundary

This spoke owns **iconography as visual language**: the design decisions that
define what an icon set looks like and how it communicates in a product.

- **Deep icon construction, keyline grids, optical corrections, variable axes** → `lead-icon-artist`
- **Variable icon font construction and pipeline** → `variable-icon-font-architect`
- **Path construction and bezier craft** → `lead-vector-designer`
- **Accessible icon communication (text alternatives, ARIA)** → `lead-accessibility-architect` / `a11y-visual`

---

## Icon Style Definition

An icon set has a visual style defined by a set of parameters. These parameters
must be made explicit and applied consistently. Implicit style = no style, because
different designers will infer different rules.

### Core Style Parameters

**Stroke Weight**
The width of strokes in outlined icons. Defined in absolute units relative to
the icon's canvas size.

- Light (1.5px at 24px canvas): delicate, refined; thin feels sophisticated
  but fragile at small sizes
- Regular (2px at 24px canvas): most common; balances legibility and refinement
- Medium (2.5px): more presence; appropriate for bold brand personalities
- Heavy (3px+): assertive; matches bold type weights; often looks cartoonish

**Rule**: Stroke weight should match the type weight in the product. An icon
next to 400-weight body text should have strokes that read the same visual weight.
Pairing thin icons with bold type, or vice versa, creates visual tension.

**Corner Radius on Icon Strokes**
The roundness of sharp corners within icons.

- 0 (sharp): precise, technical, formal
- 0.5–1px: minimal softening
- 1–2px: standard rounded; most modern UI icon sets
- 2–3px+: friendly, rounded; more consumer-facing personality

**Rule**: Corner radius must match the product's corner radius personality. An
icon with round corners in a product with sharp `border-radius: 0` components
creates a style conflict.

**Fill vs. Outline Convention**
- **Outline (default active state)**: Standard resting state for most icon sets
- **Fill (alternate, interactive state)**: Often used for active/selected states
  (bottom navigation active tab, selected bookmark)
- **Mixed**: Some sets use fill for object icons and outline for action icons —
  this can work if the rule is explicit

If the product has a design system with variable icons (see `variable-icon-font-architect`
for FILL axis), the outline/fill distinction is an axis rather than a style choice.

**Level of Abstraction**
How simplified or detailed are the icons relative to their real-world referents?

- **High abstraction**: Geometric reduction — the icon reads as a symbol, not a
  picture. Fast to read. Hard to get wrong. Loses nuance.
- **Medium abstraction**: Recognizable object with characteristic features
  preserved. The "just right" zone for most enterprise UI.
- **Low abstraction / illustrative**: Detailed, dimensional, expressive. More
  visual interest but requires more space and attention. Appropriate for empty
  states and onboarding, not toolbar icons.

**Rule**: An icon set must use a consistent level of abstraction. A set where
some icons are geometric symbols and others are detailed illustrations feels
incoherent — like two different designers made them.

---

## Visual Weight Consistency

Icons of different shapes must be optically weighted to appear the same visual
size and loudness. This is non-obvious because a star, a circle, and a rectangle
at the same pixel dimensions do not have equal perceived visual weight.

### The Keyline System

Keyline shapes define maximum fill extents for different icon geometries,
compensating for their different intrinsic visual weights. See `lead-icon-artist`
for full keyline grid specifications.

**For visual language assessment (not construction)**:
- A circle icon feels lighter than a square icon at the same size — compensate
  by allowing the circle to extend to a slightly larger bounding area
- A dense icon (many internal lines, like a spreadsheet icon) will feel heavier
  than a sparse icon (a simple arrow) — compensate by using thinner strokes on
  dense icons

### Visual Weight Audit Method

1. Select 20–30 icons from across the set
2. Display them in a uniform grid at the same size on a neutral background
3. Blur the grid at 4px gaussian
4. Each icon should reduce to approximately the same gray value
5. Icons that resolve significantly darker or lighter are weight outliers

This is the blur test applied to iconography. It surfaces weight imbalances that
are difficult to see when evaluating icons individually.

**Common weight outliers**:
- All-filled solid icons adjacent to mostly-outlined icons
- Icons with very wide strokes next to ones with thin strokes
- Icons with large filled areas (circle, diamond) next to ones with open geometry (arrow, bracket)

---

## Metaphor and Symbol Design

### Choosing the Right Metaphor

**Prefer established conventions first**: The magnifying glass = search. The
gear = settings. The house = home. The envelope = email. These are learned
conventions with years of reinforcement. Avoid reinventing them — users must
learn a new symbol with no benefit.

**When no convention exists**: For abstract concepts or domain-specific ideas
without a UI metaphor, choose based on:
1. **Concreteness**: Physical objects read faster than abstract symbols
2. **Universality**: Avoid metaphors that are culturally specific or regionally variable
3. **Distinctiveness**: The icon must be distinguishable from nearby icons in the set
4. **Silhouette strength**: At small sizes and in the FILL=1 state, can you identify
   the icon from its silhouette alone?

**Failed metaphors (and how to handle them)**:
- The floppy disk = save: Nobody under 30 has used one, but it's so established
  that replacing it causes confusion. Keep it — it's a symbol, not a picture.
- The phone handset = call: Similarly archaic but universally understood. Keep it.
- The house = home: Works only in products where "home" is a meaningful destination.
  In a single-page app with no "home" concept, this is confusing.

**Rule for failed metaphors**: If the convention is universally understood even
though it's outdated, preserve it. If the convention is genuinely ambiguous or
culturally limited, design a better one and test it.

### Metaphor Consistency Rules

- **Single perspective**: Every icon in the set uses the same viewing angle. Most
  modern icon sets use front-facing or slight top-down. Do not mix perspectives.
- **Consistent dimensionality**: Either entirely flat (2D silhouette) or consistently
  implying one level of depth. Do not mix flat icons with isometric icons.
- **Consistent detail level**: If "document" shows two line representations,
  all document-like icons show the same text treatment. Don't render "document"
  in detail and "spreadsheet" as a flat rectangle.
- **Action vs. object consistency**: Action icons (verbs: download, add, delete)
  should have visual treatments that distinguish them from object icons (nouns:
  document, user, calendar). Arrows, motion lines, and modifier symbols (plus,
  minus, checkmark) are common action indicators.

---

## Icon Size and Context

Icons aren't designed once — they're designed for a size range. Style adapts
across sizes, and the production process for a variable icon font encodes this
formally. For non-variable icon systems, the adaptation must be done manually.

### Size System

| Size | Context | Notes |
|---|---|---|
| **16px** | Dense data tables, tight navigation, inline badges | Smallest practical size; 2px strokes become 0.125× size; needs pixel-fitting |
| **20px** | Compact component sizes, secondary actions, dense toolbars | Common default in compact enterprise UIs |
| **24px** | Standard default — toolbars, navigation, primary actions | The design reference size for most icon sets |
| **32px** | Large action areas, settings section headers | More space for detail; still functional |
| **48px** | Empty states, feature callouts, touch targets | Can include more detail; more expressive |
| **64px+** | Illustrations, onboarding, hero contexts | Full illustrative treatment; may need dedicated assets |

### How Style Adapts Across Sizes

At smaller sizes, icons must:
- **Thicken strokes** (proportionally) so they remain visible
- **Widen counters** (interior spaces) so they don't fill in
- **Simplify geometry** — details that read at 24px become noise at 16px
- **Align to whole pixel boundaries** — sub-pixel strokes blur at 1x density

At larger sizes, icons can:
- **Add finer detail** that would be invisible at small sizes
- **Thin strokes** proportionally without losing legibility
- **Add expressiveness** — slight perspective, dimensional hints, refined geometry

**For variable icon systems**: These adaptations are encoded in the `opsz` axis.
See `lead-icon-artist` for detailed opsz design decisions.

---

## Color in Icons

### Monochrome (Recommended Default)

A single color, inheriting from the text or UI context. Expressed in CSS as
`currentColor`.

**When**: Almost always. Monochrome icons are:
- Flexible: they work on any background by inheriting the surface's text color
- Accessible: contrast is guaranteed by the same rules as text
- Themeable: they adapt to dark/light mode automatically
- Consistent: no per-icon color decisions needed

**Design implication**: Monochrome icons must communicate entirely through shape.
If the icon's meaning depends on a second color to distinguish parts, it will
not work as monochrome.

### Duotone

Two colors — typically a primary icon color and a secondary tint (often at
lower opacity or a complementary hue).

**When**: Feature icons, empty state illustrations, marketing-oriented contexts.
Not for functional toolbar icons. Requires explicit token mapping for both colors.

**Accessibility concern**: The secondary color must still meet contrast requirements
against its background. Don't assume a light tint is "decorative" — if it carries
meaning, it needs sufficient contrast.

### Multicolor

Full color, using multiple named colors per icon.

**When**: Only for product logos, brand identifiers, or illustrative contexts.
Never for functional UI icons (navigation, actions, form controls). Multicolor
icons don't adapt to themes, dark mode, or high-contrast modes.

---

## Icon as Communication

### The Readability Test

Show the icon to someone unfamiliar with the product. Can they identify what it
represents in 5 seconds without a label?

- If yes: the metaphor works. The icon can stand alone in contexts with enough
  surrounding context (toolbar with tab labels, for example).
- If no: the icon needs a label, or the metaphor needs to be replaced.

Many icons that designers assume are "universal" are not. The only way to know
is to test with actual users.

### Label Pairing Rules

**Always pair icons with labels when**:
- The action is infrequent or unfamiliar to the user
- The icon represents a complex domain concept
- The interface is being used for the first time (onboarding contexts)
- Errors or destructive actions are involved — never rely on an icon alone for
  actions that can't be undone

**Icons can stand alone (with tooltip fallback) when**:
- The icon follows a universal convention (search, close, menu)
- The context makes the meaning unambiguous (a plus in a "create new" area)
- The icon has been proven readable via user testing
- A tooltip is available on hover

**In enterprise UI**: Prefer labeled icons over bare icons in primary navigation.
The overhead of a label is trivial compared to the cognitive load of a toolbar
of unlabeled symbols. Toolbars that rely entirely on icon literacy are a support
burden, not a design achievement.

---

## Failure Modes Summary

| Failure Mode | Description | Fix |
|---|---|---|
| Inconsistent stroke weights | Mix of 1.5px, 2px, 2.5px strokes without a rule | Define one canonical stroke weight; audit the full set |
| Inconsistent corner radii | Sharp corners next to rounded corners without intent | Match icon corner radius to product border-radius personality |
| Mixed abstraction levels | Geometric symbols next to illustrative icons | Agree on one abstraction level; redesign outliers |
| Weight imbalance | Dense icons appear louder than sparse icons | Blur test the full set; compensate with stroke adjustments |
| Metaphor ambiguity | Icon meaning depends on label to be understood | Replace metaphor or redesign with stronger silhouette |
| Unlabeled action icons | Destructive actions (delete, remove) without labels | Always pair destructive and infrequent actions with labels |
| Multicolor functional icons | Traffic light colors in toolbar icons | Convert to monochrome; use semantic color with shape + label |
| Wrong size variant | 24px icon at 16px without adaptation | Design or source a 16px-optimized variant |

---

## Cross-Links

- `lead-icon-artist` — deep icon design language: keyline grids, optical corrections, variable axis design decisions
- `variable-icon-font-architect` — variable icon font construction and FILL/wght/opsz axis mechanics
- `gd-image-composition` — compositional principles applied to icon design
- `lead-accessibility-architect` / `a11y-visual` — accessible icon communication, ARIA, minimum touch targets
- `uid-visual-system` — icon style as part of the complete visual language
- `uid-visual-critique` — icon set audits using blur test and weight consistency evaluation

## Related
- hub → [[lead-ui-designer]]
