---
name: vis-classical-opencv
description: >
  Classical (non-learned) computer vision and the OpenCV/NumPy toolchain — the deterministic
  backbone under every deep pipeline. Filtering, edges, contours, morphology, color spaces;
  feature detection + matching (SIFT/ORB/AKAZE); geometric vision — camera calibration, undistortion,
  homography, epipolar geometry, stereo, optical flow, pose (PnP). Reach here when the answer is
  geometry or signal processing, not a neural net. Triggers: opencv, image processing, filtering,
  edges, contours, feature matching, SIFT, ORB, homography, calibration, optical flow, stereo, PnP.
aliases: [vis-classical-opencv, opencv, classical-cv]
triggers: [opencv, image processing, gaussian blur, canny, contours, morphology, color space, feature matching, sift, orb, akaze, homography, camera calibration, undistortion, epipolar, stereo, optical flow, pnp, pose estimation]
tier: spoke
hub: vision-foundations
domain: vision
prerequisites: [sci-linear-algebra]
surfaces: ["*"]
spec_version: "2.0"
---

# Vision — Classical CV & OpenCV

The deterministic half of computer vision. Deep nets get the headlines, but **geometry, signal
processing, and calibration are exact, cheap, and explainable** — and most production pipelines are a
classical front-end feeding a learned back-end. When the task is "where is the camera," "rectify this,"
or "track these corners," you want math, not a model. The geometry here is [[sci-linear-algebra]] applied
to pixels; the lens model is [[imaging-foundations]]'s ([[img-optics-light]]).

## Image as signal — the operations that don't learn
- **Filtering:** Gaussian (denoise/scale-space), median (salt-pepper), bilateral (edge-preserving),
  Sobel/Laplacian (gradients). Convolution kernels — the same operation a CNN learns, here hand-designed.
- **Thresholding & morphology:** Otsu/adaptive threshold → binary; erode/dilate/open/close to clean masks.
  Still the fastest path to "count the blobs."
- **Edges & contours:** Canny (hysteresis), `findContours`, Hough lines/circles for parametric shapes.
- **Color spaces:** work in **HSV/Lab** for illumination-robust color segmentation, not RGB. Convert
  intentionally and mind linear-vs-sRGB ([[imaging-foundations]]).

## Features — describe a point so you can find it again
- **Detect + describe:** SIFT (robust, patented-now-free), ORB (fast, binary, real-time), AKAZE.
  Keypoints + descriptors are invariant to scale/rotation by construction.
- **Match:** brute-force (Hamming for binary) or FLANN; filter with **Lowe's ratio test** + **RANSAC** to
  reject outliers. Features power panorama stitching, SLAM front-ends, and template/instance finding.

## Geometric vision — recover the 3D that the camera flattened
This is the part deep learning still doesn't replace cleanly:
- **Camera model + calibration:** intrinsics (focal, principal point), **distortion** coefficients; calibrate
  from a checkerboard; `undistort` before any metric work. The pinhole + projection math is [[sci-linear-algebra]].
- **Homography** (planar, 4 DoF up to scale): rectify documents, stitch images, map a plane — `findHomography` + RANSAC.
- **Epipolar geometry / stereo:** fundamental/essential matrix, rectification, disparity → **depth**. Triangulation
  recovers 3D points from two views.
- **Pose (PnP):** given 3D↔2D correspondences, `solvePnP` recovers camera pose — the backbone of AR and robotics.
- **Optical flow:** Lucas-Kanade (sparse, track corners) / Farnebäck (dense) — motion without identity, the
  cheap precursor to learned tracking ([[vis-detection-tracking]]).

## When classical beats deep
Choose classical when you need **exactness, zero training data, full explainability, or microsecond latency**:
fiducial/QR/ArUco detection, calibration, rectification, frame differencing, simple counting under controlled
lighting. Hand the *semantic* questions ("is this a defect / a person / a tumor") to the learned spokes.

## Related
- foundation → [[sci-linear-algebra]]
- hub → [[vision-foundations]]
- peer ↔ [[vis-detection-tracking]] · [[visual-qa-toolkit]] · [[img-photoreal-rendering]]
