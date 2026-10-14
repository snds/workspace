# Artifact Registry
<!-- Auto-maintained by any agent. Updated after each task. -->
<!-- Last updated: 2026-10-14 | Session: /optimize fix pass D (registry refresh) -->

## Media Services — 07-projects/01-mediaservices/ (git-tracked)

### 01-mediaservices/ (canvases/ git-tracked; SESSION-STATE.md local-only)
- **Purpose**: Unraid / Plex / Emby / MediaSentinel library ops. Portable handoff is `06-context/session-log.md` + `08-knowledge/engineering/pokemon-tvdb-dvd-vs-aired.md`. Local `SESSION-STATE.md` is gitignored. `canvases/` holds Cursor copies (`duplicate-scan-outcome`, `authoritative-delete-list`, `looney-tunes-loudness`).
- **Last modified**: 2026-09-03 — session-end: Aug 16–17 CUT delete + Desktop Pokémon organize recorded in the session log.

## LCARS Generative Interface — 07-projects/20-lcars-generative-interface/ (git-tracked)

### 20-lcars-generative-interface/ (README.md + SESSION-STATE.md + SPEC.md + docs/construction/ + canvases/)
- **Purpose**: Project home for the generative LCARS interface (design → plan → implementation pointers). Spec captures constitution-first Scene IR architecture, combadge roles, APCA+AA, data-first 3D viewports. Construction pack holds cuespec, IR, prove reports, and captures for S-SYS47-01. `canvases/` holds the Cursor `lcars-replication-gap` copy.
- **Last modified**: 2026-09-03 — Onori absorb: `vqa capture` path, `prove_sys47.py` tombstone, content-groups + Live handoff; LCARS app `a133bb4` off-system lint (sibling repo).

## Workspace Brain — 07-projects/19-workspace-brain/ (git-tracked)

### 19-workspace-brain/ (README.md + SESSION-STATE.md + notes/ + reports/ + canvases/)
- **Purpose**: Standing project home for workspace-subject sessions (validation, fix, migration, infrastructure) per the framework #08 project-home rule (FX-13). Git-tracked — cross-machine continuity is its point. `canvases/` holds copies of Cursor `.canvas.tsx` files; `cursor-externalize.py` also mirrors them into this checkout's live Cursor folder. Employer canvases go to that repo's `canvases/`, never here.
- **Last modified**: 2026-09-15 — six-phase workspace review landed: `workspace-harness.py` (quality/connections/tokens), `evaluate-surface-trajectories.py` (3 Layer-0 matchers collapsed to 1), `artifact-find.py` (session floor −32%), `figma-bind-probe.py` (A8, validated on 3 live nodes), `nightly.py`, `validate-evidence-grades.py`, `ruff.toml`. Reports: workspace-harness, surface-trajectories, automation-second-wave, artifact-retrieval, figma-bind-probe (all v1.0 2026-09-15). 2026-09-22: Zero-Vector harness plan (proposed): `notes/zero-vector-harness-plan_2026-09-22.md` plus the implementation-grade `reports/zero-vector-harness-detail_v1.0_2026-09-22.md` (H1–H15 specs, not-adopted list, risks, metrics, verified defects D1–D18 and X1; read by section). The paired knowledge note is `08-knowledge/cross-domain/zero-vector-design-methodology.md`.

### 19-workspace-brain/reports/ (versioned audit snapshots, `<name>_vN.N_YYYY-MM-DD.md`)
- **Purpose**: Dated audit and harness reports, never edited after the fact (artifact standards: a changed status gets a new version). Versioned reports: workspace-automation-review_v1.0_2026-09-11 (A1–A10, R1–R3), process-rigor-gaps_v1.0_2026-09-11 (R1–R16), harness-map_v1.0_2026-08-07, harness-map_v2.0_2026-09-11 (load-miss 1–15), substack-enrichment-brief_v1.0_2026-08-07, artifact-retrieval, automation-second-wave, figma-bind-probe, surface-trajectories and workspace-harness (all v1.0 2026-09-15), zero-vector-harness-detail_v1.0_2026-09-22, mechanization-review_v1.0_2026-10-13. The current state of their recommendations lives in the remediation register below, not in their `status:` lines; `validate-evidence-grades.py --status` flags a report whose status claims closure that no register row cites. The `.stamp` files and `ds-source-watch/latest.json` here are tool outputs, not reports.
- **Last modified**: 2026-09-25 — indexed here (W2-1, H8); the README's hand-kept "Current reports" table was replaced by an `artifact-find.py --path 19-workspace-brain/reports` pointer.

### 19-workspace-brain/docs/INTENT-remediation-2026-09.md
- **Purpose**: The workspace's findings register (H8 dogfood, `kind: remediation`): every recommendation from the three 2026-09-11 reports and their two 2026-09-15 follow-ups as one row with a re-runnable closure or a named judgment, DEFERRED rows with revisit triggers, OPEN rows with self-contained packets (`intent-run packet --format prompt T<n>`), the workspace's own `init --recon` card, and a preserve list. Verdict: `intent-run verdict --spec <this> --run`.
- **Last modified**: 2026-09-25 — created by W2-1: 46 findings (37 RESOLVED, 3 DEFERRED, 6 OPEN), 4 packets, approval pending.

### 19-workspace-brain/reports/mechanization-review_v1.0_2026-10-13.md
- **Purpose**: Mechanization review of the workspace: M1–M25 candidate mechanizations and bugs B1–B10 (suggested start: B1–B10, then the M25 write-cost lane). Its fixes sit on two unmerged branches awaiting Sean: `worktree-b-fixes-b1-b10` (B1–B11 + follow-ons) and `claude/kind-diffie-41820e` (M25 writes lane).
- **Last modified**: 2026-10-14 — `395ebdb` cleared the status census and employer-substance overage; written 2026-10-13.

### 19-workspace-brain/notes/zero-vector-rollout-checklist.md
- **Purpose**: Vault record of every Zero-Vector harness step by wave (open steps first, then closed steps with dates and commits). Replaces the claude.ai artifact database that held it until 2026-10-14; class-level only (public vault).
- **Last modified**: 2026-10-14 — exported from the artifact (db last updated 2026-09-26); waves 0–2 closed, wave 3 open.

## Mailbird (working name) — 07-projects/24-mailbird/ (git-tracked)

### 24-mailbird/ (README.md + SESSION-STATE.md)
- **Purpose**: Continuity baton and pointers for the open-source, ad-free PIM "super app" (mail, calendar, contacts, notes; mobile-first, web + Tauri shells). Code, research, license audit, architecture and ADRs live in the code repo `snds/Mailbird` (`docs/`), not in this vault.
- **Last modified**: 2026-10-14 — `5abef28` baton for Phase 9 ("connected calendar", PR #14); PRs #1–#13 merged.

## Fontface — 07-projects/25-fontface/ (git-tracked)

### 25-fontface/ (README.md + SESSION-STATE.md)
- **Purpose**: Continuity baton and pointers for Fontface, the clean-room Mac font manager replacing Typeface (Tauri 2 + React). Code and design docs live in `~/Projects/fontface` (public `snds/fontface`).
- **Last modified**: 2026-10-14 — `c0df598` renumbered 24 → 25 and tracked; baton refreshed by /optimize (main `826c574`).

## Portable Bootstrap Generator — 07-projects/18-bootstrap-generator/ (git-tracked)

### 18-bootstrap-generator/ (README.md + SESSION-STATE.md + generator/ + launch.py)
- **Purpose**: `wsx` interviews then scaffolds a portable second-brain workspace. Path B launcher detects folder-capable apps (Cursor/Claude/VS Code), opens the generator folder, emits all adapters.
- **Last modified**: 2026-09-17 — Path B surface picker (platform default + open folder); Windows zip on Desktop for colleague test.

## Delivery Playbooks — 02-shared-references/delivery-playbooks/

### delivery-playbooks/ (7 files: README + 00–05)
- **Size**: ~7 files, ~600 lines total
- **Purpose**: Canonical standards for HOW work is delivered — context profiles (whose work / who reviews: `personal-solo` / `centric-engineering` / `centric-design`, resolution order, fail-safe), audience contract (designer-first, forward test, three-altitude model), medium playbooks (diagrams/flows, data/charts, documents/specs), and the Proofboard validation-harness standard (plain-english contracts, show-me evidence, sandboxed sample data — Sean verifies code-heavy work without reading code).
- **Last modified**: 2026-07-09 — v1 created. Enforcement wired: dispatcher `TRIGGER_WORDS`, CLAUDE.md (section + trigger rows), framework #06 pre-output gate (context & medium check), SESSION-STATE template (`Context profile` field), user-preferences pointer. Founding anti-example: the Media Sentinel workflow-diagram-as-HTML-page failure.
- **Related pending**: "Context is King — workspace foundation refinements" backlog item in project-context.md (generalize profile resolution to every session surface).

### workspace_validation-session-prompt_v1.0_2026-07-09.md — 05-artifacts/active/ (local only, gitignored)
- **Purpose**: 6-phase test prompt validating the delivery-playbooks system in a fresh session — boot/trigger verification, context-resolution drills (incl. a deliberately unresolvable trap), audience/medium binding, a full Proofboard loop, adversarial path-walk (token-waste audit, trigger gaps, unexercised-path desk-check), scorecard. Fixed checkpoint-report format; stops for Sean's confirmation at every phase.
- **Last modified**: 2026-07-09 — v1.0 created. Not synced (05-artifacts gitignored) — copy manually to run from another machine; bump version + re-run after the "Context is King" backlog item lands.

## Skill Ecosystem & Trigger System — 05-artifacts/active/ + 03-skills/

### skill-ecosystem-stocktake_v0.3_2026-06-01.md
- **Size**: ~250 lines | 18 KB
- **Purpose**: Phase 1 — inventory of all non-workspace (plugin/marketplace + default Anthropic) skills, overlap mapping, adopt/wrap/fold-in disposition per the three-way contract.
- **Last modified**: 2026-06-01 — v0.3 MAJOR correction: zero exact-name collisions between added marketplaces and the 210 workspace skills; the 20 same-name overlaps are the default Anthropic mount (left alone). "Dedupe" task dissolved → reframed as ~8–10 semantic-overlap zones. Added Finding 3 (impeccable browser-extension + live-bridge surface, preserved for trigger expansion).

### invokable-operations-spec_v0.2_2026-06-01.md
- **Size**: ~205 lines | (companion spec)
- **Purpose**: Phase 2 — two-plane trigger model (organic description-contract + explicit `/hub verb target --modifiers` grammar), 12-verb spine, six-hub design, migration plan.
- **Last modified**: 2026-06-01 — v0.2: marked /qa POC built; reconciled dedupe references to stocktake v0.3 (no dedupe precondition).

### trigger-cheatsheet_v1.0_2026-06-01.html
- **Size**: ~424 lines | 31 KB
- **Purpose**: Self-contained HTML reference for the trigger system — two planes, verb spine, six hubs (status-tagged), targets/modifiers, 8 real-session worked combos, organic-phrasing map, impeccable modes/bridge, project trigger words, rules of thumb. Print/PDF-clean.
- **Last modified**: 2026-06-01 — v1.0 created.

### 03-skills/qa/SKILL.md
- **Size**: ~191 lines | 10 KB
- **Purpose**: `/qa` POC hub — user-invocable workspace wrapper implementing the operation grammar. Owns UI-evaluation routing; delegates to visual-qa-* spokes + visual-qa-toolkit + lead-visual-qa.
- **Last modified**: 2026-06-01 — v0.1.0 created. Verbs audit·critique·triage·inventory·spec; 8 target types; modifiers --lens/--level/--theme/--live/--out/--dry. Encodes disambiguation contract (qa judges · design-engineer authors · ds-advisor decides · impeccable creates) + preserves impeccable --live bridge with multi-spoke expansion seam.
- **Coverage**: First sibling of the 6-hub set; pattern validates remaining 5 (/ds /figma /motion /type /redesign). Synced to live skills mount.

### 03-skills/{ds,figma,motion,type,redesign}/SKILL.md  — the 5 sibling hubs
- **Size**: ds 141 · figma 124 · redesign 122 · motion 105 · type 99 lines
- **Purpose**: Complete the six-hub operation-grammar set. Each is a user-invocable workspace wrapper carrying the `/hub verb target --modifiers` grammar, a verb subset, and the cross-hub disambiguation contract; depth stays in delegated base skills/plugins.
  - `/ds` → ds-advisor + design-engineer + fe-design-tokens (system decisions, tokens, anatomy, governance)
  - `/figma` → figma-* + figma-canvas-designer + figma-plugin-dev + Figma MCP (canvas authoring, code-connect)
  - `/motion` → claude-design-skillstack libraries (motion *implementation*; principles stay in motion-* skills)
  - `/type` → type-* + lead-type-designer + gd-typography + uid-type-for-screens (type systems & letterform)
  - `/redesign` → adobe stardust pipeline + impeccable live loop (surface-scale generative redesign)
- **Last modified**: 2026-06-04 — observed built on disk; completes the set begun with /qa (2026-06-01).
- **Coverage**: Six-hub set complete. Open: design-system-ops plugin (38 commands) overlaps /ds → fold into description-contract pass; cheatsheet "planned" tags now stale.

## Workspace Infrastructure — 03-skills/ + 00-bootstrap/ + ~/.claude/

### 03-skills/workspace-bootstrap/SKILL.md
- **Size**: ~153 lines | 8 KB
- **Purpose**: Session handshake — manual re-trigger of the load protocol (the SessionStart hooks inject it automatically since bootstrap v2). Git-native: no Google Drive, no vendor-specific mechanism.
- **Last modified**: 2026-09-11 — `f70a781`. The 2026-06-01 Drive Stream-vs-Mirror resolution is gone since the git-native refactor (2026-06-16); the workspace root is the nearest ancestor with `AGENTS.md`.

### _archive/resolve-skills-symlink.sh + _archive/INSTALL-skills-resolver.md
- **Purpose**: ARCHIVED — the Drive-era machine-local resolver that pointed `~/.claude/skills` at whichever Drive root was materialized, plus its install note. Obsolete in the git-native model; kept for provenance (rows in `_archive/ARCHIVE-LOG.md`).
- **Last modified**: 2026-06-16 — archived from `00-bootstrap/setup/` (created 2026-06-01).

### 09-tools/profile_resolve.py
- **Size**: ~6069 lines
- **Purpose**: H2 declared resolver CLI and import home (tables, devices, remotes, repo walls, checkout cache, surface detection, agent check, gitcaps); H22 policy, classify, vetted-status, vetted_context, lift_env and receipts; H17 identity, override and floor (floor_decide).
- **Last modified**: 2026-10-13 — `fd5d1ab` the one GitHub route (owner → identity tables for `gh_route.py`); H17 identity, override and Claude git floor added 2026-09-23 in wave 0 (T8).

### 02-shared-references/vetted-scripts.json
- **Size**: ~25 lines
- **Purpose**: Vetted-script registry (DECISIONS-2 item 9; SENSITIVE); only the pinned copy is consulted.
- **Last modified**: 2026-09-23 — created in wave 0 (T7).

### 09-tools/fixtures/action_policy/
- **Size**: 2 files
- **Purpose**: TestActionPolicy/TestVettedContext fixtures: synthetic mirror of the committed action-policy rule ids (dev-a/dev-b) and a synthetic registry.
- **Last modified**: 2026-09-23 — created in wave 0 (T7).

### 02-shared-references/devices.json
- **Size**: ~119 lines
- **Purpose**: Declared device table (D14): hostnames, labels, projects_root, brain, ssh aliases; identities, personal markers, employer allowlist, identity rules IR1-IR3 and I1/I2 (H17).
- **Last modified**: 2026-09-23 — identity keys added in wave 0 (T8).

### 02-shared-references/delivery-playbooks/context-remotes.json
- **Size**: ~98 lines
- **Purpose**: Remote-keyed context table (H2): conduct order, owner classes at owner level, repos, employer path globs, employer_substance block for H25.
- **Last modified**: 2026-09-22 — created in wave 0 (T2).

### 09-tools/fixtures/profile_resolve/
- **Size**: 3 files
- **Purpose**: Synthetic tables (dev-a/dev-b, acme-corp/acme-bb/pat-sample/oss-upstream) for the profile_resolve self-test.
- **Last modified**: 2026-09-22 — created in wave 0 (T2).

### 00-bootstrap/doctor/pin_lib.py
- **Size**: ~826 lines
- **Purpose**: H24 pinned lib: PINNED_PATHS home, pin/current/lag, real-home guard, single write primitive; agent-pin checks.
- **Last modified**: 2026-10-13 — `fd5d1ab` pins `gh_route.py` and its two wrappers and runs its self-test at every agent pin; created 2026-09-22 in wave 0 (T3).

### 00-bootstrap/doctor/installers.py
- **Size**: ~3549 lines
- **Purpose**: H24 installers API/CLI (pin, shims, git-hooks, identity, claude-overlay, sandbox-roots, plugin, projects-pointer, launchd) with uninstall paths.
- **Last modified**: 2026-10-14 — `d3c4788` two self-tests (heal from workspace sessions, the split gh login note); created 2026-09-22 in wave 0 (T3).

### 00-bootstrap/doctor/workspace-doctor.sh
- **Size**: ~430 lines
- **Purpose**: Doctor v3: report-only unattended modes; HEAL limited to Claude-only injectors; installer flags exec installers.py.
- **Last modified**: 2026-10-14 — `d3c4788` `--check` tells a missing gh login from an unreachable API; `c59bbbe` made it executable (100755); created 2026-09-22 in wave 0 (T3).

### 09-tools/fixtures/installer/
- **Size**: 14 files
- **Purpose**: Synthetic installer fixtures: render list stand-in, stale v1 settings, probe record, fixture repo.
- **Last modified**: 2026-09-22 — created in wave 0 (T3).

### 02-shared-references/surfaces.json
- **Size**: ~5310 lines
- **Purpose**: Surface registry (H16): 22 surface rows, families, markers, formats, dialects, layers, commands, registrations, outputs, wrapper sha256, coverage (H22, H17); source for render_shims and profile_resolve detection.
- **Last modified**: 2026-10-13 — `fd5d1ab` overlay v6 + gh-route outputs; `current_wave` 2 since `f95d992` (2026-09-25); coverage.H17 and the overlay/identity-inc outputs added 2026-09-23 in wave 0 (T8).

### 00-bootstrap/doctor/render_shims.py
- **Size**: ~2369 lines
- **Purpose**: Generator and checker for every hook registration output declared in surfaces.json; Claude overlay env (v6 current; v4/v5 reproduction) and identity-inc emitters.
- **Last modified**: 2026-10-13 — `fd5d1ab` overlay v6 (the gh route credential helper); overlay and identity-inc emitters added 2026-09-23 in wave 0 (T8).

### 09-tools/fixtures/identity/floor_cases.py
- **Size**: ~491 lines
- **Purpose**: H17 hook-level fixtures: rendered floor under git config hooks, floor decisions with rule ids, bypass residuals, hasconfig identity, overlay installer on a temp HOME.
- **Last modified**: 2026-09-23 — created in wave 0 (T8).

### 09-tools/fixtures/identity/overlay-v5.golden.json
- **Size**: ~128 lines
- **Purpose**: Golden v5 overlay env and identity includes from the synthetic identity tables.
- **Last modified**: 2026-09-23 — created in wave 0 (T8).

### 09-tools/ws_hook.py
- **Size**: ~2540 lines
- **Purpose**: Neutral hook core behind the pinned ws-hook wrapper (H19).
- **Last modified**: 2026-09-22 — created in wave 0 (T1).

### 00-bootstrap/dist/ws-hook
- **Size**: ~7 lines
- **Purpose**: Byte-stable user-level hook entry; execs the pinned lib's ws_hook.py; sha256 pinned in surfaces.json.
- **Last modified**: 2026-09-22 — created in wave 0 (T1).

### 00-bootstrap/dist/ws
- **Size**: ~11 lines
- **Purpose**: Byte-stable neutral command entry: ws hook|resolve|intent|status.
- **Last modified**: 2026-09-22 — created in wave 0 (T1).

### 00-bootstrap/dist/probe/
- **Size**: 3 files
- **Purpose**: Probe registration fragments for claude-code, cursor and codex (installed only by Sean with --probe).
- **Last modified**: 2026-09-22 — created in wave 0 (T1).

### 00-bootstrap/dist/codex-config-fragment.toml
- **Size**: ~10 lines
- **Purpose**: Codex managed block: WS_SURFACE_FAMILY=codex and the telemetry writable root.
- **Last modified**: 2026-09-22 — created in wave 0 (T1).

### 00-bootstrap/dist/cursor-sandbox-fragment.json
- **Size**: ~5 lines
- **Purpose**: Cursor sandbox write root for telemetry only (config path unverified).
- **Last modified**: 2026-09-22 — created in wave 0 (T1).

### 02-shared-references/probes/README.md
- **Size**: ~54 lines
- **Purpose**: How host probe records are produced, promoted and redacted.
- **Last modified**: 2026-09-22 — created in wave 0 (T1).

### _archive/cursor-dark-shims-2026-09/
- **Size**: 6 files
- **Purpose**: Six retired Cursor shims (dark output or duplicate registration), with ARCHIVE-LOG rows.
- **Last modified**: 2026-09-22 — created in wave 0 (T1).

### 09-tools/fixtures/intent_run/
- **Size**: 2 files
- **Purpose**: Synthetic intent-spec fixtures (parser cases, a wave spec with selectors, @Tn, human: measures, HELD) for intent-run.py --self-test
- **Last modified**: 2026-09-22 — created in wave 0 (T6).

### 02-shared-references/employer-substance-baseline.json
- **Size**: ~119 lines
- **Purpose**: H25 employer-substance baseline: counts per (path, rule), no matched text; written only by T4 via check-secrets --write-baseline; may only shrink.
- **Last modified**: 2026-09-22 — created in wave 0 (T4).

### 09-tools/fixtures/employer_substance/
- **Size**: 8 files
- **Purpose**: Synthetic-owner fixtures (acme-corp/acme-bb) for check-secrets --self-test: fixture context-remotes table, planted/clean/growth texts, cache fixture, expected hits, never-print markers.
- **Last modified**: 2026-09-22 — created in wave 0 (T4).

### 09-tools/nightly.py
- **Size**: ~628 lines
- **Purpose**: Regeneration sequencer and nightly recipe entrypoint (H1): generator fixpoint, written paths, session scope, pre-commit lane.
- **Last modified**: 2026-09-22 — created in wave 0 (T5).

### 09-tools/fixtures/nightly/
- **Size**: 11 files
- **Purpose**: T5 self-test fixtures for nightly.py and the Claude dispatcher (X1 replay, timed SessionEnd accelerator, deferral payloads).
- **Last modified**: 2026-09-22 — created in wave 0 (T5).

### .claude/hooks/dispatcher.py
- **Size**: ~1761 lines
- **Purpose**: Claude Code hook dispatcher: defers to verified non-Claude hosts, SessionEnd delegates to nightly within 55 s, labels from devices.json, --self-test.
- **Last modified**: 2026-10-14 — `6dc1746` worktree auto-clean never deletes a live or dirty worktree; wave 0 changes 2026-09-22 (T5).

### 09-tools/gh_route.py
- **Size**: ~509 lines
- **Purpose**: One GitHub login route for every surface (pinned): the gh account follows the repo owner (`snds/*` → personal, the employer org → employer, any other owner → nothing). Reached as `bin/git-credential-ws` (git credential helper; lanes include + Claude overlay v6) and `bin/gh` (on PATH as `~/.local/bin/gh`). A gh call naming two owners is refused. `which` / `--self-test`.
- **Last modified**: 2026-10-14 — `4ee9ecc` ruff cleanup; created 2026-10-13 in `fd5d1ab`.

### 09-tools/pr-desk.py
- **Size**: ~382 lines
- **Purpose**: Vetted script: read a pull request's state and CI, push the checked-out feature branch, create a PR, and merge after Sean's review — only in the repos it names, through `vetted_context()` with one receipt per action.
- **Last modified**: 2026-10-14 — `4ee9ecc` ruff cleanup; created 2026-10-12 (`067ce47`).

### 09-tools/git_lanes.py
- **Size**: ~1487 lines
- **Purpose**: H18 git lanes: global config-based hooks for every local committer (Sean installs them with `--install-git-hooks`); stateless deciders by repo profile, entered through the pinned `ws-hook lane EVENT`.
- **Last modified**: 2026-10-13 — `fd5d1ab` lanes include carries the gh route; created 2026-09-24 (`05258eb`, wave 1).

### 09-tools/wall_guard.py
- **Size**: ~1712 lines
- **Purpose**: H15 workspace wall guard: one `decide()` over the action-policy table, reached from every hooked host (Claude Code, Cursor, Codex) through a generated shim; `report --days N` reads the guard log.
- **Last modified**: 2026-10-13 — `fd5d1ab` file edits are their own class (`edit`); created 2026-09-24 (`80d7ccb`, wave 1).

### 09-tools/closure.py
- **Size**: ~854 lines
- **Purpose**: H23 surface- and device-aware session closure: reads each session's touch ledger, classifies every touched repo, prints its closing action (`ws closure plan`); H25 limits on fragments from employer-touched sessions.
- **Last modified**: 2026-10-06 — `b2f5aab` Claude becomes an employer-approved surface; created 2026-09-25 (`d954d70`).

### 09-tools/workspace_mcp.py
- **Size**: ~980 lines
- **Purpose**: H21 workspace MCP server (stdio JSON-RPC, stdlib only) for MCP-only hosts — Claude Desktop Chat/Cowork, Claude Code desktop, Codex, other clients; replaces the generic workspace-fs server and refuses employer folders, generated files and path escapes on write.
- **Last modified**: 2026-09-26 — `c03a395` session_status names the mapped surface; created 2026-09-26 (`426f8fe`, W3-6).

### 09-tools/backup-projects.py
- **Size**: ~887 lines
- **Purpose**: Finds project folders under the projects root with no git repo and backs them up to new private GitHub repos (leaf projects only; skips dependency/build folders and the workspace checkout).
- **Last modified**: 2026-09-26 — `f9cf51a` blocks router and device backups; created 2026-09-26 (`a304294`).

## Meridian Design System — 07-projects/01-mediaservices/files/meridian-ds/ (local only, gitignored)

### app-shell-prototype-v0.1.jsx
- **Purpose**: Full app shell prototype — sidebar nav, topbar, 6 views, search, modals, responsive layout
- **Last modified**: 2026-03-08 — Cross-prototype alignment pass (focus ring, modal focus trap + exit animation)
- **Contents**: Token definitions · Badge/Chip scales · Responsive system · surfaceCtx() · Icon + ICON_MAP · NAV_ITEMS / NAV_BOTTOM · Button · Input · Select · typeBadgeStyle() · PosterImage · StatusPill · Card · SettingToggle · SegmentedControl · HScrollArea · Dropdown · Topbar · Sidebar · SearchBar · SearchDropdownRow · SearchDropdown · NotificationBell · Toast · PosterCard · LIBRARY_TITLES (mock data) · SearchResults · ViewDashboard · RatingBadge · EditTitleModal · ViewLibrary · ModalShell · ManageFilesModal · SearchResultRow · InteractiveSearchModal · ViewActivity · GrabConfirmDialog · SourceTierPicker · ViewQuality · QualityProfileWizard · ViewSettings · ProfileSourceBadge · QualityProfilesSection · SettingsQualitySection · SettingsGroup / SettingsRow · BottomTabBar · MeridianApp (default export) (line-number tables dropped 2026-10-14, ^pc-12(d) — search the file for a section name)

### setup-wizard-prototype-v0.1.jsx
- **Purpose**: 6-step setup wizard: account, storage, downloads, indexers, quality, health check
- **Last modified**: 2026-03-08 — Cross-prototype alignment (Card API, surfaceCtx aliases, text.tertiary contrast)
- **Contents**: Token definitions · Badge/Chip scales · surfaceCtx() · Responsive system · ICON_MAP · Icon · Button · Input · Select · Toggle · StatusPill · Card · ProgressBar · StepAccount · StepStorage · StepDownloads · StepIndexers · LANGUAGES array · LanguageSelect · StepQuality · StepHealthCheck · MobileStepIndicator · SetupWizard (default export) (line-number tables dropped 2026-10-14, ^pc-12(d) — search the file for a section name)

### meridian-design-system-v0.1.jsx
- **Purpose**: Foundation reference component library — token demos, theme switching, component gallery
- **Last modified**: 2026-03-07 — Initial creation (Phase 0)
- **Contents**: Global Primitives · Semantic Tokens · Typography · Spacing · Radius · Elevation · Motion · ThemeContext · SwatchGrid · TokenPair · TypeSample · StatusBadge · ProvenanceBadge · SampleButton · SampleCard · SampleActivityItem · SampleHealthIndicator · SampleInput · MeridianDesignSystem (export) (line-number tables dropped 2026-10-14, ^pc-12(d) — search the file for a section name)

### theme-tokens.css
- **Purpose**: CSS custom properties for dual-theme system (dark/light). All Tailwind semantic colors resolve via var() references here.
- **Last modified**: 2026-03-08 — text.tertiary dark mode contrast fix (#78859a → #8892a4)
- **Contents**: Dark theme (:root) · Light theme · System preference fallback · Surface context cascades (CSS) · Reduced motion (line-number tables dropped 2026-10-14, ^pc-12(d) — search the file for a section name)

### tailwind.config.js
- **Purpose**: Tailwind CSS config consuming CSS custom properties from theme-tokens.css
- **Last modified**: 2026-03-08 — Added testing status, info/testing ctx, radius var() refs
- **Contents**: Content + dark mode · Font families · Font sizes · Border radius · Extended colors · Spacing · Box shadow · Backdrop blur · Transition duration · Transition timing (line-number tables dropped 2026-10-14, ^pc-12(d) — search the file for a section name)

### ds-triage-report_v1.0_2026-03-08.md
- **Purpose**: Comprehensive triage report: 4-axis methodology, token coverage, ARIA compliance, cross-prototype drift, spec-to-implementation gaps. Contains DDRs DS-2026-001 through DS-2026-009.
- **Last modified**: 2026-03-08 — All H/M items resolved, DDR DS-2026-009 added

### ds-audit-report-v0.1.md
- **Purpose**: Component & token audit: structural soundness, drift analysis (spec vs CSS vs JSX), 5 critical areas for Phase 1
- **Last modified**: 2026-03-08 — Audit completed

### surface-context-audit-v0.1.md
- **Purpose**: Surface-aware context system audit: compliance checklist for tinted surfaces, 9 context maps, resolution rules
- **Last modified**: 2026-03-08 — Audit completed

### wcag-audit-v0.1.md
- **Purpose**: WCAG 2.1 AA contrast audit: 96 pairings tested, 78 pass, 8 failures with remediation, 6 intentional substandard
- **Last modified**: 2026-03-07 — Initial creation

### MERIDIAN-DS-SPEC.md
- **Purpose**: Consolidated token & component spec: three-tier architecture, surface tokens, semantic mappings, typography, spacing, radius, elevation
- **Last modified**: 2026-03-07 — Initial creation

### meridian-ds-spec-v0.1.md
- **Purpose**: Detailed v0.1 foundation spec: design principles, token architecture rationale, three-tier justification
- **Last modified**: 2026-03-07 — Initial creation

### component-anatomy-spec-v0.1.md
- **Purpose**: Component definitions: Button, Card, Input, Badge, Dialog, Select, Checkbox, Radio — anatomy, prop API, variant matrix, states, a11y
- **Last modified**: 2026-03-07 — Initial creation

### component-tokens-spec-v0.1.md
- **Purpose**: Component-tier token layer spec: naming convention, three-tier architecture, surface context system (9 contexts), override pattern
- **Last modified**: 2026-03-07 — Initial creation

### density-modes-spec-v0.1.md
- **Purpose**: Comfortable/Default/Compact density tiers: independent of theme, typography/spacing/touch target adjustments
- **Last modified**: 2026-03-07 — Initial creation

### app-shell-spec-v0.1.md
- **Purpose**: App shell architecture: sidebar+topbar layout, nav structure, search, notifications, responsive breakpoints
- **Last modified**: 2026-03-07 — Initial creation

### data-model-spec-v0.1.md
- **Purpose**: Data model: 5 design principles, 20+ entities with relationships, event sourcing
- **Last modified**: 2026-03-07 — Initial creation

### data-model-erd-v0.1.mermaid
- **Purpose**: Entity-relationship diagram: Title/Season/Episode/MediaFile/ExternalID/QualityProfile entities
- **Last modified**: 2026-03-07 — Initial creation

### module-interfaces-spec-v0.1.md
- **Purpose**: Module architecture: 12 Go modules, direct interface calls + event bus, dependency graph
- **Last modified**: 2026-03-07 — Initial creation

### go-scaffold-spec-v0.1.md
- **Purpose**: Go project structure: cmd, internal, pkg, tests, DI wiring, build/run scripts
- **Last modified**: 2026-03-07 — Initial creation

### auth-architecture-spec-v0.1.md
- **Purpose**: Auth & session design: passkey-first, zero external auth, session durability, CSRF/XSS protections
- **Last modified**: 2026-03-07 — Initial creation

### privacy-architecture-review-v0.1.md
- **Purpose**: Privacy audit: external connection registry, metadata API payloads, anonymity-preserving patterns
- **Last modified**: 2026-03-07 — Initial creation

## centricPLM — 07-projects/02-centricPLM/context/ (gitignored)

### cell-indicators-pilot.md
- **Purpose**: Authoritative running state of the C8 data-table cell-indicator system (Figma branch `cell-indicators`): DS sourcing rules, cell architecture, code-validated indicator matrix (GROUNDED/ADD-VIZ/FUTURE tiers), two-tier editability model, read-only lock+tint three-scope system, worst-case density demo, node IDs, and open Sean sign-offs.
- **Last modified**: 2026-07-02 — worst-case scattered-locks demo + tooling gotchas appended

## figma-repo-sync-plugin — 07-projects/09-figma-repo-sync-plugin/docs/ (gitignored)

### 2026-05-22-color-pipeline-refactor-plan.md
- **Purpose**: Root-cause audit (3-agent) of the shadcn→Tailwind→Figma color pipeline + phased refactor plan. Documents the divergent-parser / two-token-table / silent-literal-fallback hazards and the Phase 0–4 plan.
- **Last modified**: 2026-05-22 — Initial creation

### 2026-05-23-state-representation-decision-tree.md
- **Purpose**: Authoritative CVA variant×state→Figma spec. Locked decisions: physical State axis, normalized state-layer (Decision B), grouped `<slot>/<state>` naming with explicit `default`, ring-as-stroke-overlay anatomy, state-layer opacities (12/24/32/50%), per-component derivation. Carries the ⚠ engineer-doc requirement for the `default` affordance.
- **Last modified**: 2026-05-23 — Initial creation

## subatomic-design-tokens-course — 07-projects/23-subatomic-design-tokens-course/

### CURRICULUM.md
- **Purpose**: Generated index of the Frost *Subatomic* course (11 sections, 372 items, 360 lessons, ~13.6 h) with per-section durations, lesson titles, downloadable files, and links to the chapter notes. Regenerate from `<Projects>/subatomic-design-tokens-course/manifest/manifest.json`.
- **Last modified**: 2026-09-23 — Initial creation

### notes/ (00-01 … 09-10)
- **Purpose**: Original chapter notes (no transcript text): core concepts, three-tier architecture, naming algorithm + parity divergences, building in Figma + Style Dictionary, publishing, adoption levels, governance/SemVer, advanced axes (dark mode, sub-brands, white-label, i18n, rebrand, AI), summary + 166-link resource index. Each ends with For Sean + Mechanizable rules.
- **Last modified**: 2026-09-24 — review corrections (tier_prefixes, z-index exemption, two reworded sentences)

### synthesis/running.md
- **Purpose**: Thesis, what Subatomic added to workspace doctrine, harness calibration table on the course demo repo (incl. the 2026-09-24 review/re-run), open questions.
- **Last modified**: 2026-09-24 — adversarial review + recalibration (30 CSS warnings, 3 contrast failures, 1 dark drift)
