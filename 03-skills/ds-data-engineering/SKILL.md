---
name: ds-data-engineering
description: >
  Analytical pipeline architecture, dbt, orchestration, data warehouse design, data
  quality frameworks, and streaming infrastructure for enterprise SaaS. Use this skill
  whenever the conversation touches: dbt, dbt project structure, dbt tests, dbt
  incremental models, data contracts, pipeline orchestration, Airflow, Prefect, Dagster,
  DAG design, backfill strategy, data warehouse schema design, star schema, fact tables,
  dimension tables, slowly changing dimensions, SCD Type 1 Type 2, surrogate keys,
  multi-tenancy in the warehouse, row-level security, Great Expectations, data
  observability, Monte Carlo, Soda, data quality gates, schema evolution, schema registry,
  Avro, Protobuf, Kafka, Flink, Spark Streaming, micro-batch, streaming vs. batch
  tradeoff, or any question about designing or debugging the analytical data layer
  between operational systems and analytical consumers. This skill covers analytical
  data engineering — not OLTP schema design (be-relational-db), not ML feature
  pipeline specifics (ds-ml-engineering).
aliases: [ds-data-engineering]
spec_version: "2.0"
---

# DS: Data Engineering

Specialist lens for analytical pipeline architecture and data infrastructure in enterprise
SaaS. Part of the lead-data-scientist skill network.

---

## Domain Boundary

This skill owns **analytical data infrastructure** — the pipelines, schemas, and quality
systems that turn operational data into analytical-ready data.

- **OLTP schema design** → `be-relational-db` and `be-data-modeling`
- **Event streaming from application** → also engage `be-integration-patterns`
- **ML feature pipeline and feature stores** → `ds-ml-engineering`
- **BI tooling and self-serve analytics** → `ds-product-analytics`

---

## Pipeline Orchestration

### Framework Comparison

| Framework | Best For | Strengths | Weaknesses |
|-----------|----------|-----------|-----------|
| Apache Airflow | Established teams, large ecosystem, mature tooling | Massive community, broad operator library, good UI | Heavyweight, Python 2 legacy debt, dynamic DAGs are cumbersome |
| Prefect | Python-native modern teams, dynamic workflows | Pythonic, first-class dynamic DAGs, good local dev | Smaller ecosystem than Airflow |
| Dagster | Asset-centric thinking, software engineering standards | Asset lineage, strong typing, excellent testing story, dbt integration | Steeper learning curve, newer |

**Dagster is the forward-looking choice** for greenfield modern data stacks. Its asset-
centric model (define what you're producing, not just what runs) aligns naturally with
dbt's model-based approach and produces better lineage and data quality visibility.

For teams already on Airflow: migrate incrementally to Dagster via Airflow-to-Dagster
shims rather than full rewrites. Don't rewrite working pipelines without a forcing function.

### DAG Design Principles

- **One task = one logical unit of work**, sized to make failures cheap to retry. A task
  that does 10 things is hard to restart and hard to debug.
- **Idempotency**: re-running a DAG on the same data produces the same result. This is
  a requirement, not a preference. Non-idempotent pipelines cause data quality incidents
  on retry.
- **Backfill strategy**: every pipeline must have a defined backfill mechanism. When a
  bug fix requires reprocessing historical data, you should be able to run a date-range
  parameterized backfill without modifying the DAG code.
- **SLA monitoring**: define expected completion time per DAG; alert on SLA miss before
  downstream consumers are affected.
- **Dependency management**: use explicit task dependencies, not implicit execution order
  based on file names or schedules. Cross-DAG dependencies via sensors should be
  minimized — they create fragile implicit coupling.

---

## Transformation Layer with dbt

### Project Structure

```
models/
  sources.yml              # Source definitions and freshness checks
  staging/                 # 1:1 with source tables; light cleaning, renaming
    stg_accounts.sql
    stg_events.sql
  intermediate/            # Business logic combinations, not exposed to BI
    int_account_activity.sql
  marts/                   # Business-domain-oriented, BI-ready
    core/
      dim_accounts.sql
      fct_events.sql
    finance/
      fct_mrr.sql
    product/
      fct_feature_adoption.sql
```

**Staging layer principles**: One model per source table. Only light transformations:
rename columns to consistent conventions, cast data types, add basic derived columns
(e.g., computed timestamp). No joins. No business logic.

**Intermediate layer**: Joins, aggregations, and business logic that will be reused by
multiple mart models. Not exposed directly in BI tools. Test intermediate models as
rigorously as marts.

**Mart layer**: Denormalized, business-domain-organized, BI-ready. Optimized for query
performance. Named for the consumer (finance, product, cs) not for the transformation.

### dbt Testing

| Test Type | Purpose | Example |
|-----------|---------|---------|
| `not_null` | Column has no null values | `account_id` never null |
| `unique` | Column has no duplicates | `account_id` in dim_accounts is unique |
| `accepted_values` | Column only contains expected values | `status` in ('active', 'churned', 'suspended') |
| `relationships` | FK referential integrity between models | Every `fct_events.account_id` exists in `dim_accounts.account_id` |
| Custom generic tests | Reusable parameterized tests | Verify no future timestamps, no negative revenue |
| Singular tests | Ad-hoc SQL assertions for complex invariants | "The sum of monthly ARR must not decrease by >20% between months" |

**Treat dbt tests as data contracts**: if a test fails, downstream consumers are receiving
garbage. Failing tests in CI should block the pipeline, not be warnings.

### dbt Incremental Models

For large tables where full refresh is expensive, incremental models append or upsert
only new/changed rows.

```sql
{{ config(
    materialized='incremental',
    unique_key='event_id',
    on_schema_change='append_new_columns'
) }}

SELECT * FROM {{ source('events', 'raw_events') }}
{% if is_incremental() %}
WHERE event_timestamp > (SELECT MAX(event_timestamp) FROM {{ this }})
{% endif %}
```

**Late-arriving data**: Events that arrive with a timestamp older than the last
incremental run are silently dropped. For systems with late-arriving data, use a
`lookback_window` pattern: include data from last N days on every incremental run,
not just new data.

**`unique_key` behavior**: With `unique_key` specified, dbt performs an upsert (merge).
Without it, records are only appended. Always specify `unique_key` for event data where
records may be updated or late-arriving.

### dbt Documentation and Data Contracts

Column-level descriptions and contracts are not documentation overhead — they are the
interface specification between the transformation layer and analytical consumers.

```yaml
# contracts.yml
models:
  - name: dim_accounts
    config:
      contract:
        enforced: true  # dbt will validate column types match
    columns:
      - name: account_id
        description: "Surrogate key for the account. References fct_events.account_id"
        data_type: varchar
        constraints:
          - type: not_null
          - type: unique
```

When downstream consumers (BI tools, DS models) depend on specific columns, breaking
changes to those columns must trigger consumer notification. dbt contracts make the
dependency explicit.

---

## Data Warehouse Schema Design

### Star Schema

Core components:
- **Fact tables**: events or transactions at the lowest grain; metrics (revenue, usage
  events, support tickets). Wide rows with foreign keys to dimensions. Append-only design
  where possible.
- **Dimension tables**: entities with attributes (accounts, users, products, dates).
  Slowly changing. Optimized for filtering and grouping.
- **Surrogate keys**: system-generated integer or UUID keys for dimension tables.
  Natural keys (Salesforce ID, email) change; surrogate keys don't. Use natural keys as
  alternate keys for joining to source systems.

### Denormalized Wide Tables

For user-facing analytics or high-frequency queries, denormalized wide tables outperform
joins at query time:

- Pre-join fact + key dimension attributes into a single wide table
- Accepts storage cost in exchange for query simplicity and speed
- Document clearly which columns came from which source — lineage matters for maintenance
- Partition by `tenant_id` and `date` for typical enterprise SaaS query patterns

**Anti-pattern**: Building the entire semantic layer in the BI tool via complex joins on
normalized tables. This pushes computation into the BI layer, makes queries slow,
and makes logic hard to test or reuse.

### Slowly Changing Dimensions (SCD)

| Type | Behavior | Use When |
|------|----------|---------|
| Type 1 | Overwrite: update the current record; history lost | Low-value attributes where history doesn't matter (preferred contact preference) |
| Type 2 | Versioning: insert new row, close old row with end date; full history preserved | High-value attributes where history matters for analytics (account tier, contract value) |
| Type 3 | Prior column: add "previous_X" column; only one prior state preserved | Rare; only when exactly one level of history is needed |

**Enterprise SaaS default**: Account attributes that affect billing or analytics (contract
tier, seat count, industry vertical) should use SCD Type 2. Querying "what tier was this
account at the time of this event" requires Type 2 history.

Point-in-time correct joins using SCD Type 2:
```sql
SELECT e.*, a.account_tier
FROM fct_events e
JOIN dim_accounts_scd2 a
  ON e.account_id = a.account_id
  AND e.event_timestamp BETWEEN a.effective_from AND a.effective_to
```

### Multi-Tenancy in the Warehouse

- `tenant_id` (or `account_id`) as the first partition key on all fact tables
- Row-level security in the warehouse for any queries crossing tenant boundaries
- Aggregation queries that don't include tenant scope are almost always wrong for
  enterprise SaaS products with heterogeneous account sizes
- Warehouse-level isolation options: separate schemas per tenant (maximum isolation,
  operational overhead), shared schema with RLS (simpler operations, higher risk of
  misconfiguration)
- Cross-tenant analytics (benchmarking, cohort aggregates) must be explicitly approved
  and anonymized

---

## Data Quality Frameworks

### Great Expectations

GE defines **expectation suites** — collections of rules that a dataset must satisfy.

Integration with pipeline orchestration:
1. Define expectation suite (e.g., `accounts_staging` suite)
2. Create a checkpoint that runs the suite against fresh data
3. Run checkpoint as a task in Airflow/Dagster/Prefect after ingestion, before
   transformation dependencies run
4. On failure: block downstream tasks, alert, write failure report to data docs

Common expectations for enterprise SaaS:
- `expect_column_values_to_not_be_null` for critical keys
- `expect_column_values_to_be_between` for numeric sanity (revenue > 0, tenure_days >= 0)
- `expect_table_row_count_to_be_between` — row count drop is often the first signal of
  an ingestion failure
- `expect_column_distinct_values_to_be_in_set` for categorical enumerations
- `expect_column_pair_values_a_to_be_greater_than_b` for temporal ordering

### dbt Tests as Data Contracts

dbt tests run at transformation time. They catch:
- Upstream schema changes (new null values, type changes)
- Logic bugs introduced in transformation code
- Data quality problems that passed through ingestion

Key distinction from GE: dbt tests validate the transformed output (mart layer);
GE tests validate the raw ingested data (source layer). Both are needed.

### Data Observability Tools

**Monte Carlo, Soda, Elementary (dbt-native)** provide passive monitoring of table health
without explicit expectation authoring:

| Monitored Signal | Anomaly Detection Method |
|-----------------|--------------------------|
| Row count | ML-based anomaly detection on historical row counts |
| Null rates | Sudden increase in null % vs. historical baseline |
| Freshness | Time since last update vs. expected update cadence |
| Distribution | Statistical tests on column distributions (KS test, PSI) |
| Schema changes | DDL change detection, column addition/removal alerts |

Use data observability to catch the anomalies you didn't know to write tests for.
Use explicit dbt tests to enforce the invariants you know must hold.

---

## Streaming vs. Batch Tradeoffs

| Criterion | Batch | Micro-batch | Streaming |
|-----------|-------|-------------|-----------|
| Latency | Minutes to hours | Seconds to minutes | Sub-second |
| Complexity | Low | Medium | High |
| Cost | Low | Medium | High |
| Correctness guarantees | Exactly-once easy | Harder | Requires careful design |
| Use case | Most analytical workloads | Near-real-time dashboards | Fraud, anomaly, real-time features |

**Default to batch**. The operational complexity of streaming systems is high, and most
enterprise SaaS analytics questions don't require sub-minute data freshness.

**When streaming is justified**:
- Real-time anomaly detection on transaction streams
- ML feature computation for online inference (if features can't be pre-computed)
- Customer-facing real-time analytics where SLA requires sub-minute freshness

**Kafka + Flink/Spark Streaming**: for true streaming. Flink has better stateful stream
processing semantics and exactly-once guarantees. Spark Structured Streaming is easier
to operationalize for teams already on Spark.

**Spark Structured Streaming (micro-batch)**: processes data in micro-batches (configurable
trigger interval). Simpler programming model than Flink; slightly higher latency; good
middle ground for near-real-time with <1 minute latency requirements.

---

## Schema Evolution

Changes to source schemas break downstream pipelines. Enterprise SaaS products evolve
their data models; analytical pipelines must manage this gracefully.

### Backwards-Compatible Changes (Low Risk)
- Adding a new nullable column to a source table
- Expanding an enum's accepted values
- Increasing precision of a numeric column

Response: dbt `on_schema_change='append_new_columns'` handles this automatically for
incremental models. Add a test for the new column; update documentation.

### Breaking Changes (High Risk, Requires Coordination)
- Renaming a column that downstream models reference by name
- Changing a column's data type in a semantics-breaking way (int → string)
- Removing a column
- Changing the grain of a fact table (event-level → session-level)

Response: treat as a data contract breach. Notify all downstream consumers before the
change. Coordinate a migration window. Use column aliasing or compatibility views to
maintain both old and new schema during transition.

### Schema Registry (for Kafka Topics)

For Kafka-based event streams with Avro or Protobuf encoding:
- Schema Registry (Confluent, Apicurio) enforces schema compatibility rules
- **BACKWARD compatibility** (default): new schema can read old messages
- **FORWARD compatibility**: old schema can read new messages
- **FULL compatibility**: both; most restrictive

Compatibility rules prevent breaking schema changes from being published without explicit
compatibility checks. This is the data contract layer for streaming pipelines.

---

## Data Contracts

A data contract is an explicit agreement between an upstream producer and a downstream
consumer about what data will be produced, in what format, on what schedule, with what
quality guarantees.

Minimum contract specification:
- Schema (column names, types, nullable/not-null)
- Grain (one row per what entity/event/period)
- Update cadence and freshness SLA
- Quality guarantees (key invariants, null rates)
- Breaking change protocol (advance notice, migration path)

Without data contracts, downstream pipelines break silently when upstream systems change.
In enterprise SaaS environments with multiple teams producing data, contracts are the
interface layer between teams.

---

## Common Failure Modes

| Failure | Description | Prevention |
|---------|-------------|-----------|
| Late-arriving data silently dropped | Incremental model misses events that arrive after the incremental window | Lookback window on incremental models; monitor for late arrival patterns |
| Non-idempotent pipeline | Re-run creates duplicate rows or overwrites correct data | Test every pipeline by running it twice on the same date; results must be identical |
| No tenant isolation in aggregations | Cross-tenant averages mislead analysis | Enforce tenant_id in all analytical queries by default; code review for tenant-scoped queries |
| dbt tests treated as warnings | Schema tests fail but pipeline continues | CI/CD gate: failing dbt tests block deployment |
| Missing SCD Type 2 for key attribute | Account tier changes, but old events don't reflect the tier at the time | Audit high-value dimension attributes for SCD type appropriateness |
| Schema change breaks downstream silently | Source column renamed; dbt model fails on next run | Schema registry / data observability alerts on source schema changes before pipeline runs |

---

## Cross-Hub References

- For OLTP schema design → `be-relational-db` and `be-data-modeling`
- For event streaming from application into pipelines → `be-integration-patterns`
- For ML feature pipelines and feature stores → `ds-ml-engineering`
- For BI tooling and analytical consumers → `ds-product-analytics`
