---
name: adapter-unreal
description: >
  Thin Unreal Engine corollary adapter — Nanite, Lumen, Virtual Shadow Maps, Movie Render Queue as
  high-ceiling references for northstar matching against web/Three ship paths. Not a full Unreal
  production manual. Triggers: Unreal Lumen, Nanite, Virtual Shadow Maps, Movie Render Queue,
  Unreal northstar, UE5 reference.
aliases: [adapter-unreal]
triggers: [unreal adapter, unreal lumen, nanite, virtual shadow maps, vsm unreal, movie render queue, mrq, ue5 reference, unreal northstar, unreal engine gi]
tier: spoke
hub: realtime-visual-craft
domain: game
related: [realtime-visual-craft, img-photoreal-rendering, dynamic-gi-production, shadow-quality-craft, bake-orchestration, adapter-webgpu-three]
surfaces: ["*"]
spec_version: "2.0"
---

# Adapter — Unreal Engine (northstar corollary)

Thin corollary: use Unreal as a **high-ceiling reference** for what movie-level realtime can look
like, then map gaps honestly onto the web ship path ([[adapter-webgpu-three]]). Not a substitute for
Unreal's own docs. Doctrine: [[realtime-visual-craft]] / [[img-photoreal-rendering]].

## When to load this skill

- Writing `NORTHSTAR.md` with UE5 footage / stills as Literal or Spirit refs.
- Explaining why a web scene does not yet match Lumen bounce / Nanite density.
- Baking or lighting in Unreal for export into a web pipeline ([[bake-orchestration]]).
- Comparing shadow contact quality to Virtual Shadow Maps.

## Feature → doctrine mapping

| Unreal feature | What it proves | Web / Three corollary |
|---|---|---|
| **Lumen** | Dynamic multi-bounce GI + reflections at AAA budget | Bake + probes + IBL + thin SSGI; **no Lumen port** |
| **Nanite** | Micropoly density / continuous LOD | Chunked LOD / VT / meshlets-you-own ([[planetary-terrain-lod]], [[virtual-texturing-ops]]) |
| **Virtual Shadow Maps** | Stable high-res shadows, less cascade swim | CSM + texel snap + contact-hardening; accept seam budget |
| **Movie Render Queue** | Deterministic cinematic capture (stills/video) | Harness + lossless PNG + recorded flythrough; not MRQ |
| **Path Tracer (UE)** | Ground-truth stills | Offline Cycles / pathtracer for hero stills |

## Northstar matching workflow

1. Name the Unreal reference (build, map, clip timestamp) in `NORTHSTAR.md`.
2. State contract: Literal vs Spirit ([[realtime-visual-craft]]).
3. List **which Unreal features** create the look (Lumen vs fancy post vs Nanite).
4. For each feature, write the web cheat and residual gap in `RENDER.md`.
5. Match what you can (PBR, tonemap, IBL, baked bounce, contact AO) before chasing GI miracles.
6. Prove with native stills + motion; Unreal trailer encodes are not native truth for pixel QA.

## Bake / export notes

- Prefer Unreal as bake authority only if the **ship** content lives there; for web ship, Blender
  Cycles or a locked custom baker is often cleaner ([[bake-orchestration]]).
- If using GPULightmass for reference lightmaps, export exposure metadata with the atlas.
- Do not expect Nanite source meshes to dump cleanly to glTF without a decimated proxy path
  ([[3d-asset-pipeline]]).

## Movie Render Queue as evidence template

MRQ teaches the right evidence habits even when you are not in Unreal:
- Fixed camera paths / takes.
- Warmup frames.
- High-bit / lossless stills where possible.
- Separate beauty vs debug buffers intentionally.

Mirror that discipline with project flythroughs + `?perfcapture` ([[gpu-capture-tooling]]).

## Honest ceilings

| Claim | Verdict |
|---|---|
| "We will run Lumen in WebGPU" | False for production ship |
| "Match Lumen still with bake+IBL" | Often Spirit-matchable indoors |
| "Match Lumen under dynamic destruction" | Usually out of web budget |
| "Nanite parity" | Density Spirit via LOD/VT; not the same system |
| "VSM parity" | Improve CSM; do not claim VSM |

## Failure modes

- Treating marketplace UE cinematics as achievable web defaults.
- Copying post stacks without HDR/tonemap order discipline.
- Using compressed YouTube northstars for pixel verdicts.
- Ignoring that Lumen hides lightmap UV craft — web bake still needs UVs.

## Related
- hub → [[realtime-visual-craft]]
- peer ↔ [[adapter-webgpu-three]] · [[adapter-unity-hdrp]] · [[dynamic-gi-production]] · [[bake-orchestration]] · [[shadow-quality-craft]] · [[lead-3d-designer]]
