# SESSION-STATE — Legion (13-legion)

_Last updated: 2026-06-14 — galaxy redesign + full local-map iconography shipped (PRs #25–#57, all live); now opening the Gaia-DR3 galactic star-catalog map._

> **Live handoff moved (2026-09-23):** active Legion work is the Independent Planet Lab —
> read [docs/planet-lab-independent/SESSION-STATE.md](docs/planet-lab-independent/SESSION-STATE.md) first.
> The history below is the 2026-06-14 galaxy-map baton, kept for context.

---

## Current focus (2026-06-14) — supersedes the 2026-06-12 "Open work" below

**Active task:** Build a Gaia-DR3-style navigable galactic star-catalog map. Reference: [valhovey.github.io/gaia-mary](https://valhovey.github.io/gaia-mary/) (Project Hail Mary fan map). Requirements from Sean:
- As the camera zooms out, **categorize/highlight a region of space** (gaia-mary uses a red wireframe box) and show nearby systems with **simple angled-pointer name labels off their star**.
- **Generatively define additional stars** — catalog names + positions from public stellar surveys — to fill the whole galaxy; let the user **plot a course to a distant system**.
- A **multitiered grid overlay**, emulated but **hideable**.
- Keep the curated systems **photorealistic**; DR3 systems are **generatively generated**. Use real space-agency data for stellar type and likely planet count/types where available (real exoplanet-occurrence stats).

**Key engineering insight:** Legion already ships the **HYG v3.8 catalog (24.9k real stars** w/ true 3D positions), built by `scripts/build-star-catalog.mjs` — but the binary currently keeps only `[x,y,z,mag,B−V]` and **drops the name / HIP / HD / Gliese / spectral-type columns HYG already contains**. Enrich that extract (and generate beyond it) rather than ship Gaia DR3 wholesale (1.8 B rows). Existing `src/data/star-catalog.ts` has the 16 curated nearby systems; `src/data/cosmic-objects.ts` has placeholder nebulae/megastructures.

**Data strategy (confirmed 2026-06-14 — see memory `decision-commercial-data-licensing`):** commercial-licensing is now a STANDING policy for all work. Star base = **HYG/AT-HYG (CC-BY-SA, commercial-OK)**; **avoid Gaia DR3 catalogue (CC-BY-NC)** — use only its science (occurrence rates) as method, reconcile later if its data is ever truly needed. Backfill real planets from the **NASA Exoplanet Archive (public domain, commercial-OK)** for host stars with known planets; generate the rest from spectral type. **Galactic-map data layer shipped (PRs #58–#60):** Phase 1 — `public/star-systems-v1.json` (3,081 navigable systems ≤25 pc, real names/designations/spectral types) + `star-systems.ts` loader; Phase 2a — `system-gen.ts` deterministic generator (spectral type → stellar params + planets, Kepler-grounded occurrence trends, 12 tests); Phase 2b — `build-exoplanets.mjs` → `public/exoplanets-v1.json` (NASA Exoplanet Archive, 314 hosts/525 planets, public domain) + `exoplanets.ts` cross-matcher + `resolveSystem()` (203 catalogue stars get REAL planets, rest generated). Regenerate data: `node scripts/build-star-catalog.mjs && node scripts/build-exoplanets.mjs`.

**PIVOT (2026-06-14): scale unification before the star-map rendering.** Sean's call — the local "neighbourhood" is a microcosm of the galaxy; the galaxy IS the tiling of neighbourhoods, so the 3 mutually-inconsistent compressed scales (1 AU=10 / 1 ly=220 / 1 kpc=333 WU, ~10⁶× apart) must be FIXED, not cross-faded. Target (vetted by the project's own research, `docs/space-engine-techniques-for-legion.md` §3.4 + a 5-agent map/design workflow): **ONE metric (1 pc = 1000 WU everywhere) + float64 authoritative coords + per-frame floating origin + sector tiling + catalogue-pinning/procedural-fill.** Plan of record: **`docs/scale-unification-plan.md`** (in the Legion repo) — 6 phases + Sean's confirmed decisions.

**Sean's confirmed decisions (2026-06-14):** (1) re-pin curated stars to REAL sky positions — YES (player-visible). (2) body visual inflation → configurable in UI + re-modelled: 1:1 at/near a target, ramping to ~1.25× at outer-system, onset ~Oort distance (inverts today's 8×-close→1×-far); tune later. (3) interstellar density = local-neighbourhood density ±20–25% per sector; galaxy-visual LOD = near-camera TRUE particles + far volumetric raymarch (cloud approximation), luminance handed off at the seam.

**Next action:** **Phase 0 SHIPPED (PR #61)** — scale constants collapsed into `src/core/metrics.ts` (byte-identical; legacy + unified WU_PER_PC=1000 target). **Phase 1 SHIPPED (PR #62, deployed green):** `src/data/curated-systems.ts` = canonical `CURATED_SYSTEMS` (16 nearby stars, REAL heliocentric pc baked from the 25-pc HYG catalogue, matched by designation); `SOL_GAL_PC`(8300pc)/`REGIONAL_WU_PER_PC`/`galPos()`/`regionalScenePos()`; `STAR_SYSTEMS` derived from it; **regional markers re-pinned to real geometry** (ε Eri at origin, Sol 2308 WU, Ross 154 farthest 3874 WU; sector orb 3000→4200). **Adversarial-review workflow caught a blocker:** re-pinning `Position` to real WU emptied the star-graph — `buildStarGraph(…, 15)` linked within 15 *fictional-cube units*; closest real pair is ~352 WU → 0 edges. Fixed via `NAV_LINK_WU` (14 ly; MST longest edge 9.3 ly → 69 edges, prior density, connected); `pathfinding.test.ts` guards it. Also added a ground-truth test (each `solPc` vs catalogue JSON). 43/43 vitest. **GENERAL GOTCHA:** any coordinate-frame/scale change must re-audit *unit-bearing thresholds* (link ranges, radii, LOD breakpoints), not just the coords. **Phase 1 scope boundary:** galactic tier (`galaxy.ts GAL_SYSTEMS` / frozen `galaxy-density HOME_POS`) **deferred to Phase 2** — moving `HOME_POS` shifts the whole galaxy group/disc-AABB/skybox.

**Phase 2 — DECOMPOSED into 2a/2b/2c after a 5-agent architecture sweep (2026-06-22).** Key map findings (durable design grounding for 2b/2c): (1) the doc prescribes **NESTED frames** (galactic pc → system AU/km → planet m), NOT a flat 1pc=1000WU — the system tier + the galaxy-density model **keep their own local frames behind the broker**, which massively de-risks (no rescaling the density model). (2) `camDist`/zoom/orbit math is the **navigation UX layer, orthogonal** to the metric — the broker inserts UNDER the placement layer; keep `data.camDist` meaning "scene-WU orbit radius" (minimal blast radius, ~20 consumers unchanged). (3) Floating-origin BLOCKERS: the **disc-volume shader** holds absolute-world `uBoxMin/uBoxMax/uGalaxyOrigin` + `ro=cameraPosition` (must go per-frame camera-relative); the **camera** is absolute-positioned (`cam.pos=focus+dist·dir`) and **tracking reads `getWorldPosition`/matrixWorld** (must read the f64 store); **camera velocity** from cam.pos delta collapses under re-root (use f64 delta). (4) The galactic merge is **inseparable from the broker** (galPos at 1pc=1000WU → home at 8.3M WU, float32-dead without the floating origin) AND **must NOT re-derive the frozen `HOME_POS`** (it bakes the density-model CI snapshot/GLSL `GD_HOME`/RIFT_CLOUDS/flare/DUST_NORM) — keep HOME_POS frozen, re-point only marker placement. Full map: workflow `wcjekau59` output.

- **2a SHIPPED (PR #63, deployed green):** visual-inflation re-model (decision 2). `getEffectiveScale` inverted to **1:1 close → ~1.25× outer-system/Oort** (was inflate-close/1×-far). `visualScale`→`visualInflation` VP key (default 1.25; rename sidesteps a stale-persist migration), ramp window 20→100 AU, settings slider 1×–2×, dead `isInSolarSystem` removed. Single `renderSyncSystem` consumer; obj.scale only (positions untouched). `scale-manager.test.ts` (5 tests). 48/48 vitest. Live-verified scale.x 1.0@68WU → 1.25@3014WU.
- **2b (frame broker + floating origin) — sliced via a 3-design + adversarial-vet workflow (`wvcfnqigg`) into 2b-0..2b-4. WINNING DESIGN = "R≡0 identity policy, camera NOT moved":** keep the rebase R≡(0,0,0) and DON'T relocate the three.js camera to origin in 2b → sidesteps every hazard (bg star-shell tear-off, velocity collapse, lensFlare detach, raycast invariants) AND makes the neutrality gate a hard **0-ULP equality**, not a fuzzy SSIM tolerance. 2c flips R≡0→R=camWorld (one line) + swaps GAL_SYSTEMS→galPos.
  - **2b-0/1 SHIPPED (PR #64, deployed green):** `sceneRoot` Group (all 5 layers + 5 loose objects re-parented under it, at origin = math no-op; lights stay on `scene`); dormant `Broker` singleton in scale-manager.ts (`getTierRoot`/`getSceneRebase`/`beginFrame`, `FLOATING_ORIGIN_ACTIVE=false`, galactic origin seeded from −HOME_POS); `getGalaxyOffset()` now delegates to `Broker.getTierRoot('galactic')` (byte-identical −HOME_POS). `floating-origin.test.ts`: Broker tier-roots + a **0-ULP bare-graph mirror** (real three.js in node — sidesteps the jsdom blocker the adversary found: `createScene` needs window, `createGalaxy` needs document). 55/55 vitest. Live: sceneRoot@(0,0,0), galaxy world pos = exactly −HOME_POS, no visual change.
  - **2b-2 SHIPPED (PR #65, deployed green):** `updateGalaxyFrame()` (galaxy.ts) refreshes the galaxy group position + disc-volume AABB/origin (`uBoxMin/uBoxMax/uGalaxyOrigin`) per frame from `Broker.getTierRoot('galactic')`; `Broker.beginFrame(focus)` pinned right after `camCtrl.update` (main.ts), before all world-space consumers (single-R-per-frame). `DISC_RADIUS_WU`(=15·KPC=4995)/`DISC_Y_HALF_WU`(400) promoted to module consts (shared w/ updater). Idempotent under R≡0; live-verified group pos = exactly −HOME_POS, disc uniforms = origin ± (4995,400,4995) = byte-identical to the old build box. 55/55 vitest. (NOTE: the disc box half-extent is 15·KPC = **4995**, not 5000 — the "5000 WU" code comment is rounded.)
  - **2b-3 SHIPPED (PR #66, deployed green):** camera velocity → `_trackVelocity(dt)` from the f64 anchor (`cam.position + R`) in both orbit+flight branches (R≡0 → bit-identical; survives 2c camera relocation). `uPlanetCenter` (atmosphere/ring/surface-ring-shadow, objects.ts) now sourced from `group.getWorldPosition()` not local `group.position` — fixes the adversary MAJOR (`ro=cameraPosition−uPlanetCenter` 2c desync). `sunDir` stays local (frame-independent direction). Tracking read annotated for the 2c f64-store requirement. 55/55 vitest. Live: every written uPlanetCenter = planet world pos (3 uniforms on ringed Niflheim); no visual change. camera.ts→scale-manager: no import cycle.
  - **2b infrastructure now COMPLETE** (broker + sceneRoot + per-frame galactic frame + anchored velocity/uniforms, all R≡0-neutral & proven). **2b-4 = optional hardening** (negative test proving the 0-ULP gate has teeth; a R≠0 plumbing sanity test) — low urgency since `floating-origin.test.ts` already runs as the vitest gate. FULL design+adversary in workflow `wvcfnqigg` output.
- **★ 2c IS NOW UNBLOCKED — the visible-seam fix the user cares about (see the `2c =` bullet below + plan §"The visible seam").** It's the BIG player-visible change: flips `FLOATING_ORIGIN_ACTIVE=true` (R=camWorld), activating the camera→origin relocation + its deferred hazards (bg star-shell must follow camera, lensFlare hardcoded starOrigin=(0,0,0) main.ts, both camera code paths incl. flight early-return), AND collapses the regional neighbourhood into the unified galactic frame at real galPos. Deserves its own design pass (like 2b got) — it's high-risk + the first time the floating origin actually moves.
- **2c = THE visible-seam fix (Sean flagged it 2026-06-22 from a sector-tier screenshot: the whole Milky Way appeared ~same size as the 10-ly neighbourhood ring).** ROOT CAUSE: two incompatible frames — neighbourhood 1 ly = 220 WU vs galaxy 1 ly ≈ 0.10 WU (1 kpc = 333 WU) = **~2,150× mismatch**, colliding at the sector→arm crossfade. FIX: **collapse the REGIONAL neighbourhood tier INTO the unified galactic frame** at real `galPos()` (NOT just the GAL_SYSTEMS landmark merge — that was my earlier under-scoping). Then the neighbourhood is a speck deep in the Orion Spur; disc model scaled/placed by the broker to read at true proportions (internal 333-WU/kpc calibration stays frozen — no HOME_POS re-derive). `getGalaxyOffset`'s 3 consumers (main.ts group pos, galaxy.ts AABB, visibility.ts Sgr A* focus) move to the broker atomically. Decide the 5 GAL-only systems (Proxima/Ross128/TRAPPIST-1/Luyten/Lacaille 9352) — add to curated w/ real HYG pc, or keep as fictional landmarks.
  - **CONFIRMED 2026-06-22:** (a) browsing = **dive-in / continuous zoom** into the spur until labels resolve — NO magnified "you-are-here" inset (that re-introduces a scale lie); (b) sequencing = finish the neutral broker (2b-2/3/4) first, THEN 2c; (c) far-field LOD = **near stars = true particles, far galaxy = volumetric raymarch cloud** (billions of stars never drawn as particles — Sean's explicit point, and the resolution to "do we rescale the density model"). Convergence trace is now durably in `docs/scale-unification-plan.md` § "The visible seam — why it looks wrong today, and how the phases remove it".

Then Phase 3 (re-derive getCamDist + all ~20 legacy-WU thresholds: FOV curve, galaxy LOD, heliopause swap, reference-ring, HUD unit readout, streak gate), 4 depth partitioning (drop logarithmicDepthBuffer), 5 sector tiling + procedural fill. THEN the gaia-mary star-map rendering (markers/angled labels/region box/grid/course-plot) resumes on the unified scale.

## Repo reality since 2026-06-12 (the detailed "Open work" further down is HISTORICAL)

All merged + live at https://snds.github.io/legion/ (Sol: `?system=sol`; stats: `?stats`). Highlights, PRs #25–#57:
- **Touchscreen** support (iPhone/iPad); graphics **Settings panel** (chromatic aberration / film grain / bloom / vignette / backdrop / SMAA / photographic-sky — localStorage-persisted).
- **Galaxy redesign**: analytic emission–absorption raymarch over the shared density model; FBM-ridge spiral arms (defined-but-soft, particle falloff); **Galaxy Lab** live-tuning dev panel (🌌 LAB button); NASA SVS Deep Star Maps **photographic skybox** (dimmed 0.55→0.28); π-yaw galactic-centre alignment; HYG star field kept (complementary to the photo).
- **Heliopause orb** → external-facing only (BackSide + camDist gate; was tinting the interior); **time default → 1×**.
- **Local-map iconography arc** (the headline): heliopause icon hand-off (solar-system icons cross-fade into star-system markers; **Sol selectable + navigable**); out-of-plane **stems** to the reference plane; **context-styled markers** (home/bobs/explored/uncharted shape+colour) at **distance-accurate positions**; **label legibility** (dark halo + bold) + screen-space **declutter** (collision + priority); **cosmic object types** (nebula / Dyson sphere / Dyson swarm / megastructure + placeholder entities); **view-radius readout** (◎ AU/ly/kpc, honest per tier); **labelled reference scale ring** on the plane.
- **CI**: GitHub Actions bumped off Node 20 (checkout/setup-node v6, configure-pages v6, upload-pages-artifact v5, deploy-pages v5) ahead of the June 16 cutoff.

**Recurring process note:** branch BEFORE committing — a few commits landed on local `main` this run and needed `branch X; reset --hard origin/main; checkout X` recovery. Each change ships as branch → PR → squash-merge → Pages deploy.

---

## Current state

### Environment
- **Context profile**: `personal-solo` — Legion is a personal repo (`snds/legion`); set 2026-09-24.
- **Machine**: Personal MacBook Pro (`Voyager-2.local`)
- **OS context**: macOS, Darwin 25.4.0
- **Workspace root (design/context only)**: `/Users/snds/Library/CloudStorage/GoogleDrive-hello@snds.design/My Drive/Claude Workspace/`
- **Workspace project folder**: `[workspace root]/07-projects/13-legion/` — now holds **only** `Reference/`, `Screenshots/`, `Video/`, `Visual-Development/`, `docs/`, and this file
- **Code project root**: `/Users/snds/Projects/Legion/` (standalone, outside the workspace)
- **Remote**: https://github.com/snds/legion (**PUBLIC** as of 2026-06-11 — flipped to enable free GitHub Pages)
- **Live demo**: https://snds.github.io/legion/ (Sol system: append `?system=sol`; profiling overlay: append `?stats`)

### Active servers and processes
- **Dev server**: `npm run dev` (Vite) from `/Users/snds/Projects/Legion/` — not running at the moment
- **Build process**: `npm run build` → `tsc && vite build`
- **Test runner**: none configured yet
- **Other**: none known

### VCS state
- **Branch**: `main`
- **Last commit**: `a447bd6`+ — Phase 2 series (auto-exposure / Karis bloom / AA reorder merges)
- **Author identity**: `570874+snds@users.noreply.github.com`
- **Uncommitted changes**: clean
- **CI/CD**: `.github/workflows/deploy-pages.yml` — builds Vite app (`BASE_PATH=/legion/`) and deploys to GitHub Pages on every push to `main`. Workflow rhythm in use: branch → implement → `npm run build` → browser-verify (preview tools) → commit → PR → merge → watch deploy.
- **Test state**: no unit-test runner yet; verification is build + in-browser (preview MCP). NOTE: keep a per-resume habit of **branching before committing** — twice this session a commit landed on local `main` and needed a branch-from-HEAD + `reset --hard origin/main` recovery (no history damage, but avoidable).

### Work completed 2026-06-11/12 (8 PRs, all merged + live)
- **Research**: `docs/space-engine-techniques-for-legion.md` — durable SpaceEngine-class techniques reference (scale, orbits, visual stack, gap analysis, phased roadmap). Load it before any render/sim work.
- **PR #1** CI → GitHub Pages + subpath-safe `asset()` helper (`src/core/assets.ts`).
- **PR #2** Phase 0: Kepler fix (n=√(μ/a³), full Ω/ω/i rotation), shader-clock wrap, fixed-timestep accumulator (`src/main.ts`), stats-gl profiling (`?stats`).
- **PR #3** Phase 1a: `src/core/time.ts` `et` master clock (TDB s past J2000); canonical SECONDS unit; real orbital periods; generous warp (system table → YR/S); real Gregorian HUD calendar.
- **PR #4** Phase 1b: `src/data/jpl-ephemeris.ts` real JPL elements for Sol planets at epoch.
- **PR #5** Phase 2a: AgX tone mapping (replaced ACES).
- **PR #6** Phase 2b: `src/render/auto-exposure.ts` — center-weighted log-average metering, asymmetric eye adaptation, frame-skipped readback.
- **PR #7** Phase 2c: `src/render/bloom.ts` — threshold-free Karis mip bloom (replaced UnrealBloomPass).
- **PR #8** Phase 2d: AA pass reorder — SMAA post-tonemap, film grain last (fixes grain amplification).
- **PR #9** Phase 3a: planetshine — moons lit by parent's reflected light (`uBounce*` in `planet-surface.ts`; `objects.ts` per-frame, nearest-planet bounce, scale-invariant). Tasteful `PLANETSHINE_GAIN 2.5 / MAX 0.22`.
- **PR #10** Phase 3b: analytic ring shadow on the planet (Saturn) — fragment→sun ray ∩ ring plane in `planet-surface.ts`; ring normal from axial tilt + scale-converted radii in `objects.ts`; reuses VP `ringShadowStrength` (0.85). No shadow maps.
- **Post chain now**: RenderPass → AutoExposure → NaNSanitize → KarisBloom → (lensflare) → CA → Vignette → ColorGrade → OutputPass(AgX) → SMAA → FilmGrain.
- **Verification habit**: dim/geometry-dependent shader effects (planetshine, ring shadow) verified by a temporary high-gain "mechanism test" (crank strength → confirm it projects correctly → revert to tasteful), since the headless preview throttles rAF and can't easily frame far bodies (Saturn). 10 PRs total, all merged + live.

### Active tooling / MCP bridges
- **Desktop Commander**: live (workspace)
- **Playwright MCP**: available, not connected this session
- **Figma MCP**: not applicable to Legion
- **Other MCP connections**: none active

### Configuration in use
- **Config files active**: `vite.config.ts` (path aliases for `@core`, `@render`, `@simulation`, `@persistence`, `@audio`, `@network`, `@ui`, `@data`; manualChunks for three/audio/ai/persistence), `tsconfig.json`, `package.json`
- **Design token version**: n/a (game project, not DS)
- **Framework config**: **Three.js r0.171** (not r128 — earlier docs were stale), TypeScript 5.9, Vite 6.4, ES2022 target. WebGPU production-ready (Jan 2026) but renderer currently WebGL.
- **Runtime libs**: `bitecs` (ECS), `tone` + `howler` (audio), `dexie` + `fflate` (save), `mistreevous` + `yuka` (AI/steering), `ngraph.graph` + `ngraph.path` (pathfinding), `colyseus.js` (networking, unused so far)
- **Runtime assets**: `public/textures/` (planet maps for Sol bodies, Saturn ring alpha, Crab Nebula), `Audio/Surplus of Rare Artifacts.mp3` (intro music, not yet wired), `Fonts/Berkeley Mono Variable.{otf,woff2}` (not yet wired — index.html still uses Google Fonts CDN)

### Open work and paused threads (updated 2026-06-12 PM — PRs #11–#20 all merged+live)
- **Completed this stretch**: terminator world-space fix (#11); orbit lines solid-white + element-accurate i/Ω/ω paths + Line2 hover corridor (8px screen-space) + 0.08 rest opacity (#12,#16); belt full-Lambert + multi-star uniforms (#14); planet 1a stale-enum/storm-clock fixes (#17) + 1b Jónsson limb darkening/oblateness/per-class terminators (#18); overlay Phase 1 label decoupling + stroke floors + stack-aware gating (#19); galaxy Phases 0+1 — shared analytic density model (galaxy-density.ts + GLSL mirror w/ interpolated constants) with **7/7 vitest calibration tests proving band-not-fog** from home (#20). Repo now has vitest + `npm test`. Three phased design docs in repo docs/ (galaxy redesign, planet realism, zoom overlays).
- **NEXT: galaxy Phase 2** (volume shader v2 consuming the chunk — spec §4.2–4.4: log-step march, per-channel transmittance, premultiplied blending, delete core-glow sprites) → Phase 3 (restore galaxy-backdrop.ts bake @256 steps, system-tier sky, EV-min exposure clamp) → 4 (crossfade) → 5 (star/dust coherence) → 6 (perf). Heavy per-tier visual verification each — fresh focused runs.
- **Flagged for live-eyes**: gas-giant limb darkening/oblateness on a framed Jupiter/Saturn (headless can't frame outer planets); auto-exposure foreground FPS; planetshine taste; 0.08 orbit-line rest opacity.
- **Surfaced pre-existing issues**: regional system markers all at placeholder positions ('DIST 0.0 LY') — child labels removed until positioning+clustering; selection inspector 'SMA 0 AU'; top-bar 'ε ERI SYSTEM' hardcoded.
- **Older notes (pre-#11, still valid)**: ↓
- **Phase 3 remaining**: star PSF splats (energy-conserving, blackbody color already present via `getStellarRender`); system-entry galactic cubemap bake (also frees the disc raymarch at system tier → recovers ~41fps galaxy tier); analytic eclipse occluders (alignment-dependent, harder to verify than the ring shadow).
- **Next options (user to direct sequencing)**, from `docs/space-engine-techniques-for-legion.md` §8:
  1. **Phase 3 — physical sky & light** (high visible payoff): star photometry (mag→flux + blackbody-LUT PSF splats), analytic eclipse/ring shadows + planetshine, SH ambient from a system-entry galactic cubemap bake, half-res blue-noise galactic disc raymarch (also recovers the ~41fps galaxy tier).
  2. **Deferred Phase 1 infra** (future-facing, higher risk): per-tier depth partitioning (drop `logarithmicDepthBuffer`), float64 frame broker / floating origin, warp contract + event queue. Lower current urgency — single-system demo has no jitter and runs fine.
  3. **Phase 4 — Hillaire 2020 atmosphere** (flagship, large): 4-LUT physically-based sky replacing the fresnel-shell hack.
- **Open follow-ups (non-blocking)**: foreground FPS spot-check of auto-exposure on real hardware (headless preview throttles rAF, so a clean live FPS wasn't obtainable — dials: `METER_INTERVAL`/`LUM_RES`/`.enabled` in `auto-exposure.ts`); true MSAA + fwidth edge-AA (completes §5.10); galaxy raymarch is GPU-bound (~41fps) pending the half-res optimization.
- **Pre-existing bugs noted but out of scope**: selection inspector shows "SMA 0 AU" (planet mesh `userData` carries only type/name); top-bar "ε ERI SYSTEM" label is hardcoded (doesn't reflect `?system=sol`).
- **Pending questions**: Berkeley Mono vs Google-Fonts in `index.html`; `Audio/Surplus of Rare Artifacts.mp3` intent.
- **Blocked on**: nothing.
- **What's needed to resume**: open `/Users/snds/Projects/Legion`, `npm install` if needed, `npm run dev` (preview config name "legion", port 5173). Read `docs/space-engine-techniques-for-legion.md` first. Load `legion-project` skill + relevant sub-hub. **Branch before committing.**

### Known state of external dependencies
- **Staging environment**: none
- **API versions**: n/a
- **Asset pipeline**: planet textures sourced statically; Bobiverse art direction (NASA-industrial hard sci-fi) documented in `docs/bobiverse-gdd-visual-tiers.md` and `docs/bobiverse-gdd-audio-visual.md`

---

## Session history

### 2026-06-11/12 — SpaceEngine research + Phases 0–2 implemented (8 PRs, live)

**Focus**: Research SpaceEngine's scale/gravity/visual techniques into a durable doc, then implement the roadmap — set up a GitHub Pages live-demo pipeline and work through Phase 0 (correctness) → Phase 1 (time + ephemeris) → Phase 2 (photometric pipeline), one verified PR per slice.

**Machine**: Personal MacBook Pro (`Voyager-2.local`).

**Accomplishments**:
- 23-agent research workflow → `docs/space-engine-techniques-for-legion.md` (22 verifier corrections applied, e.g. ESA Gaia→CC-BY-NC so ship AT-HYG; reversed-Z broken in three r170–174; AgX over ACES for star colors).
- Repo made PUBLIC; CI → GitHub Pages live demo (https://snds.github.io/legion/).
- Phase 0: Kepler math fix, shader-clock wrap, fixed-timestep accumulator, stats-gl.
- Phase 1: `et` master clock + canonical-seconds unit + real periods + generous warp; real JPL ephemeris for Sol. Design call (Sean): "real periods + generous warp" — planets near-static at 1×, watch them move by warping to DAY/S–YR/S.
- Phase 2: AgX, center-weighted auto-exposure (eye adaptation), threshold-free Karis bloom, AA reorder (SMAA post-tonemap + grain last).
- Decisions: keep on-rails Keplerian (SE/KSP/Elite all do); depth-partition + frame-broker deferred (future-facing, single-system demo runs jitter-free at full float32).
- A scheduled resume task (`legion-resume-phase-2b`) was created on 2026-06-11 for 8:10pm PT but didn't fire (app closed); work was resumed manually instead.

**Next resumption needs**: pick a Phase-3 vs deferred-infra direction (see Open work). Read the research doc first. Branch before committing.

### 2026-05-10 — codebase extracted to standalone repo + visual-fidelity review

**Focus this session**: Consume the new 3D skill stack + Legion project context + reference library + current build screenshots, then deliver concrete recommendations to raise visual fidelity. Separately: extract the codebase to its own git repo and GitHub home.

**Machine**: Personal MacBook Pro (`Voyager-2.local`).

**Accomplishments**:
- Reviewed Legion project context (`legion-project` skill), V1 design pillars, hard-sci-fi visual identity, and current `docs/visual-issues.md` (all 7 prior issues marked resolved).
- Surveyed `Screenshots/` (KINDLING surface, HEARTHSTONE system, galactic-view), `Visual-Development/` (target-fidelity galaxy renders), and a representative cross-section of `Reference/` (Apollo poster, Operation Black Buck infographic, Saturn-transit B&W poster, Homeworld 2, Oblivion Tet HUD, LCARS).
- Produced prioritized recommendation set across three tiers (A: highest-leverage, B: mid-effort polish, C: V2-grade ambitious), grounded in the gap between reference vocabulary and current render output. Highest-impact recs: planet atmosphere/terminator shader, halo+core star markers with Planckian stellar tinting, animated dashed connection lines, surface-tier god-rays + tri-planar PBR ground, hex glyph internal anatomy.
- **Codebase extraction**:
  - Created standalone repo `snds/legion` on GitHub (private).
  - Copied code + runtime assets (`src/`, `public/`, `Audio/`, `Fonts/`, `index.html`, `package.json`, `package-lock.json`, `tsconfig.json`, `vite.config.ts`) to `/Users/snds/Projects/Legion/`.
  - Added `.gitignore` (node_modules, dist, .DS_Store, .env, .vite, coverage) and `README.md`.
  - `git init -b main` → single "Initial import" commit (97 files, 16,354 insertions) → pushed to `https://github.com/snds/legion`.
  - Push initially rejected by GitHub email-privacy guard; re-authored with `570874+snds@users.noreply.github.com` (GitHub no-reply for the `snds` account) and succeeded.
  - Removed the moved files from `[workspace]/07-projects/13-legion/`. Workspace folder now retains only `Reference/`, `Screenshots/`, `Video/`, `Visual-Development/`, `docs/`, `SESSION-STATE.md`.
  - No workspace deletion commit needed — `07-projects/13-legion/*` was already in `.gitignore` (the system layer intentionally excludes per-project trees).
- **Routing fix for future projects**: added `[includeIf "gitdir:~/Projects/"] path = ~/.gitconfig.personal` to `00-bootstrap/setup/gitconfig.template` so any repo created under `~/Projects/` automatically picks up the personal identity (which uses the GitHub no-reply email and avoids the privacy-block class of failure). Header comment updated accordingly.

**Stopped because**: handoff point — repo live, workspace clean, template updated. Active `~/.gitconfig` on this machine (Voyager-2) still has the hardcoded `hello@snds.design` identity and no `includeIf` blocks; `setup-identity.sh` has not been run on this machine yet. The template change will only take effect once that script runs, OR once `~/.gitconfig` is manually updated.

**Next resumption needs**:
- Decide whether to run `setup-identity.sh` on Voyager-2 to activate routed identity (or accept that the template change is a future-machine fix).
- Pick a first visual-fidelity recommendation to implement. A1 (planet atmosphere + terminator) is the largest single-frame upgrade per the review.
- Optionally: switch `index.html` from the Google Fonts CDN chain to the locally-bundled Berkeley Mono variable font.

### 2026-04-21 — seed entry (no work done this session)

**Focus this session**: Seeded by framework migration session. No Legion work performed.
**Machine**: Work MacBook (`seansands.local`) — migration session only.
**Stopped because**: seed complete; file ready for next live Legion session.

**Accomplishments**:
- SESSION-STATE.md created for this project per the spec in `00-frameworks/_session-state-template.md`.

**Next resumption needs**:
- Load `legion-project` skill + relevant sub-hub per topic.
