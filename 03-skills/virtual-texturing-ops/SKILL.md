---
name: virtual-texturing-ops
description: >
  Virtual texturing / sparse residency ops — streaming budgets, page-table indirection (including
  browser emulation of sparse textures), texel density at planetary/world scale. Use when texture
  thrash, blurry close-ups, residency spikes, or VT page faults dominate the frame. Triggers:
  virtual texturing, sparse texture, texture streaming, page table, residency, texel density,
  megatexture, sampler feedback.
aliases: [virtual-texturing-ops]
triggers: [virtual texturing, virtual texture, sparse texture, texture streaming, page table, residency budget, texel density, megatexture, sampler feedback, texture thrash, tile streaming, vt feedback]
tier: spoke
hub: realtime-visual-craft
domain: game
related: [planetary-terrain-lod, 3d-asset-pipeline, realtime-render-performance, adapter-webgpu-three, adapter-unreal]
surfaces: ["*"]
spec_version: "2.0"
---

# Virtual Texturing Ops

Owns **residency, streaming budgets, and texel-density discipline** for large worlds. Terrain LOD
structure: [[planetary-terrain-lod]]. Asset encode/compress: [[3d-asset-pipeline]]. Frame budget:
[[realtime-render-performance]].

## What "virtual texturing" means here

A large logical texture (or atlas of tiles) is **not** fully GPU-resident. A **page table** maps
UV → physical tile; a feedback/pass requests tiles; a cache evicts cold pages. Engines differ:

| Engine path | Mechanism |
|---|---|
| Unreal Virtual Texture / Runtime VT | First-class sparse + feedback |
| Unity VT / streaming mips | Streaming + VT where enabled |
| Browser / WebGPU | **Emulate** sparse: tile atlas + indirection texture + CPU/GPU feedback (no reliable sparse
  residency API across vendors) |

Do not assume `GPUTexture` sparse binding exists portably on the web. Design the indirection layer
yourself ([[adapter-webgpu-three]]).

## Budgets (write into `BUDGET.md`)

| Budget | Typical starting point | Notes |
|---|---|---|
| Physical cache size | 256–1024 MB GPU (device tier) | Cap by weakest ship GPU |
| Pages committed / frame | Fixed N (e.g. 8–64) | Hard cap; never "upload until done" |
| Upload bandwidth / frame | Device-tier table | Mobile ≪ discrete |
| Indirection resolution | Covers max VT UV space | Too coarse → wrong tiles |
| Feedback resolve | 1× or 1/2× after opaque | Budget the readback/resolve |

**Rule:** residency work is a first-class pass with a ms and MB line. Texture thrash is a hitch
source equal to geometry LOD thrash.

## Page-table indirection checklist

- [ ] Logical UV space documented (planet face, UDIM, megatexture UV).
- [ ] Page size power-of-two (128² / 256² common); matches compression block alignment.
- [ ] Indirection texture format holds page ID + mip (or packed equivalent).
- [ ] Sampling: anisotropic rules defined (aniso can request wrong pages if feedback ignores it).
- [ ] Fallback color / lowest mip always resident (never black fault).
- [ ] Eviction: LRU or distance-weighted; protect currently visible + hysteretic ring.
- [ ] Teleport / cut: burst policy (allow temporary debt, then repay) — document max debt frames.

## Browser emulation pattern (WebGPU)

1. **Physical atlas** — 2D array or large 2D atlas of tiles (BC/ASTC/KTX2 compressed where possible).
2. **Indirection** — R32Uint / RG16UI map from coarse UV to atlas slot.
3. **Feedback** — software: CPU samples desired pages from camera/LOD; or GPU: sparse feedback buffer
   written in shader, read back asynchronously (latency 1–3 frames — design for it).
4. **Uploader** — ring buffer of decode + `copyBufferToTexture` / queue writes; hard N/frame.
5. **Shader** — sample indirection → sample atlas; grad/mip from screen derivatives.

## Texel density at scale

Goal: **stable screen-space texel density** (e.g. ~1 texel/pixel at target distance), not "4K everywhere."

Checklist:
- [ ] Authoring texel density (px/m) declared per asset class (terrain, prop, hero).
- [ ] Mip bias under TAA/upsampling documented (TAA often wants −0.5 to −1 mip bias).
- [ ] Planet / large meshes: density follows LOD / distance, not UV island ego.
- [ ] Close approach: residency must promote high mips before camera arrives (prefetch along path).
- [ ] Measure: capture at native res; blurry close-up = residency or density fail, not "needs sharpen."

## Streaming ops under motion

- Prefetch along predicted camera velocity (approach-to-surface is the stress case).
- Prioritize: screen area × importance × mip urgency.
- Never stall the frame on decode; show parent mip.
- Log fault rate and cache hit % in perf harness ([[gpu-capture-tooling]]).

## Failure modes

| Symptom | Cause | Fix |
|---|---|---|
| Blurry then pop sharp | Late residency | Prefetch; raise pages/frame temporarily on approach |
| Hitch every N seconds | Burst upload / GC decode | Smooth N/frame; worker decode |
| Wrong tile flashes | Indirection race / stale page | Fence updates; double-buffer indirection |
| Shimmer under aniso | Feedback ignores aniso | Include aniso in feedback or limit aniso on VT |
| Memory climb | No eviction / leak | Cap cache; assert residency ≤ budget |
| Terrain blur at orbit OK, surface mush | Density or mip bias | Raise near residency; fix authoring px/m |

## Adapter notes

- **Unreal:** Runtime Virtual Texturing / VT as northstar for feedback + streaming behavior.
- **Three/WebGPU:** custom atlas + indirection; KTX2/Basis for tile payload ([[3d-asset-pipeline]]).
- Couple with [[planetary-terrain-lod]] bake-on-subdivision so height/albedo tiles share residency policy.

## Related
- hub → [[realtime-visual-craft]]
- peer ↔ [[adapter-webgpu-three]] · [[gpu-capture-tooling]] · [[bake-orchestration]]
