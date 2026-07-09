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

---

--- SESSION BLOCK ---
Date: 2026-07-09 (DORMANT SESSION CLOSED — work performed 2026-06-10 -> 06-11; the 02-centricPLM blocks below already continued this thread through July. Read those for current state; this block is the historical record of the founding audit/plan/Figma work.)
Agent: Claude Fable 5
Surface: Claude Code (Mac desktop app)
Machine: Work MacBook Pro (main) (CS-K746DRWXY1)
Project(s): 05-C8-PLM / 17-data table — Dojo table audit -> TanStack parity -> migration plan -> Figma D0 state variants (Tables branch `Mvspja56GC0x6myay0b9FM`)
Artifacts: (since migrated to 05-artifacts/active/)
  - c8_dojo-table-feature-audit_v1.0_2026-06-10.md — 76 features / 16 groups + 10 activation mechanisms (XML view defs ~70%); 2,477 `<View xsi:type="Table">` across 47 module XMLs
  - c8_table-surface-traversal_v1.0_2026-06-10.md — per-module distribution (top 7 = 63%), surface-type breakdown, reproducible greps
  - c8_tanstack-parity-analysis_v1.0->v1.2 — v1.2 = 8-agent re-audit vs CDS 2.0.0-develop-80: 17 covered / 31 partial / 28 missing; 12 consolidated asks + verified OSS subcomponent matrix
  - c8_table-migration-plan_v1.0->v1.2 + c8_table-migration-dashboard_v1.0/v1.1 — design/eng split, 1-designer critical path, Gantt w/ design-needed-by milestones, Jira-ready tickets, item->ticket coverage matrix
  - Figma (branch): D0 proposal page (6 create-state cards + decisions + RAT-1 frames) · 6 State values (Error, Inline Edit - Error, Save Failed, Saving, Read-only, Skipped (Bulk)) propagated to 24 cell sets (~138 variants), incl. Sean's pattern adjustments (helper padding, helper-off on Read-only/Skipped, disabled bg)
Decisions:
  - CDS DataTable (TanStack v8) = settled migration target; `manual*` server-mode flags = highest-leverage CDS ask; XML view-def->ColumnDef adapter = the migration lever for 2,477 views
  - Create-vs-ratify split: 11 of D0's 18 "missing" cell states already render in CDS code -> RAT-1 ratify pass paired with pilot; only 6 states were draw-work
  - TableOld = behavioral spec, NOT source to port (dnd-kit 6.3.1 maintenance-only -> pragmatic-drag-and-drop); OSS verified: write-excel-file (exceljs frozen 2023), papaparse, Playwright page.pdf() server-side, Standard Schema validators; NO TanStack clipboard/fill ecosystem package exists — DS-owned build
  - Figma variants built the file's own way (nested library-instance switches: Text field Error/Error+Focus/Type=Read-only, Helper text Type=Error, 005 progress_activity + edit_off, color/background/disabled). Library gaps surfaced -> 003 asks: Error+Focus + Read-only equivalents on date/reference/enum field masters; Filled+isDisabled Text field combo
  - Layout-normalization pass REVERTED at Sean's direction: canvas geometry is authored content (rows not columns; variant spacing deliberately clears abs-positioned overflows; set widths encode decisions). Recovery = restore-from-main via branch-preserved GUIDs. Standing rule: snapshot x/y/w/h before ANY bulk geometry change; ask the organizing principle, never infer it
Pending added (as of this session's close — check newer blocks for supersession):
  - Branch review/merge of D0 proposal + 24-set rollout; Sean re-spaces the added variants himself
  - D0 delta remainder + token-binding verification on cell components; charts keep/kill gate pending SPK-E3 telemetry; Jira import draft from plan v1.2
Next:
  - None new — the cell-indicators and cell-system-marathon blocks below are the live continuation of this thread
--- END BLOCK ---

--- SESSION BLOCK ---
Date: 2026-07-09 (session ran 2026-07-07 → 07-09; canvas/doc edits auto-committed at exit as 0cbfc3f/46d1166)
Agent: Claude Fable 5
Surface: Claude Code (Mac desktop app)
Machine: Work MacBook Pro (main) (CS-K746DRWXY1)
Project(s): 02-centricPLM — C8 cell system marathon: drag-to-fill + fill-range, CDS keyboard docs, mode→physical migration (Align + Validation axes), header v2, Jabili validation treatment, CVD options, dense 24px study
Artifacts:
  - 07-projects/02-centricPLM/context/cell-indicators-pilot.md — 10 new dated blocks; THE session record (node ids, findings, open decisions)
  - 08-knowledge/design/figma-ds-surface-authoring.md — rule 16 (in-flow utility rows · hidden-content wrappers = default-OFF boolean · overlay geometry re-assert) + variables/modes mechanics
  - Interactive artifact (primary deliverable per Sean): https://claude.ai/code/artifact/f05e65c1-727d-4858-aac5-6df153cad62b — migration plan / 29-set matrix / alignment grid / playground
  - Figma Tables file: .cell/drag-to-fill + drag-to-fill-range sets; Align axis on 4 sets (+56 var); Validation axis pattern on single-line (63 var, Jabili treatment); cell/header (v2) 36 var + sticker sheet; Documentation page (DataTable keyboard doc, decision matrix); ~8 demo/evidence boards
Decisions:
  - Sean: modes-as-variants REJECTED for alignment and validation → physical variants; standing rule = recolor→mode · show/hide→boolean · structure/style/alignment→physical · type-fixed→static · 003-blocked→additive-only library ask
  - Sean: explicit default modes on every variant root, never Auto (mirrors to instances; healed a live checkbox left-align regression)
  - Sean: read-only = color-only (fontStyle is a dead channel in instances — 79 bindings purged); wrapper rule = any all-hidden-children frame carries a default-OFF boolean; header labels wrap max 3 lines then ellipsis
  - Jabili (via Sean): entry validation = form treatment as-is (TF Error/Error+Focus); display validation = pale status surface + 2px severity border; warning border = orange accent interim (no warning token — CDS-WIP interface/status/* exists, adopt later)
  - Vision-evaluation doctrine: severity mode alone rendered 0 pixels (boolean-gated) and Warning amber failed 3:1 — machine-vision permutation testing is now the verification bar; test-the-override before filing library asks (two "locked internals" walls broke under direct testing)
Pending added:
  - Validation rollout decisions (Sean): CVD redundancy option A/B/C; entry-error weight parity; Error+Focus severity-over-focus 003 ask; then axis rollout to ~25 sets (+~520 var; refmap 105 — prune?); Cell Value modes verdict outstanding
  - Re-run c8 legacy-indicator asset extraction (agent lost to process exit) → build before/after indicator boards per cell type
  - Dense 24px floors → 003 asks: TF wrapper structural trim, small checkbox box, Small chips + single-row truncation; target 24 vs 26/28 pending team
  - Housekeeping batch still open: KPI parked-frame instance check; Invalid-boolean → Validation-axis instance migration + collection deprecation after rollout
Next:
  - Sean reviews the artifact decision points → treatment sign-offs → scripted Validation-axis rollout; header v1→v2 instance migration plan; P3 Active-axis demotion after
--- END BLOCK ---

--- SESSION BLOCK ---
Date: 2026-07-09
Agent: Claude Fable 5
Surface: Claude Code (Mac desktop app)
Machine: Work MacBook Pro (main) (CS-K746DRWXY1)
Project(s): 02-centricPLM — C8 data-table cell-indicator system (Figma branch `cell-indicators`; long-running session 2026-06-29 → 07-02, closed 07-09)
Artifacts:
  - 07-projects/02-centricPLM/context/cell-indicators-pilot.md — full pilot state: validation matrix, editability model, read-only system, worst-case demo (gitignored, on-disk)
  - 08-knowledge/engineering/figma-cli-authoring.md — §11 `use_figma` MCP as branch-safe fallback (committed via the 07-08 sweep)
  - 08-knowledge/design/figma-ds-surface-authoring.md — §7b clip-content-OFF standing rule, §7c indicator halo pattern (committed via the 07-08 sweep)
  - Figma (branch): 4-variant CVD corner set w/ halos · sticker board regrouped by grounding tiers + legend · `.cell/indicator-lock` + three-scope read-only demos · real-table + in-context Views demos w/ leading utility gutter · worst-case scattered-locks board (A locks / B tint-only)
Decisions:
  - All 11 indicators code-validated on 3 axes (model/rendered/usage) → tiers GROUNDED / ADD-VIZ / FUTURE; future-forward retained (Recent, AI); Inherited dropped (only expression-override exists = Computed "Overridden" struck-ƒx)
  - Computed OFF booleans, KPI (icon-status conflict), email/phone/link/barcode; ON text enums (AQL usage)
  - Read-only = lock + tint at MATCHED scope (cell / row / column-header), values stay full-contrast — replaces italic+muted (team noise concern); tooltips reason-differentiated via server AttributeEditability.Reason
  - Editability is two-tier (column-uniform + per-node) — per-cell locks within editable columns are real and common; hypothesis refuted
  - Row-lock lives in a leading utility-gutter column (flush-left tables have no outside gutter; precedent = Views toggle column)
  - Legibility = layered system: tooltip as primary teacher + contextual legend + hybrid dot→glyph-on-hover
  - Standing rules: clipsContent OFF by default everywhere; indicators on variable backgrounds get a white halo backing
Pending added:
  - Sean sign-offs: lock-vs-italic propagation to the 26 cell sets · enum-chip Computed keep/drop · worst-case density rule (always-lock / tint-only / density-adaptive)
  - Clean 005 icon board for the dot-vs-icon corner call (fix edit/refresh glyph fill; source a chat/comment glyph) · nested `Status` exposure parked until designers ask
Next:
  - On sign-off: propagate the lock read-only treatment (replace the `Cell Value` Read-only mode), componentize the utility gutter + `cell/header` `Locked` prop, then the icon board
--- END BLOCK ---

--- SESSION BLOCK ---
Date: 2026-07-09
Agent: Claude Fable 5
Machine: Personal MacBook Pro
Surface: Claude Code (Mac desktop app)
Project(s): Workspace foundations — Audience & Evidence system (delivery playbooks + context profiles + Proofboard standard)
Artifacts:
  - 02-shared-references/delivery-playbooks/ — NEW 7-file standard: README (pre-delivery gate: context → audience → translation → medium), 00-context-profiles (context is king — declared profiles, resolution order, fail-safe), 01-audience-contract (forward test, jargon rule, three altitudes w/ caveats-at-top), 02–04 medium playbooks (diagrams/flows · data/charts · documents/specs; Media Sentinel HTML-page failure preserved as founding anti-example), 05-validation-harness (Proofboard: contract register, show-me evidence, sandbox, failure gallery, honesty strip).
  - 05-artifacts/active/workspace_validation-session-prompt_v1.0_2026-07-09.md — 6-phase validation test prompt with checkpoint/confirmation loops + adversarial path-walk (token-waste audit, trigger gaps, unexercised-path desk-check). Local only — 05-artifacts is gitignored; copy before use on another machine.
Decisions:
  - Context is king = layer zero of delivery: profiles are DECLARED facts (`personal-solo` / `centric-engineering` / `centric-design`, + `visibility: public` flag), never per-task guesses. Resolution: Sean's word → project declaration → repo remote → stop and ask; fail-safe = most restrictive. Citing rule: name the profile when acting on it.
  - Placement: shared-reference playbooks now; framework #11 later only if earned (3+ consumers rule). Enforcement wired into 8 surfaces: AGENTS.md core rules, CLAUDE.md (section + trigger rows), dispatcher TRIGGER_WORDS (16 entries), #06 pre-output gate (context & medium check fires FIRST, ahead of target-user), frameworks 00-README, workspace-ontology delivery vocabulary, SESSION-STATE template `Context profile` field, user-preferences pointer.
  - Proofboard = definition of done for code-heavy work ("Sean verified it without reading code"). Must render REAL tests (no hand-authored theater), carry a failure gallery + honesty strip; per-profile meaning: personal-solo → board IS the review; centric-engineering → board alongside (never instead of) engineer evidence.
  - Adversarial review as closing gate (Sean's directive): independent agent, 12 findings — 11 fixed, 1 accepted (`diagram` trigger noise). Headline lesson: first pass was "Claude-shaped, not workspace-shaped" — AGENTS.md (entry point for all other agents, whose handoff protocol instructs commit+push) now carries the profile rule and scopes commit/push to personal-solo repos only.
Pending added:
  - "Context is King — workspace foundation refinements" (top of Active) — generalize profile resolution to every session surface: ritual, hooks, all 8 SESSION-STATE files, memory routing, skill loading.
Next:
  - Sean runs the validation session prompt in a fresh session (phases 0–5 → scorecard); re-run after the backlog item lands to compare.
  - Populate `Context profile` in all 8 SESSION-STATE files + create a Media Sentinel project entry (until then, repo remote is the only mechanical resolver — fail-safe carries the rest).
  - Optional: extract the Proofboard build procedure from 05-validation-harness.md into a 03-skills skill.
--- END BLOCK ---

--- SESSION BLOCK ---
Date: 2026-07-08
Agent: Claude Fable 5
Surface: Claude Code (Mac desktop app)
Machine: Work MacBook Pro (main) (CS-K746DRWXY1)
Project(s): Claude Workspace Infrastructure — post-mortem of the C8 cell-validation failure → trigger/dispatch layer rebuilt, foundational color/UX/a11y routing wired, self-healing added
Artifacts:
  - 06-context/audit-log.md — 2026-07-08 audit entry (14 findings: 4 P0 / 6 P1 / 4 P2; fixes + carry-forwards; resets the 72-day staleness)
  - .claude/hooks/dispatcher.py — hookEventName fix (null → payloads were SILENTLY dropped; whole context layer was dark); runtime trigger matching from skills.registry.json + _INDEX.md Triggers lines (word-boundary); foundational vocabulary (validation/warning/status color/contrast/a11y → foundations-first route); compact/resume re-orientation injection; stale-audit escalation (>2x threshold); once-per-session use_figma PreToolUse design-judgment gate; session-end registry auto-regen
  - .claude/settings.json — PreToolUse hook registered (matcher mcp__.*use_figma.*)
  - 01-frameworks/06-qa-operating-model.md — sixth operating default "System-context fidelity" + Accessibility check in the pre-output gate (judgment-framed, not prescriptive)
  - 03-skills — triggers: declared on ds-advisor / design-engineer / figma-canvas-designer / visual-qa-toolkit / a11y-visual / uid-color-for-ui; narrowed sec-supply-chain `token` + sec-authn-authz `session`; infod-encoding-theory +found-color prereq; registry regenerated (246 skills, --check green)
  - 09-tools/validate-workspace.py — new KNOWLEDGE COVERAGE check; _INDEX.md research section indexed (5 entries); `figma-plugin-patterns 2.md` conflict copy archived w/ ARCHIVE-LOG provenance
  - 08-knowledge/engineering/claude-code-hooks-contract.md — NEW: hook payload contract gotchas (hookEventName, PreToolUse deny-as-injection, SessionStart source)
  - 02-shared-references/ds-agents-binding.md + CLAUDE.md + 3 knowledge docs — system-fidelity rule mirrored; stale claims fixed (skills-manifest, handle_user_prompt_submit, 08-tools, "mirrors TRIGGER_WORDS", "loads the skill registry")
Decisions:
  - Root cause of the cell-validation failure: every carrier of the foundations was advisory, stale, empty, or dropped — dispatcher emitted hookEventName:null (harness silently drops the payload), trigger tables frozen vs registry/_INDEX, zero triggers on applied design skills, no gate at use_figma. Fixed at all four layers; the exact failing prompt now routes to the foundations chain (verified by replay).
  - Foundations are DS-independent (Sean): baseline = design-foundations → found-color → a11y-visual → uid-color-for-ui, loaded BEFORE any system-specific rules; [[radix-derived-color-system]] is a system-specific application layer — scoped with a note, never generalized to non-Radix systems (e.g. C8).
  - System-context fidelity codified (framework #06 default 6 + ds-agents-binding + gate): resolve within the target DS's own tokens/DESIGN.md/libraries; token gaps → backlog while the prompt's problem still gets solved now; a11y compliance is never deferred (per lead-accessibility-architect).
  - Gates prompt judgment, not rules (Sean correction): no prescriptive palette rules — full-color full-bleed surfaces with foreground text/icons are legitimate when the implementation holds up; the non-negotiable is VERIFICATION (APCA/WCAG pairing checks, CVD redundancy). Worked examples are emblematic, not rulesets.
  - APCA guidance is a deliberate TIER, not a contradiction (Sean): a11y-visual = accessibility floor (bare minimum) · design-engineer table = working target ("happy middle") · radix entry = Radix-scale-specific (the 12-step scale is tuned to reach it; Radix-generated palettes inherit it). Cross-linked tier notes in all three files.
Pending added:
  - C8/CDS semantic status-token gap (warning tint/stroke; orange accent border as documented interim) — flesh out status/context semantic tokens, raise as CDS ask
  - 2026-07-08 audit carry-forwards (b)–(f): remaining a11y-skill triggers decision, CVD prevalence alignment, artifact-registry line-number tables, doctor conflict-copy sweep, research/research double-nesting
Pending resolved:
  - Workspace audit staleness (72 days) — audit-log entry 2026-07-08; carry-forward (a) APCA floors resolved per Sean's tiering
Next:
  - Watch the next real design session for gate + trigger behavior in the wild (the resume re-orientation already fired live this session)
  - Decide carry-forward (b): frontmatter triggers for ux-accessibility / fe-accessibility / visual-qa-accessibility / lead-accessibility-architect / gd-color-theory / infod-encoding-theory (deferred to avoid over-firing)
--- END BLOCK ---

--- SESSION BLOCK ---
Date: 2026-07-07
Agent: Claude Fable 5
Surface: Claude Code (Mac desktop app)
Machine: Work MacBook Pro (main) (CS-K746DRWXY1)
Project(s): Centric VMS Design System — ds-docs security dependency update + parked changelog work shipped as PRs
Artifacts:
  - ds-docs PR #2 (chore/deps-security) — next 16.2.4→16.2.10 (clears all 13 GHSAs incl. 8.6 SSRF + 8.1 middleware bypass), eslint-config-next lockstep, overrides.next.postcss ^8.5.10, transitive audit fixes. npm audit 0 vulns; lint/types/build green.
  - ds-docs PR #3 (feat/changelog-hub) — the parked changelog system (hub rows + native-dialog article view, feed.json/llms.txt API routes, notification opt-in, sidebar indicator) + PageHero/KeyFacts/UseCases blocks + ~40-page content sweep. 6 CI errors + a useSearchParams prerender failure fixed forward; verified in-browser against the prod build (dialog open/close/deep-link, API url field, zero console errors).
Decisions:
  - next 16.2.10 (latest 16.2.x) still hard-pins nested postcss 8.4.31 (GHSA-qx2v-qp2m-jg93) → npm `overrides` is the only clean fix; REMOVE the override when next bumps its pin. Quirk: overrides don't retro-apply to existing lockfile entries — delete the nested package-lock entry + node_modules copy, then reinstall.
  - Fixed the parked changelog WIP forward to green rather than pushing a red PR; fixes follow repo idiom (useSyncExternalStore over setState-in-effect, Suspense-scoped useSearchParams so /docs/changelog statically prerenders).
  - Both PRs stacked on chore/license-ci (#1) because it carries the ESLint-9 pin. ds-docs CI only triggers on PRs targeting main → checks appear once #1 merges and GitHub auto-retargets. Merge order: #1 → #2 → #3.
Pending added:
  - ds-docs PR #3 ships 28 hardcoded localhost:6006 Storybook links (PageHero chips + home page) — swap when NEXT_PUBLIC_STORYBOOK_URL + deployment land (folded into the existing deployment pending item).
Next:
  - Sean assigns reviewers on ds-docs #2 + #3; merge #1 first.
  - After #1 merges: mark `lint, types, build` required status check (existing pending item), then CODEOWNERS + deployment todos.
--- END BLOCK ---

--- SESSION BLOCK ---
Date: 2026-07-06
Agent: Claude Fable 5
Surface: Claude Code (Mac desktop app)
Machine: Work MacBook Pro (main) (CS-K746DRWXY1)
Project(s): 02-centricPLM (C8-99959 floating toolbar) · workspace bootstrap v2
Artifacts:
  - workspace-bootstrap-durability-plan_v2.0_2026-07-06.md — red-teamed layered bootstrap plan (05-artifacts, local-only)
  - floating-toolbar_ticket-drafts_v1.1_2026-07-06.md — POSTED: C8-99959 comment 3565642 · CDS-1247 comment 3565643 · CDS-1388 filed + linked (Relates → CDS-1247)
  - Figma "Floating Toolbar — Responsive Collapse" board (toolbar file, node 3543-69658) — bug repro, 4-state collapse ladder on real CDS components, GTIN empty states A/B, FILL-overlap fix
Decisions:
  - Bootstrap v2 SHIPPED, all phases: deterministic layers L1–L4 + SessionEnd audit + launchd doctor (4h+login); ritual token frozen ABI; Cursor sessionStart gate PASSED (user-global ~/.cursor/hooks.json confirmed); snds plugin 0.3.0 ships the hook. See [[decision-bootstrap-v2-guarantee]].
  - C8-99959 design decision posted: bar always fits its owning pane; anchor-pinned collapse ladder (Roomy/Medium/Narrow/Floor); pane-measured breakpoints; expanded surfaces on the escape layer; slot contract {full, compact, priority, minWidth} → CDS-1247 asks.
  - Figma FILL-deficit standing rule: FILL absorbs surplus never deficit; explicit minWidth on every FILL region (library-side — minWidth is NOT overridable on instance children); fold content first, frame follows → figma-ds-surface-authoring rule 15.
Pending added:
  - Paste BEACON.md into 4 chat surfaces, then workspace-doctor --ack-chat
  - Curate 00-bootstrap/dist/beacon-repos.txt (candidates: design-system, open-design)
Next:
  - Restart Claude Code to activate snds plugin 0.3.0 hook layer
  - Watch ~/.claude/ws-state/audit.log for MISS lines over the first week
  - Follow up CDS-1247 asks + CDS-1388 with the CDS team
--- END BLOCK ---

--- SESSION BLOCK ---
Date: 2026-06-30
Agent: Claude Opus 4.8
Machine: Personal MacBook Pro
Surface: Claude Code (Mac desktop app)
Project(s): Workspace foundations — framework migration (#10) + brain /optimize audit
Artifacts:
  - 01-frameworks/10-perception-integrity.md — NEW top-level framework #10 "Perception Integrity": cross-cutting native-resolution precondition to ALL visual evaluation (design QA, game/3D, shaders, photography, data-viz). Principle here; method stays in the native-visual-eval skill.
Decisions:
  - Promoted perception integrity from Last-Mile Craft §2.5 to standalone framework #10 (it governs all visual work, not just design finishing). Named "Perception Integrity" — principle in framework, method in native-visual-eval skill.
  - Framework set is now ten (01–10): nine cross-domain operating lenses + #09 the design-domain hub. Embedded copies (#05 §2.5, #06 Resolution check + reference protocol, README #05 bullet) slimmed to pointers; #05/#06 kept reading-complete.
  - Workspace-wide framework-count enumerations updated to ten (00-README full pass, _FRAMEWORKS, _HOME, CLAUDE.md, BOOTSTRAP, brain.mdc); CLAUDE.md + brain.mdc also gained the previously-missing #09.
  - /framework-check expanded 5→10 (six core lenses always-run; situational lenses 07–10 gated by domain) — autonomous scope call, flagged for Sean to confirm.
Pending resolved:
  - Build visual-qa-toolkit skill — found already built + registered (2026-06-30 /optimize); docs flipped from "being built" to built.
Other changes:
  - /optimize full audit (first since 2026-04-27): 9 findings (P0 1 · P1 4 · P2 4), 7 fixed, logged to audit-log.md. P0 = validate-workspace was RED (memory file unlisted in MEMORY.md) → fixed, all three validators green.
  - native-visual-eval + lead-visual-qa surfaced in _SKILLS.md Visual QA cluster; _HOME skill count 60+→280+; new-project default frameworks five→ten.
Next:
  - Confirm /framework-check 5→10 gating model matches intent.
  - Refresh the opt-out optimize/SKILL.md stale "5 framework files (01–05)" read-list next time that skill is edited.
Deferred push:
  - 3 local commits (764ac03, 25509d0, + this session) NOT pushed — origin/main diverged with a1c1925 (Work MacBook Pro "externalize local memory to workspace"). Sean to handle the merge. True conflict set (5 files): session-log.md, MEMORY.md, project-context.md (additive — keep both) + CLAUDE.md, 01-frameworks/05-last-mile-craft-framework.md (both edited content — review). Suggested: `git pull --no-rebase`, resolve keeping both sides for the additive files, re-run the 3 validators, push.
--- END BLOCK ---

---

--- SESSION BLOCK ---
Date: 2026-06-30
Agent: Claude Opus 4.8
Surface: Claude Code (Mac desktop app)
Machine: Work MacBook Pro (main) (CS-K746DRWXY1)
Project(s):
  - Workspace contribution — migrated ALL durable content out of Claude Code's local/private memory into the portable workspace, and installed a standing "externalize everything" rule.
Decisions:
  - Standing directive (set by Sean): keep NOTHING durable in any agent's private memory; everything routes to the workspace (or the platform `Projects` dir for repos/working files). The only internal memory is a pointer back. Rationale: `06-context/memory/decision-externalize-everything-to-workspace.md`.
  - Cross-surface persistence via the universal contract: encoded as an AGENTS.md Core rule + ontology routing row + llms.txt + CLAUDE.md, so Claude Code / Chat / Design + any future agent inherit it.
  - Routing per the workspace-ontology map; consolidation = merge into existing knowledge entries where they fit; the two Centric efforts → `07-projects/02-centricPLM/context/`.
Artifacts (new):
  - `08-knowledge/design/figma-ds-surface-authoring.md` — DS Figma surface authoring conventions (surface/overlay rules + build-from-real-components + transliteration + clip-content).
  - `08-knowledge/engineering/figma-cli-authoring.md` — figma-cli Yolo/CDP connect / branch-target / author.
  - `06-context/memory/decision-externalize-everything-to-workspace.md` + `decision-component-pattern-framework-system.md`.
  - `07-projects/02-centricPLM/context/{cell-indicators-pilot,toolbar-context-architecture}.md` (project-local, gitignored).
Artifacts (extended):
  - knowledge: `radix-derived-color-system` (§6 role→step→use-class), `figma-plugin-patterns` (§15–17 MS-icon/section-coords/headless-MCP); frameworks #05 (§3a full-result high-res review + recursive-before-presenting QA) + #02 (control placement by scope of effect); `04-preferences` (side-chat handback); `AGENTS.md`/`CLAUDE.md`/`llms.txt`/`workspace-ontology.md` (externalize rule); knowledge `_INDEX.md` + memory `MEMORY.md` indices.
Migration:
  - 19 local memories relocated (17 + 2 a concurrent session added mid-task); "Drive is dead" memory retired (already covered by `decision-portable-workspace-refactor` + `fact-workspace-repos`). Local `.claude` memory reduced to one pointer (`externalize-to-workspace.md`). Link validator green (246 skills, 0 warnings).
Next:
  - A concurrent session was active in the same memory dir — if it writes more local memories, re-run the externalize routing for those.
  - `00-bootstrap/setup/README.md` had an orphaned (non-this-session) change left uncommitted for Sean to reconcile; the 2026-06-22 figma-repo-sync-plugin block below was previously uncommitted and is included here to preserve it.
--- END BLOCK ---
--- SESSION BLOCK ---
Date: 2026-06-22
Agent: Claude Opus 4.8
Surface: Claude Code (Mac desktop app)
Machine: Work MacBook Pro (main) (CS-K746DRWXY1)
Project(s):
  - Centric VMS Design System — centric-ui Figma library ("Centric SaaS PLM — Design System", fileKey o6o1ZuGHxDow2vHLuYXT6X). Multi-area tweaks across Components + Base UI Additions (+ Features/Layout/Cover). All work is in Figma, not workspace files.
Artifacts (Figma):
  - Typography: new Body + UI style categories + paragraph-spacing; `Foundations / Semantics / Typography Roles` collection (96 role tokens); 21 variable-bound text styles (every property incl. numeric fontWeight + paragraphSpacing → role → semantic → primitive); remapped ~1,117 text nodes file-wide (Material Symbols glyphs correctly excluded).
  - Token binding: comprehensive — every real spacing/gap/radius/border value across ALL pages + instances (incl. the new slots + demo content); added border-width-3, line-height (xtight/xloose/2xloose), paragraph-spacing tokens. Colors/stroke-weights already ~100% bound (per-side strokeWeight verified).
  - Canon (8): Card footer slot→hug; Collapsible trigger→fill; Scroll Area viewport→SLOT; Badge mode-first (Size/Shape→modes, states physical); Avatar/Badge status→modes (8→2 variants); Sidebar Menu Button +Focus; Tabs TabsList→slot + Trigger states (10 variants); Form Field label/message boolean visibility toggles + 14 feature/layout instance rewires.
  - Additions: 8 slot refactors (Menubar/NavMenu/ToggleGroup/Radio/Breadcrumb/Accordion/Carousel/Drawer-existing); Drawer-Top padding; Date Picker (popover Left&Right + nested-Calendar stroke hidden + slot padding); Combobox (Left&Right + items FILL); Calendar Day Position mode (range rounding); NavMenu Trigger +Focus / Link +Focused; Slider thumb fill fix + _Slider/Thumb subcomponent (10 variants) NOW CONSUMED by the Slider; _Avatar/Badge icon→INSTANCE_SWAP (per-status glyphs + preferred values).
  - Fixes: Avatar—Sizes duplicate-mode bug (now md/sm/lg, correct values, 0 instances affected); canvas overlap cleanup.
  - [Claude memory, ~/.claude] ds-figma-surface-conventions.md Rule 14 + MEMORY.md index — FLOATING elements absolute @ logical spot + constraints, host sized to its logical element, clipsContent off → never inflate host bbox (even boolean-toggled; surfaced by the slider-thumb value tooltip).
Decisions:
  - Mode-first variant architecture confirmed (color/size/status → modes; presence → booleans; structure → physical variants).
  - Two text categories: UI (non-wrapping control text, Regular+Medium) vs Body (wrapping, Regular+Strong, paragraph-spacing). Default body = 14.
  - Floating elements ALWAYS absolutely positioned with constraints (durable rule saved to memory).
  - Off-scale one-offs left as documented exceptions: radius-10 (Avatar shape), spacing-3 (Features), Cover gaps 89/104, Avatar "AB" 21px, stat "350" 44px, pre-existing _Calendar/Day↔Calendar 8px overlap.
Pending added:
  - PUBLISH the centric-ui library — Sean's manual Figma action (Assets panel → Publish; the Plugin API can't publish). Consuming files then pick up the new text styles, Typography Roles + mode collections, border-width-3/paragraph-spacing tokens, and _Slider/Thumb.
  - Optional polish: relocate _Slider/Thumb into the Slider section; resolve the pre-existing _Calendar/Day↔Calendar 8px overlap (needs a category relayout).
Next:
  - Sean publishes the library.
--- END BLOCK ---

--- SESSION BLOCK ---
Date: 2026-06-22
Agent: Claude Opus 4.8
Surface: Claude Code (Mac desktop app)
Machine: Work MacBook Pro (main) (CS-K746DRWXY1)
Project(s):
  - 09-figma-repo-sync-plugin — engine pass executed regen-in-the-loop (B2 tokenization + B1 Type→booleans).
Decisions:
  - Regen-in-the-loop (Option A): implement a slice → Sean regens in Figma + confirms → next slice. Used throughout B2 + B1.
  - 7 B1 decisions locked (icon-only fold-into-master, prop names, fixed padding, badge gating, cornerRadius-9999 auto, avatar -8 sanctioned, spec grid omit).
  - S6 (square icon render) DEFERRED — Figma can't bind width per-mode-conditionally (square icon cells force FIXED width → clip text); follow-up = separate icon-button or padding-tune.
Artifacts (PRs on cpes-software/centric-ui, stacked, no self-merge):
  - PR #122 B2 tokenization (transparent token bind + zero→space-0 + recursive geometry-binding pass `bindGeometryRecursively`). Verified. Build 11.4.23.
  - PR #124 B1 Type→booleans — Button + Badge now State-only ComponentSets with boolean icon-presence props; iconNode + 4-clones deleted; State expansion kept. Net −287 lines. Verified (both regens). Build 11.4.29.
  - engine-pass-plan.md (NEW) — code-grounded 3-track plan.
Key findings/fixes:
  - B2 first cut was patchy (only applyFrameStyling bound; 131 literal sites) → fixed with a recursive post-assembly geometry pass (binds equal-valued tokens → render-safe).
  - B1 boolean-prop regression: slim block deleted the "Leading content"/"Trailing content" props the hasIconAxis block creates → fixed (removed the carried-over Type-era deletes).
  - False DIRTY-START on State-only sets (legitimate State=Default base miscounted) → fixed.
  - The 7,952 "get undefined" log lines are Figma-internal LoAF perf instrumentation, not plugin errors.
Pending added:
  - C lint gate (last engine-pass track); S6 square-icon follow-up.
Next:
  - C lint gate (passive scanner → blocking + convention validators). Then S6 follow-up + the deferred items.
--- END BLOCK ---

--- SESSION BLOCK ---
Date: 2026-06-22
Agent: Claude Opus 4.8
Surface: Claude Code (Mac desktop app)
Machine: Work MacBook Pro (main) (CS-K746DRWXY1)
Project(s):
  - 09-figma-repo-sync-plugin — branch-staleness investigation → PIVOT to `main` as the base.
Decisions:
  - Investigated catching `feat/radix-color-system` up to `main`. Dry-run merge = 22 conflicts (plugin engine auto-merged clean), but discovered the team ALREADY re-landed the radix work onto `main` via merged consolidate PRs (#82 design-tokens, #83 generator-scripts, #84 figma-plugin). `main` is fresh: plugin @ 11.4.18 + radix --sem- tokens + tsconfig/eslint plugin-excludes.
  - Therefore `feat/radix-color-system` is a SUPERSEDED 8-week-stale mega-branch. ABANDONED the catch-up merge (threw away the worktree); work moves to `main`.
Artifacts:
  - Closed PR #120 (tsconfig exclude) — redundant; main already has it (+eslint ignore). Deleted its branch.
  - Rebased the 4 foundational PRs onto `main` + re-targeted bases: #116 transparent (→main), #117 shared-plugin-data (→#116 stacked), #118 Badge size/shape (→main), #119 Alert (→main). All force-pushed. Plugin files were byte-identical main↔branch (clean rebase); Badge layered onto main's cds-token badge (token-agnostic); badge/alert eslint+prettier clean.
  - Removed throwaway worktree + dead `merge/radix-catchup-main` branch.
Key findings:
  - main reintroduced ~150 cds- refs in new code the branch's codemod never saw → cds→semantic usage migration is INCOMPLETE on main (separate follow-up codemod).
  - `caution` is still an OPEN team PR (#87 → main); main lacks --sem-caution + Badge caution until it merges (soft dep for Alert/Badge caution).
Pending resolved:
  - "Catch up with main" — resolved by pivoting (main is already current; no painful merge needed).
Project status changes:
  - 09-figma-repo-sync-plugin base: `feat/radix-color-system` (dead) → `main` (fresh). 4 PRs rebased; #120 closed.
Next:
  - Quick wins on main (ScrollArea placed=0; mode-first header comment). Then Type→booleans lever + tokenization sweep + lint gate as one componentGenerator.ts pass. Watch #87 (caution) for the Alert/Badge caution dependency.
--- END BLOCK ---

--- SESSION BLOCK ---
Date: 2026-06-22
Agent: Claude Opus 4.8
Surface: Claude Code (Mac desktop app)
Machine: Work MacBook Pro (main) (CS-K746DRWXY1)
Project(s):
  - 09-figma-repo-sync-plugin — foundational fixes EXECUTED + opened as PRs (centric-ui repo).
Decisions (locked w/ Sean):
  - migration=hard-break+re-export · namespace=figmaReposync · Base-UI scope=Alert full + 22 phased · Badge data-chip=4px (rounded-sm, tokenized) · DESIGN.md=fresh + section in AGENTS.md · diagnostics flip=after ScrollArea+idempotency.
Artifacts (4 PRs on cpes-software/centric-ui, base feat/radix-color-system; NO self-merge):
  - PR #116 feat/figma-transparent-token — Figma-supplied `transparent` base primitive (sync-palette inject + genRGBA alpha fix). Build 11.4.19.
  - PR #117 feat/figma-shared-plugin-data (stacked on #116) — foundation identity → shared `figmaReposync` (6 sites, shared-first read); align+commit 2 MCP seed scripts (dsb→figmaReposync, leaf→token-name, RUN_ID→SEED_RUN_ID env); seed:export/seed:build; scripts/README. Build 11.4.20.
  - PR #118 feat/ui-badge-data-chip — Badge size(sm)+shape(rounded) axes (additive).
  - PR #119 feat/ui-alert-component — alert.tsx (Base-UI div+cva, soft-tint incl. caution).
Key correction (verified in code):
  - Mode-first lever is NARROW: Button/Badge intent/size already MODES, State correctly PHYSICAL; ONLY Type (icon presence) is wrongly physical → B1 = Type→booleans (keep State physical). Reconciler's "rip out physical variants" was an over-reach.
  - Forward-compat design: foundational fixes deliberately avoid componentGenerator.ts so the later Type→booleans + tokenization sweep + lint gate land in ONE engine pass.
Verification:
  - Plugin PRs (#116/#117): plugin `npm run check` + 468/468 tests + build. App PRs (#118/#119): eslint + prettier clean, file-level type-clean.
Pending added:
  - App `tsconfig.json` has no `exclude` → `tsc` swallows the plugin's .ts (~977 figma/Variable errors). Spawned a background task to add `exclude: ["figma-repo-sync-plugin"]`.
Next:
  - Quick wins (ScrollArea placed=0 fix; correct the mode-first header comment). Then plan/execute the Type→booleans lever (B1) + tokenization sweep (B2) + lint gate (C) as one engine pass. The big feat/radix-color-system→main PR is Sean's call.
--- END BLOCK ---

--- SESSION BLOCK ---
Date: 2026-06-22
Agent: Claude Opus 4.8
Surface: Claude Code (Mac desktop app)
Machine: Work MacBook Pro (main) (CS-K746DRWXY1)
Project(s):
  - 09-figma-repo-sync-plugin — finalization planning (code-grounded).
Artifacts:
  - 07-projects/09-figma-repo-sync-plugin/next-steps-plan.md — NEW. Grounded next-steps plan + status table for closing the gap between the hand-built gold Figma library and what the plugin generates. Produced by a 6-reader code audit + reconciler against the ACTUAL code (Build 11.4.18), not the stale docs (11.4.10 era).
  - 07-projects/09-figma-repo-sync-plugin/SESSION-STATE.md — rewritten atomically to the current baseline (was 2026-06-03 / 11.4.x split-brain saga).
Decisions:
  - Plan finalization off code ground-truth, not docs: a workflow fanned 6 Explore readers across foundations.ts / componentGenerator.ts / componentVariables.ts / centric-ui ui/ / Code Connect / SESSION-STATE, then a reconciler sequenced the work.
  - Execution order set with Sean: (1) update project state → (2) lock 6 gating decisions → (3) bottom-up foundational/scaffold fixes (forward-compatible & unobtrusive to the later generation rework) → (4) quick wins → (5) plan the Button/Badge mode-first lever.
Key findings (corrections to the docs):
  - Convergence is HALF-BUILT but DIVERGENT: 2 untracked MCP-seed scripts use a 'dsb' shared-data namespace; foundations.ts uses private keys; target 'figmaReposync' exists in neither.
  - Button + Badge are the LEAST mode-first components (still physical variants via combineAsVariants + expandSetWithStateAxis), despite the generator header claiming mode-first. This is the biggest lever.
  - Total tokenization ~70–80% (raw literals remain; 'transparent' token missing). Lint gate is passive (never blocks); zero runtime convention validators.
  - Codebase: Button+caution done; Badge needs size/shape; alert.tsx absent; all 23 Base-UI additions missing. Code Connect: zero infra. centric-ui/AGENTS.md is generic, not a DS binding; no DESIGN.md.
Pending resolved:
  - SESSION-STATE branch-404 blocker confirmed RESOLVED (now feat/radix-color-system, pushed, 0 ahead).
Pending added:
  - 6 gating decisions to lock (migration policy / namespace / Base-UI scope / Badge radius / DESIGN.md provenance / diagnostics-flip timing).
Project status changes:
  - 09-figma-repo-sync-plugin: stale-doc baseline → code-grounded plan; SESSION-STATE current as of Build 11.4.18.
Next:
  - Lock the 6 decisions, then start the bottom-up foundational fixes (convergence/scaffold), planned to keep the later generation-pathway rework unobtrusive.
--- END BLOCK ---

---

--- SESSION BLOCK ---
Date: 2026-06-18
Machine: Work MacBook Pro (main) (CS-K746DRWXY1)
Surface: Claude Code (Mac desktop app)
Project(s):
  - Component & Pattern Framework system (workspace contribution + Centric C8 PLM example).
Artifacts:
  - 01-frameworks/09-component-and-pattern-framework.md — NEW top-level framework (#09): universal 18-facet component schema, 9-category taxonomy, decision trees, compose-together model, cross-cutting laws (with citable rationale), naming divergence, lineages, AI-legible layer (§11) + A2UI (§11a), DESIGN.md protocol + gap-detection/self-prompting (§12a), playbooks, operating model, resource canon.
  - 03-skills/ux-component-library/ — evolved skill (SKILL.md → spec_version 2.1, framework pointer, delivery-system map, new working modes) + 3 references: component-authoring.md (components/props/states/examples as data), tokens-and-naming.md (taxonomy grammar + purposeful naming), ai-ready-design-systems.md (AI-ready checklist · DESIGN.md authoring · A2UI).
  - 02-shared-references/ds-agents-binding.md — reusable AGENTS.md binding (routing + always-on rules + trust levels).
  - 02-shared-references/a2ui/ — canonical-catalog.json (29-component A2UI catalog projecting the taxonomy; JSON valid, union resolves) + README.md (full 62→A2UI mapping: ~17 basic / ~16 added / ~17 composed / ~12 gaps; DESIGN.md→CSS-var theming seam).
  - 00-README.md + _FRAMEWORKS.md — indexed framework #09; brought the stale MOC current (7→9). skills.registry.json regenerated.
  - [outside workspace, local only] c8-plm/DESIGN.md — real C8 visual-identity from CDS tokens (lints 0 errors); c8-plm/AGENTS.md — tailored C8 binding.
Decisions:
  - Five-layer DS context system (framework hub + skill + ux-components MCP + DESIGN.md + AGENTS.md), organized by Wolosin's intent model. DESIGN.md stays LEAN (visual identity only); component depth on demand via MCP — the configuration Atlassian's field test found beats a monolithic DESIGN.md.
  - Evolve ux-component-library rather than add a new skill; C8 PLM as the worked DESIGN.md example from real tokens; A2UI = complementary runtime layer (payload on A2A/MCP) this system supplies the Catalog + intent + tokens to.
Pending resolved:
  - Advances "Add framework-layer pointers to key skills" (ux-component-library now references framework #09).
Next:
  - Restart Claude Code (or reinstall snds@snds-local) to load ux-component-library v2.1 with the new references live in the plugin cache.
  - Optional: validate the A2UI catalog with A2UI's conformance tooling; build a CDS renderer mapping catalog variants → --sem-* tokens; A/B-evaluate a C8 screen.
--- END BLOCK ---

--- SESSION BLOCK ---
Date: 2026-06-17
Machine: Work MacBook Pro (main) (CS-K746DRWXY1)
Surface: Claude Code (Mac desktop app)
Project(s):
  - Workspace infrastructure — Google Drive decommission cleanup (not a 07-projects project).
Artifacts:
  - Scrubbed stale Google Drive references from active docs (workspace-infrastructure.md migration banner + git-sync rewrite; project-context, 00-obsidian & 18-bootstrap SESSION-STATEs, visual-qa README, skills-vs-slash, .gitignore). Affirmations, historical record, and _archive left intact.
  - Repo rename legacy `claude-workspace-system` → canonical `snds/workspace` in active setup scripts (bootstrap.sh/.ps1, setup.py), 00-obsidian README/SESSION-STATE, project-context, 18-bootstrap SESSION-STATE. (Live remote was already snds/workspace.)
  - Removed Desktop Commander refs → filesystem MCP / native: _session-state-template, contract docs (CLAUDE.md, llms.txt, BOOTSTRAP.md, 09-tools README + build-registry.py, workspace-bootstrap SKILL.md, last-mile-craft), 6 project SESSION-STATE tooling lines.
  - dispatcher.py: legacy gitdir-store default name → workspace. .claude/settings.local.json (machine-local): stripped 29 stale legacy-gitdir/Drive permission grants. Removed stale snds-local 0.1.0 plugin cache (Drive-triggering workspace-bootstrap remnant; 0.2.0 install is clean).
Decisions:
  - Google Drive fully decommissioned as the workspace; the git checkout is the source of truth, git is the sync layer, Obsidian reads the vault. Agent memory updated (workspace-no-longer-on-gdrive). Kept historical / archive / struck-through mentions as the migration paper trail.
Next:
  - If `anthropic-skills:*` skills still surface in a future session, restart Claude Code (regenerate via 08-tools/build-local-skill-plugin.py + reinstall if needed) — phantom from the removed cache.

---

--- SESSION BLOCK ---
Date: 2026-06-16
Machine: Work MacBook Pro (main) (CS-K746DRWXY1)
Surface: Claude Code (Mac desktop app)
Project(s):
  - Obsidian vault setup (workspace tooling — not a 07-projects project).
Artifacts:
  - .obsidian/plugins/* — installed 11 community plugins: Tasks, Calendar (stable 1.5.10), QuickAdd, Linter, Image Converter, Homepage, PDF++, Banners, Charts, Tag Wrangler, Outliner. (machine-local; .obsidian is gitignored)
  - .obsidian/daily-notes.json — core Daily Notes pointed at 05-artifacts/active/daily, format YYYY-MM-DD (so Calendar targets the real daily folder).
  - .obsidian/plugins/homepage/data.json — open _HOME on startup + refresh Dataview.
  - .obsidian/plugins/obsidian-tasks-plugin/data.json — global filter #task (+ removeGlobalFilter), default query sort by due.
  - .obsidian/plugins/quickadd/data.json — added "📥 Quick Capture → Today" capture command (appends "- HH:mm {text}" to today's daily note).
  - .obsidian/plugins/obsidian-linter/data.json — format-on-save, idempotent whitespace rules only; ignores 00-bootstrap/templates, 05-artifacts/archive, .obsidian.
  - _HOME.md — added "## 📋 Open tasks" Tasks widget (already auto-committed by obsidian-git: 8e0a901).
Decisions:
  - Tasks global filter = #task so existing plain `- [ ]` checklists aren't all swept into Tasks queries; only #task items are managed. Reversible in Settings → Tasks.
  - Linter restricted to whitespace rules (no YAML/heading/content rules) to avoid noisy diffs on the git-tracked vault.
  - Installed Calendar stable 1.5.10 (repo "latest" is a calendar-beta BRAT build that won't load under the `calendar` id).
  - Did NOT auto-configure Image Converter (no data.json yet; complex/version-specific schema → corruption risk). Left at defaults; manual toggle documented.
  - .obsidian is gitignored → this plugin set + configs are LOCAL to CS-K746DRWXY1. Other machines won't get them via git; re-install there to match.
Pending added:
  - Optional: Settings → Image Converter → enable auto-convert pasted images to WebP (~85% quality) to keep the git vault lean.
  - Verify QuickAdd "📥 Quick Capture → Today" on first run; assign a hotkey if desired.
Next:
  - In-app sanity check: Homepage opens _HOME, Calendar opens daily notes in 05-artifacts/active/daily, Quick Capture lands in today's note.
--- END BLOCK ---

--- SESSION BLOCK ---
Date: 2026-06-16
Machine: Work MacBook Pro (main) (CS-K746DRWXY1)
Surface: Claude Code (Mac desktop app)
Project(s):
  - Portable workspace — post-consolidation follow-ups (skill library, tooling, capability layer). Continuation of the same-day refactor session below.
Artifacts:
  Plugin refresh:
    - 09-tools/build-local-skill-plugin.py → v0.2.0 + de-Drive docstring; rebuilt the snds-local `/snds:*` plugin from the portable checkout (18 hubs, content decoupled from Drive/DC). Runtime cache refresh is a per-machine CLI step.
  New `vision` domain (computer vision / spatial-ML) — authored natively, NOT copied from the third-party CV skills in ~/.claude:
    - 03-skills/vision-foundations (foundation: image-as-signal, CV task taxonomy, conv/attention, training/eval/deploy, ethics, + a "Seeing the work" section).
    - Spokes: vis-classical-opencv, vis-detection-tracking, vis-segmentation, vis-vlm-multimodal, vis-video-pipelines. Wired to science (math) + data (ML/eval) foundations.
  Capability-detection contract (full, portable):
    - frontmatter `requires: [<cap-id>]` (spec v2.1; carried into the registry by build-registry) + 02-shared-references/capability-registry.md (canonical JSON: kind/detect/install/fallback) + preflight protocol in AGENTS.md + 01-frameworks/08 + 09-tools/validate-capabilities.py + .github/workflows/capability-validator.yml.
  Tool skills brought in behind the contract (dependency-declared, not vendor forks):
    - figma-canvas-designer → requires figma-mcp; web-automation (new) → agent-browser; reference-video-review (new, spoke of visual-qa-toolkit) → ffmpeg+yt-dlp; ai-video-generation (new) → inference-belt.
  Vision↔assessment cross-links:
    - 12 reciprocal peer pairs connecting vision to visual-QA / game / imaging so CV is the agent's "seeing" instrument; visual-qa-toolkit gained a "pairs with the vision domain" note.
  Figma Dev Mode workflows (capability-bound spokes, not vendor forks) — the distinct external skills the canvas-design binding didn't cover:
    - figma-design-to-code, figma-code-connect, figma-design-specs, figma-diagramming — all under the figma hub, each requires figma-mcp, defer mechanical specifics to the installed skill + MCP.
  Capability consistency sweep (workspace-wide audit for skills that DRIVE an MCP/CLI but didn't declare it):
    - +requires figma-mcp on figma-mcp-tool-usage, figma-source-audit (primary path = use_figma).
    - Registered new `blender-mcp` capability (degrade→procedural); +requires on vfx-volumetrics (optional baked-asset path).
    - Codified the rule in skill-frontmatter.md: declare `requires` only where a skill *drives* the tool — not lenses/hubs (design-engineer, figma hub, /qa), Plugin-API skills (figma-component-generation, figma-variable-creation), or methodology that merely mentions a tool (vis-video-pipelines/ffmpeg; 3d-* / imaging citing Blender Cycles).
Decisions:
  - Don't copy third-party tool skills into the workspace (upstream-maintained → license/zombie risk; tool-bound stubs are useless without the tool). Instead: declare the dependency + detect/degrade. CV authored natively (better integrated) rather than imported.
  - Capability detection is surface-agnostic: MCP detected by tool-name pattern in the agent's own surface; CLI by `command -v`. Absent dependency → degrade/block/route, never silent-fail.
  - Vision's primary purpose here = SEE/critique our visual work (VLM screenshot critique, SSIM/diff regression, segment/detect to verify, Legion render + fly-through assessment) — "measure or describe what you see, don't assert it."
  - `requires` = "drives the tool when run," not "mentions it." Optionality is expressed via the capability's `fallback: degrade`, not by omitting the declaration.
Pending resolved:
  - Consolidated the 16-PR refactor stack onto `main` by fast-forward; closed #2–#16 as merged-by-ff (#1 auto-merged) and deleted all 16 refactor/* branches (no zombie PRs/branches).
  - "Do all slash skills trigger only from the new workspace?" — yes; rebuilt the stale `/snds:*` plugin so it serves new-workspace content.
  - "Any internal non-Anthropic skills worth merging?" — no copies; built the detection mechanism + brought in 4 as dependency-declared skills.
  - "External skills inventory" deferred item — CLOSED: redundant for what we rebuilt (install commands already in capability-registry); the one real gap (Figma Dev Mode workflows) was brought in instead.
  - Capability-consistency follow-up — DONE: full-workspace audit, wired the genuine tool-driving skills, codified the drives-not-mentions rule.
Project status changes:
  - Workspace skills: 233 → 246 (vision domain + 3 tool skills + 4 Figma Dev Mode spokes + figma bindings). Capabilities 5 → 6 (added blender-mcp); 12 skill requirements wired. Gate suite 5 → 6 (validate-capabilities). All green.
Next:
  - Per-machine: `claude plugin marketplace update snds-local && claude plugin install snds@snds-local` (then restart) to pick up plugin v0.2.0.
  - Optional (deferred, not selected): promoting vision↔QA peers to hard/governed_by edges if auto-load during QA/render work is wanted.
--- END BLOCK ---

---

--- SESSION BLOCK ---
Date: 2026-06-16
Machine: Work MacBook Pro (main) (CS-K746DRWXY1)
Surface: Claude Code (Mac desktop app)
Project(s):
  - Workspace refactor → portable, surface/device/LLM-agnostic, foundation-driven agent workspace. Canonical copy at github.com/snds/workspace (Drive original `claude-workspace-system` untouched).
Artifacts: (the full 16-PR stack — all now consolidated onto `main` by fast-forward)
  Standards + portable contract:
    - AGENTS.md — universal contract: portable-first rules, bootstrap-on-checkout, skill-loading precedence algorithm, multi-agent continuity/handoff, write-quality gates, adapter model. Thin adapters CLAUDE.md / CURSOR.md / PERPLEXITY.md + llms.txt + 02-shared-references/workspace-ontology.md routing map.
    - Frontmatter v2 (tier/domain/hub/prerequisites/related/governs/surfaces) as single source of truth → generated 03-skills/skills.registry.json (233 skills) + reciprocal `## Related` blocks.
    - 09-tools/{build-registry,build-related,validate-links,validate-workspace,validate-integrity}.py — five stdlib-only gates, CI-enforced.
  Governance + memory + archive:
    - 01-frameworks/08-workspace-contribution-framework.md — how/when/where/what/why to edit every layer + routing map + memory/archive protocols + portable session protocol + write-quality gates.
    - 06-context/memory/ — portable non-project memory layer (MEMORY.md index, _template, decision + fact records).
    - _archive/ARCHIVE-LOG.md — provenance ledger (why/when archived + canonical replacement; no zombies).
  Foundations-first architecture (foundations load before specialty skills) across design, engineering, product, data, game, imaging, science:
    - imaging-foundations/ + img-{optics-light,photography,photoreal-rendering,cinematography,vfx}.
    - science-foundations/ + sci-{linear-algebra,numerical-methods,physics-simulation,probability-stochastic}.
    - Expansion: mobile (react-native/ios-swiftui/android-kotlin/platform-craft); security (lead-security-architect + sec-{threat-modeling,authn-authz,appsec-owasp,supply-chain}); be-relational-db Postgres enhancement; 08-knowledge/cross-domain/skill-ecosystem-and-mcp-servers.md.
    - Galaxy/Legion: sci-astro-objects, sci-astro-structures, vfx-particle-systems, vfx-volumetrics, game-scale-traversal + 08-knowledge/game-dev/legion-galaxy-playbook.md (prescriptive recipe, complementary to the existing threejs-galaxy-visualization gotchas doc).
  - Clean contiguous folder renumber 00–09; multi-agent continuity (one unified contract, boundary + dynamic Cursor handoff); token + Obsidian polish; all 61 unspecified-tier skills resolved → 0.
Decisions:
  - Fresh isolated git repo at github.com/snds/workspace; this copy is the new canonical portable workspace. See memory decision-portable-workspace-refactor.
  - Foundations for ALL major domains; delivered as a sequenced foundation-first PR stack (#1–#16).
  - Open writes (any capable agent may write) but behind HARD gates: file quality, intent integrity, cross-link continuity, no zombies (archive-or-regenerate). Enforced by the five validators.
  - Decoupled from Google Drive / Desktop Commander / Claude-only paths — git checkout is the source of truth; the bootstrap-generator effort kept separate (learnings used, not a dependency).
  - Consolidated the entire 16-PR stack onto `main` by fast-forward (linear history preserved); closed #2–#16 as merged-by-fast-forward (#1 auto-merged) and deleted all 16 refactor/* branches (commits preserved on `main`) — no zombie PRs/branches.
Pending resolved:
  - All 7 original refactor asks (restructure, foundations, surface/LLM-agnostic + de-Google, token reduction, interconnections, Obsidian, GitHub) + follow-ups (governance, portable memory, archive-with-provenance, multi-agent continuity incl. Cursor dynamic switching, open-writes-with-gates, folder renumber, skill-library expansion).
Project status changes:
  - Workspace: Drive/Desktop-Commander/Claude-coupled → portable, git-native, LLM/surface/device-agnostic; consolidated on `main`, all five gates green (233 skills · 540 md files · 0 warnings).
Next:
  - Operate from `main` going forward; future contributions follow 01-frameworks/08 + AGENTS.md write-quality gates.
  - (Optional) per-machine: install/propagate the local skill plugin; clone github.com/snds/workspace on other devices to validate cross-surface continuity.
--- END BLOCK ---

---

--- SESSION BLOCK ---
Date: 2026-06-04
Machine: Personal MacBook Pro (Voyager-2.local) + Work MacBook Pro (main, going forward) (CS-K746DRWXY1)
Surface: Claude Code (Mac desktop app) + Desktop Commander (Personal MBP) · Claude Code (Mac desktop app) (Work MBP)
Project(s):
  - Workspace infrastructure — operation-grammar hub system (continuation of 2026-06-01)  [Personal MBP]
  - figma-repo-sync-plugin (09) — Radix palette → token-generation migration  [Work MBP]
Artifacts:
  Workspace operation-grammar hubs (Personal MBP):
    - 02-skills/{ds,figma,motion,type,redesign}/SKILL.md — the FIVE sibling hubs are now built (observed on disk this session), completing the six-hub set begun with /qa on 2026-06-01. All user-invocable, all carry the operation grammar + disambiguation contract:
        · /ds (141 lines) — design-system decisions/tokens/anatomy/governance; delegates ds-advisor + design-engineer.
        · /figma (124) — Figma authoring & code-connect; delegates figma-* + figma-canvas-designer + figma-plugin-dev; uses Figma MCP.
        · /motion (105) — motion IMPLEMENTATION (library code); wraps the skillstack libraries; principles stay in motion-* skills.
        · /type (99) — typography systems & type design; delegates type-* + lead-type-designer + gd-typography.
        · /redesign (122) — surface-scale generative redesign; wraps stardust pipeline + impeccable live loop.
    - 04-artifacts/active/trigger-cheatsheet_v1.0_2026-06-01.html — present; "planned" hub statuses are now stale (5 of 6 shipped) → flagged for refresh.
  figma-repo-sync-plugin Radix migration (Work MBP, all in ~/projects/cpes-software/centric-ui — NOT Drive; committed there, NOT pushed):
    - figma-repo-sync-plugin commit 2f88837 (Build 11.4.10) — generator-driven Radix 3-tier token model. 11 modified + 4 new files; 460 tests pass.
    - New plugin files: scripts/sync-palette.mjs (build-time generator), src/palette.generated.ts (checked-in generated), src/variableInventory.ts, src/__tests__/palette.generated.spec.ts.
    - app/app.css: new `caution` (yellow) semantic context + soft pair + @theme classes (committed in 7d9dc15).
    - Spawned-task commits: 5ed5274 (caution Badge/Button CVA variants), 7d9dc15 (cds-* → semantic usage codemod).
Decisions:
  Workspace operation-grammar hubs:
    - Six-hub set complete; the /qa POC pattern (2026-06-01) cloned cleanly to all five siblings. Disambiguation boundaries hold across hubs: /qa JUDGES · /ds DECIDES · design-engineer/ /figma AUTHOR · /motion IMPLEMENTS · /redesign CREATES.
    - design-system-ops plugin observed active (38 invocable commands: token-audit, drift-detection, component-audit, deprecation-process, governance-encoder, visual-report, etc.). Heavy SEMANTIC overlap with /ds + ds-advisor + design-engineer — a new precision zone to fold into the description-contract pass (was 8–10 zones; now ~9–11).
  figma-repo-sync-plugin Radix migration:
    - Propagation = full 3-tier mirror via a build-time generator: sync-palette.mjs parses centric-ui's palette.generated.css + app.css → checked-in palette.generated.ts; foundations.ts (Figma seeding) + styleStub TOKEN_PALETTE consume it. Re-run `npm run sync:palette` on palette changes.
    - Taxonomy: Foundations/Primitives (single mode, theme name-encoded) + Foundations/Semantics/<axis>. Migration = recreate + auto-rebind (retire legacy by name, resolve split-brain Colors, sweepUnseeded for foreign/stale vars). shade→step binding so raw shades bind to their Radix step.
    - Tailwind shades + Radix per-hue alpha NOT materialized in Figma (kept in CSS/TOKEN_PALETTE; transparency uses Tailwind /opacity, which composites Radix values). Keep all 24 hue families (decorative + future data-viz/theme-gen — CDS PLM has multiple visual themes) + black/white overlays.
    - Verified at compiled-CSS level that Radix supersedes Tailwind: palette's unlayered :root overrides Tailwind's @layer theme defaults, so bg-blue-500 renders Radix. Figma Variable.consumers reports 0 even for bound vars → trust alias-ref signal, not node-bound.
    - New `caution` context = yellow (vs warning=orange); on-fill text DARK in both modes (yellow-9 is a light solid; .dark override pins yellow-1).
    - Decorative/categorical colors = palette-direct (reference Radix families); no new semantic context.
Pending added:
  - [Workspace] Refresh trigger-cheatsheet to v1.1: flip /ds /figma /motion /type /redesign from "planned" → "live"; keep /redesign's external-bridge tag.
  - [Workspace] Add design-system-ops to the semantic-overlap reconciliation (vs /ds, ds-advisor, design-engineer); decide canonical owner per concern (its 38 commands are granular ops; /ds is the hub — likely /ds routes TO design-system-ops commands).
  - [Workspace] Update artifact-registry + (optionally) workspace CLAUDE.md / dispatcher to document the now-complete six-hub surface.
  - [figma-repo-sync-plugin] Push feat/radix-color-system + open/refresh the PR (plugin 2f88837 + caution 5ed5274 + cds-codemod 7d9dc15). Company repo — team review, no self-merge.
  - [figma-repo-sync-plugin] REVOKE the Figma PAT pasted during this session (Settings → Personal access tokens).
Pending resolved:
  - [Workspace] Build the 5 sibling hubs from the /qa pattern — DONE (all present on disk, invocable).
  - [figma-repo-sync-plugin] Mirror the Radix token architecture in figma-repo-sync-plugin foundations.ts (Primitives/Semantics tiers + Tailwind-compat + overlays). DONE — Build 11.4.10, committed 2f88837; verified clean on a real main-branch regen (0 PIN-FAILURE, foreign/legacy cruft self-healed).
Project status changes:
  - figma-repo-sync-plugin: Radix palette → token-generation migration LANDED + verified clean; plugin committed locally (2f88837), unpushed.
Next:
  - [Workspace] Still-open original thread: test-drive the hub set against the Davinci Storybook QA audit (/qa audit apps/docs --theme light --theme dark → /qa triage) — validates the hubs on real work and closes the founding ask.
  - [figma-repo-sync-plugin] Push + PR review of feat/radix-color-system; after merge, regen the Figma library; revisit a named data-viz/`category` token set if/when a stable taxonomy emerges.
Reconciled from: Personal MacBook Pro session (operation-grammar hubs) + Work MacBook Pro session (Radix migration) — both 2026-06-04. No conflicting decisions (different projects, zero overlap).
--- END BLOCK ---

---

--- SESSION BLOCK ---
Date: 2026-06-02
Machine: Work MacBook Pro (main, going forward) (CS-K746DRWXY1)
Surface: Claude Code (Mac desktop app)
Project(s): figma-repo-sync-plugin (09) + Centric VMS DS (centric-ui) — Radix color system
Artifacts: (all in ~/projects/cpes-software/centric-ui — NOT Drive)
  - app/stories/review/* — Palette Review Storybook harness (25 real shadcn components, before/after × light/dark, component filter, per-token flagging + MD/JSON export).
  - scripts/generate-color-palette/{radix-source,palette-generator,generate}.mjs — Radix-derived palette generator (ingests @radix-ui/colors; emits step primitives + Tailwind-shade aliases + alpha/overlays).
  - app/app.css + app/palette.generated.css — Radix-mapped semantic tokens + generated primitives.
  - figma-repo-sync-plugin commit 1651be6 (Bundles 11.3.82–85) — pushed.
  - 4 review PRs #64–67 (tokens/components/generator/harness) + local combined branch feat/radix-color-system.
Decisions:
  - Radix Colors = source of truth; Tailwind class names alias to nearest-OKLCh-L Radix steps (dev compat); APCA is GOVERNANCE (selection + audit), not primitive mutation — except the custom centric-blue scale (APCA solid floor).
  - centric-blue REPLACES Radix blue (emitted as --color-blue-*).
  - Brand-aware semantic hue assignment (ported from OMNI's 20°/30° collision rule): info→cyan, warning→orange, success→green, error→red — no semantic context reads as the brand.
  - accent stays neutral (shadcn hover); new --sem-selected = Radix step 5 (brand-tinted) for active/selected states.
  - Radix green-9 (#30a46c) carries white text — fixed the bright-green contrast the right way (reverted the black-text workaround).
  - 4 PRs base off the dev branch feat/figma-repo-sync-plugin (main is 170 commits behind with different component/token versions → off-main not viable). Merge order: tokens→components→harness; generator independent.
  - figma-repo-sync-plugin: EMIT_DIAGNOSTICS held ON through v1; binding scanner now splits PIN-FAILURE (real defect) vs theme-auto (expected); Button/Badge state-axis idempotency verified clean via a full regen.
  - Fixes surfaced by the harness (pre-existing, not palette regressions): added global `* { border-color }` default (Tailwind v4 currentColor); FormControl forwards aria-invalid Slot-style + Input/Textarea honor it.
  - gh CLI installed + authenticated (sean-sands-centric).
Pending added:
  - Review/merge the 4 Radix PRs #64–67 (order: tokens→components→harness; generator independent).
  - Mirror the Radix token architecture in figma-repo-sync-plugin foundations.ts (Primitives/Semantics tiers + Tailwind-compat + overlays).
  - Finalize the figma-repo-sync-plugin PR (mark ready + reviewers).
Pending resolved:
  - Verified Button/Badge state-axis idempotency + binding health (figma-repo-sync-plugin); built + verified the Palette Review harness; completed the Radix color-system re-architecture.
Project status changes:
  - Centric VMS DS (centric-ui): Radix-derived color system landed as 4 review PRs.
Next:
  - figma-repo-sync-plugin refinements against the new Radix tokens/components, working from the combined branch feat/radix-color-system.
--- END BLOCK ---

---

--- SESSION BLOCK ---
Date: 2026-06-02
Machine: Work MacBook Pro (main, going forward) (CS-K746DRWXY1)
Surface: Claude Code (Mac desktop app)
Project(s): Workspace infrastructure — skill discoverability / slash-command exposure
Artifacts:
  - 08-tools/build-local-skill-plugin.py — generator that mirrors curated 02-skills hubs into a local CC plugin (~/.claude/local-plugins/snds-local) so they surface as /snds:<name> commands.
Decisions:
  - Diagnosed: anthropic-skills:* namespace = the Cowork managed bundle (02-skills copied to the VM by cowork-skills-sync). Model-invocable but not local plugins, so absent from the interactive / menu.
  - Scope = curated hubs only (18 entry points), not all ~190 skills — spokes stay model-invoked to keep the menu clean.
  - Plugin lives OUTSIDE Drive (~/.claude/local-plugins) to dodge spaces-in-path + symlink-sync breakage; 02-skills stays the single source of truth, plugin is a rebuildable mirror.
  - Installed snds@snds-local (user scope, enabled); registered in ~/.claude/settings.json.
Pending added:
  - On other machines: run 08-tools/build-local-skill-plugin.py, then `claude plugin marketplace add ~/.claude/local-plugins/snds-local` + `claude plugin install snds@snds-local`, then restart (plugin lives in ~/.claude, not Drive-synced).
Next:
  - Restart Claude Code to surface /snds:* in the menu.
  - Optionally tune the HUBS list in the generator if more/fewer commands are wanted.
--- END BLOCK ---

---

--- SESSION BLOCK ---
Date: 2026-06-01
Machine: Personal MacBook Pro (Voyager-2.local)
Surface: Claude Code (Mac desktop app) + Desktop Commander
Project(s): Workspace infrastructure — skill ecosystem, trigger system, Drive sync resolution
Artifacts:
  - 04-artifacts/active/skill-ecosystem-stocktake_v0.3_2026-06-01.md — Phase 1 inventory of all non-workspace skills; v0.3 corrects the duplication premise (see Decisions).
  - 04-artifacts/active/invokable-operations-spec_v0.2_2026-06-01.md — Phase 2 two-plane trigger model + 12-verb spine + six-hub grammar; POC-built note.
  - 04-artifacts/active/trigger-cheatsheet_v1.0_2026-06-01.html — self-contained HTML trigger reference; 8 real-session worked combos, status-tagged hubs.
  - 02-skills/qa/SKILL.md — NEW /qa POC hub (user-invocable wrapper; verbs audit·critique·triage·inventory·spec). Synced to live mount; registered + invocable this session.
  - 02-skills/workspace-bootstrap/SKILL.md — added Stream-vs-Mirror Drive path resolution + per-machine sync-mode handling.
  - 00-bootstrap/setup/resolve-skills-symlink.sh + INSTALL-skills-resolver.md — NEW machine-local symlink resolver; wired as SessionStart hook in ~/.claude/settings.json.
  - Installed marketplaces: adobe-skills (stardust), impeccable.
Decisions:
  - Skill "dedupe" DISSOLVED: zero exact-name collisions between added marketplaces (impeccable/thedotmack/vibecad/claude-1337/skillstack/nuxt/adobe) and the 210 workspace skills. The 20 same-name overlaps are the DEFAULT Anthropic mount (anthropic-skills:*) — left entirely alone per Sean. Real remaining work = ~8–10 semantic-overlap zones, handled via description contract + hubs, not deletion.
  - Trigger model: keep organic triggering primary; add explicit /hub verb target --modifiers grammar as a precise second plane. Six hubs, one 12-verb orthogonal spine (impeccable verbs mapped as interop footnote, not canonical).
  - Hubs = wrappers (three-way contract applied to skills): thin workspace skill carries trigger vocab + routing; depth stays in base spokes/plugins. Build one at a time; /qa first.
  - Per-machine Drive sync is intentional: work Mac = Stream + offline; personal/Windows = Mirror. ~/.claude is machine-local, so each machine's skills symlink resolves independently via the new hook (first materialized root wins; [ -s ] gate rejects online-only placeholders).
  - impeccable browser-extension + live-bridge references preserved deliberately for future trigger integration / multi-spoke expansion (stocktake Finding 3).
  - arch-guild@claude-1337 fails to load (upstream bug: hooks/hooks.json present, no plugin.json hooks pointer). Left as-is this session; disable-to-silence is the fix when addressed (don't patch the regenerable clone).
Pending added:
  - Test-drive /qa on the Davinci Storybook audit (the real validation; original QA task still open).
  - Build the 5 sibling hubs (/ds /figma /motion /type /redesign) from the /qa pattern once proven.
  - Apply the description contract to the ~8–10 semantic-overlap zones (impeccable/design-engineer/ds-advisor; nuxt vue vs fw-vue).
  - Disable arch-guild@claude-1337 to silence the boot error (or await upstream fix).
  - Install the skills-resolver hook on work Mac (stream+offline) and Windows desktop.
  - Seed 07-projects/15-DavinciRemake/SESSION-STATE.md (still missing; flagged Phase 1).
  - Optionally document /qa + operation grammar in workspace CLAUDE.md / dispatcher.
Pending resolved:
  - Drive Stream→Mirror relocation broke skill file access — RESOLVED: bootstrap now resolves both roots; symlink repointed to ~/My Drive; resolver hook added.
  - Verify DC writes on Personal MacBook (long-standing deferred item) — confirmed working this session.
Next:
  - Run /qa against the Davinci Storybook (apps/docs) in light + dark, then /qa triage the findings into a phased plan — closes the original QA-audit ask and validates the hub pattern.
--- END BLOCK ---

---

--- SESSION BLOCK ---
Date: 2026-05-23
Machine: Work MacBook Pro
Surface: Claude Code (Mac desktop app)
Project(s): Centric design system — figma-repo-sync-plugin (Bundles 11.3.49 → 11.3.70)
Artifacts:
  - external: 2 commits on cpes-software/centric-ui `feat/figma-repo-sync-plugin` (1cf3b73, feeb56f) — Bundles 11.3.49–70. 445/445 tests green, build ~570kb. NOT pushed (held; 74+ commits ahead).
  - docs: 07-projects/09-figma-repo-sync-plugin/docs/2026-05-22-color-pipeline-refactor-plan.md — 3-agent root-cause audit of shadcn→Tailwind→Figma color pipeline + phased refactor plan.
  - docs: 07-projects/09-figma-repo-sync-plugin/docs/2026-05-23-state-representation-decision-tree.md — authoritative CVA variant×state→Figma spec (locked decisions, grouped naming, ring anatomy, engineer-doc requirement).
  - (?) binding regression CLOSED: Phase 0 killed the opaque-black default in resolveVariableRGBAAtMode (destructive now resolves red); page-level + Badge-glyph Colors mode pinning removed 409 unpinned-mode (?); authoritative scanner (resolvedVariableModes/resolveForConsumer + multi-value diag) proved the residual 3 (?) are cosmetic multi-value CVA tokens, not defects.
  - State-representation pattern on Button + Badge: grouped `<slot>/<state>` variable naming (explicit `default`); physical State axis; foreground-tinted state-layer overlays (hover 12% / focus 24% / pressed 32%); focus ring + error (border+ring) overlays; disabled 50%; per-component state derivation (Badge → hover/focus/error only).
  - Button Type expansion: None/Leading/Trailing/Both + Icon with size-responsive icon-side padding (new iconPaddingLeft/Right vars). Footer de-clip (rings no longer clipped). variantChild idempotency fix. Phase 1: TOKEN_PALETTE derived from COLOR_TOKENS (single source) with palette-generator migration seam.
Decisions:
  - Figma modes = a mutually-exclusive vertical slice per collection; state-as-modes is a valid/standard pattern, NOT "multiplexing" (Sean corrected my framing).
  - Component with BOTH variant + states → make ONE axis PHYSICAL (states physical, fewer; variant stays modes). Full Type×State matrix, no ceiling, consistent across all components.
  - Decision B (normalized state-layer): Figma can't mode-drive opacity, so states render as overlay nodes — fill bound to `foreground` (on-color, mode-driven, theme-aware for free), node opacity uniform per state. State-layer color = foreground (self-adapting contrast).
  - Ring = dedicated stroke overlay node (outward offset, pinned all sides) — one consistent model for focus + error.
  - Variable naming: grouped `<slot>/<state>` with EXPLICIT `default` (folder affordance, chose DX over code-literal). ENGINEER-DOC owed: document why `default` exists (structural, not code-derived) in in-Figma + Storybook docs when built.
  - Palette generator (scripts/generate-color-palette → palette.generated.css, OKLCh + APCA) is the future single source of truth. Use codebase as-is for now; COLOR_TOKENS is the documented migration swap-seam. Sean to align with engineers + build migration path before adopting.
Pending added:
  - figma plugin: Phases 2–3 (unify the two class parsers / one binder) — deferred; lower value post state-work; do as focused pass against a clean regen.
  - figma plugin: palette-generator migration — wire plugin to consume palette.generated.css; pending engineer discussion + non-breaking migration path.
  - figma plugin: Type×State regen-over-existing preserves only base cells (Leading/Trailing/Both + state clones churn ids each regen, as Badge already does); full instance-preserving idempotency not yet hardened.
  - figma plugin: engineer-doc for the `default` naming affordance (in-Figma + Storybook).
Pending resolved:
  - figma plugin: (?) binding regression on generated components — CLOSED (verified cosmetic).
  - figma plugin: Button/Badge state + icon-type representation — landed.
Project status changes:
  - figma-repo-sync-plugin: Bundle 10B/11.1 era → 11.3.70 — state-representation pattern + (?) fixes + Button Type expansion landed; 374 → 445 tests.
Next:
  - Sean: regular regen on 11.3.70 to verify idempotency (no duplicate sets, correct Type×State matrix) + full render against a clean baseline.
  - Then decide Phases 2–3 (parser/binder unification) vs other priorities.
--- END BLOCK ---

---

--- SESSION BLOCK ---
Date: 2026-05-20
Machine: Work MacBook Pro
Surface: Claude Code (Mac desktop app)
Project(s): Centric design system — figma-repo-sync-plugin (Bundles 10B.21 → 10B.28)
Artifacts:
  - external: 46 commits on `cpes-software/centric-ui feat/figma-repo-sync-plugin` (6d5d696 → 46c36b5) — Bundles 10B.21–10B.28. 406/406 tests green, build ~509kb. **NOT pushed** at Sean's preference; held until validation regen lands.
  - Bundle 10B.21 — composable slots simplified to single position-named boolean (`Leading content` / `Trailing content`); deleted redundant `showLeadingIconContent`/`showTrailingIconContent` props.
  - Bundle 10B.22 (r1–r5) — Button converted to ComponentSet with `Type=Text|Icon` variant. Colour axis renamed "Types" → "Variant". Fixed combineAsVariants children losing AUTO layout positioning; fixed applyAttributesToInstance throwing on variant-child `componentPropertyDefinitions` (now reads defs from parent SET); fixed reuse path throwing on variant-child property ops (detach-to-page → rebuild standalone → recombine; component-id preserved so consumer instances survive). variances.ts: composition.button-type-variant.
  - Bundle 10B.23 + 10B.24 — Fixed #D9D9E0 grey-fallback bug. styleStub now denylists non-color `bg-*`/`border-*` utilities (`bg-blend-*`, `bg-clip-*`, `border-solid|dashed|*`, etc.); skips CSS keywords (`transparent`, `current`); defaults uncoloured `border` to the border token. variances.ts: infrastructure.non-color-bg-utilities. +4 styleStub tests.
  - Bundle 10B.25 (r1–r3.5) — Avatar fully restructured. `.Avatar/Content` private ComponentSet with `Content=Fallback|Image|Count` replaces standalone AvatarImage/AvatarFallback/AvatarGroupCount (componentCategories: `omittedSubSuffixes`). `Avatar — Sizes` mode collection drives diameter (xs/sm/default/lg). `Avatar — Ring` mode collection drives strokeWeight (off=0 / on=2) — strokes on frame replaced child-frame ring after STRETCH/SCALE constraints didn't reflow reliably under variable-mode parent-size changes (Sean's alt). `populated AvatarGroup` fixture. Image-bake overlay UI (single randomuser.me fetch per session) with Regenerate-images toggle + per-file skip pref. Rename: `.Avatar/Content` private, `Avatar/Group` published. Forced Ring boolean default OFF via `editComponentProperty` (existing `ensureBooleanProperty` doesn't reset stale defaults). `clearExplicitVariableModeForCollection` on nested nodes each regen prevents pin accumulation breaking cascade. variances.ts: composition.avatar-content-variant.
  - Bundle 10B.26 + 10B.26.1 — Image-bake overlay (AVATAR_BAKE_PROMPT/REGEN/CONTINUE) added to types.ts/code.ts/ui.html/manifest.json (randomuser.me allowedDomain). 10B.26.1 hotfix: my 10B.26 case was inserted at end of UI switch with unbalanced braces (mistook switch close `}` for case close) → `window.onmessage` failed to parse → ALL UI handlers silently broken including Save PAT. Moved case to safe position before GENERATE_ALL_DONE; reverted brace structure. PAT/binding clientStorage was never lost — only UI was broken.
  - Bundle 10B.27 (r1–r2) — Badge as ComponentSet. `Badge — Shape` mode collection (pill / rounded). `.Badge/SlotContent` private set with `Content=Icon|Link|Spinner` (raw Material Symbols glyph TEXT as scaling lever, not locked-size icon component). Badge ComponentSet with `Type=None|Leading|Trailing|Both` baking slot visibility + per-side padding. Material font preloaded in CVA path. Single-CVA branch now calls `layoutGeneratedComponentsOnPage()` (was skipping placement). variances.ts: composition.badge-shape-and-slots.
  - Bundle 10B.28 — `ensureComposableSlotBoolean` forces default each call via `editComponentProperty` (same stale-default class as Avatar Ring r2.6). Button Icon-variant's leading slot was off by default; now on by default for Icon type.
Decisions:
  - **Strokes on frame > absolutely-positioned child frame** for reactive ring/border sizing under variable-mode size changes. STRETCH/SCALE constraints don't reapply reliably; bound strokeWeight does.
  - **Composable slots: single position-named boolean** (`Leading content` / `Trailing content`) — slot's own visibility prop, content always present underneath. No redundant inner toggle.
  - **Variant axis naming: "Variant" not "Variants" or "Types"** for the colour axis on Button. Sean wants singular noun.
  - **Modes vs physical variants:** Sean is not worried about variable-mode-driven permutation counts (40 etc.) — only physical Figma variants. Use mode collections for orthogonal cascading-attribute axes (size, shape, ring); use ComponentSet variants for behaviorally-distinct shapes (Button Type=Text|Icon, Badge Type=None|Leading|Trailing|Both, Avatar/Content Content=Fallback|Image|Count) that bake structural slot visibility / padding.
  - **Idempotency under variant rebuild:** When existingTextNode/IconNode are variant children inside a prior set, detach to page → rebuild standalone → recombine. Component-id stability preserves downstream instance references.
  - **`ensureBooleanProperty` / `ensureComposableSlotBoolean` stale-default class:** Both return the existing key without resetting `defaultValue` if the prop already exists. Use `editComponentProperty(key, { defaultValue: ... })` each call to force.
  - **`figma.root.setPluginData`** (per-file) for "skip image bake" flag; `figma.clientStorage` (per-user) reserved for PAT/binding. Per-file pref survives plugin reinstall and is correct scope for asset-fetch consent.
  - **Inline-script SyntaxError aborts the whole `<script>` block.** If `window.onmessage` doesn't parse, every UI handler dies silently. New `case` branches go in the safe middle, not appended at end where switch-close braces are easy to miscount.
  - Held push of all 46 commits at Sean's preference. Per-component walkthrough proceeds locally; push when validation lands.
Pending added:
  - Sean to regen and validate 10B.28 — Button Icon variant's leading slot should now default visible.
  - Per-component walkthrough continues. Next component TBD by Sean (Avatar ✓, Badge ✓, Button pending Icon-slot validation).
  - Push `feat/figma-repo-sync-plugin` (46 commits) when Sean signals ready.
  - Capture Patterns 15–27 in `08-knowledge/engineering/figma-plugin-patterns.md` from this session (variant-child propdef restriction, detach-recombine idempotency, stroke-on-frame over child-ring, slot `#id`-suffix matching, ensureBoolean stale-default class, modes-vs-variants criteria, glyph TEXT scaling lever, UI inline-script brace-budget, AUTO layoutPositioning after combineAsVariants, per-file vs per-user plugin data, clearExplicitVariableModeForCollection on nested nodes, styleStub Tailwind-prefix denylist discipline, `Avatar — Ring` strokeWeight binding alternative to child frame). Not authored this session — Edit failed read-first and deferred at /session-end.
Pending resolved:
  - Composable-slot simplification (10B.21).
  - Button Type=Text|Icon ComponentSet stable (10B.22 r1–r5).
  - #D9D9E0 grey fallback bug (10B.23, 10B.24).
  - Avatar full restructure including ring strokeWeight binding, image bake UX, populated AvatarGroup, Sizes mode cascade (10B.25).
  - Plugin UI handlers restored after 10B.26 brace bug (10B.26.1).
  - Badge ComponentSet with `Type=None|Leading|Trailing|Both` + `.Badge/SlotContent` glyph TEXT slot pattern (10B.27).
  - Composable-slot boolean default forced each call (10B.28).
Next:
  - Sean validates 10B.28 Button Icon regen.
  - Push held branch when Sean signals.
  - Continue per-component walkthrough on Sean's pick.
  - Write Patterns 15–27 to figma-plugin-patterns.md (carry into next session).
--- END BLOCK ---

---

--- SESSION BLOCK ---
Date: 2026-05-13
Machine: Work MacBook Pro
Surface: Claude Code (Mac desktop app)
Project(s): Centric design system — figma-repo-sync-plugin Components-page audit + 10A.2 Phases 1–3b + 10B.1.1
Artifacts:
  - external: 5 commits on `cpes-software/centric-ui feat/figma-repo-sync-plugin` (b93c76c → c74e696) — Bundles 7.2–11 + 10A.2 Phases 1, 2.1, 3b + 10B.1.1 + Phase 3a.1. 374/374 tests, build 420.3kb.
  - `08-knowledge/engineering/figma-plugin-patterns.md` — added Patterns 9–14: fallback chains never short-circuit, single-component slot-default wiring from synthetic fixture children, Tailwind layout inference leaky abstraction (3 fail modes), Figma masters show canonical example not React default, master-assembly vs slot-defaults dedup layers, diagnostic logs unblock multi-mechanism debugging.
Decisions:
  - Audit reframe: 11 ❌ from the 2026-05-12 audit looked like one bug, was actually 4+ distinct mechanisms. Diagnostic logging (`[Bundle 10A.2 diag]` lines at 4 checkpoints per compound parent) was the FIRST commit — let each component's failure mode name itself in the dev console, then split fixes into discrete shippable bundles.
  - Phase 1 (b93c76c): `fetchStoryTree` no longer returns early on story 404 or parse-empty — both paths fall through to shadcn → fixture chain. Original failure reason prefixed onto chosen-source diag. Unblocked Form / Sidebar / Sheet / NativeDialog (4 of 11 ❌ fixed).
  - Phase 2.1 (5113b1c): walker synthesizes a text child from `placeholder` attribute when HTML form-field elements (`<input>`, `<textarea>`) have empty children. Plus single-component dispatch injects fixture placeholder into the source-anatomy's nested `<input>` frame when wrapped in a styled div (the Input.tsx pattern). Unblocked Input / Textarea (2 more — 6 of 11 ✅).
  - Phase 3a (1a7ce90): `dedupeRepeatedRefs` moved to anatomyWalker.ts and exported. Added `LIST_CONTAINER_SUBCOMPONENT_NAMES` exemption (TabsList, TableRow, SelectGroup, AvatarGroup, SidebarMenu, etc. keep all N children at slot-defaults computation) + `dedupeAssemblyRepeats` special-cased for Tabs master assembly (collapses 3+ TabsContent siblings to 1). Count fix only — axis still vertical, content still uniform.
  - Phase 3a.1 (d293b42, amended): `inferLayoutMode` now (a) filters conditional classes (data-[…], group-data-[…], hover:, dark:, etc.) before flex regex matching — fixes TabsList where `inline-flex` was beaten by conditional `group-data-vertical:flex-col`, (b) supports HTML tag-default override (`<tr>` → HORIZONTAL) for TableRow, (c) supports per-componentName override (TabsList, AvatarGroup) for the cnExtractor cva-unwrap gap (`cn(tabsListVariants({variant}),...)` returns empty baseClasses). Resolution order: class → tag → componentName → block-flow default. Unblocked Tabs + Table axis (8 of 11 ✅).
  - Phase 3b (c74e696): single-component dispatch maps synthetic fixture children (`EmptyStateTitle`, `EmptyStateDescription`, `EmptyStateAction`) to slotDefaults keyed by lowercased suffix — wires fixture content into source-anatomy's `{title}`/`{description}`/`{action}` slot expressions. Plus `applyConditionalNode` defaults the frame VISIBLE (and BOOLEAN property TRUE) when inner anatomy contains a slot with a story-driven default — Figma masters show the canonical example, not React's "falsy → hidden" runtime state. Unblocked EmptyState (9 of 11 ✅).
  - Memory rules engaged: framework #06 (QA Operating Model — load by default for audits, target-user lens, sticker-sheet rubric not silhouette, every-component coverage, pre-output critical-eye gate, iteration-default mindset), proactively loaded ds-advisor + design-engineer skills, used `figma-repo-sync-plugin` upsert-in-place semantics.
  - Avatar deferred — `size-full` Tailwind class doesn't translate to Figma fill-parent layout sizing; needs deeper investigation into styleStub.
  - ScrollArea deferred — story wins (rich=13) but its single `<div>` wrapper child gets filtered by PascalCase tag check. Two paths: lower scroll-category richness threshold so fixture wins, or recurse through HTML wrappers (affects all categories).
Pending added:
  - figma-repo-sync-plugin Phase 3c — ScrollArea fix (scroll-specific richness threshold OR HTML-wrapper recursion).
  - figma-repo-sync-plugin Avatar size-full → Figma layout-sizing translation (separate bundle).
  - figma-repo-sync-plugin Phase 4 — per-instance content overrides for Tabs/Table/EmptyState (every TabsTrigger currently says "List view", every TableHead "Name", every EmptyState action button "Button"). Requires writing `componentProperties` per instance.
  - Dialog `.DialogContent` 108×845 narrow column — Bundle 10B.2 partial-slot architecture.
  - Badge `secondary` token cascade investigation.
  - Extend `extractCnBaseClassesFor` to recognize `cn(cvaCall(...), …)` patterns and pull the cva base (would obsolete HORIZONTAL_LAYOUT_COMPONENT_NAMES override list).
Pending resolved:
  - 9 of 11 ❌ from the 2026-05-12 audit promoted to ✅: Form, Sidebar, Sheet, NativeDialog (Phase 1) · Input, Textarea (Phase 2.1) · Tabs, Table (Phases 3a + 3a.1) · EmptyState (Phase 3b).
  - Bundle 7.2–11 work that was uncommitted from prior sessions — committed and pushed.
Next:
  - Phase 3c (ScrollArea) — quickest to wrap remaining ❌ at scroll-category-specific scope.
  - Then Avatar layout-sizing — needs investigation into Tailwind `size-full` → Figma `layoutSizingHorizontal/Vertical=FILL` translation, also style cascade on circular masks.
  - Sean to push back if anything from the 9 fixes looks wrong on his next regen (TabsList horizontal, EmptyState description/action visible defaults are most likely candidates for "actually no, leave it hidden").
--- END BLOCK ---

---

--- NANO BLOCK ---
Date: 2026-05-13
Machine: Work MacBook Pro
Surface: Claude Code (Mac desktop app)
Context load only — no decisions or artifacts.
--- END BLOCK ---

---

--- SESSION BLOCK ---
Date: 2026-05-12 (cont.)
Machine: Work MacBook Pro (main, going forward — CS-K746DRWXY1)
Surface: Claude Code (Mac desktop app) — worktree `laughing-mestorf-e7720b`
Project(s): Cross-project DS knowledge (Mobbin enterprise SaaS audit — full execution + synthesis + operational mechanism)
Artifacts:
  - `04-artifacts/active/enterprise-saas-pattern-audit_section-a_v0.1_2026-05-12.md` — Stream A audit, 20 PLM-critical patterns. Fast pass + deep re-audit pass for 6 flagged conditionals. 20/20 graduate; 5 of 6 deep gaps closed (Vanta density, Neon/Canva typed cells, Salesforce record-merge, 4-vendor CSV validation step, Linear inbox). 6th gap (A18 GitHub-Actions-style task queue) escalated to Section D direct-DS reads — Mobbin's catalog under-indexes infra-job surfaces.
  - `04-artifacts/active/enterprise-saas-pattern-audit_ai-forward_v0.1_2026-05-12.md` — Stream C audit, 8 AI-forward patterns. Fast pass complete; 8/8 graduate. Strongest PLM finding: C8 per-record AI summary with Maze's anchored-to-source provenance pattern — regulated-industry compliance demands hover-traceable claims.
  - `04-artifacts/active/enterprise-saas-pattern-synthesis_v0.1_2026-05-12.md` — synthesis: 5-tier impact-ranked graduation queue (28 patterns), cross-pattern primitive spine consolidated (8 Stream A structural + 7 Stream C AI-provenance primitives), cross-stream tensions resolved (cell anatomy + AI cell state share one token namespace; diff view + AI variant pick share one `LineDiff` primitive; drawer + AI chat share one primitive with new content shapes; etc.).
  - `08-knowledge/design/enterprise-saas-design-patterns.md` — **master operational entry** (~400 lines). Decision tree at top (identify the surface shape → which patterns + which primitives); compact 15-primitive reference (StatusPill, Drawer, TypedFieldEditor, ActivityItem, RelationChip, Stepper, PropertiesRail, KeyboardShortcutMenu + 7 AI-provenance primitives); when-to-build-X routing for 8 surface types; token vocabulary (density tokens / status state set / cell state matrix / drawer sizes / stepper states); AI provenance discipline checklist; 28-pattern compact catalog; 12 anti-patterns. Registered in `_INDEX.md` with 22 explicit trigger words for UserPromptSubmit auto-loading.
  - Cross-links added to `02-skills/ds-advisor/SKILL.md` (new "Related Knowledge" section after Core Principles, instructs the skill to read the master entry first on enterprise-SaaS work) and `02-skills/design-engineer/SKILL.md` (Reference Spokes table, marked auto-load on enterprise SaaS / PLM layout work).
Decisions:
  - Mobbin audit cadence: fast mode + tight keyword queries for breadth; deep mode reserved for targeted re-audit of conditional graduations and canonical-reference gaps. Fast returned in ~5s per query; deep timed out on sentence-style queries but worked on focused keyword phrases. Default to fast; flag specific patterns for deep re-audit when needed.
  - Per-pattern audit cadence: limit=5 screens, 1 search → 1 artifact edit. Cross-refs to adjacent patterns captured inline rather than skipping ahead.
  - Cross-pattern primitives surfaced 3-6× across the audit ARE the load-bearing output — Centric DS should be built primitive-first, not pattern-first. 15 primitives identified (8 structural + 7 AI-provenance).
  - Graduation strategy: don't pre-author 28 individual `08-knowledge/design/{slug}.md` entries; let Centric work demand drive depth. The master entry IS the graduation; individual entries materialize when a project touches them.
  - For PLM AI features specifically: prefer anchored-to-source-span (Maze model) over confidence-percentage alone. Regulated industries care less about "78% confident" and more about "this claim points to this verifiable evidence."
  - Stream C re-audit scheduled for ~2027-Q3 (12-18 months) when emerging patterns C4 NL-workflow / C5 canvases / C7 true-merge mature.
Pending added:
  - **Section D — direct-DS deep reads.** Atlassian, Carbon, Salesforce Lightning, Workday Canvas, Adobe Spectrum, Polaris, Primer, Fluent 2. Pre-step: enumerate available MCPs via `mcp-registry`, identify published Figma libraries reachable via Figma MCP, fall back to WebFetch. Priority targets for closing the A18 task-center gap: GitHub Primer (Actions runs), Vercel (Deployments), Stripe (Export queue).
  - **Section B audit** (18 adjacent enterprise SaaS patterns from taxonomy) — defer until Section A graduations stabilize. Most B-patterns reuse Section A primitives; lower-urgency than D.
  - **Individual pattern entry graduations** — 28 entries at `08-knowledge/design/{slug}.md` are flagged but unauthored. Graduate one-by-one as Centric work creates demand.
Pending resolved:
  - Mobbin enterprise-SaaS pattern audit kickoff (both Stream A and Stream C) — completed end-to-end. Taxonomy → audits → synthesis → operational master entry → skill cross-links.
Next:
  - **Section D direct-DS audit opens next.** Pre-step: enumerate MCPs/plugins/skills per DS before WebFetch fallback.
  - **Trigger:** when a Centric brief mentions any of the 22 trigger words registered in the master entry's frontmatter (`data table`, `record detail`, `bulk edit`, `approval workflow`, `cell anatomy`, `provenance`, etc.), the UserPromptSubmit hook should auto-surface the master entry. First substantive use will validate the mechanism.
--- END BLOCK ---

---

--- SESSION BLOCK ---
Date: 2026-05-12
Machine: Work MacBook Pro (main, going forward — CS-K746DRWXY1)
Surface: Claude Code (Mac desktop app) — worktree `laughing-mestorf-e7720b`
Project(s): Cross-project DS knowledge (enterprise SaaS pattern taxonomy + Mobbin MCP setup)
Artifacts:
  - `04-artifacts/active/enterprise-saas-pattern-taxonomy_v0.1_2026-05-12.md` — v0.2 (decisions locked). Section A (20 PLM-critical), B (18 adjacent enterprise SaaS), C (8 AI-forward), D (reference DSs). Audit work-stream shape + graduation rule. Sean answered the five open questions in-conversation; v0.2 captures them at the top.
Decisions:
  - Audit shape: two concurrent independent Mobbin streams. Stream A (Section A → B continuation) and Stream C (AI-forward) produce separate sibling artifacts; no cross-stream synthesis, only "see also" cross-references.
  - Section D (DS-source deep reads) sequenced after Streams A + C; pre-step enumerates direct-access tooling per DS (Atlassian MCP, mcp-registry queries, Figma MCP libraries, WebFetch fallback) — most direct context, least lossy.
  - Knowledge graduations land flat in `08-knowledge/design/` (no enterprise-patterns/ subdir). Skill split: `ds-advisor` for strategy/triage/governance entries; `design-engineer` for component/code/primitive entries.
  - Graduation rule expanded — a pattern graduates if it changes Centric DS, future-PLM thinking, OR how Claude generates enterprise-SaaS layouts and composes components.
  - Mobbin MCP moved from local scope (was tied to `/Users/sean.sands` cwd via default `claude mcp add`) to user scope so it loads on every Claude Code session regardless of starting directory. Backup of pre-edit `~/.claude.json` left at `~/.claude.json.bak-mobbin-cleanup`.
  - Worktree-sync gotcha: when worktree's HEAD lags behind main (other-session commit landed on main first), root-level files appear "modified" in the worktree's `git status` because the worktree's working directory is nested inside the parent workspace. Safe resolution: `git reset main` (mixed, non-destructive) when the worktree branch has zero commits ahead of main.
Pending added:
  - **After Sean's Claude Code restart + Mobbin OAuth on first call:** kickoff Stream A audit (Section A — 20 patterns) and Stream C audit (Section C — 8 AI-forward patterns) concurrently. Scaffold both output artifacts (`enterprise-saas-pattern-audit_section-a_v0.1_{date}.md` and `enterprise-saas-pattern-audit_ai-forward_v0.1_{date}.md`) before kickoff.
  - Stream A continuation pass (Section B — 18 adjacent enterprise SaaS patterns) follows after Stream A Section A reaches v0.1.
  - Section D audit (reference design systems: Atlassian, Carbon, Lightning, Workday, Spectrum, Polaris, Primer, Fluent) follows Streams A + C v0.1. Pre-step: enumerate available MCPs / plugins / skills per DS before opening WebFetch fallbacks.
Pending resolved:
  - Mobbin MCP successfully installed at user scope; first-call OAuth flow pending Sean's restart.
Next:
  - Sean fully quits Claude Code (Cmd+Q), reopens from anywhere, `/mcp` confirms `mobbin` connected (OAuth flow completes on first tool call). Reprompts in a new session — taxonomy artifact + the audit-shape decisions are already locked in v0.2 of the taxonomy doc, so the next session loads with kickoff ready.
--- END BLOCK ---

---

--- SESSION BLOCK ---
Date: 2026-05-12 (cont.)
Machine: Work MacBook Pro (main, going forward — CS-K746DRWXY1)
Surface: Claude Code (Mac desktop app)
Project(s): Centric design system — figma-repo-sync-plugin Bundles 7.2–11 audit + ships
Artifacts:
  - external: figma-repo-sync-plugin Bundles 7.2 (icon library combineAsVariants fix + orphan cleanup), 7.3 (recursive upsert for icon sets + sections + position-lock skip-on-stable), 7.4 (default Page 1 repurposing across both generators), 7.5 (per-icon event-loop yield killing the perceived hang), 7.6 (stable "icon" inner TEXT layer name + foreground variable binding detection), 7.7 (fetched-at timestamp replaces null manifest version + "v?" cleanup), 7.8 (Component page → Components rename + legacy migration)
  - external: figma-repo-sync-plugin Bundle 8 (variant cascade fix — `transparent` / `none` tokens + missing slots resolve to alpha-0 rather than the prior `background` body-default route)
  - external: figma-repo-sync-plugin Bundle 9 (typography foundation — new textStyles.ts module, 14 canonical Text Styles, async ensureScaffolding loads sans Regular/Medium/Semibold/Bold + mono Regular, applyInferredTextStyle applied to all anatomy-walker text + assembly-layer text)
  - external: figma-repo-sync-plugin Bundle 10A.1 (AlertDialog media-icon non-stretch — added `/Media$/` to NON_STRETCHING_NAME_PATTERNS)
  - external: figma-repo-sync-plugin Bundle 10B.1 (dedup pair-vs-loop heuristic — pairs stay, 3+ runs collapse; restores Dialog Cancel+Continue + AlertDialog Cancel+Action + brings Tabs N triggers back)
  - external: figma-repo-sync-plugin Bundle 11.1 (centric-shadcn-variances.md catalogs every audit-discovered divergence with keep/upstream-fix/plugin-fix recommendations)
  - external: PR opened — `[Draft] figma-repo-sync-plugin: initial implementation (FYI — iterative)` against centric-ui main, two commits (scaffolding + implementation)
Decisions:
  - Audit protocol established for design-system QA work — Framework #06 target-user lens, reference at meaningful zoom, sticker-sheet rubric (composition correctness, not footprint), every-component coverage, pre-output critical-eye gate, iteration-default mindset.
  - First imprecise audit claim ("variants collapse to outline") retracted after Sean pushed back — corrected by reading actual centric-ui source. destructive is intentionally tinted (`bg-destructive/10`); the true bug was `border-transparent` resolving to TOKEN_FALLBACK_FILL light-gray instead of alpha-0. Lesson: ground every audit claim in source code, not visual impression.
  - Centric-ui variances from canonical shadcn ARE divergences from baseline; per Sean's directive, err on the side of 1:1 parity and document. centric-shadcn-variances.md is the living catalog.
  - Dialog/Sheet partial-slot pattern (Header instance + Body SlotNode + Footer instance) is the right architecture but deferred — needs new compound-assembly mode beyond Bundle 5E's full-body slot.
  - Bundle plan structured 8 → 9 → 10A → 10B → 11; 10A/10B/11 each split into a "shippable now" part and a "deferred deeper work" part rather than blocking on the deeper pieces.
  - Plugin committed to `feat/figma-repo-sync-plugin` branch (off `main`) in centric-ui, two commits (scaffolding + implementation), opened as Draft PR for team visibility, branch tag `[Draft]` in title signals "not for review."
  - SSH remote alias mismatch surfaced on this machine: centric-ui's git remote uses `git@github-centric:` but the local `~/.ssh/config` has `github-work`. Sean handled the remote URL rewrite himself.
Pending added:
  - figma-repo-sync-plugin Bundle 10A.2 — Input/Textarea HTML-element walker handling + Form/Sheet/Sidebar/ScrollArea/EmptyState empty-anatomy investigation
  - figma-repo-sync-plugin Bundle 10B.2 — Partial-slot pattern (Header + Body SlotNode + Footer) for Dialog/Sheet/AlertDialog/Card + Dialog absolute-positioned close X
  - figma-repo-sync-plugin Bundle 11.2 — States-as-variants sweep (Switch on/off, Checkbox checked/unchecked/indeterminate, Radio selected, Input focus/error) + master preview density polish
  - figma-repo-sync-plugin follow-up audit when Sean regenerates with all current bundles applied
Pending resolved:
  - figma-repo-sync-plugin committed to centric-ui repo + Draft PR opened
  - Variant cascade leak (destructive border, ghost/link transparency, SelectTrigger bg-transparent)
  - Typography hierarchy missing (Card/Dialog/AlertDialog title vs body indistinguishable)
  - AlertDialog media-zone oversizing
  - Dialog/AlertDialog showing only one action button (Cancel+Continue collapsed)
  - Icon library hang during generation (per-icon work was synchronous between progress events)
  - Icon library "manifest v?" cosmetic gap (replaced with fetched-at timestamp)
  - Generated "Component" page renamed to "Components" with legacy migration
  - Default Page 1 now repurposed instead of left orphaned
Next:
  - On next session, Sean regenerates everything from the plugin's latest build and surfaces the regenerated Figma file URL. Re-audit each component against the same criteria, score against the bundles shipped, identify what still needs Bundle 10A.2 / 10B.2 / 11.2.
  - If Bundle 10B.2 (partial-slot pattern) is up next, scope before coding — it's a new compound-assembly mode; partial slots are different from Bundle 5E's full-body slot.
--- END BLOCK ---

---

--- SESSION BLOCK ---
Date: 2026-05-12
Machine: Work MacBook Pro (main, going forward — CS-K746DRWXY1)
Surface: Claude Code (Mac desktop app)
Project(s): Centric design system — figma-repo-sync-plugin Bundle 7.1 (Variables collection fix)
Artifacts:
  - external: figma-repo-sync-plugin @ ~/projects/cpes-software/centric-ui/figma-repo-sync-plugin — Bundle 7.1 ships fix for the "Foundations / Colors has 3 modes including spurious Value" bug introduced by Bundle 7. 334/334 tests, build 391kb. Not in workspace git.
Decisions:
  - Bundle 7.1 root cause: Bundle 7 unified two CONCEPTUALLY DIFFERENT collections under one name because they shared a textual prefix. variableSync.ts Pass 1 wrote palette primitives (cds-blue-500, single Value mode); foundations.ts seeded semantic colors (background/foreground, Light+Dark modes). Bundle 7 forced both to "Foundations / Colors" — whichever pipeline ran second added its mode to the existing collection, yielding 3 modes (Value + Light + Dark) with the Value column mostly FFFFFF because palette-primitive values lived there while semantic colors lived in Light/Dark.
  - Fix architecture: split back into two collections by SEMANTIC PURPOSE — "Foundations / Palette" (single Value mode, palette primitives from variableSync Pass 1 only) + "Foundations / Colors" (Light+Dark, semantic colors merged from foundations.ts seeds + variableSync Pass 3). Within each, both producers can safely co-author because they agree on the mode structure.
  - Migration: legacy name map updated — Foundations/Color → Palette (NOT Colors); Semantic/Color → Colors; Semantic / Colors (Bundle 7 transitional) → Colors. New Pass 3 in dedup sweep detects the 3-mode artifact: if all variables have Light+Dark values, safely drops the Value mode; if any variable is Value-only, leaves the collection and warns (clear+regenerate needed to land palette primitives in Palette).
  - Knowledge captured: 6th pattern added to 08-knowledge/engineering/figma-plugin-patterns.md — "Name unification must respect semantic purpose, not just textual similarity." Same-noun ≠ same-concept. Quick checklist for verifying before unifying: mode structure agreement, content kind, lifecycle, variable-name overlap.
Pending added:
  - Visual QA pass after clear+regenerate to confirm: single-mode Foundations / Palette appears, two-mode Foundations / Colors appears (no Value column), variable counts match expectations.
Pending resolved:
  - Bundle 7 misconfiguration (Foundations / Colors with 3 modes, white Value column)
Next:
  - Sean clears collections one more time, regenerates from scratch, verifies the corrected two-collection architecture
  - Pick next bundle direction or visual QA on 5E/5F (Popover slot, Select rebuild)
--- END BLOCK ---

---

--- SESSION BLOCK ---
Date: 2026-05-12
Machine: Personal MacBook Pro (Voyager-2)
Surface: Claude Code (Mac desktop app)
Project(s): Legion (13-legion) — reference-driven galaxy visualization rewrite
Artifacts:
  - external: https://github.com/snds/legion — 2 new commits on standalone repo (af961c9, ea72616)
  - /Users/snds/Desktop/galaxy videos/ — 4 ESA + Hayden reference videos (Stellar Nurseries 3D, Best Milky Way by Gaia, Universe Fly-Through, Hubblecast70b); 66 triage frames extracted via ffmpeg for systematic analysis
Decisions:
  - Reference-video review identified 7 structural gaps in the existing implementation: orbital-only camera (no translation), no velocity-aware effects, stacked-plane disc (cannot read correctly off-axis), nebulae as billboards (no parallax volume), no HDRI backdrop, tier-breakpoint-based LOD (popping), and no persistent feature labels. Wholesale-rewrite-friendly review per Sean's note.
  - Rewrite priority order: (1) velocity-aware micro-streaks, (2) cinematic flight-path camera, (3) volumetric raymarch disc, (4) volumetric nebulae, (5) HDRI cosmic backdrop, (6) distance-driven continuous LOD, (7) persistent labeled features. First three landed this session.
  - Star streaks gated to "minor/subdued/possibly omitted" per Sean's explicit constraint. Speed threshold 6000 WU/s — below normal navigation speeds, ramps to full only during long galactic flight-path traversals. Max stretch 1.4x sprite size, alpha drops 50% at full stretch so streaked stars register as in-motion/dimmer rather than larger/brighter.
  - Cinematic flight-path mode: quadratic Bezier with control point lifted 30% of travel distance along +Y (arcs OVER the galactic plane, not through it). Ease-in-out cubic timing matches the "settled moments" rhythm observed in ESA references. On arrival, snap_orbit_state_to_current_pos() reconstructs theta/phi/focus so orbit math resumes cleanly — no jerk. Wired to shift+dblclick.
  - Volumetric raymarch disc replaces the entire 9-disc + 8-dust stacked-plane assembly: ONE BoxGeometry, 24-step ray march in fragment shader, Beer-Lambert front-to-back compositing. Looks correct from any angle including edge-on (real thin-slab thickness when tilted), dust actually occludes light from behind through line-of-sight integration (not just per-layer dim), and goes from 17 draw calls to 1.
  - Tuned for raymarch validity: DISC_Y_HALF = 400 WU (1.2 kpc — accommodates ±1 kpc warp), uDiscThickness = 150 WU (slightly wider than observed ~0.3 kpc so march steps reliably hit material), uExtinction = 0.012 1/WU (tuned so midplane integration reaches ~0.7 alpha without saturating).
Pending added:
  - Volumetric nebulae primitives (8 named phenomena become raymarched ellipsoids so they have interior structure when camera flies past)
  - HDRI cosmic backdrop at galaxy tier
  - Distance-driven continuous LOD removing the tier-breakpoint authority
  - Persistent labeled features (angular-size-driven label fade)
Pending resolved:
  - "Star streaks during traversal" — implemented gated to subtle
  - "Cinematic flight-path camera" — implemented via shift+dblclick
  - "Replace stacked-plane disc with volumetric raymarch" — done
Next:
  - Volumetric nebulae primitives via thin-box raymarch with per-nebula FBM density
  - Or pause for hands-on testing of what's landed (flight mode + new disc) before continuing the rewrite chain
--- END BLOCK ---

---

--- SESSION BLOCK ---
Date: 2026-05-11
Machine: Work MacBook Pro (main, going forward — CS-K746DRWXY1)
Surface: Claude Code (Mac desktop app)
Project(s): Centric design system — figma-repo-sync-plugin bundles 5D.2.C / 5E / 5F / 7
Artifacts:
  - external: figma-repo-sync-plugin @ ~/projects/cpes-software/centric-ui/figma-repo-sync-plugin — Bundles 5D.2.C (dependency ordering), Card-footer polish + opacity fix, 5E (slot-driven Popover), 5F (Select trigger+toggleable-content rebuild), 7 (collection upsert + dedup). 334/334 tests passing, build 389.1kb. Not in workspace git.
Decisions:
  - Bundle 5D.2.C: PRIMITIVE_FILE_BY_NAME registry + ensurePrimitivesGenerated helper + skipPrereqs flag on GENERATE_ALL_IN_FILE so compounds auto-generate their primitive dependencies first. GENERATE_ALL_COMPONENTS sorts primitives ahead of compounds.
  - Card-footer stretch root cause: layoutAlign=STRETCH alone fails when instance master has primaryAxisSizingMode=AUTO. Fix: also set layoutSizingHorizontal/Vertical = "FILL" (modern API) — overrides master's intrinsic sizing reliably.
  - Opacity preservation: styleStub now CAPTURES /N from color classes (bg-muted/50 → fillOpacity=0.5) instead of dropping. New applyOpacityToPaints helper multiplies opacity while preserving variable bindings — foundation cascade + dark-mode swap stay intact.
  - Icon slot 100×100 bug: createFrame() seeds 100×100; AUTO sizing doesn't shrink an empty auto-layout. Fix: resizeWithoutConstraints(1, 1) before icon append so the icon's intrinsic dims drive final size.
  - Bundle 5E (Popover slot): new bodyAsSlot + bodySlotName fields on CategoryDefaults. Popover/HoverCard wrap open-state assembly inside a SlotNode named "content"; Dialog/Sheet/Tooltip keep direct children (their Header/Body/Footer is structured, not freeform).
  - Bundle 5F (Select rebuild): Select-specific assembly path (parentName==="Select" + dropdown category). Master becomes thin VERTICAL container (transparent, no surface); SelectTrigger no longer filtered as infrastructure; SelectContent gets Boolean "open" component property wired to visibility via componentPropertyReferences. Default open=true so canonical asset shows the full composition. Basic/Grouped variants deferred (would require ComponentSet promotion that doesn't fit Select's non-CVA structure).
  - Bundle 7 root cause for duplicate collections: TWO parallel pipelines wrote Foundation collections with DIFFERENT naming conventions — foundations.ts used "Foundations / Colors" (spaced, plural) while variableSync.ts used "Foundations/Color" (compact, singular). Plus CVA-axis collections (Button — Sizes ×3) duplicated because existingCollectionsByAxis had no name-based fallback when plugin-data IDs were missing/stale.
  - Bundle 7 fix: (a) 3-tier lookup in existingCollectionsByAxis — owned-IDs plugin data → collection's own plugin data → display-name match via new axisFromPretty() reverse mapping. (b) variableSync.ts unified to foundations.ts naming convention; mode names standardized to "Value" across both pipelines. (c) one-shot dedup sweep in foundations.ts: rename legacy-named collections to canonical (preserves IDs + instance bindings); same-name dupes collapse to the one with most variables, losers deleted only when zero consumers, else warned for manual resolution. Surfaces results via figma.notify.
Pending added:
  - Visual QA pass on 5E/5F (Popover slot, Select trigger+content) — needs eyes-on in Figma after regenerate
  - DropdownMenu/ContextMenu/Menubar/Combobox could inherit the Select rebuild's trigger+toggleable-content pattern (~30 min when revisited)
  - Basic-vs-Grouped Select as actual variants (ComponentSet promotion) — deferred
  - Opacity propagation through inherited text-fill cascade (currently static frames only)
Pending resolved:
  - Card footer width bug (instances 96px instead of 384px inside Card)
  - bg-muted/50 rendering fully opaque (opacity was being stripped at parse)
  - Icon slot frames stuck at 100×100 inside Button instances
  - Duplicate variable collections across foundation + CVA-axis pipelines
Next:
  - Sean clears existing Variables collections, regenerates from scratch to verify Bundle 7 produces a single canonical set
  - Visual QA on Card footer + Popover + Select after regenerate
  - Pick next bundle direction: dropdown-family rollout, ComponentSet variants, or different theme entirely
--- END BLOCK ---

---

--- SESSION BLOCK ---
Date: 2026-05-11
Machine: Personal MacBook Pro (Voyager-2)
Surface: Claude Code (Mac desktop app)
Project(s): Legion (13-legion) — codebase extraction + heavy visual-fidelity pass
Artifacts:
  - 00-bootstrap/setup/gitconfig.template — added `[includeIf "gitdir:~/Projects/"] path = ~/.gitconfig.personal` so future repos under `~/Projects/` auto-pick personal identity (snds + noreply email)
  - 07-projects/13-legion/SESSION-STATE.md — rewritten to reflect new code home; design references stay in workspace, code lives at /Users/snds/Projects/Legion
  - external: https://github.com/snds/legion — new private repo, 22 commits this session on standalone Legion codebase (Three.js + TS + Vite). Initial import + ~21 visual-fidelity follow-ups.
Decisions:
  - Codebase extraction: fresh init history (no filter-repo from workspace), HTTPS remote via gh CLI auth (SSH wasn't set up on Voyager-2 yet). hello@snds.design rejected by GitHub email-privacy guard; switched to 570874+snds@users.noreply.github.com no-reply for all Legion commits. Long-term: gitconfig template now routes ~/Projects/ to personal identity which uses no-reply by default.
  - Design refs (Reference/, Screenshots/, Video/, Visual-Development/, docs/, SESSION-STATE.md) stay in workspace; code + runtime assets (src/, public/, Audio/, Fonts/, index.html, package*.json, tsconfig.json, vite.config.ts) moved to /Users/snds/Projects/Legion. Workspace 07-projects/13-legion/* was already gitignored so deletion is invisible to workspace git.
  - Galaxy visualization: procedural shader IS the disc (continuous diffuse with logarithmic spirals + bar + dust), particles are foreground "individual stars" on top. Real Milky Way structural fidelity: pitch ~13.4°, bar ~25° from Sun-GC line at ~5kpc length, exponential-disc particle distribution, +/-1kpc warp past 7.5kpc, LMC/SMC at compressed sky-correct positions, Sgr dSph tidal stream wrapping the disc twice.
  - Disc thickness via 9 stacked star layers + 8 interleaved dust layers (NormalBlending so dust actually OCCLUDES stars-behind in render order — not just dims own layer like the original inline dust). Per-layer noise seed + arm-phase rotation breaks the "5 identical stacked spirals" look that the user flagged.
  - Stars: per-particle aSize + Planckian color (pulled toward white for realism — most stars on dark sky read as near-white pinpricks). Circular soft-falloff sprite shape per user spec ("orbs/circles with sharp diffuse light falloff"). Doubled to ~160K particles.
  - 9-tier zoom hierarchy (surface, low-orbit, orbit, inner-system, outer-system, heliopause, sector, arm, galaxy) replaces previous 6-tier. Close-in tiers (surface/low-orbit/orbit) auto-scale camDist by focused-object bounding radius — fixes the "SURFACE tier dives into the sun" bug. Default boot auto-tracks the home habitable planet (Romulus in ε Eridani).
  - Object selection: ROOT-CAUSE was that none of createPlanetMesh/createMoonMesh/createBobMesh/createStarMesh/createSystemMarker/createAlienMarker were setting userData.type, so raycast's parent-walk silently discarded every hit. Fixed by seeding userData in each factory. Dblclick = focus current tier; shift+dblclick = warp to context-appropriate tier (planet→ORBIT, star→INNER SYSTEM, system→HELIOPAUSE, phenomenon→ARM).
  - Removed cool-blue post-processing tint: ColorGradingShader shadow/highlight tints zeroed, planet-surface night-side blue glow removed, ambient color → pure black. "Space is black" per explicit user note.
  - Camera: adaptive FOV by camDist (32° telephoto close → 72° wide galactic), finer zoom step (0.012 plain wheel, 0.003 Shift, 0.04 Ctrl/Alt), hotkeys 1-9 snap to named tiers.
  - Per-layer-uniform pattern offsets (uLayerSeed + uLayerArmShift) are the right answer for stacked-disc volume — NOT extra layer count alone. 9 layers with identical patterns read as 9 concentric spirals; same 9 layers with per-layer noise/rotation read as one continuous slab.
Pending added:
  - Differential rotation of arm pattern at high time compression (deferred — needs uTime-driven vertex shader)
  - Andromeda/M31 (deferred — needs extragalactic tier with separate scale ~1Mpc/WU)
  - Local Bubble cavity around Sol (deferred — physical scale falls in a "gap" between sector and outer-system tiers)
  - Per-arm asymmetric pitch (deferred — Sgr/Perseus only differ by ~1.5°, visually marginal)
Pending resolved:
  - None at the workspace level (this session was all Legion-scoped).
Project status changes:
  - Legion (13-legion): "V1 prototype seed" → "Standalone repo + galaxy visualization pass complete (22 commits, sector→arm→galaxy seamless, Powers-of-10 transitions, real-MW structural fidelity)"
Next:
  - On next Legion session, work likely shifts from galaxy-scale visualization to system-scale gameplay (factory building, RTS combat, Bob mechanics) per the original V1 scope. Or further refinement of the close-in tiers (Local Bubble, planet surface terrain).
  - The workspace's `.git` pointer on Voyager-2 needed local repointing this session (sean.sands path vs snds path mismatch). Worth a future-machine note in 08-knowledge/cross-domain/workspace-infrastructure.md if there's a portable fix.
--- END BLOCK ---

---

--- SESSION BLOCK ---
Date: 2026-05-07 (cont.)
Machine: Work MacBook Pro (main, going forward — CS-K746DRWXY1)
Surface: Claude Code (Mac desktop app)
Project(s): Workspace Infrastructure (post-migration follow-ups)
Artifacts:
  - .claude/hooks/dispatcher.py — `_ensure_executable_bits()` self-heal at session-start; HOSTNAME_MAP gains CS-K746DRWXY1 (main work laptop going forward) and annotates CS-KQ23N94M0W as the loaner
  - 08-tools/{drive-audit,drive-monitor}.py — relocated from ~/drive-sync-tools (which now holds symlinks)
  - 08-tools/README.md — usage + when-to-use for the audit/monitor scripts
  - 00-bootstrap/setup/setup-identity.sh — idempotent two-account SSH setup; generates keys, writes ~/.ssh/config, prompts for two pubkey pastes, verifies both connections
  - 00-bootstrap/setup/gitconfig{,.personal,.work}.template — global ~/.gitconfig with `[includeIf "gitdir:..."]` directory-routed identity
  - 00-bootstrap/setup/README.md — Step 4 in "Manual steps after install" now points at setup-identity.sh
  - .gitignore — selective whitelist for 08-tools (README + drive scripts only); figma-cli-main and compile-cursor-rules.py stay ignored
Decisions:
  - Self-heal over `core.fileMode = false`. Drive's exec-bit stripping is environmental, but silencing all mode tracking workspace-wide is a bigger hammer than needed. The dispatcher restores +x on tracked-100755 files instead, preserving real mode tracking for intentional changes.
  - Selective git-track in `08-tools/`. Default-ignore stays (vendor + per-machine); just whitelist drive-audit/monitor + README so cross-machine utilities have version history.
  - Symlinks at ~/drive-sync-tools/ keep the convenience path on macOS without forking the canonical version. Workspace copy is source of truth.
  - setup-identity.sh hardcodes the two GitHub identities (snds + sean-sands-centric) rather than prompting. Loaner cycles change hostnames, not identities.
  - gitconfig's includeIf routes ~/personal/** and ~/work/**. The Claude Workspace lives at ~/.git-stores/... — neither pattern catches it, so it stays on repo-local config (intentional; identity is anchored regardless of host).
Pending resolved:
  - Move ~/drive-sync-tools/ into 08-tools/ (with README + gitignore whitelist)
  - Author 00-bootstrap/setup/setup-identity.sh (idempotent two-key pattern)
  - Author ~/.gitconfig template with includeIf blocks (3 templates in 00-bootstrap/setup/)
  - Confirm dispatcher.py exec-bit fix sticks — superseded by self-healing implementation
Project status changes:
  - Claude Workspace Infrastructure: Active → Active (next-machine setup is now a single re-runnable script + self-healing dispatcher)
Next:
  - On next machine setup: run setup-identity.sh after Drive sync settles, then the workspace clone steps in 08-knowledge/cross-domain/workspace-infrastructure.md
  - Watch for whether Drive re-strips dispatcher.py mode (now self-healing logs to stderr if it does — quiet otherwise)
--- END BLOCK ---

---

--- SESSION BLOCK ---
Date: 2026-05-07
Machine: Work MacBook Pro (main, going forward — CS-K746DRWXY1)
Surface: Claude Code (Mac desktop app)
Project(s): Workspace Infrastructure (laptop migration)
Artifacts:
  - ~/drive-sync-tools/drive-audit.py — single-pass placeholder/sync audit (per-machine, outside Drive)
  - ~/drive-sync-tools/drive-monitor.py — live sync monitor; auto-exits when 0 placeholders + size stable for 2 ticks
  - ~/.ssh/config + id_ed25519_personal + id_ed25519_work — two-identity GitHub SSH alias setup
  - ~/.git-stores/claude-workspace-system/ — workspace gitdir, cloned via --separate-git-dir
Decisions:
  - Drive placeholder detection on macOS uses UF_DATALESS chflag (0x40000000); `find -flags +dataless` or os.scandir + st.st_flags & flag
  - Single-pass Python scan is required during heavy sync — bash 4-pass `find` version did not finish in 10+ min on 125K-file workspace; one Python pass took ~37 min while still syncing
  - Two-identity GitHub pattern: separate SSH key per account; `~/.ssh/config` alias (`github.com` → snds, `github-work` → sean-sands-centric); repo-local git identity, no global
  - Workspace anchors to PERSONAL identity regardless of host laptop (snds / 570874+snds@users.noreply.github.com), enforced via repo-local config in the gitdir
  - Drive strips macOS executable bits in transit (dispatcher.py mode 100755 → 100644 on this fresh laptop); `chmod +x` restores. No other tracked scripts were affected this round.
  - 99.98% of pending placeholders were in 07-projects/; system layer (00–06, 08-skills) synced fast. Bytes finished long before files (Drive prioritizes large files first).
Pending added:
  - Move ~/drive-sync-tools/{drive-audit,drive-monitor}.py into 08-tools/ now that sync is settled
  - Author 00-bootstrap/setup/setup-identity.sh codifying the two-key pattern for next machine setup (generate keys, write ~/.ssh/config, prompt for two pubkey pastes)
  - Author ~/.gitconfig with `[includeIf "gitdir:..."]` blocks for non-workspace repos that don't carry repo-local config
  - Extend 08-knowledge/cross-domain/workspace-infrastructure.md with Drive-sync-monitoring section + multi-identity GitHub section (done this session)
Pending resolved:
  - Drive sync on new main work laptop completed overnight — Obsidian no longer hangs on vault open
  - Workspace gitdir provisioned at ~/.git-stores/claude-workspace-system; remote `origin` reachable via personal SSH alias
Project status changes:
  - Claude Workspace Infrastructure: Active → Active (sync-monitoring tools + multi-identity GH pattern landed)
Deferred commits:
  - .obsidian/plugins/obsidian-excalidraw-plugin/data.json — content drift from another machine (Obsidian Git auto-backup territory); see Step 7.5 disposition
Next:
  - Move drive-sync-tools/ into 08-tools/ and add a SKILL/README pointing future-Sean at them
  - Build setup-identity.sh and ~/.gitconfig template
  - Confirm dispatcher.py exec-bit fix sticks across reboots (Drive may re-strip on next sync)
--- END BLOCK ---

---

--- SESSION BLOCK ---
Date: 2026-05-05
Machine: Work MacBook Pro
Surface: Cursor
Project(s): 05-C8-PLM (c8-plm/table-demo)
Decisions:
  - table-demo pinned to React 18 to match CDS @types/react 18.x; React 19 blocked until CDS updates declared peer types
  - tsconfig paths must map @centricsoftware/design-system → ../CDS/dist/index.d.ts; root package.json types field points at a missing file and npm overrides cannot deduplicate @types inside file: linked packages
  - Row type aliases (type T = DataTableRowType<T> & …) cause circular TS errors; correct pattern is interface T extends DataTableRowType<T>
  - PlmUnifiedTableDemo replaces four piecemeal examples with one unified CDS DataTable wiring all TanStack + CDS features in a single component
  - Row/column reorder handled at app state (drag handle + columnOrder array); CDS DataTable has no built-in columnDnD or rowDnD API
  - Matrix lane approximated with cellsMeta rowSpan/colSpan + enableSpans; group header span via GroupingConfig.spanColumns
Pending added:
  - Review PlmUnifiedTableDemo visually in browser against Figma Tables file for fidelity
Next:
  - Open browser at http://localhost:5174 and exercise all toolbar controls
  - Consider extracting textEdit/selectEdit inline-edit primitives into a shared utility for reuse
--- END BLOCK ---

--- NANO BLOCK ---
Date: 2026-05-04
Machine: Work MacBook Pro
Surface: Cursor
Context load only — no decisions or artifacts.
--- END BLOCK ---

--- SESSION BLOCK ---
Date: 2026-05-04
Machine: Work MacBook Pro
Surface: claude.ai web
Project(s): 00-obsidian, workspace infrastructure
Decisions:
  - Cursor workspace bootstrap architecture established: brain.mdc (always-on ritual), 01-agent-controller.mdc (reads open/writes Claude-only), 02-workspace-filesystem.mdc (protocol + paths)
  - MCP server named claude-workspace (not workspace-fs) to avoid Cursor built-in name collision
  - Symlink /Users/sean.sands/claude-workspace → Drive path to avoid spaces in MCP server args
  - Reads open to any model in Cursor; writes require Claude — softened from reads-also-Claude-only
  - Nano block for trivial sessions instead of skipping entirely — preserves cross-surface last-session accuracy
  - Obsidian plugin runtime files (core-plugins.json, plugins/*/data.json) removed from git tracking — auto-modified by Obsidian, not user content
  - ps-based parent process check added to surface detection — discriminates Cursor from VS Code (both set VSCODE_PID)
  - session-end SKILL.md: surface detection probe, [Machine/Surface] commit tags, Step 7.5 orphaned changes audit with attribution via git log
  - Stale worktrees deleted from 07-projects/00-obsidian/.claude/worktrees/ (5 orphaned full workspace copies)
  - compile-cursor-rules.py generates AGENTS.md from live context files; watch mode available
  - Dispatcher shim created at /projects/.claude/hooks/dispatcher.py — Cursor resolves $CLAUDE_PROJECT_DIR to /projects, shim delegates to real dispatcher
  - .cursorignore created — excludes worktree paths, archives, Obsidian internals from Cursor indexing
Pending resolved:
  - Cursor workspace bootstrap infrastructure (new)
Next:
  - Test claude-workspace MCP in fresh Cursor session — confirm both paths accessible, all 6 projects in ritual
  - Monitor /session-end duplicate in skill picker after worktree cleanup + Cursor restart
--- END BLOCK ---

---

### 2026-06-10 — Figma-repo-sync QA sweep + design-system consolidation to main

**Machine:** CS-K746DRWXY1 (unknown — not in hostname table; add if recurring)

**Projects:** Centric VMS UI (figma-repo-sync-plugin), design-system token consolidation, workspace frameworks.

**What happened:**
- Fixed the Badge `(?)` binding bug in figma-repo-sync (root cause: per-file `ensureScaffolding` churn during generate-all staled foundation aliases). Then a 6-issue QA sweep: Tabs 28M-px width clamp, orphan prune + inventory refresh, Label empty-master fix, "Property 1" axis rename, input Error-state derivation, variant spec-row. Builds 11.4.13–11.4.18 (468 tests).
- Storybook-vs-Figma visual QA pass (palette-review harness as reference + visual-qa-toolkit); per-component anatomy/props sweep across all 24 generated components.
- Consolidated tangled local/feature branches toward `main` using a new Integration & Review framework.

**Artifacts:**
- NEW `00-frameworks/07-integration-and-review-framework.md` (registered in 00-README + _FRAMEWORKS index)
- centric-ui `.qa-out/` reports (anatomy-sweep-per-component, badge-findings) + `.qa-venv`

**Decisions:**
- `main` adopts the Radix 3-tier token system wholesale (#82).
- Canonical figma-plugin lineage = the token-model branch carrying the QA fixes.
- Repo squash-merges → independent single-concern PRs (not stacked branches).
- Defer the cds→semantic sweep (context-dependent color roles; cds-* still works via #82 aliases).

**Merged to main:** #77 (grid-ssot radius — conflict resolved keep-both), #82 (3-tier tokens + Tailwind/CDS compat). Verified both survived intact in app.css.

**Open/queued PRs:** #83 (generator scripts) + #84 (plugin, incl QA fixes + .gitignore) — ready for review. #87 (caution tokens+variant) + #88 (palette-review harness, draft, stacked on #87).

**Pending added:**
- After #87 merges → retarget + rebase #88 (harness) onto `main`.
- cds→semantic full sweep — deliberate, design-reviewed, ~39 files.
- Table + EmptyState components never reached `main`; re-add their specs to the harness when they land.

**Next:** Sean merges PRs incrementally; handle rebases/retargets as they come.

---

### 2026-04-29 — Storybook + ds-docs go to GitHub: two open PRs, new private repo

**Sessions:** 1 (Work MacBook Pro — `CS-KQ23N94M0W`)
**Focus:** Took the design-system documentation work from this conversation thread (Storybook stories + Fumadocs site + content seeding) all the way to GitHub. Shipped two PRs on the centric-ui side, stood up a brand-new private repo for ds-docs, and got CI green on the inaugural ds-docs PR.

**Key decisions:**
- **Two PRs for centric-ui, sequential.** Storybook config + foundation stories first; component stories (22 + 3 feature) held until #1 merges. Cleaner review surface; standard workflow expectation.
- **ds-docs as separate private repo.** Different stack (Next.js vs Vite), different audience, different deploy. Lives at `cpes-software/ds-docs`, mirrors centric-ui visibility.
- **Branch off `origin/main`, not local main.** Local was many commits behind upstream — branching from `origin/main` picked up upstream test fixes (apiClient + keycloakService) for free and ensured PR diffs were against current.
- **Proprietary "All Rights Reserved" LICENSE for ds-docs.** Closed-source DS; no redistribution without written consent.
- **Branch protection on ds-docs `main`:** require PR + 1 approving review + linear history + conversation resolution; force-push and deletion blocked; admin bypass enabled (sole-contributor friendliness).
- **CI: `lint` + `types:check` + `build` on Node 20.** Concurrency-cancelled per ref.
- **Pin ESLint to `^9.39.3` in ds-docs.** Fumadocs scaffold pulled ESLint 10 which breaks `eslint-config-next@16` (bundled `eslint-plugin-react` calls removed APIs `scopeManager.addGlobals`, `contextOrFilename.getFilename`).
- **`ContentTabs` uses `@radix-ui/react-tabs` directly.** Fumadocs's Tabs wrapper deliberately omits `value`/`onValueChange` (groupId-based uncontrolled sync). Controlled binding to global doc mode required the primitive.
- **`DocMode` uses `useSyncExternalStore`.** Idiomatic React 18+ pattern for localStorage subscription; eliminates `setState`-in-`useEffect` (lint rule `react-hooks/set-state-in-effect`).
- **Storybook iframe theme sync via `preview-head.html` URL-globals parser.** Reads `?globals=theme:dark` from the URL and applies `.dark` synchronously before paint, plus a dark-mode `body { background: var(--sem-background) }` override to compensate for centric-ui's `@theme inline { --color-cds-gray-100 }` baking the light value. Theme-blind primitive utilities don't propagate dark overrides; dark mode only works through `--sem-*` token chain.

**Artifacts produced (cpes-software/centric-ui — branch `feat/storybook-foundations`, commit `acc8704`):**
- `.storybook/` — Storybook 10 config (main, manager, preview, preview-head)
- `app/stories/foundations/` — 7 foundation stories + `lucide-metadata.json` (1696-icon registry)
- `package.json` + lock — Storybook 10 deps, `storybook` / `storybook:build` scripts, vitest browser-mode integration, `@storybook/react` explicit (knip)
- `vitest.config.ts` + `vitest.shims.d.ts` — projects split (app tests + storybook browser tests)
- `tsconfig.json` — `.storybook/**/*` in include
- `.gitignore` — allow `.storybook/`, ignore `storybook-static/`
- 22 component stories + 3 feature stories (`alert-dialog`, `dialog`, etc. + `FileIcon`, `UploadDropzone`, `PlaceholderWidget`) — uncommitted, queued for PR #2

**Artifacts produced (cpes-software/ds-docs — new repo):**
- Initial commit `3c52630` — Fumadocs scaffold + 8 foundation MDX + 22 component MDX + 4 patterns MDX + custom blocks (`Callout`, `DoDont`, `Anatomy`, `Spec`, `PropTable`, `ContentTabs`, `StorybookEmbed`) + foundation native layouts (`ColorPalette`, `SemanticTokens`, `TypeScale`, `TypeWeights`, `TypeSpecimens`, `SpacingScale`, `RadiusGrid`, `ShadowGrid`, `ThemeTokenMap`) + `DocModeProvider` + `DocModeToggle`
- README polish `3acf41c` — replaced create-fumadocs-app boilerplate with real description (two-tool setup, content structure, custom blocks, mode toggle, dogfooding, contribution template)
- LICENSE + `.github/workflows/ci.yml` — branch `chore/license-ci`, commits `3af0e0c` and `bf24c38`

**Live PRs:**
- centric-ui #34 — https://github.com/cpes-software/centric-ui/pull/34 — Storybook setup + foundation stories — **awaiting review**
- ds-docs #1 — https://github.com/cpes-software/ds-docs/pull/1 — LICENSE + CI — **CI green, awaiting merge**

**Cross-session memory updates:**
- `~/.claude/CLAUDE.md` — added "Always link external references" operating principle (cross-cutting, all sessions). Trigger: every PR / issue / branch / workflow run / ticket / dashboard reference includes its URL.
- `~/.claude/projects/.../memory/project_ds_docs_admin_todos.md` — created. Tracks open admin items: CODEOWNERS (waiting on Sean for reviewer list), required CI status check (post-first-green), production deployment + `NEXT_PUBLIC_STORYBOOK_URL`.

**Pending added:**
- Add CODEOWNERS to ds-docs once Sean provides the reviewer list per path.
- Mark `lint, types, build` as a required status check in ds-docs branch protection (CI is now green, ready to add).
- Wire up production deployment for ds-docs (Vercel suggested) + set `NEXT_PUBLIC_STORYBOOK_URL` for embeds.
- Open centric-ui PR #2 (component stories) once #34 merges.

**Pending resolved:**
- Storybook installed and configured in centric-ui (was a long-standing TODO).
- Foundation stories live (7 + icon browser).
- ds-docs site stood up end-to-end (Fumadocs + content + mode toggle + dogfooded tokens).
- ds-docs README, LICENSE, CI, and branch protection all in place.

**Project status changes:**
- Centric Design System: "Storybook + ds-docs documented locally" → "Two PRs in flight; ds-docs is a private GitHub repo with CI + branch protection."

**Next:**
- Sean reviews ds-docs #1 and centric-ui #34. After ds-docs#1 merges, Claude marks the CI status check required via `gh api repos/cpes-software/ds-docs/branches/main/protection`. After centric-ui#34 merges, Claude opens centric-ui PR #2 with the 25 component stories.

---

### 2026-04-28 (cont.) — Phase 2 skills + 08-knowledge vault + active surfacing system

**Sessions:** 1 (Work MacBook Pro — `CS-KQ23N94M0W`, continuation across context compaction)
**Focus:** Completed Phase 2 skill hubs (lead-devops-engineer + lead-3d-designer, 14 spokes total), scaffolded 08-knowledge/ as a new vault layer, seeded it with 7 foundational knowledge entries harvested from all session/project context, then wired a three-tier surfacing mechanism so knowledge entries are read proactively, not just written.

**Key decisions:**
- **Phase 2 spoke completion via fill-in agents.** Original Phase 2 agents created directories but left 9 spokes empty. Two targeted fill-in agents wrote the missing content; the original devops agent completed asynchronously and was preferred over the fill-in for devops (fill-in stopped). 3D agent wrote 2 new spokes; 3 others were found to have already landed from the original agent.
- **08-knowledge/ as a distinct vault layer.** Skills = how-to (operational). Context = session/project state. Knowledge = what was learned from real work (durable, cross-session insights). Kept strictly separate — entries capture the *why*, not the *what to do*.
- **Three-tier surfacing system for knowledge.** (1) _INDEX.md injected into SessionStart context so Claude knows what exists at boot. (2) KNOWLEDGE_HINTS dict in dispatcher.py maps 15 trigger keywords to entry paths — fires alongside TRIGGER_WORDS skill hints on UserPromptSubmit. (3) CLAUDE.md rule requiring knowledge entry read before domain work begins.
- **session-end Step 5: harvest knowledge.** New protocol step added to /session-end skill — scans for durable learnings at close-out and creates/updates 08-knowledge/ entries before committing.
- **08-knowledge/ added to .gitignore whitelist.** Was blocked by the catch-all `*` rule; added `!08-knowledge/` + `!08-knowledge/**` so entries are tracked in git.

**Artifacts produced:**
- `02-skills/lead-devops-engineer/SKILL.md` + 6 spokes (devops-ci-cd, devops-container-orchestration, devops-observability, devops-infrastructure-as-code, devops-release-engineering, devops-cost-optimization)
- `02-skills/lead-3d-designer/SKILL.md` + 6 spokes (3d-modeling-fundamentals, 3d-materials-shading, 3d-lighting-rendering, 3d-rigging-animation, 3d-spatial-design-for-games, 3d-asset-pipeline)
- `02-skills/skills-manifest.json` — 180 → 194 skills
- `08-knowledge/_README.md` + `_INDEX.md` — vault structure + documented surfacing mechanism
- `08-knowledge/cross-domain/workspace-infrastructure.md` — Drive+Git topology, hook dispatcher, desync bug fix
- `08-knowledge/cross-domain/workflow-patterns.md` — stale-content review, 3-bucket pending, audit_skip, session habits
- `08-knowledge/design/centric-plm-design-system.md` — DS strategy, scale, Ark UI decision, token architecture
- `08-knowledge/design/centricsymbols-icon-font.md` — 4-axis variable font architecture, pipeline, COLRv1
- `08-knowledge/design/meridian-ds-prototype.md` — token system, ARIA coverage, WCAG results
- `08-knowledge/engineering/centric-plm-codebase.md` — confirmed tech stack, dual frontend, analysis structure
- `08-knowledge/game-dev/legion-architecture.md` — Three.js+WebGPU stack, V1 scope, 3D asset context
- `.claude/hooks/dispatcher.py` — KNOWLEDGE_INDEX + KNOWLEDGE_HINTS constants; _INDEX.md in SessionStart context; knowledge hints in handle_user_prompt()
- `.claude/skills/session-end/SKILL.md` — Step 5 (harvest knowledge), Step 7 git add includes 08-knowledge/, Step 7→8 renumber
- `CLAUDE.md` — Knowledge Vault section added; read-before-work rule added
- `.gitignore` — 08-knowledge/ whitelisted

**Pending resolved:**
- Phase 2 skill hubs (lead-devops-engineer + lead-3d-designer) — complete ✓
- 08-knowledge/ vault scaffolding — complete ✓
- Knowledge vault active surfacing system — complete ✓

**Project status changes:**
- Claude Workspace Infrastructure: Active — auto-commit safety + worktree-cleanup hardened → Active — knowledge vault layer live (08-knowledge/ + 3-tier surfacing system)

**Next:**
- Act on Opus 4.7+ skill audit findings (report at `04-artifacts/active/skill-network-audit_opus-4.7_2026-04-21.md`) — highest-leverage: extract ~200 lines of design theory from ds-advisor + resolve ds-advisor/design-engineer trigger overlap
- Add framework-layer pointers to 6 highest-leverage skills
- Seed `07-projects/04-claude-figma-plugin/SESSION-STATE.md`
- Build `visual-qa-toolkit` skill (dedicated session)
- Data table cell anatomy + state matrix (PLM work)

---

### 2026-04-27 (cont.) — Drive-sync hardening: dispatcher safety guard + worktree auto-cleanup

**Sessions:** 1 (Windows Desktop — `Enterprise`, continuation of earlier session)
**Focus:** After the audit-and-merge work, hardened the SessionEnd auto-commit against two failure modes that hit during the same conversation: Drive's stat-cache lying to git (phantom entries) and stale worktree checkouts diverging from HEAD. Both would have caused `git add -A` to commit fictitious deletions and corrupt main. Designed defense-in-depth around the symptom + fixed the upstream root cause that created the legacy worktree mess.

**Key decisions:**
- **Tier-1 safety guard ships first; Tier-2 (off-Drive worktrees) explored second.** Tier-3 (`core.checkStat=minimal`) included as one-liner belt-and-suspenders but explicitly *not* a failover layer — Tier-1's content-hash fallback is the actual safety net.
- **Auto-cleanup runs at both lifecycle hooks.** SessionStart (in canonical workspace root) catches the *previous* session's worktree; SessionEnd catches *sibling* stale worktrees. Combined, any merged Drive worktree disappears within roughly one session of becoming stale. Idempotent — no-op when nothing eligible.
- **Off-Drive worktrees are considered parked work; never auto-removed.** Cleanup criteria is Drive-resident + fully merged + not the current worktree. Worktrees in `~/.claude-worktrees/` are out of scope.
- **STALE_DELETION_THRESHOLD = 5.** Heuristic for stale-worktree detection. Above this, the hook assumes the working tree is out of sync with HEAD and falls back to safe-paths regardless of Drive state.
- **Tier-2 wrapper (`claude-wt`) deferred.** Manual workflow + Claude Code feature request [#28242](https://github.com/anthropics/claude-code/issues/28242) tracked. Lower priority now that the cleanup keeps Drive worktrees from accumulating.

**Artifacts produced (this session-continuation):**
- `.claude/hooks/dispatcher.py` — major hardening:
  - `_classify_worktree_state()` detects phantom git-status entries (Drive desync) + excessive deletion count (stale worktree)
  - `_content_hash_stage()` uses `git hash-object` + `update-index --cacheinfo` to bypass stat-cache when staging the safe-paths allowlist
  - `_write_desync_notice()` / `_read_desync_notice()` write+surface a notice file at `.claude/state/desync-notice.md` flagged on the next SessionStart
  - `_ensure_drive_safe_git_config()` sets `core.checkStat=minimal` + `core.trustctime=false`
  - `_cleanup_stale_worktrees()` auto-removes Drive-resident worktrees whose branches are fully merged into main
  - `_is_inside_linked_worktree()`, `_list_worktrees()`, `_branch_fully_merged_into_main()` as supporting helpers
  - `ensure_local_gitdir()` now skips `.git` pointers containing `/worktrees/` — fixes the upstream bug that broke linked worktrees by stomping their per-worktree gitdir
  - `handle_session_end()` rewritten to use the safety guard before `git add -A`
  - `handle_session_start()` runs cleanup (only when not inside a linked worktree)
  - `build_session_start_context()` + new `_format_worktree_cleanup_notice()` thread cleanup results into the SessionStart notice block
- `.claude/skills/session-end/SKILL.md` — added "Worktree auto-cleanup (informational)" section documenting the new behavior

**Commits pushed:**
- `1a65d97` — session-end log block from earlier in the conversation
- `f788b69` — Tier-1 auto-commit safety guard
- `f26e64c` — worktree auto-cleanup + `ensure_local_gitdir()` bug fix

**Pending added:**
- `claude-wt` ergonomic wrapper for off-Drive worktree creation (Tier-2 manual workflow ergonomics; deferred)
- Verify auto-cleanup actually fires on the three legacy worktrees at next SessionStart in workspace root

**Pending resolved:**
- (none — this work prevents future occurrences of the desync class of bug)

**Project status changes:**
- Claude Workspace Infrastructure: Active — audit cadence established → Active — auto-commit safety + worktree-cleanup hardened (Drive-sync class of bug closed)

**Next:**
- Open claude in canonical workspace root (`G:/My Drive/Claude Workspace/`) — first SessionStart there will auto-clean the three legacy worktrees and surface a notice
- Decide whether to ship `claude-wt` wrapper now or defer until Drive-worktree pain returns
- Resume active pending items (smoke-test installer on MBP, decide python binary strategy, act on Opus 4.7+ skill audit findings)

---

### 2026-04-27 — Workspace audit + skill-content consolidation + audit-skip mechanism

**Sessions:** 1 (Windows Desktop — `Enterprise`)
**Focus:** First `/optimize` run. Audited the brain end-to-end, then applied fixes with stale-content review pass before any archive: read-and-diff every candidate against its successor, migrate unique content into the live SKILL.md, only then archive the loose copy.

**Key decisions:**
- **Stale-content review is mandatory before archiving** — codified as Step 4a in `.claude/skills/optimize/SKILL.md`. Read both files, diff for unique sections, classify as clean-duplicate / stale-but-useful / stale-contradictory, and write a REVIEW-NEEDED.md note for anything with unique content.
- **`audit_skip: true` frontmatter flag** — workspace-wide opt-out mechanism for files Sean wants the audit to leave alone (cross-context personal references, scratch notes, drafts). New Step 1.5 in the optimize skill grep-builds the skip-list and surfaces opt-outs in the report. First user: `_CHEATSHEET.md`.
- **Style-binding content belongs in `figma-style-binding/SKILL.md` itself** — not a hub skill, not a parent. The skill name already names the topic; splitting variable-binding knowledge across multiple skills hurts discoverability.
- **Pending items restructured into three buckets** — Active (next actions), Deferred (resurface on context match), Recently resolved (prune at next /optimize). Replaces the prior 5-bucket / chronological structure.

**Artifacts produced (this session):**
- `06-context/audit-log.md` — first entry written: 9 findings (P0:1, P1:5, P2:3), 8 fixes applied, 4 carried for review, then a follow-up integration round
- `02-skills/figma-ds-generation-pipeline/SKILL.md` — Step 0 (Stack Selection), Radix Base Color Architecture (914 primitives), and Radix Semantic Scale Binding Map merged in from the loose `figma-ds-generation-pipeline.md`
- `02-skills/figma-style-binding/SKILL.md` — Effect Style binding, Node Property binding, Gradient binding workaround, Debugging section, Font loading errors merged in from the loose `figma-style-binding.md`
- `02-skills/design-engineer/SKILL.md` — line 283 reference `~/.claude/skills/ds-stack-router/` redirected to `figma-ds-generation-pipeline/SKILL.md` § "Step 0: Stack Selection"
- `.claude/skills/optimize/SKILL.md` — added Step 1.5 (audit-skip opt-out) and Step 4a (stale-content review)
- `_CHEATSHEET.md` — added `audit_skip: true` + `audit_skip_reason` frontmatter
- `06-context/project-context.md` — Pending Items section restructured into Active (9) / Deferred (5) / Recently resolved (6); _Last updated_ 2026-04-25 → 2026-04-27; "first commit pending" line corrected
- `02-skills/_archive/duplicates_2026-04-27/` — 7 loose figma .md files archived (5 strict duplicates + 2 post-merge); `REVIEW-NEEDED.md` rewritten as a "Resolved 2026-04-27" record of what migrated where
- `02-skills/_archive/_deprecated_workspace-bootstrap-updated_2026-04-21/` — moved
- `02-skills/_archive/legacy-packages/workspace-bootstrap.skill` — moved
- `_archive/Repo.md` — moved (single-line URL captured elsewhere)
- Worktree-pinned `CLAUDE.md` — added `/optimize` line to slash-command list to match root CLAUDE.md

**Pending resolved:**
- Clean up duplicate skill files at `02-skills/` root (originally pending from 2026-04-21)
- Verify Drive MCP reads GDocs as fallback on Web/iOS — closed as low-value; DC + Drive sync is the working path

**Pending added:**
- Migrate (or delete) the two loose `figma-*.md` files flagged in REVIEW-NEEDED.md → resolved same session
- Seed `07-projects/04-claude-figma-plugin/SESSION-STATE.md` (split out from the broader "seed remaining SESSION-STATEs" item; remaining seeds 03-omni, 12-MCS, 15-DavinciRemake deferred)

**Project status changes:**
- Claude Workspace Infrastructure: Active — topology stabilized → Active — audit cadence established (first `/optimize` run logged; audit-skip mechanism live; stale-content review codified)

**Next:**
- Smoke-test installer on work MBP
- Decide Python binary strategy (recommendation: standardize on `python3` + Windows shim)
- Act on Opus 4.7+ skill audit findings + framework-layer pointers (bundle into one session)
- Build `visual-qa-toolkit` (dedicated session)

**Worktree note:** This worktree's index is desync'd from `main` (Drive sync race). Many phantom `M`/`D` entries appear in `git status` for files this session never touched. Auto-commits `1ca3098` and `312ebed` already captured this session's substantive work to `origin/main`. Do not `git add -A` from this worktree — it would commit phantom deletions.

---


**Sessions:** 1 (Windows Desktop — `Enterprise`)
**Focus:** Discovered system-layer files had been moved into `07-projects/00-obsidian/` (Sean had treated the project folder as the integration itself). Restored deployed-vs-project distinction: integration deploys to workspace root where Claude Code, Obsidian, and git expect their config; project workspace holds design history only. Consolidated installer + Obsidian templates + integration architecture doc into `00-bootstrap/`. Updated path refs everywhere. Configured git identity, renamed `master`→`main`, first commit + push to GitHub.

**Key decisions:**
- **Deployment location ≠ project location.** Integration is a cross-Claude ecosystem tool. Deployed files live at workspace root (Claude Code finds `CLAUDE.md` and `.claude/` by walking parents from CWD; Obsidian identifies a vault by `.obsidian/`; git wants `.gitignore` next to `.git/`). Project folder `07-projects/00-obsidian/` holds design/state docs only — same pattern as any installable tool.
- **`00-bootstrap/` is the home for installer + integration scaffolding.** Coexists with the legacy March-bootstrap files; not renamed, not archived.
- **Track `07-projects/00-obsidian/` in git** — the only `07-projects/` subfolder tracked. Integration's design history is part of the system layer.
- **Dispatcher session-end commit simplified to `git add -A`.** `.gitignore` is now well-scoped enough to be the single source of truth (no more explicit whitelist drift).
- **Repo-local git identity:** `snds` / `570874+snds@users.noreply.github.com`. Keeps workspace identity separate from work-machine git defaults; preserves email privacy in public commit log.
- **Filter Drive virtual files** (`.gdoc`, `.gsheet`, etc.) from git — they can't be read on Windows (no real bytes; served by Drive's filesystem driver).
- **Branch `main` not `master`** for the new repo (matches GitHub default).

**Artifacts produced (this session):**
- `07-projects/00-obsidian/SESSION-STATE.md` — per-template; reflects 2026-04-23 build + 2026-04-25 restructure
- `07-projects/00-obsidian/README.md` — explains deployed-vs-project distinction; links to architecture doc
- `.gitignore` — rewritten for new layout; removed obsolete `setup/` and `templates/` un-ignores (now under `00-bootstrap/`); added `.gdoc`/`settings.local.json` ignores; added `07-projects/00-obsidian/` un-ignore
- `00-bootstrap/OBSIDIAN-SETUP.md` — directory tree + paths updated
- `00-bootstrap/setup/README.md` + `bootstrap.sh` + `bootstrap.ps1` — `YOUR-USER` → `snds`; `setup/` → `00-bootstrap/setup/`
- `.claude/hooks/dispatcher.py` — session-end commit simplified to `git add -A`
- `.obsidian/plugins/templater-obsidian/data.json` — `templates/` → `00-bootstrap/templates/`
- `CLAUDE.md`, `_HOME.md`, `_SKILLS.md` — template path references updated
- `06-context/project-context.md` — pendings marked resolved; Active Project entry updated
- `02-skills/skills-manifest.json` — auto-reconciled (1 added: `figma-mcp-tool-usage`; 4 changed: `design-system-ops`, `figma-api-pipeline`, `research`, `workspace-bootstrap`) — incidental drift, not from this session

**Pending resolved:**
- Confirm GitHub username + create `claude-workspace-system` private repo (`snds`, done)
- `git init` + first commit + push (done — 387 files, `main` branch, tracking `origin/main`)
- Seed `07-projects/00-obsidian/SESSION-STATE.md` + `README.md` (done)

**Pending added:**
- (none — this session resolved or carried existing items, didn't introduce new ones)

**Project status changes:**
- Claude Workspace Infrastructure: Active — integration layer deployed (2026-04-23) → Active — topology stabilized + first commit pushed (`main` on `snds/claude-workspace-system`)

**Next:**
- Smoke-test `00-bootstrap/setup/setup.command` on work MBP (Sean's next session)
- Decide Python binary strategy (`python` vs `python3` + Windows shim) — recommend (b)
- Document community-plugin enablement step in daily flow
- Then: act on 2026-04-21 audit findings; seed remaining SESSION-STATE files

---

### 2026-04-23 — Obsidian + Claude Code integration (vault + hooks + installer)

**Sessions:** 1 (Windows Desktop — `Enterprise`)
**Focus:** Stand up Obsidian-as-vault + Claude Code-as-CLI integration on top of the existing Claude Workspace. Reference pattern from Mibii's dev.to article, adapted to the richer existing structure (60+ skills, 5 frameworks, DC+Drive sync, multi-machine).

**Architecture decisions:**
- **Vault = workspace root.** One source of truth. Obsidian, Claude Code, and Claude Desktop (via DC) all read/write the same filesystem.
- **Two skill systems coexist by design.** `02-skills/` stays for Claude Desktop (hub/spoke, manifest-synced). `.claude/skills/` new for Claude Code slash-commands (workflow automations).
- **Hands-off via Claude Code hooks.** `SessionStart` loads context, `UserPromptSubmit` surfaces trigger words, `Stop` stages session-log changes, `SessionEnd` auto-commits + pushes. Single Python dispatcher handles all events cross-platform.
- **Sync topology: Drive + Git layered, not either/or.** Drive stays as filesystem sync (handles binaries, zero migration). Git tracks system layer only (CLAUDE.md, `.claude/`, `.obsidian/`, `00-bootstrap`, `00-frameworks`, `01-shared-references`, `02-skills`, `03-preferences`, `06-context`, MOCs, `templates/`, `setup/`). Artifacts and projects stay out of Git — scoped via `.gitignore`.
- **Installer is single-file Python (stdlib only).** Wrapped by `.command`/`.bat` double-clickables and `bootstrap.sh`/`bootstrap.ps1` one-liners. Idempotent. Downloads Obsidian plugins directly from GitHub releases.
- **Windows hostname registered:** `Enterprise` → Windows Desktop. Updated in `workspace-bootstrap` and dispatcher.

**Artifacts produced (26 new files):**
- `CLAUDE.md` (root) — Claude Code context, link-heavy, ~120 lines
- `OBSIDIAN-SETUP.md` (root) — architecture doc + troubleshooting
- `_HOME.md`, `_PROJECTS.md`, `_SKILLS.md`, `_FRAMEWORKS.md`, `_CONTEXT.md` — MOCs with Dataview queries
- `.gitignore`, `.gitattributes` — scoped tracking of system layer only
- `.claude/settings.json` — hook config
- `.claude/hooks/dispatcher.py` — cross-platform hook dispatcher (Python stdlib only)
- `.claude/skills/today/SKILL.md` — `/today` daily note
- `.claude/skills/session-end/SKILL.md` — `/session-end` protocol
- `.claude/skills/reconcile/SKILL.md` — `/reconcile` multi-machine merge
- `.claude/skills/new-project/SKILL.md` — `/new-project` scaffolder
- `.claude/skills/framework-check/SKILL.md` — `/framework-check` critique
- `.obsidian/app.json`, `appearance.json`, `core-plugins.json`, `community-plugins.json`, `hotkeys.json`, `graph.json`, `plugins-manifest.json`
- `.obsidian/plugins/obsidian-git/data.json` — 15-min auto-commit/push/pull
- `.obsidian/plugins/templater-obsidian/data.json`
- `setup/setup.py` — installer (~350 lines, stdlib only)
- `setup/setup.command`, `setup/setup.bat` — double-clickable wrappers
- `setup/bootstrap.sh`, `setup/bootstrap.ps1` — one-liner fetchers
- `setup/README.md` — install flow + troubleshooting
- `templates/daily-note.md`, `project-readme.md`, `skill.md` — Templater templates
- `02-skills/workspace-bootstrap/SKILL.md` — edited: Windows hostname set to `Enterprise`, added note about Claude Code integration

**Pending added:**
- Confirm GitHub username (currently `YOUR-USER` placeholder in setup docs) and create private repo `claude-workspace-system`
- Run `git init` + scoped first commit + push to GitHub remote
- Smoke-test `setup/setup.command` on work MBP end-to-end
- Seed `07-projects/00-obsidian/SESSION-STATE.md` capturing this build
- Decide on Python binary strategy: currently hooks call `python` (works on Windows). macOS typically needs `python3` — recommend updating `.claude/settings.json` to use `python3` and having the Windows installer create a `python3` shim via `mklink` or PATH alias
- Community plugin enablement requires user consent on first Obsidian open — document this in the daily flow

**Pending resolved:**
- Verify Desktop Commander writes to Drive folder on Windows — confirmed (this session wrote 26 files to `G:\My Drive\Claude Workspace\`)
- Windows filesystem MCP / Desktop Commander setup — complete

**Project status changes:**
- `Claude Workspace Infrastructure`: Active — framework layer just deployed → Active — Obsidian + Claude Code integration layer deployed
- New project folder `07-projects/00-obsidian/` now has its purpose (was empty); to be formally registered in `project-context.md` next session on Mac

**Next:**
- Open this work on work MBP (`seansands.local`); Drive should have fully synced by then
- Answer GitHub username question; run `git init` + create + push private repo
- Double-click `setup/setup.command` to smoke-test the installer
- Seed `07-projects/00-obsidian/SESSION-STATE.md` and `README.md` registering the project in `_PROJECTS.md` MOC

---

### 2026-04-21 — Framework migration + audit + workspace extension

**Sessions:** 1 (Work MacBook — `seansands.local`)
**Focus:** Framework token audit, migration into `00-frameworks/`, skill network reference audit, Opus 4.7+ skill audit report, new framework-layer docs (README, team-practices, session-state template), `workspace-bootstrap` extension, per-project SESSION-STATE.md seeding, context-log refresh.

**Context:** This log is sparse between 2026-03-07 and today. Substantial work occurred in the interim (framework drafts, skill architecture shift to demand-driven loading, manifest reconciliation, multiple Figma plugin threads, CentricSymbols pipeline work, Legion development). Today's session is the first log entry since the March bootstrap checkpoint; earlier sessions either didn't write to this log or did so in GDoc_4 only. `project-context.md` has been refreshed alongside this entry to reflect current reality.

**Key decisions:**
- Framework numbering stable at 01–05. Future additions extend the sequence (06, 07…) or trigger a fresh migration session.
- Preservation-biased token audit validated: drafts were already well-edited; 0.6% reduction across 1,358 lines was the honest yield.
- `team-practices-and-decisions.md` lives in `00-frameworks/` (not as a framework, but as team-specific overlay referenced by Last-Mile Craft).
- `SESSION-STATE.md` lives per-project in `07-projects/[project]/SESSION-STATE.md`. Template spec in `00-frameworks/_session-state-template.md`.
- `workspace-bootstrap-updated/` directory archived as `_deprecated_workspace-bootstrap-updated_2026-04-21` (not deleted per the "preserve identity, never destroy" principle).

**Artifacts produced:**
- `00-frameworks/00-README.md` — orientation + compressed summaries (176 lines).
- `00-frameworks/01-aesthetic-lens.md` through `05-last-mile-craft-framework.md` — migrated + renamed + lightly audited.
- `00-frameworks/team-practices-and-decisions.md` — four-layer scaffold (193 lines).
- `00-frameworks/_session-state-template.md` — per-project operational state spec (174 lines).
- `00-frameworks/_migration-audit-notes_2026-04-21.md` — full audit log of what was cut, considered, preserved.
- `04-artifacts/active/skill-network-audit_opus-4.7_2026-04-21.md` — Opus 4.7+ audit report (203 lines).
- `02-skills/workspace-bootstrap/SKILL.md` — extended with framework awareness, SESSION-STATE.md loading, Write 5 at session end.
- `07-projects/13-legion/SESSION-STATE.md` (seed).
- `07-projects/14-variable-icon-font-generator/SESSION-STATE.md` (seed).
- `07-projects/02-centricPLM/SESSION-STATE.md` (seed).
- `07-projects/10-centric-UX-research/SESSION-STATE.md` (seed).
- `06-context/project-context.md` — full refresh reflecting current reality.

**Pending added:**
- Seed remaining active projects with SESSION-STATE.md (03-omni, 04-claude-figma-plugin, 12-MCS, 15-DavinciRemake per Sean's call).
- Act on Opus 4.7+ skill audit findings (5 prioritized items; highest-leverage is the ds-advisor extraction).
- Add framework-layer pointers to 6 highest-leverage skills (pattern documented in audit report).
- Clean up duplicate skill files at `02-skills/` root.
- Populate `team-practices-and-decisions.md` active layer as decisions surface.
- Build `visual-qa-toolkit` skill (dedicated session).
- Formally delete `_deprecated_workspace-bootstrap-updated_2026-04-21` if Sean confirms.

**Pending resolved:**
- Install workspace-bootstrap v3.1 skill. (Skill is current; no separate install needed.)

**Next:**
- Visual-QA-toolkit build in a dedicated fresh session — explicitly scoped separately per yesterday's handoff.
- Skill-network audit action pass is a separate follow-up (not urgent, but high-leverage).

---

### 2026-03-07 — Bootstrap check (session 2)

**Sessions:** 1 (Personal MacBook)
**Focus:** Session bootstrap only — no work completed

**Decisions:**
- role-and-context.md is missing from 06-context/ — needs to be created

**Pending added:**
- Create role-and-context.md in 06-context/

---

### 2026-03-07 — Workspace Architecture v3.0

**Sessions:** 1 (Personal MacBook)
**Focus:** Workspace bootstrap architecture redesign

**Key decisions:**
- Desktop Commander is available in Claude Desktop Chat — can read/write `.md` files
  to local Drive folder directly; Drive for Desktop syncs to all machines
- This replaces the Drive MCP read-only limitation entirely for Desktop environments
- Architecture: DC primary (read+write `.md`) → Drive MCP GDocs (fallback) → snapshot
- GDocs retained as read-only fallback mirrors for Web/iOS sessions
- Reconciliation workflow added: Session Blocks → end-of-day merge → DC writes result

**Artifacts produced:**
- `workspace-bootstrap-v3.0.skill`
- `GDoc_1_Preferences.md`, `GDoc_2_Role_and_Context.md`
- `GDoc_3_Project_Context.md` → replaced by `project-context.md`
- `GDoc_4_Session_Log.md` → replaced by `session-log.md`

**Pending added:**
- Install workspace-bootstrap v3.0
- Verify DC write access on all three machines
- Move `.md` context files into `06-context/` in Drive workspace

---

_[Entries added above this line by Claude via Desktop Commander]_
