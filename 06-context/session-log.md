# Session Log — Sean Sands
_Authoritative source: this file (06-context/session-log.md)_
_Written by any agent at session end — the git checkout is the source of truth._
_Entries: newest first._

---

## How This Works

**Any agent reads this at boot** to surface pending items and last session context.
**Any agent writes to this** at session end — no manual paste needed; git is the source of truth.
**Reconciliation** ("reconcile sessions") merges blocks from concurrent sessions
into a single update, then writes the result here automatically.

Keep entries concise. This is a handoff log, not a journal.

---

## Session Entries

> _Older entries archived to [session-log-archive.md](session-log-archive.md) to keep this file cheap to read. Ask to see it only if you need history._


> _Older entries archived to [session-log-archive.md](session-log-archive.md) to keep this file cheap to read. Ask to see it only if you need history._


> _Older entries archived to [session-log-archive.md](session-log-archive.md) to keep this file cheap to read. Ask to see it only if you need history._


---

### 2026-07-28 — Component contracts & schemas: framework §5a, portable model v0.2, SaaS DataTable plan

SessionID: 2026-07-28-csk746-contracts

--- SESSION BLOCK ---
Date: 2026-07-28
Agent: Claude Opus 5 (1M context)
Machine: Work MacBook Pro
Surface: Cursor (Claude Code extension)
Project(s): Design-system foundations (framework #09 + knowledge/reference layer); SaaS PLM prototype
  DataTable → TanStack replacement (employer — cpes-software/saas-plm-prototype; deliverables land in
  the employer repo, NOT mirrored here per the separation rule)
Artifacts:
  - saas-proto_datatable-contract-plan_v1.0_2026-07-28.md — DataTable contract skeleton, three-phase
    testimony→contract→signatories shape, per-phase gating criteria, TanStack boundary (machine-local,
    05-artifacts is gitignored)
Decisions:
  - Adopted the contract/schema layer from Nathan Curtis (2026-07-28) + 4 peer sources: a description
    informs, a contract ARBITRATES; Figma is a signatory, not the source; version schema and spec
    separately. Seven principles restated as pass/fail GATES.
  - Framework #09 gains §5a (the contract layer) rather than a new framework — it is a specialization
    of the existing 18-facet schema, not a peer to it. Facets 1–17 inform; facet 18 arbitrates.
  - §8d state model corrected: separating interaction/configuration/validation/selection was necessary
    but insufficient — every state must also be classified browser-driven (hover/active/focus →
    pseudo-class, OMITTED from the props interface) vs consumer-controlled (disabled/selected/expanded
    → ARIA, in the interface). One classification drives both styling and API surface.
  - C8 dgrid→TanStack work DEMOTED to supplementary for all SaaS SMB work (Sean's call). A legacy
    feature inventory is testimony too; a contract derived from it can only specify a re-creation.
    Roles retained: pitfall ledger · effort calibrator · parity horizon, consulted AFTER the draft.
    Gate: every feature cites a user job, UX spec, or canon pattern.
  - Growth horizon (Sean's call): SMB is the ENTRY POINT, not the ceiling. Scope down, don't shape
    down — SMB sets the spec, the enterprise horizon sets the schema. Operative rule: MODEL THE AXIS,
    SHIP ONE VALUE ON IT. Capability and entitlement stay orthogonal (tier boundaries move — the Figma
    variable-mode-limits pattern), so packaging never goes in a component contract.
  - Scoped OUT deliberately: no generator, no differ, no ADR log for the table migration — the
    mid-size capacity trap ("both need it, the middle and the top; only one can run it").
Knowledge written:
  - 08-knowledge/design/component-contracts-and-schemas.md — definitions, the seven gates as tests,
    investment gate, L0–L4 ladder, the wider field (Curtis/Specs · Vallaure/DS Contracts · Morales
    Achiardi · Pitre · Onori/DSDS) + reconciliations, techniques worth stealing, §8 replacement rule,
    §9 growth-horizon rule, standing rules. Indexed with 22 triggers.
  - 02-shared-references/component-contract-schema.md — portable model v0.2: constitution (type–schema
    symmetry · no runtime logic · stable API), typed model, state classification, variant-delta
    layering + resolution algorithm, invalidPropConfigurations, $binding/$ref/$extensions conventions,
    neutrality recipes, verification L1–L6 (incl. three-way differ), declared-heuristic rule, ADR
    template, adoption path, format landscape.
Pending added:
  - SaaS PLM prototype DataTable contract → TanStack replacement (full context + first three moves in
    project-context.md). Survey @ 6380a26: 16 files render `<table>` across 11,784 lines; MaterialsTable
    1,320 lines / 20+ props; 2 aria-* and 0 role=/tabIndex across the six core table files; no
    virtualization, no pagination, zero table tests.
Deferred commits:
  - .claude/hooks/dispatcher.py · 02-shared-references/delivery-playbooks/README.md ·
    03-skills/pm-discovery-research/SKILL.md · 03-skills/ux-interaction-design/SKILL.md ·
    03-skills/skills.registry.json — pre-existing dirty files, NOT from this session; left for their
    owning session (see Step 7.5 note below).
Next:
  - Table work, in order: (1) classify all 16 `<table>` surfaces as component/recipe/snowflake/
    not-a-table; (2) pin the 6 load-bearing behaviors with tests against the CURRENT implementation
    (after the port, "equivalent" stops being testable); (3) author datatable.contract.yaml resolving
    every feature's state `owner` and every §6.4 headroom axis. Only then start the port.
  - Feature list derives from saas-plm-analysis/knowledge-discovery (ux/flows, ui/specs) + SMB jobs +
    the pattern canon — cross-read, never copy across the employer boundary.
--- END BLOCK ---

---

### 2026-07-28 — /doctor triage + workspace-doctor MISS ack (Work MBP main)

SessionID: 2026-07-28-csk746-doctor

--- SESSION BLOCK ---
Date: 2026-07-28
Machine: Work MacBook Pro
Surface: Claude Code CLI
Project(s): Workspace machine-layer maintenance
Decisions:
  - /doctor MCP connectors (claude.ai HyperFrames by HeyGen, Microsoft 365) left as-is — unauthenticated but harmless OAuth connectors; not authenticating or disconnecting (Sean's call).
  - Beacon-enroll NOTEs left untouched: Projects/workspace = case-mismatch false positive (repo flags itself); Projects/design-system = employer (bitbucket/centricsoftware) → must stay OUT per standing rule; Projects/open-design = non-personal org (github.com/nexu-io) → needs classification before any enrollment.
Actions:
  - workspace-doctor --check on Work MBP main (CS-K746DRWXY1): all layers healthy, zero drift (hooks, settings.json, launchd timer, managed dist files).
  - Acked 13 historical MISSes (chaos canary + 2026-07-09 FX-session employer/parent-dir/headless runs + pre-0fb7c15 ritual/ABI mismatch). ack-mark=2026-07-28T08:34:56; re-check clean.
Pending added:
  - Optional: record Projects/design-system + Projects/open-design in 00-bootstrap/dist/beacon-repos.ignore.txt to silence recurring doctor NOTEs (or enroll open-design if personal).
Next:
  - Other machines (Work MBP loaner, Windows Enterprise): run workspace-doctor + machine-layer installs per existing pending item.
--- END BLOCK ---

---


### 2026-07-27 (pt.2) — upgrade-safety, thin adapter, and captured voice/tone prefs

SessionID: 2026-07-27-voyager-upgtest
--- SESSION BLOCK ---
Date: 2026-07-27
Machine: Personal MacBook Pro
Surface: Claude Code (Mac desktop app)
Project(s): 18-bootstrap-generator, (workspace: 04-preferences)
Summary: After v0.2 feature-complete, ran a copy-test of `wsx upgrade` against a full copy of
  ~/Projects/Workspace (801M, discarded) to find what it would do to a rich hand-built vault.
  Cataloged the negative outcomes and fixed them, then built the thin adapter, then captured
  Sean's real communication preferences.
Artifacts:
  - generator A (upgrade safety, commit b9252a5): A1 registry.build never clobbers a foreign
    skills.registry.json (writes .wsx.json alongside); A2 no fabricated placeholder profile;
    A3 build-related no longer auto-edits skills on a foreign vault (gated on the foreign flag
    captured BEFORE copy_cli creates .wsx/); A4 upgrade detects a not-wsx-generated rich vault
    and REFUSES (mirrors examine's don't-downgrade; --force overrides).
  - generator B (thin adapter, commit 6699bf0): new adapter.py + `wsx adapter [path]` maps a
    foreign vault's folders→wsx concepts (.wsx/adapter.json, reference mode) + copies the CLI.
    core.find_workspace_root recognizes an adapted vault. REFERENCE-MODE guards: upgrade refuses,
    adapters.emit refuses, moc.write_mocs builds only registry.wsx.json, wire is additive-only —
    so wsx never overwrites _HOME.md/AGENTS.md/CLAUDE.md/registry. Read-only tools (examine/health) work.
  - generator addendum (commit 1a005c2): voice/tone is now first-class — scaffold preferences
    template gains Voice + "Never do these" + Teaching-altitude sections; CLAUDE.md/AGENTS.md +
    the bridge pointer point every LLM at preferences/user-preferences.md as governing.
  - 04-preferences/user-preferences.md (commit 230a340): captured Sean's real prefs — anti-patterns
    (incl. the "honest assessment" tell), sociable-professional voice w/ practicality + light
    sarcasm (never over-index), thorough-when-it-matters, design-relative teaching + optional-source rule.
Decisions:
  - Do NOT run `wsx upgrade` on Sean's real vault — examine says it exceeds the model; upgrade
    would downgrade/clobber. The right path is the reference-mode adapter, not upgrade.
  - The copy-test found the real defects (registry clobber CRITICAL, junk profile, skill edits,
    HOME collision, scaffold clutter). Fixed all; --force is the only way to scaffold a foreign vault.
Pending resolved:
  - "Correct upgrade's negative outcomes so it's safe on an existing vault" — done (A).
  - "wsx thin adapter as a map for the future" — done (B).
  - "Help me create a profile + interactive voice/tone that adjusts all LLMs" — prefs captured +
    generator mechanism built. (Full `wsx profile init` from-context flow still TODO.)
Next:
  - Optional: `wsx adapter ~/Projects/Workspace` to run wsx read-only tooling on the real vault
    (drops a .wsx/ into the repo — Sean's call). Build `wsx profile init` (reconstruct a full
    profile from existing context). Colleague/Olga re-test of v0.2 + the adapter path.
--- END BLOCK ---

### 2026-07-27 — bootstrap-generator v0.2 COMPLETE (R1, R2, P3–P7 + tester-driven additions)

SessionID: 2026-07-27-voyager-p7done
--- SESSION BLOCK ---
Date: 2026-07-27
Machine: Personal MacBook Pro
Surface: Claude Code (Mac desktop app)
Project(s): 18-bootstrap-generator
Summary: Shipped the ENTIRE v0.2 roadmap for the bootstrap generator (wsx) — the generator's
  default target is now Sean's comprehensive model, kept effortless to use, with a hard "never
  break an existing workspace" guarantee. 14 commits, all phases built + tested (fresh-init) +
  committed. R1: numbered-taxonomy default (00–09) + memory system + neutral automation port
  (trigger-router hook, registry, build-related, SessionEnd audit) via a single-source layout.py
  resolver (numbered-canonical, flat-fallback). R2: flat→numbered migration with a baseline-diff
  broken-reference GATE (auto-rollback, change ledger) + build-related path-link fix. P3:
  session-end that generalizes (harvest→knowledge, update every PROJECT.md, open-threads) +
  emitted session-end skill. P4: `project adopt` reference-in-place (repo files never copied;
  --move/--import-docs). P5: per-tool memory bridge (extract→quarantine, point→re-anchor) +
  multi-agent SessionIDs (Agent·Surface·Machine·pid). P6: consent-gated ingestion + secretscan
  (block credentials before a PUBLIC repo). P7: `wsx wire` self-wiring off a wiring-intent
  registry, generator-independent. Plus tester-driven: identity anchor + cross-session auto-orient
  (Olga's two confusions), command cheat sheet + self-sufficiency, `wsx diagnose [--fix]`
  error-reporting/correction with full reference-integrity traversal, and a find-workspaces
  cloud-walk fix.
Artifacts:
  - 07-projects/18-bootstrap-generator/generator/wsxlib/ — NEW: layout · registry · related · tools ·
    restructure · diagnose · commands · secretscan · ingest · bridges · gitscope · examine · wire (13
    new modules) + ~16 rewired (adapters/scaffold/moc/core/health/upgrade/lifecycle/projects/…).
  - dist/*.zip rebuilt each phase (gitignored; not committed).
  - Generator commits: 60a4ac4 → 1d2b4f1 (14). Working tree clean.
Decisions:
  - Hard requirement (Sean): running the generator against an existing workspace must NOT break it —
    enforced by a baseline-diff broken-reference gate (restructure + diagnose --fix), auto-rollback,
    change ledger. Proven to fire on a simulated break.
  - Repos are REFERENCED, never copied into the (public) vault — the employer/public-repo wall; ingest
    secret-scans + blocks credentials; nothing auto-committed.
  - Testing discipline: verify CLI changes on a FRESH init (or after `wsx upgrade`), never a reused
    instance — the copied `.wsx` CLI goes stale and masks fixes/regressions (cost hours as a phantom "hang").
Pending resolved:
  - v0.2 roadmap (all 7 phases + the ingestion/adoption/dual-auth/self-wiring asks) — DONE.
Project status changes:
  - 18-bootstrap-generator: v0.2 phases 1–2 (dual-auth + examine) → v0.2 FEATURE-COMPLETE (R1,R2,P3–P7).
Next:
  - Colleague/Olga re-test of the full v0.2 (esp. bridge point for auto-orient, restructure on a real
    flat vault, ingest on a real notes folder). Possible follow-ups: bump __version__ so diagnose's
    stale-copy check has a signal; consider health scanning wired extras. Ship-as decision (SPEC §9)
    still deferred (standalone wsx repo extract).
--- END BLOCK ---


### 2026-07-27 — bootstrap-generator v0.2: dual-auth + examine; roadmap reshaped to "richer default"

SessionID: 2026-07-27-voyager-8a4d9d
--- SESSION BLOCK ---
Date: 2026-07-27
Machine: Personal MacBook Pro
Surface: Claude Code (Mac desktop app)
Project(s): 18-bootstrap-generator
Summary: Kicked off generator v0.2 (12 colleague/Olga asks → 7 phases, planned in EnterPlanMode with 4 locked decisions). Built + tested + shipped Phase 1 (GitHub work/personal dual-auth) and Phase 2 (examine-before-interview, incl. a foreign-workspace mode). Then Sean redirected the whole direction: the generator's DEFAULT should become his comprehensive workspace model (numbered taxonomy + frameworks + memory system + shared-references + the automation), kept simple to USE (automate everything, modularize complexity) — plus a full restructure migration for existing wsx workspaces. Roadmap reshaped accordingly; paused before R1 to checkpoint.

Artifacts:
  - generator/wsxlib/gitscope.py — NEW: work/personal GitHub separation. remote→scope→identity map in context/remotes.json (JSON sidecar; yamlio can't round-trip a list of maps). Non-overlap guards (one identity per scope; one URL per scope). SSH host-alias scaffold (append-only, idempotent). Repo-local identity ONLY (never global, never `-c user.*` — the documented leak vector). first_push gated to personal-solo (work refuses → branch/PR). collab prints (never runs) the gh command.
  - generator/wsxlib/examine.py — NEW: read-only. wsx examine maps interview movements (M0–M5) → profile fields → answered vs pertinent (ask only gaps), missing scaffold, inventory, broken connections. PLUS foreign-workspace mode (examine <path>) that maps a non-wsx layout onto the wsx concepts. Tested live on Sean's own workspace: 6/6 concept coverage, correctly judged as exceeding the generator.
  - generator/wsxlib/{cli,lifecycle,scaffold,upgrade}.py, schemas/profile.schema.json — profile.context (personal-solo|work) gates side-effects (+ migration retro-adds it); sync signs by scope; CLI wires remote --scope / identity --scope / push / ssh-setup / collab / examine.
  - brain/SKILL.md + interview.md — update-existing-workspace branch now EXAMINES first, asks only pertinent movements, augments additively; close-out drives the dual-auth + first-push flow; interview captures context/scope + dual-scope non-overlap.
  - DEVELOPING.md — module list + command table for the new surface.
  - dist/*.zip — rebuilt each phase (gitignored; not committed).
Decisions:
  - v0.2 locked (with Sean): ingestion = consent+quarantine+scan; project adoption = reference-in-place (move optional); GitHub = mirror the SSH-alias + repo-local model; auto-push = personal-solo ONLY; delivery = phased, sign-off between phases.
  - MAJOR REDIRECT (2026-07-27): generator default → Sean's comprehensive model (#2), but comprehensiveness in the WORKSPACE not the user's effort (automate, prompt-only-when-necessary, modularize complex parts). Existing wsx workspaces get a FULL RESTRUCTURE migration into the numbered layout. Constraint: neutral scaffolding only — never Sean's actual content (wall intact).
  - The automation/scripts/processes ARE in scope for the port, neutrally. Clean because triggers/routes are frontmatter/registry-declared (Sean's own single-source rule) → the machinery is data-driven off the person's OWN workspace, zero hardcoded content. Excluded: curated trigger tables (legion/centric), machine labels, employer profiles, Figma gate, snds plugin naming.
  - remotes.json chosen over profile.yaml for the remote map (structured data; minimal yamlio can't serialize a list of maps).
Pending resolved:
  - Phase 2 tested on Sean's real workspace (his explicit ask) — foreign-examine works, verdict honest.
Next:
  - R1 — richer neutral scaffold + numbered taxonomy as the generator default (rewire moc/adapters/health/wire/examine to new dirs; port the automation neutrally, core vs optional per Sean's modularization). Then R2 — full restructure migration (dry-run + backup + rewire + verify + rollback; highest-risk op). Then fold in P3 session-end / P4 project-adoption / P5 tool-memory-bridge+multi-agent / P6 ingestion / P7 self-wiring.
  - Retune examine_foreign verdict for the new direction (thinner foreign → offer migrate-up; exceeds-target → still "don't downgrade").
  - Full reshaped plan: ~/.claude/plans/valiant-toasting-pumpkin.md (living design doc).
--- END BLOCK ---


### 2026-07-23 — bootstrap-generator colleague-feedback pass + obsidian-second-brain learnings (both trees)

SessionID: 2026-07-23-voyager-558e3d
--- SESSION BLOCK ---
Date: 2026-07-23
Machine: Personal MacBook Pro
Surface: Claude Code (Mac desktop app)
Project(s): 18-bootstrap-generator; workspace foundation (frameworks/context/knowledge/tools)
Summary: Acted on colleague feedback for the `wsx` generator (detect ChatGPT/all LLM tools; connect the emitted graph; add a project-docs dir; corrective pass for existing workspaces), then folded ALL learnings from a review of github.com/eugeniughelbur/obsidian-second-brain into BOTH the generator and Sean's live workspace, plus workspace auto-discovery. Rebuilt the per-OS distribution zips. Closed the /health-spawned orphan task.

Artifacts:
  - generator/wsxlib/moc.py — NEW: Maps-of-Content link layer (HOME + skills/projects indexes) that reconnects the emitted vault graph (root cause: every skill file is SKILL.md, so hub/framework refs were code-spans/bold, never links)
  - generator/wsxlib/projects.py — NEW: `wsx project new|list` — per-project DOCUMENTATION folders (docs/context only, not code/assets) + Dataview-ready board.md
  - generator/wsxlib/upgrade.py — NEW: `wsx upgrade [--dry-run]` — non-destructive corrective pass over an existing workspace (adds missing scaffold + regenerates MOC layer; never clobbers hand-edits; idempotent)
  - generator/wsxlib/health.py — NEW: `wsx health` — vault graph hygiene (orphans, #stale/aging `as of`, dangling typed edges)
  - generator/wsxlib/scan.py — expanded detection (coding agents + chat/desktop apps incl. ChatGPT via macOS .app + editor-ext globs; more local LLMs) + `--find-workspaces` OS discovery
  - generator/wsxlib/scaffold.py, adapters.py, skills.py, cli.py — CRITICAL_FACTS/conventions/decisions scaffolds, adapter guidance (read CRITICAL_FACTS first + note conventions), hub-linking skeletons, wiring
  - brain/SKILL.md + .claude/skills/bootstrap-gen/SKILL.md — "update an existing workspace" branch (triggers: update/upgrade/fix/course-correct my workspace) → scan --find-workspaces → confirm → wsx upgrade → re-emit → health, WITHOUT re-interviewing
  - dist/wsx-generator-{macos,windows,linux}.zip — rebuilt (~143 KB each); verified from a clean extract (new commands + brain branch present, init→project→emit→health clean)
  - 06-context/CRITICAL_FACTS.md — NEW: tiny always-loaded hot cache; wired as CLAUDE.md load-order item 0
  - 02-shared-references/vault-graph-conventions.md — NEW: typed `relations:` (epistemic graph, knowledge/memory) + `## For future agent` preamble
  - 02-shared-references/nightly-maintenance-recipe.md — NEW: opt-in report-first maintenance routine
  - 09-tools/vault-health.py — NEW: epistemic-graph hygiene (complements validate-links.py which owns the skill graph); whitelisted in .gitignore
  - .claude/skills/health/SKILL.md — NEW: /health command
  - epistemic-standards.md §2, framework #04/#08, memory/_template.md, 08-knowledge/_README.md, _session-state-template.md — freshness rule + typed edges + preamble folded in
Decisions:
  - Two distinct graphs, kept uncrossed: the epistemic `relations:` vocabulary (builds-on/relates-to/contradicts/refutes/exemplifies) governs knowledge/memory notes; the existing skill `## Related` graph (foundation/hub/peer/governed-by, validated by validate-links.py) is untouched. Unifying them is a deliberately deferred, separate reconciliation.
  - `wsx upgrade` is non-destructive and applies by default (--dry-run to preview) — creates only missing scaffold + regenerates the generated MOC layer; never overwrites hand-edited files (Sean's call).
  - The MOC link layer (not per-skill renaming) is the fix for the disconnected graph, since Claude Code requires every skill file be named SKILL.md — path-correct relative links (root-relative from HOME, dir-relative from indexes) draw the Obsidian edges.
  - vault-health orphans/aging are advisory; #stale + dangling typed edges gate the exit code, so a scheduled run can fail on real integrity issues.
Pending resolved:
  - /health-spawned orphan task: linked ds-agents-binding.md from framework #09 (its enforcement layer) and 06-research-and-design-artifacts.md from the delivery-playbooks README (Load order + File map); vault-health now 0 orphans.
Next:
  - Colleague to test the rebuilt zips; feed back.
  - Optional/deferred: unify the two typed-edge vocabularies; wire CRITICAL_FACTS into the SessionStart hook injection; generator template externalization (scaffold TEMPLATES → files).
--- END BLOCK ---


### 2026-07-23 — workspace-doctor pass + /optimize brain audit

SessionID: 2026-07-23-voyager-q9m4
--- SESSION BLOCK ---
Date: 2026-07-23
Machine: Personal MacBook Pro
Surface: Claude Code (Mac desktop app)
Project(s): 19-workspace-brain (workspace meta — doctor + audit)
Summary: Ran workspace-doctor (all layers healthy) and acknowledged 19 stale SessionStart MISSes (12 from out-of-scope MediaSentinel, rest old/resolved workspace sessions — recent tail all OK). Then ran a full /optimize brain audit: 7 findings (P0:0, P1:2, P2:5), 6 fixed, machinery confirmed clean.
Decisions:
  - The 19 bootstrap MISSes were benign (majority from a non-workspace repo where the ritual doesn't apply; workspace sessions since are all OK) → ack to reset the baseline rather than chase them.
Pending resolved:
  - 2026-07-08 audit carry-forward (f): flattened `08-knowledge/research/research/` → `research/` (6 git mv, `_INDEX.md` updated; wikilinks basename-resolved so unaffected).
  - project-context Active Projects now matches the SESSION-STATE set: added "Portable Bootstrap Generator (wsx)" (18) + "CDS Figma–Code Audit" (16) blocks.
  - Pruned 22 resolved `[x]` pending-items → archived to session-log-archive.md; live Active bucket = 36 clean next-actions.
  - Removed stale `_archive/figma-plugin-patterns 2.md` (diff-confirmed strict subset of engineering/figma-plugin-patterns.md).
  - `_Last updated:` bumped 2026-07-15 → 2026-07-23. Audit logged to audit-log.md (clears the 14-day stale nudge).
Pending added:
  - Doctor-sweep generalization for `* 2.md` conflict-copies (item (e)) — one instance cleaned, generalized sweep still open.
Next:
  - Sean-owned (external): REVOKE the 2026-06-04 Figma PAT; GitHub Support request to purge the two centric-ui SHAs carrying the personal email.
--- END BLOCK ---


### 2026-07-23 — Bootstrap generator hardening + workspace multi-session/token-frugality resilience

SessionID: 2026-07-23-voyager-k7x2
--- SESSION BLOCK ---
Date: 2026-07-23
Machine: Personal MacBook Pro
Surface: Claude Code (Mac desktop app)
Project(s): 18-bootstrap-generator (major) + workspace system-layer (concurrency, token-frugality, framework contract)
Summary: Resumed and largely completed the portable bootstrap generator, then hardened THIS workspace for multi-session/multi-device/multi-surface use and token frugality, and propagated every change back into the generator so users get parity. ~26 commits, all gates green, three distribution zips rebuilt.
Artifacts:
  - 07-projects/18-bootstrap-generator/generator/wsxlib/{resolver,search,scan,mcp_template}.py — new: Resolver (pull/patch/generate/composite), source discovery, agent/MCP/local-LLM detection, zero-dep stdio MCP server
  - 07-projects/18-bootstrap-generator/{launch.py,package.py,packaging/} — permission-free launcher (python3 launch.py; no exec-bit/Gatekeeper) + per-OS zip packager + Apple notarization pipeline (prep)
  - 07-projects/18-bootstrap-generator/VALIDATION.md — colleague-facing proofboard
  - 07-projects/18-bootstrap-generator/dist/*.zip — macOS/Windows/Linux packages (gitignored; regen via package.py)
  - 09-tools/compact-sessions.py — new: idempotent session-fragment compaction + log archival
  - 06-context/session-log-archive.md — new: bounded-log archive (live log 200KB→27KB)
Decisions:
  - Expertise is PER-DOMAIN (a separate axis from energy): the same person can be a staff-expert in one craft and a hobbyist in another; each generated skill is written at ITS domain's altitude (hobbyist teaches; expert captures judgment). Schema gained use_context + expertise{}.
  - Resolver is a COMPOSITE builder, not just a skill fetcher: two-track sourcing (skill registries + industry-leading references), cite in the person's voice, never copy — grounded in our own skill-ecosystem knowledge that authored-from-reference beats a shallow pull.
  - Permission-independence = invoke a trusted interpreter on a data file (python3 launch.py), never ship an executable; unsigned macOS double-click can't dodge Gatekeeper without the $99 cert (pipeline prepped, not required). Recommend ~/Documents/Projects/Workspace (Documents → iCloud/backup).
  - BYO-tokens is architectural: the generator has no API key and makes no model calls; it runs on the user's own agent/account (wsx scan detects the stack; reads MCP server NAMES only, never secrets). If none detected, gate + recommend a surface before the interview.
  - Multi-session model: conflict-free per-session FRAGMENTS + union-merge logs + idempotent compaction + scoped commit (never sweep a concurrent session's WIP) + safe push-retry (autostash pinned OFF → never rebases a dirty tree). Diagnosis first: the auto-sync was non-destructive (re-hashing is cosmetic); hardened the safe defaults.
  - Token frugality is a #1 priority (workspace + generator): bounded/archived logs (O(1) read cost, not O(sessions)), read log heads not whole files, keep auto-loaded files terse. Stated in AGENTS.md core rules, framework 08 principle #6, CLAUDE.md, and every emitted adapter.
Pending resolved:
  - Bootstrap-generator command surface is stub-free (14 cmds); Resolver, emit mcp, turn-key Path A, expertise calibration, hosting, scan+gate, packaging all done + dogfooded.
  - Reconciled the long-standing brain↔schema drift (schema_version "0.2"; lifecycle continuity boolean; automation minimal/standard/full).
  - session-log.md bounded via archival; framework contract (AGENTS.md, fw08) updated to the fragment/frugal model.
Pending added:
  - Deeper wsx doctor self-heal for generated workspaces (re-emit stale adapters, verify .gitattributes) — optional polish.
  - A registry search/discovery index layer (brain currently supplies exact skill urls).
  - Externalize the generator's embedded scaffold templates (incl. the authoring framework + BYO README).
Next:
  - Optional: the doctor-self-heal polish, or drive the generator through a real colleague test.
--- END BLOCK ---


### 2026-07-22 — Game-dev perf doctrine + 4 hero-body rendering skills (Legion-driven)

--- SESSION BLOCK ---
Date: 2026-07-22
Agent: Claude Opus 4.8
Machine: Personal MacBook Pro
Surface: Claude Code (Mac desktop app)
Project(s): 13-legion (workspace skill/knowledge augmentation in service of Legion rendering)
Summary: Augmented the game-dev 3D skill network toward SpaceEngine-class hero-body fidelity. Ran a 16-agent research workflow (5 pillars → adversarial verify → synthesis, ~1.08M tokens, 156 web fetches) → master dossier; authored 4 new spoke skills; then generalized the performance requirement into a project-wide doctrine. Registry 248 → 252; all gates green (registry/related/links/integrity).
Decisions:
  - 4 new lead-game-developer spokes from the adversarially-verified dossier: planetary-terrain-lod, atmospheric-scattering-and-clouds, stellar-and-relativistic-hero-bodies, realtime-render-performance. Load-chain: foundations → hub → perf-spine → body skills (verified).
  - Honest verdicts baked in (not hype): real in-browser budget ~8–9 ms not 11.1; planet+star hit high FPS on desktop dGPU (60+DRS on integrated); black hole = scripted slow-camera hero moment, zero interactive-game precedent; WebGPU has no mesh/tessellation/VRS/fp64 → compute+indirect only; TAAU is a co-dev bet that fails on motion-vector-less content.
  - Generalized performance into a project-wide DOCTRINE (not Legion/90fps-specific): 60 FPS floor (not goal), uncapped by default (higher = smoother + lower latency), optional user frame cap in settings to reallocate GPU / cut power, input latency co-equal. Installed in game-foundations (new "Performance + responsiveness" principle) + lead-game-developer (principle #4). Renamed realtime-render-performance-90fps → realtime-render-performance (git mv; 12 files re-pointed).
  - Marketplace harvest verdict: ~90% duplicative; workspace's new skills supersede the marketplace rendering skills (anthropic-skills:threejs-* are exact dupes). Folded the one additive item (blender-web-pipeline bpy + 3D-texture/VDB-bake path) into 3d-asset-pipeline rather than a duplicate spoke.
Artifacts:
  - 08-knowledge/game-dev/legion-hero-body-rendering-research.md — master research dossier (cited, adversarially verified; §5 skill blueprint)
  - 08-knowledge/game-dev/legion-planet-surface-rendering.md — Legion planet-shader hard-won patterns (hex-artifact fix, ±0.08 treeline threshold, snow/ice, flashing-storm bug, GLSL reserved-word `active`)
  - 03-skills/{planetary-terrain-lod,atmospheric-scattering-and-clouds,stellar-and-relativistic-hero-bodies,realtime-render-performance}/SKILL.md — 4 new spokes
Pending resolved:
  - Deduplicated 3d-asset-pipeline/SKILL.md (merge artifact — whole body was duplicated); merged section-by-section, no content lost, fixed a meters-vs-cm contradiction.
Pending added:
  - Implement the 4 new skills against the live Legion repo (src/render/planet/, src/render/) — reconcile planetary-terrain-lod with the existing quadtree renderer.
  - Wire realtime-render-performance's frame-cap setting + input-latency pipeline into Legion's engine loop.
  - Flashing-storm bug: capture a repro seed next time it appears (precision/state-sync suspect).
Deferred commits:
  - 07-projects/18-bootstrap-generator/launch.py — untracked, owned by bootstrap-generator work (not this session).
Next:
  - Begin Legion-side implementation of the terrain LOD + atmosphere spokes against src/render/.
--- END BLOCK ---

---

### 2026-07-22 — Legion: planet rendering — biomes, climate, night-lights, living weather, lab UX

--- SESSION BLOCK ---
Date: 2026-07-22
Agent: Claude Opus 4.8
Machine: Personal MacBook Pro
Surface: Claude Code (Mac desktop app)
Project(s): 13-legion (Legion repo — separate git checkout at ~/Projects/Legion)
Summary: Long continuous planet-renderer session. ~22 PRs (#163–#184) all merged to main + deployed to GitHub Pages (final commit 24040e5, Pages 200). Work spanned five threads: living weather, biome/climate physics, settlement-realistic night lights, ice/snow, and lab UX — plus research docs and a systemic World-dials control model.
Decisions:
  - Cyclones are ocean-gated on the CPU (macroHeight+warpDir sample) — no hurricanes over land; storm swirls scaled down (continent-sized was wrong); large cloud-free regions added; near-imperceptible animation.
  - Climate moisture is a SIGNED additive FIELD (base + aridBelts/rainShadow/orographic/continental/altitudeDry/patchiness), never a product chain (collapses to zero). Temperature = cubic insolation fit to Earth MAT − lapse×altitude.
  - Biome palette authored DARK (pine, ~half brightness); ocean ramp made bare ground (was itself green, bleeding through). Earth-calibrated albedo desert:forest ≈ 3:1 (not 10:1). Tundra can read green.
  - Night lights = habitability field (coast/lowland/fertile/livable × cold/capNear/arid penalties, floor at trace) → density → threshold on high-freq snoise for light SHAPE; sparse (not zero) near ice caps and in large deserts; tendrils/clusters.
  - Ice: snowCover() albedo overlay (no mass), sea-ice paler/bluer than land glacier, terrain normals show through ice, multi-scale uneven cap margins (lobes/bays/altitude/current asymmetry).
  - Lightning: emissive flicker on cloud shell + surface under-glow, cyclone eyewalls + periodic cell grid gated by density.
  - Systemic World dials (variants.ts): via(lo,mid,hi,t) piecewise-lerp anchored 0.5=Earth; offset/manual-edit-preservation model (masterValues/applyOffsets/LIMITS). Old sliders preserved for revert.
  - Bake parity via single finishHeight() path; simplex fbm3 detail (not value noise); featherEdges to kill margin step-seams. Canyons added to macro.
  - Stars-through-planets fixed: starfield materials transparent:false (was in transparent pass, drawing after opaque geometry). Ledger A-06.
  - Lab controls fully live (killed Rebuild delay); camera.setViewOffset pans subject clear of docked panel; VIEW section adds auto-rotate toggle + arrow-key nudge.
  - launch.json: legion (dev/5173) + legion-preview (preview/4173) detected and saved.
Artifacts (Legion repo):
  - docs/giants-moons-rings-research.md — ice/gas giants, rings as any-archetype feature, moons/satellites per archetype, binary planets, habitable giant-moons, super-earths.
  - docs/labs-blackhole-star-nebula-requirements.md — lab requirements for black-hole / solar / nebula-nursery labs.
  - docs/planet-lab-parameter-reference.md — parameter reference for the planet lab.
Ledger (workspace, committed earlier this session): visual-failure-mode-ledger A-06 (transparent-flag defeats draw-first backdrop), P-05 recurrence note (bake value-noise), P-06 (differential-rotation smear), P-07 (hard edit-margins step-seam).
Pending resolved:
  - Cyclones-over-land, low cloud resolution, over-animated clouds, stars-through-planets, baked blockiness/step-seams, polar desertification, city-light blobs, storms flashing on live-slider ticks (refreshParams was wiping storm state), biome sage-not-pine.
Carry-forward (unresolved / not-yet-built):
  - Ephemeral cloud/LOD hexagon artifact — user confirmed cloud-layer (matching cloud shadow), then said it vanished; could not reproduce. Needs seed + repro conditions. NO fix shipped.
  - Lightning never verified in a still frame (automation rAF throttle) — needs live-motion capture.
  - Biome-height decouple (bh from plateMacro, not baked vHeight) was applied on a WRONG diagnosis (thought hexagon was a biome seam) — decide whether to keep.
  - Sun/star, nebula, black-hole labs specced not built; ice/gas-giant material split; giant rings/moons features.
Next:
  - NEXT SESSION theme (user pre-announced): "a new set of adversarially checked skills to help us improve engine performance at close zoom levels and more." Await the skills, then apply to close-zoom perf.
--- END BLOCK ---

---



### 2026-07-21 — SaaS PLM prototype → centric-ui gap audit re-run; PR #1 refreshed for Olga's review

--- SESSION BLOCK ---
Date: 2026-07-21
Agent: Claude Opus 4.8 (1M context)
Machine: Work MacBook Pro
Surface: Cursor (Claude Code extension)
Project(s): Employer design-system migration (cpes-software/saas-plm-prototype → centric-ui)
  — deliverables live in the employer repo, NOT mirrored here (separation rule); this block
  records only the fact of the work + the PR reference.
Decisions:
  - Re-ran the FULL multi-agent gap audit (not a delta pass): Olga's shadcn/Radix migration
    invalidated the prior audit's "hand-rolled" premise, so every verdict was re-derived from
    current source on both repos rather than carried forward.
  - Report verification as "two independent adversarial passes; identical rung + difficulty on
    all carried units" instead of a confirmed/adjusted count — the count proved a sampling
    artifact (swung 8/19/6 → 17/16/0 across two passes while every unit's resolution + difficulty
    stayed identical). Captured as knowledge [[adversarial-verify-label-volatility]].
  - Updated PR #1 in place (rebased onto current main) to preserve Olga's review thread rather
    than opening a fresh PR. Committed as the Centric account; PR review by Olga, no self-merge.
  - Fixed a render bug pre-delivery: raw `<table>`/`<DataTable>` in the data broke the gap-map
    matrix (innerHTML) and would mis-render on GitHub — escaped injected fields + the markdown.
Pending resolved:
  - Employer DS-migration gap report re-run: done — plan + interactive gap map refreshed, new
    per-unit detail appendix added, PR #1 updated, replied to Olga's CHANGES_REQUESTED review.
Pending added:
  - Await Olga's re-review of saas-plm-prototype PR #1 before resuming the migration build.
  - Prototype repo left checked out on `docs/centric-ui-migration-plan` (not `main`) — switch back when convenient.
Next:
  - On Olga's sign-off: resume the DS migration build, quick-win reuses first (per the refreshed plan).
--- END BLOCK ---

---

### 2026-07-20 — centric-ui local-against-cloud-dev stood up; PRs #116/#117 landed; credential-scoping + chain-order contract fixes

--- SESSION BLOCK ---
Date: 2026-07-20
Agent: Claude Opus 4.8
Machine: Work MacBook Pro
Surface: Cursor
Project(s): Centric VMS Design System (centric-ui), Workspace Brain, saas-plm knowledge base
Artifacts:
  - `06-context/memory/feedback-credential-scoping.md` — Centric-laptop credential rule (05c997d)
  - `06-context/memory/reference-saas-plm-knowledge-discovery.md` + project-context entry (61251f9)
  - `08-knowledge/engineering/centric-ui-local-against-cloud-dev.md` — the three cloud-dev traps (c73418d)
  - Contract fix across 7 files: build-related now precedes build-registry (7239d16, 1752d03)
  - centric-ui PR #179 (OPEN) — dev-proxy cloud routing + env-example/API-key corrections
  - Cloned `saas-plm-analysis/knowledge-discovery` → `<Projects>/saas-plm-analysis/` (503MB, main)
Decisions:
  - Cloud dev over Docker Compose for now: Docker not installed and 5 prereqs missing (2 needing
    other people's tokens); cloud dev works today with one command. Revisit when the JFrog token is
    being requested anyway, or if backend _data_ needs reshaping (cloud dev is shared — don't).
  - centric-ui worktree `centric-ui-main` created on `main`; the figma branch was 826 files / 77
    commits stale, so reviewing UI from it would mislead.
  - #117 build tag set to 11.4.34 (not a copy of #116's 11.4.33) so the two bundles stay
    distinguishable in the UI header — validated once #116 squash-landed 11.4.33 on main.
  - Keycloak redirect-URI three-way disagreement (realm=3000, vite=8082, example=5173) documented
    in PR #179, deliberately NOT decided — belongs to whoever owns the VMS realm.
Pending added:
  - VMS realm owner to decide redirect URI: allow 8082, or change examples to 3000 (PR #179 item 3).
  - `workflow-service` has no cloud dev hostname (DNS 000, not 401) — BE must expose it or name it.
  - centric-ui PR #179 needs reviewers (Alex Myronov natural for the proxy half — extends his #160).
  - Two abandoned centric-ui SHAs (ec04737, 86651f0) carrying `hello@snds.design` remain reachable
    by direct URL until GitHub GC; purging needs a Support request (draft offered, not written).
  - SSH to github.com:22 timing out on this network all session — all pushes went over HTTPS.
    Fix if it persists: route Host github.com / github-work via ssh.github.com:443.
Pending resolved:
  - PRs #116 + #117 — conflicts resolved (buildInfo.ts build-tag only, both times) and both merged.
  - Employer design-system migration: backend access provisioned and now working end-to-end.
Project status changes:
  - Centric VMS Design System: blocked-on-backend-access → unblocked, local FE running against cloud dev.
Corrections worth remembering (agent self-audit):
  - Committed two merge commits to an employer repo as `hello@snds.design` by passing explicit
    `-c user.*` flags that overrode an already-correct repo-local config, then reported it as a
    footnote instead of fixing it immediately. Rewritten + force-pushed; rule recorded in
    [[feedback-credential-scoping]]. Workspace repo on this machine repointed to the `github-work`
    SSH alias + Centric identity.
  - Read a git diff backwards and confidently told Sean the header fix was on `main` when the
    reverse was true. Verify diff direction by reading both files, not by reasoning about `-`/`+`.
  - Twice reported `exit=$?` that was actually `tail`'s status, masking a real failure.
Next:
  - Assign reviewers on centric-ui PR #179; raise the redirect-URI question with the VMS realm owner.
  - Resume the DS migration build now that the backend is reachable — quick-win reuses first.
  - Optional: Docker Compose setup when the JFrog token is being requested for something else.
---

### 2026-07-11 — Legion: procedural-worlds Step 0 — star+planet physical data contract (PR #157 open)

--- SESSION BLOCK ---
Date: 2026-07-11
Agent: Claude Opus 4.8
Machine: Personal MacBook Pro
Surface: Claude Code (Mac desktop app)
Project(s): 13-legion
Artifacts:
  - Legion PR #157 (OPEN, awaiting owner — not self-merged) — branch feat/worlds-data-prep.
    Extends the GENERATED body records with the physical fields the star + planet renderers read,
    so feat/worlds-star and feat/worlds-planet never edit the same data file. Pure data, no rendering.
    STAR (StellarParams): spectralType, massSolar, radiusSolar, luminositySolar, tempK, ageGyr,
    activity — derived deterministically; real B−V drives tempK. PLANET (GenPlanet): type, massEarth,
    radiusEarth, insolation, isGasGiant, hasRings, per-body seed. tsc clean, 1364 vitest pass.
Decisions:
  - Independent RNG streams for the physical fields (seedKey|starphys, seedKey|planet|i) so the
    existing planet/belt layout is byte-unchanged (belts.test untouched, green).
  - Kept coarse teffK/lumSun (drive HZ/snow-line determinism) alongside render-facing
    tempK/luminositySolar — avoided a churny rename cascade; distinction documented in the interface.
  - Curated home stars (star-catalog.ts) left authoritative/untouched — only generated bodies filled.
Handoff: baton to feat/worlds-star (plan S1) — see SESSION-STATE Live handoff (2026-07-11).
Pending: PR #157 merge (owner). Do NOT branch feat/worlds-star or feat/worlds-planet until it lands
  on main (shared base for both parallel workstreams).
--- END BLOCK ---

---

### 2026-07-10 — Legion: tabbed settings + committed save-as-default persistence (PR #146 open)

--- SESSION BLOCK ---
Date: 2026-07-10
Agent: Claude Fable 5
Machine: Personal MacBook Pro
Surface: Claude Code (Mac desktop app)
Project(s): 13-legion
Artifacts:
  - Legion PR #146 (OPEN) — tabbed CONFIG panel (DISPLAY/KEYBOARD/CREDITS, typeface hidden) +
    dev write-back endpoint: Save now writes committed src/config/*.json defaults
Decisions:
  - Persistence model: code defaults -> committed JSON overlay (written by Save via dev endpoint)
    -> localStorage fallback. localStorage demoted; committed files are the durable save.
  - Root cause of "LAB save doesn't persist": seed was missing from the galaxy preset, so saved
    looks regenerated structurally different. Fixed (seed in snapshot/apply/revert).
Pending: (resolved 2026-07-10 — both PRs merged to main on Sean's go-ahead; main green 205/205)
--- END BLOCK ---

---

### 2026-07-10 — Legion: Sol texture provenance verified (PR #145 open)

--- SESSION BLOCK ---
Date: 2026-07-10
Agent: Claude Fable 5
Machine: Personal MacBook Pro
Surface: Claude Code (Mac desktop app)
Project(s): 13-legion
Artifacts:
  - Legion PR #145 (OPEN, awaiting merge) — data-sources.ts split into 3 texture entries + public/textures/sol/NOTICE.txt
Decisions:
  - Provenance method accepted: embedded PDS/XMP metadata + MD5 + pixel correlation vs candidate downloads.
  - 10 files = Solar System Scope CC BY 4.0 (commercial OK); 4 = USGS Voyager-Galileo mosaics (public domain);
    titan/phobos/deimos stay UNVERIFIED (candidates are NC-licensed) with replace-before-release guidance.
Pending:
  - Sean: merge PR #145 (self-merge was permission-gated this session).
  - Replace titan/phobos/deimos (USGS mosaics or procedural) before any public release.
--- END BLOCK ---

---

### 2026-07-09 — Legion: physical galaxy default + credits/positions/drift/system-focus epic (PRs #141–#144)

--- SESSION BLOCK ---
Date: 2026-07-09
Agent: Claude Fable 5
Machine: Personal MacBook Pro
Surface: Claude Code (Mac desktop app)
Project(s): 13-legion
Artifacts:
  - Legion PR #141 — physical galaxy = default disc (half-float gas blur) + trackpad zoom fix
  - Legion PR #142 — data-sources attribution registry + Settings CREDITS section
  - Legion PR #143 — 3,066 real HYG systems at true x-y-z + galactic drift on the sim clock
  - Legion PR #144 — system focus + lazy loading (Sol playable from the sector, load hidden in zoom)
  - 13-legion/SESSION-STATE.md — Live handoff block rewritten (July 9)
Decisions:
  - Licensing (extends decision-commercial-data-licensing): Gaia DR3 confirmed CC BY-NC 3.0 IGO —
    attribution alone is NOT sufficient for commercial use; recorded NOT SHIPPED in the in-app
    registry. HYG v3.8 (CC BY-SA 4.0) remains the shipped base.
  - Drift clock unified: disc shader + system markers share one galactic-time clock; LAB warp
    slider demoted to a preview offset.
Pending:
  - Sol planet textures have NO recorded provenance (flagged UNVERIFIED in the credits registry) —
    must be resolved before any public release.
  - Gaia-mary map UX (labels, region box, grid, course plotting) now unblocked — next Legion focus.
--- END BLOCK ---

---
