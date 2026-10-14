# SESSION-STATE — Mailbird, working name (24-mailbird)

_Last updated: 2026-10-14 — checkpoint (PRs #1–#12 merged; Phase 8 calm inbox in PR #13)_

---

## Current state (rewritten atomically — no stale fields)

### 🤝 Live handoff (the baton — any agent reads this FIRST)

- **TL;DR (for future agent)**: An open-source, ad-free PIM "super app" with mail, calendar,
  contacts, and notes. It is mobile-first and runs on the web plus Tauri shells. The code is in
  `snds/Mailbird`, and its docs/ folder holds the research, license audit, architecture, and ADRs.
- **Current focus**: Phase 9 ("connected calendar") is in review as PR #14 (`phase-9-connected`). Sean said "merge then continue phases" again, so PR #13 is merged. Phase 9 joins the verticals: Join buttons, a Birthdays calendar, contact history, a second time zone, and missed-reminder catch-up.
- **Working set**: `crates/core/src/{meeting,connected_store}.rs`, `crates/app/src/workers.rs` (catch-up), `crates/app/src/pim_commands.rs`,
  `apps/web/src/features/calendar/{join-button.tsx,meeting.ts,second-zone.tsx,zones.ts,reminder-watcher.tsx}`, `apps/web/src/features/contacts/contact-detail.tsx`, `docs/decisions/0019-connected-calendar.md`.
- **Last action**: Merged PR #13 on Sean's word, then built Phase 9:
  - Meeting links come from known hosts only (Zoom, Meet, Teams, Webex, Jitsi, Whereby, FaceTime). Lists read the location; the event view also reads the URL and notes.
  - Schema v9 adds `contacts.birthday` and a read-only Birthdays calendar computed from contacts. A birthday opens the contact.
  - `contact_activity` lists conversations plus upcoming and past meetings on each card.
  - The second time zone is per viewer, stored in the browser.
  - Missed reminders: one OS notification at launch, and the UI pulls them once (`take_missed_reminders`).
  - Tests: Rust 163, the new demo suite `phase9` (27 checks) plus the 15 earlier suites, and a new gateway e2e on real Dovecot (including a reminder missed across a restart). The Phase 6–8 gateway suites pass.
  - Fixed: year-less vCard birthdays lost on read; catch-up stopping a minute before launch.
- **Next action**: Watch PR #14's CI. Merge only on Sean's explicit word.
  Then: the device spike (`docs/mobile-spike.md`) on Sean's hardware. Or more harvest items: bundles and grouped newsletters, sender-data sync between devices, Gmail labels, free/busy and COUNTER, a public OAuth return address for the gateway. Or the product rename.
  Sean must register a Google OAuth client and a Microsoft Entra app for real sign-ins (`docs/google-verification.md`, `docs/microsoft-setup.md`).
  Notes follow-ups: end-to-end encryption to the relay, images, linking from the note side, and export.
  Test-harness note: the shared Dovecot mailbox and SMTP sink keep state between runs; clear them before re-running the gateway suites.
- **Open decisions**: (1) the product name, which collides with Mailbird, Inc. (ADR-0006). Google verification is blocked on it;
  (2) the Tauri mobile spike vs Capacitor (ADR-0002); (3) when to subset the Material Symbols font
  (ADR-0003); (4) whether to keep Apache-2.0 for the repo license.
- **Blocked on**: nothing. No TLS round trip against a live provider has been tested yet, because
  cloud egress blocks it.
- **In-flight / do-not-touch**: none.
- **Agent thread**: Claude Opus 5.5 / Claude Code cloud (2026-10-13): research, Phase 0 (PR #1),
  Phase 1 (PR #2), Phase 1b (PR #3), Phase 1c (PR #4), Phase 2 (PR #5), Phase 2b (PR #6), Phase 3 (PR #7), Phase 4 (PR #8), Phase 4b (PR #9), Phase 5 (PR #10), Phase 6 (PR #11), Phase 7 (PR #12), Phase 8 (PR #13), all merged; Phase 9 in PR #14.

### Environment
- **Context profile**: `personal-solo` + `visibility: public`.
- **Code repo**: `github.com/snds/Mailbird` (default branch `main`).
- **Gotcha**: the Dovecot test server needs a short runtime path (unix sockets fail on long
  paths); `tools/test-mail-servers/start.sh` defaults to `/tmp/mbtest`.
- **Gotcha**: Stalwart 0.16 keeps its config in its database. `start-jmap.sh` drives the bootstrap API. The
  bootstrap admin is synthetic (its Email/query fails), so tests use a real `tester@localhost.test`.
  GitHub release downloads are blocked in cloud sessions, so the script builds from source.
- **Gotcha**: never `pkill -f <pattern>` from a shell whose own command line contains the pattern.
  Use `pgrep -x`, or an anchored `pgrep -f '^target/…'`.
- **Gotcha**: Sonner restores focus to the pre-toast element when a toast unmounts, which steals
  focus from a dialog opened by a toast action. The composer reclaims focus for its first second.
- **Gotcha**: Stalwart serves CalDAV/CardDAV on the same :8080 listener (`/.well-known/caldav` → `/dav/cal`), so the DAV test reuses `start-jmap.sh`.
- **Gotcha**: calcard pairs overrides with their series by SEQUENCE. Strip SEQUENCE before `expand_dates`, or a bumped override duplicates its occurrence.
- **Gotcha**: Hocuspocus allows one provider per document name per socket, and a destroyed provider's close can unsubscribe its replacement. Use `sessionAwareness: true`, and never pass `onSynced: undefined` (it replaces the default handler).
- **Gotcha**: never run `cargo fmt` here: the repo isn't rustfmt-formatted, and it rewrites every file. Format only new files, with `rustfmt --config max_width=180,use_small_heuristics=Max`.
- **Gotcha**: Docker works here (`sudo dockerd &`), but containers can't use the agent proxy, so image builds can't fetch crates. Build the binary on the host and test the runtime stage. Stubbing a Cargo workspace member in a Dockerfile prunes `Cargo.lock`, so those builds can't use `--locked`.
- **Gotcha**: the cloud disk fills from `target/` (about 20 GB). Use `CARGO_INCREMENTAL=0`, or delete `target/debug/incremental`.
- **Gotcha**: React events cross portals. A dialog opened inside the composer's `<form>` must stop submit and keydown propagation, or it sends the message. shadcn's base `CommandDialog` needs its children wrapped in `<Command>`.
- **Gotcha**: TanStack `mutate(args, { onSuccess })` per-call callbacks don't run if the component unmounts first. Close a view after the toast, not before. Base UI menu radio items need `closeOnClick`.
- **Gotcha**: the shadcn registry host may be blocked by cloud network policy. Components come from
  a shadcn-ui/ui git clone through `tools/shadcn-material/transform.mjs`.

### VCS state
- `phase-8-calm-inbox`: Phase 8, in PR #13. `main` has Phases 0 through 7.
