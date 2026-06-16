---
name: ds-experimentation
description: >
  A/B testing, causal inference, experiment design, statistical power, and experiment
  platform architecture for enterprise SaaS. Use this skill whenever the conversation
  touches: A/B testing, experiment design, randomization unit, control group, treatment
  group, statistical power, Type I error, Type II error, minimum detectable effect,
  significance level, p-value interpretation, multiple testing correction, Bonferroni,
  FDR, CUPED, variance reduction, causal inference, difference-in-differences,
  regression discontinuity, instrumental variables, propensity score matching, SUTVA,
  spillover effects, novelty effect, p-hacking, switchback experiments, experiment
  platforms, assignment service, guardrail metrics, or any question about measuring
  whether an intervention caused an effect. This skill covers causal measurement —
  not model evaluation (ds-ml-engineering), not metric definition ownership (pm-metrics-analytics).
---

# DS: Experimentation

Specialist lens for A/B testing, causal inference, and experiment platform design in
enterprise SaaS. Part of the lead-data-scientist skill network.

---

## Domain Boundary

This skill owns **causal measurement** — the design, execution, and interpretation of
experiments and quasi-experimental methods.

- **Metric definition and OKR framing** → also engage `pm-metrics-analytics`
- **Event instrumentation for experiment logging** → also engage `be-integration-patterns`
- **Model evaluation methodology** → `ds-ml-engineering`
- **Descriptive product analytics** → `ds-product-analytics`

---

## Experiment Design Fundamentals

### Randomization Unit Selection

The randomization unit determines what gets randomly assigned to treatment vs. control.
Getting this wrong is a structural validity problem that no statistical correction can fix.

| Unit | Use When | Risks |
|------|----------|-------|
| User | User-level behavior change, no network effects | Cross-user spillover if users interact; wrong unit if contract is at account level |
| Account/Tenant | B2B SaaS default for account-level decisions | Smaller N; account-level variance is higher |
| Session | UI/UX experiments, stateless interactions | Same user in both arms — SUTVA violation if behavior carries over |
| Page/Request | Performance experiments, no behavioral carryover | Only valid if the feature truly has no persistent effect |
| Geography / Market | Marketplace or platform products with strong network effects | Fewer units, higher variance, difficult to scale |

**B2B SaaS default**: If the product is sold to accounts, the randomization unit should
be account, not user. User-level randomization in a multi-user account creates contamination
(users talk to each other; shared workflows create spillover).

### Pre-Experiment Power Analysis

Never start an experiment without a power analysis. It determines required sample size and
duration. Inputs required:

- **α (Type I error rate)**: Typically 0.05. The probability of declaring an effect when
  none exists. Lower α = fewer false positives, more sample required.
- **β (Type II error rate)** / **Power (1-β)**: Typically 0.80 or 0.90. The probability of
  detecting a real effect. Higher power = fewer false negatives, more sample required.
- **MDE (Minimum Detectable Effect)**: The smallest effect size the business would act on.
  This is a business decision, not a statistical one. Over-powering for tiny effects
  wastes time; under-powering means real effects go undetected.
- **Baseline metric value and variance**: From historical data. Use the same time range and
  seasonal window as the planned experiment.

Sample size formula (two-sample proportions, simplified):
```
n ≈ (z_α/2 + z_β)² × 2σ² / δ²
```
Where δ = MDE, σ² = outcome variance, z values from standard normal.

For continuous metrics: use the t-test equivalent. For ratio metrics: use the delta method.

### Control/Treatment Allocation

- 50/50 split maximizes power for a given total N. Unequal splits (10/90) reduce power but
  may be necessary when treatment is risky (security change, pricing change).
- For ramped launches (10% → 50% → 100%): the early ramp is not an experiment. If you
  want to experiment, hold a stable control group throughout.
- Never use the same users as holdout across multiple sequential experiments without
  accounting for cumulative exposure.

---

## Statistical Foundations

### Type I and Type II Errors in Product Context

| Error | Statistical Name | Business Consequence |
|-------|-----------------|---------------------|
| False positive | Type I (α) | Ship a change that doesn't actually help; waste eng resources; potentially degrade |
| False negative | Type II (β) | Don't ship a change that would have helped; miss opportunity |

The cost asymmetry between these errors should drive α and power choices. For high-stakes
changes (pricing, core feature redesign), lower α (0.01) and higher power (0.90) are
justified. For low-stakes UI tweaks, 0.05/0.80 is standard.

### Interpreting p-values Correctly

p-value = the probability of observing data this extreme or more extreme, *assuming the
null hypothesis is true*. It is not:
- The probability the null hypothesis is true
- The probability the result is due to chance
- A measure of effect size or practical significance

A statistically significant result with a trivially small effect size (p=0.001, +0.01%
conversion) is not a business signal. Always report effect size with confidence interval,
not just the p-value.

### Multiple Testing Problem

Running multiple comparisons on the same experiment inflates the false positive rate. With
20 independent tests at α=0.05, you expect 1 false positive by chance.

**FWER control** (Family-Wise Error Rate): controls the probability of *any* false positive.
- Bonferroni: α_adjusted = α/m. Simple, always valid, often too conservative.
- Holm-Bonferroni: step-down procedure, less conservative than Bonferroni while still
  controlling FWER. Prefer over Bonferroni when m is moderate.

**FDR control** (False Discovery Rate): controls the *expected proportion* of false positives
among rejected hypotheses. More power than FWER control.
- Benjamini-Hochberg (BH): sort p-values ascending; reject H_i if p_i ≤ (i/m)×q.
  Appropriate when you can tolerate some false positives but want to bound their rate.

**When to use which**:
- Confirmatory experiment (few pre-registered primary metrics): FWER (Holm)
- Exploratory multi-metric analysis: FDR (BH)
- Post-hoc subgroup fishing: apply FDR and treat results as hypothesis-generating, not
  confirmatory

---

## Variance Reduction

### CUPED (Controlled-experiment Using Pre-Experiment Data)

CUPED reduces outcome variance by removing variance explained by a pre-experiment
covariate (typically the same metric measured before the experiment started).

The adjusted outcome:
```
Y_cuped = Y - θ × (X - E[X])
```
Where X is the pre-experiment covariate, θ = Cov(Y, X) / Var(X).

This does not change the expected treatment effect — it only reduces variance. A 30–50%
variance reduction is typical with a strong pre-experiment covariate (e.g., pre-experiment
revenue for a revenue metric). This translates directly to smaller required sample size or
shorter experiment duration for the same power.

Requirements: the covariate must be available for all units before the experiment starts.
In enterprise SaaS, use prior period activity metrics (logins, feature usage, ARR).

### Stratified Sampling

Pre-stratify the randomization pool on a variable correlated with the outcome (e.g., account
tier, industry vertical, tenure cohort). Ensures treatment and control groups are balanced
on this dimension. Reduces variance when the stratum variable has a large effect on outcomes.

Can be combined with CUPED for larger variance reduction.

---

## Causal Inference Without Experiments

When random assignment isn't possible, causal inference methods can estimate treatment
effects from observational data — with explicit assumptions that must be stated and defended.

### Difference-in-Differences (DiD)

**When**: A treatment was applied to some units at a specific time, and untreated units
exist that can serve as a counterfactual.

**Identifying assumption**: Parallel trends — in the absence of the treatment, treated
and control units would have followed the same trend. This is an assumption, not a testable
fact. Partially validated by checking pre-treatment trend alignment.

**Staggered rollouts**: When treatment is applied at different times to different units
(common in SaaS feature rollouts), use Callaway-Sant'Anna or Sun-Abraham estimators —
naive two-way fixed effects DiD is biased in staggered settings.

**Anti-pattern**: Comparing treated units to a convenience sample of untreated units
without demonstrating trend alignment. This is observational comparison, not DiD.

### Regression Discontinuity Design (RDD)

**When**: Treatment assignment is determined by a continuous running variable crossing a
threshold (e.g., accounts above X seats get a feature; users above Y engagement score
get an intervention).

**Sharp RDD**: Deterministic assignment at threshold. Estimates LATE (Local Average
Treatment Effect) for units near the cutoff.

**Fuzzy RDD**: Assignment probability jumps at threshold but isn't deterministic. Requires
IV estimator at the cutoff.

**Bandwidth selection**: Use data-driven bandwidth selection (Imbens-Kalyanaraman, or the
`rdrobust` package equivalent). Wider bandwidth = more power, more bias risk. Validate with
placebo cutoffs and donut-hole robustness checks.

**Key limitation**: Estimates the effect only at the threshold. Extrapolating to units far
from the cutoff requires a strong homogeneity assumption.

### Instrumental Variables (IV)

**When**: You have a variable (instrument) that affects treatment assignment but has no
direct effect on the outcome except through the treatment.

**Conditions**:
1. Relevance: instrument is correlated with treatment (testable — F-statistic > 10 rule of
   thumb for weak instrument test)
2. Exclusion restriction: instrument affects outcome only through treatment (not directly
   testable — requires domain argument)
3. Independence: instrument is as good as randomly assigned conditional on controls

**Weak instrument problem**: If the instrument is weakly correlated with treatment (low
F-stat), IV estimates are biased toward OLS and have very wide confidence intervals.

**Enterprise SaaS applications**: Natural experiments from rollout timing, sales territory
assignment, or system-enforced feature limits.

### Propensity Score Matching (PSM)

**When**: Units self-select into treatment based on observable covariates, and you can
model the selection probability.

**Procedure**:
1. Estimate propensity score p(X) = P(Treatment=1 | X) using logistic regression or ML
2. Match treated to control on propensity score (nearest neighbor, caliper, kernel)
3. Validate covariate balance in matched sample (standardized mean differences < 0.1)
4. Estimate ATT on matched sample

**Common support**: Only valid for units where the propensity score overlap is sufficient.
Check visually and trim tails if needed.

**Critical limitation**: PSM only controls for *observed* confounders. Unobserved
confounders still bias estimates. Sensitivity analysis (Rosenbaum bounds) quantifies how
much hidden bias would overturn the result.

---

## Validity Threats

| Threat | Description | Detection / Mitigation |
|--------|-------------|------------------------|
| Novelty effect | Users behave differently just because something is new, not because it's better | Extend experiment; monitor if effect decays; wait for novelty to wear off |
| Spillover / SUTVA violation | Treatment of one unit affects outcomes of control units | Choose randomization unit to avoid network; use switchback or cluster randomization |
| Simpson's paradox in subgroups | Aggregate treatment effect is positive but effect is negative in every subgroup (due to confounded segment mix) | Pre-register subgroups; check segment allocation balance |
| p-hacking / optional stopping | Testing repeatedly and stopping when p<0.05 | Pre-register experiment duration; use sequential testing methods if early stopping is needed |
| Survivorship bias | Analyzing only users who survived long enough to be measured | Track from assignment, not from first post-treatment activity |
| Instrumentation error | The metric is measured differently in treatment vs. control due to a logging bug | Verify A/A test passes; audit logging in both arms |

---

## Switchback Experiments

For marketplace or platform products where user-level randomization creates interference
(e.g., a pricing change affects supply/demand simultaneously for all users), switchback
experiments randomize over *time periods* rather than users.

- Alternate treatment and control periods (e.g., hourly or daily alternation)
- All users are in treatment during treatment periods, control during control periods
- Eliminates user-level spillover at the cost of temporal autocorrelation
- Requires careful period length choice: long enough that carryover effects decay, short
  enough to accumulate sufficient periods for power

Analysis requires cluster-robust standard errors on time periods, not users.

---

## Experiment Platform Design

A mature experiment platform includes:

| Component | Purpose |
|-----------|---------|
| Assignment service | Deterministic, consistent unit-to-variant assignment; hash-based bucketing |
| Exposure logging | Records when each unit was first exposed to treatment, with timestamp |
| Metric computation layer | Joins assignment logs to outcome events; handles multiple randomization units |
| Guardrail metrics | Automatically monitored metrics that trigger alerts or stops if degraded (error rate, latency, revenue) |
| Automated stopping rules | Sequential testing (mSPRT, always-valid p-values) or fixed-horizon with Bonferroni correction across looks |
| Experiment registry | Tracks active experiments, metric ownership, holdout populations |

**Guardrail metrics** are not the experiment's primary metric — they are safety checks.
A checkout flow experiment might have conversion as the primary metric and revenue per
user, error rate, and page load time as guardrails. If a guardrail degrades significantly,
the experiment should be stopped regardless of primary metric performance.

---

## Cross-Hub References

- For metric definition and OKR framing → `pm-metrics-analytics`
- For event instrumentation for experiment logging → `be-integration-patterns`
- For production model launch experiments (shadow/canary) → `ds-ml-engineering`
