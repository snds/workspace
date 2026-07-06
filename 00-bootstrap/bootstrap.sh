#!/usr/bin/env bash
# Fresh-machine installer. Run:
#   bash <(curl -fsSL https://raw.githubusercontent.com/snds/workspace/main/00-bootstrap/bootstrap.sh)
set -euo pipefail
WS="$HOME/Projects/workspace"
command -v git >/dev/null 2>&1 || { echo "Install Xcode CLT first: xcode-select --install"; exit 1; }
if [ ! -d "$WS/.git" ]; then
  mkdir -p "$HOME/Projects"
  git clone git@github.com:snds/workspace.git "$WS" 2>/dev/null \
    || git clone https://github.com/snds/workspace.git "$WS"
fi
exec "$WS/00-bootstrap/doctor/workspace-doctor.sh"
