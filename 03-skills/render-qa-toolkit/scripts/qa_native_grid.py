"""
qa_native_grid.py — Split a PNG into 1:1 native tiles; reject undersized "native" captures.

Usage:
    python -m scripts.qa_native_grid --input frame.png --config configs/default.yaml --output ./qa-out
    python -m scripts.qa_native_grid --input frame.png --config configs/default.yaml --output ./qa-out --labeled-native
"""
from __future__ import annotations

import argparse
import math
from pathlib import Path

import cv2
import numpy as np

from ._common import (
    Finding,
    ReportWriter,
    Severity,
    config_section,
    ensure_output_dir,
    load_config,
    load_image,
    log,
    save_bgr_image,
)

CHECK_NAME = "native_grid"

DEFAULTS = {
    "tile_size": 512,            # 1:1 tile edge in px
    "min_native_width": 1280,    # reject if declared native but smaller
    "min_native_height": 720,
    "downsample_warn_width": 800,  # width < this + labeled native → warn (Z-01)
    "grid_cols": None,           # auto from width / tile_size when null
    "write_tiles": True,
    "write_montage": True,
}


def run(
    input_path: Path,
    config: dict,
    output_dir: Path,
    labeled_native: bool = False,
) -> ReportWriter:
    cfg = config_section(config, CHECK_NAME, DEFAULTS)
    img = load_image(input_path)
    report = ReportWriter(CHECK_NAME, config_summary={**cfg, "labeled_native": labeled_native})
    report.set_metadata("input", str(input_path))
    report.set_metadata("size", f"{img.width}×{img.height}")

    tile = int(cfg["tile_size"])
    min_w = int(cfg["min_native_width"])
    min_h = int(cfg["min_native_height"])
    warn_w = int(cfg["downsample_warn_width"])

    # Downsample / false-native gates
    if labeled_native and img.width < warn_w:
        report.add_finding(Finding(
            check=CHECK_NAME,
            severity=Severity.HIGH,
            message=(
                f"Image width {img.width}px < {warn_w} and labeled native — "
                "likely a downsampled locator, not verdict pixels"
            ),
            details=(
                "Perception Integrity (#10) / ledger Z-01: never judge fine detail "
                "from a scaled preview. Recapture at true native resolution."
            ),
            measurement={"width": img.width, "height": img.height},
            ledger_id="Z-01",
        ))

    if labeled_native and (img.width < min_w or img.height < min_h):
        report.add_finding(Finding(
            check=CHECK_NAME,
            severity=Severity.CRITICAL,
            message=(
                f"Declared native capture {img.width}×{img.height} is below "
                f"configured minimum {min_w}×{min_h}"
            ),
            details="Reject this capture as native evidence. Re-run with w/h/dpr matching the official pose.",
            measurement={
                "width": img.width, "height": img.height,
                "min_native_width": min_w, "min_native_height": min_h,
            },
            ledger_id="Z-01",
        ))
        report.set_summary(
            f"REJECTED as native: {img.width}×{img.height} < {min_w}×{min_h}."
        )
        # Still write a single-tile preview for locator use
    elif img.width < min_w or img.height < min_h:
        report.add_finding(Finding(
            check=CHECK_NAME,
            severity=Severity.MEDIUM,
            message=(
                f"Image {img.width}×{img.height} is below typical native min "
                f"{min_w}×{min_h} (not labeled native — informational)"
            ),
            measurement={"width": img.width, "height": img.height},
        ))

    cols = cfg.get("grid_cols") or max(1, math.ceil(img.width / tile))
    rows = max(1, math.ceil(img.height / tile))
    report.set_metadata("grid", f"{cols}×{rows} tiles of {tile}px")

    out = ensure_output_dir(output_dir)
    tiles_dir = out / "native_tiles"
    if cfg.get("write_tiles", True):
        tiles_dir.mkdir(parents=True, exist_ok=True)

    tile_paths: list[Path] = []
    for r in range(rows):
        for c in range(cols):
            x0, y0 = c * tile, r * tile
            x1, y1 = min(x0 + tile, img.width), min(y0 + tile, img.height)
            crop = img.bgr[y0:y1, x0:x1]
            # Pad to square tile for consistent review
            canvas = np.zeros((tile, tile, 3), dtype=np.uint8)
            canvas[: y1 - y0, : x1 - x0] = crop
            name = f"tile_r{r:02d}_c{c:02d}.png"
            if cfg.get("write_tiles", True):
                path = tiles_dir / name
                save_bgr_image(canvas, path)
                tile_paths.append(path)

    report.add_finding(Finding(
        check=CHECK_NAME,
        severity=Severity.INFO,
        message=f"Wrote {len(tile_paths)} tile(s) at {tile}×{tile} (grid {cols}×{rows})",
        measurement={"tiles": len(tile_paths), "tile_size": tile, "cols": cols, "rows": rows},
    ))

    if cfg.get("write_montage", True) and tile_paths:
        # Compact contact sheet (scaled for overview only — tiles are the truth)
        thumb = 128
        sheet = np.zeros((rows * thumb, cols * thumb, 3), dtype=np.uint8)
        for r in range(rows):
            for c in range(cols):
                idx = r * cols + c
                if idx >= len(tile_paths):
                    continue
                t = cv2.imread(str(tile_paths[idx]))
                if t is None:
                    continue
                small = cv2.resize(t, (thumb, thumb), interpolation=cv2.INTER_AREA)
                sheet[r * thumb:(r + 1) * thumb, c * thumb:(c + 1) * thumb] = small
        montage_path = out / "native_grid_montage.png"
        save_bgr_image(sheet, montage_path)
        report.add_visual(montage_path.name, "Tile montage (locator only — judge tiles at 1:1)")

    if not report.summary_text:
        report.set_summary(
            f"{img.width}×{img.height} → {cols}×{rows} tiles of {tile}px "
            f"({len(tile_paths)} written)."
        )
    return report


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Split PNG into 1:1 native tiles; gate undersized native claims."
    )
    parser.add_argument("--input", required=True, help="PNG (or other image) path")
    parser.add_argument("--config", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument(
        "--labeled-native", action="store_true",
        help="User asserts this capture is native-resolution evidence. "
             "Triggers min-size reject and <800px downsample warn.",
    )
    args = parser.parse_args()

    config = load_config(args.config)
    output_dir = ensure_output_dir(args.output)
    report = run(Path(args.input), config, output_dir, labeled_native=args.labeled_native)
    report_path = output_dir / f"{CHECK_NAME}_report.md"
    report.write(report_path)
    log.info(f"{CHECK_NAME}: wrote report → {report_path}")
    print(f"Report written to {report_path} ({sum(report.counts.values())} finding(s))")


if __name__ == "__main__":
    main()
