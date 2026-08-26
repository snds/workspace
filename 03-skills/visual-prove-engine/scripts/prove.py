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

    results: list[CueResult] = [run_cue(cue, ctx) for cue in spec["cues"]]
    summary = summarize_cues(
        results, capture["status"], min_coverage=float(spec.get("min_coverage", 0.8))
    )

    payload = {
        "engine": _core.ENGINE_VERSION,
        "cuespec": spec["_path"],
        "northstar": spec.get("northstar"),
        "build": str(Path(build_path).resolve()),
        "capture": capture,
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
        "",
        f"## Verdict: **{s['verdict'].upper()}**",
        "",
        f"- Measured: **{s['measured_pass']}/{s['measured_total']} pass**"
        f" · attested (not proof): {s['attested']} · errors: {s['errors']}",
        f"- Measured coverage: {s['coverage']:.0%} · score: {s['score']:.2f}"
        + (f" · mean margin: {s['mean_margin']}" if s.get("mean_margin") is not None else ""),
    ]
    for r in payload.get("summary", {}).get("verdict_reasons", []):
        lines.append(f"- {r}")
    lines += ["", "| # | Cue | Probe | Status | Value | Target | Margin |", "|---|---|---|---|---|---|---|"]
    for c in payload["cues"]:
        val = c["value"]
        if isinstance(val, dict):
            val = ", ".join(f"{k}={v}" for k, v in val.items())
        lines.append(
            f"| {c['id']} | {c['name']} | `{c['probe']}` | {_STATUS_ICON.get(c['status'], c['status'])} "
            f"| {val if val is not None else ''} | {c['target'] if c['target'] is not None else ''} "
            f"| {c['margin'] if c['margin'] is not None else ''} |"
        )
    notes = [c for c in payload["cues"] if c.get("note")]
    if notes:
        lines += ["", "## Notes", ""]
        for c in notes:
            lines.append(f"- **{c['id']} {c['name']}**: {c['note']}")
    lines += [
        "",
        "---",
        "",
        "_A cue passes only if an instrumented probe measured it. Attested cues are",
        "declarations, not proof, and never count toward a Matches verdict._",
        "",
    ]
    return "\n".join(lines)
