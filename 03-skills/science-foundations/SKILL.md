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

## When the science spokes apply

Load a spoke when the work turns on the math being *right*, not when the math is merely present.
The test: would a wrong sign, a bad basis, an unstable step, or a mis-specified distribution
produce a result that still looks plausible? If yes, load the spoke.

| Situation | Spoke | The thing that goes silently wrong |
|---|---|---|
| Transforms, camera/world/object spaces, rotations, projections, bases | [[sci-linear-algebra]] | Composing in the wrong order or space; gimbal and quaternion normalization drift |
| Time-stepping, interpolation, root finding, accumulation over many frames | [[sci-numerical-methods]] | Precision loss and instability that look like a physics bug |
| Rigid bodies, collision response, constraints, forces | [[sci-physics-simulation]] | Energy gain or tunnelling from a variable timestep or a bad integrator |
| Sampling, noise, Monte Carlo, procedural generation, anything with a seed | [[sci-probability-stochastic]] | Correlated or unseeded randomness that cannot be reproduced or debugged |
| Astrophysical scale, orbits, stellar/structure properties | [[sci-astro-objects]] · [[sci-astro-structures]] | Unit and scale errors that survive because nothing on screen contradicts them |

Skip the spokes for arithmetic that is obviously right, for a one-line lerp, or when the real
question is aesthetic. Do not restate these principles inside a spoke: the spoke owns the medium,
this foundation owns the why.

## Validity done-gates

Math and simulation results are analysis results, so they clear the validity gates of
[#15 Analysis Operating Model](../../01-frameworks/15-analysis-operating-model.md) before being
reported as correct:

- **Units and spaces declared.** Every quantity states its unit and its coordinate space or basis.
  An unlabelled number is not a result. Scale errors are the most common defect in this domain and
  the hardest to see.
- **Stability and error characterized, not assumed.** Name the integrator or scheme, its stability
  condition, and the timestep or tolerance actually used. "It looks stable at 60 FPS" is not a
  stability claim.
- **Determinism reproducible.** Seeded RNG, fixed simulation timestep, and a stated seed or
  configuration, so the same input produces the same output on another machine. A result that
  cannot be re-run is an anecdote.
- **Sanity checks against a closed form or conservation law.** Compare to an analytic solution, a
  conserved quantity (energy, momentum, mass, probability summing to one), or a limiting case with
  a known answer. At least one independent check, always.
- **Convergence shown where it matters.** If the answer depends on step size, sample count, or
  resolution, show that it converges (or state the residual error you are accepting).
- **Floating-point assumptions surfaced.** Where equality, subtraction of near-equal values, or
  large dynamic range is involved, say how it is handled rather than trusting the default.
- **Uncertainty reported for stochastic results.** A Monte Carlo number without a variance or
  interval is half a result.

Visual consequences of the math (a render, a simulation frame, a plot) still clear
[#10 Perception Integrity](../../01-frameworks/10-perception-integrity.md) at native resolution and
[#11 Anticipatory Failure Analysis](../../01-frameworks/11-anticipatory-failure-analysis.md) before
the technique is proposed. Framework
[#13 Domain Rigor Stack](../../01-frameworks/13-domain-rigor-stack.md) is why these gates are
written down here rather than assumed.

## Related
- spoke → [[sci-astro-objects]] · [[sci-astro-structures]] · [[sci-linear-algebra]] · [[sci-numerical-methods]] · [[sci-physics-simulation]] · [[sci-probability-stochastic]]
- applies-in ← [[glsl-shader-architect]] · [[lead-data-scientist]] · [[lead-game-developer]] · [[legion-project]] · [[sci-astro-objects]] · [[sci-astro-structures]] · [[threejs-materials-master]] · [[webgpu-advanced-rendering]]
- peer ↔ [[imaging-foundations]] · [[vision-foundations]]
