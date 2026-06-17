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
spec_version: "2.1"
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

## Defers to
The exact `generate_diagram` call constraints + per-type guidance live in the installed **Figma** diagram
skill + MCP; this skill is the workspace *when/why* and type selection. Part of the [[figma]] hub's grammar.

## Related
- hub → [[figma]]
