#!/usr/bin/env python3
"""
Skills Manifest Reconciliation Script
Run per-session to keep skills-manifest.json in sync with actual skill files.

Usage:
  python3 reconcile-manifest.py                    # from 02-skills/
  python3 /path/to/Claude Workspace/02-skills/reconcile-manifest.py

Can be called by any Claude session via Desktop Commander:
  start_process("python3 '<workspace>/02-skills/reconcile-manifest.py'")
"""

import os, sys, hashlib, json, re
from datetime import datetime, timezone

# Resolve workspace paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILLS_DIR = SCRIPT_DIR  # Script lives in 02-skills/
MANIFEST_PATH = os.path.join(SKILLS_DIR, 'skills-manifest.json')

UUID_PATTERN = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')

def resolve_local_mount():
    """Dynamically find the Cowork skills mount path."""
    base = os.path.expanduser(
        '~/Library/Application Support/Claude/'
        'local-agent-mode-sessions/skills-plugin'
    )
    if not os.path.isdir(base):
        return None
    # Filter for UUID-formatted directories only
    entries = [e for e in os.listdir(base) if UUID_PATTERN.match(e)]
    if not entries:
        return None
    uuid1 = entries[0]
    inner = [e for e in os.listdir(os.path.join(base, uuid1))
             if UUID_PATTERN.match(e)]
    if not inner:
        return None
    uuid2 = inner[0]
    return os.path.join(base, uuid1, uuid2, 'skills')

def compute_hash(filepath):
    """SHA256 hash of file contents."""
    with open(filepath, 'rb') as f:
        return 'sha256:' + hashlib.sha256(f.read()).hexdigest()


def reconcile():
    now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S')

    # Load existing manifest or create empty
    if os.path.isfile(MANIFEST_PATH):
        with open(MANIFEST_PATH) as f:
            manifest = json.load(f)
    else:
        manifest = {'skills': {}}

    old_skills = manifest.get('skills', {})
    local_mount = resolve_local_mount()

    # Scan all skill directories
    new_skills = {}
    changed = []
    added = []

    skill_dirs = sorted([
        d for d in os.listdir(SKILLS_DIR)
        if os.path.isdir(os.path.join(SKILLS_DIR, d))
        and not d.startswith('_')  # skip deprecated / archived / underscore-prefixed folders
    ])

    for skill_name in skill_dirs:
        skill_dir = os.path.join(SKILLS_DIR, skill_name)
        skill_file = os.path.join(skill_dir, 'SKILL.md')

        if not os.path.isfile(skill_file):
            # Check for .skill archives or other formats
            files = os.listdir(skill_dir)
            if any(f.endswith('.skill') for f in files):
                # Preserve existing manifest entry for skill packs
                if skill_name in old_skills:
                    new_skills[skill_name] = old_skills[skill_name]
                continue
            md_files = [f for f in files if f.endswith('.md')]
            if not md_files:
                continue
            skill_file = os.path.join(skill_dir, md_files[0])

        file_hash = compute_hash(skill_file)
        existing = old_skills.get(skill_name, {})
        existing_hash = existing.get('hash', '')

        if file_hash != existing_hash:
            if skill_name in old_skills:
                changed.append(skill_name)
            else:
                added.append(skill_name)
            synced = now
        else:
            synced = existing.get('last_synced', now)

        new_skills[skill_name] = {
            'drive_path': f'02-skills/{skill_name}/SKILL.md',
            'hash': file_hash,
            'last_synced': synced
        }

    # Preserve special entries (skill packs, etc.)
    for k, v in old_skills.items():
        if v.get('type') == 'skill-pack' and k not in new_skills:
            new_skills[k] = v

    # Build updated manifest
    updated = {
        'last_sync_check': now,
        'sync_interval_minutes': 15,
        'local_mount': {
            'user': local_mount or '[unresolved]',
            'public': '/mnt/skills/public',
            'examples': '/mnt/skills/examples'
        },
        'skills': new_skills
    }

    with open(MANIFEST_PATH, 'w') as f:
        json.dump(updated, f, indent=2)

    # Report
    removed = [k for k in old_skills if k not in new_skills
               and not old_skills[k].get('type')]
    total = len(new_skills)

    print(f'Skills manifest reconciled: {total} skills registered')
    print(f'Local mount: {local_mount or "unresolved"}')
    if added:
        print(f'Added ({len(added)}): {", ".join(sorted(added))}')
    if changed:
        print(f'Changed ({len(changed)}): {", ".join(sorted(changed))}')
    if removed:
        print(f'Removed ({len(removed)}): {", ".join(sorted(removed))}')
    if not added and not changed and not removed:
        print('No changes detected — manifest is current.')

    return {
        'total': total,
        'added': added,
        'changed': changed,
        'removed': removed
    }


if __name__ == '__main__':
    reconcile()
