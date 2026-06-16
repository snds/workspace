"""
qa_color_extraction.py — Extract pixel colors and compare against a token palette.

Usage:
    python -m scripts.qa_color_extraction --input screenshot.png --config centric.yaml --output ./qa-out

What it does:
    - Samples colors at configured sample points (or auto-detects dominant colors
      from the image if no points specified).
    - Compares each sampled color against a reference token palette loaded from
      a JSON/YAML file.
    - Computes CIE76 delta-E between the sampled color and the nearest palette
      entry; flags drift beyond the configured threshold.
    - Emits a markdown report with per-sample nearest matches and an annotated
      image showing the sample points.

What it does not do:
    - CIE76 is a rough perceptual metric. A delta-E of 2.3 is the "just
      noticeable" threshold under ideal conditions; real UI contexts vary.
      For pure "is this color in the palette," delta-E < 3 is a safe match.
    - It cannot tell you which *semantic* token was intended — only which
      palette entry is perceptually nearest. For semantic drift detection,
      use `qa_visual_diff.py` against a design export.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import cv2
import numpy as np
import yaml

from ._common import (
    Finding,
    ReportWriter,
    Severity,
    config_section,
    delta_e_cie76,
    draw_bbox,
    ensure_output_dir,
    hex_to_rgb,
    load_config,
    load_image,
    log,
    rgb_to_hex,
    sample_pixel,
    save_bgr_image,
)


CHECK_NAME = "color_extraction"

DEFAULTS = {
    "palette_path": None,              # JSON/YAML file: {name: "#RRGGBB"} or [{name, hex}]
    "sample_points": None,             # list of {point: [x,y], label: str}
    "auto_detect": True,               # auto-extract dominant colors if no sample_points
    "auto_detect_count": 12,           # how many dominant colors to extract
    "delta_e_threshold": 5.0,          # acceptable perceptual drift
    "delta_e_ideal": 2.3,              # "just noticeable" reference
    "sample_radius": 3,                # pixel neighborhood for sampling
}


def _load_palette(path: str | Path) -> dict[str, tuple[int, int, int]]:
    """Load a palette from JSON or YAML. Accepts {name: hex} or [{name, hex}] shapes."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Palette file not found: {path}")

    raw = path.read_text(encoding="utf-8")
    if path.suffix.lower() in (".yaml", ".yml"):
        data = yaml.safe_load(raw)
    else:
        data = json.loads(raw)

    palette: dict[str, tuple[int, int, int]] = {}
    if isinstance(data, dict):
        for name, hex_val in data.items():
            palette[str(name)] = hex_to_rgb(str(hex_val))
    elif isinstance(data, list):
        for entry in data:
            name = entry.get("name") or entry.get("token") or entry.get("id")
            hex_val = entry.get("hex") or entry.get("value") or entry.get("color")
            if name and hex_val:
                palette[str(name)] = hex_to_rgb(str(hex_val))
    else:
        raise ValueError(f"Unrecognized palette format in {path}")

    return palette


def _dominant_colors(rgb: np.ndarray, k: int) -> list[tuple[tuple[int, int, int], int]]:
    """Extract top-k dominant colors via rough 5-bit-per-channel quantization."""
    quantized = (rgb // 8) * 8
    flat = [tuple(int(v) for v in p) for p in quantized.reshape(-1, 3)]
    counter = Counter(flat)
    return counter.most_common(k)


def _nearest_palette_entry(
    color: tuple[int, int, int],
    palette: dict[str, tuple[int, int, int]],
) -> tuple[str, tuple[int, int, int], float]:
    """Return (token_name, token_rgb, delta_e) for the nearest palette entry."""
    best_name = ""
    best_rgb = (0, 0, 0)
    best_de = float("inf")
    for name, rgb in palette.items():
        de = delta_e_cie76(color, rgb)
        if de < best_de:
            best_de = de
            best_name = name
            best_rgb = rgb
    return best_name, best_rgb, best_de


def run(input_path: Path, config: dict, output_dir: Path) -> ReportWriter:
    cfg = config_section(config, CHECK_NAME, DEFAULTS)
    threshold = cfg["delta_e_threshold"]
    ideal = cfg["delta_e_ideal"]

    img = load_image(input_path)
    report = ReportWriter(CHECK_NAME, config_summary=cfg)
    report.set_metadata("source", str(input_path))

    # Load palette (required)
    palette_path = cfg.get("palette_path")
    if not palette_path:
        report.add_finding(Finding(
            check=CHECK_NAME,
            severity=Severity.INFO,
            message="No palette_path configured — skipping palette comparison",
            details=(
                "Set `color_extraction.palette_path` in the config to enable "
                "palette drift detection. Colors will still be sampled and "
                "listed in the metadata for reference."
            ),
        ))
        palette: dict[str, tuple[int, int, int]] = {}
    else:
        palette_path = Path(palette_path)
        if not palette_path.is_absolute():
            # Resolve relative to config-adjacent path if possible
            palette_path = Path(palette_path)
        palette = _load_palette(palette_path)
        report.set_metadata("palette_size", len(palette))
        report.set_metadata("palette_source", str(palette_path))

    # Determine sample points
    samples: list[tuple[tuple[int, int], str, tuple[int, int, int]]] = []
    if cfg.get("sample_points"):
        for entry in cfg["sample_points"]:
            x, y = entry["point"]
            label = entry.get("label", f"sample_{len(samples)}")
            color = sample_pixel(img.rgb, x, y, radius=cfg["sample_radius"])
            samples.append(((x, y), label, color))
    elif cfg.get("auto_detect", True):
        dominants = _dominant_colors(img.rgb, cfg["auto_detect_count"])
        for i, (color, count) in enumerate(dominants):
            # Place a synthetic "point" at the image center for display purposes;
            # the real info is the color itself, not its location
            samples.append(((img.width // 2, img.height // 2), f"dominant_{i}_{count}px", color))

    report.set_metadata("samples", len(samples))

    annotated = img.bgr.copy()

    for (x, y), label, color in samples:
        if palette:
            token_name, token_rgb, de = _nearest_palette_entry(color, palette)
            if de <= ideal:
                severity = None  # perfect match, no finding
                status = "exact"
                marker_color = "success"
            elif de <= threshold:
                severity = Severity.LOW
                status = "close"
                marker_color = "warning"
            else:
                severity = Severity.HIGH
                status = "drift"
                marker_color = "critical"

            msg = (
                f"{label}: {rgb_to_hex(color)} → nearest token `{token_name}` "
                f"({rgb_to_hex(token_rgb)}), Δe={de:.2f}"
            )

            if severity is not None:
                report.add_finding(Finding(
                    check=CHECK_NAME,
                    severity=severity,
                    message=msg,
                    details=(
                        f"Sampled color is {status} to the nearest palette entry. "
                        f"Threshold: Δe ≤ {threshold}. Ideal (just-noticeable): Δe ≤ {ideal}."
                    ),
                    location=(max(0, x - 10), max(0, y - 10), 20, 20)
                    if cfg.get("sample_points") else None,
                    measurement={
                        "sampled_hex": rgb_to_hex(color),
                        "nearest_token": token_name,
                        "token_hex": rgb_to_hex(token_rgb),
                        "delta_e": round(de, 2),
                    },
                ))

            # Annotate if this was an explicit sample point
            if cfg.get("sample_points"):
                draw_bbox(
                    annotated,
                    (x - 8, y - 8, 16, 16),
                    color=marker_color,
                    label=f"{label}|Δe{de:.1f}",
                )
        else:
            # Palette-less run — just note the sampled color
            if cfg.get("sample_points"):
                draw_bbox(
                    annotated,
                    (x - 8, y - 8, 16, 16),
                    color="primary",
                    label=f"{label}|{rgb_to_hex(color)}",
                )

    # Always save the annotated image if we drew anything
    if cfg.get("sample_points"):
        annotated_path = ensure_output_dir(output_dir) / "color_extraction_annotated.png"
        save_bgr_image(annotated, annotated_path)
        report.add_visual(annotated_path.name, "Sample points — green/orange/red = match quality")

    # Render a dominant-color swatch strip for auto-detect mode
    if not cfg.get("sample_points") and samples:
        strip_h = 60
        swatch_w = 80
        strip = np.zeros((strip_h, swatch_w * len(samples), 3), dtype=np.uint8)
        for i, (_pt, label, color) in enumerate(samples):
            strip[:, i * swatch_w:(i + 1) * swatch_w] = (color[2], color[1], color[0])  # BGR
            cv2.putText(
                strip, rgb_to_hex(color), (i * swatch_w + 4, strip_h - 8),
                cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 255, 255), 1, cv2.LINE_AA,
            )
        strip_path = ensure_output_dir(output_dir) / "color_extraction_swatches.png"
        save_bgr_image(strip, strip_path)
        report.add_visual(strip_path.name, "Dominant colors extracted from image")

    # Summary
    drift_count = sum(1 for f in report.findings if f.severity == Severity.HIGH)
    close_count = sum(1 for f in report.findings if f.severity == Severity.LOW)
    report.set_summary(
        f"Sampled {len(samples)} color(s). "
        f"Drift (Δe > {threshold}): {drift_count}. "
        f"Close match (Δe ≤ {threshold}): {close_count}. "
        f"Exact (Δe ≤ {ideal}): {len(samples) - drift_count - close_count}."
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
    report_path = output_dir / "color_extraction_report.md"
    report.write(report_path)
    log.info(f"color_extraction: wrote report → {report_path}")
    print(f"Report written to {report_path} ({sum(report.counts.values())} finding(s))")


if __name__ == "__main__":
    main()
