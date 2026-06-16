---
title: Skills
tags: [moc, skills]
---

# Skills

Two skill systems coexist by design.

## `02-skills/` — Claude Desktop skills (full hub/spoke network)

These live in `02-skills/{skill-name}/SKILL.md`. Loaded by Claude Desktop via the skills-plugin
mount. Synced across machines via `skills-manifest.json` hash check.

```dataview
TABLE WITHOUT ID
  file.link AS "Skill",
  file.folder AS "Folder",
  file.mtime AS "Last modified"
FROM "02-skills"
WHERE file.name = "SKILL"
SORT file.mtime DESC
LIMIT 60
```

### Hubs and spoke clusters

- **Design systems:** [[02-skills/ds-advisor/SKILL|ds-advisor]], [[02-skills/design-engineer/SKILL|design-engineer]], [[02-skills/ux-component-library/SKILL|ux-component-library]]
- **Figma:** [[02-skills/figma-canvas-designer/SKILL|figma-canvas-designer]], [[02-skills/figma-plugin-dev/SKILL|figma-plugin-dev]]
- **Legion game:** [[02-skills/legion-project/SKILL|legion-project]] → [[02-skills/lead-game-designer/SKILL|lead-game-designer]] / [[02-skills/lead-art-director/SKILL|lead-art-director]] / [[02-skills/lead-game-developer/SKILL|lead-game-developer]]
- **Icon fonts:** [[02-skills/variable-icon-font-architect/SKILL|variable-icon-font-architect]] + math spokes
- **Visual QA:** [[02-skills/visual-qa-toolkit/SKILL|visual-qa-toolkit]] (being built)
- **Workspace mgmt:** [[02-skills/workspace-bootstrap/SKILL|workspace-bootstrap]], [[02-skills/cowork-skills-sync/SKILL|cowork-skills-sync]]

## `.claude/skills/` — Claude Code slash commands

Invoked by `/name` from inside Claude Code. Small, focused workflow automations.

```dataview
TABLE WITHOUT ID
  file.link AS "Skill",
  description AS "Description"
FROM ".claude/skills"
WHERE file.name = "SKILL"
SORT file.name ASC
```

## Adding a skill

**For Claude Desktop:** create `02-skills/{name}/SKILL.md` using the template at `00-bootstrap/templates/skill.md`. Run skills sync (automatic on session boot) so the hash registry picks it up.

**For Claude Code:** create `.claude/skills/{name}/SKILL.md`. It becomes available as `/{name}` on next session start.
