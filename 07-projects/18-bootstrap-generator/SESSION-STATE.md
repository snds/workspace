# SESSION-STATE — Portable Bootstrap Generator

_Last updated: 2026-07-22 19:40 — checkpoint (two-track sourcing: composite skills cite distilled industry-leading references + `wsx search` discovery; earlier this session: emit mcp, Resolver Phase 2, turn-key Path A)_

---

## Current state (rewritten atomically — no stale fields)

### Environment
- **Context profile**: `personal-solo` — personal git-native tooling, snds repos (00-context-profiles.md Examples row: this workspace family).
- **Machine**: `Voyager-2.local` (Personal MacBook Pro)
- **OS context**: macOS (Darwin 25.5.0)
- **Workspace root**: the workspace checkout (the dir containing `AGENTS.md`) — resolve by walking up; no hardcoded path
- **Project root**: `<workspace-root>/07-projects/18-bootstrap-generator`

### Active servers and processes
- **Dev server**: not running
- **Build process**: not running
- **Test runner**: manual smoke test — **green**. Full end-to-end dogfood (persona "Maya Okafor"): init → profile (19 fields) → 5-skill hub/spoke network via `wsx skill add` → emit all (11 files) → lint clean → verify passed; privacy wall verified (no personal-context leak into emitted adapters; `personal.md` gitignored).

### VCS state
- **Branch**: `main` (workspace repo `snds/workspace`)
- **Last commit**: README v1 delivery — see git log
- **Uncommitted changes**: agnostic README + SPEC tweaks + new `generator/` (CLI) + `brain/` + `DEVELOPING.md`
- **Test state at last check**: **passing** — `wsx init · profile set/get · emit all · lint · verify · session` run clean; `py_compile` clean; schemas valid JSON
- **Tracking note**: this project is **git-tracked** (whitelisted in `.gitignore`), unlike most `07-projects/` folders. Intentional — the generator should be the workspace's first non-gdrive-coupled, version-controlled project. Eventual destination per SPEC §9: a standalone `wsx` CLI repo, extractable from this folder's history.

### Active tooling / MCP bridges
- **Filesystem access**: native (Claude Code)
- **Figma MCP**: not applicable
- **Other MCP connections**: none required for spec phase

### Configuration in use
- **Config files active**: `generator/` (Python, zero-dep, Python 3.9+); `wsx` run via `python3 generator/bin/wsx`
- **Canonical doc**: `SPEC.md` (v0.2) — living spec, git-versioned (no dated-filename scheme)
- **CLI language decision**: **Python 3, zero runtime dependencies** (incl. own minimal YAML in `wsxlib/yamlio.py`) — matches the README's "no extra installs" promise and the workspace's python3 tooling convention.

### Open work and paused threads
- **Currently in progress**: the whole `wsx` command surface is **stub-free** end-to-end, and the Resolver is now a **composite builder**, not just a skill fetcher. As of 2026-07-22: Path A is turn-key (registered auto-triggering brain; skeletons `wsx lint` enforces are enriched); the **Resolver** does plan-driven pull/patch/generate **+ composite** (skills that fuse the person's judgment with distilled industry-leading references, cited via an author-voice `## Sources` block; `--cache-refs` pins them); **`wsx search`** gives two-track discovery (skill registries + reference anchors, pluggable catalog); and the **MCP runtime** is a runnable zero-dep stdio server. Full loop — `init → interview → search → profile → resolve → emit {all} → lint → verify` — runs and is dogfooded. Remaining work is enhancement (hooks, template externalization, richer registry indexes), not missing commands.
- **Pending questions**: ship-as decision (SPEC §9) — standalone `wsx` repo split, deferred (folder extracts cleanly from git history when ready).
- **Blocked on**: nothing.
- **What's needed to resume** (next phases):
  1. **Resolver (Phase 2)** — **DONE (2026-07-22).** `wsx resolve` is built (`resolver.py`): reads an approved `context/skill-plan.json` and executes PULL (fetch → pin byte-identical `0o444` → namespace `skills/pulled-<registry>-<name>/` → register), PULL+PATCH (pull + editable sibling `overlay.md`, composed into the emitted Claude-Code skill), and GENERATE (delegates to `skill add`). Enforces the unvetted-registry trust gate (`skills.sh`/community refused unless `audited`/`--allow-unvetted`), pin-drift safety (`--update`), idempotency, reindex-safety (pulled records preserved), and pin-integrity in `wsx verify`. Fetch supports `http(s)`/`file`/local (offline-testable). *Remaining Resolver polish: assigned-trigger override for pulled skills is via overlay (Claude-Code composition wired; other surfaces base-only).*
  2. **`emit mcp`** — **DONE (2026-07-22).** `wsx emit mcp` writes a self-contained, **zero-dep stdio MCP server** (`adapters/mcp/server.py`) that serves the live workspace to any MCP client, plus a ready-to-paste `mcp.json` (absolute path filled in) + README. Tools: `context_load` (walled — personal excluded unless `include_personal:true`), `skills_search`, `skills_load` (overlay-composed), `session_start`, `session_end` (appends a log block), `reconcile` (CLI-only note). Server is portable (stdlib-only, discovers its own workspace root; `WSX_WORKSPACE` override). Dogfooded by driving real JSON-RPC (initialize → tools/list → each tool). **No command-surface stubs remain.**
  3. **Make Path A turn-key** — **DONE (2026-07-22).** The brain is now a registered skill at `.claude/skills/bootstrap-gen/SKILL.md` (generator root) that auto-triggers on "set up my workspace" (verified live: Claude Code discovered + registered it on write) and points to the canonical `brain/SKILL.md`. `wsx skill add` now writes a **sectioned skeleton** (`--kind hub|spoke`) instead of a flat stub, and `wsx lint` **fails** on any generated skill still carrying `_(…)_` prompts or the skeleton banner — so a workspace can't be called done with empty skills. `brain/SKILL.md` Phase 3 now mandates enrichment + `reindex`. *Out of scope by design: a headless automated loop — the brain narrates and gates each step interactively.*
  4. **Externalize templates** — move the embedded `scaffold.py` `TEMPLATES` dict into `generator/templates/` files.
  5. **Polish (minor):** reconcile `brain/synthesis.md` worked-example values with schema enums (`lifecycle.continuity` is boolean in schema but `session-log` in the example; `automation` enum is minimal/standard/full but example uses `assisted`; `schema_version=1` vs `"0.2"`). Non-breaking (CLI doesn't enforce enums), but tidy for consistency.

### Known state of external dependencies
- **Sources (Resolver, §4)**: fetch is **built and pluggable** — `wsx resolve` pulls from any `http(s)`/`file`/local `url`; per-registry trust via the `audited` gate (unvetted refused by default). **`wsx search`** now provides the discovery layer over a pluggable catalog (`context/sources.json` or a built-in default) across **two source kinds**: `skill-registry` (fetch + filter a JSON `index_url` when present, else point at the homepage) and `reference` (industry-leading standards/guidance — found by the brain's own research, listed honestly). Enhancement remaining: real registry index endpoints (the built-in registries currently have no stable machine index, so `wsx search` points at their homepages until a `sources.json` supplies one).

---

## Session history (append-only)

_Newest first._

### 2026-07-22 19:40 — checkpoint (two-track sourcing: composite skills from references + `wsx search`)

**Focus this session** (continued): reframe the Resolver from a *skill fetcher* into a *composite builder*, per Sean's steer — "the resolver should not be beholden just to skill-library sources; the interview should look for industry-leading reference, guidance, best-practices to create the best possible composite skill."
**Machine**: `Voyager-2.local` (Personal MacBook Pro)
**Stopped because**: composite + search built + dogfooded across all source types; brain reframed; docs reconciled; ready to commit.

**Grounding**: our own `08-knowledge/cross-domain/skill-ecosystem-and-mcp-servers.md` already proved the thesis — the highest-value skills we ever built (math/physics substrate, security, imaging foundations) were **synthesized from authoritative reference**, because the directories "wrap engines and tools — none teach the substrate beneath them." And it set the attribution convention: author in our own voice + cite, **never copy**.

**Built — composite skills (`generator/wsxlib/resolver.py`)**:
- Plan entries gain **`references[]`** (`title`, optional `url`/`publisher`/`note`) and a new `source: "composite"` (also: any `generated` entry with references). `wsx resolve` writes an idempotent, marker-delimited **`## Sources & further reading`** block into the skill in the person's own voice, records the citations in the manifest (`composite: true` + `references[]`), and with **`--cache-refs`** fetches + pins + caches each reference URL read-only under `skills/<name>/references/`.
- **Enforcement**: `wsx lint` fails a composite skill whose references are recorded but whose body has no Sources block; `wsx verify`'s pin-integrity now also covers cached references.

**Built — `wsx search` (`generator/wsxlib/search.py`)**: the discovery layer for **two-track sourcing**. Pluggable catalog (`context/sources.json` override, else a built-in default) across two kinds — `skill-registry` (fetch + filter a JSON `index_url`; print candidates + a paste-ready plan fragment; no-index sources point at the homepage; unvetted flagged) and `reference` (list anchors + the honest "reference discovery is your own research" note). Offline-testable via `file://`/local `index_url`.

**Brain reframed (two-track sourcing)**: `brain/resolver.md` — funnel is now PULL / PULL+PATCH / **GENERATE-COMPOSITE**; added the "Two-track sourcing" section (skill registries via `wsx search` + industry-leading references via the brain's own research/`deep-research`), the composite mandate + attribution convention. `brain/SKILL.md` Phase 3 + cheat-sheet updated. `brain/interview.md` M2 now says: when the person names their north-stars ("whose work is the bar?"), capture them as reference seeds for composite skills.

**Fixed a real correctness bug (found by dogfooding composite)**: `wsx resolve` loaded the manifest once and did a final blanket `save_manifest`, **clobbering** records that `_generate_one`/`skills.add` wrote to disk independently (only pulls survived, via the shared in-memory dict; masked earlier because I always ran `reindex` after). Fix: each handler now load-modify-saves its own manifest changes; `resolve()` no longer holds/saves a stale copy. Verified: a mixed pull/patch/generate/composite plan now persists **all four** records correctly.

**Dogfood**: mixed 4-source plan → manifest has all 4 with correct records; `--cache-refs` caches+pins a `file://` reference (read-only); `verify` shows pins for pulled skills **and** cached refs; both lint gates fire (un-enriched skeleton; composite-missing-sources); `wsx search` filters a real local index and lists the default catalog honestly. `py_compile` clean.

**Decisions made**:
- **Composite = the default aspiration**, not an edge case: per our knowledge entry, authoring-from-reference beats a shallow pull for most high-value domains.
- **`wsx` cites; the brain distills**: the mechanical hand records/pins/injects the Sources block; synthesizing references into prose (never copying) stays the brain's job — enforced by lint.
- **Reference *finding* is the brain's research, not a faked `wsx` API**: `wsx search` handles machine-indexed skill registries deterministically and is honest that reference discovery uses the brain's web tools.

**Next resumption needs**: all enhancement now — real registry index endpoints (built-ins have no stable machine index yet), MCP hooks on the claude-code adapter, externalize scaffold templates, reconcile `synthesis.md` example values with schema enums.

---

### 2026-07-22 19:15 — checkpoint (emit mcp: the universal MCP runtime, built)

**Focus this session** (continued): after the Resolver (block below), built the last remaining stub — `wsx emit mcp`, the universal runtime.
**Machine**: `Voyager-2.local` (Personal MacBook Pro)
**Stopped because**: server is runnable + dogfooded over real JSON-RPC; docs reconciled; committed.

**What `emit mcp` produces** (new `generator/wsxlib/mcp_template.py` holds the server source; `adapters.emit_mcp` writes it out): into `adapters/mcp/` —
- **`server.py`** — a **self-contained, zero-dependency (stdlib-only) stdio MCP server** (JSON-RPC 2.0, newline-delimited, protocol `2024-11-05`). Deliberately does **not** import `wsxlib`: the generated workspace is portable and must run without the generator installed. It discovers its own workspace root from its file location (`…/adapters/mcp/server.py` → `parents[2]`), overridable via `WSX_WORKSPACE`.
- **`mcp.json`** — a copy-paste client config with the server's **absolute path already filled in** (Claude Desktop / Cursor / any MCP client).
- **`README.md`** — how to register + the degradation ladder (MCP → `wsx` CLI → context pack).

**Tools exposed**: `context_load` (canonical context; **personal walled** — excluded unless `include_personal:true`), `skills_search` (by name/hub/trigger from the manifest), `skills_load` (composes pulled+patched overlays, mirroring `wsx emit`), `session_start` (boot summary + context), `session_end` (appends a session block to the log), `reconcile` (honest CLI-only note).

**Dogfood (real MCP traffic, not a mock)**: piped a full handshake through the emitted server — `initialize` (→ correct protocolVersion/serverInfo/tools capability), `notifications/initialized` (no response, correct), `tools/list` (all 6), and `tools/call` for each tool. Verified: context loads, search finds a skill, skills_load returns the body, **the privacy wall holds** (personal excluded by default, loads on opt-in), `session_end` actually appends to the log, unknown tool → JSON-RPC `-32601`, and the `WSX_WORKSPACE` override works. `emit all` + `verify` green; the old stub note is gone.

**Decisions made**:
- **Server is emitted, self-contained, stdlib-only** — portability over DRY; the workspace can't depend on the generator being present.
- **Tool names use underscores** (`context_load`, not `context.load`) for broad client-name-validation compatibility; SPEC's dotted names map 1:1.
- **Privacy wall enforced at the tool boundary**: `context_load` excludes any `personal` section unless the caller opts in — the same wall the file adapters honor.

**Next resumption needs**: with the command surface stub-free, remaining work is *enhancement*, not gaps — a registry **search/discovery** layer for the Resolver (brain currently supplies exact urls), MCP **hooks** on the claude-code adapter, externalizing scaffold templates, and the `synthesis.md` enum reconciliation.

---

### 2026-07-22 19:05 — checkpoint (Resolver Phase 2: wsx resolve built)

**Focus this session** (continued): after turn-key Path A (block below), built the biggest remaining capability — the Resolver's mechanical hand, `wsx resolve`.
**Machine**: `Voyager-2.local` (Personal MacBook Pro)
**Stopped because**: resolve is built + dogfooded across every path; docs reconciled; ready to commit.

**What `wsx resolve` does** (new `generator/wsxlib/resolver.py`, ~230 lines, zero-dep): reads an approved **machine plan** `context/skill-plan.json` (the brain's decision record — one object per capability: `name`, `source`, for pulls `registry`+`url`, assigned `hub`/`triggers`; unvetted registries need `"audited": true`) and executes the mechanical half only:
- **PULL** → fetch (`http(s)`/`file`/local path — offline-testable) → **pin** to a content hash, stored **byte-identical** and `0o444` **read-only** → **namespace** under `skills/pulled-<registry>-<name>/` (collision-proof, provenance-obvious, flows through existing emit/lint) → register in `manifest.json` (pin, registry, url, read_only, assigned hub/triggers).
- **PULL+PATCH** → pull + scaffold an **editable sibling `overlay.md`**; `emit claude-code` **composes** `pulled base + overlay` into the mirrored skill (verified: overlay lands in the mirror, never in the read-only source).
- **GENERATE** → delegates to `wsx skill add` (the enriched skeleton).

**Invariants enforced (all dogfooded green)**: trust gate (`skills.sh`/community **refused** unless `audited` or `--allow-unvetted` — verified refuse→allow); pin-drift safety (changed upstream **skipped** with a warning until `--update` re-pins — verified); idempotency (unchanged pull = no-op); read-only `0o444` + pin==file-bytes (verified); **reindex-safety** (fixed a latent bug: `wsx skill reindex` would have clobbered resolver-owned pin/registry fields — now it preserves pulled/patched records); **pin-integrity in `wsx verify`** (new check catches a tampered pulled file — verified with a tamper test).

**Wiring**: `resolver.py` new; `cli.py` gives `resolve` its own parser (`--plan`/`--update`/`--allow-unvetted`); old `lifecycle.resolve` stub removed; `skills.reindex` preserves pulled records; `lifecycle.verify` gains the pin check; `adapters.emit_claude_code` composes overlays.

**Decisions made**:
- **Plan is JSON, brain-authored, wsx-executed**: the plan is the brain's decision record (like its prose notes); every *structural* effect (dirs, pins, manifest) is `wsx`'s. Keeps the seam clean.
- **Namespace by folder name** (`pulled-<registry>-<name>`) rather than a separate subtree — so pulled skills flow through the existing one-level `iter_skills`/emit/lint pipeline unchanged, while provenance stays obvious.
- **Pin = byte-identical**; assigned hub/triggers live in the manifest, overrides go in the overlay — never edit a pulled file. Pulled skills therefore route on their *upstream* front-matter triggers on non-composed surfaces; overlay composition is wired for the recommended Claude-Code path (documented honestly).

**Next resumption needs**: `emit mcp` (SPEC §5) is now the single biggest stub. Then minor polish: a registry *search/discovery* layer (brain currently supplies exact urls), externalize scaffold templates, reconcile `brain/synthesis.md` example values with schema enums.

---

### 2026-07-22 18:45 — checkpoint (turn-key Path A: registered brain skill + enriched skeletons + lint gate)

**Focus this session**: Resume the generator; close the "Make Path A turn-key" gap (next-resume item #3) so a stranger — not just someone who knows the commands — can actually build their own workspace.
**Machine**: `Voyager-2.local` (Personal MacBook Pro)
**Stopped because**: both halves built + dogfooded green; ready to commit.

**Verified reality first** (checkpoint was 5 weeks stale): the whole `wsx` loop still runs green — `init → profile → skill add → emit all → verify` pass; folder is git-tracked + clean; `emit mcp`/`resolve` still honest stubs. Earlier "failures" in testing were bad command grammar, not the tool.

**(a) Auto-trigger — the brain is now a registered skill.** Created `.claude/skills/bootstrap-gen/SKILL.md` at the generator root: a thin **pointer skill** (rich `description` + `triggers`) that loads the canonical `brain/SKILL.md` (kept as single source; `../../../brain/SKILL.md` resolves). Added "set up my workspace" + "build my second brain" to the brain's triggers. **Proof**: Claude Code discovered and registered `bootstrap-gen` live the moment the file was written (directory-scoped to the project) — so a plain *"set up my workspace"* now routes to the brain with no file-naming nudge. Git tracks it via the `!07-projects/18-bootstrap-generator/**` whitelist; no conflict with the workspace-root session (nested `.claude` isn't loaded by the root project).

**(b) Enriched skill bodies — no more flat stubs.** Rewrote `wsx skill add` (`skills.py`): writes a **sectioned skeleton** with `_(…)_` writing prompts — spoke (When to use / How to do it well / Worked example / Anti-patterns / Related) vs hub (What this hub owns / Spokes / Operating standards) via a new `--kind hub|spoke` flag; hubs get `role: orchestrator`. Added a mechanical **anti-stub gate** to `wsx lint`: any `source: generated` skill still carrying `_(…)_` prompts or the skeleton banner now **fails** lint (pulled skills exempt). Updated `brain/SKILL.md` Phase 3 to mandate enrichment → `reindex`, and the cheat-sheet for `--kind`.

**Dogfood**: fresh workspace, hub+spoke via `skill add` → inspected skeletons (read well) → `emit all` mirrors skills into `.claude/skills/` → `verify` green → `lint` fails on stubs (exit 1), passes once a skill is enriched (confirmed by hand-filling one). `py_compile` clean.

**Decisions made**:
- **Pointer skill, not relocation**: keep the canonical brain in `brain/` (referenced by SPEC/DEVELOPING); the registered skill is a thin loader. Reversible; avoids duplication/drift. Follow-up option: promote `brain/` to be the skill home for a fully self-contained distribution.
- **Enrichment enforced by the tool, not just discipline**: `lint` is the gate, matching how it already treats trigger overlaps — turn-key honesty ("can't ship blank skills").
- **Headless automated loop stays out of scope**: the interactive, gated brain is the intended UX.

**Next resumption needs**: Resolver PULL (`wsx resolve`, Phase 2) + `emit mcp` (SPEC §5) remain the two big stubs. Minor: reconcile `brain/synthesis.md` worked-example values with schema enums; finish externalizing scaffold templates.

---

### 2026-06-14 20:45 — checkpoint (wsx skill command + end-to-end dogfood test)

**Focus this session**: Test the generator end-to-end and close the last gap blocking Path A.
**Machine**: `Voyager-2.local` (Personal MacBook Pro)
**Stopped because**: full loop runs and verifies; ready to commit.

**Gap found by testing**: the brain's Resolver GENERATE path had no mechanical command — the seam forbids the brain writing structural files, but there was no `wsx` command to create a skill. Added `wsx skill add/list/reindex` (`wsxlib/skills.py`): creates a skill folder + front matter and registers it in `manifest.json`; `reindex` rebuilds the index from disk.

**Dogfood (persona "Maya Okafor", UX researcher)**: acted as the brain, drove the whole loop with real `wsx` calls — `init` → `profile set` (19 fields, M0–M5; lists vs strings correct) → 5 generated skills (`lead-ux-researcher` hub + 3 spokes + a personal `film-photography`) → wrote context prose directly → `emit all` (11 files: CLAUDE.md, .claude/skills ×5, AGENTS.md, .cursor/rules, context-pack, mcp stub) → `lint` clean → `verify` passed. **Privacy wall verified**: grepped every emitted adapter for personal-context terms (trail/japanese/zine) — none leaked; `personal.md` gitignored.

**Wiring**: added a concrete `wsx` command cheat-sheet to `brain/SKILL.md` (invocation path + every step incl. `skill add`) so any AI following it can drive the loop. Updated DEVELOPING.md command table.

**Decisions made**:
- **Seam nuance documented**: the brain writes plain-prose context notes (`project-context.md`, `personal.md`) directly; everything structural (scaffold, profile, skills, emit) goes through `wsx`.
- Generated skills are **stubs** the brain enriches — `wsx skill add` creates front matter + registration; the AI fills the body.

**Next resumption needs**: register the skill for auto-load (turn-key Path A), enrich generated skill bodies, then Resolver PULL (Phase 2) + `emit mcp`.

---

### 2026-06-13 17:30 — checkpoint (dummy-proof on-ramp)

**Focus this session**: Fixed getting-started after the user couldn't run it ("obtuse README, didn't see the python command, ran from the project dir to no avail").
**Machine**: `Voyager-2.local` (Personal MacBook Pro)
**Stopped because**: on-ramp verified end-to-end; ready to commit.

**Diagnosis**: README explained concepts but gave no concrete commands; running `wsx` from the generator folder fails by design ("not inside a wsx workspace") — that folder IS the generator, not a workspace. The generator-vs-workspace distinction was invisible.

**Accomplishments**:
- **Double-click on-ramp**: `start.command` (macOS) + `start.sh` + `start.bat` (Windows) — checks Python/git, asks 2 questions (where + name), runs `wsx init`, emits claude-code, prints next steps; Gatekeeper "right-click → Open" note included.
- **Friendlier CLI**: bare `wsx` prints a welcome (generator-vs-workspace + the 2 paths) instead of an argparse error; added `wsx doctor` (python/git/where-am-I/next-step). Both verified from the generator dir AND from inside a workspace.
- **README quick-start rewrite**: leads with the generator-vs-workspace gotcha, then 3 concrete paths — A (tell your AI: *"Read brain/SKILL.md and set up my workspace"*), B (double-click start), C (one terminal command + `wsx doctor`). Honest: Paths B/C work today, guided interview early.

**Decisions made**:
- **Recommended against signed binaries for now**: the tool is AI-driven + zero-dep Python (preinstalled on macOS), so binaries optimize a rare manual path at high cost (Apple Dev $99/yr + notarization + per-OS/arch builds). Better ladder: AI-driven front door → double-click script → `pipx`/`uv tool install` → (only later, at scale) a notarized binary/.app.
- The truly dummy-proof path is **"tell your AI"** (Path A), matching the AI-driven architecture.

**Next resumption needs**: unchanged — Resolver (Phase 2), `emit mcp`, auto-drive the brain, externalize templates.

---

### 2026-06-13 16:38 — checkpoint (agnostic README + runnable wsx CLI v0.1 + brain)

**Focus this session**: Made the README truly AI-agnostic (Claude *recommended*, not required), then built the generator — a runnable `wsx` CLI plus the canonical brain.
**Machine**: `Voyager-2.local` (Personal MacBook Pro)
**Stopped because**: a coherent, verified milestone — CLI runs end-to-end, docs reconciled, ready to commit.

**Accomplishments**:
- **Agnostic README**: verified 6 more tool links (agents.md ⭐ keystone — Linux Foundation open standard; Cursor, OpenAI Codex, Gemini CLI, GitHub Copilot; dropped Windsurf — domain now 308s to devin.ai). Reframed around "Claude recommended, workspace agnostic via open standards (AGENTS.md/MCP/Agent Skills)"; added a supported-agents table + an "open standards (why it isn't locked to one AI)" concept + FAQ.
- **`wsx` CLI v0.1** (Python 3, **zero deps**) — `generator/wsxlib/{cli,core,yamlio,scaffold,adapters,lifecycle}.py` + `bin/wsx` + `schemas/*` + `pyproject.toml`. Commands: `init` (vault+git scaffold), `profile get/set` (list-field-aware), `emit {claude-code,agents-md,cursor,mcp,pack,all}`, `lint` (trigger-overlap report), `verify` (profile round-trip + per-target dry-run), `session`, `sync`. `resolve` + `emit mcp` are honest stubs.
- **Canonical brain** (authored via a 6-agent workflow): `brain/{interview,synthesis,resolver,SKILL}.md` + `DEVELOPING.md`. AI-agnostic; SKILL.md is the runnable Claude adapter.
- **Verified by execution**: `wsx init → profile set → emit all → lint → verify → session` all green in a temp workspace; privacy wall holds (`context/personal.md` gitignored); `py_compile` + schema-JSON checks pass.
- **Reconciled docs**: fixed the 2 majors the consistency reviewer found in DEVELOPING.md (wrong `profile set` grammar/key; mcp build-order contradiction) and updated it to the *as-built* state; fixed SPEC "Five→Six movements" + added `schema_version`; fixed a synthesis slug.

**Decisions made**:
- **CLI = Python 3, zero dependencies** (own minimal YAML subset in `yamlio.py`) — runs anywhere without installs, honoring the README's promise; matches workspace python3 convention.
- **`wsx profile set` is list-field-aware**: known list fields (agents, machines, crafts, interests, banned, imports) split on commas; scalar fields keep commas (so `role="Senior designer, fintech"` stays a string). Aligns the hands to how the brain naturally writes.
- **mcp deferred to a stub** (heavier); the lightweight `AGENTS.md`/`pack`/`cursor` adapters already cover Cursor/Codex/Copilot/Gemini, so they land first instead.
- **v0 embeds scaffold templates in `scaffold.py`** for zero-file-dependency reliability; externalizing to `templates/` is a noted follow-up.

**Next resumption needs**:
- Phase 2 (Resolver / `wsx resolve`), `emit mcp`, wire brain → automated loop, externalize templates, reconcile brain worked-example values with schema enums (see Open work).

---

### 2026-06-13 15:10 — checkpoint (delivery README)

**Focus this session**: Authored a non-engineer-facing `README.md` as the self-contained delivery front-door.
**Machine**: `Voyager-2.local` (Personal MacBook Pro)
**Stopped because**: natural break — README written, link-verified, committed.

**Accomplishments**:
- Ran a multi-agent workflow (9 agents): 5 parallel link-verification clusters (Obsidian, Git/GitHub, Claude, MCP+registries, concepts) → draft → 3 adversarial critics (non-technical reader, link auditor, fidelity/honesty). All 15 external links fetched + confirmed resolving.
- Authored `README.md` in plain language: every jargon term defined + linked; "today you can / coming soon" honesty banner; 🚧 markers on unbuilt steps; walled-privacy section; FAQ; grouped link reference.
- Applied critic fixes: corrected the overstated paywall (Skills span all tiers; the real gate is Claude Code — Pro ≈ $20/mo, includes Claude Code, link to pricing); collapsed the confusing "two doors" into one recommended path (Claude desktop app includes Claude Code); moved the terminal out of the required list + reassured user never types `wsx`; added hub/spoke "you're a passenger" + learn-more link; named supported surfaces; dropped the "movements" metaphor.
- Removed a stray root-level `README.md` the draft sub-agent wrote to the vault root (gitignored dup).

**Decisions made**:
- README placed in the **project folder** (not vault root) so the relative `SPEC.md` / `SESSION-STATE.md` links resolve instead of 404-ing — which dissolved the reviewers' top link finding.
- Verified pricing live rather than asserting a figure (Pro ≈ $20/mo, $17 annual).

**Next resumption needs**:
- Phase 0 still pending: `profile.yaml` + `manifest.json` schemas and `wsx` command-surface stubs.

---

### 2026-06-13 14:45 — wrap-up (seeding)

**Focus this session**: Captured the portable bootstrap-generator spec (v0.2) and set the project up as a git-tracked workspace project.
**Machine**: `Voyager-2.local` (Personal MacBook Pro)
**Stopped because**: natural break — spec recorded, scaffold in place.

**Accomplishments**:
- Authored `SPEC.md` v0.2 (skill+CLI seam, git+Obsidian transport, MCP runtime, walled-context model, 5-movement interview, Resolver, Emitter, `wsx` command surface, dogfood-first build order).
- Moved the spec out of gitignored `05-artifacts/active/` into `07-projects/18-bootstrap-generator/` and whitelisted the folder in `.gitignore` so it syncs via the workspace git repo.
- Seeded this `SESSION-STATE.md`.

**Decisions made**:
- **Git-tracked from day one**, not Drive-only. Generator is the pilot for the planned gdrive removal — "do the right thing first."
- **Living `SPEC.md`** (git = version register) instead of dated `_vN.N_YYYY-MM-DD` artifact filenames, since the project is now version-controlled.
- Did **not** alter git identity config (`hello@snds.design`) — that's the deferred re-privatize/noreply decision in `project-context.md`.

**Next resumption needs**:
- Phase 0: draft `profile.yaml` + `manifest.json` schemas and `wsx` subcommand stubs.
