"""
capture.py — write a provenanced PNG + sibling *.capture.json.

This is the workspace capture path. Pack-specific wrappers (e.g. LCARS
`scripts/capture-sys47.mjs`) must call `vqa capture`, not own the contract.

Browser backends (first that works):
  1. Python `playwright`
  2. Node `playwright` via scripts/capture.mjs (resolves from cwd node_modules)

Absence is a usage error for `vqa capture`, not a silent skip. Prove still
accepts a PNG you already have; it just stays unverified without a manifest.
"""
from __future__ import annotations

import datetime
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Optional

from . import _core
from ._core import write_json

SKILL_DIR = Path(__file__).resolve().parent.parent
NODE_CAPTURE = Path(__file__).resolve().parent / "capture.mjs"
ASSISTANCE_VALUES = ("off", "on", "unknown")


def write_manifest(
    image_path: str | Path,
    *,
    viewport: dict,
    dpr: float,
    frozen: bool = True,
    url: Optional[str] = None,
    tool: str = "vqa-capture",
    reduced_motion: Optional[bool] = None,
    assistance: str = "unknown",
    renderer: Optional[str] = None,
    rng_frozen: Optional[bool] = None,
    extra: Optional[dict[str, Any]] = None,
) -> Path:
    """Write `<stem>.capture.json` next to the PNG (verify-capture cand2)."""
    if assistance not in ASSISTANCE_VALUES:
        raise ValueError(f"assistance must be one of {ASSISTANCE_VALUES}, got {assistance!r}")
    image_path = Path(image_path)
    manifest: dict[str, Any] = {
        "viewport": {
            "width": int(viewport["width"]),
            "height": int(viewport["height"]),
        },
        "dpr": float(dpr),
        "format": "png",
        "frozen": bool(frozen),
        "tool": tool,
        "time": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "assistance": assistance,
    }
    if url:
        manifest["url"] = url
    if reduced_motion is not None:
        manifest["reduced_motion"] = bool(reduced_motion)
    if renderer:
        manifest["renderer"] = renderer
    if rng_frozen is not None:
        manifest["rng_frozen"] = bool(rng_frozen)
    if extra:
        manifest.update(extra)
    out = image_path.with_suffix(".capture.json")
    write_json(manifest, out)
    return out


def playwright_backends() -> dict:
    py = False
    try:
        import playwright  # noqa: F401
        py = True
    except Exception:
        pass
    node = shutil.which("node") is not None and NODE_CAPTURE.exists()
    return {"python_playwright": py, "node_playwright_script": node}


def _capture_python_playwright(
    url: str,
    out: Path,
    viewport: dict,
    dpr: float,
    reduced_motion: bool,
    wait_ms: int,
    full_page: bool,
) -> None:
    from playwright.sync_api import sync_playwright  # type: ignore

    with sync_playwright() as p:
        browser = p.chromium.launch()
        context_kwargs: dict[str, Any] = {
            "viewport": {"width": int(viewport["width"]), "height": int(viewport["height"])},
            "device_scale_factor": float(dpr),
        }
        if reduced_motion:
            context_kwargs["reduced_motion"] = "reduce"
        page = browser.new_page(**context_kwargs)
        page.goto(url, wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(wait_ms)
        page.screenshot(path=str(out), full_page=full_page)
        browser.close()


def _capture_node_playwright(
    url: str,
    out: Path,
    viewport: dict,
    dpr: float,
    reduced_motion: bool,
    wait_ms: int,
    full_page: bool,
) -> None:
    if not NODE_CAPTURE.exists():
        raise RuntimeError(f"missing {NODE_CAPTURE}")
    env = os.environ.copy()
    env["VQA_CAPTURE_URL"] = url
    env["VQA_CAPTURE_OUT"] = str(out)
    env["VQA_CAPTURE_WIDTH"] = str(int(viewport["width"]))
    env["VQA_CAPTURE_HEIGHT"] = str(int(viewport["height"]))
    env["VQA_CAPTURE_DPR"] = str(dpr)
    env["VQA_CAPTURE_WAIT_MS"] = str(int(wait_ms))
    env["VQA_CAPTURE_FULL_PAGE"] = "1" if full_page else "0"
    env["VQA_CAPTURE_REDUCED_MOTION"] = "1" if reduced_motion else "0"
    proc = subprocess.run(
        ["node", str(NODE_CAPTURE)],
        cwd=os.getcwd(),
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout or "").strip()
        raise RuntimeError(f"node capture failed ({proc.returncode}): {detail}")


def capture_url(
    url: str,
    out: str | Path,
    *,
    viewport: dict,
    dpr: float = 2,
    reduced_motion: bool = True,
    wait_ms: int = 1000,
    full_page: bool = False,
    assistance: str = "unknown",
    renderer: Optional[str] = None,
) -> dict:
    """Capture `url` to PNG + manifest. Raises RuntimeError if no browser backend."""
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    backends = playwright_backends()
    used = None
    if backends["python_playwright"]:
        _capture_python_playwright(url, out, viewport, dpr, reduced_motion, wait_ms, full_page)
        used = "python-playwright"
    elif backends["node_playwright_script"]:
        _capture_node_playwright(url, out, viewport, dpr, reduced_motion, wait_ms, full_page)
        used = "node-playwright"
    else:
        raise RuntimeError(
            "vqa capture needs Playwright. Install one of: "
            "`python3 -m pip install playwright && python3 -m playwright install chromium` "
            "or add `playwright` to the app's node_modules and run from that repo. "
            "Or capture the PNG yourself and pass it to `vqa prove` with a hand-written manifest."
        )
    if not out.exists():
        raise RuntimeError(f"capture backend {used} did not write {out}")
    manifest = write_manifest(
        out,
        viewport=viewport,
        dpr=dpr,
        frozen=reduced_motion,
        url=url,
        tool=f"vqa-capture/{used}",
        reduced_motion=reduced_motion,
        assistance=assistance,
        renderer=renderer,
    )
    verified = _core.verify_capture(out, manifest)
    return {
        "image": str(out.resolve()),
        "manifest": str(manifest.resolve()),
        "backend": used,
        "verify": verified,
    }


def self_test() -> dict:
    """Manifest write + verify without a browser. Used by CI / doctor-adjacent checks."""
    with tempfile.TemporaryDirectory() as td:
        png = Path(td) / "fixture.png"
        _core.save_image(__import__("numpy").zeros((2160, 3840, 3), dtype="uint8"), png)
        mp = write_manifest(
            png,
            viewport={"width": 1920, "height": 1080},
            dpr=2,
            frozen=True,
            url="http://127.0.0.1/fixture",
            assistance="off",
            renderer="test",
            rng_frozen=True,
        )
        result = _core.verify_capture(png, mp)
        if result["status"] != "verified":
            raise AssertionError(f"self-test verify failed: {result}")
        if result.get("assistance") != "off":
            raise AssertionError(f"assistance not round-tripped: {result}")
        return {"status": "ok", "verify": result}


if __name__ == "__main__":
    print(json.dumps(self_test(), indent=2))
    sys.exit(0)
