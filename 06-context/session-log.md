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





# Shapr3D MCP setup

SessionID: 2026-09-14-shapr3d-mcp-setup
Date: 2026-09-14
Agent · Surface · Machine: GPT-6 · Codex desktop · Work MacBook Pro
Context profile: personal-solo, explicitly declared by Sean.
Project home: temporary name `Projects/shapr3d-personal`; final project concept/name pending reference. No numbered vault project allocated yet.

## Live handoff

- Installed Alfredoalv13/shapr3d-mcp revision `88fcefe` in the sibling Projects checkout with frozen uv dependencies.
- Registered `shapr3d` globally using the Codex CLI; read-back confirms enabled. Project config alone was not loaded by this parent task. Native tool refresh requires restart; real MCP client connection tested successfully.
- All 30 upstream tests pass. Generated test plate STEP + STL; independent mesh topology, 60 × 40 × 8 mm bounds, and analytic volume checks pass (0.00205% volume error).
- Sean installed and launched Shapr3D during the session. The server app bridge opened the STL; Computer Use observed the imported plate with four holes and captured the app window.
- Evidence and portable setup notes: `Projects/shapr3d-personal/README.md`, `validation.json`, `models/shapr3d_stl_import.png`, and reproducible smoke script.
- Upstream executes unrestricted Python. Screenshot tool falls back to entire display; prefer app-targeted Computer Use. STEP is editable-solid interchange, without feature history; STL is a mesh.
- Next: receive visual reference and dimensions; establish final project identity, create versioned models, and inspect in Shapr3D. STEP app import and app-side measurements remain unverified.
- No employer repository modified. No conceptual design work started.

# Custom desk reference intake

SessionID: 2026-09-14-custom-desk-references
Date: 2026-09-14
Agent · Surface · Machine: GPT-6 · Codex desktop · Work MacBook Pro
Context profile: personal-solo.

## Live handoff

- Sean is designing a custom desk, desktop first. Primary Pinterest form plus upper platform atop main desktop like Aero; exclude Hex Desk side extensions.
- Source references and decisions are in `Projects/shapr3d-personal/DESIGN-BRIEF.md`.
- Native Shapr3D MCP tools now callable. Imported `HEXADesk-Main.SLDPRT` successfully in Shapr3D. Exported STEP copied from Documents to project models as `hexadesk_main_reference.step`; MCP reads one solid, 2046.458 × 895.562 mm plan, 25.4 mm thickness (source Y-up).
- Original SolidWorks files preserved in project reference directory. Shelf part and complete assembly remain untested.
- Pinterest sign-in required in the in-app browser; asked Sean to sign in. Primary pin image and board not yet visually assessed. Asked for dimensions and platform equipment.
- Next: complete reference review, inspect shelf, agree dimensions, then desktop/platform study. No custom design generated yet.

# Custom desk dimensions and mounting concept

SessionID: 2026-09-14-custom-desk-materials
Date: 2026-09-14
Agent · Surface · Machine: GPT-6 · Codex desktop · Work MacBook Pro
Context profile: personal-solo.

## Live handoff

- Sean confirmed 71.93 × 29.92 inches overall desktop envelope, hardwood likely American walnut, thickness open. Magnetic ferrous underside for 3D-printed dock/KVM/accessory cradles; organization shelf with probable laptop arm; black straight and custom curved T-slot rail idea for LG ultrawide and Audioengine speakers.
- Pinterest access now works. Visually inspected both specific pins and board overview. Sustema main form has an angled wraparound outline and central seating recess. Do not claim whole-board review or generated fidelity.
- Updated `Projects/shapr3d-personal/DESIGN-BRIEF.md` with source links, proposed construction logic, verified/provisional hardware envelopes, and explicit unknowns. `desktop-parameters.json` records exact footprint and null values for undecided dimensions.
- Full rectangular 1 mm steel sheet estimated 24 lb; smaller panels proposed, not approved. Wood-movement allowances needed. Magnet capacity requires physical stack testing. Structural rail must not rely on thin sheet for arm loads.
- Live Humanscale M21BJTBC configurator shows black 8-inch/8-inch links, standard tilt, 100 mm VESA and clamp; successor M2 Pro wording. Notebook holder not selected. Native SolidWorks import and STEP conversion verified in prior entry.
- Asked whether standing or fixed base, and slim versus substantial edge. Answers pending. No custom geometry generated or final thickness selected.
- Next: use answers to develop desktop/platform layout, then fit equipment with actual revision/adapter/cable clearances. Curved rail fabrication and load ratings remain unverified. No purchase or supplier communication performed.

# Custom desk base and rail research

SessionID: 2026-09-15-custom-desk-base-rail
Agent · Surface · Machine: GPT / Codex desktop / Sean's Mac
Context: personal-solo

Sean confirms existing Humanscale laptop holder and clearance work; do not reopen that question. Prefer complete Aero standing-base reuse, but documented replacements are acceptable. Custom longitudinally bent black T-slot rail is selected in principle; investigate specifications and pricing rather than segmented alternatives. Smaller thin steel panels are accepted, with broad flexible coverage for frequently changing magnetic modules.

Working files remain outside the portable workspace in Projects/shapr3d-personal. Updated DESIGN-BRIEF.md and desktop-parameters.json; added BASE-AND-RAIL-PLAN.md. Downloaded and visually reviewed relevant Aero assembly drawings in reference/aero-es71-assembly.pdf: bolted complete base appears reusable, but mounting dimensions and revision-specific payload remain unverified. DeskHaus Apex Pro provides a documented fallback ($925 observed configuration, advertised 600 lb lifting capacity); actual interface fit remains pending. Alubend advertises one-off extrusion bending; prepared quotation requirements, no supplier contacted or custom price obtained.

Next: desktop/platform concept with provisional thickness and shelf dimensions, steel coverage zones and frame clearance. Thickness, recess, shelf dimensions and rail radius remain open. No new custom desk CAD produced in this research pass. MCP installation/test and native SolidWorks-to-STEP reference conversion were completed in prior sessions.



### 2026-09-15 — Automation second wave: A4, A5, A9 applied; A8 stays blocked

SessionID: 2026-09-15-work-mbp-automation-wave2
--- SESSION BLOCK ---
Date: 2026-09-15
Machine: Work MacBook Pro (main, going forward)
Surface: Claude Code (Mac desktop app)
Agent: Claude Opus 5
Project(s): 19-workspace-brain

Summary: Phase 6 — closed the remaining automation candidates from the 2026-09-11 review.

A5 (ruff): measured the blast radius before wiring anything. Defaults return 143 findings,
`E,F` returns 402 (395 of them line-length). Selected `E9`/`F`/`I` only — 7 errors, all
auto-fixed — and excluded BLE001/S110/S112/PLW1510 because fail-open and manual returncode
checks are the contract here, not sloppiness. Declared in `ruff.toml` so local and CI agree.
It caught its own author within the hour (two F541s in the new A9 lint).

A9 (`validate-evidence-grades.py`): any report using the evidence-grade vocabulary 3+ times
must declare the legend and name a re-runnable detector. One real violation
(`agent-load-miss-review.md`) fixed. `--strict` adds pre-registration fields but only on
two distinct experiment signals — the first cut fired on `process-rigor-gaps` because
"experiment" appears there as a trigger word in a routing table.

A4 (`nightly.py`): the recipe's executable form — fold → rebuild → verify → watch → commit
(opt-in, allowlisted paths, refuses on a red tree). Python not `.sh`, because portable-first
is a core rule and the fleet includes Windows. Nothing is scheduled.

A8 stays blocked and is stated as such: it needs a Figma produce that cannot refuse `Color/*`,
and manufacturing one would be theater.

Two new candidates from measurements the first review did not have. C1 (applied):
1,443 trigger terms, 92 claimed by >1 skill — 67 benign (same chain), 25 cross-chain, now a
harness check with a ceiling of 25 rather than fail-at-zero. C2 (queued, not built):
`06-context/artifact-registry.md` is 6,942 tokens, the largest recurring cost after AGENTS.md
itself, and it is a structural INDEX — the same shape already fixed for the skill registry and
_INDEX. A retrieval CLI plus a read-order change is real work; queued with the number attached
(~28% of the 21.7k session floor) rather than half-built at session end.

19 harness gates, all green. 48/48 matcher cases, 14/14 trajectories, vault-health 0/0, ruff clean.

Report: `07-projects/19-workspace-brain/reports/automation-second-wave_v1.0_2026-09-15.md`
Decision: `[[decision-lint-narrow-or-not-at-all]]`
--- END BLOCK ---

### 2026-09-15 — C2: the artifact registry moves behind a CLI; session floor down 32%

SessionID: 2026-09-15-work-mbp-artifact-retrieval
--- SESSION BLOCK ---
Date: 2026-09-15
Machine: Work MacBook Pro (main, going forward)
Surface: Claude Code (Mac desktop app)
Agent: Claude Opus 5
Project(s): 19-workspace-brain

Summary: `06-context/artifact-registry.md` cost 6,942 tokens and CLAUDE.md read-order item 4
told every agent to read it — the largest recurring item in the session floor after AGENTS.md
itself. It is a structural index, and the same fix was already applied twice in this workspace
(skills.registry.json → skill-loadset.py; _INDEX.md → knowledge-hints + server-side parsing)
and simply left standing in a third place.

Built `09-tools/artifact-find.py`: terms search name/path/group/purpose with name hits
outranking prose, plus `--path`, `--list`, `--json`, `--limit`. Measured: reading the file is
6,942 tokens; `--list` (the whole map) is 575; a real query is 100. A no-match points at
vault-retrieve rather than returning empty, because a bare "no results" invites the agent to
conclude nothing exists.

`--check` is half the tool — a retrieval layer whose source drifts starts missing SILENTLY,
which is worse than the whole-file read it replaced. It verifies every entry is parseable,
has a Purpose to match on, a YYYY-MM-DD to age against, and a unique name. Live: 36/36
complete. It runs in CI and in /session-end step 4, right after the step that writes the file.

Contract changed in four places (CLAUDE.md item 4, AGENTS.md item 9, _CONTEXT.md, /optimize
step 7 — where a whole-file read stays correct and is annotated as the one legitimate caller).
Harness model updated only AFTER the contract, so the number followed the cost rather than
leading it.

Result: session floor 21,697 → 14,778 (−31.9%), worst-case legal request 62,110 → 55,191.
Locked three ways: session_floor budget lowered 25,000 → 17,000 so a revert (21,720) fails CI;
a self-test asserting the ceiling sits in that gap, verified non-vacuous by raising it to
99,000 and watching the test fail; and an `avoided_by_retrieval` line so the 6,942 stays
visible instead of vanishing from the accounting.

21 harness gates green, connections 8/8, every budget met, 48/48 matcher cases, 14/14
trajectories, vault-health 0/0, ruff clean.

Not done, and stated: this does not shrink AGENTS.md (7,691) or user-preferences.md (2,331) —
both are always-on content rather than indexes, so the same trick does not apply. And the
budget catches a reverted contract, not a model that ingests the file anyway.

Report: `07-projects/19-workspace-brain/reports/artifact-retrieval_v1.0_2026-09-15.md`
Decision: `[[decision-indexes-are-queried-not-read]]`
--- END BLOCK ---

### 2026-09-15 — Surface trajectories: three Layer-0 matchers collapsed to one

SessionID: 2026-09-15-work-mbp-trajectories
--- SESSION BLOCK ---
Date: 2026-09-15
Machine: Work MacBook Pro (main, going forward)
Surface: Claude Code (Mac desktop app)
Agent: Claude Opus 5
Project(s): 19-workspace-brain

Summary: Phase 5 of the review prompt. Found three independent Layer-0 implementations —
`prompt_route.py` (Cursor), a fork inside `dispatcher.py` (Claude Code), and a copy inside
`evaluate-skill-routing.py` (the 48 fixtures). The fixtures tested the copy, so neither live
surface was under test by anything. Ran the same 48 utterances through both real entry
points: 6 divergences (12.5%). Cursor had no Layer-1 lexical fallback (contract-documented,
so non-compliance rather than difference); the Claude fork deduped knowledge hints by trigger
instead of by target and silently dropped them. Both wrong, opposite directions. That is the
"Cursor didn't find the skill" complaint, reproduced.

Collapsed to one matcher instead of patching two into agreement: ported Layer 1 into
prompt_route, made handle_user_prompt delegate, made evaluate-skill-routing import
term_matches. Re-measured: 0 divergences.

Built `09-tools/evaluate-surface-trajectories.py` — executes each surface's real entry point
(claude-code hook, cursor hook, shell-agent via skill-loadset, hookless adapters asserted
statically), asserts expect/forbid paths, headers, silence, and hook-surface PARITY, plus a
structural one-matcher guard so re-forking fails CI for every utterance, not only corpus
ones. `--self-test` plants a divergence and asserts parity fails on it. 14 cases.

Unification immediately surfaced its own cost: a bare status-note payload began appearing on
non-work utterances on both surfaces at once. Fixed with a general rule (a payload of nothing
but parenthetical notes is noise) which preserves the visible miss for work verbs; two
fixtures now hold it.

Wired: CI, the workspace-harness quality lane (17 gates), AGENTS.md enforcement chain, the
self-improve close-out row, five Layer-0 routes. All three harness lanes green; 48/48 matcher
cases; 14/14 trajectories; vault-health 0/0.

Not proven, deliberately: that a model *reads* what it receives. Injection is not compliance;
that needs real-session outcome data, not fixtures.

Report: `07-projects/19-workspace-brain/reports/surface-trajectories_v1.0_2026-09-15.md`
Decision: `[[decision-one-matcher-per-workspace]]`
--- END BLOCK ---

### 2026-09-15 — Workspace harness: reachability + traversal cost become detectors

SessionID: 2026-09-15-work-mbp-harness
--- SESSION BLOCK ---
Date: 2026-09-15
Machine: Work MacBook Pro (main, going forward)
Surface: Claude Code (Mac desktop app)
Agent: Claude Opus 5
Project(s): 19-workspace-brain

Summary: Adversarial second pass over the 2026-09-11 first-wave automation, run against the
live tree rather than the report. Found `main` CI-red in two places, both introduced by the
pass that added the gates: an unindexed knowledge entry (`plain-language.md`) and a
clock-dependent fixture in `test-validators.py` that was green only on its authoring day.
Found four Layer-0 routes naming a file that does not exist, a `status: canonical` doc
(`model-routing.md`) with zero inbound edges and zero routes, ten knowledge entries indexed
but matchable by nothing, one skill (`github-guardrails`) reachable by nothing, a
`vault-health.py` link resolver that could not resolve any note→skill edge (keyed on stem;
every skill is `SKILL.md`), and `vault-health.py` itself wired into no gate. Sixteen defects,
all fixed.

Built `09-tools/workspace-harness.py` — stdlib-only, read-only, clock-free. Three lanes:
quality (runs the enforcement chain, reimplements nothing), connections (seven graph checks
nothing else performs — Layer-0 target resolution, skill reachability, hub-chain ascent,
registry paths, knowledge routability, `_INDEX` link resolution the way `prompt_route.py`
resolves it, named-detector existence), tokens (contract floor 10,305 · session floor 21,656 ·
load set p50/p95/max 7,877/12,261/20,057 · worst-case legal request 62,069 · banned ingest
87,154 = 1.4× the legal worst case). `--self-test` proves each check can fail.

Two modelling corrections the vault forced: reachability is three grades, not two (141
hub-prose spokes are reported, never failed — failing them every run would kill the detector);
the chain invariant is subsequence, not prefix and not the tier enum (sub-spokes are legitimate
topology). Attach points so it is not another unused script: CI (`--self-test` then
`--connections --tokens`, plus `vault-health.py`), the AGENTS.md enforcement chain,
`close-out-dispatch.py` under a new `self-improve` row (`rigor_role: command-hub`), and seven
Layer-0 routes.

All three lanes green; routing corpus still 48/48; vault-health 0/0.

Not covered, deliberately: phase 5 (per-surface routing trajectories — the harness proves the
graph is traversable, not that a given model traverses it) and phase 6 (A4/A5/A8/A9 remain
open). Nothing here touches the visual/Figma lane.

Report: `07-projects/19-workspace-brain/reports/workspace-harness_v1.0_2026-09-15.md`
Decision: `[[decision-reachability-is-a-detector]]`
--- END BLOCK ---

### 2026-09-14 — Canvas live-mirror + employer repo dest

SessionID: 2026-09-14-work-c4nvx
--- SESSION BLOCK ---
Date: 2026-09-14
Machine: Work MacBook Pro
Surface: Cursor
Agent: Cursor Grok 4.6 / Cursor / Work MBP
Project(s): 19-workspace-brain
Summary: Harvest was writing git copies only, so Recents in this checkout still pointed at parent `~/Projects` canvases. `cursor-externalize.py` now mirrors vault canvases into `…-workspace/canvases/` and copies company canvases into that repo's `canvases/` (never this vault). Mixed-parent `flavours-` / `guided-setup-` moved into saas-plm-prototype.
Decisions:
  - Employer canvases dual-home in the owning `cpes-software/*` checkout's `canvases/`, not skip-and-drop.
  - Flavours / Guided Setup belong in saas-plm-prototype (design sandbox), not workspace-brain.
Evidence:
  - Live mirror @ `~/.cursor/projects/Users-sean-sands-Projects-workspace/canvases/` — verified (7 `.canvas.tsx`)
  - Employer copies @ `cpes-software/cds/canvases/` and `cpes-software/saas-plm-prototype/canvases/` — verified on disk, untracked; no employer commit (centric-engineering)
Next:
  - Open employer PRs for untracked `canvases/` in cds + saas-plm-prototype (do not auto-commit)
  - First-wave leftovers: A8 Figma bind probe, A4 nightly.sh without cron, A5 ruff, A9 analysis lint
  - Human merge cds #35 onto `main` (do not merge from an agent)
  - Open Engine residue not filed — Linear MCP absent on this Cursor session
--- END BLOCK ---

### 2026-09-11 — Plan-ahead + cds export gate

SessionID: 2026-09-11-plan-ahead-export-gate
--- SESSION BLOCK ---


### 2026-09-10 — PlanetCompiler controlled histories and connected globe

SessionID: 01a08bae-ad4a-7dc1-bfb2-f6d79fdd25fe
--- SESSION BLOCK ---
Date: 2026-09-10
Agent: Codex
Surface: Codex desktop
Machine: Personal Mac, Apple M3 Max
Project(s): PlanetCompiler; independent Planet Lab scoped handoff
Summary: Resumed the authorized native handoff. Implemented five prescribed spherical material-strip histories with versioned recipes and material/age ledgers, then connected the standalone Release compiler to bounded asynchronous Unreal MCP tools. Completed independent science and native lifecycle reviews and corrected the defects found. Debug/Release each passed 3/3 CTest suites and 65/65 independent checks, including eight planted defects; 9/9 native tests and 59 live MCP checks passed. Built and inspected an interactive evidence page using actual outputs. Human acceptance and all global-planet/visual claims remain pending. No Legion files changed.
Commits: PlanetCompiler a3cc5f0, 86ea71f, 2b470bf; local-only repository with no remote configured.
Next: Review the completed native phase-two diagnostic, then specify the bounded regional surface/hydrology model before phase 3. Preserve original high-resolution references, adversarial visual gates, and all Legion work.
Handoff: 07-projects/13-legion/docs/planet-lab-independent/SESSION-STATE.md
Follow-up: design-hook finding fixed in PlanetCompiler a0d35bf by removing a decorative side border. Browser, scoped detector and evidence-integrity checks passed; no suppressions or unresolved findings.
Phase-two follow-up: Sean approved the connected globe. Integrated spherical finite-volume core, per-birth-plate material transport, explicit supported/unresolved ledgers, native diagnostic globe and real scheduled playback. Debug/Release 5/5 core suites, 78/78 independent global checks with 13 planted corruptions, 65/65 strip regression; clean native 12/12, global MCP534, strip MCP59 and actual Slate controls8/8 passed. Six final captures were independently inspected. Preserved hot-reload, debug-overlay, stopped-playback and first-black-frame observations; corrected confirmed defects, retained unconfirmed first-use anomaly and model/rendering limits. Human acceptance remains pending. No phase 3 or Legion edits.
Phase-two commits: da88d1b, e801aa3, 342ecc7, 39071e7, 797e48f and 29744d6 (final evidence checkpoint); implementation repo remains local-only.
--- END BLOCK ---

### 2026-09-09 — Cursor employer-repo Layer-0 routing

SessionID: 2026-09-09-work-prompt-route
--- SESSION BLOCK ---
Date: 2026-09-09
Machine: Work MacBook Pro
Surface: Cursor
Project(s): 19-workspace-brain (from a cds Figma generate miss)
Summary: Semantic + theme/mode token binding already lived in design-engineer / figma hub / figma-ds-surface-authoring but did not fire in Cursor-on-cds. Gap: no beforeSubmitPrompt injection, curated `figma` route skipped the hub + token gate, vendor figma-use was MANDATORY, snds-local omitted the figma hub, wrapped YAML triggers iterated as letters. Fixed with shared prompt_route.py, user-global beforeSubmitPrompt, FIGMA_GENERATE_ROUTE, expanded triggers/hard gates, parser + plugin 0.3.1.
Evidence:
  - Knowledge: [[cursor-employer-repo-skill-routing]]
  - Decision: [[decision-cursor-prompt-route-hook]]
  - Smoke (cds cwd): `figma` → FIGMA_GENERATE_ROUTE HARD GATE; ack prompts emit `{}`
Next:
  - Restart Cursor once so hooks.json reload is certain
  - `claude plugin install snds@snds-local` (or restart) to pick up `/snds:figma` 0.3.1
  - Resume cds Wave 1 token rebind (primary-soft) after this routing fix
--- END SESSION BLOCK ---

SessionID: 2026-08-31-cds-consolidation
--- SESSION BLOCK ---
Date: 2026-08-31
Machine: Work MacBook Pro
Surface: Cursor
Agent: Claude Opus 5 / Cursor / Work MBP
Project(s): cds (was ds-docs), centric-ui, saas-plm-prototype (employer — `centric-engineering`)
Summary: Started the CDS consolidation — making `cpes-software/cds` the single DS write surface
so the system versions independently of its consumers. Strategy is mirror-gate-flip over a
deliberate dual-source period rather than a move: cds receives the DS by copy while
centric-ui stays authoritative, with a CI parity gate that fails on divergence. Four PRs
opened; centric-ui deliberately untouched.

Four structural findings, each now documented in-repo rather than in agent memory:
  - `cpes-software/ds-docs` was ALREADY renamed to `cpes-software/cds` on GitHub; only the
    local checkout and remote URL were stale.
  - CDS has never contained a `.storybook` on any branch or in any history — the two-tool
    README describes an iframe at localhost:6006 into centric-ui. Moving Storybook is part
    of the migration, not a precondition.
  - The semantic token layer is NOT in `@centric/tokens`. `@theme` + the whole `--sem-*`
    family live in `centric-ui/app/app.css` (852 lines), so the packages are visually
    self-insufficient. Three drifting copies: 852 / 479 / 307 lines across centric-ui, cds,
    proto. Generated palette drifted too (1722 in package vs 1724 in both consumers).
  - The prototype had NO DS pin. Its sync script short-circuits on a sibling checkout, so it
    silently consumed `feat/figma-regen-idempotency@0004f572` — a NON-ANCESTOR of main,
    43 commits short, missing `empty-state`/`statusTone`/`viewTransitions`. Fixed first.

Durable technique learned (worth a knowledge entry if it recurs): `git rev-parse <branch>`
resolves the LOCAL branch, which in a multi-worktree setup is routinely stale — always prefer
`origin/<ref>`. This bit twice in one session: it is the root cause of the prototype pin bug,
and my own parity manifest first recorded a 43-commit-stale sha for exactly the same reason.
Also: `secrets` is unavailable in a step-level GitHub Actions `if`, so a condition testing it
silently never matches — map to a job-level `env` first, or a gate quietly passes unchecked.

Decisions taken (Sean, this session):
  - Phase-one distribution stays vendor symlink + `file:` deps (proven in proto); registry
    publishing + build step deliberately deferred as the riskiest, non-essential change.
  - Repo identity `cds`; plain copy with provenance recorded, not history grafting.
  - Review scope: CDS mirror + Storybook + proto flip; centric-ui untouched this pass.

Evidence:
  - cds#4 plan · cds#5 workspaces+apps/docs · cds#6 packages mirror+parity gate (CI green)
  - saas-plm-prototype#57 pin guard (CI green)
  - cds#3 retargeted from the already-merged `chore/license-ci` to `main` so it is reviewable
  - Plan: `cds/docs/plans/2026-08-31-cds-consolidation-plan.md`; provenance:
    `cds/packages/{MIGRATION.md,ds-source.json}`
Next:
  - OPEN DECISION for Sean: the semantic split (PR C) needs the layer extracted from
    centric-ui's app.css. Write-surface rule says it lands upstream first; the agreed scope
    says centric-ui is untouched. Recommended resolution is additive — author
    `packages/tokens/semantic.css` in cds, add a `cdsOwned` exclusion to `ds-source.json`,
    and gate it with an extraction-faithfulness check so the temporary 4th copy is verified
    rather than trusted. Not started pending Sean's call.
  - Then PR D Storybook move (depends on C), then proto PRs F (flip to cds) and G (consume
    `@centric/tokens`, delete drifted copies, with qa/ A/B evidence).
  - Set repo secret `CENTRIC_UI_READ_TOKEN` on cds to bring the parity gate to full strength;
    without it only the offline mirror-integrity half runs (annotates a warning, does not
    silently pass).
  - cds#4/#5 are ungated until the broadened CI `pull_request` trigger in #6 lands.
--- END SESSION BLOCK ---

## 2026-09-09 — Independent Planet Lab prototype and adversarial evidence

SessionID: 01a08930-3c92-7ca0-ba45-7c9a4088ddb8
Agent · Surface · Machine: Codex / Codex desktop / personal Mac, Apple M3 Max

Sean requested an additive, completely isolated planetary-generator attempt inside Legion. Created `~/Projects/Legion/planet-lab/` with an independent WebGPU/vgpu application, own package and local Git repository. Isolated commit `b057dc1` on `codex/independent-planet-lab`. Existing Legion files and dirty work were left alone.

Implemented reduced plate kinematics and bathymetry, climate and habitation fields, evolving moisture transport, volumetric clouds and internal lightning emission, camera-relative Earth-scale rendering and continuous 19,000 km orbital insertion to 8 m terrain clearance. Nine numerical tests, native shader validation and seven browser integration checks passed. Actual 1920×1080 motion/stills, optional GPU timestamps and practical-quality timing runs were recorded.

Independent native-resolution review against inspected NASA/NOAA originals remains FAIL. Documented coarse coast geometry, terrain bands/moire, insufficient surface and cloud morphology, stylized city patterns and coarse lightning glow. Physical models remain explicit approximations. Highest-quality full-HD rendering misses the p95 target in some views; Balanced at 1632×918 passed five fixed views (8.8–9.2 ms p95), but a descent window reached 17.9 ms. Sustained 60 fps, full-HD and other GPUs remain uncertified.

Durable scoped baton: [[07-projects/13-legion/docs/planet-lab-independent/SESSION-STATE]]. Code-local README, NORTHSTAR, VISUAL-REVIEW, BUDGET and PRODUCTION-PATH hold the source provenance, test evidence and next architecture. Recommended native candidate is Unreal, with independent causal world-generation data; no native port or deployment performed.

## 2026-09-10 — Isolated Unreal development environment verified

Sean requested setup and resumed after OS permissions required a Codex restart. Created the separate personal-solo `~/Projects/PlanetCompiler` repository, branch `codex/planet-compiler-environment`, local commit `b5f2f90`. Installed Epic Launcher/UE5.8.2, Xcode26.1.1 build17B100, Metal17B54, CMake4.3.4 and Ninja1.13.2. Sean completed sign-ins and accepted the Xcode agreement. Global developer-tools selection remains CommandLineTools; native scripts set Xcode per process.

Portable C++20 Debug and Release tests pass2/2 each. Native editor host compiles, loads and opens. Official ModelContextProtocol + AllToolsets expose52 toolsets on127.0.0.1:8765. Initialize, discovery and read-only current-level query pass, including after the final restart. UE5.8.2 returns blank serverInfo metadata; discrepancy is retained in the smoke report. Disabled unused Android deployment plugin and excluded its autogenerated credential from source.

Evidence and startup instructions are in native README and evidence/setup-report.json. Native repo remains local, clean and independent; Legion sources were not modified. The visible terrain is Unreal’s default starter level, not generated by PlanetCompiler. Native causal geology, streaming renderer and portable-core adapter remain next implementation. Open PlanetCompiler as its own trusted Codex project to load its scoped MCP configuration.

Date: 2026-09-11
Machine: Work MacBook Pro
Surface: Cursor
Project(s): 19-workspace-brain; saas-plm-prototype (#77); cds (#35)
Summary: Workspace now prints a numbered order of operations before executing. Proto `cds-exports-check` gates `@centric/ui/<subpath>` against cds `origin/main` so overlay-ahead cannot hide a Pages fail. Breakers that were invisible: Toaster (`./sonner`) and SplitDragHandle after cds #34 squash.
Evidence:
  - Skill: [[plan-ahead]]
  - Knowledge: [[cds-host-consume-order]]
  - Decision: [[decision-plan-ahead-order-of-operations]]
Next:
  - Merge cds #35, then proto re-export Toaster / SplitDragHandle / ChipMultiSelect
--- END SESSION BLOCK ---

### 2026-09-03 — Figma opacity variables: UI yes, MCP layer-only

SessionID: 2026-09-03-figma-opacity-variables
--- SESSION BLOCK ---
Date: 2026-09-03
Machine: Work MacBook Pro
Surface: Cursor
Project(s): Centric SaaS PLM Design System (`o6o1ZuGHxDow2vHLuYXT6X`); workspace knowledge
Summary: Figma 2026-09-03 “Control opacity at scale” lets the UI bind a number var to color-variable + fill opacity without detaching. MCP `use_figma` / `node.set` is the Plugin API — layer opacity binds work (FLOAT 0–100); paint and color-var opacity writes reject. Applied `Opacity/*` + `opacity/{disabled,scrim,hover,focus,pressed}` and bound Components masters.
Evidence:
  - Knowledge: [[figma-opacity-variables]]
  - MCP re-probe: Button `State=Disabled` (`7:5060`) `get_variable_defs` → `"var(--opacity-disabled)": "50"`; `setBoundVariableForPaint(..., 'opacity')` → Expected 'color'; `node.set` same unrecognized `boundVariables.opacity`
Next:
  - Re-bind Overlay Black/White ramps as alias+opacity when paint/color-var writes ship
  - Do not split Radix A-steps / `interaction/*`
--- END SESSION BLOCK ---

### 2026-08-12 — Proto is the design sandbox (don't strip screens)

SessionID: 2026-08-12-proto-sandbox-model
--- SESSION BLOCK ---
Date: 2026-08-12
Machine: Work MacBook Pro
Surface: Cursor
Project(s): saas-plm-prototype, centric-ui (employer)
Summary: Sean corrected the migration reading: never delete prototype screens because centric-ui already has the page. Proto is Olga+Sean design iteration; consume `@centric/*`; lift net-new into centric-ui.
Evidence:
  - Workspace: [[decision-proto-is-design-sandbox]], pc-05 note, [[feedback-expand-acronyms]]
Next:
  - Inventory proto-only components/composites not in `@centric/ui` and lift those (ChipMultiSelect #290 already open)
  - Catalogue lives on [[decision-proto-is-design-sandbox]]; refresh when a lift lands
--- END SESSION BLOCK ---

> _Older entries archived to [session-log-archive.md](session-log-archive.md) to keep this file cheap to read. Ask to see it only if you need history._


---

### 2026-09-04 — vgpu default + conversation-driven 3D extensions

SessionID: 2026-09-04-voyager-vgpu3d
--- SESSION BLOCK ---
Date: 2026-09-04
Machine: Personal MacBook Pro
Surface: Cursor
Project(s): 19-workspace-brain
Summary: Made vgpu the project-agnostic web GPU default; wired optional 3D MCPs (chisel, maige-3d, Godot, Unity, AgentBridge) as conversation- and living-spec-driven extensions, not standing servers. Also landed concurrent Intent #17 / intent-run.py work already in the tree.
Artifacts:
  - 03-skills/vgpu-webgpu/SKILL.md
  - 03-skills/web-3d-extensions/SKILL.md
  - 08-knowledge/engineering/web-3d-runtime-stack.md
  - 06-context/memory/decision-vgpu-default-web-3d.md
  - 00-bootstrap/templates/cursor-mcp-3d-extensions.json.example
Decisions:
  - New web GPU/WGSL defaults to vgpu; existing Three (Legion) stays on the adapter
  - Extensions are driven by ordinary conversation, research, revision, and living-spec steps; MCP is execute-time preflight only
  - Standing Cursor MCP keeps vgpu HTTP; editor/CSG servers stay project/session scoped
Pending resolved:
  - none (pc-NN unchanged)
Next:
  - Intent GUI: add a local repo, then a real coordinator spec — or personal:SEA-33
  - Reload Cursor MCP if vgpu tools are missing
--- END BLOCK ---


### 2026-09-04 — ShadeGraph: research + scaffold a node-based shader design tool

SessionID: 2026-09-04-voyager-sg21a
--- SESSION BLOCK ---
Date: 2026-09-04
Machine: Personal MacBook Pro
Surface: Claude Desktop (Code tab)
Project(s): 21-shadegraph (new) · 13-legion (integration target)
Summary: Researched vgpu.sh + the Codrops "Prism with vgpu" article + industry node-based shader editors (Unreal Material Layers, Unity Shader Graph, Substance, Blender node-preview, Nuke viewer-per-node, litegraph/ComfyUI, React Flow). Traced Legion's real shader architecture (GLSL chunks + uniforms + per-archetype lab-store — already a de-facto node system). Chose the stack, scaffolded a standalone tool repo, and wrote a comprehensive design plan.
Artifacts:
  - ~/Projects/ShadeGraph/ — new standalone repo (commit 50abc6a): model/compiler/nodes/preview contracts, React app shell, Legion adapter plan
  - 07-projects/21-shadegraph/docs/DESIGN-PLAN.md — research synthesis, stack decision, data model, phased roadmap
  - 07-projects/21-shadegraph/{SESSION-STATE.md, README.md}
Decisions:
  - Stack: React + React Flow 12 (editor shell) + one shared Three/WebGPU preview renderer + pluggable compiler. Rationale: preview fidelity ⟂ node-editor framework — fidelity is owned by compiler+renderer (previews run the real target program), scale by keeping GPU work off the DOM. litegraph/canvas is the documented escape hatch.
  - Compiler targets both backends from day one: glsl-es (drives Legion now) + wgsl/tsl (WebGPU/vgpu future).
  - Home: standalone repo ~/Projects/ShadeGraph (snds/*, own git); vault 21-shadegraph holds docs/baton only (portable-first, like Legion).
  - Vault folder allowlisted in .gitignore (docs-only) so the design plan syncs cross-device.
  - **Workspace project-tracking policy clarified (Sean):** project CONTEXT (reference/guidance/intent/curated media/docs) is tracked for BOTH personal and work projects; NEVER tracked = company/app code or checked-out repos (live in their own repos: centric-ui, prototype, ~/Projects/*) and sensitive customer data (never in the workspace at all — kept with the employer repo). The gate is content-type (context vs code/repo/customer-data), not personal-vs-employer. Encoded as exclude patterns in .gitignore under "07-projects tracking policy".
Evidence:
  - ShadeGraph initial commit @ ~/Projects/ShadeGraph (git log 50abc6a, tree clean) — verified
Pending added:
  - ShadeGraph Phase 1 (graph MVP): pnpm install, wire React Flow shell to store, starter node set + inspector + JSON save/load
  - Resolve 4 open design calls (name; state lib; WGSL-via-emitters vs TSL-as-IR; Legion live-bridge vs export-only) — DESIGN-PLAN §11
Project status changes:
  - 21-shadegraph: (new) → Building (Phase 0 scaffold + design plan complete)
Migration done this session (vault content → correct homes):
  - 03-omni: relocated ~/Projects/Workspace/07-projects/03-omni → ~/Projects/omni; fresh git; new PRIVATE repo github.com/snds/omni (pushed, commit 22c3527). Vault folder now a tracked context pointer stub (allowlisted). node_modules/target excluded.
  - 13-legion/Video (455MB Homeworld 2 frame reference) → moved to ~/Desktop/Legion-Reference-Media/Video (staging). Tracked pointer added: 06-context/external-media-registry.md. Legion vault folder 462MB→6.9MB. Awaiting Sean's durable large-format storage destination.
  - 12-MCS: empty on this (personal) machine + target employer repo unreachable from snds account. Content/access live on the WORK laptop. Queued as cross-device action: playbook in 07-projects/12-MCS/SESSION-STATE.md (SESSION-STATE tracked; folder body deliberately NOT `**`-allowlisted so work-laptop customer data can't leak into the workspace repo) + pending item ^pc-44 (machine-gated, work laptop). Sean authorized PR+commit+merge to saas-plm-analysis (doc-only employer repo).
  - ShadeGraph: PUBLIC repo created + pushed → github.com/snds/shadegraph.
Next:
  - Phase 1 per DESIGN-PLAN §10 — begin graph MVP in ~/Projects/ShadeGraph
  - [WORK LAPTOP] execute ^pc-44 — MCS → saas-plm-analysis migration (see 12-MCS SESSION-STATE).
  - Remaining backfill (deferred, per-folder triage): 02-centricPLM + 11-lexical-react-native hold employer code checkouts; relocate/scrub before any tracking. Other personal folders (04,08,09,14,15) can be triaged + allowlisted for context. Update 08-knowledge/cross-domain/workspace-infrastructure.md tracking table when done.
--- END BLOCK ---


---
SessionID: claude-web-2026-09-03-model-routing
Agent: Claude Sonnet 4.6
Surface: claude.ai (web)
Machine: Voyager-2.local
Date: 2026-09-03
Branch: main
Commit: 23788ee
---

## Summary

Local LLM setup and workspace model routing infrastructure session.

## What happened

- Debugged Ollama setup on M3 Max (36GB): EOF on model pulls traced to invalid
  tag names from third-party guides (not a connectivity or disk issue); resolved
  by using `ollama run gemma4` without explicit tag suffix
- Mapped open-source model recommendations to specific work contexts (DS work,
  code, reasoning, comms, Legion creative) across the local Ollama roster
- Created `02-shared-references/model-routing.md` — new canonical shared reference
  covering Ollama, Claude, Cursor, and Codex surfaces; native-first model roster
  per surface; work context → model map; effort tiers 1–4; speed signals
- Added 13 trigger phrases to `trigger-routes.json` for model selection vocabulary
  (which model, pick a model, best model for, model routing, ollama model, local
  model, cursor model, codex model, grok or claude, effort tier, etc.)
- Regenerated `trigger-routes.md` via `build-trigger-routes.py`
- Confirmed dispatcher.py loads trigger-routes.json dynamically — no hook changes needed
- Confirmed Cursor brain.mdc already reads trigger-routes.md at session start — no rule changes needed
- All validators green (validate-links, validate-capabilities, validate-workspace)
- Committed and pushed to github.com/snds/workspace main (23788ee)

## Pending

- No new pending items from this session
- GitHub MCP not surfaced in claude.ai session despite being installed; used git
  via Desktop Commander instead — consider verifying GitHub MCP connector state

## Notes

Filesystem MCP (read/write at /Users/snds/Projects) + Desktop Commander both
available this session — used both successfully. Web surface confirmed write-capable
via Desktop Commander when workspace is on local disk.


### 2026-09-03 — Looney consolidation + dump-folder cleanup

SessionID: 2026-09-03-voyager-b7191a1
--- SESSION BLOCK ---
Date: 2026-09-03
Machine: Personal MacBook Pro
Surface: Cursor
Agent: Cursor Grok 4.6
Project(s): 01-mediaservices
Summary: Closed the Aug 26 Looney Tunes thread. Quality adjudication + consolidation put the show in one Sonarr folder (1,062 files). The Orville, Firefly, and 12 Monkeys dump twins were resolved the same way. 16 empty leftover folders were deleted. One incident: 184 intended Looney upgrades were destroyed after ffmpeg `.part` writes failed and a graveyard sweep ran anyway.
Artifacts:
  - Unraid `/mnt/user/appdata/media-sentinel/loudness/` — adjudication-report, consolidation journal/manifest, lost-upgrades.json, three-report, cleanup-journal, looney/orville profiles
  - MediaSentinel grouping/parse + tests (year-seasons, S00 specials, yearless-into-sole-year merge)
  - `07-projects/01-mediaservices/SESSION-STATE.md`
Decisions:
  - Winners go to the Sonarr-managed folder; dump/orphan folders delete only when empty of video
  - Temp ffmpeg outputs must set `-f`; destructive sweeps gate on zero errors
  - Review pair decisions before deleting losers (broken once on Orville S01, outcome still defensible)
Pending added:
  - Optional Sonarr re-grab of 184 lost Looney upgrades
  - Firefly E03/E11 Italian-only; E10 may be mislabeled (Objects in Space / War Stories)
Pending resolved:
  - User decision on Looney loudness path (dedupe-to-managed executed)
  - Duplicate dump folders for Looney, Orville, Firefly, 12 Monkeys
  - Empty leftover folder sweep
Project status changes:
  - 01-mediaservices: Aug 26 server work complete; next is `personal:SEA-34` (Desktop Pokémon → Unraid)
Next:
  - `personal:SEA-34` — copy Desktop Pokémon pack to Unraid; set TheTVDB (DVD); do not leave Horizons in 1997 Season 20
--- END BLOCK ---


### 2026-09-03 — Library CUT delete + Desktop Pokémon organize

SessionID: 2026-09-03-voyager-mslib1
--- SESSION BLOCK ---
Date: 2026-09-03
Machine: Personal MacBook Pro
Surface: Cursor
Agent: Cursor Grok 4.6
Project(s): 01-mediaservices
Summary: Closed a long MediaSentinel / Unraid library thread. Library-wide English-watchable duplicate ranking produced 2,327 CUT videos; Sean authorized live delete of those losers plus their sidecars only. Plex TV and Emby TV were scanned. Desktop ColdFusion Pokémon pack was reorganized in place to TVDB DVD seasons; it was not copied to Unraid.
Artifacts:
  - 07-projects/01-mediaservices/canvases/duplicate-scan-outcome.canvas.tsx — scan 20260816T214110-ab8d81
  - 07-projects/01-mediaservices/canvases/authoritative-delete-list.canvas.tsx — 2,327 CUT list
  - Unraid `/mnt/user/appdata/media-sentinel/exports/` — delete lists + result JSON
  - Desktop ColdFusion Pokémon pack — 1,299 videos renamed into show/season folders
  - 08-knowledge/engineering/pokemon-tvdb-dvd-vs-aired.md — DVD vs aired + production-number trap
Decisions:
  - Delete CUT extras only; keep KEEP / PRESERVE / singletons; companions of the losing video only
  - Unlink on disk (space back), not same-fs quarantine, after explicit authorization
  - Do not whisper-overwrite MST3K S6+ community `.en.srt`; copy sidecars onto tracked obfuscated files instead
  - ColdFusion `02x28`-style codes are production numbers; map Pokémon via folder context + TVDB DVD
  - Plex/Emby must use TheTVDB (DVD) for Pokémon (1997) {tvdb-76703}; default aired now maps S20 to Horizons
Evidence:
  - 2,327 videos + 5,369 sidecars unlinked; 0 listed videos remaining; 917.7 GiB @ Unraid `/mnt/user/data/media/tv` — verified
  - Plex TV section 1 refresh HTTP 200; Emby TV Recursive ValidationOnly HTTP 204 — verified
  - 1,299 Desktop Pokémon videos moved/renamed; leftover non-video only — verified
Pending added:
  - `personal:SEA-34` land organized Desktop Pokémon pack on Unraid with TVDB DVD order
Pending resolved:
  - Authoritative CUT list for run `20260816T214110-ab8d81`
  - User-authorized delete of that list + TV library scans
  - Desktop Pokémon pack season/folder organize
Project status changes:
  - 01-mediaservices: Aug 16–17 library reclaim done; Aug 26 Looney/Orville/Firefly/12 Monkeys outcome unchanged; Desktop Pokémon ready to copy
Next:
  - `personal:SEA-34` — copy Desktop Pokémon pack to Unraid and set TVDB DVD order
  - Optional leftovers stay in SESSION-STATE (Sonarr Looney upgrades, Firefly E03/E11/E10, Bazarr missing-sub keepers, MST3K S04E01 sidecar)
--- END BLOCK ---


### 2026-09-03 — LCARS pack catalog + live T3 compose

SessionID: 2026-09-03-voyager-t3ds1
--- SESSION BLOCK ---
Date: 2026-09-03
Machine: Personal MacBook Pro
Surface: Cursor
Agent: Cursor Grok 4.6
Project(s): 20-lcars-generative-interface
Summary: Built a pack catalog (primitive → variant → component → content group → layout) and recomposed the live T3 demo from composers. App landed on `main` as `e691dec` (not pushed). S-SYS47-01 Literal stays a separate switch.
Artifacts:
  - github.com/snds/LCARS `e691dec` — `src/catalog/system/` + `docs/COMPONENT-SYSTEM.md` + composed `live-t3`
  - vault `07-projects/20-lcars-generative-interface/docs/content-groups.md` — `support.controls` + variants note
Decisions:
  - Work in vectors / grammar, not per-pixel plate overlay
  - Pills are controls; spine is bars; aesthetic is barcode + hairline
  - 8px inside a family, 24px between content groups
  - T1/T4 stay recipes; T2 stays on the SYS47 literal path
  - Do not construct chrome from `public/northstars/S-SYS47-01/*.png`
Evidence:
  - App commit `e691dec` @ github.com/snds/LCARS main (local, not pushed) — verified
  - Scene emit `generate-display-svg.py --check` 122 live primitives — verified
  - vitest 65/65 @ LCARS — verified
  - Agent Todo `personal:SEA-33` @ linear.app/snds — verified
  - Ledger heartbeat `sean-cursor` @ personal:SEA-6 comment `1d0d5fc1` — blocked (approval pending)
Pending added:
  - `personal:SEA-33` review structured live T3 against the pack catalog
Pending resolved:
  - Live T3 was a flat primitive bag; now composed from the pack catalog
Project status changes:
  - 20-lcars-generative-interface: live generative path has a named catalog; Literal path unchanged
Next:
  - `personal:SEA-33` — review `?surface=live` against the pack catalog
  - Push app `e691dec` only if Sean asks
--- END BLOCK ---

### 2026-09-03 — Onori rails absorb + LCARS off-system lint

SessionID: 2026-09-03-voyager-onori1
--- SESSION BLOCK ---
Date: 2026-09-03
Machine: Personal MacBook Pro
Surface: Cursor
Agent: Cursor Grok 4.6
Project(s): 19-workspace-brain, 20-lcars-generative-interface
Summary: Assessed Sanity/Onori design-system-evals (not previously in vault). Absorbed transferable rails: isolation (`assistance off`), pack recipes, product-repo lint. Generalized LCARS capture into workspace `vqa capture`; retired `prove_sys47.py`. Added reusable `09-tools/eslint-off-system` and wired LCARS `npm run lint`.
Artifacts:
  - 08-knowledge/design/agent-output-rails.md — Onori method without cloning the tester
  - 03-skills/visual-prove-engine/scripts/capture.py + capture.mjs — project-agnostic URL→PNG+manifest
  - 09-tools/eslint-off-system/ — shared no-raw-hex + no-arbitrary-tailwind rules
  - github.com/snds/LCARS `a133bb4` — off-system ESLint + TOKENS-wired schematics + capture wrapper
  - workspace `8024215` — Onori absorb commit (ahead of origin until this session-end push)
Decisions:
  - Do not clone sanity-labs/design-system-agent-tester; workspace path is capture→prove→score
  - Isolation law: docs/catalog proves record `--assistance off`; assistance on is shipping not score
  - ESLint lives in product repos; vault owns reusable rules + doctrine only
  - Pack wrappers may pass URL/out; they must not reimplement the capture manifest
Pending added:
  - centric-ui / Davinci off-token Tailwind lint (employer PR path)
Pending resolved:
  - Sanity design-system-evals source assessment gap
  - LCARS had no ESLint / off-system gate
Project status changes:
  - 19-workspace-brain: agent-output rails + vqa capture + eslint-off-system landed
  - 20-lcars-generative-interface: capture via workspace vqa; `npm run lint` green (65 tests)
Next:
  - `personal:SEA-33` — review `?surface=live` against the pack catalog (from prior fragment)
  - Optional: centric-ui off-token Tailwind lint via employer PR path
  - Push LCARS `a133bb4` only if Sean asks (app already ahead)
--- END BLOCK ---


### 2026-09-03 — ATSMATRIX GitHub org review, skip

SessionID: 2026-09-03-voyager-c0aba2
--- SESSION BLOCK ---
Date: 2026-09-03
Machine: Personal MacBook Pro
Surface: Cursor
Agent: Cursor Grok 4.6
Project(s): 19-workspace-brain
Summary: Reviewed all 11 public repos under github.com/anyel1to (ATSMATRIX). Account is a two-week demo mill of GitHub Pages canvases. Sean agreed skip; nothing adopted.
Decisions:
  - Do not clone, skill, or knowledge-entry the ATSMATRIX set unless Sean later asks for a fake-agent-demo pattern note
  - AGENT RING architecture prose overlaps existing doctrine (state not transcripts, second reader, receipt before ship); our open-agent-engine / mission-fit / error-correction stack already owns it
  - Canvas HUDs with Math.random plus LangGraph/CrewAI name-drops are visuals, not harnesses
Next:
  - No Agent Todo from this review
  - Separate session: LCARS live-primitive visual review (not this thread)
--- END BLOCK ---


### 2026-09-02 — Open Engine enroll, visual-qa prove, branch prune

SessionID: 2026-09-02-voyager-oe9k2
--- SESSION BLOCK ---
Date: 2026-09-02
Machine: Personal MacBook Pro
Surface: Cursor
Agent: Cursor Grok 4.6
Project(s): 19-workspace-brain
Summary: Enrolled Open Engine personal lane on this Cursor (`linear-personal` → `hello@snds.design` / `linear.app/snds`). Loaded imaging+game then visual-qa packs; ran prove path (no Legion feature work). `vqa calibrate` 48/48 after fixing relative `--output` double-join (`7a40df5`). LCARS S-SYS47-01 v4 re-prove 16/16 measured, 4 named uncued residuals. Pruned merged leftover branches on personal `snds/*` clones.
Artifacts:
  - 05-artifacts/active/vqa-calibrate_v1.0_2026-09-02.md — planted-defect calibrate 48/48 (gitignored local)
  - 06-context/open-engine/personal.md — Stage 2 2026-09-02 + status operational
Decisions:
  - Domain pack is job-context constitution load, not a replay of git housekeeping
  - Visual-qa prove this session, not Legion Continuum
  - Relative `--output` on `vqa calibrate` must resolve; interact must not re-prefix existing paths
  - Prune only ancestry-merged (or squash leftover of a merged PR) personal branches; keep unique unmerged work
Evidence:
  - Open Engine personal lane @ Cursor `linear-personal` / linear.app/snds Stage 2 — verified
  - vqa calibrate 48/48 @ vqa/1.1 after relative-output fix — verified
  - LCARS S-SYS47-01 v4 `vqa prove` 16/16 measured, capture verified — verified
  - Patch `7a40df5` @ github.com/snds/workspace main — verified
  - Branch prune @ snds/workspace, davinci, legion, LCARS — verified
  - Ledger heartbeat `sean-cursor` @ personal:SEA-6 comment `1d0d5fc1` — verified
Pending resolved:
  - Open Engine personal lane not-registered on Voyager-2.local Cursor (doctor now `ok`)
Project status changes:
  - 19-workspace-brain: Open Engine personal lane operational on this machine; visual-qa pack exercised
Next:
  - Pick new work. Do not start Legion Continuum in a housekeeping thread.
  - Optional leftovers (not filed): Davinci `feat/three-way-contract` post-merge beacon commit; Davinci `chore/sync-design-system-*`; Legion `feat/scale-unification` (closed PR #149)
  - Engine: no new Agent Todo (existing ^pc-NN queue stands). First Cursor ledger comment is `sean-cursor` on personal:SEA-6.
--- END BLOCK ---


### 2026-09-02 — Legion Continuum commit, PR #17 merge, copilot integrity skip

SessionID: 2026-09-02-voyager-k8m2n
--- SESSION BLOCK ---
Date: 2026-09-02
Machine: Personal MacBook Pro
Surface: Cursor
Agent: Cursor Grok 4.6
Project(s): 13-legion (Legion repo), 19-workspace-brain
Summary: Committed remaining Legion Continuum WIP (unified accept harness, per-archetype lab store, rocky QA). Resolved workspace PR #17 conflicts (mode-first §8e + QA adversarial default as #7); GitHub merged it. Skipped vendored `copilot/` example wikilinks in integrity so vault notes stay gated.
Artifacts:
  - Legion `064e363` — feat(planet): unified accept harness, per-archetype lab store, rocky Continuum QA
  - Legion `4bee94c` — docs/canvases Continuum + fly-to-surface (prior in this thread)
  - Workspace PR #17 merged `9221e54` — §8e + QA #6 system-context + #7 adversarial
  - Workspace `b62058d` — validate-integrity skips `copilot/` only
Decisions:
  - Legion capture dumps (`refs/`, `.tmp-*`) stay local; gitignored
  - Integrity skip is `copilot/` only — not `.claude/skills/` wrappers, not `03-skills/` / `08-knowledge/`
  - PR #17 took current `project-context` / `session-log` from main (June pending list would have overwritten `^pc-NN`)
  - `compact-sessions.py` now strips leftover archive-pointer blockquotes so they do not stack
Evidence:
  - Legion Continuum WIP @ github.com/snds/legion `064e363` on main — verified
  - Workspace PR #17 @ github.com/snds/workspace `9221e54` — verified
  - Integrity skip @ github.com/snds/workspace `b62058d` on main — verified
Pending added: none
Pending resolved: none
Next:
  - Register Open Engine personal lane on Voyager-2.local (`python3 00-bootstrap/doctor/linear-lanes.py`)
  - Refresh Obsidian graph (orphans off)
  - Domain pack on real work, or `python3 09-tools/ds-source-watch.py --fetch`, or `vqa prove`
--- END BLOCK ---

