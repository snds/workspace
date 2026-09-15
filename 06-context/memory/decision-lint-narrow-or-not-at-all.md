---
type: decision
description: Automation-layer lints are deliberately narrow — ruff selects E9/F/I only, and the evidence-grade lint gates strict mode on two distinct experiment signals; a lint that is wrong by construction is worse than no lint.
created: 2026-09-15
confidence: high
relations:
  builds-on: ["[[decision-workspace-automation-first-wave]]", "[[decision-reachability-is-a-detector]]"]
  relates-to: ["[[experiment-validity-baseline]]", "[[process-rigor-gaps]]", "[[self-improve]]"]
---

## For future agent
- **TL;DR:** `ruff.toml` selects `E9`, `F`, `I` and nothing else — `BLE001`/`S110`/`S112`/`PLW1510`
  are excluded because fail-open and manual returncode checks are the contract here, not sloppiness.
  `validate-evidence-grades.py` requires a legend + a named detector on any report using the
  vocabulary 3+ times; `--strict` adds pre-registration but only on two distinct experiment signals.
  `nightly.py` is the recipe's executable form and schedules nothing.
- **As of:** 2026-09 · **Status:** current

## Context — what forced a choice
Default ruff over the tool layer returns 143 findings; `E,F` returns 402. The first cut of the
evidence-grade lint flagged `process-rigor-gaps` because the word "experiment" appears there as a
trigger word inside a routing table. Both are the same failure: a check that reports things which
are not defects trains everyone to route around it, and then it catches nothing at all.

## Decision — what we chose
Narrow every automation-layer lint to what means BROKEN or ROTTING, and measure the blast radius
before wiring anything into CI. Where a rule is right in principle but imprecise in practice, make
it opt-in (`--strict`) AND narrow its trigger, rather than shipping it loud. Where a count is
sometimes legitimate, use a declared ceiling instead of zero — cross-chain trigger collisions (25)
and hub-prose-only spokes (140) are reported against ceilings so growth is a reviewable diff.

## Rationale — why, and what we rejected
Rejected: ruff defaults (143 findings, most of them doctrine); `E501` (395 hits of style);
`RUF100` (misfires under a narrow select, flagging deliberate noqa comments); failing
cross-chain collisions at zero (some are correct); a `.sh` nightly wrapper (portable-first is a
core rule and the fleet includes Windows).

## Consequences — what this commits us to
CI now fails on undefined names, unused imports and import disorder in `09-tools/` and
`.claude/hooks/` — and on a report that stamps `VERIFIED` without a legend and a re-runnable
detector. Raising a ceiling or widening a ruleset is a deliberate diff, which is the point.
Cross-chain collisions sit AT the ceiling (25/25): the next one fails CI on purpose.
