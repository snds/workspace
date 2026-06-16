---
title: Context
tags: [moc, context]
---

# Context

Everything Claude needs to know before acting. All files in `06-context/`.

## The four context files

| File | Purpose | Who writes |
|---|---|---|
| [[06-context/role-and-context]] | Who Sean is, his work, specializations | Sean (rarely changes) |
| [[03-preferences/user-preferences]] | Communication style, tone, conventions | Sean |
| [[06-context/project-context]] | Active projects + pending items (authoritative) | Claude (via `/session-end`) |
| [[06-context/session-log]] | Session blocks, newest-first | Claude (via `/session-end`) |
| [[06-context/artifact-registry]] | Structural index of project files | Claude (via `/session-end` write 4) |

## Recent session entries

```dataview
LIST
FROM "06-context"
WHERE file.name = "session-log"
```

(For full content, click through. This MOC lists the file; the file itself holds the session blocks.)

## Pending items

See [[06-context/project-context]] § Pending Items. Authoritative list.

## How context flows

1. **Session start** — The `SessionStart` hook (`.claude/hooks/dispatcher.py session-start`) reads role, project, session log heads and injects them into Claude's context.
2. **During session** — Claude reads specific files as needed. Triggers like `legion` or `centric` route attention to specific skills.
3. **Session end** — The `/session-end` skill writes a Session Block to session-log.md, updates project-context.md, updates artifact-registry.md, commits, pushes.

## Why these files are in Git (and artifacts aren't)

The system layer (`06-context/`, `00-frameworks/`, `02-skills/`, `.claude/`, etc.) is small, text-only, and benefits hugely from version control. `04-artifacts/` is larger, iterates rapidly, and doesn't need Git history — it's versioned by the naming convention (`_vN.N_YYYY-MM-DD`).

Scope in `.gitignore`.
