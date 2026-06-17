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

## Related
- spoke → [[vis-classical-opencv]] · [[vis-detection-tracking]] · [[vis-segmentation]] · [[vis-video-pipelines]] · [[vis-vlm-multimodal]]
- peer ↔ [[imaging-foundations]] · [[science-foundations]] · [[data-foundations]]
