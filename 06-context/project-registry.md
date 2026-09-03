# Project registry — Sean Sands
_Moved from project-context.md 2026-08-07 (harness-map rec #2 — Load later).
Session-start reads project-context stubs only; open this file when you need project narratives._
_Authoritative pending queue remains [project-context.md](project-context.md) (+ detail file)._

## Active Projects

### Workspace infrastructure
**Status:** Active — knowledge vault layer live (2026-04-29)
**Summary:** Multi-session workspace with cross-device context sync via Obsidian + Git. Workspace root is **also an Obsidian vault and an agent working directory** — every capable surface reads the same filesystem via [[AGENTS]]. Claude Code hooks are one adapter (SessionStart / SessionEnd), not the contract. Sixteen frameworks + SESSION-STATE per-project template. Skill hub/spoke network. 08-knowledge/ vault layer with three-tier surfacing.

**Layered additions across recent cycles:**
- **2026-04-25 (topology cleanup):** Restored deployed-vs-project distinction. The integration's deployed files (CLAUDE.md, dotfiles, MOCs, `.claude/`, `.obsidian/`) live at workspace root where the consuming tools expect them. Installer + Obsidian templates + integration architecture doc consolidated into existing `00-bootstrap/`. Project workspace `07-projects/00-obsidian/` now holds SESSION-STATE.md + README.md only — design history, not deployment. `.gitignore` rewritten to track only the system layer + the 00-obsidian project. Dispatcher's session-end commit simplified to `git add -A` (gitignore is now the source of truth).
- **2026-04-23 (Obsidian + Claude Code):** `CLAUDE.md`, `.claude/` (settings.json + hooks/dispatcher.py + 5 slash-command skills), `.obsidian/` (plugins, hotkeys, graph, templates), root MOCs (`_HOME`, `_PROJECTS`, `_SKILLS`, `_FRAMEWORKS`, `_CONTEXT`), `.gitignore` scoped to system layer, installer (Python stdlib-only + double-clickable wrappers + one-liner fetchers), `OBSIDIAN-SETUP.md` architecture doc. Windows hostname `Enterprise` registered in workspace-bootstrap.
- **2026-04-21 (Framework layer):** `01-frameworks/` folder with five framework docs + README + team-practices scaffold + session-state template. `workspace-bootstrap` extended with framework awareness + SESSION-STATE.md loading + Write 5 at session end. Opus 4.7+ skill audit report delivered.

**Project folder:** `07-projects/00-obsidian/` — populated 2026-04-25 with SESSION-STATE.md + README.md.

**Git remote:** `https://github.com/snds/workspace` (private). Initialized 2026-04-25; first commit pushed to `main` 2026-04-25.

**Next:** Smoke-test installer on Mac. Decide Python binary strategy. Then act on 2026-04-21 audit findings and seed remaining SESSION-STATE files.

---

### CentricSymbols Variable Icon Font System
**Status:** Active development
**Summary:** Variable icon font pipeline for Centric's design system. v0.3 architecture spec active. Four variable axes (wght, FILL, GRAD, opsz). COLRv1 for per-path opacity. Hybrid Figma plugin + local FastAPI/PyInstaller server as delivery. Seven-skill hub/spoke network (`variable-icon-font-architect` hub with 7 spokes: icon design, vector construction, pipeline engineering, 4 math skills).

**Key decisions:**
- Figma is authoring environment for default masters only (wght=400, FILL=0, opsz=24).
- Weight extremes derived algorithmically via inner boundary offset.
- Round join required for variable-font point topology compatibility.

**Next:** [Sean's call — decisions pending on GRAD axis derivation approach per SESSION-STATE.]

---

### Centric VMS Design System (`centric-ui` + `ds-docs`)
**Status:** Active — four PRs in flight (2026-07-07)
**Summary:** React 19 / Vite 7 / Tailwind 4 / shadcn-style component library for the Centric VMS platform. Repo: [cpes-software/centric-ui](https://github.com/cpes-software/centric-ui) (private). 2026-04-29: scaffolded Storybook 10 with foundation stories and split component stories into a separate PR. Stood up [cpes-software/ds-docs](https://github.com/cpes-software/ds-docs) (private, Next.js + Fumadocs) as the curated narrative layer; embeds Storybook stories via custom `<StorybookEmbed>` MDX block. Seeded with 8 foundations + 22 components (Design / Code tabs) + 4 patterns. Persistent design/code mode toggle + native foundation layouts + token-level dogfooding.

**Live PRs:**
- [centric-ui #34](https://github.com/cpes-software/centric-ui/pull/34) — Storybook setup + foundation stories. Awaiting review.
- [ds-docs #1](https://github.com/cpes-software/ds-docs/pull/1) — LICENSE + CI workflow. CI green; awaiting merge.
- [ds-docs #2](https://github.com/cpes-software/ds-docs/pull/2) — security deps: next 16.2.4→16.2.10 (13 GHSAs), postcss override, npm audit clean. Stacked on #1; opened 2026-07-07.
- [ds-docs #3](https://github.com/cpes-software/ds-docs/pull/3) — changelog hub + PageHero/KeyFacts/UseCases blocks + content sweep (the formerly-uncommitted local WIP, fixed forward to green CI). Stacked on #1; opened 2026-07-07.

**Branch protection on ds-docs `main`:** require PR + 1 review + linear history + conversation resolution; force-push and deletion blocked; admin bypass enabled.

**Stack quirks worth remembering:**
- ESLint pinned to `^9.39.3` (10.x breaks `eslint-config-next@16` — still unresolved upstream, vercel/next.js#91702).
- next hard-pins its nested `postcss` to 8.4.31 even at 16.2.10 → `overrides.next.postcss ^8.5.10` in package.json clears the audit; remove when next bumps its pin. npm quirk: overrides don't retro-apply to existing lockfile entries — delete the nested entry from package-lock + node_modules, then reinstall.
- ContentTabs uses `@radix-ui/react-tabs` directly (Fumadocs's wrapper omits `value`/`onValueChange`).
- DocMode uses `useSyncExternalStore` (avoids `setState`-in-`useEffect`).
- Storybook iframe theme sync via `preview-head.html` URL-globals parser + dark-mode body bg override (centric-ui's `@theme inline` bakes light values for CDS gray utilities, so dark mode only works through `--sem-*`).

**Admin tasks** (CODEOWNERS, required status check, deployment) are tracked as Pending Items in this file — migrated out of Claude Code local memory 2026-06-30; see memory `decision-externalize-everything-to-workspace`.

**2026-06-02 — Radix-derived color system:** re-architected the centric-ui color foundation onto **Radix Colors as source of truth** (values, 12-step context semantics, contrast) with a Tailwind-class compatibility layer (nearest-OKLCh-L aliases), APCA-as-governance (selection/audit, not primitive mutation), centric-blue replacing Radix blue, and brand-aware semantic hue assignment (info→cyan, warning→orange — no semantic context collides with the brand; collision rule ported from OMNI). New `--sem-selected` (Radix step 5) for active/selected vs neutral `accent` (hover). Built a Palette Review Storybook harness (25 components, before/after × light/dark, flagging) to drive the review. Shipped as 4 PRs (#64–67). Details in memory `project_centric-ui-radix-palette`; generator lives at `~/projects/cpes-software/centric-ui/scripts/generate-color-palette/`.

**Next:** Sean assigns reviewers on ds-docs #2 + #3 (2026-07-07). ds-docs merge order **#1 → #2 → #3** (CI only triggers on PRs targeting main, so #2/#3 checks appear after #1 merges and GitHub retargets them). After ds-docs#1 merges → mark CI status check required. After centric-ui#34 merges → open the centric-ui PR with the staged component stories. Review/merge the Radix color-system PRs #64–67 (tokens→components→harness).

---

### Centric 8 PLM Design System (`cds-docs`)
**Status:** Active — scaffold complete, content sprint pending
**Project root:** `~/projects/c8-plm/` (outside Drive — see stub at [07-projects/05-C8-PLM/README.md](../07-projects/05-C8-PLM/README.md))
**Summary:** Fumadocs documentation site for the **Centric Design System (CDS)** that powers the **Centric 8 PLM** monolith — `@centricsoftware/design-system` v1.3.0-develop-13 on Bitbucket (`centricsoftware/design-system`). Parallels the VMS-side `cpes-software/ds-docs` site that shipped 2026-04-29; same scaffold (Next.js 16 + Fumadocs + Tailwind 4 + custom MDX blocks + DocMode toggle), retargeted at C8's design system.

**2026-04-30 milestone:** Scaffold spun up at `~/projects/c8-plm/cds-docs/`. 8 foundation MDX with real ported content (colors, typography, icons, sizes, validation, z-index, theme — sourced from `CDS/src/stories/*.mdx`). 59 component stubs in atomic IA (19 atoms + 18 molecules + 22 organisms — mirrors `CDS/src/components/{atoms,molecules,organisms}/`). `npm run lint`, `types:check`, `build` all green; build emits 222 static pages.

**Stack quirks worth remembering:**
- Next.js + Turbopack rejects symlinks that resolve outside the project root (`Symlink [project]/node_modules is invalid`). `node_modules` and `.next/` must live inside the project tree. Drive sync of those dirs is incompatible with the build pipeline — hence the project is at `~/projects/c8-plm/`, not in Drive.
- Same ESLint pin as VMS ds-docs: `^9.39.3` (10.x breaks `eslint-config-next@16`).
- Component IA differs from VMS: atoms/molecules/organisms (mirrors CDS source layout), not the functional primitives/inputs/layout/overlays/feedback grouping VMS uses.
- CDS itself uses **system fonts** (`-apple-system, BlinkMacSystemFont, ...`) and **Material Symbols** for icons — different from VMS's Inter Variable + Lucide. The docs site chrome still uses Lucide; only documented foundations reflect CDS's system.

**No GitHub repo / no CI / no deployment yet** — building in isolation until write access to `centricsoftware/design-system` is granted on Bitbucket.

**Next:** Decide content-fill order for the 59 component stubs (suggestion: most-used first — Buttons, Inputs, Select, Tabs, Modal, DataTable, Card, Tooltip, Icon, Text — then sweep the rest). Add `metadataBase` to layout to silence the build warning about social-card image URLs.

---

### Centric PLM Design System Work
**Status:** Active — multi-thread
**Summary:** Cross-framework DS strategy for Centric PLM serving fashion, food, and product verticals. Primary threads:
- Data table documentation (90+ tables audited, Dojo/dgrid legacy → TanStack Table modern).
- Token architecture across frameworks (Vue primary, React/Angular adapters).
- Cross-framework DS strategy (Ark UI recommended as headless foundation).
- Greenfield PLM SaaS redesign architecture exploration.

**Active Figma files:**
- Core Design System (file key: `sgsaBIZBVNjuoBDTwqZlhd`)
- Components (file key: `pyYokK7ajFtPgeQAKfjIZd`)
- Research FigJam: `RWJnQG5MLStvN7JfEllnWZ`
- Visual research board: `PuCufvvSxifLafOxHwQeMp`

**Next:** Data table cell anatomy + state matrix. Component spec work.

---

### SaaS PLM Knowledge Base (`knowledge-discovery`)
**Status:** Active — reference / consumed (cloned 2026-07-20)
**Repo:** [saas-plm-analysis/knowledge-discovery](https://github.com/saas-plm-analysis/knowledge-discovery) (private, org-owned)
**Local path:** `<Projects>/saas-plm-analysis/knowledge-discovery` — outside this workspace per the "codebases live in Projects" core rule. Full detail in memory [[reference-saas-plm-knowledge-discovery]].
**Summary:** Centric's cross-role knowledge base for the new SaaS PLM platform — legacy C8 domain
extraction mapped to target SaaS configuration, plus PM requirements, UX research, UI specs, engineering
architecture, ADRs, and a machine-consumed `ai-knowledge/` layer (patterns, legacy→new mappings, golden
examples, decision log). Agent-aware: its own `AGENTS.md` domain taxonomy, an `INDEX.md` in each of 62
directories (open the local INDEX before loading leaf files — the repo's own rule), 8 `.cursor/rules`, and
4 `.cursor/skills`.

**Why it matters here:** it is the employer-side domain source of truth that sits underneath the
`centric-ui` / VMS design-system work. `ui/design-system/` and `ux/` overlap Sean's DS threads directly —
cross-read them, never copy content across the personal/employer boundary in either direction.

**Next:** [Set when first substantively used — likely cross-reading `ui/specs` + `ux/flows` against the
centric-ui component work, and the `ai-knowledge/mappings` layer against the C8→SaaS migration threads.]

---

### Centric UX Research (Multi-Vertical)
**Status:** Active — research / analysis
**Summary:** User research across Fashion, Food, and Product Engineering verticals to derive scalable workflow models. FigJam boards and enterprise persona sets as recent deliverables.

**Operating layer:** Research and Evidence Framework (04) is the primary lens. Median persona test applied per vertical (don't collapse across verticals).

**Next:** [Captured per SESSION-STATE when project resumes.]

---

### Legion (Game Project)
**Status:** Active — V1 prototype + standalone repo
**Summary:** Interstellar hard sci-fi game inspired by The Bobiverse. Factory management × 4X strategy × RTS × narrative core. Tech stack: Three.js + WebGPU (TypeScript + GLSL).
**Code home:** `/Users/snds/Projects/Legion` → `https://github.com/snds/legion` (private). Extracted from workspace on 2026-05-11; design refs (Reference/, Screenshots/, Video/, Visual-Development/, docs/) remain in workspace at `07-projects/13-legion/` alongside SESSION-STATE.md.

**Skill set (12 skills):** `legion-project` (foundation) + `lead-game-designer` / `lead-art-director` / `lead-game-developer` (hubs) + `threejs-materials-master` / `glsl-shader-architect` / `threejs-vfx-atmosphere` / `webgpu-advanced-rendering` + the 2026-07-22 hero-body spokes `realtime-render-performance` / `planetary-terrain-lod` / `atmospheric-scattering-and-clouds` / `stellar-and-relativistic-hero-bodies` (specialty spokes). Also leans on `game-scale-traversal`, `vfx-volumetrics`, `vfx-particle-systems`, `sci-astro-objects`.

**V1 Systems (minimum viable):** Exploration, factory building, resource economy, RTS combat, Bob clone mechanics, tutorial flow.

**Visualization state (as of 2026-05-12):** 9-tier zoom hierarchy (surface→galaxy) with Powers-of-10-style seamless sector→arm→galaxy fades. Galaxy disc is now a SINGLE volumetric raymarch (one BoxGeometry, 24-step Beer-Lambert integration) replacing the previous 9-disc+8-dust stack — looks correct from any angle including edge-on, dust actually occludes light from behind through line-of-sight extinction, 1 draw call instead of 17. Per-particle stellar size/color (Planckian, ~160K stars), real-Milky-Way structural fidelity: 4 arms emerging from bar tips, ~13.4° pitch, ±1kpc galactic warp, LMC/SMC at sky-correct positions, Sgr dSph tidal stream. Cinematic flight-path camera mode (shift+dblclick triggers a Bezier-arced traversal with ease-in-out cubic timing) + velocity-aware micro-streaks on stars (gated below 6000 WU/s — subtle/minor per design). Per-object camera scale at close tiers, full hover+select+dblclick model.

**Planet-renderer state (as of 2026-07-22):** Planet material hardened end-to-end (PRs #163–#184, all merged + deployed to Pages). Living weather (CPU cyclone lifecycle, ocean-gated, bounded shear); biome/climate as signed additive moisture field + Earth-MAT temperature; Earth-calibrated dark biome palette; settlement-realistic night lights (habitability field); ice/snow overlays with uneven cap margins; storm lightning; systemic World dials (offset/manual-edit-preserving) over the raw sliders; bake parity via one finishHeight() path. Stars-through-planets bug fixed (ledger A-06). Full detail + carry-forward in SESSION-STATE.md.

**Next:** ✅ **Delivered 2026-07-22** — the adversarially-checked performance/fidelity skills landed: 4 new hero-body spokes + a **project-wide performance doctrine** (60 FPS floor, uncapped by default, optional user frame cap, input latency co-equal) + the [[legion-hero-body-rendering-research]] master dossier + [[legion-planet-surface-rendering]] hard-won patterns. **Now:** implement against `src/render/` — reconcile `planetary-terrain-lod` with the existing quadtree renderer; wire `realtime-render-performance`'s frame-cap setting + input-latency pipeline into the engine loop; then profile/optimize the planet material at close zoom. (Longer arc still: galaxy-scale viz → system-scale gameplay per V1 scope; procedural-worlds `feat/worlds-star` S1 baton also still open — see SESSION-STATE 2026-07-11 block.)

---

### Figma Plugin Development
**Status:** Multi-plugin — active
**Summary:** Several plugins under active development:
- **Claude AI Agent Plugin** — embedding Claude as autonomous design collaborator with Figma scene graph access. Phase 2 library intelligence + variable tools complete. Rate limit mitigation (compressed tool schemas ~78%, 8-message sliding window, capped tool results), stop button via AbortController, resizable window, inline markdown rendering live.
- **Component Set Manager** — batch property rename + bulk variant export with configurable filename templates.
- **figma-repo-sync-plugin** (`~/projects/cpes-software/centric-ui/figma-repo-sync-plugin/`) — TypeScript plugin that generates Figma components from shadcn / Tailwind / CVA React source. Branched at `feat/figma-repo-sync-plugin` off `main` in `cpes-software/centric-ui` (Draft PR for FYI visibility). Bundles 4 + 5 (A–F) + 7 + 7.1–7.8 + 8 + 9 + 10A.1 + 10B.1 + 11.1 shipped (2026-05-11..05-12). **2026-05-13 audit-driven bundle**: 10A.2 (Phase 1 fixture-fallback unblock for Form/Sidebar/Sheet/NativeDialog when story 404s or parses empty; Phase 2.1 Input/Textarea placeholder injection at walker + single-component dispatch; Phase 3b EmptyState slot-default wiring from synthetic compound-style fixture children + conditional auto-visible when inner slot has a default) + 10B.1.1 (list-container dedup exemption for TabsList/TableRow/SelectGroup/AvatarGroup/SidebarMenu + Tabs master-assembly dedup; Phase 3a.1 inferLayoutMode conditional-class filter + `<tr>` HORIZONTAL tag default + TabsList componentName override for cnExtractor cva-unwrap gap) — promoted 9 of 11 ❌ from the 2026-05-12 audit to ✅. 374/374 tests passing. Build 420.3kb. **Still ❌**: ScrollArea (Phase 3c — story rich=13 wins but its `<div>` wrapper child gets filtered by PascalCase tag check), Avatar (size-full → Figma fill-parent layout-sizing translation). **Still ⚠**: Dialog `.DialogContent` 108×845 narrow column (Bundle 10B.2 partial-slot architecture), Badge `secondary` token cascade gap, Tabs/Table/EmptyState per-instance content overrides (Phase 4 `componentProperties` work — every TabsTrigger currently says "List view", every TableHead "Name", every EmptyState action button "Button"). **2026-05-23 (Bundle 11.3.70, 445 tests, ~570kb):** the `(?)`-binding regression is CLOSED (Phase 0 black-default kill in resolveVariableRGBAAtMode + page-level/Badge-glyph Colors mode pinning + authoritative scanner proving residual 3 `(?)` are cosmetic multi-value CVA tokens). **State-representation pattern landed on Button + Badge** (per `07-projects/09-figma-repo-sync-plugin/docs/2026-05-23-state-representation-decision-tree.md`): grouped `<slot>/<state>` variable naming (explicit `default`); physical State axis with foreground-tinted state-layer overlays (hover 12/focus 24/pressed 32%), focus ring + error (border+ring) overlays, disabled 50%; per-component state derivation. **Button Type expansion**: None/Leading/Trailing/Both + Icon with size-responsive icon-side padding. Footer de-clip + variantChild idempotency fix. Phase 1: TOKEN_PALETTE derived from COLOR_TOKENS (single source) with documented palette-generator migration seam. **Decision**: Figma state-as-modes is valid; physical for the smaller axis (states), modes for variant; opacity can't be mode-driven → normalized state-layer (Decision B). **Pending**: regen-verify on 11.3.70; Phases 2–3 (parser/binder unification, deferred); palette-generator migration (pending engineer alignment + non-breaking path); engineer-doc for the `default` naming affordance.

**Project folder:** `07-projects/04-claude-figma-plugin/`

**Next:** Bulk export finalization → filename template UI.

**figma-repo-sync-plugin — known non-issues (do NOT iterate on these until engineering follows up):**
- **NativeDialog** — not a shadcn primitive (404s on shadcn docs and on the project's storybook branch). Likely a Centric-specific use of the HTML `<dialog>` element or a dev-side helper component. As of Phase 1 (b93c76c) the master now picks up the dialog category fixture (richness=17), so visually it shows "Are you absolutely sure?" + Cancel + Continue like the regular Dialog. Leave as-is in the generated library; we'll only refine if engineering raises a follow-up about whether this primitive should ship at all.

---

### Omni — Design-to-Production Platform
**Status:** Exploratory architecture
**Summary:** Seed product for a computational design system — canvas editor + headless component library + IDE/CLI + visual logic builder + intermediate representation (IR). Framework-agnostic (Mitosis/Radix approach).

**Hub skill:** `omni-project`

**Next:** [Captured per SESSION-STATE when project resumes.]

---

### AI-Powered Design Assessment — Exploratory
**Status:** Research / exploratory
**Summary:** Bridging visual audit (component assessment) and code generation tools for enterprise PLM. Goal: reduce manual transcription between design tools and dev handoff. Connects to the `visual-qa-toolkit` skill (instrumented-perception layer, now built) and `native-visual-eval` (native-resolution precondition, framework #10).

**Next:** Apply the visual-QA stack (`native-visual-eval` → `visual-qa-toolkit` → `lead-visual-qa`) against a real PLM component-assessment pass.

---

### LCARS Generative Interface
**Status:** Implementing — S-SYS47-01 Literal prove in progress
**Summary:** LLM-forward adaptive LCARS console/shell — natural-language intent + combadge role context recomposes legal Okudagram surfaces via typed Scene IR; immutable constitution; v1 hybrid recipes with plumbing toward v2 dynamic topology; data-first 3D viewports; APCA primary contrast with WCAG AA fallback. App at https://github.com/snds/LCARS.
**Folder:** `07-projects/20-lcars-generative-interface/`
**Triggers:** lcars, generative lcars, okudagram, scene ir, literal match, construction ir
**Next:** Measure the four named uncued residuals on S-SYS47-01 (left rail, mid-band geometry, navy sweep, timestamp), then build to them. App lives in the platform `Projects` directory, not this vault.

---

### Workspace Brain
**Status:** Active
**Summary:** Standing home for sessions whose subject is the workspace itself (validation, fix, migration, infrastructure). Established 2026-07-09 per the workspace-work project-home rule in framework #08 (FX-13); git-tracked for cross-machine continuity.
**Folder:** `07-projects/19-workspace-brain/`
**Triggers:** workspace brain, workspace fix, workspace validation, error correction, verification loop
**Next:** Prove-engine vqa/1.1 + play-prove landed 2026-08-28. Watch whether producing paths still skip independent detectors. Optional: [[mission-fit]] on one unreliable done. Do not start a parallel agent framework.

---

### Portable Bootstrap Generator (`wsx`)
**Status:** Active — **v0.2 FEATURE-COMPLETE (2026-07-27)**; colleague/Olga re-test pending
**Summary:** Scripted + LLM-enhanced generator that scaffolds a portable, git-native, token-frugal workspace-brain for any user, on any surface, BYO-tokens (no API key/model calls — runs on the user's own agent/MCP/local-LLM). **v0.2 makes the DEFAULT target Sean's comprehensive model** — numbered taxonomy (00–09), a typed memory system, shared-references, a neutral data-driven automation layer (UserPromptSubmit trigger-router + skills registry + build-related + SessionEnd audit) — all via a single-source `layout.py` resolver (numbered-canonical, flat-fallback). **Hard guarantee: running the generator against an EXISTING workspace never breaks it** — a baseline-diff broken-reference gate (in `restructure` + `diagnose --fix`) auto-rolls-back if any mutation would break a link, with a change ledger. Command surface now ~30: dual-auth (gitscope), examine (incl. foreign-vault verdict), `restructure` (flat→numbered migration), `session end` (attributed, generalizing), `project adopt` (reference-in-place, repo files never copied), `bridge` (per-tool memory + re-anchor pointer), `ingest` (consent-gated + secret-scanned), `diagnose [--fix]` (error-reporting/correction w/ full reference traversal), `wire` (self-wiring off an intent registry, generator-independent), `help`/`COMMANDS.md` cheat sheet. Identity anchor binds "workspace/second brain" to the vault across every surface (incl. MCP). Self-sufficient: the whole CLI + schemas copy into `.wsx/` so a workspace drives itself with no generator.
**Folder:** `07-projects/18-bootstrap-generator/` — **git-tracked**; 14 commits `60a4ac4 → 1d2b4f1`. Eventual destination (SPEC §9): standalone `wsx` CLI repo, extractable from this folder's history.
**Triggers:** bootstrap generator, wsx, workspace generator, portable workspace
**Next:** Colleague/Olga re-test of full v0.2 + the adapter path. Optional: `wsx adapter ~/Projects/Workspace` to run wsx read-only tooling on the real vault (drops a `.wsx/` into the repo — Sean's call). Build `wsx profile init` (reconstruct a full profile from existing context). Follow-ups: bump `__version__` so `diagnose`'s stale-`.wsx`-copy check has a signal. **Post-v0.2 (2026-07-27 pt.2):** `wsx upgrade` made safe against a foreign/rich vault (registry no-clobber, no junk profile, no skill edits, refuses + `--force`); new `wsx adapter` = reference-mode map for a hand-built vault; voice/tone now first-class in the profile (adapters + bridge pointer point every LLM at `04-preferences/user-preferences.md`). **Discipline:** test CLI changes on a FRESH `init` (or after `wsx upgrade`) — never a reused workspace (stale `.wsx` copy masks fixes/regressions).

---

### CDS Figma–Code Audit
**Status:** Active — audit complete + verified (2026-05-04); acting on gaps blocked on Sean
**Summary:** Prop-parity audit between the Centric Design System (CDS) Figma libraries and the shipped `@centricsoftware/design-system` code (v1.3.0-develop-13), surfacing where Figma and code diverge. Full audit + v1.1 prop-parity artifact written and visually verified. Codebases: `~/projects/c8-plm/cds-docs/` (Fumadocs docs, port 3001) + `~/projects/c8-plm/CDS/` (DS source + dist). All 4 CDS Figma library files read via Figma MCP.
**Folder:** `07-projects/16-CDS Figma-Code Audit/` (definitive final state: `audit_prop-parity_v1.1_2026-05-04.md`)
**Next (blocked on Sean's call — docs acknowledgment vs. CDS source PR):** act on 🔴 gaps (Button `tertiarySubtle`, Accordion `size`/`disabled`, Progress Indicator, Chip status variants, Spinner linear); 🟠 Text gaps (italic variants, Hyperlink Extra Small, UI-size naming); deep-read the Custom Icons page in 005-Iconography.

---

## Design System — Current State

**System:** Centric PLM internal DS
**Maturity:** Mid-stage — audit complete, triage and spec work in progress
**Active concerns:**
- Data table component coverage (primary current focus)
- Token migration between Figma DS versions
- Cross-framework component parity (Vue primary)
- Component deprecation communication to engineering
- Cross-framework strategy: Ark UI as candidate headless foundation

---

## Migration Note — 2026-04-21

On 2026-04-21 a framework layer was added to the workspace. Five top-level operating frameworks now live at `01-frameworks/` in the workspace root:

1. Aesthetic Lens (`01-aesthetic-lens.md`) — philosophical ground
2. UI/UX Operational Framework (`02-ui-ux-operational-framework.md`) — operational decisions
3. Collaboration and Critique Framework (`03-collaboration-and-critique-framework.md`) — conduct
4. Research and Evidence Framework (`04-research-and-evidence-framework.md`) — epistemology
5. Last-Mile Craft Framework (`05-last-mile-craft-framework.md`) — finishing discipline

Orientation + compressed summaries at `01-frameworks/00-README.md`. These frameworks sit above any project-specific skill or context. They inform design, collaboration, research, and craft decisions across every project in the workspace.

The `workspace-bootstrap` skill has been extended to be aware of the frameworks folder (silent note at boot if missing) and to load per-project `SESSION-STATE.md` files (operational state continuity between sessions). `_session-state-template.md` in the frameworks folder is the spec for those files.

The stale `workspace-bootstrap-updated` skill directory has been renamed to `_deprecated_workspace-bootstrap-updated_2026-04-21` pending Sean's removal.

A skill audit report (`05-artifacts/active/skill-network-audit_opus-4.7_2026-04-21.md`) identified five prioritized opportunities for aligning the skill network with the new framework layer. None of the recommendations have been executed yet — the report is a deliverable, not an action log.

---

## Artifact Naming Convention

```
context_descriptor_vN.N_YYYY-MM-DD.ext
```
- Never overwrite — increment version
- Minor bump = iterative changes
- Major bump = structural changes
