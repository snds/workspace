#!/usr/bin/env bash
# ws-bootstrap/cursor v3 — sessionStart injects session-status.py (notices + all
# projects + pending). Contract verified against cursor.com/docs/hooks: discard
# stdin JSON; stdout {"additional_context": "..."} into initial system context.
# User-global registration lives at ~/.cursor/hooks.json (doctor copies this file).
set -u
cat >/dev/null || true
WS=""
for _c in "$(cat "$HOME/.claude/workspace-brain-path" 2>/dev/null | head -1)" \
          "$HOME/Projects/Workspace" "$HOME/Projects/workspace" "$HOME/projects/workspace"; do
  [ -n "$_c" ] && [ -f "$_c/AGENTS.md" ] && WS="$_c" && break
done
[ -n "$WS" ] || WS="$HOME/Projects/workspace"
RULES="$(tr '\n' ' ' < "$WS/00-bootstrap/dist/RULES.txt" 2>/dev/null || true)"

emit_json() {
  python3 -c 'import json,sys; print(json.dumps({"additional_context": sys.stdin.read()}))' 2>/dev/null || printf '{}\n'
}

fallback() {
  if [ -f "$WS/AGENTS.md" ]; then
    B=$(git -C "$WS" branch --show-current 2>/dev/null || echo '?')
    S=$(git -C "$WS" rev-parse --short HEAD 2>/dev/null || echo '?')
    printf '%s\n' "[ws-bootstrap/cursor] Read $WS/AGENTS.md before any task. First-reply ritual: [workspace: LOADED · $B@$S · $(date +%Y-%m-%d) · via:cursor-hook]. Standing rules: $RULES"
  else
    printf '%s\n' "[ws-bootstrap/cursor] Workspace missing at $WS. Open with [workspace: UNREACHABLE · checkout missing]. Remote: github.com/snds/workspace. Rules: $RULES"
  fi
}

if [ -f "$WS/09-tools/session-status.py" ]; then
  CARD=$(python3 "$WS/09-tools/session-status.py" --surface Cursor --via cursor-hook/startup 2>/dev/null || true)
  if [ -n "${CARD:-}" ]; then
    printf '%s\n' "Emit this session-start card as your first reply in a NEW session. Do not shrink Active projects. Skip on continuations and Task workers / structured-output.

${CARD}" | emit_json
    exit 0
  fi
fi

fallback | emit_json
