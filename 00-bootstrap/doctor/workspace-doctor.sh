#!/usr/bin/env bash
# workspace-doctor v2. Modes: default report+repair · --quick (repairs only, <1s) ·
# --check (report only, exit 1 on drift) · --quiet · --ack · --ack-chat
set -u
# Resolve the workspace root (FX-14 — no hardcoded path): brain-path file first,
# then candidate list; AGENTS.md presence is the test.
WS=""
for _c in "$(cat "$HOME/.claude/workspace-brain-path" 2>/dev/null | head -1)" \
          "$HOME/Projects/Workspace" "$HOME/Projects/workspace" "$HOME/projects/workspace"; do
  [ -n "$_c" ] && [ -f "$_c/AGENTS.md" ] && WS="$_c" && break
done
[ -n "$WS" ] || WS="$HOME/Projects/workspace"
DIST="$WS/00-bootstrap/dist"
# Self-heal the pointer so every other consumer resolves the same root.
# mkdir FIRST: on a fresh machine ~/.claude may not exist yet, and the brain-path
# redirect would fail (the shell's own redirect error isn't even caught by 2>/dev/null),
# leaving the pointer absent — which breaks the launchd job installed in the same run.
STATE="$HOME/.claude/ws-state"; mkdir -p "$STATE"; LOG="$STATE/audit.log"
printf '%s\n' "$WS" > "$HOME/.claude/workspace-brain-path" 2>/dev/null
# Seed the audit log at install so the canary can tell "just installed" from
# "hooks dead" (fresh-install false-positive found in live Phase-1 testing).
[ -f "$LOG" ] || echo "$(date +%Y-%m-%dT%H:%M:%S) INIT" > "$LOG"
QUICK=0; CHECK=0; QUIET=0; DRIFT=0; ALERTS=""
notify() { command -v osascript >/dev/null 2>&1 && osascript -e "display notification \"$1\" with title \"workspace-doctor\"" >/dev/null 2>&1; }
for a in "$@"; do case $a in
  --quick) QUICK=1;; --check) CHECK=1;; --quiet) QUIET=1;;
  # The ACK boundary lives in its OWN state file, not as a log line: log rotation
  # (below) discards old lines and used to destroy the ACK marker with them, making
  # the MISS count jump arbitrarily (observed 2026-07-19: 36 -> 19 on rotation).
  # The log line is kept purely as a human-readable audit trail.
  --ack) _ts=$(date +%Y-%m-%dT%H:%M:%S); echo "$_ts ACK" >> "$LOG"
         printf '%s\n' "$_ts" > "$STATE/ack-mark"; echo "acknowledged"; exit 0;;
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
  # Content hash ALONE is not health: a hook with correct bytes but no +x is dead
  # ("permission denied") while hashing identical. Restores from backup, rsync
  # without -p, unzip and Time Machine all strip the exec bit. Test it explicitly.
  if [ -f "$2" ] && [ "$(sha "$1")" = "$(sha "$2")" ]; then
    if [ "$3" = exec ] && [ ! -x "$2" ]; then
      if [ "$CHECK" -eq 1 ]; then flag "DRIFT: $2 not executable"; return; fi
      if chmod +x "$2" 2>/dev/null; then DRIFT=1; say "REPAIRED: $2 (restored +x)"
      else flag "REPAIR FAILED (chmod): $2"; fi
    fi
    return
  fi
  if [ "$CHECK" -eq 1 ]; then flag "DRIFT: $2"; return; fi
  if ! mkdir -p "$(dirname "$2")" 2>/dev/null; then flag "REPAIR FAILED (mkdir): $2"; return; fi
  local TMP; TMP="$(dirname "$2")/.ws-tmp.$$"
  if ! cp "$1" "$TMP" 2>/dev/null; then rm -f "$TMP"; flag "REPAIR FAILED (cp): $2"; return; fi
  if [ "$3" = exec ]; then chmod +x "$TMP"; fi
  # Keep one generation of whatever we're about to replace. ~/.claude/CLAUDE.md and
  # ~/.cursor/hooks.json are files a human edits by hand; without this, a hand edit
  # is silently reverted within 4h with no way back (and --quiet hides the notice).
  [ -f "$2" ] && cp -p "$2" "$2.bak" 2>/dev/null
  if mv -f "$TMP" "$2" 2>/dev/null; then DRIFT=1; say "REPAIRED: $2 (previous saved to $2.bak)"; else rm -f "$TMP"; flag "REPAIR FAILED (mv): $2"; fi
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
# Liveness, not just file content: the job can be booted-out (manual bootout, failed
# login, OS upgrade, LaunchAgents quarantine) while the plist on disk still matches
# dist. Reload gated on sha alone would never notice, and the doctor's own 4-hour
# heartbeat would be dead while every layer reported healthy.
if [ -f "$PL" ] && ! launchctl list 2>/dev/null | grep -q 'design\.snds\.workspace-doctor'; then
  if [ "$CHECK" -eq 1 ]; then flag "DRIFT: launchd job not loaded — doctor timer is dead"
  elif launchctl load "$PL" 2>/dev/null; then DRIFT=1; say "REPAIRED: reloaded launchd job"
  else flag "REPAIR FAILED: launchd job not loaded and load failed"; fi
fi

# 2. settings.json registrations (merge, never clobber; merger aborts on parse errors)
SJ="$HOME/.claude/settings.json"
if ! { grep -q workspace-sessionstart "$SJ" && grep -q workspace-reassert "$SJ" && grep -q workspace-audit "$SJ"; } 2>/dev/null; then
  if [ "$CHECK" -eq 1 ]; then flag "DRIFT: $SJ missing hook registrations"
  else
    python3 "$WS/00-bootstrap/doctor/merge_settings.py" "$DIST/settings-user-fragment.json" "$SJ" 2>/dev/null; _rc=$?
    case $_rc in
      0) DRIFT=1; say "REPAIRED: $SJ (merged fragment; backup written)" ;;
      # Exit 3 = the merge changed nothing, yet the guard above still says the
      # registrations are absent. Re-running will never fix it; say so instead of
      # claiming a repair every run forever.
      3) flag "REPAIR FAILED: $SJ — merge was a no-op but hook registrations are still missing (is \"hooks\" a dict?) — fix by hand" ;;
      *) flag "REPAIR FAILED: $SJ merge aborted (unparseable settings?) — fix by hand" ;;
    esac
  fi
fi
# Check EVERY settings layer, not just the user one. A temporary "turn hooks off"
# most often lands in settings.local.json or the project file — precisely where the
# old single-file check was blind, and precisely what this alert exists to catch.
for _s in "$SJ" "$HOME/.claude/settings.local.json" "$WS/.claude/settings.json" "$WS/.claude/settings.local.json"; do
  grep -q '"disableAllHooks"[[:space:]]*:[[:space:]]*true' "$_s" 2>/dev/null && flag "ALERT: disableAllHooks=true in $_s — every hook layer is dead"
done

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
  # A missing list silently skipped the whole loop — beacon drift across every
  # personal repo would go unreported while the run still ended "all layers healthy".
  [ -f "$DIST/beacon-repos.txt" ] || flag "MISSING SOURCE: $DIST/beacon-repos.txt — beacon coverage unchecked"
  while IFS= read -r repo; do
    case "$repo" in ''|'#'*) continue;; *"/c8"*) continue;; esac
    [ -d "$repo" ] || continue   # listed on another machine; not present here
    grep -q "WORKSPACE-BEACON" "$repo/CLAUDE.md" 2>/dev/null || flag "DRIFT: beacon missing in $repo/CLAUDE.md — run 00-bootstrap/beacon-enroll.sh $repo"
  done < "$DIST/beacon-repos.txt" 2>/dev/null
  for d in "$HOME/Projects"/*/; do d="${d%/}"
    case "$d" in "$WS"|*c8*) continue;; esac
    [ -d "$d/.git" ] || continue
    grep -q "^$d" "$DIST/beacon-repos.ignore.txt" 2>/dev/null && continue   # deliberate skip, recorded
    grep -qxF "$d" "$DIST/beacon-repos.txt" 2>/dev/null || say "NOTE: $d is a git repo not enrolled for cloud beacons — run 00-bootstrap/beacon-enroll.sh --sweep --apply (classifies personal vs employer itself)"
  done

  # 6. CANARY — independent of the hook subsystem: sessions ran but audit log is silent?
  RECENT_TX=$(find "$HOME/.claude/projects" -name '*.jsonl' -mtime -2 2>/dev/null | head -1)
  if [ -n "$RECENT_TX" ] && [ -z "$(find "$LOG" -mtime -2 2>/dev/null)" ]; then
    flag "CANARY: sessions ran in the last 48h but the audit log is silent — hooks are NOT firing (disableAllHooks? harness update? ~/.claude wiped?)"
  fi
  # Count MISSes newer than the durable ACK mark (rotation-proof). No mark yet =
  # count everything retained, which is the conservative pre-ACK behaviour.
  M=$(awk -v m="$(cat "$STATE/ack-mark" 2>/dev/null)" '/ MISS /{ if ($1 "" > m "") n++ } END{print n+0}' "$LOG" 2>/dev/null)
  [ "${M:-0}" -gt 0 ] 2>/dev/null && say "AUDIT: $M un-acknowledged MISS(es) — inspect $LOG, then: workspace-doctor --ack"

  # 7. Chat-surface staleness: nag until Sean re-pastes and acks
  [ "$(sha "$DIST/BEACON.md")" != "$(cat "$STATE/chat-beacon.sha" 2>/dev/null)" ] && \
    flag "CHAT SURFACES STALE: BEACON.md changed — repaste into claude.ai preferences, Workspace project, Cursor User Rules, Perplexity Space, then: workspace-doctor --ack-chat"

  BEHIND=$(git -C "$WS" rev-list --count '@{u}..HEAD' 2>/dev/null); BEHIND=${BEHIND:-0}
  [ "$BEHIND" != "0" ] && say "SYNC: $BEHIND unpushed commit(s) — chat knowledge stale until push + Sync now"

  # 8. State hygiene (fixes marker accumulation; log rotation fixes eternal-NOTICE)
  find "$STATE" \( -name 'boot.*' -o -name 'count.*' -o -name 'ok.*' -o -name 'scan.*' -o -name 'nag.*' \) -mtime +14 -exec rm -rf {} + 2>/dev/null
  # Rotation must NOT refresh the log mtime: the canary at step 6 reads that mtime
  # to decide "sessions ran but the audit is silent". A rotating run would give the
  # log a fresh timestamp and suppress the hooks-are-dead alarm for a further 48h.
  # -r copies the pre-rotation mtime back onto the rotated file.
  if [ -f "$LOG" ] && [ "$(wc -l < "$LOG" 2>/dev/null || echo 0)" -gt 500 ]; then
    tail -100 "$LOG" > "$LOG.tmp" && touch -r "$LOG" "$LOG.tmp" 2>/dev/null && mv "$LOG.tmp" "$LOG"
  fi
fi

date +%Y-%m-%dT%H:%M:%S > "$STATE/doctor-last-run"
if [ "$DRIFT" -eq 0 ]; then say "workspace-doctor: all layers healthy."
# ALERTS is only appended by flag(); a clean REPAIR sets DRIFT without it, which
# used to fire a blank macOS notification with no explanation.
elif [ -n "$ALERTS" ]; then notify "$(printf '%.120s' "$ALERTS")"
else say "workspace-doctor: repairs applied, no alerts."; fi
[ "$CHECK" -eq 1 ] && exit "$DRIFT"; exit 0
