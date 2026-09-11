#!/usr/bin/env bash
# ws-bootstrap/cursor — beforeSubmitPrompt. Injects Layer-0 trigger-routes from the
# portable workspace even when CWD is an employer repo (cds, centric-ui). Fail-open.
# Doctor installs this to ~/.claude/hooks/cursor-prompt-route.sh; user-global
# ~/.cursor/hooks.json registers it on beforeSubmitPrompt.
set -u
WS=""
for _c in "$(cat "$HOME/.claude/workspace-brain-path" 2>/dev/null | head -1)" \
          "$HOME/Projects/Workspace" "$HOME/Projects/workspace" "$HOME/projects/workspace"; do
  [ -n "$_c" ] && [ -f "$_c/AGENTS.md" ] && WS="$_c" && break
done
[ -n "$WS" ] || { echo '{}'; exit 0; }
[ -f "$WS/09-tools/cursor-prompt-route.py" ] || { echo '{}'; exit 0; }
exec python3 "$WS/09-tools/cursor-prompt-route.py"
