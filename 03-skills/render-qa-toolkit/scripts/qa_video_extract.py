"""
qa_video_extract.py — Wrapper around ffmpeg to extract frames from a video.

Dependency: ffmpeg must be on PATH (`command -v ffmpeg`). See capability-registry
and SKILL.md. This script does not download remote URLs — pass a local file.

Usage:
    python -m scripts.qa_video_extract --input flythrough.mp4 --config configs/default.yaml --output ./qa-out
    python -m scripts.qa_video_extract --input flythrough.mp4 --config configs/default.yaml --output ./qa-out --fps 2
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path

from ._common import (
    Finding,
    ReportWriter,
    Severity,
    config_section,
    ensure_output_dir,
    load_config,
    log,
)

CHECK_NAME = "video_extract"

DEFAULTS = {
    "fps": 2,                    # extract N frames per second
    "pattern": "frame_%04d.png",
    "start_sec": None,
    "duration_sec": None,
    "extra_vf": "",              # optional additional -vf chain fragment
}


def _ffmpeg_available() -> bool:
    return shutil.which("ffmpeg") is not None


def run(input_path: Path, config: dict, output_dir: Path, fps_override: float | None = None) -> ReportWriter:
    cfg = config_section(config, CHECK_NAME, DEFAULTS)
    report = ReportWriter(CHECK_NAME, config_summary=cfg)
    report.set_metadata("input", str(input_path))

    if not input_path.exists():
        report.add_finding(Finding(
            check=CHECK_NAME,
            severity=Severity.CRITICAL,
            message=f"Video not found: {input_path}",
        ))
        report.set_summary("Failed: missing input.")
        return report

    if not _ffmpeg_available():
        report.add_finding(Finding(
            check=CHECK_NAME,
            severity=Severity.CRITICAL,
            message="ffmpeg not found on PATH",
            details=(
                "Install ffmpeg before running video_extract. "
                "macOS: `brew install ffmpeg`. "
                "See capability-registry → ffmpeg."
            ),
        ))
        report.set_summary("Blocked: ffmpeg missing.")
        return report

    out = ensure_output_dir(output_dir) / "extracted_frames"
    out.mkdir(parents=True, exist_ok=True)
    pattern = cfg.get("pattern") or "frame_%04d.png"
    dest = out / pattern

    fps = fps_override if fps_override is not None else float(cfg.get("fps", 2))
    vf_parts = [f"fps={fps}"]
    extra = (cfg.get("extra_vf") or "").strip()
    if extra:
        vf_parts.append(extra)
    vf = ",".join(vf_parts)

    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error"]
    if cfg.get("start_sec") is not None:
        cmd += ["-ss", str(cfg["start_sec"])]
    cmd += ["-i", str(input_path)]
    if cfg.get("duration_sec") is not None:
        cmd += ["-t", str(cfg["duration_sec"])]
    cmd += ["-vf", vf, str(dest)]

    report.set_metadata("ffmpeg_cmd", " ".join(cmd))
    log.info(f"Running: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        report.add_finding(Finding(
            check=CHECK_NAME,
            severity=Severity.CRITICAL,
            message=f"ffmpeg failed with exit {e.returncode}",
            details=str(e),
        ))
        report.set_summary("ffmpeg failed.")
        return report

    frames = sorted(out.glob("*.png")) + sorted(out.glob("*.jpg"))
    report.add_finding(Finding(
        check=CHECK_NAME,
        severity=Severity.INFO,
        message=f"Extracted {len(frames)} frame(s) to {out}",
        measurement={"frames": len(frames), "fps": fps, "dir": str(out)},
    ))
    report.set_metadata("frame_count", len(frames))
    report.set_metadata("frames_dir", str(out))
    report.set_summary(f"Extracted {len(frames)} frames @ fps={fps} → {out}")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract frames via ffmpeg (requires ffmpeg on PATH)."
    )
    parser.add_argument("--input", required=True, help="Local video file")
    parser.add_argument("--config", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--fps", type=float, default=None, help="Override config fps")
    args = parser.parse_args()

    config = load_config(args.config)
    output_dir = ensure_output_dir(args.output)
    report = run(Path(args.input), config, output_dir, fps_override=args.fps)
    report_path = output_dir / f"{CHECK_NAME}_report.md"
    report.write(report_path)
    log.info(f"{CHECK_NAME}: wrote report → {report_path}")
    print(f"Report written to {report_path} ({sum(report.counts.values())} finding(s))")


if __name__ == "__main__":
    main()
