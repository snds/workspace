---
name: ds-bi-platforms
description: >
  Business intelligence tooling, semantic layer design, and embedded analytics for
  enterprise SaaS. Staff/principal IC level. Use this skill whenever the conversation
  touches: Looker, LookML, Explores, Views, PDT (Persistent Derived Tables), Tableau,
  Metabase, Power BI, DAX, DirectQuery, Apache Superset, SQL Lab, semantic layer design,
  metric governance, certified metrics, business glossary, BI tool selection, self-service
  analytics, governed analytics, data literacy, row-level security, column masking, embedded
  analytics, iFrame embedding, SDK embedding, JWT signed embedding, white-label BI, embedded
  dashboard performance, in-app reporting, customer-facing dashboards, multi-tenant BI,
  BI for enterprise SaaS, bring-your-own-BI, or any question about measuring and surfacing
  data to business users or embedding analytics inside a product.
  This skill covers BI tooling and embedded analytics — not data pipeline engineering
  (ds-data-engineering), not executive narrative (ds-executive-storytelling), not product
  metrics definitions (ds-product-analytics).
hub: lead-data-scientist
---

# DS: BI Platforms & Embedded Analytics

Business intelligence tooling, semantic layer design, and embedded analytics for enterprise
SaaS. Part of the lead-data-scientist skill network.

---

## Domain Boundary

This skill owns **BI tool selection, semantic layer design, self-service governance, and
embedded analytics patterns**.

- **Data pipeline engineering, dbt models, warehouse design** → `ds-data-engineering`
- **Executive narrative and presentation of data** → `ds-executive-storytelling`
- **Product metrics, funnel analysis, experimentation** → `ds-product-analytics`
- **Data catalog, lineage, classification, retention** → `ds-data-governance`
- **Information hierarchy, visual encoding** → `lead-information-designer`

---

## BI Tool Landscape and Selection

### Tool Profiles

**Looker**
- Core differentiator: LookML semantic layer is Git-backed and centralized. All metric
  definitions live in one place; dashboards are downstream consumers.
- Best for: Organizations that want governed self-service at scale; teams with SQL-capable
  analysts; centralized data governance.
- Limitations: High cost; LookML learning curve; slow dashboard renders on complex Explores.

**Tableau**
- Core differentiator: Best-in-class visual analytics; Tableau Prep for ETL; Server/Cloud
  for enterprise distribution; Hyper engine for in-memory speed.
- Best for: Exploratory analysis, ad hoc visualization, teams with business analysts who
  resist writing SQL.
- Limitations: Metric governance is weak (anyone can define a metric differently); costly
  at scale; Desktop/Server split is confusing.

**Metabase**
- Core differentiator: Low-code, open source, self-hostable. No-SQL question builder for
  non-technical users. Pro tier adds SSO, embedding, audit logs.
- Best for: Startups, internal tools, engineering-led orgs that want to self-host.
- Limitations: Limited governance features; semantic layer is primitive; embedding features
  less mature than Looker.

**Power BI**
- Core differentiator: Deep Microsoft ecosystem integration (Excel, Teams, Azure AD,
  Synapse, Fabric). DAX is powerful for complex calculations. DirectQuery for real-time.
- Best for: Microsoft shops; finance-heavy analytics; enterprises already on Azure.
- Limitations: Windows/browser-first; DAX has steep learning curve; governance requires
  Power BI Premium; embedding requires Azure AD configuration.

**Apache Superset**
- Core differentiator: Open source, SQL Lab for ad hoc SQL + chart builder, no per-seat
  cost. Community-supported connectors for most warehouses.
- Best for: Engineering-led orgs, cost-sensitive, comfortable with self-hosting and
  operational overhead.
- Limitations: Governance features limited; no native semantic layer; embedding requires
  custom implementation; production support DIY.

### Selection Matrix

| Factor | Looker | Tableau | Metabase | Power BI | Superset |
|--------|--------|---------|----------|----------|----------|
| SQL capability required | High | Low–Medium | Low | Medium (DAX) | Medium |
| Governance maturity | Best | Poor | Limited | Good (Premium) | Poor |
| Embedding maturity | Excellent | Good | Good (Pro) | Good | Limited |
| Cost | Very High | High | Low | Medium–High | Free |
| Warehouse compatibility | Excellent | Excellent | Good | Best for Azure | Good |
| Self-service UX | Good | Best | Best | Good | Moderate |

**Decision rule for enterprise SaaS**: If embedding analytics inside your product is
a product requirement and governance matters, default to Looker. If embedding is not
required and your team is data-literate, Tableau or Looker. If cost is the primary
constraint and engineering can operate the stack, Superset or Metabase.

---

## LookML Architecture

### The Three-Layer Model

**Views** (tables + fields):
- One View per logical table or derived table
- Each View defines: dimensions (descriptive attributes), measures (aggregations),
  dimension groups (dates/times)
- Views should be additive — new fields added via refinement, not original file mutation

**Explores** (join paths + access points):
- Defines what a user can query: which Views are joined, how, with what symmetry
- Each Explore is a scoped, joinable data model — the "report" starting point
- Explore proliferation is a design smell: too many Explores means join logic is not
  being shared

**Joins**:
- `type: left_outer` is the default; choose carefully — join type determines which rows
  appear in query results
- `relationship: many_to_one` must be correct or Looker cannot compute distinct counts
  correctly (fanout problem — see Semantic Layer below)
- Symmetric aggregates: Looker uses symmetric aggregate functions internally to correct
  for fanout when `many_to_one` relationships are declared correctly

### Measures and Dimensions

The measure/dimension distinction is LookML's core abstraction:
- **Dimensions** are attributes of a row: `${user_id}`, `${country}`, `${created_date}`
- **Measures** are aggregations across rows: `count`, `sum`, `average`, `count_distinct`

Derived dimensions (computed from other fields): `type: string` with `sql: CASE WHEN …`
Derived measures: `type: number` combining other measures (e.g., conversion rate = `${completed_count} / NULLIF(${started_count}, 0)`)

### Derived Tables

| Type | Mechanism | Use When |
|------|-----------|---------|
| Native Derived Table (NDT) | LookML generates SQL from Explore/view definitions | Simple aggregations built from existing LookML models |
| SQL Derived Table | Inline SQL block in View definition | Complex SQL logic not expressible in LookML fields |
| Persistent Derived Table (PDT) | Materializes query result to a scratch schema on a schedule or trigger | Expensive computations; results are reused across queries |

PDT considerations:
- Requires `datagroup` definition for refresh scheduling
- PDTs appear as real tables in the warehouse — monitor storage costs
- Incremental PDTs (BigQuery, Snowflake) can append new rows rather than full recompute

### LookML Project Structure for Large Teams

Recommended file organization:
```
/views/          — one .lkml file per source table or logical entity
/explores/       — one .lkml file per Explore (or domain grouping)
/dashboards/     — LookML dashboard definitions (version-controlled)
/refinements/    — field/explore refinements that extend base views
/extensions/     — shared extension blocks
```

**CI/CD for LookML**: Run `lookml-linter` and Looker's content validator in CI on every
pull request. Validate that no existing Explores are broken. For LookML changes that
affect downstream dashboards, run the content validator against a development instance
before merging.

---

## Semantic Layer Design

### The Semantic Layer as Single Source of Truth

The semantic layer's job is to prevent metric inconsistency — ensuring "Monthly Active
Users" means the same thing in every dashboard, for every team, at every point in time.

**What belongs in the semantic layer:**
- Metric definitions (the SQL or LookML expression + the business logic + the filter
  conditions that define the metric)
- Dimension definitions and business-friendly labels
- Join logic (relationship types, fanout behavior)
- Access control (field-level permissions)

**What does not belong:**
- Ad hoc calculations built for a single dashboard → these should be dashboard-level
  and clearly labeled "uncertified"
- Dashboard layout or visualization choices

### Metric Naming Conventions

| Convention | Rationale |
|------------|-----------|
| `[subject]_[aggregation]_[scope]` | `active_users_weekly_count` is unambiguous |
| Avoid abbreviations in user-facing names | `mau` vs. `monthly_active_users` — the former requires knowledge to interpret |
| Include time scope in name | `revenue_30d` vs. `revenue` — explicit is safer when multiple windows exist |
| Separate rate metrics from count metrics | `conversion_rate` and `conversion_count` should never share a name |

### Certified vs. Uncertified Metrics

**Certification governance workflow:**
1. Analyst or stakeholder proposes metric definition
2. Data steward reviews logic, validates against source data
3. Data owner approves business definition
4. Metric published to semantic layer with `certified: true` label (Looker: via
   `tags: ["certified"]`; dbt Metrics: `meta: {certified: true}`)
5. Uncertified copies in dashboards flagged for cleanup

**Dashboard policy**: Certified dashboards pull from certified metrics only. Sandbox
dashboards are labeled as such and excluded from operational reporting.

### Joins and Fanout

The most common BI aggregation bug: a many-to-many join that multiplies row counts,
making SUM measures incorrect.

**Classic case**: Orders joined to Order Items. Each Order has multiple Items. Joining
on `order_id` creates one row per item per order. SUM(order.revenue) now sums the
revenue once per item, not once per order.

**Detection**: Row count on the joined query exceeds expected row count. Check via
`COUNT(DISTINCT primary_key)` vs. `COUNT(*)`.

**Prevention**:
- Declare join relationships correctly (`many_to_one`, `one_to_one`, `many_to_many`)
- Looker symmetric aggregates handle this automatically for correctly declared joins
- In raw SQL: use subquery aggregation before joining, or window functions to dedup

---

## Self-Service Analytics Governance

### The Governance Spectrum

```
← Fully Governed ————————————————————————————— Fully Self-Service →
 All metrics                Certified core +          Anyone can define
 centrally defined;         approved sandbox;          any metric;
 read-only dashboards       users can explore         no guardrails
```

Neither extreme works:
- Fully governed: Data team bottleneck; stakeholders build shadow analytics in Excel
- Fully self-service: Metric proliferation; conflicting definitions; no trust in numbers

Target: **Certified core + governed sandbox** — core operational metrics are owned and
certified by the data team; users can explore and build on top of certified data with
guardrails.

### Certified Content vs. Sandbox Content

| Dimension | Certified | Sandbox |
|-----------|-----------|---------|
| Metric definitions | Reviewed + approved | Ad hoc, user-defined |
| Visible to | All users | Creator + shared viewers |
| SLA | Data team maintains | No SLA |
| Label in BI tool | "Certified" badge | "Sandbox" or no badge |
| Included in operational reports | Yes | No |

### Data Literacy Enablement

Governance fails without user capability. Enablement program requirements:
- SQL training for analysts (not optional if BI tool is SQL-based)
- "How to read a dashboard" for business users — understanding filters, date ranges,
  aggregation type
- Office hours with the data team — recurring, low-friction access
- Self-service guides: how to find the right metric, how to request a new certified metric

### Guardrails in Self-Service

**Row-level security (RLS)**: Users see only rows they're authorized to see.
- Implement at the warehouse level where possible (Snowflake row access policies,
  BigQuery column-level security + row-level auth)
- Implement at the BI layer as a fallback (Looker `access_filter`, Tableau RLS via
  calculated fields)
- Never implement RLS only in dashboard filters — users can bypass dashboard filters

**Column masking**: PII and sensitive fields masked for users without explicit access.
- Snowflake column-level masking policies by role
- Looker field-level access via `access_grants`

**Approved data sources**: Lock self-service to certified, governed datasets. Prevent
users from joining to raw or unvetted tables.

### Tracking Usage

Dashboard proliferation is silent tech debt. Track:
- View counts per dashboard (last 30/90 days)
- Unique user count per dashboard
- Last accessed date

**Quarterly cleanup process**: Dashboards not viewed in 90 days flagged for archival;
owner notified; no response = archived. Prevents "maintained but ignored" dashboards
from misleading stakeholders.

---

## Embedded Analytics Patterns

### Embedding Approaches

| Approach | Mechanism | Use When |
|----------|-----------|---------|
| iFrame embedding | `<iframe>` pointing to BI tool URL | Simplest; least control over styling and behavior |
| SDK embedding | JavaScript SDK that renders BI content in your DOM | More control; interaction with parent app; better UX |
| API-based rendering | Fetch data from BI API; render with custom visualization library | Full control; highest effort; best white-label result |

### Signed Embedding (JWT-based)

For per-user, per-dashboard access control without requiring users to log into the BI tool:

1. Backend generates a signed JWT containing: user identity, dashboard/Explore ID,
   authorized filter values (row-level scope), expiry
2. JWT is embedded in the iFrame or SDK initialization URL
3. BI tool validates the JWT signature and renders content scoped to the authorized data

**Looker signed embedding**: Uses HMAC-SHA256 signed URLs with nonce and timestamp.
Parameters include: user attributes for row-level filtering, allowed Explore/dashboard IDs.

**Security requirements**:
- JWT signing key must be kept server-side; never expose to client
- Short expiry (15–60 minutes); refresh tokens for longer sessions
- Scope JWT to minimum required data access — don't sign for all data and filter in the UI

### Performance at Scale

Embedded dashboards in multi-tenant SaaS can receive high concurrent load. Considerations:

- **Query concurrency limits**: BI tools have per-instance query concurrency limits.
  At high tenant counts, concurrent dashboard loads can exhaust the query queue.
- **Caching**: Aggressive result caching at the BI layer (Looker: `persist_with` on
  Explores; 1-hour or 24-hour TTL for dashboard queries) dramatically reduces warehouse
  load. Per-tenant cache partitioning required if row-level security differs between tenants.
- **Async loading**: Load dashboard tiles asynchronously; show skeleton loading states
  while tiles render
- **SLA tiering**: Internal analytics SLA (best effort, P95 < 10s) vs. customer-facing
  embedded SLA (P95 < 3s, monitored, alerting)

---

## BI for Enterprise SaaS Products

### In-App Reporting

Analytics embedded inside the product as a first-class feature (not a separate "reports"
section that feels bolted on):
- Usage metrics the customer cares about (their own data, their own KPIs)
- Tied to product actions: "You used X feature N times last month. Here's how that
  compares to similar accounts."
- Actionable: a metric surface should lead to a product action, not just inform

**Build vs. embed decision**:
- Embed a BI tool when: dashboards need to be flexible/customizable by the customer;
  you have > ~5 distinct dashboard use cases
- Build custom visualizations when: the analytics is deeply integrated with product UX;
  the data model is simple; you have < ~5 fixed views

### Multi-Tenant Data Access

Row-level security patterns for multi-tenant embedded BI:

| Pattern | Mechanism |
|---------|-----------|
| Warehouse-level RLS | Row access policy scoped to `tenant_id` column; most secure |
| BI layer user attributes | Inject `tenant_id` as a user attribute in the signed JWT; filter applied at query time |
| Separate schemas per tenant | Each tenant's data in isolated schema; BI tool connects to tenant-specific schema | 

**Schema-per-tenant** is the most secure isolation model but highest operational cost.
Row-level security via user attributes (Looker) or row access policies (Snowflake) scales
better.

### The "Bring Your Own BI" Pattern

Enterprise customers want their BI tools (Tableau, Power BI, custom Redash) pointed at
your data. Implementation options:

| Option | Mechanism | Notes |
|--------|-----------|-------|
| Read replica access | Direct database credentials to a read replica | High risk; customer can query anything; rarely acceptable |
| Semantic layer API | Customer connects via Looker API or dbt Semantic Layer (JDBC/REST) | Enforces metric definitions + RLS; preferred |
| Data export to customer warehouse | Export customer's data to their own warehouse | Customer owns their copy; no direct product DB access; freshness lag |
| Reverse ETL | Push customer's product data to their destination (via Census, Hightouch) | Clean separation; customer gets data in their stack |

**Recommended**: Semantic layer API for customers who want real-time access; data export
or reverse ETL for customers who want integration into their own data warehouse.

---

## Common Failure Modes

| Failure | Mechanism | Prevention |
|---------|-----------|-----------|
| Metric inconsistency | Different dashboards define the same metric differently | Semantic layer ownership; certified metric governance |
| Fanout in aggregation | Many-to-many join creates row multiplication | Declare join relationships correctly; use symmetric aggregates; validate row counts |
| Dashboard sprawl | Uncertified dashboards accumulate; no deduplication | Usage tracking; quarterly cleanup; certified vs. sandbox labeling |
| RLS bypass via dashboard filter | Users export data or manipulate URL params to bypass filters | Enforce RLS at warehouse or BI tool query layer, not dashboard filter layer |
| Signed embed key leakage | JWT signing key exposed in client-side code | Sign JWTs server-side only; rotate key regularly; audit access logs |
| Cache invalidation failure in multi-tenant | Cache returns one tenant's data to another tenant | Per-tenant cache keys; tenant scoping in cache headers |
| Embedded dashboard load time SLA | BI tool query latency too high for customer-facing P95 | PDTs for expensive queries; aggressive result caching; async tile loading |

---

## Cross-Hub References

- For data pipeline engineering, dbt, warehouse design → `ds-data-engineering`
- For data governance, catalog, lineage, access control → `ds-data-governance`
- For executive narrative from data → `ds-executive-storytelling`
- For product metrics, funnel analysis → `ds-product-analytics`
- For information hierarchy and visual encoding → `lead-information-designer`
