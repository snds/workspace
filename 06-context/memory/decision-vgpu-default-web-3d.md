---
type: decision
description: New web 3D / shader / GPU work defaults to vgpu (vgpu.sh), not a fresh Three.js stack.
created: 2026-09-04
confidence: high
relations:
  builds-on: ["[[decision-externalize-everything-to-workspace]]"]
---

## For future agent
- **TL;DR:** Greenfield browser GPU work uses vgpu. Existing Three.js ship paths (Legion) stay on the Three adapter until an explicit migration. DCC craft is unchanged.
- **As of:** 2026-09 · **Status:** current

## Context — what forced a choice
The workspace already had deep Three.js / TSL / GLSL skills and a photoreal adapter, but no
project-agnostic WebGPU library with agent docs, MCP, CLI validation, and headless CI. vgpu
(Vercel, MIT, npm `vgpu`) is that library. ShadeGraph and Legion remain separate product repos;
the default has to live in the portable workspace or every project re-derives it.

## Decision — what we chose
1. **Default runtime** for new web 3D, WGSL, compute, canvas GPU effects, and headless snapshots:
   vgpu, via skill [[vgpu-webgpu]] and capabilities `vgpu-mcp` + `vgpu-cli`.
2. **Do not migrate** an existing Three.js tree as a side effect of an unrelated task.
3. **DCC** (Blender/Maya/Substance, topology, UVs, rigs) stays [[lead-3d-designer]]; delivery
   format for the web is glTF/GLB + `gltf-transform`.
4. Marketplace engine skills (R3F, Babylon, PlayCanvas) and optional MCPs (chisel, maige-3d, Godot, Unity, AgentBridge) are **extensions** ([[web-3d-extensions]]); they are not the web default and are not standing Cursor servers.

## Rationale — why, and what we rejected
- vgpu is designed for agents (`agents.md`, `llms.txt`, hosted MCP, `npx vgpu check/docs/examples/doctor`).
- Same program in browser, Node/Dawn, and mock tests — matches how this workspace proves work.
- Rejected "always Three" as the greenfield default: extra scene-graph cost and weaker agent surface.
- Rejected "rewrite Legion to vgpu now": the ship adapter and GLSL chunks are the live renderer.

## Consequences — what this commits us to
- Agents load [[vgpu-webgpu]] on web GPU work and preflight MCP/CLI.
- Cursor/Claude MCP templates include `https://vgpu.sh/api/mcp` as standing; optional 3D servers live in `cursor-mcp-3d-extensions.json.example`.
- GLSL/TSL skills remain for existing Three code, not as the default for new shaders.
- Optional editor/CSG/demo MCPs are documented and capability-gated so an agent can use them when the working set is that engine.
