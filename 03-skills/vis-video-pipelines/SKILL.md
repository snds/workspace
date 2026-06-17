---
name: vis-video-pipelines
description: >
  Production computer-vision pipelines on video and at scale — the engineering around the model.
  Video I/O and decoding, frame sampling, batching, temporal coherence; real-time vs. throughput
  budgets; tiling for high-res/aerial; GPU/edge deployment and export; annotation + dataset ops;
  and monitoring for drift. Reach here for "run CV on a stream / a million frames / a drone / a
  camera in the field." Triggers: video pipeline, real-time inference, frame sampling, batching,
  ffmpeg decode, tiling, SAHI, edge deployment, TensorRT, ONNX, drift monitoring, MLOps vision.
aliases: [vis-video-pipelines, cv-pipelines, video-cv]
triggers: [video pipeline, real-time inference, frame sampling, batching, video decode, ffmpeg, decord, tiling, sahi, aerial, drone footage, edge deployment, tensorrt, onnx, coreml, quantization, drift monitoring, dataset ops, annotation pipeline, mlops vision]
tier: spoke
hub: vision-foundations
domain: vision
prerequisites: [data-foundations]
surfaces: ["*"]
spec_version: "2.0"
---

# Vision — Video & Production Pipelines

The model is ~10% of a working CV system; this spoke is the other 90% — getting frames in, predictions out,
fast enough, on real hardware, and *staying* accurate. It turns [[vis-detection-tracking]] /
[[vis-segmentation]] / [[vis-vlm-multimodal]] from a notebook demo into a service. The dataset + monitoring
discipline is [[data-foundations]].

## Get the frames in (this is where time goes)
- **Decode is a bottleneck.** Use hardware-accelerated decode (NVDEC), `decord`/PyAV, or batched `ffmpeg` — naïve
  `cv2.VideoCapture` per frame stalls the GPU.
- **Sample, don't process every frame.** Most tasks tolerate 1-in-N sampling or keyframe selection; detect on a
  stride and **interpolate with a tracker** ([[vis-detection-tracking]]) between detections. Caption only sampled
  frames for VLMs.
- **Temporal coherence** is free signal: smooth predictions across frames, suppress one-frame flickers, and let
  tracking carry identity through missed detections.

## Hit the budget — real-time vs. throughput
Two different problems:
- **Real-time / streaming:** a hard **per-frame latency** budget (e.g., 33 ms @ 30 fps). Small models, INT8,
  TensorRT, minimal batch, pipeline the stages (decode ∥ infer ∥ post-process).
- **Throughput / batch:** millions of offline frames — maximize GPU utilization with large batches, sharding,
  and parallel workers; latency per frame doesn't matter, cost per frame does.
- **High-resolution & aerial/drone:** objects are tiny in a 4K frame — **tile the image (SAHI)**, infer per tile,
  merge boxes. The single most effective fix for small-object recall.

## Deploy where it has to run
- **Export + optimize:** ONNX → TensorRT (NVIDIA), CoreML (Apple), TFLite (mobile/edge). **Quantize** (INT8) and
  measure the accuracy you actually lose — on your data, not the benchmark.
- **Edge vs. server** dictates model size, power, and whether you can update weights remotely. Design for the
  constraint up front; retrofitting a server model onto a Jetson rarely works.

## Data & annotation ops
- **Annotation is a pipeline, not a one-off:** clear protocol, QA pass, class balance, and **SAM-assisted masking**
  ([[vis-segmentation]]) to cut labeling cost. Guard against train/val **leakage** from near-duplicate adjacent frames.
- **Active learning:** mine the production stream for hard/uncertain frames, label those, retrain — the cheapest path
  to accuracy ([[data-foundations]]).

## Monitor — accuracy decays silently
Production input drifts (new camera, season, lighting). Track **input-distribution drift** and proxy quality
(detection-count anomalies, confidence histograms), sample frames for periodic human audit, and alert before the
model is quietly wrong. A CV system without monitoring is a CV system you no longer know the accuracy of.

## Related
- foundation → [[data-foundations]]
- hub → [[vision-foundations]]
- peer ↔ [[vis-detection-tracking]] · [[reference-video-review]]
