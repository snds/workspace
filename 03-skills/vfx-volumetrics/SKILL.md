---
name: vfx-volumetrics
description: >
  Volumetric rendering, Three.js/WebGPU with engine corollaries — raymarched density fields,
  fbm/curl noise volumes, the participating-media model (absorption + in/out-scattering,
  Beer-Lambert, phase functions), 3D-texture vs. procedural volumes, performance (half-res,
  froxels, blue-noise jitter, temporal reprojection), and depth integration. The implementation
  beneath nebulae, dust, fog, and god rays. Triggers: volumetric, raymarching, density field,
  participating media, beer-lambert, scattering, phase function, froxel, volumetric fog, god
  rays, nebula rendering, 3d texture, signed distance, ray march.
aliases: [vfx-volumetrics]
triggers: [volumetric, raymarching, density field, participating media, beer-lambert, scattering, phase function, froxel, volumetric fog, god rays, nebula rendering, 3d texture, ray march]
tier: spoke
hub: threejs-vfx-atmosphere
domain: game
prerequisites: [threejs-vfx-atmosphere, img-vfx]
surfaces: ["*"]
spec_version: "2.0"
---

# VFX — Volumetrics

Rendering light through a medium, where the convincing nebulae/dust/fog live. The theory is
[[img-optics-light]]'s scattering; this is the real-time implementation. For Legion: nebulae, dust lanes,
atmospheric haze, engine plasma, god rays.

## The model: raymarch a density field
March a ray from the camera through the volume in steps; at each step sample **density**, accumulate
**absorption** + **in-scattering**, and composite front-to-back. The physics ([[img-optics-light]]):
- **Beer-Lambert** — light attenuates exponentially with density × distance (transmittance).
- **In-scattering** — light from sources scattered toward the eye; weighted by a **phase function**
  (Henyey-Greenstein: forward-scatter for haze/god-rays, near-isotropic for thick clouds).
- **Emission** — for self-luminous media (emission nebulae glowing at [[sci-astro-structures]]'s H-alpha/OIII).

## Building the density
- **Procedural:** **fBm / curl noise** ([[sci-probability-stochastic]]) shaped by gradients/masks — the
  workhorse for nebulae and clouds (no memory cost, animatable). Domain-warp for wispy structure.
- **3D textures / VDB-baked:** author/sim in Blender (the [[skill-ecosystem-and-mcp-servers]] Blender MCP) →
  bake to a 3D texture for art-directed shapes. Best for hero nebulae.
- Combine: low-freq baked shape + high-freq procedural detail.

## Make it real-time
Volumetrics are expensive — the techniques that make them ship:
- **Half/quarter-res** raymarch + upsample; **froxel** (frustum-voxel) grids for fog.
- **Blue-noise / dithered** step offsets + **temporal reprojection** to hide banding with few steps.
- Early-out on full opacity; limit march distance; LOD step count by distance.
- In Three.js: raymarch in a fragment shader over a proxy volume/fullscreen pass; WebGPU compute for froxels
  ([[webgpu-advanced-rendering]]).

## Integrate with the scene
Read the **depth buffer** so volumes occlude/are-occluded correctly; composite in **HDR** before tonemapping
([[img-photoreal-rendering]]); add embedded light sources (stars inside a nebula lighting the dust). God rays
= volumetric scattering from a bright source, or a cheaper radial screen-space pass.

## Related
- foundation → [[img-vfx]]
- hub → [[threejs-vfx-atmosphere]]
- peer ↔ [[vfx-particle-systems]] · [[sci-astro-structures]]
