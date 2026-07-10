#!/usr/bin/env bash
# beacon-enroll — enroll PERSONAL repos for cloud-session beacon coverage, safely.
#
#   beacon-enroll.sh <repo-path> [--personal] [--commit]   enroll one repo
#   beacon-enroll.sh --sweep [--apply] [--commit]          classify all ~/Projects repos
#
# Enrolling = (1) add the repo path to dist/beacon-repos.txt AND (2) write the
# WORKSPACE-BEACON block into that repo's CLAUDE.md — always both, atomically,
# because a listed repo with no beacon block makes the doctor raise DRIFT alerts.
#
# Classification is mechanical, per the context-profile resolution order
# (02-shared-references/delivery-playbooks/00-context-profiles.md):
#   personal  = origin remote under github.com/snds/            -> may enroll
#   employer  = github-work / cpes-software / c8 remotes or dir -> NEVER enrolled;
#               recorded in beacon-repos.ignore.txt so it stops being flagged
#   unknown   = anything else (incl. no remote) -> fail-safe: NOT enrolled unless
#               Sean's word overrides via --personal
#
# --sweep is a DRY-RUN by default; add --apply to act. --commit additionally
# commits+pushes the CLAUDE.md change inside each enrolled repo (cloud sessions
# read GitHub, so coverage is only live once the beacon is pushed).
set -u

# Resolve the workspace root (FX-14 — no hardcoded path): brain-path file first,
# then candidate list; AGENTS.md presence is the test.
WS=""
for _c in "$(cat "$HOME/.claude/workspace-brain-path" 2>/dev/null | head -1)" \
          "$HOME/Projects/Workspace" "$HOME/Projects/workspace" "$HOME/projects/workspace"; do
  [ -n "$_c" ] && [ -f "$_c/AGENTS.md" ] && WS="$_c" && break
done
[ -n "$WS" ] || { echo "FATAL: workspace root not found"; exit 1; }
DIST="$WS/00-bootstrap/dist"
LIST="$DIST/beacon-repos.txt"
IGNORE="$DIST/beacon-repos.ignore.txt"
BEACON="$DIST/BEACON.md"
[ -f "$BEACON" ] || { echo "FATAL: $BEACON missing"; exit 1; }

classify() { # $1=repo-path -> echoes personal|employer|unknown
  case "$1" in *c8*) echo employer; return;; esac
  local r; r="$(git -C "$1" remote get-url origin 2>/dev/null || true)"
  case "$r" in
    *github.com[:/]snds/*)                       echo personal;;
    *github-work*|*cpes-software*|*[:/]c8[-/]*)  echo employer;;
    *)                                           echo unknown;;
  esac
}

listed()  { grep -qxF "$1" "$LIST"   2>/dev/null; }
ignored() { grep -q "^$1"  "$IGNORE" 2>/dev/null; }

ensure_beacon_block() { # $1=repo-path
  local cm="$1/CLAUDE.md"
  if grep -q "WORKSPACE-BEACON" "$cm" 2>/dev/null; then echo "    beacon block: already present"; return 0; fi
  { [ -s "$cm" ] && printf '\n'; cat "$BEACON"; } >> "$cm" || return 1
  echo "    beacon block: written to $cm"
}

enroll() { # $1=repo-path $2=do_commit(0/1)
  local repo="$1"
  listed "$repo" || { printf '%s\n' "$repo" >> "$LIST"; echo "    beacon-repos.txt: added"; }
  listed "$repo" && ensure_beacon_block "$repo" || { echo "    ERROR enrolling $repo"; return 1; }
  if [ "$2" = 1 ]; then
    if git -C "$repo" add CLAUDE.md 2>/dev/null && \
       ! git -C "$repo" diff --cached --quiet -- CLAUDE.md; then
      git -C "$repo" commit -q -m "chore: add workspace beacon (cloud-session coverage)" -- CLAUDE.md \
        && git -C "$repo" push -q 2>/dev/null \
        && echo "    committed + pushed" \
        || echo "    committed locally; PUSH FAILED — push manually"
    else
      echo "    nothing to commit (already committed?)"
    fi
  else
    echo "    NOTE: commit + push CLAUDE.md in this repo for cloud coverage (or rerun with --commit)"
  fi
}

add_ignore() { # $1=repo-path $2=reason
  ignored "$1" || printf '%s  # %s (%s)\n' "$1" "$2" "$(date +%Y-%m-%d)" >> "$IGNORE"
}

case "${1:-}" in
  --sweep)
    APPLY=0; COMMIT=0
    for a in "$@"; do case $a in --apply) APPLY=1;; --commit) COMMIT=1;; esac; done
    [ "$APPLY" = 1 ] || echo "(dry run — add --apply to act)"
    for d in "$HOME/Projects"/*/; do d="${d%/}"
      [ -d "$d/.git" ] || continue
      [ "$d" = "$WS" ] && continue
      listed "$d" && continue
      ignored "$d" && continue
      c="$(classify "$d")"
      case "$c" in
        personal) echo "PERSONAL  $d"
                  [ "$APPLY" = 1 ] && enroll "$d" "$COMMIT";;
        employer) echo "EMPLOYER  $d — never enrolled"
                  [ "$APPLY" = 1 ] && { add_ignore "$d" "employer remote"; echo "    ignore list: recorded (no more nags)"; };;
        unknown)  echo "UNKNOWN   $d — fail-safe: not enrolled. If personal, run: $0 $d --personal";;
      esac
    done
    ;;
  ""|--help|-h)
    sed -n '2,20p' "$0"; exit 0;;
  *)
    REPO="${1%/}"; FORCE=0; COMMIT=0
    for a in "$@"; do case $a in --personal) FORCE=1;; --commit) COMMIT=1;; esac; done
    [ -d "$REPO/.git" ] || { echo "not a git repo: $REPO"; exit 1; }
    c="$(classify "$REPO")"
    case "$c" in
      employer) echo "REFUSED: $REPO classifies as EMPLOYER — never enrolled (standing rule)."; add_ignore "$REPO" "employer remote"; exit 1;;
      unknown)  [ "$FORCE" = 1 ] || { echo "UNKNOWN classification for $REPO — fail-safe: not enrolled. Re-run with --personal if Sean declares it personal."; exit 1; }
                echo "ENROLL (Sean's word via --personal): $REPO"; enroll "$REPO" "$COMMIT";;
      personal) echo "ENROLL (personal remote): $REPO"; enroll "$REPO" "$COMMIT";;
    esac
    ;;
esac
