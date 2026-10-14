# SESSION-STATE — Mailbird, working name (24-mailbird)

_Last updated: 2026-10-14 — checkpoint (PRs #1–#4 merged; Phase 2 in PR #5)_

---

## Current state (rewritten atomically — no stale fields)

### 🤝 Live handoff (the baton — any agent reads this FIRST)

- **TL;DR (for future agent)**: An open-source, ad-free PIM "super app" with mail, calendar,
  contacts, and notes. It is mobile-first and runs on the web plus Tauri shells. The code is in
  `snds/Mailbird`, and its docs/ folder holds the research, license audit, architecture, and ADRs.
- **Current focus**: Phase 2, calendars and contacts, in review as PR #5 (`phase-2-pim`). PRs #1–#4 are merged.
- **Working set**: `crates/core/src/{ical,vcard,pim_store}.rs`, `crates/core/src/net/dav.rs`,
  `crates/core/tests/dav.rs`, `apps/web/src-tauri/src/{pim_commands,workers}.rs`,
  `apps/web/src/features/{calendar,contacts}/`, `apps/web/src/core/demo-pim.ts`,
  `docs/decisions/0010-calendar-contacts.md`.
- **Last action**: Built and verified Phase 2:
  - calcard iCalendar/vCard handling with splice-on-edit, plus a CalDAV/CardDAV client on reqwest and quick-xml.
  - Store schema v4.
  - Agenda/day/week views and chrono-node quick add.
  - Contacts with duplicate merge, and composer autocomplete.
  - A two-device DAV integration test against Stalwart, now in CI.
- **Next action**: Merge PR #5. Then pick between:
  - Phase 2b: single-occurrence edits, invitations (iTIP), month view, reminders.
  - Phase 3 (notes).
- **Open decisions**: (1) the product name, which collides with Mailbird, Inc. (ADR-0006);
  (2) the Tauri mobile spike vs Capacitor (ADR-0002); (3) when to subset the Material Symbols font
  (ADR-0003); (4) whether to keep Apache-2.0 for the repo license.
- **Blocked on**: nothing. No TLS round trip against a live provider has been tested yet, because
  cloud egress blocks it.
- **In-flight / do-not-touch**: none.
- **Agent thread**: Claude Opus 5.5 / Claude Code cloud (2026-10-13): research, Phase 0 (PR #1),
  Phase 1 (PR #2), Phase 1b (PR #3), Phase 1c (PR #4), all merged; Phase 2 (PR #5).

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
- **Gotcha**: the shadcn registry host may be blocked by cloud network policy. Components come from
  a shadcn-ui/ui git clone through `tools/shadcn-material/transform.mjs`.

### VCS state
- `phase-2-pim`: Phase 2, in PR #5. `main` has Phases 0 through 1c.
