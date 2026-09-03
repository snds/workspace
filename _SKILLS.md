---
title: Skills
tags: [moc, skills]
---

# Skills

Two skill systems coexist by design.

## `03-skills/` — skill library (full hub/spoke network)

These live in `03-skills/{skill-name}/SKILL.md`. 292 skills in the generated graph.
Loaded per the precedence algorithm in `AGENTS.md`; the machine graph is
`skills.registry.json` (generated from frontmatter by `09-tools/build-registry.py`).
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

- **Domain rigor (meta):** [[01-frameworks/13-domain-rigor-stack|framework #13]] — mandatory L1–L5 for any new/improved hub
- **Design systems:** [[03-skills/ds-advisor/SKILL|ds-advisor]], [[03-skills/design-engineer/SKILL|design-engineer]], [[03-skills/design-system-ops/SKILL|design-system-ops]], [[03-skills/ux-component-library/SKILL|ux-component-library]]
- **Figma:** [[03-skills/figma-canvas-designer/SKILL|figma-canvas-designer]], [[03-skills/figma-plugin-dev/SKILL|figma-plugin-dev]]
- **Engineering:** [[03-skills/eng/SKILL|eng]] → leads + [[03-skills/arch-guild/SKILL|arch-guild]]; mobile via [[03-skills/lead-mobile-engineer/SKILL|lead-mobile-engineer]]
- **Security:** [[03-skills/lead-security-architect/SKILL|lead-security-architect]] → `sec-*` (framework #16)
- **Accessibility:** [[03-skills/lead-accessibility-architect/SKILL|lead-accessibility-architect]] + [[03-skills/a11y-audit-toolkit/SKILL|a11y-audit-toolkit]]
- **Analysis / DS / PM:** framework #15 → [[03-skills/lead-data-scientist/SKILL|lead-data-scientist]] / [[03-skills/lead-product-manager/SKILL|lead-product-manager]]
- **Legion game:** [[03-skills/legion-project/SKILL|legion-project]] → [[03-skills/lead-game-designer/SKILL|lead-game-designer]] / [[03-skills/lead-art-director/SKILL|lead-art-director]] / [[03-skills/lead-game-developer/SKILL|lead-game-developer]]
- **Realtime photoreal:** [[03-skills/realtime-visual-craft/SKILL|realtime-visual-craft]] + [[03-skills/render-qa-toolkit/SKILL|render-qa-toolkit]] + [[03-skills/interactive-capture-eval/SKILL|interactive-capture-eval]] + [[03-skills/rendering-guild/SKILL|rendering-guild]] (framework #12)
- **Icon fonts:** [[03-skills/variable-icon-font-architect/SKILL|variable-icon-font-architect]] + math spokes
- **Motion / display graphics:** [[03-skills/lead-motion-designer/SKILL|lead-motion-designer]] → [[03-skills/motion-graphic-systems/SKILL|motion-graphic-systems]] · [[03-skills/motion-programmatic-video/SKILL|motion-programmatic-video]] + implementation [[03-skills/motion/SKILL|motion]]; still craft via [[03-skills/lead-graphic-designer/SKILL|lead-graphic-designer]] → [[03-skills/gd-display-graphics/SKILL|gd-display-graphics]] · [[03-skills/gd-generation-tooling/SKILL|gd-generation-tooling]] (live SVG, not flattened plates). Law: [[display-graphic-motion-systems]]
- **Visual QA:** [[03-skills/native-visual-eval/SKILL|native-visual-eval]] (native-resolution capture — the precondition; framework #10's method) + [[03-skills/visual-qa-toolkit/SKILL|visual-qa-toolkit]] (instrumented measurement) + [[03-skills/visual-prove-engine/SKILL|visual-prove-engine]] (contract verdicts, altitudes A–G) + [[03-skills/play-prove/SKILL|play-prove]] (headless balance / feel) + [[03-skills/a11y-audit-toolkit/SKILL|a11y-audit-toolkit]] + [[03-skills/lead-visual-qa/SKILL|lead-visual-qa]] (judgment) + discipline lenses [[03-skills/visual-qa-dataviz/SKILL|visual-qa-dataviz]] · [[03-skills/visual-qa-motion/SKILL|visual-qa-motion]] · [[03-skills/visual-qa-type/SKILL|visual-qa-type]]
- **Measurement (instrumented, per substrate):** [[03-skills/visual-qa-toolkit/SKILL|visual-qa-toolkit]] (pixels) + [[03-skills/a11y-audit-toolkit/SKILL|a11y-audit-toolkit]] (DOM/WCAG) + [[03-skills/fe-perf-harness/SKILL|fe-perf-harness]] (CWV budgets) + [[03-skills/render-qa-toolkit/SKILL|render-qa-toolkit]] (rendered frames) — each degrades to a stated manual path rather than a silent pass
- **Career:** [[03-skills/career-ops-job-search/SKILL|career-ops-job-search]] (wrappers → `~/.agents/skills`)
- **Workspace mgmt:** [[03-skills/workspace-bootstrap/SKILL|workspace-bootstrap]] (session handshake) + [[03-skills/side-chat-handback/SKILL|side-chat-handback]] (`/handback` — side chat → parent inbox) + [[03-skills/open-agent-engine/SKILL|open-agent-engine]] (work movement — queue, ledger, receipts; lanes in [[06-context/open-engine/README|open-engine]]) + [[03-skills/harness-map/SKILL|harness-map]] (map the AI setup before cleaning) + [[03-skills/mission-fit/SKILL|mission-fit]] (jobs vs harness; false-success checks before trusting `done`)
- **Process plugins:** [[03-skills/process-plugins/SKILL|process-plugins]] (pstack/superpowers precedence)

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
