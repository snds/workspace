"""
qa_temporal_delta.py — Mean absolute difference across a frame sequence; flag shimmer.

Usage:
    python -m scripts.qa_temporal_delta --input ./frames/ --config configs/default.yaml --output ./qa-out
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
    list_image_files,
    load_config,
    load_image,
    log,
    save_bgr_image,
)

CHECK_NAME = "temporal_delta"

DEFAULTS = {
    "shimmer_mad_threshold": 8.0,   # mean abs diff (0–255) between consecutive frames
    "spike_mad_threshold": 18.0,    # single-pair spike
    "resize_to_first": True,
    "write_delta_preview": True,
}


def run(input_path: Path, config: dict, output_dir: Path) -> ReportWriter:
    cfg = config_section(config, CHECK_NAME, DEFAULTS)
    report = ReportWriter(CHECK_NAME, config_summary=cfg)
    report.set_metadata("input", str(input_path))

    files = list_image_files(input_path)
    if len(files) < 2:
        report.add_finding(Finding(
            check=CHECK_NAME,
            severity=Severity.CRITICAL,
            message=f"Need ≥2 frames; found {len(files)} in {input_path}",
        ))
        report.set_summary("Skipped: insufficient frames.")
        return report

    images = [load_image(p) for p in files]
    if cfg.get("resize_to_first", True):
        tw, th = images[0].width, images[0].height
        resized = []
        for im in images:
            if (im.width, im.height) != (tw, th):
                rgb = cv2.resize(im.rgb, (tw, th), interpolation=cv2.INTER_AREA)
                gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
            else:
                gray = im.gray
            resized.append(gray)
        grays = resized
    else:
        grays = [im.gray for im in images]

    mads: list[float] = []
    for i in range(1, len(grays)):
        a = grays[i - 1].astype(np.float64)
        b = grays[i].astype(np.float64)
        if a.shape != b.shape:
            report.add_finding(Finding(
                check=CHECK_NAME,
                severity=Severity.CRITICAL,
                message=f"Frame size mismatch at index {i}: {a.shape} vs {b.shape}",
            ))
            report.set_summary("Failed: inconsistent frame sizes (disable resize_to_first? no — sizes still differ).")
            return report
        mads.append(float(np.mean(np.abs(a - b))))

    mean_mad = float(np.mean(mads))
    max_mad = float(np.max(mads))
    max_i = int(np.argmax(mads)) + 1  # pair (i-1, i)

    series = [{"pair": f"{i-1}->{i}", "mad": round(m, 3)} for i, m in enumerate(mads, 1)]
    out = ensure_output_dir(output_dir)
    series_path = out / "temporal_delta_series.json"
    series_path.write_text(json.dumps({
        "mean_mad": round(mean_mad, 3),
        "max_mad": round(max_mad, 3),
        "max_pair_index": max_i,
        "series": series,
        "frames": [p.name for p in files],
    }, indent=2), encoding="utf-8")
    report.add_visual(series_path.name, "Per-pair MAD series")

    if cfg.get("write_delta_preview", True):
        a = grays[max_i - 1].astype(np.float64)
        b = grays[max_i].astype(np.float64)
        delta = np.clip(np.abs(a - b) * 4.0, 0, 255).astype(np.uint8)
        heat = cv2.applyColorMap(delta, cv2.COLORMAP_INFERNO)
        preview = out / "temporal_delta_peak.png"
        save_bgr_image(heat, preview)
        report.add_visual(preview.name, f"Peak delta pair {max_i - 1}→{max_i}")

    shimmer_t = float(cfg["shimmer_mad_threshold"])
    spike_t = float(cfg["spike_mad_threshold"])

    if mean_mad >= shimmer_t:
        report.add_finding(Finding(
            check=CHECK_NAME,
            severity=Severity.HIGH,
            message=f"Shimmer suspicion: mean MAD {mean_mad:.2f} ≥ {shimmer_t}",
            details=(
                "Elevated frame-to-frame difference under a supposedly stable camera "
                "often means screen-space dither crawl (ledger A-02) or unstable TAA."
            ),
            measurement={"mean_mad": round(mean_mad, 3), "threshold": shimmer_t},
            ledger_id="A-02",
        ))
    if max_mad >= spike_t:
        report.add_finding(Finding(
            check=CHECK_NAME,
            severity=Severity.MEDIUM,
            message=f"Temporal spike MAD {max_mad:.2f} at pair {max_i - 1}→{max_i} (threshold {spike_t})",
            measurement={"max_mad": round(max_mad, 3), "pair": max_i},
        ))
    if not any(f.severity in (Severity.HIGH, Severity.MEDIUM, Severity.CRITICAL) for f in report.findings):
        report.add_finding(Finding(
            check=CHECK_NAME,
            severity=Severity.INFO,
            message=f"Temporal MAD OK — mean={mean_mad:.2f}, max={max_mad:.2f}",
            measurement={"mean_mad": round(mean_mad, 3), "max_mad": round(max_mad, 3)},
        ))

    report.set_summary(
        f"{len(files)} frames · mean MAD={mean_mad:.2f} · max MAD={max_mad:.2f} @ pair {max_i - 1}→{max_i}"
    )
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Temporal MAD across a frame sequence.")
    parser.add_argument("--input", required=True, help="Folder of ordered frames")
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
