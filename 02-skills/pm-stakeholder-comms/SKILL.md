---
name: pm-stakeholder-comms
description: >
  Executive communication, steering committee management, cross-functional
  alignment, and product decision frameworks for enterprise SaaS PMs. Use
  this skill whenever the conversation touches: preparing an executive
  presentation, writing a product 1-pager or briefing doc, running or
  preparing for a steering committee, navigating DACI/RACI decision rights,
  distinguishing reversible vs. irreversible decisions, managing escalation,
  or aligning cross-functional stakeholders on a product direction. Also
  trigger on: "executive communication", "1-pager", "briefing doc", "BLUF",
  "steering committee", "DACI", "RACI", "stakeholder alignment",
  "decision rights", "escalation", "executive sponsor", "presenting to
  leadership", "Amazon memo", "6-pager", "asking for approval".
aliases: [pm-stakeholder-comms]
spec_version: "2.0"
---

# PM Stakeholder Communications

Specialist skill for executive communication, steering committees, and
cross-functional alignment. Part of the enterprise SaaS product management
skill network.

---

## Domain Boundary

This skill owns **communication and alignment strategy** — how to get the
right decisions made by the right people at the right time.

- **What data to put in the executive presentation** → `pm-metrics-analytics`
- **The roadmap content being presented** → `pm-roadmap-strategy`
- **Discovery evidence supporting a recommendation** → `pm-discovery-research`
- **Competitive context for a steering committee** → `pm-competitive-intelligence`
- **Data visualization and analytical evidence** → `ds-executive-storytelling`

---

## DACI Framework

DACI clarifies who does what on a decision. It's more useful than RACI for
product decisions because it distinguishes between who drives the work and
who approves the outcome.

| Role | Definition | In Practice |
|------|------------|-------------|
| **Driver** | Owns the process and ensures a decision gets made. Not necessarily the decision-maker. | PM is usually the Driver for product decisions |
| **Approver** | The one person who makes the final call. Singular. If there are two Approvers, there is no Approver. | Product leader, GM, or exec sponsor |
| **Contributors** | People who provide input, expertise, or feedback. Have voice but not a vote. | Engineering, design, sales, legal, finance |
| **Informed** | People who need to know the outcome but don't influence it. | Downstream teams, CS, support |

### When to Use DACI vs. RACI

DACI is preferable for **one-time decisions with an endpoint** (choosing an
architecture, approving a feature direction, setting a pricing tier).

RACI is preferable for **ongoing processes with roles** (who is responsible
for maintaining the integration spec, who is accountable for the quarterly roadmap review).

### Resolving DACI Conflicts

**"Two Approvers" problem**: When two people both believe they are the
Approver, decisions stall or oscillate. Resolution:
1. Name the conflict explicitly: "We have two people who believe they're
   the Approver. We need to resolve this before the decision can be made."
2. Escalate to the shared manager with the conflict named, not the
   underlying decision.
3. Don't try to make the decision while the conflict exists — it will be
   relitigated.

**"Contributor who acts like an Approver" problem**: A stakeholder who is
a Contributor but has enough organizational power to block the Approver.
Resolution: Get explicit alignment from the Approver on the DACI assignments
before the decision process begins. Verbal alignment prevents retroactive
blocking.

---

## Executive Communication Formats

### The 1-Pager

**Use for**: Decisions that need leadership input or approval; presenting
a product direction; summarizing a discovery finding; making a recommendation.

**Format**:
```
## [Feature / Initiative Name]
**Date** | **Author** | **Decision Needed By**

### The Problem
[2-4 sentences. The customer problem or business problem this addresses.
Who is affected. Why it matters now.]

### Proposed Direction
[2-4 sentences. What you're proposing. Not a full spec — the direction.
What you're committing to exploring vs. what you're recommending.]

### Tradeoffs
[Bullets. What this trades off against. What alternatives were considered
and why this direction was chosen. What risks exist.]

### The Ask
[One clear request. Approval? Input on a specific question? Resources?
Be explicit about what you need from the reader.]
```

**Rules**:
- One page. Not "approximately one page." One page.
- No background section. Start with the problem.
- The ask is singular. Multiple asks dilute attention and create waffling.
- Write for someone who hasn't been in the weeds with you.

### The Briefing Doc (BLUF Format)

**Use for**: Asynchronous executive updates; context-setting before a meeting;
giving decision-makers a pre-read.

**BLUF = Bottom Line Up Front.** Military communication practice: lead with
the conclusion, follow with supporting context. Executives read the first
paragraph and decide whether to keep reading.

**Format**:
```
## Subject Line: [Situation + Recommendation in 10 words]

**Bottom Line**: [The conclusion, recommendation, or key finding. 2-3
sentences maximum. This should be standalone — if an executive reads only
this, they understand the essential.]

---

### Situation
[What's happening. Current state. Data.]

### Complication
[What changed or what the problem is. Why action is required.]

### Resolution (Options / Recommendation)
[What to do. Options if relevant, with a clear recommendation.]

### Appendix (optional)
[Supporting data, full analysis, detailed evidence — for those who want
to go deeper. Not required reading for the decision.]
```

**What BLUF prevents**: The "building to the conclusion" presentation style
where executives sit through 10 minutes of context before hearing what you
actually want. By the time you get there, they've formed their own opinions
based on the framing, or they've mentally checked out.

### The Amazon-Style 6-Page Narrative

**Use for**: Major strategic decisions — product strategy shifts, significant
resource requests, platform investment justifications.

**Structure** (6 pages max):
1. **Statement of the problem** (the customer/business problem, with evidence)
2. **Proposed solution** (the approach, with rationale)
3. **Alternatives considered** (why this approach, not others)
4. **Dependencies and risks** (what must be true, what could go wrong)
5. **Resource requirements** (what this will cost in people, time, money)
6. **Success criteria** (how we'll know it worked)

**The silent reading rule**: Amazon reads the memo silently for the first
15–20 minutes of the meeting. No presenter walking through slides. The reader
meets the argument in its clearest form.

**Why this format produces better decisions**:
- Writing 6 pages forces clarity of thought. Bullets hide unclear thinking.
- Readers engage with the argument, not the presenter's confidence.
- The structure forces explicit treatment of tradeoffs and alternatives.

---

## Steering Committee Management

### What a Steering Committee Is (and Isn't)

A steering committee is a decision-making body for cross-functional or
cross-organizational decisions that can't be resolved at a lower level.

It is **not**:
- A status update meeting
- A venue to present work for information only
- A place where decisions are made by the loudest voice
- A meeting that happens "because the calendar says so"

### How to Prepare

**Two weeks before**:
- Identify the decisions the committee needs to make. If there are no decisions,
  cancel the meeting.
- Ensure the Approver(s) are present. A steering committee without the
  Approver is theater.
- Distribute pre-read material (1-pager or briefing doc) with enough lead
  time for async review.

**One week before**:
- Have 1:1 conversations with key participants. Surface objections, concerns,
  and questions before the room. Never be ambushed in the meeting.
- Identify who might block and why. Have a response ready.
- Confirm the decision-maker is prepared to decide, not explore.

**The day before**:
- Confirm the meeting is still happening and participants have read the pre-read.
- Identify 2-3 specific questions you'll ask the committee (forcing function
  for engagement).

### How to Run It

- Open with the decision to be made. Not with background. Not with a recap
  of the pre-read. The committee has read it. Start with: "Today we need to
  decide X. Here are the options."
- Time-box discussion. If discussion goes long, that's a signal the decision
  isn't ready — not a signal to talk longer.
- Name the decision explicitly at the end: "We've decided X. [Name] will
  do Y by [date]." Say it out loud before leaving the room.
- Follow up with written confirmation within 24 hours.

### How Not to Be Ambushed

The most common steering committee failure: a stakeholder raises a new
objection in the meeting that the PM hasn't addressed, the committee stalls,
and no decision is made.

Prevention: pre-meeting 1:1s are not optional. Any objection that surfaces
in a meeting could have been surfaced beforehand. Make it easy for stakeholders
to raise concerns privately before the meeting — they'll often be more honest
in 1:1s than in front of leadership.

---

## Decision Rights: Reversible vs. Irreversible

Jeff Bezos's Type 1/Type 2 framework is operationally useful for calibrating
how much process a decision deserves.

| Decision Type | Characteristics | Right Process |
|--------------|----------------|---------------|
| **Type 1 (irreversible)** | Can't easily be undone. High cost of being wrong. Affects many people or long time horizons. | Slow down. Get more input. Full approval process. 6-pager. |
| **Type 2 (reversible)** | Can be undone or changed. Cost of being wrong is low. Affects a bounded scope. | Move fast. Small group or individual decides. Document and move. |

**The failure mode in enterprise**: Treating Type 2 decisions like Type 1.
This creates organizational constipation — every decision feels expensive,
speed drops, and the team learns to slow down on everything.

**The PM discipline**: Consciously label decisions before starting the
approval process. "This is a Type 2 decision — we can change it in 6 weeks
if it doesn't work. I'm not going to steering committee for this."

Examples:
- Changing the label on a button: Type 2
- Deprecating an API version with enterprise customer impact: Type 1
- A/B testing a new onboarding flow: Type 2
- Changing the pricing model: Type 1
- Reordering items in a navigation menu: Type 2
- Committing to a platform architecture: Type 1

---

## Managing Up with Data

The PM who presents data without a recommendation is not managing up — they
are delegating the thinking to their manager.

### The Decision Hierarchy

1. **Data** (what happened)
2. **Insight** (what it means)
3. **Recommendation** (what to do about it)
4. **Ask** (what you need from the executive)

Present all four, in that order. Executives who receive only data respond
by asking for your recommendation. Executives who receive a recommendation
respond by evaluating it.

**Common failure**: "Here's the data, I thought you'd want to see it."
This is not useful. "Here's the data. It tells us X. I recommend Y. I need
your approval on Z to proceed." This is useful.

### Framing Data as Evidence for a Recommendation

Data is evidence, not a conclusion. The PM's job is to:
1. Choose the right data (not all available data)
2. Interpret it correctly (name the implication, not just the number)
3. Connect it to a specific recommendation
4. Acknowledge what the data doesn't tell you

---

## Cross-Functional Alignment

### Informing vs. Aligning

**Informing**: Telling stakeholders what's happening. Necessary but not
sufficient for alignment. People who've been informed can still block or
disengage.

**Aligning**: Creating genuine shared understanding of the problem, the
direction, and their role in it. People who are genuinely aligned become
active contributors.

The difference is conversation, not broadcast. Alignment requires dialogue.
A Slack message, a Confluence page, and a meeting recap are information
delivery. A 30-minute conversation where you ask "what concerns do you have
and how do we address them?" is alignment work.

### Escalation Discipline

**When to escalate**: When a decision is blocked, you've exhausted team-level
resolution, and the cost of further delay exceeds the cost of using leadership
bandwidth.

**When not to escalate**: When you haven't had the direct conversation with
the blocker first. Never escalate without first giving the person an
opportunity to resolve it 1:1.

**How to escalate without creating org debt**:
- Escalate the decision, not the person. "We need to decide X and we're
  stuck" rather than "Person Y is blocking us."
- Come with a proposed resolution, not just the conflict. Executives want
  to approve a direction, not adjudicate a dispute.
- Keep the escalation minimal: one email, one meeting. If it takes more than
  that, the decision isn't clear enough.

---

## Common Failure Modes

| Failure Mode | What Happens | How to Prevent |
|-------------|-------------|---------------|
| Asking for permission instead of input | PM presents options without a recommendation; executive says "you tell me" — decision stalls | Always present a recommendation; ask for input on specific concerns, not on the decision itself |
| Presenting options instead of a recommendation | Three equally-presented options signal you haven't done the analysis to choose | Choose one. State it. Acknowledge the tradeoffs. Make the case. |
| Ambushed in steering committee | Stakeholder raises a new objection; committee stalls | Pre-meeting 1:1s are not optional. Surface objections before the room. |
| The "data dump" exec update | 15 slides of charts with no narrative | Lead with BLUF. Data supports the narrative; it doesn't replace it. |
| Conflating approval with alignment | Leadership approved it, but CS/sales/engineering didn't know — execution is chaotic | Approval is not the same as alignment. Broadcast decisions to all Informed parties immediately. |
| DACI confusion | Multiple people believe they're the Approver; decisions get relitigated | Explicit DACI assignments at the start of any significant initiative |

---

## Cross-Hub References

- **Analytical evidence for executive presentations** → `ds-executive-storytelling`:
  PM owns the recommendation framing; DS owns the visualization and analytical rigor
- **Metrics and data for steering committee materials** → `pm-metrics-analytics`
- **Roadmap presentations** → `pm-roadmap-strategy`: the content being
  communicated through these formats
- **Launch approval** → `pm-enterprise-gtm`: the 1-pager format is the
  standard artifact for launch readiness approval
