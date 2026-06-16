"""
qa_icon_consistency.py — Analyze a set of icon exports for construction consistency.

Usage:
    python -m scripts.qa_icon_consistency --input ./icons_folder --config centric.yaml --output ./qa-out

What it does:
    - Scans a folder of icon files (PNG, SVG rendered to PNG).
    - For each icon: computes bounding box dimensions, visual weight
      (fraction of non-transparent / non-background pixels), stroke width
      approximation via distance transform, and centroid position within
      the canvas.
    - Flags outliers — icons whose measurements deviate from the set's
      central tendency beyond configured thresholds.
    - Emits a comparison grid visualization and a markdown report with
      per-icon measurements.

What it does not do:
    - For SVG input, a rendered PNG is required. The script does not parse
      SVG geometry directly; it treats icons as images. (Path-level analysis
      belongs in `variable-icon-font-architect` skill, not here.)
    - It cannot tell you whether an icon is *conceptually* consistent with
      the set. A crown and a key are both valid icons at the same weight
      and scale. It measures construction parameters, not meaning.
"""
from __future__ import annotations

import argparse
from pathlib import Path
from statistics import mean, stdev

import cv2
import numpy as np

from ._common import (
    Finding,
    ReportWriter,
    Severity,
    config_section,
    ensure_output_dir,
    load_config,
    log,
    save_bgr_image,
)


CHECK_NAME = "icon_consistency"

DEFAULTS = {
    "canvas_size": 24,                     # expected icon canvas (used for normalization)
    "extensions": [".png"],                # accepted file extensions
    "background_threshold": 240,           # pixel value above this = background
    "alpha_threshold": 10,                 # for PNGs with alpha, below this = transparent
    "bbox_size_stdev_threshold": 2.0,      # Z-score threshold for bbox size outliers
    "weight_stdev_threshold": 2.0,         # Z-score for weight outliers
    "stroke_stdev_threshold": 2.0,         # Z-score for stroke outliers
    "max_icons_in_grid": 64,               # grid visualization cap
}


def _load_icon_foreground(path: Path, alpha_threshold: int, bg_threshold: int) -> np.ndarray:
    """Load icon and return a binary mask of the foreground (1) vs. background (0)."""
    img = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
    if img is None:
        raise ValueError(f"Could not read icon: {path}")

    if img.ndim == 3 and img.shape[2] == 4:
        # RGBA — use alpha channel
        alpha = img[:, :, 3]
        mask = (alpha > alpha_threshold).astype(np.uint8)
    elif img.ndim == 3:
        # BGR — threshold grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        mask = (gray < bg_threshold).astype(np.uint8)
    else:
        # Grayscale
        mask = (img < bg_threshold).astype(np.uint8)

    return mask


def _measure_icon(mask: np.ndarray) -> dict:
    """Compute construction metrics for an icon from its binary mask."""
    h, w = mask.shape
    total_pixels = h * w
    fg_pixels = int(mask.sum())

    if fg_pixels == 0:
        return {
            "canvas_w": w, "canvas_h": h,
            "bbox_x": 0, "bbox_y": 0, "bbox_w": 0, "bbox_h": 0,
            "weight_pct": 0.0,
            "stroke_width_approx": 0.0,
            "centroid_x": w / 2, "centroid_y": h / 2,
            "optical_offset_x": 0, "optical_offset_y": 0,
            "empty": True,
        }

    # Bounding box of foreground
    ys, xs = np.where(mask > 0)
    x0, x1 = int(xs.min()), int(xs.max())
    y0, y1 = int(ys.min()), int(ys.max())
    bbox_w, bbox_h = x1 - x0 + 1, y1 - y0 + 1

    # Visual weight — fg pixels as pct of total canvas
    weight_pct = 100.0 * fg_pixels / total_pixels

    # Stroke width approximation via distance transform on the fg
    dist = cv2.distanceTransform(mask, cv2.DIST_L2, 3)
    # Approximate stroke as 2 * median of distances > 0
    nonzero_dists = dist[dist > 0]
    stroke = float(2 * np.median(nonzero_dists)) if nonzero_dists.size > 0 else 0.0

    # Centroid
    moments = cv2.moments(mask.astype(np.uint8))
    if moments["m00"] > 0:
        cx = moments["m10"] / moments["m00"]
        cy = moments["m01"] / moments["m00"]
    else:
        cx, cy = w / 2, h / 2

    return {
        "canvas_w": w, "canvas_h": h,
        "bbox_x": x0, "bbox_y": y0,
        "bbox_w": bbox_w, "bbox_h": bbox_h,
        "weight_pct": round(weight_pct, 2),
        "stroke_width_approx": round(stroke, 2),
        "centroid_x": round(cx, 2),
        "centroid_y": round(cy, 2),
        "optical_offset_x": round(cx - w / 2, 2),
        "optical_offset_y": round(cy - h / 2, 2),
        "empty": False,
    }


def _z_score(value: float, values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    m = mean(values)
    s = stdev(values)
    if s == 0:
        return 0.0
    return abs(value - m) / s


def run(input_path: Path, config: dict, output_dir: Path) -> ReportWriter:
    cfg = config_section(config, CHECK_NAME, DEFAULTS)

    report = ReportWriter(CHECK_NAME, config_summary=cfg)

    # Accept either a directory or a list-of-files (directory for batch)
    if input_path.is_dir():
        exts = tuple(e.lower() for e in cfg["extensions"])
        icon_paths = sorted([
            p for p in input_path.rglob("*")
            if p.is_file() and p.suffix.lower() in exts
        ])
    elif input_path.is_file():
        icon_paths = [input_path]
    else:
        raise FileNotFoundError(f"Input path not found: {input_path}")

    report.set_metadata("icon_count", len(icon_paths))
    report.set_metadata("source", str(input_path))

    if len(icon_paths) < 2:
        report.set_summary(
            f"Only {len(icon_paths)} icon(s) found — need at least 2 for outlier analysis."
        )
        return report

    # Measure all icons
    measurements: list[tuple[Path, dict]] = []
    for p in icon_paths:
        try:
            mask = _load_icon_foreground(p, cfg["alpha_threshold"], cfg["background_threshold"])
            m = _measure_icon(mask)
            measurements.append((p, m))
        except Exception as e:
            log.warning(f"Failed to measure {p.name}: {e}")

    if not measurements:
        report.set_summary("No icons could be measured.")
        return report

    # Gather distributions for outlier detection
    weights = [m["weight_pct"] for _, m in measurements if not m["empty"]]
    strokes = [m["stroke_width_approx"] for _, m in measurements if not m["empty"]]
    bbox_widths = [m["bbox_w"] for _, m in measurements if not m["empty"]]
    bbox_heights = [m["bbox_h"] for _, m in measurements if not m["empty"]]

    # Per-icon outlier flags
    for path, m in measurements:
        if m["empty"]:
            report.add_finding(Finding(
                check=CHECK_NAME,
                severity=Severity.MEDIUM,
                message=f"{path.name}: empty or fully transparent",
                details="Icon has no detectable foreground pixels. Likely an export error.",
                measurement={"file": path.name},
            ))
            continue

        # Weight outlier
        z_weight = _z_score(m["weight_pct"], weights)
        if z_weight > cfg["weight_stdev_threshold"]:
            report.add_finding(Finding(
                check=CHECK_NAME,
                severity=Severity.MEDIUM if z_weight < 3 else Severity.HIGH,
                message=f"{path.name}: visual weight outlier ({m['weight_pct']:.1f}%, z={z_weight:.1f})",
                details=(
                    f"Mean weight across set: {mean(weights):.1f}%, "
                    f"stdev: {stdev(weights):.1f}%."
                ),
                measurement={
                    "file": path.name,
                    "weight_pct": m["weight_pct"],
                    "mean_weight": round(mean(weights), 2),
                    "z_score": round(z_weight, 2),
                },
            ))

        # Stroke outlier
        z_stroke = _z_score(m["stroke_width_approx"], strokes)
        if z_stroke > cfg["stroke_stdev_threshold"]:
            report.add_finding(Finding(
                check=CHECK_NAME,
                severity=Severity.MEDIUM if z_stroke < 3 else Severity.HIGH,
                message=f"{path.name}: stroke width outlier ({m['stroke_width_approx']:.2f}px, z={z_stroke:.1f})",
                details=(
                    f"Mean stroke across set: {mean(strokes):.2f}px, "
                    f"stdev: {stdev(strokes):.2f}px. "
                    f"(Stroke is approximated via distance transform, not exact.)"
                ),
                measurement={
                    "file": path.name,
                    "stroke_width": m["stroke_width_approx"],
                    "mean_stroke": round(mean(strokes), 2),
                    "z_score": round(z_stroke, 2),
                },
            ))

        # Bbox outlier
        z_bw = _z_score(m["bbox_w"], bbox_widths)
        z_bh = _z_score(m["bbox_h"], bbox_heights)
        if z_bw > cfg["bbox_size_stdev_threshold"] or z_bh > cfg["bbox_size_stdev_threshold"]:
            report.add_finding(Finding(
                check=CHECK_NAME,
                severity=Severity.LOW,
                message=f"{path.name}: bbox size outlier ({m['bbox_w']}×{m['bbox_h']}px)",
                measurement={
                    "file": path.name,
                    "bbox_w": m["bbox_w"],
                    "bbox_h": m["bbox_h"],
                    "mean_bbox": f"{mean(bbox_widths):.0f}×{mean(bbox_heights):.0f}",
                    "z_scores": {"w": round(z_bw, 2), "h": round(z_bh, 2)},
                },
            ))

    # Distribution metadata
    report.set_metadata("weight_distribution", {
        "mean": round(mean(weights), 2),
        "stdev": round(stdev(weights), 2) if len(weights) > 1 else 0,
        "min": round(min(weights), 2),
        "max": round(max(weights), 2),
    })
    report.set_metadata("stroke_distribution", {
        "mean": round(mean(strokes), 2),
        "stdev": round(stdev(strokes), 2) if len(strokes) > 1 else 0,
        "min": round(min(strokes), 2),
        "max": round(max(strokes), 2),
    })

    # Grid visualization of the icon set
    grid = _make_icon_grid(measurements[:cfg["max_icons_in_grid"]], tile_size=96)
    if grid is not None:
        grid_path = ensure_output_dir(output_dir) / "icon_consistency_grid.png"
        save_bgr_image(grid, grid_path)
        report.add_visual(grid_path.name, "Icon set comparison grid")

    report.set_summary(
        f"Analyzed {len(measurements)} icon(s). "
        f"Weight: {mean(weights):.1f}% ± {stdev(weights):.1f}%. "
        f"Stroke: {mean(strokes):.2f}px ± {stdev(strokes):.2f}px. "
        f"Outliers flagged: {sum(report.counts.values())}."
    )

    return report


def _make_icon_grid(measurements: list[tuple[Path, dict]], tile_size: int = 96) -> np.ndarray | None:
    """Composite all icons into a grid for visual inspection."""
    if not measurements:
        return None

    cols = min(8, len(measurements))
    rows = (len(measurements) + cols - 1) // cols
    label_h = 14
    tile_h = tile_size + label_h

    canvas = np.ones((rows * tile_h + 4, cols * tile_size + 4, 3), dtype=np.uint8) * 245

    for idx, (path, _m) in enumerate(measurements):
        row = idx // cols
        col = idx % cols
        y = row * tile_h + 2
        x = col * tile_size + 2

        img = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
        if img is None:
            continue
        if img.ndim == 3 and img.shape[2] == 4:
            # Composite over white
            alpha = img[:, :, 3:4].astype(np.float32) / 255.0
            bgr = img[:, :, :3].astype(np.float32)
            white = np.ones_like(bgr) * 255
            img = (alpha * bgr + (1 - alpha) * white).astype(np.uint8)

        resized = cv2.resize(img, (tile_size, tile_size))
        canvas[y:y + tile_size, x:x + tile_size] = resized

        name = path.name[:14]
        cv2.putText(
            canvas, name, (x + 2, y + tile_size + label_h - 2),
            cv2.FONT_HERSHEY_SIMPLEX, 0.32, (60, 60, 60), 1, cv2.LINE_AA,
        )

    return canvas


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--input", required=True, help="Folder of icon files (or a single file)")
    parser.add_argument("--config", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    config = load_config(args.config)
    output_dir = ensure_output_dir(args.output)
    report = run(Path(args.input), config, output_dir)
    report_path = output_dir / "icon_consistency_report.md"
    report.write(report_path)
    log.info(f"icon_consistency: wrote report → {report_path}")
    print(f"Report written to {report_path} ({sum(report.counts.values())} finding(s))")


if __name__ == "__main__":
    main()
