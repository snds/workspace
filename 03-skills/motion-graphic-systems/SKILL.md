---
name: motion-graphic-systems
description: >
  Graphic-system motion: SVG and vector surfaces that move as illustration-in-time
  (masks, clip-path, stroke draw, path morph, group transforms, scan/reveal,
  telemetry loops), plus film/TV/diegetic UI motion and brand graphic systems.
  Use when the conversation touches: SVG animation, SVG mask, clip-path wipe,
  stroke-dashoffset, pathLength, DrawSVG, MorphSVG, vector graphic motion,
  diegetic UI, film UI, HUD motion, playback graphics, okudagram motion,
  display graphic animation, scan line, readout loop, LCARS-style panel motion,
  GMunk-class motion graphics, After Effects to Lottie/Rive for a graphic system.
  Not for product-chrome micro-interactions (motion-transitions), not for
  Disney-feel diagnosis alone (motion-principles), not for library syntax
  (motion-tooling / the /motion hub), and not for judging an existing clip
  (visual-qa-motion).
aliases: [motion-graphic-systems]
triggers:
  - svg animation
  - svg mask
  - clip-path
  - stroke-dashoffset
  - pathLength
  - diegetic ui
  - film ui
  - hud motion
  - graphic system motion
  - playback graphics
  - vector graphic motion
  - display graphic animation
tier: spoke
domain: design
hub: lead-motion-designer
prerequisites: [lead-motion-designer]
related: [gd-display-graphics, motion-tooling, visual-qa-motion, lead-vector-designer, motion-programmatic-video]
defers_to: [framework-02, framework-06, lead-motion-designer, motion]
rigor_role: load-chain
surfaces: ["*"]
spec_version: "2.2"
---

# Motion — Graphic Systems

Specialist lens for motion whose surface **is a graphic system**, not a product
control. Foundations: [[design-foundations]]. Direction: [[lead-motion-designer]].
This spoke covers register, SVG craft, and diegetic/film/brand graphic motion only.

L4 spoke. Judgment still goes through [[visual-qa-motion]] / `/qa`. Code routing
stays on the [[motion]] hub.

## Domain boundary

| Question | Owner |
|---|---|
| Button / modal / page transition in product chrome | [[motion-transitions]] |
| Why an easing feels wrong | [[motion-principles]] |
| Multi-element stagger in a UI list | [[motion-choreography]] |
| Which library and the API | [[motion-tooling]] + [[motion]] |
| How to *draw* the graphic | [[gd-display-graphics]] + [[lead-vector-designer]] |
| How this graphic system *moves* | **this spoke** |
| Remotion / kinetic title card / MP4 from code | [[motion-programmatic-video]] |
| Is the existing motion smooth / safe / right | [[visual-qa-motion]] |

## Name the register first

The motion constitution ([[dc-motion]]) is written for product chrome: purposeful,
compositor-cheap, no decoration. Graphic-system motion is not a waiver of that
law. It is a **different register** of the same law.

| Register | Job of motion | Default cost | Typical surface |
|---|---|---|---|
| **Product chrome** | Orient, respond, explain a control | Compositor only; short | Buttons, drawers, tables |
| **Graphic system** | Keep a composed display *alive* (scan, ready, alarm, telemetry) | Transform/opacity first; stroke/mask when the graphic requires it | HUD, schematic, brand lockup, LCARS-class panel |
| **Diegetic / film UI** | Read at camera distance, survive defocus, play on set | Designed as playback, not as a hover | In-world monitors, holograms, light tables |
| **Look-dev / rejected path** | Prove a register *before* committing production | Disposable | Holo-on-black vs practical playback |

A looping bar on a data table is decoration (constitution refuse). The same bar
on a diegetic status rail is **set dressing that communicates "this system is
live."** If you cannot name the register, default to product chrome and cut the
loop.

**Contrast**

- **Bad:** Apply 200ms ease-out to every LCARS segment because that is the
  enterprise token. The display reads as a website, not a live instrument.
- **Good:** Idle loops stay slow and low-amplitude; story beats (lock, alert,
  transport) get a one-shot with a named peak. Duration follows camera
  distance and story, not the button token.
- **Why:** Okuda's "technology unchained" (Picard archive walkthrough,
  2026 source `6DJDJri-aPI`): the software is so advanced it does not overwhelm.
  Motion that flickers every cell is the opposite of that brief.

## Compose, then animate

A frame that does not read still will not read moving. [[gd-display-graphics]]
owns the still. This spoke owns what changes.

Order:

1. **Still hierarchy** at the intended viewing distance (squint / defocus).
2. **What is allowed to move** (one primary action, optional secondary pulse).
3. **Technique** (transform, mask, stroke, morph) chosen for that action.
4. **Reduced-motion equivalent** that keeps the same information.

GMunk / Kosinski brief on *Oblivion* vs *TRON: Legacy* is the same rule at
feature scale: name the look (elegant 2D vs dense hologram) before picking
Cinema 4D vs After Effects. The tool follows the register.

## SVG technique map

Prefer the lightest tool that can express the action. Native SVG/CSS/WAAPI
before GSAP plugins before Lottie/Rive before a raster movie.

| Action | Technique | Notes |
|---|---|---|
| Move / scale / fade a group | `transform`, `opacity` | Compositor path. Default. |
| Reveal / wipe / scan | SVG `mask` or CSS `clip-path` | Animate the mask, not the artwork. `viewBox` in 0–100 units so the wipe is resolution-independent. |
| Self-drawing line | `pathLength="1"` + `stroke-dasharray` / `stroke-dashoffset`, or GSAP DrawSVG | Measure once; do not reflow `d` every frame. |
| Shape change | GSAP MorphSVG (or matched-point `d` interpolation) | Set `shapeIndex` when the morph twists. Split paths if segment mapping fails. |
| Travel along a guide | GSAP MotionPath / `offset-path` | The path is a guide, not a morph. |
| Hard graphic edges (blinds, LCARS bars) | `shape-rendering="crispEdges"` + 0.05–0.1 unit overlap | Kills 1px hairline gaps from subpixel AA. |
| Designer-authored illustrative loop | Lottie / Rive | Export from AE or a vector tool; optimize; honor reduced-motion. |
| Camera-facing playback for a shoot | Movie / image sequence | Film register. Do not pretend it is a live SVG. |

**Absolute technique bans**

- Animating `width` / `height` / `d` / `fill` on a hot path when a transform or
  mask would do.
- Rasterizing a live vector system into a movie just to get a wipe, then
  shipping the movie in a web product.
- SMIL as the only implementation (limited support; prefer CSS/WAAPI/GSAP).
- Claiming 60fps from a still or from reading the SVG source.

### Masks vs clip-path vs morph

- **clip-path / mask:** the artwork is finished; time reveals it. Use for
  scans, shutters, iris, and "power on."
- **stroke draw:** the line *is* the information. Use for schematics, traces,
  targeting reticles.
- **morph:** the *shape meaning* changes (idle glyph → alert glyph). Do not
  morph to fake a wipe.

Picard look-dev (`Pj3Q6w-Epc4`, Andrew Jarvis): seamless black + holo UI was
a **rejected register**. Seasons 2–3 chose practical playback so original
designers could stay in the language. If a project is in look-dev, record the
rejected path; do not silently mix holo bloom onto a flat LCARS grammar.

## Film / playback craft (transferable)

From Todd Marks / Images on Screen (`JiAeZfBbPHk`) and Twisted Media (C4D +
Illustrator + After Effects, Okuda as guide):

- **Practical beats post when the actors must see it.** Dead backlit
  transparencies (TNG helm) became live OLEDs so button-presses do something.
- **Light the graphic.** Playback + panel-back light must blend. A perfect
  SVG on a black rectangle will look pasted.
- **OLED / high-contrast blacks** are a material choice, not a color token.
  Black levels and off-axis shift change the design.
- **Mix 3D telemetry with flat grammar without dissolving the grammar.**
  Marks: LCARS is "not supposed to be especially fancy"; 3D sits *inside*
  the flat system, it does not replace it.
- **Polar motion** (Okuda archive): a spinner + gel behind a static Kodalith
  is analog looping. Digital equivalent: a slow phase-offset on a mask or
  gradient, not a bounce on every label.

GMunk (TRON holographic sequences; *Oblivion* light table): sketch with the
director, prototype 2D in Illustrator → After Effects, escalate to C4D
MoGraph only when the brief is 3D. In-camera playback when the schedule
allows. Audio-responsive graphics are a named choice, not a default.

## Accessibility in this register

[[motion-accessibility]] still wins. Graphic-system motion is *more* likely
to loop and occupy large area.

- Essential meaning cannot live only in the loop. A reduced-motion still must
  still say READY / ALERT / SCANNING.
- Large-field flicker and scanlines are vestibular risk. Keep amplitude low;
  never strobe.
- Film playback on a physical set is not an excuse to ship the same loop
  unbounded in a product.

## Execution protocol

1. Name register + communication job + viewing distance.
2. Lock the still with [[gd-display-graphics]] (or refuse to animate a broken
   composition).
3. List moving layers and their jobs (primary / secondary / idle).
4. Pick the lightest technique from the map. Load [[motion-tooling]] or
   [[motion]] only for the implementation.
5. Design the reduced-motion still in the same pass.
6. Prove from recorded playback ([[reference-video-review]], then
   [[visual-qa-motion]]). A still is not a pass.

### Done-gates

- Register named; idle vs story-beat motion separated.
- Still reads at intended distance without motion.
- Technique matches the action (mask/stroke/morph/transform).
- Reduced-motion equivalent carries the same information.
- Frame budget measured when the surface is interactive; film playback
  named as playback, not as "60fps UI."

### Absolute bans

- Treating graphic-system motion as decoration to be stripped by default,
  *or* treating product chrome as a place for playback loops.
- Animating every cell because the reference "looks busy."
- Judging film UI from a product-chrome duration table.
- Calling a look-dev hologram the production language without an explicit
  register change.

## Outputs

- Register + job list (idle / beat / reduced-motion).
- Technique map for the moving layers.
- Pointer to the still (IR, northstar, or composed SVG).
- Handoff to [[motion]] with tokens, not adjectives.

## Defers-to

- Workspace doctrine: [[13-domain-rigor-stack]] · [[02-ui-ux-operational-framework]] · [[lead-motion-designer]] · [[motion]]
- Plugin/base depth: `gsap-scrolltrigger`, `lottie-animations`, `rive-interactive`, `animejs` — technique only

## Related
- hub → [[lead-motion-designer]]
- peer ↔ [[gd-display-graphics]] · [[motion-tooling]] · [[visual-qa-motion]] · [[lead-vector-designer]]
- peer ↔ [[motion-programmatic-video]]
