---
title: Workspace-brain reports
status: active
date: 2026-08-07
---

# Reports

Durable copies of harness / mission audits and enrichment briefs for this project
(`07-projects/19-workspace-brain/`).

This folder is the tracked write path for workspace-brain reports. `05-artifacts/active/` is
gitignored and machine-local: a report written only there never reaches the other Mac, so a
report that should outlive the session lands here (versioned filename, never edited after the fact).

| Artifact | Filename pattern |
|---|---|
| [[harness-map]] | `harness-map_vN.N_YYYY-MM-DD.md` |
| [[mission-fit]] | `mission-fit_vN.N_YYYY-MM-DD.md` |
| Substack enrichment brief | `substack-enrichment-brief_vN.N_YYYY-MM-DD.md` |

## Finding a report

The index is the artifact registry, not a table here:
`python3 09-tools/artifact-find.py --path 19-workspace-brain/reports`.

A report is a dated snapshot. What happened to its recommendations afterwards lives in the
findings register [`../docs/INTENT-remediation-2026-09.md`](../docs/INTENT-remediation-2026-09.md),
never in an edit to the report's `status:` line (`validate-evidence-grades.py --status` checks it).

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
