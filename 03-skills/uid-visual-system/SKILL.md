---
name: uid-visual-system
description: >
  Coherent visual language, style guide development, and aesthetic consistency
  across a digital product. Use this skill when the conversation touches: visual
  system development, style guide authoring, visual language coherence, aesthetic
  consistency audits, brand-to-product visual translation, shape language, motion
  character, visual system evolution, platform-specific visual conventions, or any
  question about how to make a product look and feel like itself. This spoke is
  part of the lead-ui-designer hub skill network.
aliases: [uid-visual-system]
tier: spoke
domain: design
hub: lead-ui-designer
prerequisites: [lead-ui-designer]
spec_version: "2.0"
---

# UID: Visual System

Specialist spoke for coherent visual language and aesthetic consistency.
Part of the `lead-ui-designer` hub skill network.

---

## Domain Boundary

This spoke owns the **visual language layer** of a product — the codified rules
that govern all visual decisions and make a product recognizable as itself.

- **Token architecture that encodes the visual system** → `ds-advisor`
- **Brand identity that is upstream of the product visual language** → `gd-brand-identity`
- **Behavioral design system (patterns, components, flows)** → `ux-design-systems` + `lead-ux-designer`
- **Individual visual domains in depth** → other `uid-*` spokes

---

## Visual System Components

A complete visual system is explicit about all of the following. If any of these
are implicit or undocumented, they are a liability — inconsistent application is
inevitable because different people will infer different rules.

### Color Palette + Usage Rules
Not just swatches — the rules for what each color means and where it goes.
- Brand color: identity and recognition; used sparingly and intentionally
- Semantic colors: success/warning/error/info — these carry meaning independent of brand
- Neutral colors: surfaces, text, borders, dividers — the majority of the visual real estate
- Accent: interactive elements, focal points, emphasis

Document: which colors can appear on which backgrounds, what roles are exclusive, what contexts each color may NOT appear in.

### Type System
The complete typography scale with function assigned to each level. Not just
sizes — also weight, line height, tracking, and when each level is used.
See `uid-type-for-screens` for the full type-for-screens framework.

### Spacing System
The base unit, the scale steps, and the semantic assignments (padding-xs, gap-md,
section-spacing-lg). Not a list of numbers — a rationale for the progression.
See `uid-spatial-composition` for the full spacing framework.

### Shape Language (Border Radius Family)
Corner radius is not a single value — it's a family with a rule:
- **Micro radius** (2–4px): chips, tags, small badges
- **Component radius** (6–8px): buttons, inputs, small cards
- **Container radius** (12–16px): cards, panels, modals
- **Large radius** (20–24px+): feature cards, illustrations, hero elements
- **Pill** (9999px): toggles, full-radius buttons — used deliberately

The rule: outer containers use a larger radius than inner components. Nested
elements that have the same radius as their parent look like a rendering error,
not a design decision. The "squircle" principle: if an outer radius is R, an
inner element at P pixels of padding should use approximately R − P for its radius.

Failure mode: globally applying `border-radius: 8px` to everything, which makes
all elements look the same visual weight regardless of size or hierarchy.

### Motion Character
The personality of transitions, animations, and micro-interactions:
- Duration range (fast: ~100ms, medium: ~200ms, slow: ~300–400ms)
- Easing character (ease-out for elements entering, ease-in for leaving,
  ease-in-out for state transitions within a surface)
- The "personality" dial: does this product move crisply (functional, business) or
  fluidly (expressive, consumer)?

Motion character must be consistent — mismatched animations between parts of a
product signal that different teams built them without coordination.

### Iconography Style
The visual character of icons as a set. See `uid-iconography` for full depth.
For visual system purposes: document stroke weight, corner radius, fill vs. outline
convention, level of abstraction, and whether the icon set matches the product's
overall aesthetic personality.

### Illustration Style (If Applicable)
Line weight, color palette (does it pull from the product palette or extend it?),
perspective, character design. Illustration is often the most brand-expressive
element — it should be explicitly scoped.

### Photography Style (If Applicable)
Tone (documentary vs. editorial vs. commercial), color grading, composition rules,
subject matter. In enterprise SaaS this is often irrelevant for product UI but
critical for marketing materials.

---

## Style Guide vs. Design System

These are different artifacts serving different purposes. Both are needed.

| Artifact | What it defines | Who uses it | Lives in |
|---|---|---|---|
| **Style guide** | The aesthetic language — what the product looks and feels like, the rules behind visual decisions | Designers, brand, marketing | Figma, Notion, PDF |
| **Design system** | The encoded system — components, tokens, patterns that implement the visual language | Designers + engineers | Figma library, code package, Storybook |

A style guide without a design system means consistent visual language that
designers understand but engineers can't implement reliably. A design system
without a style guide means encoded values with no rationale — no one knows why
the values are what they are, so they can't extend the system intelligently.

The style guide is written in principles and rules. The design system is built
in tokens and components. They must align. Divergence between them is a system
health problem.

---

## Visual Language Development

### From Existing Brand Identity

If a brand identity exists (logo, brand guidelines, brand colors):

1. **Extract the visual DNA**: What shapes does the logo use? What weights? What
   is the overall personality (geometric/organic, formal/casual, crisp/soft)?
2. **Translate, don't copy**: Brand identity is designed for print and large-format
   contexts. UI requires adapting the language, not copying the artifacts. A logo
   typeface is rarely appropriate as a UI typeface.
3. **Extend coherently**: The brand provides the personality dial setting. The UI
   visual system applies that personality to components, surfaces, data tables,
   form fields — contexts that brand guidelines never address.
4. **Identify brand colors that can't be used directly**: Brand colors are often
   too saturated, too dark, or insufficiently accessible at full strength in UI
   contexts. The visual system must adapt these to usable values while preserving
   the brand character.

### Without an Established Brand Identity

Start with product principles, not visual decisions:
1. Who are the users? What's the context of use? (enterprise dashboard ≠ consumer app)
2. What should the product feel like? (precise and efficient / warm and approachable / bold and confident)
3. What are competitors doing? Where do you want to differentiate visually?
4. Build the palette first (see `uid-color-for-ui`), then derive the rest.

Failure mode: starting with a typeface or an accent color because "it looks
good" before establishing what the product is trying to feel like.

---

## Aesthetic Consistency Audit

Three fast tests for visual coherence. Run these before any design review.

### The Blur Test
Blur the screen at 4–6px gaussian. Does the hierarchy still read? Is there one
clear focal point? Are there unintended focal points drawing attention? This
tests whether visual hierarchy is built from structure and contrast, not detail.

### The Brand Test
Strip all text from the screen. Could you identify this product from a competitor's
by visual language alone? If not, the product has no visual identity — it's
generic. Conversely, if it looks more like a competitor than itself, there's a
visual language problem.

### The Five-Second Test (Visual Version)
Show the screen for 5 seconds then hide it. Ask: what did you notice first?
This should match the information hierarchy intent. If the first thing noticed
is the navigation chrome, a decorative element, or a status badge — the primary
content is not visually dominant enough.

---

## Visual System Evolution

### Evolutionary vs. Revolutionary Approaches

**Evolutionary**: Incremental changes that maintain visual continuity. One
change at a time — border radius update, type scale refinement, color
adjustment. Users and the team can adapt. Design debt is paid down gradually.

Appropriate when: the current system is functional but needs refinement;
the team is under delivery pressure; there are many consumer files / products
that would need updates.

**Revolutionary**: Comprehensive redesign of the visual language. New style
guide, new tokens, migration plan. Visual discontinuity is accepted in exchange
for a coherent foundation.

Appropriate when: the current system is fundamentally broken or incoherent;
a major product rebrand is happening anyway; the design debt has compounded to
the point where incremental fixes are more expensive than starting over.

**Almost always: start evolutionary.** Revolutionary redesigns are high-risk
and rarely necessary. Most "it needs a complete overhaul" diagnoses are actually
3–5 high-leverage evolutionary changes that would get 80% of the way there.

### Migration Planning

When any visual system change is made:
1. Document what changed and why (a DDR in `ds-advisor` format works here)
2. Identify all consumer surfaces — don't just change the token/style, assess
   how it propagates
3. Build a transition period in when needed — especially for public-facing changes
4. Archive old values; never silently delete (Obsidian links and Figma references
   break silently)

---

## Platform-Specific Considerations

### Mobile vs. Desktop Visual Language

Mobile and desktop share a visual system but apply it differently:
- **Touch targets**: minimum 44×44pt (iOS) / 48×48dp (Android) affects component sizing
- **Density**: desktop can support denser information at smaller sizes; mobile requires more generous spacing
- **Typography scale**: larger minimum sizes on mobile (typically 16px body minimum)
- **Navigation paradigm**: mobile navigation patterns affect visual layout priorities

The visual system should specify where it **conforms to OS conventions** and
where it **expresses brand** — both are legitimate choices, but they must be
explicit.

### OS Conventions vs. Brand Expression

| Domain | Conform | Differentiate |
|---|---|---|
| Navigation gestures | Yes (swipe back, pull to refresh) | No — users expect these |
| System dialogs (permissions, biometrics) | Yes — don't customize OS chrome | — |
| Typography scale base | Yes (respect OS accessibility text size settings) | Custom scale above the base |
| Color (especially systemBackground, systemFill on iOS) | Sometimes — dark mode specifically | Brand colors can differentiate |
| Icon style | Brand discretion — no OS mandate | Can fully own if consistent |

**Rule**: Conform to OS conventions when violating them creates confusion or
friction. Differentiate where brand expression adds value without compromising
usability.

---

## Cross-Links

- `gd-brand-identity` — brand identity is upstream; the visual system translates it to product
- `ds-advisor` — visual language decisions become token and component architecture here
- `uid-color-for-ui` — color palette and usage rules in depth
- `uid-type-for-screens` — type system in depth
- `uid-spatial-composition` — spacing system in depth
- `uid-surface-depth` — surface and elevation design in depth
- `uid-iconography` — icon visual language in depth
- `uid-visual-critique` — consistency audit frameworks in depth
- `lead-ux-designer` / `ux-design-systems` — the behavioral design system is built on top of this visual system

## Related
- hub → [[lead-ui-designer]]
