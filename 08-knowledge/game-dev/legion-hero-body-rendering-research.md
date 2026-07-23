---
tags: [game-dev, legion, rendering, webgpu, threejs, performance, planetary-terrain, stellar, black-hole, atmosphere, clouds, temporal-upsampling, research, dossier]
created: 2026-07-22
updated: 2026-07-22
status: stable
confidence: high
sources:
  - "workflow:legion-fidelity-research — 16 agents, 5-pillar web research + adversarial verification, 2026-07-22 (1.08M tokens, 156 web tool-uses)"
  - "Hillaire 2020 (scalable sky/atmosphere); Bruneton 2008/2020; Strugar CDLOD 2010; Schneider Nubis 2015/2022; James/Thorne 2015 (DNGR); Reed depth-precision 2015; Tessendorf ocean"
related_skills: [planetary-terrain-lod, atmospheric-scattering-and-clouds, stellar-and-relativistic-hero-bodies, realtime-render-performance-90fps, game-scale-traversal, webgpu-advanced-rendering, glsl-shader-architect, vfx-volumetrics, sci-astro-objects]
related_projects: [13-legion]
---

> **Provenance & status.** This dossier is the synthesized, adversarially-verified output of the
> `legion-fidelity-research` workflow (5 parallel pillar deep-dives → per-claim skeptic verification →
> synthesis; 2026-07-22). It is the **authoring source** for four new spoke skills —
> [[planetary-terrain-lod]], [[atmospheric-scattering-and-clouds]], [[stellar-and-relativistic-hero-bodies]],
> [[realtime-render-performance-90fps]]. Claims that did **not** survive review are quarantined in the
> Appendix; do not author them as fact. Every budget figure is a *planning estimate pending
> `timestamp-query` measurement on target hardware* (framework #06 Proofboard obligation).

# Legion Hero-Body Rendering — Master Research Dossier

**Target:** SpaceEngine-class fidelity on a single hero body (planet surface, star photosphere, or black hole) at very close zoom, holding a 90 FPS / 11.1 ms frame in a Three.js + WebGPU (WebGPURenderer + TSL / WGSL compute) browser target.
**Status:** Synthesis of five verified pillar dossiers, filtered through adversarial review. Where the optimistic dossier claim did not survive review, this document states the honest verdict. **This is the authoring source for four new workspace spoke skills (§5).**

---

## 0. The one-paragraph honest verdict

90 FPS at hero-close is **achievable for a planet surface and a star photosphere on a mid-to-high discrete desktop GPU**, achievable at **60 FPS with dynamic resolution on integrated GPUs**, and for a **black hole is realistically a scripted slow-/static-camera hero moment**, not a free-fly any-hardware default. Three things the individual dossiers under-weighted decide the outcome and must be designed in from day one: (1) **the real in-browser GPU budget is ~8–9 ms, not 11.1 ms** — compositor deadline, `requestAnimationFrame` jitter, JS GC, and queue-submit overhead consume ~1.5–2 ms, and 90 Hz only exists on 90 Hz+ panels; (2) **procedural cost must be baked/amortized, never paid inline per frame at full screen coverage** — this is the single largest lever for terrain noise, photosphere granulation, and volumetrics; (3) **temporal upsampling (TAAU) is a co-development bet, not a drop-in, and it fails precisely on the motion-vector-less content that dominates hero bodies** (procedural surface noise, volumetrics, particles, gravitationally-lensed backgrounds), so per-content temporal strategy is mandatory. The geometry/precision/culling foundation is solid and cheap; the frame breaks on **fill-rate + procedural-ALU/bandwidth + temporal disocclusion**, in that order.

---

## 1. Executive summary — recommended architecture

### 1.1 Shared spine (all hero bodies)
- **Precision spine (already in Legion, keep):** floating-origin / camera-relative rendering + **reversed-Z with `depth32float`** (near→1, far→0, `GREATER` test, clear = 0.0) as the modern default (Reed: ~0% indistinguishable-depth vs 77% for standard float32). Logarithmic depth retained **per-vertex** for the galactic→surface range, **per-fragment only on the hero body's near shells** (writing `gl_FragDepth`/`frag_depth` disables early-Z, and WebGPU has **no shipped conservative-depth escape hatch** — the WGSL proposal gpuweb #5342 is not in browsers).
- **Rasterization path (decided, non-negotiable):** **compute-generated / compute-selected meshes + `drawIndexedIndirect`.** WebGPU 2026 has **no tessellation shaders, no geometry shaders, no mesh shaders, and no hardware VRS** — do not prototype any of them. Compute + indirect is both the only available path and current best practice.
- **Post spine (already in Legion):** ACES/AgX tonemap + bloom + IBL. Note the tonemap caveats below — ACES hue-shifts saturated emissives, AgX desaturates bright cores; neither is neutral for physically-colored stars/disks.
- **Temporal + dynamic resolution as one system:** internal render at sub-native scale, resolved to native by a hand-rolled TAAU, wrapped in app-level dynamic resolution scaling (DRS) driven by `timestamp-query` (with a CPU-timer fallback). There is **no ML upscaler in-browser** (no DLSS/FSR-FG/tensor access) — TAAU is the only temporal-upscale option and has no vendor fallback.

### 1.2 Per-body headline
| Hero body | Core technique | Dominant cost | 90 FPS honesty |
|---|---|---|---|
| **Planet surface** | Cube-sphere quadtree + CDLOD morph, height+normal **baked per-patch on subdivision**, triplanar procedural shading | Terrain **generation/compute** (noise ALU) + atmosphere fill | Yes on desktop dGPU after continuous-LOD + Hillaire LUT atmosphere land; no on integrated at full res |
| **Star photosphere** | Granulation **baked to animated target** + physical limb darkening + blackbody LUT + **corona as a new additive raymarch pass** | Corona fill (full screen at close zoom) + bake spike variance | Qualified yes desktop; corona must be re-engineered to ≤2 ms |
| **Black hole** | Per-pixel Schwarzschild null-geodesic (prefer **analytic elliptic-integral deflection**) + Doppler+redshift disk | Geodesic step count near photon sphere; temporal reprojection broken at the ring | Scripted slow/static hero moment only; free-fly is open research |

---

## 2. Per-pillar sections

### 2.1 Planetary terrain LOD & surface fidelity

**Recommended stack**
1. **Structure — cube-sphere quadtree.** Six cube faces, each a restricted quadtree (±1 neighbor level), patches = a shared static grid (33×33 or 65×65) instanced per node; subdivide by screen-space edge error. Use an **area-equalizing warp (tangent-adjusted / Cobb), not raw cube normalization**, to avoid corner cell-size distortion.
2. **LOD transition — CDLOD per-vertex morph.** LOD is a function of true 3D distance (correct at any observer height). Odd-index vertices morph to their even-index coarse neighbor across the last 15–30 % of each range → adjacent edges become bit-identical before swap. Kills popping **and** T-junction cracks in one mechanism, pure vertex-shader math (trivial in TSL/WGSL). Add **short skirts only if QA still shows hairline seams**; long skirts flap at grazing angles.
3. **Geometry generation — bake, do not synthesize inline.** *This is the review's biggest correction.* Height + analytic normal are **baked into a per-patch texture on subdivision** (async compute), so the per-frame vertex cost collapses to a texture fetch — this is the actual reason CDLOD is cheap. Inline per-frame synthesis of 12–16 octaves of domain-warped ridged fBm over ~1 M+ visible verts blows the budget at close zoom. At true hero-close, a fixed baked patch cannot hold sub-pixel detail, so use a **hybrid: amortized baked low-frequency field + 1–2 `fwidth`-clamped runtime detail octaves** — and budget the +1–2 ms those runtime octaves reintroduce.
4. **Height + shading.** Ridged multifractal + domain-warped fBm with **analytic derivatives (IQ "morenoise")** — normals come from the gradient for free, avoiding ~5 finite-difference evals *and* cross-boundary normal seams. **Band-limit octaves per LOD** (4–6 far, 12–16 near) so each patch only synthesizes frequencies its grid can represent. **Triplanar procedural material blend** driven by slope/altitude/latitude — no polar-UV singularity. Exploit shipped **`shader-f16`** for noise accumulation and **`subgroups`** for reductions (both live in 2026; feature-detect).
5. **Precision — per-patch local origin.** Do sphere-displacement math in a patch-local float32 frame; reconcile to planet space in JS float64; **sample noise in a stable planet-fixed frame** (never camera-relative, or terrain crawls). float32 ULP at Earth radius (~6.37 M m) is ~0.76 m — sub-meter jitter is guaranteed without this. Table stakes.
6. **Culling — frustum + planet-horizon.** Reuse the CDLOD min/max quadtree; **inflate the horizon angle by each node's stored maxZ** so mountaintops aren't culled. Removes the entire far hemisphere at surface — the difference between a few hundred and many thousand candidate patches.

**Why:** geometry/LOD is the *solved* part; fidelity comes from noise detail + shading, not raw polygon count, so the frame is dominated by procedural ALU and shading — both of which have clean quality dials (octave count, screen-space error threshold, CDLOD `RenderGridResolutionMult`).

**90 FPS budget reasoning:** CDLOD's 1198 FPS/446k-tri figure is **prebaked-heightmap-fetch** performance and must **not** be read as evidence for procedural synthesis — different cost class. The honest terrain line item is the **noise bake amortized across patch residency**, plus the hybrid runtime detail octaves. The geometry/morph/traversal machinery is genuinely near-free.

**Phasing:** v1 = CPU quadtree traversal + GPU CDLOD morph + **baked-on-subdivision** height/normal + triplanar. v2 = migrate traversal to GPU-driven compute-quadtree + indirect draw *only after profiling shows draw calls/CPU in the budget* (unlikely at close zoom on one body). v3 = async hydraulic-erosion bakes (Mei et al.) on near-surface patches, **throttled** (N bakes/frame, prefetch along descent) to avoid the bake stampede; virtual texturing only if real albedo/DEM is ever mixed in.

**Failure modes to avoid**
- Vertex jitter / "swimming" (float32 at planet radius) — #1 close-zoom failure. Fix: per-patch local origin + float64 reconcile + planet-fixed noise.
- LOD popping — CDLOD morph across last 15–30 %.
- Cracks / T-junctions — restricted quadtree + morph + short skirts backup.
- Normal/shading seams — analytic-derivative normals from the same noise; blend the normal in the morph region, not just position.
- Noise shimmer — band-limit per LOD; **band-limiting alone is insufficient for specular/material-boundary shimmer — you still need TAA** (see §2.5).
- Horizon-cull pop — inflate by maxZ.
- Erosion-bake hitch — throttle the queue.
- Shadow-map LOD mismatch — frustum-cull on shadow camera but **LOD-select on the main camera**.
- Log-depth per-fragment defeats early-Z / Hi-Z at the overdraw-heavy close-zoom case — restrict to near shells.

**Cited sources**
| Title | Author | Year | URL |
|---|---|---|---|
| Continuous Distance-Dependent LOD (CDLOD) | Filip Strugar | 2010 | https://aggrobird.com/files/cdlod_latest.pdf |
| CDLOD reference implementation | Filip Strugar | 2010 | https://github.com/fstrugar/CDLOD |
| Procedural Planetary Multi-resolution Terrain Generation for Games | d'Oliveira & Apolinario | 2018 | https://arxiv.org/pdf/1803.04612 |
| Analytic Derivatives of Noise (morenoise) | Inigo Quilez | 2008–19 | https://iquilezles.org/articles/morenoise/ |
| fBm / Domain warping | Inigo Quilez | 2002–19 | https://iquilezles.org/articles/fbm/ · https://iquilezles.org/articles/warp/ |
| Fast Hydraulic Erosion Simulation on GPU | Mei, Decaudin, Hu | 2007 | http://www-evasion.imag.fr/Publications/2007/MDH07/FastErosion_PG07.pdf |
| 3D Engine Design for Virtual Globes (floating-origin, horizon cull) | Cozzi & Ring | 2011 | https://www.virtualglobebook.com/ |
| WebGPU (no tessellation/mesh shaders; compute+indirect is the path) | Xor (GM Shaders) | 2024 | https://mini.gmshaders.com/p/webgpu |

---

### 2.2 Atmospheric scattering, clouds & oceans

**Recommended stack**
1. **Atmosphere backbone — Hillaire 2020 LUT pipeline.** Four passes: **Transmittance LUT** (256×64) + **Multiple-Scattering LUT** (32×32), both view-independent, computed once and re-run only on parameter change; **Sky-View LUT** (~192×108) + **Aerial-Perspective froxel** (32³–64×64×32), regenerated per frame. Exponential Rayleigh + Mie + tent-shaped ozone. This is the only method that renders the same body correctly from surface **and** orbit with a moving sun, without 4D LUTs. Port from **JolifantoBambla/webgpu-sky-atmosphere** (real, working WGSL/compute reference). The **aerial-perspective froxel hazes distant geometry for free** — must use **log-depth froxel slice distribution reconciled with reversed-Z**, or distant haze pops. Bruneton 2008/2017 is the ground-truth validation reference, not the runtime path.
2. **Clouds — fully bespoke WGSL, Nubis recipe.** *Correction: takram gives you nothing here — @takram/three-clouds is GLSL-only, no WebGPU, no TSL, Earth-specific. Clouds are the largest and hardest engineering item in this pillar, not a drop-in.* Perlin-Worley base + Worley detail erosion, 2D weather map coverage, **dual-lobe Henyey-Greenstein** (forward silver lining + back-scatter), Beer + powder. Raymarch at **half resolution**, 64–128 adaptive steps with Beer's-law early-out, ~6 cone-tap light samples, blue-noise/IGN jittered start offset per pixel. Reconstruct to full-res with a **hand-rolled temporal reprojection subsystem** you must build (MRT motion vectors, history buffer, transmittance-weighted variance clipping, neighborhood clamp) — Three.js TSL has no production temporal-reprojection node.
3. **Ocean — Tessendorf FFT + Gerstner.** 2–3 cascades of 256×256 complex IFFT via hand-rolled compute butterfly passes (log₂N ping-pong per axis) for height + choppy displacement + slope/normal; blend to summed Gerstner/trochoidal for close-up and shore. Wavelength-dependent absorption for blue-offshore/green-nearshore.
4. **Night side.** Soft `smoothstep(dot(N,sunDir))` terminator gating an emissive city-lights layer below a small negative sun-elevation threshold. Effectively free.
5. **Per-body LOD (mandatory).** Full LUT+clouds+FFT only for the hero body; distant bodies fall back to single-pass analytic atmosphere + static cloud texture + shared/parameterized LUTs. This is the fix for LUT-VRAM blowup — only the hero body holds a live LUT set.

**Why:** the atmosphere half is genuinely cheap and correctly prioritized (Hillaire); it is **not** where 90 FPS breaks. Clouds and their temporal reconstruction are.

**90 FPS budget reasoning (honest):** Hillaire's native figures (0.12 ms multiscatter, 0.11 ms aerial, <2 ms Nubis) are **console/discrete-desktop** numbers; in-browser on integrated GPUs expect **2–5× inflation** (Dawn/WGSL pipeline overhead, bind-group churn, shared bandwidth). Cloud bottleneck on the median device is **3D-noise texture-fetch bandwidth** (128³ base + Worley detail, sampled per-step per-light-tap), not ALU. "Sub-millisecond" ocean FFT is discrete-desktop-only; on integrated the ping-pong bind-group overhead pushes 3 cascades toward 1–2 ms. Pillar target ~3.5–5 ms holds on discrete; on integrated the honest target is 60 FPS + DRS.

**Failure modes to avoid**
- Horizon LUT parameterization crush — copy Hillaire/Bruneton constant-φ / squared-distance mapping exactly, don't improvise.
- Single-scattering-only → black daytime/twilight sky — the multiscatter LUT supplies ambient fill and must be on from the surface.
- **Missing depth-aware (bilateral/nearest-depth) upsample** of the half-res cloud buffer against full-res terrain → edge halos, mountains poking through clouds with wrong occlusion. *The classic half-res-volumetric artifact; must be built.*
- **The through-cloud transition** (flying down through the deck) — the target scenario and where temporal reprojection breaks worst (massive disocclusion, parallax). Needs **per-cloud advection motion vectors**, not camera-only reprojection.
- **Missing cloud shadows on terrain/ocean** — dappled ground shadows are a primary close-zoom cue; the cloud pass must emit a ground-shadow term.
- Cloud ghosting/trails — transmittance-weighted variance clip + neighborhood clamp.
- Powder/phase overshoot → grey "dirty" clouds or hard silver ring — dual-lobe HG blend.
- Ocean FFT tile repetition — multiple cascades + large-scale detail break.
- Aerial-perspective froxel starvation at range — log-depth slice distribution.
- **Spherical-ocean tiling is an open gap** — blending flat FFT tiles onto planetary curvature without seams at tile boundaries/horizon in floating-origin coords is unsolved in the recommendation; needs a projection scheme before an ocean world ships.

**Cited sources**
| Title | Author | Year | URL |
|---|---|---|---|
| A Scalable and Production Ready Sky and Atmosphere Rendering Technique | Sébastien Hillaire | 2020 | https://sebh.github.io/publications/egsr2020.pdf |
| Precomputed Atmospheric Scattering (+2017 reimpl) | Bruneton & Neyret | 2008/2017 | https://inria.hal.science/inria-00288758/file/article.pdf · https://ebruneton.github.io/precomputed_atmospheric_scattering/ |
| webgpu-sky-atmosphere (WGSL port) | JolifantoBambla | 2024 | https://github.com/JolifantoBambla/webgpu-sky-atmosphere |
| The Real-time Volumetric Cloudscapes of Horizon: Zero Dawn (Nubis) | Schneider & Vos | 2015 | https://www.guerrilla-games.com/read/nubis-authoring-real-time-volumetric-cloudscapes-with-the-decima-engine |
| Nubis, Evolved (temporal upscaling) | Andrew Schneider | 2022 | https://www.guerrilla-games.com/read/nubis-evolved |
| Real-time rendering of volumetric clouds (full shader reference) | Fredrik Häggström | 2018 | https://www.diva-portal.org/smash/get/diva2:1223894/FULLTEXT01.pdf |
| Simulating Ocean Water | Jerry Tessendorf | 2001/04 | https://jtessen.people.clemson.edu/reports/papers_files/coursenotes2004.pdf |
| Ocean Rendering (trochoidal + absorption) | Outerra / Kemen | 2011 | https://outerra.blogspot.com/2011/02/ocean-rendering.html |
| Real-time Rendering of Atmosphere and Clouds in Vulkan (architecture ref) | Matěj Sakmary | 2023 | https://cescg.org/wp-content/uploads/2023/04/Sakmary-Real-time-Rendering-of-Atmosphere-and-Clouds-in-Vulkan.pdf |

---

### 2.3 Stellar surface & close-star rendering

**Recommended stack**
1. **Photosphere — bake to an animated target (the central lever).** Domain-warped 3D FBM (4 octaves is the real-time sweet spot) for the brightness field + a Worley/cellular layer for granule cells + thresholded low-frequency layer for **starspots**, written into an **object-space cube-map** target (cube-map, not equirect — avoids seam/pole pinching) and animated by advancing the noise time/w-axis. This converts the dominant per-fragment noise from "scales with screen coverage" (catastrophic at close zoom) to "fixed texel cost, lazily updated." *Correction: at true hero-close a fixed 2K–4K map is bilinear mush, so you need a **hybrid — amortized baked low-frequency + 1–2 `fwidth`-clamped runtime detail octaves**, which reintroduces +1–2 ms of coverage-scaling cost the naive bake thesis hides.*
2. **Limb darkening.** `I(μ)/I(1) = 1 − u1(1−μ) − u2(1−μ)²`, `μ = dot(N,V)`, `u1,u2` from a small Teff-indexed table (Sing/Claret), per-channel for reddened cool-star limbs. <0.1 ms. *Note: at true hero-close on a photosphere patch μ≈1 everywhere, so this matters for the mid-field full-disk view, not the money shot.*
3. **Blackbody LUT.** Planck × CIE → linear working space, **≥16-bit / float** 1D texture keyed by Teff (8-bit bands visibly). **Separate chromaticity from a hand-tuned exposure curve** — radiance spans ~9 orders of magnitude, so a linear drive clips O/B stars to white and vanishes M dwarfs. Use a wider working space (P3+) or explicit gamut mapping — sRGB clips saturated blackbody extremes to negative components.
4. **Corona — a NEW additive volumetric raymarch pass.** *Correction: "rides the nebula raymarch budget you already pay" is sleight-of-hand — sharing code is not sharing cost.* It needs **ray-sphere intersection (inner+outer radii) + 1/r density**, a different integrator from the single-box nebula, and at hero-close it projects across the **entire framebuffer**: 24–40 steps × full coverage × multi-octave turbulent 3D noise is realistically **3–5 ms of new cost**. To fit, it **must** be re-engineered: screen-coverage-adaptive step count + blue-noise jittered start + reprojection targeting ≤2 ms, with a **billboard/particle-corona fallback at closest zoom**.
5. **Chromosphere rim + prominences/flares.** Fresnel rim add (`pow(1−dot(N,V),k)`, Hα-red). Prominences/coronal loops/flares are **event-gated sparse VFX** (curl-noise particle ribbons, additive) — 0 ms idle, ~0.5–1 ms active, scheduled off corona-heavy frames.
6. **LOD-aware granulation suppression + HDR bloom.** `fwidth`/mip octave clamp + distance/limb amplitude fade (the exact SpaceEngine "suppress granulation on upper LODs" trick). Per-star **exposure-relative bloom threshold** so M-dwarf and O-star both read through one pipeline.

**Why:** the bake decouples the dominant cost from zoom; limb-darkening + blackbody LUT + bloom reuse are the genuine near-free wins (not the corona).

**90 FPS budget reasoning (honest):** dossier's 5–7 ms steady state is optimistic by **~1.5–3 ms** once you add runtime detail octaves, honest full-coverage corona fill, double-buffer bandwidth, and TAAU resolve. Realistic close-zoom worst case (star+corona fill screen, no nebula): photosphere sample+detail 1.5–2.5 ms, corona 3–5 ms, bloom 1.5–2.5 ms, limb/rim/LUT 0.4 ms, resolve 0.5 ms = **7–11 ms of star alone**. Two structural problems: **(a) the reduced-cadence bake spikes 1.5–3 ms ON the frame timeline every 2nd–3rd frame** — Three.js WebGPURenderer gives no reliable async-compute overlap to hide it, and 90 FPS under vsync is a **worst-frame**, not average, problem (one 12 ms frame = judder even at 6 ms mean); **(b) VRAM/bandwidth is real** — a 4K RGBA16F equirect is 64 MB, double-buffered (needed for temporal blend to kill strobe) 128 MB; a 6×2K cube-map 384 MB / 768 MB — a hard constraint on per-tab-limited browser GPUs.

**Failure modes to avoid**
- Granulation shimmer/aliasing at the limb — LOD/`fwidth` suppression + fade; verify at native resolution.
- Cube-map vs equirect seam/pole — sample 3D noise in object space; prefer cube-map.
- Blackbody blowing out the tonemapper — separate chromaticity from exposure; bloom threshold relative to the star's own exposure. **ACES hue-shifts blue→purple / red→orange; AgX desaturates bright cores and can erase low-contrast granulation ΔT.** Choose deliberately (likely AgX or a custom curve) and verify the granulation signal survives.
- "Cartoon lava" over-contrast — derive granule/lane ΔT from real photometry (few-hundred K), low contrast, let HDR do the drama.
- Corona double-booking with a co-visible nebula — shared step budget with priority allocation; LOD corona steps down.
- Limb-darkening mismatch across spectral class — drive u1,u2 from Teff.
- Temporal strobing from reduced-cadence bake — temporally blend two bake frames (costs double-buffer bandwidth).
- **Missing: star-as-light-source** — a close hero star is the dominant illuminant for planets/ships/dust and its IBL probe must be re-rendered as the camera descends (sky radiance changes with sun angle/altitude); this recurring cost is uncounted.
- **Missing: faculae/plage** (bright magnetic network, prominent near the limb) — nearly free as another thresholded bake layer.
- **Missing: TAA interaction** — high-frequency granulation + reduced-cadence bake + additive HDR corona fight TAA history (ghosting on the surface, additive fireflies/disocclusion trails at close zoom); animate/reproject the noise field in a space where velocity **can** be computed.

**Cited sources**
| Title | Author | Year | URL |
|---|---|---|---|
| Procedural star rendering with three.js and WebGL shaders | Ben Podgursky | 2017 | https://bpodgursky.com/2017/02/01/procedural-star-rendering-with-three-js-and-webgl-shaders/ |
| Domain warping | Inigo Quilez | n.d. | https://iquilezles.org/articles/warp/ |
| Using cellular noise to generate procedural stars | Ryan Smith (Overdraw.xyz) | 2018 | https://www.overdraw.xyz/blog/2018/7/17/using-cellular-noise-to-generate-procedural-stars |
| Stellar limb-darkening coefficients for CoRoT and Kepler | D. K. Sing (A&A) | 2010 | https://www.aanda.org/articles/aa/full_html/2010/02/aa13675-09/aa13675-09.html |
| Blackbody Rendering | Miles Macklin | 2010 | https://blog.mmacklin.com/2010/12/29/blackbody-rendering/ |
| Starlight (granulation LOD suppression) | SpaceEngine / Romanyuk | 2017 | https://spaceengine.org/news/blog170420/ |
| Physically Based Sky, Atmosphere and Cloud Rendering in Frostbite | Sébastien Hillaire | 2016 | https://blog.selfshadow.com/publications/s2016-shading-course/ |
| three.js webgpu — bloom emissive example | three.js | 2024 | https://threejs.org/examples/webgpu_postprocessing_bloom_emissive.html |

---

### 2.4 Black hole & relativistic rendering

**Recommended stack**
1. **Hero technique — per-pixel null-geodesic raymarch (Schwarzschild).** Only per-pixel geodesic integration yields a correct **photon ring, Einstein ring, and horizon shadow** — the entire payoff of a close zoom. Every cheaper family (screen-space UV warp, billboard distortion) has no multi-image structure and reads as fake at close zoom, and is a **distant-LOD tier only**. Fix the orbital plane per ray; integrate `d²u/dφ² = (3/2)·r_s·u² − u` (`u=1/r`) with **adaptive stepping** (coarse far, dense near the photon sphere — mandatory, not an optimization; fixed-step RK4 either diverges or wastes uniform steps). Absorb horizon-crossing rays; sample the HDR starfield for escapees.
2. **Prefer the analytic elliptic-integral deflection path (the review's biggest addition).** The exact Schwarzschild deflection has a closed form in Jacobi elliptic / incomplete elliptic integrals of the first kind, with fast approximate-analytic forms (arXiv:1608.04574) that translate directly to high-speed ray tracing. It sits **between** live ODE and Bruneton tables: a few special-function evals per pixel, O(1)-ish, **no table asset, all camera distances** (unlike Bruneton's regime-locked tables), and **no per-lane step-count SIMT divergence** (unlike the ODE). This is arguably the best fit for free-fly zoom and should be the primary, not the live RK4.
3. **Accretion disk shading (composable on any integrator).** Optically-thin disk from ISCO (~3 r_s) outward, Shakura-Sunyaev `T ∝ r^(-3/4)` → blackbody LUT, **both** relativistic Doppler beaming (`I ∝ δ⁻³`) **and** gravitational redshift combined (`δ = γ_oγ_s(1−d_o·v_o)(1+d_s·v_s)`) — half of either reads uncanny. Beer's-law vertical density. Comparatively cheap; the geodesic march dominates.
4. **Ring anti-aliasing — beam/cone footprint, not just supersampling.** The concrete WebGPU form: **use the ray/beam footprint to select the HDR starfield env-map MIP level.** Lensing folds the sky, so a single texel fetch aliases catastrophically; footprint-driven mipped area sampling is the actual fix (DNGR ray-bundle lesson made practical) and is cheap.
5. **Bruneton precomputed-deflection tables — a parallel build, not a runtime flag.** Constant-time O(1) lookup, the most production-real-time result on record for **non-rotating** holes — but it is a separate shader with different static assets, a different AA/composite path, and locked to a camera-distance regime that conflicts with continuous free-fly zoom. If you want it as a fallback you build and maintain it in parallel from day one; you cannot hot-swap it when the ODE overruns. The analytic path (above) is a better distance-agnostic O(1) option.
6. **Kerr — gate hard behind a scripted quality tier.** *Correction: cost is ~**3–5×** Schwarzschild plus a symplectic/Yoshida integrator, not 1.7–2×* — Kerr geodesics are non-planar (must carry the Carter constant, integrate the full system, handle Boyer-Lindquist horizon singularities). The reduced-planar-ODE intuition that makes Schwarzschild cheap does not transfer. Half-implemented spin reads as a bug.

**Why:** the close-zoom features that justify the pillar (photon/Einstein ring, shadow, multi-image) are exactly the ones only geodesic integration produces.

**90 FPS budget reasoning (honest):** the two budget-closing levers the dossier leaned on **specifically destroy the ring**. **(1) Temporal accumulation is broken at the photon ring** — lensed pixels have no single well-defined prior-frame world position (a bent ray wraps/folds), so motion vectors are undefined/many-to-one exactly where you need them; jittered accumulation works for a **locked camera** and smears/ghosts the ring under any camera motion. **(2) Half-res + bilinear upscale aliases the ring, ISCO edge, and thin Einstein arcs** — the highest-frequency, sub-pixel content in the frame, not the low-frequency bulk. **(3) SIMT divergence** — "reserve 300×8 steps only for the annulus" saves work only when expensive pixels are **coherently grouped**; the fix is explicit **tile/bin classification + separate dispatch** (ring annulus at full/super-res, sky at quarter-res), not per-lane early-out (WebGPU has no hardware VRS, so this is hand-built). **(4) WGSL has no fp64** (gpuweb #2805 still a proposal) — the `u=1/r` formulation and `(3/2)r_s u²` term have large dynamic range and catastrophic cancellation near the photon sphere; FP32-only integration is a real precision risk for a body defined by a razor-thin critical curve. **(5) Only the skybox is lensed** — scene geometry composited after the pass cannot be bent by the metric, so a ship on the far side won't lens around the shadow; correct foreground lensing needs marching that geometry (SDF/ray-traced) through the metric, a large additional cost.

**Verdict:** achievable as a **scripted, slow-/static-camera hero moment at ~60 FPS frame-time on a discrete GPU** (RTX 3060-class+ / M3 Pro+); **not** a free-fly, any-camera, any-hardware 90 FPS default. There is **zero interactive-game shipping precedent** — per-pixel geodesic lensing exists only in tech demos (Nguyen, oseiskar) and offline film (DNGR). Treat as an open research risk, not a solved budget line.

**Failure modes to avoid**
- Photon-ring aliasing/flicker — footprint MIP selection + annulus supersample + (locked-camera-only) temporal accumulation.
- Integrator instability near the horizon — adaptive stepping; symplectic for Kerr.
- Screen-space lensing for the hero shot — distant-LOD only; **plan the LOD transition band** (screen-warp → analytic → full geodesic) or you relocate the artifact to a visible pop.
- Disk banding / blown highlights — feed HDR pre-tonemap; verify the δ⁻³ beaming asymmetry survives (AgX desaturation can flatten the signature blue-shifted leading edge).
- Redshift/beaming half-implemented — both terms, always.
- Depth/compositing — decide order explicitly; output a plausible depth for disk/horizon.
- **Camera aberration** — at ISCO-orbital speeds, relativistic aberration + beaming of the whole field must compose with the static lensing solution.
- No GRRT correctness reference — validate against ipole/RAPTOR/EHT imagery at matching parameters, not just "looks like Interstellar."

**Cited sources**
| Title | Author | Year | URL |
|---|---|---|---|
| Black Hole — WebGPU Raymarcher | Martin Nguyen | 2026 | https://martinnguyen.me/projects/blackhole/ |
| Physics of a black-hole visualization | Otto Seiskari (oseiskar) | 2015 | https://oseiskar.github.io/black-hole/docs/physics.html |
| Starless / Raytracing a black hole | Riccardo Antonelli (rantonels) | 2015 | https://rantonels.github.io/starless/ |
| Approximate analytical calculations of photon geodesics in Schwarzschild | (arXiv:1608.04574) | 2016 | https://arxiv.org/abs/1608.04574 |
| Real-time High-Quality Rendering of Non-Rotating Black Holes | Eric Bruneton | 2020 | https://arxiv.org/abs/2010.08735 · https://ebruneton.github.io/black_hole_shader/ |
| Gravitational Lensing by Spinning Black Holes (Interstellar / DNGR) | James, von Tunzelmann, Franklin, Thorne | 2015 | https://arxiv.org/abs/1502.03808 |

---

### 2.5 Performance: WebGPU 90 FPS, temporal upsampling, precision

**Recommended stack**
1. **Reversed-Z + `depth32float`** — the correct near-free default. Keep.
2. **Floating origin** — keep; **the pillar's real insight: treat an origin-shift frame as a hard, full-frame temporal-history invalidation *and* a Hi-Z stale-depth skip.** This is the single most important correctness detail in the precision layer.
3. **GPU-driven frustum culling + compaction + `drawIndexedIndirect`** — fully core WebGPU, maps 1:1 from Vulkan. *But correctly deprioritized:* near-free at close zoom on one body (few instances) — it matters for the **fly-in**, not the hero close-up. Hi-Z occlusion (hand-rolled min-reduction pyramid; WebGPU has no `SAMPLER_REDUCTION_MODE_MIN`) adds value when a hero body occludes a field; **skip Hi-Z the frame after an origin shift** (stale depth).
4. **TAAU — a co-development bet, not a keystone adoption.** Three.js `TAAUNode` (WebGPU/TSL, issue #33359, since April 2026) exists but upstream itself flags its basic multi-tap resolve as **not yet production-sharp** (TAA blur/flicker amplified by upsampling; MSAA must be off). Legion would be **co-developing** it. And it needs a **valid per-pixel velocity buffer for everything it reprojects** — three of four hero bodies are dominated by motion-vector-**less** content (photosphere granulation animating in shader-time, volumetrics, particles, lensed backgrounds), where a reactive mask falls back to current-frame-only and you **pay full-resolution shading exactly where you needed the upscale**. The "render at 44 % pixels" thesis evaporates over most of a star or black hole.
5. **FSR2-style reactive + disocclusion masks — the hard 70 % of FSR2, a multi-month fork, not a graft.** Source the reactive mask (raise current-frame weight on alpha/particle content) and disocclusion mask (depth/MV divergence) — but this is built on an immature TAAUNode, so budget it as real subsystem work.
6. **Dynamic resolution scaling (DRS)** — app-level (no WebGPU DRS API): rolling GPU-frame-time (`timestamp-query` + CPU fallback) drives internal color/depth/velocity scale between ~1.5×/axis (Quality, ~44 % pixels) and ~2.0×/axis (~25 %), with **hysteresis + rate-limiting** to avoid hunting. Pre-allocate at max size, render to a sub-rect to avoid allocation churn. First and cheapest response to overrun.
7. **`shader-f16`** (shipped Chrome 120+) — for noise-heavy procedural shading (terrain FBM, granulation) f16 is a major fill/ALU/bandwidth lever; feature-detect (Qualcomm caveat gpuweb #5006).
8. **df64 double-single — last-resort, surgically scoped, with a correctness hazard.** Apply only to camera-relative translation and terrain-vertex / texture-UV math at extreme zoom. *Correction: it is **not** "pure arithmetic, no special features" — double-single depends on the compiler NOT reassociating or FMA-contracting the (hi+lo) error-compensation terms; WGSL does not guarantee strict IEEE-754 non-association, and Tint lowering to HLSL/MSL/SPIR-V can apply fast-math that silently annihilates the low word, degrading df64 back to f32 with no warning on some backends. Requires per-backend numerical validation.*
9. **`timestamp-query` profiling + overdraw budgeting** — the instrument that makes DRS/budget real; front-to-back order + Beer-Lambert early-exit protect volumetrics.

**Do NOT plan on:** mesh shaders, hardware VRS, hardware sparse textures (emulate virtual texturing with a page-table indirection texture), guaranteed multi-draw-indirect (Chrome 131 experimental behind `enable-unsafe-webgpu` — feature-detect, fall back to one indirect draw per batch), ML upscalers (no in-browser access).

**90 FPS budget reasoning (honest):** **you do not get 11.1 ms in-browser** — compositor deadline + rAF jitter + GC + queue-submit overhead leave **~8–9 ms of real GPU budget**; 90 Hz needs a 90 Hz+ panel (on 60 Hz laptop panels rAF caps at 60 and the target is moot); "sustain" implicates thermal throttling on mobile/laptop within minutes. Bottleneck differs by body: the **planet is geometry/compute-bound (terrain generation), not fill-bound** — TAAU reduces fragment work only and barely moves terrain time, so the fill-bound budget model only holds for the photosphere. The blended-volumetric budget line is architecturally inconsistent: volumetrics write no usable depth/velocity and **cannot ride the beauty-pass TAAU** — they need their **own** temporal history and composite after resolve (separate histories for beauty / volumetrics / geodesics).

**Failure modes to avoid** (all confirmed): TAAU ghosting on MV-less content; disocclusion shimmer at the horizon (transient quality event, not budget event); origin-shift history corruption; log-depth-per-fragment early-Z loss (unrecoverable in-browser — no conservative-depth); depth-fighting at scale without tight origin/df64; assuming multi-draw-indirect / timestamp-query available; render bundles used while GPU-bound (they only cut CPU encoding); DRS oscillation; raymarch overdraw at close zoom; VT streaming stalls (`copyBufferToTexture`); Hi-Z one-frame-latency pops.

**Cited sources**
| Title | Author | Year | URL |
|---|---|---|---|
| Depth Precision Visualized (reversed-Z + float32) | Nathan Reed | 2015 | https://www.reedbeta.com/blog/depth-precision-visualized/ |
| Maximizing Depth Buffer Range and Precision (log depth) | Brano Kemen (Outerra) | 2012 | https://outerra.blogspot.com/2012/11/maximizing-depth-buffer-range-and.html |
| Emulating Double Precision on the GPU (floating origin, df64) | Godot / Verschelde et al. | 2022 | https://godotengine.org/article/emulating-double-precision-gpu-render-large-worlds/ |
| GPU Driven Rendering: Compute-based Culling (frustum + Hi-Z) | vkguide.dev | ongoing | https://vkguide.dev/docs/gpudriven/compute_culling/ |
| Optimizing the Graphics Pipeline with Compute | Graham Wihlidal (EA) | 2016 | https://www.slideshare.net/gwihlidal/optimizing-the-graphics-pipeline-with-compute-gdc-2016 |
| TAAUNode (issue #33359) + webgpu_upscaling_taau example | three.js contributors | 2026 | https://github.com/mrdoob/three.js/issues/33359 · https://threejs.org/examples/webgpu_upscaling_taau.html |
| FidelityFX Super Resolution 2 (reactive/disocclusion masks) | AMD GPUOpen | 2022–23 | https://gpuopen.com/manuals/fidelityfx_sdk/techniques/super-resolution-temporal/ |
| WebGPU Render Bundle best practices | Brandon Jones (toji) | ongoing | https://toji.dev/webgpu-best-practices/render-bundles.html |
| How to use WebGPU timestamp query | Omar Shehata | 2023 | https://omar-shehata.medium.com/how-to-use-webgpu-timestamp-query-9bf81fb5344a |
| Adaptive Virtual Texturing (software VT) | Graphine / id Tech 5 lineage | 2016 | https://gpuopen.com/gdc-presentations/2016/AdaptiveVirtualTexturing.pdf |

---

## 3. Unified 90 FPS frame-budget table

**Frame wall = 11.1 ms nominal; plan against ~8–9 ms real in-browser GPU budget after ~1.5–2 ms compositor/rAF/GC/submit overhead.** Allocations below are for a **mid-to-high discrete desktop GPU at close zoom on a single hero body**, internal render ~1.5×/axis (~44 % pixels) with TAAU resolve to native. On integrated GPUs, DRS drops toward 25 % pixels and the honest target is 60 FPS. All figures are **planning estimates pending `timestamp-query` measurement on target hardware** — the dossiers honestly flag these as notional.

| Pass | Planet surface | Star photosphere | Black hole | Notes |
|---|---|---|---|---|
| GPU-driven cull + Hi-Z build | 0.3–0.6 | ~0.1 (few instances) | ~0.1 | Scales with instances, near-free at close zoom on one body |
| Precision reconcile (float64 origin / df64) | ~0.1 CPU | ~0.05 | ~0.05 | Cost is correctness plumbing on shift frames |
| Depth pre-pass / hero geometry (reversed-Z) | 1.0–1.5 | — (sphere only) | — (screen-space pass) | Early-Z intact except log-depth near shells |
| **Primary surface / body pass** | Terrain shade + triplanar **@internal res**, height/normal **prefetched from patch bake** 3.5–5.0 | Photosphere sample (baked) + hybrid runtime detail octaves 1.5–2.5 | **Geodesic march** (analytic-deflection preferred) 4–6, tile-classified (ring annulus super-res) | The dominant line item; planet is compute-bound not fill-bound |
| Async bake (amortized, off critical path) | patch height/normal + erosion, **throttled** | granulation bake **spikes 1.5–3 ms every 2nd–3rd frame ON timeline** (no reliable async overlap) | — | Bake variance is a worst-frame hazard, not an average |
| Atmosphere: Hillaire LUTs (transmittance+multiscatter cached; sky-view+aerial per-frame) | 0.5–1.5 | — | — | Aerial-perspective froxel hazes distant terrain for free |
| Volumetrics (clouds / corona / disk) **own temporal history** | clouds @half-res + depth-aware upsample 1.5–2.5 | **corona = NEW full-coverage pass 3–5** (re-engineer to ≤2) | disk shading (cheap, rides geodesic) 0.5–1.0 | Cannot ride beauty-pass TAAU; separate history + composite after resolve |
| Shadows | CSM + terminator long-shadow / self-shadow **under-specified, budget explicitly** 1.0–1.5 | — | — | Do not fold into a single sub-2 ms line at planet scale |
| TAAU resolve (→ native, fixed in output px) | 0.8–1.5 | 0.8–1.5 | **locked-camera only; broken at ring under motion** | Ring/ISCO/arcs are sub-pixel — half-res upscale aliases them |
| Post: ACES/AgX tonemap + bloom | 0.8–1.2 | 1.5–2.5 (more above-threshold area) | 1.0–1.5 (pre-tonemap HDR for beaming) | AgX desaturation can flatten granulation/beaming signal |
| **Realistic close-zoom total (star+scene)** | **~9–13 ms naive → fits after bake + LUT + LOD levers** | **~7–11 ms of star alone** | **geodesic + disk dominate; temporal levers unavailable** | Leaves little-to-negative headroom; DRS is the release valve |

**Levers when over budget, in order:** (1) DRS drops internal scale toward 25 %; (2) drop volumetric/raymarch to quarter-res + bilateral upsample; (3) reduce octaves-per-LOD / corona step count / geodesic step cap; (4) tighten screen-space error threshold; (5) skip Hi-Z on post-origin-shift frames. **Amortized work (bakes) must never enter the critical path; throttle the queue so a fast descent can't stampede it.**

---

## 4. Precision & scale strategy

Legion already has the correct spine: **floating origin + logarithmic depth (per-vertex) + reversed-Z on `depth32float`.** Terrain ties in as follows, without reintroducing jitter or z-fighting:

1. **Per-patch local origin is the terrain-side extension of floating origin.** Express each patch's vertices relative to a patch-center (or camera-anchored) local origin; do all sphere-displacement math in that **float32 local frame**; reconcile to planet space with a **float64 subtraction in JS** and pass only the small relative offset to the shader. float32 ULP at Earth radius is ~0.76 m — this is the fix for the #1 close-zoom failure (vertex swim). **Empirically test patch-center vs camera-anchored origin placement** to minimize float32 error across a full patch at the deepest LOD.
2. **Sample synthesis noise in a stable planet-fixed frame, never camera-relative** — otherwise the terrain crawls as the camera moves even with correct origins.
3. **df64 only where re-origining still quantizes** — terrain-vertex generation and texture-UV math at extreme zoom. Scope surgically (several ops per operation) and **validate numerically per backend** (Tint fast-math/FMA-contraction can silently collapse df64 to f32). Do not blanket the pipeline.
4. **Depth without new z-fighting:** reversed-Z + float32 already gives near-uniform precision; keep log-depth **per-vertex globally** and **per-fragment only on the hero body's near shells** where interpolation error shows cracks — accepting that per-fragment `frag_depth` writes disable early-Z with **no in-browser conservative-depth recovery**. For the full 9-decade galactic→surface range, evaluate **depth-range cascades / multi-frustum splitting** as the honest modern complement (the dossier's stacked log+reversed-Z is partly redundant). **Validate the existing depth setup at surface scale**, not just orbital scale, so terrain doesn't z-fight itself or the atmosphere shell.
5. **Origin-shift frames are temporal events:** on re-center, **invalidate the full TAAU history** (reprojection maps to wrong world positions otherwise) and **skip Hi-Z** (stale prior depth). Tune the shift threshold to minimize invalidation frames while keeping FP32 coordinates small — ideally hide the invalidation behind existing motion.
6. **Depth-precision vs early-Z is a perf issue, not just correctness:** log-depth-per-fragment defeats early-Z / Hi-Z in the overdraw-heavy close-zoom case — restrict it, and lean on horizon culling to keep overdraw down.

---

## 5. Skill blueprint — four new workspace spokes

All four are **spokes** hanging off `legion-project` and the existing hubs. They must teach the **honest, review-survived** verdicts, not the optimistic dossier framing. Each carries a Proofboard obligation (framework #06): every technique ships with a native-resolution proof and a `timestamp-query` measurement, not an averaged estimate.

### (a) `planetary-terrain-lod`
- **Scope:** seamless cube-sphere terrain from orbit to near-surface — quadtree/CDLOD structure, bake-on-subdivision procedural height/normal, triplanar shading, horizon culling, per-patch precision. Owns the planet hero body's geometry and surface detail.
- **Domain boundary:** builds *on* `game-scale-traversal` (floating origin / log-Z / reversed-Z spine — that skill owns the spine; this one owns the terrain-side per-patch-origin extension). Uses `webgpu-advanced-rendering` for compute+indirect mechanics but owns the terrain-specific quadtree/CDLOD. Hands atmosphere/ocean/cloud off to skill (b). Consumes noise primitives that `glsl-shader-architect` teaches but owns their band-limited-per-LOD terrain application. **Not** volumetrics (that's vfx-volumetrics / skill b).
- **Key techniques it must teach:** cube-sphere + Cobb/tangent-adjusted warp; restricted quadtree (±1); CDLOD per-vertex morph (the exact `morphVertex` math) + short-skirt backup; **bake height+normal on subdivision** (the corrected architecture — lead with this, not inline synthesis); ridged-multifractal + domain-warp fBm with analytic derivatives; band-limiting octaves per LOD; triplanar slope/altitude/latitude material blend; horizon cull with maxZ inflation; per-patch local origin + float64 reconcile + planet-fixed noise sampling; async throttled erosion bakes; explicit exclusion of tessellation/mesh shaders; f16 noise / subgroup reductions.
- **Prerequisites:** `game-scale-traversal`, `webgpu-advanced-rendering`, `glsl-shader-architect`.

### (b) `atmospheric-scattering-and-clouds`
- **Scope:** Hillaire LUT atmosphere, bespoke WGSL volumetric clouds with temporal reconstruction, FFT+Gerstner oceans, night side. Owns everything gaseous/liquid layered on a planet.
- **Domain boundary:** the **planet-facing** counterpart to skill (c)'s stellar volumetrics — this one owns breathable-atmosphere scattering, cloud decks, and water. Deepens/supersedes `threejs-vfx-atmosphere` and `vfx-volumetrics` for the planet case (those cover generic/nebula volumetrics; this owns the physically-based sky + cloud + ocean pipeline and its WebGPU-specific gaps). Consumes the aerial-perspective froxel that composites terrain (skill a) into atmosphere. **Not** stellar corona/photosphere (skill c).
- **Key techniques it must teach:** the four Hillaire LUTs + caching split (constant vs per-frame) + exact horizon parameterization; **clouds as fully bespoke WGSL** (takram is GLSL-only — say so explicitly); Perlin-Worley base + Worley erosion + weather map + dual-lobe HG + Beer/powder; **hand-rolled temporal reprojection subsystem** (motion vectors, variance clip, neighborhood clamp) as a first-class build; **depth-aware bilateral upsample** of half-res clouds; **through-cloud transition + per-cloud advection motion vectors**; **cloud shadows on terrain/ocean**; Tessendorf FFT butterfly compute + Gerstner blend + **the unsolved spherical-ocean tiling problem** (flag as open, require a projection scheme before ship); per-body LOD + shared-LUT VRAM discipline; log-depth froxel slice distribution reconciled with reversed-Z; the honest integrated-GPU bandwidth verdict + DRS ladder.
- **Prerequisites:** `webgpu-advanced-rendering`, `glsl-shader-architect`, `vfx-volumetrics`; benefits from `planetary-terrain-lod` (composites against it).

### (c) `stellar-and-relativistic-hero-bodies`
- **Scope:** the two exotic hero bodies — star photosphere/corona and black hole/relativistic lensing. Grouped because both are single-body, physically-driven, procedurally-shaded, and both live or die on temporal/coverage strategy.
- **Domain boundary:** owns the **astrophysical rendering** of stars and black holes. Pulls physical parameters (Teff, spectral class, ISCO, metric) from `sci-astro-objects` (that skill owns the astrophysics/data; this owns the *rendering*). Reuses `vfx-volumetrics` machinery for corona but owns the **new** ray-sphere corona integrator and the geodesic raymarcher. Shares the blackbody LUT + bloom coupling with `glsl-shader-architect`. **Not** planetary atmosphere (skill b).
- **Key techniques it must teach — stellar:** granulation **baked to an animated object-space cube-map** + **hybrid runtime detail octaves at hero-close** (correct the naive bake thesis); physical limb darkening from a Teff table; **blackbody LUT with chromaticity separated from exposure**, ≥16-bit, wide gamut; **corona as a genuinely new full-coverage additive raymarch pass** (ray-sphere + 1/r), re-engineered to ≤2 ms with screen-coverage-adaptive steps + blue-noise + billboard fallback; **bake-spike frame-variance** as a worst-frame hazard; faculae; star-as-light-source + descending IBL re-render; ACES-hue / AgX-desaturation tonemap tradeoff; event-gated prominences/flares. **Relativistic:** per-pixel Schwarzschild geodesic, **prefer analytic elliptic-integral deflection**; adaptive stepping; Doppler beaming + gravitational redshift together; **footprint-driven env-map MIP** for ring AA; **tile-classified variable-resolution** (ring annulus super-res); the **broken-temporal-reprojection-at-the-photon-ring** reality; **no-fp64 precision risk**; skybox-only-lensing limit; Kerr as a **3–5× scripted tier**; the honest "scripted slow-camera hero moment, not free-fly default" verdict.
- **Prerequisites:** `sci-astro-objects`, `webgpu-advanced-rendering`, `glsl-shader-architect`, `vfx-volumetrics`.

### (d) `realtime-render-performance-90fps`
- **Scope:** the cross-cutting performance/precision/temporal discipline that all three body skills depend on — the frame-budget spine. Owns TAAU/DRS, GPU-driven culling, depth precision, df64, profiling, and the WebGPU capability map.
- **Domain boundary:** the **foundation** skill the other three sit on; it owns *how to hold the frame*, they own *what to render*. Overlaps `webgpu-advanced-rendering` but is narrower and Legion-specific: this one owns the **90 FPS budget methodology, temporal-upsampling reality, and precision spine**, while webgpu-advanced-rendering owns general API mechanics. Extends `game-scale-traversal`'s precision spine with the temporal/DRS interaction (origin-shift-as-history-invalidation).
- **Key techniques it must teach:** reversed-Z + `depth32float`; floating origin with **origin-shift = full history invalidation + Hi-Z skip**; GPU frustum cull + compaction + `drawIndexedIndirect` (deprioritized at close zoom); hand-rolled Hi-Z min-reduction; **TAAU as a co-development bet** (immature TAAUNode, MV-less-content failure) + FSR2 reactive/disocclusion masks as a real fork; **separate temporal histories for beauty / volumetrics / geodesics**; app-level DRS with hysteresis; **`shader-f16`** for procedural shading; **df64 with the compiler-reassociation hazard + per-backend validation**; log-depth-per-fragment early-Z loss (no in-browser conservative-depth) + depth cascades; `timestamp-query` profiling + CPU fallback; the **~8–9 ms real in-browser budget**, 90 Hz-panel / thermal-throttle reality; the dead-path exclusion list (mesh shaders, VRS, sparse textures, guaranteed MDI, ML upscalers).
- **Prerequisites:** `webgpu-advanced-rendering`, `game-scale-traversal`.

**Skill graph:** `(d) realtime-render-performance-90fps` is foundation for `(a)`, `(b)`, `(c)`. `(a)` and `(b)` compose (terrain ↔ atmosphere/ocean). `(c)` stands alongside them as the exotic-body branch. All four load-chain up through `legion-project` → `lead-game-developer`.

---

## Appendix — claims that did NOT survive review (do not author into skills as fact)
- CDLOD's 1198 FPS / 446k-tri figure as evidence for **procedural** synthesis cost — it's prebaked-fetch performance, different cost class.
- Corona "rides the raymarch budget you already pay for free" — it's a new full-coverage integration pass (3–5 ms).
- takram as a **cloud** drop-in for WebGPU — GLSL-only, no WebGPU/TSL; clouds are fully bespoke.
- TAAUNode as a mature drop-in keystone — upstream-flagged immature; co-development bet.
- Temporal accumulation as a safe universal budget lever — broken at the photon ring and on all motion-vector-less content.
- Kerr at ~1.7–2× Schwarzschild — realistically 3–5× + symplectic integrator.
- df64 as "pure arithmetic, no special features" — compiler-reassociation hazard, needs per-backend validation.
- The 11.1 ms budget as fully renderer-available — ~8–9 ms real in-browser; 90 FPS needs a 90 Hz+ panel.
- Atmosphere as a 2–4 ms "residual" behind terrain — it should claim the frame first and be measured, not left over.
