### 2026-09-15 — Close the scoped-commit gap, verify the Open Engine, retire Windows

SessionID: 2026-09-15-work-mbp-fixes-and-engine-verify
--- SESSION BLOCK ---
Date: 2026-09-15
Machine: Work MacBook Pro (main, going forward)
Surface: Claude Code (Mac desktop app)
Agent: Claude Opus 5
Project(s): 19-workspace-brain

Summary: Cleared the outstanding items.

**Scoped-commit gap closed (the fix, not just the note).** `handle_stop` now snapshots
`git status --porcelain` once per turn and appends newly-dirty paths to the session touch
file, so Bash-written files are attributed too — previously only Edit/Write tool paths were
recorded (8 of 67 this session), which is what dropped session-end into the blanket
`git add -A` that swept a concurrent session's work. And `_stage_session_scope` now subtracts
`_other_session_claims()` — the union of every other live session's touch file — so a path
another session has declared is never staged here even if it went dirty on our watch. Three
tests added; 52/52 pass. Snapshot files are gitignored. The residual race is stated in the
entry rather than hidden, and the manual-commit caveat still stands.

**Open Engine verified — the test that had never run.** Label-filtered `list_issues` on the
personal lane: 30 issues, and all 23 anchor→issue mappings in `open-engine/personal.md`
resolve. **Zero orphaned pointers.** The other 7 are engine infra (SEA-5/6/7/8) plus three
created after the migration.

**The migration was already done; the baton was stale.** It happened 2026-07-30, substance
graduated to `project-context-detail.md` 2026-08-07, and `project-context.md` is now 93 lines
/ 12.4 KB costing 560 tokens at session start (head-30) — not the ~61 KB the stale entry
implied. The five unmigrated items are deliberate refusals (three `c8` with no valid pointer,
two lane-ambiguous), not backlog. Corrected in SESSION-STATE.

**Rec 13 closed.** Its Work-MBP half was already installed — verified `~/.cursor/hooks.json`
carries `beforeSubmitPrompt` → `cursor-prompt-route.sh`. Its Windows half is dropped: Sean is
selling the desktop. Windows retired across `fact-machine-layer-installs`, the CLAUDE.md
machine-label map (auto-loaded, so one line lighter), and the two queue items it scoped —
`^pc-03` (machine-layer installs: no Windows install route needed, and none should be built)
and `^pc-39` (author email: Personal MBP only).

**Bootstrap MISSes acknowledged.** All three dated 2026-07-29, two in an employer repo, one in
a bare `~/Projects` — seven weeks of a notice firing every session start, which is the
detector-everyone-ignores failure mode. `workspace-doctor --ack`; notices down to one.

**Reported, not actioned — deliberately.** `^pc-04`/SEA-11 is fully done in the vault but sits
in `Agent Review` on the board. Review→Done is the supervisor's transition, and this session
has spent its length insisting a machine should not claim done on judgment. `^pc-13`/SEA-15
correctly stays open: its Perplexity-Space half is genuinely unfinished.

22 harness gates green, 52/52 negative fixtures, ruff clean.
--- END BLOCK ---
