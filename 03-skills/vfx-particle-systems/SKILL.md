---
name: vfx-particle-systems
description: >
  GPU particle systems at scale, Three.js/WebGPU with engine corollaries — emitter/lifetime/
  force model, GPU simulation (transform feedback, WebGPU compute, GPGPU ping-pong textures),
  flow fields + curl noise, rendering (instanced meshes, billboards/sprites, GPU points,
  trails), soft + depth-aware particles, and scaling to millions (stars, dust, debris). The
  implementation beneath the galaxy's particulate look. Triggers: particle system, GPU
  particles, compute particles, transform feedback, GPGPU, curl noise, flow field, instancing,
  billboard, point cloud, soft particles, sprite, millions of particles, star field.
aliases: [vfx-particle-systems]
triggers: [particle system, gpu particles, compute particles, transform feedback, gpgpu, curl noise, flow field, instancing, billboard, point cloud, soft particles, sprite, star field, millions of particles]
tier: spoke
hub: threejs-vfx-atmosphere
domain: game
prerequisites: [threejs-vfx-atmosphere, img-vfx]
surfaces: ["*"]
spec_version: "2.0"
---

# VFX — Particle Systems (GPU, at scale)

The implementation craft beneath [[img-vfx]]'s particle principles. Three.js/WebGPU-specific with engine
corollaries. For Legion: stars, dust, nebula motes, engine trails, debris — all particles, often by the
million.

## Simulate on the GPU
CPU particles cap out ~10k. For galaxy scale (10⁵–10⁷), simulate on the GPU:
- **WebGPU compute shaders** (Three.js TSL / WebGPURenderer — see [[webgpu-advanced-rendering]]): a compute
  pass updates a storage buffer of particle state each frame. The modern path.
- **WebGL fallback:** GPGPU **ping-pong** float textures (position/velocity encoded as texels;
  `GPUComputationRenderer`) or **transform feedback**. State lives on the GPU; the CPU never touches it.
Encode position, velocity, age, seed per particle; update under forces; recycle dead particles.

## Motion that reads as alive
Raw random looks like static. Drive motion with **flow fields** — **curl noise** (divergence-free, so it
swirls without sources/sinks; built on [[sci-probability-stochastic]]'s noise) is the workhorse for smoke,
dust, and nebula drift. Layer constant forces (gravity wells toward a black hole, orbital velocity for a
galaxy disk via [[sci-physics-simulation]]) with turbulence. Per-particle lifetime curves (size/color/alpha
over age) carry most of the visual character.

## Render efficiently
- **GPU points / sprites** — cheapest; ideal for star fields (size-by-distance, additive blend, blackbody
  color from [[sci-astro-objects]]). Use a soft round texture, not square points.
- **Instanced meshes** — when particles need geometry/orientation (debris, asteroids).
- **Billboards** — camera-facing quads for volumetric-ish puffs.
- **Trails/ribbons** — history buffers for engine wakes, comets.

## Make it sit in the scene
- **Additive** blend for light/energy (stars, embers, plasma); **alpha** for dust/smoke.
- **Soft particles** — fade where the billboard intersects scene depth (sample the depth buffer) to kill hard
  edges. Essential for believable volumetric-ish particles.
- **HDR + bloom** ([[img-photoreal-rendering]]) makes bright particles glow correctly.
- Sort or use additive to avoid transparency artifacts; cap overdraw (the real perf killer at scale).

## Related
- foundation → [[img-vfx]]
- hub → [[threejs-vfx-atmosphere]]
- peer ↔ [[vfx-volumetrics]] · [[game-scale-traversal]]
