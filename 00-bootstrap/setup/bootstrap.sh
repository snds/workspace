#!/bin/bash
#!/bin/bash
# One-liner bootstrap for macOS / Linux.
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/snds/claude-workspace-system/main/00-bootstrap/setup/bootstrap.sh | bash
#
# Clones the repo to a temp dir, runs setup.py. Setup will then locate the Drive
# workspace folder and git-clone into it as part of its normal flow.

set -e

REPO_URL="${CLAUDE_WORKSPACE_REPO:-}"
if [ -z "$REPO_URL" ]; then
  echo "Set CLAUDE_WORKSPACE_REPO to your private repo URL before running:"
  echo "  export CLAUDE_WORKSPACE_REPO=git@github.com:snds/claude-workspace-system.git"
  echo "  curl -fsSL https://raw.githubusercontent.com/snds/claude-workspace-system/main/00-bootstrap/setup/bootstrap.sh | bash"
  exit 1
fi

TMPDIR="$(mktemp -d)"
trap 'rm -rf "$TMPDIR"' EXIT

echo "Cloning $REPO_URL to temp..."
git clone --depth 1 "$REPO_URL" "$TMPDIR/workspace"

cd "$TMPDIR/workspace"
export CLAUDE_WORKSPACE_REPO="$REPO_URL"
python3 00-bootstrap/setup/setup.py
