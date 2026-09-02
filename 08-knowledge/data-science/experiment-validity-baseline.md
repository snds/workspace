---
tags: [data-science, experimentation, evidence, methodology, validity]
created: 2026-08-03
updated: 2026-08-03
status: working
confidence: medium
sources: [03-skills/ds-experimentation/SKILL.md, 01-frameworks/15-analysis-operating-model.md, 01-frameworks/04-research-and-evidence-framework.md, 01-frameworks/11-anticipatory-failure-analysis.md, 02-shared-references/epistemic-standards.md, 02-shared-references/delivery-playbooks/05-validation-harness.md]
related_skills: [ds-experimentation, lead-data-scientist, ds-product-analytics, data-foundations]
related_projects: []
relations:
  exemplifies: ["[[15-analysis-operating-model]]"]
  relates-to: ["[[adversarial-verify-label-volatility]]", "[[silent-degradation-in-fenced-layers]]", "[[contracts-first-delivery]]"]
---

# Experiment validity baseline: decide the decision before you look at the data

## For future agent
- **TL;DR:** the workspace's standing bar for any quantitative claim, and the vault-side companion
  to [[15-analysis-operating-model]] (the L1 framework that owns the ordering). An experiment or
  analysis is only worth running if a **pre-committed decision rule** exists, and only worth
  reporting if the four validity questions are answered in order. This is doctrine assembled from
  the workspace's own skills and frameworks, not yet a record of project outcomes.
- **Key claims:**
  - *Timeless:* an analysis with no pre-committed decision rule produces a narrative, not evidence.
  - *Timeless:* stopping when a result turns significant inflates the false-positive rate; the
    stopping rule is part of the design, not a judgment call made at read time.
  - *Timeless:* the denominator, the unit of randomization, and the count of metrics inspected are
    all part of the claim. Omitting them is not simplification, it is a missing premise.
  - *Pointer:* method depth lives in [[ds-experimentation]]; evidence tiering in
    [[04-research-and-evidence-framework]]; the show-me format in the Proofboard standard.
- **As of:** 2026-08 · **Status:** current (seeded baseline, revise against real project evidence)

---

## Why this note exists

`08-knowledge/data-science/` had no entries, which meant every DS conversation restarted from the
skill's generic guidance with no workspace position on what counts as a defensible claim. The skill
tells you *how* to design an experiment; [[15-analysis-operating-model]] states the order of work
and the done-gates; this note states *what we require before believing a result*.

It is deliberately marked `working` / `confidence: medium`: it is derived from doctrine already in
the workspace, not from measured outcomes here. When a real analysis validates or breaks one of
these rules, update the specific claim and raise its confidence, rather than appending a new note.

---

## The precondition: a decision rule, written first

Before any data is pulled, write one sentence of the form:

> If the result is **X**, we will do **A**; if it is **Y**, we will do **B**.

If both branches lead to the same action, the analysis is not decision-relevant and should not be
run. This is the [[product-foundations]] test applied to measurement: discovery exists to cheaply
invalidate, and a study that cannot change the plan is output rather than outcome.

The pre-registration is short and non-negotiable: **primary metric, randomization unit, expected
direction, minimum effect worth acting on, duration, stopping rule.** Six fields. Anything decided
after seeing the data is a hypothesis for the next study, not a finding from this one.

## The four validity questions, in order

Answer them in this sequence, because a failure high up makes the ones below it moot.

1. **Construct.** Does the metric measure the thing being claimed? A proxy metric that moves for
   reasons unrelated to the mechanism is the most expensive failure, because everything downstream
   is technically correct and substantively wrong.
2. **Internal.** Is the comparison actually causal? Randomization integrity, contamination between
   arms, and interference between units belong here. Without an experiment, name the identification
   strategy explicitly (difference-in-differences, regression discontinuity, instrumental variables,
   matching) and its assumption, per [[ds-experimentation]].
3. **External.** Does it hold outside the sample and the window? Seasonality, a single-segment
   result generalized to all users, and novelty effects live here.
4. **Statistical.** Is the estimate stable? Power, variance, and multiplicity. This is last, not
   first, and it is the one most often mistaken for the whole job.

## The recurring traps

- **Peeking.** Either fix the horizon in advance or adopt a sequential method chosen in advance.
  Deciding mid-flight which of the two you are doing is the same as having no rule.
- **Uncounted multiplicity.** Every metric and every slice inspected counts, not just the one
  reported. A dashboard with thirty panels is thirty tests, and the interesting-looking panel is
  the expected outcome of looking, not a finding.
- **Unstated denominators.** A rate without its denominator, or a percentage change without its
  base, is not interpretable. State both every time.
- **Silent data corruption upstream.** A pipeline layer that degrades to empty or default makes
  "no signal" and "the mechanism broke" identical. This is the same defect documented in
  [[silent-degradation-in-fenced-layers]], and it is fatal to construct validity because the
  metric quietly stops meaning what it claims. Give the fence a side channel for *why*.
- **Reporting a volatile count as a stable score.** [[adversarial-verify-label-volatility]] is the
  workspace's own instance of this: two identical passes produced very different pass/fail tallies
  while every substantive verdict held. Report the stable substance and describe the variable part
  as variable.

## Reporting bar

Calibrate advocacy to evidence tier, and say the tier out loud: **evidenced**,
**industry-supported**, **expert judgment**, or **preference**
([[04-research-and-evidence-framework]]). "The data shows" applied to expert judgment is the most
common integrity failure in an analysis write-up, and it is invisible to a reader who was not there.

Analytical work delivered to a non-analyst ships with a **Proofboard**: the contract in plain
english, the show-me evidence, and sample data that can be re-run. See the delivery playbooks. The
reviewer should be able to check the claim without reading the query.

## Before running anything

Run the [[11-anticipatory-failure-analysis]] pass on the design: name how this specific analysis
classically fails, argue against your own plan, and derive acceptance criteria before collecting
data. Finding the flaw in the design is cheap; finding it in the write-up is not.
