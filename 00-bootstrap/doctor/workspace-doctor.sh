#!/usr/bin/env bash
# workspace-doctor v3 (H24: report-only unattended doctor). Modes:
#   default    report; heal only HEAL-class items
#   --quick    as default, skipping sections 5-8; never scan, audit or install (<1s)
#   --quiet    launchd mode: may also write telemetry/install-state.json and run the
#              PINNED profile_resolve scan --report (only when telemetry/ exists)
#   --check    report only; writes nothing; exit 1 on drift
#   --ack · --ack-chat · --no-launchctl (no launchctl/osascript; automatic when $HOME is
#              not the passwd home)
#   --install-<name>[=ARG] / --uninstall-<name>[=ARG] [--probe]
#              exec installers.py (human-run, TTY + human verdict, diff + y/N, backups)
#   --install-claude-overlay-retire-env   D-W1-4: drop the overlay from ~/.claude/settings.json env
#              (refused until a live Claude-shell probe records WS_OVERLAY_CHANNEL)
# HEAL class (the only unattended writes): ~/.claude/hooks/workspace-{sessionstart,
# reassert,audit}.sh, ~/.claude/CLAUDE.md, ~/.claude/workspace-brain-path, ~/.claude/ws-state/.
# Everything else the doctor looks at is REPORT class and names the installer to run.
set -u
# Resolve the workspace root (FX-14 — no hardcoded path): brain-path file first,
# then candidate list; AGENTS.md presence is the test.
WS=""
for _c in "$(cat "$HOME/.claude/workspace-brain-path" 2>/dev/null | head -1)" \
          "$HOME/Projects/Workspace" "$HOME/Projects/workspace" "$HOME/projects/workspace"; do
  [ -n "$_c" ] && [ -f "$_c/AGENTS.md" ] && WS="$_c" && break
done
[ -n "$WS" ] || WS="$HOME/Projects/workspace"
# A case-insensitive volume accepts any spelling; keep the on-disk one (a case change only, never a
# symlink target), so the pointer and the path compares below agree with git and the declared brain.
_p="$(cd "$WS" 2>/dev/null && { /bin/pwd -P 2>/dev/null || pwd -P; })"   # getcwd: bash's builtin keeps the typed case
[ -n "$_p" ] && [ "$(printf '%s' "$_p" | tr '[:upper:]' '[:lower:]')" = "$(printf '%s' "$WS" | tr '[:upper:]' '[:lower:]')" ] && WS="$_p"
DIST="$WS/00-bootstrap/dist"
DOC="$WS/00-bootstrap/doctor"
STATE="$HOME/.claude/ws-state"; LOG="$STATE/audit.log"
CFG="$HOME/.config/snds-workspace"; TEL="$CFG/telemetry"; LIBC="$CFG/lib/current"
QUICK=0; CHECK=0; QUIET=0; NOLC=0; DRIFT=0; ALERTS=""; INST=""; INST_ARGS=()
for a in "$@"; do case $a in
  --quick) QUICK=1;; --check) CHECK=1;; --quiet) QUIET=1;; --no-launchctl) NOLC=1;;
  --install-*|--uninstall-*)
    [ -n "$INST" ] && { echo "workspace-doctor: one installer per run" >&2; exit 2; }
    INST="$a";;
  --probe) INST_ARGS+=("--probe");;
esac; done

# Installers: explicit, human-run, one per invocation. --quick never runs one (it is the
# SessionStart path); --check writes nothing. The shell reads only the exit code.
if [ -n "$INST" ]; then
  if [ "$QUICK" -eq 1 ]; then
    [ "$QUIET" -eq 1 ] || echo "NOTE: installers never run under --quick ($INST ignored)"
  elif [ "$CHECK" -eq 1 ]; then
    echo "workspace-doctor: --check writes nothing; run $INST on its own" >&2; exit 2
  else
    _act=install; _rest="${INST#--install-}"
    case "$INST" in --uninstall-*) _act=uninstall; _rest="${INST#--uninstall-}";; esac
    exec python3 "$DOC/installers.py" "$_act" "$_rest" ${INST_ARGS[@]+"${INST_ARGS[@]}"}
  fi
fi

# launchctl and osascript only ever run for the passwd home (never for a temp HOME).
PWHOME="$(python3 -c 'import os,pwd;print(pwd.getpwuid(os.getuid()).pw_dir)' 2>/dev/null)"
[ -n "$PWHOME" ] && [ "${HOME%/}" = "${PWHOME%/}" ] || NOLC=1

for a in "$@"; do case $a in
  # The ACK boundary lives in its OWN state file, not as a log line: log rotation
  # (below) discards old lines and used to destroy the ACK marker with them, making
  # the MISS count jump arbitrarily (observed 2026-07-19: 36 -> 19 on rotation).
  # The log line is kept purely as a human-readable audit trail.
  --ack) mkdir -p "$STATE"; _ts=$(date +%Y-%m-%dT%H:%M:%S); echo "$_ts ACK" >> "$LOG"
         printf '%s\n' "$_ts" > "$STATE/ack-mark"; echo "acknowledged"; exit 0;;
  --ack-chat) mkdir -p "$STATE"; cat "$DIST/BEACON.md" "$DIST/cursor-user-rules.txt" 2>/dev/null | shasum -a 256 | cut -d' ' -f1 > "$STATE/chat-beacon.sha"; echo "chat surfaces marked current"; exit 0;;
esac; done

notify() { [ "$NOLC" -eq 1 ] && return 0; command -v osascript >/dev/null 2>&1 && osascript -e "display notification \"$1\" with title \"workspace-doctor\"" >/dev/null 2>&1; }
say() { [ "$QUIET" -eq 1 ] || echo "$@"; }
flag() { DRIFT=1; ALERTS="${ALERTS}${1}; "; say "$1"; }
note() { say "NOTE: $1"; }
sha() { shasum -a 256 "$1" 2>/dev/null | cut -d' ' -f1; }

if [ ! -f "$WS/AGENTS.md" ]; then
  notify "FATAL: workspace checkout missing at $WS"
  echo "FATAL: workspace checkout missing at $WS — run bootstrap.sh"; exit 1
fi

# HEAL: the pointer and state dir, so every other consumer resolves the same root.
# mkdir FIRST: on a fresh machine ~/.claude may not exist yet, and the brain-path
# redirect would fail (the shell's own redirect error isn't even caught by 2>/dev/null).
if [ "$CHECK" -eq 0 ]; then
  mkdir -p "$STATE"
  printf '%s\n' "$WS" > "$HOME/.claude/workspace-brain-path" 2>/dev/null
  # Seed the audit log at install so the canary can tell "just installed" from
  # "hooks dead" (fresh-install false-positive found in live Phase-1 testing).
  [ -f "$LOG" ] || echo "$(date +%Y-%m-%dT%H:%M:%S) INIT" > "$LOG"
fi

heal_file() { # $1=dist source  $2=target  $3=exec|plain — HEAL class only; atomic
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
  # Keep one generation of whatever we're about to replace. ~/.claude/CLAUDE.md is a
  # file a human edits by hand; without this, a hand edit is silently reverted.
  [ -f "$2" ] && cp -p "$2" "$2.bak" 2>/dev/null
  if mv -f "$TMP" "$2" 2>/dev/null; then DRIFT=1; say "REPAIRED: $2 (previous saved to $2.bak)"; else rm -f "$TMP"; flag "REPAIR FAILED (mv): $2"; fi
}

same_json() { # $1=dist json  $2=installed json: equal after `~/` expansion (0 same, 1 differs, 2 unreadable)
  python3 - "$1" "$2" <<'PY' 2>/dev/null
import json, os, sys
def ex(o):
    if isinstance(o, dict): return {k: ex(v) for k, v in o.items()}
    if isinstance(o, list): return [ex(v) for v in o]
    if isinstance(o, str) and o.startswith("~/"): return os.path.join(os.environ["HOME"], o[2:])
    return o
try:
    a, b = (json.load(open(p)) for p in sys.argv[1:3])
except (OSError, ValueError):
    sys.exit(2)
sys.exit(0 if ex(a) == b or a == b else 1)
PY
}

report_file() { # $1=dist source  $2=installed target  $3=installer flag  [$4=json] — REPORT class: never writes
  [ -f "$1" ] || { note "no dist source $1 (nothing to compare)"; return; }
  [ -f "$2" ] || { note "$2 not installed — to install: workspace-doctor.sh $3"; return; }
  if [ "${4:-}" = json ]; then same_json "$1" "$2"; _r=$?; else cmp -s "$1" "$2"; _r=$?; fi
  [ "$_r" -eq 0 ] || flag "DRIFT: $2 differs from dist — review, then run workspace-doctor.sh $3"
}

# 1. HEAL class: Claude-only context injectors (they only print context; atomic mv fixes
#    the self-overwrite race — L1 spawns me while running).
heal_file "$DIST/workspace-sessionstart.sh" "$HOME/.claude/hooks/workspace-sessionstart.sh" exec
heal_file "$DIST/workspace-reassert.sh"     "$HOME/.claude/hooks/workspace-reassert.sh"     exec
heal_file "$DIST/workspace-audit.sh"        "$HOME/.claude/hooks/workspace-audit.sh"        exec
heal_file "$DIST/user-CLAUDE.md"            "$HOME/.claude/CLAUDE.md"                       plain

# 1b. REPORT class: anything that runs in other hosts or employer cwds is installed only
#     by a human (installers.py). The doctor compares and names the installer.
[ -f "$DIST/cursor-sessionstart.sh" ] && \
  report_file "$DIST/cursor-sessionstart.sh" "$HOME/.claude/hooks/cursor-sessionstart.sh" "--install-shims=cursor"
report_file "$DIST/cursor-hooks.json" "$HOME/.cursor/hooks.json" "--install-shims=cursor" json
# H6 per-family beacons: the Codex user beacon and the machine-local ~/Projects pointer.
[ -d "$HOME/.codex" ] && report_file "$DIST/codex-AGENTS.md" "$HOME/.codex/AGENTS.md" "--install-shims=codex"
[ -d "$HOME/Projects" ] && report_file "$DIST/projects-AGENTS.md" "$HOME/Projects/AGENTS.md" "--install-projects-pointer"
for _r in cursor-prompt-route cursor-reassert cursor-sessionend cursor-subagent-stop; do
  [ -f "$HOME/.claude/hooks/$_r.sh" ] && note "retired script still installed: ~/.claude/hooks/$_r.sh — run workspace-doctor.sh --uninstall-shims=cursor"
done
PL="$HOME/Library/LaunchAgents/design.snds.workspace-doctor.plist"
if [ -f "$PL" ]; then
  report_file "$DIST/launchd.plist" "$PL" "--install-launchd"
  # Liveness, not just file content: the job can be booted-out while the plist matches.
  if [ "$NOLC" -eq 0 ] && ! launchctl list 2>/dev/null | grep -q 'design\.snds\.workspace-doctor'; then
    note "launchd job not loaded — doctor timer is dead; run workspace-doctor.sh --install-launchd"
  fi
else
  note "launchd job not installed — to install: workspace-doctor.sh --install-launchd"
fi

# 2. settings.json registrations and the Claude overlay (REPORT; installed only by
#    --install-claude-overlay and retired from settings env only by --install-claude-overlay-retire-env).
SJ="$HOME/.claude/settings.json"
if ! { grep -q workspace-sessionstart "$SJ" && grep -q workspace-reassert "$SJ" && grep -q workspace-audit "$SJ"; } 2>/dev/null; then
  flag "DRIFT: $SJ missing hook registrations — run workspace-doctor.sh --install-claude-overlay"
fi
# Claude surfaces are personal-only; see 06-context/memory/feedback-credential-scoping.md.
INC="$CFG/git/claude-identity.inc"
cmp -s "$DIST/git/claude-identity.inc" "$INC" 2>/dev/null || \
  flag "DRIFT: $INC missing or differs from dist — run workspace-doctor.sh --install-claude-overlay"
GHC="$CFG/gh-claude"
for _f in hosts.yml config.yml; do
  cmp -s "$DIST/gh-claude/$_f" "$GHC/$_f" 2>/dev/null || \
    flag "DRIFT: $GHC/$_f missing or differs from dist — run workspace-doctor.sh --install-claude-overlay"
done
if [ "$CHECK" -eq 1 ] && ! GH_CONFIG_DIR="$GHC" gh auth status >/dev/null 2>&1; then
  flag "NOTE: Claude gh config has no usable snds login on this machine — run: gh auth login (as snds), then gh auth switch back to this device's default account"
fi
# D-W1-4: the overlay has two channels. The env-file channel (claude-overlay.env, copied into Claude
# Code's session env file by the `ws-hook env-file` SessionStart entry) is Claude-only; the old settings
# `env` block also reaches any host that imports Claude's settings env. Either channel is healthy; both
# means the settings env is waiting to be retired (only after a live probe proves the env file).
ENVF="$CFG/claude-overlay.env"
_old=0; { grep -q '"GIT_CONFIG_KEY_0"' "$SJ" || grep -q '"GIT_AUTHOR_EMAIL"' "$SJ"; } 2>/dev/null && _old=1
if [ -f "$ENVF" ]; then
  cmp -s "$DIST/claude-overlay.env" "$ENVF" 2>/dev/null || \
    flag "DRIFT: $ENVF differs from dist — run workspace-doctor.sh --install-claude-overlay"
  grep -q 'ws-hook env-file' "$SJ" 2>/dev/null || \
    flag "DRIFT: $SJ has no ws-hook env-file SessionStart entry, so the overlay never reaches Claude's shell — run workspace-doctor.sh --install-claude-overlay"
  [ "$_old" -eq 1 ] && note "retire pending: $SJ still carries the overlay env (old channel); once a Claude shell probe records WS_OVERLAY_CHANNEL (ws_hook.py probe-env --host claude-code --record), run workspace-doctor.sh --install-claude-overlay-retire-env"
elif [ "$_old" -eq 0 ]; then
  flag "DRIFT: $SJ missing the Claude identity env overlay, and the env-file channel is not installed — run workspace-doctor.sh --install-claude-overlay"
else
  note "the Claude overlay still rides the settings env, which other hosts can import (D4) — install the env-file channel: workspace-doctor.sh --install-claude-overlay"
  _v="$(sed -n "s/^export WS_CLAUDE_OVERLAY='\(.*\)'\$/\1/p" "$DIST/claude-overlay.env" 2>/dev/null | head -1)"
  if ! grep -q "\"WS_CLAUDE_OVERLAY\": \"${_v:-v4}\"" "$SJ" 2>/dev/null || grep -q '"GIT_AUTHOR_EMAIL"' "$SJ" 2>/dev/null; then
    flag "DRIFT: $SJ carries an outdated Claude identity overlay — run workspace-doctor.sh --install-claude-overlay, live-probe a new Claude shell, then --install-claude-overlay-retire-env"
  fi
  if [ "$CHECK" -eq 1 ]; then
    # Exact comparison of the settings overlay env against the dist overlay (the env file without its
    # channel marker, rendered for this home as the old installer wrote it).
    _d="$(python3 - "$DIST/claude-overlay.env" "$SJ" "$DOC" <<'PY' 2>/dev/null
import json, re, sys
sys.path.insert(0, sys.argv[3])
import merge_settings as ms
want = {}
for ln in open(sys.argv[1], encoding="utf-8").read().splitlines():
    m = re.match(r"^export ([A-Z][A-Z0-9_]*)='((?:[^']|'\\'')*)'$", ln)
    if m:
        want[m.group(1)] = m.group(2).replace("'\\''", "'")
want.pop("WS_OVERLAY_CHANNEL", None)
want = ms.expand_env_home({"env": want})["env"]
got = json.load(open(sys.argv[2], encoding="utf-8")).get("env") or {}
have = {k: v for k, v in got.items() if ms.is_managed_env(k)}
diff = sorted(k for k in set(want) | set(have) if want.get(k) != have.get(k))
print(" ".join(diff[:20]))
sys.exit(1 if diff else 0)
PY
)"; _rc=$?
    case $_rc in
      0) : ;;
      1) flag "DRIFT: installed Claude overlay env differs from dist ($(printf '%s' "$_d" | cut -c1-200)) — run workspace-doctor.sh --install-claude-overlay, then --install-claude-overlay-retire-env after a live probe" ;;
      *) note "overlay env comparison unavailable ($SJ unreadable?)" ;;
    esac
  fi
fi
# Check EVERY settings layer, not just the user one. A temporary "turn hooks off"
# most often lands in settings.local.json or the project file — precisely where the
# old single-file check was blind, and precisely what this alert exists to catch.
for _s in "$SJ" "$HOME/.claude/settings.local.json" "$WS/.claude/settings.json" "$WS/.claude/settings.local.json"; do
  grep -q '"disableAllHooks"[[:space:]]*:[[:space:]]*true' "$_s" 2>/dev/null && flag "ALERT: disableAllHooks=true in $_s — every hook layer is dead"
done

# 3. Plugin hook config (REPORT)
PLUG="$HOME/.claude/local-plugins/snds-local/snds"
[ -d "$PLUG" ] && report_file "$DIST/plugin-hooks.json" "$PLUG/hooks/hooks.json" "--install-plugin" json

# 4. Fossils (REPORT: removal is a human step)
[ -e "$HOME/Projects/.claude/hooks/dispatcher.py" ] && \
  flag "DRIFT: Drive-era fossil present at ~/Projects/.claude/hooks/dispatcher.py — remove it by hand"

# 4b. --check extras: pin lag, git capabilities, probe records (NOTEs, never drift).
if [ "$CHECK" -eq 1 ]; then
  _lag="$(python3 "$DOC/pin_lib.py" lag --home "$HOME" --repo "$WS" 2>/dev/null)"; _rc=$?
  case $_rc in
    0) _n="$(printf '%s\n' "$_lag" | sed -n 's/^commits_behind_on_pinned_paths: //p')"
       [ "${_n:-0}" != "0" ] && note "pinned lib lags HEAD by $_n commit(s) on pinned paths — run workspace-doctor.sh --install-pin";;
    3) note "nothing pinned — run workspace-doctor.sh --install-pin";;
    *) note "pin lag unavailable";;
  esac
  python3 "$WS/09-tools/profile_resolve.py" gitcaps --check-recorded >/dev/null 2>&1; _rc=$?
  case $_rc in 0) : ;; 1) note "git capability record missing or stale — run profile_resolve.py gitcaps --record";;
    *) note "gitcaps unavailable";; esac
  # H17-R9: a URL rewrite in a git config file can undo the Claude overlay's transport block.
  python3 "$DOC/render_shims.py" --rewrite-audit >/dev/null 2>&1; _rc=$?
  case $_rc in 0) : ;; 1) note "a git config file rewrites an employer URL, so the transport block may not apply — run render_shims.py --rewrite-audit";;
    *) note "rewrite audit unavailable";; esac
  # H18: the global git lanes (REPORT; installed only by --install-git-hooks). The audit reads git config at
  # every scope, globally and per cached checkout: any entry that replaces, clears or disables a lane, or a
  # lane key outside the lane include, is drift. From an agent chain it skips
  # non-personal checkouts.
  if [ -f "$WS/09-tools/git_lanes.py" ]; then
    _la="$(python3 "$WS/09-tools/git_lanes.py" audit --cache 2>/dev/null)"; _rc=$?
    case $_rc in
      0) : ;;
      1) printf '%s\n' "$_la" | grep '^FINDING: ' | head -5 | while IFS= read -r _l; do say "  $_l"; done
         flag "DRIFT: git lanes shadowed, disabled or stale — see python3 09-tools/git_lanes.py audit --cache; remove the listed entries, or re-run workspace-doctor.sh --install-git-hooks";;
      3) note "git lanes not installed — to install: workspace-doctor.sh --install-git-hooks";;
      *) note "git lane audit unavailable";;
    esac
  fi
  _dev="$(python3 "$WS/09-tools/profile_resolve.py" device --json 2>/dev/null | python3 -c 'import json,sys;print(json.load(sys.stdin)["device"]["id"])' 2>/dev/null)"
  if [ -n "$_dev" ] && [ "$_dev" != unknown ]; then
    # devices.json declares this device's home and brain; tools use the live values, this reports drift.
    python3 - "$WS" "$_dev" <<'PY' 2>/dev/null | while IFS= read -r _l; do note "$_l"; done
import json, os, sys
ws, dev = sys.argv[1], sys.argv[2]
rows = json.load(open(os.path.join(ws, "02-shared-references", "devices.json"), encoding="utf-8")).get("devices") or []
row = next((r for r in rows if isinstance(r, dict) and r.get("id") == dev), None) or {}
home = os.path.expanduser("~")
cf = lambda p: os.path.realpath(p).rstrip("/").casefold()
if row.get("home") and cf(row["home"]) != cf(home):
    print(f"devices.json declares home {row['home']} for {dev}, but this login's home is {home}")
if row.get("brain") and cf(os.path.join(home, row["brain"])) != cf(ws):
    print(f"devices.json declares brain {row['brain']} for {dev}, but the workspace resolved to {ws}")
PY
    for _p in claude-code cursor codex copilot-vscode; do
      [ -f "$WS/02-shared-references/probes/$_p@$_dev.json" ] || note "no probe record for $_p@$_dev"
    done
  else
    note "probe state unavailable (device unresolved)"
  fi
fi

if [ "$QUICK" -eq 0 ]; then
  # 5. Personal-repo beacons + discovery of unlisted repos (REPORT)
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
  # D-W1-4: NOOVERLAY = a Claude Code session that ended without the env-file overlay marker (its shell
  # ran without the floor, the transport block and the gh belt). Same ACK boundary as MISS. A session
  # with hooks off logs nothing (no SessionEnd either): the disableAllHooks alert and the canary cover it.
  NO=$(awk -v m="$(cat "$STATE/ack-mark" 2>/dev/null)" '/ NOOVERLAY /{ if ($1 "" > m "") n++ } END{print n+0}' "$LOG" 2>/dev/null)
  [ "${NO:-0}" -gt 0 ] 2>/dev/null && flag "ALERT: $NO Claude session(s) ran without the overlay — inspect $LOG and $TEL/overlay-env.jsonl, then: workspace-doctor --ack"

  # 7. Chat-surface staleness: nag until Sean re-pastes and acks
  [ "$(cat "$DIST/BEACON.md" "$DIST/cursor-user-rules.txt" 2>/dev/null | shasum -a 256 | cut -d' ' -f1)" != "$(cat "$STATE/chat-beacon.sha" 2>/dev/null)" ] && \
    flag "CHAT SURFACES STALE: a paste beacon changed — repaste BEACON.md into claude.ai preferences, Workspace project, Perplexity Space and cursor-user-rules.txt into Cursor User Rules, then: workspace-doctor --ack-chat"

  BEHIND=$(git -C "$WS" rev-list --count '@{u}..HEAD' 2>/dev/null); BEHIND=${BEHIND:-0}
  [ "$BEHIND" != "0" ] && say "SYNC: $BEHIND unpushed commit(s) — chat knowledge stale until push + Sync now"

  if [ "$CHECK" -eq 0 ]; then
    # 8. State hygiene (HEAL: ws-state only; log rotation fixes eternal-NOTICE)
    find "$STATE" \( -name 'boot.*' -o -name 'count.*' -o -name 'ok.*' -o -name 'scan.*' -o -name 'nag.*' -o -name 'overlay.*' \) -mtime +14 -exec rm -rf {} + 2>/dev/null
    # Rotation must NOT refresh the log mtime: the canary at step 6 reads that mtime
    # to decide "sessions ran but the audit is silent". -r copies the pre-rotation
    # mtime back onto the rotated file.
    if [ -f "$LOG" ] && [ "$(wc -l < "$LOG" 2>/dev/null || echo 0)" -gt 500 ]; then
      tail -100 "$LOG" > "$LOG.tmp" && touch -r "$LOG" "$LOG.tmp" 2>/dev/null && mv "$LOG.tmp" "$LOG"
    fi
  fi

  # 9. --quiet (launchd) extras: telemetry only, and only when --install-pin created it.
  if [ "$QUIET" -eq 1 ] && [ "$CHECK" -eq 0 ]; then
    if [ -d "$TEL" ]; then
      if [ -f "$DOC/render_shims.py" ]; then
        _dev="$(python3 "$WS/09-tools/profile_resolve.py" device --json 2>/dev/null | python3 -c 'import json,sys;print(json.load(sys.stdin)["device"]["id"])' 2>/dev/null)"
        python3 "$DOC/render_shims.py" --install-state --json 2>/dev/null | \
          WS_DEV="${_dev:-unknown}" python3 -c '
import datetime, json, os, sys
d = json.load(sys.stdin)
s = d.get("surfaces", {}) if isinstance(d, dict) else {}
out = {"schema_version": 1, "device": os.environ.get("WS_DEV") or "unknown",
       "generated_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
       "surfaces": s}
p = sys.argv[1]; t = p + ".tmp"
open(t, "w").write(json.dumps(out, indent=2) + "\n"); os.replace(t, p)' "$TEL/install-state.json" 2>/dev/null
      fi
      if [ -f "$LIBC/09-tools/profile_resolve.py" ]; then
        python3 "$LIBC/09-tools/profile_resolve.py" scan --report >/dev/null 2>&1 || note "pinned scan did not run (refused or failed)"
      else
        note "nothing pinned — scan skipped (run workspace-doctor.sh --install-pin)"
      fi
    fi
  fi
fi
[ "$QUICK" -eq 0 ] && [ "$CHECK" -eq 0 ] && [ ! -e "$LIBC" ] && note "nothing pinned — run workspace-doctor.sh --install-pin"

[ "$CHECK" -eq 0 ] && date +%Y-%m-%dT%H:%M:%S > "$STATE/doctor-last-run"
if [ "$DRIFT" -eq 0 ]; then say "workspace-doctor: all layers healthy."
# ALERTS is only appended by flag(); a clean REPAIR sets DRIFT without it, which
# used to fire a blank macOS notification with no explanation.
elif [ -n "$ALERTS" ]; then notify "$(printf '%.120s' "$ALERTS")"
else say "workspace-doctor: repairs applied, no alerts."; fi
[ "$CHECK" -eq 1 ] && exit "$DRIFT"; exit 0
