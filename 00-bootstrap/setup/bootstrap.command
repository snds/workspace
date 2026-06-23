#!/bin/bash
# Double-click from Finder to grab + set up the workspace on a fresh Mac.
#
# This is a tiny stub: it fetches the canonical bootstrap.sh from GitHub and runs it,
# so it stays current and works even if downloaded on its own. The repo is PUBLIC —
# no login needed to grab it.
#
# First time after downloading: macOS Gatekeeper may block double-click ("unidentified
# developer"). Right-click the file → Open → Open, or run: xattr -d com.apple.quarantine bootstrap.command
#
# Clones to ~/Projects/Workspace by default. Override: CLAUDE_WORKSPACE_DIR=/path before running.

set -e
echo "Claude Workspace — one-click setup (macOS)"
echo "=========================================="
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/snds/workspace/main/00-bootstrap/setup/bootstrap.sh)"
echo ""
echo "Press any key to close…"
read -n 1 -s
