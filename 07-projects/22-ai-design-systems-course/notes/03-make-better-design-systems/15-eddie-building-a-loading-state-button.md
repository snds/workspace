---
title: "Eddie: Building a Loading State Button"
section: "Chapter 3: Make Better Design Systems With AI"
source: https://courses.bradfrost.com/courses/take/ai-design-systems-course/lessons/76655671-eddie-building-a-loading-state-button
duration: ~6m27s
status: noted
as-of: 2026-09-10
---

# Eddie: Building a Loading State Button

Feature branch + Storybook. New `isLoading` prop named against **documented API conventions** (`isBehavior`). Spinner helpers, classes, tokens. First pass: loading isn’t visually disabled — second pass: match disabled tokens/cursor because loading **is** disabled. Then: Storybook interaction test (default → loading) and expose the pattern in **Eddie Brain** so humans/agents use it.

Speed of first production doesn’t skip craft, tests, or MCP documentation.
