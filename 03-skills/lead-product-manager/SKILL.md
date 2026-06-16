---
name: lead-product-manager
description: >
  Staff/principal-level product management for enterprise B2B SaaS. Hub skill
  for a network of 7 specialist spokes covering discovery, roadmap strategy,
  metrics, GTM, platform/API product, stakeholder communication, and competitive
  intelligence. Use this skill whenever the conversation touches: product
  strategy, roadmap planning, prioritization frameworks, OKRs, customer
  discovery, user research synthesis, JTBD, enterprise go-to-market, ARR/NRR
  signals, API as product, platform strategy, stakeholder alignment, executive
  communication, win/loss analysis, competitive positioning, product metrics,
  instrumentation requirements, experiment framing, or any question about how
  to make better product decisions at enterprise scale. Also trigger on:
  "product manager", "PM", "product strategy", "roadmap", "discovery",
  "user research", "enterprise features", "go-to-market", "product metrics",
  "OKRs", "prioritization", "stakeholder alignment", "competitive analysis",
  "platform strategy", "API product", "enterprise SaaS PM".
aliases: [lead-product-manager]
tier: hub
domain: product
spec_version: "2.0"
prerequisites: [product-foundations]
---

# Lead Product Manager

**Hub skill** for the enterprise SaaS product management skill network. Routes
to 7 specialist spoke skills based on topic. This hub contains the operating
principles and mental models that apply across all PM work; spokes provide
domain-specific depth when needed.

---

## Spoke Network — Load On-Demand

**Do not load all spokes eagerly.** Load only the 1–2 spokes most relevant to
the current question. The hub is sufficient for triage and first-principles
reasoning; spokes add domain-specific frameworks and failure pattern libraries.

### Spoke Manifest

| Skill | Domain | Trigger When |
|-------|--------|-------------|
| `pm-discovery-research` | Enterprise B2B discovery, customer interviewing, JTBD, synthesis, opportunity sizing | Running or analyzing customer research, interview planning, synthesizing findings, opportunity sizing, evaluating evidence quality |
| `pm-roadmap-strategy` | Roadmap construction, prioritization frameworks, portfolio planning, dependency management | Building or communicating roadmaps, choosing prioritization methods, sequencing platform vs. feature work, handling dependency conflicts |
| `pm-metrics-analytics` | KPIs, OKRs, north star metrics, instrumentation requirements, experiment framing | Defining success metrics, writing OKRs, specifying event tracking, designing experiments, evaluating metric quality |
| `pm-enterprise-gtm` | ARR/ACV signals, sales-led vs. PLG, pricing/packaging, launch readiness, sales enablement | Planning a feature launch, pricing discussions, sales enablement artifacts, launch readiness reviews, ARR/NRR interpretation |
| `pm-platform-api` | Platform vs. product strategy, API as product, integration ecosystem, extensibility, developer experience | Deciding when/how to platformize, API design decisions, integration ecosystem strategy, extensibility patterns, enterprise integration table stakes |
| `pm-stakeholder-comms` | Executive communication, steering committees, cross-functional alignment, decision frameworks | Preparing executive communications, managing steering committees, DACI/decision rights, escalation decisions, 1-pagers and briefing docs |
| `pm-competitive-intelligence` | Win/loss analysis, competitive positioning, battlecard construction, market landscape | Analyzing competitive dynamics, building positioning, win/loss reviews, battlecard content, analyst relations |

### Spoke Loading Protocol

**Step 1**: Match the user's question against the Spoke Manifest. Identify
the 1–2 spokes that directly apply (rarely 3).

Common routing patterns:

| Scenario | Load |
|----------|------|
| "How should I run discovery for this feature?" | `pm-discovery-research` |
| "Help me build a roadmap / prioritize this backlog" | `pm-roadmap-strategy` |
| "What metrics should we track / how do I write OKRs?" | `pm-metrics-analytics` |
| "We're launching next quarter / need sales enablement" | `pm-enterprise-gtm` |
| "Should we build an API / platform layer?" | `pm-platform-api` |
| "How do I present this to executives / my steering committee?" | `pm-stakeholder-comms` |
| "How do we position against competitor X?" | `pm-competitive-intelligence` |
| "We won / lost a deal, what does it mean?" | `pm-competitive-intelligence` + `pm-enterprise-gtm` |
| "Defining success metrics for an experiment" | `pm-metrics-analytics` |
| "Instrumentation / event tracking requirements" | `pm-metrics-analytics` |
| "Launch readiness checklist" | `pm-enterprise-gtm` |
| "What's the right prioritization framework here?" | `pm-roadmap-strategy` |

**Step 2**: Load identified spoke(s) from:
```
[workspace root]/03-skills/[skill-name]/SKILL.md
```

**Step 3**: If the conversation shifts to a different spoke's domain,
load that spoke then — not preemptively.

---

## Core Principles

These apply across all PM work at enterprise scale. Spokes build on them;
they are never overridden.

### 1. Outcome Over Output

The roadmap is not a list of things to build. It is a sequence of bets on
outcomes. Ship a feature nobody uses and you've consumed capacity without
moving any metric that matters.

Practical implication: every initiative on the roadmap should be traceable
to a user or business outcome. If you can't state the outcome clearly, the
initiative isn't ready to be on a roadmap — it belongs in discovery.

### 2. The Enterprise Buyer/User Split

In enterprise B2B, the person who writes the check, the person who champions
the purchase, and the person who uses the product are almost never the same.

| Role | Cares About | Typical Title |
|------|-------------|---------------|
| Economic Buyer | ROI, risk reduction, contract compliance, vendor risk | CFO, VP Operations, CTO |
| Champion | Career advancement, internal credibility, solving their team's problem | Director, Program Manager, Power User |
| End User | Not being disrupted, task completion speed, avoiding frustration | Individual contributor |

Build features that serve end users. Write positioning that speaks to buyers.
Give champions ammunition to sell internally. Failing to separate these three
jobs is the most common reason enterprise products win deals but churn accounts.

### 3. Uncertainty Is the Default State

Every product decision is made with incomplete information. The PM's job is
not to eliminate uncertainty — it is to identify which uncertainties are most
dangerous to the roadmap, then reduce them as cheaply as possible before
committing capacity.

Cheap uncertainty reduction: a 45-minute customer interview, a paper prototype,
an analytics query, a JTBD assumption map.

Expensive uncertainty reduction: a six-week engineering sprint on a feature
nobody validates until it's shipped.

### 4. Build for the Workflow, Not the Feature Request

Customers describe what they want. What they tell you they want is usually a
solution framed by the tools they already have. Your job is to understand the
workflow behind the request — the sequence of tasks, handoffs, decisions, and
friction points that the request is trying to address.

A feature request is a symptom. A workflow is the diagnosis. Build the fix,
not the symptom-response.

### 5. Every Roadmap Is a Hypothesis

A roadmap is not a promise. It is the current best hypothesis about the
sequence of investments that will produce the target outcomes, given current
knowledge. New information should update it.

The trap: organizations treat roadmaps as commitments. PMs then stop updating
them when new evidence arrives because doing so feels like breaking promises.
This makes roadmaps increasingly wrong over time while maintaining the illusion
of certainty.

Operate your roadmap as a living document with explicit confidence levels.
Make the hypothesis nature visible to stakeholders — it's not weakness, it's
epistemic honesty.

---

## Enterprise SaaS Operating Directive

This skill network is calibrated to **enterprise B2B SaaS** specifically.
The following distinguishes enterprise PM work from consumer product management:

### Sales-Mediated Feedback Loops

In consumer products, you can run experiments at scale, see adoption data
quickly, and iterate fast. In enterprise SaaS:

- Sales cycles are 3–18 months. Customer feedback arrives slowly and through
  intermediaries (AEs, CSMs).
- Design partners and customer advisory boards are your primary generative
  research channel.
- Win/loss analysis is a research methodology, not a sales ops function.
- The customer success team carries signals from the installed base — a
  source most enterprise PMs under-leverage.

### Compliance and IT as Hidden Stakeholders

Enterprise buyers have IT, security, legal, and procurement in the buying
process. Features that don't meet their requirements (SSO, SCIM, audit logs,
data residency, SOC 2) don't reach users regardless of how much end users
want them. These are table stakes, not differentiators.

### Configuration Over Customization

Enterprise customers have heterogeneous processes. The product needs to be
configurable without requiring custom engineering. The failure mode is scoping
"enterprise readiness" as a separate workstream after the core product is
built — by then, the architecture makes configuration expensive.

### Long Tail of Commitment

Enterprise SaaS customers sign multi-year contracts. A feature you ship
creates a support and maintenance obligation for years, not months. The cost
of building wrong is higher. The case for discovery before commitment is
stronger.

---

## Cross-Hub References

### PM → Data Science

| From | To | When |
|------|----|------|
| `pm-metrics-analytics` | `ds-experimentation` | PM is framing an experiment — DS owns statistical design and MDE calculations |
| `pm-metrics-analytics` | `ds-product-analytics` | Shared metric definitions, funnel instrumentation, analytics pipeline requirements |
| `pm-stakeholder-comms` | `ds-executive-storytelling` | PM owns the recommendation; DS owns the analytical evidence — coordinate for exec presentations |
| `pm-roadmap-strategy` | `ds-forecasting` | Churn signals, usage forecasts, adoption curves as roadmap inputs |
| `pm-platform-api` | `ds-nlp-llm` | When building AI/LLM capabilities as product features |

### PM → Backend Engineering

| From | To | When |
|------|----|------|
| `pm-platform-api` | `be-api-design` | PM defines API product strategy; backend implements the execution |
| `pm-platform-api` | `be-integration-patterns` | Integration ecosystem execution |
| `pm-metrics-analytics` | `be-integration-patterns` | Event instrumentation requirements flow to backend |
| `pm-enterprise-gtm` | `be-auth-patterns` | SSO, SCIM, audit log requirements — enterprise table stakes |

### PM → Design

Route product definition and user stories to `design-engineer` or `ds-advisor`
when the conversation shifts from what to build to how it should work or look.

---

## Failure Mode Library (Hub-Level)

Patterns that fail across all PM domains:

- **Solution-first discovery**: Starting research with a specific solution
  in mind and running interviews to validate it. Produces confirmation bias,
  not insight.

- **The feature factory**: Treating PM as requirements translation. Backlogs
  fill up, output is high, outcome movement is invisible, morale degrades.

- **Roadmap as commitment contract**: Publishing a quarterly roadmap with
  dates, then treating it as a legal obligation rather than a hypothesis.
  Creates learned helplessness when reality changes.

- **HiPPO capture**: Allowing the highest-paid person's opinion to override
  evidence in prioritization decisions. Common in enterprise orgs with
  top-down cultures.

- **Treating all three buyers as one**: Writing positioning, doing discovery,
  or building features as if the champion, economic buyer, and end user are
  the same person. They're not.

- **Shipping without the narrative**: Launching a feature before sales,
  support, and customers understand what it does and why it exists. Reduces
  adoption regardless of feature quality.

## Related
- foundation → [[product-foundations]]
- spoke → [[pm-competitive-intelligence]] · [[pm-discovery-research]] · [[pm-enterprise-gtm]] · [[pm-metrics-analytics]] · [[pm-platform-api]] · [[pm-roadmap-strategy]] · [[pm-stakeholder-comms]]
