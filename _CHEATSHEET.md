---
title: Cheatsheet
tags: [moc, cheatsheet, reference]
audit_skip: true
audit_skip_reason: Cross-context personal reference. Persist as-is; do not flag in /optimize runs (omission from CLAUDE.md MOC list, etc.).
---

# Cheatsheet — working with Claude Code + Obsidian

Mostly transparent. There's a small core worth keeping handy.

## Automatic — you do nothing

**Claude Code**
- `SessionStart` loads context, recent log, project state, hostname, date
- Trigger words in your message auto-route relevant skills
- `SessionEnd` commits + pushes anything dangling

**Obsidian**
- Git plugin: auto-commit + push + pull every 15 min
- Templater: auto-applies templates when you create notes in `04-artifacts/active/daily/` or `07-projects/`
- Dataview tables in MOCs refresh on file focus

## Claude Code — 5 slash commands

| Command | What it does |
|---|---|
| `/today` | Daily note: yesterday's pending → today's priorities → project statuses |
| `/session-end` | Session block + commit + push (or just say "wrap up") |
| `/reconcile` | Merge session blocks from multiple machines for the same day |
| `/new-project` | Scaffold `07-projects/NN-name/` with SESSION-STATE.md |
| `/framework-check` | Critique current work through the 5 frameworks |
| `/optimize` | Brain audit: stale items, contradictions, drift; prioritized punch list; logs to audit-log.md |

## Trigger phrases — no slash needed, just say them

| You say… | What fires |
|---|---|
| "resume", "pick up where we left off", "I'm back" | Workspace bootstrap loads full context |
| "wrap up", "end of session", "done for today" | `/session-end` |
| "reconcile sessions", "end of day sync" | `/reconcile` |
| "legion", "the game", "bobiverse" | Legion project skills |
| "centric", "PLM", "data table" | Centric DS context |
| "icon font", "centricsymbols" | Variable icon font skills |
| "figma plugin" | Figma plugin dev skill |
| "omni" | Omni project skill |

## Obsidian — handy commands (`Ctrl+P` palette)

| Command | When to use |
|---|---|
| **Periodic Notes: Open today's daily note** | Better than right-click→New Note (gets proper `YYYY-MM-DD.md` filename) |
| **Git: Commit all changes** | Manual commit instead of waiting 15 min |
| **Git: Push** / **Git: Pull** | Manual sync |
| **Graph view: Open** | `Ctrl+G` shortcut also works |
| **Quick switcher: Open** | `Ctrl+O` — fastest way to jump to any note |
| **Search in all files** | `Ctrl+Shift+F` — Omnisearch (fuzzy, fast) |

## End-of-day ritual

Just say **"wrap up"** in Claude Code. Everything else is automatic.

## Per-machine setup (one time, on each new machine)

After running `00-bootstrap/setup/setup.command` (Mac) or `setup.bat` (Windows), do the per-machine `.git/` relocation off Drive — see [`00-bootstrap/OBSIDIAN-SETUP.md`](00-bootstrap/OBSIDIAN-SETUP.md) under "Git store lives off Drive". Without this, git will fail on Drive's `desktop.ini` / `.DS_Store` injection.

## Working from Cursor / VS Code / other surfaces

Open one of the multi-root workspace files in `00-bootstrap/workspaces/`:

| File | Use when working on… |
|---|---|
| `centric.code-workspace` | Centric PLM, C8-PLM, Centric UX research, context-aware DS |
| `legion.code-workspace` | Legion (game project) |
| `icon-font.code-workspace` | CentricSymbols variable icon font |
| `figma-plugins.code-workspace` | Claude Figma plugin, Component Set Manager, Figma CLI |
| `system.code-workspace` | The brain itself (CLAUDE.md, hooks, frameworks, integration project) |

In Cursor or VS Code: **File → Open Workspace from File…** → pick one. Each is the Brain folder + the relevant project folders, with other projects hidden. Cursor's AI auto-loads brain context via `.cursor/rules/brain.mdc`. Use **File → Open Recent** to switch contexts fast.

Full surface matrix + AI context discovery rules per surface: [`00-bootstrap/SURFACES.md`](00-bootstrap/SURFACES.md).

## See also

- [[_HOME|Home]] — the front door
- [[_PROJECTS|Projects]], [[_SKILLS|Skills]], [[_FRAMEWORKS|Frameworks]], [[_CONTEXT|Context]]
- [[CLAUDE|CLAUDE.md]] — what Claude Code reads at session start
- [`00-bootstrap/OBSIDIAN-SETUP.md`](00-bootstrap/OBSIDIAN-SETUP.md) — full architecture + troubleshooting
