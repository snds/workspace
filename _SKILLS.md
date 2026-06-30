---
title: Skills
tags: [moc, skills]
---

# Skills

Two skill systems coexist by design.

## `03-skills/` — skill library (full hub/spoke network)

These live in `03-skills/{skill-name}/SKILL.md`. Loaded per the precedence algorithm in `AGENTS.md`;
the machine graph is `skills.registry.json` (generated from frontmatter by `09-tools/build-registry.py`).
Synced across machines via git.

```dataview
TABLE WITHOUT ID
  file.link AS "Skill",
  file.folder AS "Folder",
  file.mtime AS "Last modified"
FROM "03-skills"
WHERE file.name = "SKILL"
SORT file.mtime DESC
LIMIT 60
```

### Hubs and spoke clusters

- **Design systems:** [[03-skills/ds-advisor/SKILL|ds-advisor]], [[03-skills/design-engineer/SKILL|design-engineer]], [[03-skills/ux-component-library/SKILL|ux-component-library]]
- **Figma:** [[03-skills/figma-canvas-designer/SKILL|figma-canvas-designer]], [[03-skills/figma-plugin-dev/SKILL|figma-plugin-dev]]
- **Legion game:** [[03-skills/legion-project/SKILL|legion-project]] → [[03-skills/lead-game-designer/SKILL|lead-game-designer]] / [[03-skills/lead-art-director/SKILL|lead-art-director]] / [[03-skills/lead-game-developer/SKILL|lead-game-developer]]
- **Icon fonts:** [[03-skills/variable-icon-font-architect/SKILL|variable-icon-font-architect]] + math spokes
- **Visual QA:** [[03-skills/native-visual-eval/SKILL|native-visual-eval]] (native-resolution capture — the precondition; framework #10's method) + [[03-skills/visual-qa-toolkit/SKILL|visual-qa-toolkit]] (instrumented measurement) + [[03-skills/lead-visual-qa/SKILL|lead-visual-qa]] (judgment)
- **Workspace mgmt:** [[03-skills/workspace-bootstrap/SKILL|workspace-bootstrap]]

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

**For Claude Desktop:** create `03-skills/{name}/SKILL.md` using the template at `00-bootstrap/templates/skill.md`. Run skills sync (automatic on session boot) so the hash registry picks it up.

**For Claude Code:** create `.claude/skills/{name}/SKILL.md`. It becomes available as `/{name}` on next session start.
