### 2026-09-15 — Surface trajectories: three Layer-0 matchers collapsed to one

SessionID: 2026-09-15-work-mbp-trajectories
--- SESSION BLOCK ---
Date: 2026-09-15
Machine: Work MacBook Pro (main, going forward)
Surface: Claude Code (Mac desktop app)
Agent: Claude Opus 5
Project(s): 19-workspace-brain

Summary: Phase 5 of the review prompt. Found three independent Layer-0 implementations —
`prompt_route.py` (Cursor), a fork inside `dispatcher.py` (Claude Code), and a copy inside
`evaluate-skill-routing.py` (the 48 fixtures). The fixtures tested the copy, so neither live
surface was under test by anything. Ran the same 48 utterances through both real entry
points: 6 divergences (12.5%). Cursor had no Layer-1 lexical fallback (contract-documented,
so non-compliance rather than difference); the Claude fork deduped knowledge hints by trigger
instead of by target and silently dropped them. Both wrong, opposite directions. That is the
"Cursor didn't find the skill" complaint, reproduced.

Collapsed to one matcher instead of patching two into agreement: ported Layer 1 into
prompt_route, made handle_user_prompt delegate, made evaluate-skill-routing import
term_matches. Re-measured: 0 divergences.

Built `09-tools/evaluate-surface-trajectories.py` — executes each surface's real entry point
(claude-code hook, cursor hook, shell-agent via skill-loadset, hookless adapters asserted
statically), asserts expect/forbid paths, headers, silence, and hook-surface PARITY, plus a
structural one-matcher guard so re-forking fails CI for every utterance, not only corpus
ones. `--self-test` plants a divergence and asserts parity fails on it. 14 cases.

Unification immediately surfaced its own cost: a bare status-note payload began appearing on
non-work utterances on both surfaces at once. Fixed with a general rule (a payload of nothing
but parenthetical notes is noise) which preserves the visible miss for work verbs; two
fixtures now hold it.

Wired: CI, the workspace-harness quality lane (17 gates), AGENTS.md enforcement chain, the
self-improve close-out row, five Layer-0 routes. All three harness lanes green; 48/48 matcher
cases; 14/14 trajectories; vault-health 0/0.

Not proven, deliberately: that a model *reads* what it receives. Injection is not compliance;
that needs real-session outcome data, not fixtures.

Report: `07-projects/19-workspace-brain/reports/surface-trajectories_v1.0_2026-09-15.md`
Decision: `[[decision-one-matcher-per-workspace]]`
--- END BLOCK ---
