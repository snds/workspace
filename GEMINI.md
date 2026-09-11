# Gemini adapter

_Thin pointer. Gemini CLI defaults to this filename; the contract is [AGENTS.md](AGENTS.md)._

**Read AGENTS.md before producing.** Do not treat this file as standing law.

1. Workspace root = the directory containing `AGENTS.md`.
2. New session: emit `python3 09-tools/session-status.py --surface Gemini` first.
3. `python3 09-tools/skill-loadset.py "…"` — ordered SKILL.md paths. Do not ingest the registry.
4. Match `02-shared-references/trigger-routes.json` (JSON, not the generated `.md`).
5. After producing: `python3 09-tools/close-out-dispatch.py --from-prompt "…" --run` then `03-skills/close-out/SKILL.md` / `self-improve`. SKIP ≠ verified.
6. Durable learnings go in the vault, never Gemini memory. Vendor Canvas/Artifact/HTML panels are not durable — write the vault file (or emit a copy-ready path). Never mix this vault into employer `c8/*`.

`.gemini/settings.json` also names `AGENTS.md` as the context file so Gemini CLI can load the contract directly.
