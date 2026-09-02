---
name: ds-source-watch
description: >
  Review upstream design-system and agentic-spec sources for drift against this
  workspace's ontology, DSDS constitution, context model, and implementation
  engineering. Trigger on "source watch", "ds source watch", "latest ds thinking",
  "refresh ds ontology sources", "Onori", "Nathan Curtis latest", or when
  /optimize flags a stale ds-source-watch snapshot. Report-first: never auto-edit
  the ontology from a fetch.
aliases: [ds-source-watch]
triggers:
  - source watch
  - ds source watch
  - latest ds thinking
  - refresh ds ontology
  - refresh ds sources
  - pj onori
  - onori
tier: spoke
domain: design
hub: ds-advisor
prerequisites: [ds-advisor]
related: [design-system-ops, harness-map]
surfaces: ["*"]
spec_version: "2.2"
rigor_role: measurement
defers_to: [ds-advisor, framework-09]
---

# DS source watch

Keeps the project-independent DS constitution honest against the field. Fetches a
curated source list, diffs hashes, and recommends vault writes. It does not apply
those writes.

**Audience:** `for: agent`

## For future agent
- **TL;DR:** `python3 09-tools/ds-source-watch.py --fetch` then judge. Ontology
  edits stay human-gated.
- **As of:** 2026-09 · **Status:** current

## Pipeline

1. **Check** — `python3 09-tools/ds-source-watch.py --check` (no network). P1 if
   the snapshot is older than `stale_days` (30) or missing.
2. **Fetch** — `--fetch`. Updates
   `07-projects/19-workspace-brain/reports/ds-source-watch/latest.json`.
3. **Judge** — for each `changed` or `new` row, read the URL, then decide whether
   the vault must move. Map `affects` to the layer:

   | affects | First file to open |
   |---|---|
   | ontology | [[workspace-ontology]] · [[idempotent-design-decisions]] |
   | dsds | [[dsds-constitution]] + the YAML beside it |
   | specs | [[component-contracts-and-schemas]] · [[component-contract-schema]] |
   | context | [[agentic-ds-context-model]] |
   | harness / agentic | [[agentic-error-correction-foundations]] · this skill's report |

4. **Write** only after Sean (or the session owner) signs off. Prefer additive
   knowledge + a DSDS `$extensions` note over rewriting laws.
5. **Refuse** — auto-editing ontology from a hash change; treating a marketing
   page rewrite as a schema change; importing another system's tokens because a
   source showed them.

## Done-gates

- `--check` or `--fetch` actually ran (transcript is not proof).
- Every `changed` / `failed` row has a recommend / ignore / blocked note.
- No constitution, ontology, or knowledge file was edited unless the user asked.

## Registry

Source of truth: `02-shared-references/ds-source-watch.json`. Add a source there
when a writer (Onori, Curtis, Wolosin, Anthropic, Google A2A/A2UI, etc.) becomes
load-bearing. Do not scrape the open web into the ontology.

## Related
- hub → [[ds-advisor]]
