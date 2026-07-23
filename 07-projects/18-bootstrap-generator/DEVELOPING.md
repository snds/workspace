# Developing the Bootstrap Generator

**The developer-facing guide for people building and extending the generator.** If you are an end user who just wants the "second brain" the tool produces, read [README.md](README.md) instead — that's the friendly, non-engineer front door. This document is the engineering counterpart: how the system is wired, how to run it, and how to extend it.

> ⚠️ **Status: early, but runnable.** The design is settled (see [SPEC.md](SPEC.md), v0.2) and a first cut of the `wsx` CLI (**v0.1**) is built and passes a smoke test: `init`, `profile get`/`set`, `emit` (`claude-code` · `agents-md` · `cursor` · `pack` · `all`), `lint`, `verify`, `session`, and `sync` all run today. `resolve` is now **built** (plan-driven fetch + pin + namespace + overlay + trust gate); the `mcp` emit target is the remaining **honest stub** (it prints what it would do and exits cleanly). The interview/synthesis/resolver *brain* is now a **registered skill** (`.claude/skills/bootstrap-gen/`) that auto-triggers in Claude Code on "set up my workspace" and drives the loop by hand via `wsx` — it is not a headless automated loop (Claude narrates and gates each step). Trust the command's own `--help` and the code over this prose if they ever disagree.

---

## 1. The architecture in one paragraph

The system has a **seam down the middle**, and the seam *is* the architecture. On one side is the **brain**: judgment and narration, authored once as neutral markdown — it conducts the interview, synthesizes a profile, decides whether each capability should be pulled/adapted/generated, and reconciles overlaps. On the other side is the **hands**: a deterministic Python CLI named **`wsx`** with no model in it — it does every mechanical thing (scaffold, read/write files, fetch+pin skills, compile adapters, lint, verify, sync). The brain never touches the filesystem inline; it *calls `wsx`* for all of that. The two sides communicate through **two manifests**, which are the contract: **`profile.yaml`** (who the person is) and **`manifest.json`** (the routing index over their skills and context). Build either side against those two files and you can develop them independently.

```
        BRAIN  (judgment markdown, model-driven)
          │  writes / reads
          ▼
   ┌──────────────────────┐
   │  profile.yaml        │   ← the person
   │  manifest.json       │   ← the routing index
   └──────────────────────┘
          ▲
          │  consumes / produces
        HANDS  (wsx — deterministic Python, no model)
```

Why this split matters when you're hacking on it:

- **The brain is portable.** It's plain markdown emitted to whatever surface the user runs (a Claude skill, an `AGENTS.md` instruction file, a pasteable context pack). Improving the interview means editing markdown, not code.
- **The hands are testable.** `wsx` is pure, deterministic file work — no LLM calls — so it can have ordinary unit tests and reproducible output.
- **Neither side reaches across the seam.** If you find yourself wanting the brain to write a file directly, or `wsx` to "decide" something, stop — that's a smell. Add a `wsx` subcommand the brain can call, or move the decision into the brain's markdown.

---

## 2. Repo layout

The generator is its own tree (today it lives inside the workspace at `07-projects/18-bootstrap-generator/`; per [SPEC.md](SPEC.md) §9 it's destined to split into a standalone `wsx` repo, extractable from this folder's history). The layout **as built** (v0 consolidates related concerns into single modules; these can split as they grow):

```
generator/
  bin/wsx                 # entrypoint shim → wsxlib.cli.main (run: python3 generator/bin/wsx …)
  wsxlib/                 # THE CLI (the hands) — deterministic Python, ZERO dependencies
    __init__.py
    cli.py                # argparse dispatch (the command surface)
    core.py               # paths, profile/manifest I/O, render, git, skill iteration
    yamlio.py             # minimal zero-dep YAML for the profile.yaml subset
    scaffold.py           # `wsx init` + the embedded neutral templates (TEMPLATES dict)
    adapters.py           # all emit targets + the ADAPTERS registry
    lifecycle.py          # lint · verify · session · sync · resolve
  schemas/
    profile.schema.json   # documents profile.yaml (the seam)
    manifest.schema.json  # documents manifest.json (the seam)
  templates/README.md     # v0 embeds the neutral templates in scaffold.py; externalize here later
  profile.example.yaml    # a fictional persona showing the produced shape
  pyproject.toml          # `pip install -e generator` exposes a `wsx` entry point (optional)

brain/                    # THE BRAIN — canonical judgment markdown, ONE neutral copy
  interview.md            # M0–M5 movements + synthesize-and-confirm gate
  synthesis.md            # answers → profile.yaml (field mapping, defaults, worked example)
  resolver.md             # pull / adapt / generate + overlap reconciliation rules
  SKILL.md                # the Claude-skill adapter of the brain — runnable in Claude Code now

README.md                 # friendly, non-engineer user guide (AI-agnostic; Claude recommended)
SPEC.md                   # the design (v0.2) — source of truth for intent
DEVELOPING.md             # this file
SESSION-STATE.md          # current working state / progress log

# Not in this repo — what `wsx init` + `wsx emit` GENERATE into a *user's* workspace:
#   context/  skills/  frameworks/  manifest.json  .obsidian/  (canonical)
#   adapters/  + tool-native:  .claude/  AGENTS.md  .cursor/   (generated, never hand-edited)
```

A few placement rules to keep the seam clean:

- **`wsxlib/` holds the only Python.** The brain is never code. If logic needs a model, it belongs in `brain/`; if it's mechanical, it belongs in `wsxlib/`.
- **`templates/` is neutral.** No real identity, no "Sean," no Claude-specific assumptions — just placeholdered structure that `wsx init` stamps out. This is the descendant of the hand-built personal workspace, with the person removed. *(v0 keeps these templates embedded as strings in `scaffold.py`'s `TEMPLATES` dict for zero-file-dependency reliability; externalizing them into real files under `templates/` is a planned follow-up.)*
- **`brain/` is authored once.** One canonical markdown corpus. Each emit target *translates* it; you don't write a Claude version and a Cursor version by hand. If you're copy-pasting brain text between surfaces, you're doing it wrong — fix the emitter.
- **`adapters/` and the tool-native files are output, not source.** They're regenerated by `wsx emit`. Editing them by hand is the cardinal sin (see §5).

---

## 3. Running `wsx` locally

There's no install step and no model in the loop — `wsx` is plain Python you invoke directly:

```bash
python3 generator/bin/wsx <command> [args]
```

Examples (these all run today):

```bash
python3 generator/bin/wsx init ./my-workspace --name "Maya Okafor" --handle maya
cd ./my-workspace
python3 /path/to/generator/bin/wsx profile get                        # print parsed profile.yaml
python3 /path/to/generator/bin/wsx profile set contexts.work.role="UX researcher" \
                                               surfaces.agents='[claude, cursor]'
python3 /path/to/generator/bin/wsx emit claude-code   # compile canonical → CLAUDE.md + .claude/skills/
python3 /path/to/generator/bin/wsx emit all           # every adapter at once
python3 /path/to/generator/bin/wsx lint               # validate skills + manifest, flag trigger overlaps
python3 /path/to/generator/bin/wsx verify             # round-trip profile + dry-run every emit target
python3 /path/to/generator/bin/wsx session end        # append a Session Block to the log
```

`wsx profile set` takes **`key=value` pairs with dotted paths** (there are no bare top-level
fields — role lives at `contexts.work.role`). Lists use inline flow form: `key='[a, b]'`. After
`pip install -e generator`, the bare `wsx` entry point replaces the `python3 …/bin/wsx` prefix.

Conventions:

- **Python 3 only**, standard library first. Adding a dependency is a deliberate choice — flag it, because `wsx` needs to run on a non-engineer's machine with minimal setup.
- **Every command is deterministic.** Same inputs → byte-identical output. That's what makes emit diffs reviewable and adapters disposable.
- **Run commands from the workspace root** (the folder containing `context/`, `skills/`, `manifest.json`). `wsx init` is the exception — it creates that root.

---

## 4. What each command does

The full command surface (from [SPEC.md](SPEC.md) §6). The brain calls these; a user never types them.

| Command | Job | Status |
|---|---|---|
| `wsx init <dir>` | Scaffold a neutral workspace (embedded templates) + create the Obsidian vault + `git init` + first commit. Establishes the canonical layout and the generated-workspace `.gitignore` (private/local rules). | **built ✓** |
| `wsx profile get` \| `set` | Read or write `profile.yaml` (the brain's only door into the profile). `set` takes `key=value` dotted pairs; `get` prints the whole file or a dotted key. `schemas/profile.schema.json` documents the shape. | **built ✓** |
| `wsx resolve [--plan F] [--update] [--allow-unvetted]` | The mechanical half of the Resolver. Reads an approved `context/skill-plan.json` and, per entry: **PULL** = fetch (`http(s)`/`file`/local) → **pin** (byte-identical, `0o444` read-only) → **namespace** (`skills/pulled-<registry>-<name>/`) → register; **PULL+PATCH** = pull + scaffold an editable sibling `overlay.md` (composed into the emitted Claude-Code skill); **GENERATE** = delegate to `skill add`. Enforces the trust gate (unvetted `skills.sh`/community refused unless `audited`), pin-drift safety (changed upstream skipped until `--update`), and idempotency. The brain decides; `wsx resolve` executes. | **built ✓** |
| `wsx emit <target>` | Compile the canonical workspace (`context/` + `skills/` + `manifest.json`) into a surface-specific adapter. Targets: `claude-code` \| `agents-md` \| `cursor` \| `mcp` \| `pack` \| `all`. | **built ✓** (`mcp` **stub**) |
| `wsx lint` | Validate the canonical skills and `manifest.json` — front-matter check, and crucially **report trigger overlaps** (two skills claiming the same trigger word). Feeds the brain's overlap-reconciliation pass. | **built ✓** |
| `wsx verify` | Dry-run: round-trip `profile.yaml` through the YAML subset + confirm every emit target can gather, without running the model. The pre-ship gate. | **built ✓** |
| `wsx session start` \| `end` \| `reconcile` | Lifecycle file ops: open/close a session block, append to the log. (`reconcile` across machines is a stub.) | **built ✓** (basic) |
| `wsx sync` | Git pull --rebase + push (or note that no remote is configured). The portability backstop. | **built ✓** (basic) |
| `wsx skill add` \| `list` \| `reindex` | The mechanical hand for the Resolver's **GENERATE** path: create a skill folder + front matter and register it in `manifest.json` (`add`), list skills grouped by hub (`list`), or rebuild the manifest index from disk (`reindex`). `add` takes `--kind hub\|spoke` and writes a **sectioned skeleton** (not a flat stub) for the brain to enrich; `lint` then fails on any generated skill still carrying `_(…)_` prompts. | **built ✓** |

The split to keep straight while implementing: **`wsx` owns the filesystem, compilation, hashing, lint, verify, git, scaffold — deterministic, no model.** The **brain** owns the interview, profile synthesis, match/rank/generate judgment, overlap-reconciliation *decisions*, and narration. `lint`/`resolve` are the clearest illustration — `wsx` *detects* overlaps and *fetches* skills; the brain *resolves* them and *chooses* what to fetch.

---

## 5. How an adapter works (and how to add one)

An **adapter** is the translator for one emit target. Each one renders the *same* canonical workspace into the format a particular surface understands, and writes it to that surface's **tool-native location**. The canonical source is authored once; adapters are thin, mechanical, and disposable.

The targets:

| Target | Renders to | Tool-native location | Status |
|---|---|---|---|
| `claude-code` | `CLAUDE.md` project memory + a mirror of each skill | `CLAUDE.md`, `.claude/skills/` | built ✓ (hooks: planned) |
| `agents-md` | A single open-standard instruction file (Codex, Copilot, Gemini CLI, …) | `AGENTS.md` at root | built ✓ |
| `cursor` | Cursor rules + the shared instruction file | `.cursor/rules/`, `AGENTS.md` | built ✓ |
| `mcp` | An MCP server exposing `context.load`, `skills.search/load`, `session.*` | `adapters/mcp/` | **stub** |
| `pack` | A flattened, pasteable context pack — the tool-less fallback | `adapters/context-pack.md` | built ✓ |

**The iron rule: adapters are generated, never hand-edited.** The whole reason for the seam is that vendor formats churn — when Cursor changes its rules format or Anthropic changes the skill frontmatter, you fix *one* adapter and re-emit, rather than chasing edits across hand-written files. If you ever feel the urge to tweak a file under `.claude/` or an emitted `AGENTS.md` directly, that change belongs upstream in `brain/`, `context/`, or the adapter module — never in the output.

**The single source each adapter translates** is the canonical skill frontmatter (`name · description · triggers · domain · role · hub · source · surfaces`). `triggers` and `description` are authored once; each adapter is responsible for expressing them in its target's idiom.

### Adding a new adapter

1. **Add an `emit_<target>(root, profile, manifest)` function** in `generator/wsxlib/adapters.py`. It uses `gather(root, profile)` to load the canonical material (context notes + skills index, with personal context excluded when walled) and returns the list of files it wrote.
2. **Register the target** in the `ADAPTERS` dict at the bottom of `adapters.py` so `wsx emit <target>` dispatches to it. Targets are an explicit, closed set — don't invent commands outside the §6 surface. Call `_record(...)` so the emit is logged in `manifest.json`.
3. **Write to the tool-native location**, not into `adapters/` as inert output if the surface expects files at a specific path (e.g. `.cursor/rules/`). Keep paths a property of the adapter, not scattered through callers.
4. **Make it deterministic and idempotent.** Re-emitting must overwrite cleanly and produce identical bytes for identical input. Treat the output as throwaway.
5. **Teach `wsx verify` how to dry-run it** — a new target isn't done until `verify` can confirm it loads on its surface.
6. **Test the round-trip**, not the file contents in isolation: canonical → emit → verify.

The MCP target is special: rather than a bespoke per-product file format, it's a single MCP server (`workspace-mcp`) that lights up many surfaces at once (Cursor, Codex, local frontends). It sits at the top of the degradation ladder — **MCP/native tools → `wsx` CLI → pasteable context pack** — so a weak or offline surface always has a fallback.

---

## 6. Build order (dogfood-first)

From [SPEC.md](SPEC.md) §7. Build in this order so the tool is usable on the recommended (Claude) path as early as possible, and so each phase has something concrete to test against:

1. **Kernel + seam (Phase 0).** Templatize `context/`/`frameworks`/lifecycle into neutral placeholders. **Lock the two manifest schemas** (`profile.yaml`, `manifest.json`) and stub the `wsx` command surface *before building either side*. Ship the Obsidian-vault scaffold + gitignore rules + `git init` inside `wsx init`. The seam is fixed first; everything else builds against it.
2. **Interview → profile (Phase 1).** The brain runs M0–M5; `wsx profile set` writes `profile.yaml`; the synthesize-and-confirm gate closes the loop.
3. **Resolver (Phase 2).** Brain judgment (pull / adapt / generate) + `wsx resolve` for fetch+pin; the overlap-reconciliation pass is mandatory.
4. **Emitter (Phase 3).** `wsx emit claude-code` **first** (dogfood the recommended path), then the thin agnostic fallbacks `agents-md` / `cursor` / `pack`. SPEC §7 originally slotted `mcp` (the universal runtime) second, but in practice it's heavier, so it's **deferred to a stub** and the lightweight `AGENTS.md`/pack adapters — which already cover Cursor, Codex, Copilot, and Gemini — land first. (The status tables in §4–§5 are the honest current state; this is the reconciliation.)
5. **Verify + install docs (Phase 4).** `wsx lint` + `wsx verify` per target; per-surface/per-machine setup docs; the walled-vs-blend toggle documented.

"Dogfood-first" is the load-bearing phrase: emit the Claude adapter before the others so the team building the generator can *run their own generated workspace* and feel the rough edges immediately.

---

## 7. Standing risks (and the design's answers)

From [SPEC.md](SPEC.md) §8. These shape day-to-day engineering choices — keep them in mind when you're tempted to take a shortcut:

- **Format churn** — vendor formats (skill frontmatter, Cursor rules, `AGENTS.md` conventions) will change out from under us. **Answer: keep adapters thin and never hand-edited.** All the durable logic lives in the canonical source; adapters are disposable translators you re-emit. The cost of a vendor change should be one adapter edit, not a migration.
- **Library trust** — pulled skills come from registries of varying trust (skills.sh is real but *unvetted*; `anthropics/skills` is high-trust; community sources vary). **Answer: pin, namespace, and treat pulled skills as read-only.** Never edit a pulled skill in place; patches live in a *sibling overlay* so the upstream stays clean and re-pullable. Audit before install.
- **Privacy** — personal context must not leak into a synced/shared repo. **Answer: personal context is local-only and gitignored**; `personal.private = true` means *never synced*; encryption is offered. Walled by default, opt-in blend. When in doubt, wall it.
- **Model variance** — the same brain runs on frontier and small/local models. **Answer: capability tiering.** A frontier model gets the full on-demand skill network; a small/local model gets a pre-flattened pack of the 8–15 highest-value skills. The `pack` emit target and the degradation ladder exist precisely for this.

---

## 8. Where to look next

- **[SPEC.md](SPEC.md)** — the authoritative design (v0.2). Every section referenced here (the seam §6, build order §7, risks §8) is fuller there. When intent is unclear, the spec wins.
- **[README.md](README.md)** — the user-facing guide. Read it to understand what the person on the other end of the interview actually experiences; the brain's tone should match it.
- **[SESSION-STATE.md](SESSION-STATE.md)** — current working state, what's in progress, and what's needed to resume. Check this before starting a session.

*The build is early but real: `init`, `profile`, `emit` (`claude-code`/`agents-md`/`cursor`/`pack`/`all`), `lint`, `verify`, `session`, and `sync` run today and pass a smoke test; `resolve` is built (plan-driven fetch/pin/namespace/overlay + trust gate) and the `mcp` target is the remaining honest stub; the interview brain is a registered auto-triggering skill (`.claude/skills/bootstrap-gen/`) that drives the loop interactively, not a headless automated loop. When the code and this doc disagree, the code and its `--help` are the truth; this doc is the map.*
