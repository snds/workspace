"""
evidence.py — assemble a harness run's evidence folder from vqa captures.

The Synapse gate (harness `visual-qa.literal`) reads one folder per run:

  capture.png    the capture under review (the first one given)
  capture.json   its manifest plus app, build, theme, the matrix of every
                 capture taken (`captures`) and the widths the app supports
  cuespec.json   the cuespec whose targets were scouted from the reference
  matrix/        every capture and its manifest, for the person reviewing

`vqa capture` writes `<stem>.capture.json` beside each PNG; this copies them
in, never edits them, and refuses when a capture lacks the theme or the run
lacks an app or a build, since the gate would only fail them later.
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Optional

from . import _core


def _manifest(png: Path) -> dict:
    mp = _core.find_manifest(png)
    if mp is None:
        raise ValueError(f"{png}: no capture manifest; take it with `vqa capture`")
    return json.loads(mp.read_text(encoding="utf-8"))


def assemble(
    out_dir: str | Path,
    captures: list[str | Path],
    *,
    app: Optional[str] = None,
    build: Optional[str] = None,
    supported_widths: Optional[list[int]] = None,
    cuespec: Optional[str | Path] = None,
) -> dict:
    """Write the evidence folder. Raises ValueError with every problem found."""
    if not captures:
        raise ValueError("name at least one capture")
    pngs = [Path(c) for c in captures]
    problems: list[str] = []
    manifests: list[dict] = []
    for png in pngs:
        if not png.exists():
            problems.append(f"{png}: missing")
            continue
        try:
            m = _manifest(png)
        except ValueError as exc:
            problems.append(str(exc))
            continue
        if m.get("theme") not in ("light", "dark"):
            problems.append(f"{png}: the manifest doesn't say its theme (capture with --theme)")
        manifests.append(m)
    first = manifests[0] if manifests else {}
    app = app or first.get("app")
    build = build or first.get("build")
    if not app:
        problems.append("no app: pass --app or capture with --app")
    if not build:
        problems.append("no build: pass --build (a commit, tag or version) or capture with --build")
    if cuespec and not Path(cuespec).exists():
        problems.append(f"{cuespec}: missing")
    if problems:
        raise ValueError("; ".join(problems))

    out = Path(out_dir)
    (out / "matrix").mkdir(parents=True, exist_ok=True)
    rows = []
    for png, m in zip(pngs, manifests):
        shutil.copy2(png, out / "matrix" / png.name)
        shutil.copy2(_core.find_manifest(png), out / "matrix" / f"{png.stem}.capture.json")
        rows.append({"theme": m["theme"], "width": int(m["viewport"]["width"]), "image": f"matrix/{png.name}"})
    shutil.copy2(pngs[0], out / "capture.png")
    widths = sorted(set(supported_widths or [r["width"] for r in rows]))
    manifest = dict(first)
    manifest.update({
        "app": app,
        "build": build,
        "captures": rows,
        "supported_widths": widths,
        "source_image": str(pngs[0]),
    })
    _core.write_json(manifest, out / "capture.json")
    if cuespec:
        shutil.copy2(cuespec, out / "cuespec.json")
    verified = _core.verify_capture(out / "capture.png", out / "capture.json")
    return {
        "evidence": str(out.resolve()),
        "captures": len(rows),
        "supported_widths": widths,
        "cuespec": bool(cuespec),
        "verify": verified,
    }
