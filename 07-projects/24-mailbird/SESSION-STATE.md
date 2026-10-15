# SESSION-STATE — Mailbird, working name (24-mailbird)

_Last updated: 2026-10-15 — checkpoint (PRs #1–#25 merged; Phase 21 change a booking in PR #26)_

---

## Current state (rewritten atomically — no stale fields)

### 🤝 Live handoff (the baton — any agent reads this FIRST)

- **TL;DR (for future agent)**: An open-source, ad-free PIM "super app" with mail, calendar,
  contacts, and notes. It is mobile-first and runs on the web plus Tauri shells. The code is in
  `snds/Mailbird`, and its docs/ folder holds the research, license audit, architecture, and ADRs.
- **Current focus**: Phase 33 ("Locked notes") is in review as PR #38 (`phase-33`). PR #37 (smart folders) is merged (squash db5bd95) on Sean's "Merge and continue when ready". Roadmap checklist artifact: https://claude.ai/artifact/RuSar7aj6GxqcgHzmXv61x.
- **Working set**: `crates/core/src/notes_lock.rs` (PBKDF2 + AES-256-GCM, `NotesLockSetting` synced), `notes_store.rs` (schema v16 `locked`/`sealed`, `apply_lock`, `AFTER_COLS` 12, save refuses locked), `crates/core/Cargo.toml` (`ring` no longer behind `net`), `crates/app/src/notes_commands.rs` (key in `AppState.notes_key`, 10-min idle lock), `apps/web/src/features/notes/lock.tsx`, `note-detail.tsx`, `note-editor.tsx` (`locked` mode), `sync.ts` (`blank`, lock setting in the index), `core/demo-notes.ts`, `docs/decisions/0043-locked-notes.md`.
- **Last action**: Built Phase 33. Tests: core+app 224, demo `phase33` (17 checks), two-device `phase33-sync` through a real relay (6 checks; relay file has no plaintext after lock), `notes-sync`, and all 36 earlier suites clean.
- **Next action**: Watch PR #38's CI. Merge only on Sean's explicit word. Next planned: 34 images + scan/OCR, 35 sketches, 36 graph view, 37 shared notes, 38 menu-bar mini calendar, 39 power settings, 40 opt-in AI (needs Sean's call on where it runs), 41 shared drafts. Update the roadmap artifact as each lands.
  Then, remaining harvest: notes graph view, checklist items drawn on cards, locked notes, repeating note reminders (location reminders wait for the device spike); mail shared drafts and opt-in AI; learn a person's usual reading hour instead of a fixed 9:00 (ADR-0041 consequences). Creating Zoom/Teams meetings needs their OAuth apps. Or the device spike, or the product rename.
  Sean must register a Google OAuth client and a Microsoft Entra app for real sign-ins (`docs/google-verification.md`, `docs/microsoft-setup.md`).
  Notes follow-ups: end-to-end encryption to the relay, images, linking from the note side, and export.
  Test-harness note: start the notes relay with a fresh data dir for each notes-sync run. Clear the shared Dovecot mailbox and SMTP sink before gateway suites (`seed_p12.py reset`). Both test servers, and the vite preview, stop when the container restarts; restart them first.
- **Open decisions**: (1) the product name, which collides with Mailbird, Inc. (ADR-0006). Google verification is blocked on it;
  (2) the Tauri mobile spike vs Capacitor (ADR-0002); (3) when to subset the Material Symbols font
  (ADR-0003); (4) whether to keep Apache-2.0 for the repo license.
- **Blocked on**: nothing. No TLS round trip against a live provider has been tested yet, because
  cloud egress blocks it.
- **In-flight / do-not-touch**: none.
- **Agent thread**: Claude Opus 5.5 / Claude Code cloud (2026-10-13): research, Phase 0 (PR #1),
  Phase 1 (PR #2), Phase 1b (PR #3), Phase 1c (PR #4), Phase 2 (PR #5), Phase 2b (PR #6), Phase 3 (PR #7), Phase 4 (PR #8), Phase 4b (PR #9), Phase 5 (PR #10), Phase 6 (PR #11), Phase 7 (PR #12), Phase 8 (PR #13), Phase 9 (PR #14), Phase 10 (PR #15), Phase 11 (PR #16), Phase 12 (PR #17), Phase 13 (PR #18), Phase 14 (PR #19), Phase 15 (PR #20), Phase 16 (PR #21), Phase 17 (PR #22), Phase 18 (PR #23), Phase 19 (PR #24), Phase 20 (PR #25), Phase 21 (PR #26), Phase 22 (PR #27), Phase 23 (PR #28), Phase 24 (PR #29), Phase 25 (PR #30), Phase 26 (PR #31), Phase 27 (PR #32), Phase 28 (PR #33), Phase 29 (PR #34), Phase 30 (PR #35), Phase 31 (PR #36), Phase 32 (PR #37), all merged; Phase 33 in PR #38.

### Design rules (from Sean's reviews)
- **Sheets on phones are bottom sheets** (2026-10-15, PR #31): full width, slide up from the bottom, a set three-quarter height (75dvh, room to breathe), rounded top corners, grab handle (drag down to dismiss), and a small (40px) floating close button in the bottom-right corner for thumb reach (Apple's newer controls; revised in a second review the same day). From `sm` up the same component is a side panel. Use `AdaptiveSheetContent` (`apps/web/src/components/ui/sheet.tsx`, tokens `--c-sheet-*`) for any new sheet; don't hand-build a phone variant. Media query for overlays (the viewport is their container); container queries for in-layout components.

### Environment
- **Context profile**: `personal-solo` + `visibility: public`.
- **Code repo**: `github.com/snds/Mailbird` (default branch `main`).
- **Gotcha**: the Dovecot test server needs a short runtime path (unix sockets fail on long
  paths); `tools/test-mail-servers/start.sh` defaults to `/tmp/mbtest`.
- **Gotcha**: Stalwart 0.16 keeps its config in its database. `start-jmap.sh` drives the bootstrap API. The
  bootstrap admin is synthetic (its Email/query fails), so tests use a real `tester@localhost.test`.
  GitHub release downloads are blocked in cloud sessions, so the script builds from source.
- **Gotcha**: the notes relay for tests is `node server.mjs` from tools/notes-relay; stop it with `for pid in $(pgrep -f '^node server.mjs'); do kill $pid; done`.
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
