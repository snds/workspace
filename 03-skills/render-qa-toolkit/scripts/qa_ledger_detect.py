"""
qa_ledger_detect.py — Best-effort heuristic hints mapped to Visual Failure-Mode Ledger IDs.

Not a substitute for native-resolution human review. Emits INFO/MEDIUM hints when
simple image statistics resemble known failure tells (banding edges, clip spikes,
screen-grid JPEG blocks, etc.).

Usage:
    python -m scripts.qa_ledger_detect --input frame.png --config configs/default.yaml --output ./qa-out
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
)

CHECK_NAME = "ledger_detect"

DEFAULTS = {
    "banding_grad_bins": 32,         # quantize luminance for isoline check
    "banding_edge_density_min": 0.04,
    "clip_pct_min": 1.0,
    "jpeg_block_score_min": 0.15,    # relative 8×8 energy ratio
}


def _banding_hint(gray: np.ndarray, bins: int, density_min: float) -> tuple[bool, float]:
    """
    Rough banding tell: after coarse luminance quantization, Canny edge density
    rises (stepped isolines). Best-effort only.
    """
    # Quantize
    q = (gray.astype(np.float64) / 255.0 * (bins - 1)).astype(np.uint8)
    q_up = (q.astype(np.float64) / max(bins - 1, 1) * 255).astype(np.uint8)
    edges = cv2.Canny(q_up, 40, 120)
    density = float(edges.mean() / 255.0)
    return density >= density_min, density


def _jpeg_block_hint(gray: np.ndarray) -> tuple[bool, float]:
    """
    Detect elevated energy on 8-pixel grid (codec blocking mistaken for banding — A-05).
    Compares mean abs vertical gradient at x%8==0 vs elsewhere.
    """
    g = gray.astype(np.float64)
    dx = np.abs(np.diff(g, axis=1))
    if dx.size == 0:
        return False, 0.0
    # columns in dx correspond to boundaries between x and x+1 → boundary after col i is index i
    # 8×8 block edges land when (i+1) % 8 == 0 → i % 8 == 7
    mask_block = np.zeros(dx.shape[1], dtype=bool)
    mask_block[7::8] = True
    block = dx[:, mask_block].mean() if mask_block.any() else 0.0
    other = dx[:, ~mask_block].mean() if (~mask_block).any() else 1.0
    score = float(block / (other + 1e-6) - 1.0)
    return score >= 0.15, score


def run(input_path: Path, config: dict, output_dir: Path) -> ReportWriter:
    cfg = config_section(config, CHECK_NAME, DEFAULTS)
    img = load_image(input_path)
    report = ReportWriter(CHECK_NAME, config_summary=cfg)
    report.set_metadata("input", str(input_path))
    report.set_metadata("size", f"{img.width}×{img.height}")
    ensure_output_dir(output_dir)

    hints = 0

    # A-01 banding
    banded, dens = _banding_hint(
        img.gray,
        int(cfg["banding_grad_bins"]),
        float(cfg["banding_edge_density_min"]),
    )
    if banded:
        hints += 1
        report.add_finding(Finding(
            check=CHECK_NAME,
            severity=Severity.MEDIUM,
            message=f"Possible banding isolines (quantized edge density={dens:.3f})",
            details="Heuristic only. Confirm on a native crop of the falloff region.",
            measurement={"edge_density": round(dens, 4)},
            ledger_id="A-01",
        ))

    # A-04 / A-03 clip
    lum = luminance_rel(img.rgb)
    high = 100.0 * float((lum >= 0.98).sum()) / lum.size
    if high >= float(cfg["clip_pct_min"]):
        hints += 1
        report.add_finding(Finding(
            check=CHECK_NAME,
            severity=Severity.MEDIUM,
            message=f"Highlight mass {high:.2f}% near clip — check bloom/additive blowout",
            measurement={"near_clip_pct": round(high, 3)},
            ledger_id="A-04",
        ))

    # A-05 JPEG mistaken for banding
    jpegish, jscore = _jpeg_block_hint(img.gray)
    # Also cheap extension check
    if input_path.suffix.lower() in {".jpg", ".jpeg"} or jpegish:
        hints += 1
        report.add_finding(Finding(
            check=CHECK_NAME,
            severity=Severity.LOW if input_path.suffix.lower() in {".jpg", ".jpeg"} else Severity.MEDIUM,
            message=(
                f"Possible codec blocking (8×8 score={jscore:.2f})"
                if jpegish else
                "Input is JPEG — recapture PNG before judging banding/edges"
            ),
            details="Ledger A-05: lossy capture often misread as render banding.",
            measurement={"block_score": round(jscore, 3), "suffix": input_path.suffix},
            ledger_id="A-05",
        ))

    # Z-01 undersized
    if img.width < 800:
        hints += 1
        report.add_finding(Finding(
            check=CHECK_NAME,
            severity=Severity.HIGH,
            message=f"Width {img.width}px looks like a locator thumbnail, not native evidence",
            ledger_id="Z-01",
        ))

    if hints == 0:
        report.add_finding(Finding(
            check=CHECK_NAME,
            severity=Severity.INFO,
            message="No ledger heuristics fired (does not mean the frame is clean)",
        ))

    report.set_summary(f"{hints} ledger hint(s) on {img.width}×{img.height} (best-effort)")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Best-effort Visual Failure-Mode Ledger heuristic hints."
    )
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
