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


---

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

### 2026-07-09 — Beacon coverage closed: enroll helper shipped, six repos beaconed, audit false-MISS fix

--- SESSION BLOCK ---
Date: 2026-07-09
Agent: Claude Fable 5
Machine: Personal MacBook Pro
Surface: Claude Code (Mac desktop app)
Project(s): 19-workspace-brain (final stretch of the fix-session thread) — beacon coverage + machine-layer hardening.
Artifacts:
  - 00-bootstrap/beacon-enroll.sh — new helper: one-command personal-repo beacon enrollment; mechanical personal/employer classification per the context-profile resolution order; --sweep/--apply/--commit; employer repos refused + recorded in beacon-repos.ignore.txt.
Decisions:
  - Beacon-paste split (Sean): claude.ai surfaces done + acked on Personal MBP; Cursor + Perplexity ride the Work MBP doctor-install session (ack state is per-machine, so nothing is lost).
  - Enrollment stays human-gated only for UNKNOWN classifications; personal/employer resolve mechanically by remote — the doctor's nag now names the helper command (the nag IS the memory aid).
  - Legion's beacon committed on its in-flight feature branch, deliberately unpushed (never publish Sean's WIP branch).
Pending resolved:
  - Curate beacon-repos.txt (six repos enrolled: Davinci/Legion/MediaSentinel/Nexus/SNDS/Zuora — all personal by remote; five pushed).
  - claude.ai half of the beacon-paste item (pasted + acked by Sean; doctor verified clean).
Next:
  - Legion beacon reaches GitHub when `fix/gas-volume-halffloat-banding` pushes (or ask Claude to cherry-pick onto main).
  - Work MBP doctor install (pending item) now also delivers beacon-enroll.sh via git.
--- END BLOCK ---

---

### 2026-07-09 — MediaSentinel: Phase 9 "The Librarian" built + deployed (9.0/9.1/9.1c), perf fences, music UI

--- SESSION BLOCK ---
Date: 2026-07-09
Agent: Claude Fable 5
Machine: Personal MacBook Pro
Surface: Claude Code (Mac desktop app)
Project(s): MediaSentinel — Phase 9 "The Librarian" (plan → 9.0/9.1/9.1c built+deployed) + perf fences + music UI
Artifacts:
  - MediaSentinel repo (main, ~12 commits): docs/librarian-plan.md (Phase 9 plan + §15a operator briefs); librarian/ package (identity spine, resolve ladder, discography audit); metadata/ clients (MusicBrainz identity, AcoustID, iTunes, Deezer, Discogs, NetCache); perf throttle stack (container caps 8cpu/6g, proc.polite nice/ionice, worker caps, NDJSON streaming); music wall metrics + multi-disc merge + artist view + location-aware wall/list toggle; Apple-library sync (JXA exporter + launchd on this Mac + POST /api/apple-library) + diff-aware artwork backfill.
  - Signal-flow artifact: https://claude.ai/code/artifact/cda6cd6e-722e-4185-86e6-13202f9d4b85
Decisions:
  - Identity doctrine: evidence families A–E, tiers T0–T4, tags verified never trusted, missing data ≠ disagreement, entity only at ≥T3, T4 gated on 9.4 refute pass.
  - Streaming co-mingling: anchored artist matching (≥2 album anchors) + per-album MB arbitration; genres are soft flags.
  - Apple personal library: Mac-side export (no Apple auth); MusicKit user-token flow is the paid upgrade path; web-token bootstrap rejected (ToS/fragility).
  - Unraid host freeze root-caused (unfenced container + 366MB rich print_json); fences now structural.
Pending added:
  - Build unified priority work queue (POST /api/evaluate, preemption via file-unit granularity) then era-aware series identity (WLIIA Carey/Tyler era map + manual override) — briefs in librarian-plan §15a.
  - Wanted-list dedupe/kind filter; deploy-script readiness wait; 9.1b Discogs concordance + goldens; Newznab music searches.
Next:
  - New session: check resolve-tranche-1 + artwork backfill results on the box, then work queue → era map (session-start prompt provided in chat).
--- END BLOCK ---

### 2026-07-09 — Fix-session continuation: FX-15/16 done, spine files removed, acceptance test + harness re-run GREEN

--- SESSION BLOCK ---
Date: 2026-07-09
Agent: Claude Fable 5
Machine: Personal MacBook Pro
Surface: Claude Code (Mac desktop app)
Project(s): 19-workspace-brain — same-session continuation on Sean's go-aheads.
Artifacts:
  - workspace_validation-report_v2.0_2026-07-09.md — post-fix compare scorecard (both v1.0 FAILs → PASS by execution)
  - workspace_version-register_v1.1_2026-07-09.md — supersedes v1.0
Decisions:
  - 14-variable-icon-font-generator profile = centric-design (Sean: code-based but generates design assets).
  - Home-dir spine files removed on Sean's confirm (byte-identical copies retained in ~/.project-spine/exports/).
  - FX-16 resolved as option A: ABI line is the ritual block's first line (CLAUDE.md + brain.mdc).
  - Harness re-run right-sized: fresh headless Phases 0–1 + carried-forward PASSes, honesty strip says so.
Pending resolved:
  - FX-15 (standards externalized: preferences + davinci-ds-boilerplate + nexus-monorepo-playbook, indexed).
  - FX-16 (ritual ABI). Harness re-run. Live Phase-A acceptance test (GREEN — note: CLI auth is separate from Desktop; `claude login` was the missing step).
Next:
  - Sean: paste beacon into 4 chat surfaces + --ack-chat (steps given in-session); machine installs on Work MBP/Windows when at those machines.
  - Residuals R1–R3 in report v2.0 — none actionable now.
--- END BLOCK ---

---

### 2026-07-09 — Workspace fix session: FX-1..FX-14 applied (machine layer, dispatcher, triggers, standards, knowledge)

--- SESSION BLOCK ---
Date: 2026-07-09
Agent: Claude Fable 5
Machine: Personal MacBook Pro
Surface: Claude Code (Mac desktop app)
Project(s): 19-workspace-brain (new standing home, FX-13) — applied validation findings FX-1..FX-14 per Sean's sign-off prompt; launched from the workspace ROOT; project dispatcher fired at boot (the fix prompt's first test, passed).
Artifacts:
  - (none in 05-artifacts — deliverables are the fix(FX-n) commit series 3729472..870d992 + audit-log per-FX outcomes)
Decisions:
  - ~/.claude/CLAUDE.md is now the doctor-managed beacon; the 12.6KB pre-beacon global standards backed up machine-locally, externalization = FX-15 (pending).
  - Workspace-work sessions get a standing project home: 07-projects/19-workspace-brain (git-tracked; framework #08 rule).
  - Single-source rule: dispatcher curated tables own cross-source routes; CLAUDE.md/workflow-patterns tables are illustrative mirrors.
  - Trigger-routes.md extraction deferred (authority just consolidated in dispatcher; don't churn twice in one day).
  - Bare `hooks` trigger deliberately NOT added to hooks-contract (React-hooks collision) — deviation from report FX-11 wording, per FX-3's own principle.
Pending added:
  - Machine-layer installs on Work MBPs + Windows (incl. one verified post-migration Windows session).
  - Validation-harness re-run to compare scorecards (pre-req: Claude Desktop re-login — OAuth 401 blocked the live headless acceptance test).
  - FX-15 externalize pre-beacon global design standards into the workspace.
  - FX-16 reconcile ritual-token ABI ([workspace: LOADED …]) with the CLAUDE.md ✓-ritual (in-workspace sessions otherwise log MISS).
  - FX-8 deferred half: tool-neutral trigger-routes.md extraction.
Pending resolved:
  - Run the workspace fix session (FX-1..FX-14) — all 14 committed or explicitly deferred; per-FX outcomes + shas in audit-log 2026-07-09 entry.
Project status changes:
  - 19-workspace-brain: (new) → Active.
Next:
  - Sean: re-login Claude Desktop (OAuth), confirm 14-variable-icon-font-generator profile (provisional centric-engineering), confirm spine-file relocation (~/CLAUDE.md + ~/AGENTS.md byte-identical to ~/.project-spine/exports/), then harness re-run.
--- END BLOCK ---

---
