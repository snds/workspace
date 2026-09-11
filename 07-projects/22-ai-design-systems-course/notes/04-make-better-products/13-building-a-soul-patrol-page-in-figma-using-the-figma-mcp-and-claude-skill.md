---
title: Building a Soul Patrol Page in Figma Using the Figma MCP and Claude Skill
section: "Chapter 4: Make Better Products with AI & Design Systems"
source: https://courses.bradfrost.com/courses/take/ai-design-systems-course/lessons/75818446-building-a-soul-patrol-page-in-figma-using-the-figma-mcp-and-claude-skill
duration: ~8m33s
status: noted
as-of: 2026-09-10
---

# Building a Soul Patrol Page in Figma Using the Figma MCP and Claude Skill

Check-engine is off (FigmaLint + Console MCP parity). Now **use** the system: donate page in Figma from Soul Patrol tokens + components. Homepage already consumes both libraries; donate is an empty stub.

Don’t prompt “build a donate page” with no extra context — the model will invent from training data and burn tokens. They add: World Central Kitchen donate URL + screenshot (research: it converts) **plus** a Claude **skill** that packs DS context and Console MCP tools (`figma_execute` / `figma_use`). Out-of-the-box MCP page gen can take **~15 minutes**; the skill is to make that smoother.

**For Sean:** on-rails Figma pages still need a skill (or equivalent) — MCP + a URL is not enough context. Inspiration from a live competitor is allowed; the DS is the constraint.
