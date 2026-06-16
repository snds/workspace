---
name: ux-research-synthesis
description: >
  Mixed-method research design, synthesis methods, and the insight-to-design pipeline
  for complex enterprise SaaS problems. Use this skill when working on: selecting the
  right research method for a question, designing enterprise user interviews, contextual
  inquiry planning, usability test protocol design, jobs-to-be-done force analysis,
  opportunity/solution tree mapping (Teresa Torres), affinity diagramming, insight
  report writing, assumption mapping, How Might We statement creation, research-to-
  requirement pipelines, and resource-constrained research ("we only have 5 users and
  2 weeks"). Also trigger on: "what research method should I use for X", "how do I
  run this interview", "how do I synthesize these research findings", "we have analytics
  data but don't know why users are doing X", "how do I turn insights into design
  requirements", "what do I actually know vs. assume about our users", or any question
  about generating or making sense of evidence about user behavior and needs in an
  enterprise context.
aliases: [ux-research-synthesis]
tier: spoke
domain: design
hub: lead-ux-designer
prerequisites: [lead-ux-designer]
spec_version: "2.0"
---

# UX — Research Synthesis

Spoke skill in the `lead-ux-designer` network. Owns research method selection,
enterprise interview design, synthesis methods, and the insight-to-design pipeline.

Does not own: statistical experiment design (→ `ds-experimentation`), product analytics
instrumentation (→ `ds-product-analytics`), IA-specific research methods like card
sorting and tree testing (documented in `ux-information-architecture`). This spoke
owns the qualitative and mixed-method research layer that informs design decisions.

---

## Research Method Selection

The method must match the question. Mismatched methods produce data that looks useful
but doesn't answer the actual question. The failure mode: running a survey when you
need a depth interview, then using the survey data to make design decisions that the
survey wasn't designed to support.

### Generative research (problem space)

Use when you need to understand the problem, the user's mental model, their existing
workflow, their underlying goals, and what would need to change for them to adopt
a new solution.

| Method | When to use | What it produces | What it doesn't produce |
|--------|------------|-----------------|------------------------|
| **Depth interview** | Understanding mental models, motivations, workflow context, organizational dynamics | Rich behavioral data; "why" behind observed actions | Statistical confidence; how many users have this problem |
| **Contextual inquiry** | Understanding actual workflow (not self-reported workflow); catching the gap between what users say they do and what they actually do | Direct behavioral observation; workflow map; artifact inventory | User attitudes and preferences |
| **Diary study** | Longitudinal behavior; tracking how use patterns change over time; documenting infrequent or hard-to-observe events | Time-distributed behavioral data | Deep causal understanding |
| **JTBD force analysis** | Understanding what drives adoption or abandonment; mapping push/pull/anxiety/habit forces | Decision context; switch triggers | Behavioral frequency data |

### Evaluative research (solution space)

Use when you have a design and need to know whether it works for users.

| Method | When to use | What it produces |
|--------|------------|-----------------|
| **Usability testing** | Testing whether users can accomplish a task with a proposed design | Task success/failure; where confusion occurs; what vocabulary users use |
| **Cognitive walkthrough** | Expert review of a design against a user task; can be done without participants | Heuristic failure list; predicted user errors |
| **Expert review (heuristic evaluation)** | Quick audit against usability heuristics; identifies obvious problems before user testing | Heuristic violation list with severity ratings |
| **Tree testing** | Validating IA findability (see `ux-information-architecture`) | Findability rates; navigation confusion points |
| **First-click testing** | Validating that users click the right element first for a given task | First-click success rate; where users click when wrong |

### Quantitative methods

Use when you need to know how often something occurs, how many users are affected,
or whether a change made things better or worse.

| Method | When to use | What it doesn't tell you |
|--------|------------|--------------------------|
| **Survey** | Attitudinal data at scale; measuring satisfaction, feature importance, demographic distribution | Why — surveys report opinions, not behavior |
| **Analytics analysis** | What users actually do at scale; funnel analysis; feature adoption; time-on-task | Why — analytics reports behavior, not intent |
| **A/B testing** | Whether design A or B produces better measured outcomes | Whether either design is the right solution to the problem |

**Critical limitation**: quantitative data tells you what. Qualitative data tells you
why. You need both for actionable design decisions. Analytics that shows users
abandoning a form at field 7 tells you where the problem is — not what the problem is.
An interview that reveals users don't understand what "field 7" is asking for tells
you what the problem is. Together, you can fix it. Separately, you're guessing.

---

## Enterprise Interview Dynamics

Enterprise user interviews have specific dynamics that consumer product research
doesn't. Ignoring them produces misleading data.

### Multi-stakeholder organizational context

Enterprise users don't just have tasks — they have organizational roles, political
constraints, approval dependencies, and downstream colleagues affected by their
work. Understanding this context is essential to understanding the behavior.

An accounts payable specialist who appears to inefficiently triple-check every invoice
may be doing so because they were blamed for an error 6 months ago and now over-verify
to protect themselves. The interface design implication of this is very different from
"the user doesn't trust the system."

Always understand the organizational context of the behavior before diagnosing the UX problem.

### Separating behavior from opinion

Enterprise users have strong opinions about their tools. These opinions are useful data,
but they are not the same as behavioral data. The interview must collect both and
keep them separated.

Behavior: "Tell me about the last time you needed to do X. Walk me through what you
actually did."

Opinion: "What did you think of that process?"

Behavioral data is more reliable than opinion data because it is grounded in actual
events. Opinions reflect what users believe about their own behavior, which is often
idealized. "Tell me about the last time" produces more accurate behavioral data than
"What do you usually do."

### The champion problem

The person who scheduled the interview session is often not the target user. Enterprise
research access flows through champions (product managers, project leads, customer
success contacts) who have incentives to present positive users and favorable contexts.

Before starting any interview: verify the participant's actual role, their usage
frequency of the relevant features, and their task context. Ask: "How often do you
use [feature X] in a typical week?" If the answer is "rarely," you may have the wrong
participant for the question you're trying to answer.

### Remote enterprise research

Screen sharing in remote sessions reveals actual workflow context in ways that in-person
whiteboard interviews do not. Before asking what the user thinks or wants, ask them
to share their screen and show you the last time they performed the relevant task.

"Can you share your screen and show me what you were looking at when you last had to
[task]?" surfaces artifacts (the actual tool, the spreadsheet they use alongside it,
the Slack message they sent to get help) that reveal the real workflow.

### Interview recording ethics

Enterprise data is often sensitive. Before recording:
- Obtain explicit consent (verbal + written in the consent form)
- Clarify what the recording will be used for and who will see it
- Confirm data handling: will the recording be stored on company servers? Third-party
  tools (Dovetail, Otter.ai)? For how long?
- Note that some enterprise agreements restrict what can be recorded — check with legal

---

## Synthesis Methods for Complex Research

### Affinity diagramming

Purpose: bottom-up grouping of observations into emergent themes. The affinity diagram
should not start with pre-defined categories — it should start with raw observations
and let categories emerge from grouping.

Process:
1. One observation per sticky note (or digital card). Observation is specific and
   behavioral — not a design implication or a judgment. "User opened a second browser
   tab to look up a value from a different system" not "Users need cross-system data."
2. Group observations that feel related into clusters. Do not name the clusters yet.
3. Once grouping stabilizes, name each cluster with a single sentence that captures
   the theme. The name should be descriptive of the observation pattern, not a solution.
4. Identify super-clusters (clusters of clusters) for higher-level themes.

Failure mode: starting with categories ("Pain Points," "Workflow Issues," "Feature
Requests") and sorting observations into them. This imposes the analyst's frame before
the data has had a chance to reveal its own structure.

### Opportunity/Solution Tree (Teresa Torres)

Structure: a hierarchical map that moves from desired outcome → opportunities →
solutions → assumptions.

- **Desired outcome**: the measurable result you're trying to achieve (not a feature)
- **Opportunity**: a user need, pain point, or job-to-be-done that, if addressed, would
  contribute to the outcome
- **Solution**: a specific design or feature that addresses an opportunity
- **Assumption**: a belief about the user, the solution, or the market that must be true
  for the solution to work

Value: prevents solution anchoring. Teams that jump directly to solutions often discover
they've solved the wrong problem. The opportunity/solution tree forces explicit articulation
of which user opportunity a solution addresses before any solution is designed.

Enterprise use case: in PLM products, the desired outcome might be "reduce the time
to approve a product change order." The opportunities might be (1) approvers don't
know when a CO requires their attention, (2) approvers can't quickly assess the impact
of a change, (3) approvers need to consult colleagues before approving but the current
workflow doesn't support this. These are three different UX opportunities that might
require three different design solutions.

### Jobs-to-be-Done force analysis

The four forces:
1. **Push**: the current situation is painful enough to consider switching or changing
2. **Pull**: the new solution is attractive enough to pursue
3. **Anxiety**: fear about adopting the new solution (risk, learning curve, switching cost)
4. **Habit**: the inertia of the current workflow ("this is how we've always done it")

In enterprise, habit force is enormous. Enterprise users have learned workflows over
years. Change creates re-learning costs. A new design that doesn't acknowledge and
address habit force will see low adoption even if the new design is objectively better.

Design implication: for any significant workflow change, identify the habit force explicitly.
What does the user currently do? What learned behavior does the new design require them
to unlearn? What bridge is needed?

### Insight-to-design pipeline

Raw research data does not directly produce design requirements. It requires a
three-layer synthesis:

**Observation** → specific, factual account of what was seen or heard. Contains no
interpretation. ("The user spent 4 minutes searching for the 'Approve' button before
calling a colleague.")

**Insight** → a pattern across multiple observations with a hypothesis about why.
("Users consistently struggle to locate primary actions in record views, suggesting
that the current visual hierarchy does not support the task flow.")

**Design principle** → an actionable implication that gives direction to design decisions.
("Primary actions in record views must be anchored to a consistent location and visually
distinguished from secondary actions, regardless of the content in the view.")

**Design requirement** → a specific, testable requirement that a design must meet.
("The primary action button must appear in the top-right of every record view header,
and there must be at most one primary action per view.")

The failure mode: jumping from observations to design requirements without the insight
and principle steps. This produces designs that are responsive to symptoms rather than
root causes.

---

## Synthesis Output Formats

### Insight report

Structure: observation + pattern + implication — three layers, not a raw data dump.

```
Finding: [Observation cluster title]
Observations: [2–4 specific behavioral observations that form this cluster]
Pattern: [What this cluster reveals about user behavior or mental model]
Implication: [What this means for design — what we should do, avoid, or prioritize]
```

The implication section is the most important and the most commonly omitted. A finding
without an implication is a data point without a recommendation. The design team needs
to know what to do with the insight.

### How Might We statements

Convert problems into design opportunities. Format: "How might we [help user persona]
[accomplish something] without [undesirable trade-off]?"

Example: "How might we help approvers quickly assess the impact of a change order
without requiring them to navigate to multiple related records?"

HMW statements should be broad enough to allow multiple solutions (not "How might we
add an impact summary widget") but specific enough to be actionable (not "How might we
improve the approval workflow").

### Assumption mapping

A grid of: known vs. unknown × confirmed vs. unconfirmed (believe/disbelieve).

| | Confirmed | Unconfirmed |
|---|---|---|
| **Known** | Facts we have evidence for | Beliefs we hold but haven't tested |
| **Unknown** | Gaps we know we have | Unknowns we haven't yet identified |

Purpose: makes the team's assumptions about users visible and prioritizes which
assumptions need validation before investing in design or development.

High-risk assumptions are those in the "unconfirmed + unknown" quadrant. These are
beliefs the team doesn't know they're holding — the most dangerous assumptions.

### Decision documentation

Every design decision made from research evidence should be documented with a link
to the evidence. Format: "We decided to [do X] based on [finding Y from research Z].
This prevents [problem W] which we observed in [N] sessions."

This prevents tribal knowledge ("someone said users don't like tabs") from overriding
evidence ("in 8 usability test sessions, users consistently missed the tab navigation").

---

## Resource-Constrained Research

### The 5-user usability test

Jakob Nielsen's finding that 5 users uncover ~85% of usability problems in a single
round remains accurate for identifying qualitative problems. The constraint: 5 users
is not statistically significant. It is appropriate for:
- Finding obvious usability failures
- Generating hypotheses about problem areas
- Validating a specific flow before development

It is not appropriate for:
- Quantifying how many users have a specific problem
- A/B comparisons
- Validating a design change fixed a measured problem

5 users, 1 round. Iterate on the critical findings. Test again. 5 more users catches
the next layer of issues. Multiple rounds of 5 is more effective than 1 round of 20.

### Stakeholder interviews as a research input

Product managers, domain experts, and customer success managers have direct access to
user behavior at scale. They are not a substitute for user research — their observations
are filtered through organizational perspective. But they provide:
- Frequency estimates for problems ("We get 10 support tickets per week about this")
- Business context that affects design constraints
- Access to the user population for recruiting

Treat stakeholder interviews as triangulation, not primary evidence.

### Analytics as a research shortcut

Behavioral analytics data (feature usage, funnel drop-off, time-on-task) can shortcut
the discovery of where problems exist. This accelerates research planning — you can
enter qualitative sessions knowing where in the workflow to probe.

Analytics cannot explain why a problem exists. Never substitute analytics for qualitative
research on the mechanism of a problem. "Users abandon at step 3" is a research question,
not a research finding.

---

## Cross-Links

- `ux-information-architecture` — card sorting and tree testing (IA-specific research methods)
- `ds-experimentation` — quantitative experiment design; statistical power; A/B test protocol
- `ds-product-analytics` — analytics analysis; behavioral data as research input
- `pm-discovery-research` — PM and UX research coordination; JTBD at the product level; participant alignment

---

## References

- Teresa Torres — Opportunity/Solution Trees: https://www.producttalk.org/opportunity-solution-tree/
- Bob Moesta — Jobs-to-be-Done: https://www.jtbd.info/
- Steve Portigal — Interviewing Users
- Erika Hall — Just Enough Research
- Nielsen Norman Group — Research methods: https://www.nngroup.com/topic/user-research/
- Dovetail — Research repository and synthesis tooling: https://dovetailapp.com/
