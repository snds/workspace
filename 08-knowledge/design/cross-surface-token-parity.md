---
title: Cross-surface token parity statuses
tags: [design-systems, tokens, figma, parity, aligned]
created: 2026-08-05
updated: 2026-08-05
status: canonical
confidence: high
sources: [session 2026-08-05 Token Spec radius/full, Sean]
related: [token-spec-page, centric-plm-design-system]
---

# Cross-surface token parity statuses

When comparing the same design intent across surfaces (Figma variables vs CSS/Tailwind vs
another codebase), use **four** outcomes — not a binary match/deviate.

| Status | Meaning |
|---|---|
| **MATCH** | Same intent **and** same technical representation (resolved value / alias model aligns). |
| **ALIGNED** | Same intent and **visually identical outcome**, but the technical implementation differs because a surface cannot express the other’s native form. |
| **DEVIATE** | Intent or visual outcome differs (wrong value, wrong referred token, different behavior). |
| **FIGMA-ONLY / missing** | Token exists on one side only (gap), not a representation mismatch. |

## Rule (Sean, 2026-08-05)

Technical implementation parity is **paramount wherever possible**. Prefer MATCH.

When surfaces have **identical intent** and the **visual outcome is identical**, but one
surface literally cannot host the other’s representation, lean to **ALIGNED** — not
DEVIATE, and never phrase it as “no parity.”

**Do not say “no parity”** when intent is shared. Intent parity holds; only the binding
mechanism differs.

### Canonical example — `radius/full`

| Surface | Representation |
|---|---|
| Figma | `radius/full` = **9999px** (variables cannot bind a non-pixel “circle”) |
| centric-ui / prototype | Tailwind **`rounded-full`** → `calc(infinity * 1px)` |

Status: **ALIGNED** (not MATCH, not DEVIATE). Same pill/circle intent; same visual result;
different native forms.

## Reference pipelines (not just resolved values)

Parity is judged on **both**:

1. **Resolved output** (the computed color / length / etc.)
2. **Reference pipeline** (alias / `var()` chain — leaf primitive and meaningful intermediates)

Prefer pipelines that are as close as each surface allows without hurting designer or
engineering experience on that surface.

| OK for MATCH | Example |
|---|---|
| Naming shape differs, leaf agrees | Figma `Color/Blue/Light/10` ≡ code `--sem-primary → --color-blue-10` |
| One extra semantic hop that maps 1:1 | Figma `surface/inverted → White` ≡ `--sem-*-foreground → --sem-inverted → --color-white` |

| ALIGNED (not DEVIATE) | Example |
|---|---|
| Same visual outcome; pipeline must differ by surface | `radius/full` 9999px vs Tailwind `rounded-full` |

| DEVIATE | Example |
|---|---|
| Different resolved value and/or different functional structure | Figma `interaction/selected → Blue/A5` vs code `--sem-selected → --color-blue-5` |

Do **not** invent false MATCH tokens in code (e.g. `--radius-full: 9999px`) just to mirror
Figma’s stand-in. Do **not** call shared-intent cases “no parity.”

