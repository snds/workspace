---
title: Subatomic Design Tokens Course
aliases: [23-subatomic-design-tokens-course, subatomic course, subatomic design tokens]
type: project
status: Active
triggers: [subatomic course, subatomic design tokens, brad frost tokens course, frost token course]
frameworks: [qa-operating-model, research-and-evidence, workspace-contribution]
created: 2026-09-23
lifecycle: define
---

# 23-subatomic-design-tokens-course

Original notes and synthesis from Brad Frost & Ian Frost, **Subatomic: The Complete Guide To Design Tokens** (Thinkific, `courses.bradfrost.com`). 11 sections, 360 video lessons (~13.6 h), plus slide PDFs, transcripts, and downloadable files.

- **Curriculum:** [[CURRICULUM]]
- **Notes:** `notes/` (one file per chapter — original summaries, not transcripts)
- **Running synthesis:** `synthesis/running.md`
- **Operational state:** [[SESSION-STATE]]
- **Source:** https://courses.bradfrost.com/courses/take/subatomic-design-tokens/lessons/62108387-welcome
- **Graduated doctrine (2026-09-23):** [[design-token-architecture]] · [[token-architecture]] · `09-tools/token-audit.py`
- **Sibling course:** [[22-ai-design-systems-course]] (AI and Design Systems)

## Project intent

### Problem & audience

Turn the Subatomic design tokens course into original notes and a synthesis, and graduate a token
architecture doctrine plus a detector. The audience is Sean's design-system work.

### Knowns & unknowns

| claim | label | tier | evidence | decision rule |
|---|---|---|---|---|
| Capture is complete (372 of 372 items) | known | T1 | SESSION-STATE TL;DR | — |
| `token-audit.py` is calibrated on the course demo repo only | known | T1 | SESSION-STATE TL;DR | — |
| `token-audit.py` holds up on a real product token source | unknown | T5 | not run yet | if its first real run flags more false positives than findings, recalibrate before wider use |

### Out of scope & later

Raw course files in the vault (they live in the Projects directory); running the tool on employer
repos from this vault. Later: value-level Figma-to-code parity (TA014) and a variable-scope probe.

## Raw course materials (outside the workspace)

The course explicitly offers its videos, transcripts, and lesson files for download (Sean's decision,
2026-09-23 — this course only; project 22's no-video rule stands for that course). Raw copies live in the
platform-relative Projects directory, **never** in this portable workspace:

`<Projects>/subatomic-design-tokens-course/`
- `videos/<NN-chapter>/` — Wistia 1080p MP4s
- `transcripts/<NN-chapter>/` — the course's own timestamped `.txt` transcripts
- `captions/<NN-chapter>/` — Wistia English captions (fallback when a lesson has no transcript file)
- `files/<NN-chapter>/` — slide PDFs and other lesson downloads
- `manifest/manifest.json` — structured course map (ids, slugs, durations, file URLs, Wistia ids)
- `fetch.py` — paced, resumable downloader (re-run it to fill gaps; it skips files already on disk)

## For future agent

Read `SESSION-STATE.md` Live handoff first, then `synthesis/running.md`. Notes are original; never paste
transcript text into the workspace (short attributed quotes only). Personal-workspace content — never copy
into `c8/*` employer repos.
