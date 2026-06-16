---
tags: [game-dev, threejs, rendering, shaders, galaxy, lod, raymarch, camera, motion-blur]
created: 2026-05-11
updated: 2026-05-12
status: stable
confidence: high
sources: [session-log 2026-05-11, session-log 2026-05-12, github.com/snds/legion commits 0664dc6 → ea72616]
related_skills: [threejs-materials-master, glsl-shader-architect, threejs-vfx-atmosphere, webgpu-advanced-rendering, legion-project]
related_projects: [13-legion]
---

# Three.js Galaxy Visualization — Hard-Won Patterns

Captured from the Legion 2026-05-11 session. Pulling out the patterns
that generalize beyond Legion so the next Three.js scene-at-scale work
doesn't repeat the same dead-ends.

> This doc is the **gotchas / hard-won patterns**. For the prescriptive
> build recipe (skill chain + ordered sequence + perf budget), see
> [[legion-galaxy-playbook]].

## The five things that matter

### 1. Selection: every interactive Object3D MUST seed `userData.type` in its factory

The single most catastrophic bug class: factories returning Three.js groups
with no `userData.type` set. Raycasters walk the parent chain looking for
type and silently discard every hit that doesn't have one. Symptoms:
"clicking doesn't seem to work" / "tooltips don't appear" — the raycaster
is firing fine, it's just rejecting the hit.

Fix: every factory function that returns a selectable object writes
`group.userData.type = 'something'` immediately after construction. Add
class-specific fields (`name`, `bodyRadius`, etc.) the inspector or
tooltip needs.

For Legion this was happening in 6 factories (planets, moons, bobs,
stars, system markers, alien markers). They'd been written months ago
and never tested via click. Tooltip + hover + dblclick all silently
failed on those classes the entire time.

**Rule of thumb:** if you can't click a thing in your scene, the *first*
diagnostic isn't camera/raycast/depth — it's `console.log(hit.object.userData)`.

### 2. Stacked-shader-layer volume: per-layer uniformity is the trap

To give a flat shader-rendered disc visible thickness when viewed
off-axis, the obvious move is stacking N copies at Y offsets. But if
all N copies use **identical** uniforms, they paint identical patterns
vertically translated. From any non-face-on angle that reads as N
discrete concentric copies, not as one volumetric slab.

Fix: per-layer **pattern uniqueness**. Two uniforms per layer:
- `uLayerSeed` offsets the noise/FBM sample → different cloud/dust
  patterns per layer
- `uLayerArmShift` rotates the procedural phase (spiral angle, etc.)
  by ±0.1 rad max → adjacent layers don't perfectly stack

Result: face-on the layers superimpose into a slightly-softer-but-
recognizable pattern (the small per-layer rotation introduces ~5° of
azimuthal blur, which actually approximates real disc velocity
dispersion). Off-axis the layers smear into volume.

**Rule of thumb:** if you stack identical-shader layers and they read
as bands when tilted, you need per-layer noise/phase offsets, not just
more layers.

### 3. Volumetric occlusion needs DEDICATED dust layers, not in-shader dust

A common pattern: bake dust attenuation into the main material via
multiplicative mix-to-dust-color. This dims the layer's *own* emission
but doesn't occlude light from other layers in the framebuffer.

For true galaxy-photo silhouette dust (where stars BEHIND the dust
visibly dim), you need separate dust planes rendered NormalBlending
with near-black color and their own alpha pattern. Interleave them
with the star planes in strict renderOrder: star-dust-star-dust. The
painter's algorithm composites correctly: each dust plane multiplies
down whatever was painted before it.

In Legion: 8 dust planes interleaved with 9 star planes, all using the
same spiral/dust pattern generator as the disc shader (so dust filaments
align spatially with the arms) but with per-layer seed offsets so the
dust patterns aren't identical across layers.

**Rule of thumb:** if you need "dust silhouettes background stars,"
in-shader multiplicative dust isn't enough — you need separate dark
planes at intermediate depths.

### 4. Powers-of-10-style seamless zoom transitions: opacity ramps, not visibility toggles

Binary `layer.visible = true/false` at tier boundaries creates the
"galaxy mesh appears abruptly when crossing the arm-tier threshold"
class of visual pop. Better:

- Lower-level visibility system enables the geometry one tier *earlier*
  than it's fully presented.
- A per-frame LOD updater drives `uOpacity` (or material.opacity) via
  a smoothstep ramp on camera distance, fading the layer in across
  the *previous* tier's range.

In Legion: galaxy disc shader enabled at SECTOR tier with discPresence
ramping 0→1 across camDist 2500→5500. At sector camDist 4000 the disc
is at ~60% presence — visible *through* the sector orb as Powers-of-10
anticipation, not popping in at arm boundary.

**Rule of thumb:** every "this layer becomes relevant at zoom tier X"
deserves a smooth opacity ramp across the previous tier's range, not a
visibility toggle.

### 5. Multi-scale camera framing needs per-object scale, not absolute camDist

Naive: define camera distance ranges per zoom tier (e.g., SURFACE = 0.6-2.5 WU).
Result: when the focused object is the star (radius ~0.5 WU), SURFACE camera
sits *inside* the star — full-screen yellow wash.

Fix: per-object focus scale. `trackedObject.userData.bodyRadius` records the
geometry radius; the CameraController multiplies close-in tier camDist by
`bodyRadius / referenceRadius` so SURFACE always frames the *focused body*
at the right angular size regardless of which planet/moon/station you've
selected.

In Legion: reference radius is 0.3 WU (Earth analog). Gas giant size 2.0 WU
gets ~6.7× framing distance at SURFACE; small moon 0.08 WU gets ~0.27×.
ORBIT tier uses half-lerp so it doesn't balloon for gas giants.

**Rule of thumb:** any zoom-tier system that names tiers semantically
("surface, low orbit, orbit, ...") needs per-focused-object scale,
otherwise the framing only works for one specific object size.

## Cross-domain implications

These patterns aren't Legion-specific — they apply to any Three.js
visualization that:
- Has multi-scale interaction (planet view → system view → galaxy view)
- Renders procedural volumes via stacked shader planes
- Needs photoreal-ish "dust occludes stars behind" rendering
- Wants Powers-of-10-style seamless zoom

Notable: this is also a useful pattern for product-design visualizations
that need to operate across scales (e.g. a city → district → block →
building viewer). Same opacity-ramp + per-object framing principles.

## Additional patterns added 2026-05-12 (post-reference-video review)

### 6. Reference-video review methodology

When the visual target is hard to articulate, ffmpeg-extract triage frames
from reference videos and review through three lenses simultaneously:
**motion design** (camera dynamics, easing curves, transition rhythm),
**3D game engine** (LOD, particles, volumetric, performance), **3D
modeling / effects** (geometry, dust occlusion, nebula representation).
The cross-product of those lenses surfaces structural gaps that a single
lens misses. In this project: 4 videos × 24-step frame extraction
identified 7 structural rewrites needed.

### 7. Stacked-plane volumes are a dead-end for off-axis viewing

Stacking N copies of a procedural disc shader at vertical offsets works
*only* face-on. Off-axis (any tilt past ~20°), the layers visibly read
as N concentric copies. Per-layer noise/rotation offset masks it
partially but doesn't fix the structural issue. **The right answer is
a volumetric raymarch on a single thin-box geometry** — looks correct
from any angle by construction, and goes from N draw calls to 1.

### 8. Volumetric raymarch tuning — the box-Y vs. scale-height trap

For a ray-marched volumetric disc to render at all, the box's Y span
must be similar to (or only slightly larger than) the disc material's
vertical scale-height. If the box is much taller than the disc, most
march samples land in empty space above/below the midplane and
contribute zero density — the entire box discards. Concretely: box
Y-half-extent ≈ 1.5× the scale-height works. Combine with an extinction
coefficient tuned so a typical midplane march accumulates 0.6–0.8
alpha (Beer-Lambert integrates exponentially, so the coefficient is
in the ballpark of 1/(stepSize × n_steps_in_dense_region)).

### 9. Beer-Lambert dust occlusion is the only correct dust solution

Dust as additive haze adds light. Dust as NormalBlending dark planes
darkens whatever is behind in render-order. Neither matches real galaxy
photos where dust silhouettes stars across arbitrary 3D distances. The
correct solution: integrate (disc_emission, dust_density) along the
view ray with Beer-Lambert. Extinction along each step blocks emission
from earlier in the march; emission from this step is then attenuated
by the integrated transmittance ahead. One math formula, no layer
stacking, dust silhouettes correctly from any angle.

### 10. Cinematic-flight camera: arc UP not THROUGH

Linear interpolation between two camera positions traverses straight
lines, which for galactic-scale travel means flying THROUGH the disc
plane — uncomfortable, no sense of perspective, no parallax. A
quadratic Bezier with the control point lifted 30% of the travel
distance along worldUp arcs the camera OVER the disc plane. The arc
gives natural parallax (foreground stars sweep past, far stars stay
stable) and matches the rhythm of every reference fly-through.

Pair with ease-in-out cubic timing: gentle acceleration + cruise +
deceleration. The deceleration phase is the "settled moment" the user
gets when arriving — the camera audibly slows, the destination resolves,
and the orbit math takes over cleanly.

### 11. Camera-mode handoff via orbital-state reconstruction

When a flight ends, the camera is at some world position with some
look-at direction. To hand back to orbital camera math (theta, phi,
camDist, focus) cleanly: compute the orbital state that REPRODUCES
the current camera position. Specifically: focus = lookAt target;
delta = camPos - focus; dist = |delta|; theta = atan2(delta.z, delta.x);
phi = acos(delta.y / dist). Set those as Game state. The next frame's
orbital math will produce the IDENTICAL camera position — zero
discontinuity. This is the right pattern for any multi-mode camera
system (cinematic → free / orbital → first-person / etc).

### 12. Velocity-aware effects need restraint at game scale

A 5-second hero shot can use 4× sprite elongation streaks for "going
fast" feel. A real-time game scene the player spends 30 minutes in
absolutely cannot — it becomes nauseating and reads as a visual bug.
Streak strength gates:
  - Below threshold (slow nav): completely off
  - Smoothstep ramp across an upper band (fast flight): ramps in
  - Hard cap on stretch (1.4× — sprite is barely longer than tall)
  - Alpha DROPS with stretch (streaked stars are dimmer than crisp)
The principle: if the user isn't sure whether the streaks are there,
that's the right amount.

## Open questions / not yet validated

- **Differential rotation** of stacked-shader patterns at high time
  compression: not yet implemented. Would need uTime in vertex shader
  rotating each layer's pattern at a radius-dependent rate. Per-particle
  alignment between the shader disc and the particle field is fragile
  — they'd need to share the same uTime-driven rotation.
- **Galactic warp** at the disc edges: implemented in Legion as
  vertex-shader Y displacement on disc planes + matching JS warp
  applied to particle positions at generation. Works visually. Untested
  whether the per-particle approach scales beyond ~200K particles in
  terms of generation time.
- **Extragalactic tier** (Andromeda at 770 kpc real distance, far
  outside any of Legion's current camDist ranges): would need its own
  scale (~1 Mpc per WU) and disc shader at that scale. Not attempted
  yet — would be a separate visualization pass.
