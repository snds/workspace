---
name: vis-detection-tracking
description: >
  Object detection and multi-object tracking — finding what's in a frame and following it across
  frames. Detector families (YOLO, RT-DETR/DETR, two-stage), anchors vs. anchor-free, NMS, the
  mAP/IoU evaluation reality; then tracking-by-detection (SORT, DeepSORT, ByteTrack), Kalman +
  Hungarian association, re-ID, and the real-time/edge budget. Reach here for "detect/count/follow
  objects in images or video." Triggers: object detection, YOLO, RT-DETR, bounding box, NMS, mAP,
  IoU, anchor, tracking, multi-object tracking, ByteTrack, SORT, Kalman, re-identification.
aliases: [vis-detection-tracking, object-detection, mot]
triggers: [object detection, yolo, rt-detr, detr, bounding box, anchor free, nms, non max suppression, map, iou, multi object tracking, tracking, bytetrack, sort, deepsort, kalman filter, hungarian, re-identification, counting]
tier: spoke
hub: vision-foundations
domain: vision
prerequisites: [sci-probability-stochastic]
surfaces: ["*"]
spec_version: "2.0"
---

# Vision — Detection & Tracking

"What objects are here, and where" — then "which one is which, over time." Detection is the workhorse of
applied CV; tracking is detection plus *identity*. The localization quality is graded by IoU, and the
association math is probabilistic ([[sci-probability-stochastic]]) — Kalman prediction + assignment.

## Detector families — pick by the speed/accuracy/data trade
- **One-stage (YOLO family, v8→v26; RT-DETR):** predict boxes + classes in a single pass. **Real-time**,
  the default for video and edge. Anchor-free designs dominate modern versions.
- **Transformer detectors (DETR / RT-DETR):** set-prediction, **no NMS** needed (bipartite matching at train
  time), cleaner on crowded scenes; RT-DETR brings it to real-time.
- **Two-stage (Faster R-CNN):** region proposals → classify. Higher accuracy on small/dense objects, slower —
  use when precision > latency (medical, inspection).
- **Open-vocabulary (GroundingDINO, YOLO-World):** detect classes named in *text* at inference — no retraining
  for new categories ([[vis-vlm-multimodal]]).

## The mechanics that bite
- **NMS:** post-process to remove duplicate boxes by IoU; the threshold trades duplicates vs. merged neighbors.
  **Soft-NMS** for crowded scenes. (Transformer detectors skip it.)
- **Anchors vs. anchor-free:** anchors need tuning to your object aspect ratios/scales; anchor-free removes that
  knob. Match the choice to your data.
- **Small objects** are the perennial failure — use higher input resolution, tiling/SAHI for aerial/drone
  ([[vis-video-pipelines]]), and feature-pyramid necks.
- **Evaluate honestly:** COCO **mAP@[.5:.95]** is the standard, but inspect **per-class precision/recall** and a
  false-positive wall — the mean hides the class that matters. Calibrate the confidence threshold to *your*
  precision/recall operating point, not the default 0.25.

## Tracking-by-detection — add identity
The dominant paradigm: detect every frame, then link detections into tracks.
- **Motion model:** a **Kalman filter** predicts each track's next box (constant-velocity) — [[sci-probability-stochastic]].
- **Association:** **IoU / Mahalanobis** cost → **Hungarian** assignment between predictions and detections.
- **The ladder:** **SORT** (Kalman + Hungarian, fast, ID-switchy) → **DeepSORT** (adds appearance **re-ID**
  embeddings to survive occlusion) → **ByteTrack** (associates *low-confidence* boxes too — strong + simple,
  the modern default).
- **What breaks it:** occlusion and crossing paths cause **ID switches**; long gaps need re-ID; camera motion
  needs compensation. Grade with **MOTA / IDF1**, not per-frame mAP — identity is the whole point.

## Deployment notes
Real-time = a **per-frame budget**. Quantize (INT8), export to TensorRT/ONNX/CoreML, batch where latency allows,
and right-size the model (nano/small for edge). The tracker is cheap; the detector is the cost — see
[[vis-video-pipelines]] for the streaming/throughput side.

## Related
- foundation → [[sci-probability-stochastic]]
- hub → [[vision-foundations]]
- peer ↔ [[vis-classical-opencv]] · [[vis-segmentation]] · [[vis-video-pipelines]] · [[visual-qa-game-design]]
