---
name: realtime-render-performance
description: >
  The frame-performance and input-latency spine for web-3D games — the doctrine and engineering that
  every rendering system sits on, whatever the target frame rate. 60 FPS is the FLOOR (not the goal);
  render uncapped by default (higher FPS = smoother + lower latency), expose an optional user frame cap
  in settings to reallocate GPU to other engine work or cut power/heat; and treat input-to-photon
  latency as a co-equal target. Covers the frame-budget method, temporal upsampling (TAAU) + dynamic
  resolution, GPU-driven culling, reversed-Z + logarithmic depth, df64, input-latency reduction, and
  the honest WebGPU capability map. Load BEFORE any hero-body / heavy-scene renderer. Triggers:
  frame rate, 60fps, frame budget, input latency, frame pacing, frame cap, vsync, temporal upsampling.
aliases: [realtime-render-performance]
triggers: [frame rate, framerate, 60fps, 120fps, frame budget, frame time, frame pacing, input latency, input lag, input delay, frame cap, fps cap, vsync, refresh rate, responsiveness, taau, temporal upsampling, temporal anti-aliasing, dynamic resolution scaling, drs, gpu profiling, timestamp query, reversed-z, depth precision, df64, double precision emulation, hi-z occlusion culling, gpu-driven rendering, indirect draw, shader-f16, webgpu performance, overdraw]
tier: spoke
hub: lead-game-developer
domain: game
prerequisites: [webgpu-advanced-rendering, game-scale-traversal]
related: [glsl-shader-architect, threejs-vfx-atmosphere]
surfaces: ["*"]
spec_version: "2.0"
---

# Realtime Render Performance — the frame & latency spine (web-3D, WebGPU)

The performance doctrine and engineering that every rendering system in a web-3D game sits on. This
skill owns **how to hold the frame and keep the game responsive**; the renderers that build on it
([[planetary-terrain-lod]], [[atmospheric-scattering-and-clouds]], [[stellar-and-relativistic-hero-bodies]],
and any heavy scene) own **what to render**. It is the project-agnostic performance spine — Legion is its
most demanding consumer, not its scope. It is the frame-budget/latency complement to
[[webgpu-advanced-rendering]] (general API mechanics) and extends the precision spine of
[[game-scale-traversal]] with the temporal/latency interaction.

## Performance doctrine (applies to ALL game work)
1. **60 FPS is the floor, not the goal.** 16.7 ms is the *worst acceptable* frame — design so the common
   case beats it comfortably. Sustained sub-60 means the experience is failing, not merely imperfect.
   Judge on the **worst frame**, not the average: one 20 ms frame under vsync is felt as a hitch even at
   a 10 ms mean.
2. **Uncapped by default — higher is better.** Never self-impose a lower frame cap. Render as fast as the
   display allows. Higher FPS buys both smoother motion **and** lower input latency, and both are felt.
   (In-browser reality: `requestAnimationFrame` locks to the display refresh — 60/120/144 Hz — so
   "uncapped" in a browser means *reach the refresh rate*, not exceed it; only a native build can run past
   refresh. Don't hard-wire a 60 cap into a game that could run at 144.)
3. **Expose an optional user frame cap in settings.** Let the player choose a target (e.g. 30 / 60 / 90 /
   120 / 144 / Unlimited). A cap deliberately hands frame budget **back**: it frees GPU/CPU headroom for
   other engine work (simulation, AI, world streaming, background compute) and cuts power draw, heat, fan
   noise, and battery use — real wins on laptops and in sim-heavy games where a player may prefer spending
   the budget on world depth over raw FPS. Implement as a **target-frame-interval throttle** (schedule the
   next frame to the target period), never a hard busy-wait, and cap at the *frame-start* boundary so input
   is still sampled late (below).
4. **Low input latency is a co-equal target.** Frame rate and input-to-photon latency are distinct axes — a
   game can run at 60 FPS and still feel laggy. Minimize the whole input→display pipeline (see below).
   Uncapping FPS is itself a latency win (fresher frames, shorter present interval), which is part of why
   the default is uncapped.

## The frame budget (generalized)
Budget = `1000 / target_fps` minus **~1.5–2 ms** of in-browser overhead you don't control (compositor
deadline, `rAF` jitter, JS GC, queue-submit). Plan against the *real* budget, and reserve headroom above
the floor:

| Target | Nominal frame | Real in-browser GPU budget |
|---|---|---|
| 60 FPS (floor) | 16.7 ms | ~14–15 ms |
| 90 FPS | 11.1 ms | ~9 ms |
| 120 FPS | 8.3 ms | ~6.5 ms |
| 144 FPS | 6.9 ms | ~5 ms |

Design the renderer so the **floor** holds on the target's weakest supported GPU (integrated), then let
uncapped mode + DRS spend any surplus on more FPS. The frame breaks on **fill-rate + procedural-ALU/
bandwidth + temporal disocclusion**, in that order — rarely on geometry/precision/culling, which are cheap.

## Input latency — the input→photon pipeline
Latency is the sum of: input sampled → simulation step → render → GPU queue → present → scanout. Each stage
adds delay; the total is what the hand feels. Levers:
- **Sample input as late as possible** in the frame — right before the sim/render step, not at frame start
  (which strands input behind a whole frame of work).
- **Keep frames-in-flight low (1–2).** A deep GPU render-ahead queue trades latency for throughput; don't
  over-buffer. In WebGPU, submit tight and don't pile up queued work.
- **Decouple simulation rate from render rate** with a fixed-timestep sim + interpolation for stability —
  but know it costs up to one sim-step of latency. For latency-critical input (camera, aim), fold the
  freshest input into the *render* frame directly rather than waiting for the next sim tick.
- **Uncapped FPS lowers latency** intrinsically (each frame carries newer input, present interval shrinks).
- **vsync / present-mode tradeoff.** vsync kills tearing but adds up to one refresh of latency. In-browser
  you are effectively vsync'd via `rAF` with no tearing control; native engines can offer immediate/mailbox
  present modes to trade a little tearing for latency.
- **A naive frame cap can ADD latency** if it sleeps at the wrong point — throttle to the target *frame-start*
  interval and still sample input late.
- **Measure it, don't guess.** Instrument input-timestamp → first present of the response (`event.timeStamp`
  in-browser; PresentMon / Reflex-analyzer class tools on native). Latency regressions are invisible to an
  FPS counter.

## Depth & precision spine
- **Reversed-Z on `depth32float`** (near→1, far→0, `GREATER`, clear = 0.0) — the near-free modern default
  (Reed: ~0 % indistinguishable-depth vs 77 % for standard float32). Keep it.
- **Logarithmic depth per-vertex** across a wide scale range; **per-fragment only on near shells** — writing
  `frag_depth` disables early-Z, and WebGPU has **no conservative-depth escape hatch** (WGSL gpuweb#5342 not
  shipped). For very wide ranges prefer **depth-range cascades / multi-frustum splitting**. Validate at the
  *closest* scale, not just the far one.
- **Floating origin's perf consequence:** an origin shift is a **full-frame temporal-history invalidation**
  *and* a **Hi-Z stale-depth skip**. On re-center, invalidate the TAAU history and skip Hi-Z next frame.
- **df64 (double-single) — last resort, surgically scoped, with a hazard.** Only for camera-relative
  translation and extreme-zoom vertex/UV math. It is **not** "pure arithmetic": it depends on the compiler
  NOT reassociating or FMA-contracting the (hi+lo) terms; WGSL doesn't guarantee IEEE-754 non-association,
  and Tint fast-math can silently collapse df64 to f32 on some backends. **Validate per backend.**

## Temporal upsampling — a co-development bet, not a drop-in
- **TAAU is the only in-browser temporal-upscale option** (no DLSS/FSR-frame-gen/tensor access). Three.js
  `TAAUNode` (WebGPU/TSL, #33359, since Apr 2026) exists but upstream flags its resolve as not
  production-sharp; you co-develop it. MSAA off.
- **It fails on motion-vector-less content** — procedural surface noise, volumetrics, particles, lensed
  backgrounds — falling back to full-res shading exactly where you wanted the upscale.
- **FSR2-style reactive + disocclusion masks are the hard 70 %** — a multi-month fork, not a graft.
- **Separate temporal histories** for beauty / volumetrics / geodesics; volumetrics can't ride the beauty
  TAAU and composite after resolve.

## Dynamic resolution scaling (DRS) — the first, cheapest release valve
App-level (no WebGPU DRS API): a rolling GPU-frame-time signal (`timestamp-query` + CPU-timer fallback)
drives internal color/depth/velocity scale between ~1.5×/axis (~44 % pixels) and ~2.0×/axis (~25 %), with
**hysteresis + rate-limiting** to avoid hunting. **Pre-allocate at max size, render to a sub-rect** to avoid
allocation churn. DRS is how uncapped mode spends surplus on quality, and how the floor is defended on weak
hardware.

## GPU-driven culling (deprioritized at close zoom)
Compute frustum cull + compaction + `drawIndexedIndirect` is core WebGPU (1:1 from Vulkan) — near-free at
close zoom on one body (few instances); it matters for the **fly-in / many-object scene**. Hi-Z occlusion
needs a **hand-rolled min-reduction pyramid** (no `SAMPLER_REDUCTION_MODE_MIN`); skip it the frame after an
origin shift.

## Cheap wins & the instrument
- **`shader-f16`** (Chrome 120+) — a major fill/ALU/bandwidth lever for noise-heavy procedural shading;
  feature-detect (Qualcomm caveat gpuweb#5006).
- **`timestamp-query` profiling + overdraw budgeting** is the instrument that makes DRS, the frame cap, and
  every budget line real. Every technique ships with a measurement, not an averaged estimate (framework #06
  Proofboard).

## Do NOT plan on (the dead-path list)
Mesh shaders · geometry shaders · tessellation shaders · hardware VRS · hardware sparse textures (emulate
virtual texturing via a page-table indirection texture) · guaranteed multi-draw-indirect (Chrome 131
experimental behind a flag — feature-detect) · ML upscalers · WGSL `fp64`. Do not prototype any of them.

## Failure modes to avoid
Self-imposed low frame cap (leaves FPS/latency on the table) · a throttle that adds latency by sleeping
late · judging on average not worst frame · TAAU ghosting on MV-less content · disocclusion shimmer at the
horizon · origin-shift history corruption · log-depth-per-fragment early-Z loss (unrecoverable in-browser) ·
depth-fighting at scale without tight origin / df64 · deep render-ahead queue inflating input latency ·
sampling input at frame start · DRS oscillation without hysteresis · render bundles used while GPU-bound
(they only cut CPU encoding) · assuming multi-draw-indirect / timestamp-query is present.

## Cited sources
- Reed, *Depth Precision Visualized* (2015) — https://www.reedbeta.com/blog/depth-precision-visualized/
- Kemen (Outerra), *Maximizing Depth Buffer Range and Precision* (2012) — https://outerra.blogspot.com/2012/11/maximizing-depth-buffer-range-and.html
- Godot / Verschelde et al., *Emulating Double Precision on the GPU* (2022) — https://godotengine.org/article/emulating-double-precision-gpu-render-large-worlds/
- vkguide.dev, *GPU Driven Rendering: Compute-based Culling* — https://vkguide.dev/docs/gpudriven/compute_culling/
- three.js, *TAAUNode* (#33359) + `webgpu_upscaling_taau` (2026) — https://github.com/mrdoob/three.js/issues/33359
- AMD GPUOpen, *FidelityFX Super Resolution 2* (reactive/disocclusion masks) — https://gpuopen.com/manuals/fidelityfx_sdk/techniques/super-resolution-temporal/
- Shehata, *How to use WebGPU timestamp query* (2023) — https://omar-shehata.medium.com/how-to-use-webgpu-timestamp-query-9bf81fb5344a

## Related
- hub → [[lead-game-developer]]
- peer ↔ [[webgpu-advanced-rendering]] · [[game-scale-traversal]]
