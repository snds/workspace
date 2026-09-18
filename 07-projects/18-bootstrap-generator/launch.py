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


def _scan():
    sys.path.insert(0, str(HERE / "generator"))
    from wsxlib import scan
    return scan


def pick_surface():
    """Auto-detect folder-capable apps; pick the platform ideal; let them override."""
    scan = _scan()
    found = scan.folder_capable()
    print("Checking which AI apps on this computer can open a folder…\n")
    if found:
        for i, a in enumerate(found, 1):
            mark = "  ← recommended here" if i == 1 else ""
            print(f"  {i}. {a['name']}  (found via {a['via']}){mark}")
        print()
        default = found[0]["name"]
        raw = ask("Which one should start the interview? (number, or skip)", "1")
        if raw.lower() in ("skip", "none", "n"):
            return scan.briefing(found[0]), False
        try:
            idx = int(raw) - 1
        except ValueError:
            idx = 0
        if idx < 0 or idx >= len(found):
            idx = 0
        return scan.briefing(found[idx]), True
    rec = scan.briefing(None)
    print("  — none found (Cursor / Claude / VS Code aren't installed, or aren't")
    print("    on PATH). That's OK — you can install one in a minute.\n")
    print(f"  Recommended on this computer: {rec['name']}")
    print(f"    {rec['install']}\n")
    return rec, False


def tell_and_open(brief, offer_open: bool) -> None:
    scan = _scan()
    print("\nNext — start the interview in your AI app:")
    print(f"  App:    {brief['name']}")
    print(f"  Folder: {HERE}")
    print(f"  How:    {brief['how']}")
    print("  Paste this in the chat:\n")
    print(f"    {brief['prompt']}\n")
    if not brief["detected"]:
        print(f"  Install {brief['name']} first: {brief['install']}")
        print("  Then open this generator folder in it (not the new workspace yet).")
        return
    if not offer_open:
        return
    yn = ask(f"Open this folder in {brief['name']} now?", "yes")
    if yn.lower().startswith("y"):
        if scan.try_open(brief, HERE):
            print(f"  ✓ launched {brief['name']}. Paste the line above into Agent chat.")
        else:
            print(f"  Couldn't launch {brief['name']} automatically. Open it yourself:")
            print(f"    {brief['how']}")


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

    brief, can_open = pick_surface()

    # An unfinished interview (even from a previous unzip) lives in ~/.wsx.
    st = wsx("interview", "status", capture_output=True, text=True)
    if st.returncode == 0 and "in-progress session found" in (st.stdout or ""):
        print(st.stdout)
        choice = ask("Continue that workspace, or start over?", "continue")
        if choice.lower().startswith("c"):
            print("\nOpen that folder in your AI assistant and say:")
            print('  "continue my workspace interview"')
            tell_and_open(brief, can_open)
            pause()
            return 0
        wsx("interview", "abandon")
        print("Unfinished interview discarded. Starting fresh.\n")

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

    # Emit every adapter so Cursor/VS Code/Claude all have their first-file.
    # wsx resolves the workspace from cwd, so run it inside the new folder.
    print("Making it AI-ready…")
    wsx("emit", "all", cwd=dest,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    print("\n✓ Done. Your workspace folder is at:")
    print(f"    {dest}\n")
    print("The interview still starts FROM THIS generator folder (the tool),")
    print("not from the new workspace. When it asks where the workspace lives,")
    print(f"answer:  {dest}")
    tell_and_open(brief, can_open)
    print("Browse notes later in Obsidian (https://obsidian.md).")
    pause()
    return 0


def _have(cmd) -> bool:
    from shutil import which
    return which(cmd) is not None


if __name__ == "__main__":
    raise SystemExit(main())
