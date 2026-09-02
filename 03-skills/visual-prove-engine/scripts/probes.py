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
  flip_region       — FLIP (or flip-lite) mean error of a rect crop vs an asset
  dreamsim_region   — DreamSim distance vs an asset (Spirit / NVS; optional)
  saliency_region   — spectral-residual mass inside a rect
  ocr_text          — recognized string vs expected (optional without tesseract)
  mesh_asset        — glTF/GLB audit (fail closed on Error)
  geometric_consistency — >=2 pinned views; never a single-still 3D pass
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

PROBE_DEFAULT_ALTITUDE = {
    "aspect": "A",
    "color_at": "A",
    "region_color": "A",
    "band_thickness": "A",
    "band_edge": "A",
    "gutter": "A",
    "region_present": "A",
    "region_absent": "A",
    "count_regions": "A",
    "ssim_region": "A",
    "shape_class": "A",
    "gradient_smooth": "A",
    "attest": "A",
    "ocr_text": "A",
    "flip_region": "B",
    "dreamsim_region": "C",
    "saliency_region": "C",
    "mesh_asset": "E",
    "geometric_consistency": "E",
}


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
    kw.setdefault(
        "altitude",
        cue.get("altitude") or PROBE_DEFAULT_ALTITUDE.get(cue.get("probe"), "A"),
    )
    kw.setdefault("optional", bool(cue.get("optional", False)))
    return CueResult(
        id=cue.get("id"),
        name=cue.get("name", str(cue.get("id"))),
        probe=cue.get("probe", "?"),
        **kw,
    )


def _skip_or_error(cue: dict, reason: str, degraded: bool = True) -> CueResult:
    if cue.get("optional", False):
        return _res(cue, status="skipped", measured=False, note=reason, degraded=degraded)
    return _res(cue, status="error", measured=False, note=reason, degraded=degraded)


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


def _crop_vs_asset(cue: dict, ctx: ProbeContext):
    rect = denorm_rect(cue["rect"], ctx.img.width, ctx.img.height)
    region = crop(ctx.img.rgb, rect)
    asset_path = ctx.resolve(cue["asset"])
    if not asset_path.exists():
        return None, None, f"asset missing: {asset_path}"
    asset = _core.load_image(asset_path)
    asset_rgb = asset.rgb
    if "asset_rect" in cue:
        asset_rgb = crop(asset_rgb, denorm_rect(cue["asset_rect"], asset.width, asset.height))
    asset_rgb = resize_rgb(asset_rgb, region.shape[1], region.shape[0])
    return region, asset_rgb, None


def probe_flip_region(cue: dict, ctx: ProbeContext) -> CueResult:
    from . import flip_metric
    region, asset_rgb, err = _crop_vs_asset(cue, ctx)
    if err:
        return _res(cue, status="error", measured=False, note=err)
    result = flip_metric.flip_map(asset_rgb, region)
    max_mean = float(cue.get("max_mean", 0.15))
    mean = result["mean"]
    margin = 1.0 - mean / max_mean if max_mean > 0 else (1.0 if mean == 0 else -1.0)
    return _res(
        cue,
        status="pass" if mean <= max_mean else "fail",
        measured=True,
        value={"mean": mean, "median": result["median"], "mad": result["mad"],
               "p95": result["p95"], "backend": result["backend"]},
        target=f"mean<={max_mean}",
        tolerance=None,
        margin=round(float(margin), 4),
        degraded=result["backend"] != "nvidia-flip",
        note=f"FLIP backend {result['backend']}",
    )


def probe_dreamsim_region(cue: dict, ctx: ProbeContext) -> CueResult:
    from . import midlevel
    region, asset_rgb, err = _crop_vs_asset(cue, ctx)
    if err:
        return _res(cue, status="error", measured=False, note=err)
    dist = midlevel.distance(region, asset_rgb)
    if dist is None:
        return _skip_or_error(
            cue,
            "DreamSim/torch unavailable — not a Literal gutter metric; "
            "install dreamsim to measure Spirit/NVS similarity",
        )
    max_dist = float(cue.get("max", 0.25))
    margin = 1.0 - dist / max_dist if max_dist > 0 else (1.0 if dist == 0 else -1.0)
    return _res(
        cue,
        status="pass" if dist <= max_dist else "fail",
        measured=True,
        value=round(dist, 4),
        target=f"<={max_dist}",
        tolerance=None,
        margin=round(float(margin), 4),
        note="DreamSim is foreground-biased; chrome-frame diffs can hide",
    )


def probe_saliency_region(cue: dict, ctx: ProbeContext) -> CueResult:
    from . import saliency
    rect = denorm_rect(cue["rect"], ctx.img.width, ctx.img.height)
    sal = saliency.spectral_residual(luma(ctx.img.rgb))
    mass = saliency.region_mass(sal, rect)
    min_mass = float(cue.get("min_mass", 0.05))
    value = mass["mass_fraction"]
    margin = (value - min_mass) / max(1e-9, 1.0 - min_mass)
    return _res(
        cue,
        status="pass" if value >= min_mass else "fail",
        measured=True,
        value=mass,
        target=f"mass_fraction>={min_mass}",
        tolerance=None,
        margin=round(float(margin), 4),
        note="spectral-residual floor (edge-biased); not UEyes gaze",
    )


def probe_ocr_text(cue: dict, ctx: ProbeContext) -> CueResult:
    from . import ocr_probe
    if "rect" in cue:
        rect = denorm_rect(cue["rect"], ctx.img.width, ctx.img.height)
        region = crop(ctx.img.rgb, rect)
    else:
        region = ctx.img.rgb
    text = ocr_probe.read_text(region, lang=str(cue.get("lang", "eng")))
    if text is None:
        return _skip_or_error(cue, "tesseract/pytesseract unavailable — text not measured")
    expect = str(cue.get("expect") or cue.get("target") or "")
    if not expect:
        return _res(cue, status="error", measured=False, note="ocr_text requires expect/target")
    got = " ".join(text.split())
    want = " ".join(expect.split())
    ok = want.lower() in got.lower() if cue.get("contains", True) else got.lower() == want.lower()
    return _res(
        cue,
        status="pass" if ok else "fail",
        measured=True,
        value=got,
        target=want,
        tolerance=None,
        margin=1.0 if ok else -1.0,
    )


def probe_mesh_asset(cue: dict, ctx: ProbeContext) -> CueResult:
    from . import mesh
    asset_path = ctx.resolve(cue["asset"])
    report = mesh.audit(asset_path)
    ok = report["status"] == "pass"
    return _res(
        cue,
        status="pass" if ok else "fail",
        measured=True,
        value={"errors": report["errors"], "stats": report["stats"], "backend": report["backend"]},
        target="no Error-level mesh issues",
        tolerance=None,
        margin=1.0 if ok else -1.0,
        degraded=not str(report["backend"]).startswith("gltf-validator"),
        note=f"mesh backend {report['backend']}",
    )


def probe_geometric_consistency(cue: dict, ctx: ProbeContext) -> CueResult:
    from . import geometry
    views = cue.get("views") or []
    resolved = []
    for v in views:
        p = ctx.resolve(v)
        resolved.append(str(p))
    if len(resolved) < 2:
        return _res(
            cue, status="error", measured=False,
            note="geometric_consistency needs >=2 pinned views; a single still is not a 3D pass",
        )
    report = geometry.consistency(
        resolved,
        min_peak=float(cue.get("min_peak", 0.08)),
        min_ssim=float(cue.get("min_ssim", 0.25)),
    )
    if report["status"] == "error":
        return _res(cue, status="error", measured=False, note=report.get("note", "geometry error"))
    ok = report["status"] == "pass"
    return _res(
        cue,
        status="pass" if ok else "fail",
        measured=True,
        value=report,
        target=f"pairwise peak>={cue.get('min_peak', 0.08)} and ssim>={cue.get('min_ssim', 0.25)}",
        tolerance=None,
        margin=1.0 if ok else -1.0,
        degraded="vggt" not in report.get("backend", ""),
        note=f"geometry backend {report.get('backend')}",
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
    "flip_region": probe_flip_region,
    "dreamsim_region": probe_dreamsim_region,
    "saliency_region": probe_saliency_region,
    "ocr_text": probe_ocr_text,
    "mesh_asset": probe_mesh_asset,
    "geometric_consistency": probe_geometric_consistency,
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
