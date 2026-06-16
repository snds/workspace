"""
qa_grid_overlay.py — Overlay grid, ruler, and baseline guides onto a screenshot.

Usage:
    python -m scripts.qa_grid_overlay --input screenshot.png --config centric.yaml --output ./qa-out

What it does:
    - Renders a ruler along the top and left edges.
    - Overlays a column grid per the config (columns, column width, gutter, margin).
    - Optionally overlays a baseline grid (every N px) for vertical rhythm checking.
    - Produces a single annotated image — this is a visualization tool, not a check.
      It does not emit findings; it produces an artifact you look at.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import cv2
import numpy as np

from ._common import (
    ANNOTATION_COLORS,
    ReportWriter,
    Severity,
    Finding,
    config_section,
    ensure_output_dir,
    load_config,
    load_image,
    log,
    save_bgr_image,
)


CHECK_NAME = "grid_overlay"

DEFAULTS = {
    "columns": 12,
    "column_width_px": None,       # if None, computed from width / columns / gutter / margin
    "gutter_px": 24,
    "margin_px": 48,
    "baseline_px": 8,              # baseline grid spacing; 0 to disable
    "ruler_spacing_px": 50,        # ruler tick every N px
    "ruler_major_spacing_px": 100,
    "column_fill_alpha": 0.08,
    "draw_column_fill": True,
    "draw_column_edges": True,
    "draw_baseline": True,
    "draw_ruler": True,
}


def _draw_ruler(image: np.ndarray, spacing: int, major_spacing: int) -> None:
    """Draw ruler ticks on top and left edges."""
    h, w = image.shape[:2]
    neutral = ANNOTATION_COLORS["neutral"]
    neutral_bgr = (neutral[2], neutral[1], neutral[0])

    # Background strip for readability
    cv2.rectangle(image, (0, 0), (w, 16), (245, 245, 245), -1)
    cv2.rectangle(image, (0, 0), (20, h), (245, 245, 245), -1)

    # Top ruler
    for x in range(0, w, spacing):
        tick_h = 8 if x % major_spacing == 0 else 4
        cv2.line(image, (x, 0), (x, tick_h), neutral_bgr, 1)
        if x % major_spacing == 0 and x > 0:
            cv2.putText(
                image, str(x), (x + 2, 12),
                cv2.FONT_HERSHEY_SIMPLEX, 0.32, neutral_bgr, 1, cv2.LINE_AA,
            )

    # Left ruler
    for y in range(0, h, spacing):
        tick_w = 8 if y % major_spacing == 0 else 4
        cv2.line(image, (0, y), (tick_w, y), neutral_bgr, 1)
        if y % major_spacing == 0 and y > 16:
            cv2.putText(
                image, str(y), (2, y - 2),
                cv2.FONT_HERSHEY_SIMPLEX, 0.32, neutral_bgr, 1, cv2.LINE_AA,
            )


def _draw_columns(
    image: np.ndarray,
    canvas_shape: tuple[int, int],
    columns: int,
    margin: int,
    gutter: int,
    col_width: int | None,
    fill_alpha: float,
    draw_fill: bool,
    draw_edges: bool,
) -> tuple[int, int]:
    """Draw a column grid. Returns (computed_col_width, content_width)."""
    h, w = canvas_shape
    content_w = w - 2 * margin
    if col_width is None:
        # content = col * cw + (col - 1) * gutter  →  cw = (content - (col-1) * gutter) / col
        col_width = (content_w - (columns - 1) * gutter) // columns
    actual_content_w = col_width * columns + gutter * (columns - 1)

    guide = ANNOTATION_COLORS["guide"]
    guide_bgr = (guide[2], guide[1], guide[0])

    if draw_fill:
        # Column fill overlay
        overlay = image.copy()
        for c in range(columns):
            cx = margin + c * (col_width + gutter)
            cv2.rectangle(overlay, (cx, 0), (cx + col_width, h), guide_bgr, -1)
        cv2.addWeighted(overlay, fill_alpha, image, 1 - fill_alpha, 0, image)

    if draw_edges:
        for c in range(columns):
            cx = margin + c * (col_width + gutter)
            cv2.line(image, (cx, 0), (cx, h), guide_bgr, 1)
            cv2.line(image, (cx + col_width, 0), (cx + col_width, h), guide_bgr, 1)

    return col_width, actual_content_w


def _draw_baseline(image: np.ndarray, spacing: int) -> None:
    """Draw a baseline grid."""
    h, w = image.shape[:2]
    guide = ANNOTATION_COLORS["guide"]
    guide_bgr = (guide[2], guide[1], guide[0])
    for y in range(spacing, h, spacing):
        # dotted line
        for x in range(0, w, 4):
            image[y, x:min(x + 2, w)] = guide_bgr


def run(input_path: Path, config: dict, output_dir: Path) -> ReportWriter:
    cfg = config_section(config, CHECK_NAME, DEFAULTS)

    img = load_image(input_path)
    report = ReportWriter(CHECK_NAME, config_summary=cfg)
    report.set_metadata("source", str(input_path))
    report.set_metadata("image_size", f"{img.width}×{img.height}")

    # Start from the original
    annotated = img.bgr.copy()

    if cfg.get("draw_baseline", True) and cfg.get("baseline_px", 0) > 0:
        _draw_baseline(annotated, cfg["baseline_px"])

    col_w, content_w = _draw_columns(
        annotated,
        (img.height, img.width),
        columns=cfg["columns"],
        margin=cfg["margin_px"],
        gutter=cfg["gutter_px"],
        col_width=cfg.get("column_width_px"),
        fill_alpha=cfg["column_fill_alpha"],
        draw_fill=cfg.get("draw_column_fill", True),
        draw_edges=cfg.get("draw_column_edges", True),
    )

    if cfg.get("draw_ruler", True):
        _draw_ruler(annotated, cfg["ruler_spacing_px"], cfg["ruler_major_spacing_px"])

    # Caption with grid summary
    caption = (
        f"Grid: {cfg['columns']} cols × {col_w}px "
        f"(gutter {cfg['gutter_px']}px, margin {cfg['margin_px']}px)"
    )
    cv2.putText(
        annotated, caption, (24, img.height - 12),
        cv2.FONT_HERSHEY_SIMPLEX, 0.45,
        (ANNOTATION_COLORS["neutral"][2],) * 1 + ANNOTATION_COLORS["neutral"][1::-1],
        1, cv2.LINE_AA,
    )

    annotated_path = ensure_output_dir(output_dir) / "grid_overlay.png"
    save_bgr_image(annotated, annotated_path)
    report.add_visual(annotated_path.name, caption)

    # Informational finding noting the computed grid
    content_fits = content_w <= (img.width - 2 * cfg["margin_px"])
    report.add_finding(Finding(
        check=CHECK_NAME,
        severity=Severity.INFO,
        message=f"Applied {cfg['columns']}-column grid at {col_w}px/column",
        details=(
            f"Content width: {content_w}px. "
            f"Margins: {cfg['margin_px']}px each side. "
            f"Gutter: {cfg['gutter_px']}px. "
            f"{'Fits within canvas.' if content_fits else 'NOTE: computed grid exceeds canvas width.'}"
        ),
        measurement={
            "columns": cfg["columns"],
            "column_width_px": col_w,
            "gutter_px": cfg["gutter_px"],
            "margin_px": cfg["margin_px"],
            "content_width_px": content_w,
            "canvas_width_px": img.width,
        },
    ))

    report.set_summary(
        f"Visualization only — no checks performed. "
        f"Applied {cfg['columns']}-column grid at {col_w}px/column with "
        f"{cfg['gutter_px']}px gutters and {cfg['margin_px']}px margins. "
        f"{'Baseline: ' + str(cfg['baseline_px']) + 'px.' if cfg.get('draw_baseline') and cfg.get('baseline_px') else ''}"
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
    report_path = output_dir / "grid_overlay_report.md"
    report.write(report_path)
    log.info(f"grid_overlay: wrote report → {report_path}")
    print(f"Report written to {report_path}")


if __name__ == "__main__":
    main()
