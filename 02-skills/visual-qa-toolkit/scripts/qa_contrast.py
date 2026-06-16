"""
qa_contrast.py — WCAG contrast verification.

Usage:
    python -m scripts.qa_contrast --input screenshot.png --config centric.yaml --output ./qa-out

What it does:
    - For each configured text region (or auto-detected text-like regions),
      samples the dominant foreground and background colors.
    - Computes WCAG 2.x contrast ratios between fg/bg pairs.
    - Flags regions that fail the configured threshold (default: WCAG AA at 4.5:1 for body text).
    - Emits an annotated image highlighting failures and a markdown report.

What it does not do:
    - It cannot reliably distinguish text from icon glyphs. For auto-detection,
      small high-contrast regions may or may not be text. For precision, specify
      `text_regions` in the config as an explicit list of bboxes.
    - It does not compute APCA (the newer algorithm that WCAG 3.x is likely to
      adopt). APCA support can be added later if needed — current Centric/Legion
      accessibility targets are WCAG 2.x.
"""
from __future__ import annotations

import argparse
from collections import Counter
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
    hex_to_rgb,
    load_config,
    load_image,
    log,
    rgb_to_hex,
    save_bgr_image,
    wcag_contrast_ratio,
)


CHECK_NAME = "contrast"

DEFAULTS = {
    "standard": "WCAG_AA",      # WCAG_AA | WCAG_AAA
    "text_size": "body",         # body | large — changes threshold
    "text_regions": None,        # list of {bbox: [x,y,w,h], label: str} — or None to auto-detect
    "auto_detect": True,
    "min_region_area": 200,
    "max_region_area_pct": 0.2,
    "sample_inner_margin": 2,    # shrink bbox by this much when sampling bg
}

# WCAG 2.x thresholds
THRESHOLDS = {
    ("WCAG_AA",  "body"):  4.5,
    ("WCAG_AA",  "large"): 3.0,
    ("WCAG_AAA", "body"):  7.0,
    ("WCAG_AAA", "large"): 4.5,
}


def _dominant_colors(pixels: np.ndarray, k: int = 2) -> list[tuple[tuple[int, int, int], int]]:
    """Return top-k dominant (color, pixel_count) pairs via rough quantization."""
    if pixels.size == 0:
        return []
    # Quantize to 5 bits per channel to cluster similar colors
    quantized = (pixels // 8) * 8
    flat = [tuple(p) for p in quantized.reshape(-1, 3)]
    counter = Counter(flat)
    return [(color, count) for color, count in counter.most_common(k)]


def _split_fg_bg(region_pixels: np.ndarray) -> tuple[tuple[int, int, int], tuple[int, int, int]]:
    """
    Given the pixels of a region, estimate (foreground, background) colors.
    Assumes background is the more dominant color, foreground is the darker/lighter
    accent that has sufficient contrast with it.
    """
    dominants = _dominant_colors(region_pixels, k=8)
    if not dominants:
        return (0, 0, 0), (255, 255, 255)

    bg = dominants[0][0]

    # Find a foreground candidate with strongest contrast vs. bg
    best_contrast = 0
    fg = bg
    for color, _count in dominants[1:]:
        c = wcag_contrast_ratio(color, bg)
        if c > best_contrast:
            best_contrast = c
            fg = color

    # If no candidate had meaningful contrast, fall back to the luminance extreme
    if best_contrast < 1.5:
        from ._common import relative_luminance
        bg_lum = relative_luminance(bg)
        pixels_flat = region_pixels.reshape(-1, 3)
        lums = np.array([relative_luminance(tuple(p)) for p in pixels_flat[:min(500, len(pixels_flat))]])
        if bg_lum > 0.5:
            idx = int(np.argmin(lums))
        else:
            idx = int(np.argmax(lums))
        fg = tuple(int(v) for v in pixels_flat[idx])

    return fg, bg


def _auto_detect_text_regions(gray: np.ndarray, min_area: int, max_area_pct: float) -> list[tuple[int, int, int, int]]:
    """Heuristic text-region detection via MSER. Returns list of bboxes."""
    total_area = gray.shape[0] * gray.shape[1]
    max_area = int(total_area * max_area_pct)

    mser = cv2.MSER_create()
    mser.setMinArea(min_area)
    mser.setMaxArea(max_area)
    regions, _ = mser.detectRegions(gray)

    bboxes = []
    for region in regions:
        x, y, w, h = cv2.boundingRect(region.reshape(-1, 1, 2))
        # Text-like aspect ratio + minimum size
        if w < 8 or h < 8:
            continue
        if w > h * 30 or h > w * 30:
            continue
        bboxes.append((x, y, w, h))

    # Deduplicate overlapping bboxes (simple NMS-lite)
    bboxes.sort(key=lambda b: b[2] * b[3], reverse=True)
    kept: list[tuple[int, int, int, int]] = []
    for bbox in bboxes:
        x1, y1, w1, h1 = bbox
        overlaps = False
        for kx, ky, kw, kh in kept:
            ix = max(x1, kx)
            iy = max(y1, ky)
            ax = min(x1 + w1, kx + kw)
            ay = min(y1 + h1, ky + kh)
            if ax > ix and ay > iy:
                inter = (ax - ix) * (ay - iy)
                if inter / (w1 * h1) > 0.5:
                    overlaps = True
                    break
        if not overlaps:
            kept.append(bbox)

    return kept


def run(input_path: Path, config: dict, output_dir: Path) -> ReportWriter:
    cfg = config_section(config, CHECK_NAME, DEFAULTS)
    standard = cfg["standard"]
    text_size = cfg["text_size"]
    threshold = THRESHOLDS.get((standard, text_size), 4.5)

    img = load_image(input_path)
    report = ReportWriter(CHECK_NAME, config_summary=cfg)
    report.set_metadata("source", str(input_path))
    report.set_metadata("standard", f"{standard} ({text_size} text → {threshold}:1)")

    # Determine regions to check
    regions: list[tuple[tuple[int, int, int, int], str]] = []
    if cfg.get("text_regions"):
        for entry in cfg["text_regions"]:
            bbox = tuple(entry["bbox"])
            label = entry.get("label", f"region_{len(regions)}")
            regions.append((bbox, label))
    elif cfg.get("auto_detect", True):
        auto_bboxes = _auto_detect_text_regions(
            img.gray,
            min_area=cfg["min_region_area"],
            max_area_pct=cfg["max_region_area_pct"],
        )
        regions = [(b, f"auto_{i}") for i, b in enumerate(auto_bboxes)]
        log.info(f"contrast: auto-detected {len(regions)} candidate text regions")

    report.set_metadata("regions_checked", len(regions))

    annotated = img.bgr.copy()
    pass_count = 0
    fail_count = 0

    for bbox, label in regions:
        x, y, w, h = bbox
        # Clamp to image bounds
        x = max(0, x); y = max(0, y)
        w = min(w, img.width - x); h = min(h, img.height - y)
        if w <= 0 or h <= 0:
            continue

        region_pixels = img.rgb[y:y+h, x:x+w]
        fg, bg = _split_fg_bg(region_pixels)
        ratio = wcag_contrast_ratio(fg, bg)

        passed = ratio >= threshold
        if passed:
            pass_count += 1
            draw_bbox(annotated, bbox, color="success", thickness=1, label=f"{ratio:.1f}")
        else:
            fail_count += 1
            # Severity scales with how far below threshold
            delta = threshold - ratio
            severity = Severity.CRITICAL if delta > 1.5 else Severity.HIGH
            report.add_finding(Finding(
                check=CHECK_NAME,
                severity=severity,
                message=f"Contrast {ratio:.2f}:1 fails {standard} {text_size} threshold ({threshold}:1)",
                details=(
                    f"Region `{label}` at ({x}, {y}) {w}×{h}px. "
                    f"Estimated foreground: {rgb_to_hex(fg)}, background: {rgb_to_hex(bg)}."
                ),
                location=bbox,
                measurement={
                    "label": label,
                    "fg": rgb_to_hex(fg),
                    "bg": rgb_to_hex(bg),
                    "contrast_ratio": round(ratio, 2),
                    "threshold": threshold,
                    "standard": standard,
                },
            ))
            draw_bbox(annotated, bbox, color="critical", thickness=2, label=f"{ratio:.1f} FAIL")

    annotated_path = ensure_output_dir(output_dir) / "contrast_annotated.png"
    save_bgr_image(annotated, annotated_path)
    report.add_visual(annotated_path.name, "Text regions — green = pass, red = fail")

    report.set_summary(
        f"Checked {len(regions)} text region(s) against {standard} {text_size} "
        f"threshold ({threshold}:1). Passed: {pass_count}. Failed: {fail_count}."
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
    report_path = output_dir / "contrast_report.md"
    report.write(report_path)
    log.info(f"contrast: wrote report → {report_path}")
    print(f"Report written to {report_path} ({sum(report.counts.values())} finding(s))")


if __name__ == "__main__":
    main()
