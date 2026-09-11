---
tags: [design-systems, brad-frost, atomic-design, ai, mortar, steel-curtain, southleft]
created: 2026-09-11
updated: 2026-09-11
status: validated
confidence: high
sources:
  - "Brad Frost — Atomic Design (atomicdesign.bradfrost.com)"
  - "Brad Frost / Southleft (TJ Pitre, Ian Frost) — AI and Design Systems (courses.bradfrost.com, captured 2026-09-10–11)"
  - "07-projects/22-ai-design-systems-course/synthesis/running.md"
related_skills: [ai-design-systems, ds-advisor, design-engineer, design-system-ops, ds-generation-pipeline, ux-component-library]
related_projects: [22-ai-design-systems-course]
relations:
  builds-on: ["[[component-contracts-and-schemas]]", "[[nathan-curtis-ds-ops-substack]]"]
  relates-to: ["[[a11y-measurement-vs-judgment]]", "[[contracts-first-delivery]]"]
---

# AI and design systems — Frost / Southleft canon absorbed

## For future agent

- **TL;DR:** Brad Frost's models (Atomic Design, three-legged stool, AI-as-mortar, steel curtain, context-based DS) are first-class workspace doctrine. Operating model = [[18-design-systems-ai-operating-model]]; procedure = [[ai-design-systems]]. This note is provenance + what was already here vs what the 2026 course added.
- **Key claims:** DS = UI infrastructure / org story, not a kit. AI fills cracks in a solid-line graph; it must not pour a parallel universe. "Is it good?" is the era's question. Determinism at the gate; LLM at authoring time. Agents are users (HTML + markdown). Gen UI = JSON + recipes + confidence.
- **As of:** 2026-09 · **Status:** current

---

## Already in the workspace (do not duplicate)

| Claim | Where it already lives |
|---|---|
| Atomic Design mapping + components/recipes/snowflakes | #09 §3, resource canon |
| Intent as the unit; AI-legible JSON; A2UI catalog | #09 §11 / §11a, [[ux-component-library]] |
| Description vs contract; testimony vs live SoR; AI at authoring, determinism at run time | [[component-contracts-and-schemas]] + #09 §5a |
| Configuration collapse / slots for AI-ready composition | [[nathan-curtis-ds-ops-substack]] |
| Axe/toolkit vs judgment; LLM must not be the a11y verdict | [[a11y-measurement-vs-judgment]], [[accessibility-beyond-wcag-baseline]] |
| Contracts-first delivery; silent degradation | [[contracts-first-delivery]], #14 |
| Figma is one signatory, not the only source of truth | component-contracts entry; ds-advisor "Figma is the knowledge center" is **altitude for designers**, not a collapse of the stool |

The course did not invent those. It **named the envelope** they sit in and gave the org/process verbs this vault was missing.

---

## What the course added (now doctrine)

### 1. Definition and stool

Frost: *A design system is critical UI infrastructure. It is the story of how your organization designs and builds digital interfaces.* Ingredients: UI standards + three-legged stool (design lib, code lib, docs) + people/process. LLMs make the storytelling layer more important — they will invent a different story if you don't give them yours.

### 2. Mortar, not a parallel universe

Solid-line dependencies replaced dotted-line copy-paste. That graph is fragile. AI oozes into cracks; it does not replace bricks. Generating a DS from scratch ≈ adopting Material wholesale.

### 3. Quality as the era question

Fourteen principles (humanity, safety, intentionality, responsibility, nuance, quality, accessibility-as-driver's-seat, foundations, context, collaboration, curiosity, multiplicity, practicality, durability). **Foundations + Context + Quality** are the crux. "Is it good?" once a site can be emitted in seconds.

### 4. Five qualities and the check engine

Complete · sound · synchronized · extensible · AI-ready. Cosmetic vs structural vs garbage-in. Wiring a DS MCP can **lower** a coverage score by finding holes — that is the engine working.

### 5. Context-based DS (TJ Pitre)

Lifecycle inheritance with reverse feedback. Designer owns the first code draft against the **published** package; named context engineer; playgrounds import the package. Claude Design forking a branded library is a defect; Story UI saying "this is all I got" is honest.

### 6. Steel curtain and on-rails

Off-rails bake-offs teach. On-rails ships. Steel curtain = CI + evals + axe **before** users see vibe slop. Look-done CEO demos are the failure mode. Codify riff vs ship.

### 7. Agents as users and gen UI

Dual publish (Kaelig): HTML canon + markdown twin. Gen UI: agent speaks JSON, blessed catalog, recipes, confidence disclosed, views ephemeral. Hyperpersonalization: tokens as handshake; more context → more safety and agency. Personalized a11y, not LLM-as-judge.

### 8. Org arc

Sell → pilot → rollout → govern. Pilot *is* the pitch (real planned-not-started work, rightsized). Govern from day one of the still-living pilot: dual-filed issues, cron inspection, tools earn a place. Care for humans.

### 9. Tool distinctions that keep biting

Official Figma MCP ≠ Console MCP (write path clones outside sets, missed icon rebinds). MCP live-SoR vs smoothed testimony — same tension as the contract entry. Git is the sandbox because AI can nuke a codebase. Cross-repo issues with product context = DS intake with a ticket the product team can use.

---

## Centric-shaped homework (do not paste into c8/*)

Keep these as personal-workspace prompts; execute inside employer repos under that profile:

- Dual HTML + markdown for agent-facing DS meaning
- Adoption-plan skill on a priority *and* a neglected legacy
- Prototyping strategy with a riff vs ship line
- Steel curtain before opening designer-owned drafts
- Record architecture so inspectors don't score Figma as "unmaintained" when it is a maintained leg
- Dead-prop / language-contract flywheel
- Do not leave a11y to LLM-as-judge

---

## Course project

Notes (not transcripts): `07-projects/22-ai-design-systems-course/`. Caption gaps remain (Ch6 selling ~44m, Ch5 A2UI, some early jams). Resource hub: https://resources.aianddesign.systems
