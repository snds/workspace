---
name: realtime-render-performance-90fps
description: >
  Holding a 90 FPS / ~11 ms frame in a Three.js + WebGPU browser target at very close zoom on a
  hero body — the frame-budget spine every hero-body renderer sits on. Temporal upsampling (TAAU)
  and dynamic resolution as one system, GPU-driven culling, reversed-Z + logarithmic depth,
  floating-origin-as-history-invalidation, df64 emulation, and timestamp-query profiling — plus
  the honest WebGPU capability map (what is NOT available in browsers). Load this BEFORE the three
  body skills; they own *what* to render, this owns *how to hold the frame*. Triggers: 90fps, frame
  budget, temporal upsampling, dynamic resolution, GPU profiling, reversed-z, df64, occlusion culling.
aliases: [realtime-render-performance-90fps]
triggers: [90fps, 90 fps, frame budget, frame time, taau, temporal upsampling, temporal anti-aliasing, dynamic resolution scaling, drs, gpu profiling, timestamp query, reversed-z, depth precision, df64, double precision emulation, hi-z occlusion culling, gpu-driven rendering, indirect draw, shader-f16, webgpu performance, overdraw]
tier: spoke
hub: lead-game-developer
domain: game
prerequisites: [webgpu-advanced-rendering, game-scale-traversal]
related: [glsl-shader-architect, threejs-vfx-atmosphere]
surfaces: ["*"]
spec_version: "2.0"
---

# Realtime Render Performance — the 90 FPS spine (WebGPU, in-browser)

The frame-budget, temporal, and precision discipline that the three hero-body skills
([[planetary-terrain-lod]], [[atmospheric-scattering-and-clouds]], [[stellar-and-relativistic-hero-bodies]])
all depend on. This skill owns **how to hold the frame**; they own **what to render**. It is the
Legion-specific, honest, 90-FPS-at-close-zoom complement to [[webgpu-advanced-rendering]] (general API
mechanics) and extends the precision spine of [[game-scale-traversal]] with its temporal/DRS interaction.

## Scope and Domain Boundary
- **This skill:** the 90 FPS budget methodology, temporal-upsampling reality, dynamic resolution, GPU
  profiling, and the depth/precision spine for close-zoom hero bodies.
- → General compute/indirect/storage-buffer mechanics, clustered lighting, GPU particles: [[webgpu-advanced-rendering]].
- → The galaxy→surface scale shells, floating origin, and log/reversed-Z *architecture*: [[game-scale-traversal]]
  (this skill adds the temporal consequence of an origin shift).
- → Terrain, atmosphere, stellar, and black-hole rendering: the three body skills above.

## The honest budget (read this first)
**You do not get 11.1 ms in-browser.** Compositor deadline + `requestAnimationFrame` jitter + JS GC +
queue-submit overhead consume ~1.5–2 ms, leaving **~8–9 ms of real GPU budget**. 90 Hz only exists on a
90 Hz+ panel — on a 60 Hz laptop panel `rAF` caps at 60 and the target is moot. "Sustain" implicates
thermal throttling on mobile/laptop within minutes. Plan against ~8–9 ms, measure per-frame, and treat
**worst-frame** (not average) as the bar: one 12 ms frame under vsync is visible judder even at 6 ms mean.
The frame breaks on **fill-rate + procedural-ALU/bandwidth + temporal disocclusion**, in that order —
never on geometry/precision/culling, which are cheap and solved.

## Depth & precision spine
- **Reversed-Z on `depth32float`** (near→1, far→0, `GREATER` test, clear = 0.0) is the near-free modern
  default (Reed: ~0 % indistinguishable-depth vs 77 % for standard float32). Keep it.
- **Logarithmic depth per-vertex** across the galactic→surface range; **per-fragment only on the hero
  body's near shells** — writing `frag_depth` disables early-Z, and WebGPU has **no conservative-depth
  escape hatch** (WGSL proposal gpuweb#5342 is not shipped). Restrict it or lose Hi-Z in the overdraw-heavy
  close-zoom case. For the full ~9-decade range, prefer **depth-range cascades / multi-frustum splitting**
  over stacking log + reversed-Z (partly redundant). Validate the depth setup at **surface** scale, not
  just orbital, so terrain doesn't z-fight the atmosphere shell.
- **Floating origin's real insight for perf:** an origin shift is a **hard, full-frame temporal-history
  invalidation** *and* a **Hi-Z stale-depth skip**. On re-center, invalidate the entire TAAU history
  (reprojection maps to wrong world positions) and skip Hi-Z the following frame. Tune the shift threshold
  to minimize invalidation frames; hide the invalidation behind existing motion.
- **df64 (double-single) — last resort, surgically scoped, with a real hazard.** Apply only to
  camera-relative translation and terrain-vertex / texture-UV math at extreme zoom. It is **not** "pure
  arithmetic": double-single depends on the compiler NOT reassociating or FMA-contracting the (hi+lo)
  compensation terms. WGSL does not guarantee strict IEEE-754 non-association, and Tint lowering to
  HLSL/MSL/SPIR-V can apply fast-math that silently annihilates the low word — degrading df64 back to f32
  with no warning on some backends. **Validate numerically per backend.** (WGSL has no `fp64`; gpuweb#2805
  is a proposal.)

## Temporal upsampling — a co-development bet, not a drop-in
- **TAAU is the only in-browser temporal-upscale option** — there is **no ML upscaler** (no DLSS,
  no FSR frame-gen, no tensor access). Three.js `TAAUNode` (WebGPU/TSL, issue #33359, since Apr 2026)
  exists but **upstream itself flags its multi-tap resolve as not production-sharp**; Legion would be
  co-developing it. MSAA must be off.
- **It fails precisely on motion-vector-less content**, which dominates hero bodies: procedural surface
  noise animating in shader-time, volumetrics, particles, gravitationally-lensed backgrounds. A reactive
  mask falls back to current-frame-only there, so you **pay full-resolution shading exactly where you
  wanted the upscale** — the "render at 44 % pixels" thesis evaporates over most of a star or black hole.
- **FSR2-style reactive + disocclusion masks are the hard 70 % of FSR2** — a multi-month fork on an
  immature TAAUNode, not a graft. Budget it as real subsystem work.
- **Separate temporal histories** for beauty / volumetrics / geodesics. Volumetrics write no usable
  depth/velocity and **cannot ride the beauty-pass TAAU**; they need their own history and composite
  *after* resolve.

## Dynamic resolution scaling (DRS) — first, cheapest release valve
App-level (there is no WebGPU DRS API): a rolling GPU-frame-time signal (`timestamp-query` + CPU-timer
fallback) drives internal color/depth/velocity scale between ~1.5×/axis (Quality, ~44 % pixels) and
~2.0×/axis (~25 %), with **hysteresis + rate-limiting** to avoid hunting. **Pre-allocate at max size and
render to a sub-rect** to avoid per-frame allocation churn.

## GPU-driven culling (correctly deprioritized at close zoom)
Compute frustum cull + compaction + `drawIndexedIndirect` is fully core WebGPU and maps 1:1 from Vulkan —
but it is near-free at close zoom on one body (few instances). It matters for the **fly-in**, not the hero
close-up. Hi-Z occlusion needs a **hand-rolled min-reduction pyramid** (WebGPU has no
`SAMPLER_REDUCTION_MODE_MIN`); skip it the frame after an origin shift.

## Cheap wins & the instrument
- **`shader-f16`** (Chrome 120+) — a major fill/ALU/bandwidth lever for noise-heavy procedural shading
  (terrain fBm, granulation); feature-detect (Qualcomm caveat gpuweb#5006).
- **`timestamp-query` profiling + overdraw budgeting** is the instrument that makes DRS and every budget
  line real — front-to-back order + Beer-Lambert early-exit protect volumetrics. Every technique ships
  with a measurement, not an averaged estimate (framework #06 Proofboard).

## Do NOT plan on (the dead-path list)
Mesh shaders · geometry shaders · tessellation shaders · hardware VRS · hardware sparse textures (emulate
virtual texturing with a page-table indirection texture) · guaranteed multi-draw-indirect (Chrome 131
experimental behind `enable-unsafe-webgpu` — feature-detect, fall back to one indirect draw per batch) ·
ML upscalers · WGSL `fp64`. Do not prototype any of them.

## Failure modes to avoid
TAAU ghosting on MV-less content · disocclusion shimmer at the horizon · origin-shift history corruption ·
log-depth-per-fragment early-Z loss (unrecoverable in-browser) · depth-fighting at scale without tight
origin / df64 · assuming multi-draw-indirect or timestamp-query is present · render bundles used while
GPU-bound (they only cut CPU encoding) · DRS oscillation without hysteresis · raymarch overdraw at close
zoom · VT streaming stalls on `copyBufferToTexture` · Hi-Z one-frame-latency pops.

## Cited sources
- Reed, *Depth Precision Visualized* (2015) — https://www.reedbeta.com/blog/depth-precision-visualized/
- Kemen (Outerra), *Maximizing Depth Buffer Range and Precision* (2012) — https://outerra.blogspot.com/2012/11/maximizing-depth-buffer-range-and.html
- Godot / Verschelde et al., *Emulating Double Precision on the GPU* (2022) — https://godotengine.org/article/emulating-double-precision-gpu-render-large-worlds/
- vkguide.dev, *GPU Driven Rendering: Compute-based Culling* — https://vkguide.dev/docs/gpudriven/compute_culling/
- three.js, *TAAUNode* (issue #33359) + `webgpu_upscaling_taau` example (2026) — https://github.com/mrdoob/three.js/issues/33359
- AMD GPUOpen, *FidelityFX Super Resolution 2* (reactive/disocclusion masks, 2022–23) — https://gpuopen.com/manuals/fidelityfx_sdk/techniques/super-resolution-temporal/
- Shehata, *How to use WebGPU timestamp query* (2023) — https://omar-shehata.medium.com/how-to-use-webgpu-timestamp-query-9bf81fb5344a

## Related
- hub → [[lead-game-developer]]
- peer ↔ [[webgpu-advanced-rendering]] · [[game-scale-traversal]]
