---
type: decision
description: When two UIs are different patterns vs a usage or variant of one parent component
created: 2026-09-14
confidence: high
relations:
  builds-on: ["[[decision-component-pattern-framework-system]]"]
  relates-to: ["[[enterprise-saas-design-patterns]]", "[[plain-language]]", "[[visual-first-documentation]]"]
---

## For future agent

- **TL;DR:** If a person can tell the jobs apart without reading the domain nouns, they are different patterns. If they share a parent component (Dialog, a property sheet, a chart type), that is a usage or variant — not a new pattern. Do not invent sideways terms for this. **As of:** 2026-09-14 · **Status:** current

## Decision

**Uniqueness.** Different user jobs with different anatomy and interactions are different patterns — even if they both contain rows, fields, or a toolbar.

**Composition.** Sharing a parent component is not uniqueness. A form in a Dialog is Dialog used as a form. A Gantt *plot* can be a Chart type named `gantt` while the Gantt *pattern* still owns schedule editing (drag, dependencies). A page that inventories, applies, and lists runs is Tabs + collections + a confirm, not a new pattern.

**One-offs.** A screen with no repeating corollary stays host-local (a snowflake). Do not force it into a pattern until the anatomy repeats.

**Chrome.** A control cluster that changes a content cluster is one paradigm. Variants are named by intent and placement: table of contents, sidebar navigation, left-panel pivots, top-tab pivots, filters / named views. Preferences (density, theme) are not this paradigm.

## Rejected

- Collapsing by visual rhyme (rows → table, fields → record, Apply → form).
- Treating an empty Dialog as its own pattern beside "form dialog."
- One mega-pattern that erases those chrome variants.
---
