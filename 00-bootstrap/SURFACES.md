# Surfaces — how each tool sees the brain

_The brain (this workspace) is consumed by multiple tools simultaneously. Each surface has its own context-discovery mechanism. This doc maps what each surface reads, how to launch it against the brain, and known gaps._

_Last updated: 2026-09-22_

---

## Surface matrix

| Surface | Context discovery | AI provider | Hooks/skills | Notes |
|---|---|---|---|---|
| **Claude Code (CLI)** | Walks up parents from CWD → `CLAUDE.md` + `.claude/` | Anthropic | Full dispatcher + slash skills + SessionStart/End | Richest hook automation. Not the only surface that may mutate the vault. |
| **Claude Code (desktop, Code tab)** | Same, plus per-session worktree under `.claude/worktrees/` | Anthropic | Yes — state on worktree branch until merged | Prefer CLI for canonical continuity. |
| **Cursor** | `.cursor/rules/*.mdc` on **first** workspace folder + project/user hooks | Cursor models (Claude/GPT/Gemini/…) | `sessionStart` (user) · `subagentStop` (project) · `.cursor/agents/` | Open Brain first or use `*.code-workspace`. Adapter: [[CURSOR]]. |
| **VS Code** + Claude Code ext | Same as CLI | Anthropic | Yes | IDE UI over the CLI hooks. |
| **VS Code** + Copilot | `.github/copilot-instructions.md` + `AGENTS.md` | OpenAI | No | Thin pointer → AGENTS.md. |
| **Gemini CLI** | `GEMINI.md` + `.gemini/settings.json` (`context.fileName` = `AGENTS.md`) | Google | No | Thin pointer; settings load the contract. |
| **Warp** | `WARP.md` | Warp | No | Thin pointer → AGENTS.md. |
| **Aider** | `CONVENTIONS.md` + `.aider.conf.yml` `read:` | any | No | Root CONVENTIONS is a pointer; PR conventions stay in `.github/CONVENTIONS.md`. |
| **Windsurf** | `.windsurf/rules/workspace.md` | Cognition | No | No `.windsurfrules` (first-match can hide AGENTS.md). |
| **Obsidian** | Folder = vault | n/a | n/a | Navigation, graph, daily notes. |
| **Claude Desktop** | Filesystem MCP | Anthropic | n/a | Skills via AGENTS.md + registry. |
| **Perplexity / generic MCP / human** | `llms.txt` → `AGENTS.md` → registry + trigger-routes | any | n/a | Adapter: [[PERPLEXITY]]. |
| **ChatGPT / Grok.com / Perplexity (no FS)** | none | various | n/a | Paste [web-session.md](adapters/web-session.md) + `dist/BEACON.md`. |
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
2. User `~/.cursor/hooks.json` `sessionStart` → `cursor-sessionstart.sh` injects `session-status.py` (doctor-managed).
3. Project `.cursor/hooks.json` → subagent-stop nudge. The preCompact, sessionEnd and beforeSubmitPrompt shims were retired on 2026-09-22 (their output never reached the model).
4. Agent follows ritual in `brain.mdc`; routes skills via [trigger-routes.md](../02-shared-references/trigger-routes.md) + registry.
5. Task tool may spawn `.cursor/agents/*` (hub load chains).

---

## Known gaps and friction

| Gap | Status / workaround |
|---|---|
| Cursor sessionStart was ABI-only | 2026-09-11: hook injects `session-status.py` (notices + all projects + pending) |
| Cursor ≠ Claude slash skills | Use `.cursor/agents/` + trigger-routes + registry |
| Compaction dropping ritual | `preCompact` reassert retired 2026-09-22 (output never reached the model); the H7 `ws route` steer replaces it in wave 1 |
| Parent `~/Projects` as root | Reopen workspace or move agent to Brain root |
| MCP not configured on a machine | Install per capability-registry; Open Engine Linear needs Cursor MCP |
| Worktrees (Claude desktop) | Prefer CLI for canonical session-end |
| iOS / web no FS | BEACON / paste `00-bootstrap/adapters/web-session.md`; RULES-ONLY ritual |

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

## Surface registry (generated)

The declared surface table is `02-shared-references/surfaces.json` (H16). Every hook registration file is rendered from it by `00-bootstrap/doctor/render_shims.py`, and `render_shims.py --check` fails on drift.

<!-- BEGIN GENERATED: surfaces -->
_Generated by `00-bootstrap/doctor/render_shims.py` from `02-shared-references/surfaces.json`; run `render_shims.py --write` after editing the table. Do not edit this block by hand._

| Surface | Family | Kind | Hookable | Dialect | Required |
|---|---|---|---|---|---|
| claude-code | claude | cli-agent | yes | claude | yes |
| claude-code-cloud | claude | cloud-agent | yes | claude | no |
| claude-chat | claude | chat | no | none | yes |
| claude-chat-desktop | claude | desktop-app | no | none | no |
| claude-in-chrome | claude | browser | no | none | no |
| cursor | cursor | ide-agent | yes | cursor | yes |
| cursor-cli | cursor | cli-agent | yes | cursor | no |
| cursor-cloud | cursor | cloud-agent | yes | cursor | no |
| codex | codex | desktop-app | yes | codex | yes |
| codex-cloud | codex | cloud-agent | no | none | no |
| gemini-cli | gemini | cli-agent | yes | none | no |
| copilot-vscode | copilot | ide-agent | yes | claude | no |
| copilot-cli | copilot | cli-agent | yes | none | no |
| copilot-cloud-agent | copilot | cloud-agent | no | none | no |
| windsurf | unknown-agent | ide-agent | yes | none | no |
| aider | unknown-agent | cli-agent | no | none | no |
| warp | unknown-agent | cli-agent | no | none | no |
| other-local-agents | unknown-agent | cli-agent | yes | none | no |
| grok-build | unknown-agent | cli-agent | yes | none | no |
| web-chat | unknown-agent | chat | no | none | no |
| mcp-clients | unknown-agent | mcp-client | no | none | no |
| human | human | human | no | none | no |

Coverage on the minimum surfaces:

| Component | claude-code | claude-chat | cursor | codex |
|---|---|---|---|---|
| H1 | unverified | backstop-only | unverified | unverified |
| H2 | unverified | advisory | unverified | unverified |
| H3 | enforced | not-applicable | enforced | enforced |
| H16 | enforced | advisory | enforced-when-installed | enforced-when-installed |
| H17 | unverified | backstop-only | unverified | unverified |
| H19 | unverified | not-applicable | unverified | unverified |
| H22 | unverified | backstop-only | advisory | advisory |
| H24 | unverified | not-applicable | unverified | unverified |
| H25 | unverified | backstop-only | unverified | unverified |

Registrations (one effective registration per surface, event and behaviour):

| Registration | Event | Command | Host skip | Claim group |
|---|---|---|---|---|
| claude-user.session-start | session-start | ws-user-sessionstart | cursor | claude-boot |
| claude-user.user-prompt | user-prompt | ws-user-reassert | cursor | - |
| claude-user.session-end | session-end | ws-user-audit | cursor | - |
| claude-project.session-start | session-start | dispatcher | cursor | - |
| claude-project.pre-tool | pre-tool | dispatcher | cursor | - |
| claude-project.user-prompt | user-prompt | dispatcher | cursor | - |
| claude-project.post-tool | post-tool | dispatcher | cursor | - |
| claude-project.stop | stop | dispatcher | cursor | - |
| claude-project.session-end | session-end | dispatcher | cursor | - |
| snds-plugin.session-start | session-start | ws-user-sessionstart | cursor | claude-boot |
| cursor-user.session-start | session-start | cursor-sessionstart | - | - |
| cursor-project.subagent-stop | subagent-stop | cursor-subagent-stop-project | - | - |
| probe-claude-user.session-start | session-start | ws-hook-probe | - | ws-probe |
| probe-claude-user.user-prompt | user-prompt | ws-hook-probe | - | ws-probe |
| probe-claude-user.stop | stop | ws-hook-probe | - | ws-probe |
| probe-claude-user.session-end | session-end | ws-hook-probe | - | ws-probe |
| probe-cursor-user.session-start | session-start | ws-hook-probe | - | ws-probe |
| probe-cursor-user.user-prompt | user-prompt | ws-hook-probe | - | ws-probe |
| probe-cursor-user.pre-compact | pre-compact | ws-hook-probe | - | ws-probe |
| probe-cursor-user.session-end | session-end | ws-hook-probe | - | ws-probe |
| probe-cursor-user.subagent-stop | subagent-stop | ws-hook-probe | - | ws-probe |
| probe-codex-user.session-start | session-start | ws-hook-probe | - | ws-probe |
| probe-codex-user.user-prompt | user-prompt | ws-hook-probe | - | ws-probe |
| probe-codex-user.stop | stop | ws-hook-probe | - | ws-probe |
<!-- END GENERATED: surfaces -->

---

## Per-machine notes

Git checkout is the source of truth. Cursor/VS Code user settings are per-machine; `.code-workspace` files sync via git. Machine-layer install state: [[fact-machine-layer-installs]].
