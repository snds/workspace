---
name: figma-design-specs
description: >
  Turn a Figma design into an implementation-ready spec/PRD — read the frame via the Figma MCP and write
  a structured, build-able description: layout + responsive behavior, exact tokens/variables, component
  inventory, states/variants, interactions, content, and a11y notes. Use when an engineer (or you) needs
  the design *documented* before building, or for a handoff/PRD. Triggers: figma spec, design spec, PRD
  from figma, design handoff doc, document this design, figma to spec, implementation spec.
aliases: [figma-design-specs, figma-designer]
triggers: [figma spec, design spec, prd from figma, design handoff doc, document this design, figma to spec, implementation spec, dev handoff spec]
tier: spoke
hub: figma
domain: design
prerequisites: [figma]
requires: [figma-mcp]
spec_version: "2.1"
---

# Figma — Design Specs / PRD

Convert a design into the words and numbers an engineer needs to build it correctly the first time. The
output is a *spec*, not code ([[figma-design-to-code]] is the codegen path) — it's the bridge between the
canvas and implementation, and it's a [[design-engineer]] / [[ds-advisor]] artifact (it must name the real
DS components + tokens, not describe pixels).

> **Tool dependency — preflight first.** Requires the `figma-mcp` capability ([[capability-registry]]).
> Confirm a `mcp__*figma*__*` tool is available; if not, **degrade** — write the spec from a pasted frame +
> exported assets. See [[AGENTS]] → "Capability preflight".

## What a build-able spec covers
- **Layout + responsive intent** — structure, spacing scale, breakpoints/auto-layout behavior.
- **Tokens, not hexes** — pull *variable bindings* (color/space/type tokens), so the spec says `surface.2`,
  not `#1A1A1A`. This is the difference between a reusable spec and a brittle one.
- **Component inventory + states** — which DS components, which variants, every interactive state
  (default/hover/focus/active/disabled/loading/empty/error).
- **Interactions, content, and a11y** — behavior on action, real/edge-case content, and accessibility notes
  ([[a11y-visual]]): roles, focus order, labels, contrast.
- **Open questions** — call out what the design *doesn't* answer rather than guessing.

## Defers to
The Dev-Mode read specifics live in the installed **Figma** skill + MCP; this skill is the workspace *when/why*
and the spec structure. Aligns with the `/figma spec` operation grammar on the [[figma]] hub.

## Related
- hub → [[figma]]
- peer ↔ [[figma-design-to-code]]
