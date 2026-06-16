---
name: infod-dashboard-patterns
description: >
  Dashboard design for enterprise products: dashboard typology (operational,
  analytical, strategic), information hierarchy, KPI card anatomy, drill-down
  architecture, filter design, responsive dashboards, and date/time controls.
  Use this spoke when designing or evaluating an executive, operational, or
  analytical dashboard; when specifying KPI card layout and content; when
  deciding on a drill-down navigation pattern; when designing filters for a
  dashboard; or when addressing responsive layout degradation for dashboards.
hub: lead-information-designer
aliases: [infod-dashboard-patterns]
tier: spoke
domain: design
prerequisites: [lead-information-designer]
spec_version: "2.0"
---

# Dashboard Patterns

Specialist spoke for enterprise dashboard design. Part of the
`lead-information-designer` skill network.

---

## Domain Boundary

This spoke owns **dashboard architecture and component decisions**.

- **Which chart type inside a dashboard tile** → `infod-statistical-viz`
- **Visual encoding within a chart** → `infod-encoding-theory`
- **Data storytelling and annotation** → `infod-narrative-design`
- **Drill-down interaction patterns** → `ux-interaction-design` (for the
  navigation mechanics); this spoke covers the design decision
- **Dashboard component tokens** → `ds-advisor`

---

## Dashboard Typology

The first design decision for any dashboard is: what type is it? Each type has
different user goals, time horizons, and design constraints.

### Operational Dashboard

**User goal**: Monitor real-time or near-real-time status; detect exceptions;
take action.

**Users**: Supply chain managers, buyers, operations staff — people responsible
for current-state outcomes.

**Time horizon**: Today, this week, rolling 30 days.

**Design constraints**:
- Five-second rule is non-negotiable — status must be readable immediately
- Emphasize exception over normal — don't color everything, color anomalies
- Action affordances must be proximate — the user acts from the dashboard,
  not after a separate navigation step
- Refresh cadence matters — show last-updated timestamp; stale data is dangerous
- Avoid: excessive charts; favor clear KPI cards and structured tables with
  status encoding

**Centric PLM examples**: Production status board, shipment tracking, on-time
delivery rate, open tasks by buyer.

### Analytical Dashboard

**User goal**: Explore patterns, identify trends, investigate hypotheses.

**Users**: Analysts, data-savvy managers — people building understanding.

**Time horizon**: Any; historical comparisons are central.

**Design constraints**:
- Interaction is expected and appropriate — filtering, cross-filtering, zooming
- More charts are appropriate; richer encoding is acceptable
- Users will study the dashboard; the five-second rule relaxes
- Comparison structure matters: period-over-period, benchmark, segment splits
- Empty states and loading states need more care (long query times are common)

**Centric PLM examples**: Category performance by season, supplier scorecard,
assortment analysis.

### Strategic Dashboard

**User goal**: Answer "how is the business performing?" at an executive level;
confirm direction; flag when intervention is needed.

**Users**: Executives, VP-level — people who need high-confidence signals, not
investigative tools.

**Time horizon**: Month, quarter, year; trend direction is the signal.

**Design constraints**:
- Extremely high information density is wrong here; 3–7 metrics is the range
- Every metric must answer a specific strategic question — "so what?" must be
  immediate
- Trend direction (up/down vs. plan) is usually more important than exact value
- Benchmarks and targets must be present — a number without context is decoration
- Narrative annotation is appropriate and expected ("EMEA underperforming YoY
  due to logistics delays — see detail")

**Centric PLM examples**: Quarterly margin summary, category health snapshot,
seasonal plan vs. actual.

---

## Information Hierarchy in Dashboards

Every dashboard should have a deliberate visual hierarchy:

```
1. PRIMARY METRIC(S)      — the headline; what the user came to see
2. CONTEXT                — what does that number mean? target, trend, benchmark
3. SUPPORTING DETAIL      — breakdown by segment, category, time period
4. DRILL-DOWN NAVIGATION  — access to more detail when an anomaly is found
```

**Design rules:**
- Primary metrics get the most visual weight (large type, prominent position)
- Context is inseparable from the primary metric — show target and trend at the
  same visual level, not hidden in a tooltip
- Supporting detail is secondary — smaller, lower on the page, accessible by scan
- Drill-down is tertiary — should be available but not visually prominent
  (it is a low-frequency action)

### The Five-Second Rule

The primary takeaway of an operational or strategic dashboard must be
readable within five seconds, without reading any prose. Test this:

1. Show the dashboard to someone unfamiliar with it
2. After five seconds, cover it
3. Ask: "Is the business on track or not?"
4. If they can answer confidently, the hierarchy works

If the answer requires studying charts or scanning tables, the hierarchy failed.
Primary status indicators are not visible enough.

### Golden Ratio Layout

For executive and strategic dashboards, the golden ratio (~1.618) provides a
stable visual hierarchy between regions:

- Primary KPI region: ~60% of vertical height
- Supporting detail region: ~38% of vertical height
- Navigation/filter region: ~2% (minimal; should recede)

This is a guide, not a rule. The constraint is: the primary region must feel
dominant without reading the content.

---

## KPI Card Anatomy

KPI cards are the primary unit of operational and strategic dashboards.
A complete KPI card contains:

```
┌─────────────────────────────────────────────┐
│  [Metric Label]                  [Status]   │
│  [Primary Value][Unit]                       │
│  [Trend Indicator] [Trend Value] [Period]   │
│  [Context: vs. Plan / vs. LY / vs. Bench]   │
│  [Spark Chart — optional]                   │
└─────────────────────────────────────────────┘
```

### Required Elements (Minimum Viable KPI Card)

| Element | Description | Design Notes |
|---------|-------------|--------------|
| **Metric Label** | Name of the metric | Short (2–4 words); avoids jargon unless the audience is expert |
| **Primary Value** | The current metric value | Largest text on the card; right-sized to fit without truncation |
| **Unit** | The unit of measurement | Smaller than the value; avoid repeating if shown in label |
| **Trend Indicator** | Direction of change from comparison period | Arrow (up/down/flat) + color + shape redundancy; never color alone |
| **Trend Magnitude** | Size of the change | Both absolute and % when both matter; chose one when space is tight |
| **Comparison Period** | What is the trend measured against? | "vs. plan", "vs. last week", "vs. LY"; never omit — a trend without a baseline is meaningless |
| **Status** | On track / warning / below threshold | Color + icon; colorblind-safe; top-right corner (conventional position) |

### Optional Elements

| Element | When to Include |
|---------|----------------|
| **Spark chart** | When the trend shape matters, not just direction |
| **Target/Plan value** | When the comparison period is vs. plan |
| **Last updated** | Operational dashboards only; required when data is not real-time |
| **Drill-down affordance** | When the card links to detail; show as a subtle chevron or "View details" link |

### Spark Chart Design

Spark charts in KPI cards are trend indicators, not data exploration tools:
- No axes, no labels, no gridlines
- Line chart for continuous time series; bar chart for discrete periods (weeks, months)
- The baseline should be zero unless the business context makes a non-zero baseline meaningful
- Width × height: narrow and short; the shape impression is the information
- Color: match the card's status color for the line; neutral for no-status cards

---

## Drill-Down Architecture

When a dashboard user finds an anomaly in a KPI, they need to investigate.
The drill-down path is the designed pathway from "something is wrong" to
"here's why and here's the data."

### Four Drill-Down Patterns

**Breadcrumb-based (page navigation)**
- User clicks → navigates to a new page with the detail view
- Back breadcrumb shows: Dashboard → Category Level → Detail
- Use when: the detail level is full-page complex (tables, charts, filters)
- Advantage: full page real estate for detail; browser navigation works
- Disadvantage: context is lost; user must navigate back to compare

**Side Panel**
- User clicks → a panel slides in from the right with detail
- The overview remains visible on the left
- Use when: the detail is lightweight (a few metrics + small chart) and the
  user needs to compare detail back against the overview
- Disadvantage: limited space; complex detail views don't fit

**Modal**
- User clicks → an overlay appears with detail content
- Use when: a single item's detail is the scope (one KPI, one record)
- Disadvantage: interrupts flow; back navigation with modals is awkward;
  do not use for complex drill-down sequences

**Separate Page (explicit navigation)**
- A dedicated analytics page that the user navigates to independently
- The dashboard links to it but does not embed the drill-down flow
- Use when: the analytical experience is genuinely separate from the operational
  monitoring experience (different user, different time horizon)

**Decision matrix:**

| Complexity | Context needed | Pattern |
|-----------|---------------|---------|
| Low (1–3 metrics) | Yes | Side panel |
| Medium (table + chart) | Yes | Side panel or breadcrumb |
| High (full analytics) | No | Breadcrumb page navigation |
| Single record | No | Modal |
| Separate use case | No | Separate page |

Cross-link to `ux-interaction-design` for the interaction patterns (focus
management, keyboard access, scroll state preservation) for each pattern.

---

## Filtering and Interactivity

### Filter Placement

- **Analytical dashboards**: Filter panel at the top or left side; filters apply
  to all charts; prominently accessible
- **Operational dashboards**: Filters are a secondary action; collapse them by
  default; prioritize the display of current state
- **Strategic dashboards**: Limit to one primary filter (time period); executives
  should not be in filter UI

### Filter State Principles

- Always show active filter state visually — applied filters that are invisible
  are a design failure (the user gets wrong data without knowing why)
- Filter chips or tags below the filter bar indicate active filters
- "Reset all" affordance must be present and immediately accessible
- Filter state should be URL-persistent — bookmarking and sharing a filtered view
  must return the same state

### Cross-Filter Behavior (Analytical Dashboards)

Cross-filtering: clicking a segment in one chart filters all other charts on the
dashboard to that segment. This is a powerful analytical pattern but has design
requirements:

- Visual feedback must be immediate: the selected segment is highlighted;
  all other data de-emphasizes
- Deselect affordance must be obvious: click again to deselect, or a clear "×"
  on the selection state
- Not appropriate for operational dashboards: unexpected filter application
  confuses operational users who expect the dashboard to always show current state

### The Cost of Interaction for Operational Users

Operational users are monitoring, not exploring. Every interaction (hover for
tooltip, click for filter, scroll for content) is a friction cost. Design the
operational dashboard to be read, not operated. Show the right information without
interaction; reserve interaction for drill-down (exception, not normal).

---

## Responsive Dashboard Design

Dashboards in enterprise SaaS are primarily used on desktop (large monitors,
data density appropriate). Mobile is secondary but must not be broken.

### Fluid vs. Fixed Column Layout

- **Fixed columns** (12-column grid): predictable; KPI cards snap to defined widths;
  appropriate when the dashboard is a single-surface experience
- **Fluid layout**: columns resize with viewport; appropriate when the dashboard
  is embedded in a resizable container (side panel in a larger workflow)

### Mobile Dashboard Degradation Strategy

When a dashboard must work on mobile (tablet or phone):

1. **Show fewer metrics**: 3–5 KPI cards on mobile vs. 8–12 on desktop;
   hide low-priority metrics behind a "More metrics" expansion
2. **Larger touch targets**: KPI cards must be at minimum 44×44pt tap targets
3. **Stack charts vertically**: horizontal charts break on narrow viewports;
   vertical bar charts degrade better than horizontal sparklines
4. **Remove decorative elements**: remove sparklines and secondary context
   from KPI cards on mobile; keep value, trend direction, status
5. **No cross-filter**: cross-filter interactions are not appropriate for
   mobile; disable or replace with explicit filter controls

---

## Date and Time Controls

Date controls are one of the most commonly misdesigned dashboard elements.

### Preset Ranges vs. Calendar Picker

Preset ranges ("This Week", "Last Month", "Last 30 Days", "YTD", "Q1 2025") are
faster for operational users and cover 95% of dashboard time range needs.
Calendar picker should be available but not the primary affordance.

**Recommended preset set for PLM dashboards:**
- Today / Yesterday
- This Week / Last Week
- This Month / Last Month
- This Quarter / Last Quarter
- Year to Date / Last Year
- Custom range (calendar picker as last resort)

### Rolling vs. Fixed Windows

- **Rolling windows** ("last 30 days") update daily — the metric is always the
  most recent N days. Use for operational monitoring.
- **Fixed windows** ("March 2025") are anchored to a calendar period. Use for
  plan-vs.-actual comparisons where the plan is tied to a specific period.

Both have legitimate uses; the dashboard must make clear which is in use.
Displaying "Last 30 days" vs. "March 2025" is not just a label choice — it
changes the metric value and must match how the metric was defined.

### Timezone Display

- Always display the timezone for any time-based metric in a multi-timezone product
- Show in the filter control or as a data attribution line below the dashboard
- Use the user's local timezone by default; provide a way to switch to UTC
  or the company's "home" timezone for global operational dashboards

---

## Cross-Links

- **`infod-encoding-theory`** — preattentive attributes for KPI status encoding;
  color-safe status indicator design
- **`infod-statistical-viz`** — chart type selection for dashboard tiles;
  spark chart design; when to use a bar vs. a line in a KPI card trend
- **`infod-narrative-design`** — annotation in dashboard context; editorial
  commentary on a strategic dashboard; the waterfall as a dashboard element
- **`infod-design-system-patterns`** — KPI card as a DS component; filter
  component token patterns; tooltip design for dashboard charts
- **`ux-interaction-design`** — drill-down interaction mechanics (focus
  management, breadcrumb navigation, modal accessibility)
- **`a11y-cognitive`** — cognitive load management in dashboard density;
  progressive disclosure for complex dashboards
- **`ds-advisor`** — dashboard component token patterns; embedding chart
  tokens in the main DS token architecture
- **`lead-data-scientist`** — metric definitions; the distinction between
  rolling and fixed windows must match the data layer's aggregation logic

---

## References

- Stephen Few — *Information Dashboard Design* (2006, 2nd ed. 2013)
- Stephen Few — *Show Me the Numbers* (2004)
- Edward Tufte — *Envisioning Information* (1990)
- Nielsen Norman Group — Dashboard Design patterns research
- Juice Analytics — "Guide to Dashboard Design": https://juiceanalytics.com/

## Related
- hub → [[lead-information-designer]]
