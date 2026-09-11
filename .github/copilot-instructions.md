# GitHub Copilot

_Thin pointer. VS Code Copilot Chat and older Copilot still look here. Copilot coding agent also reads root `AGENTS.md` — this file must stay short so the pair is not a token bomb._

**Read AGENTS.md at the repository root before producing.** This is not the contract.

1. Workspace root = the directory containing `AGENTS.md`.
2. Lookup `03-skills/skills.registry.json` → `load_chains[name]` for matching `triggers`. Do not ingest the registry.
3. Match `02-shared-references/trigger-routes.json`.
4. After producing: `03-skills/close-out/SKILL.md` then `03-skills/self-improve/SKILL.md`.
5. Durable learnings go in the vault, never Copilot memory. Never mix this vault into employer `c8/*`.
