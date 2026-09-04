# SESSION-STATE — LCARS Generative Interface

_Last updated: 2026-09-03 — session-end after Onori rails + off-system lint_

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

- **TL;DR (for future agent)**: Live T3 from pack catalog (`src/catalog/system/`). App `main` @ `a133bb4` (ahead 2, not pushed): pack catalog + off-system ESLint (`npm run lint`). Capture via workspace `vqa capture`. Literal SYS47 separate. Isolation: `--assistance off`. Pills=controls; spine=bars; 8px family / 24px groups.
- **Current focus**: Session closed. Next = `personal:SEA-33` live T3 review.
- **Working set**:
  - App: catalog + `LiveDisplay.tsx` + `eslint/off-system/` @ `a133bb4`; `scripts/capture-sys47.mjs` → workspace vqa
  - Vault: `docs/content-groups.md`; prove via `03-skills/visual-prove-engine/vqa.py`
- **Last action**: Session-end. Off-system lint landed (`a133bb4`). Cursor Grok 4.6 / Cursor / Personal MBP.
- **Next action**: `personal:SEA-33` — review `?surface=live` vs pack catalog. Push app only if Sean asks. Do not construct from flattened plates. CSS hex in `renderers.css` / `shell.css` still out of JS lint scope.
- **Open decisions**: "Matches Literal" measured within 19-cue A-altitude contract. Residuals named, not closed. Coverage 0.8421 (3 attested).
- **Blocked on**: nothing for catalog/lint; Ruffle/JPEXS needs approve if motion resumes
- **In-flight / do-not-touch**: app in snds/LCARS; vault design authority; do not treat SWF/AI as Literal overrides; leave untracked `CLAUDE.md` unless Sean wants it
- **Agent thread**: Pack catalog → Onori rails/lint → session-end. Cursor Grok 4.6 / Cursor / Personal MBP.

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

- **Branch (app)**: `main` @ `a133bb4` (2 ahead of origin; not pushed)
- **Vault**: `main` (this session-end commit). SWF dumps remain local untracked.
- **Test state at last check**: `vitest` 65/65 + `npm run lint` green (2026-09-03). Literal residuals still unmeasured.

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

- **Currently in progress**: structured live T3 review; Literal residuals still open
- **Pending questions**: Prefer System47 vs Titan as first screen?
- **Blocked on**: none for the catalog landing

---

## History (append-only)

### 2026-09-03 — Pack catalog + composed live T3

- Sean: work in vectors, not per-pixel. Then a DS pass: components, variants, layouts, refine the demo.
- App `e691dec`: `composeLiveT3()` from `src/catalog/system/`. Pills = controls; spine = bars; aesthetic = barcode + hairline. T3 pocket vs control cluster vs focal vs footer.
- Vault: `content-groups.md` gained `support.controls` + variant note. `docs/COMPONENT-SYSTEM.md` is the pack catalog.

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
