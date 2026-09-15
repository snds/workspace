### 2026-09-15 — Workspace harness: reachability + traversal cost become detectors

SessionID: 2026-09-15-work-mbp-harness
--- SESSION BLOCK ---
Date: 2026-09-15
Machine: Work MacBook Pro (main, going forward)
Surface: Claude Code (Mac desktop app)
Agent: Claude Opus 5
Project(s): 19-workspace-brain

Summary: Adversarial second pass over the 2026-09-11 first-wave automation, run against the
live tree rather than the report. Found `main` CI-red in two places, both introduced by the
pass that added the gates: an unindexed knowledge entry (`plain-language.md`) and a
clock-dependent fixture in `test-validators.py` that was green only on its authoring day.
Found four Layer-0 routes naming a file that does not exist, a `status: canonical` doc
(`model-routing.md`) with zero inbound edges and zero routes, ten knowledge entries indexed
but matchable by nothing, one skill (`github-guardrails`) reachable by nothing, a
`vault-health.py` link resolver that could not resolve any note→skill edge (keyed on stem;
every skill is `SKILL.md`), and `vault-health.py` itself wired into no gate. Sixteen defects,
all fixed.

Built `09-tools/workspace-harness.py` — stdlib-only, read-only, clock-free. Three lanes:
quality (runs the enforcement chain, reimplements nothing), connections (seven graph checks
nothing else performs — Layer-0 target resolution, skill reachability, hub-chain ascent,
registry paths, knowledge routability, `_INDEX` link resolution the way `prompt_route.py`
resolves it, named-detector existence), tokens (contract floor 10,305 · session floor 21,656 ·
load set p50/p95/max 7,877/12,261/20,057 · worst-case legal request 62,069 · banned ingest
87,154 = 1.4× the legal worst case). `--self-test` proves each check can fail.

Two modelling corrections the vault forced: reachability is three grades, not two (141
hub-prose spokes are reported, never failed — failing them every run would kill the detector);
the chain invariant is subsequence, not prefix and not the tier enum (sub-spokes are legitimate
topology). Attach points so it is not another unused script: CI (`--self-test` then
`--connections --tokens`, plus `vault-health.py`), the AGENTS.md enforcement chain,
`close-out-dispatch.py` under a new `self-improve` row (`rigor_role: command-hub`), and seven
Layer-0 routes.

All three lanes green; routing corpus still 48/48; vault-health 0/0.

Not covered, deliberately: phase 5 (per-surface routing trajectories — the harness proves the
graph is traversable, not that a given model traverses it) and phase 6 (A4/A5/A8/A9 remain
open). Nothing here touches the visual/Figma lane.

Report: `07-projects/19-workspace-brain/reports/workspace-harness_v1.0_2026-09-15.md`
Decision: `[[decision-reachability-is-a-detector]]`
--- END BLOCK ---
