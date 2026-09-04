---
name: adapter-unity-hdrp
description: >
  Thin Unity HDRP corollary adapter — HDRP pipeline, Adaptive Probe Volumes (APV), Volume framework
  as high-ceiling references for northstar matching against web/Three ship paths. Not a full Unity
  production manual. Triggers: Unity HDRP, APV, Adaptive Probe Volume, Volume framework, Unity
  northstar, HDRP reference.
aliases: [adapter-unity-hdrp]
triggers: [unity hdrp, adapter unity, adaptive probe volume, apv, hdrp volume, unity volume framework, unity northstar, hdrp gi, unity lightmap bake]
tier: spoke
hub: realtime-visual-craft
domain: game
related: [realtime-visual-craft, img-photoreal-rendering, dynamic-gi-production, bake-orchestration, adapter-webgpu-three, adapter-unreal, web-3d-extensions]
requires: [unity-mcp]
surfaces: ["*"]
spec_version: "2.1"
---

# Adapter — Unity HDRP (northstar corollary)

Thin corollary: HDRP + APV + Volumes as **reference ceilings** for lighting architecture and probe
workflows. Ship path for browser titles remains [[adapter-webgpu-three]]. Doctrine:
[[realtime-visual-craft]] / [[img-photoreal-rendering]].

## When to load this skill

- Northstar refs are HDRP footage / screenshots.
- Designing probe-grid behavior inspired by APV for a custom web irradiance volume.
- Baking in Unity for native HDRP content or export into web ([[bake-orchestration]]).
- Comparing Volume-based post/exposure stacks to Three composer order.
- Driving a **live Unity Editor**. Capability `unity-mcp` (Coplay preferred for personal-solo;
  official Unity 6 MCP needs Cloud + AI seat). Preflight; if absent, edit C#/scenes on disk.
  See [[web-3d-extensions]].

## Feature → doctrine mapping

| HDRP feature | What it proves | Web / Three corollary |
|---|---|---|
| **HDRP lighting architecture** | Physically based lights, units, exposure | Lock units/exposure in `RENDER.md`; linear + tonemap |
| **APV** | Runtime probe sampling for dynamic objects in baked worlds | Custom SH/octahedral volume; bake static ([[dynamic-gi-production]]) |
| **Volume framework** | Local/global overrides (exposure, bloom, shadows) | Explicit stacked post + zone volumes you own; no silent globals |
| **HDRP SSGI / SSR paths** | Screen-space multipath quality bar | Optional thin SSGI; document disocclusion fails |
| **Progressive / baked GI** | Lightmap authority | Cycles or Unity bake → pack → load |

## APV lessons for web probes

Steal these behaviors, not the C# API:
1. **Separate** static bake from dynamic object sampling.
2. **Blend** probes with hysteresis; avoid single-texel flicker.
- [ ] Sky/occlusion awareness when placing probes near walls.
- [ ] Local Volumes that override probe intensity / exposure for interiors.
- [ ] Streaming / brick concepts → your residency budget ([[virtual-texturing-ops]] for textures;
  probe bricks analogous for irradiance).

## Volume framework lessons

- Global volume = project defaults (tonemap, bloom, exposure).
- Local volumes = interiors / biomes; priority + blend distance authored.
- Web analog: a small stack of post profiles with spatial blend, not one god-composer with magic.

Checklist when mirroring a Unity look:
- [ ] Exposure mode understood (fixed vs automatic) — auto exposure must be motion-tested.
- [ ] Bloom threshold in HDR space before tonemap.
- [ ] Color grading after tonemap or documented as display-referred.
- [ ] Shadow / contact-shadow settings noted as CSM/contact targets, not copy-paste.

## Bake notes

- Lightmap + APV bake: keep metadata (exposure, probe spacing) with the content hash.
- Export to Three: lightmaps linear, sRGB off; probes as SH or octahedral atlas
  ([[bake-orchestration]]).
- Do not ship Unity-only shader graphs as if they were TSL — rebuild intent in materials
  ([[threejs-materials-master]]).

## Honest ceilings

| Claim | Verdict |
|---|---|
| "APV in the browser" | Behavior yes (custom); package no |
| "HDRP Volume parity" | Profile stack yes; full framework no |
| "Match HDRP SSGI" | Partial; off-screen fail remains |
| "Same auto-exposure feel" | Possible; must motion-QA |

## Failure modes

- Copying HDRP default Volume look (heavy bloom/grain) as "cinematic" without northstar.
- Assuming APV fixes missing lightmap UVs.
- Automatic exposure fighting bake exposure (double adaptation).
- Using Editor Game view (scaled) for pixel verdicts — capture native.

## Related
- hub → [[realtime-visual-craft]]
- peer ↔ [[adapter-webgpu-three]] · [[adapter-unreal]] · [[dynamic-gi-production]] · [[bake-orchestration]] · [[lead-3d-designer]] · [[web-3d-extensions]]
