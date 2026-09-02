---
tags: [game-dev, legion, threejs, webgpu, glsl, procedural-planet, normals, bump-mapping, close-zoom, lod, performance]
created: 2026-07-23
updated: 2026-07-23
status: working
confidence: medium
sources:
  - "Sandahl, 'Procedural Planet Generation', TNM084 report, Linköping Univ. (the PDF that seeded this note) — eqs. 12–13 for the tangent-plane normal perturbation"
  - "Gustavson, 'Recomputing normals for displacement and bump mapping, procedural style' (psrdnoise 3D tutorial), 2021 — https://stegu.github.io/psrdnoise/3d-tutorial/bumpmapping.pdf"
  - "Michelic, 'Real-Time Rendering of Procedurally Generated Planets', CESCG 2018 — https://cescg.org/wp-content/uploads/2018/04/Michelic-Real-Time-Rendering-of-Procedurally-Generated-Planets-2.pdf"
  - "session 2026-07-23 — PDF triage against the shipped planet renderer"
related_skills: [planetary-terrain-lod, realtime-render-performance, webgpu-advanced-rendering, glsl-shader-architect, lead-game-developer]
related_projects: [13-legion]
related_notes: [legion-planet-surface-rendering, legion-hero-body-rendering-research, legion-galaxy-playbook]
---

# Legion — Analytic-Gradient Normals for Close-Zoom Terrain Bump

**Queued for the close-zoom-performance session** (the theme Sean pre-announced closing 2026-07-22).
This is the one genuinely useful lead extracted from the Sandahl *Procedural Planet Generation* PDF —
not the paper itself (an undergrad "miniature globe" toy, behind Legion on every core axis), but two of
its references that intersect Legion's close-zoom LOD problem.

---

## The problem this addresses

Legion bakes height **and** normals to an atlas (`finishHeight()`, dual-height terrain — see
[[legion-planet-surface-rendering]]). Baked normals are cheap at runtime but have a fixed spatial
resolution: **at close zoom the highest noise octaves have no geometry and no baked-normal detail to
represent them** — you run out of atlas resolution before you run out of visible surface.

This is *exactly* the limitation the Sandahl paper concedes in its own conclusion: geometric resolution
"is not high enough for the highest octaves… could possibly be solved by rendering the higher octaves as
a bump map rather than a displacement." Legion's next session starts past where that paper stops.

## The technique: derive the normal from the noise's own gradient, not from resampling

Standard multi-tap normal reconstruction (what the Sandahl paper does in its base path, eqs. 7–10)
samples the height field **3 extra times per vertex** at small tangent-plane offsets and takes the cross
product of the displaced points. That's 3× the noise cost purely to get a normal, and the offset choice
trades aliasing against smearing.

The **analytic-gradient** approach (Gustavson psrdnoise, ref [4]) instead has the noise function return
its **analytic derivative `g = ∇noise`** alongside the value — one evaluation, exact gradient, zero extra
taps. The surface normal is then perturbed by projecting that gradient onto the tangent plane and
subtracting it from the un-perturbed normal:

```
g⊥ = g − (g·n) n          // project gradient onto tangent plane (Sandahl eq. 12)
N  = normalize(n − g⊥)     // perturbed normal (Sandahl eq. 13)
```

where `n` is the un-perturbed (sphere) normal. For an fBm sum, accumulate the **gradients** octave-by-octave
the same way you accumulate the heights (chain-rule the frequency scaling per octave), so one fBm pass
yields both the height and the correct summed gradient.

### Why this matters for Legion specifically

1. **Bump the high octaves instead of displacing them.** Keep the baked atlas for the low/mid octaves that
   drive real geometry and thresholds; at close zoom, add the **highest octaves as analytic bump only** —
   perturb the normal from the gradient, never touch geometry. Sharper than the atlas can resolve, and it
   costs ALU (which the close-zoom regime has) instead of vertices/bandwidth (which it doesn't — see the
   ~8–9 ms fill-rate/ALU budget in [[legion-hero-body-rendering-research]]).
2. **Cheaper than the 3-tap baseline** when you do need runtime normals: 1 noise eval + a gradient vs 3–4
   evals. Frees ALU in precisely the regime that is ALU-bound.
3. **No seam risk from finite-difference offset choice** — the gradient is continuous by construction, so
   it won't add a *new* class of the quadtree-leaf-edge artifacts already tracked in
   [[legion-planet-surface-rendering]].

## What Michelic (ref [5]) actually contributes — and what it doesn't

Corrected on read: Michelic 2018 is **not** a cube-sphere quadtree paper. It uses a **persistent projected
grid** — a screen-space grid projected onto the sphere, with LOD and frustum-culling folded into the
projection so tessellation concentrates where the camera looks, with continuous ground↔space transition.
Also in it: a **planar wave function modified for the sphere's curvature** (seamless, evenly-spaced ocean
waves) and **volumetric clouds over precomputed atmospheric scattering**.

**Verdict for Legion:** the projected-grid LOD is an *alternative* to Legion's committed cube-sphere +
CDLOD ([[planetary-terrain-lod]]) — do **not** adopt it, it's a different architecture, not an augmentation.
The salvageable pieces are narrow: (a) the **curved-surface wave function** if Legion adds real ocean wave
geometry (living weather + ocean ramps exist, but wave *geometry* isn't shipped), and (b) confirmation that
precomputed atmospheric scattering + volumetric clouds is the right pairing — which Legion already does per
[[legion-hero-body-rendering-research]] / [[legion-galaxy-playbook]]. Treat Michelic as corroboration, not
a new source of architecture.

## Third salvage: wrapped-diffuse SSS (Sandahl ref [7])

The atmosphere/terminator can use the **wrapped-diffuse** cheap subsurface approximation (GPU Gems ch.16):
`I_d = max(0, (L·N + w) / (1 + w))` — light wraps past the terminator by factor `w`. A ~2-line term worth a
glance against Legion's current atmosphere shader to see if it's already covered.

## Do / don't for the perf session

- **Do** prototype analytic-gradient normals for the high-octave bump path; measure ALU vs the current
  baked-atlas + any runtime tap cost at close zoom.
- **Do** require the noise routines to return `(value, gradient)` so fBm sums the gradient for free.
- **Don't** rip out the baked atlas — it still owns low/mid geometry + the analytic-macro thresholds.
- **Don't** adopt Michelic's projected-grid LOD; Legion is committed to cube-sphere CDLOD.
- **Source caveat:** the Gustavson equations here are transcribed from the Sandahl paper's restatement
  (eqs. 12–13) + known psrdnoise usage; the primary Gustavson PDF wouldn't extract cleanly this session.
  Re-read `bumpmapping.pdf` directly before implementing to confirm the exact per-octave gradient chaining.
