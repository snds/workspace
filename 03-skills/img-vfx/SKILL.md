---
name: img-vfx
description: >
  Visual-effects principles, engine-agnostic — particle systems (emitters, forces,
  lifetime), simulation-driven FX (fluids, smoke/fire, cloth, destruction), volumetrics
  (fog, god rays, atmospheric scattering), shader-driven effects, and compositing (additive
  vs. alpha, bloom, the "sell it" layering). The theory beneath real-time VFX. Triggers: vfx,
  particles, particle system, simulation, fluid, smoke, fire, volumetrics, god rays,
  atmospheric scattering, compositing, bloom, dissolve, trail, emitter.
aliases: [img-vfx]
triggers: [vfx, particles, particle system, simulation, fluid, smoke, fire effect, volumetrics, god rays, atmospheric scattering, compositing, bloom, dissolve, trail, emitter]
tier: foundation
hub: imaging-foundations
domain: imaging
surfaces: ["*"]
spec_version: "2.0"
---

# Imaging — VFX

The principles beneath effects work. Sits beneath the Three.js implementation in [[threejs-vfx-atmosphere]];
this owns the *why*, that owns the *how-in-three*. Draws on [[sci-physics-simulation]] (the sims) and
[[img-photoreal-rendering]] (how effects integrate into a lit scene).

## Particles — the workhorse
A particle system = **emitter** (shape, rate) → per-particle **lifetime** (spawn → animate → die) under
**forces** (gravity, wind, turbulence, curl noise — see [[sci-probability-stochastic]] for the noise) →
**rendering** (billboards/sprites, trails, instanced meshes, or GPU points). Most real-time FX (sparks,
embers, dust, magic, rain) are particles + the right texture + the right blend mode.

## Simulation-driven FX
Higher-fidelity effects come from physics sims: **fluids/smoke/fire** (grid or SPH solvers — usually baked
to flipbooks/VDB for real-time), **cloth + soft body**, **destruction/fracture**. Principle: *simulate
offline at quality, bake, play back cheaply* — real-time rarely simulates the hero effect live. Ties to
[[sci-physics-simulation]].

## Volumetrics + atmosphere
Light through a participating medium: **fog/haze** (depth cue + mood), **god rays** (volumetric shafts),
**atmospheric scattering** (Rayleigh/Mie — sky color, aerial perspective), clouds. These are
[[img-optics-light]]'s scattering, rendered. Hugely effective for scale + photoreal depth; in real-time,
usually screen-space or raymarched approximations.

## Compositing + the "sell it" craft
Effects rarely convince in isolation — they're *layered + composited*. Key craft: **additive** blending for
energy/light (fire, magic), **alpha** for opaque media (smoke), **bloom/glow** for HDR emission, secondary
motion + anticipation ([[lead-motion-designer]]'s principles), grounding (contact shadows, interaction with
the scene), and restraint. A great effect respects the lighting + camera it lives in — integration over
spectacle.

## Related
- hub → [[imaging-foundations]]
- applies-in ← [[vfx-particle-systems]] · [[vfx-volumetrics]]
- peer ↔ [[img-photoreal-rendering]] · [[img-cinematography]]
