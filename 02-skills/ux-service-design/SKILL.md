---
name: ux-service-design
description: >
  Service design methodology for enterprise SaaS. Staff/principal IC level. Use this
  skill when working on: service blueprinting, multi-touchpoint experience mapping,
  customer journey mapping vs. blueprinting decisions, back-stage actor mapping,
  service recovery design, moments of truth mapping, and enterprise onboarding as a
  multi-actor service. Also trigger on: "who else is involved in this workflow", "what
  happens between the product and the next step", "how does support fit into this",
  "what does onboarding look like end to end", "what are the moments that matter
  most", or any question where the scope of the design problem extends beyond the
  product UI itself to the surrounding organizational processes and touchpoints.
hub: lead-ux-designer
aliases: [ux-service-design]
tier: spoke
domain: design
prerequisites: [lead-ux-designer]
spec_version: "2.0"
---

# UX — Service Design

Spoke skill in the `lead-ux-designer` network. Owns service blueprinting, multi-touchpoint
experience design, journey mapping methodology, back-stage actor mapping, service recovery,
moments of truth, and enterprise onboarding as a service.

Does not own: the UI design within any single touchpoint (route to the relevant spoke —
`ux-interaction-design`, `ux-information-architecture`, etc.), user research methods for
validating journeys (→ `ux-research-synthesis`), or content strategy across touchpoints
(→ `ux-writing`). This spoke owns the system view: the design of the full service
including the organizational actors and processes the product depends on.

---

## Service Blueprinting

### What a service blueprint is

A service blueprint is the authoritative service design artifact. It maps the complete
service system — not just the user's experience, but the organizational processes,
actors, and infrastructure that enable it. Where a journey map shows what the user does,
the blueprint shows what everyone does.

Blueprint notation standard (Stickdorn / Gibbons):

**Five lanes (top to bottom):**

| Lane | Contains |
|---|---|
| **Physical evidence** | Artifacts the user encounters at each touchpoint (screens, emails, documents, physical materials, notifications) |
| **Customer actions** | What the user does — their actions, decisions, and touchpoints |
| **Frontstage interactions** | The visible service interactions (what the product/staff does that the user directly experiences) |
| **Backstage interactions** | Internal actions invisible to the user that enable the frontstage (data processing, review steps, workflow triggers) |
| **Support processes** | Systems, tools, and third-party services that backstage actors depend on |

**Two key lines:**

- **Line of interaction**: separates customer actions from frontstage interactions — the boundary between user and service
- **Line of visibility**: separates frontstage from backstage — the boundary between what the user sees and what they don't

The line of visibility is where service design decisions live. When a process crosses
from backstage to frontstage (or fails to when it should), that is a design decision
with user-experience consequences.

### Blueprint notation standards

Each step in a lane is a box connected by arrows indicating sequence. Notation conventions:

- **Arrows**: solid = direct sequence, dashed = information/data handoff
- **Fail points** (Gibbons): mark steps where failure is most likely or has most impact — these become recovery design requirements
- **Wait times**: annotate between steps where user wait is significant — these are perceived performance opportunities
- **Evidence links**: connect physical evidence to the step that produces it

Do not over-detail the blueprint in first draft. A blueprint that captures every
sub-process in the first session is not a blueprint — it is a process map. Start with
macro steps, add detail in subsequent rounds only where the level of detail reveals
a design problem.

### How to run a blueprinting workshop

**Participants**: product team (PM, design, FE) + representatives from support, ops,
data/engineering, and any other backstage actor whose work enables the service.

**Workshop structure (90–120 minutes):**

1. **Scope the journey** (10 min): define start and end points — what event triggers the
   journey? What event ends it? Agree before mapping.
2. **Map customer actions** (20 min): walk through what the user does, step by step.
   Keep it at task level, not micro-interaction level.
3. **Add frontstage** (15 min): for each customer action, what does the system or staff
   do in response that the user directly experiences?
4. **Add backstage** (20 min): for each frontstage step, what internal processes and
   actors make it possible?
5. **Add support processes** (10 min): systems and tools the backstage depends on.
6. **Mark fail points and wait times** (15 min): where does the service most commonly
   fail? Where does the user wait? These become the prioritized design problems.
7. **Synthesis and next steps** (10 min): what did we learn? What are the top 3 design
   problems this blueprint reveals?

**Facilitation note**: backstage actors frequently discover they don't know what the
other backstage actors do. This is the value of the workshop — not the artifact, but
the shared model it creates.

---

## Customer Journey Mapping vs. Service Blueprinting

### The distinction

| | Customer Journey Map | Service Blueprint |
|---|---|---|
| **Primary perspective** | Customer/user | System (customer + organization) |
| **Artifacts** | Touchpoints, emotions, pain points, opportunities | Lanes, fail points, wait times, handoffs |
| **Primary question** | "What is the customer experiencing?" | "What does the whole system do to deliver this experience?" |
| **Audience** | Stakeholders who need empathy for the user | Design + operational teams who need to coordinate |
| **When to use** | Discovery — understanding user perspective, identifying opportunities | Design — understanding how to deliver, where the service breaks |

Journey maps without blueprints: the failure mode is empathy without operationalizability.
A beautiful journey map that stakeholders agree represents the user's experience does not
tell anyone what to change in the back office to fix it. The map identifies the what;
the blueprint identifies the how.

### When each is the right tool

**Use journey map when:**
- The primary goal is alignment on user perspective — getting the org to care about the
  user's experience
- The user's emotional journey across touchpoints is the key design input
- You're in early discovery and don't yet know enough about backstage processes to blueprint

**Use blueprint when:**
- You're moving from problem identification to design — you need to understand what to build
- Multiple teams own different parts of the service and need to coordinate
- You've identified a pain point in a journey map and need to understand the organizational
  root cause
- Service recovery, onboarding, or support escalation are in scope — these are inherently
  multi-actor problems

**Use both when:**
- The project is large enough to warrant the investment
- The journey map is the discovery artifact and the blueprint is the design artifact — sequence them

---

## Multi-Touchpoint Experience Design

### The product is not the whole journey

PLM enterprise software (and most enterprise SaaS) is one touchpoint in a larger workflow
that includes: email threads, spreadsheets maintained outside the product, physical samples
or artifacts, in-person review meetings, approval processes in adjacent systems, and file
attachments in formats the product doesn't natively support.

The implication for UX: designing only within the product boundary is designing a
fraction of the user's experience. A beautifully designed product that requires the user
to manually transcribe data from a spreadsheet every morning has failed at the service
design level.

### Designing for a product that is not the whole journey

**Identify the adjacent touchpoints**: what does the user do immediately before entering
the product? What do they do immediately after leaving? These are the seams that the
product must be designed to fit into.

**Design the handoffs explicitly**: the moment between the product and an adjacent
touchpoint is a design surface. "Export to Excel" is not a handoff design — it is a
failure to design the handoff. What data does the user need, in what format, to
accomplish the next step in their actual workflow?

**Accept what the product cannot own**: some adjacent touchpoints are beyond the
product's scope. When the user leaves the product to do something in email or a
meeting, design for the re-entry: what does the user need to see when they return?
What state must the product preserve?

### Designing handoffs

A handoff is the moment when responsibility for the user's task transfers from one
touchpoint (or actor) to another. Handoffs fail when:

- **Context is lost**: the receiving touchpoint doesn't have the information the
  user built up in the sending touchpoint
- **State is ambiguous**: the user doesn't know whether to act in the new touchpoint
  or wait for something from the old one
- **Accountability is unclear**: neither touchpoint claims ownership of the user's task

Handoff design checklist:
- [ ] What information must be transferred? (data model + format)
- [ ] How is the user notified that the handoff has occurred?
- [ ] What is the user's expected action in the receiving touchpoint?
- [ ] What happens if the receiving actor/touchpoint fails to act?
- [ ] Who is accountable for the task during the handoff period?

---

## Back-Stage Actor Mapping

### Identifying internal actors

Back-stage actors are the internal people and teams whose work enables the frontstage
experience. For enterprise SaaS, these typically include:

| Actor | What they enable |
|---|---|
| **Engineering** | Feature delivery, performance, reliability, data pipeline |
| **Support** | User recovery when the product fails; error escalation |
| **Data/Analytics** | Data accuracy, processing pipelines, calculated fields |
| **Ops/Implementation** | Customer onboarding, configuration, migration |
| **Account management** | Relationship continuity; escalation path for enterprise issues |
| **Security/Compliance** | Access control, audit logs, data residency |

Mapping these actors against the service blueprint reveals which backstage actor owns
which step — and which steps have no clear owner (these are almost always fail points).

### Service design for support escalation

Support escalation is a service within the service. When a user encounters a problem
they cannot resolve alone, the support escalation service activates. Design for it:

**The support escalation journey:**
1. User encounters a problem
2. User attempts self-resolution (help documentation, error messages, retry)
3. User initiates support contact (in-product or external)
4. Support receives context and triage
5. Support resolves or escalates to engineering
6. Resolution communicated to user
7. User returns to their task

**Design requirements from each step:**
- Step 2: error messages must contain enough information for the user to attempt resolution and for support to triage without repeating the same questions
- Step 3: in-product support initiation must pass product context automatically (current screen, recent actions, error message) — don't make users re-explain what the product already knows
- Step 4: the support interface must surface the same context the product has — this is a data/API design requirement
- Step 6: resolution notification must include what happened and how to prevent recurrence
- Step 7: user return must not require the user to reconstruct their context (preserve state through the support episode)

---

## Service Recovery Design

### What service recovery design is

Service recovery is not error state UX. It is the end-to-end process of: detecting a
failure → notifying affected users → triaging the problem → resolving it → following up.
Each step is a design problem, and most of them involve touchpoints outside the product UI.

### The service recovery journey

| Phase | Touchpoints | Design requirements |
|---|---|---|
| **Detection** | Product monitoring, error logging, user reports | Automated detection must produce actionable context; user-reported failures must be easy to submit |
| **Notification** | Email, in-product banner, status page, account manager | Notify before users discover the problem if possible; use appropriate channel for severity (critical = proactive email; minor = in-product banner) |
| **Triage** | Support system, engineering escalation | Support must have the context to triage without calling the user; escalation path must be clear |
| **Resolution** | Engineering, ops, data teams | Resolution timeline communicated to affected users; no-update silence is a service failure of its own |
| **Follow-up** | Email, in-product notification, account manager outreach | What happened, what was done, what prevents recurrence; this is a trust-repair touchpoint — design it |

### Non-UI touchpoints in service recovery

The most consequential service recovery touchpoints are often outside the product:
- **Status page**: a public, always-available record of service health. Must be honest,
  timely, and legible to non-technical users.
- **Email notifications**: must identify affected users correctly (not send to everyone),
  describe impact specifically, and include timeline and next steps
- **Account manager outreach**: for enterprise customers, proactive human contact during
  significant outages is a service design requirement, not an optional nice-to-have

Design the email and notification templates before an outage, not during one.

---

## Moments of Truth Mapping

### The concept

Jan Carlzon's "Moments of Truth" (SAS Airlines, 1987): each point of contact between
a customer and the service is a moment that either increases or decreases trust and
satisfaction. Not all moments are equal.

**Applied to enterprise SaaS**: identify which touchpoints disproportionately affect
user satisfaction and retention — then design those touchpoints first and best.

Moments of truth in enterprise SaaS typically cluster around:
- **First successful value**: the moment the user gets something useful out of the product
  for the first time (the product lives or dies on this moment)
- **First error recovery**: the first time something goes wrong and the user successfully
  recovers — this moment disproportionately shapes trust
- **Onboarding completion**: the moment the user has configured the product to work for
  their workflow (not "account created" — actual first productive use)
- **Renewal decision context**: the period of product use that is most salient to the
  decision-maker who controls the renewal

### The peak-end rule (Kahneman)

Users do not evaluate an experience as the average of all moments — they evaluate it
based on the peak (most intense moment, positive or negative) and the end (the last
moment before evaluation).

Implications for service design:
- **Design the peak moment**: create a deliberately positive peak — the moment that
  users will remember and describe to others ("The moment I realized it calculated that
  automatically for me...")
- **Design the end moment**: the last touchpoint before any significant gap in use
  (end of onboarding, end of a long workflow, end of an annual review cycle) must
  be positive and leave the user with a sense of completion
- **Mitigate the negative peak**: the worst moment in the service (most commonly a
  serious error or a painful onboarding step) must be designed to be as non-traumatic
  as possible — because it will be remembered regardless

Service design that optimizes for the average moment while leaving the peak and end
moments to chance is leaving the most important design decisions unmade.

---

## Service Design for Enterprise Onboarding

### Onboarding as a multi-touchpoint, multi-actor service

Enterprise onboarding is not "the onboarding flow in the product." It is a service
that spans multiple touchpoints and actors over days to weeks:

| Phase | Actors | Touchpoints |
|---|---|---|
| **Sales handoff** | AE, CSM, Implementation | Contract, handoff call, intro email, kickoff deck |
| **IT provisioning** | IT admin, product | SSO configuration, user directory sync, security review |
| **Admin configuration** | Admin user, CSM, product | Admin setup wizard, configuration templates, CSM guidance calls |
| **End-user training** | End users, L&D, product | Training materials, product walkthroughs, live training sessions |
| **First value moment** | End user, product | First completed task that demonstrates product value |
| **Ongoing enablement** | End users, CSM, product | Feature announcements, training, Q&A support |

### Where UX owns the touchpoint

UX directly owns: the in-product parts of each phase — admin setup wizard, end-user
walkthroughs, configuration screens, progress indicators, onboarding checklists.

UX influences but does not own: the email templates, the training materials, the
CSM guidance, the IT documentation. However, UX should specify what information
these touchpoints must convey and what state the user must be in to successfully
enter the next product touchpoint.

### Where UX must coordinate with adjacent teams

**Sales handoff → IT provisioning**: the product must surface accurate technical
requirements for IT in a format IT can act on without asking the sales team.
This is a UX problem — an "IT setup guide" linked from the admin onboarding surface.

**Admin configuration → end-user training**: admin configuration choices affect
what end users see and can do. The onboarding design must account for this — an
end-user who enters before admin configuration is complete should see a state that
explains why and what to expect, not a broken product.

**First value moment → ongoing use**: the first value moment must be engineered,
not left to chance. Identify the specific action that most strongly predicts
retention (the "aha moment") and design the onboarding to guide every user to it.

---

## Cross-Links

- `ux-interaction-design` — detailed design of in-product touchpoints within the service journey
- `ia-mental-models` — user mental models that inform journey expectations and service design decisions
- `pm-discovery-research` — research methods for mapping current-state journeys and identifying unmet needs
- `ux-research-synthesis` — synthesis of multi-touchpoint research data; journey map construction from research

---

## References

- Marc Stickdorn & Jakob Schneider — This Is Service Design Thinking (book)
- Polaine, Løvlie & Reason — Service Design: From Insight to Implementation (book)
- Maureen Gibbons — Service Blueprinting Guide: https://www.nngroup.com/articles/service-blueprints-definition/
- Jan Carlzon — Moments of Truth (book)
- Daniel Kahneman — Thinking, Fast and Slow (peak-end rule, chapters on experience vs. memory)
- Kerry Bodine & Harley Manning — Outside In: The Power of Putting Customers at the Center of Your Business
- Nielsen Norman Group — Journey Mapping 101: https://www.nngroup.com/articles/journey-mapping-101/
- Nielsen Norman Group — Service Blueprinting: https://www.nngroup.com/articles/service-blueprints-definition/
