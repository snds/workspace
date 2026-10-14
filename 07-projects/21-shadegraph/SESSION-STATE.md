# SESSION-STATE — ShadeGraph (21-shadegraph)

_Last updated: 2026-09-04 08:10 — checkpoint (project seeded + scaffolded)_

---

## Current state (rewritten atomically — no stale fields)

### 🤝 Live handoff (the baton — any agent reads this FIRST)

- **TL;DR (for future agent)**: Standalone node-based shader design tool. Code
  lives in `~/Projects/ShadeGraph` (`snds/*`, its own git repo); this vault
  folder holds docs + baton only (like 13-legion). Legion is the first consumer
  (planet materials). Scaffold + design plan done; Phase 1 (graph MVP) is next.
- **Current focus**: dormant since 2026-09-26 (last recorded activity: the H8
  remediation live run on this repo). Phase 0 (scaffold + contracts + design
  plan) is done; Phase 1 (graph MVP) is next. Resume on the Personal MBP, where
  the code checkout lives. (Baton note 2026-10-14, /optimize — Claude Opus 5.5 ·
  Claude Code · Work MacBook Pro.)
- **Working set**: Code → `~/Projects/ShadeGraph/src/{model,compiler,nodes,preview,ui,adapters/legion}`. Plan → `docs/DESIGN-PLAN.md`.
- **Last action**: Wrote model/compiler/registry/preview contracts, app shell,
  Legion adapter plan, and `docs/DESIGN-PLAN.md` — by Claude Opus · Claude Code · Personal MacBook Pro.
- **Next action**: Phase 1 — `pnpm install` in `~/Projects/ShadeGraph`, then wire
  the React Flow shell to a store, implement a starter node set + inspector +
  JSON save/load. (See DESIGN-PLAN §10.)
- **Open decisions**: (1) name "ShadeGraph" is provisional; (2) state lib
  zustand vs custom; (3) WGSL via hand emitters vs TSL-as-IR; (4) Legion
  live-bridge in Phase 4 vs export-only. See DESIGN-PLAN §11.
- **Blocked on**: nothing.
- **In-flight / do-not-touch**: nothing known. Corrected 2026-10-14: the repo
  has commits and a remote, `snds/shadegraph` (`9b11035`, 2026-09-26). On
  2026-09-26 a Zero-Vector H8 live run here produced 9 findings and two PRs
  (CI and model id), both merged green (rollout checklist W2-5). Whether
  `pnpm install` has run since is not recorded.
- **Agent thread**: Claude Opus/Claude Code (2026-09-04): researched vgpu +
  Prism article + industry node editors; scaffolded repo; wrote design plan.

### Environment
- **Context profile**: `personal-solo` (direct commits expected; ShadeGraph is a personal repo).
- **Machine**: `Voyager-2.local` (Personal MacBook Pro)
- **OS context**: macOS (Darwin 25.5.0)
- **Workspace root**: `/Users/snds/Projects/Workspace`
- **Project root (code)**: `/Users/snds/Projects/ShadeGraph`
- **Project root (docs/baton)**: `/Users/snds/Projects/Workspace/07-projects/21-shadegraph`

### Active servers and processes
- **Dev server**: not running (`vite` on :5180 once deps installed)
- **Build / Test**: not run

### VCS state
- **Code repo**: `~/Projects/ShadeGraph` — remote `snds/shadegraph`, with commits and two merged PRs as of 2026-09-26 (`9b11035`; checklist W2-5). The 2026-09-04 "no commits yet, no remote" note was stale.
- **Vault**: tracked in `snds/workspace`; this folder committed at session-end.
- **Uncommitted changes**: yes — all scaffold files new/untracked.
- **Test state**: not run.

### Configuration in use
- **Stack**: React 18 + React Flow 12 (`@xyflow/react`) + Three r171 + Vite 6 + Vitest + zustand.
- **Backends targeted**: `glsl-es` + `wgsl` + `tsl` (both from day one).

### Open work and paused threads
- **Currently in progress**: nothing mid-edit; clean checkpoint.
- **Pending questions**: name; state lib; WGSL strategy; Legion bridge (DESIGN-PLAN §11).
- **What's needed to resume**: read DESIGN-PLAN §10 (roadmap) and start Phase 1.

---

## Session history (append-only)

### 2026-10-14 — dormant since 2026-09-26; stale VCS notes corrected (/optimize)

**Agent**: Claude Opus 5.5 · Claude Code · Work MacBook Pro. No project work. The "no commits yet, no remote" notes were stale: the repo has a remote, `snds/shadegraph` (`9b11035`), and two merged PRs from the 2026-09-26 H8 live run.

### 2026-09-04 08:10 — checkpoint

**Focus this session**: Research vgpu + the Codrops Prism article + industry
node-based shader editors; decide the stack; scaffold a standalone tool and
write the design plan.
**Machine**: Personal MacBook Pro
**Stopped because**: natural break — scaffold + plan delivered; awaiting go on Phase 1.

**Accomplishments**:
- Confirmed vgpu (agent-first WebGPU lib) + the article's read-only pipeline visualizer as the intent.
- Traced Legion's real shader architecture (GLSL chunks + uniforms + per-archetype lab-store) — it's already a de-facto node system.
- Chose React Flow 12 shell + shared GPU renderer + pluggable compiler (fidelity ⟂ framework rationale).
- Scaffolded `~/Projects/ShadeGraph` with model/compiler/registry/preview contracts + app shell + Legion adapter plan.
- Wrote `docs/DESIGN-PLAN.md` (research, decisions, model, roadmap).

**Decisions made**:
- Backends: both GLSL-ES and WGSL/TSL from day one.
- Home: standalone `~/Projects/ShadeGraph`; Legion consumes exports; vault holds docs/baton only.
- Editor: React + React Flow 12; litegraph/canvas renderer is the documented escape hatch.

**Next resumption needs**:
- `pnpm install` in the code repo; begin Phase 1 (graph MVP).

---

_Seeded by Claude Opus / Claude Code on 2026-09-04. Initial state reflects a completed Phase 0 scaffold._
