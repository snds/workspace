---
title: Claude Workspace
tags: [moc, home]
---

# Claude Workspace — Home

The front door. From here you can reach everything. Claude Code reads [[CLAUDE]] at session start;
you read this.

## Operating layer

- [[_FRAMEWORKS|Frameworks]] — the five that govern every project
- [[_CONTEXT|Context]] — who, what, where, when (role, preferences, sessions, artifacts)
- [[_SKILLS|Skills]] — 60+ skill library, hub and spokes
- [[_PROJECTS|Projects]] — active work across all domains
- [[_CHEATSHEET|Cheatsheet]] — slash commands, trigger phrases, Obsidian shortcuts

## Daily flow

1. **Start the day** — open the most recent [[04-artifacts/active/daily|daily note]], or run `/today` in Claude Code to draft one
2. **Work** — edit notes, create artifacts; Claude Code reads context automatically
3. **End the day** — run `/session-end` in Claude Code; it writes the session block, commits, pushes

If you worked on multiple machines today, run `/reconcile` to merge the session blocks into one day entry.

## Navigation shortcuts

- **Command palette:** `⌘P` / `Ctrl+P`
- **Open quickly:** `⌘O` / `Ctrl+O`
- **Search everywhere:** `⌘⇧F` / `Ctrl+Shift+F` (Omnisearch)
- **Graph view:** `⌘G` / `Ctrl+G`

## Recent changes

```dataview
TABLE file.mtime AS "Modified", file.folder AS "Folder"
FROM "06-context" OR "00-frameworks" OR "02-skills" OR "07-projects" OR ".claude/skills"
WHERE file.mtime > date(today) - dur(14 days)
SORT file.mtime DESC
LIMIT 20
```

## Pending — from project-context.md

See [[06-context/project-context]] for the authoritative list. This query surfaces only the top block.

```dataview
LIST
FROM "06-context"
WHERE file.name = "project-context"
```

## Anatomy of this vault

- **`.claude/`** — Claude Code config, hooks, slash-command skills. Don't edit in Obsidian; it's ignored.
- **`.obsidian/`** — Vault config. Also ignored.
- **`00-bootstrap/`** — Installer, Obsidian templates, integration docs (`OBSIDIAN-SETUP.md`), workspace manifest + fallback GDocs.
- **`00-frameworks/`** — The five operating frameworks.
- **`01-shared-references/`** — Standards for reasoning, artifacts, etc.
- **`02-skills/`** — 60+ Claude Desktop skills (hub/spoke). Synced via `skills-manifest.json`.
- **`03-preferences/`** — User preferences file (how Sean wants to collaborate).
- **`04-artifacts/`** — Deliverables. `active/` is WIP; `archive/` is done.
- **`05-version-registers/`** — Versioned artifact history.
- **`06-context/`** — Role, project context, session log, artifact registry.
- **`07-projects/`** — Active projects, numbered.
- **`08-tools/`** — Standalone tools used across projects.
