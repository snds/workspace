---
tags: [design-systems, documentation, examples, patterns]
created: 2026-09-14
updated: 2026-09-14
status: validated
confidence: high
related_skills: [ds-advisor, design-engineer]
relations:
  builds-on: ["[[davinci-ds-boilerplate]]"]
  relates-to: ["[[plain-language]]", "[[decision-pattern-uniqueness]]", "[[ai-and-design-systems]]"]
trigger_words:
  - documentation
  - live example
  - docs dump
  - pattern docs
  - visual documentation
  - Storybook embed
---

# Visual-first documentation

## For future agent

- **TL;DR:** A definition without a picture is unfinished. Docs show the thing with live components (or a labeled schematic of live primitives). Prose captions the picture. Do not ship a table of names as the example. **As of:** 2026-09-14 · **Status:** current
- Applies to design-system docs, specs, pattern catalogs, and any other documentation an agent writes for Sean — not only CDS.

## Rule

Every named thing on a docs page (component, pattern, template, encoding, variant, usage) has a visual within one scroll of its name. The reader should be able to tell the jobs apart without reading the domain nouns — same uniqueness test as [[decision-pattern-uniqueness]].

Text is the caption, the when-not, and the arbitration. It is not the demonstration.

## Ladder (pick the highest that is honest)

1. **Live instance** of the shipping component, in the docs app, on the page (tokens, theme, real interaction). This is the default. Chart galleries and in-page Dialogs beat an iframe.
2. **Live composition** of shipping primitives when the named thing is a pattern or page template, not a single component. Dialog + Field, Tabs + FilterChip, Data Summary on a property sheet. Label the parent and the body.
3. **Labeled schematic** when the pattern does not ship yet (Gantt schedule editing, print preview, a collection table that is not wired into docs). Build it from system tokens and primitives. Numbered pins that match the Anatomy list. Mark it **schematic** so it is not mistaken for a shipping component.
4. **Storybook embed** is a jump-out for the workbench (controls, states, a11y addon). It is not the only example. Iframes go blank when Storybook is down and they hide the composition in chrome.

Do not paste a screenshot of proto or centric-ui into system docs. Those go stale and they leak host product. Recreate the job with CDS pieces.

Do not invent a second library of hand-drawn shapes when a real component exists. Mortar, not a parallel kit ([[ai-and-design-systems]]).

## What this forbids

- A pattern or template page that is only tables, callouts, and code fences.
- Anatomy as a numbered list with no corresponding picture.
- "Form in a Dialog" explained in prose next to an empty Dialog story.
- Wire jargon or new names used as the illustration ([[plain-language]]).

## Docs-site shape (when the host is CDS / Fumadocs)

- One framed mini-surface per definition (`ExampleFrame` or equivalent): caption = the job; optional numbered overlays; optional schematic badge.
- Pair lookalikes when the page is teaching uniqueness (Dialog vs form-in-Dialog; Chart vs Gantt; collection table vs settings matrix).
- Keep Do/Don't as pictures when both states can be shown; one-line captions only.
- Code samples follow the live example, they do not replace it.

## Related

- [[davinci-ds-boilerplate]] — canonical DS docs IA still requires live preview; this entry is the enforcement when the page is a pattern or a definition.
- [[decision-visual-first-documentation]] — why this is standing, not a one-off CDS polish.
