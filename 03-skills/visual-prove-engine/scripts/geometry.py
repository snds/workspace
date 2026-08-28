"""
Geometric consistency across pinned views. Altitude E.

A single still is never a 3D pass. This module requires >=2 images (orbit
or stereo). The no-weights floor is pairwise phase-correlation peak height
after luma registration: views of the same rigid scene share structure;
unrelated images do not. VGGT / DUSt3R are used when importable and their
absence is recorded — never faked into a reconstructed mesh.

`fallback: block` at the cue level: a required geometric_consistency cue
without two views is an error, not a skip.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

import numpy as np

from . import _core, compare
from ._core import load_image, luma


def vggt_available() -> bool:
    try:
        import vggt  # noqa: F401
        return True
    except Exception:
        return False


def dust3r_available() -> bool:
    try:
        import dust3r  # noqa: F401
        return True
    except Exception:
        return False


def pair_consistency(rgb_a: np.ndarray, rgb_b: np.ndarray) -> dict:
    """Phase-correlation peak + post-register SSIM. Not a reconstruction."""
    if rgb_a.shape != rgb_b.shape:
        rgb_b = _core.resize_rgb(rgb_b, rgb_a.shape[1], rgb_a.shape[0])
    ga, gb = luma(rgb_a), luma(rgb_b)
    dy, dx = compare.phase_correlate(ga, gb)
    # Peak height of the normalized cross-power spectrum
    a = ga - ga.mean()
    b = gb - gb.mean()
    fa = np.fft.rfft2(a)
    fb = np.fft.rfft2(b)
    cross = fa * np.conj(fb)
    denom = np.abs(cross)
    denom[denom == 0] = 1e-12
    corr = np.fft.irfft2(cross / denom, s=a.shape)
    peak = float(corr.max())
    mean = float(corr.mean())
    peak_over_mean = peak / (abs(mean) + 1e-9)
    shifted = compare._shift(rgb_b, dy, dx)
    ssim_mean, _ = _core.ssim(ga, luma(shifted))
    return {
        "shift": [int(dy), int(dx)],
        "peak": round(peak, 5),
        "peak_over_mean": round(float(peak_over_mean), 3),
        "ssim_registered": round(float(ssim_mean), 4),
    }


def consistency(view_paths: list, min_peak: float = 0.08,
                min_ssim: float = 0.25) -> dict:
    paths = [Path(p) for p in view_paths]
    if len(paths) < 2:
        return {
            "status": "error",
            "backend": "none",
            "note": "geometric consistency needs >=2 pinned views; a single still is not a 3D pass",
            "pairs": [],
        }
    imgs = [load_image(p) for p in paths]
    pairs = []
    for i in range(len(imgs) - 1):
        m = pair_consistency(imgs[i].rgb, imgs[i + 1].rgb)
        m["a"] = str(paths[i])
        m["b"] = str(paths[i + 1])
        pairs.append(m)
    backend = "phase-correlation"
    extra: dict = {}
    if vggt_available():
        backend = "vggt+phase-correlation"
        extra["vggt"] = "imported; pose dump not wired — phase-correlation remains the measured gate"
    elif dust3r_available():
        backend = "dust3r+phase-correlation"
        extra["dust3r"] = "imported; pose dump not wired — phase-correlation remains the measured gate"
    ok = all(p["peak"] >= min_peak and p["ssim_registered"] >= min_ssim for p in pairs)
    return {
        "status": "pass" if ok else "fail",
        "backend": backend,
        "views": len(paths),
        "min_peak": min_peak,
        "min_ssim": min_ssim,
        "pairs": pairs,
        **extra,
    }
