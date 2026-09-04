---
title: ShadeGraph
type: project
status: Building
triggers: [shadegraph, shader tool, node shader, shader editor]
frameworks: [aesthetic-lens, ui-ux-operational, component-pattern, integration, workspace-contribution]
related_projects: [13-legion]
---

# ShadeGraph (21-shadegraph)

A reusable, node-based shader design tool. Compose layered shaders as a live
node graph, see each node's output on the node, solo any node/layer to a full
preview, and compile the same document to **GLSL ES**, **WGSL** (vgpu/WebGPU),
or **Three TSL**. Standalone + generic; **Legion** is the first consumer,
driving its planet materials.

- **Status:** Building (Phase 0 scaffold complete)
- **Code repo:** `~/Projects/ShadeGraph` (`snds/*`, own git repo — *not* in this
  vault, per portable-first: code lives in `~/Projects`).
- **This folder:** design docs + continuity baton only (same pattern as 13-legion).

## Docs

- [[07-projects/21-shadegraph/docs/DESIGN-PLAN|Design & Research Plan]] — the
  research synthesis, stack decision, data model, and phased roadmap.
- [[07-projects/21-shadegraph/SESSION-STATE|SESSION-STATE]] — operational baton.

## Origin

Prompted by [vgpu.sh](https://vgpu.sh) and the Codrops article
[_From Rays to Meshes — Building Vercel's Prism with vgpu_](https://tympanus.net/codrops/2026/09/03/from-rays-to-meshes-building-vercels-prism-with-vgpu/):
the editable version of the read-only render-pipeline visualizer the author
built there.

See `06-context/project-context.md` for the registry entry.
