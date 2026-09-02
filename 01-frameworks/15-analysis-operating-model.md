# Analysis Operating Model

*The L1 domain operating model for analysis work: data science, machine learning, experimentation, product analytics, forecasting, LLM evaluation, and the evidence side of product management. Where `data-foundations` and `product-foundations` answer "what is true about reasoning from data and about building the right thing?", this framework answers "in what order do we work, what must be true before a number is allowed to influence a decision, and what disqualifies an analysis." It sits above every analysis skill. Instantiates [#13 Domain Rigor Stack](13-domain-rigor-stack.md) for the analysis cluster.*

---

## The core conviction

**An analysis is a decision instrument, not a demonstration. The question and its decision owner come before the method, and the validity of the estimate comes before the story told about it.**

Two orderings carry the whole framework:

1. **Question before method.** Start from the decision that will be made, who makes it, and what result would change it. A method chosen before the question is a search for something interesting, and it will find something whether or not it is real.
2. **Validity before narrative.** An estimate earns its place in a slide only after its identification, data, and uncertainty are defensible. A clean story built on an invalid estimate is worse than no story, because it is persuasive.

Corollary that gets violated constantly: a number without an interval is a half-truth, and a chart without a decision owner is decoration.

---

## When this framework invokes

Default-active for any analysis, metric, experiment, model, forecast, dashboard, evaluation, or "what does the data say" request. It also fires when a product or design argument leans on a quantitative claim, because the claim inherits these gates regardless of who cited it.

Load at minimum with [#04 Research & Evidence](04-research-and-evidence-framework.md), which owns the confidence tiers and the advocacy calibration this framework's outputs are named against, and [#06 QA Operating Model](06-qa-operating-model.md) for the pre-output honesty gate. Load [#11 Anticipatory Failure Analysis](11-anticipatory-failure-analysis.md) when the deliverable is a visual encoding, because charts have classic failure modes like any other technique.

Foundations: `data-foundations` and `product-foundations`. Hubs: `lead-data-scientist`, `lead-product-manager`. Depth: `ds-*` and `pm-*` spokes.

---

## 1. Decision frame (before any data is touched)

Four answers, written down, in the analysis brief or at the top of the notebook:

| Question | Why it gates the work |
|---|---|
| **What decision does this serve?** | An analysis with no decision has no success criterion and no natural stopping point |
| **Who owns that decision?** | A named person or role, not "the team". Unowned analysis becomes an unread dashboard |
| **What result would change the decision?** | Forces a falsifiable frame and exposes analyses whose every outcome leads to the same action |
| **What is the decision deadline and reversibility?** | Sets the rigor budget. A reversible weekly call and an irreversible platform bet do not deserve the same method |

If every possible result leads to the same action, stop and say so. That is a finding, and it is cheaper than the analysis.

---

## 2. The pipeline (ordered stages)

Each stage has an exit condition. Skipping one is allowed only by naming which one and why.

| Stage | The question | Artifact | Exit condition |
|---|---|---|---|
| **1 · Question** | What decision, whose, and what would change it? | Analysis brief (or the four answers above) | The question is falsifiable and the owner is named |
| **2 · Data contract** | Where does this data come from, what does one row mean, and what is missing? | Data contract note: source, grain, freshness, metric definitions, known gaps | Provenance and grain are stated; profiling done before modeling |
| **3 · Method** | What is the cheapest method that can answer this question at this rigor budget? | Method statement with the claim class it licenses | Method is matched to the claim (descriptive, comparative, causal, predictive) |
| **4 · Validity check** | What would make this wrong, and did I check it? | Validity notes: assumptions, diagnostics, sensitivity, guardrails | Every gate in §5 that applies is satisfied or explicitly waived |
| **5 · Decision artifact** | What should the owner do, with how much confidence? | Decision memo, readout, or instrumented dashboard with an owner | Recommendation, uncertainty, evidence tier, and the conditions that would reverse it |

Stage 2 is where analyses fail most often and most invisibly. Most "the model was wrong" post-mortems are data-generation misunderstandings: a metric redefined mid-window, a join that silently duplicated rows, an event that stopped firing on one platform.

---

## 3. Data contract (stage 2 in detail)

Before analysis, state:

- **Provenance.** Which system produced this, by what process, and for what original purpose. Data collected for billing behaves differently from data collected for product telemetry.
- **Grain.** What exactly one row represents. Ambiguous grain is the root of most double counting.
- **Population and coverage.** Who is in, who is excluded, and whether exclusion correlates with the outcome. Survivors, opt-ins, and instrumented-platform-only users are not the population.
- **Metric definitions.** The exact filter, window, and denominator. A metric without a definition is a name that different people compute differently.
- **Freshness and stability.** Lag, late-arriving events, backfills, and whether history gets rewritten.
- **Known gaps.** What this data cannot answer, stated before someone asks it to.

Profile before you model: row counts over time, null rates, cardinality, duplicate keys, distribution shifts at deploy boundaries. A silent instrumentation break looks exactly like a behavior change.

---

## 4. Method ladder (name what the method can claim)

Choose the cheapest rung that answers the question, and never let the writeup claim a rung above the method.

1. **Descriptive.** What happened, to whom, when. Licenses description only, never "because".
2. **Comparative or correlational.** Groups differ, variables move together. Licenses association and hypothesis generation.
3. **Quasi-experimental.** Difference-in-differences, interrupted time series, matching, synthetic control, with an explicit identification strategy and its assumptions. Licenses a conditional causal claim if the assumptions are stated and probed.
4. **Randomized experiment.** Licenses a causal claim for the tested population, the tested variant, and the tested duration.
5. **Predictive model.** Licenses a forecast with an error bar against a stated baseline. Prediction is not explanation, and feature importance is not a causal effect.
6. **Generative or LLM-based evaluation.** Licenses a graded capability claim only against a held-out set with a written rubric and measured agreement with human judgment.

Between rung 2 and any causal statement sits the identification strategy. If it cannot be written in one sentence, the analysis is at rung 2 no matter how sophisticated the model.

---

## 5. Done-gates by work type

"Ready for review" means the gates for the touched work type are satisfied or explicitly waived with a reason.

### Experiments and A/B tests
- **Pre-registered** primary metric, hypothesis, minimum detectable effect, power calculation, and stopping rule, written before exposure starts.
- Guardrail metrics declared up front (latency, error rate, revenue, support contacts, churn-adjacent behavior).
- Randomization integrity checked: assignment balance, sample ratio mismatch test, no leakage across arms, correct unit of randomization for network or team-based products.
- No peeking against a fixed-horizon test. Sequential or Bayesian monitoring is allowed only when the method was chosen up front and the correction is applied.
- Multiple comparisons corrected or declared exploratory, including segment slices.
- Novelty and primacy considered for the observed window; effect stability reported, not only the endpoint.
- Result reported as an effect size with an interval and a practical-significance judgment, not as "significant" alone.

### Product analytics and metrics work
- Metric definition, instrumentation source, and known coverage gaps stated with the number.
- Instrumentation validated end to end before the number ships: event fires, payload correct, dedupe correct, platform parity checked.
- Segment claims are pre-specified or labeled exploratory.
- Trend claims survive a seasonality and release-boundary check.

### Forecasting
- Backtested against a naive baseline (last value, seasonal naive). A model that cannot beat the baseline is a finding, not a deliverable.
- Prediction intervals reported, and the evaluation window matches the decision horizon.
- Regime changes and structural breaks named, since a model fit across a break forecasts a world that ended.

### ML models
- Leakage check on features: nothing available only after the label exists.
- **Train/serve skew check:** identical feature computation and identical categorical handling in training and serving, verified against a real serving path rather than assumed.
- Held-out evaluation with a split that respects time and entity boundaries, no tuning on the test set.
- Metrics matched to the decision, with calibration reported where a probability drives a threshold.
- Performance reported per meaningful segment, since aggregate accuracy hides subgroup failure.
- Monitoring plan for drift and a stated retraining or rollback trigger before deployment.

### LLM and generative evaluation
- **Held-out evaluation set** with a written rubric, built and frozen before iteration begins. Prompt iteration on the eval set converts it into a training set.
- Agreement between the automated judge and human judgment measured on a sample, with the disagreement pattern described.
- Contamination considered: whether the eval items plausibly appear in training data.
- Non-determinism handled: repeated runs and variance reported, not a single lucky sample.
- Failure taxonomy reported alongside the aggregate score, because a mean hides the modes that matter.

### Dashboards and recurring reporting
- **A named decision owner and a stated decision cadence.** No owner, no dashboard.
- Every metric carries its definition, refresh cadence, and source, visible where the metric is read.
- A retirement condition: what makes this dashboard obsolete and who turns it off.
- Encoding reviewed for honesty: axis baselines, aggregation, dual axes, part-to-whole misuse. Route to `infod-*` and [#11](11-anticipatory-failure-analysis.md) for chart failure modes.

---

## 6. Communicating uncertainty (non-optional)

- Report the **effect size and its interval**, then the practical significance, and only then the statistical verdict.
- Name the **evidence tier** from [#04](04-research-and-evidence-framework.md) explicitly (evidenced, industry-supported, single high-value, expert judgment, preference), and calibrate advocacy to it.
- State what the analysis **cannot** conclude in the same breath as what it can, positioned where a skimming reader will see it.
- Distinguish "no effect detected" from "no effect", and report the interval that shows which one the data supports.
- Make the analysis **reproducible**: versioned query or code, versioned data snapshot or as-of timestamp, and stated assumptions. An analysis nobody can rerun is an anecdote with a chart.

---

## 7. Absolute bans

- **P-hacking in any form.** Peeking on a fixed-horizon test, stopping when it turns positive, swapping the primary metric after seeing results, mining segments and reporting the winner as confirmatory, or dropping inconvenient outliers without a pre-stated rule.
- **A dashboard or recurring report with no decision owner.** Unowned reporting is cost with no counterparty.
- **An LLM or model evaluation without a held-out set.** Scores from data the system was iterated against are self-report, not evaluation.
- **Causal language on associational evidence.** "Drove", "caused", "lifted", and "because" require rung 3 or above with the identification strategy stated.
- **A point estimate with no uncertainty** presented as a basis for a decision.
- **Undocumented metric redefinition.** Changing a definition and comparing across the change without saying so manufactures a trend.
- **Training on the test set**, including the softer versions: tuning on it, selecting a prompt against it, or reusing it after it leaked into iteration.
- **An analysis whose conclusion was written first.** If the recommendation predates the estimate, this is advocacy and must be labeled as such.
- **Generic plugin data-science doctrine overriding this framework.** Installed packs supply method depth behind a workspace wrapper; when they contradict these gates, these gates win.

---

## 8. Operating sequence

1. **`frame`** · write the decision frame: decision, owner, what would change it, deadline and reversibility.
2. **`contract`** · state provenance, grain, population, metric definitions, freshness, gaps. Profile the data.
3. **`design`** · choose the method rung and, for experiments, pre-register metric, MDE, power, stopping rule, and guardrails.
4. **`analyze`** · execute reproducibly: versioned code, versioned data reference, stated assumptions.
5. **`validate`** · run the §5 gates for the work type; probe assumptions and run the sensitivity that would break the claim.
6. **`decide`** · produce the decision artifact: recommendation, effect and interval, evidence tier, limits, reversal conditions.
7. **`instrument`** · if the decision recurs, hand off a monitored metric with an owner and a retirement condition.
8. **`audit`** · measured review of an existing analysis, model, or dashboard against these gates. Without diagnostics it is `critique`, not `audit`.

---

## 9. How consumers use this framework

| Consumer | What it takes from here |
|---|---|
| `lead-data-scientist` | The full pipeline and the ML, experiment, forecasting, and LLM-eval gates; routes to `ds-*` spokes |
| `ds-experimentation` | Pre-registration, randomization integrity, peeking and multiple-comparison bans |
| `ds-product-analytics` | Data contract, metric definition discipline, instrumentation validation, dashboard ownership gate |
| `ds-ml-engineering` | Leakage, train/serve skew, held-out evaluation, calibration, drift monitoring and rollback triggers |
| `ds-nlp-llm` and `ds-prompt-engineering` | Held-out eval set, rubric, judge-human agreement, contamination and non-determinism handling |
| `ds-forecasting` | Baseline comparison, prediction intervals, regime-break handling |
| `ds-executive-storytelling` and `infod-*` | Validity before narrative, uncertainty in the visual, encoding honesty |
| `lead-product-manager` and `pm-metrics-analytics` | Decision frame, evidence tier naming, and the ban on causal language over associational evidence |
| `pm-discovery-research` | Question-before-method discipline for qualitative evidence, and honest population statements |
| `ds-data-governance` and `ds-data-engineering` | The data contract as the upstream deliverable this framework depends on |

Project-scoped analysis records its frame and contract in the repo or project folder, and ships its evidence in a form Sean can verify without rerunning the notebook, per the Proofboard standard in the delivery playbooks.

---

## Relationship to other frameworks

| Framework | Role relative to #15 |
|---|---|
| #03 Collaboration & Critique | How a contested finding is argued and how disagreement is recorded |
| #04 Research & Evidence | Owns the confidence tiers and advocacy calibration this framework names its outputs against |
| #06 QA Operating Model | Pre-output gate: target reader, coverage, honesty, medium match |
| #11 Anticipatory Failure Analysis | Chart and encoding failure modes before the visual is built |
| #13 Domain Rigor Stack | The meta-model this framework instantiates as analysis's L1 |
| #14 Engineering Operating Model | Instrumentation, event contracts, and model-serving paths this framework depends on |
| `data-foundations` | Data quality, uncertainty, causation, experiment rigor, reproducibility |
| `product-foundations` | Outcomes over output, the four risks, evidence over opinion |

---

## Skills that carry the mechanics

- `data-foundations` · statistical reasoning, causation, experiment rigor, reproducibility
- `product-foundations` · outcomes, jobs to be done, the four risks, prioritization
- `lead-data-scientist` + `ds-*` · experimentation, analytics, ML, forecasting, NLP/LLM, BI, governance, data engineering
- `lead-product-manager` + `pm-*` · discovery, metrics, roadmap, platform, GTM, stakeholder communication
- `lead-information-designer` + `infod-*` · encoding theory, statistical viz, dashboard patterns, narrative design
- `ux-research-synthesis` · qualitative synthesis feeding the same decision frame
- Delivery playbooks · audience contract, data and charts medium, the Proofboard standard

---

## Operating habits

- Name the decision and its owner before opening the data.
- State the grain of one row out loud; most double counting dies there.
- Pre-register before exposure, or accept that the result is exploratory and say so.
- Match the claim to the method rung, and never upgrade the verb in the summary.
- Report the interval, the practical significance, and the evidence tier together.
- Say what the analysis cannot answer, in the readout, not in a footnote.
- Close with the decision: what to do, how confident, and what would reverse it.

---

## Related

- [[13-domain-rigor-stack]]
- [[04-research-and-evidence-framework]]
- [[06-qa-operating-model]]
- [[11-anticipatory-failure-analysis]]
- [[14-engineering-operating-model]]
- [[data-foundations]]
- [[product-foundations]]
- [[lead-data-scientist]]
- [[lead-product-manager]]
