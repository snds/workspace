"""
perceive.py — structure-independent perception of a build capture.

Segments an image into foreground regions over an estimated (or given)
background, then measures each region from pixels alone: bbox, fill color,
per-corner radius, and a shape classification (bar / pill / rounded-bar /
elbow / single-corner-card / complex).

This is the module that answers "what is visually there," independent of what
the DOM or code claims. The single-corner-card and elbow classifiers implement
the Detect columns of visual-failure-mode-ledger rows C-08 and C-09.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import numpy as np

from . import _core
from ._core import (
    Img,
    estimate_background,
    foreground_mask,
    label_components,
    rgb_to_hex,
    srgb_to_lab,
)

# Fraction of a corner window that a quarter-circle leaves uncovered.
_CORNER_GAP_RATIO = 1.0 - math.pi / 4.0  # ~0.2146


@dataclass
class Region:
    label: int
    x: int
    y: int
    w: int
    h: int
    area: int
    fill_rgb: tuple
    fill_hex: str
    occupancy: float                 # area / bbox area
    corner_radii: dict = field(default_factory=dict)  # tl/tr/bl/br → px
    shape: str = "complex"
    open_quadrant: Optional[str] = None  # for elbows

    def to_dict(self) -> dict:
        return {
            "label": int(self.label),
            "bbox": [int(self.x), int(self.y), int(self.w), int(self.h)],
            "area": int(self.area),
            "fill": self.fill_hex,
            "occupancy": round(self.occupancy, 4),
            "corner_radii": {k: round(v, 1) for k, v in self.corner_radii.items()},
            "shape": self.shape,
            "open_quadrant": self.open_quadrant,
        }


def _corner_radius(mask: np.ndarray, corner: str) -> float:
    """
    Estimate the rounding radius of one bbox corner of a region mask.
    Counts uncovered pixels in a k x k corner window; a quarter-circle of
    radius r leaves ~0.2146 * r^2 uncovered.
    """
    h, w = mask.shape
    k = max(2, min(h, w) // 2)
    if corner == "tl":
        win = mask[:k, :k]
    elif corner == "tr":
        win = mask[:k, -k:]
    elif corner == "bl":
        win = mask[-k:, :k]
    else:
        win = mask[-k:, -k:]
    missing = int(win.size - int(win.sum()))
    if missing <= 2:
        return 0.0
    r = math.sqrt(missing / _CORNER_GAP_RATIO)
    return min(r, float(k))


def _quadrant_fill(mask: np.ndarray) -> dict:
    h, w = mask.shape
    hy, hx = max(1, h // 2), max(1, w // 2)
    quads = {
        "tl": mask[:hy, :hx],
        "tr": mask[:hy, hx:],
        "bl": mask[hy:, :hx],
        "br": mask[hy:, hx:],
    }
    return {k: float(v.mean()) if v.size else 0.0 for k, v in quads.items()}


def classify_shape(mask: np.ndarray) -> tuple:
    """
    Classify a region mask. Returns (shape, corner_radii, open_quadrant).

    Grammar (deliberately LCARS-aware but generic):
      bar                — all corners sharp
      pill               — wide, end radii ~ h/2 on both ends
      rounded-bar        — all corners rounded, r well below h/2
      single-corner-card — exactly one rounded corner (ledger C-09)
      elbow              — one sparse quadrant, three dense (constant-thickness L)
      complex            — anything else
    """
    h, w = mask.shape
    occ = float(mask.mean())
    quads = _quadrant_fill(mask)
    sparse = [k for k, v in quads.items() if v < 0.35]
    dense = [k for k, v in quads.items() if v > 0.60]
    if len(sparse) == 1 and len(dense) == 3 and 0.35 <= occ <= 0.92:
        radii = {c: _corner_radius(mask, c) for c in ("tl", "tr", "bl", "br")}
        return "elbow", radii, sparse[0]

    radii = {c: _corner_radius(mask, c) for c in ("tl", "tr", "bl", "br")}
    short_side = float(min(h, w))
    sharp_thresh = max(2.0, 0.08 * short_side)
    round_thresh = max(4.0, 0.15 * short_side)
    rounded = [c for c, r in radii.items() if r > round_thresh]
    sharp = [c for c, r in radii.items() if r <= sharp_thresh]

    if len(sharp) == 4:
        return "bar", radii, None
    if len(rounded) == 1 and len(sharp) == 3:
        return "single-corner-card", radii, None
    if len(rounded) == 4:
        half = short_side / 2.0
        end_like = [r for r in radii.values() if abs(r - half) <= 0.25 * half]
        if len(end_like) == 4 and (max(h, w) / short_side) >= 1.3:
            return "pill", radii, None
        return "rounded-bar", radii, None
    return "complex", radii, None


def perceive(
    img: Img,
    background: Optional[tuple] = None,
    bg_tol_de: float = 6.0,
    min_area_frac: float = 0.00002,
    max_regions: int = 400,
) -> dict:
    """
    Full perception pass. Returns a dict payload (JSON-safe) with the
    background estimate, region inventory, gutter statistics, palette,
    and ledger-derived flags.
    """
    rgb = img.rgb
    bg = background if background is not None else estimate_background(rgb)
    fg = foreground_mask(rgb, bg, tol_de=bg_tol_de)
    labels, n = label_components(fg)
    min_area = max(4, int(min_area_frac * rgb.shape[0] * rgb.shape[1]))

    regions: list[Region] = []
    if n > 0:
        flat = labels.ravel()
        counts = np.bincount(flat, minlength=n + 1)
        order = np.argsort(counts[1:])[::-1] + 1
        ys, xs = np.nonzero(labels)
        lab_of = labels[ys, xs]
        for lb in order[: max_regions * 2]:
            area = int(counts[lb])
            if area < min_area:
                continue
            sel = lab_of == lb
            ry, rx = ys[sel], xs[sel]
            x0, x1 = int(rx.min()), int(rx.max())
            y0, y1 = int(ry.min()), int(ry.max())
            w, h = x1 - x0 + 1, y1 - y0 + 1
            mask = labels[y0 : y1 + 1, x0 : x1 + 1] == lb
            pix = rgb[ry, rx].astype(np.float64)
            fill = tuple(float(v) for v in np.median(pix, axis=0))
            shape, radii, open_q = classify_shape(mask)
            regions.append(
                Region(
                    label=int(lb),
                    x=x0,
                    y=y0,
                    w=w,
                    h=h,
                    area=area,
                    fill_rgb=fill,
                    fill_hex=rgb_to_hex(fill),
                    occupancy=area / float(w * h),
                    corner_radii=radii,
                    shape=shape,
                    open_quadrant=open_q,
                )
            )
            if len(regions) >= max_regions:
                break

    gutters = gutter_stats(fg)
    palette = dominant_palette(rgb, fg, k=8)
    flags = ledger_flags(regions, rgb)

    return {
        "engine": _core.ENGINE_VERSION,
        "image": str(img.path) if img.path else None,
        "size": [img.width, img.height],
        "background": rgb_to_hex(bg),
        "region_count": len(regions),
        "regions": [r.to_dict() for r in regions],
        "gutters": gutters,
        "palette": palette,
        "ledger_flags": flags,
    }


def gutter_stats(fg: np.ndarray) -> dict:
    """
    Background-run statistics between content, measured on the full mask.
    Horizontal gutters: per content row-band gaps along x; vertical: along y.
    Returns mode/median of interior gaps in both axes (px).
    """
    out = {}
    for axis, name in ((1, "columns"), (0, "rows")):
        profile = fg.any(axis=axis)
        gaps = _interior_gaps(profile)
        out[name] = {
            "gap_count": len(gaps),
            "mode_px": _mode(gaps),
            "median_px": float(np.median(gaps)) if gaps else None,
        }
    # Fine-grain: gaps along x within each content row (captures inter-module gutters)
    row_gaps: list[int] = []
    step = max(1, fg.shape[0] // 256)
    for y in range(0, fg.shape[0], step):
        row_gaps.extend(_interior_gaps(fg[y]))
    out["inline"] = {
        "gap_count": len(row_gaps),
        "mode_px": _mode(row_gaps),
        "median_px": float(np.median(row_gaps)) if row_gaps else None,
    }
    return out


def _interior_gaps(profile: np.ndarray) -> list:
    idx = np.nonzero(profile)[0]
    if idx.size < 2:
        return []
    gaps = np.diff(idx) - 1
    return [int(g) for g in gaps if g > 0]


def _mode(values: list) -> Optional[int]:
    if not values:
        return None
    vals, counts = np.unique(np.asarray(values), return_counts=True)
    return int(vals[int(np.argmax(counts))])


def dominant_palette(rgb: np.ndarray, fg: np.ndarray, k: int = 8) -> list:
    """Top-k quantized foreground colors with coverage fractions."""
    if not fg.any():
        return []
    px = rgb[fg]
    q = (px >> 4).astype(np.int64)
    keys = (q[:, 0] << 8) | (q[:, 1] << 4) | q[:, 2]
    vals, counts = np.unique(keys, return_counts=True)
    order = np.argsort(counts)[::-1][:k]
    total = float(px.shape[0])
    entries = []
    for i in order:
        sel = keys == vals[i]
        mean = px[sel].astype(np.float64).mean(axis=0)
        entries.append(
            {"hex": rgb_to_hex(mean), "fraction": round(float(counts[i]) / total, 4)}
        )
    return entries


def ledger_flags(regions: list, rgb: np.ndarray) -> list:
    """Machine checks derived from visual-failure-mode-ledger Detect columns."""
    flags = []
    cards = [r for r in regions if r.shape == "single-corner-card"]
    if cards:
        flags.append(
            {
                "ledger": "C-09",
                "severity": "high",
                "message": f"{len(cards)} single-corner-card region(s) — banned LCARS chrome shape",
                "regions": [c.to_dict()["bbox"] for c in cards[:10]],
            }
        )
    lum = _core.luma(rgb)
    clip_frac = float((lum >= 254.0).mean())
    if clip_frac > 0.02:
        flags.append(
            {
                "ledger": "A-04",
                "severity": "medium",
                "message": f"{clip_frac:.1%} of pixels at clip white (blowout check)",
            }
        )
    return flags


def banding_score(gray_strip: np.ndarray, axis: int = 1) -> dict:
    """
    Banding detector for a region expected to be a smooth ramp (ledger A-01).

    Definition: a smooth 8-bit ramp spanning S luminance levels shows ~S+1
    distinct levels; a banded ramp collapses onto far fewer plateaus. The
    level-deficit ratio 1 - (levels-1)/span is ~0 for a smooth ramp and → 1
    for hard banding. Plain 8-bit quantization (step height 1) is NOT banding
    and must not fire this detector.
    """
    prof = gray_strip.mean(axis=0 if axis == 1 else 1)
    if prof.size < 8:
        return {"levels": 0, "span": 0, "deficit_ratio": 0.0, "banded": False}
    levels = int(np.unique(np.round(prof)).size)
    span = float(prof.max() - prof.min())
    if span < 1.0:
        return {"levels": levels, "span": round(span, 1), "deficit_ratio": 0.0, "banded": False}
    deficit = 1.0 - (levels - 1) / span
    deficit = float(max(0.0, min(1.0, deficit)))
    d = np.abs(np.diff(prof))
    max_step = float(d.max()) if d.size else 0.0
    return {
        "levels": levels,
        "span": round(span, 1),
        "deficit_ratio": round(deficit, 4),
        "max_step": round(max_step, 2),
        "banded": bool(deficit > 0.5 and span >= 24.0 and max_step >= 2.0),
    }


def annotate(img: Img, payload: dict, out_path: str | Path) -> Path:
    """Draw region bboxes + shape labels for human review (PIL only)."""
    from PIL import Image, ImageDraw

    pil = Image.fromarray(img.rgb.astype(np.uint8), "RGB").convert("RGB")
    draw = ImageDraw.Draw(pil)
    colors = {
        "bar": (37, 99, 235),
        "pill": (22, 163, 74),
        "rounded-bar": (13, 148, 136),
        "elbow": (139, 92, 246),
        "single-corner-card": (220, 38, 38),
        "complex": (107, 114, 128),
    }
    for r in payload.get("regions", []):
        x, y, w, h = r["bbox"]
        c = colors.get(r["shape"], (107, 114, 128))
        draw.rectangle([x, y, x + w - 1, y + h - 1], outline=c, width=2)
        draw.text((x + 3, max(0, y - 12)), r["shape"], fill=c)
    p = Path(out_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    pil.save(p, format="PNG")
    return p
