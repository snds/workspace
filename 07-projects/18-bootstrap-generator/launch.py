#!/usr/bin/env python3
"""Bootstrap Generator — the permission-independent on-ramp.

Run it the way that never trips a permission or Gatekeeper prompt:

    python3 launch.py        (macOS / Linux)
    py launch.py             (Windows)

Because you invoke the trusted system Python on this plain .py file, there is no
execute bit to set and nothing for Gatekeeper/SmartScreen to block — unlike a
double-clicked .command/.sh/.app. This script also runs `wsx` the same way
(`python <script>`), so no file in the whole generator needs to be executable.

It creates a NEW workspace folder for you. (This downloaded folder is the
generator — the tool — not your workspace.)
"""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
WSX = HERE / "generator" / "bin" / "wsx"


def wsx(*args, **kw):
    # Always invoke via the current Python — never rely on an exec bit or shebang.
    return subprocess.run([sys.executable, str(WSX), *args], **kw)


def ask(prompt, default):
    try:
        val = input(f"{prompt}\n  [press Return for: {default}]\n> ").strip()
    except (EOFError, KeyboardInterrupt):
        val = ""
    return val or default


def pause():
    try:
        input("\nPress Return to close. ")
    except (EOFError, KeyboardInterrupt):
        pass


def main() -> int:
    # Line-buffer our own output so our prints interleave in the right order with
    # the child `wsx` process's output (otherwise buffering shows them out of order).
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except (AttributeError, ValueError):
        pass

    print("──────────────────────────────────────────────")
    print("   Bootstrap Generator — set up your workspace")
    print("──────────────────────────────────────────────\n")

    if not WSX.exists():
        print(f"✗ Can't find the generator at {WSX}.")
        print("  Run this from inside the unzipped generator folder.")
        pause()
        return 1

    # python3 is obviously present (it's running this). git is recommended.
    if not _have("git"):
        print("⚠ git isn't installed — your workspace won't sync across devices or keep")
        print("  history. Get it free from https://desktop.github.com , then re-run for")
        print("  sync. Continuing without it.\n")

    # Where + who. Default to Documents/Projects/Workspace: keeping it under
    # Documents means iCloud/OneDrive/Time Machine back it up automatically, and a
    # "Projects" folder gives every future project (this workspace included) one home.
    default_dest = str(Path.home() / "Documents" / "Projects" / "Workspace")
    print("Tip: the default puts your workspace in Documents/Projects/Workspace —")
    print("     Documents is auto-backed-up (iCloud/OneDrive/Time Machine), and")
    print("     'Projects' becomes the home for all your projects.\n")
    dest = ask("Where should your workspace live?", default_dest)
    dest = str(Path(dest).expanduser())
    name = ask("Your name (for the workspace):", "you")

    print("\nCreating your workspace…")
    r = wsx("init", dest, "--name", name)
    if r.returncode != 0:
        print("\n✗ Couldn't create the workspace there (the folder may already exist and")
        print("  not be empty). Try again with a different location.")
        pause()
        return 1

    # Make it AI-ready on the recommended path (harmless if it no-ops).
    # wsx resolves the workspace from cwd, so run it inside the new folder.
    wsx("emit", "claude-code", cwd=dest,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Show what assistant is available so they know where to continue.
    print("\nChecking what AI tools you have set up…\n")
    wsx("scan")

    print("\n✓ Done. Your workspace is at:")
    print(f"    {dest}\n")
    print("Next — pick ONE:")
    print("  • Best: open that folder in your AI assistant (Claude Code, Cursor, …)")
    print('    and say:   "set up my workspace"   — it interviews you and fills it in.')
    print("  • Browse it: open the folder in Obsidian (https://obsidian.md).")
    print("  • Decide where it lives online: run  python3 generator/bin/wsx remote")
    pause()
    return 0


def _have(cmd) -> bool:
    from shutil import which
    return which(cmd) is not None


if __name__ == "__main__":
    raise SystemExit(main())
