# SESSION-STATE — Legion (13-legion)

_Last updated: 2026-10-18 — wrap-up: rewritten to the baton template; the 2026-06 galaxy-map baton and older entries moved, word for word, to [history/](history/README.md) — Claude Opus · Claude Code · Work MacBook Pro_

---

## Current state (rewritten atomically — no stale fields)

### 🤝 Live handoff

- **TL;DR (for future agent)**: Legion is Sean's Bobiverse-inspired hard-sci-fi space game: Three.js + TypeScript, personal repo `snds/legion`, live at https://snds.github.io/legion/. Two threads. The **Independent Planet Lab** has been active since 2026-09 and keeps its own baton. The **galactic star-map / scale unification** work is paused at Phase 2c (last touched 2026-06-22).
- **Current focus**: the Independent Planet Lab. Read [docs/planet-lab-independent/SESSION-STATE.md](docs/planet-lab-independent/SESSION-STATE.md) first; it is the live handoff for that experiment. Its code lives in `~/Projects/Legion/planet-lab/` (own package and local git repo) and `~/Projects/PlanetCompiler` (separate personal-solo repo), both on the Personal MacBook Pro.
- **Working set**: Planet Lab — see its baton. Galaxy map — `docs/scale-unification-plan.md` (plan of record, in the Legion repo), `docs/space-engine-techniques-for-legion.md` (read before any render/sim work), `src/core/metrics.ts`, `src/data/curated-systems.ts`, `src/core/scale-manager.ts` (the `Broker`), `galaxy.ts`, `main.ts`.
- **Last action**: 2026-10-18 — this baton rewritten to the template; nothing in the Legion repo changed — by Claude Opus · Claude Code · Work MacBook Pro. Last Legion work: 2026-09-28, Planet Lab current-camera measurement checkpoint (Codex · Codex desktop · Personal MacBook Pro). Last galaxy-map work: 2026-06-22, Phase 2b infrastructure complete (PRs #61–#66, all deployed green).
- **Next action**: Planet Lab — follow "Current next action" in its baton. Galaxy map, when Sean resumes it — Phase 2c, the visible-seam fix: flip `FLOATING_ORIGIN_ACTIVE=true` (R = camWorld) and collapse the regional neighbourhood tier into the unified galactic frame at real `galPos()`. Give 2c its own design pass first, as 2b had. To resume either: open the repo on the Personal MacBook Pro, `npm install` if needed, `npm run dev` (preview config "legion", port 5173), load the `legion-project` skill, and **branch before committing**.
- **Open decisions**: (1) 2c — the 5 galaxy-only systems (Proxima, Ross 128, TRAPPIST-1, Luyten, Lacaille 9352): add them to the curated set at real HYG positions, or keep them as fictional landmarks. (2) Berkeley Mono (bundled in `Fonts/`) vs the Google Fonts link in `index.html`. (3) What `Audio/Surplus of Rare Artifacts.mp3` is for (intro music, not wired yet).
- **Blocked on**: nothing.
- **In-flight / do-not-touch**: don't fold the Planet Lab into the main Legion code, or touch the active Legion implementation for it, without Sean's instruction. Dirty Legion changes on the Personal MacBook Pro belong to other work.
- **Agent thread**: Claude · Claude Code · Work MBP (2026-10-18): rewrote this baton, history moved out → next is Planet Lab work on the Personal MBP. Codex · Codex desktop · Personal MBP (2026-09-10 → 09-28): Planet Lab native phases 1–6. Claude · Claude Code · Personal MBP (2026-06-11 → 06-22): galaxy redesign, local-map iconography, scale unification Phases 0–2b.

### Galactic star-map thread (paused at Phase 2c)

- **Goal**: a Gaia-mary-style navigable star map (reference: https://valhovey.github.io/gaia-mary/). Region highlighting as the camera zooms out, angled-pointer name labels, generated stars filling the galaxy, plotting a course to a distant system, and a hideable multitier grid. Curated systems stay photorealistic; catalogue systems are generated from real stellar type and exoplanet-occurrence data.
- **Data, all commercial-OK** (standing policy, memory `decision-commercial-data-licensing`): HYG / AT-HYG stars (CC-BY-SA); NASA Exoplanet Archive planets (public domain). Not the Gaia DR3 catalogue (CC-BY-NC) — only its science as method. Shipped in PRs #58–#60. Regenerate: `node scripts/build-star-catalog.mjs && node scripts/build-exoplanets.mjs`.
- **Scale unification** (the pivot, 2026-06-14): one metric (1 pc = 1000 WU), float64 authoritative coordinates, a per-frame floating origin, sector tiling, and catalogue pinning with procedural fill. The plan nests frames (galactic pc → system AU/km → planet m) behind the broker; `HOME_POS` stays frozen.
- **Shipped**: Phase 0 (#61), Phase 1 (#62), 2a (#63), 2b-0/1 (#64), 2b-2 (#65), 2b-3 (#66). 2b-4 is optional hardening.
- **Then**: 2c → Phase 3 (re-derive `getCamDist` and the ~20 legacy-WU thresholds) → 4 (depth partitioning) → 5 (sector tiling + procedural fill) → the star-map rendering itself.
- **Sean's confirmed calls**: curated stars at real sky positions; visual inflation 1:1 near a target, ~1.25× out at the Oort distance; interstellar density ±20–25% per sector; dive-in continuous zoom (no "you-are-here" inset); near stars as true particles, the far galaxy as a volumetric cloud.
- **Gotcha**: any change to a coordinate frame or scale must re-check every unit-bearing threshold (link ranges, radii, LOD breakpoints), not only the coordinates.
- Full detail, word for word as it stood: [history/2026-06.md](history/2026-06.md).

### Standing notes

- **Branch before committing.** Each change ships as branch → PR → squash-merge → Pages deploy. Commits landed on local `main` more than once and needed a branch-from-HEAD + `reset --hard origin/main` recovery.
- **Verification**: build, `npm test` (vitest), then in-browser checks. For dim or geometry-dependent shader effects, crank the strength to confirm the mechanism, then revert to the tasteful value.

### Environment
- **Context profile**: `personal-solo` — Legion is a personal repo (`snds/legion`); set 2026-09-24.
- **Machine**: Personal MacBook Pro (`Voyager-2.local`) for all code work. The Work MacBook Pro has no Legion checkout.
- **Workspace root**: the git checkout (the directory containing `AGENTS.md`).
- **Workspace project folder**: `07-projects/13-legion/` — holds `Reference/`, `Screenshots/`, `Video/`, `Visual-Development/`, `docs/`, `history/` and this file.
- **Code project root**: `/Users/snds/Projects/Legion/` (standalone, outside the workspace).
- **Remote**: https://github.com/snds/legion (**PUBLIC** since 2026-06-11, for free GitHub Pages).
- **Live demo**: https://snds.github.io/legion/ (Sol: `?system=sol`; profiling overlay: `?stats`).

### Active servers and processes
- **Dev server**: `npm run dev` (Vite) from the code project root — not running.
- **Build process**: `npm run build` → `tsc && vite build`.
- **Test runner**: vitest (`npm test`); 55/55 at PR #66.

### VCS state
- **Branch**: `main` (Legion repo). Planet Lab: its own local repo on `codex/independent-planet-lab`.
- **Last recorded commit**: PR #66 squash-merged to `main`, 2026-06-22. Not re-checked since; the Work MacBook Pro can't see the checkout.
- **Author identity**: `570874+snds@users.noreply.github.com`.
- **CI/CD**: `.github/workflows/deploy-pages.yml` builds the Vite app (`BASE_PATH=/legion/`) and deploys to GitHub Pages on every push to `main`.

### Active tooling / MCP bridges
- **Preview / Playwright tools**: used for in-browser verification (the headless preview throttles requestAnimationFrame, so it can't give clean FPS numbers).
- **Figma MCP**: not applicable.

### Configuration in use
- **Config files active**: `vite.config.ts` (path aliases `@core`, `@render`, `@simulation`, `@persistence`, `@audio`, `@network`, `@ui`, `@data`; manualChunks for three/audio/ai/persistence), `tsconfig.json`, `package.json`.
- **Framework config**: Three.js r0.171, TypeScript 5.9, Vite 6.4, ES2022 target. Renderer is WebGL.
- **Runtime libs**: `bitecs` (ECS), `tone` + `howler` (audio), `dexie` + `fflate` (save), `mistreevous` + `yuka` (AI/steering), `ngraph.graph` + `ngraph.path` (pathfinding), `colyseus.js` (networking, unused so far).
- **Runtime assets**: `public/textures/`, `public/star-systems-v1.json`, `public/exoplanets-v1.json`, `Audio/`, `Fonts/`.

### Known state of external dependencies
- **Asset pipeline**: planet textures sourced statically; Bobiverse art direction (NASA-industrial hard sci-fi) in `docs/bobiverse-gdd-visual-tiers.md` and `docs/bobiverse-gdd-audio-visual.md`.

---

## Session history

_Older entries are in [history/README.md](history/README.md), the long-term tier, by month; the app's Projects timeline joins them with this file._

- **2026-10-18** — Baton rewritten to the template (Claude · Claude Code · Work MBP). The galaxy-map focus, "Repo reality", "Work completed", the old "Open work" and the three session entries moved word for word to `history/`. Stale values replaced: the old Google Drive workspace path, "Last commit `a447bd6`+", "Test runner: none configured yet", and the Desktop Commander tooling line.
- **2026-09-23** — Live handoff moved to the Planet Lab's scoped baton. See [history/2026-09.md](history/2026-09.md).
- **2026-06-22** — Scale unification Phase 2b complete (PRs #61–#66). See [history/2026-06.md](history/2026-06.md).
- **2026-05-10** — Codebase extracted to the standalone `snds/legion` repo; visual-fidelity review. See [history/2026-05.md](history/2026-05.md).
- **2026-04-21** — Seeded by the framework migration. See [history/2026-04.md](history/2026-04.md).
