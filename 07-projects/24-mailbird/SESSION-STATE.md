# SESSION-STATE — Mailbird, working name (24-mailbird)

_Last updated: 2026-10-13 — checkpoint (PR #1, #2 merged; Phase 1b in PR #3)_

---

## Current state (rewritten atomically — no stale fields)

### 🤝 Live handoff (the baton — any agent reads this FIRST)

- **TL;DR (for future agent)**: An open-source, ad-free PIM "super app" with mail, calendar,
  contacts, and notes. It is mobile-first and runs on the web plus Tauri shells. The code is in
  `snds/Mailbird`, and its docs/ folder holds the research, license audit, architecture, and ADRs.
- **Current focus**: Phase 1b mail depth, in review as PR #3 (`phase-1b-mail`). PRs #1 and #2 are merged.
- **Working set**: `crates/core/src/{store,net,net/jmap,mime}.rs`, `crates/core/tests/{imap_smtp,jmap}.rs`,
  `apps/web/src/features/mail/{conversation-view,swipe-row,composer}.tsx`,
  `tools/test-mail-servers/start-jmap.sh`, `docs/decisions/0008-mail-depth.md`.
- **Last action**: Built and verified Phase 1b:
  - Conversations and attachments.
  - IDLE push and progressive backfill.
  - JMAP sync and send.
  - Swipe gestures.
  - The JMAP test runs against a Stalwart built from source.
- **Next action**: Merge PR #3, then Phase 1c:
  1. JMAP push (EventSource).
  2. Syncing Sent and Archive back from the server.
  3. A rich-text composer.
  4. Attachment previews.

  Or move to Phase 2 (calendar and contacts).
- **Open decisions**: (1) the product name, which collides with Mailbird, Inc. (ADR-0006);
  (2) the Tauri mobile spike vs Capacitor (ADR-0002); (3) when to subset the Material Symbols font
  (ADR-0003); (4) whether to keep Apache-2.0 for the repo license.
- **Blocked on**: nothing. No TLS round trip against a live provider has been tested yet, because
  cloud egress blocks it.
- **In-flight / do-not-touch**: none.
- **Agent thread**: Claude Opus 5.5 / Claude Code cloud (2026-10-13): research, Phase 0 (PR #1,
  merged), Phase 1 (PR #2).

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
- **Gotcha**: the shadcn registry host may be blocked by cloud network policy. Components come from
  a shadcn-ui/ui git clone through `tools/shadcn-material/transform.mjs`.

### VCS state
- `phase-1b-mail`: Phase 1b, in PR #3. `main` has Phase 0 + Phase 1.
