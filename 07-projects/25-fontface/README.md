---
title: Fontface
type: project
status: Active
triggers: [fontface, font manager, typeface replacement]
frameworks: [ui-ux-operational, qa-operating-model, engineering-operating-model]
related_projects: []
---

# Fontface (25-fontface)

A clean-room, subscription-free Mac font manager that replaces the Typeface app for Sean.
Typeface keeps some actions behind its paid Pro tier (a one-time purchase, not a subscription, per the 2026-10-19 assessment); Fontface never puts turning fonts on behind a paywall. The clean-room rule was dropped on 2026-10-19 (see notes/typeface-app-analysis_2026-10-19 and notes/typeface-assessment_2026-10-19).

- **Status:** Active. Phase 1 built; first user test found scanning bugs (fix in progress).
- **Code repo:** `~/Projects/fontface` (git, remote `snds/fontface`; resolves as personal-solo after Sean's `profile_resolve.py scan` on 2026-10-12). No commits yet.
- **This folder:** baton + pointers only. Design docs live in the repo: `docs/ARCHITECTURE.md`, `docs/FEATURES.md`.
- **Baton:** [[07-projects/25-fontface/SESSION-STATE|SESSION-STATE]]. Registry: `06-context/project-registry.md`.
- **Notes:** [[07-projects/25-fontface/notes/license-recovery-learnings_2026-10-13|License recovery learnings]] (YWFT and Monotype vendor findings, reconcile rules, EULA pitfalls, the proposed license registry and vendor adapters, and how each maps onto Fontface today).
- **Notes:** [[07-projects/25-fontface/notes/typeface-app-analysis_2026-10-19|Typeface app analysis]] (what Typeface 4.5.1 does inside: auto-activation, importers, formats, classification, Google sync, and a suggested backlog for Fontface).

## Project intent

- **Problem:** Sean's font library should stay on without a subscription.
- **Clean-room rule (dropped 2026-10-19, Sean):** Typeface's binary may now inform Fontface's design; see the analysis note below. Still no copied Typeface code, and binary-derived detail stays in this workspace, never in the public repo.
- **Allowed import:** a planned importer reads Sean's own exported `.typeface-backup` files (his data) to bring over tags and collections.
- **Scope:** Mac first. Windows is designed for but not built.
- Move this block to `<repo>/PROJECT.md` once the repo is under git (vault points, repo holds).

## Stack (decided 2026-10-12)

- Tauri 2: Rust core + React 19 / TypeScript / Vite web UI.
- UI: shadcn/ui (Base UI flavor, Tailwind v4). `clsx` + `tailwind-merge` replace shadcn's `cn` package. No next-themes, lucide or Geist.
- Icons: Material Symbols Rounded (bundled variable font). Type: IBM Plex Sans (UI), IBM Plex Mono (technical values), bundled via Fontsource.
- Windows plan: `AddFontResourceExW` + a per-user (HKCU) Fonts registry value + `WM_FONTCHANGE` broadcast. No admin rights needed.

## Architecture (short)

- Library database: SQLite in WAL mode (write-ahead log) at `~/Library/Application Support/design.snds.fontface/`.
- Scanner: reads `.ttf` / `.otf` / `.ttc` / `.otc` with `ttf-parser`.
- Activation: CoreText persistent user scope. Fonts stay on after quit or restart. Nothing is copied into `~/Library/Fonts`.
- Activation is per file, so faces in one collection file turn on and off together.
- Previews load over a private `ff://` URL scheme by library id. Rust splits collections into single faces.
- The database records intended activation; launch re-applies it (reconcile).

## Phases

1. Library, preview, activation — **built**.
2. Organizing: tags, collections, smart collections, filters, live folder watching, grid view.
3. Inspecting: duplicates, conflicts, compare, glyph grid, OpenType features, coverage.
4. Workflow: Typeface backup import, export/import, menu bar, launch at login, auto-activation, sync.
