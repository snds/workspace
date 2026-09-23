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
python3 09-tools/test-validators.py TestSurfaces TestWsHook     # named classes only
python3 09-tools/test-validators.py --strict-skips TestIdentity # a skip exits 3
```

`load()` takes a 09-tools stem or a repo-relative path. Exit 2 means an unknown class name.

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
git-tracked folders. Personal canvases land in `07-projects/…/canvases/` and are
mirrored into this checkout's live Cursor folder. Employer canvases land in that
repo's `canvases/` (never this vault); mixed-parent `flavours-` / `guided-setup-`
files move into `cpes-software/saas-plm-prototype/canvases/`. Cursor still will
not compile the git copies themselves. Run on every Cursor session-end.

```
python3 09-tools/cursor-externalize.py
python3 09-tools/cursor-externalize.py --check
python3 09-tools/cursor-externalize.py --self-test
```

`--check` exits 1 on vault drift, a missing live mirror (when that Cursor slug
exists on this machine), employer-repo drift, a company canvas still in a mixed
personal slug, **or** an unmapped named project slug. Legion, ephemeral Cursor
windows, and a missing employer checkout skip and do not fail. GitHub cannot see
`~/.cursor` (A10). Do not auto-commit employer repos.

## prune-our-branches.py

Session-end git hygiene. Deletes local (and leftover remote) branches only when
`gh` shows a **merged** PR for that head authored by `@me`, there is no open PR
on the same head, and the checkout is not ahead of `origin/<branch>`. Someone
else's branches, unmerged work, and dirty leftover worktrees stay. Squash
merges are not ancestors of `main` — the merged PR is the signal, not
`merge-base`. `/session-end` runs this with `--apply`.

```
python3 09-tools/prune-our-branches.py              # dry-run
python3 09-tools/prune-our-branches.py --apply
python3 09-tools/prune-our-branches.py --self-test
```

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

Living-spec runner: status, gate, ready, worktree add, verify [--run] [--root DIR] (shlex + shell=False; automated contexts run only python3 + git-tracked 09-tools/*.py), scope-audit (task writes + @T9a, HELD, JSON selectors, unreverted auto-commits); --self-test

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

Session-start card; --family auto|claude|cursor|codex (Claude collapses centric-* projects to a count and splits the pending line); label from profile_resolve.device_label(); --self-test runs the 2ff02e7 oracle.

## check-secrets.py

Stdlib scan of git-tracked files for well-known secret shapes (PEM, AKIA, GitHub/Slack/Anthropic
keys). Does not echo values. Skip `_archive`, lockfiles, `node_modules`, `*.example`.

```
python3 09-tools/check-secrets.py
```

Secret-shape scan (exit 1 on a hit) plus --class employer-substance (H25, report-only): emp-url/emp-path/emp-slug/emp-quote as path:line rule, --baseline-check / --write-baseline ratchet, --self-test.

## artifact-find.py

C2 — query the artifact registry instead of ingesting it.
`06-context/artifact-registry.md` is **~6,942 tokens**, and the contract used to tell every
agent to read it at session start: the largest recurring item in the session floor after
AGENTS.md itself. An index is for looking things up.

| Call | Cost |
|---|---|
| reading the file (the old read-order) | 6,942 |
| `--list` (every group + entry name) | 575 |
| `--path 07-projects` | 513 |
| `artifact-find.py "lcars"` | 100 |

Same fix already applied twice: `skills.registry.json` → `skill-loadset.py`, and
`08-knowledge/_INDEX.md` → knowledge-hints plus the router parsing the index server-side.

`--check` is half the tool. A retrieval layer is only as good as the structure it reads, so
the thing that queries the file also polices its shape — drift the format and queries start
missing *silently* instead of failing loudly. It runs in CI and at session-end, right after
the step that writes to the registry.

```
python3 09-tools/artifact-find.py "session state"
python3 09-tools/artifact-find.py --path 05-artifacts
python3 09-tools/artifact-find.py --list
python3 09-tools/artifact-find.py --check
```

## nightly.py

A4 — the executable form of [[nightly-maintenance-recipe]]. **Wrapper only; nothing
schedules it.** One command instead of re-reading a markdown list and hand-sequencing eight
CLIs, which is the token cost the recipe was paying every time.

`fold` (compact-sessions) → `rebuild` (fixpoint: build-registry → build-related → build-registry,
skipped as `noop` when related wrote nothing → build-trigger-routes; MUTATING) → `verify`
(workspace-harness, read-only) → `watch` (ds-source-watch --check, advisory) → `commit`
(**opt-in**; stages exactly the paths this run wrote, refused on a red tree).

`--check` writes nothing and exits 1 on drift. `--scope all|staged|session:<id>|range:<R>` sets which
dirty paths are yours (the rest are foreign, exit 4); `--budget` and `--step-timeout` mark overrunning steps SKIPPED (exit 3);
`--json` lists written and foreign paths per step; `--lane pre-commit` judges the staged skill
sources and prints the two fix lines; `--self-test` runs the hermetic fixtures (X1 replay, timed
SessionEnd accelerator).

```
python3 09-tools/nightly.py --dry-run
python3 09-tools/nightly.py --phases rebuild      # the generator fixpoint
python3 09-tools/nightly.py --check --phases rebuild
python3 09-tools/nightly.py --commit              # + commit the written paths
python3 09-tools/nightly.py --self-test
```

## validate-evidence-grades.py

A9 — a report may not stamp `VERIFIED` without saying what verified it. Any report using the
evidence-grade vocabulary 3+ times must declare the legend and name a re-runnable detector.
`--strict` additionally requires the six pre-registration fields from
[[experiment-validity-baseline]], but only on genuinely experiment-shaped documents (two
distinct signals) — one bare "experiment" is usually a trigger word in a routing table.
`03-skills/` is exempt: it defines the vocabulary.

```
python3 09-tools/validate-evidence-grades.py
python3 09-tools/validate-evidence-grades.py --strict
```

## evaluate-surface-trajectories.py

Per-surface routing trajectories. `evaluate-skill-routing.py` proves the **matcher**
routes correctly; this proves each **surface actually delivers** it, by running the
command that surface really invokes.

| Surface | Entry point |
|---|---|
| `claude-code` | `.claude/hooks/dispatcher.py user-prompt` (stdin JSON, `CLAUDE_PROJECT_DIR`) |
| `cursor` | `09-tools/cursor-prompt-route.py` (compatibility shim; the live `beforeSubmitPrompt` registration is retired) |
| `shell-agent` | `09-tools/skill-loadset.py --json` — any agent with a shell and no hook |
| `hookless` | no executable path (web ChatGPT/Grok/Perplexity); its adapter file is asserted statically |

Per case: `expect_paths`, `forbid_paths`, `expect_header`, `expect_empty`, and **`parity`** —
the hook surfaces must deliver an identical set of workspace paths. Plus a structural
one-matcher guard: the Claude hook must delegate to `prompt_route`, never fork the tier
machinery again.

Why: on 2026-09-15, six of the 48 routing fixtures delivered a different file set on Claude
Code than on Cursor. Cursor had no Layer-1 lexical fallback; the Claude hook dropped a
knowledge hint when the same trigger already produced a curated hit. Both wrong, opposite
directions, invisible because nothing ran both. Now 0 divergences, and a gate that says so.

```
python3 09-tools/evaluate-surface-trajectories.py --check
python3 09-tools/evaluate-surface-trajectories.py --utterance "qa this screenshot"
python3 09-tools/evaluate-surface-trajectories.py --self-test
```

## workspace-harness.py

The reusable test harness: **quality · connections · tokens** in one report card.
Stdlib-only, read-only, deterministic — no clock dependence, no LLM judgment in the
pass/fail path.

- **quality** runs the documented enforcement chain as subprocesses (`--check` modes,
  so the tree is never mutated) and aggregates exit codes. Reimplements nothing.
- **connections** is what nothing else checks: do Layer-0 route paths resolve, can an
  agent actually **reach** every skill (own triggers / an ancestor in some chain / a
  named route — `related` does not count, it never auto-loads) and every knowledge
  entry (hint / `_INDEX` `Triggers:` / `trigger_words`), do hub chains ascend in order,
  do `_INDEX` wikilinks resolve the way `prompt_route.py` resolves them, do the CLIs
  the contract names exist. Skills reachable only through their hub's prose are counted
  and reported, not failed.
- **tokens** prices the traversal: contract floor → session floor → load-set p50/p95/max
  → worst-case legal request → the banned-ingest number routing exists to avoid.
  `BUDGETS` are a regression gate; raising one is a deliberate, reviewable diff.
  `ALWAYS_LOADED_BYTES_CEILING` pins the always-loaded files at their 2ff02e7 byte sizes.

`--self-test` proves each check can fail — a detector that only ever passes is decor.

```
python3 09-tools/workspace-harness.py              # all three lanes
python3 09-tools/workspace-harness.py --connections --tokens
python3 09-tools/workspace-harness.py --json --stamp
python3 09-tools/workspace-harness.py --self-test
```

## profile_resolve.py

Declared resolver (H2): device, repo, where, scan, audit, detect, agent-check, gitcaps and validate-tables over devices.json and context-remotes.json; the one home for load_table, detect_surface, normalize_remote and agent_check. --self-test runs synthetic fixtures.

## 00-bootstrap/doctor/pin_lib.py

Pinned lib under ~/.config/snds-workspace: pin/current/lag with the real-home guard; --self-test.

## 00-bootstrap/doctor/installers.py

Human-run installers behind workspace-doctor.sh --install-*/--uninstall-*: refusal on agent/no TTY, diff, y/N, .ws-bak backups, install log, byte-exact uninstall; --self-test (incl. doctor modes).

## ws_hook.py

Neutral hook core (H19): payload adapters, `host --skip-any` host filter, dedupe claims, budgeted session-start card, output dialects, redacted probes (`probe-env`, `probe-promote`) and the `--host git --floor claude` adapter. `--self-test`, `--self-test-shell`.

## 00-bootstrap/doctor/render_shims.py

Renders every hook registration file from 02-shared-references/surfaces.json (H16). `--check` covers Rule C coverage, Rule R one-registration, drift and wrapper sha; also `--write`, `--list --json`, `--install-state --json`, `--rev`, `--verify-canonical` and `--self-test`.

## fixtures/nightly/

Hermetic fixtures for nightly.py and dispatcher.py self-tests: temp vault from the real generators, X1 replay, timed SessionEnd, fake resolver modules, host-shaped payload copies.

## eslint-off-system/

Reusable ESLint rules that ban raw color literals and Tailwind arbitrary
values in product repos. Doctrine: [[llm-safe-design-system-expressiveness]]
+ [[agent-output-rails]]. Each product repo owns its config and allowlists
its token SSOTs. LCARS vendors a copy under `eslint/off-system/`.

```
# see 09-tools/eslint-off-system/README.md
```

## shadcn-lint/

Independent product-repo design-system lint service (`@shadcn/lint` + token-tier
overlay). Not vault CI. Not an extension of `eslint-off-system/`. Doctrine:
[[shadcn-lint-token-tiers]] + [[decision-shadcn-lint-independent-service]].

```
python3 09-tools/shadcn-lint/probe.py --self-test
# overlay + eslint.ds.config.mjs wiring; not vault CI
# see 09-tools/shadcn-lint/README.md
```

---

These tools assume only a git checkout + Python 3 — no Google Drive, no vendor-specific file bridge.
The retired Drive-sync monitors (`drive-audit.py`, `drive-monitor.py`) live in `_archive/`
with provenance in `_archive/ARCHIVE-LOG.md`.
