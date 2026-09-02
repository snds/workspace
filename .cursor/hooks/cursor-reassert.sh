#!/usr/bin/env bash
# cursor-reassert — Cursor preCompact / beforeSubmitPrompt companion.
# Injects a short continuity reminder so compaction / model-swap doesn't lose the baton.
# Fail-open: never block the agent.
set -u
WS=""
for _c in "$(cat "$HOME/.claude/workspace-brain-path" 2>/dev/null | head -1)" \
          "$HOME/Projects/Workspace" "$HOME/Projects/workspace" "$HOME/projects/workspace"; do
  [ -n "$_c" ] && [ -f "$_c/AGENTS.md" ] && WS="$_c" && break
done
[ -n "$WS" ] || WS="$HOME/Projects/workspace"
RULES="$(cat "$WS/00-bootstrap/dist/RULES.txt" 2>/dev/null | tr '\n' ' ')"
# Discard stdin (event payload); we only inject context.
cat >/dev/null 2>&1 || true
MSG="[ws-bootstrap/cursor-reassert] Re-anchor before continuing: read $WS/AGENTS.md if not loaded; refresh the active project's SESSION-STATE.md Live handoff; route skills via $WS/02-shared-references/trigger-routes.md or 03-skills/skills.registry.json. Standing rules: $RULES"
python3 -c 'import json,sys;print(json.dumps({"additional_context":sys.argv[1]}))' "$MSG" 2>/dev/null || printf '{}\n'
