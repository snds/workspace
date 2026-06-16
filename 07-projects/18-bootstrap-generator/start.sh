#!/usr/bin/env bash
# Bootstrap Generator — the dummy-proof on-ramp.
# macOS: double-click  start.command  (it runs this).  Or run:  bash start.sh
# This creates a NEW workspace folder for you. (This downloaded folder is the
# generator — the tool — not your workspace.)

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WSX="$HERE/generator/bin/wsx"

echo "──────────────────────────────────────────────"
echo "   Bootstrap Generator — set up your workspace"
echo "──────────────────────────────────────────────"
echo

# 1) Python 3 (required)
if ! command -v python3 >/dev/null 2>&1; then
  echo "✗ Python 3 isn't installed."
  echo "  On a Mac, install Apple's free command-line tools:"
  echo "      xcode-select --install"
  echo "  …or get Python from https://www.python.org/downloads/ , then run this again."
  read -r -p "Press Return to close. " _ || true
  exit 1
fi

# 2) git (recommended, not required)
if ! command -v git >/dev/null 2>&1; then
  echo "⚠ git isn't installed — your workspace won't sync across devices or keep history."
  echo "  Get it free from https://desktop.github.com , then re-run for sync. Continuing without it."
  echo
fi

# 3) Where + who
DEFAULT_DEST="$HOME/Documents/my-workspace"
printf "Where should your workspace live?\n  [press Return for: %s]\n> " "$DEFAULT_DEST"
read -r DEST || true
DEST="${DEST:-$DEFAULT_DEST}"
DEST="${DEST/#\~/$HOME}"   # expand a leading ~

printf "Your name (for the workspace) [you]: "
read -r NAME || true
NAME="${NAME:-you}"

# 4) Build it
echo
echo "Creating your workspace…"
python3 "$WSX" init "$DEST" --name "$NAME"
if [ $? -ne 0 ]; then
  echo
  echo "✗ Couldn't create the workspace there (the folder may already exist and not be empty)."
  echo "  Try again with a different location."
  read -r -p "Press Return to close. " _ || true
  exit 1
fi

# 5) Make it AI-ready on the recommended (Claude) path — harmless if it no-ops
( cd "$DEST" && python3 "$WSX" emit claude-code >/dev/null 2>&1 ) || true

echo
echo "✓ Done. Your workspace is at:"
echo "    $DEST"
echo
echo "Next — pick ONE:"
echo "  • Browse it: open that folder in Obsidian (https://obsidian.md)."
echo "  • Let your AI fill it in: open the folder in your AI assistant"
echo "    (Claude Code, Cursor, …) and say:   \"set up my workspace\""
echo
read -r -p "Press Return to close. " _ || true
