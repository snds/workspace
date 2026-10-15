# SESSION-STATE — Mailbird, working name (24-mailbird)

_Last updated: 2026-10-15 — checkpoint (PRs #1–#21 merged; Phase 17 faces and sources in PR #22)_

---

## Current state (rewritten atomically — no stale fields)

### 🤝 Live handoff (the baton — any agent reads this FIRST)

- **TL;DR (for future agent)**: An open-source, ad-free PIM "super app" with mail, calendar,
  contacts, and notes. It is mobile-first and runs on the web plus Tauri shells. The code is in
  `snds/Mailbird`, and its docs/ folder holds the research, license audit, architecture, and ADRs.
- **Current focus**: Phase 17 ("faces and sources") is in review as PR #22 (`phase-17`). Sean said "merge then continue phases", so PR #21 is merged (squash e85cd42). Phase 17 takes the harvest row "contact source badges and photos".
- **Working set**: `crates/core/src/vcard.rs` (PHOTO lines), `crates/core/src/contacts_store.rs` (`contact_copies`, `contact_photos`), `apps/web/src/features/contacts/contact-editor.tsx` (photo field), `contact-detail.tsx` ("Also in"), `apps/web/src/features/mail/index.tsx` + `conversation-view.tsx` (sender faces), `docs/decisions/0027-faces-and-sources.md`.
- **Last action**: Merged PR #21 on Sean's word, then built Phase 17:
  - Contact photos: add, change, or remove. The app crops to a 256 px square JPEG; the vCard stores it (up to 150 KB).
  - Sender faces in the mail list and conversation, matched by address.
  - Source badges on contact rows when two or more books show; an "Also in" row links copies of the same person in other books.
  - Tests: core (184), the demo suite `phase17` (14 checks) plus the 22 earlier suites, and `gateway-p17`.
- **Next action**: Watch PR #22's CI. Merge only on Sean's explicit word.
  Then, the remaining harvest: tasks time-blocked on the calendar, travel time, regional holidays, remappable keys, rescheduling or cancelling bookings. Guests' free/busy needs real servers. Or the device spike (`docs/mobile-spike.md`) on Sean's hardware. Or the product rename.
  Sean must register a Google OAuth client and a Microsoft Entra app for real sign-ins (`docs/google-verification.md`, `docs/microsoft-setup.md`).
  Notes follow-ups: end-to-end encryption to the relay, images, linking from the note side, and export.
  Test-harness note: clear the shared Dovecot mailbox and SMTP sink before gateway suites (`seed_p12.py reset`). Both test servers, and the vite preview, stop when the container restarts; restart them first.
- **Open decisions**: (1) the product name, which collides with Mailbird, Inc. (ADR-0006). Google verification is blocked on it;
  (2) the Tauri mobile spike vs Capacitor (ADR-0002); (3) when to subset the Material Symbols font
  (ADR-0003); (4) whether to keep Apache-2.0 for the repo license.
- **Blocked on**: nothing. No TLS round trip against a live provider has been tested yet, because
  cloud egress blocks it.
- **In-flight / do-not-touch**: none.
- **Agent thread**: Claude Opus 5.5 / Claude Code cloud (2026-10-13): research, Phase 0 (PR #1),
  Phase 1 (PR #2), Phase 1b (PR #3), Phase 1c (PR #4), Phase 2 (PR #5), Phase 2b (PR #6), Phase 3 (PR #7), Phase 4 (PR #8), Phase 4b (PR #9), Phase 5 (PR #10), Phase 6 (PR #11), Phase 7 (PR #12), Phase 8 (PR #13), Phase 9 (PR #14), Phase 10 (PR #15), Phase 11 (PR #16), Phase 12 (PR #17), Phase 13 (PR #18), Phase 14 (PR #19), Phase 15 (PR #20), Phase 16 (PR #21), all merged; Phase 17 in PR #22.

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
