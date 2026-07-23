"""Shared helpers: paths, profile/manifest I/O, rendering, git, skill iteration.

This is the seam library both the CLI commands and the adapters import. The two
contract files live in a generated workspace:
  - context/profile.yaml   (the person — produced/edited by the brain via `wsx profile set`)
  - manifest.json          (the routing index — maintained by wsx)
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from . import yamlio

GEN_ROOT = Path(__file__).resolve().parent.parent  # the generator/ dir
SCHEMAS = GEN_ROOT / "schemas"


# ---------------------------------------------------------------- workspace ---
def find_workspace_root(start: str | None = None) -> Path | None:
    """Walk up from `start` (or cwd) to the nearest wsx workspace."""
    p = Path(start or os.getcwd()).resolve()
    for cand in [p, *p.parents]:
        if (cand / "manifest.json").exists() and (cand / "context").is_dir():
            return cand
    return None


def require_workspace() -> Path:
    root = find_workspace_root()
    if not root:
        raise SystemExit(
            "error: not inside a wsx workspace (no manifest.json found).\n"
            "       run 'wsx init <dir>' first, then cd into it."
        )
    return root


def today() -> str:
    return datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d")


def now_stamp() -> str:
    return datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M %Z")


# ------------------------------------------------------------------ render ---
_PLACEHOLDER = re.compile(r"\{\{([^}]+)\}\}")


def render(text: str, ctx: dict) -> str:
    """Replace {{key}} / {{a.b.c}} from a nested ctx dict. Missing keys stay literal."""
    def repl(m):
        cur = ctx
        for part in m.group(1).strip().split("."):
            if isinstance(cur, dict) and part in cur:
                cur = cur[part]
            else:
                return m.group(0)
        if isinstance(cur, list):
            return ", ".join(str(x) for x in cur)
        return "" if cur is None else str(cur)

    return _PLACEHOLDER.sub(repl, text)


# ----------------------------------------------------------------- profile ---
def profile_path(root: Path) -> Path:
    return root / "context" / "profile.yaml"


def load_profile(root: Path) -> dict:
    f = profile_path(root)
    return yamlio.loads(f.read_text(encoding="utf-8")) if f.exists() else {}


def save_profile(root: Path, prof: dict) -> None:
    profile_path(root).write_text(yamlio.dumps(prof) + "\n", encoding="utf-8")


# ---------------------------------------------------------------- manifest ---
def manifest_path(root: Path) -> Path:
    return root / "manifest.json"


def load_manifest(root: Path) -> dict:
    f = manifest_path(root)
    return json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}


def save_manifest(root: Path, man: dict) -> None:
    manifest_path(root).write_text(json.dumps(man, indent=2) + "\n", encoding="utf-8")


# -------------------------------------------------------------------- skills ---
def iter_skills(root: Path):
    """Yield (name, SKILL.md Path) for each skill folder under skills/."""
    sdir = root / "skills"
    if not sdir.is_dir():
        return
    for d in sorted(sdir.iterdir()):
        sk = d / "SKILL.md"
        if d.is_dir() and sk.exists():
            yield d.name, sk


def parse_frontmatter(path: Path):
    """Return (frontmatter_dict, body) for a markdown file with --- yaml --- header."""
    text = Path(path).read_text(encoding="utf-8")
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            fm = text[3:end].strip("\n")
            body = text[end + 4:].lstrip("\n")
            try:
                return yamlio.loads(fm), body
            except Exception:
                pass
    return {}, text


def skill_triggers(fm: dict) -> list:
    """Normalize a skill's triggers from front matter (list, or comma string)."""
    t = fm.get("triggers")
    if isinstance(t, list):
        return [str(x).strip().lower() for x in t if str(x).strip()]
    if isinstance(t, str):
        return [x.strip().lower() for x in t.split(",") if x.strip()]
    return []


# ---------------------------------------------------------------------- git ---
def git(root: Path, *args, check: bool = True, capture: bool = False):
    return subprocess.run(
        ["git", "-C", str(root), *args],
        check=check, text=True,
        capture_output=capture,
    )


def has_remote(root: Path) -> bool:
    r = git(root, "remote", check=False, capture=True)
    return bool(r.stdout.strip())


def sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()
