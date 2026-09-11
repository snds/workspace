---
title: "Soul Patrol — Dark mode across Figma, Storybook, and React Native"
section: "Chapter 4: Make Better Products with AI & Design Systems"
source: https://courses.bradfrost.com/courses/take/ai-design-systems-course/lessons/76048298-soul-patrol-dark-mode-across-figma-storybook-and-react-native
duration: ~8m00s
status: noted
as-of: 2026-09-10
---

# Soul Patrol - Dark mode across Figma, Storybook, and React Native

Org mandate: dark mode. One prompt to Claude Code: **Figma + Storybook + React Native**. Skill: **Theme Orchestrator** — don’t explore first; it already knows the token architecture (tier 1 / 2 / 3). Don’t invert colors (AI default); use muted dark identity. `create-theme` script → `Soul Patrol Dark` JSON mapping existing tokens → new values. WCAG AA audit in the skill; he still wants **Axe** as the deterministic check, not LLM-as-judge for a11y. Pipeline succeeds; Storybook theme switch works from light guidance.

**For Sean:** retheme as a **scripted token pipeline + skill**, not a Figma-only palette dump. Deterministic a11y stays in the steel curtain.
