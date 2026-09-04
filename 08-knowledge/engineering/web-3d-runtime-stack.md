---
tags: [knowledge-vault, engineering, webgpu, vgpu, 3d, mcp]
created: 2026-09-04
updated: 2026-09-04
status: stable
confidence: high
sources:
  - https://vgpu.sh/agents.md
  - https://vgpu.sh/docs/mcp
  - https://vgpu.sh/docs/cli
  - https://github.com/vercel-labs/vgpu
  - https://gltf-transform.dev/cli
  - https://github.com/DmitriyGolub/threejs-devtools-mcp
  - 08-knowledge/cross-domain/skill-ecosystem-and-mcp-servers.md
related_skills: [vgpu-webgpu, web-3d-extensions, adapter-webgpu-three, adapter-unreal, adapter-unity-hdrp, 3d-asset-pipeline, glsl-shader-architect, webgpu-advanced-rendering, lead-3d-designer]
---

# Web 3D runtime stack (vgpu default)

What to use for **web** 3D and GPU work in this workspace, after evaluating vgpu and adjacent
MCP/CLI/skill surfaces in 2026-09. Domain insight, not a project plan. Operating skill:
[[vgpu-webgpu]]. Decision: [[decision-vgpu-default-web-3d]].

## The split that keeps falling out

Web 3D work is three jobs that people collapse into one word ("3D"):

1. **DCC craft** — model, UV, rig, bake. Hub: [[lead-3d-designer]]. MCP already: `blender-mcp`.
2. **GPU program** — shaders, compute, fullscreen effects, headless snapshots. Default: **vgpu**.
3. **Scene-graph product** — cameras, glTF, lights, animation clips, drei helpers. Keep Three/R3F
   when that graph already exists (Legion) or when React-as-scene is the product.

vgpu is a small WebGPU API (`init`, `surface`, `effect`, `draw`, `compute`, `frame`, `bundle`,
`vgpu/scene`), not Blender and not a full Three ecosystem clone. Using it as a DCC is a category error.

## Adopted (wired)

| Surface | Role | Workspace hook |
|---|---|---|
| **vgpu** (`pnpm add vgpu`) | Default WebGPU runtime; WGSL modules; browser + Dawn + mock | [[vgpu-webgpu]] |
| **vgpu MCP** `https://vgpu.sh/api/mcp` | Read-only docs + verified examples (`docs`, `examples`) | capability `vgpu-mcp` |
| **vgpu CLI** `npx vgpu` | `docs`, `examples`, `check`, `doctor`, `mcp`, Dawn/software install | capability `vgpu-cli` |
| **gltf-transform** | Inspect/optimize/compress glTF/GLB for web delivery | capability `gltf-transform` → [[3d-asset-pipeline]] |
| **gltf-validator** | Error-level mesh audit | already on [[visual-prove-engine]] |
| **Blender MCP** | Hero DCC when procedural is not enough | already `blender-mcp` → [[vfx-volumetrics]] |
| **threejs-devtools-mcp** | Live inspect/edit of an *existing* Three/R3F scene (browser bridge) | capability `threejs-devtools-mcp` → [[adapter-webgpu-three]] |
| Workspace Three/TSL/GLSL spokes | Technique for trees that already use Three | [[adapter-webgpu-three]], [[webgpu-advanced-rendering]], [[glsl-shader-architect]] |

vgpu agent extras (not duplicated into the vault): [agents.md](https://vgpu.sh/agents.md),
[llms.txt](https://vgpu.sh/llms.txt), examples API `/.well-known/vgpu-examples.json`. Prefer MCP
or `npx vgpu` over scraping the site. Hosted MCP rejects legacy session HTTP; use modern streamable
HTTP. `download` of examples is local-stdio + output boundary only (macOS/Linux).

## Optional extensions (wired, not defaults)

MCP is how some *execute* verbs run (drive Godot, boolean in chisel). Research, revision
planning, living-spec steps, and `/motion --dry` do not wait on a connected server.
Conversation and [[intent-coordination]] implementor lines are valid drivers. See
[[web-3d-extensions]] → Conversation / intent protocol.

| Surface | When it is the right tool | Capability / hook | Honest limit |
|---|---|---|---|
| **chisel** | Agent CSG (boxes/booleans) → inspectable `.glb` with no GPU | `chisel-mcp` | Not final game art. `CSG_OUTPUT_DIR` in the product repo only. |
| **maige-3d-mcp** (`mcp-webgpu` repo) | Same scene live in Three / A-Frame / Babylon / R3F + WebXR in-canvas chat | `maige-3d-mcp` | Demo/compare canvas. Not Legion, not vgpu, not a ship renderer. Relay chat; no keys in git. |
| **godot-mcp** (`@satelliteoflove/godot-mcp`) | This checkout is a Godot 4.5+ project and the editor is open | `godot-mcp` | Addon + editor required. Disk-only if Godot is closed. |
| **Coplay Unity MCP** | This checkout is a Unity project; Editor running | `unity-mcp` → [[adapter-unity-hdrp]] | MIT, often `localhost:8080/mcp`. Python/`uv`. |
| **Official Unity 6 MCP** | Unity 6 + Cloud + AI seat; Sean asked for the official bridge | `unity-mcp` | Relay `~/.unity/relay`. Do not mix personal/employer Unity accounts. |
| **AgentBridge** | This checkout is UE 5.6 with Tempo | `unreal-agentbridge` → [[adapter-unreal]] | Heavy. Northstar footage does not need it. |
| **Blender MCP** | Hero DCC / volumes | `blender-mcp` | Already on [[vfx-volumetrics]]; procedural remains the default volume path. |
| **threejs-devtools-mcp** | Debug a live *product* Three/R3F tree | `threejs-devtools-mcp` | Tab must stay open. Not for vgpu greenfield. |
| Marketplace engine skills | `/motion --lib` Babylon / PlayCanvas / A-Frame / Spline / Substance | [[motion]] | Technique after runtime named; cannot override vgpu or #12. |

Playwright MCP stays skipped as a *duplicate* of `agent-browser` + `playwright` for `vqa capture`. That is overlap, not a quality judgment on Playwright.

## CLI ladder for a web 3D change

1. `npx vgpu check *.wgsl` (CI: `--require-validation`)
2. `gltf-transform inspect` then `optimize` on GLB
3. `gltf-validator` / `vqa mesh` on the shipped asset
4. `vqa prove` / #12 flythrough when the claim is look, not "compiled"

## Dated facts (re-check if #stale)

- vgpu public docs and MCP: 2026-09 (package still moving; always resolve APIs via MCP/CLI).
- threejs-devtools-mcp: npm, MIT, ~59 tools, injects a browser bridge (tab must stay open).
- chisel MCP: `npx -y github:EYamanS/chisel`, env `CSG_OUTPUT_DIR`.
- maige-3d: `npx maige-3d-mcp`; clients Three/A-Frame/Babylon/R3F on :5173–:5176.
- godot-mcp: `@satelliteoflove/godot-mcp`, Godot 4.5+.
- Coplay Unity MCP: Package Manager git URL `…/unity-mcp.git?path=/MCPForUnity#main`.
- Official Unity MCP and AgentBridge: editor + seat / UE 5.6+Tempo (re-check docs).
