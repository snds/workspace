# SESSION-STATE — Mailbird, working name (24-mailbird)

_Last updated: 2026-10-14 — checkpoint (PRs #1–#5 merged; Phase 2b in PR #6)_

---

## Current state (rewritten atomically — no stale fields)

### 🤝 Live handoff (the baton — any agent reads this FIRST)

- **TL;DR (for future agent)**: An open-source, ad-free PIM "super app" with mail, calendar,
  contacts, and notes. It is mobile-first and runs on the web plus Tauri shells. The code is in
  `snds/Mailbird`, and its docs/ folder holds the research, license audit, architecture, and ADRs.
- **Current focus**: Phase 2b calendar depth, in review as PR #6 (`phase-2b-calendar`). PRs #1–#5 are merged.
- **Working set**: `crates/core/src/{ical,itip,invite_store,pim_store,mime}.rs`, `crates/core/src/net/dav.rs`,
  `apps/web/src-tauri/src/{workers,pim_commands}.rs`, `apps/web/src/features/calendar/{month-grid,event-editor,event-detail,reminders,reminder-watcher}.tsx|ts`,
  `apps/web/src/features/mail/invite-card.tsx`, `docs/decisions/0011-calendar-depth.md`.
- **Last action**: Built and verified Phase 2b:
  - Occurrence edits (this event, or this and following).
  - VALARM reminders with OS notifications.
  - iTIP/iMIP invitations. Servers with CalDAV scheduling send the mail; otherwise it goes through the outbox.
  - Month view.
  - A composer focus-race fix.
- **Next action**: Merge PR #6, then Phase 3 (notes: Tiptap, Markdown storage, Yjs relay, Apple Notes and Keep import).
  Calendar follow-ups that remain: free/busy, COUNTER, and missed-reminder catch-up.
- **Open decisions**: (1) the product name, which collides with Mailbird, Inc. (ADR-0006);
  (2) the Tauri mobile spike vs Capacitor (ADR-0002); (3) when to subset the Material Symbols font
  (ADR-0003); (4) whether to keep Apache-2.0 for the repo license.
- **Blocked on**: nothing. No TLS round trip against a live provider has been tested yet, because
  cloud egress blocks it.
- **In-flight / do-not-touch**: none.
- **Agent thread**: Claude Opus 5.5 / Claude Code cloud (2026-10-13): research, Phase 0 (PR #1),
  Phase 1 (PR #2), Phase 1b (PR #3), Phase 1c (PR #4), Phase 2 (PR #5), all merged; Phase 2b (PR #6).

### Environment
- **Context profile**: `personal-solo` + `visibility: public`.
- **Code repo**: `github.com/snds/Mailbird` (default branch `main`).
- **Gotcha**: the Dovecot test server needs a short runtime path (unix sockets fail on long
  paths); `tools/test-mail-servers/start.sh` defaults to `/tmp/mbtest`.
- **Gotcha**: Stalwart 0.16 keeps its config in its database. `start-jmap.sh` drives the bootstrap API. The
  bootstrap admin is synthetic (its Email/query fails), so tests use a real `tester@localhost.test`.
  GitHub release downloads are blocked in cloud sessions, so the script builds from source.
- **Gotcha**: never `pkill -f <pattern>` from a shell whose own command line contains the pattern.
  Use `pgrep -x`.
- **Gotcha**: Sonner restores focus to the pre-toast element when a toast unmounts, which steals
  focus from a dialog opened by a toast action. The composer reclaims focus for its first second.
- **Gotcha**: Stalwart serves CalDAV/CardDAV on the same :8080 listener (`/.well-known/caldav` → `/dav/cal`), so the DAV test reuses `start-jmap.sh`.
- **Gotcha**: calcard pairs overrides with their series by SEQUENCE. Strip SEQUENCE before `expand_dates`, or a bumped override duplicates its occurrence.
- **Gotcha**: the shadcn registry host may be blocked by cloud network policy. Components come from
  a shadcn-ui/ui git clone through `tools/shadcn-material/transform.mjs`.

### VCS state
- `phase-2b-calendar`: Phase 2b, in PR #6. `main` has Phases 0 through 2.
