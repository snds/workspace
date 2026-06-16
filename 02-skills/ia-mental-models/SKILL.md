---
name: ia-mental-models
description: >
  User conceptual models, mental model mapping, conceptual design, and
  model-to-IA alignment. Part of the lead-information-architect skill network.
  Use this skill when the conversation touches: mental model theory (Kenneth Craik,
  Indi Young), mental model mapping from user interviews, conceptual design (defining
  system concepts before navigation), the gulf of execution and evaluation (Norman),
  enterprise user model complexity (domain models, system models, organizational
  models), aligning IA to user expectations rather than organizational structure,
  or any question about how users understand and expect systems to work. Distinguished
  from ia-research-methods (the techniques to discover mental models) and
  ia-taxonomy-classification (formalizing the structure that results from model alignment).
aliases: [ia-mental-models]
tier: spoke
domain: design
hub: lead-information-architect
prerequisites: [lead-information-architect]
spec_version: "2.0"
---

# IA: Mental Models

Specialist skill for user conceptual models, mental model mapping, and
aligning IA structure to how users actually think. Part of the
`lead-information-architect` skill network.

---

## Domain Boundary

This skill owns **understanding and aligning to how users think about
information**.

- **Techniques to discover mental models** → `ia-research-methods`
- **Formalizing the taxonomy structure that results** → `ia-taxonomy-classification`
- **Expressing the model as navigation** → `ia-navigation-systems`
- **JTBD as a mental model discovery tool** → `pm-discovery-research`
- **Synthesis methods for research data** → `ux-research-synthesis`

---

## Mental Model Theory

### Kenneth Craik — The Origin (1943)

Kenneth Craik, in *The Nature of Explanation* (1943), proposed that the mind
constructs small-scale models of reality that it uses to anticipate events
and reason about cause and effect. These are **mental models**: internal
representations of how things work.

Users carry mental models of every system they interact with. When a new
system conforms to a user's existing mental model, it feels intuitive. When
it contradicts it, users make errors, feel confused, and lose confidence.

**The IA implication**: You cannot design structure in a vacuum. You are
always designing against users' pre-existing models — of the domain, of
prior software, of analogous systems. The question is whether you discover
those models deliberately (through research) or collide with them accidentally
(through user errors).

### Don Norman — Gulf Theory (1986)

Don Norman's *The Design of Everyday Things* (1986) formalized how users
interact with systems through two gaps:

**Gulf of Execution**: "How do I make this thing do what I want?"
The user has a goal but cannot figure out what actions to take.
IA failures create execution gulfs — the user doesn't know which navigation
path leads to their goal.

**Gulf of Evaluation**: "Did what I just did work?"
The user cannot perceive the system's state after their action.
IA failures create evaluation gulfs — the user can't tell whether they're
in the right place or whether their navigation succeeded.

**Both gulfs exist in navigation**. A user trying to find "pending approvals"
faces an execution gulf if the label is "Workflow Queue" and an evaluation
gulf if the page they land on doesn't confirm they've found what they expected.

### Indi Young — Mental Model Mapping (2008)

Indi Young's methodology (*Mental Models*, 2008) translates Craik's theory
into a practical design research tool.

**The core insight**: Don't ask users about software. Ask users about tasks.
Conversations about tasks (not systems) reveal the user's mental model of
their workflow — which is the actual thing the IA must serve.

**Young's process** (summary):
1. Define the scope of the mental model (what user population, what task domain)
2. Conduct task-based interviews ("walk me through how you manage sample approvals")
3. Transcribe and break transcripts into atomic task statements
4. Group statements into "towers" — clusters of related mental activity
5. Group towers into "mental spaces" — higher-level domains of activity
6. Build the mental model diagram: user tasks above the center line; existing
   (or proposed) product features below; alignment shows which features
   support which mental tasks; gaps show unserved user needs

**The alignment diagram is an IA tool**. When towers and spaces become
navigation sections and sub-sections, the IA reflects user mental organization
rather than organizational or technical structure.

---

## Types of User Models

### The Mental Model (What the User Believes)

The user's internal representation of how the system works. This model is
built from:
- Prior experience with similar systems
- The product's visual and structural affordances
- Onboarding, documentation, and support
- Colleague instruction and workarounds

The mental model is often incorrect by designer intent — and that's fine.
The IA must meet users where their model is, not where it "should" be.

### The Conceptual Model (What the Designer Intends)

The model the designer wants the user to have. Expressed through:
- Navigation structure and labels
- Naming conventions for key objects
- Empty states and onboarding
- Documentation

**The designer's job**: Bridge the gap between the user's existing mental
model and the intended conceptual model. Not by forcing users to learn the
system model, but by designing a conceptual model that maps naturally to
users' existing mental structures.

### The System Model (How It Actually Works)

The technical implementation — database schema, service architecture, business
logic. Users should never need to know this. When system architecture leaks
into navigation and labeling, it creates a third model users must learn
that serves neither their goals nor the intended conceptual model.

**The most common enterprise IA failure**: IA that reflects the system
model (or the organizational structure) rather than user mental models.
"Materials Management" (system module) vs. "Fabrics & Trims" (user concept).
"Supplier Portal Administration" (org structure) vs. "Manage Vendors" (task).

---

## Conceptual Design

Conceptual design is the step between "understanding user mental models"
and "designing navigation." It defines the core concepts of the system
and their relationships before any navigation or visual design begins.

### The Conceptual Model Statement

A well-designed conceptual model can be expressed in 2–3 sentences:

> In this system, a **Style** is the primary product record. It contains
> **Colorways**, each of which has **Sizes** with prices. Styles move through
> an **Approval Workflow** as they progress from concept to production.

This statement is the IA foundation. It defines:
- The primary objects (Style, Colorway, Size)
- Their relationships (Style contains Colorway contains Size)
- The key process concept (Approval Workflow)

Navigation sections, labels, and information hierarchy all follow from
this statement. If you can't write a statement like this clearly, the
conceptual model is not yet defined — and navigation design is premature.

### Object-Relationship Mapping

For complex enterprise systems, map the core objects and their relationships
before designing navigation:

```
Style ──contains──> Colorway ──contains──> Size
  │                     │
  └──requires──> Bill of Materials
  │
  └──moves through──> Approval Workflow
                           │
                           └──involves──> Users (roles: Designer, Buyer, Approver)
```

This map answers structural IA questions:
- What is the primary navigation object? (Style)
- What is sub-navigated within a Style? (Colorways, BOM, Workflow state)
- What spans multiple primary objects? (Approval Workflow — navigated separately)
- What are the access roles that might need differentiated navigation? (Designer, Buyer, Approver)

---

## Mental Model Mapping Process

### Phase 1: Scoping

Define the mental model's scope before research begins:
- Which user population? (Not all users have the same mental model)
- Which task domain? (What tasks will the IA serve?)
- What's the existing system being improved vs. net new design?

For enterprise multi-role systems: scope one mental model per role, then
compare. Role models will overlap significantly in some areas and diverge
sharply in others. Where they diverge is where role-differentiated navigation
decisions live.

### Phase 2: Task-Based Interviews

**The interview question type**: Behavioral, not hypothetical.
- "Walk me through the last time you approved a sample."
- "Tell me about a time when you needed to find a product's sourcing history."
- Not: "How would you want a system to handle approvals?"

**What you're collecting**: Atomic task statements — small, specific descriptions
of mental activity. "I check whether the sample was sent by the deadline" is
an atomic task. "I manage samples" is not.

### Phase 3: Affinity Diagramming

1. Write each atomic task statement on a card (physical or digital)
2. Sort silently — group by natural affinity without pre-imposed categories
3. Name each cluster (this becomes a candidate IA section name)
4. Group clusters into higher-level spaces (these become candidate top-level nav items)
5. Look for tasks that appear in multiple clusters — these are cross-cutting
   concerns that need either ubiquitous navigation or explicit cross-linking

### Phase 4: Alignment Analysis

Plot the mental model towers against the current or proposed IA:
- Which towers are well-served by current navigation? (Preserve)
- Which towers are partially served? (Strengthen)
- Which towers have no corresponding navigation? (Gaps — new structure needed)
- Which navigation items have no corresponding mental model tower? (Orphaned nav — candidates for removal or restructuring)

---

## Enterprise Mental Model Complexity

Enterprise users carry three overlapping models simultaneously:

### Domain Model

The user's understanding of their industry and workflow, developed over years
of professional experience. A fashion designer carries a deep mental model
of the product development lifecycle — from concept sketching to sampling
to production — that exists independently of any software system.

**IA implication**: Enterprise IA must align to domain models first. If the
navigation doesn't map to how the user thinks about their job (not the software),
every interaction creates friction.

### System Model (Prior Software)

Enterprise users have deep experience with prior systems — SAP, legacy PLM,
Excel, specialized industry tools. These prior systems have shaped their
mental models of how "this kind of software" works.

**When prior system models help**: Maintaining conceptual metaphors that
users recognize ("style record", "BOM", "approval") reduces onboarding friction.

**When prior system models hurt**: Prior system complexity creates learned
helplessness — users expect enterprise software to be confusing and learn
workarounds rather than correct navigation. "That's just how it works" masks
real IA failures.

### Organizational Model

Users understand their company's structure, roles, and processes. When IA
reflects organizational structure (because it was designed by product teams
who think in org charts), it serves users who know the org structure — typically
admins and power users — but fails new users and those in different org contexts.

**The org-model trap**: Navigation sections named after internal team names
("Supply Chain Hub", "Merchant Tools", "Planning Module") that mean nothing
to users who don't know the org structure.

---

## Failure Modes

**Model assumption without research**: Designing IA based on the product team's
mental model of the domain (which matches the system model) rather than
users' mental models. The most common cause of "intuitive to us, confusing
to users."

**Role conflation**: Treating all users as if they share the same mental model.
A buyer's mental model of product approvals is fundamentally different from
a designer's. Navigation designed for one role creates friction for the other.

**Organizational structure as IA**: The navigation reflects the company's team
structure, not user workflows. Users who don't know the org chart can't navigate.

**Technical model leak**: Navigation labels and structure that expose backend
implementation. "Entity Management", "Record Administration", "Data Objects"
are all system-model labels that communicate nothing about user tasks.

**Conceptual model drift**: The conceptual model is correct at launch but the
system grows and new features are added without updating the conceptual model.
Navigation layers accumulate without coherence. After 3–4 major versions, the
navigation no longer tells a coherent story.

---

## Cross-Links

- **`ia-research-methods`**: Card sorting, tree testing, and first-click testing
  are quantitative complements to the qualitative mental model mapping process
- **`ia-taxonomy-classification`**: Mental model towers become taxonomy categories;
  user language discovered in mental model research populates controlled vocabulary
- **`ia-navigation-systems`**: Mental model spaces become navigation sections;
  tower relationships inform hierarchical depth and cross-navigation
- **`pm-discovery-research`**: JTBD research and mental model mapping are
  complementary; JTBD reveals goal motivations, mental model mapping reveals
  cognitive task structure
- **`ux-research-synthesis`**: Synthesis methods for mental model research data

---

## References

- Kenneth Craik, *The Nature of Explanation* (1943)
- Indi Young, *Mental Models: Aligning Design Strategy with Human Behavior* (2008)
- Don Norman, *The Design of Everyday Things* (1988, revised 2013)
- Philip Johnson-Laird, *Mental Models* (1983)
- Susan Carey, *Conceptual Change in Childhood* (1985)
