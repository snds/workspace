# GitHub Copilot

_Thin pointer. VS Code Copilot Chat and older Copilot still look here. Copilot coding agent also reads root `AGENTS.md` — this file must stay short so the pair is not a token bomb._

**Read AGENTS.md at the repository root before producing.** This is not the contract.

1. Workspace root = the directory containing `AGENTS.md`.
2. New session: emit `python3 09-tools/session-status.py --surface Copilot` first.
3. `python3 09-tools/skill-loadset.py "…"` — ordered SKILL.md paths. Do not ingest the registry.
4. Match `02-shared-references/trigger-routes.json`.
5. After producing: `python3 09-tools/close-out-dispatch.py --from-prompt "…" --run` then `03-skills/close-out/SKILL.md` / `self-improve`. SKIP ≠ verified.
6. Durable learnings go in the vault, never Copilot memory. Vendor Canvas/Artifact/HTML panels are not durable — write the vault file (or emit a copy-ready path). Never mix this vault into employer `c8/*`.
