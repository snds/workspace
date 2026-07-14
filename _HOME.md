---
title: Claude Workspace
tags: [moc, home]
---

# Claude Workspace — Home

The front door. From here you can reach everything. Claude Code reads [[CLAUDE]] at session start;
you read this.

## Operating layer

- [[_FRAMEWORKS|Frameworks]] — the eleven that govern every project
- [[_CONTEXT|Context]] — who, what, where, when (role, preferences, sessions, artifacts)
- [[_SKILLS|Skills]] — 280+ skill library, hub and spokes
- [[_PROJECTS|Projects]] — active work across all domains
- [[_CHEATSHEET|Cheatsheet]] — slash commands, trigger phrases, Obsidian shortcuts

## Daily flow

1. **Start the day** — open the most recent daily note in `05-artifacts/active/daily/`, or run `/today` in Claude Code to draft one
2. **Work** — edit notes, create artifacts; Claude Code reads context automatically
3. **End the day** — run `/session-end` in Claude Code; it writes the session block, commits, pushes

If you worked on multiple machines today, run `/reconcile` to merge the session blocks into one day entry.

## 📋 Open tasks

Items tagged `#task` across the vault, soonest due first. Add one anywhere with `- [ ] something #task`.

```tasks
not done
sort by due
limit 25
short mode
```

## Navigation shortcuts

- **Command palette:** `⌘P` / `Ctrl+P`
- **Open quickly:** `⌘O` / `Ctrl+O`
- **Search everywhere:** `⌘⇧F` / `Ctrl+Shift+F` (Omnisearch)
- **Graph view:** `⌘G` / `Ctrl+G`

## Recent changes

```dataview
TABLE file.mtime AS "Modified", file.folder AS "Folder"
FROM "06-context" OR "01-frameworks" OR "03-skills" OR "07-projects" OR ".claude/skills"
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
- **`00-bootstrap/`** — Getting-started + setup. Contract lives in `AGENTS.md`.
- **`01-frameworks/`** — The eleven operating frameworks (08 governs editing the workspace itself; 10 is the native-resolution perception-integrity precondition; 11 is the anticipatory failure/pre-mortem lens).
- **`02-shared-references/`** — Standards: ontology + routing map, frontmatter spec, reasoning/artifact standards.
- **`03-skills/`** — Skill library (hub/spoke). Graph in `skills.registry.json` (generated from frontmatter).
- **`04-preferences/`** — User preferences file (how Sean wants to collaborate).
- **`05-artifacts/`** — Deliverables. `active/` is WIP; `archive/` is done.
- **`06-context/`** — Role, project context, session log, artifact registry, and `memory/` (durable non-project memory).
- **`07-projects/`** — Active projects, numbered.
- **`08-knowledge/`** — Learned domain insight.
- **`09-tools/`** — Portable scripts, generators, validators.
- **`_archive/`** — Retired files + `ARCHIVE-LOG.md` provenance.
