---
title: "bradfrost.com — Fixing urgent inspection issues with Declarative Shadow DOM"
section: "Chapter 4: Make Better Products with AI & Design Systems"
source: https://courses.bradfrost.com/courses/take/ai-design-systems-course/lessons/77342876-bradfrost-com-fixing-the-most-urgent-inspection-issues-with-declarative-shadow-dom
duration: ~13m21s
status: noted
as-of: 2026-09-10
---

# bradfrost.com - Fixing the most urgent inspection issues with Declarative Shadow DOM

Work-order #1 “doesn’t fit phones” wasn’t a max-width. **FOUC:** web components need JS; Playwright screenshots before styles load → horizontal overflow. Hard WC problem. Throw SSR / progressive enhancement / **declarative shadow DOM** at Eddie. Dual-file: product bug *and* Eddie issues. Quick win on the flash, not a full architecture rewrite. He’s visibly happy it landed.
