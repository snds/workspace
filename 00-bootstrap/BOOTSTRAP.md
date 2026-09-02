# Workspace — Bootstrap Reference

A human-facing getting-started. The **authoritative** contract any agent follows is
[[AGENTS]]; the session protocol and per-layer editing rules are in
[[08-workspace-contribution-framework]]; the operational
session-handshake skill is [[workspace-bootstrap]]. This file does not duplicate them.

## What this is

A long-lived, **portable** personal operating environment for design, engineering, product, data, and
game work. It is simultaneously a git repository (the source of truth), an Obsidian vault, and an agent
workspace. Any capable model — not one vendor's — can enter and work here by reading
[[AGENTS]]. Nothing depends on Google Drive or a vendor-specific file bridge: read and write ordinary
files; git is the sync layer.

## Folder structure

```
AGENTS.md            universal contract · llms.txt  machine entry · CLAUDE/CURSOR/PERPLEXITY.md  adapters
00-bootstrap/        this getting-started + setup
01-frameworks/       operating models (01–16; 08 governs editing the workspace itself, 10 is the native-resolution perception precondition, 11 is the anticipatory failure/pre-mortem lens, 13 is domain rigor)
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
2. Read [[AGENTS]] → `03-skills/skills.registry.json` → `06-context/` (role,
   project-context, session-log head, [[06-context/memory/MEMORY|MEMORY]]) → [[04-preferences/user-preferences]].
3. Match the request to skills via `triggers`/`description`; load the `load_chains` ancestors in order
   (foundation → hub → spoke). See AGENTS.md "Skill loading precedence."

Per tool: **Claude Code/Desktop** auto-loads [[CLAUDE]] (a `SessionStart` hook can
automate the reads). **Cursor** uses [[CURSOR]] + `.cursor/rules/brain.mdc`.
**Perplexity / generic MCP / a human** follow [[AGENTS]] directly — no adapter required.

## Setup

`00-bootstrap/setup/` installs the optional ergonomics (Obsidian plugins, the Claude Code config, git).
None of it is required to *work* in the checkout — it only adds convenience. The workspace functions on a
plain `git clone` with Python 3 available for `09-tools/build-registry.py`.

## Conventions (quick reference)

- **Artifacts:** `context_descriptor_vN.N_YYYY-MM-DD.ext` — never overwrite; increment version
  (minor = iterative, major = structural). See [[artifact-standards]].
- **Where things go:** consult the routing map in [[workspace-ontology]] before
  writing. Skills → `03-skills/`; learned insight → `08-knowledge/`; durable non-project facts →
  `06-context/memory/`; retire via `_archive/` with provenance.
- **Never** rename a `SKILL.md` (add `aliases`), hand-edit generated files, or delete (archive instead).

## Shared references — load when relevant

- [[epistemic-standards]] — reasoning discipline
- [[artifact-standards]] — deliverable obligations
- [[skill-frontmatter]] — the SKILL.md frontmatter v2 spec

## Also in this folder

- [[00-bootstrap/OBSIDIAN-SETUP|OBSIDIAN-SETUP]] — vault + graph conventions
- [[00-bootstrap/SURFACES|SURFACES]] — how each tool sees the brain
- [[00-bootstrap/setup/README|setup README]] — optional install scripts
- Templates: [[00-bootstrap/templates/skill|skill]] · [[00-bootstrap/templates/project-readme|project-readme]] · [[00-bootstrap/templates/daily-note|daily-note]]
- [[00-bootstrap/adapters/_ADAPTER-TEMPLATE|_ADAPTER-TEMPLATE]]

---

*This file is a human pointer. Any agent that reads [[AGENTS]] has full context.*
