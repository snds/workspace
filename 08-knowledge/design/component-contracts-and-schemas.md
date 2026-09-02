---
tags: [design-systems, components, contracts, schema, specs, governance, ai-context, tokens]
created: 2026-07-28
updated: 2026-09-01
status: validated
confidence: high
sources:
  - "Nathan Curtis — *Component Contracts and Schemas* (nathanacurtis.substack.com, 2026-07-28)"
  - "EightShapes **Specs** schema + its ~60-ADR corpus (specsplugin.com/schema, github.com/DirectedEdges/specs)"
  - "Christine Vallaure — *Design system contracts: the component lives in neither Figma nor code*"
  - "Christian Morales Achiardi — *Design systems are contracts, not libraries* (giorris.dev)"
  - "TJ Pitre / Southleft — *Use AI to Need Less AI*"
  - "PJ Onori — **DSDS**, Design System Documentation Spec v0.15.2 (designsystemdocspec.org); shape update to v0.20.0 recorded 2026-09-01"
related_skills: [ds-advisor, design-engineer, ux-component-library, design-system-ops]
related_projects: [02-centricPLM, 09-figma-repo-sync-plugin, centric-ui]
relations:
  relates-to:
    - "[[agentic-ds-context-model]]"
---

# Component contracts and schemas — the arbitration layer above component documentation

Source: Nathan Curtis, *Component Contracts and Schemas* (2026-07-28). This entry keeps the
transferable operating content: the four definitions, the **seven gating criteria** (restated as
pass/fail tests rather than preferences), the investment gate, the maturity ladder, and the specific
places our own stack currently fails these tests.

Companion artifacts: the portable model lives at
[component-contract-schema.md](../../02-shared-references/component-contract-schema.md);
the framing sits in [[09-component-and-pattern-framework]] §5a.

---

## 1. The four definitions (get these straight before anything else)

| Term | What it is | The test |
|---|---|---|
| **Description** | An artifact that *records* decisions for a reader. | It **informs**. |
| **Contract** | An artifact that centralizes design intent in one place so it can be **implemented, verified and evolved across implementations**. | It **arbitrates**. |
| **Schema** | The **model a contract is written in** — types, hierarchies, relationships. Says nothing about any particular component. | It models what a contract *can* say. |
| **Spec** | An instance authored against the schema. | It is what a contract *does* say. |

> **A description informs. A contract arbitrates.**

**The arbitration test — the single most useful question in this entry.** When two implementations
disagree about a component, does this artifact settle it *without a human in the room?* If a person
must read, interpret, and adjudicate, you have a description. Most things called "the spec" fail this.

**A contract is a multi-party agreement.** In a multi-platform system, React, iOS, Android, Web
Components — **and Figma** — are all parties. No party owns it; each signs it and abides by it through
its implementation. This reframes Figma from *source of truth* to *one signatory*, which is the single
biggest mental shift in the piece for how we work.

**Version two things, separately.** The spec's *content* (there's a `Button` with a `size` prop) is
versioned; the schema *model* (a `Component` has `Props` such as an `EnumProp`) is versioned too, on
its own track. Implementing a contract depends on both. This is what makes "the contract is wrong"
computable and inarguable instead of a debate.

---

## 2. The seven gating criteria

Curtis frames these as principles. They are more useful as **gates** — each with a failure it
prevents, a machine-checkable test, and the smell that says you are already violating it. Run a
candidate contract through all seven; a contract that fails 4/5/6/7 is a description wearing a
contract's clothes.

### Gate 1 — Well-typed over loosely formed
**Rule.** Every value position declares what kind of value is legal there: number, boolean, or one
choice from a closed list. *A well-typed contract makes it impossible to write malformed things.*
**Prevents.** `size: med`, `size: kind of large`, a text element carrying a `backgroundColor`, a
container carrying a glyph name.
**Machine test.** Can you author an invalid value and have the artifact still "work"? If yes → fail.
**Smells.** Every value is a string. States encoded implicitly in naming conventions
(`button-primary`, `button-primary-hover`, `button-primary-active`) — an agent usually figures it out,
but *the contract can't verify it or hold implementations accountable.* Prose carrying load-bearing
decisions.

### Gate 2 — Normalized over redundant
**Rule.** *Good contracts state each decision once.* Disabled opacity is one line on the root element
in one configuration variant — not a property re-stated across 96 Figma variants (~500 layers for one
intent).
**Prevents.** Self-contradiction. **A self-contradicting artifact cannot arbitrate anything.**
**Machine test.** Grep the decision. More than one authoritative location → fail. Ask literally: *"Is
this declaration the source, or is that one?"* If nobody knows, it is not a source of truth.
**Smells.** A "single source of truth" that states colors in prose (`text-primary` (#21272A)) *and* in
a YAML inventory (`text-primary: "#1A1C1E"`). Writing agent rules/skills to *guard against drift
between intentional redundancies* — guarding is the wrong fix; remove the redundancy.

### Gate 3 — Independent over platform-biased
**Rule.** Minimize the shape's bias toward any one platform — Figma, CSS, iOS, Android.
**Prevents.** A contract that only one party can actually implement.
**Machine test.** Could an iOS engineer implement from this without knowing anything about Figma?
Could a web engineer implement it without knowing UIKit?
**Smells.** `INSTANCE_SWAP` and other Figma-native prop types; absolute positioning expressed as
Figma `constraints` rather than edges; `left`/`right` instead of `start`/`end`; string-typed props that
are really numbers.
**The reframe that matters most:** *a definition extracted untransformed from one party's
point-of-view (like a Figma file) is **testimony, not a contract**.* Extraction is step one; the
transform to a neutral model is what makes it a contract.
**Honest caveat from the source.** Perfect neutrality is a fool's errand; bias by *name* (Figma) with a
model closer to CSS proved fine in practice. Cull unintentional leaks over time; don't stall on purity.

### Gate 4 — Verifiable over readable
**Rule.** A machine can decide right or wrong without human intervention, at **two levels**:
(1) *is this a validly structured spec?* (2) *is it precisely implemented?*
**Prevents.** Silent acceptance of nonsense — a dependency that doesn't exist, a property the schema
doesn't support, an icon glyph the library doesn't ship.
**Machine test.** Feed it a deliberately broken value. Does anything reject it?
**Smells.** Markdown as the wire format — *markdown readers are built to tolerate ambiguity*.
**A format where nothing is invalid is a format where nothing is verifiable.** **Reading is review,
not verification.**
**The deletion test (adopt this).** For any load-bearing prose sentence — *"depth is achieved through
tonal layers rather than heavy shadows"* — ask: what makes a shadow heavy? what makes a layer tonal?
If you can't verify it, try deleting it. **If deleting the sentence changes the contract, that sentence
was bearing too much load** and the decision belongs in the typed model.
**The boundary trap.** A validated extract stops being strict the moment downstream consumers read a
markdown file *an LLM already smoothed and elaborated*. The verification data got stuck at the
boundary, and **every consumer downstream is inferring from inference.**

### Gate 5 — Determinism over inference
**Rule.** Same input → same output, every time. Generate twice with nothing changed and the **diff is
empty** — no reordered keys, no noise. Change one deep property, regenerate, and it appears as a
single additive change.
**Prevents.** Errors introduced upstream, invisibly, that harden exactly when you thought you were
recording truth.
**Machine test.** `generate && generate && diff` → must be empty.
**The line to hold.** *Inference I configure, not inference I hope for.* Transformations are fine and
necessary (overlaying subcomponents, glyphs and states onto a source model via naming conventions) as
long as they are mechanical, maintainable, and based on conventions the architect set.
**The reframe.** **Deterministic compilation isn't the goal — it's *evidence* the contract is good.**
If you can't compile it deterministically, the contract is under-specified. Use regeneration as a
proof, not a feature.

### Gate 6 — Efficiency over expense to keep true
**Rule.** Efficiency = *the cost of bringing the contract current is near zero* — in time, tokens, and
human attention. **Not the cost of building it, the cost of keeping it true.**
**Prevents.** Rot. **A rotted contract is worse than no contract at all, because people trust
contracts.**
**Machine test.** Time a one-property change end-to-end (edit → regenerate → downstream consumes). If
it needs a meeting, a person, or an afternoon, it will not stay true.
**The investment gate (see §3).** 25 simple components on one platform → *don't spend on this.*
100+ components across 4 implementations changing weekly → **economics decides the architecture for
you.**

### Gate 7 — Evolvable over simply flexible
**Rule.** Strict ≠ static. **A contract that can't change dies; a contract that changes without
governance was never a contract.** There must be a record of *why* the shape is what it is and *how* it
changed.
**Prevents.** Drift rebranded as flexibility — *evolving the contract privately, in a manner
undetectable downstream without reading the entire contract from scratch every time.*
**Machine test.** Can a consumer diff schema version N against N-1 and see exactly what changed, then
**opt in when ready**?
**The machinery: ADRs.** Architectural Decision Records drive new schema versions, keep specs valid,
and communicate downstream. A breadth-y ADR is a feature, not a failure — it forces iteration and
alignment before the change lands.
**The tell that it's working:** downstream partners *pushing back* ("our deterministic scripts aren't
ready — delay a week") is a **welcome outcome**. Conversations shift from complicated interpretation to
simple coordination, and change feels like business-as-usual rather than a threat to stability.

---

## 3. The investment gate — when NOT to build a contract

This is the part most easily skipped and most expensive to get wrong. Contracts are infrastructure;
infrastructure below its break-even is pure cost.

**Don't build one when:** a small component count, one implementation, infrequent change, one team
in one room. *For some, markdown may be all you need* — said by the person who spent 18 months
building a schema.

**Build one when any of these hold:**
- **Multiplicity** — components × implementations × change-frequency has passed what human vigilance
  can hold. (The system's promise of consistency, quality and pace resting on human vigilance *is* the
  failure mode; teams no longer have time for it.)
- **Arbitration is actually needed** — two or more implementations already disagree and a human is
  currently the tiebreaker.
- **Replacement/migration** — you are swapping an implementation and need a definition of "equivalent"
  that isn't "looks the same to me." (This is the highest-value, lowest-cost entry point: the contract
  pays for itself as the migration's acceptance criteria. See the DataTable/TanStack application.)
- **Agents are consuming it** — the moment agents build from the artifact, ambiguity compounds
  invisibly (Gate 4's boundary trap, Gate 5's inference layering).

**The payoff to expect.** With a strong contract, *scripts generate 80–90% of the code you need before
agents get to work* — leaving agentic inference for the last strides, not foundation-up construction,
and isolating what was generated when things change. And handoff meetings per platform team get
replaced by one repeatable command plus occasional Slack clarifications.

---

## 4. The contract maturity ladder

Useful for placing any existing artifact and naming the next rung. Climb one rung at a time; most teams
sit at L1 and believe they are at L3.

| Rung | Artifact | Arbitrates? | What it buys | What it can't do |
|---|---|---|---|---|
| **L0** | Prose docs / wiki | No | Shared understanding | Anything mechanical |
| **L1** | Templated markdown (Layout / Props / Anatomy tables) | No | Anyone authors it, PRs review it, agents read *and write* it, zero tooling | Structural validation; arbitration |
| **L2** | Typed data spec + published schema (YAML/JSON) | Structurally | Malformed becomes impossible; two-level verification begins | Prove implementations conform |
| **L3** | L2 + deterministic generation & validation (CSS, stories, TS types, scaffolds) | Yes, mechanically | Marginal cost of regeneration → ~0; empty-diff proof | Survive its own evolution |
| **L4** | L3 + versioned schema + ADR governance + consumer opt-in | Yes, over time | Change becomes business-as-usual | — |

L1 is not a failure — *markdown spread for good reasons* and is the correct answer below the
investment gate. It is a failure only when it is asked to arbitrate.

---

## 5. Where our own stack currently fails these gates

The transferable value is not the principles; it is running them against what we already have.

1. **Framework #09's 18-facet schema is a *documentation* schema, not a contract schema.** Facets 1–17
   are prose-shaped and human-authored; only facet 18 (the machine-readable intent record) is
   contract-shaped. **Delta:** treat 18 as the contract and 1–17 as commentary — anything load-bearing
   in 1–17 must be promoted into the typed record, and anything that fails the deletion test (Gate 4)
   should be deleted rather than preserved as prose.
2. **`DESIGN.md` is unverifiable by construction — and that's correct for what it does.** Its own
   philosophy is *prose over tokens*, which is right for **visual identity** (framing context) and
   wrong for **component decisions** (guidelines). Framework #09 §12 already says DESIGN.md is not the
   system of record for component usage/anatomy/states; the contract lens gives that rule teeth: prose
   cannot arbitrate, so nothing load-bearing may live only there.
3. **We currently have five candidate sources for the same decision** — Figma variants, `centric-ui`
   CVA code, `ds-docs` MDX, `DESIGN.md`, and the `ux-components` MCP. That is a Gate 2 failure by
   construction. **Delta:** name the arbiter *per decision class* (styling values, component API,
   states, a11y, content) and make the other four derived or explicitly non-normative.
4. **Figma-derived pipelines produce testimony, not contracts.** `figma-repo-sync-plugin` reads Figma
   as source. Per Gate 3 that output is a witness statement until it passes through a neutralizing
   transform (`start`/`end` not `left`/`right`; numeric props re-typed from strings; `INSTANCE_SWAP`
   resolved to a real prop type). **Delta:** make the transform layer explicit and named, not implicit
   in the generator.
5. **Canon ≠ contract.** The `ux-components` MCP answers *what a Dialog is across 68 systems*. It is a
   catalog, and a good one. It is **not** our arbitration artifact for what *our* Dialog is. Keep the
   two roles separate or the canon quietly becomes an un-owned pseudo-contract.
6. **Our state model is already a Gate 1 + Gate 2 win — keep it.** Splitting interaction enum /
   configuration booleans / validation enum / selection (framework #09 §8d, from Curtis's *Sorry State
   of States*) is exactly normalization + typing applied to states. It is the template for how the rest
   of the facets should be modeled.

---

## 6. The wider field — four peers, and what each adds

Curtis's piece links out to a live conversation. Reading the whole set (2026-07-28) changes the picture
in useful ways: **nothing contradicts the seven gates**, but three of the four add something the source
article doesn't, and two supply cautions worth respecting.

### 6a. Christian Morales Achiardi — *Design systems are contracts, not libraries*
**Adds the conceptual frame.** Using Meadows' definition of a system (elements · interconnections ·
purpose): **components and tokens are the *elements*; contracts are the *interconnections*.** Most
teams build only elements, which is why systems decay — the interconnections were never made explicit,
so they degrade silently. *"The unit of thought in a design system isn't the component. It's the
contract."*

The **derivation chain** is the most portable idea here:

```
articulated purpose  →  standards & definitions  →  required behavior  →  contracts  →  components
   ("reduce friction")   ("primary actions            (relationships          (tool-specific
                          always dominant")            between elements)       implementations)
```

> *"Building from articulation downward produces durable systems. Building from components upward
> produces libraries."*

Two more that earn their keep: **contracts persist across migrations** — when the framework changes you
rebuild the components, and the contracts hold — and the **behavioral audit**: judge a system by what it
actually does, not what its docs claim. *A system whose docs say "consistency and reusability" but whose
behavior is "every team forks the library" does not have the purpose its documentation claims.*

### 6b. Christine Vallaure — *the component lives in neither Figma nor code*
**Adds the operational discipline and the hardest rule in the set.** The contract is a **third, neutral
artifact**, and:

> **Figma and code are never allowed to update each other directly.** Changes land in the contract
> first, are reviewed like any code change, then both outputs regenerate.

That single rule is what our current five-source situation (§5.3) violates. It also brings:
- **The three-way differ** — a checker comparing contract ↔ design library ↔ code, reporting exact
  mismatches, byte-for-byte against a recorded copy. *"It's a compiler, not a generative model."*
- **The A/B evidence** — an ungoverned agent building UI scored **69/100 with 90 violations**; the same
  model held to the contract scored **100/100**, reporting gaps rather than fabricating values.
- **The markdown verdict, stated most cleanly:** *"A markdown file has to be understood, and
  understanding varies. But a contract only has to match, and matching is deterministic."*
- **A capacity caution we should take personally.** Solo/tiny teams don't need contracts (no handoff to
  arbitrate). **Mid-size orgs (~20–200) have the highest need and the *lowest* capacity to build the
  tooling.** Enterprises fit because they can staff it. *"Both need it, the middle and the top. Only one
  can run it."* Read against §3: passing the investment gate on *need* does not mean passing it on
  *capacity* — the honest answer for the middle is adopt an existing format, don't author tooling.
- **The generate direction.** Where Curtis extracts *from* Figma and transforms, Vallaure generates
  *into* Figma from the contract. Not a contradiction — brownfield vs greenfield, and they converge
  (extract once to bootstrap, then flip to generate).

### 6c. TJ Pitre / Southleft — *Use AI to Need Less AI*
**Adds the division-of-labor rule that makes Gate 5 actionable.** The work splits into two piles:
**authoring** (judgment-heavy, happens once → AI is genuinely good at it) and **enforcement** (recurs
forever, must be boring → determinism, always). The fatigue people feel isn't AI, it's *"paying
inference costs for problems that were never probabilistic to begin with."* Which button color to use is
a lookup, not a judgment call.

> **"Authority belongs to whatever layer can refuse deterministically, not whatever layer instructs
> loudest. A model can be talked around. A schema can't."**

This is the sharpest statement of why `AGENTS.md` prose and skill rules are *not* enforcement — they
instruct, they don't refuse. The enforcement layer is schema validation in CI. Also useful: the
cost framing (~1 second and zero tokens per component for deterministic extraction, vs 5–10 minutes and
~100k tokens for an agentic pass) and the call to **converge on shared formats** rather than each team
building its own pipeline.

### 6d. PJ Onori — **DSDS** (Design System Documentation Spec)

**Adds the missing half of the stack, and it is a different layer than everything above.** DSDS models
**documentation as data**. Principles still hold: portability, one unified source for humans *and*
parsers *and* agents, and scalability. *"DSDS has strong opinions, but it doesn't force them on you."*
Documentation only — if a better source of truth exists (DTCG values, CEM/specs, Storybook, Figma),
DSDS links rather than restating.

**Shape as of 0.20.0 (fetched 2026-09-01).** The 2026-07-28 note described **v0.15.2**: 6 entity types
(components, tokens, themes, foundations, patterns, guides) × 17 typed `kind` blocks (anatomy, api,
checklist, design-specifications, interactions, states, variants, …). That description is historical.
0.20.0 collapsed it:

| 0.15.2 | 0.20.0 |
|---|---|
| 6 entity types | 5 well-known kinds: `system`, `component`, `token`, `theme`, `entry` (+ namespaced custom) |
| 17 typed kind blocks | 3 section kinds (`guidelines`, `definitions`, `steps`) + generic `section` + `freeform` |
| One implied audience | `for: human \| agent \| all` on every section |
| Foundations / patterns / guides as first-class kinds | Those become `entry` or `shared[]` |

Component-specific fields moved *out* of generic section kinds: `sourceFiles`, `specs` (CEM or
equivalent), `traits` (boolean vs enum), `combos` (must / must-not pairing), `imports`. `$extensions`
remains the escape hatch.

**The mapping onto our own framework is still exact:**

| Our layer | Its machine-readable form |
|---|---|
| Framework #09 **facets 1–17** (documentation) | **DSDS** (0.20 document as a *view*, not a second schema) |
| Framework #09 **facet 18** (the arbitration record) | **Specs / DS Contracts** |
| Token values | **DTCG** |

So the formats are **complements, not competitors** — a distinction easy to miss when they all
call themselves "design system as data." If we want facets 1–17 as data rather than prose, adopt
DSDS rather than inventing a shape. Projection, audience stamps, and `combos` encoding:
[[agentic-ds-context-model]].

### 6e. The contract boundary — the one thing everyone agrees to leave OUT

Both reference implementations draw the same line, and it protects Gate 6 (a contract that swallows
everything cannot be kept true):

| In the contract | Out of it |
|---|---|
| The required **outcome** ("focus returns to the trigger on close") | The **technique** (how the focus trap is built) |
| Keyboard **map** | Interaction **craft** — drag physics, typeahead tuning, easing |
| Token bindings, computed values | CSS craftsmanship, cascade strategy |
| **Composition** examples (which slots hold what) | **Usage** examples ("what makes a good pricing card") |
| a11y **floors** — contrast, target size, roles | The a11y implementation review |
| Which prop configurations are **invalid** | Whether this component was the **wrong choice** |

**Outcome vs technique is the load-bearing distinction.** Pull craft in and the contract rots; push
outcomes out and it can't arbitrate the thing implementations most often get wrong. And the corollary:
**a contract tells you what *our* Dialog is — it never tells you that you wanted a Sheet.** The judgment
layers (framework #09 §4/§6/§7) sit above it and are not replaced by it.

---

## 7. Techniques worth stealing from the reference schema

The Specs ADR corpus (~60 records) is the most concrete artifact in the field. These transferred
directly into [[component-contract-schema]] v0.2:

- **A schema constitution** — (I) type–schema symmetry, no drift, enforced in the same commit;
  (II) no runtime logic in the model, only pure data shapes; (III) minimal, stable, intentional API,
  where removal/rename is MAJOR. Three of its ADRs exist purely to repair type/schema drift, which is
  the evidence rule I earns its place.
- **Variants are deltas, resolved by specificity** — a complete `default` plus sparse overrides; select
  variants whose configuration is a subset of the target, apply fewest-keys-first, and use
  **property-level replacement, never deep merge**. Reported >95% output reduction, and it is *the*
  concrete answer to variant explosion (3 booleans = 8 variants × 15 elements × 40 properties = 4,800
  entries, for maybe a dozen real decisions).
- **State classification — browser-driven vs consumer-controlled.** `hover`/`active`/`focus` happen to
  you (→ pseudo-class selectors, **omitted from the props interface**); `disabled`/`readonly`/`checked`/
  `expanded`/`pressed`/`selected` are set by you (→ ARIA/attribute selectors, **in the interface**). One
  classification drives both the styling output and the API surface. This extends our existing
  four-concern state model ([[figma-variable-state-representation]], framework §8d) with the axis it was
  missing, and it kills the most common component-API bug in the field: shipping a `hover` prop.
- **`invalidPropConfigurations`** — model what must *not* exist. A contract that only says what is legal
  cannot reject a whole class of malformed spec. Almost everyone omits this.
- **Opt-in inference with a declared guard and declared false positives** — the number-prop ADR names
  `"90210"` (postal code) and `"1.0"` (version string) as cases its heuristic gets wrong, *in the ADR*.
  Opt-in + written guard + named failures = configured inference. Any of the three missing = hoped-for
  inference.
- **Collapsed-or-expanded values** — `padding: 12` when uniform, `{top, end, bottom, start}` only when
  they differ. Normalization one level below the decision level.
- **Reserved-key hygiene** — `$ref` for JSON Pointer, `$binding` for prop bindings (renamed *because* it
  collided with JSON Schema), `$token` for DTCG references, `$extensions` (reverse-domain keyed) as the
  only sanctioned platform-metadata escape hatch.
- **`Conditional` as data** — `{ if: {$binding}, then, else }` keeps "the spinner shows when loading"
  verifiable without putting logic in the model.
- **"Demo content is not a default"** — `examples` separate from `default`, `default` optional. This is
  precisely the bug we already hit in the figma-repo-sync-plugin, where every generated TabsTrigger said
  "List view."
- **The three-way differ in CI** as a first-class verification level, not a nice-to-have.

---

## 8. Replacement work — the legacy feature list is testimony too

The most tempting shortcut when replacing a component is to take the old implementation's feature
inventory as the new contract's requirements. It looks rigorous — it is exhaustive, file-verified,
already paid for. **It is testimony (Gate 3), and adopting it untransformed is the same category error
as publishing a raw Figma export as the contract.** The biasing party is just an old codebase instead of
a design tool.

Why it matters more than it looks: a legacy feature list is a faithful record of what **one party**
built, under constraints that may no longer apply, for a user who may not be the new user. **A contract
derived from a legacy feature list can only ever specify a re-creation.** If the goal is a better
product rather than a port, the derivation has to run the other way.

### Articulation-downward vs components-upward

```
  ✅ articulated purpose → standards & definitions → required behavior → CONTRACT → components
  ❌ legacy components → their feature inventory → CONTRACT → new components
```

The first produces a durable system; the second produces a library that inherits decisions nobody
re-made (Morales Achiardi, §6a). For a replacement, the sources of "required behavior" are, in order:
**(1)** the product's own declared UX/product intent, **(2)** the target user's jobs — which may differ
from the legacy user's, **(3)** the lineage-neutral pattern canon, **(4)** the target library's
capability surface *as a menu, never a mandate* ("the library supports it" is not a reason to specify
it).

### What prior art is still good for

Demote it, don't discard it. Legacy migration analysis keeps three legitimate roles, all consulted
**after** the contract has a first draft — order matters, because reading it first anchors the draft:

| Role | Use it for | Never for |
|---|---|---|
| **Pitfall ledger** | Traps someone already hit — implementation-shaped findings transfer across products | Deciding what the new thing should do |
| **Effort calibration** | Sizing a feature you have *independently* decided to build | Justifying that the feature exists |
| **Parity horizon** | A later migration may need genuine parity. Note the delta; don't pre-build to it | Scoping v1 |

**Implementation-shaped findings transfer; product-shaped ones don't.** "This library feature is
actually a custom module, budget it as engineering" is true regardless of the user. "Users need
multi-level grouping on reference keys" is a claim about *those* users and must be re-derived.

### The gate

**Every feature in the contract cites its provenance** — a user job, a product/UX spec, or a named
pattern in the canon. *"The old system has it"* is not provenance. This is cheap, it is checkable in
review, and it is the whole reason for writing the contract before the port: the question gets asked
once, in the open, instead of being answered implicitly by whatever the old code happened to do.

---

## 9. Scope down, don't shape down — designing for the growth horizon

A companion to §8, and the failure mode on the *other* side. §8 says don't inherit a legacy feature
list. This says don't mistake that for permission to build a smaller thing with a lower ceiling.

**The situation.** A product targets an entry segment (SMB, self-serve, a single vertical) with a
known horizon beyond it (enterprise, platform, multi-vertical). The naive readings both fail:
build everything the horizon implies → over-built and unshippable; build only what the entry segment
needs *and shape it that way* → a rewrite at the first sign of growth.

**The correct reading:** the entry segment's workflows are the **foundation the richer processes
extend**, not a simplified fork of them. Smaller organizations routinely *aspire* to enterprise
practice — adopting it is frequently how they grow — so the entry experience should be the first floor
of the same building, not a different building.

### The mechanism is already in the contract model

This is exactly what the schema/spec split is for:

| | Carries | Answers |
|---|---|---|
| **Schema / shape** | the growth horizon | what a contract *can* say |
| **Spec / scope** | today's segment | what a contract *does* say |

They are **separately versioned** for precisely this reason (§1), and this is what **Gate 7** —
evolvable over merely flexible — is protecting. *Growth that forces a MAJOR schema break was a design
failure committed years earlier.*

> **The operative rule: model the axis, ship one value on it.**
> Declaring an axis you don't populate costs ~nothing. Adding an axis later is a breaking change across
> every consumer and every surface. Depth *values* grow cheaply; missing *concepts* do not.

### Three practices that follow

1. **Record the decision not to build.** `enabled: false` with a `rationale` (and, where useful, the
   reserved shape) preserves intent and makes the growth path legible. Silence loses the reasoning and
   invites someone to re-litigate it from scratch in a year.
2. **Watch for ownership/scope fields collapsed to a constant.** The classic: state ownership hardcoded
   to the component "for now," which turns persistence, deep-linking and saved views into a rewrite of
   every consumer. A field that *exists* with one value is a config change; a field that doesn't exist
   is an API break.
3. **Keep capability and entitlement orthogonal.** Never encode packaging or tier boundaries in a
   component contract. **Tier boundaries move** — the Figma pattern is the canonical illustration:
   capability proven at enterprise flowed downward as smaller teams found the same value foundational,
   and the delineation had to be redrawn repeatedly (variable mode limits being the well-known case).
   If a contract says a capability is "enterprise only," every re-tiering becomes a component change
   across every implementation. Entitlement gates the *configuration*; it never gates the *component*.

### Calibrate, don't extrapolate

Adoption speed differs wildly by market — a design-tooling audience absorbs change far faster than,
say, fashion, consumer goods or food manufacturing. **This is not an argument for building the horizon's
features now.** It is an argument that the architecture must never be the thing that *blocks* the
growth, whenever it arrives. Ship narrow; keep the shape wide.

---

## 10. Standing rules adopted from this

- **Run the arbitration test before calling anything a spec.** If a human must adjudicate, say
  "description" and stop over-claiming.
- **Apply the deletion test to load-bearing prose.** Unverifiable + load-bearing = move it into the
  typed model or cut it.
- **Never let an untransformed tool export be the contract.** Extract → neutralize → *then* publish.
  **This includes a legacy implementation's feature inventory** — that is testimony too, and a contract
  derived from it can only specify a re-creation (§8).
- **On replacement work, derive articulation-downward.** Purpose → required behavior → contract →
  components, never legacy-features → contract. Consult prior art *after* the draft exists, as a pitfall
  ledger and effort calibrator only. **Every feature cites its provenance; "the old system has it" is not
  provenance.**
- **Scope down, don't shape down.** The entry segment sets the *spec*; the growth horizon sets the
  *schema*. **Model the axis, ship one value on it** — declaring an axis is free, adding one later
  breaks every consumer. Record decisions not to build (`enabled: false` + rationale), never omit them.
- **Capability and entitlement stay orthogonal.** Tier boundaries move; never encode packaging in a
  component contract, or every re-tiering becomes a component change.
- **Version the model separately from the content**, and ship changes as ADRs consumers can opt into.
- **Prove the contract by regenerating twice and diffing.** Empty diff = evidence; noisy diff = the
  contract is under-specified.
- **Check the investment gate before building — on need *and* on capacity.** Below it, markdown is the
  right answer. Above it but short on capacity (the mid-size trap), adopt an existing format rather than
  authoring tooling.
- **Watch the LLM boundary.** If an agent smooths the artifact anywhere between validation and
  consumption, verification stopped there and everything after it is inference on inference.
- **AI at authoring time; determinism at run time.** Use a model to *write* a contract from a messy
  source; never to *enforce* one. Enforcement is whatever layer can refuse — a schema in CI, not prose
  in `AGENTS.md`.
- **Never let two implementations update each other directly.** Changes land in the contract, get
  reviewed, then both regenerate — and a differ proves they still agree.
- **Keep craft out.** The contract states required *outcomes*, never *techniques*; composition examples,
  never usage guidance. A contract that absorbs craft cannot be kept true.
- **Audit systems by behavior, not by documentation.** If the docs claim a purpose the actual behavior
  contradicts, the stated purpose isn't the real one.
- **Prefer convergence over invention.** Model against DTCG / Specs / DSDS and stay migratable; don't
  defend a bespoke schema.

---

## Related

- [[09-component-and-pattern-framework]] — §5a the contract layer; §5 the 18-facet schema; §11 the
  AI-legible layer; §12 the `DESIGN.md` protocol
- [component-contract-schema.md](../../02-shared-references/component-contract-schema.md) — the
  portable schema model + verification levels + ADR protocol
- [[centric-plm-design-system]] — the data-table / TanStack thread this first applies to
- [[figma-source-audit-patterns]] · [[figma-component-composition-from-react]] — the Figma-as-testimony
  problem in our own pipelines
- [[radix-derived-color-system]] · [[figma-tailwind-token-pipeline]] — token-layer precedent for
  "one theme-control point" (Gate 2 applied to tokens)
- [[adversarial-verify-label-volatility]] — why verification design matters more than verifier volume
- [[agentic-ds-context-model]] — 2026-09-01 remap onto DSDS 0.20 + agentic harness specs; three-graph rule
- [[dsds-constitution]] — project-independent DSDS 0.20 view (combos + `for:` stamps)
- [[idempotent-design-decisions]] — standing methods; not a contract and not style values
