#!/usr/bin/env bash
# ws-bootstrap/cursor v2 — emits {"continue":true,"additional_context":...}
WS="$HOME/Projects/workspace"
RULES="$(cat "$WS/00-bootstrap/dist/RULES.txt" 2>/dev/null | tr '\n' ' ')"
if [ -f "$WS/AGENTS.md" ]; then
  B=$(git -C "$WS" branch --show-current 2>/dev/null || echo '?')
  S=$(git -C "$WS" rev-parse --short HEAD 2>/dev/null || echo '?')
  CTX="[ws-bootstrap/cursor] Read $WS/AGENTS.md before any task. First-reply ritual: [workspace: LOADED · $B@$S · $(date +%Y-%m-%d) · via:cursor-hook]. Standing rules: $RULES"
else
  CTX="[ws-bootstrap/cursor] Workspace missing at $WS. Open with [workspace: UNREACHABLE · checkout missing]. Remote: github.com/snds/workspace. Rules: $RULES"
fi
python3 -c 'import json,sys;print(json.dumps({"continue":True,"additional_context":sys.argv[1]}))' "$CTX" 2>/dev/null || printf '{"continue": true}\n'
