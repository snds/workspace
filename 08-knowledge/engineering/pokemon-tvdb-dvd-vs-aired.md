---
tags: [engineering, media-library, plex, tvdb, pokemon]
created: 2026-09-03
updated: 2026-09-03
status: working
confidence: high
sources: [session 2026-09-03 MediaSentinel / Unraid library]
related_projects: [01-mediaservices, MediaSentinel]
---

# Pokémon season order: TVDB DVD vs aired, and production numbers

The ColdFusion English-dub pack uses content-type folders, not seasons. Its `02x28`-style codes
are **production numbers**. Feeding them to a season parser files Orange Islands (and later arcs)
into the wrong TVDB season.

Map from **folder context + TheTVDB DVD / English** order onto
`Pokémon (1997) {tvdb-76703}`. Spinoffs are separate series (Chronicles, Origins, Generations,
Twilight Wings, Evolutions, Hisuian Snow, Mystery Dungeon).

**Plex/Emby default aired order is wrong for this library.** Aired now maps Season 20 of the
1997 show to Horizons. The Ash saga through Journeys is DVD order. Set the show to
**TheTVDB (DVD)** before copying files onto Unraid. Do not leave Horizons files in
`Pokémon (1997) {tvdb-76703}/Season 20`.

Unraid already had a mixed `Season 1` / `Season 01` / Horizons-in-S20 tree. Treat that as
cleanup, not a merge target, when landing the Desktop pack.

Substance and folder map: `07-projects/01-mediaservices/SESSION-STATE.md`.
