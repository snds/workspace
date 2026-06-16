#!/usr/bin/env bash
# Double-clickable launcher for macOS (Finder opens .command files in Terminal).
# First time, macOS may say "unidentified developer": right-click → Open → Open.
exec "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/start.sh"
