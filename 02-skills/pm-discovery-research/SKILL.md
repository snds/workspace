---
name: pm-discovery-research
description: >
  Enterprise B2B discovery, customer interviewing, Jobs-to-be-Done, research
  synthesis, and opportunity sizing for enterprise SaaS. Use this skill
  whenever the conversation touches: planning or running customer interviews,
  multi-stakeholder interview dynamics, separating champion/buyer/user
  perspectives, Jobs-to-be-Done frameworks at enterprise scale, continuous
  discovery and opportunity trees, assumption mapping, affinity diagramming,
  JTBD force analysis, opportunity sizing without TAM/SAM/SOM theater,
  generative vs. evaluative research decisions, or any question about how
  to reduce uncertainty cheaply before committing capacity. Trigger on:
  "customer discovery", "user research", "JTBD", "jobs to be done",
  "opportunity sizing", "customer interviews", "research synthesis",
  "continuous discovery", "assumption mapping", "research methodology".
---

# PM Discovery & Research

Specialist skill for enterprise B2B discovery and customer research. Part of
the enterprise SaaS product management skill network.

---

## Domain Boundary

This skill owns **how to reduce uncertainty before building** — research
methodology, interview craft, synthesis, and opportunity sizing.

- **What to build next given known opportunities** → `pm-roadmap-strategy`
- **How to measure outcomes from what was built** → `pm-metrics-analytics`
- **How to communicate research findings to executives** → `pm-stakeholder-comms`
- **Competitive landscape research** → `pm-competitive-intelligence`

---

## Enterprise Interview Dynamics

Enterprise interviews are not consumer research interviews. The organizational
complexity changes everything.

### The Multi-Stakeholder Problem

Any enterprise workflow involves multiple roles with different (sometimes
conflicting) perspectives on the same problem. Interviewing only one role
produces a partial picture that will generate the wrong solution.

**Minimum coverage for a meaningful enterprise discovery:**

| Stakeholder | What They Know That Others Don't | Risk of Skipping |
|-------------|----------------------------------|-----------------|
| End user (IC) | Actual workflow friction, workarounds, what breaks | Build features no one uses because the real pain is invisible |
| Champion (manager/director) | Team-level priorities, internal politics, what they're accountable for | Miss the organizational problem behind the task-level problem |
| Economic buyer (VP+) | Strategic context, why this matters to the business, budget justification | Build technically right but strategically irrelevant |
| IT/Admin | Integration constraints, compliance requirements, deployment friction | Ship a product that can't be adopted |

Never aggregate across these roles. A quote from an end user is not evidence
for a buying decision. A buyer's priorities are not evidence for workflow design.

### Separating the Voices

In practice, a customer-facing interview often has a mix of roles in the room.
Techniques to maintain clarity:

- **Ask role-specific questions**: "Walk me through your day when X happens"
  produces different answers from an IC than from their manager.
- **Name the hat**: "I want to understand the business case — can I ask you to
  speak as the person who'd have to justify this budget?"
- **Follow-up on "we"**: When someone says "we need to do X," ask "who is the
  person who actually does that step?"
- **Observe, don't just ask**: If you can watch someone do the workflow, you'll
  catch the workarounds they don't mention because they've normalized them.

### Champion Capture Anti-Pattern

Champions are motivated to support you succeeding. They will tell you the
things they think you need to hear, emphasize problems that align with what
they believe you're already building, and under-report friction with the
proposed approach. This is not dishonesty — it's social dynamics.

Mitigations:
- Always interview users the champion doesn't select for you
- Ask for introductions to skeptics explicitly: "Who on your team is most
  resistant to this change and why?"
- Triangulate champion claims with usage data, support tickets, and
  independent user interviews

---

## Jobs-to-be-Done at Enterprise Scale

JTBD at consumer scale: "I hire this app to track my workouts."
JTBD at enterprise scale: the jobs are nested, political, and distributed
across roles.

### The Three Job Levels

| Level | Description | Enterprise Example |
|-------|-------------|-------------------|
| Functional job | The practical task to be done | "Get approved BOM data into the supplier portal before the cutoff" |
| Emotional job | How the person wants to feel while doing it | "Confident that I haven't introduced errors I'll be blamed for" |
| Social job | How they want to be perceived by others | "Look competent to my VP on the data readiness review" |

Enterprise products often over-index on functional jobs and under-invest in
emotional and social jobs. The emotional job (confidence, control, reduced
anxiety) is frequently what drives adoption or resistance.

### JTBD Force Analysis

Why do people adopt (or not adopt) a new way of working:

```
PUSH                           PULL
(problems with current state)  (attraction to new solution)
─────────────────────────────  ─────────────────────────────
Pain with existing workflow    Hoped-for improvement
Failing metrics / visibility   Reputation benefit
Risk exposure                  Peer adoption signal

        ANXIETY                        HABIT
        (fear of new solution)         (inertia of current state)
        ──────────────────────         ─────────────────────────
        "Will this break my process?"  "This is how we've always done it"
        Learning curve                 "Not broken enough to change"
        Data migration risk            Political investment in current tools
```

Strong adoption requires: **Push + Pull > Anxiety + Habit**

Use this force analysis in synthesis to assess whether a solution idea is
structurally positioned to overcome the inertia you found in research.

---

## Continuous Discovery (Teresa Torres Framework)

### Opportunity/Solution Tree

The Opportunity/Solution Tree is the operating structure for continuous
discovery:

```
Desired Outcome
└── Opportunity 1 (unmet need, pain point, desire)
│   ├── Opportunity 1a (sub-opportunity)
│   └── Opportunity 1b
│       └── Solution Ideas
│           └── Experiment / Assumption Test
└── Opportunity 2
    └── ...
```

- **Desired Outcome**: A business metric the team is responsible for moving.
  Not a feature. Not a project.
- **Opportunity**: A customer problem, pain, or unmet need discovered through
  research. Opportunities are customer language, not PM language.
- **Solution**: A specific product idea that addresses an opportunity.
  Solutions are PM/designer language.
- **Experiment**: The cheapest way to test the most critical assumption in
  the solution.

The tree makes explicit what many teams do implicitly wrong: jumping from
business outcome directly to solution ideas, skipping the opportunity layer.

### Continuous Discovery Cadence

Weekly touchpoint with at least one customer (interview, usability session,
or shadowing). The bar is contact, not comprehensiveness. The purpose is to
maintain a current, evidence-grounded opportunity tree rather than running
a big discovery sprint every quarter and then going dark.

In enterprise SaaS, this is harder than consumer: customers are busy,
access is mediated by CSMs, and sales will want to join calls. Negotiate
standing access agreements with CSMs. Run 20-minute "quick pulse" sessions.
Use support tickets and NPS verbatims as async signal between sessions.

---

## Assumption Mapping

Before building or committing to a roadmap item, surface the assumptions it
rests on.

### The Assumption Map Grid

```
                   KNOWN              UNKNOWN
              ┌───────────────────┬──────────────────┐
  BELIEVE     │  Safe zone.       │  Discovery gap.  │
  (we think   │  Proceed.         │  Validate        │
  it's true)  │                   │  cheaply.        │
              ├───────────────────┼──────────────────┤
  DISBELIEVE  │  Risk zone.       │  Fog of war.     │
  (we think   │  Design around    │  Prioritize      │
  it's false) │  the constraint.  │  illumination.   │
              └───────────────────┴──────────────────┘
```

**Most dangerous quadrant**: Unknown + Believe. These are assumptions the
team doesn't know they're making. Structured assumption surfacing (asking
"what has to be true for this to work?") moves items from unknown to known.

### Critical Assumption Test

Not all assumptions are equal. Weight by:
1. **Desirability**: Do users actually want this job done? Would they value this solution?
2. **Viability**: Does this make business sense? Will buyers pay? Will sales sell it?
3. **Feasibility**: Can we build it with available technology and capacity?
4. **Usability**: Can users accomplish the job with this design?

Test the most dangerous assumption first — the one that, if wrong, invalidates
the whole initiative. Don't test the easy ones.

---

## Synthesis Methods

### Affinity Diagramming

Use after a batch of interviews to find patterns:

1. One observation per sticky (digital or physical). Observations, not interpretations.
2. Group silently first — let patterns emerge without discussion anchoring.
3. Label groups with insight statements ("users compensate for X by doing Y manually"),
   not category labels ("workflow issues").
4. Tension groups are valuable: when observations cluster around a contradiction,
   you've found a structurally interesting opportunity.

**Enterprise-specific note**: Tag each observation with the role and company
segment of the person who said it. Pattern strength is different when it comes
from end users vs. buyers, or from SMB customers vs. enterprise accounts.

### JTBD Interview Transcript Coding

When coding interview transcripts for JTBD:

- Highlight job statements: "I need to [motivation] so that [outcome]"
- Flag forces: mark P (push), Pu (pull), A (anxiety), H (habit)
- Note non-use workarounds: things people do in another tool or manually that
  your product should handle
- Mark "unmet jobs": jobs customers have that no current solution serves well

### Synthesis Anti-Patterns

- **Theming too quickly**: Grouping observations by topic (e.g., "reporting",
  "onboarding") produces a feature list, not insight. Group by need, not topic.
- **Loudest voice dominance**: A single emotional story outweighs ten quieter
  data points in synthesis sessions. Weight by frequency and segment, not
  impressiveness.
- **The HiPPO synthesis problem**: If a senior stakeholder is in the synthesis
  session, their groupings anchor the room. Run synthesis without them; share
  findings after.

---

## Opportunity Sizing for Enterprise

TAM/SAM/SOM is investor theater for enterprise product decisions. You need to
answer a different question: "If we solve this, how much impact does it have
on outcomes we care about?"

### Enterprise Opportunity Sizing Framework

**1. Account coverage**: What percentage of accounts in the target segment
have this problem? Source: discovery interviews, support data, CSM surveys.

**2. Workflow coverage**: Within an account, what percentage of users or
workflows are affected? A problem that affects 2 power users per account is
not the same as one that affects the daily workflow of 200 users.

**3. Problem severity**: How much does this friction cost the customer?
Quantify in their terms: time lost per week, error rate, manual steps, risk
exposure. This becomes the value narrative.

**4. Wedge value**: Does solving this problem create leverage — expanding
usage, increasing switching cost, enabling adjacent opportunities? The
wedge is often more valuable than the direct problem.

**Sizing formula (directional, not precise):**
```
Accounts affected × Revenue per account × Churn risk reduction
+ Accounts affected × Expansion signal (upsell/cross-sell)
+ New logo conversion lift (if it's a sales blocker)
```

This is not a precise calculation. It is a forcing function for honest
conversations about relative priority.

---

## Generative vs. Evaluative Research

| Type | Question It Answers | Methods | When to Use |
|------|---------------------|---------|-------------|
| Generative | What problems exist? What jobs are being done? What's the opportunity? | JTBD interviews, contextual inquiry, diary studies, support ticket analysis | Before deciding what to build; when the opportunity space is unclear |
| Evaluative | Does this solution work? Can users accomplish the job with this design? | Usability testing, prototype testing, A/B experiments, first-click tests | After a solution is defined; to reduce execution risk before full build |

Most enterprise product teams do too much evaluative and not enough generative.
Evaluating a solution to the wrong problem is waste. The best evaluative
research is worthless if the generative work was skipped.

**The 70/30 rule (approximate)**: In a healthy discovery practice, ~70% of
research effort should be generative (understanding problems) and ~30%
evaluative (testing solutions). Most teams are inverted.

---

## Interview Anti-Patterns in Enterprise

| Anti-Pattern | What It Looks Like | Why It Fails |
|--------------|--------------------|--------------| 
| Leading questions | "Would it help you if we added a dashboard here?" | Customers say yes to features. Doesn't validate the job or the pain. |
| Solution fishing | "We're thinking of building X — does that sound useful?" | Confirms your solution rather than discovering the job. |
| HiPPO capture | Interviewing only the contacts your sales team provides | Sales selects advocates. You need critics too. |
| Abstract value questions | "How important is data accuracy to you?" | Everyone says it's very important. Useless. Ask about specific incidents instead. |
| Conflating role perspectives | Asking a manager "how do your team members use this?" | They don't know the actual workflow. Talk to the people who do it. |
| Premature why | Asking "why" immediately after a statement | Produces rationalization, not root cause. Follow with "tell me more" and let the story emerge. |
| Feature shopping | Asking which of three features they'd want most | Produces a forced-rank wish list, not job discovery. |

---

## Cross-Hub References

- **Experiment design / statistical validation** → `ds-experimentation`: when
  qualitative discovery points to a hypothesis suitable for quantitative testing
- **Translating opportunity findings into a roadmap** → `pm-roadmap-strategy`
- **Communicating research findings to executives** → `pm-stakeholder-comms`
- **Competitive discoveries from interviews** → `pm-competitive-intelligence`
