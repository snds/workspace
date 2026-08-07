---
name: vision-foundations
description: >
  The first principles of machine perception — how a computer turns pixels into meaning.
  Image formation and representation, the CV task taxonomy (classify / detect / segment /
  track / reconstruct / describe), the classical→deep transition, convolution + attention as
  spatial inductive bias, and how vision systems are trained, evaluated, and deployed. Load
  BEFORE any object-detection, segmentation, tracking, OCR, or vision-language work — distinct
  from imaging-foundations, which is about *making* images, not *understanding* them. Triggers:
  computer vision, machine vision, image classification, object detection, image segmentation,
  feature extraction, convolution, vision model, embedding, mAP, IoU, dataset, annotation.
aliases: [vision-foundations, cv-foundations]
triggers: [computer vision, machine vision, image classification, object detection, image segmentation, feature extraction, convolution, vision model, image embedding, map metric, iou, dataset, annotation, perception pipeline, deep learning vision]
tier: foundation
domain: vision
surfaces: ["*"]
spec_version: "2.0"
---

# Vision Foundations

How a machine turns a grid of numbers into *meaning*. This is the substrate beneath every
detector, segmenter, tracker, and vision-language model. It is the mirror image of
[[imaging-foundations]]: that foundation forms an image *from* light; this one recovers
*structure and semantics from* the image. The math is [[science-foundations]] (linear algebra,
probability, optimization); the training/evaluation discipline is [[data-foundations]]. This
foundation owns the **context-free principles**; concrete methods live in the spokes.

## An image is a sampled signal, not a picture
Before any model, understand what you actually have:
- A pixel grid is a **discretized, quantized projection** of a 3D scene through a lens
  ([[imaging-foundations]]'s camera model). Resolution, bit depth, color space (linear vs. sRGB),
  and **JPEG/codec artifacts** are all signal properties that change what a model can recover.
- **Geometry vs. appearance.** Some tasks need geometry (calibration, homography, depth — [[vis-classical-opencv]]);
  most deep tasks learn appearance statistics. Know which you're solving.
- **Invariances you want** (translation, scale, rotation, illumination, viewpoint) determine the
  architecture and the augmentations — they don't come for free.

## The task taxonomy (name the task before reaching for a model)
Every CV problem is one (or a composition) of these, and the *output shape* defines it:
- **Classify** — one label per image. **Detect** — boxes + labels ([[vis-detection-tracking]]).
  **Segment** — per-pixel labels: semantic / instance / panoptic ([[vis-segmentation]]).
- **Track** — identity across time ([[vis-detection-tracking]], [[vis-video-pipelines]]).
- **Reconstruct** — depth, pose, 3D, optical flow ([[vis-classical-opencv]]).
- **Describe / reason** — caption, VQA, open-vocabulary, grounding ([[vis-vlm-multimodal]]).
- Mismatching task to output is the #1 design error: "find the license plate" is OCR-after-detection,
  not classification.

## Why convolution, and why attention now
- **Convolution** bakes in the right priors for pixels — locality + translation equivariance +
  weight sharing — so CNNs learn from far less data than dense nets. This is the inductive bias that
  made deep vision work ([[science-foundations]] for the linear-algebra view: convolution = structured matmul).
- **Vision Transformers / attention** trade that bias for scale: global receptive field from layer one,
  better with huge data + pretraining. Modern systems are **hybrid** (conv stems, attention necks) or
  transformer backbones. **Self-supervised + foundation models** (CLIP, SAM, DINO) now mean you rarely
  train from scratch — you *adapt* ([[vis-vlm-multimodal]], [[vis-segmentation]]).

## Training, transfer, and data are the real work
The model is the easy part; the **data pipeline** decides the outcome ([[data-foundations]]):
- **Transfer learning is the default** — start from pretrained weights, fine-tune the head, then unfreeze.
  Training from scratch is rare and expensive.
- **Augmentation** encodes invariances (flips, crops, color jitter, mosaic, copy-paste) — it's how you
  buy robustness without more labels.
- **Labels dominate cost and quality.** Annotation protocol, class balance, label noise, and
  train/val/test **leakage** (near-duplicate frames across splits) make or break the result.
- **Domain shift** (your camera ≠ the training set) is the silent killer — validate on *your* distribution.

## Evaluation: pick the metric the task is graded on
- **Detection:** mAP at IoU thresholds (COCO mAP@[.5:.95]); watch precision/recall *per class*, not just the mean.
- **Segmentation:** mIoU / Dice. **Classification:** top-1/top-5, but use **PR-AUC** under class imbalance.
- **Tracking:** MOTA / IDF1 (identity matters, not just per-frame boxes).
- Always inspect **failure cases visually** — aggregate metrics hide systematic blind spots (small objects,
  rare classes, one lighting condition). A confusion matrix + a wall of false positives beats a single number.

## Deployment is a first-class constraint
A model that doesn't hit the latency/cost budget doesn't exist ([[vis-video-pipelines]]):
- **Quantization** (INT8), **pruning**, **distillation**, and export (ONNX / TensorRT / CoreML) trade
  accuracy for speed. Measure the accuracy you actually lose, on your data.
- **Edge vs. server** changes everything (batch size, model size, power). Real-time = a frame budget,
  not "fast."
- **Monitor for drift** in production — input distribution moves; accuracy decays silently.

## Ethics & failure modes are not optional
Vision systems fail in socially loaded ways: dataset bias (skin tone, geography), surveillance misuse,
and **over-trusted outputs** (a confident wrong box). Face recognition, demographic inference, and
tracking carry real harm — gate them on consent and necessity, and report confidence honestly.

## Seeing the work — vision as a visual-QA / render-assessment instrument
The highest-value use of this domain here isn't a shipped CV product — it's letting the agent **actually
see, articulate, and critique the visual work we make together**, then troubleshoot it. Vision is the
machine-seeing half of the review loop; the heuristic/human half is [[lead-visual-qa]] + the
[[visual-qa-toolkit]] (still-image craft lens: [last-mile craft](01-frameworks/05-last-mile-craft-framework.md)).
Reach for these techniques to turn "it looks off" into a specific, checkable observation:

- **Look at it and say what's wrong** — feed a screenshot/render to a VLM ([[vis-vlm-multimodal]]) for a
  grounded critique (layout, hierarchy, contrast, artifacts), pairing with [[visual-qa-ui-design]] /
  [[visual-qa-game-design]]. The fastest path from pixels to articulate feedback.
- **Did it change / does it match the reference?** — pixel diff, **SSIM**, histogram/edge comparison
  ([[vis-classical-opencv]]) for visual-regression and reference-matching ([[visual-qa-toolkit]],
  [[img-photoreal-rendering]]).
- **Is every element present and placed right?** — detect/segment UI components or scene objects
  ([[vis-detection-tracking]], [[vis-segmentation]]) to verify composition and catch missing/misaligned parts.
- **Assess motion + render quality in Legion** — extract frames ([[reference-video-review]]), then
  critique the fly-through, lighting, and composition against intent ([[lead-game-developer]],
  [[img-cinematography]], [[game-scale-traversal]]). The CV read complements the
  [[threejs-galaxy-visualization]] gotchas and the [[legion-galaxy-playbook]] recipe.

Principle: **measure or describe what you see, don't assert it.** A VLM critique, an SSIM number, or a
segmented overlay is evidence; "looks good" is not.

## Execution protocol

Vision work is analysis work, so it runs the analysis pipeline from
[#15 Analysis Operating Model](../../01-frameworks/15-analysis-operating-model.md): question →
method → validity → decision. The vision-specific ordering:

1. **Name the task and the output shape** (classify / detect / segment / track / reconstruct /
   describe). If the output shape is unclear, the task is not yet defined and no model choice is
   meaningful.
2. **Write the dataset contract** before touching a model: source and licence, capture conditions,
   class definitions with edge cases, annotation protocol, expected class balance, and what a
   "hard" example looks like. Ambiguous class definitions produce label noise that no architecture
   recovers from.
3. **Split before you look.** Define train / validation / test by *group* (scene, subject, camera,
   session), not by frame, and check for near-duplicate leakage. Freeze the test set; it is the
   thing you are allowed to be surprised by exactly once.
4. **Pick the metric the task is graded on** (mAP at the relevant IoU, mIoU or Dice, PR-AUC under
   imbalance, MOTA/IDF1 for identity) and the operating point (which precision/recall trade the
   consumer of this system actually needs).
5. **Baseline first**: pretrained weights, minimal fine-tune, no augmentation tricks. This is the
   number every later change is judged against, and it is often good enough.
6. **Iterate on data before architecture.** Augmentation encodes the invariances you claimed in
   step 2; relabelling the confused classes usually beats swapping backbones.
7. **Read the failures, not just the aggregate.** Confusion matrix, per-class precision/recall, and
   a wall of false positives and false negatives at native resolution
   ([#10 Perception Integrity](../../01-frameworks/10-perception-integrity.md)).
8. **Measure deployment cost on the target** (latency, memory, power) and the accuracy actually
   lost to quantization or export, on your data.

## Done-gates

Do not report a vision result as working until all of these hold. Any that cannot hold gets stated
as an unmet gate, not rounded up.

- **Dataset contract exists and is honoured.** Class definitions, annotation protocol, and split
  policy are written down; the split is group-aware and leakage-checked.
- **The test set was used once, at the end.** A number produced by repeatedly tuning against the
  test set is a training metric wearing the test set's name.
- **Metric matches the task and the operating point is named.** A single mean with no per-class
  breakdown is not an evaluation.
- **Failure modes enumerated with examples.** Small objects, rare classes, one lighting condition,
  motion blur, occlusion, domain shift: each either measured or explicitly out of scope. This is
  [#11 Anticipatory Failure Analysis](../../01-frameworks/11-anticipatory-failure-analysis.md)
  applied to a model instead of a shader.
- **Validated on the deployment distribution**, not only the benchmark. If that data does not
  exist yet, say so; it is the top risk, not a footnote.
- **Confidence reported honestly.** A confident wrong box is the characteristic harm of this
  domain. Calibration and the abstain path are part of the result.
- **When vision is used as a QA instrument** (the section above), the measurement path is named and
  the pixels are native. A VLM's prose critique is `critique`; SSIM, a pixel diff, or a detection
  overlay is `audit`. Per [#13 Domain Rigor Stack](../../01-frameworks/13-domain-rigor-stack.md),
  do not label judgment as measurement.

## Related
- spoke → [[vis-classical-opencv]] · [[vis-detection-tracking]] · [[vis-segmentation]] · [[vis-video-pipelines]] · [[vis-vlm-multimodal]]
- peer ↔ [[imaging-foundations]] · [[science-foundations]] · [[data-foundations]] · [[found-perception]] · [[lead-visual-qa]] · [[lead-game-developer]]
