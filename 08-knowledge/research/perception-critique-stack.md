---
tags: [research, vision, perception, 3d, game-design, interaction, visual-qa, metrics]
created: 2026-08-28
updated: 2026-08-28
status: working
confidence: medium
sources:
  - "Fu, Sundaram et al., DreamSim (NeurIPS 2023) + perceptual-alignment follow-up (NeurIPS 2024)"
  - "Andersson, Nilsson, Akenine-Möller et al., NVIDIA FLIP (HPG 2020) + HDR-FLIP"
  - "Alakuijala et al., Butteraugli (Google)"
  - "Mantiuk et al., HDR-VDP-2/3"
  - "Zhang et al., LPIPS (CVPR 2018); Ding et al., DISTS"
  - "Wu et al., Q-Align (ICML 2024)"
  - "Cao et al., ArtiMuse (CVPR 2026)"
  - "Wang et al., DUSt3R (CVPR 2024); Leroy et al., MASt3R (ECCV 2024); Wang et al., VGGT (CVPR 2025)"
  - "Xing et al., 3DGS-VBench (2025); MUGSQA (2025); AAAI 2026 3DGS subjective QA"
  - "arXiv:2606.18451, Cross-model VLM-judge protocol for mesh quality (2026)"
  - "arXiv:2506.12563, Benchmarking similarity metrics for novel view synthesis (2025)"
  - "Khronos glTF-Validator; @khronosgroup/gltf-asset-auditor"
  - "VisCritic (arXiv:2606.24525); VeriGUI (arXiv:2604.05477); GUI-Shepherd; GUI-PRA; StainFlow"
  - "CANVAS UI-design benchmark (AAAI 2026); UIGaze (arXiv:2604.26352); UEyes saliency"
  - "Karaev et al., CoTracker; Doersch et al., TAPIR"
  - "Jörg et al., responsiveness in games (2011); ITU-T G.1072 interactivity; Bugnet input-latency practice"
  - "PCG Benchmark (2025); AutoUE (2026); RuleSmith (2026); Godot AutoSim"
  - "Khronos Vulkan CI render-validation tutorial; WellNotWell gpu-agnostic FLIP framework"
related_skills:
  - visual-prove-engine
  - play-prove
  - visual-qa-toolkit
  - render-qa-toolkit
  - native-visual-eval
  - interactive-capture-eval
  - visual-reference-replication
  - vision-foundations
  - game-foundations
  - realtime-visual-craft
  - lead-visual-qa
  - lead-game-designer
  - lead-art-director
related_projects:
  - 20-lcars-generative-interface
  - 13-legion
relations:
  builds-on:
    - "[[measured-visual-verdicts]]"
    - "[[agentic-error-correction-foundations]]"
    - "[[visual-reference-replication-findings]]"
    - "[[visual-failure-mode-ledger]]"
    - "[[a11y-measurement-vs-judgment]]"
  relates-to:
    - "[[10-perception-integrity]]"
    - "[[12-realtime-photoreal-operational-framework]]"
    - "[[06-qa-operating-model]]"
---

# Perception critique stack: what the field can measure that we currently do not

## For future agent

- **TL;DR:** The 2026 field does not have one better metric than SSIM. It has a **ladder of altitudes** (pixel → psychovisual → mid-level learned → no-reference aesthetic → geometric/3D-native → process-reward on interaction → simulation for game feel and balance). Our prove engine is strong at the bottom rung and almost silent above it. That is why LCARS can score 16/16 while a human still sees missing rails, and why Legion still-grids cannot close 3D, motion, or feel.
- **Key claims (as of 2026-08-28, dated unless noted):**
  1. **Literal UI replication stays on the pixel rung.** DreamSim / CLIP / VLMs are the wrong primary judge for 8px gutters. Keep cuespec probes. Add FLIP (and optionally Butteraugli) as the *graphics-native* error map, not as a replacement for Δe/gutter/count.
  2. **Spirit, 3D, and photoreal need different altitudes.** DreamSim beats SSIM/LPIPS for novel-view / layout / pose. NVIDIA FLIP was designed for render-vs-ground-truth and produces a **spatial error map** that SSIM does not. Native 3DGS quality models beat 2D IQA on Gaussian content (3DGS-VBench: DISTS and deep VQA beat CLIP-IQA; GSOQA operates on primitives).
  3. **Cheap 3D proxies lie.** Chamfer distance is asymmetric and invents surfaces (DiffCD). Watertightness + CLIP-on-renders failed a 2026 VLM-judge protocol; **cross-model, order-swapped VLM judging** was the reliable signal (~26% of raw VLM verdicts flipped with presentation order).
  4. **3D from pixels is now a foundation model**, not a SfM pipeline. DUSt3R / MASt3R / VGGT reconstruct cameras + depth + pointmaps in a feed-forward pass. That is a new **consistency probe**: orbit a scene, reconstruct, score geometric agreement. It is not a beauty metric.
  5. **Mesh QA is mostly not visual.** Khronos glTF-Validator + `gltf-asset-auditor` (manifold, UV overlap, texel density, bevels) catch production defects no screenshot will. Visual and structural gates are complementary.
  6. **Operating a UI is not seeing like a user.** UIGaze (2026): VLMs approximate 7-second exploratory attention and **fail 1-second first fixations**; UI-TARS (an operator) has near-zero correlation with human gaze. CANVAS (AAAI 2026) evaluates design at three levels: SSIM, UEyes saliency, BLIP semantics.
  7. **Action-effect verification is now a trained critic**, not only a pixel delta. VisCritic (Siamese ViT on pre/post screenshots) and VeriGUI are process rewards. Our `vqa interact` is the deterministic floor; a learned critic is the Spirit layer on top, never the Literal gate.
  8. **Game feel is latency + jerk, not SSIM.** Input-to-photon (software frame-count in CI; LDAT-class hardware for truth), CoTracker/TAPIR tracks for camera/character smoothness (peak jerk, AUJ), vsync jank. ITU-T G.1072 treats interactivity as its own QoE dimension.
  9. **GPU renders are not byte-stable.** Vulkan CI practice: SwiftShader/LavaPipe for determinism, then FLIP + MAD outlier detection, not MD5 of the framebuffer. Pixel-hash goldens do not survive driver variance.
  10. **Game design quality is simulation, not vision.** PCG Benchmark (quality / diversity / controllability), Godot AutoSim (win-rate, stddev, no-dominant-strategy in CI), RuleSmith (LLM self-play + Bayesian rule search). MCTS outperforms LLMs at strategic play; LLM *confusion* is a rule-clarity detector, not a player.
- **Do not:** replace the prove engine with a VLM; use CLIP-IQA as a 3D done-gate; treat UI-TARS as a hierarchy critic; use Chamfer or SSIM as the only 3D score; let a 16/16 cuespec silence uncued residuals.

## Why this research was gated before

The 2026-08-26 prove-engine work correctly refused VLM-as-measurement for Literal UI. That refusal is still right. It also **stopped the search** at metrics the existing Python stack could run (NumPy SSIM, Δe, connected components). The field past that boundary is not "less rigorous." It is rigorous at different altitudes, with different failure modes, and it is what 3D / interaction / game work actually needs.

This entry maps the field first, then the course corrections. It does not implement them.

## The metric ladder (altitude, not ranking)

Each rung answers a different question. Mixing rungs is the #1 evaluation error (same class of bug as [[vision-foundations]] "mismatch task to output").

| Altitude | Question it can answer | Representative tools | Blind to |
|---|---|---|---|
| A. Pixel / structure | Are these *this* hex, gutter, count, crop? | SSIM, Δe, region count, alignment, our cuespec probes | GPU jitter, mid-level layout, "is this the same ship from another view" |
| B. Psychovisual (HVS) | Would a human *see a difference* at this viewing distance? | NVIDIA FLIP (+ HDR-FLIP), Butteraugli (near-threshold), HDR-VDP (visibility probability) | Semantics, missing modules that occupy similar luminance |
| C. Mid-level learned | Same layout / pose / foreground object? | DreamSim (CLIP+OpenCLIP+DINO, human-tuned), LPIPS, DISTS, shift-tolerant LPIPS | Fine 1–2px craft; DreamSim has a documented **foreground bias** |
| D. No-reference / aesthetic | Is this *good* without a pixel-twin? | Q-Align / OneAlign (text-defined levels), ArtiMuse (attribute scores), CLIP-IQA (weak on 3DGS) | Domain taste unless fine-tuned; general MOS ≠ LCARS grammar |
| E. Geometric / 3D-native | Is the *shape / primitive / asset* valid? | VGGT/DUSt3R/MASt3R reconstruction; GSOQA on Gaussians; Chamfer/F-score *with DiffCD caveats*; glTF auditor | Beauty, lighting, UI chrome |
| F. Process / interaction | Did the *action* cause the intended visual change? | `vqa interact`; VisCritic; VeriGUI; OmniParser + Point | Feel, latency, first-fixation hierarchy |
| G. Simulation / feel / balance | Does it *play*? | Input-to-photon; CoTracker jerk; PCG metrics; AutoSim win-rate; MCTS skill-gap | Pixels at all |

**Rule:** pick the altitude from the **fidelity axis** (Literal / Spirit / Standard / Intent) and the **medium** (UI still, photoreal still, orbit, mesh, interaction, game loop). A Matches verdict is only meaningful *inside the altitudes the contract named*.

## Findings by medium

### Visual design (UI, 2D craft)

CANVAS (AAAI 2026) independently rediscovered a three-level stack: feature (SSIM), pattern (UEyes saliency), object (BLIP captions), plus component-attribute checks. Human pairwise agreement with that mix was reported at ~75%. UIGaze adds the hard limit: **zero-shot VLMs do not model first fixations**. Hierarchy critique therefore needs a **saliency model trained on UI eye-tracking** (UEyes / UMSI / DeepGaze), not an operator VLM and not SSIM.

Course correction: a `saliency_region` probe (histogram intersection of UEyes-class maps vs reference) belongs in cuespec-v2 for Spirit and for "did we keep the visual hierarchy," not for Literal hex/gutter. OCR / OmniParser belongs on attested-text cues that we currently leave as attestations.

### 3D modeling and neural rendering

Two separate problems get smashed together in screenshot QA:

1. **Asset hygiene** (manifold, UVs, texel density, LOD ratios, named nodes). Deterministic. Khronos tools. No GPU.
2. **Appearing right** (silhouette, materials, lighting, novel views, splats). Perceptual and often stochastic.

On (2), 2025–2026 3DGS papers are blunt: PSNR/SSIM/LPIPS correlate poorly with MOS for Gaussian artifacts (thinning, temporal incoherence along camera paths). DISTS and deep no-reference VQA (DOVER, FAST-VQA, Q-Align) do better; models that consume **native Gaussians** do better still. DreamSim is more robust than SSIM/LPIPS for novel-view *utility* (foreground/task-relevant similarity) and less fooled by imperceptible pixel noise, which is exactly GPU/NVS jitter.

VGGT (CVPR 2025) is the practical reconstruct-from-views backbone: one forward pass, cameras + depth + pointmaps, no SfM post-opt. A prove loop for a 3D scene can be: **pin camera path → capture lossless frames → VGGT reconstruct → score pose/depth agreement with the authoring camera**. That catches "the model looks fine from the hero shot and is hollow / scaled wrong / drifting" which no single northstar PNG can.

Differentiable rendering (nvdiffrast, Mitsuba 3, SoftRas) is a **training/optimization** tool, not a QA gate, unless we start inverse-fitting a mesh to a northstar (possible for Literal 3D, expensive, not the first move).

### Interaction design

VisCritic and VeriGUI confirm the workspace intuition behind `vqa interact`: **verify the pixels after the action, do not trust the agent that clicked**. The field then goes further: Siamese visual difference encoders as *process rewards*, entity-stain tracking (StainFlow) across long GUI trajectories, OmniParser for global layout vs Point for local grounding.

Limits to import: these critics are trained on "did the task advance," not "is the motion curve right" or "is the hierarchy preserved." They will green-light an ugly but successful click.

### Game engine visuals

Industry CI that survived GPU variance:

- Pin time, RNG, vsync, and preferably a **software renderer** (SwiftShader / LavaPipe) when the gate is "did we ship a black frame / missing mesh."
- Compare with **FLIP** (viewing-distance aware, error maps) plus a robust statistic (median + MAD), not mean pixel error.
- Optional specialist CNN trained on *this* game's good vs bad frames for catastrophic-fail (black, freeze, NaN bloom).
- HDR content: tone-map (ACES) *before* FLIP or HDR-FLIP; raw HDR luminance fools SDR FLIP (documented supernova false-diff).

MD5-of-framebuffer goldens scale storage but **fail across GPUs**. Do not adopt them as the photoreal gate.

### Game design (systems, not pixels)

Visual QA cannot balance a game. The 2025–2026 stack that can:

- **PCG Benchmark**: every generator reports quality, diversity, controllability in `[0,1]`.
- **Headless simulation** (Godot AutoSim pattern): win-rate bands, stddev caps, `assert_no_dominant_strategy` in CI. Prefer a **math-model adapter** when physics/render would pollute the balance metric.
- **MCTS (or other search) for skill-gap**; LLM agents for **rule ambiguity** (systematic confusion ⇒ the rule text is unclear), not for "is this fun."
- **RuleSmith-style** Bayesian search over tunable parameters with self-play as the evaluator.

Game-foundations already states 60 FPS as floor and input latency as co-equal. That doctrine has no probe in visual-prove-engine today.

## Honesty bounds (what still cannot be automated)

- **Taste and intent.** Q-Align-class models score "excellent/good/bad" against photographic/AIGC MOS, not against a ship's LCARS grammar or Legion's northstar.
- **First-fixation hierarchy** without an eye-tracking-trained saliency model.
- **Strategic play** by an LLM. Use search.
- **Single-model VLM judges.** Position bias is large; require two families and A/B swap, same protocol as `arXiv:2606.18451`.
- **Unexpected residuals outside the cue net.** LCARS v4 16/16 with missing left rail is the exhibit. Coverage < 1.0 plus an explicit "uncued residual" list is part of the verdict, not a footnote.

## Course corrections for this workspace

**Implemented 2026-08-28** in `visual-prove-engine` (`ENGINE_VERSION` `vqa/1.1`) and sibling [[play-prove]]. `vqa calibrate` covers the new detectors. Capture decision vs item 9's first draft: missing `renderer` is a **warning**, not unverified, so existing LCARS manifests stay `verified`.

Prioritized by leverage. None of these weaken the 2026-08-26 measured-verdict contract ([[measured-visual-verdicts]]).

### 1. Name altitudes in the cuespec (framework #06 + prove engine)

Add an optional `altitude: A|B|C|D|E|F|G` (or named: `pixel|hvs|midlevel|nriqa|geometry|process|sim`) per cue. A `matches` rollup must state which altitudes were in contract. Literal packs default to A (+ B for photoreal). Spirit packs require C and a saliency cue. 3D packs require E. Interaction claims require F. Feel/balance claims require G.

This is the smallest change that stops "16/16" from being misread as "done in every sense."

### 2. Add FLIP (and optionally Butteraugli) beside SSIM

`vqa compare` and `ssim_region` should grow a `flip_region` / `flip_map` artifact. FLIP is the graphics community's actual difference evaluator; SSIM remains the cheap, dependency-light floor (calibrate still runs without torch). Capability-registry: `nvidia-flip` optional, degrade to SSIM + Δe with an explicit `degraded` flag on the prove summary (never silent).

Render-qa-toolkit northstar match should prefer FLIP maps over SSIM for photoreal stills (#12 gate A).

### 3. Optional DreamSim probe for Spirit / NVS / "is this the same object"

Not for LCARS Literal gutters. Yes for "does this novel view still look like the northstar ship," ranking candidate builds when pixel registration is hopeless, and 3DGS/NeRF work. Document foreground bias in the probe note.

### 4. Structural 3D probes (new `mesh` cue class)

Wrap `@khronosgroup/gltf-asset-auditor` + glTF-Validator as `vqa mesh ASSET SCHEMA`. Fail closed on Error; Warning is coverage, not pass. This is the 3D analogue of cuespec pixel probes and should land before any VLM mesh judge.

### 5. Geometric consistency probe (VGGT/DUSt3R)

New capture recipe: pinned orbit or two-view pair → reconstruct → score camera/depth disagreement. Lives next to `interactive-capture-eval`, not inside UI cuespecs. Needs torch + weights; capability `geometric-foundation-model` with `block` fallback (do not fake a 3D pass from one still).

### 6. Saliency + OCR as first-class UI Spirit probes

UEyes-class saliency vs reference (CANVAS pattern). OCR for currently attested strings (SYSTEM 47, NCC-1701-E). That converts three LCARS attestations into measured cues without a VLM.

### 7. Learned interaction critic *on top of* `vqa interact`

Keep pixel expected-change as the hard gate (dead control, side effect). Add VisCritic-class "did progress happen" as a process reward for long GUI / in-game tutorial paths. Never let the critic override a pixel fail.

### 8. Motion: tracks, not only luma

`vqa motion` today: duplicate frames, flicker, coarse jerk. Upgrade path: CoTracker/TAPIR on labeled points (camera, reticle, character root) → peak jerk, AUJ, overshoot, settle. Pair with **input-to-photon** (frame index of first pixel change after injected input) as a game-feel cue. Hardware LDAT remains the calibration truth; software is the CI gate.

### 9. GPU capture policy

For WebGL/engine stills: document software-renderer vs hardware tracks. Hardware captures are `unverified` for byte-identity; they may still be `verified` for FLIP-within-MAD. Update capture manifests with `renderer: swiftshader|metal|vulkan|webgl` and `rng_frozen`.

### 10. Game-design simulation lane (separate skill, not a visual probe)

Do not cram win-rates into `vqa.py`. A sibling `play-prove` (or spoke under `lead-game-designer`) that consumes a headless adapter and emits quality/diversity/controllability + balance assertions. Visual prove stays pixels; play prove stays numbers from simulation.

### 11. Cross-model VLM-judge protocol (Spirit/Intent only)

When we *do* want a language judge (mesh beauty, aesthetic, "does this screen feel LCARS"): two model families, swap order, discard inconsistent pairs, never a single score. This **refines** [[visual-reference-replication-findings]] ("refuse VLM-as-spec") rather than reversing it: VLM is a *judge of Spirit*, never the Literal spec and never a unmeasured done-claim.

### 12. Uncued-residual as a first-class ledger field

After every prove, the agent (or a VLM *suggestion* list, not a gate) must list zones the cuespec does not cover. LCARS v4 left rail / navy sweep / timestamp are the template. `coverage` already exists; **name the holes**.

## What we should not do

- Train or fine-tune a general "beauty CNN" on our own screenshots as the Literal gate (overfits, uncalibrated, replaces measurement).
- Adopt CLIP-IQA as a 3DGS done-metric (3DGS-VBench correlation is poor).
- Replace Construction IR with VGGT (reconstruction is a *check*, not an authoring source).
- Let UI-TARS / operator agents critique visual hierarchy.
- MD5 golden frames for Legion or any GPU path.
- One giant multimodal model that "does all of QA." The ladder exists because no model owns every altitude.

## Suggested first implementation slice

If a later session implements rather than researches:

1. Cuespec `altitude` field + prove.md prints altitude coverage.
2. Optional FLIP in `vqa compare` with capability degrade.
3. `vqa mesh` wrapping glTF-Validator (no torch).
4. Saliency + OCR probes for UI Spirit.
5. Capture manifest `renderer` + software-renderer recipe for WebGL.

Items 1 and 3 need no new ML weights and extend the reliability contract we already proved on LCARS.

## Pointers (do not bulk-load)

- Engine contract: [[visual-prove-engine]] / [[measured-visual-verdicts]]
- Literal UI failure modes: [[visual-reference-replication-findings]]
- Photoreal gates: [[12-realtime-photoreal-operational-framework]] / [[render-qa-toolkit]]
- Independent detection: [[agentic-error-correction-foundations]]
- Vision task taxonomy: [[vision-foundations]]
- Feel vs FPS: [[game-foundations]]
