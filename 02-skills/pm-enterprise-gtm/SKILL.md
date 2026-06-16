---
name: pm-enterprise-gtm
description: >
  Enterprise go-to-market strategy, feature launch planning, pricing and
  packaging decisions, sales enablement, and revenue signal interpretation
  for B2B SaaS. Use this skill whenever the conversation touches: planning
  a product launch, interpreting ARR/ACV/NRR/NDR signals, choosing between
  sales-led and product-led growth motions, pricing and packaging a new
  feature, writing sales enablement artifacts, launch readiness reviews,
  customer advisory boards as a GTM input, or diagnosing why adoption is
  low after launch. Also trigger on: "feature launch", "go-to-market",
  "GTM", "sales enablement", "ARR", "NRR", "NDR", "net dollar retention",
  "pricing", "packaging", "general availability", "GA", "limited availability",
  "beta", "customer advisory board", "CAB", "launch checklist".
---

# PM Enterprise GTM

Specialist skill for enterprise go-to-market strategy, launch execution,
and revenue signal interpretation. Part of the enterprise SaaS product
management skill network.

---

## Domain Boundary

This skill owns **the path from product to market** — how a product capability
gets into the hands of customers in a way that generates revenue and adoption.

- **What to build for a launch** → `pm-discovery-research` and `pm-roadmap-strategy`
- **How to measure launch success** → `pm-metrics-analytics`
- **Competitive positioning for the launch** → `pm-competitive-intelligence`
- **Executive communication for launch approval** → `pm-stakeholder-comms`
- **Enterprise table stakes (SSO, SCIM, audit logs)** → `pm-platform-api`

---

## Revenue Signals as Product Signals

ARR, ACV, NRR, and NDR are not just finance metrics. Read them as product
health signals.

### Metric Definitions and What They Tell You

| Metric | Formula | What It Signals for Product |
|--------|---------|----------------------------|
| ARR (Annual Recurring Revenue) | Active subscription value annualized | Overall business health; segmented by cohort, it reveals which customers are growing vs. at risk |
| ACV (Annual Contract Value) | Total contract value ÷ contract length | The size of deal your product supports; low ACV often signals product doesn't justify enterprise pricing |
| NRR / NDR (Net Revenue Retention / Net Dollar Retention) | (Starting ARR + expansion − contraction − churn) ÷ starting ARR | The product's ability to grow within existing accounts. NRR > 100% means you're growing even without new logos |
| Gross Revenue Retention (GRR) | (Starting ARR − contraction − churn) ÷ starting ARR | Pure retention signal, excluding expansion. Captures the floor of the business |
| Logo churn rate | Accounts lost ÷ total accounts | Product-market fit signal. High logo churn means you're solving the wrong problem or onboarding wrong accounts |

### Reading NRR as a Product Signal

**NRR > 120%**: Customers find increasing value over time. Expansion triggers
are working (seat growth, module additions, usage-based billing).

**NRR 100–120%**: Steady state. Expansion covers churn but growth requires
new logos.

**NRR 80–100%**: Contraction and churn are real forces. Customers are
downgrading or churning before the end of their contract cycle. Investigate
time-to-value, adoption gaps, and competitive alternatives.

**NRR < 80%**: Systemic value delivery failure. Product-market fit is in
question for the installed base. Requires deep discovery in churned accounts.

### ACV as a Feature Signal

Low ACV relative to product complexity is a signal that buyers don't
perceive enough value to pay for what you've built. Before adding more
features, understand what the pricing ceiling is and why:

- Is it a perception problem (value isn't visible)?
- Is it a packaging problem (valuable capabilities are buried in a tier
  nobody buys)?
- Is it a positioning problem (selling features, not outcomes)?
- Is it a product problem (the value is genuinely not there yet)?

---

## Sales-Led vs. Product-Led Growth

The motion determines how you design GTM. Most enterprise SaaS lives on a
spectrum — choose where you are deliberately.

### Sales-Led Growth (SLG)

How it works: Sales closes deals. PM supports sales by making the product
demo well, enabling AEs with positioning, and delivering features that make
renewal conversations easier.

**When SLG is right**:
- ACV > $25k (complexity justifies a sales-assisted process)
- Multi-stakeholder buying (IT, legal, procurement involved)
- Customization requirements need discovery (enterprise deals need scoping)
- Customer needs onboarding support to reach value

**PM's GTM obligations in SLG**:
- Sales doesn't sell what they don't understand — invest in enablement
- Every launch needs a clear "what does this do for the customer and for the deal"
- Feature flags and grandfathering policies are PM decisions that affect
  existing contracts — get them right

### Product-Led Growth (PLG)

How it works: Users discover, try, and adopt the product without sales
intervention. Conversion from trial to paid is driven by product value.

**When PLG works in enterprise**:
- Users have autonomy to try tools without IT approval (increasingly common
  in horizontal tools like analytics, productivity)
- Time-to-value is short enough to demonstrate within a trial
- The product has a natural viral loop within teams (collaboration, sharing)

**When PLG fails in enterprise**:
- Product requires integration and configuration to deliver value (no
  time-to-value in a short trial)
- Buyer is not the user (IT must approve before users can try)
- Security review is required before adoption is allowed

### The PLG-to-SLG Expansion Pattern

A common and effective enterprise motion: PLG at the individual/team level
for initial adoption, SLG for expansion to enterprise licensing. Product
design must support both: easy individual onboarding AND enterprise-grade
controls (SSO, SCIM, centralized admin) for when IT takes over.

---

## Feature Launch Classification

Every feature launch is not the same. The launch tier should match the
maturity of the feature and the risk of rollout.

| Tier | Access | What It Means Operationally | Contractual Implications |
|------|--------|----------------------------|-------------------------|
| Internal Alpha | Internal team only | No customer exposure. Validating feasibility. | None |
| Closed Beta | Hand-selected design partners | Design partners have agreed to provide feedback. Can be referenced in conversations, not marketed. | Beta agreements in place; not part of standard contract |
| Limited Availability (LA) | Specific accounts or segments, by request | Feature exists and works. Eligibility criteria exist (enterprise tier, region, use case). | May be included in select contracts; referenced in release notes |
| General Availability (GA) | All eligible accounts | Documented, supported, under SLA, in product. | Part of standard offering; contractual obligations apply |
| Deprecated | Existing users only | No new adoption; timeline to sunset communicated. | Obligations to existing users during deprecation period |

**Common mistake**: Shipping something to "GA" before support documentation,
training, and the rollback plan exist. GA triggers contractual SLA obligations.
Don't declare GA until you're ready to support it.

---

## Pricing and Packaging Considerations

PM is not the pricing owner (that's usually product marketing or commercial
leadership), but PM has the most complete view of what's worth paying for
and why. Own the input.

### Bundled vs. Add-On Decisions

| Bundled | Add-On |
|---------|--------|
| Feature is table stakes for the tier — its absence would feel like missing functionality | Feature has distinct value perception; customers can understand paying for it separately |
| Removing it would make the product feel incomplete | Clear ROI story that justifies a separate line item |
| It reinforces the core value proposition | Used by a subset of customers with specific needs |

### Usage-Based vs. Seat-Based Tradeoffs

| Model | Works When | Fails When |
|-------|-----------|-----------|
| Seat-based | Value scales with number of users; easy to predict for enterprise budget cycles | Heavy users subsidize light users; single high-value use case doesn't require many seats |
| Usage-based | Value scales with consumption (API calls, data volume, exports); aligns price with value | Unpredictable billing creates friction for enterprise procurement; buyers can't forecast costs |
| Outcome-based | You can measure a clear ROI outcome and price against it | Hard to measure; difficult to standardize across accounts |

**When packaging is a PM problem vs. a commercial problem**:
- PM problem: the features are in the wrong tier for the customers who need them
- Commercial problem: the right features are in the right place but the price
  point is wrong for the market
- Both: when features are bundled into tiers that don't match actual usage
  patterns, confusing buyers and suppressing adoption

---

## Sales Enablement Artifacts PMs Own

Sales enablement is not a "nice to have" add-on to a launch. In sales-led
enterprise, a feature that sales doesn't know how to sell doesn't get sold.

### Artifacts PM Owns at Launch

**1. Positioning section of the battlecard**

- What problem does this solve for the customer (in customer language)
- Who at the customer should care (role-specific messaging)
- The one-line value statement
- How this differentiates from alternatives

See `pm-competitive-intelligence` for full battlecard construction.

**2. Feature one-pager**

```
Title: [Feature name that customers would recognize]
The Problem: [2-3 sentences on the customer pain in customer language]
What We Built: [What the feature does, not how it works technically]
Who It's For: [Target role, segment, use case]
Key Benefits: [3 bullets, outcome-focused]
How to Demo: [The 2-minute demo path that makes the value obvious]
FAQ / Objection handling: [Top 3-5 questions sales will get]
```

**3. Demo environment requirements**

Define the state the demo environment must be in to demo this feature
effectively. Don't assume sales knows what data or configuration to set up.

**4. Success metrics baseline**

Before launch, document the baseline metrics you'll use to evaluate adoption.
Sales needs to know what "good adoption" looks like so they can coach accounts.

---

## Launch Readiness Checklist

Before any GA launch:

**Product readiness**
- [ ] Feature complete against the spec
- [ ] Feature flags in place and tested
- [ ] Rollback plan documented and tested
- [ ] Performance tested under expected load
- [ ] Accessibility review complete

**Customer readiness**
- [ ] In-product documentation written and published
- [ ] Support knowledge base articles ready
- [ ] Beta feedback incorporated or explicitly deferred
- [ ] Release notes drafted

**Commercial readiness**
- [ ] Sales enablement artifacts (one-pager, demo path) delivered
- [ ] CSM briefed on what's changing and what to tell accounts
- [ ] Pricing/packaging decision finalized
- [ ] Success metrics baseline captured

**Operational readiness**
- [ ] Support team trained
- [ ] Monitoring/alerting configured for new feature paths
- [ ] Customer communications drafted (if applicable)

**Stakeholder alignment**
- [ ] Launch tier and audience defined
- [ ] Comms plan approved

---

## Customer Advisory Boards as GTM Input

A customer advisory board (CAB) is both a discovery mechanism and a GTM
instrument. Used well, it does three things:

1. **Validates strategic direction** before you commit capacity (generative)
2. **Creates internal champions** for features before they launch (GTM)
3. **Produces reference customers** for early positioning (sales enablement)

**PM's role in CAB operation**:
- Own the agenda — CABs that turn into customer support forums waste everyone's time
- Bring product direction, not feature requests — the goal is strategic alignment
- Capture signals on where the market is going, not just what customers want today
- Follow up on commitments from prior sessions — CAB members remember

---

## Common Failure Modes

| Failure Mode | What Happens | How to Prevent |
|-------------|-------------|---------------|
| Launching without sales alignment | Sales doesn't know what the feature does; it doesn't get mentioned in deals | Sales enablement is a launch exit criterion, not an afterthought |
| Under-specifying enterprise requirements | GA launch that doesn't support SSO, audit logs, or SCIM; enterprise prospects can't adopt | Define table stakes checklist pre-spec (see `pm-platform-api`) |
| Shipping before the narrative is ready | Customers don't know why to care; adoption lags | Invest in the "why it matters" story before launch day |
| Treating LA as GA in communications | Support expectations, SLA expectations, and feature completeness don't match the launch tier you've communicated | Be explicit about launch tier in all external communications |
| No rollback plan | A critical bug requires feature removal; no mechanism to do it cleanly | Feature flags and documented rollback process are mandatory, not optional |
| Missing the baseline | Can't tell if the launch worked because no pre-launch metric baseline was captured | Capture baseline 2 weeks before launch, not the day of |

---

## Cross-Hub References

- **Enterprise table stakes (SSO, SCIM, audit logs)** → `pm-platform-api`:
  required before GA for enterprise-targeted launches
- **Launch success metrics definition** → `pm-metrics-analytics`: defining
  what "good adoption" looks like and how to instrument it
- **Competitive positioning for the launch** → `pm-competitive-intelligence`:
  battlecard positioning and differentiation messaging
- **Executive communication for launch approval** → `pm-stakeholder-comms`:
  1-pager and briefing format for steering committees
- **Auth and provisioning implementation** → `be-auth-patterns`: SSO/SCIM
  implementation requirements flow from GTM table stakes
