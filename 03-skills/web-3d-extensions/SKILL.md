---
name: web-3d-extensions
description: >
  Drive optional 3D MCP/CLI extensions from ordinary conversation, research,
  revision, /motion verbs, or a living-spec implementor step. Jobs: headless
  boolean CSG to glTF (chisel), live compare of the same scene in Three /
  A-Frame / Babylon / R3F (maige-3d / mcp-webgpu), Godot editor drive, Unity
  or Unreal editor bridges. Also marketplace engines (Babylon, PlayCanvas,
  A-Frame, Spline, Substance) after the runtime is named. Not the greenfield
  WebGPU default (that is vgpu-webgpu). Not DCC craft (lead-3d-designer).
  Triggers: boolean CSG, CSG to glTF, without blender solid, live scene in
  three and babylon, a-frame canvas, in-world 3d chat, drive godot editor,
  drive unity editor, agentbridge, chisel, maige-3d, mcp-webgpu, godot mcp.
aliases: [web-3d-extensions, mcp-webgpu, maige-3d, chisel-mcp]
triggers:
  - boolean csg
  - csg to gltf
  - headless csg
  - chisel
  - chisel mcp
  - maige-3d
  - mcp-webgpu
  - live babylon canvas
  - live a-frame canvas
  - same scene three babylon
  - in-world 3d chat
  - drive godot editor
  - godot editor
  - godot mcp
  - without blender
  - without opening blender
  - drive unity editor
  - unity mcp
  - agentbridge
tier: spoke
domain: game
hub: lead-game-developer
prerequisites: [lead-game-developer]
related: [vgpu-webgpu, adapter-webgpu-three, adapter-unreal, adapter-unity-hdrp, 3d-modeling-fundamentals, 3d-asset-pipeline, motion, lead-3d-designer, intent-coordination]
defers_to: [vgpu-webgpu, framework-12, realtime-visual-craft, framework-17]
requires: [chisel-mcp, maige-3d-mcp, godot-mcp]
rigor_role: command-hub
surfaces: ["*"]
spec_version: "2.2"
---

# Web 3D extensions

Surfaces for 3D work that **vgpu does not own**. They are driven the same way as everything
else here: Sean's sentence, a research pass, a revision, `/motion`, or a living-spec step
([[intent-coordination]]). There is no slash-only or MCP-first gate.

Greenfield WebGPU still [[vgpu-webgpu]]. Photoreal prove-gates still [[realtime-visual-craft]].
Art-directed meshes still [[lead-3d-designer]].

MCP is **how some verbs execute**, not how the skill is allowed to load.

## Conversation / intent protocol

Same shape as Last-Mile tier 1 then construction: name the user need, pick the surface,
then execute. Do not wait for the product name.

1. **Parse the job** (ordinary language is enough).
2. **Pick one row** in the table below. If the job is new WebGPU/WGSL, stop and use
   [[vgpu-webgpu]] instead.
3. **Match the verb:**

| Verb | What you do | MCP required? |
|---|---|---|
| research / compare / "how would we" | Catalog, install notes, honest limits, recommend a path | No |
| plan / living-spec step | Name extension + prove-gate (`gltf-transform`, `vqa mesh`, editor open, …) on the spec | No |
| generate / drive / "build this solid" / "put a node in Godot" | Preflight **that** capability; if absent, add it for this session (template) or `npx`; then call tools | Yes, or named degrade |
| revise / "make it smaller" / "boolean the hole" | Same as generate on the existing session/export | Yes if the live tool holds state |
| audit / "is this mesh legal" | [[3d-asset-pipeline]] / `vqa`; editor read-only if connected | Optional |

4. **Intent.app / living spec:** an implementor line may say `skills: [web-3d-extensions]`
   (or `vgpu-webgpu`, `adapter-unity-hdrp`, …). The coordinator does not need the MCP.
   The implementor preflights when that wave runs. Isolation still holds: editor bridges
   and `CSG_OUTPUT_DIR` point at **that worktree / product repo**, not the vault root.
5. **Revision loops** (look at chisel views, change booleans, export again) are the point
   of chisel and maige. Do them in conversation. Do not dump the user back to a config file.

## Pick the surface

| Job (said in conversation) | Surface | Capability |
|---|---|---|
| Boolean primitives, CSG bracket, glTF without Blender/GPU | **chisel** | `chisel-mcp` |
| Same scene live in Three / A-Frame / Babylon / R3F, WebXR chat | **maige-3d-mcp** (repo mcp-webgpu) | `maige-3d-mcp` |
| Godot scenes, nodes, playtest | **godot-mcp** | `godot-mcp` |
| This repo is Unity; drive the Editor | Coplay or official Unity MCP | `unity-mcp` via [[adapter-unity-hdrp]] |
| This repo is UE 5.6; drive the Editor | AgentBridge | `unreal-agentbridge` via [[adapter-unreal]] |
| Hero mesh / volumes, art-directed | Blender MCP | `blender-mcp` |
| Debug a live *product* Three/R3F tree | threejs-devtools | `threejs-devtools-mcp` |

Marketplace skills (`babylonjs-engine`, `playcanvas-engine`, `aframe-webxr`,
`spline-interactive`, `blender-web-pipeline`, `substance-3d-texturing`) stay under
[[motion]]. `/motion generate|adapt|audit|polish` is valid here too (`--lib` when known).

## Absolute bans

- Using maige as the **ship renderer** or as a substitute for vgpu / Legion Three.
- Shipping chisel GLB as final game art when silhouette/UVs/materials matter, without a
  DCC (or an explicit "blockout only" label).
- Claiming editor mutations (Godot/Unity/Unreal) when the editor is closed. Research and
  spec-writing are still allowed.
- Putting engine API keys or Unity Cloud tokens in the workspace git checkout.
- Claiming #12 / `vqa` proof from an in-world chat overlay screenshot.

## chisel (headless CSG)

[EYamanS/chisel](https://github.com/EYamanS/chisel). Primitives + booleans; software-raster
multi-view PNG; export glTF/OBJ.

1. Preflight `chisel-mcp`. If absent: add from
   `00-bootstrap/templates/cursor-mcp-3d-extensions.json.example` **for this session**
   (or `npx -y github:EYamanS/chisel`). Do not refuse the job.
2. `CSG_OUTPUT_DIR`: existing absolute dir in the **product repo or worktree**. Never the
   vault root.
3. Conversation loop: tool → read the views → revise booleans → export.
4. Then `gltf-transform optimize` + `vqa mesh` ([[3d-asset-pipeline]]). Runtime load is
   vgpu or Three.

## maige-3d / mcp-webgpu (live multi-engine canvas)

`npx maige-3d-mcp`. Clients: Three `:5173`, A-Frame `:5174`, Babylon `:5175`, R3F `:5176`.

Use for engine-compare, WebXR in-canvas direction, teaching one scene in four frameworks.
Not Legion, ShadeGraph, or any product renderer.

Relay chat needs no extra API key (this session is the model). Direct in-world chat keys
stay machine-local, never git. `pnpm dev` clients run in a product or scratch clone, not
`07-projects/`.

## Godot / Unity / Unreal

Editor must be open **to mutate**. Closed editor: research, read files, write a spec,
degrade honestly.

- Godot 4.5+: `npx -y @satelliteoflove/godot-mcp` + `--install-addon` on the Godot project.
- Unity personal-solo: Coplay MCP for Unity, often `http://localhost:8080/mcp`. Official
  Unity 6 MCP needs Cloud + AI seat; do not mix personal/employer Unity accounts.
- Unreal: AgentBridge (UE 5.6 + Tempo). Northstar stills do not need it.

Look doctrine for Unity/Unreal remains the adapters ([[adapter-unity-hdrp]],
[[adapter-unreal]]).

## Where MCP config lives

Standing `~/.cursor/mcp.json` already has vgpu (docs). These extensions are **session- or
project-scoped** because they need an export dir or a running editor, not because
conversation cannot start them. When the verb needs the tool, the agent adds the block
from `00-bootstrap/templates/cursor-mcp-3d-extensions.json.example` (project file, or
user file if Sean wants it sticky) and continues.

| Surface | When the verb needs the live tool |
|---|---|
| Cursor | Project `.cursor/mcp.json` or a one-session add from the template |
| Claude Code | `claude mcp add` **local** (cwd) for editor bridges |
| Generic | stdio `npx` as in the template, or Unity HTTP while the Editor is up |

## Related
- hub → [[lead-game-developer]]
- peer ↔ [[vgpu-webgpu]] · [[adapter-webgpu-three]] · [[adapter-unreal]] · [[adapter-unity-hdrp]] · [[3d-modeling-fundamentals]] · [[3d-asset-pipeline]] · [[motion]] · [[lead-3d-designer]] · [[intent-coordination]]
