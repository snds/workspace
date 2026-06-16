#!/bin/bash
# Double-clickable macOS installer for Claude Workspace.
# Runs from Finder; opens Terminal to show progress.
set -e
cd "$(dirname "$0")"

echo ""
echo "Claude Workspace installer (macOS)"
echo "=================================="
echo ""

# Prefer python3 (ships with macOS)
if ! command -v python3 &> /dev/null; then
  echo "Python 3 not found. Installing via Xcode Command Line Tools..."
  xcode-select --install || true
  echo "Re-run this installer after Command Line Tools finishes installing."
  exit 1
fi

python3 ./setup.py
echo ""
echo "Press any key to close..."
read -n 1 -s
