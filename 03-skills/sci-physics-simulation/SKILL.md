---
name: sci-physics-simulation
description: >
  Context-free classical mechanics for real-time simulation — kinematics + dynamics
  (F=ma), rigid bodies (linear + angular), the fixed-timestep loop, collision detection
  (broad/narrow phase) and response (impulses, restitution, friction), and constraints.
  The physics a game engine actually runs. Triggers: physics, simulation, rigid body,
  collision detection, collision response, impulse, restitution, friction, constraint,
  fixed timestep, kinematics, dynamics, broadphase, AABB, GJK.
aliases: [sci-physics-simulation]
triggers: [physics, simulation, rigid body, collision detection, collision response, impulse, restitution, friction, constraint, fixed timestep, kinematics, dynamics, broadphase, aabb, gjk]
tier: foundation
hub: science-foundations
domain: science
surfaces: ["*"]
spec_version: "2.0"
---

# Foundations — Physics Simulation

Classical mechanics as an engine runs it. Builds directly on [[sci-linear-algebra]] (everything is
vectors/quaternions) and [[sci-numerical-methods]] (the integrator).

## Kinematics + dynamics
State is position + velocity (linear) and orientation + angular velocity (rotational). **F = ma** drives
linear motion; **τ = Iα** (torque, moment of inertia) drives rotation. Integrate acceleration → velocity →
position each step (semi-implicit Euler is the workhorse; Verlet for constraint-heavy systems).

## The fixed-timestep loop (the most important pattern)
Run physics at a **constant `dt`** (e.g. 1/60 s) in an accumulator loop, decoupled from the variable render
frame rate, and **interpolate** rendered positions between the last two physics states. This buys
determinism, stability, and frame-rate independence. Variable-`dt` physics is the root of "it behaves
differently on a faster machine" bugs.

## Collision detection — broad then narrow
- **Broad phase:** cheaply cull pairs that can't touch (AABB sweep-and-prune, spatial hash, BVH). O(n²)
  naive pair testing is the classic scaling failure.
- **Narrow phase:** exact tests on surviving pairs (sphere/AABB/OBB, SAT for convex polytopes, **GJK+EPA**
  for general convex shapes) → contact point, normal, penetration depth.

## Collision response + constraints
Resolve contacts with **impulses** (instantaneous velocity changes) using **restitution** (bounciness) and
**friction** (Coulomb model). Stack stability and joints come from **constraint solvers** (sequential
impulse / position-based dynamics) iterated per step. Penetration is corrected with a small positional
"slop" bias, not a hard snap (which causes jitter).

## Determinism caveats
Cross-platform determinism requires fixed `dt`, consistent float behavior, and a fixed solver iteration
order — relevant if Legion ever needs lockstep multiplayer or replays.

## Related
- hub → [[science-foundations]]
- peer ↔ [[sci-linear-algebra]] · [[sci-numerical-methods]]
