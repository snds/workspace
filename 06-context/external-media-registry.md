---
title: External / Large-Format Media Registry
type: context
status: active
created: 2026-09-04
updated: 2026-09-04
tags: [media, reference, storage, pointers]
---

# External / Large-Format Media Registry

Large-format media (video, frame dumps, high-res render captures, big asset
packs) is **not** stored in the workspace repo — it bloats git history
permanently. Instead it lives on external/large-format storage, and **this file
is the tracked pointer** so any agent, on any machine, can find it when a task
needs it.

**How to use:** if a task references media that isn't on the local disk, look it
up here for its current location. When you move or add large media, update the
row here in the same change.

> Portable-first note: prefer a location any device can reach. A local path
> (e.g. Desktop) is a **staging** location; move to durable shared storage and
> update the row. Never make workspace logic *depend* on a cloud drive — this
> registry is a human/agent breadcrumb, not a runtime dependency.

## Registry

| Media | Project | Size | Current location | Status |
|---|---|---|---|---|
| Homeworld 2 — Campaign Ep 11 frame dump (art-direction reference, `interval_*.png`) | 13-legion | 455 MB | `~/Desktop/Legion-Reference-Media/Video/` (staging) | **Pending durable home** — Sean to provide GDrive/large-format destination; update this row when moved |

## Pending

- **13-legion video reference** — currently staged on Personal MacBook Pro
  Desktop. Awaiting Sean's large-format storage destination (GDrive or other);
  update the location above once provided so other machines can resolve it.
