---
name: data-foundations
description: >
  Context-free data + analytics first principles — data quality before modeling,
  statistical reasoning and uncertainty, correlation vs. causation, experiment
  rigor, and reproducibility. The shared root beneath data science, ML, analytics,
  and experimentation work. Load BEFORE the data hub or its spokes. Triggers:
  data quality, statistics, uncertainty, causal inference, experimentation, bias.
aliases: [data-foundations]
triggers: [data quality, statistics, uncertainty, correlation causation, causal inference, experimentation, a/b test, bias, reproducibility, sampling]
tier: foundation
domain: data
surfaces: ["*"]
spec_version: "2.0"
---

# Data Foundations

The first principles of reasoning from data. Lean by design — the single data hub
([[lead-data-scientist]]) applies these; method depth (specific models, pipelines, BI platforms) lives
in its spokes.

## Data quality precedes everything
Garbage in, garbage out is a law. Before any model or chart: understand provenance, completeness,
sampling, and how the data was *generated* (and by whom, for what purpose). Most "wrong model" failures
are upstream data failures. Profile and validate before you analyze.

## Statistical reasoning + uncertainty
Every estimate has a distribution; a point number without an interval is a half-truth. Respect sample
size and variance, beware multiple-comparisons and p-hacking, and **always represent uncertainty**
(intervals, not just means). Surprising results are more likely errors than discoveries — verify first.

## Correlation is not causation
Association ≠ cause. Confounders, selection bias, and reverse causation produce convincing-but-false
relationships. Causal claims need a causal design (randomization, natural experiment, or an explicit
identification strategy) — not a regression coefficient.

## Experiment rigor
A/B tests answer causal questions only when they're designed right: a real hypothesis, adequate power,
a pre-registered metric and stopping rule, randomization integrity, and guardrail metrics. Peeking and
moving the goalposts manufacture false wins.

## Reproducibility + honesty
An analysis you can't reproduce is an anecdote. Version data, code, and assumptions; make the path from
raw data to claim auditable. State what the data *can't* tell you as clearly as what it can.

## Related
- applies-in ← [[lead-data-scientist]]
