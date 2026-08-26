"""
probes.py — typed, deterministic cue probes for the prove engine.

Each probe takes (cue dict, context) and returns a _core.CueResult.
Probes measure pixels; they never trust code structure or DOM claims.

Probe registry (cuespec `probe` field):
  aspect            — canvas W:H vs target ratio
  color_at          — color at a normalized point vs target hex (delta-E)
  region_color      — dominant color of a rect vs target hex (delta-E)
  band_thickness    — contiguous non-background run along an axis at a position
  gutter            — background-gap mode within a rect vs target px
  region_present    — rect contains enough non-background (or target-colored) pixels
  region_absent     — inverse of region_present
  count_regions     — connected foreground components within a rect
  ssim_region       — SSIM of a rect crop vs an asset image
  shape_class       — perceive-classified shape of the dominant region in a rect
  gradient_smooth   — banding score of a ramp region (ledger A-01)
  attest            — explicitly unmeasured human/code attestation (never counts as measured)

Conventions:
  - All rects/points are fractions of the canvas [x, y, w, h] / [x, y].
  - px targets may carry `at_height`: the canvas height they were measured at;
    the probe rescales them to the build's height before comparing.
  - Every result carries a normalized margin (1 = exact, 0 = tolerance edge).
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Optional

import numpy as np

from . import _core, perceive
from ._core import (
    CueResult,
    crop,
    delta_e76,
    denorm_rect,
    estimate_background,
    foreground_mask,
    hex_to_rgb,
    label_components,
    luma,
    resize_rgb,
    rel_margin,
    rgb_to_hex,
    sample_disc,
    ssim,
)


class ProbeContext:
    """Everything a probe may need. Built once per prove run."""

    def __init__(self, img: _core.Img, spec_dir: Path, background=None):
        self.img = img
        self.spec_dir = spec_dir
        self._background = background
        self._fg = None

    @property
    def background(self):
        if self._background is None:
            self._background = estimate_background(self.img.rgb)
        return self._background

    @property
    def fg(self) -> np.ndarray:
        if self._fg is None:
            self._fg = foreground_mask(self.img.rgb, self.background)
        return self._fg

    def resolve(self, rel: str) -> Path:
        p = Path(rel).expanduser()
        return p if p.is_absolute() else (self.spec_dir / p)


def _res(cue: dict, **kw) -> CueResult:
    return CueResult(
        id=cue.get("id"),
        name=cue.get("name", str(cue.get("id"))),
        probe=cue.get("probe", "?"),
        **kw,
    )


def _scale_px(cue: dict, px: float, build_h: int) -> float:
    at_h = cue.get("at_height")
    if at_h:
        return px * (build_h / float(at_h))
    return px


# ── Probe implementations ────────────────────────────────────

def probe_aspect(cue: dict, ctx: ProbeContext) -> CueResult:
    tw, th = cue["target"]
    target = float(tw) / float(th)
    value = ctx.img.width / ctx.img.height
    tol = float(cue.get("tol", 0.01))
    margin = rel_margin(value, target, tol * target)
    return _res(
        cue,
        status="pass" if margin >= 0 else "fail",
        measured=True,
        value=round(value, 4),
        target=round(target, 4),
        tolerance=f"±{tol:.2%}",
        margin=round(margin, 4),
        note=f"canvas {ctx.img.width}x{ctx.img.height}",
    )


def probe_color_at(cue: dict, ctx: ProbeContext) -> CueResult:
    fx, fy = cue["at"]
    x = int(round(fx * ctx.img.width))
    y = int(round(fy * ctx.img.height))
    color = sample_disc(ctx.img.rgb, x, y, radius=int(cue.get("radius", 3)))
    target = hex_to_rgb(cue["target"])
    de = delta_e76(color, target)
    tol = float(cue.get("tol_de", 3.0))
    margin = 1.0 - de / tol if tol > 0 else (1.0 if de == 0 else -1.0)
    return _res(
        cue,
        status="pass" if de <= tol else "fail",
        measured=True,
        value={"hex": rgb_to_hex(color), "delta_e": round(de, 2), "at_px": [x, y]},
        target=cue["target"],
        tolerance=f"delta_e<={tol}",
        margin=round(margin, 4),
    )


def probe_region_color(cue: dict, ctx: ProbeContext) -> CueResult:
    rect = denorm_rect(cue["rect"], ctx.img.width, ctx.img.height)
    region = crop(ctx.img.rgb, rect).reshape(-1, 3).astype(np.float64)
    if cue.get("exclude_background", True):
        bg = np.asarray(ctx.background, dtype=np.float64)
        keep = np.linalg.norm(
            _core.srgb_to_lab(region) - _core.srgb_to_lab(bg.reshape(1, 3)), axis=-1
        ) > 6.0
        if keep.any():
            region = region[keep]
    color = tuple(float(v) for v in np.median(region, axis=0))
    target = hex_to_rgb(cue["target"])
    de = delta_e76(color, target)
    tol = float(cue.get("tol_de", 3.0))
    margin = 1.0 - de / tol if tol > 0 else (1.0 if de == 0 else -1.0)
    return _res(
        cue,
        status="pass" if de <= tol else "fail",
        measured=True,
        value={"hex": rgb_to_hex(color), "delta_e": round(de, 2), "rect_px": list(rect)},
        target=cue["target"],
        tolerance=f"delta_e<={tol}",
        margin=round(margin, 4),
    )


def probe_band_thickness(cue: dict, ctx: ProbeContext) -> CueResult:
    """Thickness of the contiguous foreground run crossing a scanline."""
    axis = cue.get("axis", "y")  # 'y': vertical run at given x
    if axis == "y":
        x = int(round(cue["at"] * ctx.img.width))
        y0f, y1f = cue.get("range", [0.0, 1.0])
        y0, y1 = int(y0f * ctx.img.height), int(y1f * ctx.img.height)
        line = ctx.fg[y0:y1, x]
    else:
        y = int(round(cue["at"] * ctx.img.height))
        x0f, x1f = cue.get("range", [0.0, 1.0])
        x0, x1 = int(x0f * ctx.img.width), int(x1f * ctx.img.width)
        line = ctx.fg[y, x0:x1]
    runs = _runs(line)
    value = float(max(runs)) if runs else 0.0
    dim = ctx.img.height if axis == "y" else ctx.img.width
    if "target_frac" in cue:
        target = float(cue["target_frac"]) * dim
        tol = float(cue.get("tol_frac", 0.005)) * dim
    else:
        target = _scale_px(cue, float(cue["target_px"]), dim)
        tol = _scale_px(cue, float(cue.get("tol_px", 2.0)), dim)
    margin = rel_margin(value, target, tol)
    return _res(
        cue,
        status="pass" if margin >= 0 else "fail",
        measured=True,
        value={"px": value, "runs_found": len(runs)},
        target=round(target, 1),
        tolerance=f"±{tol:.1f}px",
        margin=round(margin, 4),
    )


def probe_band_edge(cue: dict, ctx: ProbeContext) -> CueResult:
    """Position (leading edge) of the first foreground run crossing a scanline."""
    axis = cue.get("axis", "y")
    if axis == "y":
        x = int(round(cue["at"] * ctx.img.width))
        y0f, y1f = cue.get("range", [0.0, 1.0])
        y0, y1 = int(y0f * ctx.img.height), int(y1f * ctx.img.height)
        line = ctx.fg[y0:y1, x]
        base = y0
        dim = ctx.img.height
    else:
        y = int(round(cue["at"] * ctx.img.height))
        x0f, x1f = cue.get("range", [0.0, 1.0])
        x0, x1 = int(x0f * ctx.img.width), int(x1f * ctx.img.width)
        line = ctx.fg[y, x0:x1]
        base = x0
        dim = ctx.img.width
    idx = np.nonzero(line)[0]
    if idx.size == 0:
        return _res(cue, status="fail", measured=True, value=None,
                    target=cue.get("target_px", cue.get("target_frac")),
                    margin=-1.0, note="no foreground on scanline")
    value = float(base + int(idx[0]))
    if "target_frac" in cue:
        target = float(cue["target_frac"]) * dim
        tol = float(cue.get("tol_frac", 0.005)) * dim
    else:
        target = _scale_px(cue, float(cue["target_px"]), dim)
        tol = _scale_px(cue, float(cue.get("tol_px", 2.0)), dim)
    margin = rel_margin(value, target, tol)
    return _res(
        cue,
        status="pass" if margin >= 0 else "fail",
        measured=True,
        value={"edge_px": value},
        target=round(target, 1),
        tolerance=f"±{tol:.1f}px",
        margin=round(margin, 4),
    )


def _runs(line: np.ndarray) -> list:
    out, cur = [], 0
    for v in line:
        if v:
            cur += 1
        elif cur:
            out.append(cur)
            cur = 0
    if cur:
        out.append(cur)
    return out


def probe_gutter(cue: dict, ctx: ProbeContext) -> CueResult:
    rect = denorm_rect(cue.get("rect", [0, 0, 1, 1]), ctx.img.width, ctx.img.height)
    x, y, w, h = rect
    # Own mask with a higher perceptual threshold than the global foreground:
    # soft anti-aliased edge rows (delta-E ~5-8 over the background) must not
    # count as content or renderer blur shifts every measured gap.
    from ._core import foreground_mask as _fgm

    sub = _fgm(
        ctx.img.rgb[y : y + h, x : x + w],
        ctx.background,
        tol_de=float(cue.get("bg_tol_de", 10.0)),
    )
    axis = cue.get("axis", "inline")
    gaps: list = []
    if axis in ("inline", "columns"):
        step = max(1, sub.shape[0] // 256)
        for row in range(0, sub.shape[0], step):
            gaps.extend(perceive._interior_gaps(sub[row]))
    else:
        prof = sub.any(axis=1)
        gaps = perceive._interior_gaps(prof)
    gaps = [g for g in gaps if g <= max(64, sub.shape[1] // 4)]
    mode = perceive._mode(gaps)
    target = _scale_px(cue, float(cue["target_px"]), ctx.img.height)
    tol = _scale_px(cue, float(cue.get("tol_px", 1.0)), ctx.img.height)
    if mode is None:
        return _res(cue, status="fail", measured=True, value=None,
                    target=round(target, 1), tolerance=f"±{tol:.1f}px",
                    margin=-1.0, note="no interior gaps found in rect")
    margin = rel_margin(float(mode), target, tol)
    return _res(
        cue,
        status="pass" if margin >= 0 else "fail",
        measured=True,
        value={"mode_px": mode, "gap_count": len(gaps)},
        target=round(target, 1),
        tolerance=f"±{tol:.1f}px",
        margin=round(margin, 4),
    )


def probe_region_present(cue: dict, ctx: ProbeContext) -> CueResult:
    return _presence(cue, ctx, expect_present=True)


def probe_region_absent(cue: dict, ctx: ProbeContext) -> CueResult:
    return _presence(cue, ctx, expect_present=False)


def _presence(cue: dict, ctx: ProbeContext, expect_present: bool) -> CueResult:
    rect = denorm_rect(cue["rect"], ctx.img.width, ctx.img.height)
    x, y, w, h = rect
    if "color" in cue:
        target = np.asarray(hex_to_rgb(cue["color"]), dtype=np.float64)
        region = crop(ctx.img.rgb, rect)
        de = np.linalg.norm(
            _core.srgb_to_lab(region) - _core.srgb_to_lab(target.reshape(1, 1, 3)),
            axis=-1,
        )
        frac = float((de <= float(cue.get("tol_de", 6.0))).mean())
    else:
        frac = float(ctx.fg[y : y + h, x : x + w].mean())
    min_frac = float(cue.get("min_fraction", 0.05))
    ok = frac >= min_frac if expect_present else frac < min_frac
    margin = (frac - min_frac) if expect_present else (min_frac - frac)
    return _res(
        cue,
        status="pass" if ok else "fail",
        measured=True,
        value={"fraction": round(frac, 4), "rect_px": list(rect)},
        target=("present" if expect_present else "absent") + f" >= {min_frac}",
        tolerance=None,
        margin=round(float(margin), 4),
    )


def probe_count_regions(cue: dict, ctx: ProbeContext) -> CueResult:
    rect = denorm_rect(cue["rect"], ctx.img.width, ctx.img.height)
    x, y, w, h = rect
    sub = ctx.fg[y : y + h, x : x + w]
    labels, n = label_components(sub)
    if n:
        counts = np.bincount(labels.ravel())[1:]
        min_area = float(cue.get("min_area_px", 12))
        at_h = cue.get("at_height")
        if at_h:  # area scales quadratically with capture height
            min_area = max(4.0, min_area * (ctx.img.height / float(at_h)) ** 2)
        n = int((counts >= min_area).sum())
    lo, hi = cue.get("target_range", [cue.get("target", 1), cue.get("target", 1)])
    ok = lo <= n <= hi
    span = max(1.0, (hi - lo) / 2.0 + 1.0)
    margin = 1.0 - (max(lo - n, n - hi, 0) / span)
    return _res(
        cue,
        status="pass" if ok else "fail",
        measured=True,
        value=n,
        target=f"[{lo}, {hi}]",
        tolerance=None,
        margin=round(margin, 4),
    )


def probe_ssim_region(cue: dict, ctx: ProbeContext) -> CueResult:
    rect = denorm_rect(cue["rect"], ctx.img.width, ctx.img.height)
    region = crop(ctx.img.rgb, rect)
    asset_path = ctx.resolve(cue["asset"])
    if not asset_path.exists():
        return _res(cue, status="error", measured=False, value=None,
                    note=f"asset missing: {asset_path}")
    asset = _core.load_image(asset_path)
    asset_rgb = asset.rgb
    if "asset_rect" in cue:  # like-for-like: compare against the same region of the asset
        asset_rgb = crop(asset_rgb, denorm_rect(cue["asset_rect"], asset.width, asset.height))
    asset_rgb = resize_rgb(asset_rgb, region.shape[1], region.shape[0])
    score, _ = ssim(luma(region), luma(asset_rgb))
    min_score = float(cue.get("min", 0.85))
    margin = (score - min_score) / max(1e-9, 1.0 - min_score)
    return _res(
        cue,
        status="pass" if score >= min_score else "fail",
        measured=True,
        value=round(score, 4),
        target=f">={min_score}",
        tolerance=None,
        margin=round(float(margin), 4),
        note=f"asset {asset_path.name} resized to {region.shape[1]}x{region.shape[0]}",
    )


def probe_shape_class(cue: dict, ctx: ProbeContext) -> CueResult:
    rect = denorm_rect(cue["rect"], ctx.img.width, ctx.img.height)
    x, y, w, h = rect
    sub = ctx.fg[y : y + h, x : x + w]
    labels, n = label_components(sub)
    if n == 0:
        return _res(cue, status="fail", measured=True, value="empty",
                    target=cue["target"], margin=-1.0,
                    note="no foreground region in rect")
    counts = np.bincount(labels.ravel())
    counts[0] = 0
    lb = int(np.argmax(counts))
    ys, xs = np.nonzero(labels == lb)
    mask = (labels == lb)[ys.min() : ys.max() + 1, xs.min() : xs.max() + 1]
    shape, radii, open_q = perceive.classify_shape(mask)
    targets = cue["target"] if isinstance(cue["target"], list) else [cue["target"]]
    ok = shape in targets
    return _res(
        cue,
        status="pass" if ok else "fail",
        measured=True,
        value={"shape": shape, "corner_radii": {k: round(v, 1) for k, v in radii.items()},
               "open_quadrant": open_q},
        target=targets,
        tolerance=None,
        margin=1.0 if ok else -1.0,
    )


def probe_gradient_smooth(cue: dict, ctx: ProbeContext) -> CueResult:
    rect = denorm_rect(cue["rect"], ctx.img.width, ctx.img.height)
    strip = luma(crop(ctx.img.rgb, rect))
    axis = 1 if cue.get("axis", "x") == "x" else 0
    result = perceive.banding_score(strip, axis=axis)
    ok = not result["banded"]
    return _res(
        cue,
        status="pass" if ok else "fail",
        measured=True,
        value=result,
        target="smooth ramp (no plateau/step banding)",
        tolerance=None,
        margin=round(1.0 - result["deficit_ratio"], 4),
    )


def probe_attest(cue: dict, ctx: ProbeContext) -> CueResult:
    note = cue.get("note", "")
    if not note:
        return _res(cue, status="error", measured=False,
                    note="attest cue requires a note naming who/what attested")
    return _res(
        cue,
        status="attested",
        measured=False,
        value=None,
        target=cue.get("target"),
        note=note,
    )


PROBES: dict = {
    "aspect": probe_aspect,
    "color_at": probe_color_at,
    "region_color": probe_region_color,
    "band_thickness": probe_band_thickness,
    "band_edge": probe_band_edge,
    "gutter": probe_gutter,
    "region_present": probe_region_present,
    "region_absent": probe_region_absent,
    "count_regions": probe_count_regions,
    "ssim_region": probe_ssim_region,
    "shape_class": probe_shape_class,
    "gradient_smooth": probe_gradient_smooth,
    "attest": probe_attest,
}


def run_cue(cue: dict, ctx: ProbeContext) -> CueResult:
    probe = cue.get("probe")
    fn: Optional[Callable] = PROBES.get(probe)
    if fn is None:
        return _res(cue, status="error", measured=False,
                    note=f"unknown probe '{probe}' — cue not proven")
    try:
        return fn(cue, ctx)
    except KeyError as exc:
        return _res(cue, status="error", measured=False,
                    note=f"cue missing required field {exc}")
    except Exception as exc:  # deliberate: an errored probe must surface, not crash the run
        return _res(cue, status="error", measured=False, note=f"probe error: {exc}")
