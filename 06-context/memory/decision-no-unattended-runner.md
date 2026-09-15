---
type: decision
description: We are not building the unattended Open Engine runner. The safety gate stays, because it guards paths that still exist (/schedule, CronCreate, headless runs) whether or not a runner is ever built.
created: 2026-09-15
confidence: high
relations:
  builds-on: ["[[decision-intent-coordination-standard]]"]
  relates-to: ["[[agent-work-queue-boundaries]]", "[[open-agent-engine]]"]
---

## For future agent
- **TL;DR:** No unattended runner. Do not build one, do not add a timer, do not treat this as
  an open task. `09-tools/check-unattended-runner-gate.py` **stays** — it is a lock, not a
  feature, and it is silent unless something claims an unattended run.
- **As of:** 2026-09 · **Status:** current

## Context — what forced a choice
The runner sat as "authorized-but-unbuilt" on the baton for weeks, which made it read like
pending work every time Sean opened the file. Asked 2026-09-15 whether the whole thing should
be deleted as an orphaned artifact. Checked first: no timer, no cron, no launchd entry, no
queue item, and nothing reporting it stale — 0 notices, vault-health clean. The only artifact
is the gate.

## Decision — what we chose
Close the question instead of deleting the guard. Sean starts a session and asks when he wants
queue work done; that already works, so the runner buys nothing. The gate stays because the
risk it blocks does not depend on the runner existing: `/schedule`, the `CronCreate` tool, and
any headless `claude -p` run can all reach an unattended path by accident. Deleting a lock
because the door is unused is backwards.

## Rationale — why, and what we rejected
Rejected: deleting the gate with the idea (it removes enforcement and leaves the doctrine as
prose, which is what the gate was minted to replace). Rejected: leaving the baton line as-is
(it was the actual irritant — an open-looking to-do for something nobody intends to do). The
gate costs nothing at rest: it lives in `09-tools/`, which is not auto-loaded, so it adds zero
tokens per session and stays silent when idle.

## Consequences — what this commits us to
If the answer ever changes, the safe first version is small: one lane only, tools **removed**
rather than granted (`--tools` / `--disallowed-tools`, since allow-lists only add), and only
tickets Sean wrote himself — issue bodies are untrusted input by the engine's own rule.
Until then this is decided, not deferred.
