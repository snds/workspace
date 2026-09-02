---
tags: [multi-agent, verification, workflow, methodology]
created: 2026-07-21
updated: 2026-07-21
status: working
confidence: high
sources: [session-log 2026-07-21]
related_skills: []
related_projects: []
---

# Adversarial-verify label volatility — report the mapped verdict, not the pass/fail count

In a multi-agent audit workflow shaped **map each unit → adversarially verify with N skeptic
passes**, the per-unit **CONFIRMED / ADJUSTED / REFUTED label is not stable across runs.** It is a
function of how aggressively the skeptic passes happen to refute on a given sampling — a property of
the verifier temperature, not of the mapping.

**Observed (2026-07-21).** Two full verification passes over the *same* 33 mapped units, same source,
same script (mappers replaying from cache, so their inputs were byte-identical):

- Pass 1: **8 confirmed / 19 adjusted / 6 refuted**
- Pass 2: **17 confirmed / 16 adjusted / 0 refuted**

…yet **every unit's substantive verdict — resolution rung + difficulty — was identical across both
passes.** Not one moved. And every Pass-1 "refuted" unit kept its exact rung/difficulty in Pass 2,
meaning those refutations were target *refinements*, never *reversals*. The mapper layer (deterministic
inputs) is stable; the adversarial layer is not.

## Why it happens

A skeptic prompted to "default to refuted when uncertain" will over-refute at a **variable rate** run to
run. That's good for *surfacing* weak claims but bad as a *stable score*. The boolean is a coin with a
per-run bias, not a measurement.

## How to report it (and what to do instead)

- **Publish the stable substance** — the mapped verdict (where it lands, how hard) — as the result.
  Treat the verify pass as a *convergence check*: "two independent passes agreed on rung + difficulty
  for all N units; flags were refinements, not reversals." That is honest and reproducible.
- **Do not headline a "24 confirmed / 9 adjusted / 0 refuted" style count.** It reads as a stability
  metric but is sampling noise. Republishing it invites a reviewer to anchor on a number that won't
  reproduce. (A first pass of this same audit had published exactly such a count; the re-run exposed it.)
- **For a durable pass/fail, aggregate more passes** (majority of k ≥ 3) or gate on the **correction
  content** — did the rung actually change? — rather than the boolean flag.
- **Independently cross-check load-bearing claims** by reading/grepping the real source, rather than
  trusting either the mapper or the verifier. In this session the hand-checks (line counts, dependency
  presence, file existence) were what converted "the agents say so" into "verified."

## Design implication for the workflow

If a run's headline depends on the verify labels, the harness is under-specified. Either raise k and
report the aggregate, or redefine the unit's "changed?" signal off the correction diff. Keep the
adversarial pass for what it's good at — catching the genuinely weak mapping — and stop reading its
per-unit boolean as a stable grade.

Related: [[workflow-patterns]] (general multi-agent orchestration mechanics).
