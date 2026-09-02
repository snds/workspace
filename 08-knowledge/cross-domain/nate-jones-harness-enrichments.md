---
tags: [harness, agents, nate-jones, enrichment, open-engine, token-frugality]
created: 2026-08-07
updated: 2026-08-07
status: working
confidence: high
sources:
  - 07-projects/19-workspace-brain/reports/substack-enrichment-brief_v1.0_2026-08-07.md
  - natesnewsletter.substack.com (authenticated scan 2026-08-07)
related_skills: [harness-map, mission-fit, open-agent-engine, workspace-bootstrap]
related_projects: [19-workspace-brain]
relations:
  relates-to:
    - "[[agentic-ds-context-model]]"
---

# Nate Jones harness enrichments — absorbed into this workspace

## For future agent

Pointer synthesis from Nate B. Jones posts/guides that **enrich** (not replace)
[[harness-map]], [[mission-fit]], and [[open-agent-engine]]. Apply these as operating
habits; do not re-implement his product zips or dump paywalled bodies here.

## Already absorbed elsewhere

| Nate piece | Where it lives |
|---|---|
| AI Harness Audit / Cleaner | [[harness-map]] |
| False success / Mission Fit | [[mission-fit]] |
| Open Engine / handoffs + receipts | [[open-agent-engine]] + `06-context/open-engine/` |

## Applied enrichments

### 1. Skill one-job test (imported-skill trust)

Before keeping a shared/imported skill: does it encode **Sean's** judgment for **one**
clear job, or someone else's generic process? Disposition: **keep / rewrite / remove**.
Wired into `/optimize` duplication checks and [[harness-map]] dispositions.

Sources: [agent-skill-one-job-test](https://natesnewsletter.substack.com/p/agent-skill-one-job-test) ·
[Make Any Skill Your Own](https://unlock-ai.natebjones.com/guides/make-any-skill-your-own)

### 2. Agent ownership card

Every recurring agent job names: **owner** (human), **runtime**, **what it may touch**,
**who supervises done**, **kill/pause condition**. Prefer Live handoff + lane config
fields over a new skill. See [[open-agent-engine]] ownership stamp.

Source: [ai-agent-ownership](https://natesnewsletter.substack.com/p/ai-agent-ownership)

### 3. Judge layer / what may leave the building

A polished answer is not permission to publish, send, push, or spend. Pair
[[mission-fit]] Evidence with framework #06 Honesty + Proofboard — the **judge** is
human or an evidence-bearing check, never the producing agent alone.

Source: [agent-judge-layer-production-control](https://natesnewsletter.substack.com/p/agent-judge-layer-production-control)

### 4. Control layer (ship checklist beyond the model)

Before widening autonomy: tools, data reach, permissions, quality bar, proof path,
supervision, stop conditions. Fits [[harness-map]] / [[mission-fit]] preflight — not
always-on ritual prose.

Source: [agent-infrastructure-control-layer](https://natesnewsletter.substack.com/p/agent-infrastructure-control-layer)

### 5. Agent maintenance loop (seven surfaces)

On `/optimize` and periodic harness-map: **job · diet · memory · tools · reach ·
proof · value**. Retire work that no longer earns its keep.

Sources: [ai-agent-maintenance](https://natesnewsletter.substack.com/p/ai-agent-maintenance) ·
[Maintenance Loop guide](https://unlock-ai.natebjones.com/guides/agents/maintenance)

### 6. Token diet / preload cost

Token frugality remains #1. Prefer selective `load_chains` over preloading catalogs;
session-start stays orientation (~150 tokens ritual + heads), not specialist manuals.
See [[workspace-bootstrap]] token diet note.

Sources: [reduce-ai-token-usage](https://natesnewsletter.substack.com/p/reduce-ai-token-usage) ·
[cut-token-waste](https://unlock-ai.natebjones.com/guides/cut-token-waste) ·
[preload cost](https://natesnewsletter.substack.com/p/your-claude-sessions-cost-10x-what)

### 7. Bakeoff / eval discipline

Cheaper or new models earn place via **validator + manifest + fixtures**, not vibes.
Proofboard-adjacent; store eval artifacts under `09-tools` / `05-artifacts` when run —
never always-on context.

Sources: [chinese-ai-models-test](https://natesnewsletter.substack.com/p/chinese-ai-models-test) ·
[bakeoff guide](https://unlock-ai.natebjones.com/guides/chinese-model-bakeoff)

### 8. One-minute test (shape the work)

Before spinning agents: **chat vs one agent vs team vs nothing**. Default smallest
shape that can produce evidence. See [[open-agent-engine]] routing.

Sources: [agent-shaped-work](https://natesnewsletter.substack.com/p/agent-shaped-work) ·
[One-Minute Test](https://unlock-ai.natebjones.com/guides/the-one-minute-test)

### 9. Open Stack vs this workspace

Nate's Open Skills / Brain / Engine map bottlenecks. This workspace already has
**Skills + Engine**; durable state is **files + git**, not a second "Open Brain"
store (Supabase-style). Do not adopt a parallel substance layer.

Source: [Open Stack field guide](https://unlock-ai.natebjones.com/guides/open-stack/open-stack-field-guide)

### 10. Slop cost / human read-with-care

Skills and validators cannot replace a human reading consequential output carefully.
Reinforce #06 + [[mission-fit]] Evidence — one bullet, not a new skill.

Source: [ai-slop-cost](https://natesnewsletter.substack.com/p/ai-slop-cost)

### 11. Surface posture: steer vs dispatch

Different surfaces favor different harness postures (e.g. steer-heavy vs
dispatch-heavy). Same model + different harness can dominate outcomes. Adapters
(`CURSOR.md` / `CLAUDE.md`) document posture; [[harness-map]] maps per surface.

Sources: [claude-code-vs-codex-agents](https://natesnewsletter.substack.com/p/claude-code-vs-codex-agents) ·
[same-model harness](https://natesnewsletter.substack.com/p/same-model-78-vs-42-the-harness-made)

### 12. Issue trackers as agent infrastructure

Trackers work as agent infra when they support claim locks, statuses, receipts, and
pointer-shaped bodies. Validates the Linear-lane Open Engine bet — see lane README.

Source: [issue-trackers-agent-infrastructure](https://natesnewsletter.substack.com/p/issue-trackers-agent-infrastructure)

## Anti-patterns

- Re-building Cleaner / Mission Fit / Open Engine from Nate's zips when ours already land them
- Always-loading maintenance / bakeoff / Open Stack prose into session-start
- Treating LLM-as-judge without world-state evidence as supervision
