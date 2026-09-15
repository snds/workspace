---
tags: [documentation, language, design-systems, fumadocs]
created: 2026-09-15
updated: 2026-09-15
status: validated
confidence: high
related_skills: [canonical-docs-voice, ds-advisor, design-engineer]
relations:
  builds-on: ["[[visual-first-documentation]]", "[[plain-language]]"]
  relates-to: ["[[davinci-ds-boilerplate]]"]
trigger_words:
  - changelog note
  - canonical documentation
  - because the docs app
  - schematic here
  - docs voice
  - live example gap
---

# Canonical documentation

## For future agent

- **TL;DR:** Canonical documentation describes the system. It never explains why the docs site could not host a live example. If a shipping component needs a peer, add the peer to the docs app. Changelog voice belongs in changelogs. **As of:** 2026-09-15 · **Status:** current
- Skill: [[canonical-docs-voice]]. Picture ladder: [[visual-first-documentation]]. Word choice: [[plain-language]].

## Rule

A component page is the contract a product team reads. A sentence about the docs app's missing dependency, a "for now" schematic, or "the real one is in Storybook because we couldn't…" is a changelog note. It ages badly and it trains the next writer to document gaps instead of closing them.

| Surface | Voice |
|---|---|
| Title description (under the H1) | What it is, in product language. One line. |
| Component / pattern / foundation page | What it is, when to use it, how it behaves. Live instance. |
| Code tab | How to import and configure it (optional peer, height, subpath). |
| Changelog / PR / story comment | What changed in the docs host, and why. |

## Host gap → fix the host

[[visual-first-documentation]] ladder: live instance → live composition → labeled schematic → Storybook jump-out.

Schematic is honest when **the named thing does not ship** (or lives in a package this page is not mounting). It is dishonest when the component ships and the docs app simply omitted a peer (`@xyflow/react` for Flow Canvas is the type specimen). Then:

1. Add the peer (or package) to the docs app.
2. Import the CSS the component already imports.
3. If the engine cannot SSR (React Flow measures its container), load it client-only (`next/dynamic` `{ ssr: false }`) and give the frame a height.
4. Caption the job. Do not mention the former gap.

## What this forbids

- "The live example is a schematic… because the docs app does not take [peer]."
- Captions that say "in product, schematic here."
- Body copy that points at Storybook as the place the *real* component lives, except as the Open-menu workbench jump-out.
- "Until we wire X", "for now", "workaround" on a catalog page.
- A title description that is a consume note: optional peer, subpath import, package name, "not RHF".

## Related

- [[visual-first-documentation]] — the picture is the demonstration
- [[plain-language]] — ordinary words; this entry is ordinary *stance*
- [[canonical-docs-voice]] — the skill that loads this rule
