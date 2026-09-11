---
title: Design Systems × AI Operating Model
tags: [framework, design-systems, ai, atomic-design, brad-frost, mortar, steel-curtain]
created: 2026-09-11
updated: 2026-09-11
links:
  - "[[09-component-and-pattern-framework]]"
  - "[[06-qa-operating-model]]"
  - "[[14-engineering-operating-model]]"
  - "[[ds-advisor]]"
  - "[[ai-design-systems]]"
  - "[[component-contracts-and-schemas]]"
  - "[[ai-and-design-systems]]"
---

# 18 — Design Systems × AI Operating Model

*The operating model for how a design system and AI work together. Where [[09-component-and-pattern-framework|#09]] answers what each component is **for**, this framework answers: **what a design system is, how AI attaches to it, and what must be true before generated UI may ship.** It is the L1 for AI×DS work. Procedure lives in [[ai-design-systems]]; provenance in [[ai-and-design-systems]].*

Canon: Brad Frost (Atomic Design; *AI and Design Systems* with Southleft — TJ Pitre, Ian Frost). Sean's DS practice for the last eight years runs on these models. They outrank vendor plugin defaults and vibe-coding fashion.

---

## Core conviction

**A design system is critical UI infrastructure — the story of how the organization designs and builds interfaces.** It is standards + the three-legged stool (design library, code library, documentation) + people and process. History's punchline: dotted-line copy-paste became **solid-line dependencies**. That graph is hard-earned and fragile.

**AI is mortar, not a replacement.** It fills cracks between existing bricks. It does not get to pour a parallel universe of components, tokens, or docs. Design systems still do **quality-at-scale**; AI supplies speed and connective tissue. Once generation is cheap, **"Is it good?"** is the defining question.

---

## When to invoke

Any work where AI meets the design system: inspection, MCP, vibe coding, generative UI, designer-owned code drafts, agent users, DS adoption with AI, selling/piloting/governing AI×DS. Load alongside #09 for component choice; alongside #06/#14 when generated work must pass a done-gate. Steps aside for pure visual craft with no generation or agent in the loop (#01/#05).

---

## Mental models (Frost canon)

Memorize these. They resolve most AI×DS decisions before a tool is named.

| Model | Rule |
|---|---|
| **Atomic Design** | Tokens sit *below* atoms. Atoms ≈ primitives; molecules/organisms ≈ components; templates/pages ≈ screens. Composition grammar, not a folder taxonomy. Schema and choice trees stay in #09. |
| **Reuse gradient** | **Components** (agnostic, max reuse) → **Recipes** (product-specific compositions) → **Snowflakes** (one-offs). Name and govern each tier differently. Gen UI assembles recipes from the blessed catalog; it does not mint snowflakes by default. |
| **Three-legged stool** | Design lib + code lib + docs. People/process wield the stool. Do not collapse "the system" to Figma because an MCP is open. Record which legs are actually maintained. |
| **Solid-line dependencies** | Instances, packages, and published libraries are the product. Copy-paste is a regression to dotted lines. |
| **AI as mortar** | Point the model at the live graph. Generating a new kit from a prompt is the same failure as adopting Material wholesale. |
| **Five qualities** | Complete · sound · synchronized · extensible · **AI-ready**. Cosmetic polish is not the check engine. |
| **Language is the contract** | Prop names, tokens, and docs are what the model reasons with. `inverted` → `knockout` with deprecation; dead props erode trust. |
| **Context-based DS** | Each lifecycle stage inherits the last. Designer owns the first code draft against the **published** library; a named context engineer reviews; playgrounds consume the validated package. |
| **On-rails vs off-rails** | Off-rails bake-offs (v0, Bolt, Lovable, Claude Design) are education. Shipping happens on-rails (published system + steel curtain). Look-done CEO demos are the trap. |
| **Steel curtain** | Deterministic CI, evals ("does this PR solve the ticket?"), and axe **before** users see vibe output. LLM-as-judge is advisory, never the gate. |
| **Agents as users** | Illegible to machines = invisible to people using agents. Dual publish: HTML canon + markdown twin. |
| **Generative UI** | Agent speaks **JSON not code**. Blessed catalog + recipes + on-device map + **confidence** (under 50%, say so). Views are ephemeral. Do not emit new React as the default. |
| **Org arc** | **Sell → pilot → rollout → govern.** The pilot *is* the pitch. Govern from day one of the still-living pilot. Inform, don't pitch, at rollout. New tools must earn a place. |

### Fourteen principles (course constitution)

Humanity · Safety · Intentionality · Responsibility · Nuance · **Quality** · Accessibility (WCAG *and* humans in the driver's seat) · **Foundations** · **Context** · Collaboration · Curiosity · Multiplicity · Practicality · Durability.

When a demo conflicts with **Foundations / Quality / driver's-seat accessibility**, the principle wins.

---

## Ordered pipeline

Named stages. Skip only with a recorded reason.

0. **Record the architecture.** Which stool legs are maintained? (Eddie scored a missing Figma leg that Centric still keeps.) Inspectors that grade the wrong missing piece waste the cycle.
1. **Inspect, don't generate.** Check engine: cosmetic vs structural vs "AI will generate garbage." Score complete / sound / synchronized / extensible / AI-ready. Inspect a priority surface *and* a neglected legacy.
2. **Make the system AI-ready.** Kill dead props; align language; machine-readable docs (docs existing ≠ machine-readable); put remote MCP in the tools people already use. Coverage can *drop* after wiring MCP because more holes become visible — that is success.
3. **Context-based authoring.** Design ideation → design QA (deterministic lint + optional LLM-as-judge) → designer-owned first draft on a design branch against the **published** package → context-engineer PR → tests → publish → playground that imports the package (not a branded fork).
4. **Product on-rails.** Name the flavor: ongoing / greenfield / legacy adoption / retheme. Discovery wrangles scattered context. Adoption-plan skill; outside-in page shell; steel curtain before opening drafts to the org. Codify **riff vs ship**.
5. **Widen "user" to agents.** Dual HTML+markdown. Gen UI only from blessed catalog + recipes. Hyperpersonalization: tokens as handshake; more context requires proportionally more safety and user agency.
6. **Invent next UX on a sanctioned slice.** Speech→text, realtime UI, creative infinite — protect the meat-and-potatoes roadmap and mental health. Combine new with old; venture cautiously.
7. **Operationalize.** Sell with a rightsized real-product pilot (planned-not-started work). Document pass/fail into markdown that becomes rails. Rollout copies an existing rebrand/replatform comms pattern; steel curtain makes the DS default, not goodwill. Govern: dual-filed issues (product + DS), cron inspection, GitHub hooks, token budgets. Take care of people; curated signal, not every-model pings.

---

## Done-gates

A slice is ready for review only when:

- The published system was the source, not a generated fork (or the fork is explicitly off-rails and labeled).
- Steel curtain ran: tests/CI and axe (or the a11y toolkit) on the changed surface. LLM critique does not substitute.
- Language/prop/token names match the live contract; no new dead props.
- If agents will consume it: markdown twin exists or is explicitly deferred with a date.
- If gen UI: output is catalog JSON + recipe, with confidence stated. No unexplained custom components.
- Architecture (which legs exist) is written down so the next inspection scores the right graph.
- riff vs ship is named. Look-done is not shipped.

---

## Absolute bans

- **Do not generate a design system from scratch** when one exists. Same failure as adopting Material wholesale.
- **Do not treat official Figma MCP and Console MCP as the same tool.** Live SoR vs write-path mess (clones outside component sets, missed icon rebinds).
- **Do not use LLM-as-judge as the accessibility or quality steel curtain.** Axe / CI / contracts arbitrate; the model advises.
- **Do not collapse the stool to one leg** because that's the MCP you have open.
- **Do not ship off-rails output** (footer ignoring the system, branded fork of the library) as the product.
- **Do not leave agent users with HTML-only docs.** Invisible to the people using agents.
- **Do not let a playground import a fork** when the job is to consume the validated package. Story UI saying "this is all I got" is more honest than Claude Design's branded fork.

---

## Measurement (L3)

| Claim | Evidence |
|---|---|
| System is AI-ready | Inspection score + named holes; MCP-connected pass that can *lower* coverage by revealing debt |
| On-rails | CI + evals + axe on the PR; package import in the playground |
| Gen UI | JSON payload maps to catalog; confidence <50% is disclosed |
| A11y | Toolkit/axe, not an LLM paragraph |
| Adoption | Baseline inspection of a priority *and* a neglected legacy; adoption-plan artifact |
| Governance | Dual-filed issues; cron or hook-fired inspection; pass/fail notes in markdown rails |

Audit ≠ critique: a score without a steel-curtain artifact is critique.

---

## Relationship to other frameworks

- **#09** — component intent, schema, contracts, A2UI catalog. This framework decides *whether and how* AI may touch that body of intent.
- **#02** — UX operational decisions inside a screen; this framework is the system/AI envelope around those screens.
- **#06 / #10 / #11** — "Is it good?" still grades against target-user expectations on native pixels, with failure modes named before shipping slop.
- **#14** — engineering done-gates; steel curtain is the DS-shaped instance of contracts-first delivery.
- **#08 / #13** — this file is the L1; [[ai-design-systems]] is the L2 command surface.

---

## Resource canon

- Brad Frost — *Atomic Design* (atomicdesign.bradfrost.com)
- Brad Frost / Southleft — *AI and Design Systems* (courses.bradfrost.com); resource hub: https://resources.aianddesign.systems
- TJ Pitre — context-based design systems; *Use AI to Need Less AI*
- Kaelig Deloumeau-Prigent — dual publish (HTML canon + markdown twin)
- Workspace already holding the arbitration layer: [[component-contracts-and-schemas]] (testimony vs contract; AI at authoring time, determinism at run time)
