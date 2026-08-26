"""
interact.py — deterministic action-effect verification from state captures.

The primitive: an interaction step declares an EXPECTED visible effect before
it is judged (change / no_change, where, how much). The verifier then compares
the before/after captures and checks the expectation against pixels. This is
the deterministic version of pre/post-action screenshot verification from the
GUI-agent literature: the agent's claim ("I hovered and the row highlighted")
is not accepted — the pixel delta is.

Interaction spec (JSON):
{
  "spec": "vqa-interact/1",
  "steps": [
    {
      "name": "hover highlights row",
      "before": "captures/idle.png",
      "after": "captures/hover.png",
      "expect": "change",                # or "no_change"
      "region": [0.1, 0.4, 0.8, 0.08],   # optional, fractions; where change must land
      "min_changed_fraction": 0.005,     # of region (default 0.002)
      "max_outside_fraction": 0.002      # of rest of canvas (default 0.01)
    }
  ]
}

Failure modes this catches: dead controls (after == before while expecting
change), side effects (change leaking outside the declared region), and
phantom claims (an agent reporting an effect no pixel shows).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import numpy as np

from . import _core
from ._core import change_mask, denorm_rect, load_image, save_image, write_json


def load_interact_spec(path: str | Path) -> dict:
    p = Path(path)
    spec = json.loads(p.read_text(encoding="utf-8"))
    if spec.get("spec") != "vqa-interact/1":
        raise ValueError(f"unsupported interact spec version: {spec.get('spec')!r}")
    if not spec.get("steps"):
        raise ValueError("interact spec has no steps")
    spec["_dir"] = str(p.parent.resolve())
    return spec


def verify_step(step: dict, spec_dir: Path, out_dir: Optional[Path] = None,
                threshold_de: float = 4.0) -> dict:
    def resolve(rel):
        q = Path(rel).expanduser()
        return q if q.is_absolute() else spec_dir / q

    before = load_image(resolve(step["before"]))
    after = load_image(resolve(step["after"]))
    result: dict = {"name": step.get("name", "step"), "expect": step.get("expect", "change")}
    if (before.width, before.height) != (after.width, after.height):
        result.update(status="error",
                      note=f"size mismatch {before.width}x{before.height} vs {after.width}x{after.height}")
        return result

    mask = change_mask(before.rgb, after.rgb, threshold_de=threshold_de)
    total_frac = float(mask.mean())
    expect = step.get("expect", "change")

    if "region" in step:
        rect = denorm_rect(step["region"], before.width, before.height)
        x, y, w, h = rect
        region_mask = mask[y : y + h, x : x + w]
        inside_frac = float(region_mask.mean())
        outside = mask.copy()
        outside[y : y + h, x : x + w] = False
        denom = mask.size - w * h
        outside_frac = float(outside.sum() / denom) if denom > 0 else 0.0
        result["region_px"] = list(rect)
    else:
        inside_frac = total_frac
        outside_frac = 0.0

    min_changed = float(step.get("min_changed_fraction", 0.002))
    max_outside = float(step.get("max_outside_fraction", 0.01))

    reasons = []
    if expect == "change":
        if inside_frac < min_changed:
            reasons.append(
                f"expected visible change (>={min_changed:.3%}) but measured {inside_frac:.3%}"
                + (" in region" if "region" in step else "")
            )
        if outside_frac > max_outside:
            reasons.append(
                f"change leaked outside region: {outside_frac:.3%} > {max_outside:.3%}"
            )
    else:  # no_change
        if total_frac > max_outside:
            reasons.append(f"expected no change but {total_frac:.3%} of pixels changed")

    result.update(
        status="pass" if not reasons else "fail",
        changed_fraction=round(total_frac, 5),
        inside_fraction=round(inside_frac, 5),
        outside_fraction=round(outside_frac, 5),
        reasons=reasons,
    )

    if out_dir and reasons:
        vis = before.rgb.copy()
        vis[mask] = np.asarray([255, 0, 80], dtype=np.uint8)
        p = save_image(vis, Path(out_dir) / f"interact_{_slug(result['name'])}_diff.png")
        result["evidence"] = str(p)
    return result


def _slug(name: str) -> str:
    return "".join(c if c.isalnum() else "-" for c in name.lower())[:48].strip("-")


def run_interact(spec_path: str | Path, out_dir: Optional[str | Path] = None) -> dict:
    spec = load_interact_spec(spec_path)
    out = Path(out_dir) if out_dir else None
    steps = [verify_step(s, Path(spec["_dir"]), out) for s in spec["steps"]]
    passed = sum(1 for s in steps if s["status"] == "pass")
    payload = {
        "engine": _core.ENGINE_VERSION,
        "spec": str(Path(spec_path).resolve()),
        "steps_total": len(steps),
        "steps_pass": passed,
        "verdict": "pass" if passed == len(steps) else "fail",
        "steps": steps,
    }
    if out:
        write_json(payload, out / "interact.json")
    return payload
