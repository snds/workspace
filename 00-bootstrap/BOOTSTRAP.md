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
AGENTS.md            universal contract · llms.txt  machine entry · CLAUDE/CURSOR/PERPLEXITY/GEMINI/WARP.md  adapters
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
2. Emit `python3 09-tools/session-status.py --surface "<this tool>"` (notices + all
   projects + pending). Skip on continuations.
3. Read [[AGENTS]] → `06-context/` heads (role, project-context, session-log head,
   [[06-context/memory/MEMORY|MEMORY]]) → [[04-preferences/user-preferences]].
   Do not ingest `03-skills/skills.registry.json`.
4. Match the request via `python3 09-tools/skill-loadset.py "…"`; load only those
   `SKILL.md` paths (foundation → hub → spoke).

Per tool: **Claude Code/Desktop** auto-loads [[CLAUDE]] (a `SessionStart` hook can
automate the reads). **Cursor** uses [[CURSOR]] + `.cursor/rules/brain.mdc` + the
user `sessionStart` hook. **Perplexity / generic MCP / a human** follow [[AGENTS]]
directly — no adapter required.

## Setup

`00-bootstrap/setup/` installs the optional ergonomics (Obsidian plugins, the Claude Code config, git).
None of it is required to *work* in the checkout — it only adds convenience. The workspace functions on a
plain `git clone` with Python 3 available for `09-tools/build-registry.py`.

### Doctor modes and installers

`00-bootstrap/doctor/workspace-doctor.sh` reports; it installs nothing unattended.

| Mode | Behaviour |
|---|---|
| default | Reports every layer. Heals only the HEAL class: `~/.claude/hooks/workspace-{sessionstart,reassert,audit}.sh`, `~/.claude/CLAUDE.md`, `~/.claude/workspace-brain-path`, `~/.claude/ws-state/`. |
| `--quick` | As default, without the beacon, canary, chat and hygiene sections. Never scans and never runs an installer. The Claude SessionStart hook runs it outside the workspace. |
| `--quiet` | The launchd mode. May also write `telemetry/install-state.json` and run the pinned `profile_resolve.py scan --report`, only when `~/.config/snds-workspace/telemetry/` exists. |
| `--check` | Reports only, writes nothing, exits 1 on drift. Adds the exact overlay env comparison, pin lag, git capabilities and probe-record notes. |
| `--no-launchctl` | No `launchctl` or `osascript` calls. Automatic when `$HOME` is not the passwd home. |

Everything else it looks at (Cursor shims, the Claude settings overlay, `~/.config/snds-workspace`,
plugin hooks, the launchd job, fossils, beacons) is REPORT class: a drift line names the installer.

Installers are explicit and human-run, one per invocation, each with an uninstall:
`--install-<name>[=ARG]` / `--uninstall-<name>[=ARG]` for `pin`, `shims` (`=SURFACE`, `--probe`),
`git-hooks`, `identity`, `claude-overlay`, `sandbox-roots`, `plugin`, `projects-pointer` and
`launchd`. The flags exec `00-bootstrap/doctor/installers.py`, which refuses (exit 4) without a TTY
on stdin and stdout or when an agent is detected or possible, prints a diff, asks `Apply? [y/N]`,
backs each target up to `<target>.ws-bak.<UTC>` and logs to `control/install-log.jsonl`. Uninstall
restores those backups byte-for-byte. `--install-pin` copies the pinned paths at one commit into
`~/.config/snds-workspace/lib/<sha>/` (`pin_lib.py`); hooks run that copy, never the live tree.
Run installers in a plain terminal, never from an agent session.

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
