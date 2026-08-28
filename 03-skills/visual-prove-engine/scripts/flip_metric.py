"""
LDR-FLIP-lite — viewing-distance-aware perceptual difference map.

Full NVIDIA FLIP (Andersson et al., HPG 2020) is the graphics-native error
map for render-vs-ground-truth. This module implements the paper's core
ingredients in numpy so the prove engine can emit a spatial map without a
CUDA/PyTorch dependency:

  1. sRGB → linear → CIE Lab
  2. CSF-ish spatial filter whose sigma is derived from pixels-per-degree
  3. HyAB color difference
  4. Edge-feature difference (Sobel magnitude after the same filter)
  5. Combined per-pixel error in [0, 1], plus median + MAD for GPU variance

When the optional `flip_evaluator` package is importable, `flip_map` prefers
it and records `backend: nvidia-flip`. Absence is never silent: reports
carry `backend: flip-lite`.

This is altitude B. It is not a substitute for gutter/Δe/count probes.
"""
from __future__ import annotations

import math
from typing import Optional

import numpy as np

from . import _core


def pixels_per_degree(height_px: int, monitor_height_m: float = 0.33,
                      viewing_distance_m: float = 0.70) -> float:
    """FLIP default-ish: 0.7 m from a ~27-inch 16:9 panel."""
    alpha = math.degrees(2.0 * math.atan((monitor_height_m / 2.0) / viewing_distance_m))
    return height_px / max(alpha, 1e-6)


def _gauss1d(sigma: float) -> np.ndarray:
    r = max(1, int(math.ceil(3.0 * sigma)))
    x = np.arange(-r, r + 1, dtype=np.float64)
    k = np.exp(-(x * x) / (2.0 * sigma * sigma))
    k /= k.sum()
    return k


def _sep_filter(ch: np.ndarray, k: np.ndarray) -> np.ndarray:
    """Separable convolution, edge-padded. ch is HxW float."""
    pad = len(k) // 2
    h = np.pad(ch, ((0, 0), (pad, pad)), mode="edge")
    tmp = np.apply_along_axis(lambda row: np.convolve(row, k, mode="valid"), 1, h)
    v = np.pad(tmp, ((pad, pad), (0, 0)), mode="edge")
    return np.apply_along_axis(lambda col: np.convolve(col, k, mode="valid"), 0, v)


def _sobel_mag(l: np.ndarray) -> np.ndarray:
    kx = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=np.float64)
    ky = kx.T
    pad = np.pad(l, 1, mode="edge")
    gx = (
        kx[0, 0] * pad[0:-2, 0:-2] + kx[0, 1] * pad[0:-2, 1:-1] + kx[0, 2] * pad[0:-2, 2:]
        + kx[1, 0] * pad[1:-1, 0:-2] + kx[1, 1] * pad[1:-1, 1:-1] + kx[1, 2] * pad[1:-1, 2:]
        + kx[2, 0] * pad[2:, 0:-2] + kx[2, 1] * pad[2:, 1:-1] + kx[2, 2] * pad[2:, 2:]
    )
    gy = (
        ky[0, 0] * pad[0:-2, 0:-2] + ky[0, 1] * pad[0:-2, 1:-1] + ky[0, 2] * pad[0:-2, 2:]
        + ky[1, 0] * pad[1:-1, 0:-2] + ky[1, 1] * pad[1:-1, 1:-1] + ky[1, 2] * pad[1:-1, 2:]
        + ky[2, 0] * pad[2:, 0:-2] + ky[2, 1] * pad[2:, 1:-1] + ky[2, 2] * pad[2:, 2:]
    )
    return np.hypot(gx, gy)


def _try_nvidia_flip(ref_rgb: np.ndarray, test_rgb: np.ndarray) -> Optional[np.ndarray]:
    try:
        import flip_evaluator as flip  # type: ignore
    except Exception:
        return None
    try:
        err, _meta = flip.evaluate(ref_rgb, test_rgb, "LDR")
        return np.asarray(err, dtype=np.float64)
    except Exception:
        return None


def flip_map(ref_rgb: np.ndarray, test_rgb: np.ndarray,
             ppd: Optional[float] = None) -> dict:
    """
    Returns {map, mean, median, mad, p95, backend}.
    `map` is HxW float in [0, 1]; higher = more visible difference.
    """
    if ref_rgb.shape != test_rgb.shape:
        raise ValueError(f"shape mismatch {ref_rgb.shape} vs {test_rgb.shape}")
    nvidia = _try_nvidia_flip(ref_rgb, test_rgb)
    if nvidia is not None:
        err = np.clip(nvidia, 0.0, 1.0)
        backend = "nvidia-flip"
    else:
        if ppd is None:
            ppd = pixels_per_degree(ref_rgb.shape[0])
        # CSF peak ~4–8 cpd; sigma in pixels ≈ ppd / (2π * cpd)
        sigma = max(0.6, ppd / (2.0 * math.pi * 6.0))
        k = _gauss1d(sigma)
        lab_a = _core.srgb_to_lab(ref_rgb)
        lab_b = _core.srgb_to_lab(test_rgb)
        fa = np.stack([_sep_filter(lab_a[..., c], k) for c in range(3)], axis=-1)
        fb = np.stack([_sep_filter(lab_b[..., c], k) for c in range(3)], axis=-1)
        dL = fa[..., 0] - fb[..., 0]
        dC = np.hypot(fa[..., 1] - fb[..., 1], fa[..., 2] - fb[..., 2])
        # HyAB, scaled so a Lab ΔE of ~20 is near 1 before clip
        color = np.hypot(dL, dC) / 20.0
        feat = np.abs(_sobel_mag(fa[..., 0]) - _sobel_mag(fb[..., 0]))
        feat = feat / (feat.max() + 1e-6) if feat.max() > 0 else feat
        err = np.clip(color * (1.0 + 0.5 * feat), 0.0, 1.0)
        backend = "flip-lite"
    med = float(np.median(err))
    mad = float(np.median(np.abs(err - med)))
    return {
        "map": err,
        "mean": round(float(err.mean()), 5),
        "median": round(med, 5),
        "mad": round(mad, 5),
        "p95": round(float(np.percentile(err, 95)), 5),
        "backend": backend,
        "ppd": None if backend == "nvidia-flip" else round(float(ppd), 2),
    }
