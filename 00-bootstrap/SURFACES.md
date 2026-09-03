# Surfaces — how each tool sees the brain

_The brain (this workspace) is consumed by multiple tools simultaneously. Each surface has its own context-discovery mechanism. This doc maps what each surface reads, how to launch it against the brain, and known gaps._

_Last updated: 2026-09-02_

---

## Surface matrix

| Surface | Context discovery | AI provider | Hooks/skills | Notes |
|---|---|---|---|---|
| **Claude Code (CLI)** | Walks up parents from CWD → `CLAUDE.md` + `.claude/` | Anthropic | Full dispatcher + slash skills + SessionStart/End | Richest hook automation. Not the only surface that may mutate the vault. |
| **Claude Code (desktop, Code tab)** | Same, plus per-session worktree under `.claude/worktrees/` | Anthropic | Yes — state on worktree branch until merged | Prefer CLI for canonical continuity. |
| **Cursor** | `.cursor/rules/*.mdc` on **first** workspace folder + project/user hooks | Cursor models (Claude/GPT/Gemini/…) | `sessionStart` (user) · `preCompact`/`sessionEnd`/`subagentStop` (project) · `.cursor/agents/` | Open Brain first or use `*.code-workspace`. Adapter: [[CURSOR]]. |
| **VS Code** + Claude Code ext | Same as CLI | Anthropic | Yes | IDE UI over the CLI hooks. |
| **VS Code** + Copilot | `.github/copilot-instructions.md` | OpenAI | No | Not set up. |
| **Obsidian** | Folder = vault | n/a | n/a | Navigation, graph, daily notes. |
| **Claude Desktop** | Filesystem MCP | Anthropic | n/a | Skills via AGENTS.md + registry. |
| **Perplexity / generic MCP / human** | `llms.txt` → `AGENTS.md` → registry + trigger-routes | any | n/a | No adapter required. |
| **Claude iOS** | None | Anthropic | n/a | Paste or describe; no local FS. |

---

## Launching each surface against the brain

### Claude Code (CLI)

```bash
cd "<workspace path>"
claude
```

### Cursor — recommended for IDE + multi-model work

1. **File → Open Workspace from File…** → `00-bootstrap/workspaces/*.code-workspace` (Brain first), **or** open the workspace folder itself.
2. Confirm `.cursor/rules/brain.mdc` is active (Rules / agent context).
3. Optional: paste `00-bootstrap/dist/BEACON.md` into **Cursor Settings → Rules** (User Rules) as hook fallback; then `workspace-doctor.sh --ack-chat`.
4. MCP (Figma, Linear, …): Settings → MCP — see [[capability-registry]].

Do **not** open only `~/Projects` as the root if you need brain rules — attach the checkout first.

### VS Code / Obsidian / Claude Desktop / iOS

Unchanged from prior practice: multi-root `.code-workspace` for VS Code; Obsidian opens the vault; Desktop uses filesystem MCP; iOS is paste-only.

---

## Multi-root `.code-workspace` files

| File | Folders |
|---|---|
| `centric.code-workspace` | Brain + 02-centricPLM + 05-C8-PLM + 06-context-aware-DS + 10-centric-UX-research |
| `legion.code-workspace` | Brain + 13-legion |
| `icon-font.code-workspace` | Brain + 14-variable-icon-font-generator |
| `figma-plugins.code-workspace` | Brain + 04-claude-figma-plugin + 12-MCS + 09-figma-repo-sync-plugin |
| `system.code-workspace` | Brain + 00-obsidian |

Paths are relative to the file. Brain must stay first so Cursor loads `.cursor/rules/`.

---

## How Cursor finds the brain

1. First folder root → `.cursor/rules/*.mdc` (`brain.mdc` alwaysApply).
2. User `~/.cursor/hooks.json` `sessionStart` → `cursor-sessionstart.sh` (doctor-managed).
3. Project `.cursor/hooks.json` → compaction / session-end / subagent-stop nudges.
4. Agent follows ritual in `brain.mdc`; routes skills via [trigger-routes.md](../02-shared-references/trigger-routes.md) + registry.
5. Task tool may spawn `.cursor/agents/*` (hub load chains).

---

## Known gaps and friction

| Gap | Status / workaround |
|---|---|
| Cursor ≠ Claude slash skills | Use `.cursor/agents/` + trigger-routes + registry |
| Compaction dropping ritual | `preCompact` reassert hook (2026-07-30) |
| Parent `~/Projects` as root | Reopen workspace or move agent to Brain root |
| MCP not configured on a machine | Install per capability-registry; Open Engine Linear needs Cursor MCP |
| Worktrees (Claude desktop) | Prefer CLI for canonical session-end |
| iOS / web no FS | BEACON / paste; RULES-ONLY ritual |

---

## When to use which surface

| Task | Best surface |
|---|---|
| Workspace mutation, session-end, validators | Any capable agent (Cursor or Claude Code). Claude Code automates more of the handshake. |
| Multi-model IDE, Task/subagents, heavy editing | Cursor |
| Notes, wikilinks, graph | Obsidian |
| Isolated experimental branch | Claude desktop worktree |
| On-the-go discuss-only | Claude iOS |
| Sync | git commit + push |

---

## Per-machine notes

Git checkout is the source of truth. Cursor/VS Code user settings are per-machine; `.code-workspace` files sync via git. Machine-layer install state: [[fact-machine-layer-installs]].
