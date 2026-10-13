# SESSION-STATE — Mailbird, working name (24-mailbird)

_Last updated: 2026-10-13 — checkpoint (Phase 0 merged as PR #1; Phase 1 mail MVP in PR #2)_

---

## Current state (rewritten atomically — no stale fields)

### 🤝 Live handoff (the baton — any agent reads this FIRST)

- **TL;DR (for future agent)**: An open-source, ad-free PIM "super app" with mail, calendar,
  contacts, and notes. It is mobile-first and runs on the web plus Tauri shells. The code is in
  `snds/Mailbird`, and its docs/ folder holds the research, license audit, architecture, and ADRs.
- **Current focus**: Phase 1 mail MVP, in review as PR #2 (`phase-1-mail` → `main`). PR #1
  (foundation) is merged.
- **Working set**: `crates/core/src/{store,net,mime,model}.rs`, `crates/core/tests/imap_smtp.rs`,
  `apps/web/src-tauri/src/{commands,workers,secrets}.rs`, `apps/web/src/{core,features/mail}/`,
  `tools/test-mail-servers/`, `docs/decisions/0007-mail-engine.md`.
- **Last action**: Built and verified the mail MVP:
  - Store, IMAP sync, and SMTP send.
  - Undo-send outbox and local snooze.
  - Keychain storage for passwords.
  - Triage UI with sanitized HTML and blocked trackers.
  - 23 unit tests and a Dovecot integration test pass.
  - Playwright flows pass with no page errors.

  By Claude Opus 5.5 · Claude Code (cloud) · no local device.
- **Next action**: Merge PR #2, then Phase 1b:
  1. IMAP IDLE push.
  2. The JMAP adapter.
  3. Attachments and threads.
  4. Backfill beyond 500 messages.
  5. Swipe gestures.
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
- **Gotcha**: the shadcn registry host may be blocked by cloud network policy. Components come from
  a shadcn-ui/ui git clone through `tools/shadcn-material/transform.mjs`.

### VCS state
- `main`: Phase 0 foundation (squash-merged from PR #1).
- `phase-1-mail`: the mail MVP, in PR #2.
