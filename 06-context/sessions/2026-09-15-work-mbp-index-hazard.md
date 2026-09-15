### 2026-09-15 — Record the shared-git-index hazard (and a coverage gap it exposed)

SessionID: 2026-09-15-work-mbp-index-hazard
--- SESSION BLOCK ---
Date: 2026-09-15
Machine: Work MacBook Pro (main, going forward)
Surface: Claude Code (Mac desktop app)
Agent: Claude Opus 5
Project(s): 19-workspace-brain

Summary: Tree settled (Cursor's @shadcn/lint work landed, 22 harness gates green, no
divergence), so the hazard deferred earlier is now recorded. Extended
[[multi-session-workspace-resilience]] rather than minting a new entry — it already owns
git/concurrency and had a Key diagnostic lessons section.

The hazard: two agents in one working tree share `.git/index`, so `git add <mine>` followed
by `git commit` commits whatever the other agent staged in between — the commit takes the
whole index, not your paths. Hit for real this session: a commit swept in two files
belonging to the concurrent Cursor session under a message asserting it held only my work.
Recovery is `git reset --soft HEAD~1` → `git restore --staged <theirs>` → re-commit. The fix
is a pathspec-limited commit, `git commit -- <paths>`, which ignores index state.

Worth separating: the fragment model prevents merge conflicts between disjoint FILES; it does
nothing about a shared INDEX. Different layers, and only the first had been solved.

Measured a coverage gap in the documented mitigation while writing it up. Point 3 of that
entry says a PostToolUse hook records edited paths so session-end stages only those. True,
but it records only `Edit|Write|MultiEdit|NotebookEdit` — anything written through Bash
(heredoc, sed, `python3 -`) is invisible. This session's touch file held 8 paths against 67
the commits actually changed, because auto-mode routes most writes through Bash. And it runs
at session-end only, so a manual mid-session commit bypasses it entirely. Both limits are now
stated in the entry instead of being implied protection.

Also added: Layer 1 cannot see what you just wrote. `vault-retrieve.py`'s FTS index rebuilds
at SessionStart and in `nightly.py`, so a mid-session entry is invisible to the lexical
fallback until `--rebuild`. Found by checking my own work — the natural phrasing "why did git
commit take files I did not add" produced a visible Layer-0 miss with two wrong lexical hits;
after rebuild the new entry is the #1 hit. Verified all three phrasings now reach it: two via
Layer 0 triggers, one via Layer 1.

Committed with `git commit -- <paths>`, which is the practice the entry now prescribes.

22 harness gates green, vault-health 0/0 across 170 notes, ruff clean.
--- END BLOCK ---
