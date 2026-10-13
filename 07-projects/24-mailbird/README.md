---
title: Mailbird (working name)
type: project
status: Active
triggers: [mailbird, pim super app, email calendar contacts notes app, mail client]
frameworks: [ui-ux-operational, component-pattern, integration, workspace-contribution]
related_projects: []
---

# Mailbird — working name (24-mailbird)

One calm, ad-free, open-source app for mail, calendar, contacts, and notes. It is mobile-first and
runs on the web, Windows, macOS, Linux, iOS, iPadOS, and Android.

- **Status:** Active (Phase 0 foundation in PR #1)
- **Code repo:** `github.com/snds/Mailbird` (public, `personal-solo` + `visibility: public`). Code
  lives in `Projects/Mailbird`, not in this vault.
- **This folder:** the continuity baton only. Design docs live in the code repo under `docs/`
  (research, OSS stack, architecture, ADRs 0001–0006).
- **Name risk:** "Mailbird" is a live commercial email client (Mailbird, Inc.). Rename before
  release (repo ADR-0006).

## Stack

- **UI:** React 19, Vite 8, Tailwind v4, and shadcn/ui (Base UI base, Nova style).
- **Icons:** Material Symbols Rounded variable font, drawn inside an `<svg>` so shadcn's `svg`
  selectors keep working.
- **Shells:** Tauri 2 for desktop. Mobile is a spike, with Capacitor + UniFFI as the fallback.
- **Core:** Rust `pim-core`, which holds the provider adapters and a capability matrix.

## Docs

- [[07-projects/24-mailbird/SESSION-STATE|SESSION-STATE]]: the operational baton.
