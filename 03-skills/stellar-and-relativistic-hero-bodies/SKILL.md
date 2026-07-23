---
name: stellar-and-relativistic-hero-bodies
description: >
  The two exotic hero bodies — a star's photosphere/corona and a black hole's relativistic lensing —
  rendered at close zoom. Granulation baked to an animated cube-map + physical limb darkening + blackbody
  LUT + corona as a genuinely new additive raymarch pass; and per-pixel Schwarzschild null-geodesic lensing
  (prefer the analytic elliptic-integral deflection) + Doppler-beamed, redshifted accretion disk. Teaches
  the HONEST verdicts: the star holds 90 FPS with care; the black hole is a scripted slow-camera hero
  moment, not a free-fly default. Triggers: star surface, photosphere, granulation, limb darkening, corona,
  blackbody, black hole, gravitational lensing, geodesic, accretion disk, relativistic beaming, Kerr.
aliases: [stellar-and-relativistic-hero-bodies]
triggers: [star surface, photosphere, granulation, limb darkening, starspot, corona, prominence, blackbody color, black hole, gravitational lensing, geodesic raymarch, schwarzschild, kerr, accretion disk, relativistic beaming, doppler redshift, photon ring, einstein ring, hero body, stellar rendering]
tier: spoke
hub: lead-game-developer
domain: game
prerequisites: [realtime-render-performance-90fps, sci-astro-objects, vfx-volumetrics]
related: [glsl-shader-architect, vfx-particle-systems, atmospheric-scattering-and-clouds]
surfaces: ["*"]
spec_version: "2.0"
---

# Stellar & Relativistic Hero Bodies — the star and the black hole up close

The astrophysical rendering of the two exotic hero bodies. Grouped because both are single-body,
physically-driven, procedurally-shaded, and both **live or die on temporal/coverage strategy** at close
zoom. Pulls physical parameters (Teff, spectral class, ISCO, metric) from [[sci-astro-objects]] (that skill
owns the astrophysics; this owns the *rendering*), reuses [[vfx-volumetrics]] machinery, and rides the frame
spine of [[realtime-render-performance-90fps]].

## Scope and Domain Boundary
- **This skill:** star photosphere/corona rendering **and** black-hole/relativistic lensing rendering.
- → Astrophysics, data, blackbody physics, orbital mechanics: [[sci-astro-objects]].
- → Generic nebula/participating-media raymarch: [[vfx-volumetrics]] (this owns the **new** ray-sphere
  corona integrator and the geodesic raymarcher).
- → Planetary atmosphere / clouds / ocean: [[atmospheric-scattering-and-clouds]].
- → Frame budget, temporal-history, tonemap tradeoffs: [[realtime-render-performance-90fps]].

---

## Part A — Stellar surface

### Photosphere — bake to an animated target (the central lever)
Domain-warped 3D fBm (**4 octaves is the real-time sweet spot**) for the brightness field + a Worley/cellular
layer for granule cells + a thresholded low-frequency layer for **starspots**, written into an **object-space
cube-map** target (cube-map, not equirect — avoids seam/pole pinching) and animated by advancing the noise
time / w-axis. This converts the dominant per-fragment noise from "scales with screen coverage" (catastrophic
at close zoom) to "fixed texel cost, lazily updated."
> **Correction:** at true hero-close a fixed 2K–4K map is bilinear mush — use a **hybrid: amortized baked
> low-frequency + 1–2 `fwidth`-clamped runtime detail octaves**, and budget the **+1–2 ms** of
> coverage-scaling cost that reintroduces.

### The other stellar layers
- **Limb darkening:** `I(μ)/I(1) = 1 − u1(1−μ) − u2(1−μ)²`, `μ = dot(N,V)`; `u1,u2` from a small Teff-indexed
  table (Sing/Claret), per-channel for reddened cool-star limbs. <0.1 ms. (Matters for the mid-field full-disk
  view; at a photosphere close-up μ≈1 everywhere.)
- **Blackbody LUT:** Planck × CIE → linear working space, **≥16-bit / float** 1D texture keyed by Teff
  (8-bit bands visibly). **Separate chromaticity from a hand-tuned exposure curve** — radiance spans ~9 orders
  of magnitude, so a linear drive clips O/B to white and vanishes M dwarfs. Use a wider working space (P3+) or
  explicit gamut mapping; sRGB clips saturated blackbody extremes to negative components.
- **Corona — a genuinely NEW additive volumetric raymarch pass.**
  > **Correction:** "rides the nebula raymarch budget you already pay" is sleight-of-hand — sharing code is
  > not sharing cost. It needs **ray-sphere intersection (inner+outer radii) + 1/r density**, a different
  > integrator from the single-box nebula, and at hero-close it projects across the **entire framebuffer**:
  > 24–40 steps × full coverage × multi-octave turbulent noise is realistically **3–5 ms of new cost**.
  To fit, **re-engineer to ≤2 ms**: screen-coverage-adaptive step count + blue-noise jittered start +
  reprojection, with a **billboard/particle-corona fallback at closest zoom**.
- **Chromosphere rim + prominences/flares:** Fresnel rim add (`pow(1−dot(N,V),k)`, Hα-red). Prominences /
  coronal loops / flares are **event-gated sparse VFX** (curl-noise particle ribbons, additive — see
  [[vfx-particle-systems]]): 0 ms idle, ~0.5–1 ms active, scheduled off corona-heavy frames.
- **LOD granulation suppression + HDR bloom:** `fwidth`/mip octave clamp + distance/limb amplitude fade (the
  SpaceEngine "suppress granulation on upper LODs" trick). Per-star **exposure-relative bloom threshold** so
  an M-dwarf and an O-star both read through one pipeline.

### Stellar 90 FPS reality (honest)
Realistic close-zoom worst case (star + corona fill screen, no nebula): photosphere sample+detail 1.5–2.5 ms,
**corona 3–5 ms**, bloom 1.5–2.5 ms, limb/rim/LUT 0.4 ms, resolve 0.5 ms = **7–11 ms of star alone**. Two
structural hazards: **(a)** the reduced-cadence bake **spikes 1.5–3 ms ON the frame timeline every 2nd–3rd
frame** — Three.js WebGPURenderer gives no reliable async-compute overlap to hide it, and 90 FPS is a
**worst-frame** problem; **(b)** VRAM is real — a 4K RGBA16F map double-buffered is 128 MB, a 6×2K cube-map
384/768 MB, a hard constraint on per-tab browser GPU limits. Verdict: **qualified yes on desktop** once the
corona is re-engineered.

### Stellar failure modes
Granulation shimmer at the limb (LOD/`fwidth` suppression + fade; verify at native res) · cube-map vs equirect
seam/pole (sample 3D noise in object space; prefer cube-map) · blackbody blowing out the tonemapper
(**ACES hue-shifts blue→purple / red→orange; AgX desaturates bright cores and can erase low-contrast
granulation ΔT** — choose deliberately and verify the signal survives) · "cartoon lava" over-contrast (derive
granule ΔT from real photometry, few-hundred K, low contrast; let HDR do the drama) · temporal strobing from
the reduced-cadence bake (temporally blend two bake frames) · **missing star-as-light-source** (a close hero
star is the dominant illuminant; its IBL probe must re-render as the camera descends) · missing faculae/plage
(nearly free as another thresholded bake layer) · **TAA interaction** (animate/reproject the noise field in a
space where velocity *can* be computed, or the surface ghosts and the additive corona throws fireflies).

---

## Part B — Black hole & relativistic rendering

### Hero technique — per-pixel null-geodesic raymarch (Schwarzschild)
Only per-pixel geodesic integration yields a correct **photon ring, Einstein ring, and horizon shadow** — the
entire payoff of a close zoom. Every cheaper family (screen-space UV warp, billboard distortion) has no
multi-image structure, reads as fake up close, and is a **distant-LOD tier only**. Fix the orbital plane per
ray; integrate `d²u/dφ² = (3/2)·r_s·u² − u` (`u = 1/r`) with **adaptive stepping** (coarse far, dense near the
photon sphere — mandatory, not an optimization). Absorb horizon-crossing rays; sample the HDR starfield for
escapees.

### Prefer the analytic elliptic-integral deflection (the biggest win)
The exact Schwarzschild deflection has a closed form in Jacobi/incomplete elliptic integrals of the first
kind, with fast approximate-analytic forms (arXiv:1608.04574) that translate directly to high-speed ray
tracing. It sits **between** live ODE and precomputed tables: a few special-function evals per pixel, O(1)-ish,
**no table asset, all camera distances**, and **no per-lane step-count SIMT divergence**. This is the best fit
for a free-fly zoom and should be the **primary** path, not live RK4.

### Accretion disk (composable on any integrator)
Optically-thin disk from ISCO (~3 r_s) outward, Shakura-Sunyaev `T ∝ r^(−3/4)` → blackbody LUT, **both**
relativistic Doppler beaming (`I ∝ δ⁻³`) **and** gravitational redshift combined — half of either reads
uncanny. Beer's-law vertical density. Cheap relative to the geodesic march.

### Ring anti-aliasing — beam/cone footprint, not just supersampling
Lensing folds the sky, so a single starfield texel fetch aliases catastrophically. **Use the ray/beam
footprint to select the HDR starfield env-map MIP level** — footprint-driven mipped area sampling is the
actual fix (the DNGR ray-bundle lesson made practical), and it is cheap.

### Kerr — gate hard behind a scripted quality tier
> **Correction:** cost is ~**3–5× Schwarzschild plus a symplectic/Yoshida integrator**, not 1.7–2×. Kerr
> geodesics are non-planar (carry the Carter constant, integrate the full system, handle Boyer-Lindquist
> horizon singularities). Half-implemented spin reads as a bug.

### Black-hole 90 FPS reality (honest — this is an open research risk)
The two budget-closing levers the optimistic framing leaned on **specifically destroy the ring**:
**(1) Temporal accumulation is broken at the photon ring** — a bent ray has no single well-defined prior-frame
world position, so motion vectors are undefined/many-to-one exactly there; jittered accumulation works only for
a **locked camera** and smears the ring under motion. **(2) Half-res + bilinear upscale aliases the ring, ISCO
edge, and thin Einstein arcs** — the highest-frequency, sub-pixel content in the frame. **(3) SIMT divergence**
— reserving dense steps only for the annulus saves work only when expensive pixels are coherently grouped; the
fix is explicit **tile/bin classification + separate dispatch** (ring annulus at full/super-res, sky at
quarter-res), not per-lane early-out (no hardware VRS in WebGPU). **(4) No WGSL fp64** — the `u=1/r`
formulation has catastrophic cancellation near the photon sphere; FP32-only integration is a real precision
risk for a body defined by a razor-thin critical curve. **(5) Only the skybox is lensed** — scene geometry
composited after the pass cannot bend around the shadow without marching it through the metric (large extra
cost).

**Verdict:** achievable as a **scripted, slow-/static-camera hero moment at ~60 FPS on a discrete GPU**
(RTX 3060-class+ / M3 Pro+); **not** a free-fly, any-camera, any-hardware 90 FPS default. There is **zero
interactive-game shipping precedent** — per-pixel geodesic lensing exists only in tech demos and offline film.
Treat as an open research risk, not a solved budget line.

### Relativistic failure modes
Photon-ring aliasing/flicker (footprint MIP + annulus supersample + locked-camera-only accumulation) · integrator
instability near the horizon (adaptive stepping; symplectic for Kerr) · screen-space lensing used for the hero
shot (distant-LOD only; **plan the LOD transition band** screen-warp → analytic → full geodesic or you relocate
the artifact to a visible pop) · disk banding / blown highlights (feed HDR pre-tonemap; verify the δ⁻³ beaming
asymmetry survives — AgX can flatten the blue-shifted leading edge) · redshift/beaming half-implemented (both
terms, always) · camera aberration at ISCO-orbital speeds (compose with the static lensing solution) · no GRRT
reference (validate against ipole/RAPTOR/EHT imagery at matching parameters, not "looks like Interstellar").

## Cited sources
- Podgursky, *Procedural star rendering with three.js and WebGL shaders* (2017) — https://bpodgursky.com/2017/02/01/procedural-star-rendering-with-three-js-and-webgl-shaders/
- Smith (Overdraw.xyz), *Using cellular noise to generate procedural stars* (2018) — https://www.overdraw.xyz/blog/2018/7/17/using-cellular-noise-to-generate-procedural-stars
- Sing, *Stellar limb-darkening coefficients* (A&A, 2010) — https://www.aanda.org/articles/aa/full_html/2010/02/aa13675-09/aa13675-09.html
- Macklin, *Blackbody Rendering* (2010) — https://blog.mmacklin.com/2010/12/29/blackbody-rendering/
- SpaceEngine / Romanyuk, *Starlight* (granulation LOD suppression, 2017) — https://spaceengine.org/news/blog170420/
- Nguyen, *Black Hole — WebGPU Raymarcher* (2026) — https://martinnguyen.me/projects/blackhole/
- Seiskari (oseiskar), *Physics of a black-hole visualization* (2015) — https://oseiskar.github.io/black-hole/docs/physics.html
- Antonelli (rantonels), *Starless / Raytracing a black hole* (2015) — https://rantonels.github.io/starless/
- *Approximate analytical photon geodesics in Schwarzschild* (arXiv:1608.04574, 2016) — https://arxiv.org/abs/1608.04574
- Bruneton, *Real-time High-Quality Rendering of Non-Rotating Black Holes* (2020) — https://ebruneton.github.io/black_hole_shader/
- James, von Tunzelmann, Franklin, Thorne, *Gravitational Lensing by Spinning Black Holes* (Interstellar / DNGR, 2015) — https://arxiv.org/abs/1502.03808

## Related
- hub → [[lead-game-developer]]
- peer ↔ [[sci-astro-objects]] · [[vfx-volumetrics]] · [[vfx-particle-systems]] · [[glsl-shader-architect]]
