---
title: Obsidian + agent workspace integration
tags: [project, infrastructure, integration]
status: active
lifecycle: define
---

# 00-obsidian — Obsidian + agent workspace integration

The integration is **portable workspace infrastructure**, not a project deliverable.
It deploys configuration and scaffolding at the workspace root so that one filesystem
serves Obsidian plus any agent (Claude Code, Cursor, Desktop, a human). The contract
is [[AGENTS]]; `CLAUDE.md` / `CURSOR.md` are adapters.

This folder is the **project workspace** — design notes, session state, build history.
The integration's *deployed* files live at the workspace root (one level up from `07-projects/`):

```

├── AGENTS.md             ← deployed: universal contract
├── CLAUDE.md             ← deployed: Claude Code adapter
├── CURSOR.md             ← deployed: Cursor adapter
├── _HOME.md ... (5 MOCs) ← deployed: Obsidian navigation entry points
├── .claude/              ← deployed: hooks + slash-command skills
├── .obsidian/            ← deployed: vault config + plugins
├── .gitignore            ← deployed: scoped Git tracking (system layer only)
└── 00-bootstrap/         ← deployed: installer + Obsidian templates + setup docs
    ├── OBSIDIAN-SETUP.md ← architecture overview + new-machine setup
    ├── setup/            ← cross-platform installer (setup.py + wrappers)
    └── templates/        ← Templater templates for daily notes, projects, skills
```

## Project intent

### Problem & audience

One filesystem has to serve Obsidian and every agent (Claude Code, Cursor, desktop apps, a human)
with no vendor-specific file bridge. The audience is Sean, on each of his machines, plus any agent
that enters the workspace.

### Knowns & unknowns

| claim | label | tier | evidence | decision rule |
|---|---|---|---|---|
| Git is the sync layer and the checkout is the source of truth | known | T1 | the move off the cloud drive; AGENTS.md "Bootstrap on a checkout" | — |
| The 2026-04 SESSION-STATE checkpoint predates that move | known | T1 | the superseded note at the top of SESSION-STATE.md | — |
| Obsidian and the agents never clobber each other's writes | assumed | T5 | not measured | if a lost write shows up in the session log, add a check to the doctor before anything else |
| The Windows setup named in SESSION-STATE is still in use | unknown | T5 | the devices table lists macOS machines only | if no device row names Windows at the next audit, archive the Windows notes |

### Out of scope & later

The deployed files themselves (AGENTS.md, adapters, hooks) have their own homes; this block covers
the integration project. Later: rewrite the stale SESSION-STATE checkpoint.

## Why this lives in `07-projects/`

The integration is a *project* (it's designed, iterated on, has its own state and history).
Its outputs are *infrastructure* (deployed where the consuming tools expect them).
Same pattern as any tool you build for yourself: source/design lives one place,
the installed binaries live where they have to.

## Current scope

- Single-file Python installer (`00-bootstrap/setup/setup.py`) — stdlib only, idempotent, cross-platform
- Claude Code hook dispatcher (`.claude/hooks/dispatcher.py`) plus Cursor rules (`.cursor/rules/brain.mdc`)
- Claude Code slash skills (`today`, `session-end`, `reconcile`, `new-project`, `framework-check`); same jobs are askable on Cursor
- Obsidian vault config: 7 community plugins + custom hotkeys + graph + theme
- Five Obsidian MOCs at workspace root (`_HOME`, `_PROJECTS`, `_SKILLS`, `_FRAMEWORKS`, `_CONTEXT`) with Dataview queries
- Git-tracked system layer via `snds/workspace` repo on GitHub

## Provenance

Pattern from [Mibii's dev.to article](https://dev.to/mibii/claude-code-obsidian-build-a-second-brain-that-actually-thinks-d61),
adapted to an existing multi-project workspace (60+ skills, 5 frameworks, DC+Drive sync, multi-machine).

## See also

- **Operational state:** [SESSION-STATE.md](SESSION-STATE.md)
- **Architecture + setup:** [`00-bootstrap/OBSIDIAN-SETUP.md`](../../00-bootstrap/OBSIDIAN-SETUP.md)
- **Installer docs:** [`00-bootstrap/setup/README.md`](../../00-bootstrap/setup/README.md)
- **Universal contract:** [`AGENTS.md`](../../AGENTS.md)
- **Claude Code adapter:** [`CLAUDE.md`](../../CLAUDE.md)
- **Cursor adapter:** [`CURSOR.md`](../../CURSOR.md)
