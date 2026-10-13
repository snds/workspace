# SESSION-STATE — Mailbird, working name (24-mailbird)

_Last updated: 2026-10-13 — checkpoint (PRs #1–#3 merged; Phase 1c in PR #4)_

---

## Current state (rewritten atomically — no stale fields)

### 🤝 Live handoff (the baton — any agent reads this FIRST)

- **TL;DR (for future agent)**: An open-source, ad-free PIM "super app" with mail, calendar,
  contacts, and notes. It is mobile-first and runs on the web plus Tauri shells. The code is in
  `snds/Mailbird`, and its docs/ folder holds the research, license audit, architecture, and ADRs.
- **Current focus**: Phase 1c mail polish, in review as PR #4 (`phase-1c-mail`). PRs #1–#3 are merged.
- **Working set**: `crates/core/src/{store,net,net/jmap,model}.rs`, `crates/core/tests/{imap_smtp,jmap}.rs`,
  `apps/web/src/features/mail/{composer,rich-editor,use-rich-editor,rich-text,attachment-preview,attachment-kind,conversation-view}.tsx|ts`,
  `apps/web/src-tauri/src/{workers,commands}.rs`, `docs/decisions/0009-mail-polish.md`.
- **Last action**: Built and verified Phase 1c:
  - Sent/Archive sync-back (IMAP special-use with push-then-fetch; JMAP account-wide with in-place moves).
  - Unarchive op, and an explicit Message-ID for Sent dedupe.
  - JMAP EventSource push.
  - Attachment previews (img, magic-checked PDF, text).
  - Tiptap rich-text composer (multipart/alternative, pinned 3.31.3).
- **Next action**: Merge PR #4, then Phase 2 (CalDAV/CardDAV, calendar and contacts). Mail follow-ups
  that remain: CONDSTORE/QRESYNC, server Drafts, and pasted inline images.
- **Open decisions**: (1) the product name, which collides with Mailbird, Inc. (ADR-0006);
  (2) the Tauri mobile spike vs Capacitor (ADR-0002); (3) when to subset the Material Symbols font
  (ADR-0003); (4) whether to keep Apache-2.0 for the repo license.
- **Blocked on**: nothing. No TLS round trip against a live provider has been tested yet, because
  cloud egress blocks it.
- **In-flight / do-not-touch**: none.
- **Agent thread**: Claude Opus 5.5 / Claude Code cloud (2026-10-13): research, Phase 0 (PR #1),
  Phase 1 (PR #2), Phase 1b (PR #3), all merged; Phase 1c (PR #4).

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
- **Gotcha**: Sonner restores focus to the pre-toast element when a toast unmounts, which steals
  focus from a dialog opened by a toast action. The composer reclaims focus for its first second.
- **Gotcha**: the shadcn registry host may be blocked by cloud network policy. Components come from
  a shadcn-ui/ui git clone through `tools/shadcn-material/transform.mjs`.

### VCS state
- `phase-1c-mail`: Phase 1c, in PR #4. `main` has Phases 0, 1, and 1b.
