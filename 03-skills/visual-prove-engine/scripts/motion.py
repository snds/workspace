"""
motion.py — frame-sequence analysis: stutter, flicker, smoothness, easing.

Inputs are an ordered directory of frames (PNG) or a video (extracted via
ffmpeg with -vsync 0 so encoded frames map 1:1 to files). Metrics:

  duplicates      — consecutive identical frames (stutter runs, effective fps)
  flicker         — alternating global luma deltas (ledger A-02 family)
  activity        — per-pair changed-pixel fraction over time
  trajectory      — centroid track of the dominant moving region:
                    velocity / jerk RMS, monotonicity, overshoot, settle frame
  timing (opt)    — vsync jank model when a frame-timestamp manifest exists:
                    ceil(latency/vsync) changes = jank events

The jank model follows the standard vsync-boundary definition (a frame is
janky when its latency crosses a different multiple of the refresh interval
than its neighbors). Frame-content metrics are display-independent; timing
metrics require real timestamps and are skipped (reported as skipped) when
no manifest is provided — absence of timing data is never silent.
"""
from __future__ import annotations

import json
import math
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

import numpy as np

from . import _core
from ._core import change_mask, load_image, luma, write_json


def load_frames(frames_dir: Optional[str] = None, video: Optional[str] = None,
                max_frames: int = 600, downscale_to: int = 640) -> tuple:
    """
    Returns (list of RGB arrays (downscaled for analysis), source description).
    Downscaling is for tractability of per-pair stats; duplicate detection
    hashes the ORIGINAL bytes so a dropped/duplicated encoded frame is exact.
    """
    if video:
        tmp = Path(tempfile.mkdtemp(prefix="vqa_frames_"))
        cmd = [
            "ffmpeg", "-loglevel", "error", "-i", str(video),
            "-vsync", "0", str(tmp / "f_%05d.png"),
        ]
        subprocess.run(cmd, check=True)
        paths = sorted(tmp.glob("f_*.png"))
        source = f"video:{video}"
    else:
        d = Path(frames_dir)
        paths = sorted(p for p in d.iterdir() if p.suffix.lower() == ".png")
        source = f"frames:{frames_dir}"
    paths = paths[:max_frames]
    if len(paths) < 2:
        raise ValueError(f"need >=2 frames, found {len(paths)} ({source})")

    frames = []
    hashes = []
    for p in paths:
        img = load_image(p)
        hashes.append(hash(img.rgb.tobytes()))
        rgb = img.rgb
        if max(rgb.shape[:2]) > downscale_to:
            scale = downscale_to / max(rgb.shape[:2])
            rgb = _core.resize_rgb(rgb, int(rgb.shape[1] * scale), int(rgb.shape[0] * scale))
        frames.append(rgb)
    return frames, hashes, [str(p) for p in paths], source


def analyze_motion(
    frames_dir: Optional[str] = None,
    video: Optional[str] = None,
    spec: Optional[dict] = None,
    out_dir: Optional[str] = None,
    timestamps: Optional[str] = None,
) -> dict:
    spec = spec or {}
    frames, hashes, paths, source = load_frames(frames_dir, video)
    n = len(frames)

    # Duplicates / stutter (on exact original bytes)
    dupes = [i for i in range(1, n) if hashes[i] == hashes[i - 1]]
    stutter_runs = _runs_from_indices(dupes)
    max_stutter = max((r for r in stutter_runs), default=0)
    duplicate_ratio = len(dupes) / (n - 1)

    # Global activity + flicker
    lumas = [luma(f).mean() for f in frames]
    ldelta = np.diff(np.asarray(lumas))
    eps = float(spec.get("flicker_eps", 0.5))
    signs = np.sign(ldelta) * (np.abs(ldelta) > eps)
    alternations = 0
    considered = 0
    for i in range(1, len(signs)):
        if signs[i] != 0 and signs[i - 1] != 0:
            considered += 1
            if signs[i] == -signs[i - 1]:
                alternations += 1
    flicker_index = alternations / considered if considered else 0.0

    activity = []
    centroids = []
    areas = []
    for i in range(1, n):
        mask = change_mask(frames[i - 1], frames[i], threshold_de=float(spec.get("change_de", 4.0)))
        frac = float(mask.mean())
        activity.append(frac)
        area = int(mask.sum())
        areas.append(area)
        if area:
            ys, xs = np.nonzero(mask)
            centroids.append((float(xs.mean()), float(ys.mean())))
        else:
            centroids.append(None)

    traj = _trajectory_metrics(
        centroids, areas, frames[0].shape,
        floor_frac=float(spec.get("track_area_floor_frac", 0.10)),
    )

    payload = {
        "engine": _core.ENGINE_VERSION,
        "source": source,
        "frames": n,
        "analysis_size": [frames[0].shape[1], frames[0].shape[0]],
        "duplicates": {
            "count": len(dupes),
            "ratio": round(duplicate_ratio, 4),
            "max_stutter_run": int(max_stutter),
        },
        "flicker": {
            "index": round(float(flicker_index), 4),
            "mean_abs_luma_delta": round(float(np.abs(ldelta).mean()), 3),
        },
        "activity": {
            "mean_changed_fraction": round(float(np.mean(activity)), 4),
            "max_changed_fraction": round(float(np.max(activity)), 4),
            "still_pairs": int(sum(1 for a in activity if a < 1e-5)),
        },
        "trajectory": traj,
        "timing": _timing_metrics(timestamps, spec) if timestamps else
                  {"status": "skipped", "reason": "no frame-timestamp manifest provided"},
    }

    payload["verdicts"] = _motion_verdicts(payload, spec)
    if spec.get("photon"):
        payload["photon"] = _input_to_photon(frames, spec["photon"])
        payload["verdicts"].extend(_photon_verdicts(payload["photon"], spec["photon"]))
    if spec.get("track_points"):
        payload["tracks"] = _labeled_tracks(frames, spec["track_points"], spec)
        payload["verdicts"].extend(_track_verdicts(payload["tracks"], spec))
    if out_dir:
        write_json(payload, Path(out_dir) / "motion.json")
    return payload


def _runs_from_indices(idx: list) -> list:
    runs, cur = [], 0
    prev = None
    for i in idx:
        if prev is not None and i == prev + 1:
            cur += 1
        else:
            if cur:
                runs.append(cur)
            cur = 1
        prev = i
    if cur:
        runs.append(cur)
    return runs


def _trajectory_metrics(centroids: list, areas: list, shape, floor_frac: float = 0.10) -> dict:
    # A centroid is only meaningful while the change mask is comparable to the
    # moving object's cross-section; at an animation's settle tail the mask
    # decays into slivers whose centroid jitters, which would read as phantom
    # jerk. Gate on area relative to the peak change region (default 10%).
    max_area = max(areas) if areas else 0
    floor = max(32, int(floor_frac * max_area))
    pts = [
        (i, c)
        for i, (c, a) in enumerate(zip(centroids, areas))
        if c is not None and a >= floor
    ]
    if len(pts) < 4:
        return {"status": "insufficient motion", "tracked_pairs": len(pts)}
    diag = math.hypot(shape[1], shape[0])
    idx = np.asarray([i for i, _ in pts], dtype=np.float64)
    xs = np.asarray([c[0] for _, c in pts])
    ys = np.asarray([c[1] for _, c in pts])
    gaps = np.diff(idx)  # velocity per pair-index so track splits don't fake speed
    vel = np.stack([np.diff(xs) / gaps, np.diff(ys) / gaps], axis=-1)
    speed = np.linalg.norm(vel, axis=-1) / diag
    accel = np.diff(speed)
    jerk = np.diff(accel)
    # Principal axis progression + overshoot relative to final position
    p0 = np.array([xs[0], ys[0]])
    p1 = np.array([xs[-1], ys[-1]])
    travel = np.linalg.norm(p1 - p0)
    overshoot = 0.0
    monotone_frac = 1.0
    if travel > 1.0:
        axis = (p1 - p0) / travel
        prog = (np.stack([xs, ys], axis=-1) - p0) @ axis
        overshoot = float(max(0.0, (prog.max() - travel) / travel))
        dprog = np.diff(prog)
        monotone_frac = float((dprog >= -0.5).mean())
    settle = None
    for i in range(len(speed) - 1, -1, -1):
        if speed[i] > 0.002:
            settle = i + 1
            break
    return {
        "status": "ok",
        "tracked_pairs": len(pts),
        "travel_px": round(float(travel), 1),
        "mean_speed_frac": round(float(speed.mean()), 5),
        "jerk_rms": round(float(np.sqrt(np.mean(jerk ** 2))) if jerk.size else 0.0, 6),
        "max_step_frac": round(float(speed.max()), 5),
        # Speed continuity: a dropped/skipped frame shows up as an acceleration
        # spike even when the raw step stays within an easing curve's fast phase.
        "max_accel_frac": round(float(np.abs(accel).max()) if accel.size else 0.0, 5),
        "monotone_fraction": round(monotone_frac, 4),
        "overshoot_fraction": round(overshoot, 4),
        "settle_pair_index": settle,
    }


def _timing_metrics(timestamps_path: str, spec: dict) -> dict:
    """
    Vsync jank from a JSON manifest: {"target_fps": 60, "timestamps_ms": [...]}
    Jank event: ceil(frame_delta / vsync) differs from the previous frame's.
    """
    data = json.loads(Path(timestamps_path).read_text(encoding="utf-8"))
    ts = np.asarray(data["timestamps_ms"], dtype=np.float64)
    target_fps = float(data.get("target_fps", spec.get("target_fps", 60)))
    vsync = 1000.0 / target_fps
    deltas = np.diff(ts)
    if deltas.size == 0:
        return {"status": "error", "reason": "fewer than 2 timestamps"}
    buckets = np.ceil(np.maximum(deltas, 0.1) / vsync)
    jank_events = int(np.sum(buckets[1:] != buckets[:-1]))
    dropped = int(np.sum(np.maximum(buckets - 1, 0)))
    deviation = np.abs(deltas - vsync)
    return {
        "status": "ok",
        "target_fps": target_fps,
        "frames": int(ts.size),
        "avg_fps": round(1000.0 / float(deltas.mean()), 2),
        "jank_events": jank_events,
        "jank_per_second": round(jank_events / (float(ts[-1] - ts[0]) / 1000.0), 2),
        "dropped_frame_estimate": dropped,
        "p95_deviation_ms": round(float(np.percentile(deviation, 95)), 2),
    }


def _motion_verdicts(payload: dict, spec: dict) -> list:
    """Budget checks. Only budgets present in the spec are asserted."""
    verdicts = []

    def check(name, value, limit, kind="max"):
        ok = value <= limit if kind == "max" else value >= limit
        verdicts.append({
            "check": name, "value": value, "limit": limit,
            "status": "pass" if ok else "fail",
        })

    if "max_duplicate_ratio" in spec:
        check("duplicate_ratio", payload["duplicates"]["ratio"], spec["max_duplicate_ratio"])
    if "max_stutter_run" in spec:
        check("max_stutter_run", payload["duplicates"]["max_stutter_run"], spec["max_stutter_run"])
    if "max_flicker_index" in spec:
        check("flicker_index", payload["flicker"]["index"], spec["max_flicker_index"])
    traj = payload.get("trajectory", {})
    if traj.get("status") == "ok":
        if "max_jerk_rms" in spec:
            check("jerk_rms", traj["jerk_rms"], spec["max_jerk_rms"])
        if "max_step_frac" in spec:
            check("max_step_frac", traj["max_step_frac"], spec["max_step_frac"])
        if "max_accel_frac" in spec:
            check("max_accel_frac", traj["max_accel_frac"], spec["max_accel_frac"])
        if "min_monotone_fraction" in spec:
            check("monotone_fraction", traj["monotone_fraction"],
                  spec["min_monotone_fraction"], kind="min")
        if "max_overshoot_fraction" in spec:
            check("overshoot_fraction", traj["overshoot_fraction"], spec["max_overshoot_fraction"])
    timing = payload.get("timing", {})
    if timing.get("status") == "ok" and "max_jank_per_second" in spec:
        check("jank_per_second", timing["jank_per_second"], spec["max_jank_per_second"])
    return verdicts


def _ncc_search(prev: np.ndarray, nxt: np.ndarray, x: float, y: float, patch: int = 7, radius: int = 24):
    """NCC template match. Floor for CoTracker/TAPIR."""
    h, w = prev.shape[:2]
    p = patch // 2
    xi, yi = int(round(x)), int(round(y))
    x0, x1 = max(0, xi - p), min(w, xi + p + 1)
    y0, y1 = max(0, yi - p), min(h, yi + p + 1)
    templ = luma(prev[y0:y1, x0:x1])
    if templ.size < 4:
        return x, y, 0.0
    best, bx, by = -2.0, xi, yi
    for ny in range(max(p, yi - radius), min(h - p, yi + radius + 1)):
        for nx in range(max(p, xi - radius), min(w - p, xi + radius + 1)):
            crop = luma(nxt[ny - p: ny + p + 1, nx - p: nx + p + 1])
            if crop.shape != templ.shape:
                continue
            a = templ - templ.mean()
            b = crop - crop.mean()
            denom = float(np.sqrt((a * a).sum() * (b * b).sum())) + 1e-9
            ncc = float((a * b).sum() / denom)
            if ncc > best:
                best, bx, by = ncc, nx, ny
    return float(bx), float(by), best


def _labeled_tracks(frames: list, points: list, spec: dict) -> dict:
    backend = "ncc"
    try:
        import cotracker  # noqa: F401
        backend = "cotracker-unavailable-runtime"  # import presence only; NCC remains the measured path
    except Exception:
        pass
    tracks = [[(float(p[0]), float(p[1]))] for p in points]
    scores = [[] for _ in points]
    for i in range(1, len(frames)):
        for t, pts in enumerate(tracks):
            x, y = pts[-1]
            nx, ny, ncc = _ncc_search(frames[i - 1], frames[i], x, y)
            pts.append((nx, ny))
            scores[t].append(ncc)
    jerks = []
    diag = math.hypot(frames[0].shape[1], frames[0].shape[0])
    for pts in tracks:
        arr = np.asarray(pts)
        if len(arr) < 4:
            continue
        vel = np.diff(arr, axis=0) / diag
        acc = np.diff(vel, axis=0)
        jerk = np.diff(acc, axis=0)
        jerks.append(float(np.sqrt((jerk ** 2).sum(axis=1).mean())) if len(jerk) else 0.0)
    return {
        "backend": backend,
        "n_points": len(points),
        "jerk_rms_mean": round(float(np.mean(jerks)) if jerks else 0.0, 6),
        "mean_ncc": round(float(np.mean([s for row in scores for s in row])) if scores else 0.0, 4),
        "points": [[list(map(lambda v: round(v, 2), xy)) for xy in t] for t in tracks],
    }


def _input_to_photon(frames: list, photon: dict) -> dict:
    """Frame index of first pixel change after injected input."""
    inject = int(photon.get("inject_frame", 0))
    threshold = float(photon.get("min_changed_fraction", 0.002))
    region = photon.get("region")
    baseline = frames[max(0, inject - 1)] if inject > 0 else frames[0]
    first = None
    for i in range(inject, len(frames)):
        mask = change_mask(baseline, frames[i], threshold_de=float(photon.get("change_de", 4.0)))
        if region:
            x, y, w, h = denorm_rect_local(region, frames[i].shape[1], frames[i].shape[0])
            frac = float(mask[y:y + h, x:x + w].mean()) if w and h else float(mask.mean())
        else:
            frac = float(mask.mean())
        if frac >= threshold:
            first = i
            break
    latency = None if first is None else first - inject
    return {
        "inject_frame": inject,
        "first_change_frame": first,
        "latency_frames": latency,
        "measured": first is not None,
        "note": None if first is not None else "no pixel change after inject within sequence",
    }


def denorm_rect_local(rect_frac, width, height):
    return _core.denorm_rect(rect_frac, width, height)


def _photon_verdicts(photon: dict, spec: dict) -> list:
    verdicts = []
    if "max_latency_frames" in spec:
        lat = photon.get("latency_frames")
        ok = lat is not None and lat <= int(spec["max_latency_frames"])
        verdicts.append({
            "check": "input_to_photon",
            "value": lat,
            "limit": spec["max_latency_frames"],
            "status": "pass" if ok else "fail",
        })
    return verdicts


def _track_verdicts(tracks: dict, spec: dict) -> list:
    verdicts = []
    if "max_track_jerk_rms" in spec:
        val = tracks["jerk_rms_mean"]
        ok = val <= float(spec["max_track_jerk_rms"])
        verdicts.append({
            "check": "track_jerk_rms",
            "value": val,
            "limit": spec["max_track_jerk_rms"],
            "status": "pass" if ok else "fail",
        })
    return verdicts
