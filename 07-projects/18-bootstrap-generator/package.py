#!/usr/bin/env python3
"""Build per-OS distribution zips of the generator.

    python3 package.py

Produces dist/wsx-generator-{macos,windows,linux}.zip, each a self-contained
`wsx-generator/` folder: the full tool + a permission-free launcher + a plain-
language START-HERE for that OS. Nothing in the zip needs to be executable —
every launcher invokes the system Python on a .py file, which sidesteps the
execute-bit and Gatekeeper/SmartScreen prompts entirely.
"""
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"

# What ships in every zip (the tool itself + user-facing docs + the launcher).
COMMON = ["generator", "brain", ".claude", "launch.py",
          "README.md", "VALIDATION.md", "SPEC.md", "DEVELOPING.md"]

# Never ship: build junk, VCS, personal state, generated/test workspaces.
EXCLUDE_NAMES = {"__pycache__", ".git", ".DS_Store", "dist", "package.py",
                 "packaging", "SESSION-STATE.md", ".gitignore"}
EXCLUDE_SUFFIX = {".pyc", ".zip"}


def _keep(p: Path) -> bool:
    parts = set(p.parts)
    if parts & EXCLUDE_NAMES:
        return False
    if p.suffix in EXCLUDE_SUFFIX:
        return False
    return True


BYO = ("Your data stays yours: this tool has NO API key and never calls an AI model\n"
       "itself — it runs on your own AI app and account. A local model (Ollama) is\n"
       "fully private and free.\n")

# The #1 tester failure: pointing a CHAT-ONLY assistant (ChatGPT, Perplexity, Gemini in
# a browser) at a folder. Those have no filesystem access — the request can never
# succeed, and the assistant will just ask for a zip. Say so plainly, up front.
WHICH_AI = """WHICH AI CAN DO THIS?  (read this first — it saves an hour)

  ✅ CAN open this folder and build for you:
       • Claude Desktop (includes Claude Code)  https://claude.ai/download  (recommended)
       • Cursor                                 https://cursor.com
     Open this folder in one of those and type:   set up my workspace

  ⚠️  ChatGPT, Perplexity, and Gemini in a browser CANNOT open folders on your
     computer. There is nothing to "point" them at — asking them to read a path
     like /Users/you/Documents/... will always fail. That is expected, not a bug.
     To use those, hand them the portable context pack instead:
       1. Build your workspace with Claude or Cursor (above).
       2. In the workspace, run:   python3 wsx.py emit pack
       3. Paste or upload  adapters/context-pack.md  into the chat.
"""

START = {
    "macos": f"""START HERE — Bootstrap Generator (macOS)
=========================================

{WHICH_AI}
EASIEST — no setup, nothing to allow:
  1. Open THIS folder in Claude Desktop or Cursor (see above).
  2. Type:   set up my workspace
  It interviews you and builds everything. Done.

Prefer to just create the starter folder yourself?
  Option 1 — double-click:
     Right-click "start.command"  →  Open  →  Open.
     (macOS asks once because this isn't from the App Store. That's normal and
      safe — you're choosing to open your own file.)
  Option 2 — one line, no permissions:
     Open the Terminal app. Type  python3  and a SPACE, then DRAG the file
     "launch.py" from this folder into the Terminal window, and press Return.

{BYO}""",
    "windows": f"""START HERE — Bootstrap Generator (Windows)
===========================================

{WHICH_AI}
EASIEST — no setup, nothing to allow:
  1. Open THIS folder in Claude or Cursor (see above).
  2. Type:   set up my workspace
  It interviews you and builds everything. Done.

Prefer to just create the starter folder yourself?
  • Double-click  start.bat
    If Windows SmartScreen warns: click "More info" then "Run anyway".
    That's normal for downloaded tools.
  • Needs Python: if it says Python isn't found, install it from
    https://www.python.org/downloads/ (CHECK "Add Python to PATH"), then
    double-click start.bat again.

{BYO}""",
    "linux": f"""START HERE — Bootstrap Generator (Linux)
=========================================

{WHICH_AI}
EASIEST — no setup:
  Open THIS folder in Claude or Cursor (see above) and type:   set up my workspace

Or create the starter folder yourself — in a terminal in this folder:
  python3 launch.py

(Python 3 required: sudo apt install python3  /  sudo dnf install python3.)

{BYO}""",
}

# OS -> extra launcher files to include (relative to ROOT).
LAUNCHERS = {
    "macos": ["start.command", "start.sh"],
    "windows": ["start.bat"],
    "linux": ["start.sh"],
}


def _add_file(zf: zipfile.ZipFile, src: Path, arcname: str) -> None:
    zf.write(src, arcname)


def build(os_key: str) -> Path:
    DIST.mkdir(exist_ok=True)
    out = DIST / f"wsx-generator-{os_key}.zip"
    if out.exists():
        out.unlink()
    top = "wsx-generator"
    count = 0
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        # common tree
        for item in COMMON:
            src = ROOT / item
            if not src.exists():
                continue
            if src.is_dir():
                for f in sorted(src.rglob("*")):
                    if f.is_file() and _keep(f.relative_to(ROOT)):
                        zf.write(f, f"{top}/{f.relative_to(ROOT)}")
                        count += 1
            else:
                zf.write(src, f"{top}/{item}")
                count += 1
        # os launchers
        for lf in LAUNCHERS[os_key]:
            src = ROOT / lf
            if src.exists():
                zf.write(src, f"{top}/{lf}")
                count += 1
        # start-here
        zf.writestr(f"{top}/START-HERE.txt", START[os_key])
        count += 1
    print(f"  ✓ {out.relative_to(ROOT)}  ({count} files, {out.stat().st_size // 1024} KB)")
    return out


def main() -> int:
    if DIST.exists():
        shutil.rmtree(DIST)
    print("Building distribution zips…")
    for os_key in ("macos", "windows", "linux"):
        build(os_key)
    print(f"\nDone → {DIST}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
