# SESSION-STATE — LCARS Generative Interface

_Last updated: 2026-08-28 — cuespec names uncued residuals; prove engine vqa/1.1 (altitudes A–G)_

## Vault docs (this project)

- [[07-projects/20-lcars-generative-interface/README|project README]]
- [[07-projects/20-lcars-generative-interface/docs/runtime-exe-assessment|runtime-exe-assessment]]
- [[07-projects/20-lcars-generative-interface/docs/construction/runtime-swf/README|runtime-swf README]]
- [[07-projects/20-lcars-generative-interface/docs/visual-replication-requirements|visual-replication-requirements]]
- [[07-projects/20-lcars-generative-interface/docs/program-thesis|program-thesis]]
- [[07-projects/20-lcars-generative-interface/docs/vector-msd-1701d-mk4|vector-msd-1701d-mk4]]
- [[07-projects/20-lcars-generative-interface/docs/content-groups|content-groups]]

---

## Current state (rewritten atomically — no stale fields)

### Live handoff (the baton — any agent reads this FIRST, updates it on every handoff)

- **TL;DR (for future agent)**: S-SYS47-01 build v4 still measures **Matches 16/16, score 1.0, capture verified**. Cuespec now declares `default_altitude: A` and names the four uncued residuals (left rail x, mid-band geometry, navy sweep, timestamp) so 16/16 cannot silence those holes. Prove engine is `vqa/1.1` (FLIP, saliency, mesh, geometry, interact critic, photon/tracks, VLM-judge protocol; sibling `play-prove` for altitude G). Missing `renderer` on the existing capture manifest is a warning, not unverified.
- **Current focus**: cuespec v2 for the named residual zones (now first-class in the spec, still unmeasured). Motion/illustration doctrine is workspace-level ([[motion-graphic-systems]], [[gd-display-graphics]], [[gd-generation-tooling]], [[display-graphic-motion-systems]]); do not fork an LCARS-only copy. A later from-scratch recreation must emit live primitives (`generate-display-svg.py` / catalog), not `SchematicPanel` `assetSrcset` or northstar PNG cutouts.
- **Working set**:
  - App: `sys47-literal.ts` + `renderers.css` (pinned plates + mid-band rules) + `SchematicPanel.tsx` (`assetSrcset`) + `scripts/capture-sys47.mjs` (DPR 2 + manifest) + re-cropped `public/northstars/S-SYS47-01/asset_msd{,@0.5x}.png`
  - Vault: cuespec (live contract + `uncued_residuals`), `*_build_v4.prove.{json,md}`, `S-SYS47-01.ledger.{json,md}`, `captures/S-SYS47-01_build_v4.png` + `.capture.json`, `03-skills/visual-prove-engine/` vqa/1.1, `03-skills/play-prove/`
- **Last action**: Course corrections 1–12 + `/optimize` merged to workspace `main` (`0f4228a`, 2026-08-28). Session-end 2026-09-02. Cursor Grok 4.6 / Cursor / Personal MBP
- **Next action**: separate session only: from-scratch generative screen via live geometry + recursive/adversarial visual review. Do not construct from flattened plates. Also: add measured cues for the four named residuals; optional OCR on SYSTEM 47 / timestamp when tesseract is present. If local Picard/Okuda files arrive, finish the pixel pass in `05-artifacts/active/film-ui-motion-study_v1.0_2026-09-02/` (audio review already written).
- **Open decisions**: "Matches Literal" is measured within the 19-cue A-altitude contract. The residuals are named, not closed. Coverage remains 0.8421 (3 attested).
- **Blocked on**: nothing for the course-correction landing; Ruffle/JPEXS still needs approve if motion track resumes
- **In-flight / do-not-touch**: app in snds/LCARS; vault design authority; do not treat SWF/AI as Literal overrides; do not edit the 2026-08-09 matrix rows (history), extend the cuespec instead
- **Agent thread**: Instrumented prove migration 2026-08-26 → course corrections 2026-08-28

### Environment

- **Context profile**: `personal-solo`
- **Machine**: Personal MacBook Pro (`Voyager-2.local`)
- **OS context**: macOS
- **Workspace root**: git checkout of `github.com/snds/workspace` (directory containing `AGENTS.md`)
- **Project root**: `07-projects/20-lcars-generative-interface/`
- **App root**: `~/Projects/lcars-generative-interface` → https://github.com/snds/LCARS

### Active servers and processes

- **Dev server**: not assumed running (check app terminals)
- **Build process**: not running
- **Test runner**: not running
- **Other**: n/a

### VCS state

- **Branch (app)**: `cursor/lcars-generative-interface-a660` (verify with `git status` in app)
- **Vault**: `main` @ `0f4228a` (prove-engine + construction contract). SWF dumps remain local untracked.
- **Test state at last check**: `vqa calibrate` 48/48 on merge; green tests ≠ residual coverage

### Active tooling / MCP bridges

- **Filesystem access**: native (incl. Google Drive reference library)
- **Playwright MCP**: use for native build captures when proving
- **visual-qa-toolkit**: required for Literal prove gate
- **Other MCP connections**: as needed

### Configuration in use

- **Fidelity**: Literal (`NORTHSTAR.md`)
- **Design token version**: existing app tokens — must be Δe-checked against active S-ID before claiming match
- **Framework config**: Vite + React + TS + Zod + Motion + R3F

### Open work and paused threads

- **Currently in progress**: Literal recreation program; IR for S-SYS47-01 unmeasured
- **Pending questions**: Prefer System47 vs Titan as first screen?
- **Blocked on**: pixel probes / still extraction for active northstar

---

## History (append-only)

### 2026-08-09 — Composite reference library framing

- Sean: Drive EXEs→SWFs, `1701_D_Mk4.ai`, video loops, etc. guide work **in composite**; they do not replace Construction IR or override Literal acceptance. S-SYS47-01 stays Literal authority until he renames the northstar. Documented in Live handoff + `docs/visual-replication-requirements.md` / `NORTHSTAR.md` / `docs/runtime-exe-assessment.md`.

### 2026-08-09 — Vector MSD `1701_D_Mk4.ai` (static, no Illustrator)

- Drive AI file = PDF 1.6 · Illustrator 27.5 · ~5.5 MB · MediaBox ~12337×4862 pts. True vectors (551 Form XObjects, 0 images; heavy `m`/`l`/`c`). Single OCG `Layer 1` — no content-group layer map without AI. Preview + assessment: `docs/construction/references/1701d-mk4/`, `docs/vector-msd-1701d-mk4.md`. Grammar only; not S-SYS47-01 Literal.

### 2026-08-09 — Runtime EXE → Flash SWF (static)

- Six Drive MSD `.exe`s = Inno Setup + 2Flyer + Macromedia Flash SWF (DefineShape* vectors). Not System47; not Matches Literal authority.
- Assessment: `docs/runtime-exe-assessment.md`. Persisted: `docs/construction/runtime-swf/` (CWS+FWS+INI; Sovereign preferred). Ruffle/JPEXS not installed (needs Sean approve).

### 2026-08-09 — T2 content groups in Scene IR

- App: `topology: 'T2'`, regions named as content groups; mid-as-mode removed; `aestheticBar` module; elbow `variant: 'opposing'` (SVG constant stroke); SurfaceHost skips T3 greeble on T2; CSS grid areas for identity/focal/support/footer/aesthetic.
- Tests: 59 green. Literal verdict still **Partial** (no SSIM/Δe prove; callout.layer still raster-baked; elbows approx).

### 2026-08-09 — Content groups + frame topologies

- Sean: bridge curve-spines; MSD dual opposing spines; support bay numerics as node/subagent IDs; footer = minimized processes + minimap + passive aesthetic chrome.
- Documented `docs/content-groups.md`; framed `sovereign_msd.mp4` as S-SOV-MSD-01; Intent axis updated in program thesis.

### 2026-08-09 — S-SYS47-01 first Literal pass (Partial)

- Extracted 4K still t=30s; measured gutter 8px, header blue `#4f93ca`, dual header anatomy.
- App: `sys47.literal` Scene IR + layout CSS + northstar rasters under `public/northstars/S-SYS47-01/`.
- ADR-001: measured fills on Literal surface only.
- Verdict Partial — see cue matrix. Dev URL `?northstar=S-SYS47-01`.

### 2026-08-09 — Program thesis: LCARS proves transferable stack

- Sean clarified: intent is systemic/programmatic recreation that scales to other aesthetics; LCARS fidelity is the hard exam.
- Added `docs/program-thesis.md`; updated NORTHSTAR, requirements, SPEC summary, skill (four axes + system pack), findings, triggers.

### 2026-08-09 — Literal replication capability (gap → artifacts)

- Sean: craft output is a farce vs references; demand adversarial skill-gap analysis and durable artifacts so exact recreation becomes possible.
- Landed: `visual-reference-replication` skill + Construction IR schema; ledger C-03…C-08, Z-04–05; `NORTHSTAR.md`; `docs/visual-replication-requirements.md`; IR stub `S-SYS47-01`; app cursor rules for literal replication + construction grammar.
- Explicit failure: Spirit/"inspired by", VLM-as-measurement, no Construction IR, unused prove stack, constraint-driven aesthetic collapse.
- Next: measure S-SYS47-01 and Literal-implement into the live ecosystem.

### 2026-08-07 — craft / motion / schematics pass (superseded as Literal authority)

- Idle demos, motion doctrine, SVG schematics, APCA token retune in app. Sean later judged insufficient vs references.

### 2026-08-07 — v1 app complete (Tasks 1–13)

- App repo at https://github.com/snds/LCARS branch `cursor/lcars-generative-interface-a660`.
- Task 13: Antonio typography, black canvas shell chrome, README quickstart demo.

### 2026-08-07 — implementation plan

- Sean approved proceeding from SPEC to plan.
- Plan: `docs/superpowers/plans/2026-08-07-lcars-generative-interface-v1.md` (13 tasks, TDD, app at `~/Projects/lcars-generative-interface`).

### 2026-08-07 — project scaffold

- Created `20-lcars-generative-interface` via workspace new-project shape.
- Landed full design SPEC from Cloud Agent brainstorming session.
