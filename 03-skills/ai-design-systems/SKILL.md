---
name: ai-design-systems
description: >
  Operating procedure when AI meets a design system — inspection/check-engine,
  context-based designer-owned drafts, on-rails vs off-rails prototyping, steel
  curtain (CI/axe/evals not LLM-as-judge), dual publish for agent users, generative
  UI from a blessed catalog, and the sell→pilot→rollout→govern org arc. Trigger on
  vibe coding, generative UI, gen UI, A2UI, steel curtain, on-rails, off-rails,
  context-based design system, AI as mortar, FigmaLint, Story UI, Console MCP vs
  official Figma MCP, agents as users, dual publish, design system inspection,
  AI-ready DS, adoption-plan with AI, or "don't generate a design system from scratch."
  Brad Frost / Southleft models. Strategy still belongs to ds-advisor; component
  authoring to design-engineer; ops verbs to design-system-ops.
aliases: [ai-design-systems]
triggers: [ai design system, ai and design systems, vibe coding, generative ui, gen ui, a2ui, steel curtain, on-rails, off-rails, context-based design system, ai as mortar, figmalint, story ui, agents as users, dual publish, design system inspection, ai-ready, console mcp]
tier: spoke
domain: design
hub: ds-advisor
prerequisites: [ds-advisor]
related: [design-engineer, design-system-ops, ds-generation-pipeline, ux-component-library]
governed_by: [qa]
defers_to: [framework-18, framework-09, framework-13, ds-advisor, design-engineer]
rigor_role: command-hub
surfaces: ["*"]
spec_version: "2.2"
---

# AI × Design Systems — procedure

L2 command surface for [[18-design-systems-ai-operating-model]]. Foundations: [[design-foundations]] → hub [[ds-advisor]]. This spoke is the **when X, do Y** for AI attached to a living system. Do not restate Atomic Design or the component schema — those live in #18 and #09.

## When to use

AI is generating, inspecting, adopting, or serving UI *through* a design system. Vibe coding, MCP design-to-code, gen UI, agent-facing docs, DS+AI pilots.

## When NOT to use

- Component choice / anatomy / schema → [[ux-component-library]] + #09
- Token drift, deprecation, health reports without an AI loop → [[design-system-ops]]
- Figma mechanics (variables, component sets) → [[design-engineer]] + [[figma]]
- Generating a **new** token/component stack for a true greenfield with no system → ask once, then [[ds-generation-pipeline]] **after** the #17 ban is acknowledged

## Execution protocol

Name the verb. Run the matching play. Cite the steel-curtain evidence in the output.

```
/ds-ai <inspect|ready|draft|rails|agents|gen-ui|adopt>
```

### `inspect` — check engine

1. Record architecture: which stool legs are maintained (Figma / code package / docs / people-process).
2. Score the five qualities: complete · sound · synchronized · extensible · AI-ready. Separate cosmetic from structural from "AI will generate garbage."
3. Inspect **one priority** and **one neglected legacy**.
4. Output: score, named holes, what MCP would reveal that docs hide.

### `ready` — make the system AI-ready

1. Language contract: rename with deprecation; delete dead props.
2. Machine-readable docs (one file one job). "Docs exist" is not AI-ready.
3. Put remote MCP in the tools people already use. Official Figma MCP ≠ Console MCP — say which, and treat Console writes as messy (clones outside sets, missed rebinds).
4. Coverage may fall after wiring MCP. Report that as discovery, not regression theater.

### `draft` — context-based DS

Designer-owned first code draft against the **published** library, on a design branch.

1. Ideation in the design file using library components (not detached one-offs).
2. Design QA: deterministic lint first (FigmaLint-class); LLM-as-judge optional and never the gate.
3. First code draft on a branch that imports the package.
4. Named context engineer reviews the PR.
5. Tests + publish. Playgrounds (Story UI / Make / v0) **import the validated package**. A branded fork is a defect.

### `rails` — product work

1. Name the flavor: ongoing / greenfield / legacy adoption / retheme.
2. Off-rails bake-off is allowed as **education** and as a handoff *into* an on-rails rebuild. Label it. Do not ship it.
3. Adoption-plan: garage + baseline; outside-in page shell; riff vs ship bright line.
4. Steel curtain before the org sees it: CI, "does this PR solve the ticket?", axe/toolkit.

### `agents` — agents as users

1. Dual publish: HTML canon + markdown twin (Kaelig). Defer only with a date.
2. DS packages meaning beyond the org wall — tokens/docs an agent can fetch.
3. Personalized a11y via tokens/prefs; not "ask the LLM if it's accessible."

### `gen-ui` — generative UI

1. Agent emits **JSON**, not new component source.
2. Map to the blessed catalog + named recipes.
3. On-device deterministic map; optional model assist.
4. Confidence under 50% must be stated. Views are ephemeral.
5. Custom snowflake components require an explicit #09 exception + DDR.

### `adopt` — org arc

1. Name the phase: sell / pilot / rollout / govern.
2. Pilot **is** the pitch: rightsized real product, planned-not-started, inspection baseline, stack quick wins, write pass/fail into markdown rails.
3. Rollout: inform, don't pitch; copy an existing rebrand/replatform comms pattern; steel curtain makes the system default.
4. Govern from day one of the still-living pilot: dual-filed issues (product + DS), cron inspection, hooks, token budgets. New tools earn a place. Take care of people.

## Done-gates and bans

Copy [[18-design-systems-ai-operating-model]] — do not fork them here. If this skill and a plugin disagree, the framework wins.

## Outputs

- Inspection scorecard (five qualities + architecture)
- Adoption-plan (flavor, baseline, riff vs ship)
- Dual-publish checklist
- Gen-UI recipe + confidence
- Pilot/gov note (phase, success-for-them, feedback loop)

## Defers-to

- [[18-design-systems-ai-operating-model]] · [[09-component-and-pattern-framework]] · [[13-domain-rigor-stack]] · [[ds-advisor]] · [[design-engineer]]
- Plugin Figma skills are mechanics only.

## Related
- hub → [[ds-advisor]]
- governed-by → [[qa]]
- peer ↔ [[design-engineer]] · [[design-system-ops]] · [[ds-generation-pipeline]] · [[ux-component-library]] · [[lead-accessibility-architect]]
