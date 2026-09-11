---
name: artifact-ingest
description: >
  Land vendor Canvas/Artifact/HTML-preview content in the git-tracked workspace
  instead of a vendor cloud. Write-through first (filesystem agents write the vault
  file). Harvest when bytes already exist outside git: Cursor canvases via
  cursor-externalize.py; clipboard, a downloaded file, or 05-artifacts/inbox/ via
  artifact-ingest.py. Use when Sean says "vendor artifact", "llm canvas",
  "chatgpt canvas", "claude artifact", "html artifact", "clipboard ingest",
  "externalize canvas", or "artifact ingest". Not Figma canvas work. Not research
  JTBD/persona artifacts.
aliases: [artifact-ingest]
triggers:
  - vendor artifact
  - llm canvas
  - chatgpt canvas
  - claude artifact
  - html artifact
  - clipboard ingest
  - externalize canvas
  - artifact ingest
tier: cross-cutting
domain: workspace
related: [workspace-bootstrap, close-out]
governed_by: []
surfaces: ["*"]
rigor_role: load-chain
spec_version: "2.2"
---

# Artifact ingest — vendor panels are not the source of truth

Brings Claude Artifacts, ChatGPT/Gemini canvases, HTML previews, and Cursor
`.canvas.tsx` files into the vault. Doctrine: [[decision-vendor-surface-artifacts]]
+ the vendor-surface row in [[workspace-ontology]].

L4 connective tissue over two CLIs. Not a command hub — close-out SKIP is honest
unless some other hub was producing.

## When to use
Sean wants a vendor canvas/artifact/HTML preview in the workspace. Clipboard paste.
Drop-folder. Session-end harvest of Cursor canvases. "Don't leave this in ChatGPT."

## When NOT to use
- Figma canvas / component sets → [[figma]] / `$FIGMA_GENERATE_ROUTE`
- Research JTBD/persona/journey artifacts → `$ARTIFACT_ROUTE`
- Scraping claude.ai / chatgpt.com / Gemini
- Employer (`c8/*`, `cpes-software`) canvases — never into `snds/workspace`

## Behavior

1. **Write-through first.** If this surface can write files, write the vault path as
   the original (`05-artifacts/` or owning `07-projects/NN-*/`, named per
   [[artifact-standards]]). HTML that is a rich deliverable stays HTML.
2. **Cursor `.canvas.tsx` is dual-home.** Live compile path stays
   `~/.cursor/projects/<slug>/canvases/`. Then:
   `python3 09-tools/cursor-externalize.py`
   `--check` exits 1 on vault drift or an unmapped named slug. Employer, Legion,
   ephemeral windows, and `flavours-` / `guided-setup-` prefixes skip (not a fail).
3. **Already-copied bytes** (clipboard, download, drop):
   ```
   python3 09-tools/artifact-ingest.py --from-clipboard [--context X] [--descriptor Y] [--project 19-workspace-brain]
   python3 09-tools/artifact-ingest.py --from-file PATH
   python3 09-tools/artifact-ingest.py --inbox
   python3 09-tools/artifact-ingest.py --check
   ```
   Drop folder is `05-artifacts/inbox/` (gitignored). `--check` at session-end
   reports pending files; it does not promote. Secret-scan refuses the write.
4. **Web / no-FS:** emit a copy-ready fenced block plus a suggested
   `context_descriptor_vN.N_YYYY-MM-DD.ext` path. Do not scrape.

## Outputs
A vault file (or a copy-ready block). Cursor harvest copies under
`07-projects/…/canvases/`. Inbox promotions land in `05-artifacts/active/` unless
`--project` / `--out` is set.

## Related
- peer ↔ [[workspace-bootstrap]]
- peer ↔ [[close-out]]
