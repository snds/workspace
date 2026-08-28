"""
Spectral-residual saliency (Hou & Zhang, 2007) as a UI Spirit floor.

UEyes-class gaze prediction is the intended critic; this is the no-weights
stand-in that still produces a spatial map. It highlights high-contrast
structure, not semantic importance, and is biased toward edges. Use it to
ask "would a first fixation land in this rect?" not "is this the title."

Altitude C. Never a Literal gutter/count substitute.
"""
from __future__ import annotations

import math

import numpy as np

from . import _core


def _box_blur(img: np.ndarray, win: int) -> np.ndarray:
    win = max(3, int(win) | 1)
    return _core._box_mean(
        np.pad(img, win // 2, mode="wrap"), win
    )[: img.shape[0], : img.shape[1]]


def spectral_residual(gray: np.ndarray, blur: int = 9) -> np.ndarray:
    """Return a [0,1] saliency map the same shape as gray."""
    g = np.asarray(gray, dtype=np.float64)
    g = g / (g.max() + 1e-9)
    f = np.fft.fft2(g)
    log_amp = np.log(np.abs(f) + 1e-8)
    avg = _box_blur(log_amp, 3)
    residual = log_amp - avg
    sal = np.abs(np.fft.ifft2(np.exp(residual + 1j * np.angle(f)))) ** 2
    sal = _box_blur(sal, blur)
    sal = sal - sal.min()
    peak = sal.max()
    if peak > 0:
        sal = sal / peak
    return sal


def region_mass(sal: np.ndarray, rect_px) -> dict:
    x, y, w, h = rect_px
    total = float(sal.sum()) + 1e-12
    inside = float(sal[y : y + h, x : x + w].sum())
    return {
        "mass_fraction": round(inside / total, 5),
        "peak_in_region": round(float(sal[y : y + h, x : x + w].max()) if w and h else 0.0, 5),
        "peak_global": round(float(sal.max()), 5),
    }
