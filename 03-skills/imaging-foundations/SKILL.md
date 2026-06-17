---
name: imaging-foundations
description: >
  The physics + craft of forming an image with light — how light behaves, how a camera
  captures it, how a renderer simulates it photorealistically, and how cinematography +
  VFX compose it. Load before any lighting, material, shader, rendering, or camera work.
  Engine-agnostic principle with explicit Three.js/WebGPU corollaries — the route to pull
  Unreal/Unity-grade photorealism into a web engine. Triggers: light, optics, exposure,
  camera, lens, PBR, BRDF, global illumination, ray tracing, path tracing, tonemapping,
  HDR, cinematography, VFX, photorealism, rendering equation.
aliases: [imaging-foundations]
triggers: [light, optics, exposure, camera, lens, pbr, brdf, global illumination, ray tracing, path tracing, tonemapping, hdr, cinematography, vfx, photorealism, rendering equation, image based lighting]
tier: foundation
domain: imaging
surfaces: ["*"]
spec_version: "2.0"
---

# Imaging & Rendering Foundations

How an image is *made of light* — the substrate beneath every lighting setup, material, shader, and camera.
A path-traced film frame, a Three.js scene, and a photograph differ in *budget*, not in *physics*: the same
radiometry, the same camera, the same light transport. This foundation owns the **context-free principle**;
the rendering skills (`3d-*`, `threejs-*`, `glsl`, `webgpu`) own the medium-specific application. It is the
explicit bridge for bringing **offline/engine-grade photorealism (Unreal, Unity, Blender Cycles) into
Three.js + WebGPU** — the techniques transfer; only the approximations change.

> Authored: the external skill directories cover *engine wrappers* (Three.js, Unity HDRP) and AI image
> *generators*, but none teach this light/optics/camera/rendering theory. See
> [[skill-ecosystem-and-mcp-servers]].

## The five foundations
| Spoke | Owns (context-free principle) |
|---|---|
| [[img-optics-light]] | Radiometry/photometry, reflection/refraction/Fresnel, the rendering equation — the physics of light |
| [[img-photography]] | The camera: exposure triangle, sensor + dynamic range, lens (focal length/DOF/bokeh), white balance |
| [[img-photoreal-rendering]] | PBR, BRDF, global illumination (ray/path tracing, AO, IBL, light probes), shadows, tonemapping |
| [[img-cinematography]] | Camera language for moving images: shots, composition, movement, lighting setups, color grading |
| [[img-vfx]] | Effects principles: particles, simulation-driven FX, volumetrics, compositing + the "sell it" craft |

## Core convictions
- **It's all light transport.** Every shading model is an approximation of the **rendering equation**
  (energy arriving = emitted + integral of incoming × BRDF). Knowing the real equation tells you what each
  shortcut (ambient term, baked GI, screen-space tricks) is *cheating on*.
- **Linear light in, display-encoded out.** Compute in linear/HDR; only tonemap + gamma-encode at the very
  end. Most "it looks flat / blown out" bugs are a color-space/tonemapping error, not a lighting one.
- **The camera is physical.** Exposure, lens, and dynamic range are real instruments — a *physically-based
  camera* (EV, tonemapper, DOF) makes a render read as a photograph.
- **Photoreal = correct energy + correct camera + restraint.** Match real-world reference; let the GI and
  the tonemapper do the work; resist the urge to add fill lights that break energy conservation.

## Applied in (engine corollaries)
- Direction + mood → [[lead-art-director]]
- Lighting/materials → [[3d-lighting-rendering]], [[3d-materials-shading]], [[threejs-materials-master]]
- Shaders + GPU rendering → [[glsl-shader-architect]], [[webgpu-advanced-rendering]]
- Effects/atmosphere → [[threejs-vfx-atmosphere]] · camera motion → [[motion-3d-spatial]]
- The game → [[legion-project]]
- Physics of light pairs with → [[science-foundations]] ([[img-optics-light]] is the shared boundary)

## Related
- spoke → [[img-cinematography]] · [[img-optics-light]] · [[img-photography]] · [[img-photoreal-rendering]] · [[img-vfx]]
- applies-in ← [[3d-lighting-rendering]] · [[3d-materials-shading]] · [[glsl-shader-architect]] · [[lead-art-director]] · [[legion-project]] · [[motion-3d-spatial]] · [[threejs-materials-master]] · [[threejs-vfx-atmosphere]] · [[webgpu-advanced-rendering]]
- peer ↔ [[design-foundations]] · [[science-foundations]] · [[vision-foundations]]
