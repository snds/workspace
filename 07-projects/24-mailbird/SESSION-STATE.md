# SESSION-STATE — Mailbird, working name (24-mailbird)

_Last updated: 2026-10-14 — checkpoint (PRs #1–#11 merged; Phase 7 mail power in PR #12)_

---

## Current state (rewritten atomically — no stale fields)

### 🤝 Live handoff (the baton — any agent reads this FIRST)

- **TL;DR (for future agent)**: An open-source, ad-free PIM "super app" with mail, calendar,
  contacts, and notes. It is mobile-first and runs on the web plus Tauri shells. The code is in
  `snds/Mailbird`, and its docs/ folder holds the research, license audit, architecture, and ADRs.
- **Current focus**: Phase 7 ("mail power") is in review as PR #12 (`phase-7-mail-power`). Sean said "merge then continue phases", so PR #11 is merged. The roadmap defined nothing after Phase 6, so I chose Phase 7 from the research's feature harvest: send later, follow-up reminders, one-tap unsubscribe, signatures and templates, and a ⌘K menu. Sean can redirect.
- **Working set**: `crates/core/src/{compose_store,unsubscribe}.rs`, `crates/core/src/net/unsubscribe.rs`, `crates/app/src/compose_commands.rs`,
  `apps/web/src/features/{command-palette,writing-settings}.tsx`, `apps/web/src/features/mail/{send-later,scheduled-list,unsubscribe-button,signature,lanes}.ts(x)`,
  `docs/decisions/0017-mail-power.md`.
- **Last action**: Merged PR #11 on Sean's word, then built Phase 7:
  - Schema v7. Follow-ups are keyed by Message-ID and cleared by replies. The UI adds Waiting and Scheduled tabs.
  - Unsubscribe uses RFC 8058 one-click, refusing private-network addresses.
  - Signatures are normalized through the Tiptap schema so they can be swapped.
  - The new demo Playwright suite `phase7` passes, and the 13 earlier suites pass (4 needed exact Send/Reply locators). The gateway e2e on real Dovecot and SMTP passes.
  - Fixed: the composer's focus guard closed menus opened from it.
- **Next action**: Watch PR #12's CI. Merge only on Sean's explicit word.
  Then: the device spike (`docs/mobile-spike.md`) on Sean's hardware. Or pick the next harvest items: a screener for first-time senders, smart inbox lanes, Gmail labels, a public OAuth return address for the gateway. Or the product rename.
  Sean must register a Google OAuth client and a Microsoft Entra app for real sign-ins (`docs/google-verification.md`, `docs/microsoft-setup.md`).
  Notes follow-ups: end-to-end encryption to the relay, images, linking from the note side, and export.
  Calendar follow-ups: free/busy, COUNTER, and missed-reminder catch-up.
- **Open decisions**: (1) the product name, which collides with Mailbird, Inc. (ADR-0006). Google verification is blocked on it;
  (2) the Tauri mobile spike vs Capacitor (ADR-0002); (3) when to subset the Material Symbols font
  (ADR-0003); (4) whether to keep Apache-2.0 for the repo license.
- **Blocked on**: nothing. No TLS round trip against a live provider has been tested yet, because
  cloud egress blocks it.
- **In-flight / do-not-touch**: none.
- **Agent thread**: Claude Opus 5.5 / Claude Code cloud (2026-10-13): research, Phase 0 (PR #1),
  Phase 1 (PR #2), Phase 1b (PR #3), Phase 1c (PR #4), Phase 2 (PR #5), Phase 2b (PR #6), Phase 3 (PR #7), Phase 4 (PR #8), Phase 4b (PR #9), Phase 5 (PR #10), Phase 6 (PR #11), all merged; Phase 7 in PR #12.

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
- **Gotcha**: the shadcn registry host may be blocked by cloud network policy. Components come from
  a shadcn-ui/ui git clone through `tools/shadcn-material/transform.mjs`.

### VCS state
- `phase-7-mail-power`: Phase 7, in PR #12. `main` has Phases 0 through 6.
