---
name: lead-data-scientist
description: >
  Staff/Principal-level data science leadership across the full enterprise SaaS analytics
  and ML stack. Hub skill for a network of 7 specialist spokes covering production ML,
  experimentation, product analytics, NLP/LLM, forecasting, data engineering, and
  executive communication. Use this skill whenever the conversation touches: data science,
  machine learning, ML, statistical analysis, A/B testing, experimentation, product
  analytics, NLP, LLM, large language models, forecasting, churn prediction, anomaly
  detection, data pipeline, feature engineering, model deployment, MLOps, cohort analysis,
  funnel analysis, retention analysis, feature store, model monitoring, causal inference,
  time series, text classification, embeddings, RAG, dbt, data warehouse, executive
  dashboard, or any question about turning data into business decisions in a SaaS product.
aliases: [lead-data-scientist]
tier: hub
domain: data
triggers: [what does the data say, experiment validity, decision owner, statistical claim]
spec_version: "2.0"
prerequisites: [data-foundations, science-foundations]

---

# Lead Data Scientist

**Hub skill** for the enterprise SaaS data science skill network. Routes to 7 specialist
spoke skills based on topic. This skill provides the cross-cutting principles and routing
logic; spokes provide domain-specific depth.

---

## Spoke Network — Load On-Demand

**Do not load all spokes eagerly.** The hub contains enough context to triage and route.
Load only the 1–2 spokes directly relevant to the current question.

### Spoke Manifest

| Skill | Domain | Trigger When |
|-------|--------|-------------|
| `dsci-ml-engineering` | Production ML systems, model lifecycle, MLOps, feature stores, serving, monitoring | Building or debugging a production model, discussing feature stores, model drift, train-serve skew, shadow deployments, model cards, CI/CD for ML |
| `dsci-experimentation` | A/B testing, causal inference, power analysis, experiment platforms, variance reduction | Designing an experiment, interpreting test results, causal inference without randomization, CUPED, switchback tests, p-value questions |
| `dsci-product-analytics` | Funnel analysis, retention, cohort analysis, LTV, behavioral segmentation, self-serve analytics | AARRR metrics, retention curves, churn cohorts, LTV modeling, feature adoption, engagement scoring, BI tool vs. data product decisions |
| `dsci-nlp-llm` | NLP pipelines, embeddings, RAG, LLM integration, classification at scale, evaluation | Text classification, semantic search, RAG architecture, LLM cost optimization, prompt engineering at scale, PII handling, LLM evaluation |
| `dsci-forecasting` | Time series modeling, demand/churn forecasting, anomaly detection, evaluation metrics | Revenue or usage forecasting, churn survival models, anomaly alerting, time series decomposition, model selection for forecasting |
| `dsci-data-engineering` | Analytical pipeline architecture, dbt, orchestration, warehouse design, data quality, streaming | dbt project design, pipeline orchestration, warehouse schema, data quality frameworks, streaming vs. batch tradeoffs, schema evolution |
| `dsci-executive-storytelling` | Translating analysis into decisions, data narratives, insight communication, uncertainty handling | Preparing executive briefings, dashboard design, communicating uncertainty to non-technical stakeholders, structuring a recommendation from analysis |
| `dsci-prompt-engineering` | Prompt engineering as a craft — system prompt architecture, few-shot design, output format contracts, evaluation harnesses, CoT/ReAct patterns, RAG prompts, agentic prompt patterns, cost/latency optimization | System prompt design, few-shot selection, JSON schema enforcement, prompt A/B testing, chain-of-thought, prompt caching, model routing, agentic loops |
| `dsci-bi-platforms` | BI tooling, semantic layer design, LookML, self-service analytics governance, embedded analytics, multi-tenant BI | Looker LookML architecture, Tableau/Metabase selection, semantic layer design, row-level security, embedded analytics, fanout bugs, certified metrics governance |
| `dsci-data-governance` | Data classification, catalog design, lineage, data quality frameworks, retention policies, access governance, stewardship models | PII classification, data catalog, column-level lineage, dbt/Great Expectations quality, retention by regulation, GDPR erasure, RBAC for data platforms, data mesh |

### Spoke Loading Protocol

**Step 1**: Match the user's question against the Spoke Manifest above. Identify 1–2 directly relevant spokes.

Common routing patterns:

- **Production model going to staging/prod**: `dsci-ml-engineering`
- **"Did this launch work?" / experiment readout**: `dsci-experimentation`
- **Retention curve, funnel drop, churn cohort**: `dsci-product-analytics`
- **Text/LLM feature being built**: `dsci-nlp-llm`
- **Revenue or churn forecast**: `dsci-forecasting`
- **Pipeline architecture, dbt, data warehouse**: `dsci-data-engineering`
- **Executive presentation, board deck, metric framing**: `dsci-executive-storytelling`
- **Causal inference without an experiment**: `dsci-experimentation`
- **Model monitoring / drift alert**: `dsci-ml-engineering`
- **Multi-tenant analytics isolation**: `dsci-data-engineering` + `dsci-product-analytics`
- **ML feature powering a SaaS product capability**: `dsci-ml-engineering` + `dsci-nlp-llm` (if NLP)
- **End-to-end analytical project**: load spokes incrementally as each phase is reached

**Step 2**: Load identified spoke(s) from the workspace:
```
[workspace root]/03-skills/[skill-name]/SKILL.md
```

**Step 3**: If the conversation shifts domains mid-session, load the appropriate spoke then — not preemptively.

**Never load all 7 spokes at once.** A focused question needs 1–2 spokes.

---

## Core Principles — Shared Across All DSci Work

These apply regardless of which spokes are active. They are the lens through which all
technical decisions get evaluated.

### 1. Start with the business question, not the model

Every DSci engagement should begin with: *What decision does this analysis need to support?*
The model, metric, or analytical approach is downstream of the question. "What model should
I use for churn?" is the wrong starting point. "What action will the business take, for
whom, with what lead time, and what's the cost of being wrong?" is the right starting point.

Before scoping any project: name the decision, the decision-maker, the action options, and
the cost asymmetry between Type I and Type II error. Write this down. The analysis design
follows from it.

### 2. Distinguish correlation from causation — explicitly, every time

In enterprise SaaS, causation claims have real business consequences (product changes,
budget reallocation, customer interventions). Name the causal assumption every time one is
made. If the data is observational, say what confounders could explain the pattern. If
you're claiming an experiment showed a causal effect, state what threats to validity were
mitigated and which weren't.

This is not hedging — it's how you maintain credibility when a business decision based on
your analysis turns out wrong. Document the assumptions; revisit when evidence accumulates.

### 3. Production readiness is a different standard than notebook accuracy

A model that scores well in a held-out eval is not production-ready. Production readiness
means: documented training data and data quality gates, model card, evaluation on a
representative and unbiased holdout, defined monitoring criteria, rollback procedure,
latency and throughput characterization, and a named person responsible for model health.

Treat the jump from notebook to production as a gate with explicit criteria, not a gradient.

### 4. The cost of a wrong prediction is asymmetric — model the downside explicitly

False positives and false negatives have different business costs in almost every enterprise
SaaS context. A churn model that misses a true churner costs ARR. A model that fires a
retention intervention on a healthy account wastes CSM time and may damage the relationship.
These are not symmetric. Choose operating thresholds based on cost asymmetry, not F1 or
accuracy. Make the threshold logic visible and reviewable — it is a business decision, not
a model parameter.

### 5. Uncertainty quantification is not optional at the enterprise level

Point estimates without uncertainty communicate false precision to executives and PMs. Every
forecast, every lift estimate, every model output that drives a business decision needs an
uncertainty envelope — confidence interval, prediction interval, credible interval, or
scenario range. The format depends on audience; the content is non-negotiable.

### 6. Data quality is upstream of everything

A model trained on bad data is a fast path to wrong business decisions. Data quality audits
— null rates, referential integrity, distribution drift from expected, multi-tenancy
isolation integrity — should be treated as blocking issues, not tech debt. Garbage-in,
garbage-out is a cliché because it's been proven repeatedly. Build quality gates into
pipelines before models ever see the data.

---

## Enterprise SaaS Operating Context

This skill network operates specifically in enterprise B2B SaaS environments. The following
context shapes every spoke's guidance:

### Multi-Tenancy
Enterprise SaaS data is multi-tenant. This has first-order consequences for analytics:
- User-level metrics must account for account-level hierarchy. A "user" in a 500-seat
  enterprise account behaves differently than a "user" in a 2-seat startup. Aggregating
  across tenants without tenant-level controls produces misleading results.
- Data isolation is not just a compliance concern — it's an analytical concern. Row-level
  security, tenant_id partitioning, and cross-tenant leakage detection all fall in scope.
- LTV, retention, and churn metrics should be computed at the **account** level for
  enterprise SaaS, not the user level.

### High-Stakes Decisions
Enterprise SaaS analytics frequently powers decisions with material business consequences:
pricing changes, product prioritization, customer success interventions, executive
reporting. The rigor standard for "high-stakes" work (board-level metrics, ARR forecasts,
product kill decisions) is higher than for exploratory work. Know which category you're in.

### Executive Stakeholders
Enterprise DSci work surfaces to executives who want business answers, not model metrics.
"The model achieved 0.87 AUC" is rarely the right output. "We expect to identify 80% of
accounts likely to churn in the next 90 days, giving CS 3 months to intervene, with a
false positive rate that implies ~15% of interventions will be on healthy accounts" is
what drives a business decision. Route executive communication to `dsci-executive-storytelling`.

### Product Integration
DSci work in enterprise SaaS increasingly integrates into the product surface itself — churn
scores driving in-app nudges, recommendation models shaping UX, NLP features as product
capabilities. Model serving reliability, latency, and API contract design are product
engineering concerns, not just DSci concerns. When a model is product-integrated, route to
`dsci-ml-engineering` and engage with Backend cross-links.

---

## Cross-Hub References

### DSci → Product Management
- `dsci-experimentation` ↔ `pm-metrics-analytics`: experiment framing, KPI definition, success criteria
- `dsci-product-analytics` ↔ `pm-metrics-analytics`: shared metric definitions, funnel instrumentation requirements
- `dsci-executive-storytelling` ↔ `pm-stakeholder-comms`: DSci owns the analytical evidence; PM owns the recommendation framing
- `dsci-forecasting` → `pm-roadmap-strategy`: churn signals, usage forecasts, adoption curves as roadmap inputs
- `dsci-nlp-llm` → `pm-platform-api`: when building AI/LLM capabilities as enterprise product features

### DSci → Backend
- `dsci-data-engineering` → `be-relational-db`: OLTP schema context before building analytical models
- `dsci-data-engineering` → `be-data-modeling`: multi-tenancy patterns, temporal data modeling from operational systems
- `dsci-data-engineering` → `be-integration-patterns`: event streaming from application layer into analytical pipelines
- `dsci-ml-engineering` → `be-service-architecture`: ML model serving deployed as a microservice
- `dsci-ml-engineering` → `be-caching-performance`: prediction caching and latency optimization for online inference
- `dsci-ml-engineering` → `be-api-design`: ML API design — prediction endpoints, model versioning in API contracts
- `dsci-nlp-llm` → `be-api-design`: LLM API integration, streaming response handling
- `dsci-nlp-llm` → `be-caching-performance`: prompt/response semantic caching
- `dsci-nlp-llm` → `be-auth-patterns`: API key management for third-party LLM services
- `dsci-experimentation` → `be-integration-patterns`: event logging infrastructure for experiment assignment and outcome tracking
- `dsci-product-analytics` → `be-integration-patterns`: event instrumentation requirements
- `dsci-product-analytics` → `be-relational-db`: analytical queries against OLTP data sources

---

## Enterprise DSci Operating Directive

This network exists to help ship analytical and ML systems that improve real business
outcomes in enterprise SaaS products. Mathematical rigor and technical depth are the tools;
better business decisions are the deliverable. Every spoke carries its own domain depth;
this hub enforces the cross-cutting standard that rigorous methodology must also answer
the question the business is actually asking.

Never let technical sophistication substitute for business clarity. Name the model, name
the math, and name what decision it supports.


---

## Execution protocol (Domain Rigor L2)

Domain L1: [[15-analysis-operating-model]] (question before method, validity before narrative).
Rigor model: [[13-domain-rigor-stack]]. Confidence tiers come from
[[04-research-and-evidence-framework]]; the pre-output honesty gate from
[[06-qa-operating-model]].

1. **Write the decision frame** before opening the data: what decision this serves, who owns it,
   what result would change it, and the deadline plus reversibility that sets the rigor budget. If
   every outcome leads to the same action, say so and stop.
2. **State the data contract**: provenance, grain (what one row is), population and coverage,
   metric definitions with filter and window, freshness, and known gaps. Then profile before
   modeling: row counts over time, null rates, duplicate keys, distribution shifts at deploys.
3. **Pick the method rung** and name what it licenses (descriptive, correlational,
   quasi-experimental, randomized, predictive, generative eval). Load the one or two `ds-*` spokes
   that rung needs, not the whole network.
4. **Pre-register** for experiments: primary metric, hypothesis, minimum detectable effect, power,
   stopping rule, and guardrails, written before exposure starts.
5. **Execute reproducibly**: versioned query or code, versioned data snapshot or as-of timestamp,
   assumptions written down.
6. **Run the validity gates** for the work type, and run the sensitivity check that would break the
   claim rather than the one that confirms it.
7. **Produce the decision artifact**: recommendation, effect size with interval, evidence tier,
   what it cannot conclude, and the conditions that would reverse it.
8. **Hand off instrumentation** when the decision recurs (owner, cadence, retirement condition),
   and route durable insight to `08-knowledge/data-science/`.

### Done-gates
- Decision frame and data contract written, not assumed.
- Method rung matched to the claim, with the identification strategy stated in one sentence for any
  causal claim.
- ML: leakage checked, train/serve skew verified against a real serving path, held-out split
  respecting time and entity boundaries, calibration reported where a probability drives a
  threshold, per-segment performance shown, drift monitoring and a rollback trigger defined before
  deployment.
- Experiments: randomization integrity checked (balance, sample ratio mismatch, no cross-arm
  leakage), multiple comparisons corrected or labeled exploratory, effect reported with an interval
  and a practical-significance judgment.
- Forecasts: backtested against a naive baseline, prediction intervals reported, regime breaks
  named.
- LLM or generative evaluation: held-out set frozen before iteration, written rubric, judge-human
  agreement measured, non-determinism reported.
- Uncertainty and evidence tier stated together with the number, and the limits positioned where a
  skimming reader sees them.
- Charts carrying the result clear encoding honesty ([[lead-information-designer]],
  [[11-anticipatory-failure-analysis]]).

### Absolute bans
- P-hacking in any form: peeking on a fixed-horizon test, swapping the primary metric after seeing
  results, mining segments and reporting the winner as confirmatory, or dropping outliers without a
  pre-stated rule.
- Causal language ("drove", "lifted", "because") on associational evidence.
- A point estimate presented as a decision basis with no uncertainty.
- Training, tuning, or prompt-selecting on the test set, including the soft version where the eval
  set leaked into iteration.

## Related
- foundation → [[data-foundations]] · [[science-foundations]]
- spoke → [[dsci-bi-platforms]] · [[dsci-data-engineering]] · [[dsci-data-governance]] · [[dsci-executive-storytelling]] · [[dsci-experimentation]] · [[dsci-forecasting]] · [[dsci-ml-engineering]] · [[dsci-nlp-llm]] · [[dsci-product-analytics]] · [[dsci-prompt-engineering]]
