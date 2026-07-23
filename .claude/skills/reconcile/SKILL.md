---
name: reconcile
description: Merges Session Blocks from multiple concurrent sessions (different machines, same day) into clean updates for session-log.md and project-context.md. Invoked as /reconcile or triggered by "reconcile sessions"/"end of day sync"/"merge sessions".
---

# /reconcile — Cross-machine session merge

When Sean works on multiple machines in the same day, each session writes its own
Session Block. This skill merges them into a coherent update, then commits.

> **Most of this is now automatic.** Sessions write **fragments**
> (`06-context/sessions/<id>.md`), `09-tools/compact-sessions.py` folds them into
> `session-log.md` idempotently (at session-start/end), and `session-log.md`/
> `audit-log.md` are **union-merged** so concurrent appends never conflict. So the
> **session-log half rarely needs manual reconciliation** — run compaction and it's
> done. This skill's remaining job is the **structured `project-context.md`** merge
> (pending items, decisions, project statuses), which is *not* auto-merged on purpose,
> so genuine conflicts get flagged for a human, never silently guessed.

## Trigger phrases

`/reconcile`, "reconcile sessions", "end of day sync", "merge sessions",
"consolidate sessions".

## Protocol

### Step 1 — Pull latest, then compact

```bash
git pull --rebase          # autostash is pinned OFF: refuses over a dirty tree (safe)
python3 09-tools/compact-sessions.py   # fold any pending session fragments
```

`pull --rebase` won't run over uncommitted changes (commit or stash first — your
work is never stashed/stranded). Union-merge auto-resolves session-log/audit-log
conflicts. If a **structured** file (`project-context.md`) conflicts, stop and
surface it — don't auto-resolve context files.

### Step 2 — Identify blocks to merge

Read `06-context/session-log.md`. Find all Session Blocks dated today
(`Date: {today}`). If there are zero or one, nothing to reconcile —
output `No reconciliation needed.` and exit.

### Step 3 — Merge rules

For all Session Blocks dated today:

- **Artifacts:** Union all entries. Deduplicate by filename.
- **Decisions:** Union all entries. Deduplicate if identical. If two blocks show
  conflicting decisions on the same topic, **flag it, don't auto-resolve** —
  surface to Sean with both versions.
- **Pending added:** Union, deduplicate.
- **Pending resolved:** Union, deduplicate. If an item is both "added" in one
  block and "resolved" in another, treat as "resolved" (net outcome).
- **Project status changes:** Merge per project. If two blocks show different
  end-states for the same project, flag it.
- **Next:** Union, deduplicate per project.

### Step 4 — Write merged day entry

Replace all individual same-day blocks in `session-log.md` with one merged block:

```
--- SESSION BLOCK ---
Date: {today}
Machine: {machine1} + {machine2} + ...  (list all)
Project(s): {union}
...
--- END BLOCK ---
```

### Step 5 — Update project-context.md

Apply merged project status changes and pending delta.
Pending items structure:
- Remove all "Pending resolved" items from the pending list.
- Add all "Pending added" items not already in the pending list.

### Step 6 — Commit and push

```bash
git add -- 06-context/session-log.md 06-context/project-context.md
git commit -m "reconcile: merged {N} sessions for {today}"
git push
```

### Step 7 — Confirm

```
✓ Reconciled {N} sessions ({machine1}, {machine2}, ...) for {today}.
```

## Conflict handling

If any conflicts were flagged in Step 3, output them AFTER the confirmation:

```
⚠ Conflicts flagged — review before next session:
  1. {project}: status end-state conflict — {machine1} says X, {machine2} says Y
  2. ...
```

Don't auto-resolve. Leave the merged block in session-log.md with both versions
listed, and let Sean pick the next session.
