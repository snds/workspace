# Cursor Adapter

_The **Cursor adapter** over the universal contract in [AGENTS.md](AGENTS.md). It describes only how
Cursor executes that contract. The contract itself — folder semantics, read order, the skill loading
algorithm, the routing map — lives in AGENTS.md and is not duplicated here._

## How Cursor executes the contract

- **Canonical rule file:** `.cursor/rules/brain.mdc` (`alwaysApply: true`) is loaded into every Cursor
  session in this folder. It is the Cursor-canonical override for the session-start protocol. If both
  this file and `brain.mdc` are present, follow `brain.mdc` for Cursor-specific mechanics; defer to
  [AGENTS.md](AGENTS.md) for everything else.
- **Workspace root:** resolve to the directory containing `AGENTS.md` (this checkout). No cloud-drive
  mount detection.
- **Context:** read `06-context/` (role, project-context, session-log head, `memory/MEMORY.md`) and
  `04-preferences/user-preferences.md` at session start, per the portable session protocol in
  [framework 08](01-frameworks/08-workspace-contribution-framework.md).
- **Skills:** Cursor does not have Claude's slash-command skills. Load skills as documents per the
  precedence algorithm in [AGENTS.md](AGENTS.md): route by `triggers`/`description`, then read the
  `load_chains` ancestors (foundation→hub→spoke) from `03-skills/skills.registry.json`.
- **Continuity (multi-agent):** on entry, read the active project's `SESSION-STATE.md` **Live handoff**
  block to pick up exactly where the previous agent (Claude, Perplexity, a human…) left off; on
  handoff/pause/end, update it + append an attributed `session-log` entry. Cursor is one participant in a
  single unified thread — see [AGENTS.md](AGENTS.md) → "Multi-agent continuity & handoff".

## Capabilities / limits

- No `.claude/hooks` — the session-start/-end rituals are executed by reading/following the protocol,
  not by a hook. `.cursor/rules/*.mdc` provide the always-on framing (re-injected for every model).
- **Dynamic model switching:** when you swap the active model mid-task, re-anchor on your turn — re-read the
  project's Live handoff block + load the skills the task needs from the registry before acting. See
  `.cursor/rules/brain.mdc` → "Dynamic model switching" and [AGENTS.md](AGENTS.md) → "Multi-agent continuity".
- **Writing is open to any model, behind the write-quality gates** (quality ≥ standard · intent integrity ·
  cross-link continuity · no zombies). Run `build-registry.py` → `build-related.py` → `validate-integrity.py`
  → `validate-links.py` → `validate-workspace.py` before committing. See [AGENTS.md](AGENTS.md) →
  "Write-quality gates" and `.cursor/rules/01-agent-controller.mdc`.

Other adapters: [CLAUDE.md](CLAUDE.md) · [PERPLEXITY.md](PERPLEXITY.md).
