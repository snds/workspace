---
title: Intro + Chapter 1 — Core Concepts
course: Subatomic — The Complete Guide To Design Tokens (Brad Frost & Ian Frost)
sections: ["Introduction", "Chapter 1: Core Concepts"]
lessons: 19
source: https://courses.bradfrost.com/courses/take/subatomic-design-tokens/lessons/62108387-welcome
status: noted
as-of: 2026-09-23
---

# Intro + Chapter 1 — Core Concepts

Original notes (not a transcript). Raw transcripts live outside the workspace in
`<Projects>/subatomic-design-tokens-course/transcripts/00-*` and `01-*`.

## Working definition

Tokens = **design properties stored as variables, used to make UI themeable.** The Frosts layer on
four properties that matter operationally: they are the *smallest* unit of the system (the "subatomic"
layer under Atomic Design), they are *decisions* of a design language, they are *implementation-agnostic*
(one source, many outputs), and they are the *engine of themeability*. Origin credit: Jina Anne + Jon
Levine at Salesforce (Lightning Design System, ~2014–16), later standardized by the W3C Design Tokens
Community Group (DTCG).

Token-able property families: color (background / text / border / icon), typography (family, size,
weight, line-height, letter-spacing, transform), border (width, radius, style), shadow, sizing, spacing,
animation, breakpoints, z-index. **Color and typography carry the most weight.**

## Why tokens exist — "multi-all-the-things"

The recurring framing device. Real org landscapes are heterogeneous along many axes at once:

| Axis | Example they use |
|---|---|
| Multi-product | Caterpillar's many sites (cat.com, parts, used, dealer, careers) |
| Multi-brand (Aaker brand-relationship spectrum: branded house ↔ house of brands) | Marriott portfolio |
| Sub-brands | Apple product lines; Verywell → Verywell Fit / Mind |
| Rebrands / refreshes / redesigns | "almost always in progress or on the horizon" |
| White-labeling | Blend (mortgage software re-skinned per bank) |
| Product families (marketing vs. dense app) | salesforce.com vs. Salesforce app |
| Color modes (knockout/inverted, user-selectable themes, OS dark mode) | GitHub themes; `prefers-color-scheme` |
| Multi-framework | WordPress homepage + React logged-in app must look like one product |
| Multi-platform | Target web / iOS / Android / kiosk |

Every org's mix is different — the token architecture must be sized to the actual axes present.

## Business case (the "can you do multiplication?" argument)

- **Without tokens**: a brand-color change is duplicative, disconnected, slow, error-prone, and scales
  multiplicatively with touchpoints. Illustrative math: ~$50k fully-loaded per button implementation
  (plan → design → review → build → QA → release → adopt → maintain) × 88 buttons ≈ $4.4M.
- **With tokens + components**: pay a large fixed cost once (illustrative $250k component + $250k token
  system), then each additional variant is a small marginal cost (~$25k). The curves cross early; at 500
  or 1,500 buttons it is not close.
- The mechanism: brand green is given a **job** (`background-brand`), and every connected touchpoint
  listens to the job, not the hex. A rebrand becomes "publish new token version, consumers update."

## The new separation of concerns

Classic web SoC (HTML structure / CSS style / JS behavior) blurred once everything moved into JS. The
Frosts redraw the line as:

- **Component system** → structure + behavior (semantics, structural/layout CSS, API, JS). The *door and
  its hinges*.
- **Token system** → aesthetic look-and-feel. The *paint and hardware*.

Tokens flow *through* components to produce a result. CSS Zen Garden is the proof-of-concept lineage:
same markup, radically different aesthetics.

## Where tokens show up

- **Design tools** — Figma Variables (the course's primary design tool); modes switch brand/theme per frame.
- **Code** — an implementation-agnostic source (usually JSON) → a transformer (Style Dictionary in this
  course) → platform outputs (CSS custom properties, Sass, JS, iOS, Android, JSON) → consumed by apps and
  workshop tools (Storybook). Once components reference tokens, themes swap **without touching component code**.

## Tokens in the design-system ecosystem (layer cake)

Core design system = **token system + component system**, each with Figma library, repo, package, plus
Storybook and a reference site. Tokens flow to:

1. the core component library (consumers get tokens "for free"),
2. tech-specific implementations (iOS/Android/other framework libraries),
3. **recipes** (product-specific composites that don't belong in core — e.g. Maps turn-by-turn UI),
4. smart components (data-wired tables, CMS-bound forms),
5. individual product designs/code bases (snowflakes stay on-brand).

**Key claim: tokens can be adopted independently of the component library.** They travel further than
components can.

## For Sean

- The "give the brand color a job" move is the whole game — it maps directly onto the workspace's
  primitive → semantic → component tiering. The course's contribution is making *the job* the named unit.
- "Tokens travel further than components" is a good arbiter for CDS/employer-agnostic advice: when a
  product can't adopt the component library, prescribe token adoption first, not a fork.
- Business-case math is illustrative, not measured — reuse the *shape* (fixed vs. marginal cost curves),
  not the dollar figures, in any stakeholder artifact.
