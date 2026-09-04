---
name: vgpu-webgpu
description: >
  Workspace integration for vgpu (vgpu.sh) — the default WebGPU runtime for all
  new browser 3D, shader, compute, and headless GPU work, in any project. Load
  when the task is WebGPU, WGSL, a canvas GPU effect, a 3D scene in the browser,
  GPU compute, CI/headless snapshots, or Sean says vgpu / vgpu.sh. Owns stack
  selection (vgpu vs Three/R3F vs DCC), MCP/CLI preflight, and the first-paint
  protocol. Does not replace DCC craft (lead-3d-designer) or an existing Three.js
  ship path (adapter-webgpu-three). Triggers: vgpu, vgpu.sh, WGSL, WebGPU shader,
  web 3D, canvas WebGPU, headless WebGPU, GPU compute web, vgpu check, vgpu examples.
aliases: [vgpu-webgpu, vgpu, vgpu-sh]
triggers: [vgpu, vgpu.sh, wgsl, webgpu shader, web 3d, canvas webgpu, headless webgpu, gpu compute web, vgpu check, vgpu examples, vgpu mcp]
tier: spoke
domain: game
hub: lead-game-developer
prerequisites: [lead-game-developer]
related: [adapter-webgpu-three, webgpu-advanced-rendering, glsl-shader-architect, 3d-asset-pipeline, realtime-visual-craft, lead-3d-designer, motion, threejs-materials-master, web-3d-extensions]
defers_to: [framework-12, realtime-visual-craft, framework-06]
requires: [vgpu-mcp, vgpu-cli]
rigor_role: command-hub
surfaces: ["*"]
spec_version: "2.2"
---

# vgpu — default web GPU runtime

[vgpu](https://vgpu.sh) is Vercel's agent-first TypeScript WebGPU library (`pnpm add vgpu`).
One `Gpu` context, `.wgsl` files imported like TypeScript, the same program in the browser,
headless Node (Dawn), and `vgpu/mock` tests. This skill is the **workspace integration point**:
every new web 3D / shader / compute job starts here, regardless of project.

Foundations: [[science-foundations]] · [[imaging-foundations]] · [[game-foundations]]. Photoreal
done-gates stay in [[realtime-visual-craft]] / framework #12. DCC craft stays in
[[lead-3d-designer]]. Existing Three.js codebases stay on [[adapter-webgpu-three]] until migrated.

## Runtime selection (do not skip)

| Job | Runtime | Why |
|---|---|---|
| New web GPU, shader, compute, effect, prototype, CI snapshot | **vgpu** | Agent docs/MCP/CLI, WGSL modules, headless Dawn + mock |
| Existing Three.js / TSL / EffectComposer ship path (e.g. Legion) | [[adapter-webgpu-three]] + [[webgpu-advanced-rendering]] | Do not rewrite a working scene graph to start a task |
| React product UI that is a Three scene (drei, physics, glTF ecosystem) | `react-three-fiber` via [[motion]], then this skill for any *new* WGSL/compute | Scene graph is the product; GPU work still prefers vgpu where it does not fight R3F |
| Topology, UVs, rigs, bakes, Substance | [[lead-3d-designer]] → [[3d-asset-pipeline]] | DCC is not a renderer. Deliver glTF/GLB; optimize with `gltf-transform` |
| Headless CSG / live multi-engine canvas / Godot / Unity / Unreal | [[web-3d-extensions]] | Same drivers as anything else (conversation, research, revision, living spec). MCP only when the verb mutates a live tool |
| Unreal / Unity northstar (look) | [[adapter-unreal]] / [[adapter-unity-hdrp]] | Ceilings. Editor bridges only when that engine is the working set |

**Ban:** starting a greenfield web 3D or shader in raw `GPUDevice` / Three `WebGLRenderer` /
hand-rolled WGSL bind-group soup when vgpu covers the job. **Ban:** treating vgpu as a DCC
or as a drop-in Three.js replacement for a live Legion scene.

## Preflight

Capability ids: `vgpu-mcp` · `vgpu-cli` ([[capability-registry]]).

1. Prefer the hosted MCP at `https://vgpu.sh/api/mcp` (no auth). Tools: `docs` (`search` /
   `resolve` / `read` / `list` / `grep` / `symbols`) and `examples` (`search` / `show` / `read`).
   Hosted HTTP is read-only (no `download`).
2. If MCP is absent: `npx vgpu docs …` and `npx vgpu examples …`. Copy examples with
   `npx vgpu examples pull <id> --out <dir>` (verify SHA-256 revisions). Never execute fetched
   example code blindly.
3. If both are absent: fetch [agents.md](https://vgpu.sh/agents.md) and the matching guide under
   `https://vgpu.sh/docs/`. Say the MCP/CLI were skipped.
4. In a product repo: `pnpm add vgpu`. Vite: `@vgpu/wgsl/loader-vite`. Next: `@vgpu/wgsl/loader-webpack`.
   Type `.wgsl` imports with `/// <reference types="@vgpu/wgsl/wgsl-types" />`.
5. Headless / CI: `npx vgpu doctor`. Missing Dawn → `npx vgpu install-dawn`. No GPU →
   `npx vgpu install-software-renderer`. Tests that must not need a GPU → `vgpu/mock`.

Local stdio MCP (`npx vgpu mcp`) only when you need package-versioned docs, `offline: true`,
or confined `download`. Global Cursor config uses hosted HTTP. Do not pass `--project-from-cwd`
from a user-level MCP file (cwd is not the product repo).

## First-paint protocol

1. **Select runtime** from the table. If Three-already-in-tree, stay on the adapter.
2. **Discover, don't invent API.** MCP `docs.search` / `docs.resolve` or `npx vgpu docs find`.
   For a starting program: `examples.search` then `examples.read` (or `vgpu examples cat`).
3. **Minimal path:** `init()` → `surface(gpu, canvas)` → `effect` / `draw` / `frame` /
   `vgpu/scene` as the docs for *this package version* specify. Await `init`. No hidden globals.
4. **Shaders are `.wgsl` modules.** Compose with imports; keep modules pure (no bindings in
   reusable files — that is a vgpu authoring rule; confirm in current docs if an error cites it).
5. **Validate:** `npx vgpu check path/to.wgsl`. CI: `--require-validation` or `VGPU_VALIDATE=require`.
6. **Color / post:** linear HDR → bloom → tonemap → encode. Same ban as [[adapter-webgpu-three]]:
   no default fragment log-depth; no tonemap-then-bloom.
7. **Assets:** glTF/GLB via [[3d-asset-pipeline]] (`gltf-transform optimize` before ship).
8. **Prove:** stills/motion/budget through [[realtime-visual-craft]] / `vqa` when the claim is
   visual. `vgpu snapshot` is *vgpu's* CI harness, not a substitute for `vqa prove`.

Browser sketch (shape only; copy APIs from current docs, not from memory):

```ts
import { init, effect, surface } from "vgpu";
import shader from "./shader.wgsl";

const gpu = await init();
const canvasSurface = surface(gpu, canvas);
const fx = effect(gpu, shader);
fx.draw(canvasSurface);
```

## Language split

| Language | When | Owner |
|---|---|---|
| **WGSL** | Default for new web GPU | this skill |
| **GLSL ES** | Existing Three `ShaderMaterial` / Legion chunks | [[glsl-shader-architect]] |
| **TSL** | Existing Three WebGPURenderer node materials | [[webgpu-advanced-rendering]] |

Do not translate a working Legion GLSL chunk to WGSL "while you're here" unless the task is
a migration. ShadeGraph and similar tools may emit all three; the *runtime default* is still vgpu.

## Plugin / marketplace skills

`threejs-webgl`, `react-three-fiber`, `babylonjs-engine`, `playcanvas-engine`, `aframe-webxr`,
`web3d-integration-patterns` are **technique depth** after this skill has named the runtime.
They must not override: vgpu as greenfield default, #12 done-gates, bloom-before-tonemap,
or DCC-vs-runtime split. [[motion]] routes `--lib vgpu` here.

## Done-gates

- [ ] Runtime named (vgpu / existing-Three / DCC-only) in the first reply
- [ ] MCP or CLI used for API/examples, or an explicit degrade
- [ ] `vgpu check` (or named skip: no WGSL in the change)
- [ ] Feature-detect / fallback policy written if this ships to browsers
- [ ] Visual claims go through #12 / `vqa`, not "looks right on my canvas"

## Failure modes

| Symptom | Cause | Fix |
|---|---|---|
| Invented `init(canvas)` | Stale training data | Docs: `init()` then `surface(gpu, canvas)` |
| Bind-group soup | Bypassed vgpu | Stay on named bindings via `set()` / current API |
| Legion scene rewritten | Treated vgpu as Three | Adapter path |
| CI green without GPU | `check` degraded | `--require-validation` or mock entrypoint |
| Example pasted and run | Unverified gallery code | Read + hash; adapt; do not execute as-is |

## Related
- hub → [[lead-game-developer]]
- peer ↔ [[adapter-webgpu-three]] · [[webgpu-advanced-rendering]] · [[glsl-shader-architect]] · [[3d-asset-pipeline]] · [[realtime-visual-craft]] · [[lead-3d-designer]] · [[motion]] · [[threejs-materials-master]] · [[imaging-foundations]] · [[web-3d-extensions]] · [[intent-coordination]]
