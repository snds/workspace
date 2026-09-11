# GitHub Copilot

_Thin pointer. VS Code Copilot Chat and older Copilot still look here. Copilot coding agent also reads root `AGENTS.md` — this file must stay short so the pair is not a token bomb._

**Read AGENTS.md at the repository root before producing.** This is not the contract.

1. Workspace root = the directory containing `AGENTS.md`.
2. `python3 09-tools/skill-loadset.py "…"` — ordered SKILL.md paths. Do not ingest the registry.
3. Match `02-shared-references/trigger-routes.json`.
4. After producing: `python3 09-tools/close-out-dispatch.py --from-prompt "…" --run` then `03-skills/close-out/SKILL.md` / `self-improve`. SKIP ≠ verified.
5. Durable learnings go in the vault, never Copilot memory. Never mix this vault into employer `c8/*`.
