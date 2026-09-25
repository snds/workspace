# Review needed — 2026-09-25 /optimize batch

`03-skills/figma-api-pipeline/` held 7 loose `.md` files (no `SKILL.md`) that were older copies of the
folder skills. Each was content-reviewed (Step 4a) against its canonical `03-skills/<name>/SKILL.md`.
Six were clean duplicates/subsets and are archived in `figma-api-pipeline/` here. One was left in place.

## Left in place: `03-skills/figma-api-pipeline/figma-api-router.md`

Stale-but-useful. It is byte-identical to `_archive/03-skills-archive/duplicates_2026-04-27/figma-api-router.md`,
but the canonical `03-skills/figma-api-router/SKILL.md` has since been rewritten and no longer carries these sections:

- **File Access Patterns**: local file (`localFileKey=...`) needs the desktop MCP server; branch files use `branchKey` as `fileKey`.
- **Rate Limit Warning Signs**: 429 means switch to MCP or wait; the tier is decided by the file's plan, not the user's; Variables REST endpoints need Enterprise.
- **Code Size Limits**: REST Variables bulk has a 4MB request limit (the 50K `use_figma` and ~20KB response limits are already canonical).
- **MCP Tool Selection**: the read/write tool list (`get_design_context`, `get_metadata`, `get_variable_defs`, `get_screenshot` / `use_figma`, `search_design_system`, `create_new_file`).
- **Decision matrix rows**: "cross-file operations: MCP is one file per call" and "bulk variable operations" have no counterpart in the canonical matrix.

**Action for Sean:** check these facts against current Figma docs, merge the ones that still hold into
`03-skills/figma-api-router/SKILL.md`, then archive the loose file and the now-empty `figma-api-pipeline/` folder.
