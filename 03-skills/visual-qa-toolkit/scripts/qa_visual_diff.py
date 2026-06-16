"""
qa_visual_diff.py — Compare two screenshots via SSIM + pixel diff.

Usage:
    python -m scripts.qa_visual_diff --input screenshot.png --reference design_export.png --config centric.yaml --output ./qa-out

What it does:
    - Computes Structural Similarity Index (SSIM) between two images.
    - Generates a per-pixel difference map and identifies contiguous regions
      of significant difference.
    - Flags each region, reporting its size and the local SSIM score.
    - Emits side-by-side and overlay visualizations with diff regions highlighted.

What it does not do:
    - It does not attempt to register or align the two images. If the reference
      and the screenshot have different dimensions or offsets, results will be
      unreliable. Ensure both images are captured at the same size.
    - It does not understand semantic drift. A 4px text shift is a "difference"
      to SSIM but may or may not matter visually. Use severity as a prior, your
      eyes as the arbiter.
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


CHECK_NAME = "visual_diff"

DEFAULTS = {
    "reference_path": None,          # required — compared against input
    "ssim_threshold": 0.95,          # global SSIM below this is flagged
    "pixel_diff_threshold": 25,      # per-pixel intensity delta to count as "different"
    "min_region_area": 200,          # ignore tiny diff regions (noise)
    "dilation_iterations": 3,        # merge nearby diff pixels into regions
    "overlay_alpha": 0.5,
}


def run(input_path: Path, config: dict, output_dir: Path, reference_override: str | Path | None = None) -> ReportWriter:
    cfg = config_section(config, CHECK_NAME, DEFAULTS)

    reference_path = reference_override or cfg.get("reference_path")
    if not reference_path:
        report = ReportWriter(CHECK_NAME, config_summary=cfg)
        report.set_summary("Skipped: no reference_path configured or provided.")
        report.add_finding(Finding(
            check=CHECK_NAME,
            severity=Severity.INFO,
            message="visual_diff requires a reference image",
            details=(
                "Set `visual_diff.reference_path` in the config or pass "
                "--reference on the CLI to enable this check."
            ),
        ))
        return report

    input_img = load_image(input_path)
    ref_img = load_image(reference_path)

    report = ReportWriter(CHECK_NAME, config_summary={**cfg, "reference_path": str(reference_path)})
    report.set_metadata("input", str(input_path))
    report.set_metadata("reference", str(reference_path))
    report.set_metadata("input_size", f"{input_img.width}×{input_img.height}")
    report.set_metadata("reference_size", f"{ref_img.width}×{ref_img.height}")

    # Size mismatch handling
    if (input_img.width, input_img.height) != (ref_img.width, ref_img.height):
        report.add_finding(Finding(
            check=CHECK_NAME,
            severity=Severity.CRITICAL,
            message=(
                f"Image sizes differ: input is {input_img.width}×{input_img.height}, "
                f"reference is {ref_img.width}×{ref_img.height}"
            ),
            details=(
                "Visual diff requires both images to be the same size. "
                "Resizing is not attempted here — it would produce misleading "
                "interpolation artifacts in the diff. Re-capture at matching "
                "dimensions and re-run."
            ),
        ))
        report.set_summary("Skipped diff: size mismatch (see finding).")
        return report

    # Compute SSIM
    global_ssim, ssim_map = ssim(
        input_img.gray, ref_img.gray,
        full=True, data_range=255,
    )
    report.set_metadata("ssim_global", round(float(global_ssim), 4))

    # Pixel difference
    diff = cv2.absdiff(input_img.gray, ref_img.gray)
    _, mask = cv2.threshold(diff, cfg["pixel_diff_threshold"], 255, cv2.THRESH_BINARY)

    # Dilate to merge adjacent different pixels into regions
    kernel = np.ones((3, 3), np.uint8)
    dilated = cv2.dilate(mask, kernel, iterations=cfg["dilation_iterations"])

    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    regions = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        area = w * h
        if area >= cfg["min_region_area"]:
            # Local SSIM for this region
            y2 = min(y + h, ssim_map.shape[0])
            x2 = min(x + w, ssim_map.shape[1])
            local_ssim = float(ssim_map[y:y2, x:x2].mean())
            regions.append((x, y, w, h, area, local_ssim))

    regions.sort(key=lambda r: r[4], reverse=True)

    # Global SSIM finding
    if global_ssim < cfg["ssim_threshold"]:
        severity = (
            Severity.HIGH if global_ssim < 0.85
            else Severity.MEDIUM
        )
        report.add_finding(Finding(
            check=CHECK_NAME,
            severity=severity,
            message=f"Global SSIM {global_ssim:.3f} below threshold {cfg['ssim_threshold']}",
            details=(
                "Structural similarity measures overall visual agreement. "
                "Values of 1.0 = identical; below ~0.95 typically indicates "
                "noticeable differences. Review region findings for specifics."
            ),
            measurement={
                "ssim": round(float(global_ssim), 4),
                "threshold": cfg["ssim_threshold"],
            },
        ))

    # Per-region findings
    for x, y, w, h, area, local_ssim in regions:
        severity = (
            Severity.HIGH if local_ssim < 0.7
            else Severity.MEDIUM if local_ssim < 0.9
            else Severity.LOW
        )
        report.add_finding(Finding(
            check=CHECK_NAME,
            severity=severity,
            message=f"Diff region at ({x}, {y}) — {w}×{h}px, local SSIM {local_ssim:.3f}",
            location=(x, y, w, h),
            measurement={
                "area_px": area,
                "local_ssim": round(local_ssim, 4),
                "pct_of_image": round(100 * area / (input_img.width * input_img.height), 2),
            },
        ))

    # Annotated visualizations
    # 1) Input with diff regions highlighted
    annotated = input_img.bgr.copy()
    for x, y, w, h, area, local_ssim in regions:
        color = "critical" if local_ssim < 0.7 else "warning"
        draw_bbox(annotated, (x, y, w, h), color=color, thickness=2)

    annotated_path = ensure_output_dir(output_dir) / "visual_diff_annotated.png"
    save_bgr_image(annotated, annotated_path)
    report.add_visual(annotated_path.name, "Input with diff regions highlighted")

    # 2) Heatmap overlay
    inv_ssim = (1.0 - ssim_map).clip(0, 1)
    heat = (inv_ssim * 255).astype(np.uint8)
    heat_color = cv2.applyColorMap(heat, cv2.COLORMAP_JET)
    overlay = cv2.addWeighted(input_img.bgr, 1 - cfg["overlay_alpha"], heat_color, cfg["overlay_alpha"], 0)
    heat_path = ensure_output_dir(output_dir) / "visual_diff_heatmap.png"
    save_bgr_image(overlay, heat_path)
    report.add_visual(heat_path.name, "SSIM heatmap overlay (red = most different)")

    # 3) Side-by-side
    sbs = np.hstack([ref_img.bgr, input_img.bgr])
    # Add a subtle separator
    cv2.line(sbs, (input_img.width, 0), (input_img.width, input_img.height), (40, 40, 40), 2)
    sbs_path = ensure_output_dir(output_dir) / "visual_diff_side_by_side.png"
    save_bgr_image(sbs, sbs_path)
    report.add_visual(sbs_path.name, "Reference (left) vs. Input (right)")

    report.set_summary(
        f"Global SSIM: {global_ssim:.3f}. "
        f"Found {len(regions)} significant diff region(s). "
        f"Threshold: SSIM ≥ {cfg['ssim_threshold']}, "
        f"per-pixel Δ > {cfg['pixel_diff_threshold']}/255."
    )
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--input", required=True)
    parser.add_argument("--reference", required=False, help="Override reference_path from config")
    parser.add_argument("--config", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    config = load_config(args.config)
    output_dir = ensure_output_dir(args.output)
    report = run(Path(args.input), config, output_dir, reference_override=args.reference)
    report_path = output_dir / "visual_diff_report.md"
    report.write(report_path)
    log.info(f"visual_diff: wrote report → {report_path}")
    print(f"Report written to {report_path} ({sum(report.counts.values())} finding(s))")


if __name__ == "__main__":
    main()
