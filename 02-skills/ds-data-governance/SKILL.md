---
name: ds-data-governance
description: >
  Data governance for enterprise SaaS. Staff/principal IC level. Use this skill whenever
  the conversation touches: data classification tiers, PII identification, GDPR Article
  5, GDPR Article 17 right to erasure, HIPAA data retention, data catalog design, Apache
  Atlas, DataHub, Alation, Collibra, dbt Docs, business glossary, data lineage, column-level
  lineage, OpenLineage, impact analysis, data quality framework, completeness, accuracy,
  consistency, timeliness, validity, Great Expectations, dbt tests, Soda, data quality SLAs,
  retention policies, soft delete, hard delete, anonymization in place, access governance,
  principle of least privilege, role-based access control for data, attribute-based access
  control for data, row-level security, Snowflake row access policies, BigQuery column-level
  security, data access request workflow, just-in-time access for sensitive data, data
  stewardship model, data owners, data stewards, domain data ownership, data mesh, or any
  question about governing, cataloging, classifying, or controlling access to enterprise data.
  This skill covers governance policy and catalog design — not data pipeline engineering
  (ds-data-engineering), not warehouse or BI tooling (ds-bi-platforms), not authentication
  (be-auth-patterns).
hub: lead-data-scientist
aliases: [ds-data-governance]
spec_version: "2.0"
---

# DS: Data Governance

Data governance for enterprise SaaS at staff/principal IC level. Part of the
lead-data-scientist skill network.

---

## Domain Boundary

This skill owns **data classification, cataloging, lineage, quality, retention, access
governance, and stewardship**.

- **Data pipeline engineering, dbt, warehouse design** → `ds-data-engineering`
- **BI tool semantic layer, dashboard governance** → `ds-bi-platforms`
- **Application-level auth, API key management** → `be-auth-patterns`
- **Compliance legal strategy (not implementation)** → `pm-enterprise-gtm`
- **GDPR / privacy as product feature** → `ux-ai-product-design` (data transparency UX)

---

## Data Classification

### Classification Tiers

Data classification is the foundation. Without a classification scheme, you cannot
apply differential controls for storage, access, transmission, or retention.

| Tier | Examples | Storage | Transmission | Access |
|------|----------|---------|-------------|--------|
| **Public** | Marketing copy, public docs | Any | Any | Unrestricted |
| **Internal** | Business plans, org charts, internal metrics | Managed systems | Encrypted in transit | All employees |
| **Confidential** | Customer data (non-PII), financial results, source code | Encrypted at rest + in transit | Encrypted in transit | Need-to-know |
| **Restricted** | PII, PHI, payment card data, credentials | Encrypted at rest + in transit + key management | Encrypted in transit, DLP controls | Role-specific; audited |

**Classification schema maintenance**: The schema is a living document. Appoint an owner
(Data Governance Lead or CISO). Review quarterly. Publish to all employees via the data
catalog or intranet. Classification disputes escalate to the data owner, not to engineering.

### PII Identification and Classification

**Direct identifiers** — uniquely identify an individual on their own:
- Name, email address, phone number, government ID (SSN, passport, driver's license),
  biometric data, IP address (in many jurisdictions), account username

**Quasi-identifiers** — individually innocuous; combinable to identify an individual:
- ZIP code + date of birth + gender: the Latanya Sweeney study showed this combination
  identifies 87% of the US population
- Job title + employer + city; device fingerprint components

**Special categories under GDPR (Article 9)**:
- Racial or ethnic origin, political opinions, religious beliefs
- Trade union membership
- Genetic data, biometric data for identification purposes
- Health data, sex life or sexual orientation data
- These categories require explicit consent for processing; higher penalties for breach

**PII inventory as engineering artifact**: Every field in your data model should be
classified. This is not a one-time exercise — it must be embedded in the schema review
process. Any new column added to a production table should be classified at creation time.

### Classification in Practice

Schema-level implementation:
- Tag columns in the data warehouse with classification labels (Snowflake: Object Tagging;
  BigQuery: Policy Tags; dbt: `meta: {classification: restricted}`)
- Enforce that Restricted columns cannot be selected without role membership
- Include classification in dbt model documentation so the catalog reflects it

---

## Data Catalog Design

### What a Catalog Entry Covers

A catalog entry is the authoritative record for a data asset (table, view, dataset, API):

| Field | Description |
|-------|-------------|
| **Schema** | Table/column names, types, constraints |
| **Ownership** | Data owner (accountable), steward (responsible), producing team |
| **Classification** | Tier per column (Public / Internal / Confidential / Restricted) |
| **Lineage** | Upstream sources, downstream consumers |
| **Quality SLA** | Freshness requirement (e.g., updated within 4 hours of midnight UTC) |
| **Quality metrics** | Current null rates, uniqueness, row count trend |
| **Sample data** | Sanitized/anonymized sample for discovery without exposing real values |
| **Usage** | Query frequency, most common consumers, last accessed |
| **Tags** | Domain, subject area, compliance tags (PII, GDPR-in-scope, HIPAA) |

### Tool Landscape

| Tool | Type | Best For |
|------|------|---------|
| **dbt Docs** | Lightweight, code-integrated | Teams already on dbt; documentation as code; no standalone ops |
| **DataHub** (LinkedIn) | Open source, self-hosted | Engineering-led orgs comfortable with ops; good lineage |
| **Apache Atlas** | Open source, self-hosted | Hadoop/Hive-heavy environments; strong lineage |
| **Alation** | Commercial SaaS | Business-user-friendly; AI-driven search; enterprise governance |
| **Collibra** | Commercial SaaS | Regulatory compliance-heavy orgs; workflow and stewardship tooling |

**Default recommendation**: Start with dbt Docs as lightweight catalog + a business
glossary in Confluence/Notion. Graduate to DataHub or Collibra when: (a) the catalog
needs non-technical business users as primary consumers, or (b) compliance requires a
certified audit trail.

### The Business Glossary

The business glossary maps technical table/column names to business terms. It is the
semantic layer of the catalog.

Required glossary fields:
- **Business term** (human-readable): `Monthly Active Users`
- **Technical mapping**: `mart.user_activity.mau_count`
- **Definition**: "A user who performed at least one session in a given calendar month."
- **Owner**: who is accountable for this definition
- **Certified**: boolean — has this definition been reviewed and approved?
- **Effective date**: when this definition became official
- **Change log**: history of definition changes

**Governance workflow**: Any change to a certified business term triggers a review cycle
(steward review + owner approval) before the change is published. This prevents silent
redefinition of metrics.

---

## Data Lineage

### Why Lineage Matters

Three operational use cases that justify the investment:

**Impact analysis**: "If we change the source `orders` table schema, what breaks?" With
column-level lineage, you can enumerate: every dbt model that reads `orders.revenue`,
every downstream view, every dashboard tile, every API endpoint. Without lineage, the
answer is "grep the codebase and hope."

**Root cause analysis**: "Why is the `mrr` metric wrong on the dashboard?" With lineage,
you trace: dashboard pulls from `mart.mrr_monthly`, which is built from `stg.subscriptions`,
which reads from `raw.stripe_invoices`. You can isolate which layer introduced the error.

**Compliance**: "Where did this customer's email address come from, and who has accessed it?"
Lineage provides the provenance chain required for GDPR data subject access requests
and breach impact assessment.

### Column-Level vs. Table-Level Lineage

Table-level lineage (A feeds B) is the minimum. Column-level lineage (the `revenue` field
in table B comes from the `amount` field in table A, transformed by `SUM(amount) * 0.9`)
is what you need for root cause analysis and impact analysis.

Column-level lineage requires either:
- Parsing SQL `SELECT` statements to extract field-level provenance (what DataHub, dbt,
  and Apache Atlas do)
- Instrumentation in the transformation code (OpenLineage SDK)

### Tools

| Tool | Lineage Level | Integration |
|------|--------------|-------------|
| **dbt lineage graph** | Table + column level (for dbt models) | Native in dbt Docs; free |
| **OpenLineage** | Table + column level | Open standard; emitters for Spark, Airflow, dbt, Flink |
| **DataHub** | Table + column level | Ingests OpenLineage; native connectors for most warehouses |
| **Apache Atlas** | Table + column level | Hadoop ecosystem native; less coverage for cloud warehouses |
| **Collibra Lineage** | Table + column level | Commercial; broadest connector coverage; enterprise audit |

**Default**: Use dbt's native lineage for dbt-managed models. Add OpenLineage emitters
for Spark/Airflow jobs. Ship both to DataHub as the unified lineage store if the
organization needs a single catalog+lineage surface.

---

## Data Quality Framework

### The Five Dimensions

| Dimension | Definition | Example Failure |
|-----------|-----------|----------------|
| **Completeness** | Required fields are populated | `user_id` NULL on 15% of rows in events table |
| **Accuracy** | Values reflect real-world state | `revenue` field contains negative values from refund bug |
| **Consistency** | Same entity has same values across systems | `customer.status = "active"` in CRM but `subscription.active = false` in billing |
| **Timeliness** | Data arrives within the required freshness window | Daily batch pipeline ran 3 hours late; dashboard shows yesterday's data |
| **Validity** | Values conform to the defined domain/schema | `email` field contains free-text notes instead of email addresses |

### Profiling as the Baseline

Before writing quality rules, profile the current state:
- Null rates per column
- Uniqueness rates for expected-unique fields
- Value distributions for categorical fields (unexpected categories = validity issues)
- Row count trends over time (sudden drops or spikes = upstream failures)
- Min/max/p25/p50/p75/p95 for numeric fields

**Tools**: dbt's `dbt-profiler` package, `great_expectations` for profiling, Soda's
`scan` for distribution statistics. Profiling results should be stored and trended —
a drift in null rate is more informative than a static measurement.

### Quality Enforcement Tools

| Tool | Mechanism | Integration |
|------|-----------|------------|
| **dbt tests** | YAML-defined tests on dbt models; `not_null`, `unique`, `accepted_values`, `relationships` | Native to dbt; runs in CI pipeline on model build |
| **Great Expectations** | Python expectation library; expectation suites on DataFrames or SQL tables | Flexible; integrates with Airflow, Spark, dbt |
| **Soda** | SQL-based quality checks; `soda scan`; SodaCL DSL | Strong for warehouse-native checks; SaaS monitoring dashboard available |
| **dbt-expectations** | dbt package extending built-in tests with GE-style expectations | Best of both if already on dbt |

**Quality checks in CI**: Run dbt tests on every pull request that modifies a model.
Quality failures block merge. This is the gate that prevents bad data from reaching production.

### Data Quality SLAs

A freshness SLA ("this table is updated within 4 hours of midnight UTC") is a contract,
not a goal. Operating requirements:

- Monitor freshness continuously (query `MAX(updated_at)` on a schedule)
- Alert on breach before stakeholders notice (not after a dashboard complaint)
- SLA breach is an incident, not a metric — it gets a postmortem if it breaks an
  external commitment
- SLAs must be achievable given pipeline capacity and upstream source SLAs; don't
  commit to 1-hour freshness if the source system delivers data every 6 hours

---

## Retention Policies

### Regulatory Requirements by Data Type

| Data Type | Regulation | Minimum Retention | Maximum Retention |
|-----------|-----------|------------------|------------------|
| Financial records | SOX, SEC Rule 17a-4 | 7 years | — |
| Healthcare records | HIPAA | 6 years (state laws may be longer) | — |
| Personal data (EU residents) | GDPR Article 5(1)(e) | No minimum; retain only as long as necessary for stated purpose | Purpose-limited |
| Audit logs | SOC 2, ISO 27001 | 1 year typical; 7 years for financial audit logs | — |
| Backup data | — | Per business continuity policy | Align with personal data retention |

**Storage limitation principle** (GDPR Article 5(1)(e)): Personal data must not be kept
longer than necessary for the purpose for which it was collected. This requires:
- A documented purpose for each data collection
- A defined retention period for each purpose
- A mechanism to delete or anonymize data when the period expires

### Deletion and Anonymization Spectrum

| Approach | What it does | When to use |
|----------|-------------|------------|
| **Hard delete** | Row permanently removed from storage | When regulatory or contractual requirement demands irreversibility |
| **Soft delete** | Row flagged `deleted_at = now()` but still present | When you need to retain the record for audit or restore; PII must still be purged on schedule |
| **Anonymization in place** | PII fields replaced with NULL or a non-reversible hash | When the record's aggregate/statistical value must be retained but the individual must not be identifiable |
| **Pseudonymization** | PII replaced with a consistent token; mapping held separately | When re-identification might be needed for specific authorized purposes (support, legal hold) |

**Critical distinction**: GDPR's right to erasure (Article 17) cannot be satisfied by
soft delete alone. Soft delete still stores the PII. Erasure requires either hard delete
of the row or anonymization of all personal data fields. The audit log of the deletion
event itself may be retained (without PII content).

### Right to Erasure — Implementation Patterns

GDPR Article 17 requires deletion of a data subject's personal data upon request,
within 30 days.

**Cascade delete pattern**:
1. Identify all tables containing the user's personal data (requires PII inventory)
2. Delete or anonymize in reverse dependency order (child tables first, parent last)
3. Write a deletion record to an audit log (event: erasure requested, timestamp, user ID hash — not PII)
4. Verify deletion via a post-delete query against all affected tables

**Anonymization-in-place pattern**:
- NULL all direct PII fields (`email = NULL`, `name = NULL`, `phone = NULL`)
- Replace quasi-identifiers with bucketed values (`zip_code = LEFT(zip_code, 3)` or NULL)
- Retain aggregate/behavioral data (session counts, feature usage) as it is no longer personal data

**Backup consideration**: If the user's PII exists in a database backup, erasure from live
systems is insufficient. Options: (a) delete backups older than the erasure request date
on a rolling basis, (b) document that backup retention is time-bounded and will achieve
erasure by its expiry, (c) for enterprise contracts with strict requirements, use backup
encryption with key deletion.

---

## Access Governance

### Principle of Least Privilege for Data

Every user, service account, and application should have access to exactly the data it
needs for its current function — no more, no wider, no longer.

**Common violations**:
- Analysts have SELECT on all tables including Restricted-tier
- Service accounts have warehouse admin because "it was easier to set up that way"
- Former employees' data access not revoked (access review gap)
- Overly broad data access granted once and never reviewed

### Role-Based vs. Attribute-Based Access Control

| Model | Mechanism | Use When |
|-------|-----------|---------|
| **RBAC** | Roles assigned to users; roles granted to tables/columns | Most data platforms; simpler to manage; works for stable access patterns |
| **ABAC** | Access based on attributes of the user + data + environment | Complex data access rules (time-of-day, data sensitivity + user clearance level, department + project); harder to audit |

**Enterprise default**: RBAC with a well-defined role hierarchy. ABAC for specific
high-security use cases (dynamic, context-sensitive access) where RBAC cannot express
the policy.

### Warehouse-Level Access Controls

**Snowflake**:
- Row access policies: `CREATE ROW ACCESS POLICY` scoped to roles or user attributes
- Column masking policies: mask or NULL specific columns by role
- Object-level privileges: `GRANT SELECT ON TABLE x TO ROLE analyst_role`
- Network policies: restrict access by IP range for sensitive roles

**BigQuery**:
- Column-level security via Policy Tags (Data Catalog integration)
- Row-level security via row access policies (condition expressions)
- IAM roles at dataset, table, or view level
- VPC Service Controls for network perimeter

### Data Access Request Workflow

Formal workflow prevents ad hoc access grants that bypass review:

1. **Request**: Requester submits: data asset name, justification (business purpose),
   access level needed (read/write), duration required
2. **Approval**: Data steward reviews justification against classification and
   need-to-know criteria; escalate Restricted tier to data owner + security
3. **Provisioning**: Automated where possible (Terraform for warehouse role grants,
   IGA tool for access provisioning)
4. **Access review**: Quarterly automated review of all granted access; access owners
   confirm each grant is still needed or it is revoked
5. **Revocation**: Access expires on the approved duration or on role change / departure;
   automated where possible

### Just-in-Time Access for Sensitive Data

For Restricted-tier data, permanent access grants are a risk. JIT access provides:
- **Temporary elevation**: Access granted for a defined window (4 hours, 1 day)
- **Audit log**: Every JIT grant and its usage is logged
- **Auto-expiry**: Access automatically revoked at window end; no manual revocation step required
- **Break-glass access**: Emergency elevated access with mandatory post-hoc review

Tools: AWS IAM Identity Center temporary sessions, Snowflake network policy + session
policies, HashiCorp Vault database secrets engine, Teleport for database access.

---

## Stewardship Model

### Roles

| Role | Accountable For | Typical Profile |
|------|----------------|----------------|
| **Data Owner** | Business definition, classification decisions, approval authority | VP or Director of the domain (Finance owns financial data, HR owns HR data) |
| **Data Steward** | Operational maintenance: catalog entries, quality issues, access request review, consumer questions | Senior analyst or data engineer embedded in the domain |
| **Data Consumer** | Using data correctly per its classification and purpose | Any analyst, engineer, or business user |

**The steward is not the owner.** The owner has accountability (they answer to the CISO
or DPA if data is misused). The steward has responsibility (they do the day-to-day work).
Conflating these roles leaves the operational work undone or the accountability unclear.

### Domain-Oriented Data Ownership (Data Mesh)

Data mesh decentralizes data ownership to domain teams (the team that produces the data
owns it as a product).

**When to consider**: Organization has > ~5 distinct data-producing domains; the central
data team is a bottleneck for all catalog maintenance and quality issues; domain teams
already have embedded data engineers.

**Requirements for domain ownership to work**:
- Central governance standards (classification scheme, quality SLA format, catalog entry
  schema) defined centrally and enforced consistently
- Domain teams have the capability to fulfill stewardship responsibilities
- Federated computational governance: the platform enforces standards automatically
  (not via manual review)

**When not to use**: Small organizations; immature data teams in domains; when central
coordination is genuinely efficient.

---

## Common Failure Modes

| Failure | Mechanism | Prevention |
|---------|-----------|-----------|
| Unclassified PII in production | New columns added without classification review | Embed classification in schema review process; tag at column creation |
| Catalog abandonment | Catalog entries go stale; users stop trusting it | Stewardship model with clear owners; automated freshness metrics in catalog |
| Right to erasure compliance gap | Soft delete treated as erasure; PII retained in backups | Enforce anonymization-in-place; document backup retention policy; automate deletion pipeline |
| Metric definition drift | Business glossary not updated when metric logic changes | Change-control workflow for certified terms; changelog required on update |
| Access grant never revoked | Access granted ad hoc; no expiry; no review | JIT access with auto-expiry; quarterly access review; automated off-boarding revocation |
| Quality failures invisible until stakeholder complaint | No proactive monitoring; quality checks only in CI | Runtime quality monitoring with alerting; SLA breach = incident |
| Lineage gaps at transformation boundaries | ETL outside dbt has no lineage instrumentation | OpenLineage emitters on all transformation engines; lineage coverage as a governance KPI |

---

## Cross-Hub References

- For data pipeline engineering, dbt, warehouse schema design → `ds-data-engineering`
- For BI semantic layer and dashboard governance → `ds-bi-platforms`
- For application auth and API key management → `be-auth-patterns`
- For compliance as enterprise sales and GTM motion → `pm-enterprise-gtm`
- For legal compliance considerations (a11y parallel) → `a11y-legal-compliance`

## Related
- hub → [[lead-data-scientist]]
