# SESSION-STATE — Mailbird, working name (24-mailbird)

_Last updated: 2026-10-15 — checkpoint (PRs #1–#25 merged; Phase 21 change a booking in PR #26)_

---

## Current state (rewritten atomically — no stale fields)

### 🤝 Live handoff (the baton — any agent reads this FIRST)

- **TL;DR (for future agent)**: An open-source, ad-free PIM "super app" with mail, calendar,
  contacts, and notes. It is mobile-first and runs on the web plus Tauri shells. The code is in
  `snds/Mailbird`, and its docs/ folder holds the research, license audit, architecture, and ADRs.
- **Current focus**: Unicron consumption (ADR-0047) is in review as PR #42 (branch `unicron`). Sean authorized merging it once CI is green. PRs #40 (Phase 35, scans and text in images) and #41 (Phase 36, sketches) are merged, as is `snds/unicron#1` (the sheet's `wide` prop). Live demo preview (the demo build, republished as changes land): https://claude.ai/artifact/FhmYjBeUVUAdWWxK37eMvu. Roadmap artifact: https://claude.ai/artifact/RuSar7aj6GxqcgHzmXv61x.
- **Working set**: `vendor/unicron` (submodule, pinned to main 5a8cf8e), `pnpm-workspace.yaml` (unicron packages; `onlyBuiltDependencies: ["@snds/dsa"]`), `apps/web/src/styles/app-extension.css` (Mailbird roles + `--c-*` knobs), `apps/web/src/index.css` (`@import "@unicron/ui/styles"`), `dsa.config.json`, `.dsa/baseline.json`, `.github/workflows/ci.yml` (submodules + `pnpm ds:ratchet`), `apps/gateway/Dockerfile` (git installed; vendor packages copied), `tools/shadcn-material/transform.mjs` (`--alias-mode package`), `docs/decisions/0047-unicron.md`.
- **Last action**: Unicron move proven identical: 133 tokens match in light and dark; 15 of 16 screenshots are pixel-identical, and the last differs only by sub-threshold anti-aliasing; all 38 browser suites pass. Then fixed CI on PR #42: the lockfile now clones dsa over HTTPS, and the web image installs git. Replied to the requesting session (session_01DG9oy7EGG6unMww4vC7sSH).
- **Next action**: Merge PR #42 when green (authorized), then republish the preview. **Next phase (Sean, 2026-10-15): a DSA review and cleanup before more product work.** Take stock of the baseline (274 className overrides, 2 style overrides, 2 Button look-alikes: `InterestingCalendarsButton`, `UnsubscribeButton`) and the 28 pattern candidates. Propose promotions to unicron: icon Button/Fab, DialogHeader title+description, DropdownMenuItem with icon, Tooltip icon button, NativeSelect, ActionDialog footer. Clean up the app, then lower the ratchet baseline. After that: graph view, menu-bar mini calendar, power settings. Shared notes waits for the identity/persona crate (Sean confirmed). Later: opt-in AI (needs Sean's call on where it runs), shared drafts.
  Follow-ups: drop orphaned images after a grace period, a full-screen image view, multi-page scans, more OCR languages, native scanners (VisionKit / ML Kit) in the device spike.
  Sean must register a Google OAuth client and a Microsoft Entra app for real sign-ins (`docs/google-verification.md`, `docs/microsoft-setup.md`).
  Test-harness note: start the notes relay with a fresh (new, never-used) data dir for each sync run — don't `rm -rf` a variable path (the safety check blocks it). Clear the shared Dovecot mailbox and SMTP sink before gateway suites (`seed_p12.py reset`). Test servers and the vite preview stop when the container restarts. The cloud proxy blocks codeload.github.com tarballs, so use `git+https` git deps, never `github:`. The built-in browser can't open container localhost; preview through the Artifact (vite build --base ./; tesseract's `.gz` model isn't a servable type, so text reading is off there). The host wraps the page in its own skeleton with unlayered `body{background:#fff;color:#000;font:14px system}`, which beats the app's `@layer base`: keep the preview-only `<style>` in the published index.html (`:root{color-scheme:light dark} body{font:inherit;background:var(--background);color:var(--foreground)}`) or dark mode breaks.
- **Open decisions**: (1) the product name, which collides with Mailbird, Inc. (ADR-0006). Google verification is blocked on it;
  (2) the Tauri mobile spike vs Capacitor (ADR-0002); (3) when to subset the Material Symbols font
  (ADR-0003); (4) whether to keep Apache-2.0 for the repo license. (5) **Scope add from Lockdown (2026-10-15, Sean):** a self-host bundle with a mail server, DNS tooling and 3-2-1 backup lives in Mailbird's scope; locked notes get a Lockdown recovery path when linked (Lockdown D5, D7; see `snds/lockdown` `docs/plan/00-ecosystem.md`). **Also (Lockdown D12):** Mailbird is the test-bed for the shared identity/persona crate, built in `crates/core` first with the Phase 33 note lock as first consumer, extracted later. Not scheduled yet; shared notes waits for it (Sean confirmed 2026-10-15).
- **Blocked on**: nothing. No TLS round trip against a live provider has been tested yet, because
  cloud egress blocks it.
- **In-flight / do-not-touch**: none.
- **Agent thread**: Claude Opus 5.5 / Claude Code cloud (2026-10-13): research, Phase 0 (PR #1),
  Phase 1 (PR #2), Phase 1b (PR #3), Phase 1c (PR #4), Phase 2 (PR #5), Phase 2b (PR #6), Phase 3 (PR #7), Phase 4 (PR #8), Phase 4b (PR #9), Phase 5 (PR #10), Phase 6 (PR #11), Phase 7 (PR #12), Phase 8 (PR #13), Phase 9 (PR #14), Phase 10 (PR #15), Phase 11 (PR #16), Phase 12 (PR #17), Phase 13 (PR #18), Phase 14 (PR #19), Phase 15 (PR #20), Phase 16 (PR #21), Phase 17 (PR #22), Phase 18 (PR #23), Phase 19 (PR #24), Phase 20 (PR #25), Phase 21 (PR #26), Phase 22 (PR #27), Phase 23 (PR #28), Phase 24 (PR #29), Phase 25 (PR #30), Phase 26 (PR #31), Phase 27 (PR #32), Phase 28 (PR #33), Phase 29 (PR #34), Phase 30 (PR #35), Phase 31 (PR #36), Phase 32 (PR #37), Phase 33 (PR #38), Phase 34 (PR #39), Phase 35 (PR #40), Phase 36 (PR #41), all merged; Unicron in PR #42.

### Design rules (from Sean's reviews)
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
