"""
Mid-level perceptual similarity (DreamSim). Altitude C.

DreamSim is the right tool for Spirit / novel-view / "is this the same object
and pose" questions. It is the wrong tool for Literal gutters, 8px gaps, and
hex fills. Foreground-biased: a matching hero with a different chrome frame
can still score close.

When torch / dreamsim are absent the probe degrades — skip if optional, else
error. Never silent.
"""
from __future__ import annotations

from typing import Optional

import numpy as np


def available() -> bool:
    try:
        import dreamsim  # noqa: F401
        import torch  # noqa: F401
        return True
    except Exception:
        return False


_MODEL = None


def _model():
    global _MODEL
    if _MODEL is None:
        from dreamsim import dreamsim as _load  # type: ignore
        _MODEL = _load(pretrained=True, device="cpu")
    return _MODEL


def distance(rgb_a: np.ndarray, rgb_b: np.ndarray) -> Optional[float]:
    """
    DreamSim distance in ~[0, 1] (higher = more different). None if unavailable.
    """
    if not available():
        return None
    if rgb_a.shape != rgb_b.shape:
        from . import _core
        rgb_b = _core.resize_rgb(rgb_b, rgb_a.shape[1], rgb_a.shape[0])
    try:
        import torch
        from PIL import Image
        model, preprocess = _model()
        ta = preprocess(Image.fromarray(rgb_a.astype("uint8"), "RGB")).unsqueeze(0)
        tb = preprocess(Image.fromarray(rgb_b.astype("uint8"), "RGB")).unsqueeze(0)
        with torch.no_grad():
            d = model(ta, tb)
        return float(d.item() if hasattr(d, "item") else d)
    except Exception:
        return None
