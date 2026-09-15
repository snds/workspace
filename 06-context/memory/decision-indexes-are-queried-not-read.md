---
type: decision
description: Any index in this workspace is queried through a CLI, never ingested — skills.registry.json, 08-knowledge/_INDEX.md and now 06-context/artifact-registry.md; the token budget is lowered each time so a revert fails CI.
created: 2026-09-15
confidence: high
relations:
  builds-on: ["[[decision-reachability-is-a-detector]]", "[[decision-lint-narrow-or-not-at-all]]"]
  relates-to: ["[[knowledge-vault-design]]", "[[agent-load-miss-review]]", "[[self-improve]]"]
---

## For future agent
- **TL;DR:** Three indexes, three CLIs, one rule. `skills.registry.json` → `skill-loadset.py`.
  `08-knowledge/_INDEX.md` → knowledge-hints + `prompt_route.py` parsing it server-side.
  `06-context/artifact-registry.md` → `python3 09-tools/artifact-find.py "<terms>"` (`--list`,
  `--path`, `--check`). If you add a fourth index, it needs a CLI before it needs a read-order line.
- **As of:** 2026-09 · **Status:** current

## Context — what forced a choice
The harness priced the session floor and `artifact-registry.md` was 6,942 tokens of it — the
largest recurring item after AGENTS.md itself, larger than the adapter, role, preferences,
project-context head and session-log head combined. CLAUDE.md read-order item 4 told every agent
to read it. The same mistake had already been fixed twice elsewhere and simply left standing here,
which is the general pattern: an index grows quietly and nobody re-reads the read order.

## Decision — what we chose
Move the index behind a retrieval CLI and change the contract to say query, never ingest. Then
**lower the budget by the saving** (session_floor 25,000 → 17,000) so reverting costs 21,720 and
fails CI, add a self-test asserting the ceiling sits in that gap, and keep an
`avoided_by_retrieval` line in the report so the number stays visible instead of vanishing from
the accounting. Ship the format check in the same tool: a retrieval layer whose source drifts
starts missing silently, which is worse than the whole-file read it replaced.

## Rationale — why, and what we rejected
Rejected: shrinking the registry (it is the source of truth, and `/optimize` legitimately reads it
whole — that one caller is annotated as correct); leaving the budget where it was (a saving that
can be silently undone gets paid for twice); a query tool without `--check` (invisible failure);
applying the same trick to `AGENTS.md` or `user-preferences.md` — those are always-on content, not
indexes, and pretending otherwise just moves cost somewhere unmeasured.

## Consequences — what this commits us to
Session-end still WRITES the registry and must keep the `- **Purpose**:` / `- **Last modified**:`
shape; `artifact-find.py --check` runs there and in CI. A new index without a CLI is a regression.
What none of this buys: obedience. The budget catches a reverted contract, not a model that
ingests the file anyway — injection is not compliance.
