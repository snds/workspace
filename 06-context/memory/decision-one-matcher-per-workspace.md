---
type: decision
description: Layer-0 matching has exactly one implementation (09-tools/prompt_route.py); every surface delegates, and evaluate-surface-trajectories.py runs each surface's real entry point to prove they deliver the same context.
created: 2026-09-15
confidence: high
relations:
  builds-on: ["[[decision-reachability-is-a-detector]]", "[[decision-tool-native-adapters]]"]
  relates-to: ["[[agentic-error-correction-foundations]]", "[[agent-load-miss-review]]", "[[cursor-employer-repo-skill-routing]]", "[[self-improve]]"]
---

## For future agent
- **TL;DR:** One matcher: `09-tools/prompt_route.py`. The Claude hook delegates; never fork
  the tier machinery back into `dispatcher.py`. `python3 09-tools/evaluate-surface-trajectories.py --check`
  runs each surface's REAL entry point and fails on divergence. `--utterance "…"` shows what
  each surface delivers. Adding a surface = a `deliver_*` function plus cases.
- **As of:** 2026-09 · **Status:** current

## Context — what forced a choice
"Cursor didn't find the skill" was assumed to be model quality. It was measurable: three
independent Layer-0 implementations existed (prompt_route for Cursor, a fork inside
dispatcher.py for Claude Code, a copy inside evaluate-skill-routing.py for the fixtures).
The fixtures tested the copy, so neither live surface was under test. Six of 48 utterances
delivered a different file set per surface — Cursor had no Layer-1 lexical fallback, and the
Claude fork deduped a knowledge hint away whenever the same trigger had already produced a
curated hit. Both wrong, opposite directions, invisible because nothing ran both.

## Decision — what we chose
Collapse to one matcher rather than patch two into agreement. Port Layer 1 into
`prompt_route`; make `handle_user_prompt` delegate; import `term_matches` in the evaluator
instead of copying it. Then test **delivery**, not matching: a trajectory suite that executes
each surface's own entry point, asserts per-surface expectations, asserts hook-surface
parity, and carries a structural guard that the Claude hook has not re-forked the matcher.
Hookless surfaces have no executable path, so their adapter files are asserted statically.

## Rationale — why, and what we rejected
Rejected: patching each matcher separately (re-creates drift on a slower clock); declaring
today's divergences "intentional surface differences" (they were defects — one surface
violated the documented contract); mirroring all 48 matcher cases as trajectories (pays the
subprocess cost for no new information — the matcher corpus is the breadth, trajectories are
the delivery proof).

## Consequences — what this commits us to
A new surface needs a `deliver_*` function and cases, or it is untested. Re-forking the
matcher into a hook fails CI structurally, not just on corpus utterances. Behaviour changes
now land on every surface at once — during this change a bare status-note payload started
appearing on non-work utterances on both surfaces simultaneously; that is the trade for
unification, and it is why two silence fixtures exist. Still unproven, deliberately: that a
model *reads* what it receives. Injection is not compliance.
