"""
compare.py — reference-vs-build comparison with registration, tiled SSIM,
delta-E statistics, and multi-candidate ranking.

Scale handling: the build is resampled to the reference's dimensions when
aspect ratios agree (within a small tolerance). Aspect mismatch is reported,
not silently cropped. Fine translation is registered by phase correlation
(pure numpy FFT) within a bounded search radius so global metrics are not
dominated by a 1-2px capture offset.

Honest limits: cross-scale SSIM rewards structural agreement, not pixel
identity; a composition mismatch shows up as low tile scores across large
areas rather than a precise geometry diff (that is `prove`'s job).
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

import numpy as np

from . import _core
from ._core import Img, delta_e_map, load_image, luma, resize_rgb, save_image, ssim, write_json


def phase_correlate(gray_ref: np.ndarray, gray_mov: np.ndarray, max_shift: int = 32):
    """Estimate (dy, dx) translation of mov relative to ref. Pure numpy."""
    a = gray_ref - gray_ref.mean()
    b = gray_mov - gray_mov.mean()
    fa = np.fft.rfft2(a)
    fb = np.fft.rfft2(b)
    cross = fa * np.conj(fb)
    denom = np.abs(cross)
    denom[denom == 0] = 1e-12
    corr = np.fft.irfft2(cross / denom, s=a.shape)
    peak = np.unravel_index(int(np.argmax(corr)), corr.shape)
    dy, dx = peak
    if dy > a.shape[0] // 2:
        dy -= a.shape[0]
    if dx > a.shape[1] // 2:
        dx -= a.shape[1]
    dy = int(np.clip(dy, -max_shift, max_shift))
    dx = int(np.clip(dx, -max_shift, max_shift))
    return dy, dx


def _shift(rgb: np.ndarray, dy: int, dx: int, fill=(0, 0, 0)) -> np.ndarray:
    out = np.empty_like(rgb)
    out[...] = np.asarray(fill, dtype=rgb.dtype)
    h, w = rgb.shape[:2]
    ys0, ys1 = max(0, dy), min(h, h + dy)
    xs0, xs1 = max(0, dx), min(w, w + dx)
    yd0, yd1 = max(0, -dy), min(h, h - dy)
    xd0, xd1 = max(0, -dx), min(w, w - dx)
    out[ys0:ys1, xs0:xs1] = rgb[yd0:yd1, xd0:xd1]
    return out


def compare_pair(
    ref: Img,
    build: Img,
    out_dir: Optional[str | Path] = None,
    tile: int = 8,
    label: str = "build",
) -> dict:
    """Compare one build against the reference. Returns metric payload."""
    ar_ref = ref.width / ref.height
    ar_build = build.width / build.height
    aspect_delta = abs(ar_ref - ar_build) / ar_ref

    work = build.rgb
    if (build.width, build.height) != (ref.width, ref.height):
        work = resize_rgb(work, ref.width, ref.height)

    dy, dx = phase_correlate(luma(ref.rgb), luma(work))
    if dy or dx:
        work = _shift(work, dy, dx)

    ssim_mean, ssim_map = ssim(luma(ref.rgb), luma(work))
    de = delta_e_map(ref.rgb, work)
    tiles = _tile_scores(ssim_map, tile)

    payload = {
        "label": label,
        "reference": str(ref.path) if ref.path else None,
        "build": str(build.path) if build.path else None,
        "ref_size": [ref.width, ref.height],
        "build_size": [build.width, build.height],
        "aspect_delta": round(float(aspect_delta), 4),
        "registration": {"dy": dy, "dx": dx},
        "ssim": round(ssim_mean, 4),
        "delta_e": {
            "mean": round(float(de.mean()), 2),
            "p95": round(float(np.percentile(de, 95)), 2),
            "max": round(float(de.max()), 2),
            "frac_over_10": round(float((de > 10).mean()), 4),
        },
        "worst_tiles": tiles,
    }
    if aspect_delta > 0.02:
        payload["warning"] = (
            f"aspect mismatch {ar_build:.3f} vs {ar_ref:.3f} — build was stretched to "
            "reference dims; treat global metrics as degraded"
        )

    if out_dir:
        out = Path(out_dir)
        stem = Path(build.path).stem if build.path else label
        heat = _heatmap(de, cap=25.0)
        p1 = save_image(heat, out / f"{stem}_deltaE_heat.png")
        sm = np.clip((1.0 - ssim_map) * 255.0, 0, 255).astype(np.uint8)
        p2 = save_image(np.stack([sm, sm, sm], axis=-1), out / f"{stem}_ssim_inv.png")
        side = _side_by_side(ref.rgb, work)
        p3 = save_image(side, out / f"{stem}_side_by_side.png")
        payload["artifacts"] = [str(p1), str(p2), str(p3)]
    return payload


def _tile_scores(ssim_map: np.ndarray, grid: int) -> list:
    h, w = ssim_map.shape
    th, tw = max(1, h // grid), max(1, w // grid)
    scores = []
    for gy in range(grid):
        for gx in range(grid):
            block = ssim_map[gy * th : (gy + 1) * th, gx * tw : (gx + 1) * tw]
            if block.size:
                scores.append((float(block.mean()), gy, gx))
    scores.sort(key=lambda t: t[0])
    return [
        {"tile": [gy, gx], "ssim": round(s, 4)} for s, gy, gx in scores[:8]
    ]


def _heatmap(de: np.ndarray, cap: float = 25.0) -> np.ndarray:
    t = np.clip(de / cap, 0.0, 1.0)
    r = (255 * t).astype(np.uint8)
    g = (255 * (1.0 - np.abs(t - 0.5) * 2)).astype(np.uint8)
    b = (255 * (1.0 - t)).astype(np.uint8)
    return np.stack([r, g, b], axis=-1)


def _side_by_side(a: np.ndarray, b: np.ndarray, gap: int = 8) -> np.ndarray:
    h = max(a.shape[0], b.shape[0])
    w = a.shape[1] + b.shape[1] + gap
    out = np.zeros((h, w, 3), dtype=np.uint8)
    out[: a.shape[0], : a.shape[1]] = a
    out[: b.shape[0], a.shape[1] + gap :] = b
    return out


def compare_rank(
    reference_path: str | Path,
    build_paths: list,
    out_dir: Optional[str | Path] = None,
) -> dict:
    """
    Compare several builds against one reference and rank them.
    Composite closeness = mean(SSIM, 1 - clipped mean delta-E / 25).
    Used for improvement verification: a later build must not rank below
    an earlier accepted one.
    """
    ref = load_image(reference_path)
    entries = []
    for bp in build_paths:
        build = load_image(bp)
        m = compare_pair(ref, build, out_dir=out_dir, label=Path(bp).stem)
        closeness = float(np.mean([m["ssim"], 1.0 - min(m["delta_e"]["mean"], 25.0) / 25.0]))
        m["closeness"] = round(closeness, 4)
        entries.append(m)
    ranked = sorted(entries, key=lambda e: e["closeness"], reverse=True)
    payload = {
        "engine": _core.ENGINE_VERSION,
        "reference": str(Path(reference_path).resolve()),
        "ranking": [
            {"rank": i + 1, "build": e["build"], "closeness": e["closeness"],
             "ssim": e["ssim"], "delta_e_mean": e["delta_e"]["mean"]}
            for i, e in enumerate(ranked)
        ],
        "detail": entries,
    }
    if out_dir:
        write_json(payload, Path(out_dir) / "compare_rank.json")
    return payload
