---
name: sci-numerical-methods
description: >
  Context-free numerical computing — floating-point reality, interpolation (lerp/slerp/
  splines/easing), numerical integration (Euler/semi-implicit/Verlet/RK4), root-finding,
  and stability/error analysis. How to compute with real numbers without the result drifting,
  exploding, or jittering. Triggers: floating point, epsilon, interpolation, lerp, easing,
  integration, Euler, Verlet, RK4, stability, numerical error, timestep, convergence.
aliases: [sci-numerical-methods]
triggers: [floating point, epsilon, interpolation, lerp, easing, numerical integration, euler, verlet, rk4, stability, numerical error, convergence, root finding]
tier: foundation
hub: science-foundations
domain: science
surfaces: ["*"]
spec_version: "2.0"
---

# Foundations — Numerical Methods

Computing with real numbers on finite hardware. The principles hold for a physics step, an animation
curve, a shader, and an optimizer.

## Floating point is not the reals
Values are approximate; **never test floats for equality** (use an epsilon tolerance scaled to magnitude).
Catastrophic cancellation (subtracting near-equal numbers) destroys precision; accumulation drifts. Order
of operations changes results. Design around it: prefer stable formulations, accumulate in higher precision,
reset/renormalize periodically (e.g. re-normalize quaternions each step).

## Interpolation
Moving between values smoothly: **lerp** (linear), **slerp** (rotations — constant angular velocity),
**splines** (Catmull-Rom/Bézier for paths), **easing** (perceptual time-warping). Key distinction:
interpolate in the *right space* (color in OKLCH not sRGB; rotation via slerp not component lerp).

## Numerical integration (the simulation engine)
Advancing state over time. The choice is a stability/cost/accuracy trade:
- **Explicit (forward) Euler** — simplest, *unstable* for stiff/oscillatory systems (springs blow up).
- **Semi-implicit (symplectic) Euler** — update velocity then position; cheap and stable for games. The default.
- **Verlet** — position-based, energy-stable, great for cloth/particles/constraints.
- **RK4** — accurate, costly; for when fidelity matters more than frame budget.
Pair any of these with a **fixed timestep** (see [[sci-physics-simulation]]) for determinism.

## Stability + error
A method is *stable* if errors don't grow unboundedly. Smaller `dt` improves accuracy but costs frames;
stiff systems need implicit/symplectic methods, not smaller steps. Always ask: does this converge, and
does the error stay bounded?

## Related
- hub → [[science-foundations]]
- peer ↔ [[sci-linear-algebra]] · [[sci-physics-simulation]] · [[sci-probability-stochastic]]
