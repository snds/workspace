---
name: ds-ml-engineering
description: >
  Production ML systems, model lifecycle management, MLOps, and serving infrastructure
  for enterprise SaaS. Use this skill whenever the conversation touches: model training
  pipelines, model deployment, feature engineering, feature stores, online vs. batch
  inference, streaming inference, model monitoring, data drift, concept drift, prediction
  drift, model registry, MLflow, Weights & Biases, model versioning, reproducibility,
  CI/CD for ML, shadow mode deployments, canary releases for models, train-serve skew,
  model cards, production evaluation, MLOps platform design, or any question about taking
  a model from research/notebook to production and keeping it healthy there. This skill
  covers production ML engineering — not experiment design (ds-experimentation), not
  analytical use of models (ds-product-analytics), not NLP-specific pipelines (ds-nlp-llm).
---

# DS: ML Engineering

Specialist lens for production ML systems in enterprise SaaS. Part of the lead-data-scientist
skill network.

---

## Domain Boundary

This skill owns **production ML engineering** — the systems, practices, and operational
patterns that take models from research to production and keep them healthy there.

- **Experiment design and causal inference** → `ds-experimentation`
- **NLP/LLM-specific pipelines** → `ds-nlp-llm`
- **Model serving as a microservice** → also load `be-service-architecture`
- **Prediction caching / latency** → also load `be-caching-performance`
- **ML API contract design** → also load `be-api-design`
- **Analytical pipeline and data warehouse** → `ds-data-engineering`

---

## Model Development Lifecycle

Each transition is a gate. Treat it as one.

```
Research → Training → Evaluation → Staging → Production → Monitoring
    |            |          |           |          |            |
  [Framing    [Data      [Eval      [Shadow    [Canary     [Drift +
   gate]       gate]     gate]      gate]      gate]       health
                                                            gate]
```

### Framing Gate (Research → Training)
Before writing a line of training code, document:
- Business question and decision the model supports
- Success metric (business-level, not just ML metric)
- Cost asymmetry: what's the consequence of FP vs. FN in this context?
- Data availability and data quality assessment
- Baseline (rule-based, heuristic, or prior model) — if you don't know the baseline, you can't measure improvement

### Data Gate (Training)
Before training:
- Training data time range and rationale for the cutoff
- Label definition — is the label what the business actually cares about, or a proxy?
- Label leakage check: does any feature contain future information?
- Class balance and planned strategy (oversampling, class weights, threshold tuning)
- Point-in-time correctness for all features: would this feature value have been available at prediction time?

### Evaluation Gate (Evaluation → Staging)
Before moving to staging:
- Holdout set is temporally separated, not randomly split (for time-sensitive models)
- Evaluation on subgroups: does performance degrade for any customer segment that matters?
- Comparison against baseline
- Operating threshold set based on cost asymmetry, not default 0.5 or argmax
- Model card drafted (see below)

### Shadow Gate (Staging)
Shadow mode: new model runs alongside production model, predictions logged but not served.
- Minimum shadow period proportional to prediction cadence and business cycle
- Compare shadow predictions vs. production predictions — measure disagreement rate
- Identify high-divergence cases for qualitative review
- Validate serving latency under production load

### Canary Gate (Production entry)
- Route small % of traffic (5–10%) to new model
- Monitor business-level metrics, not just model metrics
- Define success window and abort criteria in advance
- Staged rollout: 5% → 20% → 50% → 100%, with a hold period at each step

### Health Gate (Ongoing Monitoring)
See Monitoring section.

---

## Feature Engineering and Feature Stores

### Point-in-Time Correctness (Train-Serve Skew Prevention)

**Train-serve skew** is the single most common production failure mode in ML systems. It
occurs when features available at training time differ from features available at inference
time — due to data leakage, timing bugs, or transformation inconsistencies.

Prevention checklist:
- All features must be computable from data available at prediction_time, not from any
  future data
- Training pipeline and serving pipeline should share identical transformation code — not
  parallel implementations
- Time-based features (rolling windows, lags) require a time-travel query or snapshot;
  naive joins on live tables will leak
- Test: take a historical prediction request, compute features using both pipelines,
  compare values — they should be identical

### Online vs. Offline Feature Store

| Dimension | Offline Store | Online Store |
|-----------|--------------|-------------|
| Storage | Data warehouse / data lake | Low-latency KV store (Redis, DynamoDB) |
| Use case | Training data generation, batch scoring | Real-time inference |
| Latency | Minutes to hours acceptable | <10ms required |
| Freshness | Historical, point-in-time queries | Near-real-time or live |
| Scale | Petabyte-capable | Bounded by serving tier budget |
| Examples | BigQuery, Snowflake, S3+Parquet | Redis, Feast, Tecton, Vertex AI Feature Store |

### Feature Versioning
- Features are versioned, not just models. A model trained on feature_v2 cannot be served
  with feature_v3 without revalidation.
- Feature lineage documentation: what upstream data sources produce this feature? What
  transformation logic? What's the SLA for freshness?
- Breaking feature changes (change in semantics, schema change) require a new feature
  version and a retraining plan, not a silent update.

---

## Model Serving Patterns

### Online Inference (Synchronous REST/gRPC)

Target use cases: user-facing predictions, real-time scoring, interactive features.

Key considerations:
- **Latency SLA**: Define P50/P95/P99. P99 matters for user-facing features. Budget
  inference latency as a fraction of total API SLA (e.g., if API SLA is 300ms, inference
  budget might be 50–100ms including overhead).
- **Model complexity vs. latency**: Tree ensembles (XGBoost/LightGBM) typically serve in
  1–5ms. Neural networks require GPU or careful CPU optimization for sub-50ms.
- **Serialization overhead**: gRPC with protobuf outperforms REST/JSON for high-throughput
  internal services. For external APIs, REST is standard.
- **Concurrency and autoscaling**: Model servers must autoscale independently of the
  application tier. Single-threaded Python inference is a common bottleneck.

### Batch Inference (Scheduled Scoring)

Target use cases: nightly churn scores, weekly LTV updates, campaign targeting lists.

Key considerations:
- **Freshness vs. efficiency tradeoff**: Batch scoring is cheap per prediction but
  introduces staleness. Define acceptable staleness for the use case.
- **Scale**: Spark or Dask for distributed batch scoring at scale. Single-node pandas is
  fine up to ~10M rows depending on feature computation cost.
- **Output storage**: Scored results land in the warehouse or a serving DB. Design for
  the downstream consumer — BI tool vs. API vs. application DB.
- **Backfill strategy**: New model should be able to backfill historical scores for
  comparison and evaluation.

### Streaming Inference (Event-Triggered)

Target use cases: real-time anomaly detection, fraud scoring on transactions, in-session
behavioral triggers.

Key considerations:
- **Kafka-integrated inference**: Consume events from Kafka topic, compute features on
  the stream, produce predictions to output topic.
- **Stateful feature computation**: Rolling window aggregates (last N events) require
  stateful stream processing (Flink, Spark Structured Streaming). Managing state
  correctly is hard — prefer stateless or pre-materialized features in online store
  when possible.
- **Exactly-once vs. at-least-once**: For predictions that trigger downstream actions,
  exactly-once semantics matter. Design idempotent consumers.

---

## MLOps Fundamentals

### Model Registry

A model registry (MLflow Model Registry, W&B Model Registry, Vertex AI Model Registry)
is the system of record for model artifacts, versions, and lifecycle state.

Minimum registry record per model version:
- Git SHA of training code
- Training data version / query hash
- Hyperparameters (full config, not just tuned params)
- Evaluation metrics (all relevant splits and subgroups)
- Model artifacts (serialized model, feature transformers)
- Deployment status (staging / production / archived)
- Model card link

Without a registry, model versioning is implicit and rollback is manual and risky.

### Reproducibility Requirements

A model is reproducible if: given the same training data version, code SHA, and
hyperparameters, retraining produces predictions within tolerance of the original.
Non-reproducibility sources:
- Random seed not fixed (training, data splits, dropout)
- Training data query is not deterministic (missing ORDER BY on a timestamp)
- Environment differences (library version drift)
- Floating-point non-determinism on GPU (acceptable if documented)

### CI/CD for Models

Model CI/CD pipeline stages:
1. **Unit tests**: feature transformation logic, custom metrics, data validation
2. **Integration test**: end-to-end training on a small data sample, prediction on test
   fixtures, output schema validation
3. **Evaluation gate**: automated comparison of new model vs. production baseline —
   reject if performance regresses beyond threshold
4. **Staging deployment**: automatic if evaluation gate passes
5. **Production promotion**: manual gate or automated with canary + automated health check

---

## Monitoring

Three distinct types of drift require separate detection strategies.

### Data Drift (Input Distribution Shift)
The distribution of input features has changed from training distribution.
- Detection: KS test, Population Stability Index (PSI), chi-squared for categoricals
- PSI interpretation: <0.1 no significant change; 0.1–0.2 moderate change; >0.2 major shift
- Response: investigate upstream data pipeline; if distribution shift is real (not a bug),
  consider retraining

### Concept Drift (Feature-Target Relationship Changes)
The relationship between features and the target has changed — the model's learned
function no longer reflects reality.
- Detection: tracked holdout evaluation with ground truth labels; model performance
  degradation on recent data
- Harder to detect quickly because it requires ground truth labels, which may be delayed
  (e.g., churn labels are only available after the churn event)
- Response: retrain on more recent data; consider online learning or more frequent
  retraining cadence

### Prediction Drift (Output Distribution Shift)
The distribution of model outputs has changed — even if inputs look normal.
- Detection: statistical tests on prediction score distribution over time; sudden shifts
  in mean prediction or class distribution
- Often a leading indicator of concept drift or a sign of upstream data pipeline issues
- Response: investigate; distinguish between real behavior change (expected) and
  pipeline/model bug (not expected)

### Monitoring Infrastructure Minimum Standard
- Prediction volume: are we serving the expected number of predictions?
- Prediction distribution: is the score distribution stable?
- Latency: P50/P95/P99 per endpoint
- Error rate: inference errors, feature computation failures
- Business metric correlation: is the metric the model is supposed to improve actually
  improving? (lagging indicator but most important)

---

## Model Cards

A model card is the minimum documentation standard before production. No model ships
without one.

### Required Sections

| Section | Content |
|---------|---------|
| Model description | What it predicts, who requested it, intended use cases |
| Training data | Time range, data sources, preprocessing, known limitations |
| Evaluation | Metrics on holdout, subgroup performance, comparison to baseline |
| Performance characteristics | Latency, throughput, memory footprint |
| Intended use | Approved use cases, decision it supports |
| Out-of-scope use | Uses the model was NOT designed for |
| Known limitations | Edge cases, distribution ranges, failure modes |
| Fairness evaluation | Performance across customer segments, account sizes, industries |
| Monitoring plan | Drift metrics, alerting thresholds, review cadence |
| Owners | Model owner, data owner, reviewing DS |

---

## Common Failure Modes

| Failure | Mechanism | Prevention |
|---------|-----------|-----------|
| Train-serve skew | Training and serving feature pipelines diverge | Shared transformation code; automated feature parity tests |
| Silent model degradation | Model performance decays without triggering alerts | Prediction distribution monitoring + ground-truth evaluation cadence |
| Evaluation on biased holdout | Random split instead of temporal split for time-sensitive models | Always use temporal holdout for anything with time-dependent features |
| Label leakage | Future information included in training features | Explicit point-in-time check per feature |
| Threshold at default 0.5 | Ignores asymmetric cost of FP vs. FN | Set threshold based on documented cost analysis |
| No rollback plan | Production incident with no clear path to restore prior model | Maintain prior model version in registry; document rollback procedure |
| Feature store cold start | Online store lacks a feature key at inference time | Define fallback behavior for missing features; populate store before model launch |

---

## Cross-Hub References

- For model serving as microservice → `be-service-architecture`
- For prediction caching and latency optimization → `be-caching-performance`
- For ML API design and versioning in API contracts → `be-api-design`
- For experiment design around model launches → `ds-experimentation`
- For NLP/LLM-specific model patterns → `ds-nlp-llm`
- For the data pipeline feeding training data → `ds-data-engineering`
