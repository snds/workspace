"""
qa_histogram_hdr.py — Luminance histogram stats; flag clipping.

Usage:
    python -m scripts.qa_histogram_hdr --input frame.png --config configs/default.yaml --output ./qa-out
"""
from __future__ import annotations

import argparse
import json
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

CHECK_NAME = "histogram_hdr"

DEFAULTS = {
    "clip_low_pct": 0.5,       # % of pixels at floor → crush
    "clip_high_pct": 0.5,      # % of pixels at ceiling → blowout
    "bins": 256,
    "write_histogram_image": True,
}


def run(input_path: Path, config: dict, output_dir: Path) -> ReportWriter:
    cfg = config_section(config, CHECK_NAME, DEFAULTS)
    img = load_image(input_path)
    report = ReportWriter(CHECK_NAME, config_summary=cfg)
    report.set_metadata("input", str(input_path))
    report.set_metadata("size", f"{img.width}×{img.height}")

    lum = luminance_rel(img.rgb)
    flat = lum.ravel()
    bins = int(cfg["bins"])
    hist, edges = np.histogram(flat, bins=bins, range=(0.0, 1.0))
    total = flat.size

    mean = float(flat.mean())
    std = float(flat.std())
    p01, p50, p99 = (float(np.percentile(flat, p)) for p in (1, 50, 99))
    low_pct = 100.0 * float((flat <= 1.0 / 255.0).sum()) / total
    high_pct = 100.0 * float((flat >= 254.0 / 255.0).sum()) / total

    stats = {
        "mean": round(mean, 4),
        "std": round(std, 4),
        "p01": round(p01, 4),
        "p50": round(p50, 4),
        "p99": round(p99, 4),
        "clip_low_pct": round(low_pct, 3),
        "clip_high_pct": round(high_pct, 3),
    }
    report.set_metadata("luminance", stats)

    out = ensure_output_dir(output_dir)
    stats_path = out / "histogram_hdr_stats.json"
    stats_path.write_text(json.dumps({"stats": stats, "bins": hist.tolist()}, indent=2), encoding="utf-8")
    report.add_visual(stats_path.name, "Histogram stats JSON")

    if cfg.get("write_histogram_image", True):
        h_img = 200
        w_img = bins
        canvas = np.zeros((h_img, w_img, 3), dtype=np.uint8)
        peak = max(int(hist.max()), 1)
        for i, v in enumerate(hist):
            bar_h = int(round((v / peak) * (h_img - 4)))
            cv2.line(canvas, (i, h_img - 1), (i, h_img - 1 - bar_h), (200, 200, 200), 1)
        # Mark clip ends
        cv2.line(canvas, (0, 0), (0, h_img), (0, 0, 220), 2)
        cv2.line(canvas, (bins - 1, 0), (bins - 1, h_img), (0, 0, 220), 2)
        hist_path = out / "histogram_hdr.png"
        save_bgr_image(canvas, hist_path)
        report.add_visual(hist_path.name, "Luminance histogram (red edges = clip bins)")

    clip_low = float(cfg["clip_low_pct"])
    clip_high = float(cfg["clip_high_pct"])

    if low_pct >= clip_low:
        report.add_finding(Finding(
            check=CHECK_NAME,
            severity=Severity.HIGH,
            message=f"Shadow crush: {low_pct:.2f}% of pixels at floor (threshold {clip_low}%)",
            measurement={"clip_low_pct": round(low_pct, 3)},
            ledger_id="A-04",
        ))
    if high_pct >= clip_high:
        report.add_finding(Finding(
            check=CHECK_NAME,
            severity=Severity.HIGH,
            message=f"Highlight blowout: {high_pct:.2f}% of pixels at ceiling (threshold {clip_high}%)",
            details="Dense additive overlaps or clipped bloom often spike the max bin (ledger A-04).",
            measurement={"clip_high_pct": round(high_pct, 3)},
            ledger_id="A-04",
        ))
    if not any(f.severity in (Severity.HIGH, Severity.CRITICAL) for f in report.findings):
        report.add_finding(Finding(
            check=CHECK_NAME,
            severity=Severity.INFO,
            message=f"Luminance OK — mean={mean:.3f}, p50={p50:.3f}, clip L/H={low_pct:.2f}%/{high_pct:.2f}%",
            measurement=stats,
        ))

    report.set_summary(
        f"mean={mean:.3f} · p50={p50:.3f} · clip_low={low_pct:.2f}% · clip_high={high_pct:.2f}%"
    )
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Luminance histogram + clipping flags.")
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
