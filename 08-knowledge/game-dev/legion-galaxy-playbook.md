---
tags: [game-dev, legion, galaxy, playbook, recipe, threejs, webgpu, volumetrics, particles, scale-traversal, photoreal]
created: 2026-06-16
updated: 2026-06-16
status: stable
confidence: high
sources: [skill-ecosystem-and-mcp-servers, threejs-galaxy-visualization, session-log 2026-06-16]
related_skills: [sci-astro-objects, sci-astro-structures, vfx-particle-systems, vfx-volumetrics, game-scale-traversal, img-photoreal-rendering, img-cinematography, threejs-vfx-atmosphere, webgpu-advanced-rendering, legion-project]
related_projects: [13-legion]
---

# Legion Galaxy Playbook — the prescriptive build recipe

The ordered recipe for building (and refining) Legion's galaxy in Three.js + WebGPU, wiring the
foundation + technique skills into one pipeline. This is the **"how to build it"**; the **"traps we
already hit"** live in [[threejs-galaxy-visualization]] (12 hard-won patterns) — this playbook references
them rather than restating, so the two don't duplicate.

## Load this skill chain first
For galaxy work, the precedence resolves (foundations → application):
`design-foundations` + `imaging-foundations` + `img-vfx` + `science-foundations` → `lead-game-developer`
→ `threejs-vfx-atmosphere` → **[[vfx-particle-systems]]**, **[[vfx-volumetrics]]**, plus
**[[game-scale-traversal]]**, **[[sci-astro-objects]]**, **[[sci-astro-structures]]**,
**[[img-photoreal-rendering]]**, **[[img-cinematography]]**. (Trigger words: *galaxy, nebula, star field,
black hole, flythrough, volumetric* surface these automatically.)

## The build sequence

**1 — Scale architecture (do this first; everything else depends on it).** Establish the nested-scale
shells (galaxy → sector → system → body → surface) with **floating-origin / camera-relative rendering** and
a **logarithmic (or reversed-Z) depth buffer** — see [[game-scale-traversal]]. Get precision + depth right
*before* adding content, or you rebuild later.

**2 — Star field.** Instanced **GPU points/sprites** ([[vfx-particle-systems]]) colored by **blackbody
temperature** and brightened by luminosity+distance ([[sci-astro-objects]]) — mostly white/blue-white with
scattered orange/red, additive blend, soft round sprite, HDR so bloom catches the bright ones. Budget by
angular size; resolve to individual systems on approach (LOD cross-fade, step 7).

**3 — Galaxy disc + nebulae.** A **single-box volumetric raymarch** (not stacked planes — [[threejs-galaxy-visualization]]
#7/#8) with **Beer-Lambert** extinction + emission ([[vfx-volumetrics]]); emission colored by gas type
(**H-alpha red, OIII teal** — [[sci-astro-structures]]); density from fBm/curl noise (low-freq baked shape
from Blender → 3D texture, + high-freq procedural detail). Tune box-Y ≈ 1.5× scale-height (#8).

**4 — Dust occlusion.** Integrate dust density into the same raymarch via **Beer-Lambert** so dust
silhouettes stars behind it from any angle — this is the *only* correct dust solution ([[threejs-galaxy-visualization]] #9).

**5 — Render pipeline.** Compute **linear/HDR** → **ACES (or AgX) tonemap** → sRGB encode
([[img-photoreal-rendering]]); add **bloom** for emissive bodies and **IBL** from the star/nebula
environment. A physically-based camera (EV, subtle DOF on arrival) per [[img-photography]] sells it.

**6 — Hero bodies.** Black holes = lensing post-shader + bright Doppler-beamed accretion disk
([[sci-astro-objects]]); gas-giant rings = instanced particle fields ([[vfx-particle-systems]]); atmospheres
= Rayleigh/Mie scattering ([[img-optics-light]]).

**7 — Flythrough camera.** Seamless galaxy→system→planet zoom: **opacity-ramp LOD cross-fades** (not
visibility toggles — #4), **per-focused-object framing scale** (#5), an **arc-up quadratic-Bezier path**
(don't fly *through* the disc — #10) with **ease-in-out cubic** timing and **log-space** distance interpolation
(constant *perceived* speed), focus-pull + slerp orientation ([[img-cinematography]], [[game-scale-traversal]]),
and **orbital-state-reconstruction handoff** back to the orbital camera (#11). Gate velocity streaks hard (#12).

## Performance budget (target 60 fps)
- **Particles** on the GPU (WebGPU compute or GPGPU ping-pong — [[vfx-particle-systems]], [[webgpu-advanced-rendering]]);
  the CPU never touches per-particle state. Star fields scale to 10⁵–10⁷ as points.
- **Volumetrics** are the cost center: **half/quarter-res** raymarch + blue-noise jitter + temporal
  reprojection, capped step count, early-out on full opacity, march only the dense region ([[vfx-volumetrics]]).
- **LOD by angular size**, not raw distance; impostors for distant systems; stream/generate detail on approach.
- **Overdraw** is the real killer at scale — additive star fields + transparent volumes overlap heavily; keep
  the volumetric pass low-res and the particle sprites small.
- **Draw calls:** one raymarch box beats N stacked planes (#7); instance everything else.

## Gotchas
Don't relearn them — read [[threejs-galaxy-visualization]] (selection `userData.type`, per-layer pattern
uniqueness, dust occlusion, opacity-ramp LOD, per-object framing, arc-up camera, mode handoff, streak restraint).

## Blender asset path
Author hero nebulae / models in Blender, bake density to VDB/3D-texture, load in Three.js — via the
**Blender MCP** (`ahujasid/blender-mcp`), per [[skill-ecosystem-and-mcp-servers]].
