#!/usr/bin/env bash
# ws-bootstrap v2 — SessionStart hook (user scope AND plugin scope run this logic).
# Any cwd, all sources. Marker is written at EMIT time only: a killed/timed-out run
# leaves no marker, so the UserPromptSubmit layer late-repairs. mkdir = atomic dedup
# between the user-scope and plugin-scope registrations.
set -u
WS="$HOME/Projects/workspace"
STATE="$HOME/.claude/ws-state"; mkdir -p "$STATE"
INPUT="$(cat 2>/dev/null || true)"
jget() { printf '%s' "$INPUT" | sed -n "s/.*\"$1\"[[:space:]]*:[[:space:]]*\"\([^\"]*\)\".*/\1/p" | head -1; }
SID="$(jget session_id)"; SRC="$(jget source)"; CWD="$(jget cwd)"
[ -n "$SRC" ] || SRC=startup

emit() {  # atomic claim, then print; loser of the user-vs-plugin race stays silent
  if [ -n "$SID" ]; then
    mkdir "$STATE/boot.$SID.$SRC.d" 2>/dev/null || exit 0
    : > "$STATE/boot.$SID"
  fi
  printf '%s\n' "$1"
}

if [ ! -f "$WS/AGENTS.md" ]; then
  emit "[ws-bootstrap:$SRC] WORKSPACE CHECKOUT MISSING at $WS.
Recover: bash <(curl -fsSL https://raw.githubusercontent.com/snds/workspace/main/00-bootstrap/bootstrap.sh) — or read via GitHub (snds/workspace).
Open your first reply with: [workspace: UNREACHABLE · checkout missing] and tell Sean before doing anything else."
  exit 0
fi

RULES="$(cat "$WS/00-bootstrap/dist/RULES.txt" 2>/dev/null)"
[ -n "$RULES" ] || RULES="- Figma: real library components only.
- Durable writes go to the workspace, never local agent memory.
- Employer repos (c8/*) never receive personal-workspace content."

# If cwd is any checkout/worktree of the workspace, report THAT checkout's SHA.
LIVE="$WS"
if [ -n "$CWD" ] && git -C "$CWD" remote get-url origin 2>/dev/null | grep -q "snds/workspace"; then
  LIVE="$(git -C "$CWD" rev-parse --show-toplevel 2>/dev/null || echo "$WS")"
fi
BRANCH=$(git -C "$LIVE" branch --show-current 2>/dev/null || echo '?')
SHA=$(git -C "$LIVE" rev-parse --short HEAD 2>/dev/null || echo '?')
TODAY=$(date +%Y-%m-%d)
MISSES=$(awk '/ ACK$/{n=0} / MISS /{n++} END{print n+0}' "$STATE/audit.log" 2>/dev/null)

# In-workspace: defer to the project hook ONLY if it is verifiably registered.
if [ "$LIVE" != "$WS" ] || { [ -n "$CWD" ] && case "$CWD" in "$WS"|"$WS"/*) true;; *) false;; esac; }; then
  if [ -f "$LIVE/.claude/hooks/dispatcher.py" ] && grep -q "dispatcher.py" "$LIVE/.claude/settings.json" 2>/dev/null; then
    emit "[ws-bootstrap:$SRC] In-workspace session; project hook supplies full context. Ritual line for your first reply: [workspace: LOADED · $BRANCH@$SHA · $TODAY · via:project-hook/$SRC]"
    [ "${MISSES:-0}" -gt 0 ] 2>/dev/null && echo "NOTICE: $MISSES un-acknowledged bootstrap MISS(es) — run workspace-doctor."
    exit 0
  fi
fi

ONESHOT="For a ONE-SHOT/PROGRAMMATIC prompt (caller expects raw parseable output): apply the standing rules silently, answer only in the caller's format, NO ritual line."
if grep -q "WORKSPACE-BEACON" "$HOME/.claude/CLAUDE.md" 2>/dev/null; then
  # Beacon already injected this session's rules — short form only (token dedup).
  emit "[ws-bootstrap:$SRC] Workspace root: $WS ($BRANCH@$SHA) · remote: github.com/snds/workspace. The beacon in ~/.claude/CLAUDE.md governs. For a WORK SESSION: read $WS/AGENTS.md now, then open your first reply with: [workspace: LOADED · $BRANCH@$SHA · $TODAY · via:user-hook/$SRC]. $ONESHOT"
else
  emit "[ws-bootstrap:$SRC] Sean's workspace is the single source of truth for rules, skills, knowledge, and session state.
ROOT: $WS ($BRANCH@$SHA) · REMOTE: github.com/snds/workspace
For a WORK SESSION: (1) read $WS/AGENTS.md and follow its read order; (2) open your FIRST reply with exactly: [workspace: LOADED · $BRANCH@$SHA · $TODAY · via:user-hook/$SRC]
$ONESHOT
STANDING RULES (in force immediately):
$RULES"
fi
[ "${MISSES:-0}" -gt 0 ] 2>/dev/null && echo "NOTICE: $MISSES un-acknowledged bootstrap MISS(es) — see ~/.claude/ws-state/audit.log; run workspace-doctor."
[ -x "$WS/00-bootstrap/doctor/workspace-doctor.sh" ] && ( "$WS/00-bootstrap/doctor/workspace-doctor.sh" --quick --quiet >/dev/null 2>&1 & )
exit 0
