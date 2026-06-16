#!/bin/bash
# install-icon-font-skills.sh
# Creates symlinks from Google Drive skills into Claude's skill directories
# so agents (Claude Desktop, Claude Code, Cowork) can discover them.
#
# Run this on each machine where you want the skills available.
# Only needs to run once per machine — Drive sync handles updates.

set -euo pipefail

# --- Configuration ---
# Adjust DRIVE_SKILLS to match your machine's Google Drive mount path.
# macOS default (Google Drive for Desktop):
DRIVE_SKILLS="$HOME/Library/CloudStorage/GoogleDrive-hello@snds.design/My Drive/Claude Workspace/02-skills"

# Claude Code skills directory
CLAUDE_CODE_SKILLS="$HOME/.claude/skills"

# Cowork skills directory (auto-detected)
COWORK_BASE="$HOME/Library/Application Support/Claude"

# --- Icon Font Network Skills ---
SKILLS=(
  "variable-icon-font-architect"
  "lead-vector-designer"
  "lead-icon-artist"
  "lead-technical-digital-artist"
  "math-bezier-spline-theory"
  "math-computational-geometry"
  "math-optical-optimization"
  "math-interpolation-designspace"
)

# --- Functions ---
link_skill() {
  local source="$1"
  local target_dir="$2"
  local skill_name=$(basename "$source")
  local target="$target_dir/$skill_name"

  if [ -L "$target" ]; then
    echo "  ↻ $skill_name (symlink exists, skipping)"
  elif [ -d "$target" ]; then
    echo "  ⚠ $skill_name (real directory exists — remove manually if stale)"
  else
    ln -s "$source" "$target"
    echo "  ✓ $skill_name"
  fi
}

# --- Claude Code ---
echo ""
echo "=== Claude Code ($CLAUDE_CODE_SKILLS) ==="
mkdir -p "$CLAUDE_CODE_SKILLS"
for skill in "${SKILLS[@]}"; do
  source="$DRIVE_SKILLS/$skill"
  if [ -d "$source" ]; then
    link_skill "$source" "$CLAUDE_CODE_SKILLS"
  else
    echo "  ✗ $skill (not found in Drive)"
  fi
done

# --- Cowork (find the skills-plugin directory) ---
echo ""
echo "=== Cowork ==="
# Cowork stores skills in a deeply nested UUID path. Find it.
COWORK_SKILLS=$(find "$COWORK_BASE" -type d -name "skills-plugin" 2>/dev/null | head -1)
if [ -n "$COWORK_SKILLS" ]; then
  echo "Found Cowork skills at: $COWORK_SKILLS"
  for skill in "${SKILLS[@]}"; do
    source="$DRIVE_SKILLS/$skill"
    if [ -d "$source" ]; then
      link_skill "$source" "$COWORK_SKILLS"
    else
      echo "  ✗ $skill (not found in Drive)"
    fi
  done
else
  echo "  Cowork skills directory not found — skipping."
  echo "  (Install Cowork and run this script again if needed.)"
fi

echo ""
echo "Done. Skills will be available in new Claude sessions."
echo "Drive sync keeps the content updated automatically."
