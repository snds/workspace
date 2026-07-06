#!/usr/bin/env bash
# workspace-doctor v2. Modes: default report+repair · --quick (repairs only, <1s) ·
# --check (report only, exit 1 on drift) · --quiet · --ack · --ack-chat
set -u
WS="$HOME/Projects/workspace"; DIST="$WS/00-bootstrap/dist"
STATE="$HOME/.claude/ws-state"; mkdir -p "$STATE"; LOG="$STATE/audit.log"
# Seed the audit log at install so the canary can tell "just installed" from
# "hooks dead" (fresh-install false-positive found in live Phase-1 testing).
[ -f "$LOG" ] || echo "$(date +%Y-%m-%dT%H:%M:%S) INIT" > "$LOG"
QUICK=0; CHECK=0; QUIET=0; DRIFT=0; ALERTS=""
notify() { command -v osascript >/dev/null 2>&1 && osascript -e "display notification \"$1\" with title \"workspace-doctor\"" >/dev/null 2>&1; }
for a in "$@"; do case $a in
  --quick) QUICK=1;; --check) CHECK=1;; --quiet) QUIET=1;;
  --ack) echo "$(date +%Y-%m-%dT%H:%M:%S) ACK" >> "$LOG"; echo "acknowledged"; exit 0;;
  --ack-chat) shasum -a 256 "$DIST/BEACON.md" | cut -d' ' -f1 > "$STATE/chat-beacon.sha"; echo "chat surfaces marked current"; exit 0;;
esac; done
say() { [ "$QUIET" -eq 1 ] || echo "$@"; }
flag() { DRIFT=1; ALERTS="${ALERTS}${1}; "; say "$1"; }
sha() { shasum -a 256 "$1" 2>/dev/null | cut -d' ' -f1; }

if [ ! -f "$WS/AGENTS.md" ]; then
  notify "FATAL: workspace checkout missing at $WS"
  echo "FATAL: workspace checkout missing at $WS — run bootstrap.sh"; exit 1
fi

repair_file() { # $1=dist source  $2=target  $3=exec|plain — atomic, honest about failure
  [ -f "$1" ] || { flag "MISSING SOURCE: $1 (git pull the workspace)"; return; }
  [ -f "$2" ] && [ "$(sha "$1")" = "$(sha "$2")" ] && return
  if [ "$CHECK" -eq 1 ]; then flag "DRIFT: $2"; return; fi
  if ! mkdir -p "$(dirname "$2")" 2>/dev/null; then flag "REPAIR FAILED (mkdir): $2"; return; fi
  local TMP; TMP="$(dirname "$2")/.ws-tmp.$$"
  if ! cp "$1" "$TMP" 2>/dev/null; then rm -f "$TMP"; flag "REPAIR FAILED (cp): $2"; return; fi
  if [ "$3" = exec ]; then chmod +x "$TMP"; fi
  if mv -f "$TMP" "$2" 2>/dev/null; then DRIFT=1; say "REPAIRED: $2"; else rm -f "$TMP"; flag "REPAIR FAILED (mv): $2"; fi
}

# 1. Managed files (atomic mv fixes the self-overwrite race — L1 spawns me while running)
repair_file "$DIST/workspace-sessionstart.sh" "$HOME/.claude/hooks/workspace-sessionstart.sh" exec
repair_file "$DIST/workspace-reassert.sh"     "$HOME/.claude/hooks/workspace-reassert.sh"     exec
repair_file "$DIST/workspace-audit.sh"        "$HOME/.claude/hooks/workspace-audit.sh"        exec
repair_file "$DIST/cursor-sessionstart.sh"    "$HOME/.claude/hooks/cursor-sessionstart.sh"    exec
repair_file "$DIST/user-CLAUDE.md"            "$HOME/.claude/CLAUDE.md"                       plain
repair_file "$DIST/cursor-hooks.json"         "$HOME/.cursor/hooks.json"                      plain
PL="$HOME/Library/LaunchAgents/design.snds.workspace-doctor.plist"; PB="$(sha "$PL")"
repair_file "$DIST/launchd.plist" "$PL" plain
if [ "$(sha "$PL")" != "$PB" ] && [ "$CHECK" -eq 0 ]; then launchctl unload "$PL" 2>/dev/null; launchctl load "$PL" 2>/dev/null; fi

# 2. settings.json registrations (merge, never clobber; merger aborts on parse errors)
SJ="$HOME/.claude/settings.json"
if ! { grep -q workspace-sessionstart "$SJ" && grep -q workspace-reassert "$SJ" && grep -q workspace-audit "$SJ"; } 2>/dev/null; then
  if [ "$CHECK" -eq 1 ]; then flag "DRIFT: $SJ missing hook registrations"
  elif python3 "$WS/00-bootstrap/doctor/merge_settings.py" "$DIST/settings-user-fragment.json" "$SJ" 2>/dev/null; then
    DRIFT=1; say "REPAIRED: $SJ (merged fragment; backup written)"
  else flag "REPAIR FAILED: $SJ merge aborted (unparseable settings?) — fix by hand"; fi
fi
grep -q '"disableAllHooks"[[:space:]]*:[[:space:]]*true' "$SJ" 2>/dev/null && flag "ALERT: disableAllHooks=true — every hook layer is dead"

# 3. Plugin hook config
PLUG="$HOME/.claude/local-plugins/snds-local/snds"
[ -d "$PLUG" ] && repair_file "$DIST/plugin-hooks.json" "$PLUG/hooks/hooks.json" plain

# 4. Fossils stay dead
if [ -e "$HOME/Projects/.claude/hooks/dispatcher.py" ]; then
  if [ "$CHECK" -eq 1 ]; then flag "DRIFT: Drive-era fossil present"
  else rm -f "$HOME/Projects/.claude/hooks/dispatcher.py"; DRIFT=1; say "REPAIRED: removed fossil dispatcher.py"; fi
fi

if [ "$QUICK" -eq 0 ]; then
  # 5. Personal-repo beacons + discovery of unlisted repos
  while IFS= read -r repo; do
    case "$repo" in ''|'#'*) continue;; *"/c8"*) continue;; esac
    grep -q "WORKSPACE-BEACON" "$repo/CLAUDE.md" 2>/dev/null || flag "DRIFT: beacon missing in $repo/CLAUDE.md"
  done < "$DIST/beacon-repos.txt" 2>/dev/null
  for d in "$HOME/Projects"/*/; do d="${d%/}"
    case "$d" in "$WS"|*c8*) continue;; esac
    [ -d "$d/.git" ] || continue
    grep -qxF "$d" "$DIST/beacon-repos.txt" 2>/dev/null || say "NOTE: $d is a git repo not in beacon-repos.txt — add it (cloud-session coverage) or ignore"
  done

  # 6. CANARY — independent of the hook subsystem: sessions ran but audit log is silent?
  RECENT_TX=$(find "$HOME/.claude/projects" -name '*.jsonl' -mtime -2 2>/dev/null | head -1)
  if [ -n "$RECENT_TX" ] && [ -z "$(find "$LOG" -mtime -2 2>/dev/null)" ]; then
    flag "CANARY: sessions ran in the last 48h but the audit log is silent — hooks are NOT firing (disableAllHooks? harness update? ~/.claude wiped?)"
  fi
  M=$(awk '/ ACK$/{n=0} / MISS /{n++} END{print n+0}' "$LOG" 2>/dev/null)
  [ "${M:-0}" -gt 0 ] 2>/dev/null && say "AUDIT: $M un-acknowledged MISS(es) — inspect $LOG, then: workspace-doctor --ack"

  # 7. Chat-surface staleness: nag until Sean re-pastes and acks
  [ "$(sha "$DIST/BEACON.md")" != "$(cat "$STATE/chat-beacon.sha" 2>/dev/null)" ] && \
    flag "CHAT SURFACES STALE: BEACON.md changed — repaste into claude.ai preferences, Workspace project, Cursor User Rules, Perplexity Space, then: workspace-doctor --ack-chat"

  BEHIND=$(git -C "$WS" rev-list --count '@{u}..HEAD' 2>/dev/null); BEHIND=${BEHIND:-0}
  [ "$BEHIND" != "0" ] && say "SYNC: $BEHIND unpushed commit(s) — chat knowledge stale until push + Sync now"

  # 8. State hygiene (fixes marker accumulation; log rotation fixes eternal-NOTICE)
  find "$STATE" \( -name 'boot.*' -o -name 'count.*' \) -mtime +14 -exec rm -rf {} + 2>/dev/null
  [ -f "$LOG" ] && [ "$(wc -l < "$LOG" 2>/dev/null || echo 0)" -gt 500 ] && { tail -100 "$LOG" > "$LOG.tmp" && mv "$LOG.tmp" "$LOG"; }
fi

date +%Y-%m-%dT%H:%M:%S > "$STATE/doctor-last-run"
if [ "$DRIFT" -eq 0 ]; then say "workspace-doctor: all layers healthy."
else notify "$(printf '%.120s' "$ALERTS")"; fi
[ "$CHECK" -eq 1 ] && exit "$DRIFT"; exit 0
