<!-- See .github/CONVENTIONS.md for the full conventions. Keep diffs small and reviewable. -->

## What changed
<!-- One paragraph: what and why. -->

## Skills touched
<!-- List skill dirs and their layer. e.g. -->
<!-- - `design-foundations` (foundation, new) -->
<!-- - `uid-color-for-ui` (spoke) — extracted shared principle up to found-color -->

## Layer / structure
- [ ] New/changed frontmatter follows the v2 spec (`tier`, `hub`, `prerequisites`, `aliases`)
- [ ] `02-skills/skills.registry.json` regenerated (`python3 09-tools/build-registry.py`)
- [ ] Cross-links use the typed `## Related` block and are **reciprocal**
- [ ] No `SKILL.md` file/dir renamed (or: renames listed below + loader paths/wikilinks re-pointed)

## Routing / governance (if this adds content)
- [ ] Content placed per the routing map (skill / framework / knowledge / memory / context / preference)

## Archive (if anything was retired)
- [ ] `_archive/ARCHIVE-LOG.md` entry added with reason + `superseded_by`; tombstone left if linked

## Token delta
<!-- Rough +/- lines. Flag if a foundation extracted duplication out of specialty spokes. -->

## Verification
<!-- What you ran: build-registry.py, validate-links.py, a load-chain spot check, Obsidian graph, etc. -->
