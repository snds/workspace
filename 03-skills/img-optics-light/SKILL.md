---
name: img-optics-light
description: >
  The physics of light for imaging — radiometry vs. photometry, the inverse-square law,
  reflection/refraction/Fresnel, absorption/scattering/subsurface, and the rendering
  equation that unifies them. The shared boundary between physics and rendering: what every
  shading model approximates. Triggers: radiometry, photometry, irradiance, radiance, flux,
  inverse square, fresnel, refraction, scattering, subsurface, rendering equation, BRDF physics,
  energy conservation.
aliases: [img-optics-light]
triggers: [radiometry, photometry, irradiance, radiance, flux, inverse square, fresnel, refraction, scattering, subsurface, rendering equation, energy conservation, light physics]
tier: foundation
hub: imaging-foundations
domain: imaging
surfaces: ["*"]
spec_version: "2.0"
---

# Imaging — Optics & Light

The physics. Sits on the boundary with [[science-foundations]] (this is applied radiometry); everything in
[[img-photoreal-rendering]] is an approximation of what's here.

## Radiometry vs. photometry
**Radiometry** measures physical light energy (radiant flux W, irradiance W/m², **radiance** W/m²/sr — the
quantity a renderer actually transports). **Photometry** is the same weighted by human eye sensitivity
(lumens, lux, candela, nits). Renderers think in radiance; cameras and displays think in photometric units.
Light falls off by the **inverse-square law** — double the distance, quarter the intensity (the reason point
lights need physically-correct falloff to read right).

## Surface interaction
When light hits a surface it **reflects** (specular = mirror-like at the **Fresnel** angle; diffuse =
scattered), **refracts** (bends entering a medium — index of refraction), is **absorbed** (becomes color +
heat), or **scatters** beneath the surface (**subsurface scattering** — skin, wax, marble, foliage).
**Fresnel** is the key intuition: *everything is more reflective at grazing angles* — the rim of every object,
water at the horizon. Microscopic roughness spreads the reflection (the basis of roughness/glossiness).

## The rendering equation (the one equation)
Outgoing radiance at a point = emitted radiance + the **integral over the hemisphere** of (incoming radiance
× BRDF × cosθ). Every renderer — rasterizer, ray tracer, path tracer — is solving or approximating this. It
encodes **energy conservation** (a surface can't reflect more than it receives) and **why global illumination
matters** (the "incoming radiance" includes light bounced off *everything else*). Memorize its shape and you
know what each technique simplifies.

## Why this is the lever for photoreal
Real-world reference looks right because real light obeys these laws. Approximations look wrong when they
*violate* them (non-conserving materials, missing Fresnel, no indirect light). Photorealism is fidelity to
this physics within budget — see [[img-photoreal-rendering]].

## Related
- hub → [[imaging-foundations]]
- peer ↔ [[img-photoreal-rendering]]
