---
title: Dated claims in research findings
tags: [research, dated claims, freshness, as of, stale]
triggers: [dated claims, freshness, stale claim, last checked]
created: 2026-10-22
updated: 2026-10-22
status: working
confidence: high
sources: [02-shared-references/epistemic-standards.md §2]
related_skills: [lead-research, research-computing, research-industry]
related_projects: [26-synapse]
---

# Dated claims in research findings

## For future agent
- **TL;DR:** The freshness rule is [[epistemic-standards]] §2 (timeless, dated, or pointer; `#stale`
  when past its horizon). This note is how research applies it: every source has a date, and every
  claim that can drift says *as of when*. Fast fields get short horizons.
- **As of:** 2026-10 · **Status:** current

## In a finding

- **Every source** carries its date (publication, version, or when it was last checked).
- **Every drifting claim** carries `as of YYYY-MM` (or a full date): prices, versions, features,
  laws, rankings, market share, people's roles, "the latest".
- **The finding** carries its own `as of` in the Depth line, so a reader knows when the whole
  picture was true.
- **Timeless claims** (a proof, a principle, a historical fact well established) need no date, but
  their source still has one.

## Horizons by field (when to re-check)

| Field | Re-check after |
|---|---|
| Software, AI tools, prices, features | 3–6 months |
| Standards in draft, regulations being changed | Each new version or status change |
| Markets, competitors | 6–12 months |
| Empirical science in active fields | 1–3 years, or on a major replication |
| Published standards in force | On the next edition |
| Mathematics (proved results), settled history | Rarely; check for corrections |

Past the horizon, tag `#stale` rather than silently trust; `/health` surfaces drift.

## Related
- [[19-research-operating-model]] · [[lead-research]] · [[citing-sources]] · [[epistemic-standards]]
