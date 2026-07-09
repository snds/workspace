# UI/UX Operational Framework

*A companion to the Aesthetic Lens. Where the lens answers "why does this feel right?", this framework answers "how do we systematically make decisions about hierarchy, interaction, information flow, and metaphor?" Both sit at the top tier — above project-specific skills like ds-advisor, figma-canvas-designer, or any domain-specific work. Neither is project-gated. Both stay holistic and contiguous.*

---

## The core conviction

**Information architecture and interaction design should be shaped by context — role, task, phase, expertise — and should adapt intelligently without requiring manual configuration or losing coherence.**

Interaction patterns should never be inherited unexamined. Every pattern choice is an opportunity to ask whether it actually serves the user's need in this context, or whether it's a legacy assumption dressed up as a standard.

---

## The first question: metaphor and pattern choice

Before reaching for any interaction model — tables, forms, lists, cards, timelines, maps, dashboards, wizards, modals — ask:

**What does the user actually need to accomplish in this context, and what's the most direct way to serve that?**

This is the single most important check in any IA decision. It's easy to inherit patterns from what exists, what the customer is used to, or what was built before. Sometimes those patterns are correct. Often they're not — they're just the legacy shape of previous constraints.

### Interrogate or pragmatic? Know which mode you're in.

Not every pattern needs to be questioned every time. The distinction:

- **Interrogate when there's evidence of friction or misalignment.** If users are working around the pattern, if density is unmanageable, if it takes five+ steps to reach a common goal, if one pattern is being used for radically different tasks (e.g., data tables everywhere for everything) — that's a signal the pattern itself may be wrong, not just overstuffed. Research deeper. Explore alternatives.
- **Pragmatism when the pattern serves the need adequately.** If the cost of change outweighs the benefit, if users are fluent and the workflow flows, if the pattern is genuinely the right metaphor — move forward. Revisit when evidence warrants it.

The escape hatch for pragmatism: sometimes the path of least resistance is the right choice *for now*. Users often don't know what they don't know — they've worked in what they've had. Honor that reality while staying open to the possibility that what they have isn't what they need long-term.

### The data table as an illustration (not a rule)

Example: Centric PLM uses data tables *everywhere for everything*. That ubiquity is a symptom, not a solution. The metaphor was inherited from Excel — what customers *knew* — not derived from what each workflow actually requires.

The real questions a workflow should provoke:

- Do users need to see this information at a glance, or do they need to interrogate it deeply? (Cards vs. table.)
- Do they need to edit in bulk always, or occasionally? (If occasionally, hide bulk edit behind an advanced view.)
- Is the data relational, temporal, spatial, or comparative? Each suggests a different pattern. (Timelines for sequence. Maps for spatial. Tables for comparison. Cards for scanning.)
- Are they scanning, deciding, entering, editing, or reporting? Each task wants a different interaction.

The power-user data table — filters, bulk actions, advanced configuration — is absolutely valid. But it belongs *behind the wall*: accessible via toggle, advanced view, or expert mode, not as the default interaction. The primary surface should serve the most common task for that context, in the most direct way possible.

This principle generalizes: **any pattern used universally is probably wrong somewhere.** If one interaction model is doing all the work, information architecture is likely broken upstream.

---

## Three-layer design thinking

### Layer 1: Information architecture — what matters now

Map the user's actual workflow: entry point → decision → action → outcome. For each phase, identify:

- **Primary information:** What must be visible to make the next decision?
- **Secondary information:** What provides context or alternatives?
- **Tertiary information:** What's available if needed but shouldn't clutter the primary view?
- **Contextual triggers:** What changes based on role, task phase, or user expertise?

This isn't about hiding information. It's about sequencing it so cognitive load matches actual need.

**The guiding principle: surface information where the user is, or where they need it to be — don't make them travel to it.** Bringing the water to the horse, rather than guiding the horse to water.

### Layer 2: Interaction model — how intent becomes action

Design for the *minimum necessary interaction* to complete the task, not the maximum possible options:

- **What's the happy path?** Can a typical user complete the core task in 3–4 interactions?
- **Where do expert users diverge?** Can they shortcut or customize without breaking the model for everyone else?
- **What's the failure recovery?** If something goes wrong, is the path back clear and forgiving?
- **When does the UI adapt?** Should interaction complexity change based on user behavior, expertise, or context?

### Layer 3: Visual hierarchy and feedback — how clarity supports action

Information hierarchy should *visually express* task priority:

- **Most important:** Largest, highest contrast, center or leading edge
- **Supporting:** Medium visual weight, accessible but not competing
- **Available if needed:** Lower contrast, grouped, collapsible, or in secondary panels
- **System feedback:** Clear, immediate, using motion and color purposefully (not decoratively)

Pair this with the Aesthetic Lens: density is fine if *earned*, hierarchy is clear because the architecture is *authored*, and visual language suggests the system understands what the user is trying to do.

---

## Expertise: a first-class research question

Don't assume novice-by-default with progressive expert reveal. That model is valid for consumer software and for domains where users genuinely learn the tool over time — but enterprise and professional software often has a mix.

Research should identify, for each persona and context:

- **Expert at entry.** Users who arrive with full domain and tool fluency. Designing a novice-first experience for them is paternalistic and slows them down. They need the expert UI exposed from day one.
- **Progressive learners.** Users who grow into expertise. Novice-first with layered reveal works here. The system should grow with them, not require a re-learning event when they level up.
- **Situational experts.** Fluent in some areas, novice in others — e.g., expert in fashion PLM domain but new to the software, or fluent in the software but new to a specific module. The interface should adapt by *area of task*, not treat the user as uniformly expert or novice.
- **Occasional users.** Experts who return infrequently and need light re-onboarding each time.

The takeaway: expertise isn't a single axis from novice to expert. It's multi-dimensional, context-dependent, and often situational. Design accordingly.

---

## Decision frameworks for common pattern categories

These aren't rules. They're defaults worth questioning when context demands.

### Forms and data entry
- Sequence fields by task logic, not alphabetical or "organizational" ordering.
- Show only fields relevant to current context; reveal conditionally rather than hiding.
- Provide inline validation that helps, not punishes.
- Use visual grouping to show relationships; avoid false separation.

### Data display and browsing
Before defaulting to a table:
- Is the user scanning, comparing, deciding, or editing? Match the pattern to the task.
- Can cards, lists, or a split-view serve the at-a-glance case better?
- If a table is genuinely right: lead with the identifying attribute; sequence columns by frequency of use or decision importance.
- Consider progressive disclosure — show 5 columns at a glance, full detail on demand.
- Advanced table capabilities (bulk edit, advanced filter, full export) belong behind a deliberate toggle, not in the primary view.

### Navigation and wayfinding
- Primary navigation reflects *primary workflows*, not organizational structure.
- Secondary navigation answers "where am I?" and "what can I do from here?"
- Breadcrumbs or context trails show decision path, not just hierarchy.
- If a user is five levels deep, the IA is probably wrong.

### Role-based and expertise-based adaptation
- Start with the correct entry model for each persona (not always novice).
- Layer in expert options non-invasively (keyboard shortcuts, bulk actions, advanced filters) where progressive growth is expected.
- Never *hide* things behind permissions that should be visible for context.
- Test the "role transition" — when someone moves from novice to expert, does the interface grow with them, or does it require re-learning?

### Control placement by scope of effect

Place — and evaluate the placement of — every actionable control by the **scope of effect** it has
and the **user intent** behind it, not by where it visually fits, which surface has room, or what it
resembles. Contextual or visual similarity between controls does not imply equivalent intent.
App-global affordances belong to global chrome; page/object-wide affordances to the page surface;
region/section affordances to that region; item/row/selection affordances to that element. Two
corollaries must *both* hold:

- **Don't merge by appearance.** Two controls that look alike but act at different scopes stay
  visually/spatially distinct and scope-signposted — never collapsed into one just because they share
  a form factor.
- **Don't fragment by surface.** The same intent reimplemented across several surfaces gets unified
  into one primitive, bound to scope — not rebuilt per location.

Placement-by-resemblance produces three failures: cognitive load (learning which of two
identical-looking controls does what), wrong-scope mistakes (acting on the object when they meant the
row), and false consolidation (merging by look breaks intent). Review checklist, per control: (1)
What is its scope of effect? [global / page-or-object / region-section / item-row / current-selection].
(2) Does its placement match that scope? (3) Where it resembles another control, is the *intent* the
same or only the form factor? (4) Is the scope made *visible* (label, grouping, position,
containment), or must the user infer it? **Corollary for repeated elements** (e.g. multiple tables on
one page): a scope-bound control must bind to the *specific* instance it affects and stay attached to
it — a shared/hoisted control cannot disambiguate which instance it acts on; containment becomes the
primary scope signpost. (Generalized from the Centric PLM toolbar/table work; context-independent.)

---

## Governance for scaled coherence

As patterns multiply across a product:

- **Token-first decisions.** Color, typography, spacing come from a shared language, not per-feature choices.
- **Pattern reuse with context awareness.** A form in onboarding behaves differently from a form in settings, but uses the same components.
- **Feedback loops.** User research flows into IA iteration; don't let features calcify.
- **Constraints as features.** Limit the number of valid IA patterns (e.g., a defined set of table layouts, card types, modal patterns), then design within those constraints.

---

## Integration with the Aesthetic Lens

Every design decision should pass through both:

- Information architecture that feels *authored* for specific contexts (not templated).
- Interaction models that feel *inevitable* given constraints (not arbitrary).
- Visual hierarchy that feels *earned* (density has purpose; simplicity has reason).
- Adaptation that feels *intelligent* (the system anticipates need, not guesses).

Every interaction should feel like the designer understood the user's actual problem and shaped the experience accordingly.

---

## What this framework is not

- Not a prescriptive checklist. Defaults are starting points, not rules.
- Not a replacement for design systems or project-specific patterns — it's the lens through which those systems are evaluated.
- Not universally applied. Non-UX creative work invokes the Aesthetic Lens only. UX work invokes both.
- Not static. Evidence from research, usage data, or direct user feedback should feed back into both frameworks over time.

It's the *how* that carries across projects, so IA and interaction thinking stay coherent even when the product shifts.
