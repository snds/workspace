---
title: "Eddie: Closing Keyboard & Behavioral Testing Gaps"
section: "Chapter 3: Make Better Design Systems With AI"
source: https://courses.bradfrost.com/courses/take/ai-design-systems-course/lessons/76661429-eddie-closing-keyboard-behavioral-testing-gaps
duration: ~4m46s
status: noted
as-of: 2026-09-10
---

# Eddie: Closing Keyboard & Behavioral Testing Gaps

Work order: behavioral tests + visual regression. Chromatic exists but **not blocking** — by design while the language is still moving; they’ll turn it on later. Real hole: keyboard unit tests gone (tooltip Enter/Escape works in UI, **not in Vitest**). 1,363 tests and still missing the crucial handlers. Don’t confuse volume with coverage.
