---
tags: [design-systems, color, theming, tokens, shadcn, emphasis-engine]
created: 2026-10-08
updated: 2026-10-08
status: working
confidence: high
sources: [emphasis-engine hand profile src/engine/profiles/shadcn.ts, src/app/preview.tsx, probe report docs/probes/shadcn.md]
related_skills: [ds-advisor, design-engineer]
related_projects: [emphasis-engine]
relations:
  relates-to:
    - "[[ds-native-theming-survey]]"
    - "[[radix-derived-color-system]]"
---

# shadcn/ui — how its color works, learned by theming it

## For future agent
- **TL;DR:** About 30 flat semantic variables (`--background`, `--primary`, `--muted`, `--border`, `--input`, `--ring`, …). There are no state tokens: components make hover, press, and soft fills with Tailwind opacity modifiers (`bg-primary/90`, `bg-destructive/10`) and `color-mix()`. So contrast depends on what's underneath.
- **Key claims:** below. Verified by the component probe and a hand-written profile of 31 recipes.
- **As of:** 2026-10-08 · **Status:** current
- **Audience:** `for: all`

## At a glance
- shadcn/ui is copied into the app, not installed. This app uses the base-nova preset on Base UI primitives with Tailwind v4.
- License: MIT. Docs: ui.shadcn.com/docs/theming.

## How its color works
- **One flat tier.** Variables are named by job: `background`, `card`, `popover`, `primary`, `secondary`, `muted`, `accent`, `destructive`, `border`, `input`, `ring`, `chart-1..5`, `sidebar-*`. Each fill has a `-foreground` partner.
- **Modes:** a `.dark` class on `<html>` swaps the whole set. The values are OKLCH literals.
- **States come from opacity, not tokens.** Primary hover is `primary/90`. Destructive soft fills are `destructive/10` (`/20` in dark). Inputs in dark mode are `input/30`. Focus rings are `ring/50`. A brand that's fine at rest can fail once it's thinned over a card.
- **Shared variables do double duty.** `--input` is both the field border and the dark field fill. `--accent` is the hover surface, not a brand accent. Retheming one job moves the other.
- **Muted vs. card:** in stock dark, `muted` and `card` sit very close. Profile recipes are needed to keep them apart.

## Building the native page
- shadcn is the app's own component kit, so its preview renders inside the app with scoped CSS variables. No iframe is needed. The other 12 systems get iframe pages ([[ds-native-theming-survey]]).

## What the solved theme reaches
- Everything. Every component reads the variables. The only gap is states built from opacity: the solver has to account for the alpha, and does, through recipes.

## Accessibility notes
- Stock field borders sit near 1.3:1, under WCAG 1.4.11's 3:1 for control edges.
- The dark primary sits near Lc 12 against the page.
- The focus ring at 50% can miss 3:1 over a card.
- The app's "Force accessibility" switches exist because of these three.

## Ideas for the Centric design system
- **Avoid opacity as the state model in dense tables.** `/90` and `/10` change contrast with whatever row color is underneath.
- **Avoid one variable serving two jobs** (`--input` as border and fill). Split it in the semantic tier.
- **Borrow the `-foreground` pairing.** It's simple, and every framework can read it.
