---
title: Installing Story UI into Soul Patrol Design System
section: "Chapter 4: Make Better Products with AI & Design Systems"
source: https://courses.bradfrost.com/courses/take/ai-design-systems-course/lessons/75130758-installing-story-ui-into-soul-patrol-design-system
duration: ~5m24s
status: noted
as-of: 2026-09-10
---

# Installing Story UI into Soul Patrol Design System

npm install → init wizard → run Story UI MCP + Storybook together. Install **next to Storybook** (here: `packages/soul-patrol-web-components`, not monorepo root). Detected Vite WC Storybook, 58 stories. Point at real `components/` path. Auto-detect vs Shoelace vs custom. Generated stories → `src/stories/generated`. Port 4001. Claude API key. Lit import path may be wrong — they hit that next.
