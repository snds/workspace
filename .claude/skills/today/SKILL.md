---
name: today
description: Daily note. Carries yesterday's open tasks forward, surfaces project priorities, drafts today's focus. Invoked as /today.
---

# /today — Daily planning note

Creates or opens today's daily note at `04-artifacts/active/daily/YYYY/YYYY-MM-DD.md`.
Carries forward open tasks from the most recent prior daily, surfaces current project
priorities, and drafts a focus block.

## Behavior

1. **Resolve today's path.** `04-artifacts/active/daily/{YYYY}/{YYYY-MM-DD}.md`.
   Create the `YYYY` directory if missing.

2. **Check if today's note exists.**
   - If exists: read and display. Do not overwrite. Offer to append.
   - If not: proceed to create.

3. **Find yesterday's (or most recent) daily note.**
   `ls 04-artifacts/active/daily/{YYYY}/` — pick the highest-dated file before today.
   Read it. Extract open tasks (`- [ ]` lines) from the **## Tasks** section.

4. **Read current project context.** `06-context/project-context.md` — extract
   the "Pending Items" section + any projects with recent activity in `session-log.md`.

5. **Draft today's note** using the template below.

6. **Confirm with Sean.** Show the draft, ask if anything should be added or adjusted
   before writing.

## Template

```markdown
---
title: {YYYY-MM-DD}
date: {YYYY-MM-DD}
tags: [daily]
machine: {machine label from hostname}
---

# {YYYY-MM-DD} — {day of week}

## Focus
- (top 3 priorities for today — drafted from carried-over + project pending)

## Tasks
### Carried forward
- [ ] (from yesterday's open tasks)

### New
- [ ]

## Project priorities surfaced
- **{project name}:** {pending item summary}
- ...

## Notes

## End of day
- (filled at session-end)
```

## Notes

- This note is an artifact, not a context file. It does **not** get committed
  to Git by default (see `.gitignore`) — it's local to the machine Sean worked from.
- If Sean wants to promote a decision from the daily into project context,
  that happens at `/session-end`, not here.
- If today's note already exists and Sean runs `/today` again, the skill
  should **append a new "## Update" section** with the current time, not overwrite.
