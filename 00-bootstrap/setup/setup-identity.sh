#!/usr/bin/env bash
# setup-identity.sh — Codify the two-account GitHub SSH + git identity pattern
# on a fresh macOS machine. Idempotent: safe to re-run.
#
# What this does:
#   1. Generate two ed25519 SSH keys (personal + work) labeled with hostname
#   2. Write ~/.ssh/config with host aliases (github.com → personal, github-work → work)
#   3. Print both pubkeys with paste targets for each GitHub account
#   4. Wait for user confirmation, then verify both `ssh -T` connections
#   5. Optionally install ~/.gitconfig with includeIf directory-routed identity
#
# After running, clone repos via:
#   personal:  git@github.com:snds/<repo>.git
#   work:      git@github-work:cpes-software/<repo>.git
#
# Workspace clone steps live in 08-knowledge/cross-domain/workspace-infrastructure.md.

set -uo pipefail

# --- Configuration (hardcoded per Sean's identities) ---

PERSONAL_USER="snds"
PERSONAL_EMAIL="hello@snds.design"
PERSONAL_NOREPLY="570874+snds@users.noreply.github.com"

WORK_USER="sean-sands-centric"
WORK_EMAIL="sean.sands@centricsoftware.com"
WORK_NAME="Sean Sands"

HOST=$(hostname)
SSH_DIR="$HOME/.ssh"
KEY_PERSONAL="$SSH_DIR/id_ed25519_personal"
KEY_WORK="$SSH_DIR/id_ed25519_work"
SSH_CONFIG="$SSH_DIR/config"

GITCONFIG="$HOME/.gitconfig"
GITCONFIG_PERSONAL="$HOME/.gitconfig.personal"
GITCONFIG_WORK="$HOME/.gitconfig.work"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE_DIR="$SCRIPT_DIR"

# --- Output helpers ---

step() { printf "\n\033[1;34m▸\033[0m %s\n" "$*"; }
ok()   { printf "  \033[32m✓\033[0m %s\n" "$*"; }
warn() { printf "  \033[33m⚠\033[0m %s\n" "$*"; }
err()  { printf "  \033[31m✗\033[0m %s\n" "$*" >&2; }
ask() {
  printf "  \033[36m?\033[0m %s [y/N] " "$*"
  read -r reply
  [ "$reply" = "y" ] || [ "$reply" = "Y" ] || [ "$reply" = "yes" ]
}
overwrite_ok() {
  local path=$1
  if [ -e "$path" ]; then
    ask "$path exists. Overwrite?" || { warn "Keeping existing $path"; return 1; }
  fi
  return 0
}

# --- Sanity checks ---

if [ "$(uname -s)" != "Darwin" ]; then
  err "This script targets macOS. Detected: $(uname -s)"
  exit 1
fi

mkdir -p "$SSH_DIR" && chmod 700 "$SSH_DIR"

# --- Step 1: SSH keys ---

step "Generating SSH keys (ed25519, no passphrase, labeled with hostname)"

if overwrite_ok "$KEY_PERSONAL"; then
  rm -f "$KEY_PERSONAL" "$KEY_PERSONAL.pub"
  ssh-keygen -t ed25519 -C "$PERSONAL_EMAIL ($HOST)" -f "$KEY_PERSONAL" -N "" >/dev/null
  ok "Generated $KEY_PERSONAL"
fi

if overwrite_ok "$KEY_WORK"; then
  rm -f "$KEY_WORK" "$KEY_WORK.pub"
  ssh-keygen -t ed25519 -C "$WORK_USER ($HOST)" -f "$KEY_WORK" -N "" >/dev/null
  ok "Generated $KEY_WORK"
fi

chmod 600 "$KEY_PERSONAL" "$KEY_WORK" 2>/dev/null || true

# --- Step 2: SSH config ---

step "Writing $SSH_CONFIG"

if overwrite_ok "$SSH_CONFIG"; then
  cat > "$SSH_CONFIG" <<EOF
# SSH config — two GitHub identities on one machine
# Personal: github.com → $PERSONAL_USER (uses id_ed25519_personal)
# Work:     github-work → $WORK_USER (uses id_ed25519_work)
#
# Clone personal repos:  git@github.com:$PERSONAL_USER/<repo>.git
# Clone work repos:      git@github-work:cpes-software/<repo>.git
#                                  ^^^^^^^^^^^ alias, NOT a real hostname

Host github.com
  HostName github.com
  User git
  IdentityFile ~/.ssh/id_ed25519_personal
  IdentitiesOnly yes
  AddKeysToAgent yes
  UseKeychain yes

Host github-work
  HostName github.com
  User git
  IdentityFile ~/.ssh/id_ed25519_work
  IdentitiesOnly yes
  AddKeysToAgent yes
  UseKeychain yes
EOF
  chmod 600 "$SSH_CONFIG"
  ok "Wrote $SSH_CONFIG"
fi

# --- Step 3: Print pubkeys ---

step "Pubkeys to paste into GitHub"

cat <<EOF

  ┌────────────────────────────────────────────────────────────────────┐
  │ 1. PERSONAL — paste at github.com/settings/ssh/new                 │
  │    Sign in as: $PERSONAL_USER
  │    Suggested title: $HOST (personal)
  └────────────────────────────────────────────────────────────────────┘

$(cat "$KEY_PERSONAL.pub")

  ┌────────────────────────────────────────────────────────────────────┐
  │ 2. WORK — paste at github.com/settings/ssh/new                     │
  │    Sign in as: $WORK_USER
  │    Suggested title: $HOST (work)
  └────────────────────────────────────────────────────────────────────┘

$(cat "$KEY_WORK.pub")

EOF

while ! ask "Both pubkeys pasted into their respective GitHub accounts?"; do
  warn "Waiting — paste both, then answer y."
done

# --- Step 4: Verify ---

step "Verifying SSH connections"

personal_result=$(ssh -o StrictHostKeyChecking=accept-new -T git@github.com 2>&1 | head -1 || true)
if echo "$personal_result" | grep -q "Hi $PERSONAL_USER"; then
  ok "Personal: $personal_result"
else
  err "Personal FAILED: $personal_result"
  err "Confirm the pubkey was pasted into the snds account, then re-run."
fi

work_result=$(ssh -o StrictHostKeyChecking=accept-new -T github-work 2>&1 | head -1 || true)
if echo "$work_result" | grep -q "Hi $WORK_USER"; then
  ok "Work: $work_result"
else
  err "Work FAILED: $work_result"
  err "Confirm the pubkey was pasted into the $WORK_USER account, then re-run."
fi

# --- Step 5: Optional gitconfig ---

step "~/.gitconfig with includeIf identity routing"
echo "  Routes identity by directory:"
echo "    ~/personal/**  → uses snds + GitHub no-reply email"
echo "    ~/work/**      → uses Sean Sands + sean.sands@centricsoftware.com"
echo "  Repos outside both (incl. the Claude Workspace) use repo-local config."

if ask "Install ~/.gitconfig template?"; then
  for src_name in gitconfig.template gitconfig.personal.template gitconfig.work.template; do
    src="$TEMPLATE_DIR/$src_name"
    case "$src_name" in
      gitconfig.template)         dst="$GITCONFIG" ;;
      gitconfig.personal.template) dst="$GITCONFIG_PERSONAL" ;;
      gitconfig.work.template)    dst="$GITCONFIG_WORK" ;;
    esac
    if [ ! -f "$src" ]; then
      warn "Template missing: $src — skipping $dst"
      continue
    fi
    if overwrite_ok "$dst"; then
      cp "$src" "$dst"
      ok "Wrote $dst"
    fi
  done
fi

# --- Done ---

step "Identity setup complete"
cat <<EOF

  Clone personal repos:  git@github.com:$PERSONAL_USER/<repo>.git
  Clone work repos:      git@github-work:cpes-software/<repo>.git

  Workspace clone (separate-git-dir pattern) is documented in:
    08-knowledge/cross-domain/workspace-infrastructure.md

EOF
