---
name: vis-segmentation
description: >
  Per-pixel understanding — semantic, instance, and panoptic segmentation, plus the promptable
  foundation-model era (SAM / SAM 2 / SAM 3). Architectures (U-Net, Mask R-CNN, Mask2Former),
  masks vs. boxes, zero-shot + promptable masking, video object segmentation, and the mIoU/Dice
  evaluation reality. Reach here when a bounding box isn't enough and you need the exact shape —
  medical, satellite, manufacturing, matting, editing. Triggers: segmentation, semantic, instance,
  panoptic, mask, SAM, Segment Anything, U-Net, Mask R-CNN, mIoU, Dice, matting.
aliases: [vis-segmentation, segmentation, sam]
triggers: [segmentation, semantic segmentation, instance segmentation, panoptic, mask, segment anything, sam, sam2, sam3, u-net, mask r-cnn, mask2former, miou, dice coefficient, matting, video object segmentation]
tier: spoke
hub: vision-foundations
domain: vision
surfaces: ["*"]
spec_version: "2.0"
---

# Vision — Segmentation

When a box is too coarse and you need the **exact pixels**. Segmentation answers "which pixels belong to
what," and since SAM it has become largely **promptable and zero-shot** — a foundation-model capability you
adapt, not a network you train from scratch ([[vision-foundations]]).

## Three problems wearing one name
- **Semantic:** label every pixel by *class* (road, sky, tumor). No object identity — all "car" pixels are one mask.
- **Instance:** separate *objects* of the same class (car #1 vs. car #2) — boxes + per-object masks.
- **Panoptic:** the union — every pixel gets a class *and*, for "things," an instance id. The complete scene parse.
- Pick by the question: "how much road" (semantic) vs. "how many cars and their shapes" (instance).

## Architectures — the lineage
- **U-Net:** encoder-decoder with skip connections; still the backbone of **medical + satellite** segmentation
  (works with few labels). The reference design for dense prediction.
- **Mask R-CNN:** Faster R-CNN ([[vis-detection-tracking]]) + a mask head — detect-then-segment, the instance workhorse.
- **Transformer-era (Mask2Former, OneFormer):** unify semantic/instance/panoptic with masked attention — one model, all three tasks.

## The SAM shift — promptable, zero-shot masking
**Segment Anything (SAM / SAM 2 / SAM 3)** changed the default: prompt with a point, box, or text and get a
high-quality mask on objects it was never trained on.
- **Use it as a labeling accelerator** (interactive masks → training data), an interactive editing/selection
  backend, or a zero-shot mask source feeding a downstream classifier.
- **SAM 2** extends to **video object segmentation** — propagate a mask across frames with memory ([[vis-video-pipelines]]).
- Combine with open-vocab detection or a VLM ([[vis-vlm-multimodal]]) for **text → mask** ("segment every pallet").

## Evaluate per-pixel, look at boundaries
- **mIoU** (semantic), **mask AP** (instance), **PQ** (panoptic), **Dice** (medical — sensitive to small structures).
- Aggregate scores hide **boundary error** and **thin/small structures** — overlay predicted masks on the image
  and inspect edges. A 0.9 mIoU model can still leak across the one boundary your application depends on.

## Practical notes
Masks are expensive to label — lean on SAM-assisted annotation. Resolution matters more than for detection
(boundaries live in high-frequency detail). For real-time (robotics, AR), use lightweight semantic models;
reserve heavy promptable models for offline or interactive use.

## Related
- hub → [[vision-foundations]]
- peer ↔ [[vis-detection-tracking]] · [[vis-vlm-multimodal]]
