---
name: skill-placement
description: >
  HIGH PRIORITY: Automatic skill placement workflow for any skills created
  with Sean. Ensures all skills are placed in Google Drive Claude Workspace
  (source of truth) and then copied to Claude's skill access directory.
  Includes validation to confirm 1:1 file matching between locations.
  Trigger this skill AUTOMATICALLY at the start of any skill creation task,
  before generating any skill content. Also trigger when Sean mentions
  "create a skill", "generate skill", "make a skill", or any skill creation
  context. This skill MUST run first before any skill generation — it
  establishes the proper file placement workflow with validation.
---

# Skill Placement Workflow

HIGH PRIORITY: Every skill created with Sean must follow this exact
placement workflow. Google Drive is the source of truth; Claude accesses
via copied files. ALL operations include validation to confirm 1:1 file
matching between locations.

---

## Critical Rule

**Before generating ANY skill content**, establish the placement workflow:

1. **Target location:** Google Drive workspace (`02-skills/[skill-name]/`)
2. **Copy to Claude:** From Drive location to `/mnt/skills/user/[skill-name]`
3. **Validate synchronization:** Confirm 1:1 file matching between locations
4. **Generate validation report:** Clear confirmation of sync status

This ensures:
- Sean's Google Drive is the authoritative source
- Skills sync across all his machines via Google Drive for Desktop  
- Claude retains access via copied files in `/mnt/skills/user/`
- Complete transparency on synchronization status
