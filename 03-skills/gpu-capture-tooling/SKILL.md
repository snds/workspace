---
name: gpu-capture-tooling
description: >
  GPU timing and capture doctrine — browser timestamp-query method first, then RenderDoc / Metal
  / PIX escalation; when stills vs video capture for QA. Use when measuring pass ms, hunting
  hitches, or deciding evidence type for render QA. Triggers: timestamp query, GPU timer,
  RenderDoc, PIX, Metal capture, perfcapture, frame capture, pass timing, GPU profiling.
aliases: [gpu-capture-tooling]
triggers: [timestamp query, gpu timer, gpu profiling, renderdoc, pix capture, metal frame capture, perfcapture, pass timing, frame capture, gpu capture, webgpu timestamp, performance capture]
tier: spoke
hub: realtime-visual-craft
domain: game
related: [realtime-render-performance, render-qa-toolkit, interactive-capture-eval, adapter-webgpu-three, shadow-quality-craft]
surfaces: ["*"]
spec_version: "2.0"
---

# GPU Capture Tooling

Owns **how to measure and escalate** GPU cost and how to choose capture modality for QA. Frame
doctrine: [[realtime-render-performance]]. Visual motion evidence: [[interactive-capture-eval]].
Harness aggregation: [[render-qa-toolkit]].

## Doctrine (order of operations)

1. **Instrument in-app** with timestamp queries / pass scopes → JSON harness (`?perfcapture` or equiv).
2. **Reproduce** the official pose or flythrough from `BUDGET.md` / `NORTHSTAR.md`.
3. **Escalate** to RenderDoc / Metal / PIX only when in-app timers cannot explain the hitch.
4. **Never** ship a "budget OK" claim from an FPS overlay alone.

## Browser timestamp-query doctrine

### Setup
- Enable timestamp query feature on device (`timestamp-query` / equivalent).
- Wrap each named pass: `writeTimestamp` begin/end around encode scope.
- Resolve on CPU **asynchronously**; do not stall the frame for readback every frame.
- Report **median and worst** over a window (e.g. 120 frames), not a single sample.

### Naming contract
Pass names must match `BUDGET.md` lines: `ShadowCSM`, `Opaque`, `SSGI`, `Bloom`, `Tonemap`, etc.
Unnamed "misc" time is a bug in the harness.

### WebGPU gotchas
- Timestamp support is **not universal**; feature-detect and degrade to CPU `performance.now`
  bracketing (less accurate, still directional).
- Disjoint timer / clock domain: treat absolute ms as comparable within one device session.
- Three.js: prefer renderer/pass hooks over wrapping `requestAnimationFrame` only
  ([[adapter-webgpu-three]]).
- `?perfcapture` (or project equivalent) should dump JSON: pose id, pass ms, worst frame, GPU
  tier string.

### Checklist
- [ ] Feature detect → log capability in harness header.
- [ ] Warmup frames discarded (shader compile / residency).
- [ ] Official poses + flythrough both timed.
- [ ] Worst-frame called out; mean alone is insufficient.
- [ ] Capture committed or attached to QA note with machine label.

## Escalation: RenderDoc / Metal / PIX

| Tool | When | What you get |
|---|---|---|
| **RenderDoc** | Draw-call / resource / barrier mystery on desktop GL/Vulkan/D3D | Event browser, texture views, pipeline state |
| **Xcode Metal capture** | Safari / Metal backend, Apple Silicon | Encoder timings, dependency viewer |
| **PIX** | D3D12 / Xbox path | Timing flames, memory, shader QA |
| **Chrome/Edge Performance + WebGPU** | Browser-only, coarse | Timeline; weaker than native GPU captures |

Escalation checklist:
- [ ] Same scene pose as the in-app timer spike.
- [ ] Capture **one** bad frame and one good frame for diff.
- [ ] Note driver / OS / browser versions.
- [ ] Look for: unexpected full-screen passes, mip thrash, sync readbacks, pipeline bubbles.
- [ ] Fix lands with a **re-run of in-app timestamps**, not only a screenshot of the capture UI.

## Stills vs video for QA

| Claim type | Evidence | Fail if |
|---|---|---|
| Material / lighting / exposure | Native still (PNG), grid if needed | Thumbnail / fit-to-window only |
| TAA, volumetrics, dither, cascades, LOD, GI temporal | Video flythrough + frame-by-frame | Still-only approval |
| Frame budget | Harness JSON along path | FPS counter vibe |
| Shadow swimming / cascade | Slow orbit video | Parked camera still |
| Texture residency | Approach video + residency counters | Single parked mip view |

**Rule:** if the failure mode is temporal, the proof is temporal. See framework #12 triple done-gate.

## Hitch taxonomy (map tool → cause)

| Observation | First tool | Likely cause |
|---|---|---|
| One pass ms spikes | Timestamp query | Algorithm / resolution / dispatch size |
| All passes shift later | Timeline / PIX | CPU submit, GC, sync |
| Rare multi-frame stall | Video + counters | Streaming / compile / residency |
| Looks fine, feels laggy | Input→photon path | Buffering / late input sample |
| Only on camera move | Motion capture + CSM/GI timers | Cascade swim / temporal reject |

## Minimal harness schema (illustrative)

```json
{
  "pose": "orbit-01",
  "backend": "webgpu",
  "timestampQuery": true,
  "frames": 120,
  "passes_ms": { "Opaque": { "p50": 2.1, "p99": 3.4 }, "ShadowCSM": { "p50": 1.2, "p99": 4.8 } },
  "worst_frame_ms": 18.2
}
```

Store under the project's perf-capture path; compare against `BUDGET.md` envelopes.

## Failure modes of the tooling itself

- Trusting first frame after shader compile.
- Readback every frame → the profiler causes the hitch.
- Comparing timestamps across different GPUs without retargeting budgets.
- RenderDoc on a different quality tier than ship settings.
- Judging pre-tonemap / pre-composer buffers as final look.

## Related
- hub → [[realtime-visual-craft]]
- peer ↔ [[shadow-quality-craft]] · [[virtual-texturing-ops]] · [[adapter-webgpu-three]]
