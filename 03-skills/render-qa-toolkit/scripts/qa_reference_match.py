"""
qa_reference_match.py — SSIM + optional mean-abs RGB (delta-E-style) vs a northstar still.

Usage:
    python -m scripts.qa_reference_match --input frame.png --reference northstar.png \\
        --config configs/default.yaml --output ./qa-out
"""
from __future__ import annotations

import argparse
from pathlib import Path

import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim

from ._common import (
    Finding,
    ReportWriter,
    Severity,
    config_section,
    draw_bbox,
    ensure_output_dir,
    load_config,
    load_image,
    log,
    save_bgr_image,
)

CHECK_NAME = "reference_match"

DEFAULTS = {
    "ssim_threshold": 0.90,
    "rgb_mad_threshold": 18.0,   # mean abs channel delta 0–255
    "pixel_diff_threshold": 30,
    "min_region_area": 400,
    "dilation_iterations": 3,
    "overlay_alpha": 0.5,
    "compute_lab_mad": True,     # CIE76-ish mean abs in Lab (OpenCV Lab)
}


def run(
    input_path: Path,
    config: dict,
    output_dir: Path,
    reference_override: str | Path | None = None,
) -> ReportWriter:
    cfg = config_section(config, CHECK_NAME, DEFAULTS)
    reference_path = reference_override or cfg.get("reference_path")
    report = ReportWriter(CHECK_NAME, config_summary={**cfg, "reference_path": str(reference_path) if reference_path else None})

    if not reference_path:
        report.add_finding(Finding(
            check=CHECK_NAME,
            severity=Severity.INFO,
            message="reference_match requires --reference or reference_path in config",
        ))
        report.set_summary("Skipped: no reference.")
        return report

    inp = load_image(input_path)
    ref = load_image(reference_path)
    report.set_metadata("input", str(input_path))
    report.set_metadata("reference", str(reference_path))
    report.set_metadata("input_size", f"{inp.width}×{inp.height}")
    report.set_metadata("reference_size", f"{ref.width}×{ref.height}")

    if (inp.width, inp.height) != (ref.width, ref.height):
        report.add_finding(Finding(
            check=CHECK_NAME,
            severity=Severity.CRITICAL,
            message=(
                f"Size mismatch: input {inp.width}×{inp.height} vs "
                f"reference {ref.width}×{ref.height}"
            ),
            details="Do not resize for match scoring — recapture at matching dimensions.",
        ))
        report.set_summary("Skipped: size mismatch.")
        return report

    global_ssim, ssim_map = ssim(inp.gray, ref.gray, full=True, data_range=255)
    rgb_mad = float(np.mean(np.abs(inp.rgb.astype(np.float64) - ref.rgb.astype(np.float64))))

    lab_mad = None
    if cfg.get("compute_lab_mad", True):
        lab_i = cv2.cvtColor(inp.rgb, cv2.COLOR_RGB2LAB).astype(np.float64)
        lab_r = cv2.cvtColor(ref.rgb, cv2.COLOR_RGB2LAB).astype(np.float64)
        lab_mad = float(np.mean(np.abs(lab_i - lab_r)))

    report.set_metadata("ssim", round(float(global_ssim), 4))
    report.set_metadata("rgb_mad", round(rgb_mad, 3))
    if lab_mad is not None:
        report.set_metadata("lab_mad", round(lab_mad, 3))

    ssim_t = float(cfg["ssim_threshold"])
    rgb_t = float(cfg["rgb_mad_threshold"])

    if global_ssim < ssim_t:
        sev = Severity.HIGH if global_ssim < 0.8 else Severity.MEDIUM
        report.add_finding(Finding(
            check=CHECK_NAME,
            severity=sev,
            message=f"SSIM {global_ssim:.3f} below threshold {ssim_t}",
            measurement={"ssim": round(float(global_ssim), 4), "threshold": ssim_t},
        ))
    if rgb_mad > rgb_t:
        report.add_finding(Finding(
            check=CHECK_NAME,
            severity=Severity.MEDIUM,
            message=f"RGB mean-abs {rgb_mad:.2f} above threshold {rgb_t}",
            measurement={"rgb_mad": round(rgb_mad, 3), "threshold": rgb_t, "lab_mad": round(lab_mad, 3) if lab_mad else None},
        ))
    if not any(f.severity in (Severity.HIGH, Severity.MEDIUM, Severity.CRITICAL) for f in report.findings):
        report.add_finding(Finding(
            check=CHECK_NAME,
            severity=Severity.INFO,
            message=f"Match OK — SSIM={global_ssim:.3f}, RGB MAD={rgb_mad:.2f}",
            measurement={"ssim": round(float(global_ssim), 4), "rgb_mad": round(rgb_mad, 3)},
        ))

    # Diff regions
    diff = cv2.absdiff(inp.gray, ref.gray)
    _, mask = cv2.threshold(diff, int(cfg["pixel_diff_threshold"]), 255, cv2.THRESH_BINARY)
    kernel = np.ones((3, 3), np.uint8)
    dilated = cv2.dilate(mask, kernel, iterations=int(cfg["dilation_iterations"]))
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    annotated = inp.bgr.copy()
    region_count = 0
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if w * h < int(cfg["min_region_area"]):
            continue
        region_count += 1
        draw_bbox(annotated, (x, y, w, h), color="warning", thickness=2)

    out = ensure_output_dir(output_dir)
    ann_path = out / "reference_match_annotated.png"
    save_bgr_image(annotated, ann_path)
    report.add_visual(ann_path.name, "Input with diff regions")

    inv = (1.0 - ssim_map).clip(0, 1)
    heat = cv2.applyColorMap((inv * 255).astype(np.uint8), cv2.COLORMAP_JET)
    alpha = float(cfg["overlay_alpha"])
    overlay = cv2.addWeighted(inp.bgr, 1 - alpha, heat, alpha, 0)
    heat_path = out / "reference_match_heatmap.png"
    save_bgr_image(overlay, heat_path)
    report.add_visual(heat_path.name, "SSIM heatmap overlay")

    sbs = np.hstack([ref.bgr, inp.bgr])
    sbs_path = out / "reference_match_side_by_side.png"
    save_bgr_image(sbs, sbs_path)
    report.add_visual(sbs_path.name, "Reference (left) vs input (right)")

    report.set_summary(
        f"SSIM={global_ssim:.3f} · RGB MAD={rgb_mad:.2f}"
        + (f" · Lab MAD={lab_mad:.2f}" if lab_mad is not None else "")
        + f" · {region_count} diff region(s)"
    )
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="SSIM + RGB MAD vs a northstar reference.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--reference", required=False)
    parser.add_argument("--config", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    config = load_config(args.config)
    output_dir = ensure_output_dir(args.output)
    report = run(Path(args.input), config, output_dir, reference_override=args.reference)
    report_path = output_dir / f"{CHECK_NAME}_report.md"
    report.write(report_path)
    log.info(f"{CHECK_NAME}: wrote report → {report_path}")
    print(f"Report written to {report_path} ({sum(report.counts.values())} finding(s))")


if __name__ == "__main__":
    main()
