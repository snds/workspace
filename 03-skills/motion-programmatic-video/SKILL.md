---
name: motion-programmatic-video
description: >
  Motion graphics as a delivered video or title card: Remotion, Motion Canvas,
  Manim, After Effects, kinetic typography, beat-sync, safe areas, and the
  stills-before-encode verify loop. Use when the conversation touches: Remotion,
  Motion Canvas, Manim, programmatic video, data-driven video, kinetic typography,
  split-text title card, lyric card, explainer video, beat sync, title-safe,
  frame-accurate render, CSV-to-MP4. Not for product-chrome transitions
  (motion-transitions), not for live SVG/HUD systems (motion-graphic-systems),
  not for library syntax of GSAP/Framer (motion-tooling / /motion), and not for
  judging a clip that already exists (visual-qa-motion).
aliases: [motion-programmatic-video]
triggers:
  - remotion
  - motion canvas
  - manim
  - programmatic video
  - kinetic typography
  - title card
  - beat sync
  - data-driven video
tier: spoke
domain: design
hub: lead-motion-designer
prerequisites: [lead-motion-designer]
related: [motion-graphic-systems, motion-tooling, motion, visual-qa-motion, gd-brand-identity]
defers_to: [framework-02, framework-06, lead-motion-designer, motion]
rigor_role: load-chain
surfaces: ["*"]
spec_version: "2.2"
---

# Motion — Programmatic Video

Specialist lens for motion whose **deliverable is a video or title card**,
not a product control. Foundations: [[design-foundations]]. Direction:
[[lead-motion-designer]]. Implementation of UI libraries stays on [[motion]].

L4 spoke. Judgment of an existing clip goes through [[visual-qa-motion]] /
[[reference-video-review]]. Do not vendor marketplace video packs
(TikTok / Reels / ecommerce templates).

## Domain boundary

| Question | Owner |
|---|---|
| Button / modal / page transition | [[motion-transitions]] |
| Live SVG / HUD / diegetic panel | [[motion-graphic-systems]] |
| Why an easing feels wrong | [[motion-principles]] |
| UI library API (GSAP, Framer, Lottie) | [[motion-tooling]] + [[motion]] |
| Mark construction, IP, raster→vector | [[gd-brand-identity]] |
| Render an MP4/GIF from code or AE | **this spoke** |
| Is the existing clip smooth / safe | [[visual-qa-motion]] |

Name the register first ([[dc-motion]]). This spoke is **programmatic video**.
A looping mesh behind a dashboard is product chrome (usually refuse). The same
loop as a 6-second brand sting is this register.

## Surfaces — cheapest that ships the frame

Walk down; stop at the first that fits. Tool follows the artifact.

| Need | Surface |
|---|---|
| One-off title / logo sting, designer-authored | After Effects → Lottie/Rive only if it must play in-app |
| Versioned, data-driven, CI-renderable React video | Remotion (`useCurrentFrame`, clamp `interpolate`) |
| Code-first explainer with a canvas timeline | Motion Canvas |
| Math / educational proof animation | Manim |
| In-page UI motion | Not this spoke → [[motion]] |

Do not install a video renderer to fade a button.

## Shot before motion

Compose the still, then animate. Laws absorbed from shot-composition craft
(iart / classical framing), not from a pack:

1. **One focal point** per beat. Rank size > contrast > color > position.
2. **Title-safe.** Keep type, marks, and faces inside the margin for every
   target aspect. 16:9 ~5% all sides. 9:16: top ~12–14%, bottom ~18–20%.
3. **Restack, do not crop** when adapting 16:9 → 9:16. Focal stays in the
   center band; secondary elements reflow.
4. **One camera move per beat.** Push *or* pan *or* parallax. Stacked moves
   read as chaos.
5. **1/3 travel.** No element crosses more than a third of the frame without
   an intermediate keyframe or a paired scale/opacity change.
6. **Depth roles.** Background = ambient (slow), mid = support, foreground =
   the move the eye follows. Same speed on every layer is "the template moved."

**Contrast**

| Bad | Good | Why |
|---|---|---|
| Phone, headline, and logo all centered; all three slide left at 1.0×; 9:16 is a side crop | Phone on a thirds power point; bg 0.2× / mid 0.6× / fg 1.2×; one push; 9:16 restacks type above the phone | Hierarchy and safe area survive the crop; depth is assigned, not guessed |
| Character-stagger a 12-word headline on a settings screen | Word or line stagger on a title card; UI type does not kinetic-dance | Kinetic type is a video register. In product chrome it is decoration |

## Kinetic type

Allowed on title cards, stingers, lyric/caption videos. Default unit is
**word or line**, not character, unless the brief is a single word or a
logo lockup. Variable-font weight can carry the motion without a slide.

In product chrome, type motion is a [[motion-transitions]] question: keep it
near-imperceptible or omit it.

## Deliver-and-verify

Video is frame-deterministic when time is the only input. Prove stills
**before** encoding.

1. Render frames at start, mid, and last (`durationInFrames - 1`).
2. Inspect each still: copy exact, numbers bound, type inside safe area,
   no missing font, no off-canvas crop.
3. Encode the MP4/GIF only after those stills pass.
4. For batch/CSV: prove **one** representative props set first.

**Determinism bans:** `Date.now()`, `Math.random()`, rAF timers. Seeded
random only. Bake beat timestamps offline; do not analyze audio at render
time (headless has no clock).

Remotion specifics stay in the Remotion docs. This spoke owns the
**contract**: frame-driven, clamped interpolation, shipped props (not just
defaults), stills-before-encode.

## Brand and IP

Logo stings load [[gd-brand-identity]] first. Do not animate a mark that
has no static system. AI-generated marks are testimony until Bezier cleanup
and IP review land.

## Execution protocol

1. Name register = programmatic video (or refuse and send to chrome / graphic-system).
2. Lock aspect, fps, duration, and the still (focal + safe area + restack plan).
3. Pick the cheapest surface from the table.
4. Animate the few layers that earn motion. 1/3 travel. One camera move.
5. Reduced-motion equivalent for any in-app playback of the same graphic.
6. Stills at 0 / mid / end, then encode. Playback review via
   [[reference-video-review]] then [[visual-qa-motion]].

### Done-gates

- Register named; artifact is a video or title card, not a control.
- Still reads without motion; critical content inside title-safe on every aspect.
- Surface chosen from the table; no extra renderer.
- Stills at start/mid/end inspected against the shipped props.
- Encoded file plays; numbers and type match the stills.
- No unseeded randomness; beats are baked if audio is in the brief.

### Absolute bans

- Vendoring a social-video skill pack as workspace doctrine.
- Encoding before the three stills pass.
- Cropping 16:9 to 9:16 and calling it adapted.
- Kinetic character-stagger on dense product chrome.
- Judging an MP4 from a single poster frame.

## Outputs

- Frame spec (aspect, fps, duration) + still plan (focal, layers, safe areas).
- Surface + verify receipt (paths to the three stills + the encode).
- Handoff to [[motion]] only when the same graphic must also run as in-page UI.

## Defers-to

- Workspace doctrine: [[13-domain-rigor-stack]] · [[02-ui-ux-operational-framework]] · [[lead-motion-designer]] · [[motion]]
- Plugin/base depth: Remotion, Motion Canvas, Manim, After Effects, `lottie-animations` — technique only

## Related
- hub → [[lead-motion-designer]]
- peer ↔ [[motion-graphic-systems]] · [[motion-tooling]] · [[motion]] · [[visual-qa-motion]] · [[gd-brand-identity]]
