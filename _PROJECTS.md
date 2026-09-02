---
title: Projects
tags: [moc, projects]
---

# Projects

All projects under `07-projects/`. Active ones also registered in [[06-context/project-context]].

## Active

```dataview
TABLE WITHOUT ID
  file.link AS "Project",
  status AS "Status",
  join(triggers) AS "Triggers",
  file.mtime AS "Last touched"
FROM "07-projects"
WHERE type = "project"
  AND (status = "Active" OR status = "Planning")
SORT file.mtime DESC
```

## Paused / Archived

```dataview
TABLE WITHOUT ID
  file.link AS "Project",
  status AS "Status",
  file.mtime AS "Last touched"
FROM "07-projects"
WHERE type = "project"
  AND (status = "Paused" OR status = "Archived")
SORT file.mtime DESC
```

## All project folders (fallback — includes unregistered)

```dataview
LIST
FROM "07-projects"
WHERE file.folder = file.link.folder AND file.name = "README"
SORT file.folder ASC
```

## Create a new project

In Claude Code, run `/new-project`. It scaffolds the folder, seeds SESSION-STATE, registers it
in `06-context/project-context.md`, and this MOC picks it up automatically on next refresh.

## Graph index (static — Dataview does not create graph edges)

Path-qualified so colliding stems (`SESSION-STATE`, `README`) resolve. Folders with neither file stay off this list on purpose.

- [[07-projects/00-obsidian/SESSION-STATE|00-obsidian]] · [[07-projects/00-obsidian/README|00-obsidian README]]
- [[07-projects/01-mediaservices/SESSION-STATE|01-mediaservices]]
- [[07-projects/02-centricPLM/SESSION-STATE|02-centricPLM]] · [[07-projects/02-centricPLM/README|02-centricPLM README]]
- [[07-projects/03-omni/README|03-omni]]
- [[07-projects/04-claude-figma-plugin/README|04-claude-figma-plugin]]
- [[07-projects/05-C8-PLM/README|05-C8-PLM]]
- [[07-projects/09-figma-repo-sync-plugin/SESSION-STATE|09-figma-repo-sync-plugin]]
- [[07-projects/10-centric-UX-research/SESSION-STATE|10-centric-UX-research]]
- [[07-projects/13-legion/SESSION-STATE|13-legion]]
- [[07-projects/14-variable-icon-font-generator/SESSION-STATE|14-variable-icon-font-generator]]
- [[07-projects/15-DavinciRemake/README|15-DavinciRemake]]
- [[07-projects/16-CDS Figma-Code Audit/SESSION-STATE|16-CDS Figma-Code Audit]]
- [[07-projects/18-bootstrap-generator/SESSION-STATE|18-bootstrap-generator]] · [[07-projects/18-bootstrap-generator/README|18-bootstrap-generator README]]
- [[07-projects/19-workspace-brain/SESSION-STATE|19-workspace-brain]] · [[07-projects/19-workspace-brain/README|19-workspace-brain README]]
- [[07-projects/20-lcars-generative-interface/SESSION-STATE|20-lcars-generative-interface]] · [[07-projects/20-lcars-generative-interface/README|20-lcars README]]

## Notes

- Legacy projects (those without `type: project` frontmatter in their README) won't appear in the Dataview tables. Run `/new-project` or manually add the frontmatter to register them.
- Status values: `Planning`, `Active`, `Paused`, `Archived`. Stick to these for the queries to work.
- Obsidian graph edges come from `[[wikilinks]]` (and markdown links to `.md` files), not from Dataview. Use the Graph index above when a project looks like an island.
