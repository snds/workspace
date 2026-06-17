---
name: img-photoreal-rendering
description: >
  Photorealistic rendering theory, engine-agnostic with Three.js/WebGPU corollaries — PBR
  (metal/rough, BRDFs, energy conservation), global illumination (ray tracing, path tracing,
  ambient occlusion, image-based lighting, light probes, radiosity, lightmaps), shadow
  techniques, and the linear/HDR → tonemap → encode pipeline. How offline/engine photorealism
  maps to real-time web. Triggers: PBR, physically based rendering, BRDF, metallic roughness,
  global illumination, ray tracing, path tracing, ambient occlusion, IBL, light probe,
  lightmap, radiosity, shadow mapping, tonemapping, ACES, deferred rendering.
aliases: [img-photoreal-rendering]
triggers: [pbr, physically based rendering, brdf, metallic roughness, global illumination, ray tracing, path tracing, ambient occlusion, ibl, light probe, lightmap, radiosity, shadow mapping, tonemapping, aces, deferred rendering]
tier: foundation
hub: imaging-foundations
domain: imaging
surfaces: ["*"]
spec_version: "2.0"
---

# Imaging — Photorealistic Rendering

The techniques that approximate [[img-optics-light]]'s rendering equation within a frame budget. Stated
engine-agnostically with **Three.js/WebGPU corollaries**, so techniques from Unreal/Unity/Blender Cycles
transfer to the web — the principle is constant; only the approximation changes.

## PBR — physically based rendering
A material model that obeys energy conservation so surfaces look right under *any* lighting. The standard
**metallic-roughness** workflow: base color (albedo), metallic (0/1), roughness, normal, AO. The shading is a
**BRDF** (typically Cook-Torrance: a Fresnel-weighted microfacet specular + diffuse) — a direct
discretization of the rendering equation's integrand. *Corollary:* Three.js `MeshStandardMaterial`/
`MeshPhysicalMaterial` and WebGPU/TSL PBR are this exact model; author textures in linear, sRGB only for color.

## Global illumination (the realism multiplier)
Direct light alone looks flat; realism is the **indirect** bounce. The ladder of techniques, costliest-last:
- **Ambient occlusion** (contact shadows — SSAO real-time, baked AO offline) — cheap, huge payoff.
- **Image-based lighting (IBL)** — light the scene from an HDRI environment map (irradiance + prefiltered
  specular). *The single biggest real-time photoreal win; Three.js: `PMREMGenerator` + env map.*
- **Light probes / irradiance volumes** — sampled indirect light for dynamic objects.
- **Lightmaps / baked GI** — radiosity-style precomputed bounce for static scenes (Blender/Unity bake → load).
- **Ray tracing / path tracing** — the ground truth (trace light paths, Monte Carlo over the rendering
  equation — see [[sci-probability-stochastic]]). Offline (Cycles) or real-time via hardware RT / WebGPU
  compute; in Three.js, `three-gpu-pathtracer` for stills, screen-space/RT hybrids for motion.
Choose by static-vs-dynamic and budget: bake what's static, probe/SSGI what's dynamic, path-trace hero stills.

## Shadows, tonemapping, the pipeline
**Shadows:** shadow mapping (+ cascades for large scenes, PCF/contact-hardening for softness); RT shadows
where affordable. **The pipeline that makes-or-breaks it:** render **linear + HDR** → **tonemap** (ACES /
AgX / Khronos PBR Neutral) → gamma-encode for display. Wrong order = washed-out or clipped. *Three.js:*
`renderer.toneMapping = ACESFilmicToneMapping`, `outputColorSpace = SRGB`. **Deferred vs. forward** shading
governs how many lights you can afford.

## Bringing engine-grade photoreal to the web
The gap to Unreal/Unity is *budget*, not *physics*: same PBR, same GI goals. Real-time web strategy: strong
**IBL + baked GI + good tonemapping + SSAO + post (bloom/DOF/grain)** gets ~90% of the look; reserve
path-tracing for cinematics/stills. Match real reference; conserve energy; tonemap last.

## Related
- hub → [[imaging-foundations]]
- peer ↔ [[img-optics-light]] · [[img-vfx]] · [[vis-classical-opencv]]
