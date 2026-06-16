---
tags: [legion, game-dev, threejs, webgpu, typescript, glsl, bobiverse]
created: 2026-04-28
updated: 2026-04-28
status: working
confidence: medium
sources: [project-context 2026-04-28, session-state 13-legion]
related_skills: [legion-project, lead-game-designer, lead-art-director, lead-game-developer, threejs-materials-master, glsl-shader-architect, threejs-vfx-atmosphere, webgpu-advanced-rendering, lead-3d-designer]
related_projects: [13-legion]
---

# Legion — Architecture and Design Decisions

What we know about the Legion game project: tech stack, design philosophy, V1 scope, and the working context for continuing development. The session state is sparse (project seeded but not yet resumed in a live session), so this captures what's known from the project context.

---

## What Legion Is

An interstellar hard sci-fi strategy game inspired by the Bobiverse series by Dennis E. Taylor. The core gameplay loop combines:
- **Factory management** — building and automating production chains
- **4X strategy** — explore, expand, exploit, exterminate at an interstellar scale
- **RTS combat** — real-time tactical engagements
- **Narrative core** — the Bob clone mechanic; each Bob is a von Neumann probe carrying a version of the same human consciousness

**Aesthetic direction:** Hard sci-fi realism. The Bobiverse aesthetic. Not stylized, not cartoony — technically grounded visual design with the kind of details that reward inspection.

---

## Tech Stack

| Layer | Technology | Notes |
|-------|-----------|-------|
| Rendering | Three.js | Primary renderer |
| GPU API | WebGPU | Production-ready as of Jan 2026 |
| Language | TypeScript | Primary codebase language |
| Shaders | GLSL | Vertex/fragment shaders via Three.js |
| Build | Vite | Fast dev server + bundler |

**Current runtime target:** Browser (playable browser prototype exists)

**Why WebGPU over WebGL:** WebGPU became production-ready in January 2026 across major browsers. Provides compute shaders, better GPU utilization, and eliminates some WebGL API quirks. The project is positioned to take advantage of this transition.

---

## V1 Systems (Minimum Viable)

The current V1 target includes these systems — nothing more:
1. **Exploration** — probe movement, discovery mechanics
2. **Factory building** — placing and connecting production facilities
3. **Resource economy** — extraction, processing, allocation
4. **RTS combat** — tactical engagements (scope TBD)
5. **Bob clone mechanics** — the identity/individuation system unique to the Bobiverse premise
6. **Tutorial flow** — onboarding for new players

These are the gates. Work that doesn't serve one of these systems is post-V1 scope.

---

## 3D Asset Context

The 3D work for Legion is principally **space station and spaceship interiors** plus **probe exteriors**. Key reference from the Bobiverse: von Neumann probes are self-replicating spacecraft — functional, not aesthetic. The visual design should feel *built for purpose*, not designed for appearance.

**Spatial scale conventions for space stations:**
- Corridor width: ~1.5–2m (tight, functional)
- Ceiling height: 2.2–2.5m (utilitarian)
- Compartment depth: varies by function (engineering bays are larger than crew quarters)
- Docking bay scale: must accommodate probe approach vectors

The `3d-spatial-design-for-games` skill has Legion-specific spatial reference tables.

---

## Skill Routing for Legion Work

The `legion-project` skill is the foundation. Then route by topic:

| Work type | Skills to load |
|-----------|---------------|
| Game mechanics design | `lead-game-designer` |
| Visual direction, aesthetic | `lead-art-director` |
| Three.js code, rendering | `lead-game-developer` + `threejs-materials-master` |
| GLSL shader work | `glsl-shader-architect` |
| VFX, atmosphere, particles | `threejs-vfx-atmosphere` |
| WebGPU-specific features | `webgpu-advanced-rendering` |
| 3D asset creation | `lead-3d-designer` → spokes |
| Space asset pipeline (glTF, etc.) | `3d-asset-pipeline` |

The workspace-bootstrap `UserPromptSubmit` hook triggers on "legion", "the game", "bobiverse" and auto-loads the legion skill context.

---

## What We Don't Yet Know (Open Questions)

From the session state — these were captured as "to be determined on next live session":
- Current branch and commit state of the prototype
- Active Vite config and Three.js version pinning (r128 was referenced in project docs)
- Asset pipeline state — what assets exist, where they live
- Which V1 systems are implemented vs. designed vs. not started

The session state file was seeded 2026-04-21 without a live Legion session. The current state of the code is unknown until a session explicitly resumes the project.
