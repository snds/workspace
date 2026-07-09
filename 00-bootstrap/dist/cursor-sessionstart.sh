#!/usr/bin/env bash
# ws-bootstrap/cursor v2 — sessionStart hook. Contract verified 2026-07-06 against
# cursor.com/docs/hooks: stdin JSON, stdout {"additional_context": "..."} injected
# into the conversation's initial system context. Fire-and-forget. User-global
# registration lives at ~/.cursor/hooks.json (doctor-managed).
WS="$HOME/Projects/workspace"
RULES="$(cat "$WS/00-bootstrap/dist/RULES.txt" 2>/dev/null | tr '\n' ' ')"
if [ -f "$WS/AGENTS.md" ]; then
  B=$(git -C "$WS" branch --show-current 2>/dev/null || echo '?')
  S=$(git -C "$WS" rev-parse --short HEAD 2>/dev/null || echo '?')
  CTX="[ws-bootstrap/cursor] Read $WS/AGENTS.md before any task. First-reply ritual: [workspace: LOADED · $B@$S · $(date +%Y-%m-%d) · via:cursor-hook]. Standing rules: $RULES"
else
  CTX="[ws-bootstrap/cursor] Workspace missing at $WS. Open with [workspace: UNREACHABLE · checkout missing]. Remote: github.com/snds/workspace. Rules: $RULES"
fi
python3 -c 'import json,sys;print(json.dumps({"additional_context":sys.argv[1]}))' "$CTX" 2>/dev/null || printf '{}\n'
