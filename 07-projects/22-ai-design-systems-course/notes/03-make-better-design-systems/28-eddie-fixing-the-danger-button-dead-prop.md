---
title: "Eddie: Fixing the Danger Button Dead Prop"
section: "Chapter 3: Make Better Design Systems With AI"
source: https://courses.bradfrost.com/courses/take/ai-design-systems-course/lessons/76655958-eddie-fixing-the-danger-button-dead-prop
duration: ~7m25s
status: noted
as-of: 2026-09-10
---

# Eddie: Fixing the Danger Button Dead Prop

Station 2 (7/10): `variant="danger"` declared in TS, **no styles, no Storybook**. Quote they love: a documented API that silently does nothing **erodes trust in every other prop**.

Language: tokens say `error`; button says `danger` (delete-account / danger zone ≠ validation error). Inspector asks: add button-danger **tier-three** tokens. Buttons are the exception to “always tier-two semantics” — they point at their Subatomic tokens course.

**For Sean:** hunt dead props in Centric APIs. Same trust paper-cut.
