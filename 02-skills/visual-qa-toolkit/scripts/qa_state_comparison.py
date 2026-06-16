"""
qa_state_comparison.py — Compare component state screenshots for meaningful differentiation.

Usage:
    python -m scripts.qa_state_comparison --input ./states_folder --config centric.yaml --output ./qa-out

What it does:
    - Scans a folder of state screenshots (e.g., default.png, hover.png, focus.png).
    - Computes pairwise SSIM between each pair of states.
    - Flags state pairs that are too similar — per the config, states are expected
      to differ meaningfully (hover should not look identical to default, focus should
      have a visible affordance, etc.).
    - Emits a similarity matrix visualization and a markdown report.

What it does not do:
    - It does not know which states should differ most. Default and disabled are
      expected to look quite different; hover and active may be subtly different
      by design. Configure per-pair thresholds if precision is needed.
    - File naming matters. The script infers state names from filenames (e.g.,
      `default.png` → `default`). Non-standard names still work but the report
      will use whatever stem the file has.
"""
from __future__ import annotations

import argparse
from itertools import combinations
from pathlib import Path

import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim

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


CHECK_NAME = "state_comparison"

DEFAULTS = {
    "extensions": [".png", ".jpg", ".jpeg"],
    "expected_states": ["default", "hover", "focus", "active", "disabled"],
    "min_ssim_delta": 0.02,      # states must differ by at least 1 - this from each other
    "critical_pairs": [          # pairs that MUST differ noticeably
        ["default", "hover"],
        ["default", "focus"],
        ["default", "active"],
        ["default", "disabled"],
    ],
    "critical_min_delta": 0.04,
    "resize_to_smallest": True,
}


def _load_states(input_path: Path, extensions: list[str]) -> dict[str, np.ndarray]:
    """Load all state images from a folder. Returns {state_name: gray_array}."""
    exts = tuple(e.lower() for e in extensions)
    files = sorted([
        p for p in input_path.iterdir()
        if p.is_file() and p.suffix.lower() in exts
    ])
    states: dict[str, np.ndarray] = {}
    for p in files:
        img = load_image(p)
        states[p.stem.lower()] = img.gray
    return states


def _align_size(states: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    """Resize all state images to the smallest common dimensions."""
    if not states:
        return states
    min_h = min(arr.shape[0] for arr in states.values())
    min_w = min(arr.shape[1] for arr in states.values())
    return {
        name: cv2.resize(arr, (min_w, min_h)) if arr.shape != (min_h, min_w) else arr
        for name, arr in states.items()
    }


def _ssim_score(a: np.ndarray, b: np.ndarray) -> float:
    if a.shape != b.shape:
        return 0.0
    return float(ssim(a, b, data_range=255))


def _render_matrix(
    state_names: list[str],
    matrix: list[list[float]],
    critical_flags: set[tuple[str, str]],
) -> np.ndarray:
    """Render the SSIM similarity matrix as a heatmap-like image with labels."""
    n = len(state_names)
    cell = 48
    left_gutter = 100
    top_gutter = 60
    size_px = n * cell
    img = np.ones((top_gutter + size_px + 20, left_gutter + size_px + 20, 3), dtype=np.uint8) * 245

    # Labels
    for i, name in enumerate(state_names):
        # Column header
        cv2.putText(
            img, name[:12], (left_gutter + i * cell + 4, top_gutter - 6),
            cv2.FONT_HERSHEY_SIMPLEX, 0.36, (40, 40, 40), 1, cv2.LINE_AA,
        )
        # Row header
        cv2.putText(
            img, name[:12], (4, top_gutter + i * cell + cell // 2 + 4),
            cv2.FONT_HERSHEY_SIMPLEX, 0.36, (40, 40, 40), 1, cv2.LINE_AA,
        )

    # Cells
    for i in range(n):
        for j in range(n):
            v = matrix[i][j]
            # Higher SSIM = more similar = warmer
            r = int(np.clip(v * 255, 0, 255))
            g = int(np.clip((1 - abs(v - 0.5) * 2) * 200, 0, 200))
            b = int(np.clip((1 - v) * 255, 0, 255))
            cell_color = (b, g, r)

            x0 = left_gutter + j * cell
            y0 = top_gutter + i * cell
            cv2.rectangle(img, (x0, y0), (x0 + cell - 1, y0 + cell - 1), cell_color, -1)

            # Flag critical pair violations with a red border
            pair = tuple(sorted([state_names[i], state_names[j]]))
            if pair in critical_flags and i != j:
                cv2.rectangle(img, (x0, y0), (x0 + cell - 1, y0 + cell - 1), (0, 0, 220), 2)

            # Value label — use contrasting text
            text_color = (255, 255, 255) if (r + g + b) / 3 < 128 else (20, 20, 20)
            cv2.putText(
                img, f"{v:.2f}", (x0 + 6, y0 + cell // 2 + 4),
                cv2.FONT_HERSHEY_SIMPLEX, 0.36, text_color, 1, cv2.LINE_AA,
            )

    return img


def run(input_path: Path, config: dict, output_dir: Path) -> ReportWriter:
    cfg = config_section(config, CHECK_NAME, DEFAULTS)

    report = ReportWriter(CHECK_NAME, config_summary=cfg)

    if not input_path.is_dir():
        report.add_finding(Finding(
            check=CHECK_NAME,
            severity=Severity.CRITICAL,
            message=f"Input must be a directory of state images: {input_path}",
        ))
        report.set_summary("Skipped: input is not a directory.")
        return report

    states = _load_states(input_path, cfg["extensions"])
    report.set_metadata("states_found", sorted(states.keys()))
    report.set_metadata("state_count", len(states))

    if len(states) < 2:
        report.set_summary(f"Only {len(states)} state(s) found — need ≥2 to compare.")
        return report

    if cfg.get("resize_to_smallest", True):
        states = _align_size(states)

    # Report missing expected states
    expected = set(s.lower() for s in cfg.get("expected_states", []))
    found = set(states.keys())
    missing = expected - found
    for m in sorted(missing):
        report.add_finding(Finding(
            check=CHECK_NAME,
            severity=Severity.LOW,
            message=f"Expected state `{m}` not found in folder",
            details=(
                f"Expected states per config: {sorted(expected)}. "
                f"Found: {sorted(found)}."
            ),
        ))

    # Pairwise SSIM
    state_names = sorted(states.keys())
    n = len(state_names)
    matrix = [[0.0] * n for _ in range(n)]

    critical_pairs = {tuple(sorted([a.lower(), b.lower()])) for a, b in cfg.get("critical_pairs", [])}
    flagged_critical: set[tuple[str, str]] = set()

    for i, a in enumerate(state_names):
        matrix[i][i] = 1.0
        for j in range(i + 1, n):
            b = state_names[j]
            score = _ssim_score(states[a], states[b])
            matrix[i][j] = score
            matrix[j][i] = score

            delta = 1.0 - score
            pair = tuple(sorted([a, b]))

            if pair in critical_pairs:
                if delta < cfg["critical_min_delta"]:
                    flagged_critical.add(pair)
                    report.add_finding(Finding(
                        check=CHECK_NAME,
                        severity=Severity.HIGH,
                        message=(
                            f"Critical state pair ({a} vs. {b}) too similar: "
                            f"SSIM {score:.3f} (Δ {delta:.3f} < {cfg['critical_min_delta']})"
                        ),
                        details=(
                            "These states are expected to be visually distinct. "
                            "If the difference is intentional (e.g., a subtle focus ring), "
                            "consider whether the affordance is strong enough."
                        ),
                        measurement={
                            "state_a": a,
                            "state_b": b,
                            "ssim": round(score, 4),
                            "delta": round(delta, 4),
                            "threshold": cfg["critical_min_delta"],
                        },
                    ))
            elif delta < cfg["min_ssim_delta"]:
                report.add_finding(Finding(
                    check=CHECK_NAME,
                    severity=Severity.MEDIUM,
                    message=(
                        f"State pair ({a} vs. {b}) nearly identical: "
                        f"SSIM {score:.3f} (Δ {delta:.3f} < {cfg['min_ssim_delta']})"
                    ),
                    measurement={
                        "state_a": a,
                        "state_b": b,
                        "ssim": round(score, 4),
                        "delta": round(delta, 4),
                    },
                ))

    # Matrix image
    matrix_img = _render_matrix(state_names, matrix, flagged_critical)
    matrix_path = ensure_output_dir(output_dir) / "state_comparison_matrix.png"
    save_bgr_image(matrix_img, matrix_path)
    report.add_visual(matrix_path.name, "Pairwise SSIM matrix (higher = more similar)")

    report.set_metadata("ssim_matrix", {
        state_names[i]: {state_names[j]: round(matrix[i][j], 4) for j in range(n)}
        for i in range(n)
    })

    report.set_summary(
        f"Compared {n} state(s) across {n * (n - 1) // 2} pair(s). "
        f"Critical pairs: {len(critical_pairs)}. "
        f"Flagged for insufficient differentiation: {sum(report.counts.values())}."
    )

    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--input", required=True, help="Folder of state screenshots")
    parser.add_argument("--config", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    config = load_config(args.config)
    output_dir = ensure_output_dir(args.output)
    report = run(Path(args.input), config, output_dir)
    report_path = output_dir / "state_comparison_report.md"
    report.write(report_path)
    log.info(f"state_comparison: wrote report → {report_path}")
    print(f"Report written to {report_path} ({sum(report.counts.values())} finding(s))")


if __name__ == "__main__":
    main()
