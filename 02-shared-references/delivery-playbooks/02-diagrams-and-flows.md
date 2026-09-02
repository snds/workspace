---
title: Diagrams & Flows — the medium is the requirement
status: canonical
date: 2026-07-09
tags: [diagrams, flows, notation, medium, delivery]
---

# Diagrams and flows — the medium is the requirement

Fires when the request's own words say **workflow, flow, journey, diagram, map, "how does it
work," "show me the steps."** Those words bind the medium: the deliverable is a rendered
visual diagram. Prose describing a flow, a code listing, or an application page is a different
medium and does not satisfy the request.

**Founding anti-example.** Media Sentinel workflow-diagram request → delivered as an
engineering-voiced HTML page, neither diagram nor designer-readable. Both axes failed at once:
medium (page ≠ diagram) and audience (engineer vocabulary for a design reader). This playbook
exists so that never repeats.

---

## Two diagram types — pick by what the request asks

### 1. Flow diagram (default for "workflow / journey / flow")

The UX-native notation Sean and his managers already read:

- **Actions** — rounded rectangles, verb-first plain-english labels ("Review the article").
- **Decisions** — diamonds, phrased as questions with labeled exits ("Matches a watchlist
  term? — yes / no").
- **Destinations / outcomes** — where the actor lands ("Article archived").
- **Swimlanes** — one lane per role or actor (the user, the system, a third party). If the
  system does something invisible, it gets its own lane — visible, not hidden.
- **Start and end points** explicitly marked. Every path reaches an end; no dangling arrows.

### 2. System picture (for "how does it work" about internals)

The same back-of-house content engineers would diagram — inputs and outputs, processing steps,
gates, loops — drawn for a design reader:

- **Inputs/sources** enter from the left or top, labeled by what they are in plain english
  ("News sites we watch"), not by protocol or technology.
- **Processing steps** as labeled boxes describing *what happens to the thing* ("Checks the
  source against your block list"), not the component name.
- **Gates and loops** made explicit and readable ("waits 5 minutes, then checks again").
- **A legend, always** — every shape and line style used, defined in one line each.
- Technology names appear only in a de-emphasized annotation layer, never as the primary label.

---

## Medium and format

- **Rendered visual first:** FigJam (via the Figma MCP `generate_diagram`), SVG, or Mermaid
  rendered to an image — per the reader's destination. Mermaid *source* is not a deliverable
  to a designer; the rendered result is.
- Self-contained and forwardable per [[artifact-standards]] — naming convention, versioned,
  opens by double-click.
- An interactive HTML page is only the right medium when interactivity was requested —
  and even then it embeds the diagram, it doesn't replace it.

## Quality bar

- Passes the forward test ([[01-audience-contract]]) — Sean's manager can read it cold.
- One diagram, one question. A flow *and* a system picture is two diagrams, not one hybrid.
- Every label plain-english; jargon rule applies to annotations too.
- Legible at the size it will actually be viewed — judged per [[10-perception-integrity]]
  (native resolution) before claiming it's clean.
- Complex systems get an overview diagram plus detail diagrams, never one dense mega-map.

## Pre-delivery checklist

0. Context profile resolved and cited? ([[00-context-profiles]] — always first)
1. Is it actually a diagram (rendered, visual, spatial) — not prose or a page?
2. Right type for the request — flow (actors and choices) vs. system picture (internals)?
3. Swimlanes/roles explicit? Every decision phrased as a question with labeled exits?
4. Legend present? Labels verb-first and plain?
5. Forward test passed?
