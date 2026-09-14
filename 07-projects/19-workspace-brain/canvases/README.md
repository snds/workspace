---
title: Cursor canvas copies
---

# Cursor canvases (vault copies)

Cursor only compiles `.canvas.tsx` from the machine-local folder
`~/.cursor/projects/<slug>/canvases/`. That folder is **not** this git tree.

These files are copies so the content travels with `snds/workspace`. This
checkout's Cursor window compiles from
`~/.cursor/projects/Users-sean-sands-Projects-workspace/canvases/` (or
`Users-snds-Projects-Workspace` on the other Mac). Recents can still list
canvases that live under a parent `~/Projects` slug — harvest now mirrors
vault copies into this window's live folder so they open here.

Sync (session-end on Cursor):

```
python3 09-tools/cursor-externalize.py
python3 09-tools/cursor-externalize.py --check
```

`--check` fails on unmapped named slugs. Legion / ephemeral windows skip.
Employer canvases do not land here — they copy into that repo's `canvases/`.
Clipboard or a dropped file:
`python3 09-tools/artifact-ingest.py --from-clipboard` / `--inbox`.

Routing: workspace-brain canvases land here; `lcars-*` go to
`07-projects/20-lcars-generative-interface/canvases/`; MediaSentinel analysis
canvases go to `07-projects/01-mediaservices/canvases/`. Legion canvases stay
with the Legion repo, not this vault. Centric canvases go to that repo's
`canvases/` directory, never this vault.
