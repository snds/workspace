---
name: bake-orchestration
description: >
  Lightmap and probe bake orchestration — bake → pack → engine load across Blender / Unreal /
  Unity into glTF/Three or native. Use when setting up bake pipelines, atlas packing, probe
  export, or diagnosing seams / UV / exposure mismatches after import. Triggers: lightmap bake,
  probe bake, bake pipeline, lightmap pack, glTF lightmap, APV bake, GPULightmass, Cycles bake.
aliases: [bake-orchestration]
triggers: [lightmap bake, probe bake, bake orchestration, bake pipeline, lightmap atlas, lightmap pack, gltf lightmap, irradiance bake, gpulightmass, cycles bake, apv bake, lightmap uv, bake to three]
tier: spoke
hub: realtime-visual-craft
domain: imaging
related: [3d-lighting-rendering, 3d-asset-pipeline, dynamic-gi-production, adapter-webgpu-three, adapter-unreal, adapter-unity-hdrp]
surfaces: ["*"]
spec_version: "2.0"
---

# Bake Orchestration

Owns the **offline GI bake → pack → runtime load** pipeline. Lighting design intent:
[[3d-lighting-rendering]]. Mesh/UV/export hygiene: [[3d-asset-pipeline]]. Runtime GI choice:
[[dynamic-gi-production]].

## Pipeline stages (always name them)

```
Author (UVs, materials, lights)
  → Bake (lightmaps / probes / AO)
    → Pack (atlas, metadata, exposure)
      → Load (engine / glTF / Three)
        → Verify (still + motion + exposure match)
```

Skip a stage and you get "baked in DCC, broken in engine" tickets.

## Pre-bake checklist

- [ ] **Lightmap UVs** unique, non-overlapping, adequate padding (2–4 px at atlas res).
- [ ] Scale: texel density target set (e.g. 10–40 px/m by content class).
- [ ] Materials: albedo in linear workflow; emissives tagged for bake contribution.
- [ ] Lights: only lights meant to bake are active; runtime-only lights excluded.
- [ ] Static/dynamic split documented; dynamic objects get probes, not lightmaps.
- [ ] Exposure / reference middle-gray locked (same tonemap intent as runtime).
- [ ] Northstar stills listed for bake acceptance (`NORTHSTAR.md`).

## Bake backends (pick one source of truth)

| Source | Strength | Export path |
|---|---|---|
| Blender Cycles | Controllable, scriptable | EXR lightmaps + JSON probe grid → pack |
| Unreal GPULightmass / CPU | High quality, engine-native | Keep native; or export for web via custom |
| Unity Progressive / APV bake | HDRP-integrated | Native APV; lightmaps via export tools |
| Custom path tracer | Hero stills | Not a streaming bake; archive EXR |

**Rule:** one bake authority per content set. Do not mix Cycles albedo response with Unreal
tonemap without an exposure contract.

## Pack stage

Outputs to version:
1. **Lightmap atlas** (or UDIM set) — EXR or HDR for edit; BC6H/ASTC/KTX2 for ship.
2. **UV channel index** documented (usually UV1).
3. **Probe grid** — positions + SH coefficients or octahedral irradiance.
4. **Metadata JSON** — atlas size, exposure scale, color space, probe spacing, bake commit hash.
5. **AO / bent-normal** if separate (do not bake AO into albedo).

Checklist:
- [ ] Atlas packing waste < threshold; no island crush.
- [ ] Dilate / pad lightmap charts (prevents UV filter seams).
- [ ] Color space tagged (`linear`, `ACEScg`, etc.).
- [ ] Exposure scale so runtime IBL + bake do not double-brighten.

## Load stage — native vs web

### Native (Unreal / Unity)
- Import settings: lightmap UV index, compression, sRGB **off** for lightmaps.
- APV / probe volumes: bake then assign to scene Volume ([[adapter-unity-hdrp]], [[adapter-unreal]]).
- Validate in-engine with the same tonemap volume as ship.

### Web / glTF / Three ([[adapter-webgpu-three]])
- Prefer **custom extras** or known extensions for lightmap refs (document the schema in-repo).
- Load: `MeshStandardNodeMaterial` / standard material with lightmap slot; multiply correctly
  (lightmap * albedo, not replace).
- Probes: SH L1/L2 uniforms or octahedral atlas sampler.
- PMREM IBL remains; bake is local multipath, not a substitute for env specular.
- Composer / tonemap: judge final display buffer, not pre-tonemap RT.

## Verification gate

- [ ] Still: native-res compare vs bake viewport / northstar (seams, exposure, color).
- [ ] Motion: camera move across atlas seams and probe boundaries ([[interactive-capture-eval]]).
- [ ] Dynamic prop: samples probes; not black / not double-lit.
- [ ] Change light → rebake path documented (what invalidates the cache).

## Failure modes

| Symptom | Cause | Fix |
|---|---|---|
| Black seams / halos | Insufficient UV padding / dilation | Pad + dilate; raise atlas res |
| Chessboard noise | Overlapping lightmap UVs | Unique unwrap; validate overlaps |
| Too bright in engine | sRGB on lightmap or double IBL | Linear lightmap; exposure contract |
| Flat after load | Lightmap not bound / wrong UV | Check UV1 + material slot |
| Probe flicker on props | Sparse grid / no interp | Denser grid; SH order; hysteresis |
| Web mismatch vs Blender | Tonemap / color space | Match AgX/ACES intent; metadata scale |

## Automation sketch

1. CI job: validate UV overlaps + density floor.
2. Bake farm: deterministic seed + locked addon versions.
3. Pack writes content-addressed atlas + `bake-manifest.json`.
4. Runtime asserts manifest hash matches loaded assets.

## Related
- hub → [[realtime-visual-craft]]
- peer ↔ [[dynamic-gi-production]] · [[virtual-texturing-ops]] · [[adapter-webgpu-three]] · [[adapter-unreal]] · [[adapter-unity-hdrp]]
