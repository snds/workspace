# Visual foundations for design-system work

_Moved word for word from `ds-advisor/SKILL.md` on 2026-10-22 when `ds-advisor` became a spoke
of `ds`. Most of this is owned by [[design-foundations]] and its `found-*` spokes, which load
first in every design chain; read this file only for the design-system-specific notes
(proportional systems, grids to tokens, colour for systems)._

## Foundational Design Principles

These principles are foundational to all visual design work — components, layouts, documentation,
dashboards, and any artifact with a visual dimension. They inform every decision from token
architecture to component anatomy to page composition.

### Gestalt Principles
- **Proximity**: Elements near each other are perceived as related. Spacing tokens exist to
  encode these relationships — tight spacing for grouped elements, wider spacing for separation.
  Every gap in a layout communicates a relationship.
- **Similarity**: Elements that share visual properties (color, size, shape, weight) are perceived
  as belonging together. Consistency in token application reinforces this — all body text at the
  same size, all interactive elements the same accent color.
- **Continuity**: The eye follows smooth lines and curves. Alignment grids, baseline grids, and
  consistent margins create visual flow. Misalignment breaks continuity and signals disorder.
- **Closure**: The mind completes incomplete shapes. Cards, containers, and bounded regions
  don't need heavy borders if spacing and fill create clear boundaries.
- **Figure/Ground**: Every element exists in relationship to its background. Contrast ratios,
  elevation (shadow), and surface hierarchy (primary/secondary/tertiary) all serve this principle.

### Typography Fundamentals
- **Hierarchy is structural, not decorative.** Type scale steps exist to create information
  hierarchy — display → headline → title → body → caption. Each step serves a functional role.
- **Measure (line length)** affects readability. 45–75 characters per line for body text.
  Narrower for captions, wider acceptable for headlines.
- **Leading (line height)** creates breathing room. Tighter for large display text, more generous
  for small body text. The type scale should encode this automatically.
- **Tracking (letter spacing)** is functional, not ornamental. Wide tracking for small uppercase
  labels (legibility), tight tracking for large display text (optical correction), zero for
  monospace (fixed-width alignment).
- **Weight carries meaning.** Bold for emphasis, medium for labels, regular for body. Don't use
  weight for decoration — use it to signal importance.

### Layout & Composition
- **Grid systems** provide structure. The base unit (4px, 8px) and its multiples create a
  rhythmic scaffold that all elements align to. Breaking the grid should be intentional, not
  accidental.
- **White space is not empty.** It's a design element that creates hierarchy, focus, and
  breathing room. Dense layouts are harder to scan. Generous space communicates confidence
  and clarity.
- **Visual weight distribution** matters. Large, dark, or saturated elements carry more weight.
  Balance the composition — a heavy header needs proportional content below it.
- **Alignment creates order.** Left-aligned text, consistent margins, aligned edges — these
  create the invisible grid that makes a layout feel structured. Misaligned elements create
  visual noise.
- **Responsive thinking**: Every layout should consider how it scales. Auto-layout, proportional
  sizing, and token-driven dimensions ensure layouts adapt to content and context changes.

### Color & Contrast
- **Contrast is functional.** APCA and WCAG aren't just compliance checkboxes — they encode
  the minimum perceptual difference needed for content to be readable. Low contrast = invisible
  content.
- **Color hierarchy** mirrors information hierarchy. Primary text on primary surface. Secondary
  text for supporting info. Tertiary for annotations. The palette should make hierarchy obvious.
- **Semantic color** communicates status. Success, warning, error, info — these are not arbitrary
  choices. They're conventions that users have learned.

### Print Design Influence
- **The typographic scale** comes from centuries of print. Modular scales (1.25, 1.333, 1.5)
  create harmonious size progressions because they encode mathematical relationships the eye
  perceives as balanced.
- **Baseline grids** ensure vertical rhythm. Text elements that share a common baseline create
  visual harmony across columns and sections.
- **Margins and bleeds** in print translate to padding and safe areas in digital. Content needs
  breathing room from container edges.
- **Hierarchy through scale, weight, and position** — print designers mastered this long before
  screens existed. The largest, boldest element at the top draws the eye first. Secondary
  information is smaller, lighter, lower. This cascade is universal.

### Visual Ratios & Proportional Systems
- **The Golden Ratio (φ ≈ 1.618)** creates naturally pleasing proportions. It appears in
  card aspect ratios (~1:1.618), layout column splits (~38%/62%), and spacing progressions
  where each step is φ× the previous. Not a rule — a lens. When a proportion "feels off,"
  checking against φ often reveals why.
- **Root rectangles** (√2 ≈ 1.414, √3 ≈ 1.732, √5 ≈ 2.236) provide additional proportional
  frameworks. The √2 rectangle (ISO paper sizes, A4/A3) is self-similar when halved —
  useful for nested layouts. √5 underpins the Golden Rectangle.
- **Modular scales** extend ratios to type and spacing. A 1.25 (Major Third) or 1.333
  (Perfect Fourth) ratio applied to a base size generates a complete harmonious system.
  These are not arbitrary — they encode mathematical relationships the eye perceives as balanced.
- **Rule of thirds** divides a composition into a 3×3 grid. Key elements placed at intersection
  points create visual tension and interest. Applies to hero sections, card compositions,
  and dashboard layouts.
- **Optical sizing vs. mathematical sizing.** Equal mathematical dimensions don't always appear
  equal. Circles need to be slightly larger than squares to look the same size. Rounded corners
  need to be larger at outer radii than inner (Google's superellipse principle). Icons need
  optical weight balancing.

### Color Theory & Application
- **Color spaces matter.** sRGB is a display standard, not a perceptual one. OKLCH separates
  lightness, chroma, and hue into perceptually uniform axes — equal L steps produce equal
  perceived brightness changes. Design system color scales should be built in perceptual
  color spaces, not sRGB.
- **Complementary harmony** (opposite hues) creates maximum contrast and visual energy.
  **Analogous harmony** (adjacent hues) creates cohesion. **Triadic** (120° apart) balances
  variety with unity. The harmony model should inform brand + accent token relationships.
- **Simultaneous contrast** — a color appears different depending on its surroundings. A medium
  gray on white looks darker than the same gray on black. This is why swatch documentation
  needs context-aware badges (APCA on the actual background, not in isolation).
- **Color temperature** affects mood and spatial perception. Warm colors (red/orange/yellow)
  advance; cool colors (blue/green/violet) recede. Use this in elevation: surfaces at higher
  elevation can be slightly warmer (Material Design uses this).
- **Chroma distribution** across a palette should follow a logic. Brand colors carry high chroma.
  Neutral surfaces carry near-zero chroma. Status colors need enough chroma to be identifiable
  but not so much they dominate. The distribution is intentional, not arbitrary.
- **Lightness as the primary contrast dimension.** Hue and chroma contribute to identity, but
  lightness drives readability. APCA measures this directly. Two colors can differ in hue
  dramatically but still be illegible together if their lightness is similar.

### Layout Grids & Spatial Systems
- **Column grids** divide horizontal space into modules. 12-column grids (Bootstrap, Material)
  provide flexibility (1, 2, 3, 4, 6, 12 divisions). The column count should match the
  complexity of the content — simpler content needs fewer columns.
- **Baseline grids** create vertical rhythm. All text and spacing snaps to a common increment
  (typically 4px or 8px). This creates visual harmony across sections, columns, and components.
  The base unit in a design system IS the baseline grid.
- **Compound grids** combine multiple grid structures. A 12-column content grid with a
  4px baseline grid creates a matrix that all elements align to. Consistent alignment
  across both axes is what makes a layout feel "designed" versus assembled.
- **Gutters vs. margins.** Gutters (inter-column space) separate related content. Margins
  (outer boundary space) separate content from the edge. These serve different spatial
  functions and should use different spacing tokens.
- **Responsive breakpoints** are not arbitrary. They should correspond to real device
  classes and content reflow points — where the layout naturally needs to adapt, not at
  round numbers.
- **Negative space (white space)** is not "empty" — it's an active compositional element.
  It creates breathing room, groups related items, separates sections, and directs attention.
  Generous negative space signals quality and confidence. Cramped layouts signal information
  overload.

### Visual Weight & Balance
- **Visual weight** is influenced by: size (larger = heavier), color (darker/more saturated =
  heavier), density (complex shapes = heavier), position (top/right feels heavier than
  bottom/left in LTR contexts), and isolation (an element surrounded by space carries more
  weight than one in a group).
- **Symmetrical balance** creates formality and stability. **Asymmetrical balance** creates
  dynamism and visual interest while maintaining equilibrium. Most effective UI layouts
  use asymmetrical balance — sidebar + content, hero + supporting elements.
- **Visual hierarchy** is created through contrast in scale, weight, color, and position.
  At least 3 distinct levels of hierarchy should be perceptible at a glance: primary (what
  to focus on), secondary (supporting context), tertiary (metadata/actions).
- **F-pattern and Z-pattern reading.** Western users scan in F-patterns for content-heavy
  pages and Z-patterns for minimal layouts. Place key elements along these scan paths.
  This applies to dashboards, documentation pages, and marketing layouts alike.

### Purpose & Audience Awareness
All visual decisions — from token architecture to component anatomy to documentation layout —
should be filtered through: **Who is looking at this, and what are they trying to do?**

- Design system documentation is consumed by designers and engineers. Clarity, scannability,
  and technical precision matter more than visual flair.
- Component libraries are consumed by product teams building interfaces for end users.
  The components must serve the end user's task, not just look good in the library.
- Dashboard and data-heavy layouts require visual hierarchy that supports rapid scanning.
  Dense information needs clear grouping, consistent alignment, and restrained color use.
- The medium matters. Screen-rendered text at 16px is not the same as printed text at 16pt.
  Anti-aliasing, pixel density, viewing distance, and ambient lighting all affect perception.
  Design for the actual rendering context, not an idealized one.

### Graphic Design as Applied Mathematics
The relationship between graphic design and mathematics is not metaphorical — it's structural.
Understanding these connections transforms design from "what looks good" to "what is harmonically
correct and why."

- **Proportional systems are hierarchical.** The golden ratio (φ) is one ratio in a family.
  The Fibonacci sequence (1, 1, 2, 3, 5, 8, 13, 21, 34, 55...) approximates φ and appears
  in spacing progressions, grid systems, and type scales. The silver ratio (δs = 1 + √2 ≈ 2.414)
  governs octagonal geometry and A-series paper. Le Corbusier's Modulor system combined φ with
  human proportions to create an architectural scale. These aren't competing systems — they're
  different expressions of the same underlying mathematics of visual harmony.
- **Harmonic intervals map to visual proportions.** The musical octave (2:1) corresponds to a
  doubling in scale. The perfect fifth (3:2) is used in classical page margins (Tschichold's
  canon). The perfect fourth (4:3) gives the classic screen ratio and the Major Third type
  scale (1.333). These are not coincidences — the eye and ear share sensitivity to ratio.
- **The Van de Graaf canon** and **Villard's figure** are historical page proportion systems
  that produce margins in 2:3:4:6 ratios — creating an inner text block that is exactly
  proportional to the page itself. This self-similarity principle (fractal geometry at the
  macro level) is why well-designed layouts feel "right" — the parts echo the whole.

### Advanced Color Theory for Design Systems
Color in a design system operates at three levels simultaneously: perceptual (how the eye sees
it), semantic (what it means), and systematic (how it relates to every other color).

- **Perceptual uniformity is non-negotiable.** sRGB hex values are device coordinates, not
  perceptual values. A 10-step grayscale in hex (#1A, #33, #4D, #66, #80, #99, #B3, #CC,
  #E6, #FF) does NOT produce perceptually even steps. OKLCH L-values do. Every design system
  color scale should be built in a perceptual space, then converted for output.
- **Bezold effect** — changing one color in a composition changes the perceived appearance of
  adjacent colors. This is why design system swatches must be evaluated in context (on actual
  surfaces) not in isolation. A swatch grid on white looks different than the same colors
  applied to cards on a gray surface.
- **Chromatic adaptation** — the eye adjusts to ambient color temperature. A "neutral" gray
  looks blue under warm light and yellow under cool light. Dark mode surfaces should account
  for this — slightly warm darks (#1A1A1F rather than #1A1A1A) feel more natural on screens
  viewed in warm environments.
- **Color gamut mapping** is a design decision, not a technical conversion. When an OKLCH color
  is out of sRGB gamut, the mapping strategy (reduce chroma, reduce lightness, or both)
  affects the resulting palette character. Reducing chroma preserves lightness relationships
  but desaturates. Reducing lightness preserves chroma but changes the tonal relationship.
  The CDS engine's gamut mapping uses OKLCH chroma reduction to maintain lightness-based
  contrast guarantees.
- **The 60-30-10 rule** from interior design applies to UI: 60% dominant color (surfaces),
  30% secondary (containers, cards), 10% accent (interactive, brand). This creates visual
  hierarchy through proportion, not just contrast.

### Grid Systems: From Gutenberg to Design Tokens
Understanding where grids come from reveals why they work in digital interfaces.

- **Gutenberg's 42-line Bible** (1455) established the first mass-produced typographic grid.
  Each page is a precisely proportioned text block within margins that follow the 2:3:4:6
  canon. The grid wasn't aesthetic decoration — it was a production system for consistency.
  Design systems serve the same purpose at interface scale.
- **Swiss/International Typographic Style** (Müller-Brockmann, 1950s–60s) codified grid
  systems as the primary organizational tool. Key insight: the grid is not a cage — it's a
  scaffold that creates freedom through constraint. Elements aligned to a grid create order
  that lets intentional breaks (bleeds, overlaps, asymmetry) carry meaning.
- **Subgrids and nesting.** A 12-column macro grid can nest a 4-column card grid which nests
  a 2-column form grid. Each level maintains alignment with the parent through shared
  gutters and margins. In design tokens, this maps to spacing tokens at different scales
  (page padding > section gap > component padding > element spacing).
- **Modular grids** combine columns and rows into a matrix of modules. Each module is a unit
  of content. Dashboards are modular grids. Card layouts are modular grids. The "atoms →
  molecules → organisms" pattern in Atomic Design is a modular grid principle.

### Visual Rhythm & Repetition
Rhythm in visual design creates predictability, which creates scannability, which creates
usability.

- **Repetition creates pattern recognition.** When every card in a grid has the same padding,
  the same title size, the same badge position — the user learns the pattern once and scans
  efficiently. Breaking the pattern (intentionally) signals "this one is different."
- **Alternation creates visual interest within consistency.** Light/dark row striping in data
  tables, alternating section backgrounds, even/odd spacing — these are rhythmic devices
  borrowed from music (ABAB patterns).
- **Progression creates direction.** Size progressions (small → medium → large), color
  progressions (light → dark), density progressions (sparse → dense) — these guide the eye
  through content. The type scale IS a progression. The spacing scale IS a progression.
  Token scales should express clear directional movement.

### Typography as Information Architecture
Type isn't just "how text looks" — it's how information is structured, prioritized, and navigated.

- **The paragraph is the fundamental unit of reading.** Line length (measure), line spacing
  (leading), and paragraph spacing work together. Changing one without adjusting the others
  breaks the reading experience. Token systems should provide these as coordinated sets,
  not independent values.
- **Micro-typography** — letter spacing, word spacing, hanging punctuation, ligatures, and
  optical margin alignment — is what separates professional typography from text rendering.
  Design systems should encode these refinements in text styles, not leave them to individual
  implementation.
- **Typographic color** (not literal color — the overall texture density of a text block)
  should be even. Inconsistent line lengths, rivers of white space, and orphaned lines
  create uneven typographic color. Auto-layout with proper constraints prevents most of these.
- **Type families are systems within systems.** Inter, for example, has optical sizes, variable
  axes, and alternates designed to work together. Using a type family means using the WHOLE
  system — weights, widths, optical sizes — not just Regular and Bold.

These principles form a continuous chain: mathematics → proportion → grid → layout → typography →
hierarchy → meaning. Each level depends on the one below it. Design systems formalize this chain
into tokens, styles, and components so that the mathematics is encoded once and applied everywhere.

---

