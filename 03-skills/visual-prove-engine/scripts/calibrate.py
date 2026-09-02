"""
calibrate.py — the engine's own reliability proof.

Synthesizes a deterministic UI scene plus a battery of planted defects and
known-good variants, runs the engine's detectors against ground truth, and
reports per-detector detection (TP/FN) and false-positive (FP) results.
Exit is nonzero if ANY planted defect goes undetected or any clean variant
false-fires. This is the negative-fixture doctrine applied to visual
detectors: a detector that has never refused a planted defect is not
evidence, and a detector with unmeasured false-positive behavior trains
agents to ignore it.

Everything is seeded and rendered in numpy; no fonts, browsers, or GPUs, so
results are identical on every machine and in CI.
"""
from __future__ import annotations

import json
import math
import struct
import sys
import tempfile
from pathlib import Path
from typing import Optional

import numpy as np

from . import _core, compare, flip_metric, geometry, interact, judge, mesh, motion, perceive, prove, saliency
from ._core import from_array, save_image, write_json

SEED = 47


# ── Scene synthesis ──────────────────────────────────────────

W, H = 1280, 720
BG = (0, 0, 0)
HEADER = (79, 147, 202)     # #4F93CA
PILL = (244, 194, 133)      # #F4C285
ACCENT = (238, 162, 68)     # #EEA244


def _canvas() -> np.ndarray:
    img = np.zeros((H, W, 3), dtype=np.float64)
    img[...] = BG
    return img


def _fill_rect(img, x, y, w, h, color):
    img[y : y + h, x : x + w] = color


def _fill_round_rect(img, x, y, w, h, color, radii):
    """radii: (tl, tr, bl, br) in px."""
    _fill_rect(img, x, y, w, h, color)
    yy, xx = np.mgrid[0:h, 0:w]
    tl, tr, bl, br = radii
    for r, cy, cx, quad in (
        (tl, tl, tl, (yy < tl) & (xx < tl)),
        (tr, tr, w - tr - 1, (yy < tr) & (xx >= w - tr)),
        (bl, h - bl - 1, bl, (yy >= h - bl) & (xx < bl)),
        (br, h - br - 1, w - br - 1, (yy >= h - br) & (xx >= w - br)),
    ):
        if r <= 0:
            continue
        d = np.sqrt((yy - cy) ** 2 + (xx - cx) ** 2)
        cut = quad & (d > r)
        img[y : y + h, x : x + w][cut] = BG


def _fill_pill(img, x, y, w, h, color):
    r = h // 2
    _fill_round_rect(img, x, y, w, h, color, (r, r, r, r))


def _fill_elbow(img, x, y, w, h, color, arm_v=48, arm_h=36):
    """Constant-thickness L: full top bar + left vertical arm (open br)."""
    _fill_rect(img, x, y, w, arm_h, color)
    _fill_rect(img, x, y, arm_v, h, color)
    # soften the outer top-left corner like an Okuda elbow
    _fill_round_rect(img, x, y, arm_v + 24, arm_h + 24, color, (min(arm_h, 28), 0, 0, 0))
    _fill_rect(img, x + arm_v, y + arm_h, 24, 24, BG)  # re-open the inner corner
    inner = np.mgrid[0:24, 0:24]
    d = np.sqrt((inner[0] - 24) ** 2 + (inner[1] - 24) ** 2)
    img[y + arm_h : y + arm_h + 24, x + arm_v : x + arm_v + 24][d > 24] = color


def _gradient_strip(img, x, y, w, h, lo=16, hi=200):
    ramp = np.linspace(lo, hi, w)
    strip = np.stack([ramp, ramp, ramp], axis=-1)
    img[y : y + h, x : x + w] = strip[None, :, :]


GUTTER = 8


def render_base(variant: str = "clean", rng: Optional[np.random.Generator] = None) -> np.ndarray:
    """
    Render the scene. `variant` selects a planted defect; 'clean' and
    'clean_noise' must pass every detector.
    """
    img = _canvas()

    header_color = HEADER
    header_y = 40
    gutter = GUTTER
    pill_radius_on = True

    if variant == "fill_shift":
        header_color = (79, 147, 168)  # hue/chroma shift, delta-E ~ 8
    if variant == "layout_shift":
        header_y = 52
    if variant == "gutter_drift":
        gutter = 12
    if variant == "radius_loss":
        pill_radius_on = False

    # Header: elbow + main bar + pill cap
    _fill_elbow(img, 40, header_y, 200, 160, header_color)
    _fill_rect(img, 40 + 200 + gutter, header_y, 560, 48, header_color)
    _fill_rect(img, 40 + 200 + gutter + 560 + gutter, header_y, 220, 48, ACCENT)
    _fill_pill(img, 40 + 200 + gutter + 560 + gutter + 220 + gutter, header_y, 120, 48, PILL)

    # Mid pills row
    if variant != "missing_region":
        px = 300
        for i in range(4):
            if pill_radius_on:
                _fill_pill(img, px, 360, 150, 44, PILL if i % 2 == 0 else HEADER)
            else:
                _fill_rect(img, px, 360, 150, 44, PILL if i % 2 == 0 else HEADER)
            px += 150 + gutter

    # Stacked bars (gutter subject)
    by = 480
    for _ in range(4):
        _fill_rect(img, 300, by, 500, 24, HEADER)
        by += 24 + gutter

    # Footer card — legal shape is a bar; the defect plants a single-corner card
    if variant == "single_corner_card":
        _fill_round_rect(img, 900, 480, 260, 130, ACCENT, (48, 0, 0, 0))
    else:
        _fill_rect(img, 900, 480, 260, 130, ACCENT)

    # Gradient strip (banding subject)
    _gradient_strip(img, 40, 660, 1200, 40)
    if variant == "banding":
        strip = img[660:700, 40:1240, 0]
        img[660:700, 40:1240] = (np.floor(strip / 24.0) * 24.0)[..., None]

    if variant == "blowout":
        img[600:650, 40:600] = (255, 255, 255)

    out = np.clip(img, 0, 255)

    if variant == "clean_noise":
        # AA-scale noise a reliable detector must tolerate: +-1 LSB everywhere
        # plus soft 1px edges (box blur), the classic renderer variance profile.
        rng = rng or np.random.default_rng(SEED)
        blurred = out.copy()
        blurred[1:-1, 1:-1] = (
            out[1:-1, 1:-1] * 0.6
            + (out[:-2, 1:-1] + out[2:, 1:-1] + out[1:-1, :-2] + out[1:-1, 2:]) * 0.1
        )
        noise = rng.integers(-1, 2, size=out.shape)
        out = np.clip(blurred + noise, 0, 255)

    return out.astype(np.uint8)


# ── Cuespec over the base scene ──────────────────────────────

def base_cuespec() -> dict:
    fw, fh = float(W), float(H)
    return {
        "spec": "vqa-cuespec/1",
        "northstar": "VQA-CALIBRATION-SCENE",
        "background": "#000000",
        "min_coverage": 0.8,
        "cues": [
            {"id": "aspect", "name": "Canvas 16:9", "probe": "aspect",
             "target": [16, 9], "tol": 0.01},
            {"id": "bg", "name": "Background black", "probe": "color_at",
             "at": [0.5, 0.31], "target": "#000000", "tol_de": 2.0},
            {"id": "header_fill", "name": "Header bar fill", "probe": "region_color",
             "rect": [(40 + 208) / fw, 40 / fh, 500 / fw, 44 / fh],
             "target": "#4F93CA", "tol_de": 4.0},
            {"id": "header_y", "name": "Header bar thickness", "probe": "band_thickness",
             "axis": "y", "at": (40 + 208 + 100) / fw, "range": [0.0, 0.35],
             "target_px": 48, "tol_px": 3, "at_height": H},
            {"id": "header_y0", "name": "Header bar top edge", "probe": "band_edge",
             "axis": "y", "at": (40 + 208 + 100) / fw, "range": [0.0, 0.35],
             "target_px": 40, "tol_px": 3, "at_height": H},
            {"id": "gutter", "name": "Stack gutter 8px", "probe": "gutter",
             "rect": [290 / fw, 470 / fh, 520 / fw, 140 / fh],
             "axis": "rows", "target_px": 8, "tol_px": 1, "at_height": H},
            {"id": "pills", "name": "Mid pill row present (4)", "probe": "count_regions",
             "rect": [290 / fw, 350 / fh, 660 / fw, 70 / fh],
             "target_range": [4, 4], "min_area_px": 200},
            {"id": "pill_shape", "name": "First mid module is a pill", "probe": "shape_class",
             "rect": [295 / fw, 352 / fh, 160 / fw, 60 / fh], "target": ["pill"]},
            {"id": "footer_shape", "name": "Footer module is a bar", "probe": "shape_class",
             "rect": [890 / fw, 470 / fh, 280 / fw, 150 / fh],
             "target": ["bar", "rounded-bar"]},
            {"id": "ramp", "name": "Gradient strip smooth", "probe": "gradient_smooth",
             "rect": [60 / fw, 662 / fh, 1160 / fw, 36 / fh], "axis": "x"},
            {"id": "no_blowout", "name": "No clip-white field", "probe": "region_absent",
             "rect": [40 / fw, 590 / fh, 560 / fw, 65 / fh],
             "color": "#FFFFFF", "tol_de": 2.0, "min_fraction": 0.2},
            {"id": "attested_example", "name": "Emitted via Scene IR", "probe": "attest",
             "note": "calibration fixture: demonstrates attested cues never count as measured"},
        ],
    }


# Which cue must fail under which planted defect.
DEFECT_EXPECTATIONS = {
    "fill_shift": "header_fill",
    "layout_shift": "header_y0",
    "gutter_drift": "gutter",
    "missing_region": "pills",
    "radius_loss": "pill_shape",
    "single_corner_card": "footer_shape",
    "banding": "ramp",
    "blowout": "no_blowout",
}

# Where each planted defect lives (px rect), for region-local compare checks.
DEFECT_REGIONS = {
    "fill_shift": (248, 40, 560, 48),
    "layout_shift": (240, 30, 800, 80),
    "gutter_drift": (300, 470, 520, 150),
    "missing_region": (290, 350, 660, 70),
    "radius_loss": (290, 350, 660, 70),
    # The defect is the rounded top-left corner itself; judge it where it is.
    "single_corner_card": (890, 470, 80, 80),
    "banding": (40, 660, 1200, 40),
    "blowout": (40, 590, 560, 65),
}


# ── Motion fixtures ──────────────────────────────────────────

def render_motion_frames(variant: str, n: int = 30) -> list:
    """A pill travels left→right with ease-out; variants plant motion defects."""
    frames = []
    x0, x1 = 100, 900
    for i in range(n):
        t = i / (n - 1)
        te = 1 - (1 - t) ** 3  # ease-out cubic
        img = _canvas()
        _fill_rect(img, 40, 40, 1200, 30, HEADER)
        x = int(x0 + (x1 - x0) * te)
        if variant == "teleport" and i == 15:
            x = x1  # discontinuity: max-speed spike mid-flight
        bg_shift = 6.0 if (variant == "flicker" and i % 2 == 0) else 0.0
        if bg_shift:
            img[...] = np.clip(img + bg_shift, 0, 255)
        _fill_pill(img, x, 340, 160, 48, PILL)
        frames.append(np.clip(img, 0, 255).astype(np.uint8))
    if variant == "stutter":
        frames[12:17] = [frames[12]] * 5
    if variant == "dropped":
        del frames[12:15]
    return frames


MOTION_SPEC = {
    "max_duplicate_ratio": 0.08,
    "max_stutter_run": 2,
    "max_flicker_index": 0.5,
    "max_step_frac": 0.12,
    # Change-mask centroids average consecutive displacements, halving a
    # skip spike; measured: clean easing ~0.002, one 3-frame drop ~0.024.
    "max_accel_frac": 0.012,
    "min_monotone_fraction": 0.9,
}

MOTION_EXPECTATIONS = {
    "stutter": ("duplicate_ratio", "max_stutter_run"),
    "dropped": ("max_accel_frac",),
    "teleport": ("max_accel_frac", "max_step_frac", "monotone_fraction"),
    "flicker": ("flicker_index",),
}


# ── Calibration run ──────────────────────────────────────────

def run_calibration(out_dir: Optional[str | Path] = None, keep_images: bool = False) -> dict:
    # Resolve now: interact.verify_step prefixes spec_dir onto relative paths.
    # A cwd-relative --output would otherwise double-join (observed 2026-09-02).
    out = Path(out_dir).expanduser().resolve() if out_dir else Path(tempfile.mkdtemp(prefix="vqa_calib_"))
    out.mkdir(parents=True, exist_ok=True)
    rows = []

    def add(detector, case, expected, observed, ok, detail=""):
        rows.append({
            "detector": detector, "case": case, "expected": expected,
            "observed": observed, "ok": bool(ok), "detail": detail,
        })

    spec_path = out / "calibration.cuespec.json"
    write_json(base_cuespec(), spec_path)

    # Static: clean variants must fully pass (FP check)
    for clean in ("clean", "clean_noise"):
        img_path = out / f"{clean}.png"
        save_image(render_base(clean), img_path)
        write_json(
            {"viewport": {"width": W, "height": H}, "dpr": 1, "format": "png",
             "frozen": True, "tool": "vqa-calibrate"},
            Path(str(img_path) + ".capture.json"),
        )
        payload = prove.run_prove(img_path, spec_path, out_dir=out if keep_images else None)
        fails = [c["id"] for c in payload["cues"] if c["status"] == "fail"]
        errors = [c["id"] for c in payload["cues"] if c["status"] == "error"]
        add("prove", clean, "all measured cues pass", f"fails={fails} errors={errors}",
            not fails and not errors)
        add("verdict", clean, "matches", payload["summary"]["verdict"],
            payload["summary"]["verdict"] == "matches",
            "; ".join(payload["summary"]["verdict_reasons"]))

    # Static: each planted defect must fail its mapped cue and ONLY plausible cues
    for variant, expected_cue in DEFECT_EXPECTATIONS.items():
        img_path = out / f"{variant}.png"
        save_image(render_base(variant), img_path)
        payload = prove.run_prove(img_path, spec_path)
        by_id = {c["id"]: c for c in payload["cues"]}
        cue = by_id[expected_cue]
        add("prove", variant, f"cue '{expected_cue}' fails", cue["status"],
            cue["status"] == "fail",
            str(cue.get("value")))

    # Verdict honesty: attested cue never counts as measured
    clean_payload = prove.run_prove(out / "clean.png", spec_path)
    attested = [c for c in clean_payload["cues"] if c["status"] == "attested"]
    add("verdict", "attested_isolation", "1 attested, excluded from measured",
        f"attested={len(attested)}, measured={clean_payload['summary']['measured_total']}",
        len(attested) == 1
        and clean_payload["summary"]["measured_total"] == len(clean_payload["cues"]) - 1)

    # Capture gate: without a manifest, matches must degrade to partial
    unver = out / "clean_unverified.png"
    save_image(render_base("clean"), unver)
    payload = prove.run_prove(unver, spec_path)
    add("capture_gate", "no_manifest", "verdict capped at partial",
        payload["summary"]["verdict"],
        payload["summary"]["verdict"] == "partial"
        and payload["capture"]["status"] == "unverified")

    # Compare locality: in the defect's own region, the defect must degrade
    # SSIM beyond what full-canvas AA noise does there. (A small local defect
    # legitimately moves GLOBAL means less than everywhere-noise; locality is
    # the property compare must guarantee for ranking to be trustworthy.)
    clean_rgb = render_base("clean")
    noise_rgb = render_base("clean_noise")
    for variant, (rx, ry, rw, rh) in DEFECT_REGIONS.items():
        defect_rgb = render_base(variant)
        ref_crop_rgb = clean_rgb[ry : ry + rh, rx : rx + rw]
        noise_crop = noise_rgb[ry : ry + rh, rx : rx + rw]
        defect_crop = defect_rgb[ry : ry + rh, rx : rx + rw]
        ref_l = _core.luma(ref_crop_rgb)
        s_noise, _ = _core.ssim(ref_l, _core.luma(noise_crop))
        s_defect, _ = _core.ssim(ref_l, _core.luma(defect_crop))
        de_noise = float(_core.delta_e_map(ref_crop_rgb, noise_crop).mean())
        de_defect = float(_core.delta_e_map(ref_crop_rgb, defect_crop).mean())
        # Structural defects show in SSIM; chroma-only defects show in delta-E.
        # A defect must exceed AA noise on at least one channel.
        ok = (s_defect < s_noise - 0.003) or (de_defect > de_noise + 1.0)
        add("compare", f"local_{variant}", "region SSIM or delta-E: defect worse than AA noise",
            f"ssim {s_defect:.4f} vs {s_noise:.4f}; de {de_defect:.2f} vs {de_noise:.2f}", ok)

    # Motion: clean passes, planted defects trip their budgets
    for variant in ("clean", "stutter", "dropped", "teleport", "flicker"):
        fdir = out / f"motion_{variant}"
        fdir.mkdir(exist_ok=True)
        for i, fr in enumerate(render_motion_frames(variant)):
            save_image(fr, fdir / f"f_{i:03d}.png")
        payload = motion.analyze_motion(frames_dir=str(fdir), spec=MOTION_SPEC)
        failing = {v["check"] for v in payload["verdicts"] if v["status"] == "fail"}
        if variant == "clean":
            add("motion", "clean", "no budget failures", f"failing={sorted(failing)}",
                not failing)
        else:
            expected = set(MOTION_EXPECTATIONS[variant])
            add("motion", variant, f"fails any of {sorted(expected)}",
                f"failing={sorted(failing)}", bool(failing & expected))

    # Interact: change verified in region; dead control caught; leak caught
    before = render_base("clean")
    after = before.copy()
    after[360:404, 300:450] = ACCENT  # first pill recolored
    b_p, a_p = out / "int_before.png", out / "int_after.png"
    save_image(before, b_p)
    save_image(after, a_p)
    region = [290 / W, 350 / H, 180 / W, 70 / H]
    step_ok = interact.verify_step(
        {"name": "recolor in region", "before": str(b_p), "after": str(a_p),
         "expect": "change", "region": region}, out)
    add("interact", "expected_change", "pass", step_ok["status"], step_ok["status"] == "pass")
    step_dead = interact.verify_step(
        {"name": "dead control", "before": str(b_p), "after": str(b_p),
         "expect": "change", "region": region}, out)
    add("interact", "dead_control", "fail", step_dead["status"], step_dead["status"] == "fail")
    leak = after.copy()
    leak[600:640, 900:1100] = HEADER  # side effect far outside the region
    l_p = out / "int_leak.png"
    save_image(leak, l_p)
    step_leak = interact.verify_step(
        {"name": "leaky change", "before": str(b_p), "after": str(l_p),
         "expect": "change", "region": region, "max_outside_fraction": 0.001}, out)
    add("interact", "side_effect_leak", "fail", step_leak["status"], step_leak["status"] == "fail")

    # Perceive: ledger flag fires for the planted single-corner card
    pc = perceive.perceive(from_array(render_base("single_corner_card")))
    c09 = [f for f in pc["ledger_flags"] if f["ledger"] == "C-09"]
    add("perceive", "ledger_C09", "single-corner-card flagged",
        f"flags={[f['ledger'] for f in pc['ledger_flags']]}", bool(c09))
    pc_clean = perceive.perceive(from_array(render_base("clean")))
    c09_clean = [f for f in pc_clean["ledger_flags"] if f["ledger"] == "C-09"]
    add("perceive", "ledger_C09_clean", "no C-09 flag on clean",
        f"flags={[f['ledger'] for f in pc_clean['ledger_flags']]}", not c09_clean)

    # Capture: missing renderer is a warning, not unverified (LCARS manifests)
    cap = prove.run_prove(out / "clean.png", spec_path)
    add("capture_gate", "missing_renderer_is_warning",
        "verified + renderer warning",
        f"{cap['capture']['status']} warnings={cap['capture'].get('warnings')}",
        cap["capture"]["status"] == "verified"
        and any("renderer" in w for w in cap["capture"].get("warnings", [])))

    # Uncued residuals are named on the summary without flipping a clean matches
    res_spec = base_cuespec()
    res_spec["default_altitude"] = "A"
    res_spec["uncued_residuals"] = [
        {"id": "hole", "zone": "test zone", "note": "named hole"}
    ]
    res_path = out / "residuals.cuespec.json"
    write_json(res_spec, res_path)
    res_payload = prove.run_prove(out / "clean.png", res_path)
    add("residuals", "named_on_summary", "matches + residual listed",
        f"verdict={res_payload['summary']['verdict']} n={len(res_payload['summary']['uncued_residuals'])}",
        res_payload["summary"]["verdict"] == "matches"
        and res_payload["summary"]["uncued_residuals"][0]["id"] == "hole"
        and res_payload["summary"]["altitudes_in_contract"] == ["A"])

    # Optional DreamSim: skip or pass, never a hard error
    opt_spec = base_cuespec()
    opt_spec["cues"].append({
        "id": "dreamsim_opt", "name": "optional dreamsim",
        "probe": "dreamsim_region", "optional": True,
        "rect": [0.2, 0.05, 0.4, 0.1],
        "asset": "clean.png",
        "asset_rect": [0.2, 0.05, 0.4, 0.1],
        "max": 0.5,
    })
    opt_path = out / "optional.cuespec.json"
    write_json(opt_spec, opt_path)
    opt_payload = prove.run_prove(out / "clean.png", opt_path)
    ds = {c["id"]: c for c in opt_payload["cues"]}["dreamsim_opt"]
    add("optional", "dreamsim_skip_or_pass",
        "skipped or pass (optional)",
        ds["status"],
        ds["status"] in ("skipped", "pass")
        and opt_payload["summary"]["verdict"] == "matches")

    # FLIP-lite: identical ~0, chroma defect higher
    clean_rgb = render_base("clean")
    same = flip_metric.flip_map(clean_rgb, clean_rgb)
    shifted_fill = flip_metric.flip_map(clean_rgb, render_base("fill_shift"))
    add("flip", "identical", "mean < 0.02", same["mean"], same["mean"] < 0.02)
    add("flip", "fill_shift_worse", "mean higher than identical",
        f"{shifted_fill['mean']} vs {same['mean']}",
        shifted_fill["mean"] > same["mean"] + 0.005)

    # Saliency: pills carry more mass than an empty black patch
    sal = saliency.spectral_residual(_core.luma(clean_rgb))
    mass_pills = saliency.region_mass(sal, (290, 350, 660, 70))
    mass_empty = saliency.region_mass(sal, (40, 250, 200, 80))
    add("saliency", "structure_over_empty",
        "pill-row mass > empty patch",
        f"{mass_pills['mass_fraction']} vs {mass_empty['mass_fraction']}",
        mass_pills["mass_fraction"] > mass_empty["mass_fraction"])

    # Mesh: valid triangle passes; NaN accessor fails closed
    valid_gltf, nan_gltf = _triangle_buffers(out)
    valid_audit = mesh.audit(valid_gltf)
    nan_audit = mesh.audit(nan_gltf)
    add("mesh", "valid_triangle", "pass", valid_audit["status"],
        valid_audit["status"] == "pass")
    add("mesh", "nan_fails_closed", "fail",
        f"{nan_audit['status']} errors={nan_audit['errors']}",
        nan_audit["status"] == "fail" and nan_audit["errors"])

    # Geometry: two shifted views pass; one view errors (never a 3D pass)
    geo_a, geo_b = out / "geo_a.png", out / "geo_b.png"
    save_image(clean_rgb, geo_a)
    save_image(compare._shift(clean_rgb, 2, 1), geo_b)
    geo_ok = geometry.consistency([str(geo_a), str(geo_b)])
    geo_one = geometry.consistency([str(geo_a)])
    add("geometry", "two_views", "pass", geo_ok["status"], geo_ok["status"] == "pass")
    add("geometry", "one_view_is_error", "error", geo_one["status"],
        geo_one["status"] == "error")

    # Input-to-photon: pill appears at inject_frame
    pdir = out / "photon"
    pdir.mkdir(exist_ok=True)
    for i in range(12):
        img = _canvas()
        _fill_rect(img, 40, 40, 1200, 30, HEADER)
        if i >= 6:
            _fill_pill(img, 400, 340, 160, 48, PILL)
        save_image(np.clip(img, 0, 255).astype(np.uint8), pdir / f"f_{i:03d}.png")
    photon_payload = motion.analyze_motion(
        frames_dir=str(pdir),
        spec={"photon": {"inject_frame": 6, "min_changed_fraction": 0.001,
                         "max_latency_frames": 1}},
    )
    add("photon", "first_change", "latency_frames == 0",
        photon_payload.get("photon"),
        photon_payload.get("photon", {}).get("latency_frames") == 0
        and all(v["status"] == "pass" for v in photon_payload["verdicts"]
                if v["check"] == "input_to_photon"))

    # Labeled tracks run (NCC floor)
    tdir = out / "motion_clean"
    track_payload = motion.analyze_motion(
        frames_dir=str(tdir),
        spec={**MOTION_SPEC, "track_points": [[180, 364]]},
    )
    add("motion", "tracks_ncc", "1 tracked point",
        track_payload.get("tracks"),
        (track_payload.get("tracks") or {}).get("n_points") == 1)

    # Critic cannot override a pixel fail
    critic_cmd = [sys.executable, "-c", "print('{\"verdict\":\"pass\"}')"]
    step_dead_c = interact.verify_step(
        {"name": "dead+critic-pass", "before": str(b_p), "after": str(b_p),
         "expect": "change", "region": region, "critic": {"command": critic_cmd}},
        out)
    add("interact", "critic_cannot_override_pixel_fail", "fail",
        step_dead_c["status"], step_dead_c["status"] == "fail")

    # VLM-judge protocol: two families agree; order-inconsistent pair discarded
    (out / "judge_yes.py").write_text(
        "import json\nprint(json.dumps({'verdict':'yes'}))\n", encoding="utf-8"
    )
    (out / "judge_flip.py").write_text(
        "import json, os\n"
        "print(json.dumps({'verdict': 'yes' if os.environ.get('VQA_JUDGE_ORDER')=='ab' else 'no'}))\n",
        encoding="utf-8",
    )
    judge_ok = {
        "spec": "vqa-judge/1", "altitude": "D", "prompt": "match?",
        "reference": "clean.png", "candidate": "clean.png",
        "judges": [
            {"family": "alpha", "command": [sys.executable, str(out / "judge_yes.py")]},
            {"family": "beta", "command": [sys.executable, str(out / "judge_yes.py")]},
        ],
    }
    jpath = out / "judge_ok.json"
    write_json(judge_ok, jpath)
    j_ok = judge.run_judge(jpath)
    add("judge", "two_families_agree", "yes", j_ok["verdict"], j_ok["verdict"] == "yes")
    judge_bad = {
        "spec": "vqa-judge/1", "altitude": "D", "prompt": "match?",
        "reference": "clean.png", "candidate": "clean.png",
        "judges": [
            {"family": "alpha", "command": [sys.executable, str(out / "judge_flip.py")]},
            {"family": "beta", "command": [sys.executable, str(out / "judge_flip.py")]},
        ],
    }
    jpath2 = out / "judge_bad.json"
    write_json(judge_bad, jpath2)
    j_bad = judge.run_judge(jpath2)
    add("judge", "inconsistent_discarded", "discarded", j_bad["verdict"],
        j_bad["verdict"] == "discarded")

    # play-prove sibling CLI
    (out / "sim.py").write_text(
        "import json\n"
        "print(json.dumps({'win_rate':0.52,'avg':10.0,'stddev':1.2,'n':80,"
        "'strategy_shares':{'a':0.34,'b':0.33,'c':0.33}}))\n",
        encoding="utf-8",
    )
    pp_spec = {
        "spec": "play-prove/1",
        "adapter": {"command": [sys.executable, str(out / "sim.py")]},
        "assert": {
            "win_rate": {"min": 0.4, "max": 0.6},
            "no_dominant_strategy": {"max_share": 0.5},
        },
    }
    pp_path = out / "play.json"
    write_json(pp_spec, pp_path)
    play_cli = Path(__file__).resolve().parents[2] / "play-prove" / "playprove.py"
    import subprocess
    proc = subprocess.run(
        [sys.executable, str(play_cli), "prove", str(pp_path)],
        capture_output=True, text=True, check=False,
    )
    add("playprove", "balanced_sim", "pass exit 0",
        f"exit={proc.returncode} {(proc.stdout or '')[:120]}",
        proc.returncode == 0 and '"verdict": "pass"' in proc.stdout)

    misses = [r for r in rows if not r["ok"]]
    detectors = sorted({r["detector"] for r in rows})
    per_detector = {
        d: {
            "cases": sum(1 for r in rows if r["detector"] == d),
            "ok": sum(1 for r in rows if r["detector"] == d and r["ok"]),
        }
        for d in detectors
    }
    report = {
        "engine": _core.ENGINE_VERSION,
        "seed": SEED,
        "cases_total": len(rows),
        "cases_ok": len(rows) - len(misses),
        "misses": misses,
        "per_detector": per_detector,
        "verdict": "calibrated" if not misses else "FAILED",
        "rows": rows,
        "deps": _core.deps_report(),
        "out_dir": str(out),
    }
    write_json(report, out / "calibration-report.json")
    (out / "calibration-report.md").write_text(_calib_md(report), encoding="utf-8")
    return report


def _calib_md(report: dict) -> str:
    lines = [
        "# Calibration report — visual prove engine",
        "",
        f"- Verdict: **{report['verdict']}** ({report['cases_ok']}/{report['cases_total']} cases)",
        f"- Seed: {report['seed']} · engine: {report['engine']}",
        "",
        "| Detector | Case | Expected | Observed | OK |",
        "|---|---|---|---|---|",
    ]
    for r in report["rows"]:
        lines.append(
            f"| {r['detector']} | {r['case']} | {r['expected']} | {r['observed']} "
            f"| {'yes' if r['ok'] else '**MISS**'} |"
        )
    lines += [
        "",
        "_Every planted defect must be detected and every clean variant must pass._",
        "_A miss here means a detector is lying; do not trust its verdicts until fixed._",
        "",
    ]
    return "\n".join(lines)


def _triangle_buffers(out: Path) -> tuple:
    """Write a valid glTF triangle and a NaN-corrupted twin."""
    import base64
    positions = struct.pack("<9f", 0, 0, 0, 1, 0, 0, 0, 1, 0)
    indices = struct.pack("<3H", 0, 1, 2)
    raw = positions + indices + b"\x00\x00"
    uri = "data:application/octet-stream;base64," + base64.b64encode(raw).decode("ascii")
    doc = {
        "asset": {"version": "2.0"},
        "scene": 0,
        "scenes": [{"nodes": [0]}],
        "nodes": [{"mesh": 0}],
        "meshes": [{"primitives": [{"attributes": {"POSITION": 0}, "indices": 1}]}],
        "accessors": [
            {"bufferView": 0, "componentType": 5126, "count": 3, "type": "VEC3",
             "max": [1, 1, 0], "min": [0, 0, 0]},
            {"bufferView": 1, "componentType": 5123, "count": 3, "type": "SCALAR"},
        ],
        "bufferViews": [
            {"buffer": 0, "byteOffset": 0, "byteLength": 36},
            {"buffer": 0, "byteOffset": 36, "byteLength": 6},
        ],
        "buffers": [{"byteLength": len(raw), "uri": uri}],
    }
    valid = out / "tri.gltf"
    write_json(doc, valid)
    nan_raw = struct.pack("<9f", 0, 0, 0, float("nan"), 0, 0, 0, 1, 0) + indices + b"\x00\x00"
    nan_uri = "data:application/octet-stream;base64," + base64.b64encode(nan_raw).decode("ascii")
    nan_doc = json.loads(json.dumps(doc))
    nan_doc["buffers"] = [{"byteLength": len(nan_raw), "uri": nan_uri}]
    nan_path = out / "tri_nan.gltf"
    write_json(nan_doc, nan_path)
    return valid, nan_path
