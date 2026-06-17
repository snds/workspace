---
name: figma-design-to-code
description: >
  Translate a Figma design into production code with high visual fidelity — read the selected frame
  via the Figma MCP (layout, tokens, components, assets) and generate framework code that matches it
  1:1, mapped to the project's design-system components rather than raw CSS. Use when the user gives a
  Figma URL/selection and wants it built. The reasoning lens is design-engineer; the mechanical read
  is the Figma Dev Mode MCP. Triggers: implement design, figma to code, build this component, generate
  code from figma, design to code, 1:1 fidelity, figma URL implement.
aliases: [figma-design-to-code, figma-implement-design]
triggers: [implement design, figma to code, build this component from figma, generate code from figma, design to code, 1:1 fidelity, figma url implement, dev mode handoff]
tier: spoke
hub: figma
domain: design
prerequisites: [figma]
requires: [figma-mcp]
spec_version: "2.1"
---

# Figma — Design to Code

Turn a Figma frame into production component code that matches it visually *and* uses the real design
system — not pixel-pushed one-off CSS. This is the inverse of [[figma-canvas-designer]] (which authors
*on* the canvas); here the canvas is the source and **code is the output**. Reason about it through
[[design-engineer]] (design + code in one lens) and [[ds-advisor]] (which component/token is correct).

> **Tool dependency — preflight first.** Requires the `figma-mcp` capability ([[capability-registry]]).
> Confirm a `mcp__*figma*__*` tool is available; if not, **degrade** — ask the user to paste the frame +
> specs or export assets, and implement from those. See [[AGENTS]] → "Capability preflight".

## The workflow
1. **Read the design, don't guess it** — pull layout, spacing, type, color *variables/tokens*, component
   instances, and assets from the selection via the Figma MCP. Variable bindings tell you the *intended
   token*, not just a hex value.
2. **Map to the design system first** — every frame node should resolve to an existing DS component +
   tokens ([[ds-advisor]]); only fall to custom markup where no component exists. A 1:1 pixel match built
   from raw divs is a failure, not a success.
3. **Generate, then verify visually** — produce the code, then compare against the frame
   ([[visual-qa-toolkit]] SSIM/diff, or a [[vis-vlm-multimodal]] critique) and close the gaps. Fidelity
   is *measured*, not asserted.
4. **Honor framework + a11y conventions** — match the project's component patterns and accessibility
   ([[a11y-visual]]); don't invent prop names or break keyboard/semantics.

## Defers to
The mechanical Dev-Mode read/codegen specifics live in the installed **Figma Dev Mode** skill + the Figma
MCP tools; this skill is the workspace *when/why* and the DS-correct mapping discipline. For Code Connect
(component → snippet mapping) use [[figma-code-connect]]; for spec/PRD extraction use [[figma-design-specs]].

## Related
- hub → [[figma]]
- peer ↔ [[figma-code-connect]] · [[figma-design-specs]]
