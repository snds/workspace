"""
_common.py — Shared utilities for the render-qa-toolkit.

Simplified sibling of visual-qa-toolkit's _common: config, image I/O,
Finding / ReportWriter, and light annotation helpers. No UI-element
detection or WCAG math — those stay in visual-qa-toolkit.
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from typing import Any

import cv2
import numpy as np
import yaml
from PIL import Image


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter("[%(name)s] %(levelname)s: %(message)s")
        )
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


log = get_logger("render-qa")


class Severity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


SEVERITY_ICON = {
    Severity.CRITICAL: "🔴",
    Severity.HIGH: "🟠",
    Severity.MEDIUM: "🟡",
    Severity.LOW: "🔵",
    Severity.INFO: "⚪",
}


@dataclass
class Finding:
    check: str
    severity: Severity
    message: str
    details: str = ""
    location: tuple[int, int, int, int] | None = None
    measurement: dict[str, Any] = field(default_factory=dict)
    annotated_image: str | None = None
    ledger_id: str | None = None  # optional Visual Failure-Mode Ledger ID

    def to_dict(self) -> dict:
        d = asdict(self)
        d["severity"] = self.severity.value
        return d


def load_config(path: str | Path) -> dict:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Config not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f) or {}
    if not isinstance(config, dict):
        raise ValueError(f"Config root must be a mapping, got {type(config)}")
    return config


def config_section(config: dict, section: str, defaults: dict | None = None) -> dict:
    section_data = config.get(section, {}) or {}
    if defaults:
        return {**defaults, **section_data}
    return section_data


def is_check_enabled(config: dict, check_name: str) -> bool:
    enabled = config.get("enabled_checks")
    if enabled is not None:
        return check_name in enabled
    section = config.get(check_name, {})
    return section.get("enabled", True) if isinstance(section, dict) else True


@dataclass
class LoadedImage:
    path: Path
    pil: Image.Image
    rgb: np.ndarray
    gray: np.ndarray
    bgr: np.ndarray
    width: int
    height: int


def load_image(path: str | Path) -> LoadedImage:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Image not found: {path}")
    pil = Image.open(path).convert("RGBA")
    rgb = np.array(pil.convert("RGB"))
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    return LoadedImage(
        path=path, pil=pil, rgb=rgb, gray=gray, bgr=bgr,
        width=pil.width, height=pil.height,
    )


def load_json(path: str | Path) -> dict | list:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"JSON not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def ensure_output_dir(output_path: str | Path, subdir: str | None = None) -> Path:
    path = Path(output_path)
    if subdir:
        path = path / subdir
    path.mkdir(parents=True, exist_ok=True)
    return path


def list_image_files(folder: str | Path, extensions: tuple[str, ...] = (".png", ".jpg", ".jpeg", ".webp")) -> list[Path]:
    folder = Path(folder)
    if not folder.is_dir():
        raise NotADirectoryError(f"Not a directory: {folder}")
    files = [
        p for p in sorted(folder.iterdir())
        if p.is_file() and p.suffix.lower() in extensions
    ]
    return files


def luminance_rel(rgb: np.ndarray) -> np.ndarray:
    """Approximate relative luminance (0–1) from uint8 RGB."""
    r = rgb[..., 0].astype(np.float64) / 255.0
    g = rgb[..., 1].astype(np.float64) / 255.0
    b = rgb[..., 2].astype(np.float64) / 255.0
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


ANNOTATION_COLORS = {
    "primary": (37, 99, 235),
    "warning": (234, 88, 12),
    "critical": (220, 38, 38),
    "success": (22, 163, 74),
    "guide": (139, 92, 246),
    "neutral": (107, 114, 128),
}


def draw_bbox(
    image_bgr: np.ndarray,
    bbox: tuple[int, int, int, int],
    color: str = "primary",
    thickness: int = 2,
    label: str = "",
) -> np.ndarray:
    x, y, w, h = bbox
    rgb = ANNOTATION_COLORS[color]
    bgr = (rgb[2], rgb[1], rgb[0])
    cv2.rectangle(image_bgr, (x, y), (x + w, y + h), bgr, thickness)
    if label:
        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)
        cv2.rectangle(image_bgr, (x, y - th - 4), (x + tw + 4, y), bgr, -1)
        cv2.putText(
            image_bgr, label, (x + 2, y - 2),
            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1, cv2.LINE_AA,
        )
    return image_bgr


def save_bgr_image(image_bgr: np.ndarray, path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(path), image_bgr)
    return path


def save_rgb_image(image_rgb: np.ndarray, path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(image_rgb.astype(np.uint8)).save(path)
    return path


class ReportWriter:
    def __init__(self, check_name: str, config_summary: dict | None = None):
        self.check_name = check_name
        self.config_summary = config_summary or {}
        self.summary_text: str = ""
        self.findings: list[Finding] = []
        self.visuals: list[tuple[str, str]] = []
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
        counts = self.counts
        if any(counts.values()):
            lines.append("**Findings by severity:**")
            lines.append("")
            for sev in Severity:
                if counts[sev] > 0:
                    lines.append(f"- {SEVERITY_ICON[sev]} {sev.value.capitalize()}: {counts[sev]}")
            lines.append("")
        if self.findings:
            lines.append("## Findings")
            lines.append("")
            for sev in Severity:
                group = [f for f in self.findings if f.severity == sev]
                if not group:
                    continue
                lines.append(f"### {SEVERITY_ICON[sev]} {sev.value.capitalize()} ({len(group)})")
                lines.append("")
                for i, f in enumerate(group, 1):
                    lid = f" [{f.ledger_id}]" if f.ledger_id else ""
                    lines.append(f"**{i}. {f.message}{lid}**")
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
        if self.visuals:
            lines.append("## Visual References")
            lines.append("")
            for path, caption in self.visuals:
                if caption:
                    lines.append(f"**{caption}**")
                    lines.append("")
                lines.append(f"![{caption}]({path})")
                lines.append("")
        if self.config_summary:
            lines.append("## Configuration")
            lines.append("")
            lines.append("```yaml")
            lines.append(yaml.dump(self.config_summary, default_flow_style=False).rstrip())
            lines.append("```")
            lines.append("")
        if self.metadata:
            lines.append("## Metadata")
            lines.append("")
            for k, v in self.metadata.items():
                lines.append(f"- **{k}**: {v}")
            lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("_Generated by `render-qa-toolkit`_")
        return "\n".join(lines)

    def write(self, output_path: str | Path) -> Path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(self.to_markdown(), encoding="utf-8")
        return output_path

    def to_json_summary(self) -> dict:
        return {
            "check": self.check_name,
            "summary": self.summary_text,
            "counts": {k.value: v for k, v in self.counts.items()},
            "findings": [f.to_dict() for f in self.findings],
            "visuals": [{"path": p, "caption": c} for p, c in self.visuals],
            "metadata": self.metadata,
        }


def normalize_perfcapture(data: dict) -> dict:
    """
    Normalize Legion ?perfcapture JSON (and simplified forms) into:
      {passes: [{name, ms}], total_ms, raw_mode, extras}

    Accepted shapes:
      - {passes: [{name, ms}], total_ms}
      - {mode: 'passes', rows: [{pass|name, medianMs|ms}], totalMedianMs|total_ms}
      - {mode: 'composite', gpuMedianMs, ...} → single synthetic pass
      - {mode: 'capture', rows: [{phase, gpuMedianMs}], ...}
    """
    if not isinstance(data, dict):
        raise ValueError("perfcapture JSON root must be an object")

    extras: dict[str, Any] = {}
    for k in ("mode", "method", "viewport", "baselineAu", "attribution", "note"):
        if k in data:
            extras[k] = data[k]

    # Simplified / preferred form
    if "passes" in data and isinstance(data["passes"], list):
        passes = []
        for p in data["passes"]:
            name = p.get("name") or p.get("pass") or p.get("phase") or "unnamed"
            ms = p.get("ms", p.get("medianMs", p.get("gpuMedianMs")))
            if ms is None:
                continue
            passes.append({"name": str(name), "ms": float(ms)})
        total = data.get("total_ms", data.get("totalMedianMs"))
        if total is None:
            total = sum(p["ms"] for p in passes)
        return {
            "passes": passes,
            "total_ms": float(total),
            "raw_mode": data.get("mode", "passes"),
            "extras": extras,
        }

    # Legion passes / capture rows
    if "rows" in data and isinstance(data["rows"], list):
        passes = []
        for r in data["rows"]:
            name = r.get("pass") or r.get("phase") or r.get("name") or "unnamed"
            ms = r.get("medianMs", r.get("ms", r.get("gpuMedianMs")))
            if ms is None:
                continue
            passes.append({"name": str(name), "ms": float(ms)})
        total = data.get("totalMedianMs", data.get("total_ms"))
        if total is None:
            total = sum(p["ms"] for p in passes)
        return {
            "passes": passes,
            "total_ms": float(total),
            "raw_mode": data.get("mode", "rows"),
            "extras": extras,
        }

    # Composite single number
    if "gpuMedianMs" in data:
        ms = float(data["gpuMedianMs"])
        return {
            "passes": [{"name": "composite", "ms": ms}],
            "total_ms": ms,
            "raw_mode": data.get("mode", "composite"),
            "extras": extras,
        }

    raise ValueError(
        "Unrecognized perfcapture JSON. Expected passes[], rows[], or gpuMedianMs."
    )


def print_waterfall(passes: list[dict], total_ms: float, budget_ms: float | None = None) -> str:
    """ASCII waterfall of pass ms; returns the printed string."""
    if not passes:
        text = "(no passes)"
        print(text)
        return text
    ranked = sorted(passes, key=lambda p: p["ms"], reverse=True)
    max_ms = max(p["ms"] for p in ranked) or 1.0
    bar_w = 40
    lines = []
    lines.append(f"{'pass':<28} {'ms':>8}  bar")
    lines.append("-" * 80)
    for p in ranked:
        width = int(round((p["ms"] / max_ms) * bar_w))
        bar = "█" * width
        lines.append(f"{p['name']:<28} {p['ms']:>8.3f}  {bar}")
    lines.append("-" * 80)
    budget_note = f"  (budget {budget_ms:.2f} ms)" if budget_ms is not None else ""
    lines.append(f"{'TOTAL':<28} {total_ms:>8.3f}{budget_note}")
    text = "\n".join(lines)
    print(text)
    return text
