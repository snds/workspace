---
tags: [cross-domain, engineering, git, concurrency, token-frugality, workspace-ops]
created: 2026-07-23
updated: 2026-09-15
status: stable
confidence: high
sources: [session-log 2026-07-23, session-log 2026-09-15, .claude/hooks/dispatcher.py, 09-tools/compact-sessions.py]
related_skills: []
related_projects: [18-bootstrap-generator, 19-workspace-brain]
triggers: [multi-session, concurrent session, cross-machine sync, session-log, git pull rebase, autostash, token frugality, session fragment, compaction, workspace resilience, shared index, git index, scoped commit, git add, concurrent agents, same working tree]
---

# Multi-session, token-frugal workspace resilience

A validated architecture for a git-backed knowledge workspace used concurrently across
machines, sessions, and surfaces (Claude Code, Cursor extension) — without collisions,
broken merges, lost context, or runaway token cost. Built + proven 2026-07-23; lives in
`.claude/hooks/dispatcher.py`, `09-tools/compact-sessions.py`, `.gitattributes`, and is
generalized into the bootstrap generator (`wsx`).

## The model (CRDT-lite operation log)

Turn shared-mutable-file contention into **conflict-free append-only ops + deterministic
compaction**. Writers never touch the same bytes; a pure function rebuilds the views.

1. **Per-session fragments.** Each session writes its block to its own file
   (`06-context/sessions/<id>.md`, with a `SessionID:` line). Disjoint files never merge-
   conflict. `compact-sessions.py` folds them into `session-log.md` newest-first, deduped
   by SessionID — idempotent (re-run converges), self-healing (any machine, any time).
2. **Union-merge the append-only logs.** `.gitattributes`: `session-log.md merge=union`
   → concurrent appends keep BOTH sides, never conflict. Backstop to the fragment model.
3. **Scoped commit.** A PostToolUse hook records this session's edited paths; session-end
   stages only those (+ reconciled log) — so a concurrent session's in-flight WIP is never
   swept into the wrong commit. Falls back to `git add -A` when untracked.
   **Two coverage limits, measured 2026-09-15 — do not assume this protects you.** It records
   only `Edit|Write|MultiEdit|NotebookEdit` paths, so anything written through **Bash**
   (heredoc, `sed`, a `python3 -` script) is invisible: in a Bash-heavy session the touch file
   held **8** paths against **67** the commits actually changed. And it runs at **session-end
   only** — a manual `git commit` mid-session bypasses it entirely.
4. **Safe push-retry.** On non-fast-forward: `git pull --rebase` (autostash pinned **OFF**
   → refuses over a dirty tree, never stashes/strands work), union auto-resolves logs, then
   retry. A structured-file conflict aborts + defers to `/reconcile`. Non-lossy, idempotent.

## Token frugality (a #1 priority)

A "second brain" that auto-injects context every session is a recurring token tax; it must
justify every token.

- **Bounded reads, always** — read a log's HEAD, never a whole growing file. (Boot injection
  already used `read_head`; the risk was full reads.)
- **Cap growth by archival** — keep the live log small (~48 KB); move older blocks to
  `session-log-archive.md`, read only on demand. Turns read cost O(sessions) → O(1). Measured
  win: `session-log.md` 200 KB (~50k tok) → 27 KB (~7k tok), content-preserving.
- **Pointer, not payload; lazy skills** — smallest sufficient context; load a skill only on
  trigger. Keep **auto-loaded** files (contract, CLAUDE.md, .cursor rules) terse — each line
  is a recurring per-session cost.

## Key diagnostic lessons

- **`rebase.autoStash=false` is the load-bearing safety pin.** With it off, a dirty-tree
  `pull --rebase` *refuses* (safe) instead of stashing and risking a stranded stash on a pop
  conflict. Pin it (local config + gitconfig template + re-assert each session).
- **Cosmetic ≠ destructive.** Cross-machine `pull --rebase` re-hashes local commits (re-picks
  them onto arriving commits) — alarming but non-lossy. Check the reflog before assuming loss.
- **Diagnose before hardening.** The auto-sync was already non-destructive; the fix was
  pinning safe defaults + graceful dirty-tree guards, not a rewrite.
- **The git index is shared; `git add` is not a claim on it.** Two agents in one working tree
  share `.git/index`, so `git add <mine>` then `git commit` commits *whatever else the other
  agent staged in between* — the commit takes the whole index, not your paths. Observed
  2026-09-15: a commit swept in two files belonging to a concurrent Cursor session, under a
  message asserting it contained only this session's work. **Use a pathspec-limited commit —
  `git commit -- <paths>` — which ignores index state and commits exactly those paths.**
  Recovery is `git reset --soft HEAD~1`, `git restore --staged <theirs>`, re-commit; their
  files return to untracked, where that session left them. Disjoint *files* (fragment model
  above) prevent merge conflicts but do nothing about a shared *index*; these are different
  layers and only the first was solved.
- **Layer 1 cannot see what you just wrote.** `vault-retrieve.py`'s FTS index is rebuilt at
  SessionStart and by `nightly.py`, so an entry authored mid-session is invisible to the
  lexical fallback until `python3 09-tools/vault-retrieve.py --rebuild --quiet`. Run it after
  adding knowledge, or the session that wrote the entry is the one session that cannot find
  it (observed while recording the index hazard above).
