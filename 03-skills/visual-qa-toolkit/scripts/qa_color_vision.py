"""
qa_color_vision.py — Simulate color blindness and flag indistinguishable color pairs.

Usage:
    python -m scripts.qa_color_vision --input screenshot.png --config centric.yaml --output ./qa-out

What it does:
    - Applies daltonization matrices to simulate deuteranopia, protanopia,
      and tritanopia on the input image.
    - For each simulation, extracts dominant colors from the simulated image
      and compares them to the original's dominant colors.
    - Flags pairs of colors that were visually distinct in the original but
      collapse to near-identical under a simulation (information loss).
    - Emits side-by-side panels of original + all simulations.

What it does not do:
    - The simulation matrices are linear approximations (Brettel/Viénot/Mollon).
      They are industry-standard but not a substitute for testing with actual
      users who have CVD.
    - Identifying information loss by color pairs is a heuristic — if two
      colors encode meaningful distinctions in your UI, that distinction is
      what matters, not the raw color difference. Use the side-by-side as
      the primary artifact; findings are a prompt for inspection.
"""
from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path

import cv2
import numpy as np

from ._common import (
    Finding,
    ReportWriter,
    Severity,
    config_section,
    delta_e_cie76,
    ensure_output_dir,
    load_config,
    load_image,
    log,
    rgb_to_hex,
    save_bgr_image,
)


CHECK_NAME = "color_vision"

DEFAULTS = {
    "simulations": ["deuteranopia", "protanopia", "tritanopia"],
    "dominant_color_count": 8,
    "distinct_original_threshold": 10.0,   # Δe — colors must be this distinct in original
    "collapse_threshold": 4.0,             # Δe — below this they're "indistinguishable" after
    "min_area_pct": 0.5,                   # ignore colors with very low coverage
}


# Matrices from Machado, Oliveira & Fernandes (2009) — widely used approximation.
# Applied in linear RGB space (we use sRGB here as a simplification; error is modest).
CVD_MATRICES = {
    "deuteranopia": np.array([
        [0.367322, 0.860646, -0.227968],
        [0.280085, 0.672501,  0.047413],
        [-0.01182, 0.042940,  0.968881],
    ]),
    "protanopia": np.array([
        [0.152286, 1.052583, -0.204868],
        [0.114503, 0.786281,  0.099216],
        [-0.00364, -0.048116, 1.051755],
    ]),
    "tritanopia": np.array([
        [1.255528, -0.076749, -0.178779],
        [-0.078411, 0.930809,  0.147602],
        [0.004733, 0.691367,  0.303900],
    ]),
}


def _simulate_cvd(rgb: np.ndarray, simulation: str) -> np.ndarray:
    """Apply a CVD simulation matrix. Input/output: uint8 RGB (H, W, 3)."""
    matrix = CVD_MATRICES[simulation]
    flat = rgb.reshape(-1, 3).astype(np.float32)
    transformed = flat @ matrix.T
    transformed = np.clip(transformed, 0, 255).astype(np.uint8)
    return transformed.reshape(rgb.shape)


def _dominant_colors(rgb: np.ndarray, k: int, min_count: int) -> list[tuple[tuple[int, int, int], int]]:
    quantized = (rgb // 8) * 8
    flat = [tuple(int(v) for v in p) for p in quantized.reshape(-1, 3)]
    counter = Counter(flat)
    filtered = [(c, n) for c, n in counter.most_common(k * 3) if n >= min_count]
    return filtered[:k]


def run(input_path: Path, config: dict, output_dir: Path) -> ReportWriter:
    cfg = config_section(config, CHECK_NAME, DEFAULTS)

    img = load_image(input_path)
    report = ReportWriter(CHECK_NAME, config_summary=cfg)
    report.set_metadata("source", str(input_path))

    total_pixels = img.width * img.height
    min_count = int(total_pixels * (cfg["min_area_pct"] / 100.0))

    # Original dominant colors
    original_dominants = _dominant_colors(img.rgb, cfg["dominant_color_count"], min_count)
    report.set_metadata("dominant_colors_detected", len(original_dominants))

    # Identify distinct pairs in the original
    distinct_pairs: list[tuple[tuple[int, int, int], tuple[int, int, int]]] = []
    for i, (c1, _) in enumerate(original_dominants):
        for c2, _ in original_dominants[i+1:]:
            if delta_e_cie76(c1, c2) >= cfg["distinct_original_threshold"]:
                distinct_pairs.append((c1, c2))

    report.set_metadata("distinct_color_pairs", len(distinct_pairs))

    # Simulate each CVD type, check which distinct pairs collapse
    simulation_panels: list[np.ndarray] = [img.bgr]
    simulation_labels: list[str] = ["Original"]

    collapse_findings_per_sim: dict[str, int] = {}

    for sim_name in cfg["simulations"]:
        if sim_name not in CVD_MATRICES:
            log.warning(f"color_vision: unknown simulation '{sim_name}', skipping")
            continue

        simulated_rgb = _simulate_cvd(img.rgb, sim_name)
        simulated_bgr = cv2.cvtColor(simulated_rgb, cv2.COLOR_RGB2BGR)
        simulation_panels.append(simulated_bgr)
        simulation_labels.append(sim_name.capitalize())

        # Save individual sim
        sim_path = ensure_output_dir(output_dir) / f"color_vision_{sim_name}.png"
        save_bgr_image(simulated_bgr, sim_path)

        # Check collapse: for each distinct pair in the original, what's the Δe
        # between those same colors when transformed?
        collapses = 0
        for c1, c2 in distinct_pairs:
            c1_sim = tuple(int(v) for v in (_simulate_cvd(np.array([[c1]], dtype=np.uint8), sim_name))[0, 0])
            c2_sim = tuple(int(v) for v in (_simulate_cvd(np.array([[c2]], dtype=np.uint8), sim_name))[0, 0])
            sim_de = delta_e_cie76(c1_sim, c2_sim)

            if sim_de < cfg["collapse_threshold"]:
                collapses += 1
                original_de = delta_e_cie76(c1, c2)
                report.add_finding(Finding(
                    check=CHECK_NAME,
                    severity=Severity.HIGH,
                    message=(
                        f"{sim_name}: {rgb_to_hex(c1)} and {rgb_to_hex(c2)} "
                        f"collapse (Δe {original_de:.1f} → {sim_de:.1f})"
                    ),
                    details=(
                        f"These two colors are visually distinct in the original "
                        f"(Δe {original_de:.1f} ≥ {cfg['distinct_original_threshold']}) "
                        f"but become nearly indistinguishable under {sim_name} simulation "
                        f"(Δe {sim_de:.1f} < {cfg['collapse_threshold']}). If these "
                        f"colors encode meaningful information in the UI, that "
                        f"information is lost for users with this CVD type."
                    ),
                    measurement={
                        "simulation": sim_name,
                        "color_a": rgb_to_hex(c1),
                        "color_b": rgb_to_hex(c2),
                        "original_delta_e": round(original_de, 2),
                        "simulated_delta_e": round(sim_de, 2),
                    },
                ))

        collapse_findings_per_sim[sim_name] = collapses

    # Composite panel: original + all simulations stacked horizontally
    panel_h = img.height
    # Scale each panel to fit a reasonable width if images are large
    max_panel_w = 600
    scale = min(1.0, max_panel_w / img.width)
    sh = int(panel_h * scale)
    sw = int(img.width * scale)

    resized_panels = [cv2.resize(p, (sw, sh)) for p in simulation_panels]

    # Label strip
    label_h = 32
    composite = np.ones((sh + label_h, sw * len(resized_panels), 3), dtype=np.uint8) * 30

    for i, (panel, label) in enumerate(zip(resized_panels, simulation_labels)):
        composite[label_h:label_h + sh, i * sw:(i + 1) * sw] = panel
        cv2.putText(
            composite, label, (i * sw + 8, 22),
            cv2.FONT_HERSHEY_SIMPLEX, 0.55, (240, 240, 240), 1, cv2.LINE_AA,
        )

    composite_path = ensure_output_dir(output_dir) / "color_vision_comparison.png"
    save_bgr_image(composite, composite_path)
    report.add_visual(composite_path.name, "Original + CVD simulations side-by-side")

    total_collapses = sum(collapse_findings_per_sim.values())
    collapses_summary = ", ".join(f"{k}: {v}" for k, v in collapse_findings_per_sim.items())
    report.set_summary(
        f"Simulated {len(collapse_findings_per_sim)} CVD condition(s). "
        f"Analyzed {len(distinct_pairs)} distinct color pair(s) from {len(original_dominants)} dominant colors. "
        f"Color pair collapses per simulation — {collapses_summary}. "
        f"Total collapse findings: {total_collapses}."
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
    report_path = output_dir / "color_vision_report.md"
    report.write(report_path)
    log.info(f"color_vision: wrote report → {report_path}")
    print(f"Report written to {report_path} ({sum(report.counts.values())} finding(s))")


if __name__ == "__main__":
    main()
