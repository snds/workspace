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

## validate-integrity.py

Write-quality + cross-link continuity: skill `name` == dir, every `[[wikilink]]` in tracked
markdown resolves, no superseded-but-live files, no unfilled scaffold tokens. Skips `_archive/`,
templates, `session-log.md`, the bootstrap-generator tree, and vendored `copilot/` (third-party
example `[[Note Name]]` syntax, not vault notes). Does **not** skip `.claude/skills/` wrappers
or anything under `03-skills/` / `08-knowledge/`.

```
python3 09-tools/validate-integrity.py            # report; exit 1 on any error
python3 09-tools/validate-integrity.py --strict   # also fail on warnings
```

## validate-workspace.py

Governance integrity: archive provenance (every `_archive/` file has an `ARCHIVE-LOG.md`
entry) and memory-index coverage (every `06-context/memory/` entry is listed in `MEMORY.md`).

```
python3 09-tools/validate-workspace.py
```

## test-validators.py

Negative fixtures for the detectors. The live-tree validators only see a healthy
checkout; a broken detector looks green forever. This harness plants small broken
trees and asserts each checker refuses them.

```
python3 09-tools/test-validators.py
```

CI: `.github/workflows/validator-fixtures.yml`. Run this after changing a
`validate-*.py` or `vault-health.py`.

## build-trigger-routes.py

Generates `02-shared-references/trigger-routes.md` from curated
`trigger-routes.json` + hub/foundation/cross-cutting triggers in the skill registry.
Claude's dispatcher loads the same JSON; Cursor and other agents read the markdown.

```
python3 09-tools/build-trigger-routes.py
python3 09-tools/build-trigger-routes.py --check
```

## evaluate-skill-routing.py

Adversarial Layer 0 harness. Replays curated utterances in
`02-shared-references/skill-routing-cases.jsonl` against the same word-boundary
match the dispatcher uses (curated routes + registry triggers + `_INDEX.md`
triggers). Lints stopword / too-short triggers. Not a daemon: run at session
start when the stamp is stale, after skill / trigger-routes / corpus edits,
from `/health` and `/optimize` surface 5, after skill authoring, and mid-session
with `--utterance` when a prompt mis-routes.

```
python3 09-tools/evaluate-skill-routing.py              # run corpus; write stamp on pass
python3 09-tools/evaluate-skill-routing.py --check      # CI / write-gate; no stamp write
python3 09-tools/evaluate-skill-routing.py --lint
python3 09-tools/evaluate-skill-routing.py --stale
python3 09-tools/evaluate-skill-routing.py --utterance "…"
```

Stamp: `07-projects/19-workspace-brain/reports/skill-routing-harness.stamp`.

## build-local-skill-plugin.py

Mirrors curated hubs from `03-skills/` into a local Claude Code plugin so they appear as
native `/snds:<name>` slash commands. Claude-specific ergonomics; optional.

## check-terminology.py

Enforces recorded word rules from `06-context/memory/feedback-*.md` (currently no active
regex rules after the 2026-07-30 vendor-term correction).

## check-unattended-runner-gate.py

Hard gate for Open Engine scheduled / headless runners (harness-map #6). Idle exit 0 unless
`UNATTENDED_RUNNER=1` or `--require`; then demands `OPEN_ENGINE_TOOLS`,
`OPEN_ENGINE_DISALLOWED_TOOLS` (Bash/Edit/Write/Agent/CronCreate), and `OPEN_ENGINE_STRICT_MCP=1`.

```
python3 09-tools/check-unattended-runner-gate.py
UNATTENDED_RUNNER=1 OPEN_ENGINE_TOOLS='…' OPEN_ENGINE_DISALLOWED_TOOLS='Bash,Edit,Write,Agent,CronCreate' \
  OPEN_ENGINE_STRICT_MCP=1 python3 09-tools/check-unattended-runner-gate.py --require
```

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

## ds-source-watch.py

Fetches the curated DS / agentic source list in `02-shared-references/ds-source-watch.json`
and diffs content hashes. Report-first: never edits ontology. `--check` is the
`/optimize` probe (no network). `--fetch` updates the snapshot under
`07-projects/19-workspace-brain/reports/ds-source-watch/`. See [[ds-source-watch]].

```
python3 09-tools/ds-source-watch.py --check
python3 09-tools/ds-source-watch.py --fetch
```

## generate-display-svg.py

Emit a live HUD / schematic SVG from a JSON display grammar. Legal primitives
only (`elbow`, `bar`, `pill`, `rect`, `sweep`, `rail`, `label`, `circle`).
Refuses raster kinds, `href`/`srcset`, and image paths. Stdlib-only. Driven
by [[gd-generation-tooling]]. Example scene:
`09-tools/fixtures/display-scene.hud-example.json`.

```
python3 09-tools/generate-display-svg.py --check 09-tools/fixtures/display-scene.hud-example.json
python3 09-tools/generate-display-svg.py --emit SCENE.json -o ARTIFACT.svg
python3 09-tools/generate-display-svg.py --self-test
python3 09-tools/generate-display-svg.py --schema
```

## cursor-externalize.py

Copies Cursor-local `.canvas.tsx` files from `~/.cursor/projects/*/canvases/` into
git-tracked `07-projects/…/canvases/`. Cursor still compiles only the live path.
Run on every Cursor session-end. `--check` exits 1 on drift.

```
python3 09-tools/cursor-externalize.py
python3 09-tools/cursor-externalize.py --check
python3 09-tools/cursor-externalize.py --self-test
```

`--check` exits 1 on vault drift **or** an unmapped named project slug. Employer
(`cpes-software`), Legion, ephemeral Cursor windows, and `flavours-` /
`guided-setup-` prefixes skip and do not fail. GitHub cannot see `~/.cursor` (A10).

## artifact-ingest.py

Land vendor Canvas/Artifact/HTML content that already exists outside git
(clipboard, a downloaded file, or `05-artifacts/inbox/`). Write-through is still
the contract — this is harvest. Secret-scan before write. HTML stays HTML.
Never copies employer paths. Does not overwrite (bumps `vN.N`).

```
python3 09-tools/artifact-ingest.py --from-clipboard --context ingest --descriptor notes
python3 09-tools/artifact-ingest.py --from-file PATH --project 19-workspace-brain
python3 09-tools/artifact-ingest.py --inbox
python3 09-tools/artifact-ingest.py --check
python3 09-tools/artifact-ingest.py --self-test
```

`--check` exits 1 when the drop-folder has pending files (session-end reports;
does not promote). Doctrine: [[decision-vendor-surface-artifacts]].

## intent-run.py

Portable kernel of Intent coordination: approval gate, ready waves, git
worktrees, checklist measures. Optional desktop app via `install-app` /
`open-app` / `doctor`. Doctrine: [[17-intent-coordination-operating-model]].

```
python3 09-tools/intent-run.py doctor
python3 09-tools/intent-run.py daemon            # live intentd status
python3 09-tools/intent-run.py daemon workspace.list
python3 09-tools/intent-run.py gate --spec docs/INTENT.md
python3 09-tools/intent-run.py ready --spec docs/INTENT.md
python3 09-tools/intent-run.py worktree add T1 --spec docs/INTENT.md
python3 09-tools/intent-run.py verify --spec docs/INTENT.md
python3 09-tools/intent-run.py verify --spec docs/INTENT.md --run
python3 09-tools/intent-run.py install-app   # optional GUI; macOS copies Intent.app
```

Measures are printed unless `--run`. Never auto-commit. Context profile on the spec still governs landing.

## skill-loadset.py

AGENTS.md `load_set` as a CLI. Utterance → matched skills, ordered `SKILL.md` paths
(foundation-first), suggestions, and the close-out command. Do not ingest the registry.

```
python3 09-tools/skill-loadset.py "dark-mode palette for this dashboard"
python3 09-tools/skill-loadset.py --json "…"
python3 09-tools/skill-loadset.py --self-test
```

Layer 0 miss injection and `CURSOR.md` / `brain.mdc` point here. `--self-test` is the CI smoke.

## close-out-dispatch.py

Named L3 for every `rigor_role: command-hub` skill. `--check` is A2 (coverage). `--run`
executes CLI detectors; SKIP classes are not verified; exit 2 is honest skip only.

```
python3 09-tools/close-out-dispatch.py --from-prompt "build this in figma" --run
python3 09-tools/close-out-dispatch.py --hub qa --run
python3 09-tools/close-out-dispatch.py --check
```

Produce-language followthrough in `prompt_route.py` names this CLI. Close-out step 2 runs it first.

## validate-layer0-schema.py

Refuse malformed `trigger-routes.json`, `knowledge-hints.json`, and routing-case JSONL.
Malformed Layer 0 currently fail-opens to `{}`. Schemas:
`02-shared-references/schemas/`.

```
python3 09-tools/validate-layer0-schema.py --check
```

## session-status.py

Portable session-start card (notices + last session + pending count + every
`07-projects/*/SESSION-STATE.md` + git). Same shape Claude Code already rendered.
Hooks inject stdout; any agent can emit it on a new session.

```
python3 09-tools/session-status.py
python3 09-tools/session-status.py --surface Cursor --via cursor-hook/startup
python3 09-tools/session-status.py --json
python3 09-tools/session-status.py --check
```

## check-secrets.py

Stdlib scan of git-tracked files for well-known secret shapes (PEM, AKIA, GitHub/Slack/Anthropic
keys). Does not echo values. Skip `_archive`, lockfiles, `node_modules`, `*.example`.

```
python3 09-tools/check-secrets.py
```

## eslint-off-system/

Reusable ESLint rules that ban raw color literals and Tailwind arbitrary
values in product repos. Doctrine: [[llm-safe-design-system-expressiveness]]
+ [[agent-output-rails]]. Each product repo owns its config and allowlists
its token SSOTs. LCARS vendors a copy under `eslint/off-system/`.

```
# see 09-tools/eslint-off-system/README.md
```

---

These tools assume only a git checkout + Python 3 — no Google Drive, no vendor-specific file bridge.
The retired Drive-sync monitors (`drive-audit.py`, `drive-monitor.py`) live in `_archive/`
with provenance in `_archive/ARCHIVE-LOG.md`.
