### 2026-09-15 — Automation second wave: A4, A5, A9 applied; A8 stays blocked

SessionID: 2026-09-15-work-mbp-automation-wave2
--- SESSION BLOCK ---
Date: 2026-09-15
Machine: Work MacBook Pro (main, going forward)
Surface: Claude Code (Mac desktop app)
Agent: Claude Opus 5
Project(s): 19-workspace-brain

Summary: Phase 6 — closed the remaining automation candidates from the 2026-09-11 review.

A5 (ruff): measured the blast radius before wiring anything. Defaults return 143 findings,
`E,F` returns 402 (395 of them line-length). Selected `E9`/`F`/`I` only — 7 errors, all
auto-fixed — and excluded BLE001/S110/S112/PLW1510 because fail-open and manual returncode
checks are the contract here, not sloppiness. Declared in `ruff.toml` so local and CI agree.
It caught its own author within the hour (two F541s in the new A9 lint).

A9 (`validate-evidence-grades.py`): any report using the evidence-grade vocabulary 3+ times
must declare the legend and name a re-runnable detector. One real violation
(`agent-load-miss-review.md`) fixed. `--strict` adds pre-registration fields but only on
two distinct experiment signals — the first cut fired on `process-rigor-gaps` because
"experiment" appears there as a trigger word in a routing table.

A4 (`nightly.py`): the recipe's executable form — fold → rebuild → verify → watch → commit
(opt-in, allowlisted paths, refuses on a red tree). Python not `.sh`, because portable-first
is a core rule and the fleet includes Windows. Nothing is scheduled.

A8 stays blocked and is stated as such: it needs a Figma produce that cannot refuse `Color/*`,
and manufacturing one would be theater.

Two new candidates from measurements the first review did not have. C1 (applied):
1,443 trigger terms, 92 claimed by >1 skill — 67 benign (same chain), 25 cross-chain, now a
harness check with a ceiling of 25 rather than fail-at-zero. C2 (queued, not built):
`06-context/artifact-registry.md` is 6,942 tokens, the largest recurring cost after AGENTS.md
itself, and it is a structural INDEX — the same shape already fixed for the skill registry and
_INDEX. A retrieval CLI plus a read-order change is real work; queued with the number attached
(~28% of the 21.7k session floor) rather than half-built at session end.

19 harness gates, all green. 48/48 matcher cases, 14/14 trajectories, vault-health 0/0, ruff clean.

Report: `07-projects/19-workspace-brain/reports/automation-second-wave_v1.0_2026-09-15.md`
Decision: `[[decision-lint-narrow-or-not-at-all]]`
--- END BLOCK ---
