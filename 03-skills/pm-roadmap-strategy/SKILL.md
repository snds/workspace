---
name: pm-roadmap-strategy
description: >
  Roadmap construction, prioritization frameworks, portfolio planning, and
  dependency management for enterprise SaaS product teams. Use this skill
  whenever the conversation touches: building or communicating a roadmap,
  choosing a prioritization method (RICE, WSJF, Kano, opportunity scoring),
  sequencing platform versus feature work, managing dependency conflicts,
  portfolio-level planning, communicating uncertainty without losing
  credibility, or handling the organizational dynamics of roadmap ownership.
  Also trigger on: "roadmap", "prioritization", "backlog grooming", "RICE",
  "WSJF", "Kano model", "now/next/later", "quarterly planning", "platform
  sequencing", "portfolio roadmap", "dependency management", "cost of delay".
aliases: [pm-roadmap-strategy]
spec_version: "2.0"
---

# PM Roadmap & Strategy

Specialist skill for roadmap construction, prioritization, and portfolio
planning. Part of the enterprise SaaS product management skill network.

---

## Domain Boundary

This skill owns **sequencing decisions** — what order to build things in,
how to communicate that order, and how to manage the tradeoffs.

- **What opportunities to put on the roadmap** → `pm-discovery-research`
- **How to measure outcomes from roadmap execution** → `pm-metrics-analytics`
- **How to communicate the roadmap to executives** → `pm-stakeholder-comms`
- **How platform decisions affect roadmap structure** → `pm-platform-api`

---

## Outcome-Based vs. Output-Based Roadmaps

This is not a philosophical debate. It is a practical choice with real
tradeoffs depending on what you're trying to achieve.

### Output-Based Roadmap

Format: "Q1: Feature A. Q2: Feature B. Q3: Integration C."

**When it works**:
- Stakeholders require date-level specificity for external commitments (contracts,
  regulatory, sales pipeline)
- Work is well-understood (low uncertainty, high confidence in estimates)
- Team needs clarity on sequencing more than flexibility on what to build

**When it fails**:
- Work is exploratory or discovery is ongoing — dates become anchors that
  distort prioritization
- Circumstances change but the roadmap doesn't, creating "zombie commitments"
- Engineering estimates are wrong (they usually are) and the roadmap becomes
  fiction by week 6

### Outcome-Based Roadmap

Format: "H1: Reduce time-to-first-value for new accounts. H2: Expand
workflow coverage for enterprise configurability."

**When it works**:
- Team needs latitude to find the best solution to a real problem
- Discovery is ongoing and the solution space isn't locked
- You're managing a portfolio and need to give teams ownership of outcomes,
  not just tasks

**When it fails**:
- Leadership reads outcomes-based roadmaps as "no commitment"
- Sales needs something specific to tell prospects
- Team isn't clear what work maps to which outcome, producing diffusion

### Hybrid: Outcome Themes + Near-Term Output

The pragmatic enterprise pattern: **outcomes in the horizon view, outputs
in the quarterly view**. Horizon 1 (current quarter) has specific deliverables.
Horizon 2 (next quarter) has themes with probable items. Horizon 3 (6-12 months)
has outcome objectives only.

---

## Prioritization Frameworks

Use these with honest awareness of their failure modes. No framework substitutes
for judgment — they structure judgment.

### RICE

**Formula**: `(Reach × Impact × Confidence) ÷ Effort`

| Factor | What It Measures | Common Mistake |
|--------|-----------------|----------------|
| Reach | How many users/accounts affected per period | Counting seats, not actual active users |
| Impact | How much it moves the target metric | Inflating impact estimates to win prioritization |
| Confidence | How sure you are about R, I, and E estimates | Defaulting to 80% when actual confidence is 30% |
| Effort | Engineering effort in person-weeks | Forgetting design, QA, documentation, migration work |

**Best for**: Comparing a backlog of well-defined initiatives against a
single metric. Forces quantification.

**Fails when**: Confidence scores are inflated to make preferred items win.
The confidence number needs to be earned through research, not assigned
to win the argument.

**Enterprise specific**: Reach calculations are tricky — 1 account with 500
users may matter more than 50 accounts with 2 users each. Weight by account
tier, not just user count.

---

### WSJF (Weighted Shortest Job First)

**Formula**: `Cost of Delay ÷ Job Duration`

**Cost of Delay components**:
- **User/business value**: Revenue impact, cost avoidance, customer satisfaction
- **Time criticality**: Does value decay over time? Is there a market window?
- **Risk reduction / opportunity enablement**: Does this unblock other work?

**Best for**: Program-level sequencing where you have multiple initiatives
competing for capacity. WSJF explicitly values time — it answers "what's
the cost of waiting?" rather than just "what's the value?"

**Key insight**: A smaller, faster initiative with high cost of delay beats
a larger, higher-value initiative if the delay cost is asymmetric. WSJF
pushes teams to do the short, high-leverage work first.

**Fails when**: Cost of delay is hard to estimate honestly (common in
enterprise where revenue impact is mediated by sales cycles) or when teams
game the "job duration" estimate to make their initiative win.

---

### Kano Model

Maps features onto three categories:

| Category | Definition | Example |
|----------|------------|---------|
| Basic needs (must-haves) | Expected by default; absence creates dissatisfaction; presence is neutral | Audit logs for enterprise, SSO, data export |
| Performance needs (linear) | More = better; directly tied to satisfaction | Report speed, search accuracy, processing throughput |
| Delight (excitement) | Unexpected; creates satisfaction when present; absence is neutral | Intelligent suggestions, workflow automation |

**How to use in enterprise**:

1. Don't invest in delighters until basic needs are complete — shipping a
   beautiful AI feature while SSO is missing destroys enterprise credibility.
2. Performance needs are where differentiation compounds — be the fastest,
   most configurable, most accurate.
3. What was a delighter 2 years ago becomes a basic need — track category
   drift actively.

**Kano survey approach** (when you need data, not just intuition):
- Functional question: "How do you feel if [feature] is present?"
- Dysfunctional question: "How do you feel if [feature] is absent?"
- Score matrix maps response pairs to Kano category.

---

### Opportunity Scoring (Ulwick / JTBD)

**Formula**: `Opportunity Score = Importance + max(0, Importance − Satisfaction)`

Survey customers on two dimensions for each job:
- **Importance**: How important is it that you can accomplish X? (1–10)
- **Current satisfaction**: How satisfied are you with your current ability to accomplish X? (1–10)

Opportunities with high importance and low satisfaction are underserved.
Opportunities with low importance are overcrowded regardless of satisfaction.

**Best for**: When you have a defined job map and want to find which jobs
are most worth solving. Produces an evidence-based opportunity list.

**Fails when**: Survey sample is too small, importance ratings are inflated
(respondents rate everything as important), or the job statements are too
abstract to produce actionable scores.

---

## Now / Next / Later vs. Quarterly Timeline

| Format | When to Use | Risk |
|--------|-------------|------|
| Now/Next/Later | Uncertainty is high, sequencing matters more than dates | Leadership reads "Later" as "never"; no accountability signal |
| Quarterly timeline | Confidence is sufficient to commit to a quarter | Dates become anchors that survive even when underlying estimates are wrong |
| Milestone-based | Work is outcome-gated (e.g., "after beta closes") | Dependencies make milestone dates hard to pin |

**Rule of thumb**: Use dates when you have meaningful confidence. Use themes
when you don't. Mixing them (specific dates on uncertain work) creates the
worst of both: false precision that erodes trust when you miss.

---

## Platform Sequencing

### Foundation Before Features

The failure pattern: shipping user-visible features on a weak technical
foundation because features are visible and foundations are not. This
accumulates platform debt that makes every subsequent feature slower and
more fragile.

The discipline: identify which platform capabilities multiple product features
depend on, and sequence those first — even though they have no direct
customer-visible value on their own.

Platform primitives worth sequencing first in enterprise SaaS:
- Permissions and access control model (configurable, role-based, auditable)
- Data model extensibility (custom fields, custom objects)
- Integration hooks (webhooks, outbound events)
- API foundation (versioned, rate-limited, documented)
- Audit log infrastructure

These aren't features. They're the foundation that makes features enterprise-ready.

### Platform vs. Feature Tradeoffs

| Invest in Platform When | Invest in Features When |
|------------------------|------------------------|
| Multiple teams/features would use the same capability | A specific customer segment need is urgent and concrete |
| The capability is a prerequisite for the feature set customers need | Platform investment requires 3+ features to justify ROI |
| Technical debt is making feature delivery unsustainably slow | Platform is "nice to have" rationalization for avoiding delivery |

### Portfolio Roadmaps

Horizontal platform vs. vertical feature tradeoffs at portfolio level:

- **Horizontal investment**: Capabilities usable across products/segments
  (reporting, integrations, notifications). High leverage, delayed ROI signal.
- **Vertical investment**: Capabilities for a specific segment or workflow.
  Faster ROI signal, limited leverage.

Portfolio health check: If 100% of your roadmap is vertical, you're building
a collection of point solutions with no compounding. If 100% is horizontal,
you're building infrastructure with no customer pull.

---

## Communicating Uncertainty Without Losing Credibility

The trap: PMs feel pressure to express certainty they don't have because
stakeholders reward confidence. This corrupts the roadmap.

### Confidence Levels in Communication

Make uncertainty explicit and legible:

```
● Committed  — We've started. Delivery within this quarter barring emergencies.
◐ High       — Well-understood, designed, estimated. Confident in next quarter.
○ Planned    — Intent is clear. Requires design/discovery before committing.
◌ Exploratory — We believe this matters. Research required before sizing.
```

Label roadmap items with confidence levels. This is not weakness — it is
precision about what you actually know.

### The Roadmap Narrative

Every roadmap needs a narrative: "We are focusing on X because of Y evidence,
which we believe will produce Z outcome. This is why items A, B, C are in
that order."

Without the narrative, stakeholders read the roadmap as a list of things
someone asked for. With the narrative, it reads as a strategy. Strategies
earn investment; lists earn negotiation.

---

## The "Roadmap as Commitment Trap" Failure Pattern

**How it happens**:
1. PM publishes a quarterly roadmap with specific features and dates.
2. Stakeholders treat it as a contract.
3. New evidence arrives (customer interviews, competitive change, usage data).
4. PM doesn't update the roadmap because changing it feels like breaking a promise.
5. The team ships what was committed even though it's now the wrong thing.
6. Features ship to low adoption. Post-mortem reveals the evidence was there
   to change course, but nobody acted on it.

**The fix**: Frame roadmaps as hypotheses from the start. Build regular
"roadmap review" checkpoints (monthly) where updating based on new evidence
is the expected behavior, not a failure.

Stakeholder contract: "We commit to the outcomes. The specific solutions
are our current best hypothesis and will be updated as we learn."

---

## Dependency Management

### Mapping Dependencies

For each initiative, identify:
- **Upstream dependencies**: What does this depend on being done first?
- **Downstream unlocks**: What does completing this enable?
- **Cross-team dependencies**: Which teams outside your own must contribute?

Visualize as a dependency graph (not a Gantt chart). The critical path is
the longest chain of dependent items — that's what constrains your roadmap,
not the largest item.

### Cross-Team Dependency Failure Modes

- **Silent dependency**: Your roadmap assumes another team will deliver X,
  but you haven't aligned with them. Discovered late.
- **Shared infrastructure deadlock**: Two teams both need a platform capability,
  neither owns building it.
- **HiPPO resolution**: Dependencies resolved by escalating to leadership
  rather than negotiating team-to-team. Creates a tax on executive time
  and doesn't scale.

Resolution: Make dependencies explicit in roadmap reviews. Assign owners
to shared capabilities at the start of the planning cycle, not mid-execution.

---

## Cross-Hub References

- **Research-informed prioritization** → `pm-discovery-research`: opportunity
  scores and customer evidence feed into RICE/WSJF inputs
- **Communicating roadmap to executives** → `pm-stakeholder-comms`: the
  narrative structure and 1-pager format for roadmap presentations
- **Platform sequencing decisions** → `pm-platform-api`: when the roadmap
  item is a platform investment rather than a user-facing feature
- **Usage forecasts and churn signals as roadmap inputs** → `ds-forecasting`
