---
name: adapter-webgpu-three
description: >
  Primary engine adapter — maps realtime photoreal doctrine (#12) onto Three.js / WebGPU / TSL.
  Gotchas: no fragment logarithmic depth as default, post order (bloom before tonemap), EffectComposer
  vs renderer readback, ?perfcapture harness. Use for any Legion/web ship path implementation detail.
  Triggers: Three WebGPU, TSL adapter, WebGPURenderer, EffectComposer order, perfcapture, log depth.
aliases: [adapter-webgpu-three]
triggers: [adapter webgpu, three webgpu adapter, webgpu three, tsl post order, effectcomposer tonemap, bloom before tonemap, perfcapture, logarithmic depth buffer, renderer readback, three.js webgpu]
tier: spoke
hub: realtime-visual-craft
domain: game
related: [webgpu-advanced-rendering, threejs-materials-master, threejs-vfx-atmosphere, realtime-visual-craft, realtime-render-performance, dynamic-gi-production, gpu-capture-tooling, vgpu-webgpu]
requires: [threejs-devtools-mcp]
surfaces: ["*"]
spec_version: "2.1"
---

# Adapter — WebGPU / Three.js (primary)

Translates framework #12 and imaging/performance doctrine into **Three.js + WebGPURenderer + TSL**
APIs. Principles stay in [[realtime-visual-craft]] / [[img-photoreal-rendering]] /
[[realtime-render-performance]]. API mechanics: [[webgpu-advanced-rendering]]. Materials:
[[threejs-materials-master]]. Post/VFX: [[threejs-vfx-atmosphere]].

## Role

This is the **ship adapter** for **existing** Three.js browser titles (Legion and kin).
Greenfield web GPU / WGSL / headless snapshots start at [[vgpu-webgpu]], not a new Three tree.
Unreal/Unity adapters are northstar ceilings, not defaults ([[adapter-unreal]], [[adapter-unity-hdrp]]).
Optional live inspect: capability `threejs-devtools-mcp` (browser tab must stay open).

## Capability map (honest)

| Doctrine need | Three / WebGPU reality |
|---|---|
| PBR + IBL | `MeshStandard/Physical` + `PMREMGenerator` — strong |
| Baked GI | Lightmap / custom probes — you own pack/load ([[bake-orchestration]]) |
| Dynamic GI | Thin SSGI / probes; **not** Lumen |
| Shadows | CSM + PCF/PCSS custom; RT experimental |
| Post | Composer or node post; **order matters** |
| Precision | Reverse-Z / careful log depth — **avoid frag log-depth default** |
| Perf harness | `?perfcapture` (or project flag) → JSON |

## Absolute gotchas

### 1. No fragment logarithmic depth as default
`logarithmicDepthBuffer: true` (or frag log-depth hacks) **defeats early-Z / Hi-Z** and burns the
overdraw-heavy near-camera case. Prefer:
- reverse-Z where available,
- view/projection hygiene + floating origin ([[game-scale-traversal]]),
- log depth only on near shells if absolutely required — document the tax in `BUDGET.md`.

### 2. Post order — bloom before tonemap
Correct display pipe: **linear HDR scene → bloom (and most glows) → tonemap → encode/output color
space**. Tonemap then bloom = wrong energy, halo mush, "AI marketing HDRI" look.

Checklist:
- [ ] Scene render target is HDR / linear.
- [ ] Bloom samples HDR.
- [ ] Tonemap is last look op (before optional grain/LUT that expect display-referred — document).
- [ ] `outputColorSpace` / `toneMapping` not double-applied (renderer **and** composer).

### 3. Composer vs `renderer` readback
- Final pixels for QA = **what the composer presents**, not an intermediate `WebGLRenderTarget` /
  `RenderTarget` grabbed from mid-stack.
- `renderer.readRenderTargetPixels` / async read on the wrong target → false "fixed" claims.
- Screenshots for northstar: after tonemap + output encode; lossless PNG; native resolution.

### 4. `?perfcapture` harness
Wire a URL flag (project convention: `?perfcapture`) that:
1. Runs official poses / flythroughs.
2. Collects timestamp-query pass ms ([[gpu-capture-tooling]]).
3. Dumps JSON (pose, p50/p99, worst frame, backend).
4. Does not enable debug overlays that change the cost.

## Implementation checklist (new scene)

- [ ] `WebGPURenderer` + `await renderer.init()`; feature-detect fallback policy written.
- [ ] Color: linear workflow; tonemap named (ACES / AgX / Neutral) in `RENDER.md`.
- [ ] IBL via PMREM; intensity locked to bake exposure contract.
- [ ] Shadows: cascade count + map size in `BUDGET.md`; texel snap on.
- [ ] Post stack order reviewed (bloom → tonemap).
- [ ] No default frag log-depth.
- [ ] Perf flag works on clean load (no lab-only code path).
- [ ] Motion QA path recorded before "looks done."

## Mapping #12 technique ladder → Three

1. Direct + PBR materials → node/standard materials.
2. AO → SSAO pass or baked AO map.
3. IBL → PMREM env.
4. Probes / lightmaps → custom uniforms / lightmap slot ([[bake-orchestration]]).
5. SSGI / DDGI → custom; budget ruthlessly.
6. Path trace → `three-gpu-pathtracer` or offline for stills only.

## Failure modes

| Symptom | Cause | Fix |
|---|---|---|
| Washed bloom | Tonemap before bloom / double tonemap | Reorder; single tonemap |
| QA mismatch vs on-screen | Readback mid-composer | Capture final present |
| Near-camera hitch | Frag log-depth + overdraw | Remove log-depth; reverse-Z / origin |
| "WebGPU Lumen" expectation | Misread northstar | Document ceiling; bake+IBL |
| Perf JSON empty | No timestamp feature | Detect + CPU fallback; still report |

## Related
- hub → [[realtime-visual-craft]]
- peer ↔ [[dynamic-gi-production]] · [[shadow-quality-craft]] · [[bake-orchestration]] · [[gpu-capture-tooling]] · [[adapter-unreal]] · [[adapter-unity-hdrp]] · [[virtual-texturing-ops]] · [[lead-3d-designer]] · [[legion-project]] · [[vgpu-webgpu]] · [[web-3d-extensions]]
