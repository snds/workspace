---
name: figma-diagramming
description: >
  Generate editable FigJam diagrams from Mermaid — flowcharts, architecture diagrams, sequence/decision
  flows — via the Figma MCP diagram tool, then refine on the board. Use when the user wants a diagram
  *in Figma/FigJam* (not a static image): system architecture, user flow, data flow, org/process maps.
  Load before any diagram-generation MCP call. Triggers: figjam diagram, generate diagram, mermaid to
  figma, flowchart in figma, architecture diagram, sequence diagram, user flow diagram.
aliases: [figma-diagramming, figma-generate-diagram]
triggers: [figjam diagram, generate diagram, mermaid to figma, flowchart in figma, architecture diagram, sequence diagram, user flow diagram, process map figjam]
tier: spoke
hub: figma
domain: design
prerequisites: [figma]
requires: [figma-mcp]
defers_to: [framework-13, figma]
spec_version: "2.2"
---

# Figma — Diagramming (Mermaid → FigJam)

Produce an *editable* diagram on a FigJam board from Mermaid syntax — usable for architecture, flows, and
process maps that the team can then rearrange and annotate. Distinct from the other figma spokes: this is
communication/visualization, not UI design or codegen.

> **Tool dependency — preflight first.** Requires the `figma-mcp` capability ([[capability-registry]]).
> Confirm the diagram MCP tool is available; if not, **degrade** — hand the user Mermaid source (or a
> static SVG) they can paste/import. See [[AGENTS]] → "Capability preflight".

## Get it right the first time
- **Is a diagram the right artifact?** A flow/architecture/sequence → yes. A data viz or a UI layout → no
  (use a chart or [[figma-canvas-designer]]).
- **Pick the diagram type to the intent** — flowchart for process, sequence for interactions over time,
  architecture for components/systems. The type changes the Mermaid grammar and the layout result.
- **Author clean Mermaid** — valid syntax, sensible node labels, not too dense; the tool renders what you
  give it, so malformed/overstuffed Mermaid produces a messy board.
- **Refine on the board** — generation is the start; expect to regroup/relabel in FigJam after.

## Type selection

The diagram type is a communication decision, not a syntax preference. Pick from what the reader has
to be able to *do* with it:

| The reader needs to | Type | Mermaid grammar |
|---|---|---|
| Follow a process, including branches and loops | Flowchart | `flowchart TD` / `LR` |
| See who talks to whom, in what order, over time | Sequence | `sequenceDiagram` |
| Understand what the parts are and how they connect | Architecture (flowchart with subgraphs) | `flowchart` + `subgraph` |
| See the lifecycle of one thing through its states | State | `stateDiagram-v2` |
| See a data or entity structure | ER / class | `erDiagram` / `classDiagram` |
| See when things happen relative to each other | Timeline / Gantt | `timeline` / `gantt` |

Layout direction is part of the message: `LR` reads as progression through time or a pipeline, `TD`
reads as decomposition or hierarchy. Choosing the wrong one makes a correct diagram feel wrong.

## Legibility gate

A diagram is a delivery artifact, so the delivery playbook applies
([`02-shared-references/delivery-playbooks/02-diagrams-and-flows.md`](../../02-shared-references/delivery-playbooks/02-diagrams-and-flows.md)),
and the request's own words decide the medium: someone who asked for a diagram is not satisfied by
prose. Before handing the board over:

- **Node count is readable.** Past roughly 15 to 20 nodes on one board, split into a parent view
  plus detail views instead of shrinking everything.
- **Labels are nouns and verbs, not sentences.** Long labels blow out the auto-layout and force the
  reader to read rather than scan.
- **One crossing convention.** If edges cross, they cross for a reason; rearrange rather than
  letting the generator's first pass stand.
- **The critical path is visually distinct** (order, position, or grouping), so the main story is
  legible before the exceptions are.
- **It survives the export.** Check the rendered board at the size it will be viewed, per
  [#10 Perception Integrity](../../01-frameworks/10-perception-integrity.md), before calling it done.

## Defers to
The exact `generate_diagram` call constraints + per-type guidance live in the installed **Figma** diagram
skill + MCP; this skill is the workspace *when/why* and type selection. Part of the [[figma]] hub's grammar,
whose rigor obligations come from [#13 Domain Rigor Stack](../../01-frameworks/13-domain-rigor-stack.md):
plugin depth supplies the mechanics, the workspace owns the type-selection and legibility gates above.

## Related
- hub → [[figma]]
