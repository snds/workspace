---
name: atmospheric-scattering-and-clouds
description: >
  Physically-based planetary atmosphere (Hillaire 2020 LUT pipeline), bespoke WGSL volumetric clouds
  with a hand-rolled temporal-reconstruction subsystem, FFT + Gerstner oceans, and the night side —
  everything gaseous or liquid layered on a planet, seen from surface AND orbit, at 90 FPS. Owns the
  planet-facing volumetric/scattering pipeline and its WebGPU-specific gaps. Triggers: atmospheric
  scattering, Rayleigh, Mie, Hillaire sky, aerial perspective, volumetric clouds, Nubis, cloud shadows,
  FFT ocean, Gerstner, planetary atmosphere, terminator.
aliases: [atmospheric-scattering-and-clouds]
triggers: [atmospheric scattering, rayleigh, mie, hillaire, sky atmosphere, aerial perspective, transmittance lut, multiple scattering, volumetric clouds, nubis, cloud shadows, perlin-worley, henyey-greenstein, ocean rendering, fft ocean, tessendorf, gerstner, planetary atmosphere, terminator, night side]
tier: spoke
hub: lead-game-developer
domain: game
prerequisites: [realtime-render-performance-90fps, vfx-volumetrics]
related: [glsl-shader-architect, planetary-terrain-lod, threejs-vfx-atmosphere]
surfaces: ["*"]
spec_version: "2.0"
---

# Atmospheric Scattering & Clouds — the planet's gaseous/liquid layers

Physically-based sky, cloud, and ocean rendering on a planet, correct from the surface **and** from orbit,
at 90 FPS. The planet-facing counterpart to the stellar volumetrics in
[[stellar-and-relativistic-hero-bodies]]; composites onto [[planetary-terrain-lod]] and rides the frame
spine of [[realtime-render-performance-90fps]].

## Scope and Domain Boundary
- **This skill:** breathable-atmosphere scattering, cloud decks + their temporal reconstruction, water,
  night side. Deepens/supersedes [[threejs-vfx-atmosphere]] and [[vfx-volumetrics]] **for the planet case**
  (those cover generic post-FX and nebula volumetrics; this owns the physically-based sky + cloud + ocean
  pipeline and its WebGPU gaps).
- → Terrain it composites onto: [[planetary-terrain-lod]] (consumes the aerial-perspective froxel).
- → Stellar corona / photosphere: [[stellar-and-relativistic-hero-bodies]].
- → Frame budget, half-res + temporal reconstruction reality: [[realtime-render-performance-90fps]].

## The honest priority: atmosphere is cheap, clouds are where 90 FPS breaks
The scattering half (Hillaire) is genuinely cheap and correctly prioritized — it is **not** the bottleneck.
**Clouds and their temporal reconstruction are the largest, hardest engineering item in this pillar** and
must be treated as first-class subsystem work, not a drop-in.

## Atmosphere backbone — Hillaire 2020 LUT pipeline
Four passes:
- **Transmittance LUT** (256×64) + **Multiple-Scattering LUT** (32×32) — view-independent, computed once,
  re-run only on parameter change.
- **Sky-View LUT** (~192×108) + **Aerial-Perspective froxel** (32³–64×64×32) — regenerated per frame.

Exponential Rayleigh + Mie + tent-shaped ozone. This is the **only** method that renders the same body
correctly from surface **and** orbit with a moving sun, without 4D LUTs. Port from
**JolifantoBambla/webgpu-sky-atmosphere** (real, working WGSL/compute reference). The **aerial-perspective
froxel hazes distant terrain for free** — but it **must** use a **log-depth froxel slice distribution
reconciled with reversed-Z**, or distant haze pops. The **multiscatter LUT supplies ambient fill and must
be on from the surface**, or you get a black daytime/twilight sky. Bruneton 2008/2017 is the ground-truth
**validation** reference, not the runtime path.

## Clouds — fully bespoke WGSL, Nubis recipe (NOT a drop-in)
> **Correction (survived adversarial review):** `@takram/three-clouds` gives you nothing here — it is
> GLSL-only, no WebGPU, no TSL, Earth-specific. Clouds are fully bespoke WGSL.

- **Modeling:** Perlin-Worley base + Worley detail erosion, 2D weather map coverage, **dual-lobe
  Henyey-Greenstein** (forward silver lining + back-scatter), Beer + powder.
- **Marching:** at **half resolution**, 64–128 adaptive steps with Beer's-law early-out, ~6 cone-tap light
  samples, blue-noise / IGN jittered start offset per pixel.
- **Reconstruction:** a **hand-rolled temporal-reprojection subsystem you must build** — MRT motion vectors,
  history buffer, transmittance-weighted variance clipping, neighborhood clamp. Three.js TSL has **no**
  production temporal-reprojection node.
- **Bottleneck on the median device is 3D-noise texture-fetch bandwidth** (128³ base + Worley detail,
  sampled per-step per-light-tap), not ALU.

## Ocean — Tessendorf FFT + Gerstner
2–3 cascades of 256×256 complex IFFT via **hand-rolled compute butterfly passes** (log₂N ping-pong per axis)
for height + choppy displacement + slope/normal; blend to summed Gerstner/trochoidal for close-up and shore.
Wavelength-dependent absorption for blue-offshore / green-nearshore. **Open gap — flag before an ocean world
ships:** blending flat FFT tiles onto planetary curvature without seams at tile boundaries/horizon in
floating-origin coordinates is unsolved here; it needs a projection scheme.

## Night side
Soft `smoothstep(dot(N, sunDir))` terminator gating an emissive city-lights layer below a small negative
sun-elevation threshold. Effectively free. (Legion's storm/city-light layers live in the planet shader —
keep terminator gating continuous to avoid the flashing-storm class of bugs.)

## Per-body LOD (mandatory — the VRAM fix)
Full LUT + clouds + FFT **only for the hero body**; distant bodies fall back to single-pass analytic
atmosphere + static cloud texture + shared/parameterized LUTs. Only the hero body holds a **live LUT set** —
this is the fix for LUT-VRAM blowup.

## 90 FPS budget reasoning (honest)
Hillaire's native figures (0.12 ms multiscatter, 0.11 ms aerial, <2 ms Nubis) are **console/discrete-desktop**
numbers; **in-browser on integrated GPUs expect 2–5× inflation** (Dawn/WGSL pipeline overhead, bind-group
churn, shared bandwidth). "Sub-millisecond" ocean FFT is discrete-desktop-only; on integrated, ping-pong
bind-group overhead pushes 3 cascades toward 1–2 ms. Pillar target **~3.5–5 ms holds on discrete; on
integrated the honest target is 60 FPS + DRS**.

## Failure modes to avoid
- **Missing depth-aware (bilateral / nearest-depth) upsample** of the half-res cloud buffer against full-res
  terrain → edge halos, mountains poking through clouds with wrong occlusion. The classic half-res-volumetric
  artifact; must be built.
- **The through-cloud transition** (flying down through the deck) — the target scenario and where temporal
  reprojection breaks worst (massive disocclusion, parallax). Needs **per-cloud advection motion vectors**,
  not camera-only reprojection.
- **Missing cloud shadows on terrain/ocean** — dappled ground shadows are a primary close-zoom cue; the
  cloud pass must emit a ground-shadow term.
- **Horizon LUT parameterization crush** — copy Hillaire/Bruneton constant-φ / squared-distance mapping
  exactly; don't improvise.
- **Single-scattering-only** → black daytime/twilight sky — multiscatter LUT on from the surface.
- Cloud ghosting/trails — transmittance-weighted variance clip + neighborhood clamp.
- Powder/phase overshoot → grey "dirty" clouds or a hard silver ring — dual-lobe HG blend.
- Ocean FFT tile repetition — multiple cascades + large-scale detail break; **spherical tiling is an open
  gap** (above).
- Aerial-perspective froxel starvation at range — log-depth slice distribution.

## Cited sources
- Hillaire, *A Scalable and Production Ready Sky and Atmosphere Rendering Technique* (2020) — https://sebh.github.io/publications/egsr2020.pdf
- Bruneton & Neyret, *Precomputed Atmospheric Scattering* (2008 / 2017 reimpl) — https://ebruneton.github.io/precomputed_atmospheric_scattering/
- JolifantoBambla, *webgpu-sky-atmosphere* (WGSL port, 2024) — https://github.com/JolifantoBambla/webgpu-sky-atmosphere
- Schneider & Vos, *The Real-time Volumetric Cloudscapes of Horizon: Zero Dawn (Nubis)* (2015) — https://www.guerrilla-games.com/read/nubis-authoring-real-time-volumetric-cloudscapes-with-the-decima-engine · *Nubis, Evolved* (2022) https://www.guerrilla-games.com/read/nubis-evolved
- Häggström, *Real-time rendering of volumetric clouds* (full shader ref, 2018) — https://www.diva-portal.org/smash/get/diva2:1223894/FULLTEXT01.pdf
- Tessendorf, *Simulating Ocean Water* (2001/04) — https://jtessen.people.clemson.edu/reports/papers_files/coursenotes2004.pdf
- Sakmary, *Real-time Rendering of Atmosphere and Clouds in Vulkan* (architecture ref, 2023) — https://cescg.org/wp-content/uploads/2023/04/Sakmary-Real-time-Rendering-of-Atmosphere-and-Clouds-in-Vulkan.pdf

## Related
- hub → [[lead-game-developer]]
- peer ↔ [[vfx-volumetrics]] · [[threejs-vfx-atmosphere]] · [[planetary-terrain-lod]] · [[glsl-shader-architect]]
