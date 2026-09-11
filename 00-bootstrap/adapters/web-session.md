# Web LLM session pack (ChatGPT, Grok.com, Perplexity Space)

No coding agent on the web auto-discovers repo files. Paste this as **custom instructions**
or the first message of a Project/Space, then attach or fetch `AGENTS.md` if the surface
can read files. This is not a second contract.

**Read AGENTS.md before producing** (GitHub: `snds/workspace`, or the local checkout).
If you cannot fetch files, say `[workspace: RULES-ONLY · via:<surface>]` and still follow
the standing rules below. Do not invent workspace doctrine from training data.

1. Workspace root = the directory containing `AGENTS.md`.
2. Lookup `03-skills/skills.registry.json` → `load_chains[name]` for matching `triggers`. Do not ingest the registry.
3. Match `02-shared-references/trigger-routes.json`.
4. After producing: `03-skills/close-out/SKILL.md` then `03-skills/self-improve/SKILL.md`.
5. Durable learnings go in the vault, never this chat's memory. Never mix this vault into employer `c8/*`.
6. Figma work uses real library components, never hand-built shapes.

Also paste `00-bootstrap/dist/BEACON.md` into user rules when the surface has them.
Other adapters: `CLAUDE.md` · `CURSOR.md` · `GEMINI.md` · `PERPLEXITY.md` · `WARP.md`.
