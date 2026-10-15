# SESSION-STATE — Mailbird, working name (24-mailbird)

_Last updated: 2026-10-15 — checkpoint (PRs #1–#25 merged; Phase 21 change a booking in PR #26)_

---

## Current state (rewritten atomically — no stale fields)

### 🤝 Live handoff (the baton — any agent reads this FIRST)

- **TL;DR (for future agent)**: An open-source, ad-free PIM "super app" with mail, calendar,
  contacts, and notes. It is mobile-first and runs on the web plus Tauri shells. The code is in
  `snds/Mailbird`, and its docs/ folder holds the research, license audit, architecture, and ADRs.
- **Current focus**: Phase 38, the design-system cleanup (ADR-0048), on Mailbird branch `ds-cleanup`. Its upstream half is `snds/unicron#2` (branch `ds-promotions`, CI green). Merge order: unicron#2 first, then re-pin `vendor/unicron` to its squash commit on main, then the Mailbird PR. Both need Sean's word. PR #42 (Unicron consumption, ADR-0047) is merged as ba4ffad. DSA review page: https://claude.ai/artifact/Qd8nQsy82wRnAgNfuhC4Li. Live demo preview: https://claude.ai/artifact/FhmYjBeUVUAdWWxK37eMvu. Roadmap: https://claude.ai/artifact/RuSar7aj6GxqcgHzmXv61x.
- **Working set**:
  - unicron: `packages/ui/src/components/icon-button.tsx`, `icon.tsx` (`tone`), `ui/button.tsx` (`shape`, `ghost-muted`, `ghost-destructive`), `ui/dialog.tsx` (`DialogActions`, `DialogAction`, title Back button, corner close hidden on phones with a Cancel), `ui/sheet.tsx` (`fullscreen`), `docs/03-components.md`, `docs/04-patterns.md` (promotion log).
  - Mailbird: ~45 files in `apps/web/src`, `.dsa/baseline.json` (241/2/0/0), `docs/decisions/0048-design-system-cleanup.md`.
  - Scratch: before/after captures in the Mailbird scratchpad (`capture-ds.mjs`, `cmp.mjs`, and the `ds-before` and `ds-after2` folders), plus the codemod at `scratchpad/codemod.py`.
- **Last action**: Applied Sean's two calls (glass menus; dialog actions as a row of round icon buttons on phones, laid out like Apple's sheet controls). Before that: 37/38 suites passed, and the one failure (phase2b) was a test bug, an event made near midnight spans two days, fixed in the test. The full rerun is in progress.
- **Next action**: When the rerun is green, push `ds-cleanup`, open the Mailbird PR, republish the review page and the live preview, then wait on Sean's word to merge. After that, product work: graph view, menu-bar mini calendar, power settings. Next DS sweep: 43 raw `<button>`s in 24 files.
  Follow-ups: drop orphaned images after a grace period, a full-screen image view, multi-page scans, more OCR languages, native scanners (VisionKit / ML Kit) in the device spike.
  Sean must register a Google OAuth client and a Microsoft Entra app for real sign-ins (`docs/google-verification.md`, `docs/microsoft-setup.md`).
  Test-harness note: start the notes relay with a fresh (new, never-used) data dir for each sync run — don't `rm -rf` a variable path (the safety check blocks it). Clear the shared Dovecot mailbox and SMTP sink before gateway suites (`seed_p12.py reset`). Test servers and the vite preview stop when the container restarts. The cloud proxy blocks codeload.github.com tarballs, so use `git+https` git deps, never `github:`. The built-in browser can't open container localhost; preview through the Artifact (vite build --base ./; tesseract's `.gz` model isn't a servable type, so text reading is off there). The host wraps the page in its own skeleton with unlayered `body{background:#fff;color:#000;font:14px system}`, which beats the app's `@layer base`: keep the preview-only `<style>` in the published index.html (`:root{color-scheme:light dark} body{font:inherit;background:var(--background);color:var(--foreground)}`) or dark mode breaks.
- **Open decisions**: (1) the product name, which collides with Mailbird, Inc. (ADR-0006). Google verification is blocked on it;
  (2) the Tauri mobile spike vs Capacitor (ADR-0002); (3) when to subset the Material Symbols font
  (ADR-0003); (4) whether to keep Apache-2.0 for the repo license. (5) **Scope add from Lockdown (2026-10-15, Sean):** a self-host bundle with a mail server, DNS tooling and 3-2-1 backup lives in Mailbird's scope; locked notes get a Lockdown recovery path when linked (Lockdown D5, D7; see `snds/lockdown` `docs/plan/00-ecosystem.md`). **Also (Lockdown D12):** Mailbird is the test-bed for the shared identity/persona crate, built in `crates/core` first with the Phase 33 note lock as first consumer, extracted later. Not scheduled yet; shared notes waits for it (Sean confirmed 2026-10-15). **On hold (Sean, 2026-10-15): don't start the crate.** Sean is settling its two open decisions with the Lockdown session: the ecosystem identifier, and whether Android shares one signing key (`snds/lockdown` `docs/plan/01-identity.md` §11).
- **Blocked on**: nothing. No TLS round trip against a live provider has been tested yet, because
  cloud egress blocks it.
- **In-flight / do-not-touch**: none.
- **Agent thread**: Claude Opus 5.5 / Claude Code cloud (2026-10-13): research, Phase 0 (PR #1),
  Phase 1 (PR #2), Phase 1b (PR #3), Phase 1c (PR #4), Phase 2 (PR #5), Phase 2b (PR #6), Phase 3 (PR #7), Phase 4 (PR #8), Phase 4b (PR #9), Phase 5 (PR #10), Phase 6 (PR #11), Phase 7 (PR #12), Phase 8 (PR #13), Phase 9 (PR #14), Phase 10 (PR #15), Phase 11 (PR #16), Phase 12 (PR #17), Phase 13 (PR #18), Phase 14 (PR #19), Phase 15 (PR #20), Phase 16 (PR #21), Phase 17 (PR #22), Phase 18 (PR #23), Phase 19 (PR #24), Phase 20 (PR #25), Phase 21 (PR #26), Phase 22 (PR #27), Phase 23 (PR #28), Phase 24 (PR #29), Phase 25 (PR #30), Phase 26 (PR #31), Phase 27 (PR #32), Phase 28 (PR #33), Phase 29 (PR #34), Phase 30 (PR #35), Phase 31 (PR #36), Phase 32 (PR #37), Phase 33 (PR #38), Phase 34 (PR #39), Phase 35 (PR #40), Phase 36 (PR #41), all merged; Unicron in PR #42.

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
