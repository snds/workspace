---
tags: [cross-domain, engineering, git, concurrency, token-frugality, workspace-ops]
created: 2026-07-23
updated: 2026-07-23
status: stable
confidence: high
sources: [session-log 2026-07-23, .claude/hooks/dispatcher.py, 09-tools/compact-sessions.py]
related_skills: []
related_projects: [18-bootstrap-generator, 19-workspace-brain]
triggers: [multi-session, concurrent session, cross-machine sync, session-log, git pull rebase, autostash, token frugality, session fragment, compaction, workspace resilience]
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
