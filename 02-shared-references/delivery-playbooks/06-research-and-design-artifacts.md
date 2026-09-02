---
title: Research & Design Artifacts — which one, in what order, authored how
status: canonical
date: 2026-07-21
tags: [research, artifacts, journey-map, jtbd, service-blueprint, user-story, use-case, user-flow, persona, selection, authoring, delivery]
---

# Research & design artifacts — which one, in what order, authored how

Fires when the request names or implies a UX-research / product artifact — **user journey (map),
customer journey, JTBD / jobs-to-be-done, service design, service blueprint, user story, use case,
user flow, task flow, site map, persona, experience map** — or asks **"which artifact do I need
for this?"** These words bind the deliverable: each is a *distinct* artifact with its own altitude,
audience, format, and place in the sequence. Producing the wrong one — or the right one authored the
wrong way — fails the request even if the content is correct.

This playbook is the **selector and the authoring contract.** It decides *which* artifact and *how*
to write it for a mixed audience. The deep methodology for building each lives in the linked spokes
(`ux-service-design`, `ux-interaction-design`, `ux-research-synthesis`, `pm-discovery-research`); this
file is what you load first to pick correctly and author to standard.

---

## The failure this prevents (read first)

Two founding anti-examples, both from real work:

1. **Cryptic cross-references instead of spelled-out detail.** A "workflow with screenshots" that
   labelled each gap with a code like `CORE-14` or `COL-02` — a reference into a register the reader
   doesn't have. The reader (a PM, an engineer, a manager) cannot act on `CORE-14`. **Every claim must
   be spelled out on the artifact itself**, in words, where it is read. An artifact is not an index into
   another document.

2. **Undefined domain jargon.** A diagram that used *"lab-dip"* with no explanation. A lab-dip is *a
   small swatch of fabric dyed to a target colour, sent by a mill so the brand can approve the exact
   shade before bulk production.* If a term like that appears without a plain-English gloss in context,
   the artifact is illegible to anyone outside the domain — which is most of its audience. **Define
   every insider term the first time it appears, in one plain sentence, right there.**

The audience for these artifacts is **UX designers, product managers, and front- and back-end
engineers** who do not share the domain's insider vocabulary. The [[01-audience-contract]] forward
test applies: someone one step removed must read it cold and understand it. If it needs tribal
knowledge or a lookup table, it is not finished.

---

## The artifact map

Eight artifacts, from highest altitude (why, strategic) to lowest (how, concrete). "Altitude" = how
zoomed-out the view is. "Persona-anchored" = written from a specific named user's point of view.

| Artifact | Answers | Altitude | Persona-anchored? | Author it when… | Form in one line |
|---|---|---|---|---|---|
| **Jobs-to-be-Done (JTBD)** | *Why* — what progress the person seeks, in what circumstance | Highest · strategic · solution-agnostic | **No** — job & context, not a character | Framing *what problem to solve*, before committing to a solution | *"When [situation], I want to [motivation], so I can [outcome]"* + the four forces + job map |
| **Persona** | *Who* — the archetypal user, their goals, context, frustrations | Strategic · a research-grounded character | Is the anchor | You need a shared, named stand-in for a segment to hang journeys/stories on | Card: name, role, goals, context, needs, pains, a real quote |
| **User journey map** | *What it's like* to pursue a goal across touchpoints over time | Macro · zoom-out · one persona | **Yes** | You need empathy + to find the high-impact moments across the whole experience | Matrix: stages across the top; lanes down the side (actions, thoughts, **emotion curve**, pains, touchpoints, channels, opportunities) |
| **Service blueprint** | *How the organization delivers* that experience — front + back stage + systems | System · zoom-out further | The journey is the top lane; then it's org-wide | The cause (or the fix) lives **behind the curtain** — hand-offs, systems, ownership, multi-channel | The journey on top; beneath it Frontstage / Backstage / Support, split by three lines |
| **User story** | *What* one user wants and the value of it | Mid · a thin feature slice | **Yes** | Slicing a validated need into sprint-sized, conversational value | *"As a [persona], I want [action], so that [benefit]"* + acceptance criteria + INVEST |
| **Use case** | *How*, step by step, an actor and the system reach a goal — **including everything that can go differently** | Low · concrete · solution-specific | Via its primary actor | A feature is genuinely complex — many alternate paths, multiple actors, regulated, high error cost | Title, actors, pre-conditions, numbered main flow, **alternate flows**, post-conditions |
| **User flow** | *What exact steps and choices* complete one task in the product — and where users drop off | Micro · zoom-in · one product | The typical user, product actions only, **no emotion** | Designing or diagnosing one task path before wireframes | Flowchart: entry → screen/action nodes → **decision diamonds** with labelled branches → exit |
| **Task flow** | The single simplest happy path through a task | Micro · linear · no branches | Typical user | A quick, linear sketch before elaborating into a full user flow | One straight line of steps, start → end, no decisions |

Adjacent artifacts you'll occasionally reach for: a **site map** (the static tree of a product's
pages/sections — structure, not sequence); an **experience map** (a journey map *not* tied to one
product — the whole life experience around a need); a **workflow** (see the flows spoke — process-
centric, includes system/staff/backend steps, not just what the user does).

---

## Order of operations — what follows what

These artifacts chain. Each is fed by the one(s) before it. You rarely make all of them; you make the
ones the question needs, but you make them **in dependency order** — never invent a journey map from
assumptions, never write a use case before the story it elaborates exists.

```
  RESEARCH                      interviews · field & diary studies · usability tests · analytics
  (never skip; never assume)         │
                                     ▼
  JTBD                          the job(s) — why, solution-agnostic       ── strategy
                                     │   "JTBD precedes both personas and stories"
                                     ▼
  PERSONA                       who has these jobs, in what context
                                     │
                                     ▼
  USER JOURNEY MAP              what it's like for that persona, with emotion   ── zoom OUT
                                     │   identifies the high-value moments
                     ┌───────────────┴───────────────┐
                     ▼                                ▼
  SERVICE BLUEPRINT (zoom OUT further)      TASK FLOW → USER FLOW (zoom IN)
  how the org delivers it —                the exact steps + decisions inside
  front/back stage + systems               one of those moments, in the product
                     │                                │
                     └───────────────┬────────────────┘
                                     ▼
  USER STORIES                  what to build, sprint-sized, from the user's value
                                     │   only the complex ones →
                                     ▼
  USE CASES                     how it works step-by-step + every alternate flow
                                     │
                                     ▼
  WIREFRAMES / WIREFLOWS → PROTOTYPE → BUILD → QA (against acceptance criteria) → COMPLIANCE
```

Key dependencies, stated plainly:
- **A journey map needs a persona and real research first.** No persona, no map — you'd be guessing.
- **A user flow is a deep-dive inside a journey-map moment.** The journey says *where* it matters; the
  flow details *how* that one task works. Capture both when you can — macro + micro.
- **A service blueprint extends a journey map downward.** The journey is literally its top lane; the
  blueprint then reveals the front-stage, back-stage, and support machinery that produces it.
- **A use case elaborates a story, not the reverse (usually).** Write the story first; add a use case
  only when the feature's alternate flows are too many/risky to leave in conversation. (Some teams
  invert this to fix foundational system behaviour first — treat order as context-dependent, but
  default to story-first.)
- **Everything traces back to a job and to observed behaviour.** If an artifact can't be traced to
  research, it's an assumption wearing a template.

---

## Selection guide — pick the right one

Start from what the request is actually trying to learn or decide:

**"Why would anyone want this / what problem are we really solving?"** → **JTBD.** Solution-agnostic.
Don't name a feature yet.

**"What is it like to be this user, and where do we help?"** → **User journey map.** One persona,
emotion curve, across channels/time.

**Journey map vs. user flow** — three questions (NN/g):
1. *Multiple channels?* Many channels → journey. One product → flow.
2. *Timeframe?* Days/weeks/months → journey. Minutes/hours → flow.
3. *Do you need emotion?* Yes → journey. Steps only → flow.

**Journey map vs. service blueprint** — the altitude test:
- The problem is the **customer's felt experience** and the fix is in one team's control → **journey map**.
- The problem is **behind the curtain** — broken hand-offs between teams, missing systems, unclear
  ownership, multi-department/vendor consistency — or you're **designing a whole service** → **service
  blueprint.** Rule of thumb: fixing the back stage often fixes the front stage; when the interesting
  cause is internal, blueprint it.

**"What exact steps complete this task / where do people drop off?"** → **User flow** (branching, with
decisions and exits). If you just need the single happy path, a **task flow** first.

**User story vs. use case** — the complexity test. Default to a **story** (lightweight, "a placeholder
for a conversation"). Escalate to a **use case** only when the feature has **5+ meaningful alternate
flows**, **multiple/third-party actors**, **regulatory documentation** needs, a **distributed team**
where conversation is expensive, or a **high cost of a missed path** (money, health, security). The
value of a use case is the alternate flows — if there aren't many, don't write one.

**"Evaluate the whole app / system"** → operate at **service-design altitude** (blueprint thinking):
approachable but system-level abstraction, front-to-back, not a per-screen critique. Name the
touchpoints, the actors (including the org's own staff and systems), and where the seams are.

---

## Per-artifact authoring specs

Concise templates and anatomy. Deep methodology is in the linked spokes.

### JTBD — Jobs-to-be-Done  → depth: [[pm-discovery-research]], [[ux-research-synthesis]]
- **Statement:** *"When [situation], I want to [motivation], so I can [expected outcome]."*
- Cover all three dimensions of the job: **functional** (the practical task), **emotional** (how it
  should make them feel), **social** (how it affects how others see them).
- Map the **job stages** (trigger → intermediate steps → end state) and check the **four forces** that
  govern switching: **Push** (pain of today) + **Pull** (draw of the new) drive change; **Anxiety**
  (risk of the new) + **Habit** (inertia of today) resist it. In enterprise, habit is enormous.
- **Not** persona-anchored — the circumstance outranks who the person is. Don't confuse a job with a
  feature ("track steps" is a feature; *"stay healthy despite a busy schedule"* is the job).

### Persona  → depth: [[ux-research-synthesis]]
- A **research-grounded** archetype, not a demographic cartoon. Name, role, context, goals,
  needs/motivations, frustrations, and a **real verbatim quote** from research.
- One persona per segment. It exists to anchor journeys, stories, and use-case actors to a real
  point of view — so those artifacts say "Alex, the print designer" not "the user."

### User journey map  → depth: [[ux-service-design]]
- **Matrix.** Columns = the chronological **stages** (specific and real, e.g. Define → Compare →
  Negotiate → Select — not vague placeholders). Rows = the lanes, in this order:
  - **Header band:** the persona; the scenario, their goal, and expectations.
  - **Actions** (what they do) · **Thoughts** (what they ask themselves) · **Emotion curve** (the
    signature line of highs and lows — the layer that makes it a journey, not a flow) · **Pain points**
    · **Touchpoints** · **Channels** · **Opportunities** (each tied to a specific pain).
- From the **user's** perspective, never the company's. Backed by research, never assumptions. It's a
  living artifact — versioned, revisited — not a poster.

### Service blueprint  → depth: [[ux-service-design]]
- The **journey map's continuation downward** into the organization. Columns are the customer's steps
  (from the journey); lanes top-to-bottom, separated by three lines:
  - **Physical evidence** (what the customer sees/touches at each step) *[optional top lane]*
  - **Customer actions**
  - **── Line of interaction ──** (where the customer touches the org)
  - **Frontstage** (org actions the customer *sees* — staff and customer-facing tech/self-service)
  - **── Line of visibility ──** (the curtain: above = seen, below = unseen)
  - **Backstage** (staff actions the customer *doesn't* see)
  - **── Line of internal interaction ──**
  - **Support processes / systems** (tech, databases, vendors, back-office)
  - Add-on lanes as fidelity warrants: **time, emotion, metrics, pain points**. Single arrow = one-way;
    double arrow = a two-way exchange/dependency.
- One blueprint per scenario/persona/channel (a business has many). Blueprint the **real** process, not
  the idealized one — "how things are supposed to be done is rarely how they're done."

### User story  → depth: [[pm-discovery-research]]
- **Template:** *"As a [persona], I want [observable action], so that [benefit the user values]."*
- **Acceptance criteria:** 3–7 testable conditions agreed before the sprint, commonly *Given [context],
  When [action], Then [outcome].*
- **INVEST:** Independent · Negotiable · Valuable · Estimable · Small (fits a sprint) · Testable.
- It is deliberately lightweight — "a placeholder for a conversation, not a specification." If it
  doesn't fit on a postcard, it's not a story. Ground it in observed behaviour, not speculation; never
  skip acceptance criteria.

### Use case  → depth: [[pm-discovery-research]]
- **Structure:** Title (imperative goal) · Primary actor · Secondary actors · Pre-conditions ·
  **Main flow** (numbered steps, present tense) · **Alternate flows** (numbered branches — errors,
  exceptions, edge paths — *this is the point of the artifact*) · Post-conditions.
- Solution-specific and system-centric. Write one only when complexity earns it (see the complexity
  test). Don't leave alternate flows trapped in conversation; don't write use cases for everything.

### User flow (and task flow)  → depth: [[ux-interaction-design]]
- **Directional flowchart** read start → finish:
  - **Entry point(s)** (multiple is normal) · **screen/state nodes** (rectangles) · **action nodes**
    · **decision diamonds** phrased as questions with **labelled branches** ("Logged in? — yes / no")
    · **arrows** for direction · **exit points** (successful completion *and* drop-off).
  - Standard shapes: oval = start/end, rectangle = screen/step, diamond = decision.
- Map **all outcomes**, not just the happy path — the drop-offs are where the insight is. Product
  actions only; **no emotion layer** (that belongs on the journey map). A **task flow** is the simpler
  cousin: one straight linear path, no branches — sketch it first, then elaborate.
- A **workflow** ≠ a user flow: a workflow is process-centric and includes the system/staff/backend
  steps; a user flow shows only what the *user* does. If the request is "the whole process including
  the system side," that's a workflow (or a service blueprint), not a user flow — say so.

---

## Authoring rules (non-negotiable, every artifact)

1. **Spell it out where it's read.** No code-references, ticket-IDs, or "see register" pointers as the
   content of a cell or node. If the finding is "there's no screen to request a fabric sample," write
   *that* — not `US5`. The artifact is self-contained.
2. **Define every domain term in plain English, in context, the first time.** *Lab-dip* → "a dyed
   fabric swatch a mill sends to approve the exact colour before bulk." *BOM* → "bill of materials —
   the list of every material and part that goes into a product." No unexplained insider words.
3. **Match altitude to the artifact.** User-level artifacts (journey, story, use-case actor, flow) are
   written from a **named persona's** point of view — "Alex needs…", not "the user needs…". Whole-
   system evaluation is done at **service-design altitude** — approachable, but front-to-back across
   the org, not a per-screen critique.
4. **Ground in research, not assumptions.** Every artifact traces to observed behaviour, a real quote,
   or data. An untraceable artifact is a guess in a template — label speculation as speculation.
5. **One artifact, one question.** A journey *and* a flow is two artifacts, not a hybrid. A journey
   map that lost its emotion curve has become a flow; a flow carrying emotion has muddied itself.
6. **Pass the forward test.** [[01-audience-contract]] — a PM/engineer/manager one step removed reads
   it cold and gets it. Judge legibility at the size it's actually viewed ([[10-perception-integrity]]).
7. **Living, versioned, self-contained.** Title, date, version; opens standalone ([[artifact-standards]]).

---

## Pre-delivery checklist

0. Context profile resolved and cited? ([[00-context-profiles]] — always first.)
1. **Right artifact** for the question — ran it through the selection guide (why→JTBD, feel→journey,
   internal-cause→blueprint, steps→flow, build→story/use-case)?
2. Authored at the **right altitude** — persona-named at user level, service-design abstraction at
   system level?
3. **Everything spelled out** on the artifact — zero cryptic references; every domain term defined?
4. **Grounded in research**, not assumptions?
5. If it's a journey — is the **emotion curve** present? If a flow — are **decisions and drop-offs**
   shown, not just the happy path? If a blueprint — are the **three lines** and the back-stage present?
6. Forward test passed; legible at viewing size?

---

## Cross-links

- [[02-diagrams-and-flows]] — the visual notation/medium rules for any of these when rendered as a diagram
- [[01-audience-contract]] — the forward test and three altitudes; the audience contract this enforces
- [[ux-service-design]] — journey mapping + service blueprint methodology (deep)
- [[ux-interaction-design]] — user flows, task flows, workflow vs. user flow (deep)
- [[ux-research-synthesis]] — research methods, JTBD force analysis, personas, insight pipeline (deep)
- [[pm-discovery-research]] — JTBD at product scale, user stories, use cases (deep)
- [[lead-ux-designer]] · [[lead-product-manager]] — the hubs these spokes hang from

## References
- Nielsen Norman Group — *Journey Mapping 101*, *User Journeys vs User Flows*, *Service Blueprinting*
- UXtweak — User Journey Map, Jobs-to-be-Done, Service Design & Blueprint guides + examples
- uxcam / UX Magazine — User Stories vs Use Cases
- Optimizely, Matomo — User Flow definitions + worked examples
- Christensen / Ulwick / Moesta (JTBD) · Cohn (stories, INVEST) · Cockburn / Jacobson (use cases)
