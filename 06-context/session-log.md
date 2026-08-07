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

### 2026-08-05 — Layer-1 vault retrieve + dispatcher fallback

SessionID: 2026-08-05-voyager-5d6242
--- SESSION BLOCK ---
Date: 2026-08-05
Machine: Personal MacBook Pro
Surface: Cursor
Agent: Cursor Grok 4.5
Project(s): 19-workspace-brain
Summary: Shipped Layer-1 lexical vault retrieval (`09-tools/vault-retrieve.py`, stdlib FTS5) and wired it as a capped Claude dispatcher fallback when Layer 0 under-fires; Cursor gets CLI-on-demand only.
Artifacts:
  - 09-tools/vault-retrieve.py — FTS index/rebuild/query + graph expand; machine-local `.claude/state/vault-retrieve/`
  - .claude/hooks/dispatcher.py — SessionStart index refresh; UserPromptSubmit lexical tier (min 2 Layer-0 targets, cap 2, `--cached`)
Decisions:
  - Triggers stay primary; lexical is gap-fill only (not a peer flood on every prompt)
  - Index personal vault layers only — no `07-projects/` / employer surfaces
  - Cursor has no prompt-hook equivalent → document CLI; do not fake a dispatcher tier there
Pending added:
  - Optional: golden-set eval of trigger misses vs lexical baseline
  - Optional: dense/embedding path as capability-registry entry with degrade→lexical
Pending resolved:
  - (none from prior baton; this session was additive tooling)
Next:
  - Prove lexical fallback in a live Claude Code session (SessionStart rebuild + under-fire inject)
  - Optionally design dense Layer 2 only after golden-set shows lexical gaps worth the capability
  - Prior baton still open: review personal:SEA-11; decide personal:SEA-32
Git: 55b9f2a (feature) + this session commit
--- END BLOCK ---


### 2026-08-03 — Domain rigor stack hardening

SessionID: 2026-08-03-voyager-r7k2
--- SESSION BLOCK ---
Date: 2026-08-03
Machine: Personal MacBook Pro
Surface: Cursor
Project(s): Workspace (skill hubs / domain rigor)
Summary: Encoded five-layer domain rigor stack (#13) and shipped L1–L5 hardening across hubs/spokes outside the parallel photoreal session; measurement toolkits + reciprocity/capability follow-ups landed.
Artifacts:
  - 01-frameworks/13-domain-rigor-stack.md — reusable L1–L5 contribution mechanism
  - 01-frameworks/14-engineering-operating-model.md — eng L1 gates
  - 01-frameworks/15-analysis-operating-model.md — analysis L1 gates
  - 01-frameworks/16-security-operating-model.md — security L1 gates
  - 03-skills/a11y-audit-toolkit + fe-perf-harness — break measurement monoculture
  - Command hubs: eng, arch-guild, process-plugins, design-system-ops; career hub = job-search-strategist
Decisions:
  - Domain rigor is a five-layer stack (ops model → command hub → measurement → load chain → multi-voice + doctrine precedence), not UI/UX-only.
  - Plugin skills defer to AGENTS.md / frameworks; frontmatter `defers_to` + `rigor_role` are first-class.
  - Contested photoreal/3D/game surface (Framework #12, img-photoreal*, legion-*, 08-knowledge/research|game-dev) owned by parallel session — do not collide.
  - Career: hub = job-search-strategist; spokes wrap ~/.agents/skills mirrors.
Pending resolved:
  - Specialist/rigor gap evaluation across Workspace hubs (execute comprehensively, including former leave-alones).
  - Measurement monoculture: a11y toolkit, FE perf harness, /qa lenses motion|dataviz|type|security.
Next:
  - Spot-check career routing docs vs hub = job-search-strategist if a session touches job search.
  - Use Framework #13 as the gate when adding or hardening any new domain skill cluster.
--- END BLOCK ---


### 2026-08-03 — Realtime photoreal rigor stack (#12)

SessionID: 2026-08-03-voyager-b505c2
--- SESSION BLOCK ---
Date: 2026-08-03
Machine: Personal MacBook Pro
Surface: Cursor
Project(s): Workspace (skills/frameworks); Legion (consumer contracts only)
Artifacts:
  - 01-frameworks/12-realtime-photoreal-operational-framework.md — triple done-gate + movie-level northstar ops
  - 03-skills/realtime-visual-craft/ — Impeccable-shaped command hub + RENDER/BUDGET/NORTHSTAR templates
  - 03-skills/render-qa-toolkit/ — frame/motion/still measurement suite (Legion ?perfcapture config)
  - 03-skills/interactive-capture-eval/, visual-qa-photoreal-rendering/, rendering-guild/ — motion capture + photoreal QA + guild
  - 03-skills/{dynamic-gi,shadow-quality,virtual-texturing,bake-orchestration,gpu-capture,adapter-*}/ — AAA spokes + engine adapters
  - Legion RENDER.md / BUDGET.md / NORTHSTAR.md + docs/render-acceptance-harness.md — project consumer contracts
Decisions:
  - Multi-engine principles with thin Unreal/Unity adapters (1B); full rigor stack in one program (2B)
  - Legion is test platform only — skills stay in Workspace
  - Evaluation requires still grid + flythrough frame-by-frame + measured ms; low-res/still-only verdicts banned
  - Movie-level fidelity gated by named NORTHSTAR stills/videos/game examples
Pending resolved:
  - Workspace photoreal connective tissue (framework #12 + command hub + measurement + guild + adapters)
  - Legion contracts landed on main (dcd9abb)
Next:
  - Run a live Legion acceptance pass on official poses + flythroughs in native Chrome (not IDE-browser alone)
  - Sign concrete northstar file paths into Legion NORTHSTAR.md as captures are approved
  - Optional: register Open Agent Engine personal lane when MCP is available (skipped this session — not-registered)
--- END BLOCK ---


### 2026-07-30 — SaaS PLM: global density model + pill/chip shapes (PR #13 for Olga)

SessionID: 2026-07-30-work-density01
--- SESSION BLOCK ---
Date: 2026-07-30
Agent: Composer / Auto
Surface: Cursor
Machine: Work MacBook Pro (main, CS-K746DRWXY1)
Project(s): SaaS PLM prototype (employer — `centric-engineering` profile)
Summary: Shipped a user-controllable Compact/Normal/Spacious density axis (header toggle, localStorage, FOUC boot) across chrome, tables, forms, and radius. Softened the ladder one mode (Compact = old Normal / centric h-8). Added shape rules so density doesn't collapse meaning: checkbox `--radius-check` + circle variant (card grids default circle); pill vs chip via half-rate `--radius-chip` (4/6/8); `ds:check` guards for primitive call sites, glyphs, and chips. Committed the full working tree (density + prior DataTable foundation/token-lab) and opened PR #13 for Olga.
Artifacts:
  - Employer PR: https://github.com/cpes-software/saas-plm-prototype/pull/13 (`feat/global-density` @ `240a767`)
  - Employer: `src/styles/density.css`, `src/app/lib/density.ts`, `DensityToggle`, `SheetFooter`, Badge/Checkbox/StatusPill/TypeTag/ChipMultiSelect shape work, `design-system.rules.json` + `ds-core` lint/tests
  - Docs in employer repo only: `DESIGN-SYSTEM.md`, `PROJECT-NOTES.md`, `AGENTS.md` / `CLAUDE.md` / `MIGRATION-TO-CENTRIC-UI.md` / `CENTRIC-UI-SYNC.md` (C14 ROW_DENSITY note)
Decisions:
  - Default density = Normal (one step softer than original prototype); Centric's 32px reference lives in Compact.
  - Checkbox glyphs stay 4px off-ladder; opt-in `shape="circle"`; `CardSelectControl` defaults to circle (all card grids).
  - Pill = `rounded-full`; chip = `--radius-chip` half-rate ladder — ChipMultiSelect `pill`/`linkPill` made real capsules.
  - Never put density scale on a primitive via `className` (call-site rule); add a `cva` size/shape instead.
Pending added:
  - Olga review of PR #13 (density feel across modes; card circles; pills vs chips; sheet CTAs)
Pending resolved:
  - Prior "review + commit/PR employer DataTable branch" — folded into the same PR #13 push (density-led framing)
Next:
  - Olga reviews/merges #13
  - Deepen Materials LandingDataTable domain cells if still needed post-merge
  - Lift density axis + shape tokens into centric-ui when ready; ROW_DENSITY sync (C14)
--- END SESSION BLOCK ---

### 2026-07-30 — SaaS PLM DataTable: Layer A+B visual parity (LandingDataTable + Materials lab)

SessionID: 2026-07-30-work-dt02
--- SESSION BLOCK ---
Date: 2026-07-30
Machine: Work MacBook Pro (main)
Surface: Cursor
Project(s): SaaS PLM prototype (employer — `centric-engineering` profile)
Summary: Brought `@centric/data-table` visual parity through Layer A (lab recipe) and Layer B (shared `LandingDataTable`). Actions column stays in the DOM for a11y; recipe CSS hides its chrome; floating Edit/Remove pill on hover/focus. Lab now switches Seasons | Materials (Materials = subset stress, not full 21-prop port).
Artifacts:
  - Employer: `src/app/features/landingDataTable/` (`LandingDataTable`, column helpers, recipe CSS); `src/table-lab.tsx` rewired; `table-lab.css` removed (recipe lives with the wrapper)
  - `05-artifacts/active/saas-proto_datatable-visual-parity-plan_v1.0_2026-07-30.md` — A+B marked complete
  - Repo `PROJECT-NOTES.md` + `CENTRIC-UI-SYNC.md` (actions-header a11y finding)
Decisions:
  - Floating Edit+Remove is the landing actions pattern; package actions column kept for semantics; `⋮` returns only as overflow past two actions.
  - Materials lab starts as a representative subset; full domain cells are a follow-on, not a TanStack fork.
  - Prefer nested system components (`StatusPill`, `InlineEditText`, `TypeTag`, `TableRowActions`) over table-local chrome.
Learnings:
  - Transparent borders (not `border: 0`) preserve sticky offsets on the actions column.
  - Package `DataTableRowActionsHeaderCell` has contradictory `aria-hidden` + `sr-only` — upstream finding, do not patch the copy.
Next:
  - Review + commit/PR employer branch (never auto-commit)
  - Deepen Materials domain cells on the recipe
  - Layer C = file/send upstream findings; WP-0 memo still unsent
--- END SESSION BLOCK ---

### 2026-07-30 — SaaS PLM DataTable: plan reviewed, premise overturned, table copied in + comparison lab live

SessionID: 2026-07-30-work-dt01
--- SESSION BLOCK ---
Date: 2026-07-30
Machine: Work MacBook Pro (main)
Surface: Claude Code (VS Code extension)
Project(s): SaaS PLM prototype / centric-ui (employer — `centric-engineering` profile)
Summary: Reviewed the DataTable contract plan against live source in three checkouts. Every survey number verified exactly (16 files / 11,784 lines / 2 aria / 0 role / 21 props), but the plan's premise was stale — `@centric/data-table` already ships in centric-ui `main` (TanStack v8 + react-virtual, ~19k lines, tested). Sean initially chose "contract arbitrates, proto consolidates", then **reversed it**: the goal is migratable parity, so the prototype should consume centric-ui's table as closely as possible, dependencies included. Copied the package in byte-identical, added a `~` alias so copies need no edits, and built a side-by-side comparison lab. Caught a runtime crash the build could not see.
Artifacts:
  - `05-artifacts/active/saas-proto_datatable-implementation-plan_v1.0_2026-07-28.md` — review + 9 work packages (SUPERSEDED in part by the reversal below; WP-0 findings still stand)
  - `05-artifacts/active/saas-proto_datatable-wp0-alignment-memo_v1.0_2026-07-28.md` — send-ready memo, **not sent**
  - Employer repo (uncommitted, branch `feat/datatable-centric-ui-foundation`): `CENTRIC-UI-SYNC.md`, 6 copied primitives, 166-file local copy of `src/app/features/dataTable/`, `src/table-lab.tsx` + `table-lab.html`
Decisions:
  - **Reversal (Sean):** prototype DOES take TanStack and centric-ui's deps. "Either we consume what they have or we duplicate it" — zero issue with the table + supporting deps being the prototype's dependencies. Supersedes the 2026-07-28 "proto never adopts TanStack" call and its `no @tanstack/*` tripwire.
  - Prototype stays a separate repo for now — freedom over zero-drift; manual sync accepted until the move into centric-ui.
  - Sync strategy: **byte-identical copies + a `~` → `src/app` alias**, so re-syncing is `cp` with no per-file port. Copied tree excluded from `ds:check` for the same reason `components/ui/` is.
Learnings:
  - `@centric/data-table` is **not standalone** — it reaches into its host app's `~/components/ui/*` and `~/lib/*` 41 times. Consuming the table means adopting the foundation under it.
  - lingui is **runtime-only** here (no macros, inline English in `<Trans message>`), so no Vite plugin, no CLI, no catalogs. Earlier claim that it was a heavy build-time system was wrong.
  - lucide 0.487 → 1.x verified additive: **106 icons checked, 0 missing.** date-fns 3→4 fixed a *pre-existing* peer break with `@base-ui/react`.
  - **The build is not proof in this repo.** Build passed green while the lab rendered blank — nuqs needs a framework adapter. Only a real browser load found it. nuqs 2.9.3 does ship `adapters/react-router/v8`.
  - Upstream finding: centric-ui's own `FilterOptionSearchInput.tsx:36` uses `h-9 rounded-md` — off the centric control scale. Recorded, not patched.
Next:
  - Employer branch is **uncommitted and unpushed** — review, then commit/PR (branch → PR → human review; never auto-commit).
  - Put `MaterialsTable` (21 props) through the lab — the hard case where real differences will show.
  - Revisit the contract's role: with one implementation, it becomes a requirements/acceptance doc, not an arbitration artifact.
--- END SESSION BLOCK ---

---

### 2026-07-30 — Unlock AI review; Open Engine close-out and a withdrawn runner

SessionID: 2026-07-30-work-oe3f
--- SESSION BLOCK ---
Date: 2026-07-30
Machine: Work MacBook Pro
Surface: Cursor
Project(s): 19-workspace-brain
Summary: Read Nate B. Jones' Unlock AI property end to end, adopted Open Engine as a workspace-governed skill with two isolated Linear lanes, then closed out a third parallel pass — building a scheduled runner, discovering a concurrent session had already rejected one, testing that rejection, and finding it correct.
Artifacts:
  - 03-skills/open-agent-engine/SKILL.md — the engine procedure (authored earlier this thread; extended here with verified isolation evidence and the cold-start rule)
  - 00-bootstrap/doctor/linear-lanes.py — deterministic lane preflight, wired into session-start Notices
  - 06-context/open-engine/{README,personal}.md — lane index + canonical machine→lane manifest
  - 08-knowledge/cross-domain/workspace-infrastructure.md — new section "Headless Claude Code"
Decisions:
  - Scheduled runner WITHDRAWN. Built lane-scoped with --strict-mcp-config, then found commit 4dee209 had already scoped and rejected one; tested its central objection and it held.
  - Deny, don't allow. Any future unattended runner is gated on --tools / --disallowed-tools; --allowed-tools is not a restriction mechanism.
  - Session-start token trim SUPERSEDED, not merely deferred — project-context.md is now the substance store and each ^pc-NN anchor is the sole pointer for a Linear issue, so trimming is a per-item graduate → repoint → remove migration.
  - Two lanes over one shared Linear workspace; isolation is structural (per-lane MCP auth context), and the c8 lane is movement-only.
Pending resolved:
  - Open Engine build — complete. Both lanes live, four smoke tests passed, five validators green.
Next:
  - Unchanged from the prior pass: review personal:SEA-11, decide personal:SEA-32, give ^pc-07/^pc-11 machine-local homes, resolve lane ambiguity on ^pc-30/^pc-41.
  - Unrelated and pre-existing: 3 un-acknowledged bootstrap MISSes (two from centric-ui sessions) — run workspace-doctor.sh.
--- END BLOCK ---

## Findings worth keeping (detail behind the Decisions above)

**`--allowed-tools` grants; it does not restrict.** A session launched with
`--allowed-tools "mcp__linear-personal"` still reported `Bash`, `Edit`, `Write`, `Agent`,
`CronCreate`, `RemoteTrigger`. The naming invites the opposite reading, and I read it the wrong way
while building. Since issue bodies are untrusted input by the engine's own rule, an unattended runner
built that way turns "anyone who can write to that board" into "anyone who can run commands on this
laptop." Full detail: [[workspace-infrastructure]] → "Headless Claude Code".

**`--strict-mcp-config` does isolate.** Probed: `SERVERS: linear-personal` / `C8_PRESENT: no`. The
other lane is absent, not merely unused. This is now evidence under a claim the docs previously
asserted.

**`mcp-remote` cold start is a silent-failure path.** A headless session can begin before its server
connects and honestly report "no MCP tools available" — indistinguishable from an empty queue. Same
shape as the `auth-incomplete` bug in the detector: a failure wearing success's clothes. The ritual
now distinguishes absent / not-yet-connected / empty.

**Two detector bugs found by testing against reality rather than assumption:** `validate-integrity`
resolves wikilinks against *git-tracked* files (a new skill is unaddressable until `git add -N`), and
the `provisioned` check matched the bare word `PENDING` in prose — including the lane config's own
status banner, so a fully-provisioned lane reported `not-provisioned`.

**Process note.** Three sessions worked this subsystem concurrently. Two independently designed a
scheduled runner and reached opposite conclusions; one `git add -A` swept another session's staged
work into the wrong commit. The engine's own session-boundary discipline is the fix, and `/reconcile`
existed for exactly this — worth invoking *before* parallel passes, not only after.


### 2026-07-30 — Open Agent Engine: provisioned, smoke-tested, wired to the rituals, backlog migrated

SessionID: 2026-07-30-csk746-openengine

--- SESSION BLOCK ---
Date: 2026-07-30
Agent: Claude Opus 5
Machine: Work MacBook Pro (`CS-K746DRWXY1`)
Surface: Cursor (Claude Code extension)
Project(s): 19-workspace-brain — Open Agent Engine (both lanes); 06-context backlog migration
Artifacts:
  - 08-knowledge/engineering/agent-work-queue-boundaries.md — seven tracker-agnostic boundary
    constraints found by testing, not reasoning
Decisions:
  - Stage-2 identity verification passed on both lanes; the workspace-slug check degrades to a
    first-write gate, because no Linear read exposes an org slug on an empty board
  - Six engine statuses created by hand (Sean) — the MCP has no status-creation or team-creation op
  - Unattended scheduled runs AUTHORIZED via the `personal:SEA-8` human hold, then deliberately
    NOT exercised
  - **No timer — the session boundary is the heartbeat.** Cloud routines cannot reach Linear at all;
    a local runner with full autonomy makes untrusted issue bodies a path to a shell; and a timer
    only buys progress-while-absent, which is not how Sean works
  - Migration is pointer-shaped, so items CANNOT be deleted from project-context.md — the
    architecture enforces Sean's "don't remove until validated" instead of discipline doing it
  - Employer-lane issues carry no path into this repo; resolution goes through a machine-local table
Pending added:
  - `personal:SEA-32` — the six statuses have no "someday" bucket and the claim rule is
    priority-blind; harmless while runs are human-triggered, real the moment anything is unattended
  - 5 items could not be migrated (`^pc-07`, `^pc-11`, `^pc-30`, `^pc-41`, `^pc-42`) — two need a
    machine-local home before they can be filed without writing substance to the employer board;
    two are lane-ambiguous; one has nothing to point at
Pending resolved:
  - `^pc-04` trigger-routes reference — delivered by a concurrent Cursor session; `personal:SEA-11`
    moved to `Agent Review` (not Done) because the work is still uncommitted
  - `^pc-13` beacon paste — Cursor User Rules done, Perplexity Space still open; issue stays open
Project status changes:
  - Open Agent Engine: build → live on both lanes, all four smoke tests passed
Deferred commits:
  - A concurrent Cursor session's work (~20 modified + ~10 untracked: Cursor rules/hooks,
    trigger-routes system, workspace-doctor, AGENTS.md, .gitignore, archive move) is uncommitted and
    was deliberately NOT swept into this session's commits — see the orphaned-changes audit
Next:
  - Commit the concurrent Cursor session's work under its own attribution, then close
    `personal:SEA-11`
  - Decide `personal:SEA-32` (seventh status vs priority-aware claim rule)
  - Give `^pc-07` / `^pc-11` machine-local homes so they can be filed; resolve the lane ambiguity
    on `^pc-30` / `^pc-41`
  - First ordinary session is the real test of the ritual integration — does the engine line appear
    only when it should, and does `/session-end` file residue pointer-shaped?
--- END BLOCK ---

SessionID: 2026-07-30-csk746-cursor-multiagent

--- SESSION BLOCK ---
Date: 2026-07-30
Agent: Composer
Surface: Cursor
Machine: Work MacBook Pro (CS-K746DRWXY1)
Project(s): 19-workspace-brain (Cursor multi-agent / multi-model hardening)
Artifacts:
  - 02-shared-references/trigger-routes.json + generated trigger-routes.md
  - 09-tools/build-trigger-routes.py
  - .cursor/hooks.json + hooks (reassert / sessionend / subagent-stop)
  - .cursor/agents/{workspace-bootstrap,ds-advisor,design-engineer,lead-ui-designer,lead-ux-designer}.md
  - 00-bootstrap/templates/cursor-mcp.json.example
  - _archive/compile-cursor-rules.py (retired landmine)
Decisions:
  - AGENTS.md remains hand-authored; compile-cursor-rules.py archived (would overwrite with Claude-only-writes policy).
  - Curated trigger routes live in trigger-routes.json; dispatcher loads JSON; markdown is generated for non-Claude agents.
  - Cursor project hooks cover preCompact / sessionEnd / subagentStop; user-global hooks still own sessionStart (+ doctor mirrors).
Pending resolved:
  - ^pc-04 trigger-routes reference
  - ^pc-13 Cursor User Rules BEACON (Perplexity still open)
Pending added: none
Project status changes:
  - Machine-layer fact: Work MBP → partial (Cursor hooks + BEACON); full doctor still open (^pc-03)
Next:
  - Run full workspace-doctor.sh on this machine when convenient; configure ~/.cursor/mcp.json from the example if Linear/Figma needed in Cursor
  - Prefer opening 00-bootstrap/workspaces/*.code-workspace (Brain first) for future Cursor sessions
--- END BLOCK ---


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

