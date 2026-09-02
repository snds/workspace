---
name: web-automation
description: >
  Drive a real browser to do what static fetching can't — log in, click through flows, scroll
  infinite/JS-rendered pages, fill forms, and scrape SPA dashboards — via the agent-browser CLI
  (Chromium over CDP, accessibility-tree snapshots). Use when a page needs interaction or renders
  client-side and WebFetch returns empty/partial HTML. Cross-cutting utility for research, scraping,
  competitive teardown, and end-to-end UI checks. Triggers: browser automation, scrape, headless
  browser, agent-browser, CDP, click through, log in to, fill form, infinite scroll, SPA, JS-rendered.
aliases: [web-automation]
triggers: [browser automation, scrape, web scraping, headless browser, agent-browser, cdp, click through the, log in, fill form, infinite scroll, spa, js-rendered, dynamic page, accessibility tree snapshot]
tier: cross-cutting
domain: engineering
surfaces: ["*"]
requires: [agent-browser]
spec_version: "2.1"
---

# Web Automation (agent-browser)

Reach for this when a page won't yield to a plain fetch — anything behind a login, rendered by
JavaScript, or that needs clicking/scrolling to reveal content. This skill is the **when & why**;
the CLI carries the **how** (its own always-current usage docs).

> **Tool dependency — preflight first.** Requires the `agent-browser` capability ([[capability-registry]]).
> Probe `command -v agent-browser` before use. If absent: for **static** pages, degrade to WebFetch/WebSearch;
> for **interactive/JS-rendered** pages there is no portable fallback — surface the install
> (`npm i -g agent-browser && agent-browser install`) and stop. See [[AGENTS]] → "Capability preflight".

## Decide: do you actually need a browser?
- **No** — static HTML, an API, or a document → use WebFetch/WebSearch. Cheaper, faster, no dependency.
- **Yes** — login walls, client-side rendering (React/Vue SPA), infinite scroll, multi-step flows,
  cookie/consent gates, or anything you must *interact with* to reveal.

## Working pattern
1. **Load the CLI's own guide first** — `agent-browser skills get core` (it serves version-matched
   workflows; this skill deliberately doesn't restate them so they can't go stale).
2. **Snapshot, then act on refs.** Work from the accessibility-tree snapshot (`@eN` element refs) rather
   than pixel coordinates — reliable across layout shifts.
3. **Headed when a human should watch** (demos, debugging); headless for batch scraping.
4. **Be a good citizen** — respect robots/ToS, rate-limit, and never automate credential abuse or
   mass-targeting. Authorized use only.

## Common jobs
- **Scrape rendered data** a fetch can't see (dashboards, listings) → snapshot → extract → structure.
- **Competitive/reference teardown** — capture flows and states for design review ([[reference-video-review]]
  for the video equivalent).
- **End-to-end UI sanity** — drive a built app through a critical path to confirm it works.
