"""
_common.py — Shared utilities for the visual-qa-toolkit.

Every QA script imports from this module. Keeps cross-script behavior
consistent: config schema, image loading, element detection, report
formatting, and output directory conventions.

No script-specific logic belongs here. If something is only used by one
script, it lives in that script.
"""
from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from typing import Any, Iterable

import cv2
import numpy as np
import yaml
from PIL import Image


# ─────────────────────────────────────────────────────────────
# Logging
# ─────────────────────────────────────────────────────────────

def get_logger(name: str) -> logging.Logger:
    """Consistent logger formatting across all scripts."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter("[%(name)s] %(levelname)s: %(message)s")
        )
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


log = get_logger("qa")


# ─────────────────────────────────────────────────────────────
# Severity model
# ─────────────────────────────────────────────────────────────

class Severity(str, Enum):
    """Severity of a finding. String values so they serialize cleanly."""
    CRITICAL = "critical"   # WCAG fail, broken state, definitely wrong
    HIGH     = "high"       # measurable drift beyond tolerance
    MEDIUM   = "medium"     # borderline, likely noise but worth checking
    LOW      = "low"        # informational, consider reviewing
    INFO     = "info"       # observation, not a problem


SEVERITY_ICON = {
    Severity.CRITICAL: "🔴",
    Severity.HIGH:     "🟠",
    Severity.MEDIUM:   "🟡",
    Severity.LOW:      "🔵",
    Severity.INFO:     "⚪",
}


@dataclass
class Finding:
    """A single issue detected by a QA script."""
    check: str                              # which check raised this
    severity: Severity                      # how severe
    message: str                            # one-line summary
    details: str = ""                       # longer explanation, optional
    location: tuple[int, int, int, int] | None = None  # (x, y, w, h) bbox in source image
    measurement: dict[str, Any] = field(default_factory=dict)  # structured data
    annotated_image: str | None = None      # relative path to annotated output

    def to_dict(self) -> dict:
        d = asdict(self)
        d["severity"] = self.severity.value
        return d


# ─────────────────────────────────────────────────────────────
# Config loading
# ─────────────────────────────────────────────────────────────

def load_config(path: str | Path) -> dict:
    """
    Load a YAML config file. Returns a dict.

    The schema is open — scripts pull the sections they need. A missing
    section is a signal to skip that check. Use `config_section()` to
    pull per-script config with sensible defaults.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Config not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f) or {}
    if not isinstance(config, dict):
        raise ValueError(f"Config root must be a mapping, got {type(config)}")
    return config


def config_section(config: dict, section: str, defaults: dict | None = None) -> dict:
    """Pull a config section with defaults merged in. Script-local config."""
    section_data = config.get(section, {}) or {}
    if defaults:
        return {**defaults, **section_data}
    return section_data


def is_check_enabled(config: dict, check_name: str) -> bool:
    """
    Check whether a given check should run.

    If `enabled_checks` is present in config, only listed checks run.
    If absent, all checks run (opt-out via explicit `enabled: false` in section).
    """
    enabled = config.get("enabled_checks")
    if enabled is not None:
        return check_name in enabled
    section = config.get(check_name, {})
    return section.get("enabled", True) if isinstance(section, dict) else True


# ─────────────────────────────────────────────────────────────
# Image loading
# ─────────────────────────────────────────────────────────────

@dataclass
class LoadedImage:
    """An image with its metadata."""
    path: Path
    pil: Image.Image          # Pillow image (RGBA)
    rgb: np.ndarray           # numpy RGB array (H, W, 3) uint8
    gray: np.ndarray          # numpy grayscale (H, W) uint8
    bgr: np.ndarray           # OpenCV BGR array (H, W, 3) uint8
    width: int
    height: int
    dpi: tuple[float, float]  # (x_dpi, y_dpi), may be (72, 72) if unknown


def load_image(path: str | Path) -> LoadedImage:
    """Load an image into multiple representations for convenience."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Image not found: {path}")

    pil = Image.open(path).convert("RGBA")
    rgb = np.array(pil.convert("RGB"))
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    dpi = pil.info.get("dpi", (72.0, 72.0))

    return LoadedImage(
        path=path, pil=pil, rgb=rgb, gray=gray, bgr=bgr,
        width=pil.width, height=pil.height, dpi=dpi,
    )


# ─────────────────────────────────────────────────────────────
# Element detection — shared across alignment + spacing scripts
# ─────────────────────────────────────────────────────────────

@dataclass
class Element:
    """A detected UI element. A bounding box with optional labels."""
    x: int
    y: int
    w: int
    h: int
    area: int
    label: str = ""  # optional — set by callers

    @property
    def right(self) -> int:
        return self.x + self.w

    @property
    def bottom(self) -> int:
        return self.y + self.h

    @property
    def center_x(self) -> float:
        return self.x + self.w / 2

    @property
    def center_y(self) -> float:
        return self.y + self.h / 2

    def bbox(self) -> tuple[int, int, int, int]:
        return (self.x, self.y, self.w, self.h)


def detect_elements(
    image: LoadedImage,
    min_area: int = 100,
    max_area_pct: float = 0.5,
    canny_low: int = 50,
    canny_high: int = 150,
    dilate_iter: int = 2,
) -> list[Element]:
    """
    Detect UI elements via edge detection + contour extraction.

    This is a heuristic approach — it works well for crisp UI screenshots
    with clear boundaries, less well for photo-heavy or gradient-heavy
    images. Scripts that need more targeted detection should implement
    their own logic and not rely on this.

    Returns elements sorted top-to-bottom, left-to-right.
    """
    total_area = image.width * image.height
    max_area = int(total_area * max_area_pct)

    # Edge-detect, then dilate to merge broken segments into blobs
    edges = cv2.Canny(image.gray, canny_low, canny_high)
    kernel = np.ones((3, 3), np.uint8)
    dilated = cv2.dilate(edges, kernel, iterations=dilate_iter)

    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    elements: list[Element] = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        area = w * h
        if area < min_area or area > max_area:
            continue
        elements.append(Element(x=x, y=y, w=w, h=h, area=area))

    # Sort top-to-bottom, then left-to-right
    elements.sort(key=lambda e: (e.y, e.x))
    return elements


# ─────────────────────────────────────────────────────────────
# Output directory management
# ─────────────────────────────────────────────────────────────

def ensure_output_dir(output_path: str | Path, subdir: str | None = None) -> Path:
    """Make sure output directory exists and return Path."""
    path = Path(output_path)
    if subdir:
        path = path / subdir
    path.mkdir(parents=True, exist_ok=True)
    return path


# ─────────────────────────────────────────────────────────────
# Report writing
# ─────────────────────────────────────────────────────────────

class ReportWriter:
    """
    Build a consistent markdown report for a single QA script.

    Usage:
        r = ReportWriter("alignment", config_summary={"tolerance_px": 1})
        r.add_summary("Scanned 42 elements; 3 alignment issues flagged.")
        r.add_finding(Finding(...))
        r.add_visual("./output/alignment_annotated.png", "Annotated alignment check")
        r.write("./output/alignment_report.md")
    """

    def __init__(self, check_name: str, config_summary: dict | None = None):
        self.check_name = check_name
        self.config_summary = config_summary or {}
        self.summary_text: str = ""
        self.findings: list[Finding] = []
        self.visuals: list[tuple[str, str]] = []  # (path, caption)
        self.metadata: dict[str, Any] = {}

    def set_summary(self, text: str) -> None:
        self.summary_text = text

    def add_finding(self, finding: Finding) -> None:
        self.findings.append(finding)

    def add_visual(self, path: str, caption: str = "") -> None:
        self.visuals.append((path, caption))

    def set_metadata(self, key: str, value: Any) -> None:
        self.metadata[key] = value

    @property
    def counts(self) -> dict[Severity, int]:
        counts = {s: 0 for s in Severity}
        for f in self.findings:
            counts[f.severity] += 1
        return counts

    def to_markdown(self) -> str:
        lines: list[str] = []
        lines.append(f"# {self.check_name.replace('_', ' ').title()} Report")
        lines.append("")

        if self.summary_text:
            lines.append("## Summary")
            lines.append("")
            lines.append(self.summary_text)
            lines.append("")

        # Counts by severity
        counts = self.counts
        if any(counts.values()):
            lines.append("**Findings by severity:**")
            lines.append("")
            for sev in Severity:
                if counts[sev] > 0:
                    lines.append(f"- {SEVERITY_ICON[sev]} {sev.value.capitalize()}: {counts[sev]}")
            lines.append("")

        # Findings
        if self.findings:
            lines.append("## Findings")
            lines.append("")
            # Group by severity, critical first
            for sev in Severity:
                group = [f for f in self.findings if f.severity == sev]
                if not group:
                    continue
                lines.append(f"### {SEVERITY_ICON[sev]} {sev.value.capitalize()} ({len(group)})")
                lines.append("")
                for i, f in enumerate(group, 1):
                    lines.append(f"**{i}. {f.message}**")
                    if f.location:
                        x, y, w, h = f.location
                        lines.append(f"  - Location: `({x}, {y}) {w}×{h}px`")
                    if f.measurement:
                        for k, v in f.measurement.items():
                            lines.append(f"  - {k}: `{v}`")
                    if f.details:
                        lines.append("")
                        lines.append(f"  {f.details}")
                    if f.annotated_image:
                        lines.append(f"  - Annotated: `{f.annotated_image}`")
                    lines.append("")
        else:
            lines.append("## Findings")
            lines.append("")
            lines.append("_No findings._")
            lines.append("")

        # Visuals
        if self.visuals:
            lines.append("## Visual References")
            lines.append("")
            for path, caption in self.visuals:
                if caption:
                    lines.append(f"**{caption}**")
                    lines.append("")
                lines.append(f"![{caption}]({path})")
                lines.append("")

        # Configuration
        if self.config_summary:
            lines.append("## Configuration")
            lines.append("")
            lines.append("```yaml")
            lines.append(yaml.dump(self.config_summary, default_flow_style=False).rstrip())
            lines.append("```")
            lines.append("")

        # Metadata
        if self.metadata:
            lines.append("## Metadata")
            lines.append("")
            for k, v in self.metadata.items():
                lines.append(f"- **{k}**: {v}")
            lines.append("")

        lines.append("---")
        lines.append("")
        lines.append("_Generated by `visual-qa-toolkit`_")

        return "\n".join(lines)

    def write(self, output_path: str | Path) -> Path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(self.to_markdown(), encoding="utf-8")
        return output_path

    def to_json_summary(self) -> dict:
        """For use by the suite runner's consolidated report."""
        return {
            "check": self.check_name,
            "summary": self.summary_text,
            "counts": {k.value: v for k, v in self.counts.items()},
            "findings": [f.to_dict() for f in self.findings],
            "visuals": [{"path": p, "caption": c} for p, c in self.visuals],
            "metadata": self.metadata,
        }


# ─────────────────────────────────────────────────────────────
# Annotation helpers
# ─────────────────────────────────────────────────────────────

# Colors used for annotations — consistent across scripts
ANNOTATION_COLORS = {
    "primary":    (37, 99, 235),    # blue — detected elements
    "warning":    (234, 88, 12),    # orange — borderline / medium findings
    "critical":   (220, 38, 38),    # red — critical findings
    "success":    (22, 163, 74),    # green — passed checks
    "guide":      (139, 92, 246),   # violet — reference/grid lines
    "neutral":    (107, 114, 128),  # gray — labels
}


def draw_bbox(
    image_bgr: np.ndarray,
    bbox: tuple[int, int, int, int],
    color: str = "primary",
    thickness: int = 2,
    label: str = "",
) -> np.ndarray:
    """Draw a labeled bounding box on a BGR image (in place)."""
    x, y, w, h = bbox
    rgb = ANNOTATION_COLORS[color]
    bgr = (rgb[2], rgb[1], rgb[0])
    cv2.rectangle(image_bgr, (x, y), (x + w, y + h), bgr, thickness)
    if label:
        # Draw label with background for readability
        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)
        cv2.rectangle(image_bgr, (x, y - th - 4), (x + tw + 4, y), bgr, -1)
        cv2.putText(
            image_bgr, label, (x + 2, y - 2),
            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1, cv2.LINE_AA,
        )
    return image_bgr


def draw_measurement(
    image_bgr: np.ndarray,
    start: tuple[int, int],
    end: tuple[int, int],
    label: str,
    color: str = "warning",
) -> np.ndarray:
    """Draw a measurement line between two points with a label."""
    rgb = ANNOTATION_COLORS[color]
    bgr = (rgb[2], rgb[1], rgb[0])
    cv2.line(image_bgr, start, end, bgr, 2, cv2.LINE_AA)
    # Tick marks at endpoints
    if start[0] == end[0]:  # vertical line
        cv2.line(image_bgr, (start[0] - 4, start[1]), (start[0] + 4, start[1]), bgr, 1)
        cv2.line(image_bgr, (end[0] - 4, end[1]), (end[0] + 4, end[1]), bgr, 1)
    elif start[1] == end[1]:  # horizontal line
        cv2.line(image_bgr, (start[0], start[1] - 4), (start[0], start[1] + 4), bgr, 1)
        cv2.line(image_bgr, (end[0], end[1] - 4), (end[0], end[1] + 4), bgr, 1)

    mx = (start[0] + end[0]) // 2
    my = (start[1] + end[1]) // 2
    (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.45, 1)
    cv2.rectangle(image_bgr, (mx + 4, my - th - 2), (mx + tw + 8, my + 2), bgr, -1)
    cv2.putText(
        image_bgr, label, (mx + 6, my),
        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1, cv2.LINE_AA,
    )
    return image_bgr


def save_bgr_image(image_bgr: np.ndarray, path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(path), image_bgr)
    return path


# ─────────────────────────────────────────────────────────────
# Color utilities — WCAG contrast, sRGB/linear, delta-E
# ─────────────────────────────────────────────────────────────

def sample_pixel(rgb_array: np.ndarray, x: int, y: int, radius: int = 2) -> tuple[int, int, int]:
    """Sample a pixel color averaging a small neighborhood to reduce aliasing noise."""
    h, w = rgb_array.shape[:2]
    x0, x1 = max(0, x - radius), min(w, x + radius + 1)
    y0, y1 = max(0, y - radius), min(h, y + radius + 1)
    region = rgb_array[y0:y1, x0:x1]
    mean = region.reshape(-1, 3).mean(axis=0)
    return tuple(int(round(v)) for v in mean)


def srgb_to_linear(channel: float) -> float:
    """sRGB gamma correction to linear."""
    c = channel / 255.0
    if c <= 0.03928:
        return c / 12.92
    return ((c + 0.055) / 1.055) ** 2.4


def relative_luminance(rgb: tuple[int, int, int]) -> float:
    """WCAG 2.x relative luminance formula."""
    r, g, b = rgb
    rl = srgb_to_linear(r)
    gl = srgb_to_linear(g)
    bl = srgb_to_linear(b)
    return 0.2126 * rl + 0.7152 * gl + 0.0722 * bl


def wcag_contrast_ratio(fg: tuple[int, int, int], bg: tuple[int, int, int]) -> float:
    """WCAG 2.x contrast ratio (1.0 to 21.0)."""
    l1 = relative_luminance(fg)
    l2 = relative_luminance(bg)
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def delta_e_cie76(c1: tuple[int, int, int], c2: tuple[int, int, int]) -> float:
    """
    Rough CIE76 delta-E in Lab space. Good enough for "is this color in the
    palette" — not a substitute for CIEDE2000 for perceptual matching, but
    substantially better than RGB euclidean.
    """
    lab1 = cv2.cvtColor(np.uint8([[c1]]), cv2.COLOR_RGB2LAB)[0][0].astype(float)
    lab2 = cv2.cvtColor(np.uint8([[c2]]), cv2.COLOR_RGB2LAB)[0][0].astype(float)
    return float(np.linalg.norm(lab1 - lab2))


def hex_to_rgb(hex_str: str) -> tuple[int, int, int]:
    """`#RRGGBB` or `RRGGBB` → (r, g, b)."""
    h = hex_str.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    return "#{:02X}{:02X}{:02X}".format(*rgb)
