"""
_core.py — shared primitives for the visual prove engine.

Design constraints:
- Hard dependencies: numpy + Pillow only. cv2 / scipy / skimage are optional
  accelerators; their absence degrades loudly (recorded in `deps_report()`),
  never silently.
- Everything deterministic: no wall-clock in metrics, no unseeded randomness.
- True CIE Lab (L 0..100) so delta-E tolerances mean standard CIE76 units.
  (Note: visual-qa-toolkit's cv2-uint8 Lab inflates L by 255/100; do not mix
  tolerance values between the two without rescaling.)
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import numpy as np
from PIL import Image

ENGINE_VERSION = "vqa/1.1"

# ── Optional dependencies ────────────────────────────────────

try:  # pragma: no cover - environment dependent
    import cv2  # type: ignore
except Exception:  # pragma: no cover
    cv2 = None

try:  # pragma: no cover
    from scipy import ndimage as _ndimage  # type: ignore
except Exception:  # pragma: no cover
    _ndimage = None


def deps_report() -> dict:
    """Which optional deps are present, and what degrades without them."""
    import shutil

    flip_nvidia = False
    try:
        import flip_evaluator  # noqa: F401
        flip_nvidia = True
    except Exception:
        pass
    dreamsim = False
    try:
        import dreamsim  # noqa: F401
        import torch  # noqa: F401
        dreamsim = True
    except Exception:
        pass
    tesseract = shutil.which("tesseract") is not None
    try:
        import pytesseract  # noqa: F401
        tesseract = True
    except Exception:
        pass
    gltf_validator = shutil.which("gltf-validator") is not None
    vggt = False
    try:
        import vggt  # noqa: F401
        vggt = True
    except Exception:
        pass

    degraded = []
    if cv2 is None and _ndimage is None:
        degraded.append(
            "connected-components falls back to pure python (slow on >2MP; inputs are downscaled for labeling)"
        )
    if cv2 is None:
        degraded.append("optical flow (motion jerk via flow) unavailable; frame-delta jerk still runs")
    if not flip_nvidia:
        degraded.append("FLIP uses flip-lite (CSF+HyAB+edges), not nvidia-flip")
    if not dreamsim:
        degraded.append("DreamSim unavailable — dreamsim_region skips if optional, else errors")
    if not tesseract:
        degraded.append("OCR unavailable — ocr_text skips if optional, else errors")
    if not gltf_validator:
        degraded.append("gltf-validator absent — mesh audit uses stdlib parser (still fail-closed on NaN)")
    if not vggt:
        degraded.append("VGGT/DUSt3R absent — geometric_consistency uses phase-correlation only; never a single-still 3D pass")
    py_pw = False
    try:
        import playwright  # noqa: F401
        py_pw = True
    except Exception:
        pass
    if not py_pw:
        degraded.append(
            "Playwright absent — `vqa capture` needs python-playwright or cwd node_modules; "
            "prove still accepts an existing PNG"
        )

    return {
        "numpy": True,
        "pillow": True,
        "cv2": cv2 is not None,
        "scipy": _ndimage is not None,
        "ffmpeg": shutil.which("ffmpeg") is not None,
        "nvidia_flip": flip_nvidia,
        "dreamsim": dreamsim,
        "tesseract": tesseract,
        "gltf_validator": gltf_validator,
        "vggt": vggt,
        "playwright": py_pw,
        "degraded": degraded,
    }


# ── Image IO ─────────────────────────────────────────────────

@dataclass
class Img:
    path: Optional[Path]
    rgb: np.ndarray  # (H, W, 3) uint8
    width: int
    height: int

    @property
    def gray(self) -> np.ndarray:
        return luma(self.rgb)


def load_image(path: str | Path) -> Img:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"image not found: {p}")
    pil = Image.open(p).convert("RGB")
    rgb = np.asarray(pil, dtype=np.uint8)
    return Img(path=p, rgb=rgb, width=pil.width, height=pil.height)


def from_array(rgb: np.ndarray) -> Img:
    rgb = np.ascontiguousarray(rgb.astype(np.uint8))
    h, w = rgb.shape[:2]
    return Img(path=None, rgb=rgb, width=w, height=h)


def save_image(rgb: np.ndarray, path: str | Path) -> Path:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(rgb.astype(np.uint8), "RGB").save(p, format="PNG")
    return p


def luma(rgb: np.ndarray) -> np.ndarray:
    """Rec.709 luma, float64 (H, W)."""
    a = rgb.astype(np.float64)
    return 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]


def resize_rgb(rgb: np.ndarray, width: int, height: int) -> np.ndarray:
    pil = Image.fromarray(rgb.astype(np.uint8), "RGB").resize(
        (int(width), int(height)), Image.LANCZOS
    )
    return np.asarray(pil, dtype=np.uint8)


# ── Color: sRGB → CIE Lab (D65), CIE76 delta-E ───────────────

_M_SRGB_XYZ = np.array(
    [
        [0.4124564, 0.3575761, 0.1804375],
        [0.2126729, 0.7151522, 0.0721750],
        [0.0193339, 0.1191920, 0.9503041],
    ]
)
_D65 = np.array([0.95047, 1.0, 1.08883])


def srgb_to_lab(rgb: np.ndarray) -> np.ndarray:
    """rgb: (..., 3) 0..255 → Lab (..., 3) with L in 0..100."""
    c = np.asarray(rgb, dtype=np.float64) / 255.0
    lin = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    xyz = lin @ _M_SRGB_XYZ.T
    t = xyz / _D65
    d = 6.0 / 29.0
    f = np.where(t > d ** 3, np.cbrt(t), t / (3 * d * d) + 4.0 / 29.0)
    L = 116.0 * f[..., 1] - 16.0
    a = 500.0 * (f[..., 0] - f[..., 1])
    b = 200.0 * (f[..., 1] - f[..., 2])
    return np.stack([L, a, b], axis=-1)


def delta_e76(c1, c2) -> float:
    """CIE76 delta-E between two RGB colors (tuples or arrays, 0..255)."""
    lab1 = srgb_to_lab(np.asarray(c1, dtype=np.float64))
    lab2 = srgb_to_lab(np.asarray(c2, dtype=np.float64))
    return float(np.linalg.norm(lab1 - lab2))


def delta_e_map(rgb_a: np.ndarray, rgb_b: np.ndarray) -> np.ndarray:
    """Per-pixel CIE76 delta-E map between two same-shape RGB images."""
    if rgb_a.shape != rgb_b.shape:
        raise ValueError(f"shape mismatch: {rgb_a.shape} vs {rgb_b.shape}")
    return np.linalg.norm(srgb_to_lab(rgb_a) - srgb_to_lab(rgb_b), axis=-1)


def hex_to_rgb(hex_str: str) -> tuple:
    h = hex_str.lstrip("#")
    if len(h) == 3:
        h = "".join(ch * 2 for ch in h)
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb) -> str:
    r, g, b = (int(round(float(v))) for v in rgb)
    return "#{:02X}{:02X}{:02X}".format(r, g, b)


# ── SSIM (pure numpy, uniform window) ────────────────────────

def _box_mean(img: np.ndarray, win: int) -> np.ndarray:
    """Mean filter via integral image; 'valid' output."""
    ii = np.cumsum(np.cumsum(img.astype(np.float64), axis=0), axis=1)
    ii = np.pad(ii, ((1, 0), (1, 0)), mode="constant")
    s = ii[win:, win:] - ii[:-win, win:] - ii[win:, :-win] + ii[:-win, :-win]
    return s / float(win * win)


def ssim(gray_a: np.ndarray, gray_b: np.ndarray, win: int = 8):
    """
    Structural similarity on grayscale float arrays (0..255 scale).
    Returns (mean_ssim, ssim_map). Deterministic; no external deps.
    """
    if gray_a.shape != gray_b.shape:
        raise ValueError(f"shape mismatch: {gray_a.shape} vs {gray_b.shape}")
    h, w = gray_a.shape
    win = max(2, min(win, h, w))
    a = gray_a.astype(np.float64)
    b = gray_b.astype(np.float64)
    c1 = (0.01 * 255.0) ** 2
    c2 = (0.03 * 255.0) ** 2
    mu_a = _box_mean(a, win)
    mu_b = _box_mean(b, win)
    var_a = np.clip(_box_mean(a * a, win) - mu_a * mu_a, 0.0, None)
    var_b = np.clip(_box_mean(b * b, win) - mu_b * mu_b, 0.0, None)
    cov = _box_mean(a * b, win) - mu_a * mu_b
    num = (2 * mu_a * mu_b + c1) * (2 * cov + c2)
    den = (mu_a ** 2 + mu_b ** 2 + c1) * (var_a + var_b + c2)
    smap = num / den
    return float(smap.mean()), smap


# ── Change mask (pixelmatch-style semantics) ─────────────────

def change_mask(
    rgb_a: np.ndarray,
    rgb_b: np.ndarray,
    threshold_de: float = 4.0,
    erode_aa: bool = True,
) -> np.ndarray:
    """
    Boolean per-pixel change mask. Perceptual (delta-E) threshold, then an
    optional single-pixel erosion so anti-aliased 1px edges do not count as
    change (the AA-tolerance idea from pixelmatch, done morphologically).
    """
    de = delta_e_map(rgb_a, rgb_b)
    mask = de > threshold_de
    if erode_aa and mask.any():
        mask = _erode3(mask)
    return mask


def _erode3(mask: np.ndarray) -> np.ndarray:
    """3x3 binary erosion, pure numpy."""
    p = np.pad(mask, 1, mode="constant", constant_values=False)
    out = p[1:-1, 1:-1].copy()
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            out &= p[1 + dy : p.shape[0] - 1 + dy, 1 + dx : p.shape[1] - 1 + dx]
    return out


def _dilate3(mask: np.ndarray) -> np.ndarray:
    p = np.pad(mask, 1, mode="constant", constant_values=False)
    out = p[1:-1, 1:-1].copy()
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            out |= p[1 + dy : p.shape[0] - 1 + dy, 1 + dx : p.shape[1] - 1 + dx]
    return out


# ── Connected components (scipy → cv2 → fallback) ────────────

def label_components(mask: np.ndarray):
    """
    Label a boolean mask. Returns (labels int32 array, count).
    Prefers scipy, then cv2; the pure-python fallback downscales large masks
    for tractability (recorded by the caller via deps_report()).
    """
    if _ndimage is not None:
        labels, n = _ndimage.label(mask)
        return labels.astype(np.int32), int(n)
    if cv2 is not None:
        n, labels = cv2.connectedComponents(mask.astype(np.uint8), connectivity=4)
        return labels.astype(np.int32), int(n) - 1
    return _label_fallback(mask)


def _label_fallback(mask: np.ndarray):
    h, w = mask.shape
    scale = 1
    m = mask
    while m.shape[0] * m.shape[1] > 2_000_000:
        scale *= 2
        m = mask[::scale, ::scale]
    labels_small = np.zeros(m.shape, dtype=np.int32)
    current = 0
    hh, ww = m.shape
    for sy in range(hh):
        row = m[sy]
        for sx in range(ww):
            if row[sx] and labels_small[sy, sx] == 0:
                current += 1
                stack = [(sy, sx)]
                while stack:
                    y, x = stack.pop()
                    if y < 0 or y >= hh or x < 0 or x >= ww:
                        continue
                    if not m[y, x] or labels_small[y, x] != 0:
                        continue
                    labels_small[y, x] = current
                    stack.extend(((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)))
    if scale == 1:
        return labels_small, current
    # Upscale nearest to original shape.
    labels = np.repeat(np.repeat(labels_small, scale, axis=0), scale, axis=1)
    labels = labels[:h, :w]
    return labels.astype(np.int32), current


# ── Geometry helpers ─────────────────────────────────────────

def denorm_rect(rect_frac, width: int, height: int):
    """[x, y, w, h] fractions → integer pixel rect, clamped to canvas."""
    x, y, w, h = rect_frac
    px = int(round(x * width))
    py = int(round(y * height))
    pw = max(1, int(round(w * width)))
    ph = max(1, int(round(h * height)))
    px = min(max(px, 0), width - 1)
    py = min(max(py, 0), height - 1)
    pw = min(pw, width - px)
    ph = min(ph, height - py)
    return px, py, pw, ph


def crop(rgb: np.ndarray, rect_px) -> np.ndarray:
    x, y, w, h = rect_px
    return rgb[y : y + h, x : x + w]


def sample_disc(rgb: np.ndarray, x: int, y: int, radius: int = 3):
    """Mean color in a small square neighborhood (AA-noise robust)."""
    h, w = rgb.shape[:2]
    x0, x1 = max(0, x - radius), min(w, x + radius + 1)
    y0, y1 = max(0, y - radius), min(h, y + radius + 1)
    region = rgb[y0:y1, x0:x1].reshape(-1, 3).astype(np.float64)
    return tuple(float(v) for v in region.mean(axis=0))


def estimate_background(rgb: np.ndarray) -> tuple:
    """Most common quantized color (5-bit/channel), returned as exact mean of that bin."""
    q = (rgb >> 3).reshape(-1, 3)
    keys = (q[:, 0].astype(np.int64) << 10) | (q[:, 1].astype(np.int64) << 5) | q[:, 2].astype(np.int64)
    vals, counts = np.unique(keys, return_counts=True)
    top = vals[int(np.argmax(counts))]
    sel = keys == top
    mean = rgb.reshape(-1, 3)[sel].astype(np.float64).mean(axis=0)
    return tuple(float(v) for v in mean)


def foreground_mask(rgb: np.ndarray, background, tol_de: float = 6.0) -> np.ndarray:
    """Pixels whose delta-E from the background exceeds tol."""
    bg = np.asarray(background, dtype=np.float64).reshape(1, 1, 3)
    de = np.linalg.norm(srgb_to_lab(rgb) - srgb_to_lab(bg), axis=-1)
    return de > tol_de


# ── Capture manifest ─────────────────────────────────────────

CAPTURE_REQUIRED = ("viewport", "dpr", "format")
# Optional provenance. Missing values are warnings, not unverified.
# Existing LCARS manifests without `renderer` must stay verified.
CAPTURE_WARN_FIELDS = ("renderer", "rng_frozen")


def find_manifest(image_path: Path) -> Optional[Path]:
    cand = image_path.with_suffix(image_path.suffix + ".capture.json")
    if cand.exists():
        return cand
    cand2 = image_path.with_suffix(".capture.json")
    return cand2 if cand2.exists() else None


def verify_capture(image_path: str | Path, manifest_path: Optional[str | Path] = None) -> dict:
    """
    Verify a capture against its manifest. Returns a dict with
    status: 'verified' | 'unverified', and reasons. Never raises for a
    missing manifest — unverified is a first-class, reportable state.
    """
    image_path = Path(image_path)
    result: dict[str, Any] = {
        "image": str(image_path), "status": "unverified", "reasons": [], "warnings": [],
    }
    if not image_path.exists():
        result["reasons"].append("image missing")
        return result
    with Image.open(image_path) as im:
        fmt = (im.format or "").lower()
        width, height = im.size
    result["width"], result["height"], result["format"] = width, height, fmt
    if fmt != "png":
        result["reasons"].append(f"lossy or non-png format: {fmt} (banding/edge judgments unsafe)")
    mp = Path(manifest_path) if manifest_path else find_manifest(image_path)
    if mp is None:
        result["reasons"].append("no capture manifest (*.capture.json) — provenance unknown")
        return result
    try:
        manifest = json.loads(mp.read_text(encoding="utf-8"))
    except Exception as exc:
        result["reasons"].append(f"manifest unreadable: {exc}")
        return result
    result["manifest"] = str(mp)
    missing = [k for k in CAPTURE_REQUIRED if k not in manifest]
    if missing:
        result["reasons"].append(f"manifest missing fields: {missing}")
    vp = manifest.get("viewport") or {}
    dpr = float(manifest.get("dpr", 1) or 1)
    exp_w = int(round(float(vp.get("width", 0)) * dpr))
    exp_h = int(round(float(vp.get("height", 0)) * dpr))
    if exp_w and exp_h and (exp_w, exp_h) != (width, height):
        result["reasons"].append(
            f"dimensions {width}x{height} != viewport*dpr {exp_w}x{exp_h}"
        )
    if str(manifest.get("format", "")).lower() not in ("png", ""):
        result["reasons"].append("manifest declares non-png capture")
    if not manifest.get("frozen", False):
        result["reasons"].append("animations/clock not declared frozen (motion smear risk in stills)")
    if "renderer" not in manifest:
        result["warnings"].append(
            "manifest has no renderer (swiftshader|metal|vulkan|webgl|...) — "
            "GPU goldens are not byte-stable; missing renderer is a warning, not unverified"
        )
    else:
        result["renderer"] = manifest.get("renderer")
    if "rng_frozen" not in manifest:
        result["warnings"].append("manifest has no rng_frozen declaration")
    else:
        result["rng_frozen"] = manifest.get("rng_frozen")
    if "assistance" in manifest:
        result["assistance"] = manifest.get("assistance")
    if not result["reasons"]:
        result["status"] = "verified"
        result["meta"] = {
            k: manifest.get(k)
            for k in ("url", "commit", "tool", "time", "assistance", "reduced_motion")
            if k in manifest
        }
    return result


# ── Result model ─────────────────────────────────────────────

@dataclass
class CueResult:
    id: Any
    name: str
    probe: str
    status: str  # pass | fail | attested | error | skipped
    measured: bool
    value: Any = None
    target: Any = None
    tolerance: Any = None
    margin: Optional[float] = None  # >0 inside tolerance, <0 outside (normalized)
    note: str = ""
    evidence: list = field(default_factory=list)
    altitude: str = "A"
    optional: bool = False
    degraded: bool = False

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "probe": self.probe,
            "status": self.status,
            "measured": self.measured,
            "value": self.value,
            "target": self.target,
            "tolerance": self.tolerance,
            "margin": self.margin,
            "note": self.note,
            "evidence": self.evidence,
            "altitude": self.altitude,
            "optional": self.optional,
            "degraded": self.degraded,
        }


def summarize_cues(
    results: list,
    capture_status: str,
    min_coverage: float = 0.8,
    uncued_residuals: Optional[list] = None,
    required_altitudes: Optional[list] = None,
) -> dict:
    # Optional skips do not count toward coverage (they are not in the contract).
    contract = [r for r in results if not (r.status == "skipped" and r.optional)]
    skipped = [r for r in results if r.status == "skipped"]
    measured = [r for r in contract if r.measured]
    measured_pass = [r for r in measured if r.status == "pass"]
    measured_fail = [r for r in measured if r.status == "fail"]
    errors = [r for r in contract if r.status == "error"]
    attested = [r for r in contract if r.status == "attested"]
    total = len(contract)
    coverage = (len(measured) / total) if total else 0.0
    score = (len(measured_pass) / len(measured)) if measured else 0.0
    reasons = []
    if measured_fail:
        verdict = "fail" if len(measured_fail) > len(measured) / 2 else "partial"
        reasons.append(f"{len(measured_fail)} measured cue(s) failing")
    elif errors:
        verdict = "partial"
        reasons.append(f"{len(errors)} cue(s) errored (not proven)")
    else:
        verdict = "matches"
    if verdict == "matches" and coverage < min_coverage:
        verdict = "partial"
        reasons.append(
            f"measured coverage {coverage:.0%} below floor {min_coverage:.0%} "
            f"({len(attested)} attested cue(s) do not count as proof)"
        )
    if verdict == "matches" and capture_status != "verified":
        verdict = "partial"
        reasons.append("capture unverified — matches verdict requires a verified capture manifest")
    altitudes_in_contract = sorted({r.altitude for r in contract if r.altitude})
    altitude_coverage = {}
    for alt in altitudes_in_contract:
        at = [r for r in contract if r.altitude == alt]
        m_at = [r for r in at if r.measured]
        altitude_coverage[alt] = {
            "cues": len(at),
            "measured": len(m_at),
            "pass": sum(1 for r in m_at if r.status == "pass"),
            "fail": sum(1 for r in m_at if r.status == "fail"),
        }
    if required_altitudes:
        missing_req = [a for a in required_altitudes if a not in altitudes_in_contract]
        if missing_req:
            reasons.append(f"required altitudes not in contract: {missing_req}")
            if verdict == "matches":
                verdict = "partial"
    residuals = list(uncued_residuals or [])
    if residuals:
        reasons.append(
            f"{len(residuals)} uncued residual(s) named — matches at contracted altitudes "
            "does not cover these zones"
        )
    margins = [r.margin for r in measured if r.margin is not None]
    return {
        "verdict": verdict,
        "verdict_reasons": reasons,
        "cues_total": total,
        "measured_total": len(measured),
        "measured_pass": len(measured_pass),
        "measured_fail": len(measured_fail),
        "attested": len(attested),
        "errors": len(errors),
        "skipped_optional": sum(1 for r in skipped if r.optional),
        "coverage": round(coverage, 4),
        "score": round(score, 4),
        "mean_margin": round(float(np.mean(margins)), 4) if margins else None,
        "capture": capture_status,
        "altitudes_in_contract": altitudes_in_contract,
        "altitude_coverage": altitude_coverage,
        "uncued_residuals": residuals,
    }


def write_json(data: dict, path: str | Path) -> Path:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    return p


def rel_margin(value: float, target: float, tol: float) -> float:
    """Normalized margin: 1 at exact target, 0 at tolerance edge, <0 outside."""
    if tol <= 0:
        return 1.0 if value == target else -1.0
    return 1.0 - abs(value - target) / tol
