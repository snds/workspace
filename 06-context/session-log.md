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

### 2026-09-02 — Ontology and knowledge graphs for agents

SessionID: 2026-09-02-voyager-ontkg
--- SESSION BLOCK ---
Date: 2026-09-02
Machine: Personal MacBook Pro
Surface: Cursor
Agent: Cursor Grok 4.6
Project(s): 19-workspace-brain (teaching; no project files changed)
Summary: Explained ontology (shared types and legal relations) vs knowledge graph (typed facts in that vocabulary), and how agents use classify → traverse → constrain → write-back instead of dumping similar text. Mapped the same split onto this vault: workspace-ontology + skill frontmatter as schema; registry load_chains, routing map, and epistemic `relations:` as the graphs; retrieval finds candidates, types decide what may act.
Decisions:
  - Career-ops trigger on the letter `i` treated as a misfire; did not load job-search skills
Next:
  - Sean picks a follow-up if wanted: walk one vault decision through the graph; contrast ontology+graph vs RAG/skills/memory; or sketch a domain graph (PLM / LCARS / tokens) on top of the workspace ontology
--- END BLOCK ---

### 2026-09-02 — Prove-engine merge close + DSDS persist

SessionID: 2026-09-02-voyager-e4f1a
--- SESSION BLOCK ---
Date: 2026-09-02
Machine: Personal MacBook Pro
Surface: Cursor
Agent: Cursor Grok 4.6
Project(s): 19-workspace-brain, 20-lcars-generative-interface
Summary: Closed the prove-engine thread (vqa/1.1 altitudes A–G, play-prove, /optimize, LCARS uncued residuals) already merged to main as 0f4228a. Persisted the 2026-09-01 project-independent DSDS constitution + ds-source-watch landing that was still sitting staged. Folded the 2026-08-26 Looney Tunes fragment into session-log.
Artifacts:
  - 03-skills/visual-prove-engine/ vqa/1.1 + 03-skills/play-prove/ (on main via 54a2efe / 0f4228a)
  - 02-shared-references/dsds/dsds-constitution.md + workspace-ds-constitution.dsds.yaml
  - 02-shared-references/idempotent-design-decisions.md + 03-skills/ds-source-watch/ + 09-tools/ds-source-watch.py
Decisions:
  - Personal-solo merge to main, not a PR; SWF dumps stay untracked
  - DS constitution is project-independent; projects extend it, they do not fork it
Evidence:
  - prove-engine merge @ github.com/snds/workspace main 0f4228a — verified
Pending resolved:
  - Prove-engine course corrections 1–12 + /optimize landed on origin/main
Next:
  - Run `python3 09-tools/ds-source-watch.py --fetch` when the first snapshot should be judged
  - LCARS: add measured cues for the four named uncued residuals, then build to them
--- END BLOCK ---


### 2026-08-26 — Looney Tunes loudness analysis + full subtitle coverage

SessionID: 2026-08-26-voyager-b7191a1
--- SESSION BLOCK ---
Date: 2026-08-26
Machine: Personal MacBook Pro
Surface: Cursor
Agent: Claude Fable 5
Project(s): 01-mediaservices
Summary: Measured EBU R128 loudness for all 2,919 Looney Tunes files plus watched reference titles; derived a -21.9 LUFS reference target and a -6.6 dB best nominal gain for the set Plex actually plays. Found the real problem is spread, not level: Plex prefers the unmanaged dump folder for 1,035 of 1,064 episodes (15.1 dB p10-p90 spread) while the Sonarr-managed twins are already leveled (1.7 dB spread, nominal -7.4 dB). Separately closed the subtitle gap on played copies: 781 sidecars placed (721 copied from managed twins, 46 extracted from embedded tracks, 14 subgen/whisper), final audit 1,064/1,064 covered, 0 uncovered.
Artifacts:
  - Server /mnt/user/appdata/media-sentinel/loudness/ — results.jsonl (2,919 measurements), summary.json, gains.csv (per-file clip-safe gains), plex-preferred.json (episode → played file map), subtitle-sync-journal.txt (781-line delete-list of every sidecar placed)
  - Canvas looney-tunes-loudness.canvas.tsx (Cursor, MediaSentinel project) — full analysis
  - MediaSentinel repo scratch/loudness-scan.py + scratch/loudness-analyze.py (gitignored scratch)
Decisions:
  - Loudness fix recommendation: point Plex at the managed copies (MediaSentinel dedupe path) then apply one nominal gain of -7.4 dB, instead of per-file gain edits on 1,871 dump files
  - Subtitle quality order enforced: human sidecar > extracted embedded > whisper; nothing overwritten, every placement journaled for reversal
  - subgen used only for the 14 episodes with no human-made source anywhere
Pending added:
  - User decision: adopt dedupe-to-managed recommendation vs per-file gains from gains.csv
  - If dedupe chosen: run MediaSentinel duplicate adjudication on the two Looney Tunes folders
Pending resolved:
  - (none from prior baton)
Next:
  - Await user's pick on the loudness remediation path; gains.csv is ready either way
Git: MediaSentinel repo untouched (scratch/ + docs/ only, uncommitted); workspace this commit
--- END BLOCK ---

---

## Evening continuation: consolidation executed

Looney Tunes consolidated to the single Sonarr folder (1,062 files, Plex rebuilt show as ratingKey 40463, zero dupes, 100% subs, loudness leveled). The Orville / Firefly / 12 Monkeys duplicate folders resolved by MediaSentinel adjudication; 16 empty leftover folders deleted.

Incident: 184 quality-upgrade source files destroyed (ffmpeg `.part` format-inference failure followed by an unconditional graveyard sweep). Library not degraded; upgrade list saved to `lost-upgrades.json` for Sonarr re-grab. Lessons journaled in project SESSION-STATE: explicit `-f` on temp outputs, sweeps gate on zero errors, review decisions before deletions, smoke-test destructive batches.

Repo: parser fix (4-digit year-seasons, S00 specials) and grouping fix (yearless names merge into sole year variant) with tests; suite 578 green, uncommitted.


### 2026-08-11 — cui ViewToolbar bg-card consistency

SessionID: 2026-08-11-work-a7c2e1
--- SESSION BLOCK ---
Date: 2026-08-11
Machine: Work MacBook Pro
Surface: Cursor
Project(s): centric-ui (employer)
Summary: Materials ViewToolbar used bg-background (darker) via single-toolbar flag; switched all collection toolbars to bg-card to match Material Colours / Samples. Pushed follow-up commit to PR #284.
Evidence:
  - PR updated @ https://github.com/cpes-software/centric-ui/pull/284 — verified
Next:
  - Review/merge https://github.com/cpes-software/centric-ui/pull/284
--- END BLOCK ---


### 2026-08-11 — cui data-table landing parity + sticky actions

SessionID: 2026-08-11-work-40891f
--- SESSION BLOCK ---
Date: 2026-08-11
Machine: Work MacBook Pro
Surface: Cursor
Project(s): centric-ui (employer)
Summary: Finished Materials landing table parity work in `@centric/data-table`: decoupled sticky row actions into spacer + float host (fixes stacked hover wash), restored package header border/pad, wired landing density to global Compact/Normal/Spacious, stripped fighting landing CSS. Opened PR.
Evidence:
  - PR opened @ https://github.com/cpes-software/centric-ui/pull/284 — verified
Decisions:
  - Sticky actions: in-flow spacer (wash + width) + zero-width sticky float host (pill only)
  - Landing tables follow global app density; non-landing BO tables keep view-config density
  - Header separator/height owned by package, not Materials recipe; radii deferred post density-merge
Next:
  - Review/merge https://github.com/cpes-software/centric-ui/pull/284
  - After merge: revisit table shell radii if still off vs demo
--- END BLOCK ---


### 2026-08-11 — Local centric-service stack for UI API auth

SessionID: 2026-08-11-work-localstack
--- SESSION BLOCK ---
Date: 2026-08-11
Agent: Cursor Grok 4.5
Surface: Cursor
Machine: Work MacBook Pro (CS-K746DRWXY1)
Project(s): centric-ui (employer), centric-service
Artifacts:
  - ~/Projects/cpes-software/centric-service — cloned
  - ~/Projects/cpes-software/platform-golden-verticals — cloned (sibling for volume-mode flavours)
  - centric-ui `.env.local` / `.env.compose.local` — local compose creds (`DUMMY-123`, provisioner `cpes-record-service`)
  - centric-ui `vite.config.ts` — `server.host: true` (IPv4+IPv6; fixes ERR_CONNECTION_REFUSED -102)
  - Colima Docker runtime (20GB / 6 CPU) — Docker Desktop cask install blocked on sudo
Decisions:
  - Local stack path (Leanne): compose + `npm run dev`, not Cursor-hosted server.
  - Local Keycloak user `test`/`test` (realm VMS, org test-org) is fine for FE work.
  - Flavour provisioner unauthorized was wrong API identity (`cpes-admin-portal`+cloud key); use `cpes-record-service`+`DUMMY-123` locally.
Pending added:
  - Colima memory pressure: Keycloak OOM (exit 137) → nginx 502; may need to stop LocalStack/OpenSearch-dashboards when idle.
  - Golden provisioner poller can hang after JWT expiry (`status=unknown`); volume-mode sibling checkout is the reliable local source.
  - `gh auth` token invalid on this machine; GHCR pull still needs PAT/`gh auth login` if not building `centric-service:local`.
Pending resolved:
  - Unauthorized API / no local backend — stack up; login + provisioner identity fixed for local compose.
Next:
  - Keep UI via terminal: `cd ~/Projects/cpes-software/centric-ui && npm run dev` (agents' nohup sessions die).
  - If Keycloak 502 again: `docker start keycloak` (or compose up keycloak) after OOM.
  - Optional: trim compose services / bump Colima RAM further to stop Keycloak OOMs.
--- END BLOCK ---


### 2026-08-10 — Harness-map cycle closed + CI triage

SessionID: 2026-08-10-work-hmclose
--- SESSION BLOCK ---
Date: 2026-08-10
Machine: Work MacBook Pro
Surface: Cursor
Agent: Cursor Grok 4.5
Project(s): 19-workspace-brain
Summary: Closed the harness-map cycle — applied #1–#3+#6, accepted #4/#5/#7/#8 standing; triaged email CI failures (INDEX/MEMORY orphans, fixed by #1); main green and pushed through `6b92c1a`.
Artifacts:
  - 07-projects/19-workspace-brain/reports/harness-map_v1.0_2026-08-07.md — map + stamp + applied/accepted dispositions
  - 07-projects/19-workspace-brain/reports/harness-map.stamp — first real stamp (2026-08-07)
  - 06-context/project-context-detail.md — graduated pending substance
  - 06-context/project-registry.md — Active Projects narratives (load later)
  - 09-tools/check-unattended-runner-gate.py — unattended runner hard gate
Decisions:
  - Apply harness-map #1–#3+#6; leave #4 Keep, #5/#8 Probation, #7 Load later/Keep as standing (Sean ack).
  - Retest #5 on next plugin publish; revisit #8 ~2026-09-07.
Evidence:
  - workspace CI all green after apply @ github.com/snds/workspace actions on e2d28eb — verified
  - prior workspace-integrity failures (runs 31190694022, 31191199865) = INDEX/MEMORY orphans — verified fixed by #1
Pending added: (none)
Pending resolved:
  - Harness-map first-run + stamp (was next action on baton)
Project status changes:
  - 19-workspace-brain: harness-map cycle closed; baton points at optional mission-fit + probation retests
Next:
  - Optional: mission-fit on one unreliable “done”
  - Retest harness-map #5 on next build-local-skill-plugin publish
  - Revisit harness-map #8 (~2026-09-07)
  - Still open from prior baton: ^pc-07 / ^pc-11 homes; lane ambiguity ^pc-30 / ^pc-41
--- END BLOCK ---


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
---

### 2026-08-04 — Token Spec page (Figma ↔ code)

SessionID: 2026-08-04-token-spec-page
--- SESSION BLOCK ---
Date: 2026-08-04
Agent: Composer
Surface: Cursor
Machine: Work MacBook Pro
Project(s): Centric SaaS PLM — Figma DS (`o6o1ZuGHxDow2vHLuYXT6X`); centric-ui tokens read-only
Summary: Built a **Token Spec** page in the DS file from live Figma variables, paired each
  semantic token with its centric-ui `--sem-*` (when mapped), flagged raw/alias deviations,
  and tagged representable-but-missing tokens on both sides.
Artifacts:
  - Figma page `Token Spec` (id `405:1679`, index 2 after Cover separator)
  - `08-knowledge/design/token-spec-page.md`
  - `08-knowledge/design/token-spec-figma-vs-code.json`
Decisions / findings:
  - 74 semantic colors: 40 MATCH · 6 DEVIATE · 28 FIGMA-ONLY
  - Deviations concentrated on selected/sidebar chrome: Figma uses `interaction/*` opacity
    overlays + `action/primary` foregrounds; code still uses solid `blue-5` / `blue-11` and
    zinc sidebar accent.
  - Density + `interaction/*` + `status/caution*` are Figma-ahead (no code counterparts).
  - Missing in Figma (representable): `--header-h`, `--shadow-cds-drop-{1,2,3}`.
  - (Superseded 2026-08-05) Radii now density-modeled with `xxs`.
Next:
  - Optionally sync code selected/sidebar to Figma interaction model, or document intentional lag.
  - Add effect variables for CDS drop shadows if Figma should own them.
--- END SESSION BLOCK ---

### 2026-08-05 — Added prototype library comparison
Summary: Rebuilt Token Spec as three-way (Figma ↔ centric-ui ↔ saas-plm-prototype).
  Density + radii call out Normal-axis offset (Figma Normal = Proto Compact).
  Proto-only density tokens tagged MISSING IN FIGMA.

### 2026-08-05 — Align Figma density/radii to prototype
Summary: Figma Density + Radii updated to prototype values; missing density
  tokens added; proto gained padding-x/sm twin, radius-none,
  radius-full. Token Spec rebuilt (18 density MATCH). Later: Radii
  density-modeled + `radius/xxs`; centric-ui density port.

### 2026-07-31 — Figma DS library: semantic density modes + collection cleanup

SessionID: 2026-07-31-work-figma-density
--- SESSION BLOCK ---
Date: 2026-07-31
Agent: Opus 4.8
Surface: Cursor
Machine: Work MacBook Pro (main, CS-K746DRWXY1)
Project(s): Centric SaaS PLM — Figma Design System library (file `o6o1ZuGHxDow2vHLuYXT6X`)
Summary: Refactored the near-publish Figma variable library in four moves. (1) Built a
  `Foundations / Semantics / Density` collection — modes Normal(default)/Compact/Spacious,
  23 tokens (control-height, padding-x/y, gap, control-radius, container/*) each aliasing the
  existing Spacing/Radii scale so **Normal == the current design pixel-for-pixel**. (2) Applied
  density across every page by rebinding structural props to density tokens (heights + radii via
  the Button/Select Size collections and blanket 8/12px radius; vertical padding + gaps + container
  insets 16/24 across Components, Base UI Additions, Features, Layout) — ~1,500 rebinds, all on
  non-instance nodes so instances inherit cleanly. An initial explicit-Normal stamp was later
  **reverted**: Density and Colors now remain Auto on components/subcomponents and inherit from
  app/chrome or audit shells; collection defaults remain Normal/Light. (3) Deleted the redundant
  `Typography Roles` collection — it was a pure 1:1 alias layer; rebound all 21 text styles' 126
  fields straight to `Foundations / Semantics / Typography`, no stray refs. (4) Normalized all 14
  component collection names to spaced `Component / Axis` (` — ` → ` / `, `Sizes` → `Size`).
  Verified: 0 em-dash collections, Roles gone, density resolves at all 3 modes, side-by-side
  screenshot of Button/Badge/Select/Input/Checkbox/Card confirms Compact/Normal/Spacious cascade.
Artifacts:
  - Figma file `o6o1ZuGHxDow2vHLuYXT6X` (Centric SaaS PLM - Design System) — variables/styles mutated in place
  - Knowledge updated: `08-knowledge/design/centric-plm-design-system.md` (density-via-modes + collapse patterns)
Decisions:
  - Density lives in the **semantic layer** as a mode-set collection, not per-component — components
    consume density tokens; the two axes (component Size × Density mode) compose independently.
  - Normal is the pinned default and is value-identical to the pre-refactor library (zero visual drift).
  - Horizontal *control* padding (8/10/12) stays fixed; only *container* insets (16/24) breathe on X.
  - An alias-only intermediate collection (Roles) is waste — bind styles/consumers to semantics directly.
  - Density/Colors are context axes: component roots and nested instances stay Auto; only app/chrome,
    page, feature, or audit shells set explicit modes. Collection defaults are Normal/Light.
Pending resolved:
  - Slash-group semantic scale names (Typography 29 + Spacing 36 + Radii 10 + Border Widths 6)
  - Semantic color category folders (`surface/` `action/` `status/` `chrome/` `sidebar/`) — 54 tokens
  - Cataloged + deleted 42 `cds/*` bridge tokens (zero Figma consumers); map at
    `08-knowledge/design/cds-to-radix-color-map.md` for centric-ui migration
  - `Calendar Day / Position` → `Calendar / Radii` with `Day/{corner}` vars + Title-Case modes;
    rebound `_Calendar/Day` corners (was dead wiring onto density-only radii)
  - Instance-vs-context method documented (`figma-component-token-axes`); density `control-font-size/*`;
    Button/Avatar Size `fontSize` wired through Size×Density; `Sidebar / Surface` pilot binds
    chrome fill/stroke + Menu Button focus ring (primary retained as capacity)
Pending added:
  - (Optional) Make Switch/Avatar/Badge Size collections density-aware for non-type dims (height already on Button).
  - centric-ui: retire CDS color usages using [[cds-to-radix-color-map]] → intent tokens (employer work).
  - Apply instance-vs-context recipe to remaining shells (Card/Popover → surface/* foregrounds).
  - Build Audit / Density Figma pages seeded from saas-plm-prototype (plan Part C).
Pending resolved:
  - Decisions: Figma Density Normal stays **32**; `line-height/relaxed` → **28**; baseline wrappers deferred
  - Full density type ladder (`type-size|leading|paragraph/*`); all 21 styles rebound; Button/Avatar Size×Density type wired
  - Cleared 2,387 direct explicit Density pins (plus inherited nested pins that disappeared with their
    masters) across Icons, Components, Additions, Features, and Layout; verified zero Density/Color
    context overrides remain. Auto inheritance test: Button resolved 28/12 Compact, 32/14 Normal,
    36/16 Spacious and inherited Dark/Light from its parent shell.
Pending resolved:
  - Vertical-rhythm audit + repair. Seed: `Example density` section `313:2782` (three Sidebar shells with
    explicit Compact/Normal/Spacious). Confirmed failure mode: horizontal AL + counter-axis CENTER +
    pad-Y bound to `space/0` + FIXED height with **no** Density-backed height → row frozen across modes.
    Centering alone carries no vertical rhythm. Audit + fixes: `08-knowledge/design/density-vertical-rhythm-audit.md`.
  - Repair recipe (repeatable): **HUG vertical + `padding-y/*` + `minHeight` → `control-height/*`**.
    Plain HUG+padding drifts off the control ladder at Spacious because the type ladder grows
    line-height 16/20/24 while `control-height/*` grows 28/32/36 (Menu Button hit 40 vs Select 36).
  - Fixed 9 masters (Compact/Normal/Spacious verified by temp three-mode test board, then deleted):
    `_Sidebar/Menu Button` 28/32/36 · Layout `Header` 40/48/56 · `_Table/Cell` + `_Table/Head` 32/40/48 ·
    `_Tabs/Trigger` 24/28/36 · `_Pagination/Item` 32/36/40 · `_Calendar/Day` 28/32/36 ·
    `_Dialog/Close` + `_Sheet/Close` 24/28/32. Button/Select already correct (28/32/36) — left as reference.
  - Only Normal-value drift: `_Tabs/Trigger` 26 → 28 (26 was off-ladder; 28 = `control-height/sm`).
Pending resolved:
  - Density `icon-size/*` ladder (xs/sm/md/lg → 12/16/20/24 Normal). Wired 4,244 icon masters'
    fontSize → `icon-size/md`; Button Size.iconSize → ladder; Menu Item → sm. Glyph **and box** now
    measure 16/20/24 (md) and 12/16/20 (sm) across Compact/Normal/Spacious.
  - Root blocker was **not** a Figma component-set limitation (earlier read was wrong): icon masters
    carried `min/maxWidth` + `min/maxHeight` pinned to 20, freezing the frame. Recipe per Sean:
    clear bound width/height, clear all four min/max, glyph TEXT → HUG/HUG, frame → HUG/HUG, and let
    `fontSize` → `icon-size/*` drive. Never re-bind frame width/height. Same unpin applied to 64
    consumer icon instances.
  - Gotcha: `Material Symbols Outlined` is missing in this agent environment (`hasMissingFont`), so
    plugin-side `node.width` reports stale 20×20. Verify icon sizing via server-rendered screenshot.
  - Button Size sm icon Normal 14→16; default binding corrected 16→20 to match prior render.
Icon consumer audit (434 instances across Components / Additions / Features / Layout):
  - Density-aware: 180 `icon-size/md` + 63 Button `iconSize` + 20 sm + 2 xs. **20×20 confirmed default**
    (all 4,244 masters bind `fontSize` → `icon-size/md`).
  - **171 density-blind literals** (14/16/18) from manual instance resizes. Figma stores a manual icon
    resize as a **0.8 scale override**, not a fontSize override — so it now *multiplies* the token:
    Sean's `more_vert` reads 12.8 / 16 / 19.2 (C/N/S) instead of 16 / 20 / 24.
  - **Hard blocker (corrected):** first read blamed the missing font — wrong. Control test: same
    `setBoundVariable('fontSize', …)` was dropped on `_Select/Item`'s **Inter** label (font loads fine,
    0 instances above). So **instance children reject fontSize variable binds, period**; paint writes
    on the same nodes succeed. Reinstalling Material Symbols does not unblock it — the bind must live
    on the main component. 145 of 156 rebinds were dropped this way, silently, no throw.
  - Font status: `Material Symbols Outlined` still not enumerated by Figma after Sean's Font Book
    reinstall (Rounded + Sharp are). Figma caches fonts at launch → needs an app restart. Only affects
    *measurement* trust, not the write path.
  - **Working fix path** (verified on `26:2177`): capture glyph fill + bound colour var →
    `instance.resetOverrides()` (clears the scale override) → re-apply via `setBoundVariableForPaint`.
    Step 2 silently reverts colour (`surface/muted/foreground` → `surface/foreground`); repaired.
    Blocks a blind sweep: reset returns every icon to the master's 20, which is wrong for the
    deliberately-small ones — those need a **Size variant on the icon component**.
  - Slot content is structurally locked: `insertChild` → negative index, `remove()` → "not allowed",
    `resetOverrides()` does not clear the inherited scale. Reach via **raw id** (`17:692`), not `I…;…`.
    Attempted Button swap for `UserIdentity` more_vert; it carried the 0.8 scale (72.8×25.6) — reverted clean.
  - Bare-icon vs icon-button classification recorded in the audit doc (~40 should become icon buttons;
    selects/tree chevrons/status glyphs/menu leading icons correctly stay bare).
Pending added:
  - **Needs Sean:** confirm Layout shell icon restore map (Business Objects→`business`, Team→`group`,
    Schema Registry→`schema`, …) — originals were not recoverable after the wipe.
  - Promote `UserIdentity` → `_Sidebar/User` (5 inline slot copies still).
  - Convert remaining interactive bare icons to Button + `Layout=icon-only` (Toast close, table row
    actions, widget overflow, etc.) — UserIdentity more_vert ×5 already done.
  - P2 sweep: Card / Dialog / Sheet / Empty State / Dropdown / Command / Menubar content slots still bind
    pad-Y to `space/*` instead of `padding-y/*` or `container/*` — inset is non-zero but density-blind.
  - Republish library after this structural round (adds to `^pc-18`).
Resolved this turn (fork):
  - **Regression:** blind `resetOverrides` wiped nested icon swaps → Layout Menu Buttons → `home`.
    Root cause confirmed: nested swaps without INSTANCE_SWAP are override-only.
  - Restored 40 Layout Menu Buttons via new `Icon` INSTANCE_SWAP (map above — Sean confirm).
  - Added INSTANCE_SWAP (+ exposed) on Menu Button, Button leading/trailing, Input, Select, Dialog/Sheet
    Close, Collapsible Trigger, Menu Item, Toast, Alert, Accordion Item, NavMenu Trigger.
  - `Icon / Size` live (default/xs/sm/lg/control); masters on `size`; Button icons → `control`.
  - `Button / Layout` (default / icon-only) + `iconOnlyPaddingX`; Button pad-X rebound to Layout.
  - UserIdentity more_vert → icon-only Button `More actions` (ghost/sm/icon-only/more_vert) ×5.
Icon Button + Menu Button round (Sean's direction):
  - Built **`Icon Button`** (`350:2877`) that *nests a real Button instance* rather than reimplementing it.
    1:1 by construction: inner Button FIXED width bound to `Button / Size`.`height` — the same token as
    height. `Button / Layout = icon-only` for padding; Variant/Size modes **cleared** so consumers drive
    them; `isExposedInstance = true` bubbles up `Leading icon instance` + `State` (icon exposed 2 levels).
    Verified square xs/sm/default/lg × Compact/Normal/Spacious (20 → 40).
  - UserIdentity ×5 swapped onto Icon Button (ghost/sm) — 24/28/32, the 0.8 scale drift finally gone.
  - **Menu Button colour bug (Sean spotted):** nav icon glyphs had drifted to `sidebar/foreground`
    (static) or a bare `foreground`, while labels used state-aware `Sidebar / Menu Button`.`foreground`
    → Selected went blue on text but stayed dark on the icon. Rebound 45 glyphs.
    Rule: a nested icon binds the *same* state variable as its sibling label.
  - **Icon semantics follow the label:** Dashboard → `dashboard` (`home` is only the master placeholder).
    10 swaps corrected. Cleared 4 stale `characters:"Search"` overrides on Documents rows — safe now that
    identity lives in the INSTANCE_SWAP prop rather than an override.
  - **Render caveat:** file data verified correct (masters *and* instances read `description` /
    `more_vert`, right codepoints, right mains) but server screenshots still show the old search / add
    glyphs. Missing `Material Symbols Outlined` means the app can't re-lay-out that text, so the
    rasterisation is stale. Swaps to *untouched* masters do render (dashboard appeared immediately).
    Figma still doesn't enumerate the font after the Font Book reinstall → **needs a Figma restart**.
Render lag resolved (Sean, after restart): Figma's renderer sometimes won't repaint a component
  until a user clicks *inside* it. He verified this — file data was correct all along, as the
  inspection said. One Compact menu item needed an instance reset + redo of overrides; rest updated.
  Standing lesson: when file data and a server screenshot disagree, trust the data and ask for a
  click/restart before re-editing. Do NOT "fix" a phantom.
Button ghost status + inverse (Sean's ask):
  - 6 new `Button / Variant` modes → 17 total: `ghost-{info,success,warning,caution,danger}` +
    `ghost-inverse`. Background + border transparent; only text/icon carry the status colour.
    `ghost-inverse` uses `action/primary/foreground` so a ghost on a filled surface reads light.
  - **Contrast catch:** first pass aliased the solid `status/*` hues (matching the existing
    `destructive` mode). Measured against `surface/background` — *all five* fail AA in Light, and
    `status/caution` (#ffe629) is 1.26:1, i.e. invisible. Rebound foregrounds to
    `status/*/soft/foreground` (4.51–5.21 Light, 8.95–14.14 Dark). Rings keep the solid hue —
    non-text UI component, 3:1 bar, saturated reads better. Verified by screenshot.
  - Existing `destructive` mode still carries the solid fg at 3.91 — flagged, untouched.
  - ~~Gap found: Hover pixel-identical to Default on every variant~~ **WRONG — my error.** The probe
    read only `fills` + a `/overlay|hover/i` name regex; the real node is `[state-layer]`, so it was
    missed. Hover always worked (foreground-tinted layer @0.12/0.24/0.32 node opacity).
    Lesson: a name-regex probe is not an inspection — enumerate children, read every paint.
Interaction semantics generalised (Sean's direction — overlays, not per-variant bg tokens):
  - 18 `interaction/*` tokens in Foundations/Semantics/Colors aliasing Radix **A4=hover / A5=pressed**
    per hue + Black/White overlay for solid/inverse. Hues: primary→Blue, info→Cyan, success→Green,
    warning→Orange, caution→Yellow, danger→Red, neutral→Zinc.
  - `Button / Variant` +`overlay/hover`/`overlay/pressed`, resolved per mode to the right family
    (solid | neutral | hue-keyed | inverse). Existing `[state-layer]` rebound to them at opacity 1,
    so alpha now lives in the token, not the node. Icon Button inherits (nests a real Button).
  - Alpha-in-token vs alpha-as-paint-opacity: authoring rule 17c only kills *paint* opacity on bound
    fills. Radix A-steps carry alpha in the colour value → they render. Proved it: bound fill,
    literal composite, and literal rgba all rasterised identically to `#e8e8ec`.
  - Verified pixel-exact by sampling the server PNG at node bounds (ghost 232,232,236 · default
    8,106,201 · ghost-info 202,241,246 · ghost-inverse 34,132,227) — all within 1/255 of prediction.
  - Unified 3 competing mechanisms → one: state-layer nodes (Button, Tabs), mode-driven `background`
    vars (Select Item, Table Row, Sidebar Menu Button), and direct opaque fills (Calendar Day,
    Pagination Item, Menubar/NavMenu Trigger, Toggle, Menu Item row).
  - Value shifts worth knowing: Table Row hover was Zinc **A2** (α0.02, below perceptual floor) → A4;
    Sidebar Menu Button hover was `sidebar/accent` → neutral alpha; Menu Item destructive highlight
    → `interaction/danger/hover`.
  - Left alone deliberately: Resizable Handle + Slider Thumb (hover changes the control, not a
    surface behind it) and all Selected/Active states (persistent state ≠ interaction feedback).
  - `surface/inverted/foreground` idea DROPPED — I'd oversold it. A fixed-polarity token can't work
    on *any* background; `ghost-inverse` stays an explicit consumer choice. Real options if ever
    needed: per-solid `on-*` pairings, or APCA-resolved contrast at runtime.
  - Docs: new [[interaction-state-semantics]] (architecture + centric-ui reconciliation plan).
Link + ghost/primary (Sean):
  - Link already had the state-layer; it was on *neutral* Zinc. Rebound `overlay/hover|pressed` for
    `link` → `interaction/primary/*` so brand links get a blue wash, not gray.
  - New `ghost/primary`: rest = `surface/foreground`; hover/pressed fg → `action/primary`; overlay →
    `interaction/primary/*`. Channel: `foreground/hover` + `foreground/pressed` on Button/Variant
    (seeded = default for every other mode; only ghost/primary elevates). Hover/Open/Pressed rebound
    label+icon to those tokens.
  - Verified: ghost/primary Default fg (41,45,49) → Hover (21,126,226); wash (213,239,255) matches
    link hover. ghost/secondary stays neutral wash (232,232,236).
  - Naming (Sean): slash-grouped all ghosts — `ghost` → `ghost/secondary`, `ghost-primary` →
    `ghost/primary`, and `ghost-{info,success,warning,caution,danger,inverse}` → `ghost/*`. Mode IDs
    stable; UserIdentity Icon Buttons still resolve on `ghost/secondary` (id `7:3`).
Brand as default hover/active voice (Sean):
  - Most chrome hovers → brand Blue A4 bg + `action/primary` fg. Selected → Blue A5 opacity (not
    solid Blue/5) + full brand fg. New tokens: `interaction/selected`, `interaction/selected/foreground`.
  - Rebound `sidebar/selected`, `chrome/selected` (+ fg) and `sidebar/accent` (+ fg) to those.
  - Sidebar Menu Button Selected resolves Blue A5 @α0.24 / fg `#0976e0` (was opaque `#cbe2ff` / Blue11).
  - Shifted to primary hover: Sidebar, Select Highlighted, Table Row, Tabs state-layers, Calendar Day,
    Pagination, Menubar/NavMenu Trigger, Toggle Off-Hover, Menu Item Default highlight.
  - Stay zinc: Button ghost/secondary·outline·secondary; **table cell** hover.
Table cascade exception (Sean — important):
  - Stack bottom→top: data fill → row primary overlay → column primary overlay → cell zinc overlay.
  - Why zinc on cell: primary-on-primary adds no info; neutral reads as "this cell." Alpha means
    coloured cells tint rather than get covered — the reason selected must stay opacity, not solid.
  - Scaffolded `Table / Cell` collection (Default transparent / Hover → `interaction/hover`); bound
    cell master. Column hover + coloured-cell fixture still open.
Avatar — regression I caused, plus a real gap (Sean: "circle gets very small, text breaches"):
  - ROOT CAUSE was mine, not a token gap. The earlier icon-unpinning sweep matched on
    "small + square + has a TEXT child" — `Avatar` (32x32, fallback initials "AB") fit that shape
    exactly, so 11 instances got flipped to HUG/HUG with their `width`/`height` binds cleared. The
    circle collapsed onto the glyph bbox: 19x20 Normal, 17x16 Compact, 22x24 Spacious — not even
    square, which is why initials touched the edge.
  - LESSON: never shape-match a structural sweep. "Square + small + text child" describes icons AND
    avatars AND badges AND count chips. Gate on master identity (component-set name / key), not
    geometry. Also: `resetOverrides()` and geometry sweeps are the two blast-radius tools here.
  - Fixed all 11 → FIXED/FIXED rebound to `Avatar / Size`.`size`. Verified 32x32 in all three density
    sidebars, initials centred. Masters already had primary+counter axis CENTER; untouched.
  - API notes: `set_minWidth` throws "cannot be overridden in an instance" — skip min/max on
    instances. Cross-page collect-then-write goes stale ("Node not found") on deep nested IDs, but
    the writes had actually landed; re-measure before assuming failure.
  - THE ACTUAL GAP (Sean picked both #1s — dedicated `avatar-size/*` + library-wide):
    Created `avatar-size/{sm,md,lg}` on Density (scopes WIDTH_HEIGHT), aliasing space/*:
    sm 24/20/28, md 32/28/36, lg **40/36/44** (preserves Normal 40; ±4 step; not control-height/lg).
    Rebound `Avatar / Size`.`size` sm→avatar-size/sm, md→…/md, lg→…/lg. Features 40×40 outlier →
    mode `lg` + bound. Live sidebars: Compact **28**, Normal **32**, Spacious **36**; glyph/circle
    ratio stable ~0.43–0.44 (was 0.375→0.50). Hover Card 48px = intentional `scaleFactor: 1.5`, leave.
    Write path this turn: figma-cli CDP (official `plugin-figma-figma` MCP not connected in Cursor).
Nested icon-only Button → Icon Button (Sean):
  - Census: 17 master-nested icon-only Buttons (Label=false) across Schema Action Buttons,
    Graph/Canvas/View toolbars, Header (+ theme-switcher xs×3). App Shell was instance-nested —
    inherits Header. UserIdentity already Icon Button.
  - Swapped all 17 → `Icon Button` (`350:2877`); preserved `ghost/secondary` + Size sm/xs + leading
    icon (all still placeholder `add` in these feature stubs).
  - Fixed Icon Button 1:1: inner Button width now binds to `Button / Size`.`height` (was hug; square
    only at md by luck). Cleared stale shell height/radius binds from swap. Result: sm 28², xs 24²,
    md 32²; density sidebars UserIdentity 28/32/36.
  - Re-census: **0** remaining nested icon-only Buttons on component masters.
Bare action icons → Icon Button (Sean):
  - ~47 master swaps: Input clear, Alert/Toast dismiss, Widget chrome (more/add/pin/close),
    Schema Palette add, Member/Relationship delete (`ghost/danger`), Documents Table
    download/delete + page chevrons, Inline Edit edit/confirm/cancel, Calendar month nav.
  - Gotchas: sibling variants can land as Icon Button with default `add` icon after first swap —
    re-set Leading to `close`. `scaleFactor` 0.8 on feature frames carries through swap — reset to 1
    or sizes read 0.8×. Outer HUG can stick at stale px after scale reset — resize to inner then HUG.
  - Skipped: Dialog/Sheet Close (already 28² wrappers), Pagination text+chevron pairs, disclosures,
    menu leadings, status glyphs, tiny decorative `open_in_new`.
Pagination → real Buttons + shared tokens (Sean):
  - Sean: Dialog close handled via parent subcomponent (leave alone). Pagination Prev/Next should be
    regular Buttons; Item should too, same token needs.
  - New `Pagination / Control` (single Value mode): background/default|active, foreground/*,
    border/default, overlay/hover|pressed → `interaction/primary/*`, radius → control-radius/sm,
    height → control-height/lg.
  - New Button / Variant mode **`pagination`**: outline-like rest (transparent bg + chrome border)
    but overlays alias Pagination / Control (primary hover/press — matches page-item chrome).
  - `_Pagination/Item` rebuilt: each State nests a real Button (square width=height @ lg).
    Default/Hover/Disabled → Variant=pagination; Active → Variant=default (solid primary).
  - Prev/Next frames → Button instances (pagination/lg, chevron leading/trailing, radius override
    to Pagination radius). Labels restored 1/2/3/8; item "1" Active.
INSTANCE_SWAP preferred lists cleared (Sean):
  - All 19 icon INSTANCE_SWAP props across 13 hosts (Button, Input, Select, Menu Button, Alert,
    Toast, Menu Item, etc.) — `preferredValues: []`. Re-census: 0 remaining. Swap UI no longer
    surfaces a Preferred shortlist.
Next:
  - Table column-hover surface + coloured-cell cascade proof
  - Optional: expose nested Button on `_Pagination/Item`; TEXT `Page` prop
  - centric-ui: `::after` state layer + interaction tokens; map former `ghost` → `ghost/secondary`;
    selected = primary A5 not solid. Employer repo → branch → PR → review.
  - Visual audit pages in Figma (prototype as capture seed only)
  - When Style Dictionary lands, map `/` → nested path; strip color category prefix for shadcn CSS
    (`action/primary` → `--primary`) or keep nested — decide at export time.
--- END SESSION BLOCK ---


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
