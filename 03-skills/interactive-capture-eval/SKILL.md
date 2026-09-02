---
name: interactive-capture-eval
description: >
  Protocol for evaluating realtime visuals under real camera and interaction: define interaction
  paths → record at native/lossless → extract frames (ffmpeg) → grid-assess 1:1 tiles per framework
  #10 / native-visual-eval → judge motion first, then still beauty. Use whenever a claim involves
  camera move, look, roll, zoom/scale traversal, LOD, TAA, volumetrics, dither, cascades, or
  floating-origin — still-only approval is an automatic fail. Pairs with reference-video-review for
  decomposition and realtime-visual-craft flythrough/interact. Triggers: flythrough capture, record
  interaction, extract frames, motion QA, frame-by-frame review, interactive path.
aliases: [interactive-capture-eval]
triggers: [interactive capture, flythrough capture, record path, extract frames, ffmpeg frames, motion qa, frame-by-frame, interaction path, camera path review, judge motion first, lossless capture, native recording]
tier: cross-cutting
domain: quality
related: [native-visual-eval, reference-video-review, render-qa-toolkit, realtime-visual-craft, lead-visual-qa, visual-qa-photoreal-rendering, failure-mode-premortem]
surfaces: ["*"]
spec_version: "2.0"
---

# Interactive Capture Eval

**Directive: for any motion- or interaction-sensitive claim, record the path, extract frames, assess
at native 1:1, and judge motion before still beauty. A single screenshot cannot close the gate.**

This is the measurement protocol behind framework [#12](../../01-frameworks/12-realtime-photoreal-operational-framework.md)
gate B and the `flythrough` / `interact` command in [[realtime-visual-craft]]. Capture integrity follows
[#10](../../01-frameworks/10-perception-integrity.md) / [[native-visual-eval]].

---

## When to load

- Camera, LOD, temporal AA, volumetrics, dither, shadow cascades, scale traversal, origin shifts
- Any "fixed / matches / ships" claim that includes how it looks **while moving**
- Closing `realtime-visual-craft` harden-done when motion is in scope

Do **not** use a live window glance or a fit-to-window screenshot as the archive of record.

---

## Protocol

### 1 · Define interaction paths

Write path IDs (usually into project `RENDER.md`):

| Must cover | Examples |
|---|---|
| Move | Orbit, strafe, translate along surface approach |
| Look | Pitch/yaw sweeps across contrasty silhouettes |
| Orientation / roll | Banked turns if the camera allows |
| Zoom / scale | Near↔far, globe→surface, weapon→horizon |
| Project stresses | LOD swaps, cascade splits, origin recenter, disocclusion-heavy pans |

Each path needs: start pose, end pose, duration or input script, and **what failure it is meant to expose**.

### 2 · Record at native / lossless

Prefer, in order:

1. Project harness PNG sequence / lossless frame dump at drawable size
2. High-bitrate video at native framebuffer resolution (not CSS display size)
3. OS screen capture only if it preserves native pixels end-to-end

Log: resolution, refresh, path ID, build/preset, TAA history warm/cold, whether vsync/rAF locked.

**Ban:** JPEG screen grabs, compressed preview exports, downscaled "share" videos as verdict sources.

### 3 · Extract frames (ffmpeg)

Base extract (adjust fps to content; denser under stress):

```bash
ffmpeg -i capture.mp4 -vf "fps=12" -start_number 1 out/f_%03d.png
```

Dense sample a stress window (example: seconds 4.0–6.5 at 30 fps):

```bash
ffmpeg -ss 4.0 -to 6.5 -i capture.mp4 -vf "fps=30" out/stress_%03d.png
```

Prefer PNG. Keep original video alongside extracts. For already-lossless PNG sequences, skip re-encode; index the sequence directly.

Use [[reference-video-review]] when comparing against northstar trailer clips (timestamps, key frames).

### 4 · Grid-assess 1:1 tiles (#10)

For any frame under judgment:

1. Open/read at **native** pixel size
2. If larger than one truthful tool view, **chunk into 1:1 tiles** and assess tile-by-tile
3. State dimensions judged
4. Treat any thumbnail / fit-to-window image as a **locator only**

Never close "banding gone / aliasing gone / matches" from a downsampled tile.

### 5 · Judge motion first

Order of judgment:

1. **Temporal stability** — crawl, shimmer, ghosting, pumping exposure
2. **Structural continuity** — LOD pops, cascade seams, morph cracks
3. **Energy continuity** — flash frames, tonemap flicker, bloom popping
4. **Then** still beauty / northstar still match on representative frames

A beautiful mid-path still with swimming cascades is a fail.

---

## Report shape

```
## Interactive capture: {path IDs}
Record: {res, codec/PNG, duration, build}
Extract: {base fps, stress windows}
Frames reviewed: {list or ranges}
Motion findings: …
Still findings (native tiles): …
Gate B: met | not-met
```

---

## Pairing

| Step | Skill |
|---|---|
| Native tiles | [[native-visual-eval]] |
| Ref / capture video breakdown | [[reference-video-review]] |
| Photoreal lens | [[visual-qa-photoreal-rendering]] |
| Command surface | [[realtime-visual-craft]] (`flythrough`) |

---

## Absolute bans

- Still-only QA for motion-sensitive features
- Verdicts from low-res / fit-to-window / lossy previews
- Closing done on one hero frame when interaction is in the claim
- "Looked fine while I flew around" with no artifact on disk

## Related
- peer ↔ [[lead-visual-qa]] · [[native-visual-eval]] · [[reference-video-review]] · [[render-qa-toolkit]] · [[realtime-visual-craft]] · [[visual-qa-photoreal-rendering]] · [[failure-mode-premortem]] · [[rendering-guild]] · [[legion-project]]
- peer ↔ [[visual-prove-engine]]
