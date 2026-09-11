---
title: Hyper-Personalized Website Browser Plugin Demo
section: "Chapter 5: Inventing the Future with AI & Design Systems"
source: https://courses.bradfrost.com/courses/take/ai-design-systems-course/lessons/77895551-hyper-personalized-website-browser-plugin-demo
duration: ~13m51s
status: noted
as-of: 2026-09-10
---

# Hyper-Personalized Website Browser Plugin Demo

Working title **Burndown** — talk to a site, apply prefs, persist. Half-hour prototype; the point is *users* can do this. LLM writes CSS/JS into **localStorage**; styles travel page to page (Steel Curtain Wikipedia → Steelers → NFL stays GeoCities).

**Rebuild with Eddie:** Nike homepage swapped to Eddie header/hero/feature blocks/footer; then he can flip **dark / Wowee Zowee / Altitude** and hit “everything.” Plugin points at **Eddie MCP**, maps live HTML → Eddie components. Full rebuild is page-by-page (unlike tack-on CSS). Same trick as a **legacy-adoption preview** (Atomic Design course site in a minute) — also a bug-finder for Eddie.

**A11y:** Who Can Use → Target with “I have protanopia” → reds shift; user then picks blue; Add to Cart stays blue. Not perfect; iteration locks the experience. **ADHD / noise:** Amazon PDP + **Death to Bullshit** (2013 talk) nukes header/footer/nav/sponsored junk; leftover ads get a manual ID remove. Next PDP inherits the sculpt.

Parlor trick *and* user-in-control of experiences orgs have been subjecting them to. May never ship the plugin.

**For Sean:** client-side DS restyle ≠ production adoption — but it’s a cheap “what would this look like on Eddie/Centric” conversation, and a reminder users will personalize whether you designed for it.
