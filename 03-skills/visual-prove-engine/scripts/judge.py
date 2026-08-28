"""
Cross-model VLM-judge protocol. Spirit / Intent only.

Never a Literal spec. Two model families, A/B order swap, discard inconsistent
pairs. A leftover singleton after discard is not a vote.

Judge spec (JSON):
{
  "spec": "vqa-judge/1",
  "altitude": "D",
  "prompt": "Does the screenshot match the LCARS Spirit of the reference? yes|no",
  "reference": "ref.png",
  "candidate": "build.png",
  "judges": [
    {"family": "claude", "command": ["python3", "judge_a.py"]},
    {"family": "gpt", "command": ["python3", "judge_b.py"]}
  ]
}

Each command is invoked twice (candidate-first and reference-first) with env:
  VQA_JUDGE_A, VQA_JUDGE_B, VQA_JUDGE_PROMPT, VQA_JUDGE_ORDER=ab|ba
Stdout must be JSON: {"verdict": "yes"|"no", "note": "..."}.
"""
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Optional

from . import _core
from ._core import write_json


def load_spec(path: str | Path) -> dict:
    p = Path(path)
    spec = json.loads(p.read_text(encoding="utf-8"))
    if spec.get("spec") != "vqa-judge/1":
        raise ValueError(f"unsupported judge spec: {spec.get('spec')!r}")
    if spec.get("altitude", "D") in ("A", "B"):
        raise ValueError(
            "vqa-judge is Spirit/Intent only (altitude C/D/F). "
            "Do not use it as a Literal (A/B) spec."
        )
    judges = spec.get("judges") or []
    families = {j.get("family") for j in judges}
    if len(families) < 2:
        raise ValueError("need two model families; a single VLM is not a protocol")
    spec["_dir"] = str(p.parent.resolve())
    spec["_path"] = str(p.resolve())
    return spec


def _run_judge(cmd: list, env: dict, cwd: Path) -> dict:
    proc = subprocess.run(
        cmd, capture_output=True, text=True, check=False,
        env={**os.environ, **env}, cwd=str(cwd),
    )
    if proc.returncode != 0:
        return {"status": "error", "note": f"exit {proc.returncode}: {proc.stderr[-400:]}"}
    try:
        payload = json.loads(proc.stdout.strip().splitlines()[-1])
    except Exception as exc:
        return {"status": "error", "note": f"stdout is not JSON: {exc}"}
    verdict = str(payload.get("verdict", "")).lower()
    if verdict not in ("yes", "no"):
        return {"status": "error", "note": f"verdict not yes|no: {verdict!r}"}
    return {"status": "ok", "verdict": verdict, "note": payload.get("note", "")}


def run_judge(spec_path: str | Path, out_dir: Optional[str | Path] = None) -> dict:
    spec = load_spec(spec_path)
    cwd = Path(spec["_dir"])
    ref = str((cwd / spec["reference"]).resolve()) if not Path(spec["reference"]).is_absolute() else spec["reference"]
    cand = str((cwd / spec["candidate"]).resolve()) if not Path(spec["candidate"]).is_absolute() else spec["candidate"]
    prompt = spec["prompt"]

    families = []
    discarded = []
    kept = []
    for judge in spec["judges"]:
        family = judge["family"]
        cmd = list(judge["command"])
        ab = _run_judge(cmd, {
            "VQA_JUDGE_A": cand, "VQA_JUDGE_B": ref,
            "VQA_JUDGE_PROMPT": prompt, "VQA_JUDGE_ORDER": "ab",
        }, cwd)
        ba = _run_judge(cmd, {
            "VQA_JUDGE_A": ref, "VQA_JUDGE_B": cand,
            "VQA_JUDGE_PROMPT": prompt, "VQA_JUDGE_ORDER": "ba",
        }, cwd)
        # ba asks the swapped pair; invert yes/no so both mean "candidate matches reference"
        if ba["status"] == "ok":
            ba["verdict_normalized"] = "yes" if ba["verdict"] == "yes" else "no"
            # When order is ba, A is reference and B is candidate. The prompt must
            # be written as "does A match B" so ba.yes means the same as ab.yes.
            # We require the judge to answer the prompt as given; inconsistency
            # (ab != ba) discards the pair.
        record = {"family": family, "ab": ab, "ba": ba}
        families.append(record)
        if ab["status"] != "ok" or ba["status"] != "ok":
            discarded.append({**record, "reason": "backend error"})
            continue
        if ab["verdict"] != ba["verdict"]:
            discarded.append({**record, "reason": "order-inconsistent; discarded"})
            continue
        kept.append({"family": family, "verdict": ab["verdict"]})

    if len(kept) < 2:
        verdict = "discarded"
        note = (
            f"need two consistent family votes, kept {len(kept)}; "
            "a leftover singleton is not a vote"
        )
    else:
        votes = {k["verdict"] for k in kept}
        if len(votes) == 1:
            verdict = kept[0]["verdict"]
            note = f"{len(kept)} families agree"
        else:
            verdict = "split"
            note = "consistent families disagree; no rollup"

    payload = {
        "engine": _core.ENGINE_VERSION,
        "spec": spec["_path"],
        "altitude": spec.get("altitude", "D"),
        "literal": False,
        "verdict": verdict,
        "note": note,
        "kept": kept,
        "discarded": discarded,
        "families": families,
    }
    if out_dir:
        write_json(payload, Path(out_dir) / "judge.json")
    return payload
