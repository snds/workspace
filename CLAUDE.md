# Claude Adapter — Claude Code / Desktop

_This is the **Claude adapter** over the universal contract in [AGENTS.md](AGENTS.md). It describes
only how Claude executes that contract (hooks, slash commands, the session-start ritual). The contract
itself — folder semantics, read order, the skill loading algorithm, the routing map — lives in
AGENTS.md and is not duplicated here. Auto-loaded into every Claude Code session run from this directory._

---

## What this is

The workspace is Sean's cross-device, **portable** design + engineering environment. The git checkout
is the source of truth; the plain filesystem is the I/O layer. The same files serve several readers:

- **Obsidian** reads this folder as a vault — notes, MOCs, graph, templates.
- **Claude Code** (you) runs from here — loads context at session start, writes changes back.
- **Any other agent** (Cursor, Perplexity, a generic MCP client) enters via [AGENTS.md](AGENTS.md).

Whatever Obsidian sees, you see. Whatever you write, Obsidian sees on next focus. Nothing here requires
Google Drive or a vendor-specific file bridge — read and write ordinary files; git is the sync layer.

---

## Context — load these before acting

When starting a non-trivial task, read (in this order):

1. **[06-context/role-and-context.md](06-context/role-and-context.md)** — who Sean is, his work, specializations
2. **[06-context/project-context.md](06-context/project-context.md)** — active projects + pending items (authoritative)
3. **[06-context/session-log.md](06-context/session-log.md)** — recent session entries, newest-first
4. **[06-context/artifact-registry.md](06-context/artifact-registry.md)** — structural index of known files
5. **[04-preferences/user-preferences.md](04-preferences/user-preferences.md)** — communication style, tone

The `SessionStart` hook loads these automatically. If the hook didn't fire (e.g., you were
invoked headless), read them explicitly before answering substantive questions.

---

## Session-start ritual (mandatory)

> **Cursor users:** `.cursor/rules/brain.mdc` is the Cursor-canonical override for this ritual. If both are loaded, follow `brain.mdc`. The format below is the Claude Code / Claude Desktop reference.

**Before responding to the user's first message in a new session,** output a session-start summary in exactly this format. This is non-negotiable — Sean works across surfaces (Claude Code, Cursor, VS Code, iOS app), machines (Mac, Windows, Linux), and contexts (personal, Centric employer work). A consistent visible summary is how he confirms the brain loaded correctly and re-orients regardless of where he is.

Render it as a markdown block, exactly this shape, before any other response:

```
**✓ Workspace loaded** — {Machine label} · {YYYY-MM-DD HH:MM TZ}

- **Surface:** {Claude Code (Mac desktop app) | Claude Code (Windows desktop app) | Cursor | VS Code | iOS | etc. — best inference from environment}
- **Last session:** {YYYY-MM-DD} — {one-line title from session-log.md}
- **Pending:** {N} items → see [06-context/project-context.md](06-context/project-context.md)
- **Active projects ({N}):**
  - **{folder-name}** ({last-updated date}) — {first-line title from latest SESSION-STATE.md entry}
  - ...
- **Git:** `{branch}` @ `{short-sha}`, {clean | N modified} {· worktree: {worktree-name} if applicable}

What's on the agenda today?
```

Rules:
- Pull data from the SessionStart hook's injected context (`06-context/project-context.md` head + `06-context/session-log.md` head). If a field can't be determined, omit that line rather than guess.
- Limit "Active projects" to those with `SESSION-STATE.md` files in `07-projects/*/`. List all of them, not a curated subset.
- If the session is in a worktree (branch starts with `claude/`), append `· worktree: <name>` to the Git line so Sean knows.
- Do not editorialize, do not skip the format because the user "just" asked something simple, do not summarize differently each session. The format IS the deliverable.
- If `06-context/role-and-context.md` or related context files weren't injected by the hook (e.g., headless invocation), read them via the Read tool first, THEN output the ritual.
- After the ritual block, respond to the user's message normally.
- **If the SessionStart context contains a `## Notices` section, render those notices as bulleted warnings AT THE TOP of the ritual block (above the ✓ Workspace loaded line) so they're impossible to miss.** Notices include things like Claude Code version changes since last session and stale workspace audits.

This ritual costs ~150 tokens per session start in exchange for cross-surface continuity and reliable confirmation that the brain loaded.

---

## Frameworks (the operating layer)

Eight top-level frameworks govern all project work. They sit **above** any skill.

- **[01-frameworks/01-aesthetic-lens.md](01-frameworks/01-aesthetic-lens.md)** — philosophical ground, visual/aesthetic judgment
- **[01-frameworks/02-ui-ux-operational-framework.md](01-frameworks/02-ui-ux-operational-framework.md)** — UX/UI operational decisions
- **[01-frameworks/03-collaboration-and-critique-framework.md](01-frameworks/03-collaboration-and-critique-framework.md)** — conduct, critique, handoff
- **[01-frameworks/04-research-and-evidence-framework.md](01-frameworks/04-research-and-evidence-framework.md)** — epistemology, evidence standards
- **[01-frameworks/05-last-mile-craft-framework.md](01-frameworks/05-last-mile-craft-framework.md)** — finishing discipline, augmented perception
- **[01-frameworks/06-qa-operating-model.md](01-frameworks/06-qa-operating-model.md)** — target-user QA lens, default skill loading, reference-comparison protocol, iteration-default mindset
- **[01-frameworks/07-integration-and-review-framework.md](01-frameworks/07-integration-and-review-framework.md)** — branching, PRs, merge order, reviewable diffs
- **[01-frameworks/08-workspace-contribution-framework.md](01-frameworks/08-workspace-contribution-framework.md)** — how/when/where/what/why to edit the workspace itself; routing map, memory + archive protocols

Compressed summaries: **[01-frameworks/00-README.md](01-frameworks/00-README.md)** — read this first.
Team practices: **[01-frameworks/team-practices-and-decisions.md](01-frameworks/team-practices-and-decisions.md)**.

Use `/framework-check` to run current work through all six as a critique pass.

**Always-load for QA work:** any task signalling audit, review, critique, refinement, clean-up, iteration, alignment, or last-mile finish loads framework #06 *before* doing anything else. The pre-output gate in #06 is non-negotiable.

---

## Knowledge Vault

Accumulated domain insights that outlive individual sessions: `08-knowledge/`. Distinct from
skills (operational how-to) and context (session/project state). Entries cover what was
actually learned from real work — validated patterns, working theories, research synthesis.

- **[08-knowledge/_README.md](08-knowledge/_README.md)** — conventions, entry format, when to read/write
- **[08-knowledge/_INDEX.md](08-knowledge/_INDEX.md)** — navigable index of all entries

Subdirectories: `design/`, `engineering/`, `data-science/`, `game-dev/`, `research/`, `cross-domain/`.

Claude should propose writing a knowledge entry when a session produces a durable insight.

**Before substantive domain work:** check `08-knowledge/_INDEX.md` (loaded at session start)
for a relevant entry and read it before diving in. The `UserPromptSubmit` hook surfaces a
reminder automatically when trigger words match — follow it. Don't skip this step: the entries
capture hard-won constraints and decisions that aren't in the skills or session log.

---

## Skills

Two skill systems, intentionally separate.

### `03-skills/` — the full hub/spoke network

The skill library. **You don't auto-load these** — load per the precedence algorithm in
[AGENTS.md](AGENTS.md) (route by `triggers`/`description`, then load the `load_chains` ancestors
foundation-first). The machine graph is `03-skills/skills.registry.json` (generated from frontmatter
by `09-tools/build-registry.py` — not a Drive sync). Hub skills to know about:

- **Design / DS:** `ds-advisor`, `design-engineer`, `figma-canvas-designer`, `figma-plugin-dev`
- **Legion (game):** `legion-project` → `lead-game-designer` / `lead-art-director` / `lead-game-developer`
- **Icon fonts:** `variable-icon-font-architect` + math/vector/geometry spokes
- **Visual QA:** `visual-qa-toolkit` + discipline-specific spokes
- **Workspace mgmt:** `workspace-bootstrap`

Full list: `ls 03-skills/`. Each directory has a `SKILL.md` whose frontmatter defines its graph edges.

### `.claude/skills/` — Claude Code workflow skills

Slash-command workflows native to Claude Code. Small, focused, invocable by `/name`:

- **`/today`** — daily note: yesterday's pending → today's priorities → project statuses
- **`/session-end`** — write session block, update project-context, commit, push
- **`/reconcile`** — merge session blocks from multiple machines
- **`/new-project`** — scaffold `07-projects/NN-name/` with SESSION-STATE template
- **`/framework-check`** — critique current work through the five frameworks
- **`/optimize`** — workspace audit: stale items, contradictions, drift, consolidation; logs to `06-context/audit-log.md`

---

## Projects

Active projects live in `07-projects/NN-name/`. Each carries a `SESSION-STATE.md` with the
operational state (template at [01-frameworks/_session-state-template.md](01-frameworks/_session-state-template.md)).

**Trigger words** route context automatically (handled by the `UserPromptSubmit` hook):

| Trigger | Loads |
|---|---|
| `legion`, `the game`, `bobiverse` | `03-skills/legion-project/SKILL.md` + appropriate hub |
| `centric`, `PLM`, `data table` | Design system context, Ark UI notes, cell anatomy WIP |
| `icon font`, `centricsymbols`, `variable axis` | `variable-icon-font-architect` + math spokes |
| `figma plugin`, `plugin dev` | `figma-plugin-dev` |
| `omni` | `omni-project` |

Current active projects and their status: **[06-context/project-context.md](06-context/project-context.md)**.

---

## Conventions

### File naming
- Artifacts: `context_descriptor_vN.N_YYYY-MM-DD.ext`
- Never overwrite — increment version. Minor = iterative, major = structural.
- Sessions write to `05-artifacts/active/`; archive moves to `05-artifacts/archive/`.

### Markdown + Obsidian
- Use `[[wikilinks]]` for internal connections — the graph view depends on them.
- YAML frontmatter on any note that has metadata (status, tags, date, links).
- Tags: lowercase, hyphenated (`#data-tables`, `#session-log`).
- Tasks: `- [ ]` open, `- [x]` done. Daily notes surface open tasks automatically.

### Machine labels (used in session blocks)
Resolve from `hostname` at boot. Never ask, never carry forward.

| Hostname | Label |
|---|---|
| `Voyager-2.local` | Personal MacBook Pro |
| `seansands.local` | Work MacBook Pro |
| `CS-KQ23N94M0W` | Work MacBook Pro (loaner) |
| `CS-K746DRWXY1` | Work MacBook Pro (main, going forward) |
| `Enterprise` | Windows Desktop |

### Never do
- Never delete notes — move to `_archive/` subfolders.
- Never overwrite artifacts — increment version.
- Never modify `00-bootstrap/templates/` content without asking.
- Never rename files without asking — Obsidian links will break silently.
- Never commit `05-artifacts/` or most of `07-projects/` — see `.gitignore`.
- **Never store durable content in Claude Code's local/private memory.** Externalize everything to the
  workspace at its correct layer per the [AGENTS.md](AGENTS.md) "Externalize everything" Core rule and
  the [routing map](02-shared-references/workspace-ontology.md). The local `.claude` memory holds only
  a single pointer back to the workspace — nothing else.

---

## Paths

- **Workspace root:** the directory containing `AGENTS.md` (this checkout). Resolve by walking up to
  it — no hardcoded paths, no cloud-drive mount detection.
- **Git remote:** `snds/workspace` on GitHub (the canonical portable workspace). The legacy Drive-based
  original (`claude-workspace-system`) is separate and untouched — see `06-context/memory/fact-workspace-repos.md`.

---

## Session lifecycle

1. **Start** — `SessionStart` hook loads context + the skill registry + current date. If resuming a
   project, read its `SESSION-STATE.md` **Live handoff** block to pick up where the last agent left off.
2. **Work** — use tools freely. Default to reading context files before claiming to know something.
   Keep the Live handoff block current as you go.
3. **End / handoff** — `/session-end` writes the attributed session block, updates the Live handoff block,
   commits, pushes. Hook catches stray exits.

**Multi-agent continuity:** Claude is one participant in a single unified thread — the same contract and
shared state apply to Cursor, Perplexity, other models, and a human. See
[AGENTS.md](AGENTS.md) → "Multi-agent continuity & handoff". For the full session-end protocol, see
[.claude/skills/session-end/SKILL.md](.claude/skills/session-end/SKILL.md).
