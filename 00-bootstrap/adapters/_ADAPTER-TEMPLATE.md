# <Tool> Adapter — template

Copy this to a root-level `<TOOL>.md` (e.g. `GEMINI.md`, `COPILOT.md`, `OLLAMA.md`) to onboard a new
agent. **An adapter is optional** — any agent that executes [AGENTS.md](../../AGENTS.md) participates at
full fidelity. The adapter only documents that tool's ergonomics and limits. It is a thin layer over the
one contract, never a separate contract.

Whitelist the new file in `.gitignore` (the root-contract block) so it's tracked.

---

# <Tool> Adapter

_The **<Tool>** adapter over the universal contract in [AGENTS.md](AGENTS.md). Describes only how <Tool>
executes that contract — folder semantics, read order, the skill loading algorithm, the routing map, and
the multi-agent handoff protocol all live in AGENTS.md and are not duplicated here._

## How <Tool> executes the contract
- **Workspace root:** the directory containing `AGENTS.md` (this checkout). No cloud-drive paths.
- **Entry:** read `llms.txt` → `AGENTS.md` → `03-skills/skills.registry.json`, then `06-context/`
  (role, project-context, session-log head, `memory/MEMORY.md`).
- **Skills:** load per the precedence algorithm in AGENTS.md — route by `triggers`/`description`, then
  read the `load_chains` ancestors (foundation → hub → spoke).
- **Continuity:** on entry, read the active project's `SESSION-STATE.md` **Live handoff** block; on
  handoff/pause/end, update it + append a `session-log` entry stamped `Agent · Surface · Machine`. This is
  what keeps a multi-agent project a single unified thread.

## <Tool>-specific mechanics
- **Auto-load mechanism:** [how this tool loads context — rule file, system prompt, plugin, manual paste]
- **Identity stamp:** Agent = `<model/tool>`, Surface = `<tool>`.
- **Capabilities / limits:** [filesystem read/write? hooks? slash commands? web? what's unavailable]
- **Writes:** go to the filesystem, committed via git; follow the routing map before writing.

Other adapters: [CLAUDE.md](CLAUDE.md) · [CURSOR.md](CURSOR.md) · [PERPLEXITY.md](PERPLEXITY.md).
