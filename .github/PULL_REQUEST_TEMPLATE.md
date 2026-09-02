<!-- See .github/CONVENTIONS.md for the full conventions. Keep diffs small and reviewable. -->

## What changed
<!-- One paragraph: what and why. -->

## Skills touched
<!-- List skill dirs and their layer. e.g. -->
<!-- - `design-foundations` (foundation, new) -->
<!-- - `uid-color-for-ui` (spoke) — extracted shared principle up to found-color -->

## Layer / structure
- [ ] New/changed frontmatter follows the v2 spec (`tier`, `hub`, `prerequisites`, `aliases`)
- [ ] `03-skills/skills.registry.json` regenerated (`python3 09-tools/build-registry.py`)
- [ ] Cross-links use the typed `## Related` block and are **reciprocal**
- [ ] No `SKILL.md` file/dir renamed (or: renames listed below + loader paths/wikilinks re-pointed)

## Routing / governance (if this adds content)
- [ ] Content placed per the routing map (skill / framework / knowledge / memory / context / preference)

## Write-quality gates (every change — any agent)
- [ ] **Quality** ≥ workspace standard — no stubs/TODOs/unfilled tokens; established structure + voice
- [ ] **Intent integrity** — no data/context/intent loss vs. the prior version (semantic; reviewer confirms)
- [ ] **Cross-link continuity** — every related/cross-linked file updated; registry + Related regenerated
- [ ] **No zombies** — nothing orphaned/superseded-but-live; dramatic changes archived + regenerated + repointed

## Archive (if anything was retired)
- [ ] `_archive/ARCHIVE-LOG.md` entry added with reason + `superseded_by`; tombstone left if linked

## Token delta
<!-- Rough +/- lines. Flag if a foundation extracted duplication out of specialty spokes. -->

## Verification
- [ ] Ran `build-related.py` → `build-registry.py` → `validate-integrity.py` → `validate-links.py` → `validate-workspace.py` (all green — registry *after* related; it hashes what related rewrites)
<!-- Plus any spot checks: a load-chain trace, Obsidian graph, etc. -->
