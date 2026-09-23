#!/usr/bin/env bash
# ws-reassert v3 — UserPromptSubmit hook. Silent on the happy path.
# State lives in ~/.claude/ws-state (survives TMPDIR purges — no false late-repairs).
#
# v3 (2026-07-19) closes the COMPLIANCE gap found in the 07-16 audit backlog:
# v2 keyed only off boot.$SID, so it detected hook NON-EXECUTION but never ritual
# NON-COMPLIANCE. On a compact/resume the SessionStart hook fires (marker written,
# reassert goes silent) but the model — mid-task, treating the injected line as
# context rather than a fresh obligation — never emits the token. Nothing noticed
# until the SessionEnd audit logged MISS, far too late to repair. Session
# e2153515 burned 6 MISSes that way; e46f9154 burned 21.
# v3 reads the transcript and re-asserts when the token is genuinely absent.
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
INPUT="$(cat 2>/dev/null || true)"
# grep -o + head -1 takes the FIRST match (the old greedy sed anchored to the LAST).
jget() { printf '%s' "$INPUT" | grep -o "\"$1\"[[:space:]]*:[[:space:]]*\"[^\"]*\"" | head -1 | sed "s/.*:[[:space:]]*\"//; s/\"$//"; }
SID="$(jget session_id)"; TP="$(jget transcript_path)"
[ -n "$SID" ] || exit 0    # cannot identify the session -> fail open, never false-alarm
MARK="$STATE/boot.$SID"; CNT="$STATE/count.$SID"
OKM="$STATE/ok.$SID"; SCAN="$STATE/scan.$SID"; NAG="$STATE/nag.$SID"
RULES="$(cat "$WS/00-bootstrap/dist/RULES.txt" 2>/dev/null | tr '\n' ' ')"

# --- Layer 1: bootstrap never ran (v2 behaviour, unchanged) --------------------
if [ ! -f "$MARK" ]; then
  : > "$MARK"; echo 1 > "$CNT"
  echo "[ws-reassert] The workspace bootstrap hook did NOT run for this session. Unless the caller demands raw structured output: read $WS/AGENTS.md (or github.com/snds/workspace) before answering, and open your reply with [workspace: LOADED (late) · via:prompt-hook]. Standing rules in force now: $RULES"
  exit 0
fi

N=$(( $(cat "$CNT" 2>/dev/null || echo 0) + 1 )); echo "$N" > "$CNT"

# --- Layer 2: bootstrap ran, but did the model actually COMPLY? ---------------
# Fast path: once seen, never scan again. Cheapest possible steady state.
if [ ! -f "$OKM" ] && [ -n "$TP" ] && [ -f "$TP" ]; then
  # Scan only bytes appended since the last look (transcripts reach tens of MB).
  # State file holds: "<byte-offset> <cumulative-assistant-msg-count>".
  OFF=$(cut -d' ' -f1 "$SCAN" 2>/dev/null); OFF=${OFF:-0}
  PRIOR=$(cut -d' ' -f2 "$SCAN" 2>/dev/null); PRIOR=${PRIOR:-0}
  case "$OFF" in ''|*[!0-9]*) OFF=0;; esac
  case "$PRIOR" in ''|*[!0-9]*) PRIOR=0;; esac

  RES="$(python3 - "$TP" "$OFF" 2>/dev/null <<'PY'
import json, sys
path, off = sys.argv[1], int(sys.argv[2])
try:
    f = open(path, "rb")
except Exception:
    sys.exit(3)
f.seek(0, 2); size = f.tell()
if off > size: off = 0          # transcript truncated/rotated -> rescan from 0
f.seek(off)
data = f.read()
cut = data.rfind(b"\n")          # consume only COMPLETE lines; a partial tail is
consumed = cut + 1 if cut >= 0 else 0   # re-read next time rather than dropped
found, n = False, 0
for raw in (data[:consumed].split(b"\n") if consumed else []):
    if not raw.strip(): continue
    try: e = json.loads(raw.decode("utf-8", "replace"))
    except Exception: continue
    m = e.get("message") or {}
    # Hook-injected context rides non-assistant entries (type "attachment") and
    # DOES contain the token — matching it would fake an OK. Assistant role only,
    # same predicate as workspace-audit.sh.
    if (m.get("role") or e.get("type")) != "assistant": continue
    n += 1
    if "workspace: LOADED" in json.dumps(m.get("content", "")): found = True
print(off + consumed, n, 1 if found else 0)
PY
)"

  if [ -n "$RES" ]; then
    NEWOFF=$(printf '%s' "$RES" | cut -d' ' -f1)
    NEWN=$(printf '%s' "$RES" | cut -d' ' -f2)
    FOUND=$(printf '%s' "$RES" | cut -d' ' -f3)
    TOTAL=$(( PRIOR + NEWN ))
    echo "$NEWOFF $TOTAL" > "$SCAN"
    if [ "$FOUND" = "1" ]; then
      : > "$OKM"                        # sticky: never scan this session again
    elif [ "$TOTAL" -gt 0 ]; then
      # The model has already produced output THIS session without ever emitting
      # the token. TOTAL==0 means it simply hasn't replied yet (first prompt) —
      # and it also exempts headless one-shots, which never see a 2nd prompt.
      NN=$(( $(cat "$NAG" 2>/dev/null || echo 0) + 1 )); echo "$NN" > "$NAG"
      if [ "$NN" -le 3 ]; then          # capped: assert, don't nag forever
        echo "[ws-reassert] RITUAL MISSING: this session has produced replies but never emitted the workspace ritual token — the SessionEnd audit will log a MISS. This is the compaction/resume path: the bootstrap line was injected but not acted on. Unless the caller demands raw structured output, open your NEXT reply with [workspace: LOADED (late) · via:prompt-hook] before anything else. If compaction dropped context, re-read $WS/AGENTS.md first. Standing rules in force: $RULES"
      fi
    fi
  fi
fi

# --- Layer 3: periodic rules heartbeat (v2 behaviour, unchanged) --------------
[ $(( N % 15 )) -eq 0 ] && echo "[ws-reassert] Workspace rules at $WS remain in force: $RULES If compaction dropped context, re-read AGENTS.md."
exit 0
