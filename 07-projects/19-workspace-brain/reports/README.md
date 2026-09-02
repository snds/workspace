---
title: Workspace-brain reports
status: active
date: 2026-08-07
---

# Reports

Durable copies of harness / mission audits and enrichment briefs for this project
(`07-projects/19-workspace-brain/`).

Primary write path for skill reports remains `05-artifacts/active/` (versioned filenames).
Copy or dual-write here when the report should live beside the project for Obsidian
navigation.

| Artifact | Filename pattern |
|---|---|
| [[harness-map]] | `harness-map_vN.N_YYYY-MM-DD.md` |
| [[mission-fit]] | `mission-fit_vN.N_YYYY-MM-DD.md` |
| Substack enrichment brief | `substack-enrichment-brief_vN.N_YYYY-MM-DD.md` |

## Current reports

| File | Notes |
|---|---|
| [substack-enrichment-brief_v1.0_2026-08-07.md](./substack-enrichment-brief_v1.0_2026-08-07.md) | Nate + Curtis scan — pointers + landing suggestions only (no paywalled bodies) |

## `harness-map.stamp` convention

When a real [[harness-map]] report is written, also write/overwrite:

```
07-projects/19-workspace-brain/reports/harness-map.stamp
```

Format:

```
date: YYYY-MM-DD
report: <filename>
surface: <surface>
```

Session-start Notices (Claude dispatcher + Cursor `brain.mdc`) warn if the stamp’s
`date:` is **>30 days** old. **Silent if the stamp is missing** — no nag before the
first map. Do **not** invent a stamp for freshness; only write it when a map actually ran.
