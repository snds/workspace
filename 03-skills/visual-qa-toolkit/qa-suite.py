"""
qa-suite.py — Orchestrator for the visual-qa-toolkit.

Usage:
    python qa-suite.py --input screenshot.png --config default.yaml --output ./qa-out
    python qa-suite.py --context ~/projects/myproj/.visual-qa-context.yaml
    python qa-suite.py --context ~/proj/.ctx.yaml --input today-screen.png
    python qa-suite.py --input ./states_dir --config default.yaml --output ./qa-out --only state_comparison

What it does:
    - Loads the config and dispatches to each enabled QA script in-process.
    - Optionally loads a --context file that supplies CLI defaults and
      per-check config overrides. CLI args win; context fills the rest.
    - Captures each script's ReportWriter, writes individual reports per
      check AND a consolidated markdown report that summarizes every check.
    - Writes a machine-readable JSON summary alongside the markdown for
      downstream consumption.

Precedence (highest wins):
    CLI args  >  context.defaults  >  config file  >  script defaults
    context.check_overrides is deep-merged INTO the loaded config.

Dispatch logic:
    - Image-input checks (most of them) receive a single image path.
    - Folder-input checks (icon_consistency, state_comparison) need a directory.
    - visual_diff needs both an input AND a reference path (from config or CLI).
    - The suite tries to be forgiving: if a check is skipped due to missing
      inputs, it's noted in the consolidated report but does not stop the suite.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Callable

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
from scripts._context import (
    load_context,
    apply_default,
    deep_merge,
)
from scripts import (
    qa_alignment,
    qa_spacing,
    qa_contrast,
    qa_color_extraction,
    qa_visual_diff,
    qa_color_vision,
    qa_icon_consistency,
    qa_typography,
    qa_grid_overlay,
    qa_state_comparison,
)


# Registry — (check_name, module, input_mode) where input_mode drives dispatch
IMAGE_INPUT = "image"   # expects a single image file
FOLDER_INPUT = "folder" # expects a directory

CHECKS: list[tuple[str, object, str]] = [
    ("alignment",        qa_alignment,        IMAGE_INPUT),
    ("spacing",          qa_spacing,          IMAGE_INPUT),
    ("contrast",         qa_contrast,         IMAGE_INPUT),
    ("color_extraction", qa_color_extraction, IMAGE_INPUT),
    ("visual_diff",      qa_visual_diff,      IMAGE_INPUT),
    ("color_vision",     qa_color_vision,     IMAGE_INPUT),
    ("typography",       qa_typography,       IMAGE_INPUT),
    ("grid_overlay",     qa_grid_overlay,     IMAGE_INPUT),
    ("icon_consistency", qa_icon_consistency, FOLDER_INPUT),
    ("state_comparison", qa_state_comparison, FOLDER_INPUT),
]


def _consolidated_report(
    reports: list[tuple[str, ReportWriter]],
    skipped: list[tuple[str, str]],
    config_path: Path,
    input_path: Path,
    project_label: str = "",
    context_path: str = "",
) -> str:
    """Build the consolidated markdown report from individual reports."""
    lines: list[str] = []
    lines.append("# Visual QA — Consolidated Report")
    lines.append("")
    if project_label:
        lines.append(f"- **Project**: {project_label}")
    lines.append(f"- **Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"- **Input**: `{input_path}`")
    lines.append(f"- **Config**: `{config_path}`")
    if context_path:
        lines.append(f"- **Context**: `{context_path}`")
    lines.append("")

    # Aggregate counts
    total_counts = {s: 0 for s in Severity}
    for _check, r in reports:
        for sev, n in r.counts.items():
            total_counts[sev] += n

    lines.append("## Overall")
    lines.append("")
    lines.append(f"**Checks run:** {len(reports)} · **Skipped:** {len(skipped)}")
    lines.append("")
    any_findings = any(total_counts.values())
    if any_findings:
        lines.append("**Findings across all checks:**")
        lines.append("")
        for sev in Severity:
            if total_counts[sev] > 0:
                lines.append(f"- {SEVERITY_ICON[sev]} {sev.value.capitalize()}: {total_counts[sev]}")
        lines.append("")
    else:
        lines.append("No findings.")
        lines.append("")

    # Per-check summary table
    lines.append("## Per-check summary")
    lines.append("")
    lines.append("| Check | Critical | High | Medium | Low | Info | Report |")
    lines.append("|---|---:|---:|---:|---:|---:|---|")
    for check, r in reports:
        c = r.counts
        lines.append(
            f"| **{check}** | "
            f"{c[Severity.CRITICAL]} | "
            f"{c[Severity.HIGH]} | "
            f"{c[Severity.MEDIUM]} | "
            f"{c[Severity.LOW]} | "
            f"{c[Severity.INFO]} | "
            f"[`{check}_report.md`]({check}_report.md) |"
        )
    lines.append("")

    if skipped:
        lines.append("## Skipped checks")
        lines.append("")
        for check, reason in skipped:
            lines.append(f"- **{check}**: {reason}")
        lines.append("")

    # Top findings across all checks — highest severity first, capped
    lines.append("## Top findings")
    lines.append("")
    all_findings: list[tuple[str, Finding]] = []
    for check, r in reports:
        for f in r.findings:
            all_findings.append((check, f))

    # Order: severity first, then preserve insertion order within severity
    sev_order = {s: i for i, s in enumerate(Severity)}
    all_findings.sort(key=lambda t: sev_order[t[1].severity])

    top_n = 20
    for check, f in all_findings[:top_n]:
        lines.append(f"- {SEVERITY_ICON[f.severity]} **[{check}]** {f.message}")
    if len(all_findings) > top_n:
        lines.append(f"- _…and {len(all_findings) - top_n} more. See individual reports._")
    if not all_findings:
        lines.append("_No findings._")
    lines.append("")

    # Summaries from each individual report
    lines.append("## Check summaries")
    lines.append("")
    for check, r in reports:
        lines.append(f"### {check}")
        lines.append("")
        if r.summary_text:
            lines.append(r.summary_text)
        else:
            lines.append("_No summary._")
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("_Consolidated by `qa-suite.py` from the `visual-qa-toolkit`._")
    return "\n".join(lines)


def _json_summary(reports: list[tuple[str, ReportWriter]], skipped: list[tuple[str, str]]) -> dict:
    """Machine-readable summary for downstream consumption."""
    return {
        "generated_at": datetime.now().isoformat(),
        "checks_run": [check for check, _ in reports],
        "skipped": [{"check": c, "reason": r} for c, r in skipped],
        "reports": {check: r.to_json_summary() for check, r in reports},
    }


def main():
    parser = argparse.ArgumentParser(
        description="Orchestrator for the visual-qa-toolkit."
    )
    parser.add_argument(
        "--context", default=None,
        help="Project context file (YAML). Supplies defaults for other args "
             "and merges check_overrides into the config."
    )
    parser.add_argument("--input", default=None, help="Image file, or a folder for folder-input checks")
    parser.add_argument("--config", default=None, help="YAML config file")
    parser.add_argument("--output", default=None, help="Output directory")
    parser.add_argument(
        "--only", default=None,
        help="Comma-separated list of checks to run (overrides config)"
    )
    parser.add_argument(
        "--folder-for", default=None,
        help="Folder path for folder-input checks when --input is an image "
             "(allows running image + folder checks in one suite invocation)"
    )
    parser.add_argument(
        "--reference", default=None,
        help="Reference image path for visual_diff (overrides config)"
    )
    args = parser.parse_args()

    # Load --context if provided
    context: dict = {}
    project_label = ""
    context_path = ""
    if args.context:
        context = load_context(args.context)
        project_label = context.get("project", "")
        context_path = context.get("_context_path", "")
        log.info(f"▶ Loaded context: {project_label or '(unnamed)'} from {context_path}")

    ctx_defaults = context.get("defaults", {})

    # Precedence: CLI wins, then context defaults. Validate required after merge.
    eff_input   = apply_default(args.input,      ctx_defaults, "input")
    eff_config  = apply_default(args.config,     ctx_defaults, "config")
    eff_output  = apply_default(args.output,     ctx_defaults, "output")
    eff_only    = apply_default(args.only,       ctx_defaults, "only")
    eff_folder  = apply_default(args.folder_for, ctx_defaults, "folder_for")
    eff_ref     = apply_default(args.reference,  ctx_defaults, "reference")

    missing = []
    if not eff_input:  missing.append("--input")
    if not eff_config: missing.append("--config")
    if not eff_output: missing.append("--output")
    if missing:
        parser.error(
            f"missing required arg(s) (neither CLI nor --context supplied): "
            f"{', '.join(missing)}"
        )

    # Load config and deep-merge any check_overrides from context
    config = load_config(eff_config)
    overrides = context.get("check_overrides", {})
    if overrides:
        config = deep_merge(config, overrides)
        log.info(
            f"▶ Applied context check_overrides for: "
            f"{', '.join(sorted(overrides.keys()))}"
        )

    input_path = Path(eff_input)
    output_dir = ensure_output_dir(eff_output)
    folder_path = Path(eff_folder) if eff_folder else None

    # Determine which checks to run
    only = None
    if eff_only:
        only = set(c.strip() for c in eff_only.split(","))

    reports: list[tuple[str, ReportWriter]] = []
    skipped: list[tuple[str, str]] = []

    for check_name, module, input_mode in CHECKS:
        if only is not None:
            if check_name not in only:
                skipped.append((check_name, "not in --only list"))
                continue
        elif not is_check_enabled(config, check_name):
            skipped.append((check_name, "disabled in config"))
            continue

        # Choose the right input path for this check
        check_input: Path
        if input_mode == FOLDER_INPUT:
            if folder_path is not None:
                check_input = folder_path
            elif input_path.is_dir():
                check_input = input_path
            else:
                skipped.append((check_name, "requires a folder input (pass --folder-for or use a directory as --input)"))
                continue
        else:
            if input_path.is_file():
                check_input = input_path
            else:
                skipped.append((check_name, "requires an image file as --input"))
                continue

        log.info(f"▶ Running {check_name}...")
        try:
            if check_name == "visual_diff":
                # Special: accepts an optional reference override
                report = module.run(
                    check_input, config, output_dir,
                    reference_override=eff_ref,
                )
            else:
                report = module.run(check_input, config, output_dir)

            report_path = output_dir / f"{check_name}_report.md"
            report.write(report_path)
            log.info(f"  ✓ {check_name} → {report_path} ({sum(report.counts.values())} finding(s))")
            reports.append((check_name, report))
        except Exception as e:
            log.error(f"  ✗ {check_name} failed: {e}")
            # Build a minimal report noting the failure so it appears in the consolidated output
            err_report = ReportWriter(check_name)
            err_report.set_summary(f"Check failed with error: {e}")
            err_report.add_finding(Finding(
                check=check_name,
                severity=Severity.CRITICAL,
                message=f"Check execution failed: {type(e).__name__}: {e}",
                details="Review script logs for details.",
            ))
            reports.append((check_name, err_report))

    # Consolidated markdown
    consolidated_md = _consolidated_report(
        reports, skipped, Path(eff_config), input_path,
        project_label=project_label, context_path=context_path,
    )
    consolidated_path = output_dir / "qa_report.md"
    consolidated_path.write_text(consolidated_md, encoding="utf-8")
    log.info(f"▶ Consolidated report → {consolidated_path}")

    # Machine-readable JSON
    json_path = output_dir / "qa_report.json"
    json_path.write_text(json.dumps(_json_summary(reports, skipped), indent=2), encoding="utf-8")
    log.info(f"▶ JSON summary → {json_path}")

    # Print a terse terminal summary
    print()
    print(f"✓ Suite complete — {len(reports)} check(s) run, {len(skipped)} skipped")
    print(f"  Consolidated: {consolidated_path}")
    print(f"  JSON:         {json_path}")
    print(f"  Individual reports and annotated images in: {output_dir}")

    # Exit code reflects severity — useful for CI
    any_critical = any(
        r.counts[Severity.CRITICAL] > 0 for _, r in reports
    )
    any_high = any(
        r.counts[Severity.HIGH] > 0 for _, r in reports
    )
    if any_critical:
        sys.exit(2)
    elif any_high:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
