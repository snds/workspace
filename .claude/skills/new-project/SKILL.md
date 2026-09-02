---
name: new-project
description: Scaffolds a new project under 07-projects/ with SESSION-STATE.md, README, and standard folder shape. Registers it in project-context.md and _PROJECTS.md MOC. Invoked as /new-project.
---

# /new-project — Scaffold a new project

Creates `07-projects/NN-name/` with the standard shape, seeds it with
SESSION-STATE from the template, adds it to project-context.md, and updates
the MOC.

## Trigger phrases

`/new-project`, "scaffold new project", "start a new project",
"add project {name}".

## Protocol

### Step 1 — Collect inputs

Ask Sean (or accept as arguments):
- **Project name** (short, hyphenated: `data-table-audit`, not "Data Table Audit")
- **One-line summary**
- **Initial status** (default: `Planning`)
- **Trigger words** (optional — for the UserPromptSubmit hook to route to this project)
- **Associated frameworks** (default: all eleven — can narrow later)

### Step 2 — Resolve next NN

```bash
ls 07-projects/ | grep -E '^[0-9]{2}-' | sort | tail -1
```

Parse the highest `NN`, increment. If `07-projects/` is empty, start at `00`.

### Step 3 — Create folder and files

```
07-projects/{NN}-{name}/
├── README.md                    # short project overview
├── SESSION-STATE.md             # operational state (from template)
└── notes/                       # freeform notes folder (Obsidian-friendly)
```

Seed `SESSION-STATE.md` from `01-frameworks/_session-state-template.md`.
Seed `README.md` with summary, status, trigger words, framework refs, and
a link back to the project-context.md entry.

### Step 4 — Register in project-context.md

Append a new entry under `## Active Projects` in `06-context/project-context.md`:

```markdown
### {Project Name}
**Status:** {initial status}
**Summary:** {one-line summary}
**Folder:** `07-projects/{NN}-{name}/`
**Triggers:** {trigger words, comma-separated} (or _none_)
**Next:** [Captured per SESSION-STATE when project resumes.]
```

Preserve alphabetical or numeric order as it exists.

### Step 5 — Register in _PROJECTS.md MOC

Add a row to the Dataview table in `_PROJECTS.md` — actually, Dataview queries
auto-populate from frontmatter, so no manual edit needed. Just confirm the
new `README.md` has the right frontmatter for the query to pick it up:

```yaml
---
title: {Project Name}
type: project
status: {initial status}
triggers: [trigger1, trigger2]
frameworks: [aesthetic-lens, ui-ux-operational, ...]
---
```

### Step 6 — Register trigger words (if any)

If trigger words were provided, add them to the `TRIGGER_WORDS` dict in
`.claude/hooks/dispatcher.py`. Otherwise skip.

### Step 7 — Confirm

```
✓ Created 07-projects/{NN}-{name}/
✓ Added to project-context.md
✓ Registered in _PROJECTS.md MOC
{✓ Registered trigger words: {...} | (no triggers)}
```

The session-end commit will pick up all changes. No manual commit here.
