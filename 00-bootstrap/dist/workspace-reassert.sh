#!/usr/bin/env bash
# ws-reassert v2 — UserPromptSubmit hook. Silent on the happy path.
# State lives in ~/.claude/ws-state (survives TMPDIR purges — no false late-repairs).
set -u
# Resolve the workspace root (FX-14 — no hardcoded path): brain-path file first,
# then candidate list; AGENTS.md presence is the test.
WS=""
for _c in "$(cat "$HOME/.claude/workspace-brain-path" 2>/dev/null | head -1)" \
          "$HOME/Projects/Workspace" "$HOME/Projects/workspace" "$HOME/projects/workspace"; do
  [ -n "$_c" ] && [ -f "$_c/AGENTS.md" ] && WS="$_c" && break
done
[ -n "$WS" ] || WS="$HOME/Projects/workspace"
STATE="$HOME/.claude/ws-state"; mkdir -p "$STATE"
SID="$(cat 2>/dev/null | sed -n 's/.*"session_id"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -1)"
[ -n "$SID" ] || exit 0    # cannot identify the session -> fail open, never false-alarm
MARK="$STATE/boot.$SID"; CNT="$STATE/count.$SID"
RULES="$(cat "$WS/00-bootstrap/dist/RULES.txt" 2>/dev/null | tr '\n' ' ')"
if [ ! -f "$MARK" ]; then
  : > "$MARK"; echo 1 > "$CNT"
  echo "[ws-reassert] The workspace bootstrap hook did NOT run for this session. Unless the caller demands raw structured output: read $WS/AGENTS.md (or github.com/snds/workspace) before answering, and open your reply with [workspace: LOADED (late) · via:prompt-hook]. Standing rules in force now: $RULES"
  exit 0
fi
N=$(( $(cat "$CNT" 2>/dev/null || echo 0) + 1 )); echo "$N" > "$CNT"
[ $(( N % 15 )) -eq 0 ] && echo "[ws-reassert] Workspace rules at $WS remain in force: $RULES If compaction dropped context, re-read AGENTS.md."
exit 0
