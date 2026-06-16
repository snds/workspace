# Surfaces — how each tool sees the brain

_The brain (this workspace) is consumed by multiple tools simultaneously. Each surface has its own context-discovery mechanism. This doc maps what each surface reads, how to launch it against the brain, and the known gaps._

_Last updated: 2026-04-27_

---

## Surface matrix

| Surface | Context discovery | AI provider | Hooks/skills | Notes |
|---|---|---|---|---|
| **Claude Code (CLI)** | Walks up parents from CWD → finds `CLAUDE.md` + `.claude/` | Anthropic (you) | Yes — full dispatcher + 5 slash commands | Cleanest brain integration. Recommended for workspace work. |
| **Claude Code (desktop app, Code tab)** | Same as CLI, but auto-creates a per-session worktree at `<project>/.claude/worktrees/<random>` on a `claude/<random>` branch | Anthropic | Yes — but state lives on worktree branch until merged | Worktrees are mandatory in the desktop app, not configurable. Useful for experimental safety; awkward for cross-surface continuity. |
| **Cursor** | `.cursor/rules/*.mdc` at the FIRST workspace folder root | Cursor's AI (typically Claude or GPT) | No (Cursor doesn't read `.claude/hooks/`) | Brain rule lives at [`/.cursor/rules/brain.mdc`](../.cursor/rules/brain.mdc). Cursor's AI auto-loads it whenever Brain is the first folder in the workspace. |
| **VS Code** + Claude Code extension | Same as CLI — walks up to find `CLAUDE.md` | Anthropic | Yes (extension respects hooks) | Use this if you prefer VS Code's UI to the desktop app. Worktree behavior depends on extension settings. |
| **VS Code** + Copilot | `.github/copilot-instructions.md` per repo root | OpenAI | No | Not currently set up. Mirror would live at workspace root if needed. |
| **Obsidian** | Folder = vault; reads everything | n/a (no AI) | n/a | UI for navigation, editing, graph view, daily notes. Plugins: Dataview, Templater, Git, Excalidraw, etc. |
| **Claude Desktop** (chat app) | Reads workspace files via whatever filesystem MCP is configured | Anthropic | n/a (no hook system in chat) | Skills load per the precedence algorithm in `AGENTS.md` against `03-skills/skills.registry.json`. |
| **Perplexity / generic MCP / a human** | Reads `llms.txt` → `AGENTS.md` → registry | any | n/a | No adapter required — follows the universal contract directly. |
| **Claude iOS app** | None — no local filesystem access | Anthropic | n/a | Brain context only available if you paste/reference it explicitly. Use for chat continuity, not file operations. |

---

## Launching each surface against the brain

### Claude Code (CLI) — recommended for workspace work

```bash
cd "<workspace path>"     # or any subfolder of the workspace
claude
```

Hooks fire automatically. CLAUDE.md auto-loads. No worktree.

### Claude Code (desktop app)

Open the desktop app → Code tab → New session → pick the workspace folder. Worktree is created automatically; you'll see `claude/<random>` branch. Your changes live on that branch until the worktree's session-end hook merges (or doesn't, if a manual merge is needed).

### Cursor — recommended for IDE work

1. Open Cursor
2. **File → Open Workspace from File…** — pick one of the `00-bootstrap/workspaces/*.code-workspace` files
3. The Brain folder is the first root → Cursor reads `.cursor/rules/brain.mdc` automatically
4. Cursor's AI now has brain context for any chat in this workspace

### VS Code — same multi-root workspace approach

1. Open VS Code
2. **File → Open Workspace from File…** — pick one of the `00-bootstrap/workspaces/*.code-workspace` files
3. Open a terminal in any folder; `claude` finds `CLAUDE.md` by walking up

### Obsidian

Already configured. Open the app → vault is `Claude Workspace`. Just use it.

### Claude Desktop

Open the chat app. The `workspace-bootstrap` skill loads context via whatever filesystem MCP is configured when triggered. Phrases like "continuing", "I'm back", "let's get started" trigger the bootstrap.

### Claude iOS

No filesystem access. If you need brain context in an iOS chat, paste relevant snippets manually, or describe the situation and let Claude pull from training/web search.

---

## Multi-root `.code-workspace` files

The bridge between the brain's "many folders" reality and IDEs' "one folder is a project" mental model is the **multi-root workspace file** — a JSON file that lists multiple folders to be loaded as a single editor window.

Five starter workspace files live in [`00-bootstrap/workspaces/`](workspaces/):

| File | Folders |
|---|---|
| `centric.code-workspace` | Brain + 02-centricPLM + 05-C8-PLM + 06-context-aware-DS + 10-centric-UX-research |
| `legion.code-workspace` | Brain + 13-legion |
| `icon-font.code-workspace` | Brain + 14-variable-icon-font-generator |
| `figma-plugins.code-workspace` | Brain + 04-claude-figma-plugin + 12-MCS + 09-figmaCLI-test |
| `system.code-workspace` | Brain + 00-obsidian (for working on the brain itself) |

Paths inside these files are **relative** (`../..` etc.) so they work on Windows + Mac + Linux unchanged.

To create a new context: copy one of the existing files, change the folder list and the `files.exclude` block to match. Save with a descriptive name. Open via **File → Open Workspace from File…**.

Recently-opened workspaces appear in **File → Open Recent**, which is the fastest way to switch contexts.

---

## How the AI on each surface finds the brain

### When Claude Code starts (CLI or extension or desktop app)

1. Reads `.claude/settings.json` from the project root (walking up from CWD)
2. Fires `SessionStart` hook → `dispatcher.py session-start`
3. Hook injects `06-context/*` heads + structured summary as `additionalContext`
4. Reads `CLAUDE.md` from the project root
5. Renders the mandatory session-start ritual (defined in CLAUDE.md)

### When Cursor starts

1. Reads `.cursor/rules/*.mdc` from the first workspace folder
2. `brain.mdc` (`alwaysApply: true`) is loaded into every chat in this workspace
3. AI has brain context for everything, even in chats started from a sub-folder

### When VS Code (with Claude Code extension) starts

Same as Claude Code CLI — the extension is the CLI in IDE clothing.

### When Obsidian opens the vault

Filesystem reads only. No AI involved. Plugins handle the smarts (Dataview queries, Templater, Git auto-sync).

---

## Known gaps and friction

| Gap | Workaround |
|---|---|
| Cursor's AI doesn't run `.claude/hooks/` | The `brain.mdc` rule covers most of what hooks would inject. SessionStart context (last session, pending count, project states) isn't auto-rendered in Cursor — you'd need to ask Claude to summarize. Acceptable for now. |
| Worktrees in the Claude Code desktop app create per-session branches that live until merged | Use the CLI (`claude` from a terminal) for canonical work; reserve the desktop app's Code tab for genuinely experimental sessions where branch isolation is desirable. |
| Switching between contexts (Centric → Legion → Icon font) means switching workspace files | One click in **File → Open Recent**. Each workspace remembers its open files separately. |
| iOS / web Claude has no filesystem access | Brain context must be pasted or described. For long-running threads on iOS, summarize the relevant brain content into the chat once and Claude will reference it from context window. |
| GitHub Copilot in VS Code doesn't read `CLAUDE.md` | Mirror to `.github/copilot-instructions.md` if you start using Copilot heavily. Not currently set up. |
| Cursor rules cascade requires Brain to be the first folder root | All starter workspace files put Brain first. If you create your own, follow the same convention. |

---

## Per-machine notes

The workspace is a plain git checkout — clone it anywhere; no per-machine mount or `.git` relocation is
needed. (The legacy Drive-based original required moving `.git` off Drive; that workaround is obsolete here.)

Cursor and VS Code store user-level settings outside the workspace, so font, theme, etc. are per-machine.
The `.code-workspace` files only carry workspace-scoped settings (folders + `files.exclude`); they're the
same on every machine via git.

---

## When to use which surface

Rough heuristic — adjust based on the work:

| Task | Best surface |
|---|---|
| Quick chat about a problem; reading session log; updating context | Claude Code CLI |
| Writing notes, navigating wikilinks, daily notes, graph view | Obsidian |
| Heavy code editing with intellisense + AI completion | Cursor (or VS Code with extension) |
| Experimental refactor in isolation | Claude Code desktop app (worktree mode is a feature here, not a bug) |
| Quick file lookups + reads from anywhere on the machine | Claude Desktop (filesystem MCP) |
| Continuing a thought thread on the go (read/discuss only) | Claude iOS app |
| Cross-machine sync | git — commit + push; pull on the other machine |
