# SESSION-STATE — Subatomic Design Tokens Course

_Last updated: 2026-09-23 — capture complete; doctrine graduated_

---

## Current state (rewritten atomically — no stale fields)

### Live handoff (the baton — any agent reads this FIRST, updates it on every handoff)

- **TL;DR**: Capture complete (372/372 items; 360 1080p videos, 358 course transcripts + Wistia captions for gaps, slides, 7 demo repos — 5.4 GB in `<Projects>/subatomic-design-tokens-course/`). Original notes for every chapter in `notes/`. Doctrine graduated: knowledge **[[design-token-architecture]]**, skill **`token-architecture`**, L3 detector **`09-tools/token-audit.py`** (23 rules, self-tested + calibrated on the course demo repo), counter-stance in framework #09, cross-links in `fe-design-tokens` / `design-system-ops` / `tokens-and-naming.md`.
- **Current focus**: none — capture + graduation done
- **Working set**: this folder · `08-knowledge/design/design-token-architecture.md` · `03-skills/token-architecture/SKILL.md` · `09-tools/token-audit.py`
- **Last action**: Calibrated `token-audit.py` on the Frostd demo (found 3 real contrast failures, 1 dark-theme font-family drift, 15 component-CSS literals; fixed 5 false-positive classes)
- **Next action**: Optional backlog — (1) value-level Figma↔code parity in TA014 (px↔rem, unitless LH, per-mode alias resolution); (2) MCP-driven Figma probe for variable scopes / publish set (tier 1 unscoped + hidden); (3) run `token-audit.py` against a real product token source (not employer repos from this vault — copy the tool into the product repo per the independence contract)
- **Open decisions**: none
- **Blocked on**: nothing
- **In-flight / do-not-touch**: never commit raw course media/transcripts into the vault; never paste into `c8/*`; Figma "duplicate" links in `files/04-*` would create files in Sean's Figma account — only on request
- **Agent thread**: `Claude Opus 5.5 / Claude Code / Work MBP (2026-09-23): capture + synthesis + graduation`

### Environment

- **Context profile**: `personal-solo`
- **Machine**: Work MacBook Pro
- **Project root**: `07-projects/23-subatomic-design-tokens-course/`

---

## History (append-only)

### 2026-09-23 — capture complete + graduation

- Paced download finished with 0 errors (manifest merged in three transfers via saved tool-result files after browser downloads/clipboard/localhost were blocked in the in-app browser; page timers throttled while the pane was hidden → MessageChannel-hop pacing).
- Chapters 5–8 notes drafted by delegated agents under a no-transcript/original-words contract; Ch1–4 + summary by the lead agent. Two mislabelled course transcripts (204, 369) replaced by Wistia captions.
- Graduated to knowledge/skill/detector/framework pointer; routing + knowledge hints + corpus cases added (52/52).

### 2026-09-23 — capture started

- Course map pulled from `/api/course_player/v2/courses/subatomic-design-tokens` (11 chapters, 372 items: 360 video lessons, 6 downloads, 5 HTML items, 1 survey; ~13.6 h).
- Videos are Wistia embeds (`fast.wistia.com/embed/medias/<id>.json` exposes 224p–4K + original + English captions). 1080p chosen (~7 GB total vs ~150 GB originals).
- Each lesson ships a Thinkific `Transcript` `.txt` (timestamped) and, per chapter, slide PDFs.
