---
tags: [language, writing, terminology, design-systems]
created: 2026-09-14
updated: 2026-09-29
status: stable
confidence: high
related_skills: [ds-advisor, design-engineer, plain-voice]
relations:
  relates-to: ["[[decision-pattern-uniqueness]]", "[[canonical-documentation]]"]
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

## Chat and plans (2026-09-29)

Plans, reviews, and explanations *to Sean* use the same bar as the terminology table, plus
the packaging in `04-preferences/user-preferences.md` → Response Style.

1. **TL;DR** — one sentence. What is true, or what to do.
2. **Explain** — short sentences, one idea each. Design-system vocabulary stays. Engineering
   vocabulary (stacking, CI, pin, overlay, git SHA) is defined in ordinary words the first
   time: what it *does*, then the name.
3. **Detail** — file names, class strings, and test assertions after the picture is clear.

Anti-pattern: a plan that leads with `z-[200]`, `belowSearch`, and “Pages clones main” before
saying the picture opens behind the sheet.

Full audience model: `02-shared-references/delivery-playbooks/01-audience-contract.md`.
Skill: [[plain-voice]].
---
