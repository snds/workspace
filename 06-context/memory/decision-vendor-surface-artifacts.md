---
type: decision
description: Vendor Canvas/Artifact/HTML-preview panels are not durable storage — write through to the vault (or emit a copy-ready path on web)
created: 2026-09-11
confidence: high
relations:
  builds-on: ["[[decision-externalize-everything-to-workspace]]"]
  relates-to: ["[[decision-portable-workspace-refactor]]", "[[artifact-standards]]"]
---

## For future agent
- **TL;DR:** Claude Artifacts, ChatGPT/Gemini canvases, HTML previews, and chat-generated docs are vendor panels, not the source of truth. Filesystem agents write the vault file as the original. Cursor `.canvas.tsx` is dual-home (live compile path + git-tracked copy). Web surfaces emit a copy-ready block with a suggested path. Do not scrape vendor UIs. Do not copy `c8/*` canvases into this vault.
- **As of:** 2026-09 · **Status:** current

## Context — what forced a choice
LLMs park standalone analytical output in surface-specific stores: Cursor `~/.cursor/projects/*/canvases/`, Claude.ai Artifacts, ChatGPT/Gemini canvases, HTML preview panes. Those copies are invisible to every other agent, unversioned, and often cloud-only. [[decision-externalize-everything-to-workspace]] already bans private memory; it did not name this panel class. Cursor harvest (`cursor-externalize.py`) covers one live compile path and is session-end only — GitHub cannot see `~/.cursor` (automation review A10). A Layer 0 miss on "canvas artifacts / HTML files / clipboard ingest" showed the routing map had no vendor-surface row.

## Decision — what we chose
**Write-through.** Vendor Canvas / Artifact / HTML-preview panels are not durable storage.

- **Filesystem surfaces:** write the vault file as the original — owning `07-projects/NN-*/` when project-scoped, `05-artifacts/` when it is a generated deliverable — named per [[artifact-standards]]. Working code still goes to platform `Projects/`, never this vault.
- **Cursor `.canvas.tsx`:** dual-home. The IDE compiles only from `~/.cursor/projects/<slug>/canvases/`. The git-tracked copy under `07-projects/…/canvases/` is the portable source of truth (`python3 09-tools/cursor-externalize.py` at session-end). Do not refuse Cursor canvases; do not treat the live path as the only copy. Prefer a vault `md`/`html` when a live canvas is not required for interactivity.
- **HTML** that is a rich deliverable **stays HTML** (self-contained, per artifact-standards). Do not mandate Markdown conversion.
- **Web / no-filesystem surfaces:** emit a copy-ready fenced block plus a suggested `context_descriptor_vN.N_YYYY-MM-DD.ext` path. Do not scrape claude.ai / chatgpt.com / Gemini.
- **Employer wall:** never copy `c8/*` / Centric canvases into `snds/workspace`.
- **This slice is policy.** Harvest slug-map repair, drop-folder / clipboard ingest CLI, and a dedicated skill are later slices.

## Rationale — why, and what we rejected
(1) Scrape each vendor UI — not portable, TOS-fragile, and the opposite of filesystem-as-I/O. (2) Convert everything to Markdown — this vault already treats self-contained HTML as a first-class deliverable. (3) Refuse Cursor canvases — the IDE will not compile vault copies; dual-home is required. (4) Put the rule only in `CURSOR.md` — then Claude.ai / Gemini / Perplexity never inherit it. Policy lives in [[AGENTS]] (one sentence) + [[workspace-ontology]] + this decision; adapters stay one line.

## Consequences — what this commits us to
Agents with a filesystem must not treat a vendor panel as the finished artifact. Session-end still runs `cursor-externalize.py` on Cursor; that is harvest of the live compile path, not a substitute for write-through. `--check` remaining false-green on unmatched slugs (this Mac: `Users-sean-sands-projects`) is a harvest-slice bug, not an excuse to skip write-through. Inbox / `pbcopy` / `artifact-ingest.py` wait until this policy is the contract.
