---
title: "bradfrost.com — Generating A Footer With And Without System Guardrails"
section: "Chapter 4: Make Better Products with AI & Design Systems"
source: https://courses.bradfrost.com/courses/take/ai-design-systems-course/lessons/77064896-bradfrost-com-generating-a-footer-with-and-without-system-guardrails
duration: ~4m52s
status: noted
as-of: 2026-09-10
---

# bradfrost.com - Generating A Footer With And Without System Guardrails

**“Most important lesson in the course”:** how to make AI *consistently* use the DS, not approximate from training.

Demo: Cursor agent in bradfrost.com (Brad doesn’t usually; Claude-ecosystem ADHD). Prompt: homepage footer that recreates primary nav. Agent even had Eddie Brain and he **skipped it** to show off-rails. Result: invented `homepage-footer`, some tokens, **ignored Eddie**. That’s the industry’s generative frustration.

Same prompt next, **with** DS context and guardrails (lesson 27).
