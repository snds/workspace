---
name: lead-icon-artist
description: >
  Icon and symbol design language, visual semantics, and optical correctness.
  Use this skill whenever the conversation touches: icon metaphor selection,
  visual semiotics, icon grid and keyline systems, optical correction (overshoot,
  weight compensation, counter balancing), pixel-fitting and hinting strategy,
  designing for variable axes (how FILL/wght/opsz affect design decisions), icon
  legibility at small sizes, stylistic consistency across an icon set, Material
  Design icon principles, icon naming taxonomy, icon briefs/specifications, visual
  weight balancing, negative space in icons, perspective and dimensionality
  conventions, or any question about *what to draw and why*. This skill covers
  icon design intent — not path construction craft (lead-vector-designer) or
  pipeline engineering (lead-technical-digital-artist).
aliases: [lead-icon-artist]
tier: hub
domain: design
spec_version: "2.0"
---

# Lead Icon Artist

Specialist lens for icon design language, visual semantics, and optical
correctness. Part of the precision vector & parametric design skill network.

---

## Domain Boundary

This skill owns **icon design decisions** — what to draw, why, and how design
choices support legibility, consistency, and the variable axis model.

- **How to construct paths** → `lead-vector-designer`
- **How to compile into fonts** → `lead-technical-digital-artist`
- **Interpolation mechanics & axis specs** → `variable-icon-font-architect` (hub)

---

## Core Competencies

### Icon Grid & Keyline System

#### Project-Specific: The 24×24 Grid (CentricSymbols Default)

The grid defines the icon's live area and alignment structure:

- **Canvas**: 24×24 units
- **Live area**: 20×20 units (2-unit padding on all sides)
- **Trim area**: The 2-unit border serves as optical breathing room — no primary
  geometry should touch or cross this boundary
- **Optical center**: Slightly above geometric center (≈11.5 from top, not 12) —
  icons optically centered feel more balanced

#### Keyline Shapes

Keyline shapes normalize visual weight across icons with different geometries:

| Shape | Dimensions | Use When |
|-------|-----------|----------|
| Square | 18×18 | Blocky, rectangular subjects (settings, grid, card) |
| Circle | 20×20 | Circular subjects (account, globe, radio button) |
| Tall rectangle | 16×20 | Vertically oriented subjects (document, phone, person) |
| Wide rectangle | 20×16 | Horizontally oriented subjects (landscape, video, mail) |

The keyline is a guide, not a cage — organic shapes may extend slightly beyond
if optical balance requires it.

### Optical Corrections

#### Overshoot

Round and pointed shapes must extend slightly beyond the geometric boundary
to appear the same size as flat-edged shapes:

- Circles overshoot by ~0.5–1 unit beyond the keyline edge
- Pointed vertices (triangles, arrows) overshoot by ~1 unit
- Without overshoot, circles appear smaller than squares at the same dimension

#### Weight Compensation

- Horizontal strokes appear heavier than vertical strokes at the same thickness
  (physiological bias) — compensate by making horizontals ~2–5% thinner
- Diagonal strokes at 45° appear thinner — compensate by making them ~5–8%
  thicker than horizontals
- These compensations are subtle and may be handled at the variable axis level
  rather than per-icon

#### Counter Balancing

Enclosed negative spaces (counters) must be large enough to remain legible at
the smallest optical size:

- At `opsz=20`, counters should be ≥2 grid units wide
- At `opsz=24`, counters can be ≥1.5 grid units
- If a counter would collapse below minimum at small sizes, the `opsz=20`
  master should simplify the geometry (fewer details, wider counters)

### Designing for Variable Axes

Each axis imposes design constraints that must be considered at the sketching
stage, not as an afterthought.

#### FILL Axis Design Decisions

The outlined (FILL=0) and filled (FILL=1) states must be **visually
equivalent** — the same metaphor, the same recognizability, the same visual
weight center.

| Decision | FILL=0 (Outlined) | FILL=1 (Filled) |
|----------|-------------------|-----------------|
| Primary shape | Stroke defines silhouette | Solid mass defines silhouette |
| Internal detail | Visible as counter shapes | May merge into solid or become cutouts |
| Visual weight | Lighter, more refined | Heavier, more assertive |
| Recognition | Relies on outline + counter | Relies on silhouette alone |

**Design test**: Can the user identify the icon from its FILL=1 silhouette
alone? If not, the metaphor depends too heavily on internal detail and needs
rethinking.

#### wght Axis Design Decisions

- Thin weights (100–300): stroke-dominant, minimal visual mass, counters open
- Regular weights (400): balanced, the "canonical" design
- Bold weights (500–700): mass-dominant, counters may narrow but must stay open

**Key constraint**: The icon's metaphor and recognizability must be preserved
across the full weight range. If a detail disappears at thin weight, it's not
essential — consider removing it at all weights for consistency.

#### opsz Axis Design Decisions

Optical size is about **legibility at rendered size**, not aesthetic preference:

| opsz Value | Rendered At | Design Strategy |
|-----------|------------|-----------------|
| 20 | Small (badges, status) | Simplify geometry, widen counters, thicken strokes, remove fine detail |
| 24 | Default (toolbar, nav) | Full detail, balanced proportions |
| 40 | Large (empty states) | Can add fine detail, thinner strokes relative to size |
| 48 | Display (hero, onboard) | Maximum detail, finest possible strokes |

**opsz=20 test**: Print the icon at 20px on screen. Can you identify it
instantly? If you squint or hesitate, simplify further.

### Visual Semantics & Metaphor

#### Metaphor Selection Principles

1. **Universal over cultural**: Prefer metaphors that work globally (gear for
   settings, not a wrench — wrench implies repair, not configuration)
2. **Concrete over abstract**: A physical object (envelope for mail) reads
   faster than an abstract symbol
3. **Established conventions first**: Don't reinvent when a strong convention
   exists (magnifying glass for search, house for home)
4. **PLM-domain specificity**: CentricSymbols serves fashion, food, and product
   verticals — some metaphors need domain-specific variants (fabric swatch,
   recipe, BOM hierarchy)

#### Metaphor Consistency Rules

- **Single perspective**: All icons in the set use the same viewing angle
  (typically front-facing or slight top-down for objects with depth)
- **Consistent dimensionality**: Either all flat (2D silhouette) or all with
  consistent implied depth — don't mix
- **Consistent detail level**: If "document" shows two lines of text, all
  document-type icons show the same text treatment
- **Action vs. object**: Use consistent patterns for action icons (verb) vs.
  object icons (noun) — e.g., actions often have motion indicators (arrows,
  lines)

### Icon Naming Taxonomy

Consistent naming supports the GSUB ligature system and developer experience:

#### Naming Convention

```
[category]_[object]_[modifier]
```

Examples:
- `file_document` (base object)
- `file_document_add` (action modifier)
- `file_document_error` (state modifier)
- `navigation_arrow_back` (category + object + direction)

#### Project-Specific: Category Prefixes (CentricSymbols)

| Prefix | Domain |
|--------|--------|
| `file_` | Documents, attachments, media |
| `navigation_` | Arrows, menus, pagination |
| `action_` | CRUD operations, workflow actions |
| `status_` | States, alerts, indicators |
| `content_` | Data display, formatting |
| `plm_` | Domain-specific PLM concepts |
| `comm_` | Communication, collaboration |

### Visual Weight Balancing

Within a set, all icons should feel like they belong together at the same
visual "loudness":

#### Weight Audit Method

1. Blur the entire icon set at 4px gaussian blur
2. Each icon should reduce to a roughly similar gray value
3. Icons that appear significantly darker or lighter need rebalancing
4. Common offenders: solid fills vs. stroked outlines, dense vs. sparse geometry

#### Density Balancing

- Icons with more internal detail (circuit board, calendar) appear heavier
  than sparse ones (circle, arrow)
- Compensate by using thinner strokes on dense icons or reducing detail count
- The `wght` axis should not be used to fix density imbalance — it's a global
  control, not per-icon

### Pixel-Fitting Strategy

At small sizes (opsz=20, rendered at 20px), sub-pixel rendering causes blur:

#### Rules

- At opsz=20: all horizontal and vertical strokes should align to whole pixel
  boundaries
- Diagonal and curved strokes can't pixel-fit perfectly — rely on stroke
  thickness (≥2px at rendered size) for legibility
- Test at 1x (no retina) — pixel-fitting matters most on standard displays
- At opsz=24+: pixel-fitting is less critical due to larger rendered size and
  prevalence of retina displays

---

## Icon Design Brief Format

When specifying a new icon, provide:

```markdown
### Icon: [name]

**Metaphor**: [physical object or concept being represented]
**Category**: [taxonomy prefix]
**Use context**: [where in the PLM UI this appears]

**FILL behavior**:
- FILL=0: [what the outlined version looks like]
- FILL=1: [what fills, what becomes a cutout]

**opsz=20 simplification**:
- [what details get removed or widened]

**Related icons**: [other icons this should visually harmonize with]
**Avoid**: [common misinterpretations or too-similar existing icons]
```

---

## Quality Checklist

Before approving any icon design for vector construction:

- [ ] Metaphor is clear and unambiguous at a glance
- [ ] Silhouette (FILL=1) is recognizable without internal detail
- [ ] Fits within appropriate keyline shape
- [ ] Optical corrections applied (overshoot, weight compensation)
- [ ] Counters are large enough for opsz=20 legibility
- [ ] Visual weight is balanced relative to the rest of the set
- [ ] Consistent perspective and dimensionality with set
- [ ] Name follows taxonomy convention
- [ ] FILL=0 → FILL=1 transition is designed (not an afterthought)
- [ ] opsz=20 simplification is specified
- [ ] No cultural bias in metaphor selection


---

## Visual QA Cross-Link

When an icon or icon set reaches a review-ready state, route to `lead-visual-qa`
for a final visual quality pass. This skill is a natural upstream producer of
output that `lead-visual-qa` is designed to evaluate.

Relevant spoke for icon output:
- **`visual-qa-graphic-design`**: Iconography sub-specialty — visual weight
  consistency across the set, blur test, optical size correctness, metaphor
  clarity, stroke language uniformity
- **`visual-qa-ui-design`**: Icon-in-UI context — sizing relative to text,
  optical cap-height alignment, touch target compliance, interactive state coverage

Trigger automatically when declaring an icon or set ready for production.

---

## Design-Forward Operating Directive

This skill is the aesthetic center of gravity for the entire icon font system.
Every other spoke — vector construction, pipeline engineering, all four math
skills — exists to serve the design decisions made here.

### Principles

1. **The eye is the final validator.** Mathematical models of overshoot,
   weight perception, and counter legibility are powerful tools — but they
   are approximations of human perception, not replacements for it. Use
   `math-optical-optimization` to generate starting values and quantitative
   baselines, then refine by visual judgment.

2. **Consistency is a design system property.** A single icon can be beautiful
   and still fail if it doesn't harmonize with the set. Visual weight audits,
   keyline adherence, and metaphor consistency are system-level design
   concerns that override individual icon aesthetics when they conflict.

3. **Design for the axis range, not the default.** Every icon exists across a
   4-dimensional space (wght × FILL × GRAD × opsz). A design that looks
   perfect at the default but breaks at thin weight or small optical size is
   incomplete. Route to `math-interpolation-designspace` to understand how
   design choices propagate across the designspace — then make choices that
   hold up everywhere, not just at the origin.

4. **Structural elegance reduces downstream problems.** A well-conceived icon
   with clear silhouette, deliberate counter proportions, and intentional
   FILL behavior will survive vector construction, pipeline processing, and
   interpolation with fewer artifacts than one that was sketched loosely and
   "fixed" later. Invest design effort early.

5. **Articulate visual intent with precision.** When specifying an icon, use
   the design brief format to make implicit decisions explicit. "It should
   look like a gear" is insufficient — "8-tooth spur gear, front-facing, with
   circular center counter sized for opsz=20 legibility, FILL=1 as solid
   silhouette with counter preserved as cutout" gives downstream skills the
   clarity they need.
