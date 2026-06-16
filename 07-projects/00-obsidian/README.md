---
title: Obsidian + Claude Code Integration
tags: [project, infrastructure, integration]
status: active
---

# 00-obsidian — Obsidian + Claude Code Integration

The integration is a **cross-Claude ecosystem tool**, not a project deliverable.
It deploys configuration and scaffolding at the workspace root so that one filesystem
serves three consumers simultaneously: Obsidian, Claude Code, and Claude Desktop.

This folder is the **project workspace** — design notes, session state, build history.
The integration's *deployed* files live at the workspace root (one level up from `07-projects/`):

```

├── CLAUDE.md             ← deployed: Claude Code context
├── _HOME.md ... (5 MOCs) ← deployed: Obsidian navigation entry points
├── .claude/              ← deployed: hooks + slash-command skills
├── .obsidian/            ← deployed: vault config + plugins
├── .gitignore            ← deployed: scoped Git tracking (system layer only)
└── 00-bootstrap/         ← deployed: installer + Obsidian templates + setup docs
    ├── OBSIDIAN-SETUP.md ← architecture overview + new-machine setup
    ├── setup/            ← cross-platform installer (setup.py + wrappers)
    └── templates/        ← Templater templates for daily notes, projects, skills
```

## Why this lives in `07-projects/`

The integration is a *project* (it's designed, iterated on, has its own state and history).
Its outputs are *infrastructure* (deployed where the consuming tools expect them).
Same pattern as any tool you build for yourself: source/design lives one place,
the installed binaries live where they have to.

## Current scope

- Single-file Python installer (`00-bootstrap/setup/setup.py`) — stdlib only, idempotent, cross-platform
- Cross-platform Claude Code hook dispatcher (`.claude/hooks/dispatcher.py`)
- Five `/`-command skills (`today`, `session-end`, `reconcile`, `new-project`, `framework-check`)
- Obsidian vault config: 7 community plugins + custom hotkeys + graph + theme
- Five Obsidian MOCs at workspace root (`_HOME`, `_PROJECTS`, `_SKILLS`, `_FRAMEWORKS`, `_CONTEXT`) with Dataview queries
- Git-tracked system layer via `claude-workspace-system` repo on GitHub

## Provenance

Pattern from [Mibii's dev.to article](https://dev.to/mibii/claude-code-obsidian-build-a-second-brain-that-actually-thinks-d61),
adapted to an existing multi-project Claude Workspace (60+ skills, 5 frameworks, DC+Drive sync, multi-machine).

## See also

- **Operational state:** [SESSION-STATE.md](SESSION-STATE.md)
- **Architecture + setup:** [`00-bootstrap/OBSIDIAN-SETUP.md`](../../00-bootstrap/OBSIDIAN-SETUP.md)
- **Installer docs:** [`00-bootstrap/setup/README.md`](../../00-bootstrap/setup/README.md)
- **Claude Code context:** [`CLAUDE.md`](../../CLAUDE.md)
