#!/bin/sh
# resolve-skills-symlink.sh — machine-local resolver for the Claude Workspace skills mount.
#
# WHY: Google Drive can be in Stream mode (files online-only until offlined) or
# Mirror mode (always-local), and the two modes expose the workspace at DIFFERENT
# roots. ~/.claude/skills is a machine-local symlink, so each machine should point it
# at whichever root is actually MATERIALIZED here. This lets Sean run stream+offline
# on the work Mac and mirror on personal/Windows with one identical script.
#
# RULE: pick the first candidate whose probe file has real local bytes ([ -s ]).
# Existence alone is NOT enough — a stale stream mount lists fine while every file is
# a 0-byte placeholder. Materialization is the gate.
#
# Safe + idempotent: only repoints when the resolved target differs; never clobbers a
# real (non-symlink) ~/.claude/skills directory.

set -u
PROBE="06-context/session-log.md"          # canonical "is this mount real?" file
LINK="$HOME/.claude/skills"

# Candidate workspace roots, in preference order. Mirror first, then Stream, then
# wildcards / Windows drives. Non-existent candidates are skipped harmlessly.
CANDIDATES="
$HOME/My Drive/Claude Workspace
$HOME/Library/CloudStorage/GoogleDrive-hello@snds.design/My Drive/Claude Workspace
"
# Glob-expanded fallbacks (multi-account stream mounts) + Windows mirror drives.
for g in "$HOME"/Library/CloudStorage/GoogleDrive-*/My\ Drive/Claude\ Workspace \
         /g/My\ Drive/Claude\ Workspace /h/My\ Drive/Claude\ Workspace; do
  [ -e "$g" ] && CANDIDATES="$CANDIDATES
$g"
done

RESOLVED=""
OLDIFS=$IFS; IFS='
'
for ROOT in $CANDIDATES; do
  [ -n "$ROOT" ] || continue
  if [ -d "$ROOT/02-skills" ] && [ -s "$ROOT/$PROBE" ]; then
    RESOLVED="$ROOT/02-skills"
    break
  fi
done
IFS=$OLDIFS

if [ -z "$RESOLVED" ]; then
  echo "resolve-skills-symlink: no materialized workspace root found (Drive offline or dehydrated)" >&2
  exit 0   # non-fatal: let bootstrap fall back to Drive MCP
fi

# Don't clobber a real directory placed at ~/.claude/skills.
if [ -e "$LINK" ] && [ ! -L "$LINK" ]; then
  echo "resolve-skills-symlink: $LINK is a real directory, not a symlink — leaving untouched" >&2
  exit 0
fi

CURRENT=""
[ -L "$LINK" ] && CURRENT="$(readlink "$LINK")"
if [ "$CURRENT" = "$RESOLVED" ]; then
  exit 0   # already correct, silent
fi

mkdir -p "$HOME/.claude"
ln -sfn "$RESOLVED" "$LINK"
echo "resolve-skills-symlink: repointed $LINK -> $RESOLVED" >&2
exit 0
