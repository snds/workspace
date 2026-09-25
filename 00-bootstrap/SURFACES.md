# Surfaces — how each tool sees the brain

_The brain (this workspace) is consumed by multiple tools simultaneously. Each surface has its own context-discovery mechanism. This doc maps what each surface reads, how to launch it against the brain, and known gaps._

_Last updated: 2026-09-23_

---

## Surface matrix

| Surface | Context discovery | AI provider | Hooks/skills | Notes |
|---|---|---|---|---|
| **Claude Code (CLI)** | Walks up parents from CWD → `CLAUDE.md` + `.claude/` | Anthropic | Full dispatcher + slash skills + SessionStart/End | Richest hook automation. Not the only surface that may mutate the vault. |
| **Claude Code (desktop, Code tab)** | Same, plus per-session worktree under `.claude/worktrees/` | Anthropic | Yes — state on worktree branch until merged | Prefer CLI for canonical continuity. |
| **Cursor** | `.cursor/rules/*.mdc` on **first** workspace folder + project/user hooks | Cursor models (Claude/GPT/Gemini/…) | `sessionStart` (user) · `subagentStop` (project) · `.cursor/agents/` | Open Brain first or use `*.code-workspace`. Adapter: [[CURSOR]]. |
| **VS Code** + Claude Code ext | Same as CLI | Anthropic | Yes | IDE UI over the CLI hooks. |
| **VS Code** + Copilot | `.github/copilot-instructions.md` + `AGENTS.md` | OpenAI | Hook API yes; none wired | Thin pointer → AGENTS.md. |
| **Gemini CLI** | `GEMINI.md` + `.gemini/settings.json` (`context.fileName` = `AGENTS.md`) | Google | Hook API yes; none wired | Thin pointer; settings load the contract. |
| **Warp** | `WARP.md` | Warp | No | Thin pointer → AGENTS.md. |
| **Aider** | `.aider.conf.yml` `read:` (AGENTS.md, llms.txt, CONVENTIONS.md) | any | No | Root CONVENTIONS is a pointer; PR conventions stay in `.github/CONVENTIONS.md`. |
| **Windsurf** | `.windsurf/rules/*.md` (`trigger: always_on`) + `AGENTS.md` | Cognition | Hook API yes; none wired | No `.windsurfrules`. AGENTS.md exceeds the 12,000-char rule limit, so `contract-core.md` is generated from its invariant sections. |
| **Obsidian** | Folder = vault | n/a | n/a | Navigation, graph, daily notes. |
| **Claude Desktop** | Filesystem MCP | Anthropic | n/a | Skills via AGENTS.md + `trigger-routes-digest.md`. |
| **Perplexity / generic MCP / human** | `llms.txt` → `AGENTS.md` → `skill-loadset.py` or `trigger-routes-digest.md` | any | n/a | Adapter: [[PERPLEXITY]]. |
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
3. Optional: paste `00-bootstrap/dist/cursor-user-rules.txt` into **Cursor Settings → Rules** (User Rules) as hook fallback; then `workspace-doctor.sh --ack-chat`.
4. MCP (Figma, Linear, …): Settings → MCP — see [[capability-registry]].

Do **not** open only `~/Projects` as the root if you need brain rules — attach the checkout first.

### VS Code / Obsidian / Claude Desktop / iOS

Unchanged from prior practice: multi-root `.code-workspace` for VS Code; Obsidian opens the vault; Desktop uses filesystem MCP; iOS is paste-only.

---

## Per-family beacons (H6)

Rendered by `render_shims.py` from `02-shared-references/beacons.json` (drift and size caps fail `--check`).
Installing is a human step:

| File | Goes to | How |
|---|---|---|
| `dist/BEACON.md` | claude.ai preferences, Workspace project, Perplexity Space | paste, then `--ack-chat` |
| `dist/user-CLAUDE.md` | `~/.claude/CLAUDE.md` (Claude: personal-only) | the doctor heals it from the pinned copy (`--install-pin` adopts a new one) |
| `dist/codex-AGENTS.md` | `~/.codex/AGENTS.md` (counts toward the 32 KiB Codex window) | `workspace-doctor.sh --install-shims=codex` |
| `dist/cursor-user-rules.txt` | Cursor Settings → Rules (advisory) | paste, then `--ack-chat` |
| `dist/projects-AGENTS.md` | `~/Projects/AGENTS.md` (machine-local pointer, ≤1 KiB) | `workspace-doctor.sh --install-projects-pointer` |
| `dist/RULES.txt` | standing rules the SessionStart hooks inject | none (read from the checkout) |

`workspace-doctor.sh --check` compares the installed Codex beacon and `~/Projects` pointer with dist.

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
4. Agent follows ritual in `brain.mdc`; routes skills via `python3 09-tools/skill-loadset.py "<utterance>"`.
5. Task tool may spawn `.cursor/agents/*` (hub load chains).

---

## Known gaps and friction

| Gap | Status / workaround |
|---|---|
| Cursor sessionStart was ABI-only | 2026-09-11: hook injects `session-status.py` (notices + all projects + pending) |
| Cursor ≠ Claude slash skills | Use `.cursor/agents/` + `skill-loadset.py` |
| Compaction dropping ritual | `preCompact` reassert retired 2026-09-22 (output never reached the model); the H7 `ws route` steer replaces it in wave 1 |
| Parent `~/Projects` as root | Reopen workspace or move agent to Brain root |
| MCP not configured on a machine | Install per capability-registry; Open Engine Linear needs Cursor MCP |
| Worktrees (Claude desktop) | Prefer CLI for canonical session-end |
| iOS / web no FS | BEACON / paste `00-bootstrap/adapters/web-session.md`; RULES-ONLY ritual |
| Claude injector heal pinned (H20) | Wave 1: the doctor refreshes the Claude-only injectors (hook scripts and the user CLAUDE.md) only from the pinned copy and reports a checkout that differs; nothing pinned = report only. Session-start and scheduled runs use the pinned doctor (`bin/ws-doctor`). Residual until each device re-pins (`--install-pin`) and reinstalls its scheduled job (`--install-launchd`): until then the old hook and job start the checkout's doctor, which heals only from the pin. |

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

Coverage on the minimum surfaces (scope: `shared` is held to parity on the hookable ones by `workspace-harness.py --parity`; `claude-restriction` exists to hold Claude back):

| Component | Scope | claude-code | claude-chat | cursor | codex |
|---|---|---|---|---|---|
| H1 | shared | unverified | backstop-only | unverified | unverified |
| H2 | shared | enforced-partial | advisory | unverified | unverified |
| H3 | shared | enforced | not-applicable | enforced | enforced |
| H15 | shared | enforced-partial | backstop-only | enforced-partial | enforced-when-installed |
| H16 | shared | enforced | advisory | enforced-when-installed | enforced-when-installed |
| H17 | claude-restriction | enforced-partial | backstop-only | advisory | advisory |
| H18 | shared | enforced-when-installed | backstop-only | enforced-when-installed | enforced-when-installed |
| H19 | shared | enforced-partial | not-applicable | enforced-partial | unverified |
| H20 | shared | enforced | not-applicable | advisory | advisory |
| H22 | shared | enforced-partial | backstop-only | advisory | advisory |
| H24 | shared | enforced-partial | not-applicable | enforced-partial | enforced-partial |
| H25 | shared | unverified | backstop-only | unverified | unverified |
| H23 | shared | enforced-partial | not-applicable | enforced-partial | enforced-partial |

Registrations (one effective registration per surface, event and behaviour):

| Registration | Event | Command | Host skip | Claim group |
|---|---|---|---|---|
| claude-user.session-start | session-start | ws-user-sessionstart | cursor | claude-boot |
| claude-user.env-file | session-start | ws-overlay-env-file | cursor | - |
| claude-user.user-prompt | user-prompt | ws-user-reassert | cursor | - |
| claude-user.session-end | session-end | ws-user-audit | cursor | - |
| claude-user.pre-tool | pre-tool | ws-guard-claude | cursor | - |
| claude-user.post-tool | post-tool | ws-ledger-claude | cursor | - |
| claude-user.sweep | session-start | ws-sweep-claude | cursor | - |
| claude-project.session-start | session-start | dispatcher | cursor | - |
| claude-project.pre-tool | pre-tool | dispatcher | cursor | - |
| claude-project.user-prompt | user-prompt | dispatcher | cursor | - |
| claude-project.post-tool | post-tool | dispatcher | cursor | - |
| claude-project.stop | stop | dispatcher | cursor | - |
| claude-project.session-end | session-end | dispatcher | cursor | - |
| snds-plugin.session-start | session-start | ws-user-sessionstart | cursor | claude-boot |
| cursor-user.session-start | session-start | cursor-sessionstart | - | - |
| cursor-user.pre-shell | pre-shell | ws-guard-cursor | - | - |
| cursor-user.pre-tool | pre-tool | ws-guard-cursor | - | - |
| cursor-user.pre-mcp | pre-mcp | ws-guard-cursor | - | - |
| cursor-user.post-edit | post-edit | ws-ledger-cursor | - | - |
| cursor-user.post-shell | post-shell | ws-ledger-cursor | - | - |
| cursor-user.sweep | session-start | ws-sweep-cursor | - | - |
| cursor-project.subagent-stop | subagent-stop | cursor-subagent-stop-project | - | - |
| codex-user.pre-tool | pre-tool | ws-guard-codex | - | - |
| codex-user.post-tool | post-tool | ws-ledger-codex | - | - |
| codex-user.sweep | session-start | ws-sweep-codex | - | - |
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

Rendered outputs (installers read this mapping from `render_shims.py --list --json`; the `overlay` output is the Claude overlay env file, which only `--install-claude-overlay` installs):

| Output | Path | Install mode | Installs to | Overlay |
|---|---|---|---|---|
| claude-user-fragment | `00-bootstrap/dist/settings-user-fragment.json` | claude-settings-keys | `~/.claude/settings.json` | - |
| claude-overlay-env | `00-bootstrap/dist/claude-overlay.env` | whole-file | - | v5 |
| claude-identity-inc | `00-bootstrap/dist/git/claude-identity.inc` | whole-file | - | - |
| claude-project-settings | `.claude/settings.json` | tracked | `.claude/settings.json` | - |
| cursor-user-hooks | `00-bootstrap/dist/cursor-hooks.json` | whole-file | `~/.cursor/hooks.json` | - |
| cursor-project-hooks | `.cursor/hooks.json` | tracked | `.cursor/hooks.json` | - |
| snds-plugin-hooks | `00-bootstrap/dist/plugin-hooks.json` | whole-file | `~/.claude/local-plugins/snds-local/snds/hooks/hooks.json` | - |
| codex-config-fragment | `00-bootstrap/dist/codex-config-fragment.toml` | managed-block | `~/.codex/config.toml` | - |
| cursor-sandbox-fragment | `00-bootstrap/dist/cursor-sandbox-fragment.json` | whole-file | - | - |
| codex-user-hooks | `00-bootstrap/dist/codex-hooks.json` | merge-hook-entries | `~/.codex/hooks.json` | - |
| codex-wall-rules | `00-bootstrap/dist/codex-workspace-wall.rules` | whole-file | `~/.codex/rules/workspace-wall.rules` | - |
| claude-permissions-template | `00-bootstrap/dist/claude-permissions-template.json` | whole-file | - | - |
| wall-belts | `00-bootstrap/dist/wall-belts.json` | whole-file | - | - |
| probe-claude-code | `00-bootstrap/dist/probe/claude-code.json` | merge-hook-entries | `~/.claude/settings.json` | - |
| probe-cursor | `00-bootstrap/dist/probe/cursor.json` | merge-hook-entries | `~/.cursor/hooks.json` | - |
| probe-codex | `00-bootstrap/dist/probe/codex.json` | merge-hook-entries | `~/.codex/hooks.json` | - |
| beacon-paste | `00-bootstrap/dist/BEACON.md` | whole-file | - | - |
| beacon-claude-user | `00-bootstrap/dist/user-CLAUDE.md` | whole-file | - | - |
| beacon-codex | `00-bootstrap/dist/codex-AGENTS.md` | whole-file | `~/.codex/AGENTS.md` | - |
| beacon-cursor-user-rules | `00-bootstrap/dist/cursor-user-rules.txt` | whole-file | - | - |
| beacon-projects-pointer | `00-bootstrap/dist/projects-AGENTS.md` | whole-file | - | - |
| beacon-rules | `00-bootstrap/dist/RULES.txt` | whole-file | - | - |
| windsurf-contract-core | `.windsurf/rules/contract-core.md` | tracked | - | - |
| surfaces-md-block | `00-bootstrap/SURFACES.md` | tracked | - | - |
<!-- END GENERATED: surfaces -->

---

## Per-machine notes

Git checkout is the source of truth. Cursor/VS Code user settings are per-machine; `.code-workspace` files sync via git. Machine-layer install state: [[fact-machine-layer-installs]].
