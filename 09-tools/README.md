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

## compile-cursor-rules.py

Compiles workspace context into `AGENTS.md` for non-Claude tools. `--watch` for file-watch mode.

## build-local-skill-plugin.py

Mirrors curated hubs from `03-skills/` into a local Claude Code plugin so they appear as
native `/snds:<name>` slash commands. Claude-specific ergonomics; optional.

---

These tools assume only a git checkout + Python 3 — no Google Drive, no vendor-specific file bridge.
The retired Drive-sync monitors (`drive-audit.py`, `drive-monitor.py`) live in `_archive/`
with provenance in `_archive/ARCHIVE-LOG.md`.
