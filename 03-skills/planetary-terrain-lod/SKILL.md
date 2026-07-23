---
name: planetary-terrain-lod
description: >
  Seamless cube-sphere planetary terrain from orbit to near-surface at SpaceEngine fidelity, holding
  90 FPS — quadtree/CDLOD structure, height+normal BAKED per-patch on subdivision (the corrected
  architecture, not inline synthesis), analytic-derivative procedural noise, triplanar shading,
  planet-horizon culling, and per-patch local-origin precision. Owns the planet hero body's geometry
  and surface detail. Triggers: planetary terrain, cube-sphere, quadtree LOD, CDLOD, chunked LOD,
  geometry clipmaps, terrain LOD, heightfield, procedural planet surface, triplanar, horizon culling.
aliases: [planetary-terrain-lod]
triggers: [planetary terrain, planet surface, cube-sphere, cube sphere, quadtree lod, cdlod, chunked lod, geometry clipmaps, terrain lod, heightfield, displacement, procedural planet, triplanar, horizon culling, ridged multifractal, terrain morph]
tier: spoke
hub: lead-game-developer
domain: game
prerequisites: [realtime-render-performance-90fps]
related: [glsl-shader-architect, game-scale-traversal, atmospheric-scattering-and-clouds]
surfaces: ["*"]
spec_version: "2.0"
---

# Planetary Terrain LOD — cube-sphere surface, orbit → near-surface

Seamless planet terrain at SpaceEngine fidelity, holding 90 FPS at hero-close zoom. Owns the planet's
geometry and surface detail; sits on the frame-budget spine ([[realtime-render-performance-90fps]]) and
extends the floating-origin precision spine of [[game-scale-traversal]] to the terrain patch.

## Scope and Domain Boundary
- **This skill:** cube-sphere quadtree, CDLOD, bake-on-subdivision height/normal, procedural terrain
  noise + triplanar shading, horizon culling, per-patch precision.
- → Floating origin / log-Z / reversed-Z *spine*: [[game-scale-traversal]] owns it; this owns the
  **terrain-side per-patch-origin extension**.
- → Frame budget, TAAU, DRS, df64 hazard: [[realtime-render-performance-90fps]].
- → Atmosphere shell, cloud deck, ocean composited onto the terrain: [[atmospheric-scattering-and-clouds]].
- → Noise math *primitives*: [[glsl-shader-architect]]; this owns their **band-limited-per-LOD terrain
  application**. **Not** volumetrics.

## The geometry is the solved part — fidelity lives in noise + shading
Raw polygon count is not the cost; the frame is dominated by **procedural ALU** (noise synthesis) and
**shading**. Both have clean quality dials: octave count, screen-space error threshold, CDLOD grid-resolution
multiplier. Design around amortizing the noise, not multiplying triangles.

## Structure — cube-sphere quadtree
Six cube faces, each a **restricted quadtree** (±1 neighbor level), patches = a shared static grid
(33×33 or 65×65) instanced per node; subdivide by screen-space edge error. Use an **area-equalizing warp
(tangent-adjusted / Cobb), not raw cube normalization**, or corner cells distort badly.

## LOD transition — CDLOD per-vertex morph
LOD is a function of **true 3D distance** (correct at any observer height). Odd-index vertices morph to
their even-index coarse neighbor across the last **15–30 %** of each range → adjacent edges become
bit-identical before the swap. This kills popping **and** T-junction cracks in one mechanism, pure
vertex-shader math (trivial in TSL/WGSL). Add **short skirts only if QA still shows hairline seams** —
long skirts flap at grazing angles.

## Geometry generation — BAKE, do not synthesize inline (the key correction)
This is the single most important architectural point, and the one naive planet tutorials get wrong.
**Height + analytic normal are baked into a per-patch texture on subdivision (async compute)**, so the
per-frame vertex cost collapses to a texture fetch — *this* is the actual reason CDLOD is cheap. Inline
per-frame synthesis of 12–16 octaves of domain-warped ridged fBm over ~1 M+ visible verts blows the budget
at close zoom. **Do not read CDLOD's 1198 FPS / 446k-tri figure as evidence for procedural cost — that is
prebaked-fetch performance, a different cost class.**

At true hero-close a fixed baked patch cannot hold sub-pixel detail, so use a **hybrid: amortized baked
low-frequency field + 1–2 `fwidth`-clamped runtime detail octaves** — and **budget the +1–2 ms** those
runtime octaves reintroduce (they scale with screen coverage; the naive bake thesis hides this).

## Height + shading
- **Ridged multifractal + domain-warped fBm with analytic derivatives** (IQ "morenoise") — normals come
  from the gradient for free, avoiding ~5 finite-difference evals *and* cross-boundary normal seams.
- **Band-limit octaves per LOD** (4–6 far, 12–16 near) so each patch only synthesizes frequencies its grid
  can represent. Band-limiting alone does **not** fix specular/material-boundary shimmer — you still need
  TAA (see [[realtime-render-performance-90fps]]).
- **Triplanar procedural material blend** driven by slope / altitude / latitude — no polar-UV singularity.
- Exploit **`shader-f16`** for noise accumulation and **subgroups** for reductions (both shipped 2026;
  feature-detect).

## Precision — per-patch local origin (terrain-side floating origin)
Do sphere-displacement math in a **patch-local float32 frame**; reconcile to planet space with a **float64
subtraction in JS** and pass only the small relative offset to the shader. **Sample synthesis noise in a
stable planet-fixed frame, never camera-relative** — or the terrain crawls as the camera moves. float32 ULP
at Earth radius (~6.37 M m) is ~0.76 m — sub-meter vertex "swim" is guaranteed without this. Table stakes,
and the #1 close-zoom failure. Empirically test patch-center vs camera-anchored origin placement.

## Culling — frustum + planet-horizon
Reuse the CDLOD min/max quadtree; **inflate the horizon angle by each node's stored maxZ** so mountaintops
aren't culled. Removes the entire far hemisphere at surface — the difference between a few hundred and many
thousand candidate patches, and the main lever keeping overdraw (and per-fragment log-depth cost) down.

## Phasing
- **v1:** CPU quadtree traversal + GPU CDLOD morph + **baked-on-subdivision** height/normal + triplanar.
- **v2:** migrate traversal to GPU-driven compute-quadtree + indirect draw **only after profiling shows
  draw calls / CPU in the budget** (unlikely at close zoom on one body).
- **v3:** async hydraulic-erosion bakes (Mei et al.) on near-surface patches, **throttled** (N bakes/frame,
  prefetch along descent) to avoid a bake stampede; software virtual texturing only if real albedo/DEM is
  ever mixed in.

## Legion reconcile note
Legion already ships a quadtree planet renderer (`src/render/planet/`) with a **baked height atlas** plus a
continuous **analytic `plateMacro`** height. The hard-won lesson there is the direct application of the
"seams amplify thresholds" failure mode below: the **hexagonal-artifact fix decoupled biome color from the
baked atlas** — climate temp/moisture now sample the smooth macro height, because tiny baked-seam steps at
quadtree leaf boundaries were crossing the narrow ±0.08 treeline smoothstep. Keep baked relief for geometry
/ normals / displacement; use continuous analytic height for anything threshold-sensitive (climate, biome
color). See knowledge: `08-knowledge/game-dev/legion-planet-surface-rendering.md`.

## Failure modes to avoid
- **Vertex jitter / "swimming"** (float32 at planet radius) — per-patch local origin + float64 reconcile +
  planet-fixed noise. #1 close-zoom failure.
- **LOD popping** — CDLOD morph across the last 15–30 %.
- **Cracks / T-junctions** — restricted quadtree + morph + short-skirt backup.
- **Normal/shading seams** — analytic-derivative normals from the same noise; blend the normal in the morph
  region, not just position.
- **Threshold flips at leaf seams** (the Legion hex artifact) — never drive a narrow smoothstep (treeline,
  snowline, biome boundary) off discontinuous baked-atlas height; use continuous analytic height.
- **Noise shimmer** — band-limit per LOD, then TAA for the residual.
- **Horizon-cull pop** — inflate by maxZ.
- **Erosion-bake hitch** — throttle the queue; a fast descent must not stampede it.
- **Shadow-map LOD mismatch** — frustum-cull on the shadow camera but **LOD-select on the main camera**.
- **Log-depth per-fragment defeats early-Z / Hi-Z** at the overdraw-heavy close-zoom case — restrict to
  near shells.

## Cited sources
- Strugar, *Continuous Distance-Dependent LOD (CDLOD)* (2010) — https://aggrobird.com/files/cdlod_latest.pdf · impl https://github.com/fstrugar/CDLOD
- d'Oliveira & Apolinário, *Procedural Planetary Multi-resolution Terrain Generation for Games* (2018) — https://arxiv.org/pdf/1803.04612
- Quílez, *Analytic Derivatives of Noise (morenoise)* — https://iquilezles.org/articles/morenoise/ · *fBm / domain warping* https://iquilezles.org/articles/fbm/ · https://iquilezles.org/articles/warp/
- Mei, Decaudin, Hu, *Fast Hydraulic Erosion Simulation on GPU* (2007) — http://www-evasion.imag.fr/Publications/2007/MDH07/FastErosion_PG07.pdf
- Cozzi & Ring, *3D Engine Design for Virtual Globes* (floating origin, horizon cull, 2011) — https://www.virtualglobebook.com/

## Related
- hub → [[lead-game-developer]]
- peer ↔ [[game-scale-traversal]] · [[glsl-shader-architect]] · [[atmospheric-scattering-and-clouds]]
