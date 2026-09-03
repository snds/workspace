# Workspace + Obsidian — Setup & Architecture

_Last updated: 2026-09-02_

The workspace doubles as an Obsidian vault. One folder on disk serves several consumers simultaneously;
the **git checkout is the source of truth** and the plain filesystem is the contract. The universal
agent contract is [[AGENTS]]; this doc covers the Obsidian-specific layer.

## Consumers of the same folder

- **Obsidian** — note-taking UI, graph view, templates, plugins. Reads everything.
- **Cursor** — reads [[AGENTS]] via `.cursor/rules/brain.mdc`; project/user hooks optional. Adapter: [[CURSOR]].
- **Claude Code** — reads `CLAUDE.md` + `.claude/` config; a `SessionStart` hook automates the boot reads. Adapter: [[CLAUDE]].
- **Any other agent** (Perplexity, a generic MCP client, a human) — enters via [[AGENTS]].

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
├── 00-bootstrap/ 01-frameworks/ 02-shared-references/ 03-skills/ 04-preferences/
├── 05-artifacts/ 06-context/ 07-projects/ 08-knowledge/ 09-tools/ _archive/
```

## How the consumers see it

**Obsidian** — opens the root as a vault; ignores `.claude/`, `.obsidian/`, `05-artifacts/archive/`, etc.
(see `userIgnoreFilters` in `.obsidian/app.json`); renders MOCs with live Dataview queries; uses
`[[wikilinks]]` (`useMarkdownLinks: false`). The Obsidian Git plugin can auto-commit + push on a timer.

**Claude Code** — `cd` into the checkout, run `claude`. `CLAUDE.md` loads automatically; the `SessionStart`
hook injects `06-context/*` heads; slash commands (`/today`, `/session-end`, `/reconcile`, `/new-project`,
`/framework-check`) come from `.claude/skills/`; `SessionEnd` commits + pushes. These are Claude-adapter
ergonomics — the workspace works without them (the portable session protocol in framework 08 covers it).

**Any other agent** — reads `llms.txt` → [[AGENTS]] → `03-skills/skills.registry.json`, then follows the
loading-precedence algorithm. No hooks required.

## Sync topology

- **Version control = git**, repo `snds/workspace` on GitHub. It is the source of truth and the sync layer.
  `.gitignore` tracks the system layer (whitelist by folder); see it for what's tracked.
- **Cross-machine:** `git clone` anywhere — no cloud-drive mount, no per-machine `.git` relocation. (The
  legacy Drive-based original needed `.git` moved off Drive to avoid `desktop.ini` corruption; that
  workaround is obsolete here — see [[fact-workspace-repos]]).

## New-machine setup

1. `git clone git@github.com:snds/workspace.git` (or your fork).
2. Ensure Python 3 is available (for `09-tools/build-registry.py`).
3. Optional ergonomics: run `00-bootstrap/setup/` to install Obsidian plugins, the Claude Code config, and git/gh.
4. Open the folder in Obsidian (vault) and/or Cursor. `claude` is optional adapter ergonomics.

## Troubleshooting

**Hooks aren't firing (Claude Code):** verify `.claude/settings.json` is valid JSON; Python is on PATH;
test `python3 .claude/hooks/dispatcher.py session-start < /dev/null`.

**Obsidian doesn't see installed plugins:** Settings → Community plugins → turn on; re-run
`python3 00-bootstrap/setup/setup.py` to re-download missing plugins.

**Git refuses to push:** `gh auth login` → `gh auth setup-git`; check `git remote -v`.

**Registry/links CI failing:** run `python3 09-tools/build-registry.py` and `python3 09-tools/validate-links.py`
locally; commit the regenerated `skills.registry.json`.

## Graph view (why islands exist)

Obsidian Graph is **not** the skill-load graph and **not** Dataview.

- **Dataview `LIST` / `TABLE` does not create edges.** `_PROJECTS.md` tables can look complete while
  project `SESSION-STATE.md` files still sit as islands. Use the static Graph index on [[_PROJECTS]].
- **Stem collisions.** Many files are named `SKILL.md`, `SESSION-STATE.md`, or `README.md`. Bare
  `[[SESSION-STATE]]` cannot resolve. Path-qualify: `[[07-projects/19-workspace-brain/SESSION-STATE]]`.
  Skills resolve as `[[design-foundations]]` because each hub/spoke sets YAML `aliases:` (and
  `aliases` only apply when frontmatter parses). Native Graph still labels those nodes `SKILL`.
  **Juggl** (`HEmile/juggl`) reads YAML `name` / `title` as the node label, so a skill shows as
  `design-foundations` and a map shows as `Skills` / `Knowledge vault index`. Open via command
  palette: "Juggl: Open local graph" from the note you care about. Global Graph stays the nebula.
- **Color groups (first match wins).** Source of truth: `.obsidian/graph.json`. Specific queries
  (maps, skill families) come **before** the `file:SKILL.md` catch-all. Juggl colors live in
  `.obsidian/plugins/juggl/graph.css` and should stay in the same hue set.
- **Search filter (paste into Graph search to hide noise):**
  `-file:LICENSE -file:CHANGELOG -file:README -path:_archive -file:desktop -file:.DS_Store -file:Thumbs -path:copilot -path:03-skills/design-system-ops/skills`
  Maps only: `file:_HOME OR file:_MOC OR file:_INDEX OR file:_SKILLS OR file:_PROJECTS OR file:_CONTEXT OR file:_FRAMEWORKS OR file:_CHEATSHEET OR tag:#moc`
- **Expected remaining islands (do not star-link these into the ontology):**
  - `copilot/` prompt copies (filtered from Graph)
  - `.superpowers/` SDD task briefs
  - vendored trees (React Native dump, figma-cli docs, nested `design-system-ops/commands/`)
  - generated `05-artifacts/` session dumps
- YAML constitutions (`dc-*.yaml`) are not graph nodes. Markdown indexes are: [[domain-constitutions]].

See also [[vault-graph-conventions]] (typed epistemic edges vs skill `## Related` vs domain artifacts).
