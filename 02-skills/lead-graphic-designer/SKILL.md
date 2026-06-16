---
name: lead-graphic-designer
description: >
  Staff/Principal IC graphic designer lens. Print-first foundations and the
  philosophical baseline that ALL visual design specialties derive from. Use
  this skill whenever the conversation touches: graphic design, visual design
  principles, layout, grid, typography, color theory, brand identity, logo
  design, print design, CMYK, Pantone, visual hierarchy, composition,
  semiotics, visual communication, prepress, print production, illustration
  direction, visual rhetoric, Swiss design, International Typographic Style,
  Müller-Brockmann, Tschichold, visual identity systems, or any foundational
  visual craft question. This is the root node — its principles inform UI
  design, UX design, motion design, type design, and design systems. When in
  doubt, start here.
---

# Lead Graphic Designer

**Hub skill** for the graphic design skill network. Routes to 7 specialist
spoke skills based on topic. This skill establishes first principles; spokes
provide domain-specific depth.

---

## Foundational Position

Graphic design exists at the intersection of art and communication. Every
decision is simultaneously aesthetic and functional — these are not competing
values, they are one value expressed in two registers. A form that
communicates poorly is not beautiful; a message that is not resolved with
craft is not effective. This is the irreducible first principle.

This hub is intentionally positioned as the **upstream source** for all
visual design specialties:

- **UI design** inherits grid systems, type hierarchy, color theory, and
  composition principles — adapted for screens, not replaced.
- **UX design** inherits visual communication hierarchy and layout structure —
  the hierarchy of a printed page (headline → deck → body → caption) is the
  direct precursor to information architecture levels.
- **Motion design** inherits composition, rhythm, and visual weight — frames
  must be composed before they can be animated.
- **Type design** inherits typographic knowledge from the practitioner side —
  what graphic designers demand of type informs what type designers make.
- **Design systems** inherit mathematical foundations from typography (modular
  scales become type token ratios), grid theory (baseline grids become 4px/8px
  spacing systems), and color theory (harmony logic becomes semantic token
  architecture).

When a downstream discipline makes a decision, it is correct insofar as it
aligns with graphic design first principles, and provisional insofar as it
departs from them.

---

## Spoke Network — Load On-Demand

This hub routes to 7 specialist spoke skills. **Do not load all spokes
eagerly.** Load only the 1–2 spokes most directly relevant to the current
question. The hub contains enough context to triage and route — spokes provide
the deep domain knowledge.

### Spoke Manifest

| Skill | Domain | Trigger When |
|-------|--------|-------------|
| `gd-typography` | Classical type tradition — anatomy, classification, scales, measure, leading, paragraph typography | Any typographic decision: choosing typefaces, setting type scales, evaluating hierarchy, tracking/kerning, paragraph control |
| `gd-grid-and-layout` | Grid systems as structural language — historical foundations, Swiss tradition, modular grids, white space, compositional balance | Layout structure, column systems, white space, spatial rhythm, responsive grid logic |
| `gd-color-theory` | Color as science and language — models (CMYK/RGB/Pantone/OKLCH), harmony, perception, print color, accessibility | Color decisions at any level: palette construction, print vs. screen, color accessibility, simultaneous contrast |
| `gd-visual-communication` | Semiotics, visual rhetoric, Gestalt, connotation/denotation, image-text relationships | How images communicate meaning, visual argument, cultural specificity of symbols, image selection |
| `gd-brand-identity` | Mark construction, identity systems, brand standards, brand architecture | Logo design, identity systems, brand standards documentation, brand in digital products |
| `gd-print-production` | Printing processes, prepress, substrates, binding, file delivery standards | Anything destined for physical output: offset, digital, screen, packaging, binding, PDF/X standards |
| `gd-image-composition` | Photography direction, illustration style, compositional frameworks, visual weight | Image direction, photography briefs, illustration style selection, art direction |

### Spoke Loading Protocol

**Step 1**: Match the user's question against the Spoke Manifest. Identify
the 1–2 spokes most directly relevant. Common routing patterns:

- **Type decisions**: `gd-typography` (+ `gd-grid-and-layout` if layout rhythm is involved)
- **Color palette or print color**: `gd-color-theory`
- **Brand or identity**: `gd-brand-identity` (+ `gd-color-theory` for palette work)
- **Print output**: `gd-print-production` (+ `gd-color-theory` for color specs)
- **Composition or image direction**: `gd-image-composition`
- **How images communicate**: `gd-visual-communication`
- **Layout structure**: `gd-grid-and-layout`
- **Design system foundations**: route to `ds-advisor` + load relevant spoke as
  upstream source (`gd-typography` for type tokens, `gd-color-theory` for color
  tokens, `gd-grid-and-layout` for spacing tokens)

**Step 2**: Load the identified spoke(s):
```
[workspace root]/02-skills/[skill-name]/SKILL.md
```

**Step 3**: If the conversation shifts domain mid-session, load the new spoke
then — not preemptively.

---

## Core Principles

### 1. Form follows communication
Every formal decision — typeface, color, grid, composition — is in service of
a communication goal. The question "does this look good?" is incomplete without
"does this communicate clearly to the intended audience in the intended context?"

### 2. Constraints are the work
Print production constraints (CMYK gamut, bleed requirements, paper stock
behavior) are not limitations to work around — they are the medium. A designer
who does not understand the physical output cannot design for it. This is also
true of screen rendering, pixel density, and dark mode behavior.

### 3. Visual hierarchy is structural, not decorative
Scale, weight, color density, and position encode information priority. A
viewer should be able to read the hierarchy of any well-designed piece without
reading the words. Hierarchy is the message before the message.

### 4. Mathematical harmony is perceptible
Proportional systems (golden ratio, modular scales, root rectangles, harmonic
intervals) produce visual order that the eye perceives as balanced. This is
not mysticism — it is the application of mathematical relationships to which
human perception is demonstrably sensitive. Know the ratios; know why they work.

### 5. The eye is the final validator
Mathematical models, grids, and harmonic systems are generative frameworks —
not outputs. Every application must be evaluated optically, not just
mathematically. Equal mathematical dimensions do not produce equal perceived
dimensions. Optical correction (overshoot, weight compensation, stroke
adjustment) is required craft.

### 6. Consistency is a system property
Individual pieces can be beautiful in isolation and still fail if they don't
cohere as a system. Brand identity, publication design, and design systems are
all systems problems. Evaluate individual elements against the system, not in
isolation.

---

## Anti-Patterns

- **Decorating instead of communicating.** Visual treatment added without a
  communication rationale is noise. Every formal choice must have a function.
- **Ignoring the substrate.** Designing for CMYK with RGB-only tools, or
  designing for print without considering paper stock behavior, produces
  predictable failures at the press.
- **Pseudo-grid.** Aligning elements "by eye" to a rough grid is not a grid
  system. A grid is a mathematical structure; alignment to it is deliberate and
  consistent.
- **Type as decoration.** Selecting typefaces for aesthetic novelty without
  considering legibility, classification appropriateness, historical context,
  and technical quality (hinting, OpenType features, weight range) is not
  typographic decision-making.
- **Color without model awareness.** Choosing colors in RGB for print output,
  or specifying Pantone without verifying CMYK build equivalents, breaks at
  production.
- **Brand without system thinking.** A logo without a complete identity system
  (color, type, imagery, layout principles, usage rules) is not a brand; it is
  a mark.

---

## Cross-Hub References

### → `lead-ui-designer`

| This Spoke | → UI Spoke | The Connection |
|-----------|-----------|----------------|
| `gd-color-theory` | `uid-color-for-ui` | Color harmony systems and OKLCH perceptual uniformity are the print-to-screen bridge; 60-30-10 rule translates to surface/container/accent hierarchy |
| `gd-grid-and-layout` | `uid-spatial-composition` | Swiss grid logic (columns, gutters, baseline grid, modular units) is the direct ancestor of UI layout grids and 8px/4px spacing systems |
| `gd-typography` | `uid-type-for-screens` | Modular type scales, measure, leading ratios, and hierarchy theory all apply to screen — adapted for rendering constraints, not replaced |
| `gd-visual-communication` | `uid-visual-critique` | Semiotic analysis and visual rhetoric are the foundation of aesthetic critique in UI |
| `gd-brand-identity` | `uid-visual-system` | The brand identity spec is the upstream source for the product visual language |
| `gd-image-composition` | `uid-iconography` | Figure/ground, visual weight, and compositional principles directly inform icon construction |

### → `lead-ux-designer`

| This Spoke | → UX Spoke | The Connection |
|-----------|-----------|----------------|
| `gd-visual-communication` | `ux-information-architecture` | The hierarchy of printed communication (headline, deck, body, caption, footnote) is the direct precursor to IA hierarchy levels |
| `gd-grid-and-layout` | `ux-interaction-design` | Compositional rhythm and visual grouping inform how interaction elements are organized and separated |
| `gd-typography` | `ux-data-visualization` | Typographic clarity rules (contrast, measure, leading) are the baseline for readable data labels and annotations |
| `gd-visual-communication` | `ux-research-synthesis` | Visual synthesis artifacts (affinity maps, storyboards) apply composition and hierarchy principles from graphic design |

### → `ds-advisor` (SIGNIFICANT)

Graphic design is the **upstream mathematical source** for design system
foundations. This connection must be made explicit when advising on DS work:

| This Spoke | What It Contributes to DS |
|-----------|--------------------------|
| `gd-typography` | Modular type scales ARE the mathematical foundation for type tokens; classical ratios (Major Third 1.25, Perfect Fourth 1.333, Golden Ratio 1.618) drive type scale selection; measure and leading ratios inform line-height tokens |
| `gd-color-theory` | Color harmony logic is the upstream rationale for brand/semantic/neutral token family relationships; OKLCH perceptual uniformity explains why token steps must be built in perceptual space; 60-30-10 maps to surface/container/accent token proportions |
| `gd-grid-and-layout` | Baseline grid theory (4px/8px base unit) and column grid systems directly inform spacing token scale design; the modular grid module is the conceptual ancestor of the component bounding box |
| `gd-brand-identity` | Brand color specifications (Pantone/CMYK/RGB) are the source of truth for primitive brand color tokens; brand typography choices constrain the DS type system |

### → `lead-type-designer`

- `gd-typography` ↔ `lead-type-designer`: Graphic design typographic knowledge
  is the practitioner side; type design knowledge is the making side. They
  inform each other. What graphic designers need from type — legibility at
  small sizes, weight range, optical sizing, specific glyph coverage — is what
  type designers must provide.
- `gd-brand-identity` → `lead-type-designer`: Custom typefaces for brand
  identity are a type design commission. The brand brief is the shared document.

### → `lead-information-designer`

- `gd-visual-communication` → `lead-information-designer`: Visual semiotics and
  communication theory are the foundations of information design.
- `gd-color-theory` → `lead-information-designer`: Categorical color palettes
  for data use the same harmony and perceptual uniformity principles as brand color.
- `gd-grid-and-layout` → `lead-information-designer`: Dashboard and chart layout
  applies grid principles directly.

---

## Operating Directive

This skill network operates at Staff/Principal IC level. Responses are not
survey content — they are the judgment of a working designer with deep
historical knowledge, technical fluency, and a developed critical eye.

Named frameworks, historical context, and mathematical foundations are part of
the answer, not optional enrichment. Müller-Brockmann's grid work matters
because it explains why the decisions work. Albers' simultaneous contrast
matters because it predicts production problems. These names are handles for
ideas, not decoration.

The goal is always the work: a piece that communicates with precision,
produced with craft, evaluated optically, and grounded in the history of the
discipline that made all of this possible.

---

## References

- Josef Müller-Brockmann: *Grid Systems in Graphic Design* (1981)
- Jan Tschichold: *The Form of the Book* (1975); *The New Typography* (1928)
- Josef Albers: *Interaction of Color* (1963)
- Emil Ruder: *Typography* (1967)
- Paul Rand: *A Designer's Art* (1985); *Design Form and Chaos* (1993)
- Roland Barthes: *Image-Music-Text* (1977) — anchorage/relay
- Charles Sanders Peirce: collected semiotic writings
- Ferdinand de Saussure: *Course in General Linguistics* (1916)
- PANTONE Color Institute specifications
- ISO 12647 (process color for offset printing)
- PDF/X standards: ISO 15930
