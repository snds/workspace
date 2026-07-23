# SESSION-STATE — Portable Bootstrap Generator

_Last updated: 2026-07-23 — checkpoint (colleague-feedback pass: broader `wsx scan` detection incl. ChatGPT/desktop chat apps, connective **MOC layer** so the emitted vault graph is no longer islands, `projects/` per-project documentation tree + `wsx project`, and `wsx upgrade` corrective pass for already-generated workspaces; earlier: permission-free `launch.py` + per-OS zips, scan gate + BYO-tokens, authoring framework, `wsx remote`, expertise calibration, two-track sourcing, emit mcp, Resolver Phase 2, turn-key Path A)_

### 2026-07-23 — colleague feedback (four asks, all built + dogfooded)

1. **Detect ChatGPT / all popular LLM tools** — `scan.py` now splits detection into **coding agents** (Claude Code, Cursor, Codex, Gemini-CLI, Copilot, Windsurf, Zed, Aider, Amazon Q, Continue/Cline/Roo/Cody — via PATH + config + macOS `.app` + editor-extension globs) and **chat/desktop apps** (ChatGPT, Claude desktop, Perplexity, Copilot, Msty, Cherry Studio → `pack` surface). Local-LLM probes gained GPT4All + TextGen. `_suggest` prefers a coding surface, falls back to `pack` for chat-only.
2. **Nothing connected the skills/frameworks (islanded graph)** — root cause: every skill file is `SKILL.md` and `Related`/framework refs were code-spans/bold, not links. New `moc.py` regenerates a **Map-of-Content link layer** — `HOME.md` (root front door) + `skills/_INDEX.md` + `projects/_INDEX.md` — with path-correct relative links (root-relative from HOME, dir-relative from the indexes) so Obsidian draws edges. New skill skeletons now link their hub + the index. MOCs regenerate on `init`/`skill add`/`reindex`/`emit all`/`project new`/`upgrade`.
3. **Project documentation directory** — new `projects/` tree (docs & context only, **not** code/assets): `wsx project new "<name>"` → `projects/<slug>/PROJECT.md` (overview · where the code lives · live handoff · decisions · pending) + `notes/`. `.gitignore` guards keep code trees out. AGENTS.md/CLAUDE.md adapters now point the AI at `projects/<name>/PROJECT.md` + `HOME.md`.
4. **Corrective pass on existing workspaces** — new `wsx upgrade [--dry-run]`: non-destructive (adds missing scaffold, regenerates the MOC layer, never clobbers hand-edited files), idempotent, applies by default. This is also what retro-connects a pre-existing islanded graph.

Verified end-to-end: `init → skill add hub+spoke → project new → reindex → lint (only expected skeleton warnings) → emit all → verify` clean; `upgrade` on a simulated legacy workspace added missing pieces, preserved a hand-edited file, reconnected the graph, re-ran idempotently, verify still green. `py_compile` clean across all modules.

**Second batch (2026-07-23, later) — ALL `obsidian-second-brain` learnings built into BOTH the generator and Sean's live workspace, plus workspace auto-discovery:**

Generator (`wsx`): scaffolds `context/CRITICAL_FACTS.md` (tiny always-loaded hot cache), `context/conventions.md` (typed-edge `relations:` vocab + freshness + `## For future agent` preamble), `context/decisions/` ADR folder + `_TEMPLATE.md`; `wsx project new` now emits a `## For future agent` block + a Dataview-ready `board.md` (`#status/*`); new **`wsx health`** (orphans + `#stale`/aging `as of` + dangling typed edges; advisory vs. exit-gating); **`wsx scan --find-workspaces`** shallow-walks the usual homes (~/Documents, ~/Projects, Obsidian iCloud vault) to locate an existing workspace; adapters (AGENTS/CLAUDE) now say read CRITICAL_FACTS first + follow the note conventions; HOME links the new context notes; `wsx upgrade` retro-adds all of it. Brain SKILL gained an **"update an existing workspace"** branch (triggers: "update/upgrade/fix/course-correct my workspace") that runs `scan --find-workspaces` → confirm → `wsx upgrade` → re-emit → `wsx health`, WITHOUT re-interviewing.

Sean's workspace: `06-context/CRITICAL_FACTS.md` (real content, wired as load-order item 0 in CLAUDE.md); `02-shared-references/vault-graph-conventions.md` (typed edges scoped to the *epistemic* graph — knowledge/memory — explicitly NOT crossing the existing skill `## Related` graph) + `## For future agent` preamble; freshness three-state rule added to `epistemic-standards.md` §2 and pointed to from framework #04; framework #08 gained a "Graph & freshness conventions" subsection; `memory/_template.md` enriched to full ADR shape + `relations:` + preamble; `08-knowledge/_README.md` entry format gained `relations:` + freshness + preamble; session-state template gained a TL;DR line; new **`09-tools/vault-health.py`** + **`/health` skill** (epistemic-graph hygiene, complements `validate-links.py` which owns the skill graph); opt-in `02-shared-references/nightly-maintenance-recipe.md`. All validators green (`validate-links` 252 skills 0 warn, `validate-workspace` ok); `vault-health` surfaced 2 genuine pre-existing orphans (spawned as a background task).

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
- **Currently in progress**: **VALIDATED, colleague-ready, self-sufficient, and BYO-tokens.** The `wsx` surface is stub-free (**13 commands**), the Resolver is a composite builder, skills write at a per-domain expertise altitude, every workspace ships a supreme `frameworks/skill-authoring.md`, `wsx remote` settles free hosting, and **`wsx scan`** detects the user's own agents/MCP/local-LLMs to pre-fill setup — reinforcing that the generator has **no API key and makes no model calls** (runs on the user's own tools/account; a local model is fully private, zero token cost). `VALIDATION.md` is the proofboard. As of 2026-07-22: Path A is turn-key (registered auto-triggering brain; skeletons `wsx lint` enforces are enriched); the **Resolver** does plan-driven pull/patch/generate **+ composite** (skills that fuse the person's judgment with distilled industry-leading references, cited via an author-voice `## Sources` block; `--cache-refs` pins them); **`wsx search`** gives two-track discovery (skill registries + reference anchors, pluggable catalog); and the **MCP runtime** is a runnable zero-dep stdio server. Full loop — `init → interview → search → profile → resolve → emit {all} → lint → verify` — runs and is dogfooded. Remaining work is enhancement (hooks, template externalization, richer registry indexes), not missing commands.
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

### 2026-07-22 21:20 — checkpoint (permission-free launcher + per-OS distribution zips)

**Focus**: Sean asked for zipped generator packages (mac/win/linux) with a **permission-independent executable** — prior exec scripts always tripped the macOS exec-bit/Gatekeeper flag. **Constraint added mid-task**: must suit a *non-technical* user; open to the $99 Apple cert but hoping for an existing-cert open-source route.

**Honest finding given first**: there is **no** unsigned double-click path on macOS that avoids Gatekeeper — and no way to borrow someone else's notarized wrapper for an arbitrary script. The "already has the cert" answer *in spirit* is the user's **own AI app** (Claude/Cursor, already notarized) or Python.org's signed installer. Sean chose the **free path (A + C + launch.py)**; I prepped the $99 pipeline for later.

**Built**:
- **`launch.py`** — the permission-free launcher: run as `python3 launch.py`, so **no exec bit** and **nothing for Gatekeeper/SmartScreen** to block (it invokes `wsx` via `python <script>` too — no file in the tool needs to be executable). Fixed stdout line-buffering so prompts read in the right order. `start.command`/`.sh`/`.bat` now just delegate to it.
- **`package.py`** → `dist/wsx-generator-{macos,windows,linux}.zip` (~117 KB each). Each is a self-contained `wsx-generator/` with the tool + `launch.py` + the OS launcher + a plain-language **START-HERE.txt** that leads with the zero-permission path (open in your AI app → "set up my workspace"), then double-click (right-click→Open on mac / SmartScreen Run-anyway on win), then `python3 launch.py`. Excludes SESSION-STATE, junk, test workspaces. `dist/` gitignored.
- **`packaging/`** — the optional $99 notarized path, drop-in for later: `make-macos-app.sh` (builds a `.app`), `sign-notarize.sh` (codesign→notarytool→staple from env/keychain creds — no secrets in repo), `macos-notarization.md` (walkthrough).

**Validated end-to-end**: extracted the mac zip fresh, ran `python3 launch.py` with piped answers → scaffolded a workspace (CLAUDE.md + skill-authoring.md present), scan showed the stack, correct output ordering. `make-macos-app.sh` builds a valid bundle (plist lints OK).

**Zips are at**: `07-projects/18-bootstrap-generator/dist/` (gitignored; regenerate anytime with `python3 package.py`).

**Decisions**: (1) permission-independence = "invoke a trusted interpreter on a data file," never ship an executable — the durable fix. (2) For a non-technical user the AI-app path (A) dominates and is $0/permission-free; the launcher is the no-AI fallback. (3) $99 notarization is prepped but not required.

**Next**: the auto-sync/working-tree-reset hook fix (Sean queued it as the next task).

---

### 2026-07-22 21:00 — checkpoint (surface-recommendation gate when none detected)

**Focus** (continued): Sean — if a user has no LLM set up, recommend selecting a surface/LLM **before** the interview, so the generator can leverage it for the heavy lifting → best outcome.
**Machine**: `Voyager-2.local`. **Stopped because**: gate built + both branches dogfooded; committed.

**Built**: `wsx scan` now computes **`needs_setup`** (no agent AND no local model) and prints a prioritized **RECOMMENDATION** block — Claude Code (recommended) → Cursor → frontier chat + AGENTS.md/pack → local Ollama — each with the *why* and an install pointer, plus the honest note that a frontier model yields richer skills and that a bare `wsx init` starter is the fallback. **Brain gate**: interview M0 + SKILL.md Phase 1 now **pause on `needs_setup`**, recommend a surface, help the person set one up and re-scan, and only fall back to the mechanical path if they insist — never silently run a degraded interview.

**Dogfood**: real machine → `needs_setup=false` (Claude Code present), no gate; simulated empty stack → the full recommendation block fires. `py_compile` clean.

**Decision**: the generator's output quality is bounded by the assistant driving it, so "pick a capable surface first" is a *gate*, not a suggestion — but it degrades gracefully (mechanical scaffold) rather than blocking.

---

### 2026-07-22 20:50 — checkpoint (`wsx scan` — detect the user's own stack + BYO-tokens)

**Focus this session** (continued): Sean asked whether the generator scans for installed agentic tools / MCP / local-LLMs and lets users bring their own tokens — not tied to his API or to using Claude unless the user has their own account. **Answer given first**: token/account isolation was *already* guaranteed (the `wsx` engine has zero API calls / no key — verified by grep; the "brain" is whatever agent the user already runs). The gap was **detection + explicit selection**. He chose "full scan + select"; built it.

**Built — `wsx scan`** (`generator/wsxlib/scan.py`, zero-dep):
- **agents** — PATH binaries + known config dirs for Claude Code, Cursor, Codex, Gemini, Copilot, Windsurf, Aider, Continue; each maps to its emit target.
- **mcp** — reads standard MCP configs (`claude_desktop_config.json`, `.cursor/mcp.json`, `~/.claude.json`) and extracts **server NAMES ONLY** — never the `env`/values (which can hold API keys). **Security-verified**: written `scan.json` has 0 secret-bearing content.
- **local_llms** — probes localhost (Ollama :11434, LM Studio :1234, Jan :1337) with a 0.5s timeout; a local model ⇒ fully offline, zero token cost.
- Suggests `surfaces.*`/`models.*` pre-fill (brain confirms); `--json` for the brain, `--write` saves `context/scan.json`. Works with or without a workspace.

**Dogfooded on this real machine**: detected **Claude Code** (PATH) + **Cursor** (config), the MCP server **`figma-desktop`** by name only (no secrets), no local LLM running, suggested primary=claude-code/tier=frontier. `--json` clean; `--write` safe.

**Wired into the brain + BYO note**: interview M0 now **scans first, then confirms** (don't ask cold) and states BYO-tokens plainly; SKILL.md Phase 0 (agnostic + BYO promise), Phase 1, and cheat-sheet updated; synthesis maps scan→surfaces/models. BYO-tokens line added to the generated-workspace README template, `VALIDATION.md` (new contract row), and DEVELOPING.

**Decisions made**:
- **Detection reads names only, never secrets** — the one real risk (MCP `env` API keys) is designed out; verified.
- **Scan suggests, brain confirms** — no silent auto-config; the person always sees and can override.
- **BYO-tokens is stated everywhere the user looks** (interview, workspace README, proofboard) because it's a trust property, not a feature footnote.

**Next resumption needs**: still just enhancement — real registry search indexes, MCP hooks, externalize scaffold templates (now including the authoring framework + BYO README). Command surface is 13 and stub-free.

---

### 2026-07-22 20:30 — checkpoint (self-perpetuating authoring framework + `wsx remote` hosting)

**Focus this session** (continued): Sean's "single addition" to reach completion — (a) a top-level default framework in the *generated* workspace that supersedes the surface's native "build a skill" so the owner keeps this generator's rigor forever, and (b) a step that asks **where the workspace should live**, recommending free hosting.
**Machine**: `Voyager-2.local` (Personal MacBook Pro)
**Stopped because**: both built + dogfooded + validated; docs + VALIDATION.md updated; committed.

**(A) Supreme authoring framework** (`scaffold.py` + `adapters.py`): every generated workspace now ships **`frameworks/skill-authoring.md`** (~100 lines) — a governing doc that **SUPERSEDES the LLM/surface's native skill-builder**. It encodes the generator's rigor for post-hand-off authoring of skills/hubs/spokes/frameworks/playbooks: pick the unit, set the **altitude from per-domain expertise**, **two-track source (skills + references) and cite in the person's voice**, write the sectioned skeleton, **reconcile triggers**, and pass an **acceptance checklist** — with a `wsx` fast-path when present and an identical manual path when not. All four emitted adapters (CLAUDE.md, AGENTS.md, Cursor rule, context pack) carry a **SUPREME RULE** pointing to it, so any surface routes "build me a skill" through it. `frameworks/00-README.md` lists it first.

**(B) `wsx remote` — where it lives** (`lifecycle.py` + `cli.py`): bare `wsx remote` recommends **free** homes (private **GitHub** repo, **GitLab**, **Codeberg**, or **local-only**) and explains the flow; `wsx remote <url>` sets the git remote **and** records `transport.remote`. `wsx init` now prompts the hosting decision; `wsx sync`'s no-remote note points at it. **We never create accounts/repos** — the person makes an empty repo, `wsx` wires it, `wsx sync` pushes. Brain: interview M0 asks the hosting question with the free recs; synthesis maps `transport.remote`; SKILL.md cheat-sheet + closing report walk the owner through it and remind them new skills go through the authoring framework.

**Dogfood/validation**: fresh init prompts hosting + ships `skill-authoring.md`; `emit all` → CLAUDE.md carries the SUPREME rule (all 4 adapters reference the framework); `wsx remote` lists 4 free options; `wsx remote <url>` wires origin + records `transport.remote`; `verify` green. Command surface now 12: `init·profile·emit·doctor·lint·verify·sync·resolve·remote·search·session·skill`.

**Decisions made**:
- **The framework is instructional-first** (works on any surface, `wsx`-optional) so a portable workspace keeps the rigor even where the CLI isn't installed.
- **Supremacy is stated in every adapter**, not just the framework file, so the native skill-builder is actually overridden wherever the owner works.
- **Hosting: recommend + wire, never provision** — account/repo creation is the user's (and off-limits to the agent); `wsx remote` handles only the mechanical wiring.

**Next resumption needs**: the product is complete for the colleague test. Pure enhancement remains — real registry search indexes, MCP hooks, externalize scaffold templates (the framework/authoring doc is now another good candidate to externalize).

---

### 2026-07-22 20:10 — checkpoint (per-domain expertise calibration + validated for colleague)

**Focus this session** (continued): per Sean's steer — the generator must determine **use-context** (personal/professional/mixed) and prioritize the user's **level of knowledge/seniority/time-in-industry, per skillset** (his example: hobbyist in game design/3D, staff-level expert UX). Then drive to a **validated final output** a colleague can test.
**Machine**: `Voyager-2.local` (Personal MacBook Pro)
**Stopped because**: feature built + validated end-to-end mirroring the exact mixed-expertise case; VALIDATION.md written; committed.

**The core insight built in**: expertise is **per-domain, a separate axis from energy** — the same person is routinely an expert in one craft and a hobbyist in another, and each skill must be written at the altitude for *its* domain.
- **Schema**: `use_context` (personal/professional/mixed) + `expertise{}` (per-domain `{level, seniority?, years?}`).
- **`wsx skill add --level {hobbyist,intermediate,advanced,expert} --seniority`** shapes the skeleton: hobbyist → teaching tone + a **"Foundations to learn"** section; expert → assumes fluency, adds **"Judgment calls & edge cases"** and (with seniority) **"Setting the bar & leading"**. Recorded in front matter + manifest; passed through `wsx resolve` plan entries.
- **Brain**: interview §4a (level ≠ energy, per-domain), M0 settles `use_context` first, M1 seniority, M2 per-craft level; synthesis maps to `use_context`+`expertise{}`; resolver/SKILL read `profile.expertise{}` per domain to set `--level`.
- **Bonus**: reconciled the long-standing brain↔schema drift (`schema_version` → "0.2"; `lifecycle.continuity` boolean; `automation` minimal/standard/full).

**VALIDATED (persona "Priya Nair" — staff UX expert + game/3D hobbyist, mixed)**: one profile → the **same person's** two skills emit at **opposite altitudes** — `ux-research` (expert/staff: "do NOT re-explain fundamentals… capture THEIR judgment", + Judgment/Leadership sections, + cited Sources from a composite reference) vs `game-design` (hobbyist: "TEACH: define jargon, explain the why", + Foundations to learn). Full pipeline green: `init → profile(use_context+expertise) → resolve --cache-refs → emit all (10 files) → verify passed → lint` (lint correctly flags the un-enriched skeletons — the gate working). On-ramp confirmed: registered `bootstrap-gen` skill, `start.*` scripts, `wsx doctor`. Wrote **`VALIDATION.md`** — a colleague-facing proofboard (plain-English contracts + evidence + run instructions).

**⚠ Incident (recovered)**: mid-session a workspace sync/auto-commit reset the working tree to HEAD, discarding my uncommitted expertise edits (all but synthesis.md). Re-applied every change from memory, re-validated, and **committed immediately** in two locked commits (`code`, then `brain`). Lesson: commit each coherent unit promptly; the auto-commit hook can rewrite history / reset the tree under a long turn.

**Decisions made**:
- **Level is per-domain and separate from energy** — the load-bearing model choice; a global rating would misfit the common expert-in-one/hobbyist-in-another person.
- **Altitude is enforced structurally** (different skeleton sections + a front-matter `level`), not left to prose discipline.
- **Delivered a proofboard, not just code** — the colleague can verify the guarantees without reading Python (workspace delivery-playbook convention).

**Next resumption needs**: genuinely just enhancement now — real registry search indexes, MCP hooks on the claude-code adapter, externalize scaffold templates. The product is colleague-testable today.

---

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
