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



### 2026-09-15 — vault CI green after Layer-0 brain-root fix

SessionID: 2026-09-15-work-n3p8r
--- SESSION BLOCK ---
Date: 2026-09-15
Machine: Work MacBook Pro
Surface: Cursor
Agent: Cursor Grok 4.6 / Cursor / Work MBP
Project(s): 19-workspace-brain
Summary: Follow-up after lint:ds session-end — committed leftover canonical-docs housekeeping, then fixed GitHub Actions workspace-integrity (Cursor trajectory self-test empty because `resolve_brain_root` ignored cwd/CLAUDE_PROJECT_DIR). HEAD `9178aaf` integrity + fixtures green.
Artifacts: none new (CI + docs already on main)
Decisions:
  - `resolve_brain_root` must consider CLAUDE_PROJECT_DIR, cwd, and parents so a clean GHA checkout of snds/workspace routes without ~/.claude/workspace-brain-path
  - Layer-0 handback routes must not name gitignored `06-context/side-chat-inbox.md` (clone-invisible; harness now treats gitignored paths as missing)
Pending resolved:
  - canonical-docs-voice leftover (title-description + YAML block-list triggers) committed as `c69baef`
  - workspace-integrity Cursor trajectory self-test on Actions — fixed `9178aaf`, confirmed green
Evidence:
  - workspace-integrity success @ https://github.com/snds/workspace/actions/runs/34994953678 — verified
  - validator-fixtures success @ https://github.com/snds/workspace/actions/runs/34994953629 — verified
Next:
  - Human review of cui #398; after merge remove centric-ui-lint-ds
  - Later: wave 2 shadcn rules; CDS theme reset; proto pre-commit lint:ds; ratchet paydown
--- END BLOCK ---

### 2026-09-15 — lint:ds overlay land + session-end

SessionID: 2026-09-15-work-k7m2q
--- SESSION BLOCK ---
Date: 2026-09-15
Machine: Work MacBook Pro
Surface: Cursor
Agent: Cursor Grok 4.6 / Cursor / Work MBP
Project(s): 19-workspace-brain; cds; centric-ui; saas-plm-prototype
Summary: Stand up `09-tools/shadcn-lint/` as an independent product-repo lint service; install `lint:ds` on cds (baseline 0), proto (ratchet 5410, merged), cui (ratchet 988, in review). Outstanding-item lists are numbered and unblocked-first.
Artifacts:
  - 09-tools/shadcn-lint/ — overlay + probe + host configs + ratchet (whitelisted in .gitignore)
  - 08-knowledge/engineering/shadcn-lint-token-tiers.md
  - 06-context/memory/decision-shadcn-lint-independent-service.md
Decisions:
  - Overlay-first; do not fold @shadcn/lint into vault CI or eslint-off-system
  - Wave 1 errors = no-raw-colors + ds-lint/no-tier-leakage only
  - CDS packages baseline 0; cui/proto ratchet existing debt
  - Theme reset is a later product-CSS PR
Evidence:
  - cds #41 merged @ https://github.com/cpes-software/cds/pull/41 — verified
  - proto #81 merged; Pages on main succeeded @ https://github.com/cpes-software/saas-plm-prototype/pull/81 — verified
  - vault overlay `51e7859` + merge `f446cbb` pushed to snds/workspace main — verified
  - cui #398 CI green, REVIEW_REQUIRED @ https://github.com/cpes-software/centric-ui/pull/398 — verified
Deferred commits:
  - 03-skills/canonical-docs-voice/SKILL.md — pending, not this overlay (stash: canonical-docs leftover)
  - 08-knowledge/design/canonical-documentation.md — pending, not this overlay
Next:
  - Human review of cui #398; after merge remove centric-ui-lint-ds
  - Later: wave 2 shadcn rules; CDS theme reset; proto pre-commit lint:ds; ratchet paydown
--- END BLOCK ---

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





### 2026-09-15 — A8 third node: R2's premise demonstrated, `wght` settled as a true positive

SessionID: 2026-09-15-work-mbp-probe-wght
--- SESSION BLOCK ---
Date: 2026-09-15
Machine: Work MacBook Pro (main, going forward)
Surface: Claude Code (Mac desktop app)
Agent: Claude Opus 5
Project(s): 19-workspace-brain

Summary: Third live node, probed to settle whether the raw variable-font weight axis (`wght`)
was a true positive or an artifact of Figma echoing a resolved axis. Settled: true positive,
and the same data proves R2's underlying premise.

The decisive evidence is a natural experiment, not an argument. A 15px focus-ring radius
appears in node 1 as the BARE property `radiusRing: 15`, with no focus-ring token anywhere in
that node's map; it appears in node 3 as the TOKEN `focus-ring-radius/md: 15`, with no bare
key. One concept, one value, two nodes — bare where unbound, token where bound. If bare keys
were echoes of bound properties, node 3 would show both; it shows one. So a bare key can be
trusted to mean unbound, which is the assumption R2 rests on and had not previously been
tested.

Applied to `wght`: node 1 reports 400 while its only weight token is `font-weight/medium: 500`;
node 2 reports 461 against tokens 500 and 600. Neither value exists as a token in its own map,
so neither can be an echo. Node 3 reports 400 alongside `font-weight/normal: 400`, which is
coincidence — 400 is Regular. Likely cause worth naming: the `ligature/*` entries show this
file uses variable ICON fonts, which carry their own `wght` axis; `var(--icon-size)` is bound
and the icon weight axis is not, which also explains node 2's otherwise odd 461.

Also confirmed on node 3: the rebuilt property-name discriminator holds — `foreground` passes,
and the Figma-only construction tokens (`Day/top-left` and siblings, sanctioned by doctrine
rule 0) pass as tokens. No metadata was supplied for this node and the probe correctly
reported `verified: R1, R2` only, declining to claim R3 rather than implying a clean tree.

Three nodes now: node 1 eight R2 hits, node 2 one, node 3 five. R1 clean on all three — the
hard gate has not over-fired once on real production work.

CONCURRENCY: the Cursor `@shadcn/lint` work is still in-flight and uncommitted in this tree,
with its routing fixture red and `trigger-routes.md` drifted. This commit again contains only
the probe files.
--- END BLOCK ---

### 2026-09-15 — A8 over-fire test: a second node rebuilt the R2 discriminator

SessionID: 2026-09-15-work-mbp-probe-overfire
--- SESSION BLOCK ---
Date: 2026-09-15
Machine: Work MacBook Pro (main, going forward)
Surface: Claude Code (Mac desktop app)
Agent: Claude Opus 5
Project(s): 19-workspace-brain

Summary: Sean asked for a second node specifically to check whether R2 over-fires. It did,
immediately, and the fix is the more valuable half of A8.

The separator-based discriminator flagged `foreground` — a real single-word semantic token,
sitting among `surface/popover` and `chrome/border/subtle` with a `var(--sem-muted-foreground)`
CSS twin. Flagging it would have told a designer to bind something already bound.

Three attempts, each failing on live data the previous one had not seen: "a token has a
slash" flagged doctrine's own `space-0` / `radius-none` / `border-width-0`; "a token has a
separator" flagged `foreground`; the rule that holds is **"the key names a Figma/CSS
property"**. Token names are unbounded and system-specific; property names are a closed,
stable set. Keying on the open set was the error, and the tell was in the first node all
along — it was full of bound fills and produced no colour-valued bare key, because unbound
values only ever surface under a property name.

After the rebuild: node 2 reports 1 hit (was 2), node 1 still reports 8 (unchanged).
Precision up, detection unweakened.

R3 also gained live vocabulary: real trees use `symbol` / `instance` / `slot` / `frame` /
`text`, and a `slot` nested inside an instance must not reset instance context or every icon
vector in a composed overlay would be flagged. Pinned by self-test.

Open, stated: both nodes report a raw variable-font weight axis (`wght`) at different values
while named weight tokens exist in the file. Consistent and probably genuine — if Figma
merely echoed a resolved axis, node 2's would match its bound weight token, and it does not.
Not rounded up to certain.

Generalised into [[decision-capture-and-assess-split]]: when writing a discriminator,
enumerate the closed set, never the open one.

CONCURRENCY NOTE: a Cursor session (Grok 4.6) landed `@shadcn/lint` work in this same tree
mid-session — new routes, knowledge-hints, `_INDEX`, `09-tools/shadcn-lint/`, and a baton
rewrite. Its `shadcn-lint-service` routing fixture is currently RED and `trigger-routes.md`
has drift; both belong to that in-flight work, not to this. This commit deliberately contains
only the probe files, so their work is left untouched in the tree for them to finish. I
corrected one stale line in their baton rewrite (it still said the probe had only seen
synthetic fixtures).
--- END BLOCK ---

### 2026-09-15 — A8 live validation: real MCP output corrected the probe twice

SessionID: 2026-09-15-work-mbp-figma-probe-live
--- SESSION BLOCK ---
Date: 2026-09-15
Machine: Work MacBook Pro (main, going forward)
Surface: Claude Code (Mac desktop app)
Agent: Claude Opus 5
Project(s): 19-workspace-brain

Summary: Closed the gap left by the A8 fragment earlier today — Sean supplied a node URL and
`figma-bind-probe.py` was fed real MCP output for the first time. It ran end to end and
corrected the capture contract in two places that fixtures could never have caught.

(1) `get_metadata` returns `<frame …><symbol …/></frame>`: types are element TAGS and there
is NO paint attribute at all. The original R3-from-metadata path required a node to be
"painted", so it could never fire on real output — and a self-test asserted it worked, using
an invented `type="RECTANGLE" fill="#fff"` shape Figma does not emit. R3 now judges a raw
shape by tree position: top-level chrome fails, the same shape inside an instance is that
component's own internals (icon vectors) and is left alone.

(2) `get_variable_defs` returns a MIXED map — token paths, `var(--x)` references, and bare
property names whose values are the resolved literals of UNBOUND properties. That third kind
is precisely what R2 exists to refuse and it is visible nowhere else; the probe was not
reading the map for R2 at all. Before the fix it would have reported "R1 and R3 verified, 0
violations" on a component carrying eight unbound properties — a false pass, the worst
outcome for a prove-gate. A follow-on fragility surfaced while fixing it: "a token has a
slash" would have flagged doctrine's own hyphenated spellings (`space-0`, `radius-none`,
`border-width-0`), so the discriminator is now "a token has a separator", pinned in both
directions by self-test.

Findings on the live node: R1 clean — no `Color/*` primitives anywhere, which is the evidence
that the hard gate does not over-fire on real production work. R3 clean — every child is a
variant symbol. R2 found eight unbound properties spanning height, padding, gap, radius,
focus-ring radius, font size, line height and weight: exactly the families the Density
standing rule names, on a control, while tokens for those families exist in the same file.
Reported to Sean in session; the capture stayed in the scratchpad.

Also corrected a rule I had written wrong earlier in the day: I justified scratchpad-only
captures as wall 3 ("employer content must not be committed here"). Wall 3 is
one-directional — nothing personal into employer repos — and employer design data is tracked
in this vault by design (CDS file key, token names and hex values already live across
02-centricPLM, 09-figma-repo-sync-plugin, project-context-detail and the log archive). Fixed
in the probe docstring, its --emit-template help, figma hub step 7, the close-out SKIP text,
the decision memo and the report. A wrong rule written into a skill surface gets followed
later, so it was worth the pass.

Generalisable lesson, recorded in [[decision-capture-and-assess-split]]: a detector built
only against fixtures of your own design tests your imagination, not the tool.

22 harness gates green, 43/43 negative fixtures, ruff clean.

Report: `07-projects/19-workspace-brain/reports/figma-bind-probe_v1.0_2026-09-15.md`
--- END BLOCK ---

### 2026-09-12 — PlanetCompiler regional catchment and shared terrain completion

SessionID: 01a08bae-ad4a-7dc1-bfb2-f6d79fdd25fe-phase3-2026-09-12
ParentSessionID: 01a08bae-ad4a-7dc1-bfb2-f6d79fdd25fe
--- SESSION BLOCK ---
Date: 2026-09-12
Agent: Codex
Surface: Codex desktop
Machine: Personal Mac, Apple M3 Max
Project(s): PlanetCompiler; independent Planet Lab
Continuity: The September 10 phases-one/two note was already folded into session-log.md by another machine. This additive continuation retains the same parent task and uses a distinct compaction key so new completion evidence is not discarded.
Phase-three follow-up: Sean authorized Continue and resumed on September 12. Completed the conditioned catchment core, separate routing/physical ground, finite lake water and conservative solid accounts, authoritative shared-triangle queries, bounded native display and editor playback. Debug/Release each 7 core suites,112 regional checks/24 planted corruptions,78 global and65 strip checks pass. Final native17/17, live regional1771/1771 with five byte-equal histories/90queries, actualSlate controls8/8 and eleven independent original-pixel captures pass. Corrected below-scene placement and animated-focus failure; preserved all eleven failed images and later cropped top view. Final wider top passes. Scientific and rendering limits/human acceptance remain explicit. Independent first84/86 report was overwritten; reconstruction is labeled and original104/106 preserved. All implementation remains PlanetCompiler; Legion untouched.
Phase-three source checkpoints: f0bf700,234d8e8,18a762c,a468110,a112e1c,a0fe2ae (final evidence checkpoint); source/evidence checker, all seven intent criteria and canonical validators pass; complete artifact manifest at evidence/phase-3/phase-report.json. Native editor left clean/stopped on final5000-year elevation at localhost8765; agents complete.
Phase-four follow-up: Sean instructed Continue after phase three. Completed immutable regional quadtree hierarchy, explicit mixed-detail stitches, all-mask triangle-overlay errors, separate source/committed queries and atomic async-cooked native collision/display publication. Review corrected nonmonotone balancing, worker marker path, valid-root placement and subtle/absolute child-transform bypass. Preserve the first oracle runs, initial 18/24 native failure, zero-probe live attempt and complete pre-guard run. Debug/Release each pass 9/9 core suites, 105/105 independent terrain checks with 22 planted corruptions and 21,900 geometric probes, plus 1,120 actual source and 1,120 emitted queries. Prior regional/global/strip audits pass 112/78/65 each. Final native 24/24, live 1,837/1,837 with 13,200 real collision probes (12,992 distinct), eight actual controls and all twelve independently inspected original captures pass. Maximum actual world mismatch is 1.758e-6 m against the 0.02 m collision/display gate.
Phase-four checkpoint: e9593d3, source/evidence checker and all seven intent criteria pass; evidence/phase-4/phase-report.json records source and all retained artifact hashes. Native source 8a9faa9 independently reviewed. Editor PID 66415 left clean on N64 finest Elevation at 2,000 years, actual terrain selected/focused and only localhost8765 listening. No pending replacement, PIE or open assets; observer removed, all agents complete. Source spacing remains 500 m at 32 km/N64. No added geology, continuous streaming/geomorphing, production traversal, frame-rate or photographic acceptance. Human acceptance remains pending. Native repo has no remote; Legion remains untouched. Canonical generation, routing, integrity, links, workspace, first-wave detector and negative-fixture validation passes.
Phase-five active: Sean continued. Frozen camera/quantization/readiness contract and independent design review at native9edd216; intent gate/ready passed. G5/U5/V5 implementing in isolated view-core/view-unreal/view-oracle worktrees. V5 freezes before new implementation access. Root owns all editor calls and ≥100submissions/10publications/2000collision-probes, actual controls, motion/pixel review and source/evidence closeout. No phase-five acceptance is closed yet.
Next: complete phase five within its bounded contract. Preserve original references, adversarial visual gates and Legion.
Handoff: 07-projects/13-legion/docs/planet-lab-independent/SESSION-STATE.md
--- END BLOCK ---

### 2026-09-15 — Proto PR 79 merge conflicts resolved

SessionID: 2026-09-15-work-p79cf
--- SESSION BLOCK ---
Date: 2026-09-15
Machine: Work MacBook Pro
Surface: Cursor
Project(s): saas-plm-prototype (cpes-software)
Summary: Merged origin/main into feat/page-composer-model so proto PR 79 is mergeable after #80 Material Symbols. Kept page-composer wiring; Pages tab uses `web`, Configure page uses `open_in_new`; renamed ComposerTree.tsx → ComposerTreeList.tsx to avoid a case-insensitive clash with composerTree.ts.
Decisions:
  - centric-engineering: push the conflict resolution; do not self-merge the PR.
Evidence:
  - PR 79 mergeable + CI (build, ds-check, CodeQL) @ https://github.com/cpes-software/saas-plm-prototype/pull/79 — verified
Next:
  - Human review and merge of proto PR 79 (no Linear file — GitHub PR is the tracker).
--- END BLOCK ---

### 2026-09-15 — A8: the Figma construction gate becomes a detector

SessionID: 2026-09-15-work-mbp-figma-probe
--- SESSION BLOCK ---
Date: 2026-09-15
Machine: Work MacBook Pro (main, going forward)
Surface: Claude Code (Mac desktop app)
Agent: Claude Opus 5
Project(s): 19-workspace-brain

Summary: A8, the last open row from the 2026-09-11 automation review. It was classified a
capability mint rather than a check because capture needs MCP, which only the agent has.
Resolved by splitting the gate at the tool boundary: the agent captures via
get_variable_defs/get_metadata into its scratchpad, and `09-tools/figma-bind-probe.py`
judges the capture deterministically. `--emit-template` prints the exact MCP calls so the
agent half is mechanical.

Rules taken verbatim from the figma hub hard gate and figma-ds-surface-authoring: R1 a bound
`Color/*` primitive (FAIL), R2 raw unbound value with zeros explicitly not exempt (FAIL), R3
painted rect where an instance belongs (FAIL), R4 density-unaware ladder on a control (WARN,
because general surface radius may correctly use the Radii ladder), R0 an allow entry with no
written reason (FAIL — doctrine says exceptions are noted, not silently left). An empty
capture exits 2, never 0: "no findings" and "no evidence" are different claims.

Preflight defect found on the way: capability-registry detected Figma with `mcp__*figma*__*`,
but Claude Code mounts the server under a UUID (`mcp__<uuid>__use_figma`), so the capability
read as ABSENT while live and authenticated — every `requires: [figma-mcp]` skill would have
silently degraded. Pattern fixed to `mcp__*figma*` with the reason recorded inline. Found only
because A8 forced a real preflight instead of a documented one.

Employer wall: `whoami` is sean.sands@centricsoftware.com (Centric org). Running the probe is
fine (read-only, Sean's own work account) but captures are employer content — both fixtures
are synthetic and say so, and the skill, CLI help and close-out SKIP text all say scratchpad.

Wired: close-out figma row goes from two bare SKIPs to SKIP-for-capture plus a real CLI for
assess; harness quality lane (22 gates); CI runs the self-test and both fixtures, asserting
the violation fixture FAILS; figma hub step 7; five Layer-0 routes. The old
`test_figma_is_honest_skip` encoded the pre-A8 world and is now
`test_figma_splits_capture_from_assess`, asserting both halves.

OPEN AND STATED: the probe has never been fed real MCP output. The capture contract comes
from documented tool shapes, not observed ones. One Figma node URL and one run closes it.
Recorded as a gap rather than rounded up to done.

22 harness gates green, 43/43 negative fixtures, 48/48 matcher cases, 14/14 trajectories,
ruff clean.

Report: `07-projects/19-workspace-brain/reports/figma-bind-probe_v1.0_2026-09-15.md`
Decision: `[[decision-capture-and-assess-split]]`
--- END BLOCK ---

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
