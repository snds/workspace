#!/usr/bin/env python3
"""
side-chat-handback.py — helpers for the side-chat → parent inbox.

The agent authors 06-context/side-chat-inbox.md (see 03-skills/side-chat-handback).
This script only does the mechanical bits: resolve workspace root, clip the
"For the parent" paragraph, report pending/consumed status.

Usage:
  python3 09-tools/side-chat-handback.py --status
  python3 09-tools/side-chat-handback.py --clip-from-inbox
  python3 09-tools/side-chat-handback.py --mark-consumed
  python3 09-tools/side-chat-handback.py --path
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path


def workspace_root() -> Path:
    here = Path(__file__).resolve().parent.parent
    if (here / "AGENTS.md").is_file():
        return here
    brain = Path.home() / ".claude" / "workspace-brain-path"
    if brain.is_file():
        p = Path(brain.read_text(encoding="utf-8").strip().splitlines()[0])
        if (p / "AGENTS.md").is_file():
            return p
    for cand in (
        Path.home() / "Projects" / "Workspace",
        Path.home() / "Projects" / "workspace",
        Path.home() / "projects" / "workspace",
    ):
        if (cand / "AGENTS.md").is_file():
            return cand
    return here


def inbox_path(root: Path | None = None) -> Path:
    return (root or workspace_root()) / "06-context" / "side-chat-inbox.md"


def read_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end < 0:
        return {}
    block = text[3:end]
    out: dict[str, str] = {}
    for line in block.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            out[k.strip()] = v.strip()
    return out


def for_the_parent(text: str) -> str:
    m = re.search(
        r"^## For the parent\s*\n+(.*?)(?=\n## |\Z)",
        text,
        re.MULTILINE | re.DOTALL,
    )
    if not m:
        return ""
    return m.group(1).strip()


def pbcopy(text: str) -> bool:
    try:
        subprocess.run(["pbcopy"], input=text.encode("utf-8"), check=True)
        return True
    except (OSError, subprocess.CalledProcessError):
        return False


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--path", action="store_true", help="print inbox path")
    ap.add_argument("--status", action="store_true", help="print pending|consumed|missing")
    ap.add_argument(
        "--clip-from-inbox",
        action="store_true",
        help="copy 'For the parent' paragraph to the clipboard (macOS pbcopy)",
    )
    ap.add_argument(
        "--mark-consumed",
        action="store_true",
        help="set frontmatter status: consumed (no-op if missing)",
    )
    args = ap.parse_args()
    root = workspace_root()
    path = inbox_path(root)

    if args.path:
        print(path)
        return 0

    if not path.is_file():
        if args.status:
            print("missing")
            return 0
        print(f"no inbox at {path}", file=sys.stderr)
        return 1

    text = path.read_text(encoding="utf-8")
    fm = read_frontmatter(text)
    status = fm.get("status", "unknown")

    if args.status:
        print(status)
        return 0

    if args.clip_from_inbox:
        para = for_the_parent(text)
        if not para:
            print("no '## For the parent' section", file=sys.stderr)
            return 1
        if pbcopy(para):
            print("clipboard-ok")
            return 0
        print("clipboard-fail", file=sys.stderr)
        return 1

    if args.mark_consumed:
        if "status:" in text.split("---", 2)[1]:
            new = re.sub(
                r"(?m)^status:\s*\S+",
                "status: consumed",
                text,
                count=1,
            )
        else:
            new = text
        path.write_text(new, encoding="utf-8")
        print("consumed")
        return 0

    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
