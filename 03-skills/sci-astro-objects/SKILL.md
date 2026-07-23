---
name: sci-astro-objects
description: >
  Astrophysics of stellar + compact objects, focused on physics AND visual appearance for
  rendering — stellar classification + color temperature (OBAFGKM, the HR diagram), binary/
  multiple systems, black holes (event horizon, accretion disk, gravitational lensing,
  relativistic beaming, jets), neutron stars/pulsars/magnetars, and planets/gas giants/rings.
  How these bodies actually look + why, so a hard-SF render is plausible. Triggers: star,
  stellar classification, color temperature, HR diagram, binary star, black hole, accretion
  disk, gravitational lensing, neutron star, pulsar, gas giant, exoplanet, blackbody.
aliases: [sci-astro-objects]
triggers: [star, stellar classification, color temperature, hr diagram, binary star, black hole, accretion disk, gravitational lensing, neutron star, pulsar, gas giant, exoplanet, blackbody, relativistic beaming]
tier: spoke
hub: science-foundations
domain: science
prerequisites: [science-foundations]
surfaces: ["*"]
spec_version: "2.0"
---

# Astrophysics — Stellar & Compact Objects

The bodies of a galaxy, with the physics that fixes how they *look*. Pairs with [[img-photoreal-rendering]]
(blackbody → color), [[sci-physics-simulation]] (orbits/gravity), and [[sci-astro-structures]] (what they're
embedded in). For Legion: get the physics right and the galaxy reads as hard-SF, not fantasy.

## Stars — color is temperature
A star is a blackbody: its color is its **surface temperature**, not arbitrary. The **OBAFGKM** sequence
runs hot→cool: O/B blue-white (~30,000–10,000 K), A white, F/G yellow-white (Sun ~5,800 K), K orange,
M red (~3,000 K). Map temperature → blackbody RGB for accurate star color (a real starfield is mostly
white/blue-white with scattered orange/red — *not* the rainbow of bad space art). The **HR diagram**
(luminosity vs. temperature) places main-sequence, giants (huge, cool, bright), and white dwarfs (tiny, hot,
dim). Brightness in render = luminosity + inverse-square distance + HDR/bloom (see [[img-photography]]).

## Binary & multiple systems
Most stars are in **binaries/multiples** orbiting a common barycenter (Kepler/Newton — [[sci-physics-simulation]]).
Visual flavor: contrasting-color pairs (blue giant + orange companion), eclipsing binaries (periodic dimming),
mass transfer + accretion streams in close pairs. A binary sky (two suns, double shadows) is a strong sci-fi
visual and physically legitimate.

## Black holes — the showpiece
Not "a black ball." The visuals are relativistic: an **accretion disk** (hot, differentially rotating,
blue-shifted/brighter on the approaching side — **relativistic beaming + Doppler**), **gravitational lensing**
that bends the far side of the disk *over and under* the shadow (the Interstellar/EHT look), the **photon
ring** + black **shadow** (~2.6× the Schwarzschild radius), and relativistic **jets** from the poles.
Approximate in real-time with a lensing post-shader + a bright disk; path-trace for stills.

## Neutron stars, pulsars, magnetars
Stellar corpses: tiny (~20 km), extreme gravity, **pulsars** sweep lighthouse beams (periodic flashes),
**magnetars** have colossal magnetic fields. Visually: intense point sources, beamed jets, sometimes a
surrounding remnant ([[sci-astro-structures]]).

## Planets, gas giants, rings
Terrestrial (rock, thin/no atmosphere), gas/ice giants (banded atmospheres — Jupiter/Neptune palettes,
storms, **rings** = particle fields → render as [[vfx-particle-systems]]/instanced), moons. Atmosphere needs
**Rayleigh/Mie scattering** ([[img-optics-light]]) for the blue-limb + sunset look.

## Related
- foundation → [[science-foundations]]
- hub → [[science-foundations]]
- peer ↔ [[sci-astro-structures]] · [[stellar-and-relativistic-hero-bodies]]
