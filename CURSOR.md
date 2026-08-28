# Cursor Adapter

_The **Cursor adapter** over the universal contract in [AGENTS.md](AGENTS.md). It describes only how
Cursor executes that contract. Folder semantics, read order, skill loading, routing map, and
multi-agent handoff live in AGENTS.md — not duplicated here._

## How Cursor executes the contract

- **Canonical always-on rule:** `.cursor/rules/brain.mdc` (`alwaysApply: true`) injects the contract
  framing into every request for every model. Write gates: `.cursor/rules/01-agent-controller.mdc`.
  If both this file and `brain.mdc` are present, follow `brain.mdc` for Cursor mechanics; defer to
  [AGENTS.md](AGENTS.md) for everything else.
- **Workspace root:** open **this checkout** (the folder containing `AGENTS.md`), or a
  `00-bootstrap/workspaces/*.code-workspace` file with **Brain as the first folder**. Opening a
  parent (`~/Projects`) alone does not attach `brain.mdc` — use **move agent to workspace root** or
  reopen via the `.code-workspace` file.
- **Context:** read `06-context/` (role, project-context head, session-log head, `memory/MEMORY.md`)
  and `04-preferences/user-preferences.md` at session start per framework 08.
- **Skills:** Cursor has no Claude slash commands. Route via
  [trigger-routes.md](02-shared-references/trigger-routes.md) (curated) then
  `03-skills/skills.registry.json` (`load_chains`, foundation→hub→spoke). Project Task agents live in
  `.cursor/agents/` and encode the same load chains. When triggers miss, run
  `python3 09-tools/vault-retrieve.py "<query>"` or say that Layer 0 missed.
  Empty retrieve or a failed CLI is not "nothing in the vault."
- **Continuity:** on entry, read the active project's `SESSION-STATE.md` **Live handoff**; on
  handoff/pause/end, update it + write a `06-context/sessions/<id>.md` fragment (not a direct
  `session-log.md` append). Stamp `Agent · Surface · Machine`.

## Hooks (Cursor-native)

| Layer | Location | Events |
|---|---|---|
| User-global (doctor-managed) | `~/.cursor/hooks.json` ← `00-bootstrap/dist/cursor-hooks.json` | `sessionStart` (+ mirrors of project events when installed) |
| Project (repo) | `.cursor/hooks.json` | `preCompact`, `sessionEnd`, `subagentStop` |

- **sessionStart** — injects root + ritual ABI `[workspace: LOADED · … · via:cursor-hook]`.
- **preCompact** — re-anchor reminder (compaction survival; Claude's prompt-reassert analogue).
- **sessionEnd** — nudge Live handoff + session fragment.
- **subagentStop** — nudge parent to fold Task results into the baton.

Scripts: `.cursor/hooks/*.sh` (project) and `00-bootstrap/dist/cursor-*.sh` (installed by doctor).
Fail-open. Structured-output / subagent turns skip the ritual line (see BEACON exemption).

## Dynamic model switching + parallel agents

- **Model swap mid-task:** no session boundary. `alwaysApply` re-injects rules; **re-anchor** — re-read
  Live handoff + load skills for the task before acting. Chat history is shared; workspace state is not.
- **Parallel Task / subagents:** write **session fragments** only; one agent owns Live handoff updates
  at a time. Do not race-append `session-log.md`. Prefer `.cursor/agents/*` so workers load the skill graph.
- **Employer repos:** resolve context profile first — `centric-engineering` = branch → PR → human review;
  never auto-commit/push from a Cursor agent.

## Capabilities / limits

- Writes are open to any model behind the write-quality gates (see `01-agent-controller.mdc` /
  AGENTS.md). Before commit: `build-related.py` → `build-registry.py` → `build-trigger-routes.py` →
  validators (integrity → links → workspace). Done on a write means those
  validators ran this session. Negative fixtures: `python3 09-tools/test-validators.py`.
- **User Rules beacon:** paste `00-bootstrap/dist/BEACON.md` into Cursor Settings → Rules (fallback when
  hooks miss). Doctor nags until `workspace-doctor.sh --ack-chat`.
- **MCP:** configure in Cursor Settings → MCP (or `~/.cursor/mcp.json`). See
  [capability-registry.md](02-shared-references/capability-registry.md) for per-surface install.
  Linear lanes / Figma are not assumed present until configured on this machine.
- `.claude/skills/` slash commands are Claude-only; use `.cursor/agents/` + registry instead.

Other adapters: [CLAUDE.md](CLAUDE.md) · [PERPLEXITY.md](PERPLEXITY.md).
