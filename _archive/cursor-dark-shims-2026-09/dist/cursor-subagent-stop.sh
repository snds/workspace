#!/usr/bin/env bash
# cursor-subagent-stop — after a Task/subagent finishes, remind the parent to refresh the baton.
# Returns followup_message when supported; fail-open otherwise.
set -u
INPUT="$(cat 2>/dev/null || true)"
WS=""
for _c in "$(cat "$HOME/.claude/workspace-brain-path" 2>/dev/null | head -1)" \
          "$HOME/Projects/Workspace" "$HOME/Projects/workspace" "$HOME/projects/workspace"; do
  [ -n "$_c" ] && [ -f "$_c/AGENTS.md" ] && WS="$_c" && break
done
[ -n "$WS" ] || WS="$HOME/Projects/workspace"
MSG="Subagent finished. Re-read the active project's SESSION-STATE.md Live handoff; fold useful findings into it (or a 06-context/sessions/ fragment). Concurrent agents must not append session-log.md directly. Stamp Agent · Surface · Machine."
# Prefer followup_message (subagentStop); also emit additional_context for hosts that accept it.
python3 -c 'import json,sys;print(json.dumps({"followup_message":sys.argv[1],"additional_context":sys.argv[1]}))' "$MSG" 2>/dev/null || printf '{}\n'
