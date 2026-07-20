# Workspace Conventions

How to make changes here cleanly. The full per-layer governance is in
[01-frameworks/08-workspace-contribution-framework.md](../01-frameworks/08-workspace-contribution-framework.md);
the vocabulary + routing map is in
[02-shared-references/workspace-ontology.md](../02-shared-references/workspace-ontology.md).
This file is the quick reference.

## Commits
- Small, single-purpose, dependency-ordered. One concern per commit.
- Message: `type: short imperative summary`. Types: `feat`, `fix`, `refactor`, `docs`, `chore`,
  `skill` (skill content), `registry` (generated graph). Body explains *why* when non-obvious.
- Don't commit generated files by hand-editing them — regenerate (`skills.registry.json`).

## Branches + PRs
- Branch per change: `refactor/<topic>`, `skill/<name>`, `docs/<topic>`.
- Open a PR using the template. CI must be green: `registry-drift` + `link-validator`.

## The layer model (skills)
`foundation → hub → spoke`, with `cross-cutting` lenses (a11y, visual-qa) applied sideways.
Foundations own context-free principle; specialty spokes own applied-in-context. See
[skill-frontmatter.md](../02-shared-references/skill-frontmatter.md).

## Frontmatter (source of truth for the skill graph)
Keys: `name` (= dir name) · `description` · `aliases` · `triggers` · `tier` · `domain` · `hub` ·
`prerequisites` (hard, 0–2, transitive) · `related` (soft) · `governed_by` · `surfaces` ·
`spec_version`. After editing, run `python3 09-tools/build-registry.py`.

## Cross-links — the typed `## Related` block
Wikilinks by basename (resolved via `aliases`). Vocabulary:
`foundation · hub · spoke · applies-in · governed-by · peer · encodes-into`.
**Structural links are generated** from the frontmatter graph by `09-tools/build-related.py`
(foundation/hub/spoke/applies-in/governed-by/governs) — don't hand-edit them; edit the frontmatter
and regenerate. Hand-authored `peer ↔` lines and prose above `## Related` are preserved.
**Reciprocity is mandatory** (guaranteed by the generator) and CI-enforced. Only `foundation →`
carries load precedence; the rest are navigational.

## Hard rules
- **Never rename a `SKILL.md` file or its directory** without re-pointing every loader path and
  wikilink. Add `aliases` instead. 200+ files hardcode `03-skills/<name>/SKILL.md`.
- **Never delete.** Archive to `_archive/` with an `ARCHIVE-LOG.md` entry (reason + `superseded_by`)
  and leave a tombstone redirect where external links may exist.
- **Never hand-edit** `skills.registry.json` — it is generated from frontmatter.
- Consult the routing map before adding content; put it in the right layer the first time.

## Write-quality gates (any agent may write — these are how it stays safe)
Writing is open to any capable agent (not just Claude); correctness is enforced by validation + CI, not
model identity. Every write must clear: **(1) quality** ≥ standard (no stubs/TODOs/unfilled tokens),
**(2) intent integrity** (no data/context/intent loss), **(3) cross-link continuity** (update every
related file + regenerate + validate), **(4) no zombies** (dramatic change → archive-with-provenance +
regenerate + repoint; never leave orphaned/superseded-but-live/stub files). Full spec: `AGENTS.md` →
"Write-quality gates" and framework 08.

## Generators / validators (`09-tools/`, stdlib-only)
- `build-registry.py` — frontmatter → `skills.registry.json` (`--check` for CI drift).
- `build-related.py` — frontmatter graph → reciprocal `## Related` blocks (`--check` for CI drift).
- `validate-integrity.py` — write-quality gates: name==dir, cross-link continuity (no dangling wikilinks),
  no superseded-but-live, no unfilled scaffold/stub tokens, thin-doc smells (`--strict` to fail on warnings).
- `validate-links.py` — dangling + reciprocity on the typed `## Related` graph.
- `validate-workspace.py` — archive provenance + memory-index coverage.

Before committing any change: `build-related.py` → `build-registry.py` → `validate-integrity.py` →
`validate-links.py` → `validate-workspace.py`. CI runs all five.

`build-registry` must run **after** `build-related`: the registry stores a content hash per skill, and
`build-related` rewrites `## Related` blocks inside SKILL.md. Registry-first commits stale hashes and CI
fails on `registry-drift` / `capability-validator`.
