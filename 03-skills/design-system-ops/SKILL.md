---
name: design-system-ops
description: >-
  Design system operations command hub — token audits, drift detection, governance,
  deprecation, system health, stakeholder briefs. Use when running a design system
  (not merely consuming one): "audit tokens", "drift check", "DS governance",
  "deprecation plan", "system health", "theme audit", "docs coverage". Wraps the
  vendored skills/commands in this directory. Not for component authoring
  (design-engineer) or DS strategy (ds-advisor).
aliases: [design-system-ops]
triggers: [design system ops, token audit, audit my tokens, drift detection, ds governance, system health, deprecation plan, theme audit, docs coverage]
tier: hub
domain: design
prerequisites: [design-foundations]
related: [ds-advisor, design-engineer, ux-component-library, figma, qa]
defers_to: [framework-09, framework-13, ds-advisor, design-engineer]
rigor_role: command-hub
surfaces: ["*"]
spec_version: "2.3"
---

# Design System Ops — Operations Hub

**Wrapper (L2)** over the vendored pack in this directory (`skills/`, `commands/`,
`knowledge-notes/`). Owns triggers and doctrine. Nested skills hold procedure depth.
Pack landing page: [[03-skills/design-system-ops/README|design-system-ops README]].

## Owns vs defers

| This hub | Defer to |
|---|---|
| Token/drift/governance/ops workflows | — |
| DS strategy / which system to build | [[ds-advisor]] |
| Component authoring / implementation | [[design-engineer]] |
| Component schema / DESIGN.md | framework #09 |
| Pixel QA of UI | `/qa` + [[visual-qa-toolkit]] |

## Operation grammar

```
/ds-ops <verb> [target]
```

| Verb / command | Nested entry |
|---|---|
| `token-audit` | `commands/token-audit.md` → `skills/token-audit` |
| `theme-audit` | `commands/theme-audit.md` → `skills/theme-audit` |
| `docs-coverage` | `commands/docs-coverage.md` → `skills/docs-coverage` |
| `drift-check` | `commands/drift-check.md` |
| `system-health` | `commands/system-health.md` |
| `governance-review` | `commands/governance-review.md` |
| `component-audit` | `commands/component-audit.md` |
| `full-diagnostic` | `commands/full-diagnostic.md` (five-skill core; add theme/docs when those surfaces exist) |

Prefer the command file's instructions; do not paste entire nested skills into context unless needed.

## Knowledge note

Vendored `knowledge-notes/` are pack-local. Durable workspace insight belongs in
`08-knowledge/design/` (see [[ds-ops-governance-notes]] when present). Do not treat
vendored notes as overriding #09.

## Defers-to

- [[09-component-and-pattern-framework]] · [[13-domain-rigor-stack]] · [[ds-advisor]] · [[design-engineer]]

## Related
- foundation → [[design-foundations]]
- peer ↔ [[ds-advisor]] · [[design-engineer]] · [[qa]] · [[figma]]
