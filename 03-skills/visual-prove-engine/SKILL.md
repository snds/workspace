---
name: visual-prove-engine
description: >
  Deterministic visual measurement engine that makes visual verdicts falsifiable.
  Use when a visual claim needs proof instead of narrative: proving a build against
  a reference contract (cuespec), ranking candidate builds by closeness to a
  northstar, detecting stutter/flicker/teleport in frame sequences, verifying an
  interaction actually changed pixels, tracking build-over-build improvement with
  regression rollback, or checking the engine's own detectors against planted
  defects. Trigger on: prove this build, cuespec, measured verdict, does the
  screenshot really match, rank these builds, visual improvement loop, jank check,
  frame-sequence analysis, action-effect verification, self-critical visual review,
  "the code says it renders but does it". A cue passes only if an instrumented
  probe measured it; agent or human declarations are recorded as attestations and
  never count toward a Matches verdict. Structure-independent: judges pixels, not
  DOM or code claims. Do NOT use for heuristic/experiential critique
  (lead-visual-qa), single-metric screenshot audits (visual-qa-toolkit), or
  photoreal render judgment (render-qa-toolkit).
aliases: [visual-prove-engine, vqa-engine, prove-engine]
triggers: [prove this build, cuespec, measured verdict, visual prove, rank builds, improvement ledger, visual trajectory, jank check, frame sequence analysis, action-effect, planted defects, visual calibration, self-critical visual]
tier: cross-cutting
domain: quality
hub: lead-visual-qa
related: [visual-qa-toolkit, render-qa-toolkit, native-visual-eval, interactive-capture-eval, visual-reference-replication, reference-video-review]
requires: [python-imaging, ffmpeg]
spec_version: "2.1"
---

# Visual Prove Engine

One CLI (`vqa.py`) that turns "looks right to me" into a measured, reproducible,
regression-guarded verdict. Built because per-project prove scripts kept declaring
`pass: True` from code inspection while the pixels disagreed (the LCARS silhouette
chip was claimed present in a passing cue matrix; this engine measured 0.0 percent
foreground in that zone and the crop confirmed pure black).

The core split: **the cuespec is data; the runner is tested code.** Cue targets are
authored once from the reference, then every build is measured against them by the
same probes the calibration suite validates.

## Verdict vocabulary (non-negotiable)

- **measured pass/fail**: an instrumented probe sampled build pixels and compared
  against the contract. Only these count toward the verdict.
- **attested**: a human or code-level claim (text identity without OCR, "emitted via
  Scene IR"). Recorded, displayed, never counted as proof.
- **matches / partial / fail**: computed from measured cues + coverage, never declared.
- Capture provenance is part of the verdict: no `*.capture.json` manifest means the
  report says `unverified` even when all cues pass.

## Subcommands

| Command | What it does |
|---|---|
| `vqa doctor` | Dependency + degradation report (numpy/Pillow required; scipy/OpenCV accelerate; ffmpeg only for `--video`) |
| `vqa verify-capture IMG` | Validate a capture manifest (viewport, DPR, freeze state) |
| `vqa perceive IMG` | Structure-independent inventory: regions, shapes, palette, background, plus ledger failure-mode detectors (banding, blowout, illegal shapes) |
| `vqa prove BUILD CUESPEC` | Run a cuespec, emit `*.prove.json` + `*.prove.md` with measured/attested split |
| `vqa compare REF BUILD...` | Register (phase correlation), SSIM + delta-E maps, rank candidates by closeness |
| `vqa motion --frames DIR\|--video F` | Duplicate/stutter, flicker, trajectory smoothness (speed/accel/jerk, overshoot, settle), vsync jank with timestamps |
| `vqa interact SPEC` | Action-effect verification: expected pixel change happened in region, no side effects elsewhere, catches dead controls and phantom claims |
| `vqa score --ledger L --from PROVE` | Append run to improvement ledger; movement = improved/regressed/flat; `--enforce` exits non-zero on regression (rollback gate) |
| `vqa calibrate` | Self-test: synthesizes a scene with planted defects + known-good variants, requires every detector to catch every defect with zero false fires |

## The reliability contract

Trust in the engine is itself measured, not asserted:

1. `vqa calibrate` plants defects with known ground truth (color drift, layout shift,
   radius loss, single-corner card, banding, missing/extra regions, gutter drift,
   dropped frames, teleport, flicker, dead control, side effect) alongside clean and
   noise-only variants. Every detector must catch every planted defect and must not
   fire on the clean variants. Exit is non-zero otherwise. Run it after any engine change.
2. Cue thresholds are derived from reference measurements (scout the reference with
   the same probes), never from what a build happens to produce. Record the
   derivation in the cuespec `_provenance` field.
3. The ledger reports `newly_failing` cues even when the aggregate score improved,
   so an improvement claim cannot hide a localized regression.

## Improvement loop (the reliable path from worse to better)

```
1. scout reference  ->  author S-XXX.cuespec.json (targets from measured reality)
2. vqa prove build cuespec        -> measured verdict + failing cues with margins
3. fix the worst-margin cue only  -> smallest change that moves a measurement
4. vqa prove + vqa score --ledger -> movement recorded; --enforce blocks regression
5. repeat until matches; ledger.md is the proof artifact
```

Worked example on real project data: `07-projects/20-lcars-generative-interface/docs/construction/S-SYS47-01.cuespec.json`
(19 cues, 16 measured / 3 attested). Build v2 scored 0.50 (8/16), v3 scored 0.81
(13/16, movement improved, 7 newly passing, 2 newly failing flagged). Ranking agreed
with human judgment on v2 vs v3, and prove refuted one false "pass" from the manual
cue matrix (silhouette chip). Ledger: `S-SYS47-01.ledger.md` in the same directory.

## Honest degradation

Core probes run on numpy + Pillow alone. SciPy/OpenCV accelerate connected-components
when present (identical results, faster). `--video` needs ffmpeg; without it, supply
`--frames`. `vqa doctor` reports the active tier; reports embed it so a verdict can
never silently depend on an absent tool.

## Related
- hub → [[lead-visual-qa]]
- peer ↔ [[visual-qa-toolkit]] · [[render-qa-toolkit]] · [[native-visual-eval]] · [[interactive-capture-eval]] · [[visual-reference-replication]] · [[reference-video-review]]
