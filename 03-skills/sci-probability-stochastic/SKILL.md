---
name: sci-probability-stochastic
description: >
  Context-free probability + stochastic methods — distributions, sampling, seeded RNG,
  coherent noise (Perlin/simplex/value/worley), and Monte Carlo. The math behind
  procedural generation, particle/VFX variation, AI decision-making, and the sampling
  core of ML/rendering. Triggers: probability, distribution, random, RNG, seed, sampling,
  noise, Perlin, simplex, procedural generation, Monte Carlo, weighted random, gaussian.
aliases: [sci-probability-stochastic]
triggers: [probability, distribution, random, rng, seed, sampling, noise, perlin, simplex, procedural generation, monte carlo, weighted random, gaussian]
tier: foundation
hub: science-foundations
domain: science
surfaces: ["*"]
spec_version: "2.0"
---

# Foundations — Probability & Stochastic Methods

Reasoning and generating under randomness. Serves procedural game content, VFX variation, AI behavior,
and the sampling core of ML and rendering. (The *inferential* side — uncertainty, causation, experiment
rigor — lives in [[data-foundations]]; this is the *generative/computational* side.)

## Distributions are the vocabulary
"Random" is never enough — name the distribution. **Uniform** (flat), **Gaussian/normal** (natural
variation, central limit), **Poisson** (event counts), **exponential** (waiting times), **power-law**
(loot/rarity tails). Choosing the right distribution is most of the work; shape the feel of a system by
shaping its distribution.

## Seeded, reproducible randomness
Use a **seeded PRNG**, never an unseedable global `random()`. Seeding buys reproducible procedural worlds,
debuggable "random" bugs, replays, and deterministic tests. Separate streams per system (terrain vs. loot)
so one doesn't perturb another.

## Coherent noise (the procedural workhorse)
Raw random is white noise — useless for terrain. **Coherent noise** (Perlin, simplex, value, worley/cellular)
is smooth and continuous; layering octaves (**fractal Brownian motion**) builds natural terrain, clouds,
textures, and organic motion. Pick the noise by the structure you want (worley for cells/cracks, simplex
for smooth fields).

## Sampling + Monte Carlo
Estimate hard quantities by sampling: **Monte Carlo** integration underlies path-traced rendering,
**importance sampling** cuts variance, **rejection/inverse-transform** sampling draws from arbitrary
distributions, **weighted random** drives loot tables and AI choice. Variance is the enemy; more samples
and better sampling reduce it.

## Related
- hub → [[science-foundations]]
- applies-in ← [[vis-detection-tracking]]
- peer ↔ [[sci-numerical-methods]]
