---
name: design-foundations
description: >
  The context-free first principles of design — visual perception, color,
  typography, composition, and hierarchy — that hold true in any medium (print,
  screen, motion, data, 3D, game). Load this BEFORE any specialty design hub or
  spoke so specialty work inherits the principles instead of re-deriving them.
  Triggers whenever design, visual, UI, UX, layout, color, type, composition,
  hierarchy, or aesthetic judgment is in play.
aliases: [design-foundations]
triggers: [design, visual design, ui, ux, layout, color, typography, composition, hierarchy, contrast, gestalt, aesthetic, design critique]
tier: foundation
domain: design
surfaces: ["*"]
spec_version: "2.0"
---

# Design Foundations

The shared root beneath every design discipline. These are the principles that are equally true for a
poster, a dashboard, a title sequence, a chart, and a game HUD. Specialty hubs (UI, graphic, UX, type,
motion, information, 3D) apply them **in a medium**; this hub owns the **why it's true anywhere**.

**Content-ownership rule:** if a statement is equally true across print, screen, motion, data, and 3D,
it belongs in a foundation spoke. If it names a medium-specific constraint (pixel grid, CMYK gamut,
dark-mode surface lightness, frame rate), it belongs in the specialty spoke. See [[workspace-ontology]].

## Loading

This foundation loads **before** the discipline hub and the specialty spoke. Any design request resolves
the chain `design-foundations → <discipline hub> → <specialty spoke>` (a color spoke also pulls in
[[found-color]] first). The five foundation spokes are loaded individually as the topic requires — don't
load all five for a narrow question.

## The five foundations

| Spoke | Owns (context-free principle) |
|---|---|
| [[found-perception]] | Gestalt laws, figure/ground, pre-attentive processing, visual weight, optical vs. mathematical equality — the eye as the validator |
| [[found-color]] | Perceptual color (OKLCH), harmony systems, simultaneous contrast, color-vision deficiency mechanics, proportion (60-30-10) |
| [[found-typography]] | Letterform anatomy, classification logic, modular scales, measure/leading relationships, type as hierarchy |
| [[found-composition]] | Grid theory, balance, rhythm, proximity/alignment, white space, the relationship between elements |
| [[found-hierarchy]] | How scale/weight/color/position/space encode priority; contrast as the engine of hierarchy |

## Core convictions (apply across all spokes)

- **Contrast is the engine.** Nothing reads as important without something to be more important *than*.
- **The eye outranks the math.** Optical adjustment beats measured equality (overshoot, spacing, alignment).
- **Restraint scales; decoration doesn't.** Authored constraint reads as intentional; generic abundance reads as noise.
- **Evaluate in context, never in isolation.** Color, weight, and spacing are all relative to their neighbors.

## Related
- spoke → [[found-perception]] · [[found-color]] · [[found-typography]] · [[found-composition]] · [[found-hierarchy]]
- applies-in ← [[lead-ui-designer]] · [[lead-graphic-designer]] · [[lead-ux-designer]] · [[lead-type-designer]] · [[lead-motion-designer]] · [[lead-information-designer]] · [[lead-3d-designer]]
