"""
OCR probe for currently attested strings.

Altitude A when it runs (the string is a pixel fact). Without tesseract /
pytesseract the probe cannot honestly measure text: it skips if the cue is
`optional`, else errors. Never silently pass.
"""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Optional


def available() -> dict:
    pyt = False
    try:
        import pytesseract  # noqa: F401
        pyt = True
    except Exception:
        pass
    cli = shutil.which("tesseract")
    return {"pytesseract": pyt, "tesseract": cli is not None, "cli": cli}


def read_text(rgb, lang: str = "eng") -> Optional[str]:
    """rgb uint8 HxWx3 → stripped text, or None if no backend."""
    info = available()
    if info["pytesseract"]:
        from PIL import Image
        import pytesseract  # type: ignore
        img = Image.fromarray(rgb.astype("uint8"), "RGB")
        return pytesseract.image_to_string(img, lang=lang).strip()
    if info["cli"]:
        from PIL import Image
        import tempfile
        tmp = Path(tempfile.mkdtemp(prefix="vqa_ocr_")) / "crop.png"
        Image.fromarray(rgb.astype("uint8"), "RGB").save(tmp)
        proc = subprocess.run(
            [info["cli"], str(tmp), "stdout", "-l", lang],
            capture_output=True, text=True, check=False,
        )
        if proc.returncode != 0:
            return None
        return (proc.stdout or "").strip()
    return None
