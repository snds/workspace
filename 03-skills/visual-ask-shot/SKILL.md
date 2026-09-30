---
name: visual-ask-shot
description: >
  Before any visual or structural UI question to Sean, attach a screenshot of
  the real surface. If the issue or PR already has a shot, show it with the
  question. If it does not, capture from the correct source — Storybook for a
  CDS primitive, the running host for nest/host chrome, Figma when that is the
  source of truth. Do not ask Close placement, hover wells, stacking, spacing,
  or “does this look right” as text-only. Use on plans, PR reviews, issues,
  canvases, and any visual call. Guaranteed: no picture, no visual question.
aliases: [visual-ask-shot, screenshot-with-the-question, visual-question-shot]
triggers:
  - screenshot
  - visual
  - Close
  - hover
  - stacking
  - lightbox
  - photo viewer
  - does this look
  - placement
  - spacing
  - overlay
  - sheet
  - dialog
  - chip
tier: cross-cutting
domain: design
related: [plain-voice, plan-ahead, native-visual-eval, lead-visual-qa, visual-first-documentation]
surfaces: ["*"]
spec_version: "2.2"
---

# Visual asks carry a picture

Sean answers visual and structural calls from pixels, not from class names.

This is not a QA verdict ([[lead-visual-qa]], [[visual-prove-engine]]). It is
the rule that a visual *question* ships with a shot of the thing being decided.

## When to use

Any question about placement, stacking, hover, spacing, chrome, Close, a
viewer, or “how should this look.” Plans and canvases included. Employer
chats included.

## When NOT to use

API names, export maps, catalog adds with no visible change, git sequence.

## Guaranteed run

Before the question leaves the reply:

1. **Already attached?** Issue, PR, or the user sent a shot. Put that image
   next to the question. Do not recapture unless it is the wrong surface.
2. **Nothing attached?** Capture now. Do not ask first and promise a shot later.

## Correct source

| The question is about… | Capture from |
|---|---|
| A CDS primitive (Dialog lightbox, Object Chip, Button) | Storybook story of that wrap, opened to the state |
| Nesting or host chrome (viewer inside a sheet, header History) | The running host (prototype) at that route |
| A Figma property or unpublished library change | The Figma node, not a code story |

Wrong source is a miss. A Storybook card is not a sheet nest. A table thumb is
not the photo viewer.

## Capture

Use the browser tools on this surface. Open the route, reach the state, shoot
the viewport that shows the control. Unlock when done.

If the server is down, start it. If you cannot reach the surface, say so and
do not ask the visual question as if the picture existed.

## With the question

Put the shot first. Then the call in plain voice ([[plain-voice]]). Name what
to look at in the picture (“Close sits 8px outside the top-right of the
picture, not in the screen corner”).
