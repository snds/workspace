---
name: visual-reference-replication
description: >
  Literal recreation of a complex UI or visual surface from named reference stills/video —
  not "inspired by." Forces Construction IR transcription, measured geometry/color/type,
  instrumented prove-gates (SSIM/Δe/alignment), and refusal of VLM narrative as measurement.
  Proves a system pack (grammar + tokens + catalog + northstars) can be transcribed and emitted
  programmatically — LCARS is the hard exam; the pipeline is meant to transfer to other
  aesthetics/systems. Use when: recreate this screen, match this reference exactly, literal
  fidelity, design transcription, Okudagram/LCARS recreation, pixel-accurate UI clone, reference
  teardown before coding, "farce" / inspired-by rejection, northstar Literal contract, systemic
  visual recreation, system pack. Load BEFORE implementing UI from screenshots or screensaver
  loops. Distinct from lead-visual-qa Spirit evaluation and from redesign/uplift.
aliases: [visual-reference-replication, literal-ui-replication, design-transcription]
triggers: [literal match, recreate this screen, match this reference, design transcription, construction ir, pixel accurate ui, okudagram recreation, lcars recreation, inspired by rejected, northstar literal, reference teardown, visual replication, system pack, systemic recreation]
tier: spoke
hub: lead-visual-qa
domain: quality
prerequisites: [design-foundations, native-visual-eval]
related: [visual-qa-toolkit, reference-video-review, lead-visual-qa, design-engineer, realtime-visual-craft, visual-prove-engine]
governed_by: []
governs: []
surfaces: ["*"]
spec_version: "1.2"
---

# Visual Reference Replication (Literal)

**Default contract is Literal.** "Looks LCARS-ish," "captures the vibe," and "tests green" are not done criteria. Done = named northstar cues pass under native-resolution evidence + measurement.

**Program framing:** faithful recreation is how you *prove* a visual system is understood well enough to emit it programmatically. The Construction IR + cue + prove pipeline is **system-agnostic**. Domain chrome (Okudagram elbows, Material cards, …) lives in a **system pack**. If the pack is LCARS today, another aesthetic can load later without inventing a new method — but only after the hard pack is proven Literal and IR-driven.

If the user has not named a fidelity contract, **ask**. If they say exact / recreate / match / farce / inspired-by is insufficient → **Literal**. Do not silently downgrade to Spirit.

## Four axes of fidelity

For generative / systemic work, Literal aesthetic alone is incomplete. Track all four:

| Axis | Question |
|---|---|
| Concept | What kind of product/surface is this? |
| Context | What situation/role/data drives the assembly? |
| Intent | What job does each region communicate? |
| Aesthetic | Does measured geometry/color/type/motion match the northstar? |

Recreation briefs usually start on Aesthetic (prove the eye). Product work must not drop Concept/Context/Intent when wiring Scene IR and recipes.

## Hard refusals

Stop and correct course if any of these appear:

1. **Coding before Construction IR** for the named still
2. **Hex / radii / gutters invented from VLM prose** instead of sampled from native pixels
3. **Any Matches Literal / Partial / Fail verdict, or a progress claim, without prove artifacts** (native side-by-side + at least one instrumented check + cited prove.json or capture paths). Declaring match without measurement is the original form of this refusal.
4. **Shipping placeholder assets** (hand-waved SVG, emoji, stock) as stand-ins for reference geometry without labeling them `PLACEHOLDER — not northstar`
5. **Letting secondary constraints** (token count caps, APCA retunes, density) silently rewrite the visual authority of the northstar without an explicit ADR
6. **Single-corner “cards” as LCARS** (three sharp + one radius) — legal shapes are pill, sharp bar/segment, or true elbow only (ledger **C-09**)

## Pipeline (mandatory order)

```
Task Progress:
- [ ] 0. Contract: Literal | Spirit | Standard | Intent (name it)
- [ ] 1. Northstar: path/URL + S-ID / V-ID + crop plan
- [ ] 2. Native capture of reference (and later of build)
- [ ] 3. Construction IR transcribed (see reference/construction-ir.md)
- [ ] 4. Cue matrix written (must-pass list)
- [ ] 5. Implement only from IR + cue matrix
- [ ] 6. Prove: native side-by-side + measurement
- [ ] 7. Verdict: Matches Literal | Partial (list gaps) | Fail
```

Step 6 is part of implement, not a later `/verify`. Step 7 is illegal if step 6 is unchecked.

### 0–1. Contract + northstar

Write into the project `NORTHSTAR.md` (or session baton if no file yet):

| ID | Path | Match type | Acceptance cues (falsifiable) |
|---|---|---|---|
| S-01 | …/still.png | Literal | spine width ratio; elbow outer R; gutter px; 3 sampled fills Δe≤3; type face/case/tracking |

No moodboard blobs. One row per still or key video frame.

### 2. Native pixels first

Load [[native-visual-eval]]. Reference and build captures are PNG at native subject resolution. Thumbnails/locators are not evidence.

### 3. Transcribe Construction IR

Produce a machine-checkable structure **before** React/CSS. Minimum fields in [reference/construction-ir.md](reference/construction-ir.md):

- Canvas size, safe margins, gutter constant
- Frame graph (spines, elbows, rails, voids) with measured sizes
- Segment inventory (id, role, fill sample Lab/hex, radius corners, label, alignment)
- Content modules in reading order with bounding boxes
- Typography specimens (face, weight, case, size px, tracking)
- Motion cues if video (what moves, cadence, what stays locked)
- Asset list (schematic / icon / texture) with source crop coords

**Sampling rule:** colors and sizes come from pixel probes or `visual-qa-toolkit` color_extraction / alignment — never from model "memory" of LCARS.

### 4. Cue matrix

Convert IR into a checklist the prove step can fail. Example cues:

- Left spine width / canvas width within ±2%
- Elbow outer radius within ±2px at capture scale
- Inter-segment gutter constant (state measured px)
- Header fill Δe vs sampled ref ≤ 3 (CIE76) under same color space
- Condensed all-caps labels present in named regions
- Schematic silhouette IoU / SSIM threshold against traced asset

**Encode the matrix as a `vqa-cuespec/1` JSON** ([[visual-prove-engine]]) rather than a
markdown-only table: scout the reference with the engine's probes to derive targets,
record the derivation in `_provenance`, and mark anything unmeasurable as an `attest`
cue so it can never inflate the verdict. Pattern:
`07-projects/20-lcars-generative-interface/docs/construction/S-SYS47-01.cuespec.json`.

### 5. Implement from IR only

Map IR nodes → components. If the codebase cannot express an IR node (true constant-thickness elbow arc, nested mini-frame), **stop and extend the grammar** — do not approximate and call it done.

### 6. Prove

1. Capture build at same viewport/DPR as reference study plan
2. Side-by-side native crops (full + 2–3 critical tiles: elbow join, gutter, type)
3. Run `vqa prove BUILD CUESPEC` ([[visual-prove-engine]]) — the measured/attested split
   and margins per cue are the verdict input; `vqa compare` ranks builds; `vqa score --ledger`
   records the trajectory and blocks regressions with `--enforce`
4. Run `visual-qa-toolkit` for single-metric depth where needed: `visual_diff`, `color_extraction`, `alignment`, `spacing`
5. For video northstars: [[reference-video-review]] keyframes vs analogous build moments, plus `vqa motion --frames` for stutter/flicker/settle measurement

Do not proceed to §7 until these exist on disk and are cited.

### 7. Verdict language

- **Matches Literal** — all must-pass cues met; cite evidence paths
- **Partial** — list unmet cues as next-pass scope; do not claim finished
- **Fail** — structural mismatch (wrong frame grammar); restart from transcription

## Adversarial self-check (before claiming progress)

Ask and answer in the baton:

1. Could a stranger overlay ref and build and see the same frame graph?
2. Which cue would Sean fail in under 3 seconds?
3. Did I optimize for test green / density caps / APCA at the cost of northstar authority?
4. Did an image-description paragraph substitute for measurement?

If (3) or (4) is yes → not Literal progress.

## Related
- foundation → [[design-foundations]]
- hub → [[lead-visual-qa]]
- peer ↔ [[visual-prove-engine]]
