# Cursor Adapter

_The **Cursor adapter** over the universal contract in [AGENTS.md](AGENTS.md). It describes only how
Cursor executes that contract. Folder semantics, read order, skill loading, routing map, and
multi-agent handoff live in AGENTS.md — not duplicated here._

## How Cursor executes the contract

- **Canonical always-on rule:** `.cursor/rules/brain.mdc` (`alwaysApply: true`) injects the contract
  framing into every request for every model. Write gates: `.cursor/rules/01-agent-controller.mdc`.
  If both this file and `brain.mdc` are present, follow `brain.mdc` for Cursor mechanics; defer to
  [AGENTS.md](AGENTS.md) for everything else. **One home (harness-map #3):** do not paste standing law
  into User Rules beyond the thin BEACON; do not treat [CLAUDE.md](CLAUDE.md) as Cursor always-on
  (Claude adapter only — ritual + slash skills).
- **Workspace root:** open **this checkout** (the folder containing `AGENTS.md`), or a
  `00-bootstrap/workspaces/*.code-workspace` file with **Brain as the first folder**. Opening a
  parent (`~/Projects`) alone does not attach `brain.mdc` — use **move agent to workspace root** or
  reopen via the `.code-workspace` file.
- **Context:** read `06-context/` (role, **project-context stubs** only at start — detail/registry
  on demand, session-log head, `memory/MEMORY.md`)
  and `04-preferences/user-preferences.md` at session start per framework 08.
- **Skills:** Cursor has no Claude slash commands. Route via
  `python3 09-tools/skill-loadset.py "<utterance>"` (never ingest the registry or `trigger-routes.md`).
  After producing, run `python3 09-tools/close-out-dispatch.py --from-prompt "<utterance>" --run`.
  Project Task agents live in `.cursor/agents/` and encode the same load chains. When
  triggers miss, run that loadset CLI then `python3 09-tools/vault-retrieve.py "<query>"`
  or say that Layer 0 missed. Empty retrieve or a failed CLI is not "nothing in the vault."
- **Continuity:** on entry, read the active project's `SESSION-STATE.md` **Live handoff**; on
  handoff/pause/end, update it + write a `06-context/sessions/<id>.md` fragment (not a direct
  `session-log.md` append). Stamp `Agent · Surface · Machine`. On session-end also run
  `python3 09-tools/cursor-externalize.py` so Cursor canvases are copied into git-tracked
  `07-projects/…/canvases/` (employer canvases → that repo's `canvases/`, never this vault).
  Cursor still compiles only from `~/.cursor/projects/…`. The live
  `.canvas.tsx` is compile-only; the vault copy is the durable twin. Prefer a vault `md`/`html`
  when a live canvas is not required for interactivity
  ([decision-vendor-surface-artifacts](06-context/memory/decision-vendor-surface-artifacts.md)).

## Hooks (Cursor-native)

| Layer | Location | Events |
|---|---|---|
| User-global (installer) | `~/.cursor/hooks.json` ← `00-bootstrap/dist/cursor-hooks.json` | `sessionStart` |
| Project (repo) | `.cursor/hooks.json` | `subagentStop` |

Generated from `02-shared-references/surfaces.json`; see the block in `00-bootstrap/SURFACES.md`.

- **sessionStart** — injects `session-status.py` ritual card (notices + all projects + pending).
  Emit that card as the first reply. Fallback ABI: `[workspace: LOADED · … · via:cursor-hook]`.
- **subagentStop** — nudge parent to fold Task results into the baton.

Scripts: `.cursor/hooks/*.sh` (project) and `00-bootstrap/dist/cursor-*.sh` (`--install-shims`).
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
  AGENTS.md). Before commit: `python3 09-tools/nightly.py --phases rebuild`, then
  `python3 09-tools/workspace-harness.py` (chain: framework 08). Done on a write means those ran this session.
- **User Rules beacon:** paste `00-bootstrap/dist/BEACON.md` into Cursor Settings → Rules (fallback when
  hooks miss). Doctor nags until `workspace-doctor.sh --ack-chat`.
- **MCP:** configure in Cursor Settings → MCP (or `~/.cursor/mcp.json`). See
  [capability-registry.md](02-shared-references/capability-registry.md) for per-surface install.
  Linear lanes / Figma are not assumed present until configured on this machine.
- `.claude/skills/` slash commands are Claude-only; use `.cursor/agents/` + `skill-loadset.py` instead.

## Surface posture

Cursor tends **steer-heavy** (always-on `brain.mdc`, multi-model swaps, parent owns the
baton; Task agents are workers). Claude Code tends **dispatch-heavy** (hooks + slash
skills + SessionStart injection). Same model + different harness can dominate outcomes —
map posture in [[harness-map]]; see [[nate-jones-harness-enrichments]] §11.

Other adapters: [CLAUDE.md](CLAUDE.md) · [PERPLEXITY.md](PERPLEXITY.md).
