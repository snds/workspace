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

## Notes

- Legacy projects (those without `type: project` frontmatter in their README) won't appear in the Dataview tables. Run `/new-project` or manually add the frontmatter to register them.
- Status values: `Planning`, `Active`, `Paused`, `Archived`. Stick to these for the queries to work.
