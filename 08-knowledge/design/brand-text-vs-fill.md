---
title: Brand text vs brand fill (primary-text)
status: living
updated: 2026-09-15
related: [interaction-state-semantics, radix-derived-color-system, figma-component-token-axes]
---

# Brand text vs brand fill

`action/primary` / `--sem-primary` is **Blue/10** — a solid **fill** stepped for white-on-brand APCA.
It is **not** a text color on tinted surfaces (Blue A4/A5 selected/hover washes).

Radix text roles are steps **11–12**. Selected nav text uses **Blue/11** (aligned with soft status `*-soft-foreground`).

| Token | Primitive | Role |
|---|---|---|
| `action/primary` / `--sem-primary` | Blue/10 | Solid brand fill |
| `action/primary/foreground` / `--sem-primary-foreground` | inverted white | Text **on** solid primary |
| `action/primary-text` / `--sem-primary-text` | Blue/11 | Brand text on tinted/neutral surfaces |
| `action/primary/soft` / `--sem-primary-soft` | Blue/3 | Brand-soft fill (chips, tinted brand chrome) |
| `action/primary/soft/foreground` / `--sem-primary-soft-foreground` | aliases `primary-text` (Blue/11) | Text/icon on brand-soft |
| `action/primary/soft/border` / `--sem-primary-soft-border` | Blue/6 | Border on brand-soft |

Consumers of selected/hover wash foregrounds (`interaction/selected/foreground`,
`sidebar/accent/foreground`, `chrome/selected/foreground`, …) alias
`action/primary-text`, **not** `action/primary`.

Brand-soft uses the same 3 / 11 / 6 recipe as status-soft, **in the brand hue**. Do not
paint brand-tinted chrome with `info-soft` (cyan). Hover wash on a labelled value is
`interaction/primary/hover` (Blue A4), not the chip fill.

Code consumes Tailwind semantic utilities (`bg-primary-soft`). Do not mint `--object-chip-*`
CSS vars. Figma component Color collections alias these semantics; WEB syntax is
`var(--sem-primary-soft*)` so both surfaces publish one map.

Changed 2026-08-05 in centric-ui, saas-plm-prototype, and Figma DS
`o6o1ZuGHxDow2vHLuYXT6X` (initially Blue/12, then Blue/11). Brand-soft pair added
2026-09-15 (cds + same Figma file).
