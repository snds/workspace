---
title: ShadeGraph — Design & Research Plan
type: design-doc
project: 21-shadegraph
status: draft
created: 2026-09-04
updated: 2026-09-04
author: Sean Sands (with Claude Opus / Claude Code)
related_projects: [13-legion]
tags: [shader, node-editor, webgpu, glsl, tsl, three, legion, tooling]
---

# ShadeGraph — Design & Research Plan

A reusable, node-based shader design tool. Compose layered shaders as a live
node graph; see each node's output on the node; solo any node/layer to a full
preview; compile the same document to GLSL ES, WGSL (vgpu/WebGPU), or Three TSL.
Standalone and generic; **Legion** is the first consumer (planet materials).

> **Provenance.** Prompted by [vgpu.sh](https://vgpu.sh) and the Codrops article
> [_From Rays to Meshes — Building Vercel's Prism with vgpu_](https://tympanus.net/codrops/2026/09/03/from-rays-to-meshes-building-vercels-prism-with-vgpu/).
> The article's author hand-built a **read-only** render-pipeline visualizer to
> understand how shader layers mixed. ShadeGraph is the editable version, built
> to scale to any WebGPU shader work.

---

## 1. Goal & requirements

**Goal:** a tool that lets Sean visually author and tune shaders and *layers of
shaders* — generic enough to stand alone, powerful enough to drive Legion's
planets directly.

Requirements (from the brief):

- **Nodes:** add nodes of varying types; connect/disconnect; delete.
- **On-node feedback:** live output/outcome of a node's params + connections
  shown *on the node itself*, including the effect of its parents.
- **Chain preview:** preview the entire chained output.
- **Layers:** manage layers of shaders — add layers of varying types, remove,
  enable/disable, show/hide, (implied) reorder + blend.
- **Fidelity:** an accurate live representation of the final target output —
  perceived as game/film/intent-ready.
- **Scale:** performantly view/manage/edit *large* diagrams across multiple
  layers.
- **Portability:** WebGPU-first future (vgpu) while driving Legion's current
  GLSL today. "Scale for any shader work we do using WebGPU."

---

## 2. Industry research — patterns worth stealing

Node-based shader/material/compositing tools converge on a small set of proven
patterns. Mapped to our requirements:

| Requirement | Best-in-class reference | Pattern we adopt |
|---|---|---|
| Typed connect/disconnect | **Unreal Material Editor**, **Unity Shader Graph** | Color-coded, type-validated sockets (float/vec/sampler/normal); illegal links rejected at drag time |
| Live output *on the node* | **Substance 3D Designer** (thumbnail per node), **Blender** node-preview add-ons ([Node Peek](https://github.com/mlstr0m/node-peek), [Shader View](https://alekseym88.github.io/shader-view-page/), [GSoC node preview](https://devtalk.blender.org/t/gsoc-2023-shader-editor-node-preview-weekly-reports/29359)) | Per-node offscreen render thumbnail that updates live |
| Preview entire chain | **Nuke** viewer-per-node | "Solo any node/layer to the main viewer" + a master/output node |
| Manage shader layers | **Unreal Material Layers**, **Substance** layer stack, Photoshop | A layer stack *surface distinct from the graph*: blend mode, opacity, enable, show/hide, reorder, solo |
| Enable/disable node | **Blender** (M-mute), **Nuke** (D-disable) | Node bypass (pass-through of primary input) |
| Reusable / generic | **Unity** sub-graphs, **Unreal** material functions, **Houdini** HDAs | Subgraphs/node groups + a serializable, backend-neutral document |
| Large-graph perf | **ComfyUI/litegraph** (single-canvas, huge graphs) | Viewport culling, zoom-LOD, GPU work off the DOM; canvas-renderer as escape hatch |
| Adaptive quality | The **Prism** article (GPU tier · battery · FPS) | Degrade preview res/refresh under load rather than stall |

**Web node-UI libraries surveyed:** [React Flow 12](https://reactflow.dev/)
(Oct 2025 — richest ecosystem, viewport culling, memoized custom nodes),
[litegraph.js](https://github.com/jagenjo/litegraph.js/) (single-canvas,
Blueprint-like, powers ComfyUI at scale), [Rete.js](https://www.libhunt.com/r/rete)
(framework-agnostic dataflow), and the [awesome-node-based-uis](https://github.com/xyflow/awesome-node-based-uis)
list. [SpearNode/SHADERed](https://shadered.org/blog?id=10) shows the
Unity-Shader-Graph-in-the-browser precedent.

**The architectural key:** keep **two coordinated surfaces** — a vertical
**layer stack** (managing the shader layers of e.g. a planet) and a **node
graph** (authoring what's inside a layer). This is how Substance and Unreal keep
both "layers" and "graphs" first-class instead of one unreadable mega-graph.

---

## 3. The decisive insight: fidelity ⟂ framework

The two hard requirements — *accurate live output* and *large-graph
performance* — live in **different layers**, so they are solved independently:

- **Fidelity is owned by the compiler + a shared GPU renderer**, not the diagram
  library. If per-node thumbnails and the main viewer render the *same compiled
  program* on the *same backend/rig* the shipping target uses, the preview is
  correct **by construction** — it is the target shader running. No node-UI
  library touches that pixel path.
- **Scale is owned by keeping GPU work off the DOM.** DOM nodes stay tiny
  (header + sockets + one `<canvas>`), memoized, viewport-culled, zoom-LOD'd; a
  single throttled scheduler re-renders only *dirty + visible* thumbnails into a
  pooled set of small render targets. GPU cost tracks visible-thumbnail count
  (capped), never total node count.

Because of this split, the editor framework choice is "just" about editing
ergonomics, per-node UI richness, polish, and velocity.

---

## 4. Stack decision

**React + React Flow 12 (editor shell) · one shared Three/WebGPU renderer (all
previews) · backend-pluggable compiler.**

Rationale against Sean's exact criteria:

1. **Fidelity by construction** (see §3) — same compiler feeds viewer +
   thumbnails on the target backend.
2. **Large graphs stay fast** — minimal DOM nodes + `onlyRenderVisibleElements`
   + zoom-LOD + a single GPU scheduler with a per-frame thumbnail budget.
3. **Game/film-ready polish + velocity** — React Flow 12 has the deepest
   ecosystem/theming/interaction patterns; the layer stack, blend modes,
   inspectors, marquee/undo come fastest and cleanest here.
4. **Escape hatch** — the document model is framework-agnostic, so if DOM node
   count ever bottlenecks at extreme scale, the *graph view* can be swapped for
   a canvas renderer (the ComfyUI/litegraph model) without touching the model,
   compiler, or preview runtime.

**Alternative seriously weighed:** litegraph.js (single-canvas, proven at ComfyUI
scale with per-node image previews). Not chosen as the foundation because
canvas-drawn widgets make rich per-node editing, the layer-stack UI, and pro
theming harder — and React Flow closes the perf gap precisely because our
per-node DOM is minimal and the heavy work is shared GPU. It remains the
documented fallback.

**Other locked decisions (this session):**

- **Backends: both from day one** — `glsl-es` (drives Legion now) *and*
  `wgsl` + `tsl` (WebGPU/vgpu future). Dual-target from the start proves the
  abstraction earliest.
- **Home: standalone repo** `~/Projects/ShadeGraph` (`snds/*`), Legion consumes
  its exports. Honors portable-first (code in `~/Projects`, not the vault). Docs
  + baton in `07-projects/21-shadegraph/`.

---

## 5. Data model (the durable artifact)

Everything projects from a pure, serializable `ShaderDocument`
(`src/model/document.ts`). Summary:

- **Socket** — `{id, label, type, direction, defaultValue}`; `SocketType` =
  float | vec2..4 | color | bool | int | sampler2D | cubemap | normal.
  `SOCKET_COMPATIBILITY` drives drag-time validation.
- **NodeParam** — an exposed uniform: `{type, value, ui, min/max/step, exposed,
  bindUniform}`. `bindUniform` maps to an existing engine uniform (e.g. Legion's
  `uNormalStrength`); `exposed` promotes it to the document **blackboard**.
- **ShaderNode** — `{type, position, params, bypassed, previewEnabled,
  collapsed, groupId}`. `type` keys the node registry.
- **Edge** — typed `{source:{node,socket}, target:{node,socket}}`.
- **ShaderGraph** — `{nodes, edges, groups, outputNodeId}`.
- **SubGraph** — reusable graph with a typed interface (Unity sub-graph /
  Unreal material function / Houdini HDA).
- **ShaderLayer** — `{name, graph, blend, opacity, enabled, visible, soloed,
  maskGraphId}`. `enabled` = contributes to composite; `visible` = shown in
  preview even if disabled; `soloed` = only soloed layers composite.
- **LayerStack** — bottom-to-top `layers[]` + `activeLayerId`.
- **ShaderDocument** — `{archetype, previewRig, layerStack, subGraphs,
  blackboard, meta}`. `previewRig` picks preview geometry (sphere/fullscreen/
  mesh/skybox) so a planet previews on a sphere, a post-effect on a quad.

This model is the contract every other subsystem depends on and is the thing we
version + migrate.

---

## 6. Compiler (backend-pluggable)

`src/compiler/backend.ts`. A backend is a **pure function** of (document,
options) → `CompiledProgram` — **no GPU device needed to compile** (headless /
CI / agentic, matching vgpu's ethos).

- `ShaderBackend` implements `compileGraph()` and `compileDocument()`.
- Node-type source lives in **per-backend emitters** (`NodeEmitter`) beside the
  backend, so node definitions stay pure data.
- `CompileOptions.previewNodeId` / `previewLayerId` compile the graph *up to* a
  node/layer and output it directly — this is what powers per-node thumbnails
  and Nuke-style solo.
- `BackendRegistry` — the same document compiles to every registered target;
  the UI just picks one.

Day-one targets: `glsl-es` (Legion today), `wgsl` (vgpu/native WebGPU), `tsl`
(Three NodeMaterial on WebGPURenderer — Legion's likely migration path off r171
GLSL). A `glsl3` target is trivial to add later.

---

## 7. Preview runtime (fidelity + scale)

`src/preview/scheduler.ts`. One shared renderer; the `PreviewScheduler`:

- `setDocument / setTarget / setRig` — recompile + re-render on change.
- `setViewerSource({document|node|layer})` — main viewer shows the full
  composite, a soloed node, or an isolated layer.
- `markDirty(nodeId)` / `markAllDirty()` — dirtiness propagates downstream and
  coalesces re-renders.
- `setVisibleNodes()` — only in-viewport nodes get live thumbnails.
- `requestThumbnail()` — resolves to a texture/canvas the node card draws;
  pooled fixed-size render targets, capped resolution.
- `setThumbnailBudget(ms)` — reserve most of the frame for the main viewer so
  interaction stays smooth.
- Adaptive signals (GPU tier · battery · FPS) drop preview res/refresh under
  load (Prism-style).

---

## 8. UI surfaces

```
┌─────────────┬───────────────────────────────┬──────────────┐
│ Layer Stack │        Node Graph (canvas)     │  Inspector   │
│ add/remove  │  React Flow · typed sockets ·  │  params of   │
│ blend/opac  │  per-node live thumbnails      │  selection + │
│ eye/solo    │                                │  blackboard  │
│ reorder     ├───────────────────────────────┤              │
│ (drag)      │        Main Viewer             │  Backend +   │
│             │  composite · solo node/layer   │  code panel  │
└─────────────┴───────────────────────────────┴──────────────┘
```

- **Layer stack (left):** Photoshop-like. Add layer (of a type/preset), delete,
  drag-reorder, eye (visible), enable checkbox, solo, blend-mode dropdown,
  opacity slider, active-layer highlight.
- **Node graph (center):** React Flow. Add-node palette (by category), typed
  color-coded sockets, connection validation, delete, bypass toggle, collapse,
  group/comment frames, per-node thumbnail. Editing the *active layer's* graph.
- **Inspector (right):** params of the current selection with correct widgets
  (slider/color/toggle/select/texture/vector); "expose to blackboard" toggle;
  a read-only compiled-source panel with click-to-source; backend picker.
- **Main viewer (bottom-center):** the shared renderer output for the current
  `ViewerSource`; rig switch; play/pause time.

---

## 9. Legion integration

Legion (`~/Projects/Legion`, Three r171, GLSL ES) is *already* a de-facto node
system — which is why it's the ideal first consumer:

- GLSL **chunks** (`GLSL_SIMPLEX/FBM/PLATES/TERRAIN/RAMP/CLOUDS`) → `legion.chunk.*`
  nodes.
- **Uniforms** → exposed params with `bindUniform`.
- **Per-archetype lab-store** (rocky/continuum/star/blackhole/nebula, Save/Revert)
  → one `ShaderDocument` per archetype + blackboard export.
- **Conceptual layers** (surface/atmosphere/clouds/rings/giant-bands/impostor) →
  the layer stack.

Adapter plan (Phase 4) and the exact seams are in
`~/Projects/ShadeGraph/src/adapters/legion/README.md`. ShadeGraph never depends
on Legion and never writes to the Legion repo without an explicit export.

---

## 10. Phased roadmap

- **Phase 0 — Scaffold (done this session):** repo, contracts (model, compiler,
  registry, preview scheduler), app shell, adapter plan, this doc.
- **Phase 1 — Graph MVP:** React Flow shell wired to the store; add/connect/
  delete typed nodes; a starter node set (input.uv, math.mix/add/mul, noise.fbm,
  color.ramp, output.surface); inspector params; save/load JSON.
- **Phase 2 — Preview runtime:** shared renderer; main viewer; `glsl-es` backend
  end-to-end; per-node thumbnails + solo-to-viewer; dirty scheduling.
- **Phase 3 — Layer stack:** layer CRUD, reorder, blend/opacity/enable/visible/
  solo; composite compile.
- **Phase 4 — Legion adapter:** import chunks + an archetype; blackboard export;
  optional live dev bridge.
- **Phase 5 — WebGPU backends:** `wgsl` + `tsl`; backend switch in the viewer;
  validate a document renders identically across targets.
- **Phase 6 — Scale & reuse:** subgraphs/node groups; large-graph perf pass
  (culling/LOD/budget tuning); adaptive quality; comment frames.

Done-gates borrow Legion's discipline (§ RENDER/BUDGET/NORTHSTAR): a preview is
"accurate" only when a node/layer soloed in ShadeGraph matches the same shader
rendered in the target engine, verified frame-by-frame.

---

## 11. Open questions / decisions pending

- **Name.** "ShadeGraph" is a working name — rebrand candidates welcome.
- **State lib.** Scaffold lists `zustand`; confirm vs. a custom store.
- **WGSL emission strategy.** Hand-rolled emitters vs. leaning on TSL as the
  common IR and letting Three emit WGSL. (Leaning TSL-as-IR reduces backend
  count to essentially 2: GLSL-ES emitter + TSL, with WGSL via Three.)
- **Legion live-bridge.** Worth building in Phase 4, or export-only until Legion
  moves to WebGPU?
- **Persistence.** Local JSON files vs. a document library; and where exported
  Legion presets land in the Legion repo.

---

## 12. Sources

- [vgpu.sh](https://vgpu.sh) · [Codrops: Building Vercel's Prism with vgpu](https://tympanus.net/codrops/2026/09/03/from-rays-to-meshes-building-vercels-prism-with-vgpu/)
- [React Flow](https://reactflow.dev/) · [awesome-node-based-uis](https://github.com/xyflow/awesome-node-based-uis) · [litegraph.js](https://github.com/jagenjo/litegraph.js/) · [Rete.js](https://www.libhunt.com/r/rete)
- [Blender node preview (GSoC)](https://devtalk.blender.org/t/gsoc-2023-shader-editor-node-preview-weekly-reports/29359) · [Node Peek](https://github.com/mlstr0m/node-peek) · [Shader View](https://alekseym88.github.io/shader-view-page/) · [SpearNode / SHADERed](https://shadered.org/blog?id=10)
