### 2026-09-15 — Unattended runner: decided not to build it; guard stays

SessionID: 2026-09-15-work-mbp-runner-decision
--- SESSION BLOCK ---
Date: 2026-09-15
Machine: Work MacBook Pro (main, going forward)
Surface: Claude Code (Mac desktop app)
Agent: Claude Opus 5
Project(s): 19-workspace-brain

Summary: Sean asked whether to delete the unattended runner and its tasks as an orphaned
artifact that reports stale. Checked before answering: nothing reports it stale (0 notices,
vault-health clean across 170 notes), there is no timer, no cron entry, no launchd agent, and
no queue item. The only artifact is `09-tools/check-unattended-runner-gate.py`.

Recommendation given and taken: keep the gate, close the question. The gate is a lock, not a
feature — it refuses unsafe unattended runs and is silent otherwise. The risk it blocks does
not depend on a runner existing, because `/schedule`, the `CronCreate` tool and any headless
`claude -p` run can reach an unattended path by accident. Deleting a lock because the door is
unused is backwards. It also costs nothing at rest: `09-tools/` is not auto-loaded, so zero
tokens per session.

The actual irritant was one baton line reading "authorized-but-unbuilt", which looks like a
pending task for something nobody intends to do. Replaced with a decided line pointing at
[[decision-no-unattended-runner]], which also records what a safe first version would look
like if the answer ever changes: one lane, tools removed rather than granted, and only
tickets Sean wrote himself.
--- END BLOCK ---
