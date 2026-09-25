#!/bin/sh
# ws-hook-repo.sh — repo-relative wall-guard entry (H15) for committed shims. A cloud VM has no
# $HOME/.config/snds-workspace wrapper, so a committed hook calls this file by its repo path. It finds
# the repo from its own location (fallback: $CURSOR_PROJECT_DIR, then $CLAUDE_PROJECT_DIR) and runs the
# guard from the same checkout. Fails open: no python3 or no guard gives no decision (exit 0).
D="$(CDPATH= cd -- "$(dirname -- "$0")" 2>/dev/null && pwd)"
if [ -z "$D" ] || [ ! -f "$D/wall_guard.py" ]; then
  P="${CURSOR_PROJECT_DIR:-${CLAUDE_PROJECT_DIR:-}}"
  [ -n "$P" ] && D="$P/09-tools"
fi
command -v python3 >/dev/null 2>&1 || exit 0
[ -n "$D" ] && [ -f "$D/wall_guard.py" ] || exit 0
exec python3 "$D/wall_guard.py" hook "$@"
