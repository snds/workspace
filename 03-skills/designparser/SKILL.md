---
name: designparser
description: >
  Call the DesignParser MCP for evidence-backed design rules (77 rules, 14
  categories). Use when designing, critiquing, or auditing any UI/UX/visual/
  print/motion surface, or when Sean says designparser, "what rules apply",
  suggest_rules_for_context, or evaluate_design. This skill drives the MCP.
  It does not replace design-foundations, APCA contrast policy, /qa measurement,
  or a target system's own tokens. Do not copy rule bodies into the vault.
aliases: [designparser]
triggers: [designparser, designparser rules, what rules apply, suggest_rules_for_context, evaluate_design]
tier: cross-cutting
domain: design
prerequisites: [design-foundations]
related: [lead-ui-designer, lead-ux-designer, qa, a11y-visual]
defers_to: [framework-06, framework-13, a11y-visual, uid-color-for-ui]
requires: [designparser-mcp]
rigor_role: measurement
surfaces: ["*"]
spec_version: "2.2"
---

# DesignParser — call the rules, do not vendor them

L3 lookup over [designparser-mcp](https://github.com/designparser/designparser-mcp)
(v2.4, `npx -y designparser-mcp`). 77 rules in 14 categories, each with TL;DR,
key numbers, and sources. Code is MIT. Rule text is © designparser: use it in
work; do **not** republish it as a vault dataset.

`design-foundations` already orders the call on every design chain. This file is
the tool protocol.

## Preflight

Capability id: `designparser-mcp` ([[capability-registry]]). Detect a tool matching
`suggest_rules_for_context`. If absent: **degrade** — continue with foundations +
hub/spoke, say the rule lookup was skipped, surface the install. Do not invent
rule IDs.

## Call protocol (any design task)

1. One sentence: medium + surface + constraint (e.g. "enterprise SaaS compact density, dark mode, data table toolbar").
2. `suggest_rules_for_context` with that sentence. That is the default call.
3. Cite rule IDs in the work (`touch-target`, `wcag-contrast`, …).
4. Then apply [[design-foundations]] → hub → spoke, and the **target system's own tokens**.
5. `get_rule` / `get_rules_batch` only when a cited ID needs the deep-dive.
6. `evaluate_design` when judging an existing UI (description, HTML/CSS, or a screenshot you can describe). Checklist only. Not a `/qa` measured verdict.

### Tool pick

| Tool | When |
|---|---|
| `suggest_rules_for_context` | Default. Starting or changing a design. |
| `evaluate_design` | Critique / audit of something that exists. Optional `focus`. |
| `get_rule` / `get_rules_batch` | Deep-dive on known IDs (batch max 8). |
| `search_rules` | Fuzzy ("touch target research"). |
| `list_rules` | Browse by `category`, `priority`, or `tags`. |

All tools are read-only.

## Doctrine (workspace wins)

| Conflict | Winner |
|---|---|
| WCAG contrast numbers vs APCA-as-governance | Workspace: WCAG is the legal floor; APCA governs semantics ([[radix-derived-color-system]], [[a11y-visual]], [[uid-color-for-ui]]) |
| Generic spacing/type recipes vs a live DS | Target system tokens. Gaps are backlog, not a bypass ([[llm-safe-design-system-expressiveness]]) |
| `evaluate_design` checklist vs `/qa` | `/qa` + toolkits own measured verdicts. DesignParser is testimony + a checklist |
| "Never break" critical rules vs product constraint | Name the rule, name the constraint, decide. Do not silently drop the rule |

**Bad / good / why**
- Bad: paste 77 rules into `08-knowledge/` or answer WCAG from memory with no tool call.
- Good: `suggest_rules_for_context` → cite IDs → apply foundation + the system's tokens.
- Why: license forbids republishing the corpus; training data drifts; the MCP is the current source.

## Category → workspace owner

Do not let a category replace the owner. Use the rule, then the spoke.

| DesignParser category | Owner |
|---|---|
| `color` | [[found-color]] → [[uid-color-for-ui]] + [[a11y-visual]] |
| `typography` | [[found-typography]] → type/UI type spokes |
| `spacing` · `layout` | [[found-composition]] |
| `shadows` · `visual` | [[lead-ui-designer]] |
| `ux-laws` · `interaction` · `forms` | [[lead-ux-designer]] → [[ux-interaction-design]] |
| `navigation` | [[ux-information-architecture]] |
| `icons` | [[lead-icon-artist]] |
| `motion` | [[lead-motion-designer]] / `/motion` |
| `media` | imaging / visual spokes as the task implies |
| `print` | foundation (print-true) → [[lead-graphic-designer]] |

## Absolute bans

- Do not copy rule bodies into `08-knowledge/`, skills, or always-on rules.
- Do not treat an `evaluate_design` list as a Proofboard or `vqa` verdict.
- Do not skip the call because the topic "is well known."
- Do not install or vendor the GitHub `rules/` tree into this checkout.

## Defers-to

- [[06-qa-operating-model]] · [[13-domain-rigor-stack]] · [[a11y-visual]] · [[uid-color-for-ui]]
- MCP depth: `npx -y designparser-mcp` (upstream). We do not fork it.

## Related
- foundation → [[design-foundations]]
