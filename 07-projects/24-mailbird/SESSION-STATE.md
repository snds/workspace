# SESSION-STATE — Mailbird, working name (24-mailbird)

_Last updated: 2026-10-17 — checkpoint (PRs through #61 merged; #62–#64 notes-image follow-ups open)_

---

## Current state (rewritten atomically — no stale fields)

### 🤝 Live handoff (the baton — any agent reads this FIRST)

- **TL;DR (for future agent)**: An open-source, ad-free PIM "super app" with mail, calendar,
  contacts, and notes. It is mobile-first and runs on the web plus Tauri shells. The code is in
  `snds/Mailbird`, and its docs/ folder holds the research, license audit, architecture, and ADRs.
- **Current focus**: #61 merged (ADR-0065 relay key SecretField). Three independent PRs open, each off main: #62 unused note images go after 30 days (ADR-0066, schema v23, `filesGone` index map), #63 full-screen image viewer (ADR-0067, `phase50`), #64 multi-page scans (ADR-0068, `phase51`). Merge on Sean's word; any order (each touches different files, except docs/architecture.md rows, which merge cleanly).
- **Working set**:
  - Mailbird stack: #58 E2E — relay `tools/notes-relay/server.mjs` (sealed `mailbird/x/…` logs over stateless messages, `mailbird/registry`, `SEALED` mark), web `features/notes/sealed.ts` (`SealedProvider`), `sync.ts`, `shared-docs.ts`, `relay-dialog.tsx`, core v21 (`NoteShare.key`, `team_threads.key`), app `RelayConfig.key` (keychain `notes-relay-key`). Shared inbox — gateway `apps/gateway/src/members.rs` + `lib.rs` (members.json, invitations, `MEMBER_COMMANDS`, `/api/members|join|here`), `tests/team.rs`, core v22 `inbox_team.rs`, web `features/team/inbox-team.tsx`, `features/team-members.tsx`, `gateway-sign-in.tsx` (`/join`), `isMember()` limits.
  - Scratch: `pw/phase48.mjs` (E2E: laptop, phone, guest, relay :1248, greps the relay data dir), `pw/gateway-p49.mjs` + `scripts/gw49.sh` + `scripts/seed_p49.py` (shared inbox on the debug gateway with Dovecot), `pw/phase47.mjs`, `pw/phase46.mjs`. regress.sh runs 46 suites. Disk: the Rust `target/` grows past the session's allowance (18 GB); delete it when builds die with exit 101.
  - Upgrading unicron: change the version in the two tarball URLs (`apps/web/package.json`, the tokens override in `pnpm-workspace.yaml`), `pnpm install`, then the screen comparison and `pnpm ds:ratchet`.
  - Scratch: `pw/phase41.mjs` and `pw/gateway-p41.mjs` in the Mailbird scratchpad; `regress.sh` now runs 40 suites (about 25 minutes, so run it in the background with a 30-minute timeout). Never run prettier here: there's no config, and its defaults reflow whole files.
- **Last action**: Merged #61 on Sean's word; built #62–#64. Rust (clippy, 245 core tests) and web checks clean; phase50 11/11, phase51 10/10, phase35 15/15 on their branches; full regressions queued branch by branch (`scratchpad/regress-branches.sh`).
- **Next action**: Merge #62–#64 on Sean's word. Remaining follow-ups that need hardware or downloads: more OCR languages (model files), native scanners (VisionKit / ML Kit, device spike), a core clipboard path (`copyRef`) and native image save on desktop/phone. Then what needs Sean: the hardware session, the Google OAuth client and Microsoft Entra app, and the open decisions (product name first).
  Follow-ups: more OCR languages, native scanners (VisionKit / ML Kit) in the device spike. (Orphaned images, the full-screen view, and multi-page scans are #62–#64.)
  Sean must register a Google OAuth client and a Microsoft Entra app for real sign-ins (`docs/google-verification.md`, `docs/microsoft-setup.md`).
  Test-harness note: start the notes relay with a fresh (new, never-used) data dir for each sync run — don't `rm -rf` a variable path (the safety check blocks it). Clear the shared Dovecot mailbox and SMTP sink before gateway suites (`seed_p12.py reset`). Test servers and the vite preview stop when the container restarts. The cloud proxy blocks codeload.github.com tarballs, so use `git+https` git deps, never `github:`. The built-in browser can't open container localhost; preview through the Artifact (vite build --base ./; tesseract's `.gz` model isn't a servable type, so text reading is off there). The host wraps the page in its own skeleton with unlayered `body{background:#fff;color:#000;font:14px system}`, which beats the app's `@layer base`: keep the preview-only `<style>` in the published index.html (`:root{color-scheme:light dark} body{font:inherit;background:var(--background);color:var(--foreground)}`) or dark mode breaks.
- **Inbound 2026-10-17 · Unicron color work — DONE in Mailbird #60 (tokens 0.5.0 / ui 0.7.1; `--vertical-*-text` 600/300, wikilinks, today label, today chip and Screener badge pairs; apca-w3 Lc 79–92; no component contrast patches existed)**: Unicron now judges contrast APCA first, by what each component paints (unicron#27, #30). Mailbird is on tokens 0.1.0 / ui 0.3.0; current is **tokens 0.5.0 / ui 0.7.1**.
  - **What moves for you:** muted text (light `neutral.600`, dark `neutral.200`), focus ring (`neutral.900` / `neutral.100`), field borders `--input` (`neutral.450` / 35% white, now 3:1), `--destructive` (`red.600` / `red.300`, readable as text), light `--warning` `amber.400`, dark `--info` `blue.500` with white text, pressed toggles in the primary fill. Also in ui: dialog `size` (your ~20 dialog overrides), `ItemMain`, `beforeContent` + `--c-dialog-titlebar-inset`, `IconButton` disabled fix.
  - **Nothing to remove:** `app-extension.css` overrides no core role (only `--sidebar`, same value). Check component-level contrast patches you added for old Unicron values; most should now go.
  - **Fix in your roles (measured, APCA Lc; reading text needs 75):** the area hues are fills, and you draw them as text. `text-vertical-notes` ×12 and `--c-note-wikilink-text`: amber Lc 44 light / 70 dark. `text-vertical-mail` ×7: blue 67 / 50. `text-vertical-contacts` ×3: green 60 / 56. `text-vertical-calendar` ×2 and the mini-calendar's today label: coral 65 / 51. The today chip, white on coral: 70 light, 56 dark. **Fix:** add text roles (`--vertical-*-text`) on Unicron's new text steps, `--g-{hue}-600` light and `--g-{hue}-300` dark (Lc 76–87). Keep `--vertical-*` on `500`/`400` for fills, dots and borders. For the dark today chip, use a `600`/`300` fill choice or dark text.
  - **Expect screenshot baselines to shift** (field edges, muted text, destructive, status fills).
- **Inbound 2026-10-17 · next Unicron bump (from the Synapse session):** current is **tokens 0.7.0 / ui 0.9.0** (tokens from unicron #34, #35; you pin tokens 0.5.0 in `pnpm-workspace.yaml`). `--destructive` moved to `red.700` / `red.200`, so destructive text on a selected row reads Lc 76+ (was 74). Light `--warning` moved to `amber.450`, so the fill reads Lc 31+ against the sidebar (was 27). ui 0.8 and 0.9 are additive (multiline `SecretField` with `name`/`required`/`onBlur`, `CommandItemAction`, `Skeleton variant="row"`; CodeDisplay copy by reference). No code change. Screenshots shift slightly for destructive text and the light warning fill.
- **Open decisions**: (1) the product name, which collides with Mailbird, Inc. (ADR-0006). Google verification is blocked on it;
  (2) the Tauri mobile spike vs Capacitor (ADR-0002); (3) when to subset the Material Symbols font
  (ADR-0003); (4) whether to keep Apache-2.0 for the repo license. (5) **Scope add from Lockdown (2026-10-15, Sean):** a self-host bundle with a mail server, DNS tooling and 3-2-1 backup lives in Mailbird's scope; locked notes get a Lockdown recovery path when linked (Lockdown D5, D7; see `snds/lockdown` `docs/plan/00-ecosystem.md`). **Also (Lockdown D12):** Mailbird is the test-bed for the shared identity/persona crate, built in `crates/core` first with the Phase 33 note lock as first consumer, extracted later. Not scheduled yet; shared notes waits for it (Sean confirmed 2026-10-15). **Being built by the Lockdown session** (Sean green-lit it) on Mailbird branch `identity-crate` (`crates/identity`). Don't start it here, and don't edit the root `Cargo.toml` until that PR lands. The Phase 33 note-lock re-wrap follows as that session's PR. Sean is settling its two open decisions with the Lockdown session: the ecosystem identifier, and whether Android shares one signing key (`snds/lockdown` `docs/plan/01-identity.md` §11).
- **Blocked on**: nothing. No TLS round trip against a live provider has been tested yet, because
  cloud egress blocks it.
- **In-flight / do-not-touch**: none.
- **Agent thread**: Claude Opus 5.5 / Claude Code cloud (2026-10-13): research, Phase 0 (PR #1),
  Phase 1 (PR #2), Phase 1b (PR #3), Phase 1c (PR #4), Phase 2 (PR #5), Phase 2b (PR #6), Phase 3 (PR #7), Phase 4 (PR #8), Phase 4b (PR #9), Phase 5 (PR #10), Phase 6 (PR #11), Phase 7 (PR #12), Phase 8 (PR #13), Phase 9 (PR #14), Phase 10 (PR #15), Phase 11 (PR #16), Phase 12 (PR #17), Phase 13 (PR #18), Phase 14 (PR #19), Phase 15 (PR #20), Phase 16 (PR #21), Phase 17 (PR #22), Phase 18 (PR #23), Phase 19 (PR #24), Phase 20 (PR #25), Phase 21 (PR #26), Phase 22 (PR #27), Phase 23 (PR #28), Phase 24 (PR #29), Phase 25 (PR #30), Phase 26 (PR #31), Phase 27 (PR #32), Phase 28 (PR #33), Phase 29 (PR #34), Phase 30 (PR #35), Phase 31 (PR #36), Phase 32 (PR #37), Phase 33 (PR #38), Phase 34 (PR #39), Phase 35 (PR #40), Phase 36 (PR #41), Phase 37 (PR #42), Phase 38 (PR #43), identity crate (#46, #47), Phase 39 (PR #45), Phase 40 (PR #48), Phase 41 (PR #49), Phase 42 (PR #50), all merged; Phase 43 power settings in PR #51 (2026-10-17), Phase 44 shared notes in PR #52 (2026-10-17), the raw-button sweep in PR #53 (2026-10-17), unicron#9 and dsa#2 for its follow-ups, and their adoption in PR #54 (2026-10-17, merged), Phase 45 opt-in AI in PR #55 (2026-10-17, merged), Phase 46 team conversations in PR #56, Phase 47 presence + files in PR #57, Phase 48 end-to-end encrypted sync in PR #58, Phase 49 shared inbox in PR #59 (2026-10-17), and unicron#14.

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
