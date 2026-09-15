### 2026-09-15 — C2: the artifact registry moves behind a CLI; session floor down 32%

SessionID: 2026-09-15-work-mbp-artifact-retrieval
--- SESSION BLOCK ---
Date: 2026-09-15
Machine: Work MacBook Pro (main, going forward)
Surface: Claude Code (Mac desktop app)
Agent: Claude Opus 5
Project(s): 19-workspace-brain

Summary: `06-context/artifact-registry.md` cost 6,942 tokens and CLAUDE.md read-order item 4
told every agent to read it — the largest recurring item in the session floor after AGENTS.md
itself. It is a structural index, and the same fix was already applied twice in this workspace
(skills.registry.json → skill-loadset.py; _INDEX.md → knowledge-hints + server-side parsing)
and simply left standing in a third place.

Built `09-tools/artifact-find.py`: terms search name/path/group/purpose with name hits
outranking prose, plus `--path`, `--list`, `--json`, `--limit`. Measured: reading the file is
6,942 tokens; `--list` (the whole map) is 575; a real query is 100. A no-match points at
vault-retrieve rather than returning empty, because a bare "no results" invites the agent to
conclude nothing exists.

`--check` is half the tool — a retrieval layer whose source drifts starts missing SILENTLY,
which is worse than the whole-file read it replaced. It verifies every entry is parseable,
has a Purpose to match on, a YYYY-MM-DD to age against, and a unique name. Live: 36/36
complete. It runs in CI and in /session-end step 4, right after the step that writes the file.

Contract changed in four places (CLAUDE.md item 4, AGENTS.md item 9, _CONTEXT.md, /optimize
step 7 — where a whole-file read stays correct and is annotated as the one legitimate caller).
Harness model updated only AFTER the contract, so the number followed the cost rather than
leading it.

Result: session floor 21,697 → 14,778 (−31.9%), worst-case legal request 62,110 → 55,191.
Locked three ways: session_floor budget lowered 25,000 → 17,000 so a revert (21,720) fails CI;
a self-test asserting the ceiling sits in that gap, verified non-vacuous by raising it to
99,000 and watching the test fail; and an `avoided_by_retrieval` line so the 6,942 stays
visible instead of vanishing from the accounting.

21 harness gates green, connections 8/8, every budget met, 48/48 matcher cases, 14/14
trajectories, vault-health 0/0, ruff clean.

Not done, and stated: this does not shrink AGENTS.md (7,691) or user-preferences.md (2,331) —
both are always-on content rather than indexes, so the same trick does not apply. And the
budget catches a reverted contract, not a model that ingests the file anyway.

Report: `07-projects/19-workspace-brain/reports/artifact-retrieval_v1.0_2026-09-15.md`
Decision: `[[decision-indexes-are-queried-not-read]]`
--- END BLOCK ---
