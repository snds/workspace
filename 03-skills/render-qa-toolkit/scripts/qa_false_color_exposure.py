"""
qa_false_color_exposure.py — Write a false-color exposure overlay PNG.

Usage:
    python -m scripts.qa_false_color_exposure --input frame.png --config configs/default.yaml --output ./qa-out
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
    ensure_output_dir,
    load_config,
    load_image,
    log,
    luminance_rel,
    save_bgr_image,
)

CHECK_NAME = "false_color_exposure"

DEFAULTS = {
    "overlay_alpha": 0.55,
    # Stops: (luminance upper bound, BGR color) — classic exposure zebra-ish map
    "stops": [
        [0.02, [40, 40, 180]],     # crushed — blue
        [0.10, [180, 80, 40]],     # deep shadow — cyan-ish in BGR terms tuned
        [0.35, [40, 160, 40]],     # mid — green
        [0.70, [40, 200, 220]],    # bright — yellow
        [0.95, [40, 40, 220]],     # near clip — red
        [1.01, [255, 255, 255]],   # clipped — white
    ],
}


def _false_color(lum: np.ndarray, stops: list) -> np.ndarray:
    h, w = lum.shape
    out = np.zeros((h, w, 3), dtype=np.uint8)
    prev = 0.0
    for upper, bgr in stops:
        mask = (lum >= prev) & (lum < float(upper))
        out[mask] = np.array(bgr, dtype=np.uint8)
        prev = float(upper)
    return out


def run(input_path: Path, config: dict, output_dir: Path) -> ReportWriter:
    cfg = config_section(config, CHECK_NAME, DEFAULTS)
    img = load_image(input_path)
    report = ReportWriter(CHECK_NAME, config_summary={k: v for k, v in cfg.items() if k != "stops"})
    report.set_metadata("input", str(input_path))

    lum = luminance_rel(img.rgb)
    fc = _false_color(lum, cfg["stops"])
    alpha = float(cfg.get("overlay_alpha", 0.55))
    overlay = cv2.addWeighted(img.bgr, 1.0 - alpha, fc, alpha, 0)

    out = ensure_output_dir(output_dir)
    pure_path = out / "false_color_map.png"
    overlay_path = out / "false_color_exposure.png"
    save_bgr_image(fc, pure_path)
    save_bgr_image(overlay, overlay_path)
    report.add_visual(pure_path.name, "False-color luminance map")
    report.add_visual(overlay_path.name, "Exposure overlay on source")

    clip_pct = 100.0 * float((lum >= 0.98).sum()) / lum.size
    crush_pct = 100.0 * float((lum <= 0.02).sum()) / lum.size
    report.add_finding(Finding(
        check=CHECK_NAME,
        severity=Severity.INFO,
        message=f"False-color map written — crush≤0.02: {crush_pct:.2f}%, near-clip≥0.98: {clip_pct:.2f}%",
        measurement={"crush_pct": round(crush_pct, 3), "near_clip_pct": round(clip_pct, 3)},
    ))
    if clip_pct > 1.0:
        report.add_finding(Finding(
            check=CHECK_NAME,
            severity=Severity.MEDIUM,
            message=f"Near-clip region {clip_pct:.2f}% — review white/red zones in overlay",
            ledger_id="A-04",
        ))

    report.set_summary(f"Overlay written → {overlay_path.name}")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="False-color exposure overlay.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    config = load_config(args.config)
    output_dir = ensure_output_dir(args.output)
    report = run(Path(args.input), config, output_dir)
    report_path = output_dir / f"{CHECK_NAME}_report.md"
    report.write(report_path)
    log.info(f"{CHECK_NAME}: wrote report → {report_path}")
    print(f"Report written to {report_path} ({sum(report.counts.values())} finding(s))")


if __name__ == "__main__":
    main()
