#!/usr/bin/env python3
"""
fe_perf_budget.py — assert a Lighthouse report against a performance budget.

Usage:
    python3 scripts/fe_perf_budget.py --report lhr.json --budget configs/default.budget.json
    python3 scripts/fe_perf_budget.py --report .lighthouseci/ --budget budgets/orders.json --out ./perf-out
    python3 scripts/fe_perf_budget.py --report a.json --report b.json --report c.json --budget b.json --strict

What it does:
    - Reads one or more Lighthouse JSON reports (a file, several files, or a
      directory of `lhr-*.json` as LHCI writes). With more than one report it
      asserts the MEDIAN, because a single lab run is noise.
    - Asserts three budget families: category scores (minimums), timing/metric
      audits (maximums), and transfer sizes per resource type (maximums, KiB).
    - Classifies every assertion pass / warn / fail / inconclusive and prints a
      report in the shared /qa shape (or JSON).

Exit codes:
    0  every assertion passed (warnings allowed unless --strict)
    1  at least one assertion failed (or warned, with --strict)
    2  INCONCLUSIVE — a budgeted metric is absent from the report, or nothing
       was assertable. Never treated as a pass.
    3  usage / input error (missing report, unreadable budget)

Stdlib only: no Lighthouse, Node, or network needed to assert a report that was
produced elsewhere (LHCI in CI, a PageSpeed Insights export, a hosted runner).
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

# Budgeted metrics map to Lighthouse audit ids. `numericValue` units: ms for
# timings, unitless for CLS.
METRIC_AUDITS = {
    "first-contentful-paint": ("First Contentful Paint", "ms"),
    "largest-contentful-paint": ("Largest Contentful Paint", "ms"),
    "speed-index": ("Speed Index", "ms"),
    "total-blocking-time": ("Total Blocking Time", "ms"),
    "cumulative-layout-shift": ("Cumulative Layout Shift", ""),
    "interactive": ("Time to Interactive", "ms"),
    "server-response-time": ("Server Response Time", "ms"),
    "max-potential-fid": ("Max Potential FID", "ms"),
    "interaction-to-next-paint": ("Interaction to Next Paint", "ms"),
}

DEFAULT_WARN_MARGIN_PCT = 10.0


# ─── loading ─────────────────────────────────────────────────────────────────

def collect_report_paths(args_reports: list[str]) -> list[Path]:
    paths: list[Path] = []
    for raw in args_reports:
        p = Path(raw).expanduser()
        if p.is_dir():
            found = sorted(p.glob("lhr-*.json")) or sorted(p.glob("*.json"))
            if not found:
                raise FileNotFoundError(f"no Lighthouse JSON found in {p}")
            paths.extend(found)
        elif p.is_file():
            paths.append(p)
        else:
            raise FileNotFoundError(f"report not found: {p}")
    return paths


def load_report(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    # LHCI `--upload.target=filesystem` and some CI wrappers nest the report.
    if "audits" not in data:
        for key in ("lhr", "report", "lighthouseResult"):
            if isinstance(data.get(key), dict) and "audits" in data[key]:
                return data[key]
        raise ValueError(f"{path.name} is not a Lighthouse report (no `audits`)")
    return data


def category_score(report: dict, cid: str):
    cat = (report.get("categories") or {}).get(cid) or {}
    score = cat.get("score")
    return float(score) if isinstance(score, (int, float)) else None


def metric_value(report: dict, aid: str):
    audit = (report.get("audits") or {}).get(aid) or {}
    val = audit.get("numericValue")
    return float(val) if isinstance(val, (int, float)) else None


def resource_kb(report: dict, resource_type: str):
    """Transfer size in KiB for a resource type from the resource-summary audit."""
    items = (((report.get("audits") or {}).get("resource-summary") or {})
             .get("details") or {}).get("items") or []
    for item in items:
        if str(item.get("resourceType", "")).lower() == resource_type.lower():
            size = item.get("transferSize")
            if isinstance(size, (int, float)):
                return float(size) / 1024.0
    return None


def median_or_none(values: list[float | None]):
    present = [v for v in values if v is not None]
    if not present:
        return None, 0
    return statistics.median(present), len(present)


# ─── assertion model ─────────────────────────────────────────────────────────

def classify_max(value: float, limit: float, margin_pct: float) -> str:
    if value > limit:
        return "fail"
    if value >= limit * (1 - margin_pct / 100.0):
        return "warn"
    return "pass"


def classify_min(value: float, limit: float, margin_pct: float) -> str:
    if value < limit:
        return "fail"
    if value >= 1.0:
        return "pass"          # a perfect score has no headroom left to ask for
    ceiling = min(1.0, limit * (1 + margin_pct / 100.0))
    if value <= ceiling:
        return "warn"
    return "pass"


def fmt(value: float | None, unit: str) -> str:
    if value is None:
        return "n/a"
    if unit == "ms":
        return f"{value:.0f}ms"
    if unit == "KiB":
        return f"{value:.0f}KiB"
    if unit == "score":
        return f"{value:.2f}"
    return f"{value:.3f}".rstrip("0").rstrip(".")


def assess(reports: list[dict], budget: dict) -> tuple[list[dict], dict]:
    margin = float(budget.get("warn_margin_pct", DEFAULT_WARN_MARGIN_PCT))
    results: list[dict] = []

    for cid, limit in (budget.get("categories") or {}).items():
        value, n = median_or_none([category_score(r, cid) for r in reports])
        results.append(_result(f"category:{cid}", "min", float(limit), value, "score",
                               n, len(reports), margin, classify_min))

    for aid, limit in (budget.get("metrics") or {}).items():
        unit = METRIC_AUDITS.get(aid, ("", ""))[1]
        value, n = median_or_none([metric_value(r, aid) for r in reports])
        results.append(_result(f"metric:{aid}", "max", float(limit), value, unit,
                               n, len(reports), margin, classify_max))

    for rtype, limit in (budget.get("resource_sizes_kb") or {}).items():
        value, n = median_or_none([resource_kb(r, rtype) for r in reports])
        results.append(_result(f"resource:{rtype}", "max", float(limit), value, "KiB",
                               n, len(reports), margin, classify_max))

    counts = {k: 0 for k in ("pass", "warn", "fail", "inconclusive")}
    for r in results:
        counts[r["status"]] += 1
    return results, counts


def _result(name, direction, limit, value, unit, n_present, n_reports, margin, classifier) -> dict:
    if value is None:
        status, note = "inconclusive", "not present in the report(s)"
    else:
        status = classifier(value, limit, margin)
        note = (f"median of {n_present}/{n_reports} runs" if n_reports > 1
                else "single run")
    return {
        "assertion": name,
        "direction": direction,          # min | max
        "limit": limit,
        "value": value,
        "unit": unit,
        "status": status,                # pass | warn | fail | inconclusive
        "note": note,
    }


# ─── reporting ───────────────────────────────────────────────────────────────

STATUS_LABEL = {"pass": "pass", "warn": "warn", "fail": "FAIL", "inconclusive": "INCONCLUSIVE"}


def render_markdown(payload: dict) -> str:
    b = payload["budget_name"]
    lines = [
        f"## QA Report — {payload['target']} · audit · lens:performance · budget:{b}",
        f"Standard: {payload['assertion_count']} budget assertion(s), "
        f"warn margin {payload['warn_margin_pct']:.0f}%",
        f"Method:   Lighthouse JSON × {payload['report_count']} "
        f"({'median' if payload['report_count'] > 1 else 'single run'})",
        "",
        "### Findings  (status: FAIL | warn | INCONCLUSIVE | pass)",
    ]
    order = {"fail": 0, "inconclusive": 1, "warn": 2, "pass": 3}
    for r in sorted(payload["results"], key=lambda x: (order[x["status"]], x["assertion"])):
        comparator = "≥" if r["direction"] == "min" else "≤"
        lines.append(
            f"- [{STATUS_LABEL[r['status']]}] {r['assertion']} — "
            f"{fmt(r['value'], r['unit'])} vs budget {comparator} {fmt(r['limit'], r['unit'])}"
            f"  ({r['note']})")
    c = payload["counts"]
    lines += [
        "",
        "### Summary",
        f"fail {c['fail']} · warn {c['warn']} · inconclusive {c['inconclusive']} · pass {c['pass']}"
        f"  ·  verdict: {payload['verdict']}",
        "",
        "### Next",
        payload["next"],
    ]
    return "\n".join(lines) + "\n"


def next_line(counts: dict, strict: bool) -> str:
    if counts["fail"]:
        return ("Regression: profile the failing metric before optimizing — `fe-performance` "
                "owns the diagnosis (bundle, render path, image/font strategy). Do not raise "
                "the budget to make the build green.")
    if counts["inconclusive"]:
        return ("A budgeted metric is missing from the report: confirm the run used the right "
                "Lighthouse version/preset and that the audit actually executed. An absent "
                "metric is not a pass.")
    if counts["warn"]:
        return ("Within budget but inside the warn margin — the next change is likely to break "
                "it. Ratchet the budget down only when a run is comfortably under it."
                + (" --strict is on, so warnings fail the build." if strict else ""))
    return ("Comfortably inside budget. Consider ratcheting the budget to the current value so "
            "the gain is locked in.")


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Assert Lighthouse report(s) against a performance budget. Stdlib only.")
    ap.add_argument("--report", action="append", required=True,
                    help="Lighthouse JSON file, or a directory of lhr-*.json (repeatable)")
    ap.add_argument("--budget", required=True, help="budget JSON (see configs/default.budget.json)")
    ap.add_argument("--format", choices=["markdown", "json"], default="markdown")
    ap.add_argument("--out", help="directory for perf_budget.md + perf_budget.json")
    ap.add_argument("--strict", action="store_true", help="treat warn as fail")
    args = ap.parse_args()

    try:
        paths = collect_report_paths(args.report)
        reports = [load_report(p) for p in paths]
        budget = json.loads(Path(args.budget).expanduser().read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 3

    results, counts = assess(reports, budget)
    if not results:
        print("error: budget declares no assertions (categories / metrics / resource_sizes_kb)",
              file=sys.stderr)
        return 3

    failed = counts["fail"] > 0 or (args.strict and counts["warn"] > 0)
    if failed:
        verdict, code = "fail", 1
    elif counts["inconclusive"]:
        verdict, code = "inconclusive", 2
    else:
        verdict, code = "pass", 0

    target = (budget.get("target")
              or (reports[0].get("finalDisplayedUrl") or reports[0].get("finalUrl")
                  or reports[0].get("requestedUrl") or paths[0].name))
    payload = {
        "schema": "fe-perf-harness/1.0",
        "target": target,
        "budget_name": budget.get("name", Path(args.budget).stem),
        "warn_margin_pct": float(budget.get("warn_margin_pct", DEFAULT_WARN_MARGIN_PCT)),
        "strict": bool(args.strict),
        "report_count": len(reports),
        "reports": [str(p) for p in paths],
        "assertion_count": len(results),
        "counts": counts,
        "verdict": verdict,
        "results": results,
        "next": next_line(counts, args.strict),
    }

    if args.out:
        out_dir = Path(args.out).expanduser()
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "perf_budget.json").write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        (out_dir / "perf_budget.md").write_text(render_markdown(payload), encoding="utf-8")

    if args.format == "json":
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(render_markdown(payload), end="")
    return code


if __name__ == "__main__":
    sys.exit(main())
