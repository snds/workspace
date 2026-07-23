---
tags: [game-dev, legion, planetary-terrain, shaders, biomes, glsl, webgpu, gotcha, hard-won]
created: 2026-07-22
updated: 2026-07-22
status: stable
confidence: high
sources:
  - "Legion session memory 2026-07-19 → 2026-07-23 (biome/hex-artifact/snow/storm work in src/render/planet/)"
  - "observations S467/S469/S470/S471, 5745–5759"
related_skills: [planetary-terrain-lod, atmospheric-scattering-and-clouds, glsl-shader-architect, game-scale-traversal]
related_projects: [13-legion]
---

# Legion Planet-Surface Rendering — hard-won patterns

The Legion-specific companion to [[planetary-terrain-lod]]. Legion already ships a working quadtree planet
renderer (`src/render/planet/shaders.ts` + `glsl.ts`); this entry records the traps that were actually hit
tuning its surface, so they aren't relearned. The *general* technique lives in the skill; the *Legion truths*
live here.

## Architecture in one breath
- **Dual-height terrain.** A **baked height atlas** (`hh`, per-texel) drives relief, normals, and
  displacement. A separate **continuous analytic macro height** (`plateMacro`, direction-based) drives
  anything threshold-sensitive. The two are normalized the same way so baked and analytic agree.
- **Whittaker biomes.** Land color = `mix(albedo, biomeColor(temp, moisture), cover * uLushDepth)`, where
  `temp` includes an **altitude lapse-rate** term (`temp -= uLapseRate * height`) and `cover` is a treeline
  smoothstep modulated by moisture.
- **Polar ice / snow.** Latitude-based `snowCover(seaT, uLatitudeIce)` with fBm (freq ~8) for a "floe and
  lead" texture (not a solid disc); ice reduces specular by `(1 - pack)` to read as matte vs glossy water.
- **Clouds / storms.** A parameterized cloud+storm layer (cyclones, storm size, turbulence, circulation)
  over the surface.

## The hex-artifact lesson (the big one)
**Symptom:** hexagonal tan patches along straight lines at quadtree **leaf boundaries**.
**Root cause:** biome temperature/moisture were sampled from the **discontinuous baked atlas height** (`hh`).
Tiny height steps at leaf-atlas seams, amplified by the lapse-rate term, crossed the **narrow treeline
smoothstep** (a ~±0.08 / 0.16-unit window) and flipped the biome color along the seam — a threshold flip, not
a geometry bug.
**Fix:** compute climate temp/moisture from the **smooth analytic `plateMacro` height (`bh`)**, not the baked
atlas. Baked relief still drives geometry, normals, and displacement — **only the biome-color climate inputs
were decoupled** onto the continuous field.
**Generalizable rule (now in the skill):** *never drive a narrow threshold (treeline, snowline, biome/ice
boundary) off discontinuous baked-atlas height. Use continuous analytic height for anything a smoothstep
gates; keep baked height for geometry.* This is a specific instance of the workspace's
[[silent-degradation-in-fenced-layers]] shape — a discontinuity in one layer silently corrupting a
threshold in another.

## The treeline window
Treeline is a **smoothstep from `(uTreeline − 0.06)` to `(uTreeline + 0.10)`** (0.16-unit temperature
window). Vegetation `cover = smoothstep(tempWindow) * (0.35 + 0.65 * smoothstep(moisture 0.05→0.35))` — moisture
sets the bare-rock proportion. The narrowness of this window is exactly what made sub-seam height steps visible;
widening thresholds or smoothing inputs is the lever when banding appears.

## Snow / ice (and the planned expansion)
Current snow is **ocean-only**, latitude-keyed, fBm-textured, blue-white albedo (≈0.80,0.87,0.97), alpha ≤0.9.
Planned (decision, not yet built): **exponential** snow overlay radiating from expanding ice caps (not linear),
a white overlay atop existing topography (not a terrain edit), with a Glacial preset covering the whole planet
and thinner radiating ocean ice. Keys off the same cap-mass field the terrain height already uses.

## Open bug — flashing storms
Cloud controls (**cyclones, storm size**, and secondarily **turbulence, circulation**) intermittently trigger
**flashing storms**. Seed-dependent, hard to reproduce (one instance was isolated then the seed was lost).
Smells like **floating-point precision / animation-state-sync / frame-timing** in the storm pass, not a logic
error. Open — capture the seed next time it reproduces.

## GLSL gotcha — reserved words
`active` is a **GLSL reserved keyword**; using it as a variable silently compiles until it doesn't (`'active'
is illegal use of reserved word`, fragment shader fails to link). Renamed to `belt`. **Lesson:** an incomplete
rename bites twice — grep found the fix at line 242 but missed a second `active` at line 354. When renaming a
shader identifier, grep the *whole* generated shader string, not the first hit. (WGSL/TSL has its own reserved
set — re-check on any GLSL→WGSL port.)

## Related
- technique → [[planetary-terrain-lod]]
- research → [[legion-hero-body-rendering-research]]
- reliability shape → [[silent-degradation-in-fenced-layers]]
