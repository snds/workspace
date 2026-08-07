---
name: render-qa-toolkit
description: >
  Deterministic measurement toolkit for realtime / photoreal render QA — frame-budget
  ingestion from ?perfcapture JSON, pass attribution waterfalls, native 1:1 tile grids,
  luminance/exposure histograms, false-color overlays, temporal shimmer deltas, motion-stress
  peaks, northstar SSIM match, ffmpeg frame extract, and best-effort Visual Failure-Mode
  Ledger heuristics. Use when proving the triple done-gate (native stills + motion frames +
  measured ms), auditing GPU pass costs, flagging banding/clip/shimmer from captures, or
  comparing a render still to a northstar. Trigger on: perfcapture, frame budget, pass
  waterfall, native grid tiles, false color exposure, temporal delta, shimmer, flythrough
  QA, motion stress frames, render SSIM, ledger detect. Do NOT trigger for UI craft audits
  (use visual-qa-toolkit) or semantic VLM critique alone (use vision / lead-visual-qa).
aliases: [render-qa-toolkit]
triggers: [render qa, perfcapture, frame budget, pass attribution, native grid, false color exposure, temporal delta, shimmer, flythrough qa, motion stress, render ssim, ledger detect, gpu ms]
tier: cross-cutting
domain: quality
hub: realtime-visual-craft
related: [visual-qa-toolkit, native-visual-eval, failure-mode-premortem, reference-video-review, realtime-render-performance, interactive-capture-eval, realtime-visual-craft, lead-visual-qa, visual-qa-photoreal-rendering]
requires: [ffmpeg]
surfaces: ["*"]
spec_version: "2.1"
---

# Render QA Toolkit

A sibling of [[visual-qa-toolkit]] for **realtime / photoreal render measurement**. Ten focused
Python scripts plus an orchestrator that turn harness JSON and lossless captures into structured
findings — the measurement half of framework [#12 Realtime Photoreal Operational](../../01-frameworks/12-realtime-photoreal-operational-framework.md).

> **Pairs with capture + craft, not a replacement for judgment.**
> - [[native-visual-eval]] — get true 1:1 pixels before any visual claim
> - [[interactive-capture-eval]] — record → extract → grid-assess
> - [[realtime-visual-craft]] — command router for the #12 operating sequence
> - [[failure-mode-premortem]] + [Visual Failure-Mode Ledger](../../08-knowledge/cross-domain/visual-failure-mode-ledger.md) — technique failure modes
> - [[lead-visual-qa]] / [[visual-qa-photoreal-rendering]] — semantic judgment after measurement

**Legion** is the first consumer of `?perfcapture` JSON through this toolkit. Paste console /
`window.__perfCapture` output into a file the user provides — never invent paths.

## Triple done-gate (all three required)

A still-only report is **incomplete**. This toolkit supplies the instruments for each gate:

| Gate | What "done" requires | Toolkit checks |
|---|---|---|
| **A — Still fidelity** | Native-resolution captures; 1:1 tile grid when the subject exceeds one truthful view; match northstar + ledger tells | `native_grid`, `histogram_hdr`, `false_color_exposure`, `reference_match`, `ledger_detect` |
| **B — Motion / interaction** | Recorded paths covering move / look / roll / zoom-scale; frame-by-frame review; dense samples at stress points | `video_extract`, `temporal_delta`, `motion_stress` |
| **C — Frame budget** | Measured worst-frame / pass ms at official poses **and** along flythroughs — from harness JSON, not FPS vibes | `frame_budget`, `pass_attribution` |

Claiming "fixed / matches / ships" without all three gates is a ban under #12.

## When to use this skill

| Check | What it measures |
|---|---|
| `frame_budget` | Ingest `{passes:[{name,ms}], total_ms, …}` (also Legion `rows` / `gpuMedianMs` shapes) vs config budget; print waterfall; non-zero exit on fail |
| `pass_attribution` | Rank passes by ms; flag dominant shares |
| `native_grid` | Split PNG into 1:1 tiles; reject undersized "native"; warn if width <800 and labeled native |
| `histogram_hdr` | Luminance histogram stats; flag crush / blowout |
| `false_color_exposure` | Write false-color exposure overlay PNG |
| `temporal_delta` | Sequence mean abs diff; flag shimmer |
| `motion_stress` | Labeled stress-frames folder; summarize peaks |
| `reference_match` | SSIM + RGB/Lab mean-abs vs northstar; annotated diff |
| `video_extract` | ffmpeg wrapper to extract frames (**requires ffmpeg on PATH**) |
| `ledger_detect` | Best-effort heuristic hints → ledger IDs (A-01, A-04, A-05, Z-01, …) |

## Invocation protocol — inputs come from the user, not from filesystem hunting

The toolkit is project-agnostic. It operates on **paths the user supplies**: a perfcapture JSON
file, a PNG still, a frames folder, a video, a northstar reference, and a config. It has no
knowledge of Legion's checkout layout, capture dump folders, or northstar asset trees.

When an agent runs the toolkit on behalf of a user:

1. **Ask for the input path(s).** Don't assume `~/Downloads` or hunt the repo for
   `.tmp-continuum-frames`. If the user uploaded a file, use that path.
2. **Ask which config.** `configs/default.yaml`, `configs/legion.yaml` (tuning example), or a
   project-owned config path the user controls.
3. **Ask for the reference still** if `reference_match` is in scope.
4. **Ask for the frames folder / video** if motion checks are in scope.
5. **Ask whether the still is labeled native** before treating it as Gate A evidence
   (`--labeled-native`).

Never hunt the filesystem for project-specific artifacts. Configs and CLI paths carry context.

### Legion `?perfcapture` example

Official pose pattern (document when locking a budget baseline):

```
?lab=planet&perfcapture&au=0.8&w=1280&h=720&dpr=2
```

Save the printed JSON / `window.__perfCapture` to a file the user names, then:

```bash
python qa-suite.py \
  --perf ~/captures/lab-0.8au.json \
  --config configs/legion.yaml \
  --output ~/qa-out/lab-0.8au \
  --only frame_budget,pass_attribution
```

Simplified JSON shape (also accepted):

```json
{
  "passes": [
    {"name": "RenderPass", "ms": 4.2},
    {"name": "UnrealBloomPass", "ms": 2.1}
  ],
  "total_ms": 11.8
}
```

Legion native shapes (`mode: passes|composite|capture` with `rows` / `gpuMedianMs`) are normalized
automatically via `normalize_perfcapture()`.

## How to invoke

### Full suite

```bash
cd "03-skills/render-qa-toolkit"
python3 qa-suite.py \
  --image ~/captures/frame.png \
  --perf ~/captures/perf.json \
  --config configs/default.yaml \
  --output ~/qa-out \
  --labeled-native
```

### Subset + mixed inputs

```bash
python3 qa-suite.py \
  --image ~/captures/frame.png \
  --perf ~/captures/perf.json \
  --frames ~/captures/fly-frames \
  --reference ~/northstars/planet_still.png \
  --config configs/legion.yaml \
  --output ~/qa-out \
  --only frame_budget,native_grid,temporal_delta,reference_match \
  --labeled-native
```

### Individual script

```bash
python3 -m scripts.qa_frame_budget \
  --input ~/captures/perf.json \
  --config configs/legion.yaml \
  --output ~/qa-out
```

Every script and the suite expose `--help`.

## Input requirements per check

| Check | Input | Notes |
|---|---|---|
| `frame_budget`, `pass_attribution` | JSON file | `--perf` |
| `native_grid`, `histogram_hdr`, `false_color_exposure`, `reference_match`, `ledger_detect` | image file | `--image` (PNG preferred) |
| `reference_match` | image + reference | `--image` + `--reference`; identical dimensions |
| `temporal_delta`, `motion_stress` | folder of frames | `--frames`; stress labels = prefix before `_NNN` |
| `video_extract` | local video | `--video`; **ffmpeg required**; no URL download |

## Config structure

YAML. Each check has a section; omit a section to use script defaults. Set `enabled_checks` to
run a subset; otherwise sections with `enabled: false` are skipped.

**Shipped configs:**

- `configs/default.yaml` — generic 14 ms real budget, standard thresholds
- `configs/legion.yaml` — Legion pose URL placeholders, flythrough notes, slightly tighter
  shimmer / clip thresholds, denser `video_extract` fps

For a real project gate, author a config the user owns and pass `--config /path/to/it.yaml`.

## Outputs

- `qa_report.md` / `qa_report.json` — consolidated
- `<check>_report.md` — per-check
- Artifacts: waterfalls, tile grids, histograms, false-color overlays, delta heatmaps, extracted frames

## Exit codes

- `0` — no critical or high findings
- `1` — ≥1 high
- `2` — ≥1 critical (also `qa_frame_budget` alone when over budget)

## Honest limits

- Ledger detection is **heuristic** — confirm at native resolution; do not treat as proof.
- Temporal MAD flags motion energy, not semantic "wrong LOD."
- SSIM does not understand Spirit vs Literal fidelity contracts — judgment stays with visual QA.
- `video_extract` blocks without ffmpeg; other checks run without it.

## File layout

```
render-qa-toolkit/
├── SKILL.md
├── README.md
├── requirements.txt
├── qa-suite.py
├── scripts/
│   ├── __init__.py
│   ├── _common.py
│   ├── qa_frame_budget.py
│   ├── qa_pass_attribution.py
│   ├── qa_native_grid.py
│   ├── qa_histogram_hdr.py
│   ├── qa_false_color_exposure.py
│   ├── qa_temporal_delta.py
│   ├── qa_motion_stress.py
│   ├── qa_reference_match.py
│   ├── qa_video_extract.py
│   └── qa_ledger_detect.py
└── configs/
    ├── default.yaml
    └── legion.yaml
```

## Related
- hub → [[realtime-visual-craft]]
- peer ↔ [[realtime-visual-craft]]
- peer ↔ [[visual-qa-toolkit]] · [[native-visual-eval]] · [[failure-mode-premortem]] · [[reference-video-review]] · [[realtime-render-performance]] · [[interactive-capture-eval]] · [[lead-visual-qa]] · [[visual-qa-photoreal-rendering]] · [[lead-game-developer]] · [[legion-project]] · [[rendering-guild]]
