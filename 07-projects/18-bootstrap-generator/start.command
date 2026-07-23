#!/usr/bin/env bash
# Double-clickable launcher for macOS (Finder opens .command files in Terminal).
# First time, macOS says "unidentified developer" because this isn't from the App
# Store — that's expected: right-click this file → Open → Open (just once).
#
# This only shells out to Python; it never relies on any file being executable.
cd "$(dirname "${BASH_SOURCE[0]}")" || exit 1
exec python3 launch.py
