---
name: cowork-skills-sync
description: >
  Syncs skills from Google Drive to the Cowork VM's skills-plugin directory
  using Desktop Commander. Google Drive is the source of truth. Run this at
  the start of every Cowork session (called by workspace-bootstrap) and on
  demand when skills have been updated. Trigger on: "sync skills",
  "update skills", "refresh skills", "skills out of date", or any phrase
  suggesting Cowork skills need updating. Also runs silently as part of
  workspace-bootstrap boot sequence.
---

# Cowork Skills Sync

Resolves a fundamental Cowork limitation: the VM cannot follow symlinks to
Google Drive because the Drive filesystem isn't mounted inside the sandbox.
This skill uses Desktop Commander (which runs on the host) to replace broken
symlinks with real directory copies, and keeps them in sync with the Drive
source of truth.

---

## Why This Exists

Cowork mounts user skills via a `skills-plugin` directory on the host. When
skills are stored in Google Drive and symlinked into that directory, the
symlinks resolve fine on macOS but break inside the VM. The VM sees the
symlink entries but can't traverse them — so `SKILL.md` reads fail silently.

This skill fixes that by:
1. Detecting broken symlinks in the skills-plugin directory
2. Replacing them with actual copies from Google Drive
3. Keeping existing copies up to date when the Drive source changes
4. Handling both top-level skills and design-system-ops sub-skills

---

## Prerequisites

- **Desktop Commander** must be available (this skill is DC-only)
- **Google Drive for Desktop** must be running and synced
- The workspace root must be resolvable (see workspace-bootstrap for path resolution)

If DC is not available, skip silently — this skill is a no-op outside Cowork
with DC.

---

## Path Constants

These are resolved dynamically at runtime. Do not hardcode UUIDs.

### Google Drive Source (authoritative)

```
GDRIVE_ROOT = ~/Library/CloudStorage/GoogleDrive-hello@snds.design/My Drive/Claude Workspace/02-skills
```

Contains:
- Top-level skill directories (ds-advisor/, figma-plugin/, etc.)
- `design-system-ops/skills/` subdirectory (38+ skills with references/)
- `design-system-ops/skills/*.md` standalone agent files
- `skills-manifest.json`

### Cowork Skills-Plugin Target

```bash
BASE="$HOME/Library/Application Support/Claude/local-agent-mode-sessions/skills-plugin"
UUID1=$(ls "$BASE" | head -1)
UUID2=$(ls "$BASE/$UUID1" | head -1)
TARGET="$BASE/$UUID1/$UUID2/skills"
```

This is where Cowork reads skills from. The VM mounts this as
`/mnt/.skills/skills/` (read-only from inside the VM).

---

## Sync Protocol

### Step 1 — Resolve Paths

Use Desktop Commander to resolve both paths. If either fails, abort with
a warning — do not guess paths.

```bash
# Resolve Google Drive
GDRIVE_ROOT="$HOME/Library/CloudStorage/GoogleDrive-hello@snds.design/My Drive/Claude Workspace/02-skills"
ls "$GDRIVE_ROOT" > /dev/null 2>&1 || { echo "ERROR: Google Drive not accessible"; exit 1; }

# Resolve skills-plugin
BASE="$HOME/Library/Application Support/Claude/local-agent-mode-sessions/skills-plugin"
UUID1=$(ls "$BASE" | head -1)
UUID2=$(ls "$BASE/$UUID1" | head -1)
TARGET="$BASE/$UUID1/$UUID2/skills"
ls "$TARGET" > /dev/null 2>&1 || { echo "ERROR: Skills-plugin directory not found"; exit 1; }
```

### Step 2 — Fix Broken Symlinks

Check every entry in `$TARGET`. If it's a symlink (broken or not), replace
it with a recursive copy from the Drive source.

```bash
for entry in "$TARGET"/*/; do
  name=$(basename "$entry")
  if [ -L "$TARGET/$name" ]; then
    # It's a symlink — replace with real copy
    source="$GDRIVE_ROOT/$name"
    if [ -d "$source" ]; then
      rm "$TARGET/$name"
      cp -R "$source" "$TARGET/$name"
      echo "FIXED: $name (symlink → copy)"
    fi
  fi
done
```

This is idempotent — once a symlink is replaced, it becomes a real directory
and won't be touched again by this step.

### Step 3 — Sync Top-Level Skills (Drive → Target)

For each skill directory in `$GDRIVE_ROOT` (excluding `design-system-ops`
and non-directory files):

1. If the skill doesn't exist in `$TARGET`: copy it
2. If it exists: compare the SKILL.md hash
3. If hashes differ: the Drive copy wins — replace the target

```bash
for source_dir in "$GDRIVE_ROOT"/*/; do
  name=$(basename "$source_dir")
  
  # Skip design-system-ops (handled separately) and non-skill entries
  [ "$name" = "design-system-ops" ] && continue
  [ ! -f "$source_dir/SKILL.md" ] && continue
  
  target_dir="$TARGET/$name"
  
  if [ ! -d "$target_dir" ]; then
    # New skill — copy entire directory
    cp -R "$source_dir" "$target_dir"
    echo "ADDED: $name"
  else
    # Existing skill — check if Drive version is newer
    drive_hash=$(shasum -a 256 "$source_dir/SKILL.md" | awk '{print $1}')
    target_hash=$(shasum -a 256 "$target_dir/SKILL.md" 2>/dev/null | awk '{print $1}')
    
    if [ "$drive_hash" != "$target_hash" ]; then
      rm -rf "$target_dir"
      cp -R "$source_dir" "$target_dir"
      echo "UPDATED: $name"
    fi
  fi
done
```

### Step 4 — Sync Design-System-Ops Skills

The `design-system-ops/skills/` directory contains two types of entries:
- **Skill directories** (with SKILL.md inside) — copy as skill directories
- **Standalone agent .md files** — wrap in a directory with SKILL.md

```bash
DSOPS="$GDRIVE_ROOT/design-system-ops/skills"

# Skill directories
for source_dir in "$DSOPS"/*/; do
  name=$(basename "$source_dir")
  [ ! -f "$source_dir/SKILL.md" ] && continue
  
  target_dir="$TARGET/$name"
  
  if [ ! -d "$target_dir" ]; then
    cp -R "$source_dir" "$target_dir"
    echo "ADDED (ds-ops): $name"
  else
    drive_hash=$(shasum -a 256 "$source_dir/SKILL.md" | awk '{print $1}')
    target_hash=$(shasum -a 256 "$target_dir/SKILL.md" 2>/dev/null | awk '{print $1}')
    
    if [ "$drive_hash" != "$target_hash" ]; then
      rm -rf "$target_dir"
      cp -R "$source_dir" "$target_dir"
      echo "UPDATED (ds-ops): $name"
    fi
  fi
done

# Standalone agent .md files → wrap as skill directories
for agent_file in "$DSOPS"/*.md; do
  [ ! -f "$agent_file" ] && continue
  fname=$(basename "$agent_file")
  skill_name="${fname%.md}"
  target_dir="$TARGET/$skill_name"
  
  if [ ! -d "$target_dir" ]; then
    mkdir -p "$target_dir"
    cp "$agent_file" "$target_dir/SKILL.md"
    echo "ADDED (agent): $skill_name"
  else
    drive_hash=$(shasum -a 256 "$agent_file" | awk '{print $1}')
    target_hash=$(shasum -a 256 "$target_dir/SKILL.md" 2>/dev/null | awk '{print $1}')
    
    if [ "$drive_hash" != "$target_hash" ]; then
      cp "$agent_file" "$target_dir/SKILL.md"
      echo "UPDATED (agent): $skill_name"
    fi
  fi
done
```

### Step 5 — Remove Orphaned Skills

If a skill exists in `$TARGET` but not in Drive (and isn't a platform/built-in
skill), it should be flagged but NOT auto-deleted. Built-in skills (those
managed by Anthropic/Cowork) are identified by having existed before any
Drive sync — they are never touched.

```bash
# Known built-in skills — never delete these
BUILTINS="algorithmic-art brand-guidelines canvas-design doc-coauthoring docx internal-comms mcp-builder pdf pptx schedule skill-creator slack-gif-creator theme-factory web-artifacts-builder xlsx"

for target_dir in "$TARGET"/*/; do
  name=$(basename "$target_dir")
  
  # Skip built-ins
  echo "$BUILTINS" | grep -qw "$name" && continue
  
  # Check if it exists in Drive (top-level or ds-ops)
  if [ ! -d "$GDRIVE_ROOT/$name" ] && [ ! -d "$DSOPS/$name" ] && [ ! -f "$DSOPS/$name.md" ]; then
    echo "ORPHAN: $name (exists in target but not in Drive — keeping)"
  fi
done
```

### Step 6 — Report

Output a one-line summary. Silent if nothing changed.

```
Format when changes occurred:
  ✓ Skills synced — [N] added, [M] updated, [K] fixed symlinks

Format when no changes:
  ✓ Skills in sync — [total] skills verified
```

---

## Running the Sync

### At Boot (via workspace-bootstrap)

Called silently as part of the boot sequence. Runs after DC is confirmed
available. Output is folded into the boot confirmation line.

### On Demand

User says "sync skills" or similar. Run the full protocol and report results.

### After Skill Edits

When a skill is modified in a Cowork session:
1. Write the updated SKILL.md to Google Drive (source of truth)
2. Run Step 3 or Step 4 for just that skill to update the local mount
3. Update the skills-manifest.json hash

This ensures Drive stays authoritative and the local copy stays current.

---

## Implementation as a Single Script

For efficiency, the entire sync can be run as a single Desktop Commander
`start_process` call. Combine Steps 1–6 into one bash script. This avoids
multiple round-trips between Claude and DC.

The script should:
- Exit 0 on success (even if no changes needed)
- Exit 1 on path resolution failure
- Print one line per action taken (FIXED/ADDED/UPDATED/ORPHAN)
- Print a summary line at the end
- Be safe to run repeatedly (fully idempotent)

---

## Limitations

- **One-way sync**: Drive → Cowork target only. If a skill is edited
  directly in the skills-plugin directory (rare), it will be overwritten
  on next sync. Always edit skills in Drive.
- **Session-scoped**: The skills-plugin path includes session UUIDs that
  may change between Cowork sessions. The path is re-resolved every time.
- **No VM write-back**: The VM sees `.skills/skills/` as read-only. All
  writes go through Desktop Commander on the host side.
- **Design-system-ops structure**: Agent `.md` files are wrapped as skill
  directories. If the upstream repo changes this convention, the wrapping
  logic may need updating.
