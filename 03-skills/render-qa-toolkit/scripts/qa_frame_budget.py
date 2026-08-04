"""
qa_frame_budget.py — Ingest ?perfcapture-like JSON and check against frame budget.

Usage:
    python -m scripts.qa_frame_budget --input capture.json --config configs/default.yaml --output ./qa-out

Exit codes (standalone):
    0 — within budget
    1 — over budget (or high findings)
    2 — critical / unreadable input
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from ._common import (
    Finding,
    ReportWriter,
    Severity,
    config_section,
    ensure_output_dir,
    load_config,
    load_json,
    log,
    normalize_perfcapture,
    print_waterfall,
)

CHECK_NAME = "frame_budget"

DEFAULTS = {
    "budget_ms": 16.67,          # 60 Hz floor before compositor overhead
    "real_budget_ms": 14.0,      # practical in-browser GPU budget at 60 fps
    "use_real_budget": True,     # compare against real_budget_ms when true
    "warn_pct": 0.85,            # warn when total ≥ this fraction of budget
}


def run(input_path: Path, config: dict, output_dir: Path) -> ReportWriter:
    cfg = config_section(config, CHECK_NAME, DEFAULTS)
    report = ReportWriter(CHECK_NAME, config_summary=cfg)
    report.set_metadata("input", str(input_path))

    raw = load_json(input_path)
    if not isinstance(raw, dict):
        report.add_finding(Finding(
            check=CHECK_NAME,
            severity=Severity.CRITICAL,
            message="perfcapture JSON root must be an object",
        ))
        report.set_summary("Failed: invalid JSON shape.")
        return report

    try:
        norm = normalize_perfcapture(raw)
    except ValueError as e:
        report.add_finding(Finding(
            check=CHECK_NAME,
            severity=Severity.CRITICAL,
            message=str(e),
        ))
        report.set_summary("Failed: unrecognized perfcapture shape.")
        return report

    budget = float(cfg["real_budget_ms"] if cfg.get("use_real_budget", True) else cfg["budget_ms"])
    total = norm["total_ms"]
    passes = norm["passes"]

    report.set_metadata("raw_mode", norm["raw_mode"])
    report.set_metadata("total_ms", round(total, 3))
    report.set_metadata("budget_ms", budget)
    report.set_metadata("pass_count", len(passes))
    if norm.get("extras"):
        for k, v in norm["extras"].items():
            if k in ("viewport", "baselineAu", "method"):
                report.set_metadata(k, v)

    print()
    print(f"Frame budget waterfall — budget {budget:.2f} ms")
    waterfall = print_waterfall(passes, total, budget_ms=budget)
    wf_path = ensure_output_dir(output_dir) / "frame_budget_waterfall.txt"
    wf_path.write_text(waterfall + "\n", encoding="utf-8")
    report.add_visual(wf_path.name, "Pass waterfall (text)")

    ratio = total / budget if budget > 0 else float("inf")
    if total > budget:
        report.add_finding(Finding(
            check=CHECK_NAME,
            severity=Severity.CRITICAL,
            message=f"Total {total:.3f} ms exceeds budget {budget:.2f} ms ({ratio:.0%})",
            details=(
                "60 fps floor ≈ 16.67 ms; real in-browser GPU budget after compositor "
                "overhead is ~14–15 ms. Numbers must come from harness JSON (?perfcapture), "
                "not FPS counter vibes."
            ),
            measurement={"total_ms": round(total, 3), "budget_ms": budget, "ratio": round(ratio, 3)},
        ))
    elif ratio >= float(cfg.get("warn_pct", 0.85)):
        report.add_finding(Finding(
            check=CHECK_NAME,
            severity=Severity.HIGH,
            message=f"Total {total:.3f} ms is {ratio:.0%} of budget {budget:.2f} ms (headroom thin)",
            measurement={"total_ms": round(total, 3), "budget_ms": budget, "ratio": round(ratio, 3)},
        ))
    else:
        report.add_finding(Finding(
            check=CHECK_NAME,
            severity=Severity.INFO,
            message=f"Total {total:.3f} ms within budget {budget:.2f} ms ({ratio:.0%})",
            measurement={"total_ms": round(total, 3), "budget_ms": budget, "ratio": round(ratio, 3)},
        ))

    report.set_summary(
        f"total={total:.3f} ms · budget={budget:.2f} ms · "
        f"{len(passes)} pass(es) · mode={norm['raw_mode']}"
    )
    return report


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Check ?perfcapture JSON against frame budget; print waterfall."
    )
    parser.add_argument("--input", required=True, help="Path to perfcapture JSON")
    parser.add_argument("--config", required=True, help="YAML config")
    parser.add_argument("--output", required=True, help="Output directory")
    args = parser.parse_args()

    config = load_config(args.config)
    output_dir = ensure_output_dir(args.output)
    report = run(Path(args.input), config, output_dir)
    report_path = output_dir / f"{CHECK_NAME}_report.md"
    report.write(report_path)
    log.info(f"{CHECK_NAME}: wrote report → {report_path}")
    print(f"Report written to {report_path} ({sum(report.counts.values())} finding(s))")

    if report.counts[Severity.CRITICAL] > 0:
        sys.exit(2)
    if report.counts[Severity.HIGH] > 0:
        sys.exit(1)
    # Also fail if total over budget even if severity mapping changes
    over = any(
        f.severity == Severity.CRITICAL and "exceeds budget" in f.message
        for f in report.findings
    )
    sys.exit(2 if over else 0)


if __name__ == "__main__":
    main()
