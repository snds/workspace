---
title: Context-Based Design Systems Overview
section: "Chapter 3: Make Better Design Systems With AI"
source: https://courses.bradfrost.com/courses/take/ai-design-systems-course/lessons/77363868-context-based-design-systems-overview
duration: ~12m14s
status: noted
as-of: 2026-09-10
---

# Context-Based Design Systems Overview

The method promised since Intro. Works for **design-led or code-led**. Lifecycle (they walk it from canvas):

1. **Design ideation** — component, metadata, variants, themes, states, tokens; talk to eng about events/interaction *here*.
2. **Design QA** — FigmaLint / Figma Check Designs. Lint the *designed* component (hardcode, layer names, props, states, descriptions, annotations) the way you’d lint before a commit. Docs so humans *and* AI know intent.
3. **Design-to-dev protocol** — MCP (official Figma, Console, CLIs) so the agent reads specs **and** peripheral context. Product designers should **own the first code draft** on a design branch — especially motion/easing/events — then view in Storybook. Cuts the designer↔dev loop.
4. **Engineering oversight / context engineer** — PR from the design branch. Someone who knows org coding standards + architecture reviews the designer’s draft. Overlap in the PR; then the context engineer shepherds.
5. **Validation/testing** — whatever the org uses (unit, e2e, VRT, AI or manual). Not one-size.
6. **Publish & version** — validated set → npm (or equivalent).
7. **Prompt & iterate playground** — Story UI, Figma Make, Claude Design, v0, etc. Prototyping **imports the validated package**, not a lookalike kit.
8. **Approval & integration** — shippable prototype and/or the new component land in the product. Cycle restarts.

Human layer: designer owns intent→draft on a breakable branch; PR is shared; context engineer owns the rest of the pipe.

**For Sean:** this is the inheritance chain. Centric analog = designer-owned first draft against the real DS package, PR to FE with a named reviewer role, playgrounds that consume the published library (not a parallel universe). Still unproven at Centric until a pilot runs this loop once.
