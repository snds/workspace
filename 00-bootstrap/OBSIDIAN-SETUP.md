# Workspace + Obsidian — Setup & Architecture

_Last updated: 2026-06-16_

The workspace doubles as an Obsidian vault. One folder on disk serves several consumers simultaneously;
the **git checkout is the source of truth** and the plain filesystem is the contract. The universal
agent contract is [AGENTS.md](../AGENTS.md); this doc covers the Obsidian-specific layer.

## Consumers of the same folder

- **Obsidian** — note-taking UI, graph view, templates, plugins. Reads everything.
- **Claude Code** — reads `CLAUDE.md` + `.claude/` config; a `SessionStart` hook automates the boot reads.
- **Any other agent** (Cursor, Perplexity, a generic MCP client, a human) — enters via [AGENTS.md](../AGENTS.md).

No sync bridge, no cloud drive, no API layer. Whatever Obsidian sees, every agent sees. Git is the sync
and history layer across machines.

## Directory map

```
<checkout>/                                ← Obsidian vault root = working dir (contains AGENTS.md)
├── AGENTS.md  llms.txt  CLAUDE.md  CURSOR.md  PERPLEXITY.md   ← contract + adapters
├── _HOME.md _MOC.md _SKILLS.md ...         ← MOCs (Maps of Content) for Obsidian nav
├── .claude/                                ← Claude Code config — NOT shown in Obsidian
│   ├── settings.json · hooks/dispatcher.py · skills/ (/today, /session-end, …)
├── .obsidian/                              ← vault config — NOT shown in Obsidian
│   ├── app.json · graph.json (color groups) · community-plugins.json · plugins/ (per-machine)
├── 00-bootstrap/ 00-frameworks/ 01-shared-references/ 02-skills/ 03-preferences/
├── 04-artifacts/ 05-version-registers/ 06-context/ 07-projects/ 08-knowledge/ 09-tools/ _archive/
```

## How the consumers see it

**Obsidian** — opens the root as a vault; ignores `.claude/`, `.obsidian/`, `04-artifacts/archive/`, etc.
(see `userIgnoreFilters` in `.obsidian/app.json`); renders MOCs with live Dataview queries; uses
`[[wikilinks]]` (`useMarkdownLinks: false`). The Obsidian Git plugin can auto-commit + push on a timer.

**Claude Code** — `cd` into the checkout, run `claude`. `CLAUDE.md` loads automatically; the `SessionStart`
hook injects `06-context/*` heads; slash commands (`/today`, `/session-end`, `/reconcile`, `/new-project`,
`/framework-check`) come from `.claude/skills/`; `SessionEnd` commits + pushes. These are Claude-adapter
ergonomics — the workspace works without them (the portable session protocol in framework 08 covers it).

**Any other agent** — reads `llms.txt` → `AGENTS.md` → `02-skills/skills.registry.json`, then follows the
loading-precedence algorithm. No hooks required.

## Sync topology

- **Version control = git**, repo `snds/workspace` on GitHub. It is the source of truth and the sync layer.
  `.gitignore` tracks the system layer (whitelist by folder); see it for what's tracked.
- **Cross-machine:** `git clone` anywhere — no cloud-drive mount, no per-machine `.git` relocation. (The
  legacy Drive-based original needed `.git` moved off Drive to avoid `desktop.ini` corruption; that
  workaround is obsolete here — see `06-context/memory/fact-workspace-repos.md`.)

## New-machine setup

1. `git clone git@github.com:snds/workspace.git` (or your fork).
2. Ensure Python 3 is available (for `09-tools/build-registry.py`).
3. Optional ergonomics: run `00-bootstrap/setup/` to install Obsidian plugins, the Claude Code config, and git/gh.
4. Open the folder in Obsidian (vault) and/or run `claude` from it.

## Troubleshooting

**Hooks aren't firing (Claude Code):** verify `.claude/settings.json` is valid JSON; Python is on PATH;
test `python3 .claude/hooks/dispatcher.py session-start < /dev/null`.

**Obsidian doesn't see installed plugins:** Settings → Community plugins → turn on; re-run
`python3 00-bootstrap/setup/setup.py` to re-download missing plugins.

**Git refuses to push:** `gh auth login` → `gh auth setup-git`; check `git remote -v`.

**Registry/links CI failing:** run `python3 09-tools/build-registry.py` and `python3 09-tools/validate-links.py`
locally; commit the regenerated `skills.registry.json`.
