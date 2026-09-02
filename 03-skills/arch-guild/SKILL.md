---
name: arch-guild
description: >-
  Multi-voice engineering review router. Use for architecture reviews, correctness
  debates, distributed-systems risk, performance-at-scale, antifragility, and
  security threat lenses on engineering designs. Wraps the claude-1337 arch-guild
  specialist agents (dijkstra, knuth, lamport, taleb, vector, etc.). Workspace owns
  triggers and doctrine; plugin owns agent depth.
aliases: [arch-guild]
triggers: [arch guild, architecture review, multi-voice review, dijkstra, lamport, knuth, engineering guild]
tier: hub
domain: engineering
prerequisites: [eng-foundations]
related: [eng, lead-backend-engineer, lead-frontend-engineer, lead-devops-engineer, lead-security-architect]
defers_to: [framework-14, framework-13, framework-16, eng-foundations]
rigor_role: multi-voice
surfaces: ["*"]
spec_version: "2.2"
---

# Arch Guild — Multi-voice Engineering Review

**Wrapper (L5).** Depth: Cursor plugin `claude-1337/arch-guild` (named specialist agents +
evals). This skill owns *when* to invoke and which workspace doctrines bind the outcome.

## When to use

- Structural eng review (`/eng review`)
- Competing constraints (consistency vs latency, security vs throughput)
- Pre-merge of high-blast-radius changes

## Protocol

1. Load [[14-engineering-operating-model]] (+ #16 if trust boundaries).
2. State the decision question and constraints in one paragraph.
3. Invoke the relevant guild voices from the plugin (do not reimplement their prompts here).
4. Synthesize with Lotfi-style trade-off scoring when voices conflict; Ixian-style success metrics after.
5. Record decision in ADR / PR; workspace frameworks win on conflict with plugin advice.

## Defers-to

- [[13-domain-rigor-stack]] · [[14-engineering-operating-model]] · [[16-security-operating-model]]
- Plugin agents are advisory depth, not policy

## Related
- foundation → [[eng-foundations]]
- peer ↔ [[lead-backend-engineer]] · [[lead-frontend-engineer]] · [[lead-security-architect]]
