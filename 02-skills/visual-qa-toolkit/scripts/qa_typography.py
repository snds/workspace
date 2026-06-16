"""
qa_typography.py — Measure text region heights and flag type-scale inconsistencies.

Usage:
    python -m scripts.qa_typography --input screenshot.png --config centric.yaml --output ./qa-out

What it does:
    - Detects text-like regions via MSER (or uses explicit bboxes from config).
    - Approximates cap-height of each region via vertical projection of pixels
      that are darker/lighter than the background.
    - Compares each measured height against the configured type scale.
    - Flags heights that don't match any scale value within tolerance.
    - Emits an annotated image with measured heights labeled.

Honest limits:
    - Cap-height estimation from a screenshot is approximate — subpixel
      rendering, font hinting, and anti-aliasing all make exact measurement
      unreliable. Treat these findings as "this region deserves a look,"
      not as definitive type-scale violations.
    - The script does not identify font family or weight. For those, a
      design-vs-code comparison is more direct than image analysis.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import cv2
import numpy as np

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


CHECK_NAME = "typography"

DEFAULTS = {
    "type_scale_px": [12, 14, 16, 20, 24, 32, 40, 48],
    "tolerance_px": 2,
    "text_regions": None,            # explicit bboxes, else auto-detect
    "auto_detect": True,
    "min_region_area": 150,
    "max_region_area_pct": 0.1,
    "min_height_px": 8,
    "max_height_px": 120,
}


def _auto_detect_text_regions(gray: np.ndarray, min_area: int, max_area_pct: float) -> list[tuple[int, int, int, int]]:
    """Similar to qa_contrast — MSER-based text region detection."""
    total_area = gray.shape[0] * gray.shape[1]
    max_area = int(total_area * max_area_pct)

    mser = cv2.MSER_create()
    mser.setMinArea(min_area)
    mser.setMaxArea(max_area)
    regions, _ = mser.detectRegions(gray)

    bboxes: list[tuple[int, int, int, int]] = []
    for r in regions:
        x, y, w, h = cv2.boundingRect(r.reshape(-1, 1, 2))
        if w < 8 or h < 8 or w > h * 30:
            continue
        bboxes.append((x, y, w, h))

    bboxes.sort(key=lambda b: b[2] * b[3], reverse=True)
    kept: list[tuple[int, int, int, int]] = []
    for bbox in bboxes:
        x1, y1, w1, h1 = bbox
        overlaps = False
        for kx, ky, kw, kh in kept:
            ix, iy = max(x1, kx), max(y1, ky)
            ax, ay = min(x1 + w1, kx + kw), min(y1 + h1, ky + kh)
            if ax > ix and ay > iy:
                inter = (ax - ix) * (ay - iy)
                if inter / (w1 * h1) > 0.5:
                    overlaps = True
                    break
        if not overlaps:
            kept.append(bbox)
    return kept


def _measure_cap_height(gray_region: np.ndarray) -> int:
    """
    Approximate cap-height by finding the tight vertical bounds of the
    "ink" (pixels significantly different from the background).
    """
    if gray_region.size == 0:
        return 0

    # Estimate background as the median (most text-on-bg regions are majority bg)
    bg = int(np.median(gray_region))

    # Pixels sufficiently different from background are "ink"
    diff = np.abs(gray_region.astype(int) - bg)
    threshold = max(20, int(0.2 * 255))
    ink_mask = diff > threshold

    # Row-wise ink presence
    row_has_ink = ink_mask.any(axis=1)
    if not row_has_ink.any():
        return 0

    ink_rows = np.where(row_has_ink)[0]
    return int(ink_rows[-1] - ink_rows[0] + 1)


def _match_scale(height: int, scale: list[int], tolerance: int) -> tuple[int, int] | None:
    deviations = [(s, abs(height - s)) for s in scale]
    nearest, delta = min(deviations, key=lambda p: p[1])
    if delta <= tolerance:
        return (nearest, delta)
    return None


def run(input_path: Path, config: dict, output_dir: Path) -> ReportWriter:
    cfg = config_section(config, CHECK_NAME, DEFAULTS)
    scale = cfg["type_scale_px"]
    tolerance = cfg["tolerance_px"]

    img = load_image(input_path)
    report = ReportWriter(CHECK_NAME, config_summary=cfg)
    report.set_metadata("source", str(input_path))
    report.set_metadata("scale", scale)
    report.set_metadata("tolerance_px", tolerance)

    # Get regions
    regions: list[tuple[tuple[int, int, int, int], str]] = []
    if cfg.get("text_regions"):
        for entry in cfg["text_regions"]:
            bbox = tuple(entry["bbox"])
            label = entry.get("label", f"region_{len(regions)}")
            regions.append((bbox, label))
    elif cfg.get("auto_detect", True):
        auto = _auto_detect_text_regions(
            img.gray,
            min_area=cfg["min_region_area"],
            max_area_pct=cfg["max_region_area_pct"],
        )
        regions = [(b, f"auto_{i}") for i, b in enumerate(auto)]

    report.set_metadata("regions_analyzed", len(regions))

    annotated = img.bgr.copy()
    measurements: list[tuple[str, tuple[int, int, int, int], int]] = []

    for bbox, label in regions:
        x, y, w, h = bbox
        x = max(0, x); y = max(0, y)
        w = min(w, img.width - x); h = min(h, img.height - y)
        if w <= 0 or h <= 0:
            continue

        region = img.gray[y:y + h, x:x + w]
        cap_h = _measure_cap_height(region)

        if not (cfg["min_height_px"] <= cap_h <= cfg["max_height_px"]):
            # Out of plausible text-size range; skip
            continue

        measurements.append((label, bbox, cap_h))
        match = _match_scale(cap_h, scale, tolerance)
        if match is None:
            nearest = min(scale, key=lambda s: abs(cap_h - s))
            delta = abs(cap_h - nearest)
            severity = Severity.MEDIUM if delta <= tolerance * 2 else Severity.HIGH
            report.add_finding(Finding(
                check=CHECK_NAME,
                severity=severity,
                message=(
                    f"{label}: cap-height ~{cap_h}px doesn't match scale "
                    f"(nearest: {nearest}px, off by {delta}px)"
                ),
                details=(
                    f"Measurement is approximate — ±1–2px error is normal due to "
                    f"anti-aliasing and hinting. Worth checking if this text is "
                    f"authored against a scale of `{scale}`."
                ),
                location=bbox,
                measurement={
                    "label": label,
                    "measured_height_px": cap_h,
                    "nearest_scale_value": nearest,
                    "deviation_px": delta,
                },
            ))
            draw_bbox(annotated, bbox, color="critical", thickness=1, label=f"~{cap_h}px")
        else:
            nearest, delta = match
            draw_bbox(annotated, bbox, color="success", thickness=1, label=f"~{cap_h}px")

    if measurements:
        heights = [m[2] for m in measurements]
        report.set_metadata("height_distribution", {
            "unique_values": sorted(set(heights)),
            "count_per_value": {h: heights.count(h) for h in sorted(set(heights))},
        })

    annotated_path = ensure_output_dir(output_dir) / "typography_annotated.png"
    save_bgr_image(annotated, annotated_path)
    report.add_visual(annotated_path.name, "Text regions with approximated cap-heights")

    total = sum(report.counts.values())
    report.set_summary(
        f"Analyzed {len(measurements)} text region(s) against scale {scale} "
        f"(tolerance ±{tolerance}px). Off-scale: {total}."
    )

    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--input", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    config = load_config(args.config)
    output_dir = ensure_output_dir(args.output)
    report = run(Path(args.input), config, output_dir)
    report_path = output_dir / "typography_report.md"
    report.write(report_path)
    log.info(f"typography: wrote report → {report_path}")
    print(f"Report written to {report_path} ({sum(report.counts.values())} finding(s))")


if __name__ == "__main__":
    main()
