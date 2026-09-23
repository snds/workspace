#!/usr/bin/env bash
# cursor-sessionend — remind the agent to write a session fragment + update Live handoff.
# Fail-open. Cursor sessionEnd may not always await agent follow-up; keep the nudge short.
set -u
WS=""
for _c in "$(cat "$HOME/.claude/workspace-brain-path" 2>/dev/null | head -1)" \
          "$HOME/Projects/Workspace" "$HOME/Projects/workspace" "$HOME/projects/workspace"; do
  [ -n "$_c" ] && [ -f "$_c/AGENTS.md" ] && WS="$_c" && break
done
[ -n "$WS" ] || WS="$HOME/Projects/workspace"
cat >/dev/null 2>&1 || true
MSG="[ws-bootstrap/cursor-sessionend] Before yielding: (1) rewrite the active project's SESSION-STATE.md Live handoff atomically; (2) write a session fragment to $WS/06-context/sessions/<id>.md stamped Agent · Surface · Machine — do NOT append session-log.md directly; (3) run python3 $WS/09-tools/cursor-externalize.py so Cursor canvases are copied into the vault; (4) leave a clear next action."
python3 -c 'import json,sys;print(json.dumps({"additional_context":sys.argv[1]}))' "$MSG" 2>/dev/null || printf '{}\n'
