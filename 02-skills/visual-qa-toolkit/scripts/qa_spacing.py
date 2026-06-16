"""
qa_spacing.py — Measure gaps between elements and flag orphan spacing values.

Usage:
    python -m scripts.qa_spacing --input screenshot.png --config centric.yaml --output ./qa-out

What it does:
    - Detects UI element bounding boxes.
    - Measures the gaps between adjacent elements (horizontally and vertically).
    - Compares each gap against a configured spacing scale (e.g., [4, 8, 12, 16, 24, 32]).
    - Flags gaps that don't match any scale value within tolerance ("orphan" values).
    - Emits an annotated image with measurement overlays and a markdown report.

What it does not do:
    - It doesn't know which gaps are between related elements (a label and its
      input) vs. unrelated elements (the button and the footer). All adjacent
      gaps are measured. Use findings to inform triage, not to issue verdicts.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from ._common import (
    Element,
    Finding,
    ReportWriter,
    Severity,
    config_section,
    detect_elements,
    draw_bbox,
    draw_measurement,
    ensure_output_dir,
    load_config,
    load_image,
    log,
    save_bgr_image,
)

import numpy as np


CHECK_NAME = "spacing"

DEFAULTS = {
    "base_scale": [4, 8, 12, 16, 24, 32, 48, 64],
    "tolerance_px": 2,
    "min_element_area": 400,
    "max_element_area_pct": 0.5,
    "max_gap_px": 200,           # ignore gaps larger than this (unrelated elements)
    "min_gap_px": 2,             # ignore gaps smaller than this (overlap noise)
    "overlap_threshold_pct": 0.3, # axis overlap required to count as adjacent
}


def _horizontal_overlap_pct(a: Element, b: Element) -> float:
    """How much do two elements overlap vertically (fraction of smaller height)."""
    overlap = max(0, min(a.bottom, b.bottom) - max(a.y, b.y))
    smaller = min(a.h, b.h)
    return overlap / smaller if smaller > 0 else 0.0


def _vertical_overlap_pct(a: Element, b: Element) -> float:
    """How much do two elements overlap horizontally (fraction of smaller width)."""
    overlap = max(0, min(a.right, b.right) - max(a.x, b.x))
    smaller = min(a.w, b.w)
    return overlap / smaller if smaller > 0 else 0.0


def _find_adjacent_horizontal(elements: list[Element], overlap_threshold: float, max_gap: int, min_gap: int) -> list[tuple[Element, Element, int]]:
    """Find pairs of elements that are horizontally adjacent. Returns (left, right, gap)."""
    pairs = []
    sorted_elements = sorted(elements, key=lambda e: e.x)
    for i, left in enumerate(sorted_elements):
        # Find the nearest element to the right with vertical overlap
        candidates = [
            (e, e.x - left.right) for e in sorted_elements[i+1:]
            if e.x >= left.right
            and _horizontal_overlap_pct(left, e) >= overlap_threshold
        ]
        if not candidates:
            continue
        right, gap = min(candidates, key=lambda c: c[1])
        if min_gap <= gap <= max_gap:
            pairs.append((left, right, gap))
    return pairs


def _find_adjacent_vertical(elements: list[Element], overlap_threshold: float, max_gap: int, min_gap: int) -> list[tuple[Element, Element, int]]:
    """Find pairs that are vertically adjacent. Returns (top, bottom, gap)."""
    pairs = []
    sorted_elements = sorted(elements, key=lambda e: e.y)
    for i, top in enumerate(sorted_elements):
        candidates = [
            (e, e.y - top.bottom) for e in sorted_elements[i+1:]
            if e.y >= top.bottom
            and _vertical_overlap_pct(top, e) >= overlap_threshold
        ]
        if not candidates:
            continue
        bottom, gap = min(candidates, key=lambda c: c[1])
        if min_gap <= gap <= max_gap:
            pairs.append((top, bottom, gap))
    return pairs


def _match_scale(gap: int, scale: list[int], tolerance: int) -> tuple[int, int] | None:
    """
    Return (nearest_scale_value, deviation) if gap matches the scale within tolerance.
    Return None if no match (gap is an orphan value).
    """
    deviations = [(s, abs(gap - s)) for s in scale]
    nearest, delta = min(deviations, key=lambda p: p[1])
    if delta <= tolerance:
        return (nearest, delta)
    return None


def run(input_path: Path, config: dict, output_dir: Path) -> ReportWriter:
    cfg = config_section(config, CHECK_NAME, DEFAULTS)
    scale = cfg["base_scale"]
    tolerance = cfg["tolerance_px"]

    img = load_image(input_path)
    elements = detect_elements(
        img,
        min_area=cfg["min_element_area"],
        max_area_pct=cfg["max_element_area_pct"],
    )
    log.info(f"spacing: detected {len(elements)} elements")

    report = ReportWriter(CHECK_NAME, config_summary=cfg)
    report.set_metadata("source", str(input_path))
    report.set_metadata("image_size", f"{img.width}×{img.height}")
    report.set_metadata("elements_detected", len(elements))

    h_pairs = _find_adjacent_horizontal(elements, cfg["overlap_threshold_pct"], cfg["max_gap_px"], cfg["min_gap_px"])
    v_pairs = _find_adjacent_vertical(elements, cfg["overlap_threshold_pct"], cfg["max_gap_px"], cfg["min_gap_px"])

    report.set_metadata("horizontal_gaps_measured", len(h_pairs))
    report.set_metadata("vertical_gaps_measured", len(v_pairs))

    annotated = img.bgr.copy()
    for elem in elements:
        draw_bbox(annotated, elem.bbox(), color="primary", thickness=1)

    orphan_count = 0

    def process_pair(axis: str, a: Element, b: Element, gap: int, start_pt, end_pt):
        nonlocal orphan_count
        match = _match_scale(gap, scale, tolerance)
        if match is None:
            orphan_count += 1
            # Find closest scale value for context
            nearest = min(scale, key=lambda s: abs(gap - s))
            delta = abs(gap - nearest)
            severity = Severity.HIGH if delta > tolerance * 2 else Severity.MEDIUM
            report.add_finding(Finding(
                check=CHECK_NAME,
                severity=severity,
                message=f"{axis.capitalize()} gap of {gap}px doesn't match scale (nearest: {nearest}px, off by {delta}px)",
                details=(
                    f"Gap measured between element at ({a.x}, {a.y}) and element at "
                    f"({b.x}, {b.y}). Scale is {scale}, tolerance ±{tolerance}px."
                ),
                location=(min(a.x, b.x), min(a.y, b.y),
                          max(a.right, b.right) - min(a.x, b.x),
                          max(a.bottom, b.bottom) - min(a.y, b.y)),
                measurement={
                    "axis": axis,
                    "gap_px": gap,
                    "nearest_scale_value": nearest,
                    "deviation_px": delta,
                },
            ))
            draw_measurement(annotated, start_pt, end_pt, f"{gap}px ⚠", color="critical")
        else:
            nearest, delta = match
            draw_measurement(annotated, start_pt, end_pt, f"{gap}px", color="success" if delta == 0 else "warning")

    for left, right, gap in h_pairs:
        mid_y = (max(left.y, right.y) + min(left.bottom, right.bottom)) // 2
        process_pair("horizontal", left, right, gap, (left.right, mid_y), (right.x, mid_y))

    for top, bottom, gap in v_pairs:
        mid_x = (max(top.x, bottom.x) + min(top.right, bottom.right)) // 2
        process_pair("vertical", top, bottom, gap, (mid_x, top.bottom), (mid_x, bottom.y))

    annotated_path = ensure_output_dir(output_dir) / "spacing_annotated.png"
    save_bgr_image(annotated, annotated_path)
    report.add_visual(annotated_path.name, "Measured gaps — green/orange = on scale, red = orphan value")

    total_gaps = len(h_pairs) + len(v_pairs)
    report.set_summary(
        f"Measured {total_gaps} gap(s) ({len(h_pairs)} horizontal, {len(v_pairs)} vertical). "
        f"Scale: {scale}. Tolerance: ±{tolerance}px. "
        f"Orphan values: {orphan_count}."
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
    report_path = output_dir / "spacing_report.md"
    report.write(report_path)
    log.info(f"spacing: wrote report → {report_path}")
    print(f"Report written to {report_path} ({sum(report.counts.values())} finding(s))")


if __name__ == "__main__":
    main()
