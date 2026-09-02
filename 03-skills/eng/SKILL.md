---
name: eng
description: >-
  Engineering delivery command hub for FE/BE/DevOps/mobile. Use when shaping
  contracts, implementing behind boundaries, reviewing architecture, hardening
  security/perf, or shipping with rollback. Trigger on "/eng", "shape the API",
  "ship this service", "review this architecture", "harden auth", "rollback plan",
  "engineering done-gate". Wrapper over lead-*-engineer hubs and arch-guild.
  Not for pure design craft (/qa, design-engineer) or photoreal (#12).
user-invocable: true
argument-hint: "[shape|implement|review|harden|ship] [target] [--surface fe|be|devops|mobile] [--dry]"
aliases: [eng]
triggers: [eng, engineering delivery, shape contract, ship service, harden auth, rollback plan, architecture review]
tier: hub
domain: engineering
prerequisites: [eng-foundations]
related: [lead-frontend-engineer, lead-backend-engineer, lead-devops-engineer, lead-mobile-engineer, lead-security-architect, arch-guild]
defers_to: [framework-14, framework-16, framework-13, eng-foundations]
rigor_role: command-hub
surfaces: ["*"]
spec_version: "2.2"
---

# /eng — Engineering Delivery Hub

Thin **wrapper** (Domain Rigor L2). Owns verb grammar, done-gate reminders, and routing.
Depth lives in lead hubs and spokes. Doctrine: [[14-engineering-operating-model]],
[[16-security-operating-model]], [[13-domain-rigor-stack]].

## Operation grammar

```
/eng <verb> <target> [--surface fe|be|devops|mobile] [--dry]
```

| Verb | Meaning | Default route |
|---|---|---|
| `shape` | Name the contract before code | matching lead + ADR habit |
| `implement` | Build behind the contract | `fe-*` / `be-*` / `devops-*` / `mobile-*` |
| `review` | Multi-voice correctness/architecture review | `arch-guild` + relevant lead |
| `harden` | Security, perf, a11y, resilience | `lead-security-architect`, `fe-perf-harness`, `a11y-audit-toolkit` |
| `ship` | Release with rollback + signals | `lead-devops-engineer` + #14 ship gate |

Omitted verb → infer from language; ask once if ambiguous. `--dry` reports plan only.

## Absolute bans

- Ship new trust boundaries without #16 threat-model delta
- Skip rollback/expand-contract on migrations
- Call something an "audit" without measurement
- Let pstack/superpowers override #06 / #11 / #13 / #14

## Defers-to

- Workspace frameworks #13, #14, #16 win over plugin engineering advice
- Plugin `arch-guild` / pstack supply technique voices only via [[arch-guild]] wrapper

## Related
- foundation → [[eng-foundations]]
- peer ↔ [[qa]] · [[lead-security-architect]]
