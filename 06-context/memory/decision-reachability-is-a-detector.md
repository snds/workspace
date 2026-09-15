---
type: decision
description: The validators prove files are well-formed; workspace-harness.py proves an agent can REACH them and prices the traversal — reachability and token cost are detectors now, not review topics.
created: 2026-09-15
confidence: high
relations:
  builds-on: ["[[decision-workspace-automation-first-wave]]", "[[decision-self-improving-workspace]]"]
  relates-to: ["[[agentic-error-correction-foundations]]", "[[process-rigor-gaps]]", "[[self-improve]]"]
---

## For future agent
- **TL;DR:** Well-formed and unreachable is the shape of "the agent didn't find the skill."
  `python3 09-tools/workspace-harness.py` — three lanes: quality (runs the chain), connections
  (can anything reach this), tokens (what reaching it costs). `--self-test` first. `BUDGETS` is
  raised only by a deliberate diff. Wired into CI, the AGENTS enforcement chain, and
  `close-out-dispatch.py` under `self-improve`.
- **As of:** 2026-09 · **Status:** current

## Context — what forced a choice
An adversarial pass over the first-wave automation found `main` CI-red in two places, both
introduced by the pass that added the gates. Four Layer-0 routes named a file that does not
exist; a `status: canonical` doc had zero inbound edges and zero routes; ten knowledge entries
were indexed but matchable by nothing; one skill was reachable by nothing at all. Every one of
those files passed every validator, because no validator asks whether anything can reach a file.

## Decision — what we chose
Reachability and traversal cost become machine checks, in one harness that **runs** the existing
validators rather than reimplementing them. Three grades of reachability, not two: `hub-prose`
(no machine route but the hub's SKILL.md names it) is counted and reported, never failed —
failing 141 spokes every run teaches everyone to ignore the report. The chain invariant is the
parent's order surviving as a **subsequence** of the child's, not a prefix and not the tier enum,
because sub-spokes are legitimate topology here.

## Rationale — why, and what we rejected
Rejected: a stricter tier rule (would flag correct structure); failing hub-prose spokes (noise
that kills the detector); running the quality lane in CI (those jobs already exist); an absolute
token truth (`bytes/4` is an estimate, so gate on relative regression and say so). The estimator
reproduces the ~21.6k session floor recorded earlier by a different method — the only evidence
we have that it is not inventing numbers.

## Consequences — what this commits us to
A new skill with no triggers and no chain now fails CI. A knowledge entry with no hint, no
`_INDEX` `Triggers:`, and no `trigger_words` fails CI. Growth in the always-loaded files fails
CI when it crosses a budget. `self-improve` carries `rigor_role: command-hub`, so it must keep
naming a detector. Test fixtures never hardcode a date: the clock-bomb test that broke this
month is the reason the harness has no clock in it.
