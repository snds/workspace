---
tags: [language, writing, terminology, design-systems]
created: 2026-09-14
updated: 2026-09-14
status: stable
confidence: high
related_skills: [ds-advisor, design-engineer]
relations:
  relates-to: ["[[decision-pattern-uniqueness]]"]
trigger_words:
  - chassis
  - lateral terminology
  - plain language
  - jargon
  - parent component
  - usage versus variant
---

# Plain language — prefer the ordinary word

## For future agent

- **TL;DR:** Use words the reader already has. Do not invent sideways terms that are more precise on paper and foggier in use. This is general, not design-systems-only.
- **As of:** 2026-09-14 · **Status:** current

## Rule

If "dialog," "parent component," "usage," or "variant" will do, do not say "chassis," "coordinated-view paradigm," or a freshly coined synonym. Efficiency of jargon is not worth the fog.

Name the thing by what the user does, then by the component they can open in the library. Keep specialist vocabulary for tokens, variants, states, anatomy, and slots — those already have jobs.

## Examples

| Fog | Prefer |
|---|---|
| Overlay chassis | Dialog (header, body, optional footer) |
| Host composition | A page made of Tabs + a table + a confirm |
| Coordinated-view paradigm | Chrome: a control cluster that changes a content cluster |
| Document sheet | Print preview (page or a gated region) |

Applies in chat, docs, specs, and canvas labels. Same bar in engineering and PM writing.
---
