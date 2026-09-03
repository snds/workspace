"""
prove.py — run a declarative cuespec against a build capture.

The cuespec is data; this runner is tested code. That split is the point:
per-project prove scripts with hand-coded `pass: True` cues are the failure
mode this engine replaces. Here a cue can only pass if a registered probe
measured it; anything else is attested / errored and is reported as such.

Cuespec schema (JSON):
{
  "spec": "vqa-cuespec/1",
  "northstar": "S-XXX-NN",
  "reference": {"path": "...", "width": 3840, "height": 2160},   # optional
  "min_coverage": 0.8,                                            # optional
  "background": "#000000",                                        # optional
  "cues": [ {"id": 1, "name": "...", "probe": "...", ...}, ... ]
}
"""
from __future__ import annotations

import datetime
from pathlib import Path
from typing import Optional

from . import _core
from ._core import CueResult, hex_to_rgb, load_image, summarize_cues, verify_capture, write_json
from .probes import ProbeContext, run_cue

import json


def load_cuespec(path: str | Path) -> dict:
    p = Path(path)
    spec = json.loads(p.read_text(encoding="utf-8"))
    if spec.get("spec") != "vqa-cuespec/1":
        raise ValueError(f"unsupported cuespec version: {spec.get('spec')!r}")
    if not isinstance(spec.get("cues"), list) or not spec["cues"]:
        raise ValueError("cuespec has no cues")
    spec["_dir"] = str(p.parent.resolve())
    spec["_path"] = str(p.resolve())
    return spec


def run_prove(
    build_path: str | Path,
    cuespec_path: str | Path,
    out_dir: Optional[str | Path] = None,
    manifest_path: Optional[str | Path] = None,
) -> dict:
    spec = load_cuespec(cuespec_path)
    img = load_image(build_path)
    capture = verify_capture(build_path, manifest_path)

    background = hex_to_rgb(spec["background"]) if spec.get("background") else None
    ctx = ProbeContext(img, Path(spec["_dir"]), background=background)

    default_alt = spec.get("default_altitude", "A")
    results: list[CueResult] = []
    for cue in spec["cues"]:
        c = dict(cue)
        c.setdefault("altitude", default_alt)
        results.append(run_cue(c, ctx))
    summary = summarize_cues(
        results,
        capture["status"],
        min_coverage=float(spec.get("min_coverage", 0.8)),
        uncued_residuals=spec.get("uncued_residuals") or [],
        required_altitudes=spec.get("required_altitudes"),
    )

    provenance = spec.get("_provenance") or {}
    required_assistance = provenance.get("assistance")
    observed_assistance = capture.get("assistance") or (capture.get("meta") or {}).get("assistance")
    isolation_notes: list[str] = []
    if required_assistance == "off" and observed_assistance in (None, "unknown", "on"):
        isolation_notes.append(
            "cuespec _provenance.assistance is off but capture assistance is "
            f"{observed_assistance!r} — extra rails (chunks/lint/MCP) can hide doc/catalog failure"
        )

    payload = {
        "engine": _core.ENGINE_VERSION,
        "cuespec": spec["_path"],
        "northstar": spec.get("northstar"),
        "build": str(Path(build_path).resolve()),
        "capture": capture,
        "assistance": {
            "required": required_assistance,
            "observed": observed_assistance,
            "notes": isolation_notes,
        },
        "generated": datetime.datetime.now().isoformat(timespec="seconds"),
        "summary": summary,
        "cues": [r.to_dict() for r in results],
        "deps": _core.deps_report(),
    }

    if out_dir:
        out = Path(out_dir)
        stem = Path(build_path).stem
        write_json(payload, out / f"{stem}.prove.json")
        (out / f"{stem}.prove.md").parent.mkdir(parents=True, exist_ok=True)
        (out / f"{stem}.prove.md").write_text(to_markdown(payload), encoding="utf-8")
        payload["artifacts"] = [str(out / f"{stem}.prove.json"), str(out / f"{stem}.prove.md")]
    return payload


_STATUS_ICON = {"pass": "PASS", "fail": "FAIL", "attested": "ATTESTED", "error": "ERROR", "skipped": "SKIP"}


def to_markdown(payload: dict) -> str:
    s = payload["summary"]
    lines = [
        f"# Prove report — {payload.get('northstar') or Path(payload['build']).name}",
        "",
        f"- Build: `{payload['build']}`",
        f"- Cuespec: `{payload['cuespec']}`",
        f"- Capture: **{payload['capture']['status']}**"
        + (f" ({'; '.join(payload['capture']['reasons'])})" if payload["capture"]["reasons"] else ""),
        f"- Generated: {payload['generated']} by {payload['engine']}",
        f"- Altitudes in contract: {', '.join(s.get('altitudes_in_contract') or ['A'])}",
        "",
        f"## Verdict: **{s['verdict'].upper()}**",
        "",
        f"- Measured: **{s['measured_pass']}/{s['measured_total']} pass**"
        f" · attested (not proof): {s['attested']} · errors: {s['errors']}",
        f"- Measured coverage: {s['coverage']:.0%} · score: {s['score']:.2f}"
        + (f" · mean margin: {s['mean_margin']}" if s.get("mean_margin") is not None else ""),
    ]
    warns = payload.get("capture", {}).get("warnings") or []
    for w in warns:
        lines.append(f"- Capture warning: {w}")
    assist = payload.get("assistance") or {}
    if assist.get("required") or assist.get("observed"):
        lines.append(
            f"- Assistance: required={assist.get('required')} observed={assist.get('observed')}"
        )
    for note in assist.get("notes") or []:
        lines.append(f"- Isolation: {note}")
    for r in payload.get("summary", {}).get("verdict_reasons", []):
        lines.append(f"- {r}")
    lines += ["", "| # | Cue | Probe | Alt | Status | Value | Target | Margin |",
              "|---|---|---|---|---|---|---|---|"]
    for c in payload["cues"]:
        val = c["value"]
        if isinstance(val, dict):
            val = ", ".join(f"{k}={v}" for k, v in list(val.items())[:6])
        lines.append(
            f"| {c['id']} | {c['name']} | `{c['probe']}` | {c.get('altitude', 'A')} "
            f"| {_STATUS_ICON.get(c['status'], c['status'])} "
            f"| {val if val is not None else ''} | {c['target'] if c['target'] is not None else ''} "
            f"| {c['margin'] if c['margin'] is not None else ''} |"
        )
    notes = [c for c in payload["cues"] if c.get("note")]
    if notes:
        lines += ["", "## Notes", ""]
        for c in notes:
            lines.append(f"- **{c['id']} {c['name']}**: {c['note']}")
    residuals = s.get("uncued_residuals") or []
    if residuals:
        lines += ["", "## Uncued residuals", ""]
        lines.append("Named holes in the cue net. A matches verdict does not cover these.")
        lines.append("")
        for r in residuals:
            if isinstance(r, dict):
                lines.append(f"- **{r.get('id', '?')}** ({r.get('zone', '')}): {r.get('note', '')}")
            else:
                lines.append(f"- {r}")
    lines += [
        "",
        "---",
        "",
        "_A cue passes only if an instrumented probe measured it. Attested cues are",
        "declarations, not proof, and never count toward a Matches verdict._",
        "",
    ]
    return "\n".join(lines)
