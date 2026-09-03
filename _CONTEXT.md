---
title: Context
tags: [moc, context]
---

# Context

Everything an agent needs to know before acting. All files in `06-context/`.

## The context files

| File | Purpose | Who writes |
|---|---|---|
| [[06-context/role-and-context]] | Who Sean is, his work, specializations | Sean (rarely changes) |
| [[04-preferences/user-preferences]] | Communication style, tone, conventions | Sean |
| [[06-context/project-context]] | Active projects + pending items (authoritative) | Any agent (via session-end) |
| [[06-context/session-log]] | Session blocks, newest-first | Any agent (via session-end) |
| [[06-context/artifact-registry]] | Structural index of project files | Any agent (via session-end write 4) |
| [[06-context/memory/MEMORY]] | Durable non-project facts + decisions index | Any agent (when a durable fact emerges) |

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

1. **Session start** — Any agent reads [[AGENTS]] then the context heads. Claude Code also injects those heads via `SessionStart` (`.claude/hooks/dispatcher.py`). Cursor re-reads via `.cursor/rules/brain.mdc`.
2. **During session** — The agent reads specific files as needed. Triggers like `legion` or `centric` route attention to specific skills.
3. **Session end** — Session-end writes a Session Block to session-log.md, updates project-context.md, updates artifact-registry.md, commits, pushes. Claude Code slash: `/session-end`.

## Why these files are in Git (and artifacts aren't)

The system layer (`06-context/`, `01-frameworks/`, `03-skills/`, `.claude/`, etc.) is small, text-only, and benefits hugely from version control. `05-artifacts/` is larger, iterates rapidly, and doesn't need Git history — it's versioned by the naming convention (`_vN.N_YYYY-MM-DD`).

Scope in `.gitignore`.
