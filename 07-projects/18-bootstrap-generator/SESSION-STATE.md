# SESSION-STATE — Portable Bootstrap Generator

_Last updated: 2026-09-17 — Path B picker + Windows zip on Desktop._

### 🤝 Live handoff (the baton)

- **Current focus:** Path B surface picker + Windows handoff zip. Waves 0–7 still proved (`wsx` 0.3.0).
- **Working set:** `launch.py`, `generator/wsxlib/scan.py`, README Path B, `package.py`
- **Last action:** Session-end 2026-09-17 — Path B picker committing; `wsx-generator-windows.zip` on Desktop.
- **Next action:** Colleague tests `start.bat` on PC (Cursor default). Then Olga/full path when asked.
- **Do-not-touch:** `wsx upgrade` / `restructure` on Sean's real vault; do not copy personal trigger tables, employer org names, or Cursor slug tables into templates; never emit `.cursorrules` / `.windsurfrules` / `.clinerules`.
- **Agent thread:** Cursor Grok 4.6 / Cursor / Work MBP (2026-09-17 session-end).

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

## v0.2 roadmap (12 asks → 7 phases; plan approved 2026-07-27)

Plan file: `~/.claude/plans/valiant-toasting-pumpkin.md`. Phased, low-risk first, sign-off between
phases. Locked decisions: ingestion = consent+quarantine+scan; project adoption = reference-in-place
(move optional); GitHub = mirror the SSH-alias + repo-local model; auto-push = personal-solo ONLY.

- **Phase 1 — GitHub work/personal dual-auth + first push (asks 8–11): ✅ DONE 2026-07-27.**
  New `gitscope.py`. `profile.context` = personal-solo|work (gates every side-effect; migration
  retro-adds it). Remote→scope→identity map in `context/remotes.json` (JSON sidecar — `yamlio`
  can't round-trip a list of maps). `wsx remote <url> --scope personal|work` refuses one identity
  spanning both scopes / one URL across scopes (non-overlap enforced). `wsx ssh-setup` appends SSH
  host-aliases (`github.com`/`github-work`), never overwrites, idempotent. `wsx identity --scope`
  applies **repo-local** name/email (never global, never `-c user.*` — the documented leak vector).
  `wsx push` finalizes auth with first commit+push, **gated to personal-solo** (work refuses →
  branch/PR/review). `wsx collab <account>` prints (never runs) the `gh` command to add a work
  account to the private personal repo. `sync` now signs by scope. Brain close-out + interview
  updated to capture context/scope and drive the new flow. All guards + gates tested; zips rebuilt.
- **Phase 2 — examine-before-interview / additive augmentation (ask 12): ✅ DONE 2026-07-27.**
  New `examine.py` (READ-ONLY). `wsx examine [--json]` maps each interview movement (M0–M5) to the
  profile fields it fills and reports answered vs still-pertinent (so the brain asks ONLY the gaps,
  never re-asks), plus missing scaffold, the hub/spoke/project inventory (don't re-propose), and
  broken connections (orphans/dangling — reuses `health` helpers quietly). Apply is `wsx upgrade`
  (non-destructive) + targeted `wsx profile set`. Verified additive: on a partial+degraded vault,
  augmentation preserved the answered profile, a user note, and its `refutes` edge verbatim while
  restoring HOME + knowledge scaffold. Brain "update existing workspace" branch now examines FIRST,
  asks only pertinent movements, augments additively. Optional-empty M3/banned don't count as gaps.
- **R1 — richer neutral scaffold + numbered taxonomy as the default: ✅ DONE 2026-07-27.**
  New `layout.py` = the taxonomy source of truth (logical→numbered map; `Layout` resolver is
  numbered-canonical, flat-fallback so legacy workspaces keep working until R2; `remap()` routes
  template keys). `wsx init` now scaffolds the numbered comprehensive model: `01-frameworks`
  `02-shared-references` (epistemic-standards) `03-skills` `04-preferences` (user-preferences,
  promoted from profile) `06-context` (+ **memory system**: typed fact/decision/feedback/reference
  `_TEMPLATE` + `MEMORY.md` index) `07-projects` `08-knowledge` `09-tools`. `00-bootstrap`/
  `05-artifacts` are OPTIONAL (not scaffolded). Every module rewired through `layout` (16 files);
  adapters resolve dir tokens at emit via a lookbehind-guarded substitution (protects `.claude/skills/`);
  emitted MCP server + hooks detect layout at RUNTIME (survive R2). **Automation ported neutrally,
  data-driven off frontmatter (zero hardcoded content):** `registry.py`→`skills.registry.json`;
  UserPromptSubmit **trigger-router** hook (auto-surfaces skills/knowledge on their own declared
  triggers); **SessionEnd audit** hook; `related.py` build-related (typed `## Related` from hub graph,
  marker-delimited idempotent); `09-tools/{build-registry,build-related,validate,check-terminology}.py`.
  Excluded per privacy wall: Sean's trigger tables, machine labels, employer profiles, Figma gate,
  snds naming. `examine_foreign` verdict retuned (thinner→migrate-up; exceeds→don't-downgrade).
  **Tested:** py_compile clean; init→emit→verify/health/lint GREEN on fresh numbered AND legacy-flat
  (upgrade adds pieces at flat paths, no numbered siblings, hand-note preserved); router/build-related/
  validate/session-audit all functional on both layouts + idempotent; 3 zips rebuilt + clean-extract
  smoke green (numbered taxonomy, tools, hooks, registry); Sean's `check-terminology.py` clean
  (used copy-in / copied-in for *our* CLI — still correct after the 2026-07-30 vendor-term
  correction; engineering "vendored" is for external code in-tree, not self-owned tooling);
  examine verdicts correct on Sean's real vault (exceeds) and a thin fixture (migrate-up).
- **R2 — full restructure migration for existing flat workspaces: ✅ DONE 2026-07-27.**
  New `restructure.py` + `wsx restructure` (the highest-risk op, built defensively). **Dry-run by
  DEFAULT** (`--apply` required to write). On apply: snapshots the flat dirs + changed config to
  `_archive/pre-restructure-<stamp>/` (+ `migration.json`); moves each flat dir → numbered via
  `shutil.move` then `git add -A` (git records them as RENAMES — history follows); reindexes the
  manifest (skill paths → numbered); rewrites **every path-encoding reference** segment-by-segment —
  md-link/image-embed targets (incl. `../skills/…` cross-dir relatives) AND **Dataview `FROM "dir/…"`
  queries** (the gap caught in review: project `board.md` kanban queries; protects `.claude/skills/`
  and other generated dirs; wikilinks/typed-edges are basename-resolved so untouched) +
  `.gitignore`/`.gitattributes`; runs `upgrade` to fill the new-core dirs a flat vault lacked;
  re-emits every adapter/hook/index/registry; then **verify + health**.
  **HARD-REQUIREMENT GATE (Sean's "must not break AT ALL"):** it snapshots every functional reference
  BEFORE touching anything and re-resolves them all AFTER; a baseline-diff flags any reference broken
  ONLY post-rewire → **auto-rollback, applies nothing**. A full **change ledger** lands in
  `migration.json` (dirs moved · files rewritten · pre-existing-broken vs breaks-introduced=[]).
  `--rollback` restores flat from backup. **Idempotent** (no-op on numbered); **refuses** ambiguous
  flat+numbered coexistence. Also fixed this turn: `build-related` now emits **resolving path-links**
  (`[x](../x/SKILL.md)`) not dead `[[SKILL]]` wikilinks, is wired into `upgrade` so existing vaults
  GAIN the typed graph, and **skips any hand-authored `## Related`** (never clobbers/duplicates).
  **Proven:** flat fixture WITH a project board → `FROM "projects/x"`→`FROM "07-projects/x"`,
  cross-dir md-links rewired, hand-`## Related` untouched, typed edge preserved, git renames, verify/
  health GREEN, ledger `breaks_introduced: []`; the gate directly demonstrated to FIRE + roll back on a
  simulated break; rollback restores flat + board query + verify GREEN; re-run no-op. Zips rebuilt;
  clean-extract exposes `restructure`; check-terminology clean.
- **P3 — session-end that generalizes + saves everywhere (ask 5): ✅ DONE 2026-07-27.**
  `lifecycle.session("end")` now writes an **attributed** fragment — Agent · Surface · Machine
  (hostname default) · Project(s) — with a richer block (Summary/Artifacts/Decisions/Knowledge/Next)
  via new `wsx session end --summary/--next/--surface/--agent/--project`; folds it via `compact`; and
  **surfaces the judgment work still owed**: lists every open `PROJECT.md` handoff to update, or points
  to `open-threads.md` when no project is active, plus the knowledge-harvest reminder. New scaffold
  `06-context/open-threads.md` (non-project loose ends; HOME-linked; added to legacy vaults by `upgrade`).
  Emitted **session-end SKILL** (`.claude/skills/session-end/`, triggers "wrap up"/"done for today"/…) —
  the neutral 8-step close-out: harvest generalizable insight → `knowledge/`, update every open project
  handoff, loose ends → `open-threads.md`, record durable decisions → memory/ADR, then `wsx session end`
  + `sync`. AGENTS.md/CLAUDE.md session-end prose enriched so agnostic surfaces get the generalize-then-
  record behavior too. **Tested:** both branches (open project → lists its handoff; none → open-threads),
  attributed block folds correctly, green on fresh numbered AND legacy flat (open-threads + skill resolve
  to the right dir), zips rebuilt + clean-extract ships the skill, check-terminology clean.
- **Identity anchor (pre-P4, from Olga's live confusion): ✅ DONE 2026-07-27.** Olga asked her
  Claude "are you connected to my 2nd-brain workspace?" and it hedged — surfacing the enterprise
  connectors (Notion/Confluence/Drive/Slack/…) as "the second brain" instead of her generated vault.
  Fix: every workspace now **asserts its own identity** so any tool/LLM binds "workspace / second
  brain / 2nd brain / micro-brain / my notes / my vault / gather across my work" to **THIS vault by
  default**, never a commercial connector unless the user explicitly names one. Neutral
  `_identity_anchor(profile)` injected near the top of CLAUDE.md · AGENTS.md · .cursor rule ·
  context-pack, into the always-injected `CRITICAL_FACTS.md` (new workspaces) + the SessionStart hook
  standing-rules, the README front-door, and the emitted MCP server's boot context (CRITICAL_FACTS now
  leads CORE_CONTEXT). Overridable per the user's explicit direction. Tested: anchor present + name-
  interpolated across all 8 surfaces; MCP `session_start` surfaces it; verify/health/lint green; zips
  rebuilt; terminology clean.
- **P4 — adopt existing projects, reference-in-place (asks 3,4): ✅ DONE 2026-07-27.**
  `wsx project adopt <path> [--move] [--import-docs]` (projects.py). Default **reference-in-place**:
  detects git repo (remote/branch) or plain folder, scans stack/README/docs (skipping build+vcs
  noise), writes/updates a marker-delimited **adoption record** in `PROJECT.md` pointing at where the
  code lives — **a git repo's files are NEVER copied** into the (public) vault (reference-only, honoring
  the employer/public-repo wall). `--import-docs` copies a **plain** folder's loose docs into `notes/`
  with provenance headers and **skips secret-like files** (`.env`/`.pem`/`id_rsa`/…); refused for git
  repos. `--move` git-aware-relocates the project to sit **beside** the vault (keeps the vault a clean
  git citizen), `.git` intact. **Idempotent** (re-adopt refreshes the record + skips already-imported
  docs, no dupes). Registers in the projects MOC + HOME. **Tested:** git repo (0 files copied,
  remote/branch/stack captured, import refused) · plain folder (docs imported, `.env` skipped,
  provenance) · idempotent re-adopt (notes stable, 1 adoption block) · `--move` (relocated beside vault
  w/ .git) · verify/health/lint green · zips + clean-extract adopt works · terminology clean.
- **P5 — per-tool memory bridge + multi-agent accommodation (asks 6,7): ✅ DONE 2026-07-27.**
  New `bridges.py` + `wsx bridge list|extract|point` over a per-tool registry (Claude Code, Codex,
  Gemini, Cursor, Copilot, Windsurf, Continue, Cline, Roo, Aider, ChatGPT/Claude-desktop, Perplexity),
  reusing `scan` detection. **extract** copies a tool's own memory/instructions into
  `.wsx/quarantine/<tool>/` **read-only + manifest** — gitignored, never promoted (the consent-gated
  ingestion pass scans/classifies it later); **skips secret-like files** (`.env`/`token`/`.key`/…) and
  non-text. **point** writes an **idempotent, marker-delimited workspace pointer** into a tool's OWN
  global config (`~/.claude/CLAUDE.md`, etc.) so it re-anchors here on every session — reinforcing the
  identity anchor beyond the vault dir; tools without a safe global config get honest guidance. Never
  clobbers; only writes when the tool's config dir exists. **Multi-agent:** `SessionID` now namespaced
  per **Agent·Surface·Machine (+ pid)** so parallel agents write DISJOINT fragment files (proven: two
  concurrent processes with identical agent/surface/machine at the same second → distinct SessionIDs;
  two parallel `session end` both fold, 0 loss). The always-on re-anchor contract (alwaysApply cursor
  rule + CLAUDE.md + hooks + MCP + identity anchor + bridge pointer) covers dynamic model swaps.
  `.wsx/quarantine/` gitignored in the scaffold. **Tested** with a FAKE HOME (never touched real
  configs): extract stages memory + skips `.env`; point is idempotent (1 block after 2 runs) + preserves
  existing content; green; zips + clean-extract; terminology clean.
- **Command cheat sheet + self-sufficiency guarantee (pre-P6): ✅ DONE 2026-07-27.** New `commands.py`
  = ONE source of truth → `wsx help` (terminal) + a generated **`COMMANDS.md`** in the workspace (linked
  from HOME, regenerated by write_mocs on init/emit/upgrade), so a user OR an LLM always has the full
  command set (`bridge list`, `diagnose`, …). Every command runs from the workspace's copied-in `.wsx/`
  CLI with no install; to GUARANTEE that, `copy_cli` now also copies `schemas/` into `.wsx/schemas/`
  (any generator asset the CLI references travels with the workspace). `wsx help` command added.
- **Error-reporting + correction mechanism for existing workspaces (pre-P6): ✅ DONE 2026-07-27.**
  New `diagnose.py` + `wsx diagnose [--fix]`: a preflight over an EXISTING workspace that turns a
  malformed file into a reported FINDING (not a crash) — checks workspace marker, layout (flat→migrate),
  missing scaffold, integrity (profile/manifest round-trip), manifest↔disk skill drift, emitted adapters,
  graph (orphans/dangling typed edges), **references (md-links + Dataview `FROM` resolve on disk — the
  piece `health` misses)**, self-sufficiency (copied CLI + version), and git (repo/commits/identity/
  remote). Each finding carries a one-line fix. **`--fix` applies only SAFE, non-destructive corrections**
  (upgrade → emit → reindex) and does a **before/after baseline-diff of every reference** to confirm the
  correction didn't INTRODUCE a broken link — answering "do the connections still map after we edit?"
  (proven: catches a broken md-link health missed; --fix introduces no new breaks; distinguishes
  auto-fixable from needs-a-hand). **`wsx init` hardened**: pointed at an existing wsx workspace it
  REFUSES + redirects to diagnose/upgrade/restructure (never clobbers); a foreign workspace → examine.
  Maintenance skill now leads with `diagnose`. Fixed a `#stale` false-positive (COMMANDS.md exempted
  from the graph). Green; zips; terminology clean.
- **P6 — consent-gated ingestion (ask 1): ✅ DONE 2026-07-27.** New `secretscan.py` (the GATE:
  OpenAI/Anthropic/AWS/GCP/GitHub/Slack/Stripe/Twilio/SendGrid keys, private-key blocks, JWTs, and
  env-style secret assignments → **block**; public/WAN IPs → **review**; placeholders + private IPs
  ignored; matches redacted; **safe-by-default** — a false positive over-quarantines, a false negative
  is unacceptable) + new `ingest.py` + `wsx ingest discover|<path> [--apply]`. Flow: **discover**
  (top-level-only scan of Documents/Desktop/Projects/note-vaults + per-OS **cloud-sync roots** —
  locally-synced only, NO deep crawl so an online-only cloud folder can't hang it) → name a source →
  **read-only copy to `.wsx/quarantine/ingest/`** (gitignored) → **secret-scan (block hits — never
  staged)** → **classify** (project → reference-in-place `adopt` PROPOSAL, never copied; knowledge;
  framework-candidate by content/name hints; raw) → PLAN → **`--apply` promotes only the safe docs**
  into `<knowledge|frameworks>/ingested/` (provenance + review banner + a reachable `_INDEX.md`; won't
  collide with scaffold; idempotent). Nothing enters git until the person reviews + `sync`s. Doubly
  consent-gated (name the source, then `--apply`). scan._search_roots extended with cloud roots.
  **Verify (exact plan fixture): planted API key + a note + a project folder → key caught & quarantined
  (0 hits anywhere in the vault), note→knowledge, principles→framework-candidate, folder→project
  proposal (app.py NOT copied), nothing auto-committed; green; discover 0.1s; zips + clean-extract ship
  secretscan+ingest; terminology clean.** (Gotcha noted: a reused test workspace runs its STALE `.wsx`
  copy — always test ingest changes on a FRESH init or after `wsx upgrade`.)
- **P7 — self-wiring, generator-independent (ask 2): ✅ DONE 2026-07-27. FINAL PHASE.** New `wire.py`
  + `wsx wire`: a discovery-driven pass over a declarative **wiring-intent registry** (`INTENT`:
  dir-kind → {home, index, registry, trackable}). It finds anything loose — **unanticipated top-level
  content dirs** the taxonomy doesn't own, un-indexed skills, dirs accidentally gitignored — and wires
  each to every destination the registry implies: gives it an `_INDEX.md` (notes reachable), links it
  from a discovery-driven **HOME "Other areas"** section (moc.write_home now calls `wire.discover_extras`),
  adds a `!<dir>/` **gitignore whitelist** negation if it was ignored, reindexes skills, and re-emits
  all adapters/hooks/tools. Idempotent; runs off the **copied-in `.wsx` CLI with NO generator present**.
  Wired into `diagnose` (reports unwired dirs; `--fix` runs wire). **Verify (exact plan fixture): an
  unexpected `10-research/` with a note → wire linked it from HOME + created its `_INDEX` + (when the
  dir was gitignored) whitelisted it; re-run a no-op; green; generator-independent (`.wsx/wsxlib/wire.py`);
  clean-extract self-wires; fresh-init sweep clean (worst 0.17s); terminology clean.**

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

_Older entries are in [history/](history/), by month; the app's Projects timeline joins them with this file._

_Newest first._

_Prior stamp (superseded 2026-09-17): 2026-07-27 — v0.2 R1 shipped (numbered taxonomy as the generator DEFAULT + neutral automation port); earlier: colleague-feedback pass ( broader `wsx scan` detection incl. ChatGPT/desktop chat apps, connective **MOC layer** so the emitted vault graph is no longer islands, `projects/` per-project documentation tree + `wsx project`, and `wsx upgrade` corrective pass for already-generated workspaces; earlier: permission-free `launch.py` + per-OS zips, scan gate + BYO-tokens, authoring framework, `wsx remote`, expertise calibration, two-track sourcing, emit mcp, Resolver Phase 2, turn-key Path A)_

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

