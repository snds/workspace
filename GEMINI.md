# Gemini adapter

_Thin pointer. Gemini CLI defaults to this filename; the contract is [AGENTS.md](AGENTS.md)._

**Read AGENTS.md before producing.** Do not treat this file as standing law.

1. Workspace root = the directory containing `AGENTS.md`.
2. Lookup `03-skills/skills.registry.json` → `load_chains[name]` for matching `triggers`. Do not ingest the registry.
3. Match `02-shared-references/trigger-routes.json` (JSON, not the generated `.md`).
4. After producing: `03-skills/close-out/SKILL.md` then `03-skills/self-improve/SKILL.md`.
5. Durable learnings go in the vault, never Gemini memory. Never mix this vault into employer `c8/*`.

`.gemini/settings.json` also names `AGENTS.md` as the context file so Gemini CLI can load the contract directly.
