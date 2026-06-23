#!/bin/bash
# Workspace one-click bootstrap — macOS / Linux.
#
# From-scratch grab: ensures git, clones the workspace into a PERMANENT location,
# runs the installer, and opens Obsidian. The repo is PUBLIC, so no auth is needed
# to grab it (you only need auth to push later — `gh auth login`).
#
# Run any of:
#   curl -fsSL https://raw.githubusercontent.com/snds/workspace/main/00-bootstrap/setup/bootstrap.sh | bash
#   ./bootstrap.sh                 # clones to ~/Projects/Workspace
#   ./bootstrap.sh ~/some/path     # custom target
#
# Overrides (env): CLAUDE_WORKSPACE_REPO, CLAUDE_WORKSPACE_DIR, CLAUDE_WORKSPACE_BRANCH

set -euo pipefail

REPO_URL="${CLAUDE_WORKSPACE_REPO:-https://github.com/snds/workspace.git}"
TARGET="${1:-${CLAUDE_WORKSPACE_DIR:-$HOME/Projects/Workspace}}"
BRANCH="${CLAUDE_WORKSPACE_BRANCH:-main}"

say()  { printf '\n\033[1m%s\033[0m\n' "$1"; }
info() { printf '  • %s\n' "$1"; }
ok()   { printf '  \033[32m✓\033[0m %s\n' "$1"; }

# 1. Ensure git is available.
if ! command -v git >/dev/null 2>&1; then
  if [[ "$(uname)" == "Darwin" ]]; then
    say "Installing git via Xcode Command Line Tools…"
    xcode-select --install || true
    echo "Re-run this script once Command Line Tools finish installing." ; exit 1
  else
    echo "git not found. Install it (e.g. 'sudo apt install git' / 'sudo dnf install git') and re-run." ; exit 1
  fi
fi

say "Workspace → $TARGET"
info "repo:   $REPO_URL"
info "branch: $BRANCH"

# 2. Grab. Three cases, all non-destructive.
if [[ -d "$TARGET/.git" ]]; then
  # (a) Already a checkout — just update.
  info "Existing checkout found — updating."
  git -C "$TARGET" remote set-url origin "$REPO_URL" 2>/dev/null || git -C "$TARGET" remote add origin "$REPO_URL"
  git -C "$TARGET" fetch origin "$BRANCH"
  git -C "$TARGET" checkout "$BRANCH" 2>/dev/null || git -C "$TARGET" checkout -b "$BRANCH" --track "origin/$BRANCH"
  git -C "$TARGET" pull --rebase origin "$BRANCH"
  ok "Updated to latest origin/$BRANCH"
elif [[ -e "$TARGET" && -n "$(ls -A "$TARGET" 2>/dev/null)" ]]; then
  # (b) Folder exists, non-empty, but NOT a git repo (e.g. brought in by Obsidian Sync).
  #     Adopt the history WITHOUT touching local files — never clobbers, never fails on conflicts.
  info "Folder is non-empty with no .git — adopting it as the checkout (non-destructive)."
  git -C "$TARGET" init -q
  git -C "$TARGET" symbolic-ref HEAD "refs/heads/$BRANCH"
  git -C "$TARGET" remote add origin "$REPO_URL" 2>/dev/null || git -C "$TARGET" remote set-url origin "$REPO_URL"
  git -C "$TARGET" fetch origin "$BRANCH"
  git -C "$TARGET" reset "origin/$BRANCH"                                  # mixed: adopt history, keep working files
  git -C "$TARGET" branch --set-upstream-to="origin/$BRANCH" "$BRANCH" 2>/dev/null || true
  ok "Adopted. Review differences vs origin/$BRANCH:"
  info "  git -C \"$TARGET\" status"
else
  # (c) Fresh clone into an empty / missing path.
  info "Cloning fresh…"
  mkdir -p "$(dirname "$TARGET")"
  git clone --branch "$BRANCH" "$REPO_URL" "$TARGET"
  ok "Cloned to $TARGET"
fi

# 3. Run the cross-platform installer from inside the checkout (tooling + Obsidian plugins).
if command -v python3 >/dev/null 2>&1; then
  say "Running setup…"
  CLAUDE_WORKSPACE_REPO="$REPO_URL" python3 "$TARGET/00-bootstrap/setup/setup.py" || \
    echo "  (setup.py reported issues — the checkout is fine; re-run it later if needed.)"
else
  echo "  python3 not found — skipping setup.py. Install Python 3 and run:"
  echo "    python3 \"$TARGET/00-bootstrap/setup/setup.py\""
fi

# 4. Open the vault in Obsidian.
if command -v open >/dev/null 2>&1; then
  open -a Obsidian "$TARGET" 2>/dev/null || open "$TARGET" 2>/dev/null || true
elif command -v xdg-open >/dev/null 2>&1; then
  xdg-open "$TARGET" 2>/dev/null || true
fi

say "Done → $TARGET"
echo "  Next: open it in Obsidian (Open folder as vault) and run 'claude' from a terminal there."
