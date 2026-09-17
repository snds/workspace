"""`wsx dispatch` — close-out detector table. Non-zero exit. Honest skip.

Tiny: command-hub → one CLI (`wsx lint|verify|health`) or skip. Not a pasted essay.
A missing detector that cannot be minted is an honest skip, not a silent `done`.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from . import core

# Hub name → argv after `wsx.py`. Override per-skill with front-matter `detector:`.
_TABLE = {
    "close-out": ["verify"],
    "plan-ahead": ["lint"],
    "self-improve": ["health"],
}


def _detector_for(root: Path, hub: str) -> list | None:
    for name, sk in core.iter_skills(root):
        if name != hub:
            continue
        fm, _ = core.parse_frontmatter(sk)
        raw = str(fm.get("detector") or "").strip()
        if raw.lower() in ("skip", "none", "honest-skip"):
            return None
        if raw:
            return [p for p in re_split(raw) if p]
        return list(_TABLE.get(hub) or ["verify"])
    return list(_TABLE.get(hub) or ["verify"]) if hub in _TABLE else None


def re_split(raw: str) -> list:
    return [p.strip() for p in raw.replace(",", " ").split() if p.strip()]


def run(root: Path, hub: str = "close-out") -> int:
    hub = (hub or "close-out").strip()
    cmds = _detector_for(root, hub)
    if cmds is None:
        print(f"wsx dispatch — honest skip ({hub}: no detector / detector: skip)")
        print("  Do not claim done. Page the human if this produce still needs a proof gate.")
        return 0
    wsx = root / "wsx.py"
    py = sys.executable
    print(f"wsx dispatch — {hub} → {', '.join(cmds)}\n")
    rc = 0
    for cmd in cmds:
        print(f"===== wsx {cmd} =====")
        r = subprocess.run([py, str(wsx), cmd], cwd=str(root))
        rc = rc or r.returncode
    if rc:
        print("\nwsx dispatch — FAILED. Not done. Do not write verified/done.")
    else:
        print("\nwsx dispatch — detectors passed.")
    return rc
