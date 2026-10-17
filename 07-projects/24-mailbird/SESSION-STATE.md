# SESSION-STATE — Mailbird, working name (24-mailbird)

_Last updated: 2026-10-17 — checkpoint (PRs through #50 merged; Phase 43 power settings in PR #51)_

---

## Current state (rewritten atomically — no stale fields)

### 🤝 Live handoff (the baton — any agent reads this FIRST)

- **TL;DR (for future agent)**: An open-source, ad-free PIM "super app" with mail, calendar,
  contacts, and notes. It is mobile-first and runs on the web plus Tauri shells. The code is in
  `snds/Mailbird`, and its docs/ folder holds the research, license audit, architecture, and ADRs.
- **Current focus**: Phase 44, shared notes (ADR-0056), is open as Mailbird #52 on branch `shared-notes`. Phase 43 (power settings) merged as #51. Phase 44: a per-note share link (edit or view) through the owner's relay; `crates/core/src/note_shares.rs` (schema v19), the relay's `mailbird/shared/<id>` docs with HMAC share tokens and the index `shares` list, `features/notes/{share-link,shared-docs,share-dialog,shared-note-card,use-add-shared}.ts(x)`. Ratchet flat at 240. Merge only on Sean's word.
- **Working set**:
  - Mailbird #52: the files above, plus `features/notes/{sync,sync-runner,note-editor,note-detail,index}.tsx`, `features/mail/conversation-view.tsx`, `core/{types,client,demo,demo-notes}.ts`, `crates/core/src/{model,notes_store,notes_lock,store}.rs`, `crates/app/src/{dispatch,notes_commands}.rs`, `tools/notes-relay/{server,test}.mjs` + README, `docs/decisions/0056-shared-notes.md`.
  - Upgrading unicron: change the version in the two tarball URLs (`apps/web/package.json`, the tokens override in `pnpm-workspace.yaml`), `pnpm install`, then the screen comparison and `pnpm ds:ratchet`.
  - Scratch: `pw/phase41.mjs` and `pw/gateway-p41.mjs` in the Mailbird scratchpad; `regress.sh` now runs 40 suites (about 25 minutes, so run it in the background with a 30-minute timeout). Never run prettier here: there's no config, and its defaults reflow whole files.
- **Last action**: Merged #51 on Sean's word. Built Phase 44 (Sean chose "Share link"), verified it (relay tests, core 233, app, clippy, phase44 36 checks with a real relay, ratchet 240), opened PR #52, subscribed, and set a 50-minute check-in. Full regression (43 suites) was running at push; re-run phase44 after the final rebuild.
- **Next action**: Confirm the regression and CI, then merge #52 on Sean's word. Next: the raw-button DS sweep. OS-dependent checks are batched for a hardware session (ADR-0054's checklist, the mobile device spike). Follow-ups: E2E for shared notes, images for guests, who-has-the-link presence; answering read receipts (prompt only), a sync window, per-account intervals; map follow-ups.
  Follow-ups: drop orphaned images after a grace period, a full-screen image view, multi-page scans, more OCR languages, native scanners (VisionKit / ML Kit) in the device spike.
  Sean must register a Google OAuth client and a Microsoft Entra app for real sign-ins (`docs/google-verification.md`, `docs/microsoft-setup.md`).
  Test-harness note: start the notes relay with a fresh (new, never-used) data dir for each sync run — don't `rm -rf` a variable path (the safety check blocks it). Clear the shared Dovecot mailbox and SMTP sink before gateway suites (`seed_p12.py reset`). Test servers and the vite preview stop when the container restarts. The cloud proxy blocks codeload.github.com tarballs, so use `git+https` git deps, never `github:`. The built-in browser can't open container localhost; preview through the Artifact (vite build --base ./; tesseract's `.gz` model isn't a servable type, so text reading is off there). The host wraps the page in its own skeleton with unlayered `body{background:#fff;color:#000;font:14px system}`, which beats the app's `@layer base`: keep the preview-only `<style>` in the published index.html (`:root{color-scheme:light dark} body{font:inherit;background:var(--background);color:var(--foreground)}`) or dark mode breaks.
- **Open decisions**: (1) the product name, which collides with Mailbird, Inc. (ADR-0006). Google verification is blocked on it;
  (2) the Tauri mobile spike vs Capacitor (ADR-0002); (3) when to subset the Material Symbols font
  (ADR-0003); (4) whether to keep Apache-2.0 for the repo license. (5) **Scope add from Lockdown (2026-10-15, Sean):** a self-host bundle with a mail server, DNS tooling and 3-2-1 backup lives in Mailbird's scope; locked notes get a Lockdown recovery path when linked (Lockdown D5, D7; see `snds/lockdown` `docs/plan/00-ecosystem.md`). **Also (Lockdown D12):** Mailbird is the test-bed for the shared identity/persona crate, built in `crates/core` first with the Phase 33 note lock as first consumer, extracted later. Not scheduled yet; shared notes waits for it (Sean confirmed 2026-10-15). **Being built by the Lockdown session** (Sean green-lit it) on Mailbird branch `identity-crate` (`crates/identity`). Don't start it here, and don't edit the root `Cargo.toml` until that PR lands. The Phase 33 note-lock re-wrap follows as that session's PR. Sean is settling its two open decisions with the Lockdown session: the ecosystem identifier, and whether Android shares one signing key (`snds/lockdown` `docs/plan/01-identity.md` §11).
- **Blocked on**: nothing. No TLS round trip against a live provider has been tested yet, because
  cloud egress blocks it.
- **In-flight / do-not-touch**: none.
- **Agent thread**: Claude Opus 5.5 / Claude Code cloud (2026-10-13): research, Phase 0 (PR #1),
  Phase 1 (PR #2), Phase 1b (PR #3), Phase 1c (PR #4), Phase 2 (PR #5), Phase 2b (PR #6), Phase 3 (PR #7), Phase 4 (PR #8), Phase 4b (PR #9), Phase 5 (PR #10), Phase 6 (PR #11), Phase 7 (PR #12), Phase 8 (PR #13), Phase 9 (PR #14), Phase 10 (PR #15), Phase 11 (PR #16), Phase 12 (PR #17), Phase 13 (PR #18), Phase 14 (PR #19), Phase 15 (PR #20), Phase 16 (PR #21), Phase 17 (PR #22), Phase 18 (PR #23), Phase 19 (PR #24), Phase 20 (PR #25), Phase 21 (PR #26), Phase 22 (PR #27), Phase 23 (PR #28), Phase 24 (PR #29), Phase 25 (PR #30), Phase 26 (PR #31), Phase 27 (PR #32), Phase 28 (PR #33), Phase 29 (PR #34), Phase 30 (PR #35), Phase 31 (PR #36), Phase 32 (PR #37), Phase 33 (PR #38), Phase 34 (PR #39), Phase 35 (PR #40), Phase 36 (PR #41), Phase 37 (PR #42), Phase 38 (PR #43), identity crate (#46, #47), Phase 39 (PR #45), Phase 40 (PR #48), Phase 41 (PR #49), Phase 42 (PR #50), all merged; Phase 43 power settings in PR #51 (2026-10-17), Phase 44 shared notes in PR #52 (2026-10-17).

### Design rules (from Sean's reviews)
- **Menus are frosted glass** (2026-10-15, DSA review): never override a menu to solid.
- **Dialog actions on phones are a row of round 40px icon buttons** (2026-10-15, DSA review): ✓ to confirm (filled), × to cancel, and a tinted trash can on the far left. They follow the layout of Apple's sheet controls, not the glass look. Use `DialogActions` / `DialogAction` from `@unicron/ui` for any dialog with a Cancel. A single-action dialog keeps a text button.
- **Sheets on phones are bottom sheets** (2026-10-15, PR #31): full width, slide up from the bottom, a set three-quarter height (75dvh, room to breathe), rounded top corners, grab handle (drag down to dismiss), and a small (40px) floating close button in the bottom-right corner for thumb reach (Apple's newer controls; revised in a second review the same day). From `sm` up the same component is a side panel. Use `AdaptiveSheetContent` from `@unicron/ui` (`wide` prop for wider panels; tokens `--c-sheet-*`) for any new sheet; don't hand-build a phone variant. Media query for overlays (the viewport is their container); container queries for in-layout components.

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
- **Gotcha**: AdaptiveSheetContent's `className` styles the inner scroll area, not the panel; use its `wide` prop for a wider side panel.
- **Gotcha**: the cloud disk fills from `target/` (about 20 GB). Use `CARGO_INCREMENTAL=0`, or delete `target/debug/incremental`.
- **Gotcha**: React events cross portals. A dialog opened inside the composer's `<form>` must stop submit and keydown propagation, or it sends the message. shadcn's base `CommandDialog` needs its children wrapped in `<Command>`.
- **Gotcha**: TanStack `mutate(args, { onSuccess })` per-call callbacks don't run if the component unmounts first. Close a view after the toast, not before. Base UI menu radio items need `closeOnClick`.
- **Gotcha**: the shadcn registry host may be blocked by cloud network policy. Components come from
  a shadcn-ui/ui git clone through `tools/shadcn-material/transform.mjs`.

### VCS state
- `phase-8-calm-inbox`: Phase 8, in PR #13. `main` has Phases 0 through 7.
