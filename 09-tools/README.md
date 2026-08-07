# 09-tools/

Workspace utilities. Most of `09-tools/` is gitignored (vendor + per-machine tools); the
files listed here are explicitly whitelisted in `.gitignore` because they're portable,
stdlib-only, and useful on every machine.

---

## build-registry.py

Generates `03-skills/skills.registry.json` (the routing + dependency graph) from each
`SKILL.md`'s frontmatter. Single source of truth = frontmatter. Validates the graph
(no cycles, no dangling prerequisites) and precomputes `load_chains` (foundation→hub→spoke).

```
python3 09-tools/build-registry.py            # regenerate
python3 09-tools/build-registry.py --check    # CI: fail on drift or invalid graph
```

## validate-links.py

Validates the typed `## Related` wikilink graph across skills: no dangling links, typed
relations reciprocal (A `foundation→`B ⟹ B `applies-in←`A), and warns when a design/eng
spoke lacks a `foundation →` link. Only inspects the canonical typed format.

```
python3 09-tools/validate-links.py            # report; exit 1 on any error
python3 09-tools/validate-links.py --strict   # also fail on warnings
```

## validate-workspace.py

Governance integrity: archive provenance (every `_archive/` file has an `ARCHIVE-LOG.md`
entry) and memory-index coverage (every `06-context/memory/` entry is listed in `MEMORY.md`).

```
python3 09-tools/validate-workspace.py
```

## build-trigger-routes.py

Generates `02-shared-references/trigger-routes.md` from curated
`trigger-routes.json` + hub/foundation/cross-cutting triggers in the skill registry.
Claude's dispatcher loads the same JSON; Cursor and other agents read the markdown.

```
python3 09-tools/build-trigger-routes.py
python3 09-tools/build-trigger-routes.py --check
```

## build-local-skill-plugin.py

Mirrors curated hubs from `03-skills/` into a local Claude Code plugin so they appear as
native `/snds:<name>` slash commands. Claude-specific ergonomics; optional.

## check-terminology.py

Enforces recorded word rules from `06-context/memory/feedback-*.md` (currently no active
regex rules after the 2026-07-30 vendor-term correction).

## side-chat-handback.py

Helpers for [[side-chat-handback]]: `--status`, `--clip-from-inbox`, `--mark-consumed`, `--path`.
The agent authors `06-context/side-chat-inbox.md`; this script does clipboard + status flips.

```
python3 09-tools/side-chat-handback.py --status
python3 09-tools/side-chat-handback.py --clip-from-inbox
```

## vault-retrieve.py

Layer-1 lexical retrieval over the personal vault (FTS5). Complements Layer-0 trigger
routing when vocabulary misses. Indexes frameworks, shared references, skills,
preferences, memory, and knowledge. Returns ranked paths + short snippets (prefers
each note's `## For future agent` TL;DR). Optional one-hop expand via knowledge
`relations:` and skill `## Related`. Index is machine-local under
`.claude/state/vault-retrieve/` (already gitignored); rebuildable from git. Does
**not** index `07-projects/` or employer surfaces.

```
python3 09-tools/vault-retrieve.py "contracts first delivery"
python3 09-tools/vault-retrieve.py "session fragment" --limit 6
python3 09-tools/vault-retrieve.py --rebuild
python3 09-tools/vault-retrieve.py --check
python3 09-tools/vault-retrieve.py "token frugal" --json
python3 09-tools/vault-retrieve.py "…" --cached   # query only; no rebuild
python3 09-tools/vault-retrieve.py "…" --strict   # AND-only (dispatcher hot path)
python3 09-tools/vault-retrieve.py --eval         # golden set (exit 1 on FAIL)
```

Auto-rebuilds when the corpus fingerprint drifts (unless `--cached`). Stdlib-only (sqlite3 FTS5).
Stopwords + `--strict` keep procedural chatter from OR-matching noise.

Claude Code: SessionStart runs `--rebuild --quiet`; UserPromptSubmit uses
`--cached` (stopwords + OR min-overlap; no graph expand) when Layer 0 yields
fewer than 2 unique targets (cap 2). Cursor and other surfaces call the CLI on demand.

## vault-health.py

Epistemic-graph hygiene: stale claims, dangling `relations:` edges, orphan notes.
See the module docstring; pairs with [[vault-graph-conventions]].
---

These tools assume only a git checkout + Python 3 — no Google Drive, no vendor-specific file bridge.
The retired Drive-sync monitors (`drive-audit.py`, `drive-monitor.py`) live in `_archive/`
with provenance in `_archive/ARCHIVE-LOG.md`.
