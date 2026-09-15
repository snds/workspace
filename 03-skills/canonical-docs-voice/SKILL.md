---
name: canonical-docs-voice
description: >
  Voice and host-honesty for canonical documentation (Fumadocs, component pages,
  pattern catalogs, specs). Use when writing or editing docs pages, MDX, live
  examples, captions, or design-system documentation. Forbids changelog notes,
  "because the docs app couldn't…", and any caption that explains a site gap
  instead of the component. Fix the docs host so the live instance can ship.
aliases: [canonical-docs-voice, docs-voice, changelog-voice]
triggers:
  [
    documentation,
    fumadocs,
    mdx,
    live example,
    schematic,
    changelog note,
    canonical documentation,
    docs page,
    write docs,
    component docs,
    because the docs app,
  ]
tier: spoke
domain: design
hub: ds-advisor
prerequisites: [ds-advisor]
related: [design-engineer]
surfaces: ["*"]
spec_version: "2.2"
---

# Canonical docs voice

Canonical pages describe the **system**. They do not describe the docs site's
implementation debt.

Knowledge: [[canonical-documentation]] · [[visual-first-documentation]] · [[plain-language]]

## When to use

Writing or editing Fumadocs MDX, live examples, captions, pattern pages, or any
reader-facing catalog. Also when a live example is about to become a schematic
"for now."

## When NOT to use

Changelogs, PR bodies, session logs, commit messages, Storybook story comments,
migration notes. Those surfaces *should* say what changed and why.

## Behavior

1. **Write for the reader of the library**, not for the next agent debugging the
   docs app. Caption the job: what the user does with this component.
2. **Live instance is the default** ([[visual-first-documentation]]). If the
   component ships and the docs app is missing a peer, package, or CSS import,
   add that dependency. Do not document the gap.
3. **Schematic** is only for something that does not ship (or is a different
   package this page is not mounting). Mark it schematic. Still caption the
   *job*, never "schematic here because X is not in the docs app."
4. **Code tab** may list consume facts (optional peer, subpath import, required
   height). That is how to use it. It is not an apology.
5. **Never** put changelog voice on a canonical page: "for now", "until we…",
   "because the docs app does not…", "this used to be…", "Storybook has the real
   one because we couldn't."

## Forbidden (canonical pages)

> The live example is a schematic of the node sequence. The pannable canvas,
> MiniMap, and Controls live in Storybook because the docs app does not take
> the React Flow peer.

> Graph canvas — `@centric/ui/flow-canvas` in product, schematic here

## Prefer

> Style → colourway → sample — pan and zoom

Then show the live canvas. Storybook remains the args-panel jump-out in the
Open menu, not a substitute explained in the body.

## Related
- hub → [[ds-advisor]]
- peer ↔ [[design-engineer]]
