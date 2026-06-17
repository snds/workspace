---
name: science-foundations
description: >
  The mathematical + physical first principles that underlie simulation, rendering,
  and machine learning — linear algebra, numerical methods, classical mechanics, and
  probability. Load before any specialty that does real math: a game engine, a shader,
  a physics step, an ML model. The substrate beneath game development, real-time
  rendering, and data science. Triggers: math, physics, linear algebra, vector, matrix,
  quaternion, simulation, numerical, integration, probability, Monte Carlo, collision.
aliases: [science-foundations]
triggers: [math, physics, linear algebra, vector, matrix, quaternion, transform, simulation, numerical methods, integration, probability, monte carlo, collision, mechanics]
tier: foundation
domain: science
surfaces: ["*"]
spec_version: "2.0"
---

# Science Foundations

The math and physics that real engineering rests on. A game engine, a GPU shader, a physics
step, and an ML model are all the *same handful of mathematical objects* applied in a medium —
vectors, matrices, derivatives, distributions. This foundation owns the **context-free principle**;
the specialty (engine code, GLSL, a training loop) owns the application. Distinct from the font
`math-*` spokes (bezier/boolean/optical), which are 2D glyph-geometry-specific.

> Adapted/synthesized from canonical game-math + numerical-methods references (e.g. the
> "math for game developers" tradition — vectors → transforms → simulation). External community
> skills on mcpmarket/skills.sh wrap *engines* (Three.js, Unity, Unreal); none teach this
> substrate, so it is authored here.

## The four foundations

| Spoke | Owns (context-free principle) |
|---|---|
| [[sci-linear-algebra]] | Vectors, matrices, quaternions, bases, transforms, projections — the language of space |
| [[sci-numerical-methods]] | Floating point, interpolation, integration schemes, stability, error — computing with reals |
| [[sci-physics-simulation]] | Classical mechanics, rigid-body dynamics, collision, constraints, the fixed-timestep loop |
| [[sci-probability-stochastic]] | Distributions, sampling, noise, Monte Carlo — reasoning + generating under randomness |

## Core convictions (apply across all spokes)

- **Coordinate everything.** Every position, velocity, color, and weight is a vector in *some* space;
  name the space and the basis before you compute.
- **The float is not the real.** Finite precision means equality is a lie, order of operations matters,
  and stability is a design property, not an afterthought.
- **Simulate in fixed steps; render in variable ones.** Determinism and stability come from a constant
  physics `dt`, decoupled from frame rate.
- **Randomness is a tool with a seed.** Reproducible stochasticity (seeded RNG, named distributions)
  beats "just call random()".

## Applied in
- Game engine + physics → [[lead-game-developer]], [[legion-project]]
- Real-time rendering math → [[webgpu-advanced-rendering]], [[glsl-shader-architect]], [[threejs-materials-master]]
- ML / statistics math → [[lead-data-scientist]] (pairs with [[data-foundations]] for the reasoning layer)

## Related
- spoke → [[sci-astro-objects]] · [[sci-astro-structures]] · [[sci-linear-algebra]] · [[sci-numerical-methods]] · [[sci-physics-simulation]] · [[sci-probability-stochastic]]
- applies-in ← [[glsl-shader-architect]] · [[lead-data-scientist]] · [[lead-game-developer]] · [[legion-project]] · [[sci-astro-objects]] · [[sci-astro-structures]] · [[threejs-materials-master]] · [[webgpu-advanced-rendering]]
- peer ↔ [[imaging-foundations]] · [[vision-foundations]]
