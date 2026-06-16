---
name: ds-product-analytics
description: >
  Funnel analysis, retention modeling, cohort analysis, customer LTV, behavioral
  segmentation, and self-serve analytics infrastructure for enterprise SaaS. Use this
  skill whenever the conversation touches: AARRR metrics, activation rate, retention
  curves, churn cohorts, D1/D7/D30 retention, monthly/quarterly retention for enterprise,
  customer lifetime value, CLV, LTV modeling, BG/NBD, expansion ARR, NRR, funnel
  analysis, funnel drop-off, conversion funnel, feature adoption analytics, product
  qualified leads, PQL, engagement scoring, RFM analysis, behavioral segmentation,
  k-means on product data, cohort analysis, survivorship bias in retention, Looker,
  Tableau, BI tooling, self-serve analytics, or any question about understanding how
  users and accounts behave in the product and what that means for the business.
  This skill covers descriptive and predictive product analytics — not experiment
  design (ds-experimentation), not production ML serving (ds-ml-engineering).
aliases: [ds-product-analytics]
spec_version: "2.0"
tier: spoke
domain: data
hub: lead-data-scientist
prerequisites: [lead-data-scientist]
---

# DS: Product Analytics

Specialist lens for product analytics in enterprise SaaS. Part of the lead-data-scientist
skill network.

---

## Domain Boundary

This skill owns **behavioral analysis of users and accounts in the product** — funnel
analysis, retention, LTV, segmentation, and self-serve analytics infrastructure.

- **Causal measurement (did this feature change behavior?)** → `ds-experimentation`
- **Production models on behavioral data** → `ds-ml-engineering`
- **Metric definition and OKR ownership** → also engage `pm-metrics-analytics`
- **Event instrumentation** → also engage `be-integration-patterns`
- **Analytical queries on OLTP source data** → also engage `be-relational-db`

---

## AARRR in Enterprise SaaS Context

The AARRR framework applies to B2B SaaS, but the metric owner and the time horizon differ
significantly from consumer products.

| Stage | Enterprise SaaS Metric | Owner | Time Horizon |
|-------|------------------------|-------|-------------|
| Acquisition | Lead quality score, SQLs from product signals | Marketing/Sales | Days to weeks |
| Activation | Time-to-value, completion of core workflow within trial | Product / CS | Days to weeks |
| Retention | Net Revenue Retention (NRR), logo retention | Product / CS | Monthly to annual |
| Referral | Net Promoter Score (NPS), expansion from advocacy | CS / Marketing | Quarterly |
| Revenue | Expansion ARR, upsell conversion rate | Sales / CS | Quarterly |

**Multi-tenancy note**: In B2B SaaS, these metrics must be measured at the **account**
level, not the user level. An account that retains a 500-seat enterprise contract is worth
orders of magnitude more than 500 individual SMB users. User-level AARRR analysis is
misleading unless you understand the account distribution your users live in.

### Activation — The Most Underanalyzed Stage

Activation rate (% of new accounts completing the core value workflow within a defined
time window) is frequently:
- Poorly defined ("activation" means different things to different teams)
- Measured inconsistently (event logged differently for new vs. legacy onboarding paths)
- Not tracked against revenue outcomes to validate the definition

Best practice: Define activation with a hypothesis ("accounts that X within Y days have
higher 6-month retention"). Validate the hypothesis with cohort survival analysis. If
the event doesn't predict retention, redefine activation.

---

## Funnel Analysis

### Defining the Funnel

A funnel is a sequence of events that represents progress toward a desired outcome.

| Dimension | Decision |
|-----------|---------|
| Event-based vs. session-based | Event-based (any session) is standard; session-based appropriate when the flow must be completed in one session |
| Attribution window | Maximum time allowed between funnel steps. Too short = artificial drop-off; too long = noisy signal. Set based on typical time-to-complete from empirical data |
| Entry point | What qualifies a unit to enter the funnel? First occurrence? Any occurrence? After a triggering event? |
| Multi-path funnels | Users can reach the same step via different paths. Model as a directed graph if paths matter; collapse to common steps if only the steps matter |
| Granularity | Account-level or user-level? Mixed funnels (account-level activation, user-level feature adoption) are common but need careful interpretation |

### Common Failure Modes in Funnel Analysis

- **Re-entries inflate counts**: A user who starts the funnel twice counts twice unless
  you define a unique-unit funnel. Know which you're measuring.
- **Ignoring multi-tenancy**: If a 1000-seat account drops from step 2 to step 3, that
  looks like 1 account drop in account-level funnel but 1000 users in user-level. Neither
  is wrong, but they answer different questions.
- **Attribution window too narrow**: Sets an artificial conversion rate. Check the
  distribution of time-to-complete; the window should cover the 80th percentile.
- **Vanity funnel steps**: Including steps that are technically in the UI path but don't
  predict downstream outcomes. Validate each step's correlation with business outcomes.

---

## Retention Analysis

### Cohort Retention Curves

Cohort retention is measured as: of all accounts (or users) that first activated in period
P, what % are still active in period P+N?

For enterprise SaaS:
- Monthly cohorts, measured at monthly intervals
- "Active" definition tied to meaningful product engagement, not login
- Plot log-scaled time on x-axis when retention is low in early periods

### Retention Curve Shapes and Interpretation

| Shape | Pattern | Signal |
|-------|---------|--------|
| Flattening curve | High early churn, stabilizes to a floor | Core retained segment exists; acquisition is bringing in low-fit users |
| Declining to zero | Continuous churn, no retention floor | Product-market fit problem or wrong retention definition |
| Smile curve | Initial drop, then increase | Expansion or re-engagement effect; investigate what drives the re-engagement |
| Near-flat from day 1 | Very high early retention | Strong product-market fit; verify the active definition isn't too loose |

**Enterprise SaaS specifics**: Annual contracts mask true retention. An account on a 12-month
contract won't churn until renewal — so your 1-month retention rate will look artificially
high for annual-contract cohorts. Segment retention analysis by contract type.

### NRR (Net Revenue Retention)

NRR = (Beginning ARR + Expansion ARR − Contraction ARR − Churned ARR) / Beginning ARR

NRR > 100% means the business grows even without new customer acquisition. This is the
defining metric of a healthy enterprise SaaS business. Best-in-class is >120%.

Product analytics contribution to NRR: identifying leading indicators of expansion
(breadth and depth of feature adoption, seat utilization) and contraction/churn (declining
engagement, support escalation patterns, economic signals).

---

## Customer LTV Models

### Contractual CLV (Enterprise SaaS Default)

For known-contract businesses:
```
CLV = ACV × Gross Margin × (1 / Monthly Churn Rate)
    = ACV × Gross Margin × Average Customer Lifetime (months)
```

Assumptions: constant monthly churn rate (geometric), constant ACV. Both are heroic
assumptions for enterprise accounts. The value is in sensitivity analysis:
- If churn improves from 2% to 1.5% monthly, how does CLV change?
- What is the CLV impact of a 10% upsell in year 2?

### Expansion LTV

Standard CLV ignores expansion. For businesses with strong upsell/cross-sell:
```
CLV_expansion = Σ (ACV_t × Gross Margin) / (1 + r)^t × P(retained_t)
```
Requires modeling expansion probability by cohort and tenure. Segments with higher
expansion tendency (by initial use case, vertical, or onboarding path) may have
dramatically higher LTV than their initial ACV suggests.

### BG/NBD Model (Non-Contractual Contexts)

For usage-based or product-led contexts where "churn" isn't a discrete event:
- Beta-Geometric/NBD models individual purchase/activity timing and dropout probability
- Produces individual-level expected future transactions and "alive" probability
- Requires individual transaction history; implemented in the `lifetimes` Python library
- Valid for PLG motion where users can go dormant without explicit churn

---

## Behavioral Segmentation

### RFM Analysis

RFM (Recency, Frequency, Monetary) scores each account on:
- **Recency**: How recently did they engage?
- **Frequency**: How often do they engage?
- **Monetary**: What ARR or usage value do they represent?

Operationally: compute quintile ranks (1–5) per dimension; combine scores; use to
prioritize CS intervention. High-frequency, high-monetary, low-recency accounts are
at-risk churners for immediate outreach. High-frequency, high-monetary, high-recency
accounts are expansion candidates.

### K-Means Clustering on Behavioral Features

For more nuanced segmentation beyond RFM:
- Features: seat utilization rate, feature breadth score, API usage rate, support ticket
  volume, login frequency, days since last activity
- Standardize features before clustering (StandardScaler or RobustScaler)
- Determine k with elbow method + silhouette score — don't default to k=5
- Profile each cluster with business metrics (retention rate, NRR, ACV) to validate
  that the clusters are business-meaningful, not just statistically distinct
- Label clusters with interpretable names that non-DS stakeholders can use

**Anti-pattern**: Clustering on features that are highly correlated with each other
produces clusters that are really just proxies for account size. Include diverse feature
dimensions.

### Engagement Scoring (Product Qualified Leads)

A PQL score quantifies how much a specific account (or user in PLG) has activated relative
to the behaviors that predict conversion or expansion.

Design principles:
- Weight features by their empirical correlation with conversion outcome (logistic
  regression or gradient boosting — not arbitrary weights)
- Include recency weighting: activity from last 14 days matters more than 90 days ago
- Validate score against holdout conversion data; calibrate if needed
- Refresh score frequently enough for the use case (daily for active PQL triggers, weekly
  for CS review)

---

## Feature Adoption Analytics

Two dimensions of adoption inform very different interventions:

| Dimension | Definition | Metric |
|-----------|-----------|--------|
| Breadth | % of available features/modules used by account | Features used / Features available |
| Depth | Frequency of use within a feature | Events per active user per period |
| Stickiness | DAU/MAU ratio (consumer) or weekly active / monthly active (enterprise) | WAU / MAU for the feature |

**Adoption curve analysis**: Track cohort-level breadth adoption over account tenure.
Accounts that adopt N features within first 90 days have higher NRR at 12 months —
validate this hypothesis for your product, then use it to set activation targets.

**Multi-tenancy in adoption analytics**: A feature is "adopted" by an account when a
meaningful fraction of its seats use it, not when one power user discovers it.
Define account-level adoption as: ≥X% of active users in the account have used the
feature at least Y times in the past Z days. Tune X, Y, Z per feature based on typical
usage patterns.

---

## Self-Serve Analytics Infrastructure

### What Belongs Where

| Use Case | Right Tool |
|----------|-----------|
| Business metrics, executive dashboards, stakeholder reports | BI tool (Looker, Tableau, Mode) |
| Recurring standardized queries (weekly retention report) | dbt model + BI tool |
| Complex multi-step analysis (funnel with custom attribution) | Python/SQL notebook, exported to BI if recurring |
| One-off exploratory question | SQL or Python notebook; don't build infrastructure for it |
| Real-time alerting on metric degradation | Data observability tool + alerting pipeline |
| Model-powered scores (churn, PQL) | Data product — dedicated pipeline, not ad-hoc |

Build infrastructure (dbt model, BI dashboard) only when a query will be run repeatedly
and has a consistent consumer. Ad-hoc analysis infrastructure is tech debt.

### Looker/Tableau Anti-Patterns
- **Logic in the BI tool**: Calculation logic in LookML or Tableau calculated fields that
  belongs in a dbt model — it won't be tested, versioned, or reused correctly
- **Direct connection to OLTP database**: BI tools should read from the analytical
  warehouse, not the production database — OLTP query patterns differ from analytical
- **One dashboard per request**: Proliferation of similar dashboards with slightly
  different definitions; resolve with a single source-of-truth metric layer in dbt

---

## Common Failure Modes

| Failure | Description | Prevention |
|---------|-------------|-----------|
| Vanity metrics | Metrics that look good but don't correlate with revenue or retention | Validate every metric against 6-month NRR or ARR outcomes before socializing |
| Survivorship bias in cohort analysis | Only analyzing accounts that are still active today, biasing retention estimates upward | Start cohorts from first activation; include churned accounts |
| User ≠ Account | User-level analysis for a B2B metric | Define the unit of analysis at project start; almost always account for revenue metrics |
| Ignoring multi-tenancy | Mixing enterprise 500-seat accounts with SMB 2-seat accounts in averages | Segment by account tier; compute medians not means for ARR-weighted metrics |
| Confusing correlation with causation | "Accounts that use feature X have 2x NRR" → ship feature X to everyone | This is a selection effect, not a causal claim; run an experiment or apply causal inference methods |
| No baseline for time-series | Reporting metric changes without seasonal context | Year-over-year comparison; cohort-matched comparison; not just month-over-month |

---

## Cross-Hub References

- For metric alignment and OKR ownership → `pm-metrics-analytics`
- For event data pipeline and instrumentation requirements → `be-integration-patterns`
- For analytical queries on OLTP data sources → `be-relational-db`
- For causal measurement of feature impact → `ds-experimentation`
- For churn prediction models → `ds-ml-engineering` and `ds-forecasting`

## Related
- hub → [[lead-data-scientist]]
