# Workspace — Bootstrap Reference

A human-facing getting-started. The **authoritative** contract any agent follows is
[AGENTS.md](../AGENTS.md); the session protocol and per-layer editing rules are in
[framework 08](../01-frameworks/08-workspace-contribution-framework.md); the operational
session-handshake skill is `03-skills/workspace-bootstrap/SKILL.md`. This file does not duplicate them.

## What this is

A long-lived, **portable** personal operating environment for design, engineering, product, data, and
game work. It is simultaneously a git repository (the source of truth), an Obsidian vault, and an agent
workspace. Any capable model — not one vendor's — can enter and work here by reading
[AGENTS.md](../AGENTS.md). Nothing depends on Google Drive or Desktop Commander: read and write ordinary
files; git is the sync layer.

## Folder structure

```
AGENTS.md            universal contract · llms.txt  machine entry · CLAUDE/CURSOR/PERPLEXITY.md  adapters
00-bootstrap/        this getting-started + setup
01-frameworks/       operating models (01–08; 08 governs editing the workspace itself)
02-shared-references/ standards: ontology + routing map, frontmatter spec, epistemic/artifact standards
03-skills/           skill library + skills.registry.json (generated graph)
04-preferences/      behavioral defaults
05-artifacts/        generated outputs (versioned)
06-context/          role, project-context, session-log, artifact-registry, memory/
07-projects/         project workspaces (each with SESSION-STATE.md)
08-knowledge/        learned domain insight
09-tools/            portable scripts/generators/validators
_archive/            retired files + ARCHIVE-LOG.md provenance
```

## How to start a session

1. Resolve the workspace root: the directory containing `AGENTS.md` (this checkout).
2. Read [AGENTS.md](../AGENTS.md) → `03-skills/skills.registry.json` → `06-context/` (role,
   project-context, session-log head, `memory/MEMORY.md`) → `04-preferences/user-preferences.md`.
3. Match the request to skills via `triggers`/`description`; load the `load_chains` ancestors in order
   (foundation → hub → spoke). See AGENTS.md "Skill loading precedence."

Per tool: **Claude Code/Desktop** auto-loads [CLAUDE.md](../CLAUDE.md) (a `SessionStart` hook can
automate the reads). **Cursor** uses [CURSOR.md](../CURSOR.md) + `.cursor/rules/brain.mdc`.
**Perplexity / generic MCP / a human** follow [AGENTS.md](../AGENTS.md) directly — no adapter required.

## Setup

`00-bootstrap/setup/` installs the optional ergonomics (Obsidian plugins, the Claude Code config, git).
None of it is required to *work* in the checkout — it only adds convenience. The workspace functions on a
plain `git clone` with Python 3 available for `09-tools/build-registry.py`.

## Conventions (quick reference)

- **Artifacts:** `context_descriptor_vN.N_YYYY-MM-DD.ext` — never overwrite; increment version
  (minor = iterative, major = structural). See `02-shared-references/artifact-standards.md`.
- **Where things go:** consult the routing map in `02-shared-references/workspace-ontology.md` before
  writing. Skills → `03-skills/`; learned insight → `08-knowledge/`; durable non-project facts →
  `06-context/memory/`; retire via `_archive/` with provenance.
- **Never** rename a `SKILL.md` (add `aliases`), hand-edit generated files, or delete (archive instead).

## Shared references — load when relevant

- `02-shared-references/epistemic-standards.md` — reasoning discipline
- `02-shared-references/artifact-standards.md` — deliverable obligations
- `02-shared-references/skill-frontmatter.md` — the SKILL.md frontmatter v2 spec

---

*This file is a human pointer. Any agent that reads [AGENTS.md](../AGENTS.md) has full context.*
