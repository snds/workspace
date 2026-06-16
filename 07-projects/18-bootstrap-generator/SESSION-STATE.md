# SESSION-STATE — Portable Bootstrap Generator

_Last updated: 2026-06-14 20:45 — checkpoint (wsx skill command + full end-to-end dogfood test)_

---

## Current state (rewritten atomically — no stale fields)

### Environment
- **Machine**: `Voyager-2.local` (Personal MacBook Pro)
- **OS context**: macOS (Darwin 25.5.0)
- **Workspace root**: `/Users/snds/My Drive/Claude Workspace`
- **Project root**: `/Users/snds/My Drive/Claude Workspace/07-projects/18-bootstrap-generator`

### Active servers and processes
- **Dev server**: not running
- **Build process**: not running
- **Test runner**: manual smoke test — **green**. Full end-to-end dogfood (persona "Maya Okafor"): init → profile (19 fields) → 5-skill hub/spoke network via `wsx skill add` → emit all (11 files) → lint clean → verify passed; privacy wall verified (no personal-context leak into emitted adapters; `personal.md` gitignored).

### VCS state
- **Branch**: `main` (workspace repo `claude-workspace-system`)
- **Last commit**: README v1 delivery — see git log
- **Uncommitted changes**: agnostic README + SPEC tweaks + new `generator/` (CLI) + `brain/` + `DEVELOPING.md`
- **Test state at last check**: **passing** — `wsx init · profile set/get · emit all · lint · verify · session` run clean; `py_compile` clean; schemas valid JSON
- **Tracking note**: this project is **git-tracked** (whitelisted in `.gitignore`), unlike most `07-projects/` folders. Intentional — the generator should be the workspace's first non-gdrive-coupled, version-controlled project. Eventual destination per SPEC §9: a standalone `wsx` CLI repo, extractable from this folder's history.

### Active tooling / MCP bridges
- **Desktop Commander**: not connected (Claude Code session)
- **Figma MCP**: not applicable
- **Other MCP connections**: none required for spec phase

### Configuration in use
- **Config files active**: `generator/` (Python, zero-dep, Python 3.9+); `wsx` run via `python3 generator/bin/wsx`
- **Canonical doc**: `SPEC.md` (v0.2) — living spec, git-versioned (no dated-filename scheme)
- **CLI language decision**: **Python 3, zero runtime dependencies** (incl. own minimal YAML in `wsxlib/yamlio.py`) — matches the README's "no extra installs" promise and the workspace's python3 tooling convention.

### Open work and paused threads
- **Currently in progress**: Phase 0 + Phase 1 + on-ramp + a **working end-to-end loop**. Added `wsx skill add/list/reindex` (the Resolver GENERATE hand). Dogfooded the whole brain→wsx loop *manually* (Path A) on a persona — it produces a complete, AI-ready workspace. `brain/SKILL.md` now carries a concrete `wsx` command cheat-sheet so any AI can drive it. Not yet auto-invoked as a registered skill; generated skills are stubs the brain enriches.
- **Pending questions**: ship-as decision (SPEC §9) — standalone `wsx` repo split, deferred (folder extracts cleanly from git history when ready).
- **Blocked on**: nothing.
- **What's needed to resume** (next phases):
  1. **Resolver (Phase 2)** — implement `wsx resolve` (currently a stub): registry fetch + pin + namespace; wire the skill-plan review gate.
  2. **`emit mcp`** — currently a stub; build the `workspace-mcp` server (SPEC §5).
  3. **Make Path A turn-key** — the brain runs end-to-end *manually* today (dogfooded ✓) and `SKILL.md` has the command cheat-sheet; remaining: register it as an auto-loaded skill/plugin so "set up my workspace" triggers it without a nudge, and have it enrich generated skill bodies (not just stubs).
  4. **Externalize templates** — move the embedded `scaffold.py` `TEMPLATES` dict into `generator/templates/` files.
  5. **Polish (minor):** reconcile `brain/synthesis.md` worked-example values with schema enums (`lifecycle.continuity` is boolean in schema but `session-log` in the example; `automation` enum is minimal/standard/full but example uses `assisted`; `schema_version=1` vs `"0.2"`). Non-breaking (CLI doesn't enforce enums), but tidy for consistency.

### Known state of external dependencies
- **Registries to wire (Resolver, §4)**: skills.sh, anthropics/skills, agentskills.io, community, user imports — none integrated yet (Phase 2).

---

## Session history (append-only)

_Newest first._

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
