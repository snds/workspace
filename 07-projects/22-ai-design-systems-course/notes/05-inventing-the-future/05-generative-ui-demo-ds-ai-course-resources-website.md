---
title: "Generative UI Demo — DS+AI Course Resources Website"
section: "Chapter 5: Inventing the Future with AI & Design Systems"
source: https://courses.bradfrost.com/courses/take/ai-design-systems-course/lessons/77919293-generative-ui-demo-ds-ai-course-resources-website
duration: ~12m15s
status: noted
as-of: 2026-09-10
---

# Generative UI Demo - DS+AI Course Resources Website

Dogfood: resources.aianddesign.systems uses **A2UI-shaped JSON, not arbitrary code**, so UI renders natively across web/mobile/desktop from Eddie. Query box: “Tell me about Figma Console MCP” → course video cards + glossary + community links. “What’s new this month?” → **timeline** (no videos/glossary). “Resources added month-by-month in 2026” → **bar chart** + stat cards. Same site, different composition — Google-flight-widget energy, but with DS ingredients.

**Agent speaks JSON, not code:** `BeginRendering` names the surface; surface update lists component types/IDs; stubs like “display a video grid with these items.” Reduced test case = smart default for speed (web-perf analogy). Data models stitch to components (stat row, resource timeline, definition).

Eddie Brain v60: “these are the only shapes the renderer will build” — generated from each component’s **intent + do’s/don’ts**, same tables a human would read. Recipes (video grid = grid+card+tag) so the agent pours data, doesn’t invent composition. Glossary card isn’t an Eddie recipe yet — product-level compose; he wants to promote it.

**Two engines:** on-device **deterministic keyword → JSON** (instant) vs optional Claude (smarter, slower). Confidence score: **under 50% it says so instead of guessing**. View is **ephemeral** — next query wipes it. “A numbers question gets a chart, not a list.”

**For Sean:** this is the load-bearing gen-UI picture — blessed catalog + recipes + machine-readable when-to-use + JSON renderer + confidence, not LLM emitting React.
