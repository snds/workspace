---
name: session-end
description: End-of-session protocol. Writes Session Block to session-log.md, updates project-context.md, runs skills sync, commits and pushes to Git. Invoked as /session-end or triggered by "end of session"/"wrap up"/"done for today".
---

# /session-end — Close out the session cleanly

Writes a Session Block, updates project context, commits to Git, pushes to remote.
The `SessionEnd` hook will catch and commit anything not committed explicitly, but
the block itself needs Claude to author — the hook can't know what was decided.

## Trigger phrases

Invoke explicitly as `/session-end`, or auto-trigger on any of:
"end of session", "wrap up", "session done", "that's it for now", "done for today",
"let's close out", "logging off".

## Surface detection (run first, before any other step)

Run this probe to identify the current surface:

```bash
printf "CURSOR:%s\nTERM_PROG:%s\nVSCODE_PID:%s\nCC_ENTRY:%s\nCLAUDE_PROJ:%s\nDESKTOP:%s\nPARENT:%s\n" \
  "${CURSOR_TRACE:-}" "${TERM_PROGRAM:-}" "${VSCODE_PID:-}" \
  "${CLAUDE_CODE_ENTRYPOINT:-}" "${CLAUDE_PROJECT_DIR:-}" "${CLAUDE_DESKTOP_APP:-}" \
  "$(ps -p $PPID -o comm= 2>/dev/null)"
```

Decision table (first match wins):

| Signal | Surface label |
|---|---|
| `CURSOR_TRACE` set OR `TERM_PROGRAM=cursor` | `Cursor` |
| `VSCODE_PID` set AND parent process contains `Cursor` | `Cursor` |
| `VSCODE_PID` set OR `CLAUDE_CODE_ENTRYPOINT=ide` | `VS Code + Claude Code` |
| `CLAUDE_CODE_ENTRYPOINT=cli` | `Claude Code CLI` |
| `CLAUDE_PROJECT_DIR` set, no above signals | `Claude Code` |
| `CLAUDE_DESKTOP_APP` set | `Claude Desktop / Cowork` |
| No signals (web session, hooks not running) | `claude.ai web` |

**Note on Cursor vs VS Code:** Cursor is built on VS Code and sets `VSCODE_PID`, so
the parent process check (`ps -p $PPID -o comm=`) is the reliable discriminator when
`CURSOR_TRACE` and `TERM_PROGRAM` are both unset. If `ps` is unavailable, fall back
to contextual signals — if `brain.mdc` rules are loaded, you are in Cursor.

Resolve machine label from `hostname` per the standard table. Together these give
you the **session signature**: `{Machine label} / {Surface}` — e.g. `Work MacBook Pro / Cursor`.

## Protocol

### Step 1 — Generate Session Block

Draft using the Session Block format (see template below). Base it on:
- Files modified this session (via `git status` + `git diff`)
- Decisions stated by Sean in the conversation
- Pending items added or resolved
- Project status changes
- Next actions for any active project

One line per entry. Omit empty sections.

### Step 2 — Write to session-log.md

Append the block under `## Session Entries` in `06-context/session-log.md`.
**Newest-first** — insert at the top of the section, not the bottom.

### Step 3 — Update project-context.md (only if needed)

Apply pending adds/resolves and project status changes. Skip if no changes.

### Step 4 — Update artifact-registry.md (only if files were created/modified)

For any file created or modified in `07-projects/` this session, update or add its
entry in `06-context/artifact-registry.md`.

### Step 5 — Harvest knowledge (if warranted)

Scan the session for durable insights — decisions whose *why* isn't captured elsewhere,
discovered constraints, validated patterns, research synthesis. If found, write or update
an entry in `08-knowledge/{domain}/` and update `08-knowledge/_INDEX.md`.
Skip for purely mechanical sessions.

```yaml
---
tags: [domain-tag, topic-tag]
created: YYYY-MM-DD
updated: YYYY-MM-DD
status: working | stable | superseded
confidence: high | medium | low | speculative
sources: [session-log date, project name]
related_skills: [skill-name]
related_projects: [project-name]
---
```

### Step 6 — Regenerate the skill registry

If any `SKILL.md` frontmatter changed this session, run
`python3 09-tools/build-registry.py` and commit the regenerated
`03-skills/skills.registry.json` alongside the session log. No Drive/mount sync —
git is the source of truth.

### Step 7 — Commit + push (session changes only)

Use the session signature from surface detection in the commit message:

```bash
git add -A -- .claude CLAUDE.md 06-context 01-frameworks 02-shared-references \
               03-skills 04-preferences 00-bootstrap 08-knowledge \
               _HOME.md _PROJECTS.md _SKILLS.md _FRAMEWORKS.md _CONTEXT.md
git commit -m "session: {YYYY-MM-DD} [{session signature}] — {one-line summary}"
git push
```

Example: `session: 2026-05-04 [Work MacBook Pro / Cursor] — data table cell anatomy`

The `[Machine / Surface]` tag in every commit message makes each file's origin
queryable via `git log -1 --format="%s" -- {filepath}`.

If `git push` fails, surface the error and stop. Don't retry.

### Step 7.5 — Orphaned changes audit

After the session commit, check for remaining dirty tracked files:

```bash
cd "."
git status --short
```

**If the working tree is clean:** output the confirm line (Step 8) and stop.

**If dirty files remain:** for each file, look up its last commit to determine origin:

```bash
git log -1 --format="%s" -- {filepath}
```

Extract the `[Machine / Surface]` tag from the commit message if present.
Files with no prior commit (untracked) are attributed to the current session's
machine but marked as `surface: unknown`.

Group by origin and present:

```
⚠ Uncommitted workspace changes not from this session:

  {Machine label} / {Surface} (last committed {date}):
    • {filepath}
    • {filepath}

  Commit these as a housekeeping pass? (yes / no / show diff)
```

- **yes** → `git add {files}` + `git commit -m "workspace: housekeeping [{origin}] — {date}"` + push
- **show diff** → `git diff {files}`, then ask again
- **no** → leave dirty, note them in the session block under a `Deferred commits:` section
  so the next session knows they're intentionally pending

Do not auto-commit. Always ask. These files belong to another session's context
and committing them silently under the wrong message corrupts the audit trail.

### Step 8 — Confirm

```
✓ Session logged and pushed — {N} files committed.
```

---

## Session Block Template

```
--- SESSION BLOCK ---
Date: {YYYY-MM-DD}
Machine: {Work MacBook Pro | Personal MacBook Pro | Windows Desktop}
Surface: {Cursor | Claude Code CLI | Claude Code | VS Code + Claude Code | Claude Desktop / Cowork | claude.ai web}
Project(s): {project name(s) worked on this session}
Artifacts:
  - {filename_vN.N_YYYY-MM-DD.ext} — {one-line description}
Decisions:
  - {decision made, rationale in one line}
Pending added:
  - {new item}
Pending resolved:
  - {item completed}
Project status changes:
  - {project name}: {old status} → {new status}
Deferred commits:
  - {filepath} — pending, owned by {Machine / Surface}
Next:
  - {specific next action}
--- END BLOCK ---
```

Omit any section with no content. Keep entries to one line.
`Deferred commits:` only appears when Step 7.5 results in a "no" answer.

---

## Cursor surface overrides

When running in Cursor (detected via surface detection or `brain.mdc` context):

- **Step 6** — run `python3 09-tools/build-registry.py` from the terminal if skills changed.
- **Skip the SessionEnd hook reference** — hooks are Claude Code only.
- **Read/write files via the filesystem**; use the terminal for git.
- **Surface detection probe** still applies — run it in terminal.
- Confirm line: `✓ Session logged and pushed — {N} files committed. Obsidian will reflect on next focus.`

All other steps including 7.5 run identically.

---

## Notes

- **Never ask Sean which machine he's on.** Resolve from `hostname`.
- **Newest-first** in session-log.md. workspace-bootstrap reads top-down.
- **Trivial sessions** (no decisions, no file changes, no artifacts): write a **nano block**
  instead of a full session block, then commit it. A nano block preserves cross-surface
  continuity — without it, every surface shows a stale "last session" date.

  ```
  --- NANO BLOCK ---
  Date: {YYYY-MM-DD}
  Machine: {label}
  Surface: {surface}
  Context load only — no decisions or artifacts.
  --- END BLOCK ---
  ```

  Commit with: `session: {date} [{signature}] — context load only`
  Still run Step 7.5 after — orphaned changes can exist even in trivial sessions.
- The `[Machine / Surface]` commit tag is how future sessions attribute dirty files.
  Old commits without it will show `surface: unknown` — that's expected during transition.

## Worktree auto-cleanup (informational)

The `SessionEnd` hook auto-removes Drive-resident worktrees whose branches are
fully merged into `main`. Worktrees with unmerged commits, detached HEAD, or
located off-Drive are skipped. A stale-checkout state triggers the auto-commit
safety guard before cleanup runs.
