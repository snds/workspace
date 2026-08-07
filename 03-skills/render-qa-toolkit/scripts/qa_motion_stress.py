"""
qa_motion_stress.py — Temporal MAD on a labeled stress-frames folder; summarize peaks.

Expects a folder of frames (optionally with stress labels in filenames, e.g.
  lod_swap_001.png, roll_012.png, approach_003.png). Groups by label prefix
  (text before the last underscore+digits) when present.

Usage:
    python -m scripts.qa_motion_stress --input ./stress-frames/ --config configs/legion.yaml --output ./qa-out
"""
from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
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
)

CHECK_NAME = "motion_stress"

DEFAULTS = {
    "peak_mad_threshold": 20.0,
    "group_mean_threshold": 12.0,
    "resize_to_first": True,
}

_LABEL_RE = re.compile(r"^(?P<label>.+?)_(?P<idx>\d+)$", re.IGNORECASE)


def _label_for(path: Path) -> str:
    stem = path.stem
    m = _LABEL_RE.match(stem)
    if m:
        return m.group("label")
    # fallback: whole stem without trailing digits
    return re.sub(r"_\d+$", "", stem) or "ungrouped"


def run(input_path: Path, config: dict, output_dir: Path) -> ReportWriter:
    cfg = config_section(config, CHECK_NAME, DEFAULTS)
    report = ReportWriter(CHECK_NAME, config_summary=cfg)
    report.set_metadata("input", str(input_path))

    files = list_image_files(input_path)
    if len(files) < 2:
        report.add_finding(Finding(
            check=CHECK_NAME,
            severity=Severity.CRITICAL,
            message=f"Need ≥2 stress frames; found {len(files)}",
        ))
        report.set_summary("Skipped: insufficient frames.")
        return report

    groups: dict[str, list[Path]] = defaultdict(list)
    for p in files:
        groups[_label_for(p)].append(p)

    summary: dict[str, dict] = {}
    global_peaks: list[tuple[str, float, str]] = []

    for label, paths in sorted(groups.items()):
        paths = sorted(paths)
        if len(paths) < 2:
            summary[label] = {"frames": len(paths), "mean_mad": None, "max_mad": None, "note": "single frame"}
            continue
        images = [load_image(p) for p in paths]
        tw, th = images[0].width, images[0].height
        grays = []
        for im in images:
            if cfg.get("resize_to_first", True) and (im.width, im.height) != (tw, th):
                rgb = cv2.resize(im.rgb, (tw, th), interpolation=cv2.INTER_AREA)
                grays.append(cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY))
            else:
                grays.append(im.gray)
        mads = []
        for i in range(1, len(grays)):
            mads.append(float(np.mean(np.abs(
                grays[i - 1].astype(np.float64) - grays[i].astype(np.float64)
            ))))
        mean_mad = float(np.mean(mads))
        max_mad = float(np.max(mads))
        max_pair = int(np.argmax(mads)) + 1
        summary[label] = {
            "frames": len(paths),
            "mean_mad": round(mean_mad, 3),
            "max_mad": round(max_mad, 3),
            "max_pair": f"{max_pair - 1}->{max_pair}",
        }
        global_peaks.append((label, max_mad, summary[label]["max_pair"]))

        peak_t = float(cfg["peak_mad_threshold"])
        group_t = float(cfg["group_mean_threshold"])
        if max_mad >= peak_t:
            report.add_finding(Finding(
                check=CHECK_NAME,
                severity=Severity.HIGH,
                message=f"Stress peak [{label}] MAD {max_mad:.2f} at {summary[label]['max_pair']}",
                measurement=summary[label],
            ))
        elif mean_mad >= group_t:
            report.add_finding(Finding(
                check=CHECK_NAME,
                severity=Severity.MEDIUM,
                message=f"Stress group [{label}] mean MAD {mean_mad:.2f} ≥ {group_t}",
                measurement=summary[label],
            ))
        else:
            report.add_finding(Finding(
                check=CHECK_NAME,
                severity=Severity.INFO,
                message=f"[{label}] mean={mean_mad:.2f} max={max_mad:.2f}",
                measurement=summary[label],
            ))

    out = ensure_output_dir(output_dir)
    sum_path = out / "motion_stress_summary.json"
    peaks_sorted = sorted(global_peaks, key=lambda t: t[1], reverse=True)
    payload = {
        "groups": summary,
        "peaks": [
            {"label": lab, "max_mad": round(mad, 3), "pair": pair}
            for lab, mad, pair in peaks_sorted
        ],
    }
    sum_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    report.add_visual(sum_path.name, "Per-stress-group MAD summary")

    top = peaks_sorted[0] if peaks_sorted else None
    report.set_summary(
        f"{len(files)} frames in {len(groups)} group(s)"
        + (f"; top peak [{top[0]}] MAD={top[1]:.2f}" if top else "")
    )
    return report


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Summarize temporal peaks in a labeled stress-frames folder."
    )
    parser.add_argument("--input", required=True, help="Folder of labeled stress frames")
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
