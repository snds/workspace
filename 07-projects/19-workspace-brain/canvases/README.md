---
title: Cursor canvas copies
---

# Cursor canvases (vault copies)

Cursor only compiles `.canvas.tsx` from the machine-local folder
`~/.cursor/projects/<slug>/canvases/`. That folder is **not** this git tree.

These files are copies so the content travels with `snds/workspace`. Open the live
canvas in Cursor from `~/.cursor/projects/…`; treat this folder as the portable
source of truth.

Sync (session-end on Cursor):

```
python3 09-tools/cursor-externalize.py
python3 09-tools/cursor-externalize.py --check
```

Routing: workspace-brain canvases land here; `lcars-*` go to
`07-projects/20-lcars-generative-interface/canvases/`; MediaSentinel analysis
canvases go to `07-projects/01-mediaservices/canvases/`. Legion canvases stay
with the Legion repo, not this vault.
