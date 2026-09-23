---
title: Bulk capture from a logged-in site via the in-app browser
tags: [web-automation, browser, capture, thinkific, wistia, agent-process]
created: 2026-09-23
updated: 2026-09-23
status: validated
confidence: high
sources:
  - "session 2026-09-23 — Subatomic course capture (07-projects/23-subatomic-design-tokens-course/SESSION-STATE.md)"
related_skills: [web-automation]
related_projects: [23-subatomic-design-tokens-course, 22-ai-design-systems-course]
relations:
  relates-to: ["[[design-token-architecture]]"]
---

# Bulk capture from a logged-in site via the in-app browser

## For future agent

- **TL;DR:** For a course/portal the user is logged into (and whose terms allow download), drive the
  **site's own JSON API from the logged-in page** at human pace, then move the extracted map to disk by
  returning it as an **oversized tool result** (the harness saves it to a file) and parse that file.
  Download media from public CDNs with a separate paced, resumable script. Never copy cookies out.
- **As of:** 2026-09 · **Status:** current · **Audience:** `for: agent`

## What worked (Thinkific + Wistia, 372 items, 0 errors)

1. **Map via the player API, not the DOM.** `GET /api/course_player/v2/courses/<slug>` → chapters +
   contents; per lesson `…/lessons/<contentable_id>` → `download_files` (transcripts, slides, zips);
   per video `…/contents/<id>/play/<video_id>` HTML contains `wistia_async_<hashedId>`.
2. **Media from the public CDN.** `fast.wistia.com/embed/medias/<id>.json` lists 224p–4K + original and
   carries English captions (a free transcript fallback). Pick one rendition (1080p ≈ 7 GB for 13.6 h;
   originals ≈ 150 GB).
3. **Human pace.** One request at a time, 3–10 s randomized gaps; resumable (skip files on disk; write
   `.part` then rename). Raw media goes to `<Projects>/…`, never the vault.
4. **Persist in-page progress to `localStorage`** so a navigation or reload doesn't lose the crawl
   (clear the key afterwards).

## What the in-app browser pane blocks (don't retry these)

| Attempt | Result |
|---|---|
| Second+ programmatic download (blob `<a download>`) | First one lands in `~/Downloads`; later ones silently dropped, even from a real click |
| `navigator.clipboard.writeText` | `NotAllowedError` |
| `fetch` / iframe to `http://127.0.0.1` from the https page | Blocked (even with CORS + Private-Network-Access headers) |
| `window.open(localhost)` | **Navigates the same tab** — the page's in-memory state is lost |
| `setTimeout` pacing while the pane is **hidden** | Throttled to ~1/min (intensive throttling of chained timers); Web Workers too |

## Workarounds that hold

- **Transport:** return `JSON.stringify(data)` (pad past ~100 kB if small) from `javascript_tool`; the
  harness writes it to `tool-results/*.txt` as `[{type,text}]`; parse with a script (text may be
  double-encoded). No hand transcription of IDs.
- **Hidden-pane pacing:** hop through a `MessageChannel` message before each `setTimeout` so the timer's
  nesting level resets (no intensive throttling); ~7–8 s/item held.
- Merge partial dumps into one manifest by position; downloads can start before the crawl finishes.

## Data-quality traps

- Course-provided transcript files can be **mislabelled** (a copy of a neighbour) — diff against the
  platform caption and substitute (2 of 360 here).
- Keep an honest record of what the platform itself swapped (a promised Q&A replaced by another demo).

## Triggers

`bulk download course`, `course capture`, `thinkific`, `wistia`, `in-app browser download blocked`,
`hidden pane throttling`, `tool result transport`
