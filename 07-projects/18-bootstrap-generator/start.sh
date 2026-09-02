#!/usr/bin/env bash
# Bootstrap Generator — on-ramp for Linux/macOS.
# Run it permission-free with:   python3 launch.py
# (This wrapper just calls that; nothing here needs an execute bit.)
cd "$(dirname "${BASH_SOURCE[0]}")" || exit 1
if command -v python3 >/dev/null 2>&1; then
  exec python3 launch.py
fi
echo "Python 3 isn't installed. On Debian/Ubuntu: sudo apt install python3"
echo "On Fedora: sudo dnf install python3 . Then: python3 launch.py"
