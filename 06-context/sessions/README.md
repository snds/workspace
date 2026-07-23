# Session fragments — conflict-free session records

Each session writes its Session Block to its **own file** here
(`<date>-<machine>-<shortid>.md`) instead of prepending to the shared
`../session-log.md`. Disjoint files can't collide, so any number of sessions on
any number of machines/surfaces record in parallel with **zero merge conflicts**.

`09-tools/compact-sessions.py` folds fragments into `../session-log.md`
(newest-first) and removes the folded fragment. It is **idempotent** (dedupes by
the `SessionID:` marker — a fragment already in the log is skipped) and **self-
healing** (safe to run any number of times, on any machine; runs at session-start
and from the doctor). The git history keeps every fragment even after folding.

A fragment is a normal Session Block plus a unique `SessionID:` line, e.g.:

```
### 2026-07-22 — Short title

SessionID: 2026-07-22-voyager-a1b2c3
--- SESSION BLOCK ---
Date: 2026-07-22
Machine: Personal MacBook Pro
Surface: Claude Code (Mac desktop app)
Project(s): …
Summary: …
--- END BLOCK ---
```

Transient per-session files (`*.touched`, `*.alive`) are gitignored — only `*.md`
fragments and this README are tracked.
