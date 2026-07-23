---
name: game-scale-traversal
description: >
  Rendering + camera across astronomical scale — the galaxy→system→planet→surface zoom and
  flythrough. Floating-origin / camera-relative rendering, logarithmic + reversed-Z depth,
  hierarchical LOD + impostors, nested scale "shells" with unit rebasing, and the cinematic
  zoom camera (eased, focus-pull, dolly). Solves the float-precision + depth + LOD problems
  that break naive huge-scale scenes. Three.js/WebGPU with engine corollaries. Triggers: scale
  traversal, floating origin, camera relative, logarithmic depth, reversed-z, z-fighting, LOD,
  impostor, powers of ten, galaxy zoom, flythrough, space camera, double precision, level of detail.
aliases: [game-scale-traversal]
triggers: [scale traversal, floating origin, camera relative rendering, logarithmic depth, reversed-z, z-fighting, lod, impostor, powers of ten, galaxy zoom, flythrough, space camera, double precision, level of detail]
tier: spoke
hub: lead-game-developer
domain: game
prerequisites: [lead-game-developer]
surfaces: ["*"]
spec_version: "2.0"
---

# Game — Scale Traversal (galaxy → planet zoom/flythrough)

The hardest part of a space game's *feel*: moving continuously across ~20 orders of magnitude (kiloparsecs →
metres) without precision, depth, or LOD breaking. Builds on [[sci-linear-algebra]] (transforms/precision),
[[sci-astro-structures]] (the scale spans), and the rendering skills. This is what makes Legion's galaxy
flythrough convincing.

## The precision problem (and the fix)
32-bit floats have ~7 significant digits — at galactic distances, positions jitter and geometry shears.
**Don't move the world far from the origin.** Fixes:
- **Floating origin / camera-relative rendering:** keep the camera near (0,0,0) and translate the world to it
  (rebase when the camera drifts past a threshold). Compute in camera-relative space.
- **Hierarchical / nested coordinates:** represent position as (sector + local offset) — double or integer
  sector index + float local. Galaxy → system → body → surface as nested frames, each with its own origin.
- **Render in shells/passes:** distant galaxy (points/volumes) and near scene (meshes) drawn in separate
  passes with rescaled units, composited — never in one float world.

## The depth problem
A near plane at 1 m and far plane at light-years destroys the depth buffer (z-fighting). Fixes:
- **Logarithmic depth buffer** (Three.js `logarithmicDepthBuffer`) or **reversed-Z** (float depth, near=1) for
  precision across huge ranges.
- Or **per-shell depth ranges:** render each scale band with its own near/far and clear depth between.

## LOD across scales
- **Continuous LOD + impostors:** a galaxy is a volume/point-cloud far away → resolves into individual star
  systems → a star + planets → a planet surface. Cross-fade representations by apparent size (angular
  diameter), not raw distance.
- **Star fields** as [[vfx-particle-systems]] points until close; **nebulae** as [[vfx-volumetrics]] always.
- Stream/generate detail on approach (procedural — [[sci-probability-stochastic]] seeds); budget by angular size.
- **At the surface boundary the shell hands off to the hero-body renderers.** This skill owns the *inter-shell*
  traversal + precision *architecture*; the terminal close-zoom body is owned elsewhere: planet surface →
  [[planetary-terrain-lod]] (cube-sphere quadtree + CDLOD, per-patch-origin as the terrain-side extension of
  floating origin); atmosphere/cloud/ocean → [[atmospheric-scattering-and-clouds]]; star + black hole →
  [[stellar-and-relativistic-hero-bodies]]. The close-zoom **90 FPS budget, temporal upsampling (TAAU/DRS),
  origin-shift-as-history-invalidation, and df64** discipline live in [[realtime-render-performance]].

## The cinematic zoom camera
A great flythrough is *directed*, not a linear lerp ([[img-cinematography]] + [[motion-3d-spatial]]):
- **Exponential/eased** distance change (constant *perceived* speed across scales — log-space interpolation),
  not constant linear velocity (which feels frozen then violent).
- **Focus pull + DOF** ([[img-photography]]) and FOV easing on arrival; frame the target (rule of thirds).
- Smooth orientation via **slerp** ([[sci-linear-algebra]]); anticipation + settle, not snap.
- Hand off control between scale shells seamlessly so the player never sees the seam.

## Related
- hub → [[lead-game-developer]]
- peer ↔ [[motion-3d-spatial]] · [[vfx-particle-systems]] · [[planetary-terrain-lod]] · [[realtime-render-performance]]
