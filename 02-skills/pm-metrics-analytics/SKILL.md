---
name: pm-metrics-analytics
description: >
  KPIs, OKRs, north star metrics, instrumentation requirements, and experiment
  framing for enterprise SaaS product teams. Use this skill whenever the
  conversation touches: defining a north star metric, writing OKRs that
  aren't gameable, identifying leading vs. lagging indicators, specifying
  event instrumentation for engineering, writing experiment hypotheses,
  evaluating metric quality, understanding Goodhart's Law in practice, or
  diagnosing why a metric isn't telling you what you thought it would.
  Also trigger on: "success metrics", "OKRs", "KPIs", "north star metric",
  "event tracking", "instrumentation", "experiment design", "A/B test framing",
  "leading indicators", "product analytics", "metric definition", "data spec".
---

# PM Metrics & Analytics

Specialist skill for metric definition, OKR writing, instrumentation
requirements, and experiment framing. Part of the enterprise SaaS product
management skill network.

---

## Domain Boundary

This skill owns **what to measure and how to specify measurement** — metric
frameworks, OKR craft, event tracking specs, and experiment framing.

- **Statistical experiment design, MDE, p-values** → `ds-experimentation`
- **Building analytics pipelines and dashboards** → `ds-product-analytics`
- **Communicating metrics to executives** → `pm-stakeholder-comms`
- **Using metrics to prioritize the roadmap** → `pm-roadmap-strategy`

---

## North Star Metric Framework

A north star metric (NSM) is the single metric that best captures the value
your product delivers to customers. When it goes up, both customers and the
business benefit. When it goes down, something fundamental is wrong.

### NSM Criteria

A good North Star Metric:
- **Measures customer value delivery**, not business extraction (not revenue
  directly — revenue follows when you get the NSM right)
- **Is leading relative to revenue** — it predicts future revenue, not
  just confirms past revenue
- **Is actionable** — the team can influence it through product decisions
- **Is singular** — one metric, not a composite score that hides what's moving

### NSM Examples in Enterprise SaaS Contexts

| Product Type | NSM Candidate | Why It Works |
|-------------|---------------|-------------|
| Collaboration tool | Weekly active collaborators | Captures network value and habitual use |
| Data platform | Queries run per active account/week | Measures value extracted from the platform |
| Workflow automation | Workflows completed successfully | Captures functional job completion |
| PLM / enterprise workflow | Active workflow steps processed/week | Measures workflow adoption, not just login |

### NSM Anti-Patterns

- **Revenue as NSM**: Revenue is a lagging outcome, not a leading indicator
  of value. You can have high revenue and a collapsing NSM at the same time
  (locked-in contracts disguise declining value delivery).
- **Composite "health scores"**: A blended score is impossible to act on.
  When the score moves, you don't know why. Use component metrics for
  diagnosis; reserve the composite for exec reporting if required.
- **Activity metrics**: Logins, page views, and sessions measure presence,
  not value. Users log in to find that something is broken. Sessions don't
  equal outcomes.

---

## Input vs. Output Metrics

| Type | What It Measures | Who Controls It | Cadence |
|------|-----------------|-----------------|---------|
| Output (lagging) | Business result: revenue, churn, NPS | Nobody directly — it results from inputs | Quarterly, monthly |
| Input (leading) | Team behavior or product signal that predicts output | The product team, directly | Weekly, sprint |

**The PM trap**: Managing entirely to output metrics (revenue, churn) gives
you a rearview mirror. By the time output metrics move, the cause is weeks
or months old.

**The opposite trap**: Managing to input metrics without validating they
predict the output you care about. Not every correlation is causal.

Healthy metrics practice: Define 1–2 output metrics (business outcomes),
then identify 3–5 input metrics with evidence that they predict those outputs.
Manage to the inputs weekly; validate the input-output relationship quarterly.

---

## OKR Writing at Enterprise Product Team Level

OKRs fail in most enterprise organizations for predictable reasons. Here's
what good looks like.

### Objective Criteria

Good objectives are:
- **Directional, not measurable** — the direction of ambition, stated qualitatively
- **Inspiring enough to focus** — teams should feel it matters
- **Time-bound** — relevant to the planning cycle (quarter or half-year)

Bad: "Improve platform performance." (Too vague, not directional)
Bad: "Ship API v2 by end of Q3." (That's an output, not an objective)
Good: "Make our platform the most reliable and performant in our category for enterprise accounts."

### Key Result Criteria

Good key results are:
- **Measurable** — binary (did it happen?) or numeric (what is the value?)
- **Outcome-focused**, not output-focused — "adoption rate" not "feature shipped"
- **Falsifiable** — you can be wrong about them. If you're always going to hit them,
  they're not key results, they're activity tracking.
- **Non-gameable** — team shouldn't be able to move the metric without
  moving the underlying reality it's supposed to measure

Good: "P99 API response time < 200ms across all enterprise accounts by end of quarter"
Good: "Weekly active collaborators grow from 340 to 500 in target segment"
Bad: "Complete API performance audit" (that's a task)
Bad: "Customer satisfaction with performance improves" (not measurable)

### The 60-70% Rule

OKRs should be ambitious enough that achieving 60-70% is a success. If you're
consistently hitting 100%, the targets aren't ambitious — they're task lists.
If you're consistently hitting 20%, the targets aren't OKRs — they're aspirations
disconnected from the team's capacity and control.

Calibrate by asking: "If everything goes well and the team executes excellently,
what would we expect to achieve? Set the KR there."

---

## Goodhart's Law and Metric Gaming

**Goodhart's Law**: "When a measure becomes a target, it ceases to be a good measure."

This is not an edge case. It is the default state of any metric that:
- Has organizational accountability attached to it
- Is visible to the people whose behavior would move it
- Is imperfectly correlated with the underlying thing it's supposed to measure

### Enterprise SaaS Metric Gaming Examples

| Metric | Gaming Pattern | What It Produces |
|--------|---------------|-----------------|
| New features shipped | Teams break large features into small ones to inflate count | Fragmented UX, no outcome movement |
| NPS response rate | CSMs encourage responses from happy customers | Inflated NPS, unrepresentative sample |
| "Active users" (logins) | Automated scripts, forced logins in onboarding flows | Engagement numbers that mask churn risk |
| Time-to-close (support) | Closing tickets without resolution | Re-opened tickets, customer frustration |
| Story points | Points inflate to "look productive" | Velocity numbers with no predictive power |

### Defenses Against Gaming

1. **Ratio metrics over absolute counts**: Active users / total users is harder
   to game than active user count alone.
2. **Paired metrics**: Track the metric and its adversarial counterpart. If
   you track tickets closed, also track tickets reopened.
3. **Metric reviews**: Periodically review whether high metrics reflect
   genuine improvement or measurement artifacts. Bring healthy skepticism.
4. **Separate metric ownership from metric accountability**: The person
   accountable for moving a metric shouldn't also be the person who defines
   what counts.

---

## Instrumentation Requirements

### Writing Event Taxonomy Specs

PM owns defining what to track. Engineering implements it. The gap between
"we should track that" and "here is the exact spec" is where most
instrumentation debt originates.

**Event spec format:**

```
Event Name: [action]_[object]_[context]
  e.g.: workflow_step_completed, report_exported, user_invited

Description: What the user did and why this is worth tracking.

Trigger condition: The exact moment this fires. Be specific about what
  constitutes the action vs. adjacent actions that should NOT fire this event.

Properties:
  - user_id (string): The ID of the user performing the action
  - account_id (string): The account/org the user belongs to
  - [object]_id (string): ID of the specific object involved
  - [context-specific properties]: e.g., workflow_type, export_format
  - timestamp (datetime): Server-side timestamp (not client)

Non-events (do NOT fire):
  - [List actions that might look similar but shouldn't fire this event]

Example:
  User clicks "Export" on a BOM report and the download begins.
  { event: "report_exported", user_id: "u_123", account_id: "a_456",
    report_id: "r_789", export_format: "xlsx" }
```

### Property Naming Standards

- Use `snake_case` for all property names
- IDs: `[object]_id` pattern — `user_id`, `account_id`, `workflow_id`
- Boolean properties: `is_[state]` — `is_admin`, `is_trial_account`
- Enum properties: document all valid values in the spec
- Timestamps: UTC, ISO 8601, server-side preferred over client-side
- Avoid PII in event properties unless required and explicitly approved

### Event Taxonomy Anti-Patterns

- **Event explosion**: Tracking every UI interaction produces noise that
  buries signal. Track meaningful actions at the job level, not every click.
- **Underspecified events**: "User did something with a report" — what something?
  Vague events produce vague answers.
- **Missing context**: An event without account-level context makes segmentation
  impossible. Always include user_id and account_id at minimum.
- **Client-only timestamps**: Clock skew and offline scenarios make client
  timestamps unreliable for sequencing. Use server-side timestamps.

---

## Experiment Framing

### Hypothesis Format

A testable experiment hypothesis contains:
1. **What we believe**: A specific claim about user behavior or product outcome
2. **What we'll do**: The change we'll make
3. **What we expect to happen**: The measurable outcome we predict
4. **Why we believe it**: The evidence or reasoning supporting the prediction

**Template**:
```
We believe that [user segment] experiences [friction/need] because [evidence].
We will [change/intervention].
We expect to see [metric] move from [baseline] to [target] within [timeframe].
This will be confirmed/refuted when [success criteria].
```

**Example**:
```
We believe that new enterprise users abandon setup during the SSO configuration
step because support tickets spike at that point and 3 discovery interviews
confirmed users don't know where to find their IdP metadata.

We will add contextual inline documentation with provider-specific guides
(Okta, Azure AD, Google) at the SSO configuration step.

We expect setup completion rate for enterprise accounts to increase from 62%
to 75% within 30 days of launch.

This will be confirmed if: completion rate ≥ 75% at 30 days, and refuted if:
no movement in 30 days (suggesting the friction is elsewhere).
```

### Defining Success Before the Test

Success and failure criteria must be defined before the test runs, not after.
Post-hoc framing produces motivated reasoning — you'll find a way to read
ambiguous results as confirming your hypothesis.

Document:
- **Primary success metric**: What must move, by how much, in what timeframe
- **Secondary metrics to monitor**: Things you don't want to accidentally break
- **Failure threshold**: The specific result that means "stop, don't ship"
- **Minimum run time**: How long before you evaluate (prevents peeking)

Route statistical design questions (MDE, sample size, p-value, significance
thresholds) to `ds-experimentation`.

---

## Leading vs. Lagging Indicators

**Leading indicators** predict outcomes before they happen. They're upstream
in the causal chain. They're actionable — you can influence them now.

**Lagging indicators** confirm outcomes that already happened. They're
downstream. They validate that leading indicators mattered.

### Enterprise SaaS Indicator Examples

| Lagging (Confirms) | Leading (Predicts) |
|-------------------|--------------------|
| Annual churn rate | Early usage drop in months 3-6 post-onboarding |
| NPS score | Support ticket frequency, feature adoption rate |
| Net Revenue Retention (NRR) | Product-qualified leads, expansion trigger events |
| Renewal rate | Stakeholder breadth (# of power users per account) |
| New logo conversion | Time-to-value in trial, setup completion rate |

**The leading indicator validation problem**: Not every correlation is causal.
Before treating a metric as a leading indicator, validate the relationship
with historical data. Does high early engagement actually correlate with
lower churn in your data, or are you assuming it does?

---

## Cross-Hub References

- **Statistical design for experiments** → `ds-experimentation`: MDE
  calculations, significance thresholds, sequential testing methods
- **Analytics pipeline and funnel instrumentation** → `ds-product-analytics`:
  when metric definitions need to be implemented in a data warehouse
- **Communicating metrics in exec presentations** → `pm-stakeholder-comms`
- **Metrics as roadmap inputs** → `pm-roadmap-strategy`: north star movement
  and leading indicator changes should inform sequencing decisions
