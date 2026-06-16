"""
qa_alignment.py — Detect elements and flag edge misalignments.

Usage:
    python -m scripts.qa_alignment --input screenshot.png --config centric.yaml --output ./qa-out

What it does:
    - Detects UI element bounding boxes via edge + contour analysis.
    - Groups elements that should plausibly share an edge (same column of
      left-edges, same row of top-edges).
    - Within each group, flags any element whose edge deviates from the
      group median by more than the configured tolerance.
    - Emits a markdown report and an annotated image with reference lines
      drawn through the detected alignment axes.

What it does not do:
    - It cannot know which elements are *supposed* to align. It infers from
      edge clustering. Elements that happen to be near each other but are
      semantically unrelated may be grouped wrongly. Treat findings as signal,
      not verdicts — false positives are normal.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path

from ._common import (
    ANNOTATION_COLORS,
    Element,
    Finding,
    ReportWriter,
    Severity,
    config_section,
    detect_elements,
    draw_bbox,
    ensure_output_dir,
    load_config,
    load_image,
    log,
    save_bgr_image,
)

import cv2
import numpy as np


CHECK_NAME = "alignment"

DEFAULTS = {
    "tolerance_px": 1,           # deviation from cluster median that triggers a flag
    "cluster_tolerance_px": 4,   # max distance for edges to be considered "the same" alignment axis
    "min_cluster_size": 2,       # need at least N elements sharing an edge to flag
    "min_element_area": 400,     # minimum area to consider (filters out noise)
    "max_element_area_pct": 0.5, # ignore huge elements (likely containers)
    "edges_to_check": ["left", "right", "top", "bottom"],
}


def _cluster_edges(
    edge_values: list[tuple[int, Element]],
    cluster_tolerance: int,
) -> list[list[tuple[int, Element]]]:
    """
    Group (edge_value, element) pairs into clusters by proximity.
    Values within `cluster_tolerance` pixels of each other join the same cluster.
    """
    if not edge_values:
        return []
    sorted_pairs = sorted(edge_values, key=lambda p: p[0])
    clusters: list[list[tuple[int, Element]]] = [[sorted_pairs[0]]]
    for pair in sorted_pairs[1:]:
        last_cluster = clusters[-1]
        last_median = np.median([p[0] for p in last_cluster])
        if abs(pair[0] - last_median) <= cluster_tolerance:
            last_cluster.append(pair)
        else:
            clusters.append([pair])
    return clusters


def run(input_path: Path, config: dict, output_dir: Path) -> ReportWriter:
    cfg = config_section(config, CHECK_NAME, DEFAULTS)
    tolerance = cfg["tolerance_px"]
    cluster_tol = cfg["cluster_tolerance_px"]
    min_cluster = cfg["min_cluster_size"]

    img = load_image(input_path)
    elements = detect_elements(
        img,
        min_area=cfg["min_element_area"],
        max_area_pct=cfg["max_element_area_pct"],
    )
    log.info(f"alignment: detected {len(elements)} elements")

    report = ReportWriter(CHECK_NAME, config_summary=cfg)
    report.set_metadata("source", str(input_path))
    report.set_metadata("image_size", f"{img.width}×{img.height}")
    report.set_metadata("elements_detected", len(elements))

    # For each edge type, collect values per element and cluster them
    edge_accessors = {
        "left":   lambda e: e.x,
        "right":  lambda e: e.right,
        "top":    lambda e: e.y,
        "bottom": lambda e: e.bottom,
    }

    all_flagged_elements: set[int] = set()
    cluster_lines: list[tuple[str, int]] = []  # (axis_direction, coord)

    for edge_name in cfg["edges_to_check"]:
        accessor = edge_accessors[edge_name]
        pairs = [(accessor(e), e) for e in elements]
        clusters = _cluster_edges(pairs, cluster_tol)

        for cluster in clusters:
            if len(cluster) < min_cluster:
                continue
            values = [p[0] for p in cluster]
            median = int(np.median(values))
            spread = max(values) - min(values)

            # Record the alignment axis for visualization
            direction = "vertical" if edge_name in ("left", "right") else "horizontal"
            cluster_lines.append((direction, median))

            if spread > tolerance:
                # Find elements deviating from median
                for value, elem in cluster:
                    deviation = abs(value - median)
                    if deviation > tolerance:
                        severity = (
                            Severity.HIGH if deviation > tolerance * 3
                            else Severity.MEDIUM
                        )
                        report.add_finding(Finding(
                            check=CHECK_NAME,
                            severity=severity,
                            message=(
                                f"{edge_name.capitalize()}-edge off by {deviation}px "
                                f"(tolerance {tolerance}px)"
                            ),
                            details=(
                                f"Element at ({elem.x}, {elem.y}) {elem.w}×{elem.h}px "
                                f"has a {edge_name} edge at {value}px, but shares an "
                                f"alignment axis with {len(cluster)-1} other element(s) "
                                f"whose median {edge_name} edge is at {median}px."
                            ),
                            location=elem.bbox(),
                            measurement={
                                "edge": edge_name,
                                "element_value": value,
                                "cluster_median": median,
                                "deviation_px": deviation,
                                "cluster_size": len(cluster),
                            },
                        ))
                        all_flagged_elements.add(id(elem))

    # Annotate
    annotated = img.bgr.copy()

    # Draw alignment axes first (so bboxes overlay)
    guide_rgb = ANNOTATION_COLORS["guide"]
    guide_bgr = (guide_rgb[2], guide_rgb[1], guide_rgb[0])
    for direction, coord in cluster_lines:
        if direction == "vertical":
            cv2.line(annotated, (coord, 0), (coord, img.height), guide_bgr, 1, cv2.LINE_AA)
        else:
            cv2.line(annotated, (0, coord), (img.width, coord), guide_bgr, 1, cv2.LINE_AA)

    # Then element bboxes, colored by flagged status
    for i, elem in enumerate(elements):
        color = "critical" if id(elem) in all_flagged_elements else "primary"
        draw_bbox(annotated, elem.bbox(), color=color, thickness=2)

    annotated_path = ensure_output_dir(output_dir) / "alignment_annotated.png"
    save_bgr_image(annotated, annotated_path)
    report.add_visual(annotated_path.name, "Detected elements with alignment axes (violet)")

    # Summary
    total = sum(report.counts.values())
    if total == 0:
        report.set_summary(
            f"Scanned {len(elements)} elements across {len(cluster_lines)} alignment axes. "
            f"No misalignments beyond ±{tolerance}px."
        )
    else:
        report.set_summary(
            f"Scanned {len(elements)} elements across {len(cluster_lines)} alignment axes. "
            f"Flagged {total} edge deviation(s) beyond ±{tolerance}px."
        )

    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--input", required=True, help="Path to screenshot image")
    parser.add_argument("--config", required=True, help="Path to YAML config")
    parser.add_argument("--output", required=True, help="Output directory for report and annotations")
    args = parser.parse_args()

    config = load_config(args.config)
    output_dir = ensure_output_dir(args.output)
    report = run(Path(args.input), config, output_dir)
    report_path = output_dir / "alignment_report.md"
    report.write(report_path)
    log.info(f"alignment: wrote report → {report_path}")
    print(f"Report written to {report_path} ({sum(report.counts.values())} finding(s))")


if __name__ == "__main__":
    main()
