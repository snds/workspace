---
title: Rendered emphasis vs coded emphasis (text levels)
status: living
updated: 2026-10-20
related: [brand-text-vs-fill]
---

# Rendered emphasis vs coded emphasis

**Contrast checks validate the coded colour; the eye reads the drawn pixels.** Measured in WebKit (the
Mac app engine) across the workspace app on Unicron 0.14, about 2.3k text runs and icons, light and dark:

- **One low ink means one low level.** With only `foreground` and `muted-foreground`, seven
  low-emphasis jobs (overline, support text, meta, inactive tab, empty-state text, a key on a fill,
  muted icons) drew within 6 Lc of each other in light (67–73) and 4 in dark (72–76). Hierarchy
  needs discrete levels about 12–15 Lc apart *drawn*; two inks can't give three levels.
- **Rendering takes contrast off small type unevenly.** Antialiasing cost 10–12 Lc on 11–13 px muted
  text in light, 6–8 on 14 px primary, and only 4–6 in dark (light strokes on dark spread). So dark
  mode draws muted text closer to primary than the tokens say.
- **Size and weight cancel ink.** An 11 px weight-600 caps overline draws as strong as 13 px
  weight-400 support text. Icons have heavier strokes than text, so a muted icon draws 2–3 Lc above
  muted text: tie the icon font's weight axis to the text level it sits with.
- **Opacity stacking was not the cause** here: only disabled controls (50%) were drawn through an
  opacity, and no text used a translucent ink.

**Rule of thumb:** under APCA Bronze (Lc 75 for text under 16 px), the room between the floor and
primary text (~106) holds three levels (≈81 / 93 / 106 coded, ≈70 / 84 / 98 drawn). Use all three,
give each text role one level, and check separation on drawn pixels, not only floors on coded pairs.

Tool: the workspace app repo's `scripts/emphasis-audit.swift` (WebKit, reads glyph pixels) and
`scripts/emphasis-audit.mjs` (APCA per role). Emphasis Engine's own levels are `--<role>-text-1…5`
(minimal → maximal; Lc 45/60/75/90/100 light, 45/60/75/85/90 dark).
