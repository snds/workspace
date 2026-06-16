---
name: ds-executive-storytelling
description: >
  Translating data analysis into executive decisions, structuring data narratives,
  communicating uncertainty, and building executive-grade dashboards and briefings
  for enterprise SaaS. Use this skill whenever the conversation touches: executive
  presentation of data, board deck analysis, Pyramid Principle, BLUF communication,
  data storytelling, insight communication, recommendation structure, communicating
  confidence intervals to non-technical audiences, scenario framing, executive
  dashboards, KPI dashboard design, communicating uncertainty, p-value translation,
  survivorship bias explanation, correlation vs. causation for executives, regression
  to the mean, structuring a data briefing, framing a business recommendation from
  analysis, or any question about how to make analytical findings land with business
  stakeholders who want decisions, not model metrics. This skill covers analytical
  communication — not the analytical methods themselves (see other DS spokes).
---

# DS: Executive Storytelling

Specialist lens for translating data science work into executive decisions in enterprise
SaaS. Part of the lead-data-scientist skill network.

---

## Domain Boundary

This skill owns **how analytical findings are communicated and structured for business
impact**.

- **The analytical foundation of the findings** → appropriate DS spoke
- **PM alignment on what the exec needs to decide** → also engage `pm-stakeholder-comms`
- **Metric definition and OKR ownership** → `pm-metrics-analytics`

This skill operates at the intersection of rigorous analysis and business communication.
It is not about simplifying. It is about structuring complex, uncertain findings so the
right decision gets made.

---

## The Insight → Recommendation → Decision Chain

Most DS work stops at insight. That is not enough.

| Stage | Output | Who Owns It |
|-------|--------|------------|
| Analysis | Findings and evidence | Data Science |
| **Insight** | What the findings mean for the business | Data Science |
| **Recommendation** | What action the business should take | DS + PM / DS + Leadership |
| **Decision** | Which option is chosen and why | Decision-maker (Exec, PM) |

"Accounts in the bottom usage quartile have 3× higher churn rate" is a finding.

"High-churn-risk accounts are concentrated in a specific vertical and entry price point,
which suggests the onboarding experience is failing a specific segment rather than a
general activation problem" is an insight.

"We recommend a targeted onboarding intervention for new accounts in that vertical within
the first 30 days, which we estimate could recover ~$800K ARR annually at current acquisition
volume" is a recommendation.

Always know which stage you're delivering. Executives cannot make decisions from findings.

---

## Pyramid Principle Applied to Data

The Pyramid Principle: lead with the conclusion, support with arguments, support each
argument with data. Inverted from academic writing — conclusion first, not last.

### Structure for a Data Briefing

```
1. THE ANSWER (1 sentence)
   What does this analysis conclude?

2. SO WHAT (1-2 sentences)
   What does this mean for the business decision at hand?

3. KEY EVIDENCE (3-5 bullets)
   The most important supporting findings, each in 1 sentence.
   Each finding has a "so what" embedded: not just the number, but what it implies.

4. CAVEATS AND LIMITATIONS (1 brief section)
   What we don't know; what assumptions were made; where we'd be wrong.

5. METHODOLOGY (appendix / backup slides)
   Available for Q&A; not front-loaded.
```

**Anti-pattern**: "We started with N=50,000 accounts. After filtering for accounts active
in the last 90 days, we had N=32,000. We then grouped by cohort... [3 paragraphs of
methodology]... and found that churn is concentrated in segment X."

**Corrected**: "Churn risk is concentrated in our lowest-tier accounts in the manufacturing
vertical — 72% of at-risk ARR is in a segment representing 8% of accounts. Here's the
evidence and what we recommend."

---

## BLUF for Data Briefings

BLUF (Bottom Line Up Front): the "so what" lives in the first sentence, not the last.
This is the default for all executive data communication.

BLUF format:
```
[Conclusion/recommendation] because [key evidence], and we're [confidence level].
```

Examples:
- "We recommend pausing the Q3 expansion campaign because our most recent cohort analysis
  shows activation rates have declined 18% for enterprise-tier accounts, and we don't
  yet understand why."
- "The A/B test result is inconclusive — the effect was in the expected direction but
  didn't reach significance. We need 3 more weeks to reach the required sample size."
- "We estimate churn risk is elevated going into Q4, with high confidence the number is
  between 7-9% of ARR at risk. The base case is 8%."

---

## Choosing the Right Visualization

The visualization is not decoration — it is the argument. Choose it based on the claim
being made, not aesthetic preference or chart variety.

### Decision Table

| Claim Type | Right Chart | Do NOT Use |
|-----------|-------------|-----------|
| Change over time | Line chart (continuous); bar chart (discrete periods) | Pie chart; scatter for time series |
| Comparison across groups | Bar chart (few groups); dot plot (many groups) | Pie chart for >3 groups; 3D bars |
| Part-to-whole | Stacked bar (with % labels); treemap for hierarchical | Pie chart for >3 segments; donut |
| Distribution | Histogram (raw distribution); box plot (summary + outliers); violin (distribution shape) | Bar chart of averages (hides distribution) |
| Correlation / relationship | Scatter plot; small multiples for stratification | Correlation matrix for executives |
| Flow / funnel | Funnel chart; Sankey for multi-path | Bar chart (loses funnel shape signal) |
| Geographic | Choropleth (rate data); proportional symbol (absolute data) | Default color scales that misrepresent continuous data |
| Table | When precision matters more than pattern recognition; when N of items > 10 | Chart when numbers are being compared exactly |

### Executive Visualization Anti-Patterns

- **Pie charts with >3 segments**: humans cannot accurately compare arc lengths. If you
  need >3 segments, use a bar chart.
- **Dual y-axis charts**: almost always misleading because the visual relationship between
  the two series changes with axis scaling. Tell two separate stories on two separate charts.
- **3D charts**: the 3D perspective distorts visual comparison. Never.
- **Bar charts for time series**: suggests discrete intervals; use lines for continuous time.
- **Averages without distributions**: reporting "average account ACV is $24K" without
  showing that the distribution is bimodal with peaks at $8K and $80K misleads completely.
- **Truncated y-axes**: starting the y-axis at a non-zero value exaggerates small differences.
  Use when the meaningful range genuinely doesn't include zero; label clearly when you do.

### Calibrating Visualization Complexity to Audience

| Audience | Appropriate Complexity |
|---------|----------------------|
| Board / C-suite | 3-5 charts max per briefing; no multi-panel; no log scales without explanation |
| VP / Director | Can handle multi-panel, trend analysis, before/after comparisons |
| PM / technical lead | Full analytical charts; cohort heatmaps; box plots; log scales fine |
| DS / analyst | All chart types; raw model outputs acceptable |

---

## Communicating Uncertainty to Executives

Uncertainty is not a weakness to hide — it is information the decision-maker needs.

### Why Point Estimates Lie

A churn forecast that says "8% of ARR will churn in Q4" without an uncertainty range:
- Implies false precision
- Prevents the decision-maker from stress-testing their plans
- Makes DS look wrong when actuals come in at 10%

A forecast that says "our base case is 8%, with a reasonable range of 6-11%" enables
the exec to plan for downside and know the confidence level of their planning assumptions.

### How to Frame Uncertainty

| Framing | When | Example |
|---------|------|---------|
| Confidence interval | Quantitative estimates with statistical derivation | "The effect is between +2% and +8% with 90% confidence" |
| Prediction interval | Forecasts of future individual outcomes | "We expect 7-10% churn, with 80% of scenarios falling in that range" |
| Scenario framing | Strategic planning, model uncertainty is high | "Base case: 8% churn. Downside scenario (if macro deteriorates): 12%. Upside: 5%." |
| Sensitivity analysis | When a key assumption is uncertain | "If activation rate improves to X, the churn forecast drops to Y" |

**p-values to non-technical audiences**: "p=0.03" lands as noise. Translate:
"We're 97% confident this difference isn't due to random chance" — then caveat that
statistical significance and business significance are different, and state the effect size.

**Scenario framing often lands better than confidence intervals**: "Our best estimate is X,
our cautious estimate for planning purposes is Y, and it would take Z circumstance to
push the number below Y" gives decision-makers the intuition they need without
requiring them to interpret a probability distribution.

---

## Common Executive Misconceptions to Proactively Address

Address these before you're asked. Waiting to be questioned weakens credibility.

### Correlation ≠ Causation

State this explicitly every time a correlation is presented. Then provide the most
plausible alternative explanation.

"Accounts that use Feature X have 2× higher NRR. We can't conclude from this data alone
that Feature X causes higher retention — it's possible that higher-engagement accounts
both adopt more features AND have higher retention for other reasons. To establish
causation, we would need an experiment."

### Small Sample Size

State N prominently and its implications for confidence. Don't wait to be asked.

"This analysis is based on 47 accounts. The patterns are suggestive but the confidence
intervals are wide. I'd recommend validating with a larger cohort before making a
significant resource allocation decision."

### Regression to the Mean

Visible when: an intervention is applied after a metric hits an extreme value, and the
metric then improves — the improvement may be regression to the mean, not causal impact.

"We launched the customer success intervention with the 20 lowest-engagement accounts.
Engagement improved in 16 of them over the next 90 days. However, we should be cautious
interpreting this as causal — accounts at extreme low engagement tend to recover
partially regardless of intervention. To measure true impact, we need a randomized
holdout."

### Survivorship Bias

Common in retention analysis. If you're analyzing the behavior of accounts that are
still active, you've excluded the churned accounts — whose behavior before churning
is precisely what you need to understand.

"This engagement analysis covers our current customer base. Accounts that have already
churned aren't represented here. The features that look predictive of success may simply
reflect what engaged customers do — not what drives engagement."

---

## Structuring Executive Dashboards

### Design Principles

1. **3-5 key metrics maximum per view**. More is noise. If everything is highlighted,
   nothing is.
2. **Clear metric ownership**: each metric has a name, definition, and owner. No ambiguity
   about what "active users" means.
3. **Directional context on every metric**:
   - Trend: is it going up or down over the relevant period?
   - vs. Target: is it above or below plan/OKR?
   - vs. Prior Period: YoY or cohort-matched comparison (not just MoM, which has seasonal noise)
4. **One level of drill-down maximum**: the top-level metric should link to a breakdown,
   but the executive view should not require the breakdown to understand the headline.
5. **Alert thresholds**: metrics should have visual indicators when they're outside
   acceptable bounds — red/yellow/green based on documented criteria, not arbitrary.

### Metric Hierarchy for Enterprise SaaS Dashboard

```
NORTH STAR
└── ARR / NRR

HEALTH INDICATORS
├── Logo Retention (%)
├── Expansion ARR ($ and % of base)
├── New ARR (from sales pipeline → closed)
└── Churn ARR ($)

LEADING INDICATORS (predict future health)
├── Activation Rate (new account cohort, 30-day)
├── Engagement Score (current portfolio)
├── Feature Adoption Breadth (% of seats using core features)
└── At-Risk Account Count (from churn model / CS flags)

OPERATIONAL METRICS (for product/CS, not board level)
├── Support CSAT
├── Onboarding completion rate
└── Specific feature usage metrics
```

### Dashboard Anti-Patterns

- **Too many metrics**: 20 KPIs on one page makes everything equally important and
  therefore equally ignorable
- **No context for the number**: "NRR: 108%" with no trend, no target, no historical
  baseline tells the executive nothing about whether to be concerned
- **Self-serving metric selection**: only showing metrics that are improving; hiding
  the metrics that are declining
- **Staleness without indication**: if a metric hasn't refreshed, it must say so.
  Stale data presented as current is worse than no data.

---

## The "So What" Test

Before presenting any chart, table, or finding, answer: *so what?*

If you can't complete the sentence "This means the business should..." or "This means
the exec should be [more/less] concerned about X because...", the finding is not ready
to present.

Data without a "so what" is homework, not a briefing. The DS's job is to have done
the thinking to get to the "so what" before the room gets together, not in the room.

---

## Cross-Hub References

- For the analytical foundation of findings → appropriate DS spoke for the domain
- For PM alignment on recommendation framing and stakeholder management → `pm-stakeholder-comms`
- For metric definition and OKR ownership → `pm-metrics-analytics`
- For the visual communication craft — chart selection, data encoding, dashboard architecture, narrative visualization — route to `lead-information-designer`; this spoke provides the analytical story; `infod-narrative-design` and `infod-dashboard-patterns` provide the designed form it takes
