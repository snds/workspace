#!/usr/bin/env python3
"""
playprove.py — headless simulation / balance prove. Altitude G.

Sibling of visual-prove-engine, not a `vqa.py` subcommand. Pixel cameras
pollute feel/balance measurements; this CLI consumes metrics a user-supplied
adapter already computed (win-rate, strategy shares, score moments).

Spec (JSON):
{
  "spec": "play-prove/1",
  "adapter": {"command": ["python3", "sim.py", "--json"]},
  "assert": {
    "win_rate": {"min": 0.40, "max": 0.60},
    "avg": {"min": 0},
    "stddev": {"max": 50},
    "no_dominant_strategy": {"max_share": 0.45, "key": "strategy_shares"}
  }
}

Adapter stdout (last JSON line):
{"win_rate": 0.52, "avg": 12.1, "stddev": 2.0, "n": 200,
 "strategy_shares": {"rush": 0.3, "boom": 0.35, "turtle": 0.35}}

Exit: 0 pass · 1 fail · 2 usage/adapter error.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


SPEC_VERSION = "play-prove/1"


def load_spec(path: str | Path) -> dict:
    p = Path(path)
    spec = json.loads(p.read_text(encoding="utf-8"))
    if spec.get("spec") != SPEC_VERSION:
        raise ValueError(f"unsupported play-prove spec: {spec.get('spec')!r}")
    if not spec.get("adapter", {}).get("command"):
        raise ValueError("adapter.command required")
    spec["_dir"] = str(p.parent.resolve())
    spec["_path"] = str(p.resolve())
    return spec


def run_adapter(spec: dict) -> dict:
    cmd = list(spec["adapter"]["command"])
    proc = subprocess.run(
        cmd, capture_output=True, text=True, check=False, cwd=spec["_dir"],
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"adapter exit {proc.returncode}: {(proc.stderr or proc.stdout)[-500:]}"
        )
    lines = [ln for ln in (proc.stdout or "").splitlines() if ln.strip()]
    if not lines:
        raise RuntimeError("adapter produced no stdout")
    return json.loads(lines[-1])


def check_asserts(metrics: dict, asserts: dict) -> list:
    verdicts = []
    for name, rule in (asserts or {}).items():
        if name == "no_dominant_strategy":
            key = rule.get("key", "strategy_shares")
            shares = metrics.get(key) or {}
            max_share = max(shares.values()) if shares else None
            limit = float(rule.get("max_share", 0.5))
            ok = max_share is not None and max_share <= limit
            verdicts.append({
                "check": name, "value": max_share, "limit": limit,
                "status": "pass" if ok else "fail",
                "note": None if shares else f"metrics missing '{key}'",
            })
            continue
        value = metrics.get(name)
        if value is None:
            verdicts.append({
                "check": name, "value": None, "status": "fail",
                "note": f"adapter did not emit '{name}'",
            })
            continue
        lo = rule.get("min")
        hi = rule.get("max")
        ok = True
        if lo is not None:
            ok = ok and float(value) >= float(lo)
        if hi is not None:
            ok = ok and float(value) <= float(hi)
        verdicts.append({
            "check": name, "value": value,
            "min": lo, "max": hi,
            "status": "pass" if ok else "fail",
        })
    return verdicts


def run_prove(spec_path: str | Path, out_dir: str | Path | None = None) -> dict:
    spec = load_spec(spec_path)
    metrics = run_adapter(spec)
    verdicts = check_asserts(metrics, spec.get("assert") or {})
    failing = [v for v in verdicts if v["status"] != "pass"]
    payload = {
        "engine": "play-prove/1",
        "spec": spec["_path"],
        "altitude": "G",
        "metrics": metrics,
        "verdicts": verdicts,
        "verdict": "pass" if not failing else "fail",
        "note": (
            "Headless simulation metrics. Do not substitute a screenshot prove "
            "or a VLM playtest for this contract."
        ),
    }
    if out_dir:
        out = Path(out_dir)
        out.mkdir(parents=True, exist_ok=True)
        (out / "play-prove.json").write_text(
            json.dumps(payload, indent=2) + "\n", encoding="utf-8"
        )
        payload["artifacts"] = [str(out / "play-prove.json")]
    return payload


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="playprove", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    pr = sub.add_parser("prove", help="run a play-prove spec")
    pr.add_argument("spec")
    pr.add_argument("--output")
    args = p.parse_args(argv)
    try:
        payload = run_prove(args.spec, out_dir=args.output)
    except Exception as exc:
        print(json.dumps({"verdict": "error", "note": str(exc)}, indent=2))
        return 2
    print(json.dumps(payload, indent=2))
    return 0 if payload["verdict"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
