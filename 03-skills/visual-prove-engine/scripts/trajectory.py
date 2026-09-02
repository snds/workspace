"""
trajectory.py — the improvement-loop ledger.

Turns individual prove runs into a scored trajectory so an iteration loop has
a machine verdict for "did this edit make the build closer to the reference":

  vqa score --ledger <ledger.json> --from <prove.json> [--enforce]

Contract for the loop (documented in SKILL.md, enforced here):
  1. Baseline: run prove, record the score with `vqa score`.
  2. Edit, re-capture (same capture contract), re-prove, re-score.
  3. `improved` — keep the edit. `regressed` — REVERT the edit before trying
     anything else (--enforce exits 1 so a harness can gate on it).
  4. Stop when the score plateaus for `stall_limit` consecutive accepted runs
     or every measured cue passes; report honestly either way.

Ranking uses (score, measured_pass, mean_margin) lexicographically so a run
cannot "improve" by dropping cues from measurement: a coverage drop is
reported as its own flag and blocks an `improved` verdict under --enforce.
"""
from __future__ import annotations

import datetime
import json
from pathlib import Path
from typing import Optional

from . import _core
from ._core import write_json


def _entry_from_prove(prove_payload: dict, note: str = "") -> dict:
    s = prove_payload["summary"]
    return {
        "time": datetime.datetime.now().isoformat(timespec="seconds"),
        "build": prove_payload.get("build"),
        "verdict": s["verdict"],
        "score": s["score"],
        "measured_pass": s["measured_pass"],
        "measured_total": s["measured_total"],
        "coverage": s["coverage"],
        "mean_margin": s.get("mean_margin"),
        "capture": s.get("capture"),
        "failing_cues": [
            {"id": c["id"], "name": c["name"], "margin": c.get("margin")}
            for c in prove_payload.get("cues", [])
            if c["status"] == "fail"
        ],
        "note": note,
    }


def _key(entry: dict) -> tuple:
    return (
        entry.get("score", 0.0),
        entry.get("measured_pass", 0),
        entry.get("mean_margin") if entry.get("mean_margin") is not None else -1.0,
    )


def record_score(
    ledger_path: str | Path,
    prove_json_path: str | Path,
    note: str = "",
    enforce: bool = False,
    stall_limit: int = 3,
) -> dict:
    ledger_path = Path(ledger_path)
    prove_payload = json.loads(Path(prove_json_path).read_text(encoding="utf-8"))
    entry = _entry_from_prove(prove_payload, note=note)

    if ledger_path.exists():
        ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    else:
        ledger = {"engine": _core.ENGINE_VERSION, "cuespec": prove_payload.get("cuespec"),
                  "runs": []}

    prev = ledger["runs"][-1] if ledger["runs"] else None
    flags = []
    if prev is None:
        movement = "baseline"
    else:
        k_new, k_prev = _key(entry), _key(prev)
        if k_new > k_prev:
            movement = "improved"
        elif k_new < k_prev:
            movement = "regressed"
        else:
            movement = "flat"
        if entry["coverage"] < prev["coverage"] - 1e-9:
            flags.append(
                f"measured coverage dropped {prev['coverage']:.0%} -> {entry['coverage']:.0%}"
                " — a run must not improve by measuring less"
            )
        prev_fail = {c["id"] for c in prev.get("failing_cues", [])}
        now_fail = {c["id"] for c in entry.get("failing_cues", [])}
        entry["newly_passing"] = sorted(prev_fail - now_fail, key=str)
        entry["newly_failing"] = sorted(now_fail - prev_fail, key=str)
        if entry["newly_failing"]:
            flags.append(f"cues newly failing: {entry['newly_failing']}")

    entry["movement"] = movement
    entry["flags"] = flags
    ledger["runs"].append(entry)

    # Stall detection over accepted (non-regressed) tail
    tail = [r for r in ledger["runs"][-(stall_limit + 1):]]
    stalled = (
        len(tail) >= stall_limit + 1
        and all(r.get("movement") in ("flat", "baseline") for r in tail[1:])
    )
    ledger["status"] = {
        "runs": len(ledger["runs"]),
        "best_score": max(r["score"] for r in ledger["runs"]),
        "last_movement": movement,
        "stalled": stalled,
        "done": entry["measured_total"] > 0 and entry["measured_pass"] == entry["measured_total"],
    }

    write_json(ledger, ledger_path)
    md_path = ledger_path.with_suffix(".md")
    md_path.write_text(_to_markdown(ledger), encoding="utf-8")

    result = {
        "movement": movement,
        "flags": flags,
        "entry": entry,
        "status": ledger["status"],
        "ledger": str(ledger_path),
        "trajectory_md": str(md_path),
        "enforce_fail": bool(enforce and (movement == "regressed" or flags)),
    }
    return result


def _to_markdown(ledger: dict) -> str:
    lines = [
        "# Score trajectory",
        "",
        f"- Cuespec: `{ledger.get('cuespec')}`",
        f"- Runs: {ledger['status']['runs']} · best score: {ledger['status']['best_score']:.2f}"
        f" · done: {ledger['status']['done']} · stalled: {ledger['status']['stalled']}",
        "",
        "| # | Time | Score | Pass | Coverage | Margin | Movement | Flags |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for i, r in enumerate(ledger["runs"], 1):
        lines.append(
            f"| {i} | {r['time']} | {r['score']:.2f} | {r['measured_pass']}/{r['measured_total']} "
            f"| {r['coverage']:.0%} | {r.get('mean_margin')} | {r.get('movement', '')} "
            f"| {'; '.join(r.get('flags', [])) or ''} |"
        )
    lines += [
        "",
        "_Movement compares (score, measured passes, mean margin) with the previous run._",
        "_A regressed run means: revert the edit before trying anything else._",
        "",
    ]
    return "\n".join(lines)
