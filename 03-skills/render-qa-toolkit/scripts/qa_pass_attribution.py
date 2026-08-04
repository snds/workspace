"""
qa_pass_attribution.py — Rank render passes by milliseconds.

Usage:
    python -m scripts.qa_pass_attribution --input capture.json --config configs/default.yaml --output ./qa-out
"""
from __future__ import annotations

import argparse
import json
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

CHECK_NAME = "pass_attribution"

DEFAULTS = {
    "top_n": 10,
    "flag_share_pct": 0.35,  # flag a single pass that eats ≥ this of total
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

    passes = sorted(norm["passes"], key=lambda p: p["ms"], reverse=True)
    total = norm["total_ms"] or 1.0
    top_n = int(cfg.get("top_n", 10))

    print()
    print("Pass attribution (ranked by ms)")
    waterfall = print_waterfall(passes, norm["total_ms"])

    ranking = [
        {"rank": i + 1, "name": p["name"], "ms": round(p["ms"], 3),
         "share_pct": round(100.0 * p["ms"] / total, 1)}
        for i, p in enumerate(passes)
    ]
    rank_path = ensure_output_dir(output_dir) / "pass_attribution_ranking.json"
    rank_path.write_text(json.dumps(ranking, indent=2), encoding="utf-8")
    report.add_visual(rank_path.name, "Ranked pass list (JSON)")
    wf_path = output_dir / "pass_attribution_waterfall.txt"
    wf_path.write_text(waterfall + "\n", encoding="utf-8")
    report.add_visual(wf_path.name, "Waterfall (text)")

    flag_share = float(cfg.get("flag_share_pct", 0.35))
    for p in passes[:top_n]:
        share = p["ms"] / total
        sev = Severity.HIGH if share >= flag_share else Severity.INFO
        report.add_finding(Finding(
            check=CHECK_NAME,
            severity=sev,
            message=f"{p['name']}: {p['ms']:.3f} ms ({share:.0%} of total)",
            measurement={"ms": round(p["ms"], 3), "share": round(share, 3)},
        ))

    report.set_summary(
        f"{len(passes)} pass(es); top={passes[0]['name'] if passes else 'n/a'} "
        f"@ {passes[0]['ms']:.3f} ms" if passes else "No passes."
    )
    if not passes:
        report.set_summary("No passes in input.")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Rank perfcapture passes by ms.")
    parser.add_argument("--input", required=True, help="Path to perfcapture JSON")
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
