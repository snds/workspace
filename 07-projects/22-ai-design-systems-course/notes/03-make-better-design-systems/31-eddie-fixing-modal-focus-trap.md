---
title: "Eddie: Fixing Modal Focus Trap"
section: "Chapter 3: Make Better Design Systems With AI"
source: https://courses.bradfrost.com/courses/take/ai-design-systems-course/lessons/76656769-eddie-fixing-modal-focus-trap
duration: ~11m10s
status: noted
as-of: 2026-09-10
---

# Eddie: Fixing Modal Focus Trap

Biggest inspection finding: Eddie Modal/Drawer have no real focus management. Demo: open modal, focus stays on trigger; Tab escapes onto the page underneath. Blocking UI must cycle Cancel/OK/X only; Escape/buttons dismiss. They quote W3C “no keyboard trap” / dialog focus.

Don’t blindly trust the agent — **feed the spec** (W3C + inspection issue) into the session. Storybook interaction tests were already failing; that’s the tell.
