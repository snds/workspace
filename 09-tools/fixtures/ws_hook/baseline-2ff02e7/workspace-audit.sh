#!/usr/bin/env bash
# ws-audit v2 — SessionEnd hook. OK only if an ASSISTANT message contains the ritual
# token (hook-injected context cannot fake an OK). One-exchange sessions (headless -p,
# subagents) log SKIP, not MISS. Crash/SIGKILL sessions log nothing — the doctor
# canary covers that class, not this script.
set -u
STATE="$HOME/.claude/ws-state"; mkdir -p "$STATE"
INPUT="$(cat 2>/dev/null || true)"
# grep -o + head -1 takes the FIRST match. The old sed used a greedy `.*` prefix,
# which anchored to the LAST occurrence: a nested/repeated key (e.g. a "source"
# inside a meta object) silently won over the real top-level one.
jget() { printf '%s' "$INPUT" | grep -o "\"$1\"[[:space:]]*:[[:space:]]*\"[^\"]*\"" | head -1 | sed "s/.*:[[:space:]]*\"//; s/\"$//"; }
TP="$(jget transcript_path)"; SID="$(jget session_id)"; CWD="$(jget cwd)"
LOG="$STATE/audit.log"; TS=$(date +%Y-%m-%dT%H:%M:%S)
[ -f "$TP" ] || { echo "$TS SKIP ${SID:-?} no-transcript" >> "$LOG"; exit 0; }
# Gate on the ACTUAL dependency (python3), not the Xcode CLT. The old gate made
# the audit wholly inert on Linux (no xcode-select binary at all) and on any Mac
# using Homebrew/pyenv python without CLT installed — the workspace is explicitly
# cross-platform, so that silently disabled this layer on entire machines.
command -v python3 >/dev/null 2>&1 || { echo "$TS SKIP ${SID:-?} no-python3" >> "$LOG"; exit 0; }
python3 - "$TP" <<'PY' >/dev/null 2>&1; R=$?
import json, sys
prompts, ok = 0, False
for line in open(sys.argv[1], encoding="utf-8", errors="replace"):
    try: e = json.loads(line)
    except Exception: continue
    # Subagent/sidechain turns are a DIFFERENT agent's output — they must not
    # satisfy (or count against) the parent session's ritual. Verified 2026-07-19:
    # 6 sidechain assistant messages across the transcript corpus carry the token,
    # each of which would have flipped its parent session to a false OK.
    if e.get("isSidechain"): continue
    m = e.get("message") or {}
    role = m.get("role") or e.get("type")
    if role == "user" and not e.get("isMeta"):
        # Tool results ride user-role messages in the transcript; counting them
        # made every tool-using headless one-shot look multi-prompt -> false MISS
        # (found 2026-07-09: four claude -p runs logged MISS under the one-shot
        # exemption). Count only human prompts.
        c = m.get("content")
        if isinstance(c, list) and any(isinstance(b, dict) and b.get("type") == "tool_result" for b in c):
            continue
        prompts += 1
    if role == "assistant" and "workspace: LOADED" in json.dumps(m.get("content", "")): ok = True
sys.exit(0 if ok else (2 if prompts <= 1 else 1))
PY
case $R in
  0) echo "$TS OK   ${SID:-?} cwd=${CWD:-?}" >> "$LOG" ;;
  2) echo "$TS SKIP ${SID:-?} one-shot"      >> "$LOG" ;;
  1) echo "$TS MISS ${SID:-?} cwd=${CWD:-?}" >> "$LOG" ;;
  *) echo "$TS SKIP ${SID:-?} parse-error"   >> "$LOG" ;;
esac
exit 0
