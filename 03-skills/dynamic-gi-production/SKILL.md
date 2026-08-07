---
name: dynamic-gi-production
description: >
  Production global-illumination recipes for realtime — probe volumes, DDGI/SSGI, ReSTIR-class
  sampling; bake-vs-dynamic decision matrix; honest WebGPU ceilings vs Unreal Lumen / Unity APV.
  Use when choosing GI technique, budgeting bounce light, diagnosing light leak / temporal
  instability, or mapping engine GI features to web. Triggers: DDGI, SSGI, ReSTIR, probe volume,
  irradiance volume, dynamic GI, bake vs dynamic, Lumen, APV, light probe grid.
aliases: [dynamic-gi-production]
triggers: [ddgi, ssgi, restir, probe volume, irradiance volume, dynamic gi, global illumination bake, bake vs dynamic, lumen, apv, light probe grid, irradiance probes, screen space gi, probe atlas]
tier: spoke
hub: realtime-visual-craft
domain: imaging
related: [img-photoreal-rendering, realtime-render-performance, adapter-webgpu-three, adapter-unreal, adapter-unity-hdrp, bake-orchestration, shadow-quality-craft]
surfaces: ["*"]
spec_version: "2.0"
---

# Dynamic GI Production

Engine-agnostic GI choice and ops. Principles first; adapters translate ceilings. Owns **which
bounce technique ships and how it fails**; theory lives in [[img-photoreal-rendering]]; frame cost
in [[realtime-render-performance]].

## Decision matrix — bake vs dynamic

| Scene trait | Prefer | Why |
|---|---|---|
| Static architecture, hero materials | Bake (lightmaps / probe bake) | Stable, cheap at runtime, highest fidelity per ms |
| Moving lights / time-of-day / destroyable geo | Dynamic probes / SSGI / hybrid | Bake invalidates; pay update cost |
| Characters / props in baked rooms | Irradiance volume + SH probes | Sample baked field; no per-object lightmap UVs |
| Cinematic still / one-shot hero | Path trace / ReSTIR offline | Budget unlimited for the frame |
| Browser / WebGPU primary target | IBL + baked probes + SSAO (+ thin SSGI) | No Lumen-class software RT; see ceiling |

**Rule:** bake what does not move; probe what moves through static; screen-space only for contact
bounce you cannot afford to store; never claim "Lumen on web."

## Technique ladder (name the cheat)

1. **IBL / HDRI** — largest realtime photoreal win; no multi-bounce. Cheat: infinite distant lighting.
2. **Baked lightmaps / probe bake** — multi-bounce for static. Cheat: no dynamic emitters; UV/atlas cost.
3. **Probe volume / irradiance grid** — trilinear SH or octahedral irradiance. Cheat: low spatial
   frequency; leaks through thin walls without occlusion/depth-aware probes.
4. **DDGI-class** — world-space probes with visibility + hysteresis. Cheat: probe spacing vs thin
   geometry; update latency under camera cut.
5. **SSGI** — screen-space multipath. Cheat: missing off-screen; edge ghosting; TAA-dependent.
6. **ReSTIR / hardware RT / path trace** — near ground truth. Cheat: noise, denoiser lag; WebGPU
   rarely has production RT core access.

Climb only until the fidelity contract in `NORTHSTAR.md` holds under the frame budget in `BUDGET.md`.

## Probe volume ops checklist

- [ ] World bounds cover all playable volume (not just authored room AABB).
- [ ] Probe spacing ≤ thinnest lit corridor / doorway you care about (else leak).
- [ ] Depth/visibility test or hysteresis on before shipping (naked irradiance = light bleed).
- [ ] Sky/IBL contribution authored once; probes do not double-count environment.
- [ ] Dynamic object sampling: SH L1 or octahedral fetch, not a second full bake.
- [ ] Teleport / cut: force probe refresh or blend window; do not show stale irradiance for >2 frames.
- [ ] Budget line in `BUDGET.md`: probe update ms + sample ms + atlas memory.

## SSGI / screen-space checklist

- [ ] Runs after opaque G-buffer / depth; before tonemap; after or with AO as designed.
- [ ] Thickness / max-ray distance dialed to room scale (planet-scale scenes need world probes, not SSGI alone).
- [ ] Disocclusion: history reject + clamp; still-only QA is an automatic fail ([[interactive-capture-eval]]).
- [ ] Off-screen miss accepted in contract, or filled by probes (hybrid).

## ReSTIR-class (when you actually need it)

Use for: many dynamic lights, glossy transport, or cinematic moments. Production path: reservoir
reuse + spatiotemporal reuse + denoiser. **Do not** enable on every frame in browser without a
measured budget — ReSTIR without a denoiser is noise; with a denoiser is latency and ghosting.

## Honest WebGPU ceiling vs Unreal Lumen / Unity APV

| Capability | Unreal Lumen | Unity HDRP APV | WebGPU / Three (typical) |
|---|---|---|---|
| Software RT / SDF multi-bounce | Yes (high end) | Limited | No production equivalent |
| Probe / irradiance volume | Yes | APV first-class | Manual SH/octahedral or bake import |
| SSGI | Yes | Yes (path) | Custom or post stack; quality ≪ AAA |
| Hardware RT | Console/PC path | DXR/Vulkan path | Sparse / experimental; not a ship default |
| Runtime bake invalidation | Strong | Strong | You own it; usually offline rebake |

**Northstar use of Lumen/APV:** reference what the look *should* be under full GI; match with bake +
IBL + probes on web; document the remaining gap in `RENDER.md`. See [[adapter-unreal]],
[[adapter-unity-hdrp]], [[adapter-webgpu-three]].

## Failure modes

| Symptom | Likely cause | Fix |
|---|---|---|
| Light through walls | Probe spacing / no visibility | Tighten grid; enable depth-aware probes |
| Flicker under move | Temporal GI / TAA conflict | Longer hysteresis; reject on depth discontinuity |
| Flat interiors | Missing bounce; HDRI-only | Bake or probe; raise indirect intensity carefully (energy) |
| Dark dynamic props | Props not sampling probes | Bind irradiance volume to material |
| Frame spikes on cut | Full probe update | Amortize; pre-warm; async update budget |
| "Looks like Lumen" claim from still | Marketing HDRI + bloom | Motion + budget gate; name the cheat |

## Adapter notes

- **Three/WebGPU:** prefer baked lightmaps / probe atlas + `PMREMGenerator` IBL; SSGI only if budgeted.
  No frag log-depth defaults. Post order: bloom before tonemap ([[adapter-webgpu-three]]).
- **Unreal:** Lumen for northstar matching; bake still wins for static shipping content on mid GPUs.
- **Unity HDRP:** APV for dynamic objects in baked scenes; Volume framework for overrides.

## Related
- hub → [[realtime-visual-craft]]
- peer ↔ [[shadow-quality-craft]] · [[bake-orchestration]] · [[adapter-webgpu-three]] · [[adapter-unreal]] · [[adapter-unity-hdrp]]
