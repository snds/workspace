---
tags: [knowledge-vault, cross-domain, skills, mcp-servers, skill-ecosystem, evaluation]
created: 2026-06-16
updated: 2026-06-16
status: stable
confidence: high
sources: [skills.sh, mcpmarket.com/tools/skills, mcpmarket.com/server, session-log 2026-06-16]
related_skills: [science-foundations, lead-security-architect, mobile-react-native]
related_projects: [00-obsidian, 13-legion]
---

# Skill Ecosystem Evaluation + MCP Server Recommendations

What a review of the external agent-skill directories (skills.sh, mcpmarket.com) yielded for our library,
the dedup decisions made, and which MCP servers are worth integrating. Captured so a future pass doesn't
re-litigate the same evaluation.

## How the external directories actually break down
Across **skills.sh** ("Open Agent Skills Ecosystem") and **mcpmarket.com** (20 categories, ~150k skills),
the catalog is dominated by three buckets — and dedup removed most:
1. **Tool integrations** (Azure/AWS, Lark/Slack/Discord, Supabase, GitHub auto-fixer, Notion). These are
   **MCP servers**, not authored knowledge skills — they belong in the connector layer, not `03-skills/`.
2. **Already covered** — `frontend-design`, `web-design-guidelines` (→ our `found-*`/`uid-*`), `find-skills`,
   `agent-browser` (we have both), `improve-codebase-architecture` (→ `eng-foundations`/`fe-component-architecture`),
   and the **entire Three.js game-dev skill cluster** (animation, shaders, materials, post-processing,
   geometry, lighting) which our `threejs-materials-master` / `threejs-vfx-atmosphere` / `glsl-shader-architect`
   / `webgpu-advanced-rendering` already cover, deeper.
3. **Genuine gaps** — what we added (below).

**Key finding:** these directories wrap *engines and tools* (Three.js, Unity, Unreal, Blender). **None teach
the math/physics substrate** beneath them — confirming that the science domain had to be authored, not imported.

## What we added (2026-06-16)
- **`science-foundations`** + `sci-linear-algebra`, `sci-numerical-methods`, `sci-physics-simulation`,
  `sci-probability-stochastic` — the math/physics substrate. Wired as a foundation under `lead-game-developer`,
  the rendering skills, `lead-data-scientist`, and `legion-project`. **Directly serves the Legion engine.**
- **Mobile** — `mobile-react-native`, `mobile-ios-swiftui`, `mobile-android-kotlin`, `mobile-platform-craft`
  (spokes of `lead-frontend-engineer`). Synthesized from idiomatic-Kotlin / Flutter / Android-Clean-Architecture
  community practice.
- **Security** — `lead-security-architect` (cross-cutting hub) + `sec-threat-modeling`, `sec-authn-authz`,
  `sec-appsec-owasp`, `sec-supply-chain`. Governs `be-api-design`, `fe-api-integration`, `devops-ci-cd`;
  complements (does not duplicate) the existing `be-security-posture`.
- **Enhancement:** Postgres-specific practices appended to `be-relational-db` (EXPLAIN, index types, MVCC/VACUUM,
  jsonb, RLS, pooling).

## Deliberately NOT added (dedup discipline)
- Three.js/WebGL game skills → we cover them deeper already.
- Design-guideline skills → our `found-*`/`uid-*`/`gd-*` network is more comprehensive.
- Codebase-architecture skill → already in `eng-foundations` + `fe-component-architecture`.
- Engine integrations (Unity/Unreal/Godot/Bevy/Roblox) → out of scope (Legion is Three.js + WebGPU).
- Marketing/e-commerce/social automation → not relevant to this workspace.

## Attribution convention
External-informed skills carry an inline `_Synthesized/adapted from <source>_` note (we author in our own
voice + frontmatter v2, never copy). This satisfies "extract from the author what's necessary" without
importing foreign structure.

## MCP servers worth integrating
From `mcpmarket.com/server` (game-dev = 600+ servers). Integration is a per-client config action (Claude
settings → Connectors), not a repo change.

| Server | Why | Priority |
|---|---|---|
| **Blender MCP** | Prompt-driven 3D modeling / scene creation — the **Legion asset pipeline**. Top game-dev server. | **High (Legion)** |
| **Postgres / SQLite MCP** | DB introspection for any data-backed work; pairs with `be-relational-db`. | Medium |
| **Figma MCP** | Already connected. | (have it) |
| **GitHub MCP** | Already connected. | (have it) |
| **Atlassian MCP** | Already connected. | (have it) |
| **Playwright MCP** | Redundant — we have the `agent-browser` skill (Playwright-based, used to scrape mcpmarket here). | Skip |
| **Godot / Unity / Unreal MCP** | Only if Legion ever leaves Three.js + WebGPU. | Low |

## Note on scraping mcpmarket
mcpmarket.com hard-blocks WebFetch (HTTP 429, Cloudflare) but renders fine via the `agent-browser` skill
(real Chromium over CDP). Its `/tools/skills/categories/<slug>` filter URLs and `/categories/<slug>` (servers)
are the addressable views.
