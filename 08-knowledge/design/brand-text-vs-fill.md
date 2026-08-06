---
title: Brand text vs brand fill (primary-text)
status: living
updated: 2026-08-05
related: [interaction-state-semantics, radix-derived-color-system]
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

Consumers of selected/hover wash foregrounds (`interaction/selected/foreground`,
`sidebar/accent/foreground`, `chrome/selected/foreground`, …) alias
`action/primary-text`, **not** `action/primary`.

Changed 2026-08-05 in centric-ui, saas-plm-prototype, and Figma DS
`o6o1ZuGHxDow2vHLuYXT6X` (initially Blue/12, then Blue/11).
