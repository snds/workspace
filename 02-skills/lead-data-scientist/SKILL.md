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
spec_version: "2.0"
prerequisites: [data-foundations]
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
| `ds-ml-engineering` | Production ML systems, model lifecycle, MLOps, feature stores, serving, monitoring | Building or debugging a production model, discussing feature stores, model drift, train-serve skew, shadow deployments, model cards, CI/CD for ML |
| `ds-experimentation` | A/B testing, causal inference, power analysis, experiment platforms, variance reduction | Designing an experiment, interpreting test results, causal inference without randomization, CUPED, switchback tests, p-value questions |
| `ds-product-analytics` | Funnel analysis, retention, cohort analysis, LTV, behavioral segmentation, self-serve analytics | AARRR metrics, retention curves, churn cohorts, LTV modeling, feature adoption, engagement scoring, BI tool vs. data product decisions |
| `ds-nlp-llm` | NLP pipelines, embeddings, RAG, LLM integration, classification at scale, evaluation | Text classification, semantic search, RAG architecture, LLM cost optimization, prompt engineering at scale, PII handling, LLM evaluation |
| `ds-forecasting` | Time series modeling, demand/churn forecasting, anomaly detection, evaluation metrics | Revenue or usage forecasting, churn survival models, anomaly alerting, time series decomposition, model selection for forecasting |
| `ds-data-engineering` | Analytical pipeline architecture, dbt, orchestration, warehouse design, data quality, streaming | dbt project design, pipeline orchestration, warehouse schema, data quality frameworks, streaming vs. batch tradeoffs, schema evolution |
| `ds-executive-storytelling` | Translating analysis into decisions, data narratives, insight communication, uncertainty handling | Preparing executive briefings, dashboard design, communicating uncertainty to non-technical stakeholders, structuring a recommendation from analysis |
| `ds-prompt-engineering` | Prompt engineering as a craft — system prompt architecture, few-shot design, output format contracts, evaluation harnesses, CoT/ReAct patterns, RAG prompts, agentic prompt patterns, cost/latency optimization | System prompt design, few-shot selection, JSON schema enforcement, prompt A/B testing, chain-of-thought, prompt caching, model routing, agentic loops |
| `ds-bi-platforms` | BI tooling, semantic layer design, LookML, self-service analytics governance, embedded analytics, multi-tenant BI | Looker LookML architecture, Tableau/Metabase selection, semantic layer design, row-level security, embedded analytics, fanout bugs, certified metrics governance |
| `ds-data-governance` | Data classification, catalog design, lineage, data quality frameworks, retention policies, access governance, stewardship models | PII classification, data catalog, column-level lineage, dbt/Great Expectations quality, retention by regulation, GDPR erasure, RBAC for data platforms, data mesh |

### Spoke Loading Protocol

**Step 1**: Match the user's question against the Spoke Manifest above. Identify 1–2 directly relevant spokes.

Common routing patterns:

- **Production model going to staging/prod**: `ds-ml-engineering`
- **"Did this launch work?" / experiment readout**: `ds-experimentation`
- **Retention curve, funnel drop, churn cohort**: `ds-product-analytics`
- **Text/LLM feature being built**: `ds-nlp-llm`
- **Revenue or churn forecast**: `ds-forecasting`
- **Pipeline architecture, dbt, data warehouse**: `ds-data-engineering`
- **Executive presentation, board deck, metric framing**: `ds-executive-storytelling`
- **Causal inference without an experiment**: `ds-experimentation`
- **Model monitoring / drift alert**: `ds-ml-engineering`
- **Multi-tenant analytics isolation**: `ds-data-engineering` + `ds-product-analytics`
- **ML feature powering a SaaS product capability**: `ds-ml-engineering` + `ds-nlp-llm` (if NLP)
- **End-to-end analytical project**: load spokes incrementally as each phase is reached

**Step 2**: Load identified spoke(s) from the workspace:
```
[workspace root]/02-skills/[skill-name]/SKILL.md
```

**Step 3**: If the conversation shifts domains mid-session, load the appropriate spoke then — not preemptively.

**Never load all 7 spokes at once.** A focused question needs 1–2 spokes.

---

## Core Principles — Shared Across All DS Work

These apply regardless of which spokes are active. They are the lens through which all
technical decisions get evaluated.

### 1. Start with the business question, not the model

Every DS engagement should begin with: *What decision does this analysis need to support?*
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
Enterprise DS work surfaces to executives who want business answers, not model metrics.
"The model achieved 0.87 AUC" is rarely the right output. "We expect to identify 80% of
accounts likely to churn in the next 90 days, giving CS 3 months to intervene, with a
false positive rate that implies ~15% of interventions will be on healthy accounts" is
what drives a business decision. Route executive communication to `ds-executive-storytelling`.

### Product Integration
DS work in enterprise SaaS increasingly integrates into the product surface itself — churn
scores driving in-app nudges, recommendation models shaping UX, NLP features as product
capabilities. Model serving reliability, latency, and API contract design are product
engineering concerns, not just DS concerns. When a model is product-integrated, route to
`ds-ml-engineering` and engage with Backend cross-links.

---

## Cross-Hub References

### DS → Product Management
- `ds-experimentation` ↔ `pm-metrics-analytics`: experiment framing, KPI definition, success criteria
- `ds-product-analytics` ↔ `pm-metrics-analytics`: shared metric definitions, funnel instrumentation requirements
- `ds-executive-storytelling` ↔ `pm-stakeholder-comms`: DS owns the analytical evidence; PM owns the recommendation framing
- `ds-forecasting` → `pm-roadmap-strategy`: churn signals, usage forecasts, adoption curves as roadmap inputs
- `ds-nlp-llm` → `pm-platform-api`: when building AI/LLM capabilities as enterprise product features

### DS → Backend
- `ds-data-engineering` → `be-relational-db`: OLTP schema context before building analytical models
- `ds-data-engineering` → `be-data-modeling`: multi-tenancy patterns, temporal data modeling from operational systems
- `ds-data-engineering` → `be-integration-patterns`: event streaming from application layer into analytical pipelines
- `ds-ml-engineering` → `be-service-architecture`: ML model serving deployed as a microservice
- `ds-ml-engineering` → `be-caching-performance`: prediction caching and latency optimization for online inference
- `ds-ml-engineering` → `be-api-design`: ML API design — prediction endpoints, model versioning in API contracts
- `ds-nlp-llm` → `be-api-design`: LLM API integration, streaming response handling
- `ds-nlp-llm` → `be-caching-performance`: prompt/response semantic caching
- `ds-nlp-llm` → `be-auth-patterns`: API key management for third-party LLM services
- `ds-experimentation` → `be-integration-patterns`: event logging infrastructure for experiment assignment and outcome tracking
- `ds-product-analytics` → `be-integration-patterns`: event instrumentation requirements
- `ds-product-analytics` → `be-relational-db`: analytical queries against OLTP data sources

---

## Enterprise DS Operating Directive

This network exists to help ship analytical and ML systems that improve real business
outcomes in enterprise SaaS products. Mathematical rigor and technical depth are the tools;
better business decisions are the deliverable. Every spoke carries its own domain depth;
this hub enforces the cross-cutting standard that rigorous methodology must also answer
the question the business is actually asking.

Never let technical sophistication substitute for business clarity. Name the model, name
the math, and name what decision it supports.

## Related
- foundation → [[data-foundations]]
