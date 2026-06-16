---
name: sci-astro-structures
description: >
  Astrophysics of large-scale structures, focused on physics AND appearance for rendering —
  nebulae (emission, reflection, dark, planetary, supernova remnants) and what colors them,
  galaxies (spiral/elliptical/irregular structure, arms, bulge, halo, dust lanes), the
  interstellar medium + dust, star-forming regions, and cosmic scale. How to make a galaxy
  read as real. Triggers: nebula, emission nebula, reflection nebula, dark nebula, planetary
  nebula, supernova remnant, galaxy, spiral arm, dust lane, interstellar medium, star forming,
  H-alpha, cosmic scale, parsec, light year.
aliases: [sci-astro-structures]
triggers: [nebula, emission nebula, reflection nebula, dark nebula, planetary nebula, supernova remnant, galaxy, spiral arm, dust lane, interstellar medium, star forming, h-alpha, cosmic scale, parsec, light year]
tier: spoke
hub: science-foundations
domain: science
prerequisites: [science-foundations]
surfaces: ["*"]
spec_version: "2.0"
---

# Astrophysics — Nebulae, Galaxies & Scale

The large-scale structures, with the physics that fixes their color + form. Pairs with [[vfx-volumetrics]]
(render nebulae as volumes), [[sci-astro-objects]] (what populates them), and [[img-optics-light]] (scattering
+ emission). For Legion: nebula color and galaxy structure are where space art most often goes wrong.

## Nebulae — color has a cause
Type determines look (don't paint arbitrary purples):
- **Emission** — ionized gas glowing at specific lines: **H-alpha red** (the dominant cosmic red), **O III
  teal/green**, S II deeper red. Star-forming regions (e.g. Orion, Eagle) are emission + dust.
- **Reflection** — dust scattering nearby starlight; **blue** (Rayleigh-like — short wavelengths scatter more).
- **Dark / absorption** — cold dust blocking light (silhouettes, Bok globules, the Horsehead). Negative space.
- **Planetary** — a dying star's shed shell, often O III teal rings/shells.
- **Supernova remnant** — filamentary, shock-heated, expanding (the Veil); often with a neutron star inside.
Real nebulae are *faint and diffuse* — the saturated Hubble images are stretched + false-color. For a
believable look: layered volumetric density + emission color by gas type + embedded stars, not opaque clouds.

## Galaxies — structure
- **Spiral** — flat **disk** with **arms** (density waves, brightest where star formation is — blue young
  clusters + pink H-alpha knots along the arms), a yellow-red central **bulge**, dark **dust lanes** tracing
  the arms, a faint spherical **halo** of old stars + globular clusters.
- **Elliptical** — smooth, old (red/yellow), little dust/structure.
- **Irregular** — chaotic, often interacting.
The Milky Way (Legion's likely template) is a barred spiral; from inside, it's the band of the night sky
(dense star fields + dark dust rifts). Render: instanced **point/sprite stars** by population color +
volumetric arms/dust + bulge glow.

## Interstellar medium, star formation, scale
The **ISM** is gas + dust between stars (the raw material — denser in arms). **Star-forming regions** =
emission nebula + young hot blue stars + dust. **Scale** is the hard part: AU (planets), light-years (stars),
**parsecs/kiloparsecs** (galaxy). These spans break naive float precision — the camera/precision problem is
[[game-scale-traversal]].

## Related
- foundation → [[science-foundations]]
- hub → [[science-foundations]]
- peer ↔ [[sci-astro-objects]] · [[vfx-volumetrics]]
