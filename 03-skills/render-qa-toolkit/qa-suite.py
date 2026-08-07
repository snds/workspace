#!/usr/bin/env python3
"""
qa-suite.py — Orchestrator for the render-qa-toolkit.

Usage:
    python qa-suite.py --config configs/legion.yaml --output ./qa-out --perf capture.json
    python qa-suite.py --config configs/default.yaml --output ./qa-out \\
        --image beauty.png --reference northstar.png --frames ./frames \\
        --only native_grid,histogram_hdr,reference_match,temporal_delta \\
        --labeled-native
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

from scripts._common import (
    Finding,
    ReportWriter,
    Severity,
    SEVERITY_ICON,
    ensure_output_dir,
    is_check_enabled,
    load_config,
    log,
)
from scripts import (
    qa_frame_budget,
    qa_pass_attribution,
    qa_native_grid,
    qa_histogram_hdr,
    qa_false_color_exposure,
    qa_temporal_delta,
    qa_motion_stress,
    qa_reference_match,
    qa_video_extract,
    qa_ledger_detect,
)

PERF_CHECKS = ("frame_budget", "pass_attribution")
IMAGE_CHECKS = (
    "native_grid",
    "histogram_hdr",
    "false_color_exposure",
    "ledger_detect",
)
FRAME_FOLDER_CHECKS = ("temporal_delta", "motion_stress")

MODULES = {
    "frame_budget": qa_frame_budget,
    "pass_attribution": qa_pass_attribution,
    "native_grid": qa_native_grid,
    "histogram_hdr": qa_histogram_hdr,
    "false_color_exposure": qa_false_color_exposure,
    "temporal_delta": qa_temporal_delta,
    "motion_stress": qa_motion_stress,
    "reference_match": qa_reference_match,
    "video_extract": qa_video_extract,
    "ledger_detect": qa_ledger_detect,
}


def _run_safe(name: str, fn) -> ReportWriter:
    try:
        return fn()
    except Exception as e:
        log.error("  ✗ %s failed: %s", name, e)
        err = ReportWriter(name)
        err.set_summary(f"Check failed with error: {e}")
        err.add_finding(Finding(
            check=name,
            severity=Severity.CRITICAL,
            message=f"Check execution failed: {type(e).__name__}: {e}",
        ))
        return err


def main() -> int:
    ap = argparse.ArgumentParser(
        description=(
            "Orchestrator for the render-qa-toolkit "
            "(frame budget, native grid, temporal, northstar match)."
        )
    )
    ap.add_argument("--config", required=True, type=Path, help="YAML config")
    ap.add_argument("--output", required=True, type=Path, help="Output directory")
    ap.add_argument("--perf", type=Path, help="perfcapture JSON (?perfcapture paste)")
    ap.add_argument("--image", type=Path, help="PNG/JPG still for image checks")
    ap.add_argument("--reference", type=Path, help="Northstar still for reference_match")
    ap.add_argument("--frames", type=Path, help="Folder of frames (temporal / motion stress)")
    ap.add_argument("--video", type=Path, help="Local video for video_extract (needs ffmpeg)")
    ap.add_argument(
        "--only",
        type=str,
        default="",
        help="Comma-separated check names to run",
    )
    ap.add_argument(
        "--labeled-native",
        action="store_true",
        help="Assert --image is native-resolution evidence (native_grid gates)",
    )
    args = ap.parse_args()

    config = load_config(args.config)
    out = ensure_output_dir(args.output)
    only = {s.strip() for s in args.only.split(",") if s.strip()} if args.only else None

    reports: list[tuple[str, ReportWriter]] = []
    skipped: list[tuple[str, str]] = []

    def want(name: str) -> bool:
        if only is not None:
            return name in only
        return is_check_enabled(config, name)

    for name in PERF_CHECKS:
        if not want(name):
            if only is not None and name not in only:
                skipped.append((name, "not in --only list"))
            elif not is_check_enabled(config, name):
                skipped.append((name, "disabled in config"))
            continue
        if not args.perf:
            skipped.append((name, "requires --perf JSON"))
            continue
        log.info("▶ Running %s...", name)
        reports.append((name, _run_safe(name, lambda n=name: MODULES[n].run(args.perf, config, out))))

    for name in IMAGE_CHECKS:
        if not want(name):
            if only is not None and name not in only:
                skipped.append((name, "not in --only list"))
            elif not is_check_enabled(config, name):
                skipped.append((name, "disabled in config"))
            continue
        if not args.image:
            skipped.append((name, "requires --image"))
            continue
        log.info("▶ Running %s...", name)
        if name == "native_grid":
            reports.append((
                name,
                _run_safe(
                    name,
                    lambda: qa_native_grid.run(
                        args.image, config, out, labeled_native=args.labeled_native
                    ),
                ),
            ))
        else:
            reports.append((name, _run_safe(name, lambda n=name: MODULES[n].run(args.image, config, out))))

    for name in FRAME_FOLDER_CHECKS:
        if not want(name):
            if only is not None and name not in only:
                skipped.append((name, "not in --only list"))
            elif not is_check_enabled(config, name):
                skipped.append((name, "disabled in config"))
            continue
        if not args.frames:
            skipped.append((name, "requires --frames folder"))
            continue
        log.info("▶ Running %s...", name)
        reports.append((name, _run_safe(name, lambda n=name: MODULES[n].run(args.frames, config, out))))

    if want("reference_match"):
        if not args.image or not args.reference:
            skipped.append(("reference_match", "requires --image and --reference"))
        else:
            log.info("▶ Running reference_match...")
            reports.append((
                "reference_match",
                _run_safe(
                    "reference_match",
                    lambda: qa_reference_match.run(
                        args.image, config, out, reference_override=args.reference
                    ),
                ),
            ))
    elif only is not None and "reference_match" not in only:
        skipped.append(("reference_match", "not in --only list"))
    elif not is_check_enabled(config, "reference_match"):
        skipped.append(("reference_match", "disabled in config"))

    if want("video_extract"):
        if not args.video:
            skipped.append(("video_extract", "requires --video"))
        else:
            log.info("▶ Running video_extract...")
            reports.append((
                "video_extract",
                _run_safe(
                    "video_extract",
                    lambda: qa_video_extract.run(args.video, config, out),
                ),
            ))
    elif only is not None and "video_extract" not in only:
        skipped.append(("video_extract", "not in --only list"))
    elif not is_check_enabled(config, "video_extract"):
        skipped.append(("video_extract", "disabled in config"))

    # Per-check reports
    for check, r in reports:
        r.write(out / f"{check}_report.md")

    # Consolidated markdown
    lines: list[str] = [
        "# Render QA — Consolidated Report",
        "",
        f"- **Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"- **Config**: `{args.config}`",
        f"- **Checks run**: {len(reports)} · **Skipped**: {len(skipped)}",
        "",
        "## Overall",
        "",
    ]
    total_counts = {s: 0 for s in Severity}
    for _, r in reports:
        for sev, n in r.counts.items():
            total_counts[sev] += n
    if any(total_counts.values()):
        lines.append("**Findings across all checks:**")
        lines.append("")
        for sev in Severity:
            if total_counts[sev] > 0:
                lines.append(f"- {SEVERITY_ICON[sev]} {sev.value.capitalize()}: {total_counts[sev]}")
        lines.append("")
    else:
        lines.append("No findings.")
        lines.append("")

    lines += [
        "## Per-check summary",
        "",
        "| Check | Critical | High | Medium | Low | Info | Report |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for check, r in reports:
        c = r.counts
        lines.append(
            f"| **{check}** | {c[Severity.CRITICAL]} | {c[Severity.HIGH]} | "
            f"{c[Severity.MEDIUM]} | {c[Severity.LOW]} | {c[Severity.INFO]} | "
            f"[`{check}_report.md`]({check}_report.md) |"
        )

    if skipped:
        lines.append("")
        lines.append("## Skipped")
        lines.append("")
        for name, reason in skipped:
            lines.append(f"- `{name}`: {reason}")

    lines.append("")
    lines.append("## Top findings")
    lines.append("")
    all_findings: list[tuple[str, Finding]] = []
    for check, r in reports:
        for f in r.findings:
            all_findings.append((check, f))
    sev_order = {s: i for i, s in enumerate(Severity)}
    all_findings.sort(key=lambda t: sev_order[t[1].severity])
    for check, f in all_findings[:20]:
        lid = f" `{f.ledger_id}`" if f.ledger_id else ""
        lines.append(f"- {SEVERITY_ICON[f.severity]} **[{check}]**{lid} {f.message}")
    if not all_findings:
        lines.append("_No findings._")
    if len(all_findings) > 20:
        lines.append(f"- _…and {len(all_findings) - 20} more._")

    lines += [
        "",
        "## Triple done-gate reminder",
        "",
        "Still grid + motion frame sequence + measured ms. "
        "A single screenshot alone is incomplete.",
        "",
        "---",
        "",
        "_Consolidated by `qa-suite.py` from the `render-qa-toolkit`._",
        "",
    ]
    (out / "qa_report.md").write_text("\n".join(lines), encoding="utf-8")
    # Keep alias for earlier drafts
    (out / "consolidated-report.md").write_text("\n".join(lines), encoding="utf-8")

    summary = {
        "generated_at": datetime.now().isoformat(),
        "checks_run": [c for c, _ in reports],
        "skipped": [{"check": n, "reason": r} for n, r in skipped],
        "reports": {c: r.to_json_summary() for c, r in reports},
    }
    (out / "qa_report.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    print()
    print(f"✓ Suite complete — {len(reports)} check(s) run, {len(skipped)} skipped")
    print(f"  Consolidated: {out / 'qa_report.md'}")
    print(f"  JSON:         {out / 'qa_report.json'}")

    any_critical = any(r.counts[Severity.CRITICAL] > 0 for _, r in reports)
    any_high = any(r.counts[Severity.HIGH] > 0 for _, r in reports)
    if any_critical:
        return 2
    if any_high:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
