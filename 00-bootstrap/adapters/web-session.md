# Web LLM session pack (ChatGPT, Grok.com, Perplexity Space)

No coding agent on the web auto-discovers repo files. Paste this as **custom instructions**
or the first message of a Project/Space, then attach or fetch `AGENTS.md` if the surface
can read files. This is not a second contract.

**Read AGENTS.md before producing** (GitHub: `snds/workspace`, or the local checkout).
If you cannot fetch files, say `[workspace: RULES-ONLY · via:<surface>]` and still follow
the standing rules below. Do not invent workspace doctrine from training data.

1. Workspace root = the directory containing `AGENTS.md`.
2. New session: emit `python3 09-tools/session-status.py --surface web` first if you can run it; otherwise list pending + Live handoff from pasted files.
3. `python3 09-tools/skill-loadset.py "…"` — ordered SKILL.md paths. Do not ingest the registry.
4. Match `02-shared-references/trigger-routes.json`.
5. After producing: `python3 09-tools/close-out-dispatch.py --from-prompt "…" --run` then `03-skills/close-out/SKILL.md` / `self-improve`. SKIP ≠ verified.
6. Durable learnings go in the vault, never this chat's memory. Never mix this vault into employer `c8/*`.
7. Figma work uses real library components, never hand-built shapes.
8. Do not treat Canvas/Artifact/HTML-preview panels as durable. Emit a copy-ready fenced block plus a suggested vault path (`context_descriptor_vN.N_YYYY-MM-DD.ext` under `05-artifacts/` or the owning `07-projects/NN-*/`).

Also paste `00-bootstrap/dist/BEACON.md` into user rules when the surface has them.
Other adapters: `CLAUDE.md` · `CURSOR.md` · `GEMINI.md` · `PERPLEXITY.md` · `WARP.md`.
