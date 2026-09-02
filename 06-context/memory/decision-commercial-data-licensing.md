---
type: decision
description: Default to commercially-usable data/asset sources for all work; use non-commercial sources (e.g. Gaia DR3, CC-BY-NC) only when they uniquely provide needed data, and reconcile later.
created: 2026-06-14
confidence: high
---

Standing policy for **all** projects (surfaced first on Legion's galactic star map, but durable and general): prefer **commercially-licensable** data, datasets, and assets by default, so any project can go commercial without a licensing reckoning. Reach for a **non-commercial** source only when it uniquely offers data we genuinely need — and when we do, isolate it, mark it, and **reconcile later** (replace, relicense, or seek a commercial grant).

**Source licenses confirmed (2026-06-14):**
- **HYG database v3.8 / AT-HYG** (astronexus) — **CC-BY-SA 4.0** → commercial OK. Share-Alike binds the *derived data file* (attribute HYG; the catalogue derivative is CC-BY-SA), **not** the game/app code. This is Legion's star-catalogue base.
- **Gaia DR3** (ESA) — **CC-BY-NC 3.0 IGO** → non-commercial by default; ESA has a separate commercial-use terms process. Avoid shipping its catalogue; its *science* (e.g. exoplanet occurrence rates) is fine to use as method, not data.
- **NASA Exoplanet Archive / NASA / JPL / USNO** — US-government works → **public domain** → commercial OK. Preferred backfill for real exoplanet/system data.
- **Hipparcos / Tycho-2** (ESA) — freely usable; reach Tycho-2 via AT-HYG (CC-BY-SA) for a clean commercial chain.

**How to apply:** before ingesting any external dataset/asset, check its license; record it in the project's NOTICE/attribution. Default-allow: public-domain (gov), CC0, CC-BY, CC-BY-SA (with attribution; SA scoped to the data file). Default-deny for shipped data: CC-BY-NC, CC-BY-ND, "research/academic only," unstated. When a deny-list source is the only one with the data, quarantine it behind a clear marker and a reconcile-later note.

**Why:** Legion (and other projects) may commercialize; retrofitting licensing after building on NC data is costly and risky. Cheap to get right up front.

**Alternatives rejected:** (a) ship Gaia DR3 wholesale — best astrometry/coverage but CC-BY-NC blocks commercial use; (b) ignore licensing until launch — accrues hidden legal debt across the whole asset base.
