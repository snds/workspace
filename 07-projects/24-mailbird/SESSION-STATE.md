# SESSION-STATE — Mailbird, working name (24-mailbird)

_Last updated: 2026-10-14 — checkpoint (PRs #1–#6 merged; Phase 3 in PR #7)_

---

## Current state (rewritten atomically — no stale fields)

### 🤝 Live handoff (the baton — any agent reads this FIRST)

- **TL;DR (for future agent)**: An open-source, ad-free PIM "super app" with mail, calendar,
  contacts, and notes. It is mobile-first and runs on the web plus Tauri shells. The code is in
  `snds/Mailbird`, and its docs/ folder holds the research, license audit, architecture, and ADRs.
- **Current focus**: Phase 3 notes, in review as PR #7 (`phase-3-notes`). PRs #1–#6 are merged.
- **Working set**: `crates/core/src/{notes_store,notes_import}.rs`, `apps/web/src-tauri/src/notes_commands.rs`,
  `apps/web/src/features/notes/*` (editor, sync, ydoc, import, relay dialog), `apps/web/src/core/demo-notes.ts`,
  `tools/notes-relay/` (Hocuspocus relay + test), `docs/decisions/0012-notes.md`.
- **Last action**: Merged PR #6, then built and verified Phase 3:
  - Notes stored as Markdown and edited as Yjs, with checklists and the first line as the title.
  - Live sync through a self-hosted Hocuspocus relay: one record index, plus one Yjs document per note.
  - Links to events, contacts, and conversations.
  - Import from Keep Takeout and Markdown folders.
- **Next action**: Merge PR #7, then Phase 4 (Gmail API + Google verification, Microsoft Graph).
  Notes follow-ups: end-to-end encryption to the relay, images, linking from the note side, and export.
  Calendar follow-ups: free/busy, COUNTER, and missed-reminder catch-up.
- **Open decisions**: (1) the product name, which collides with Mailbird, Inc. (ADR-0006);
  (2) the Tauri mobile spike vs Capacitor (ADR-0002); (3) when to subset the Material Symbols font
  (ADR-0003); (4) whether to keep Apache-2.0 for the repo license.
- **Blocked on**: nothing. No TLS round trip against a live provider has been tested yet, because
  cloud egress blocks it.
- **In-flight / do-not-touch**: none.
- **Agent thread**: Claude Opus 5.5 / Claude Code cloud (2026-10-13): research, Phase 0 (PR #1),
  Phase 1 (PR #2), Phase 1b (PR #3), Phase 1c (PR #4), Phase 2 (PR #5), Phase 2b (PR #6), all merged; Phase 3 (PR #7).

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
- **Gotcha**: Stalwart serves CalDAV/CardDAV on the same :8080 listener (`/.well-known/caldav` → `/dav/cal`), so the DAV test reuses `start-jmap.sh`.
- **Gotcha**: calcard pairs overrides with their series by SEQUENCE. Strip SEQUENCE before `expand_dates`, or a bumped override duplicates its occurrence.
- **Gotcha**: Hocuspocus allows one provider per document name per socket, and a destroyed provider's close can unsubscribe its replacement. Use `sessionAwareness: true`, and never pass `onSynced: undefined` (it replaces the default handler).
- **Gotcha**: the shadcn registry host may be blocked by cloud network policy. Components come from
  a shadcn-ui/ui git clone through `tools/shadcn-material/transform.mjs`.

### VCS state
- `phase-3-notes`: Phase 3, in PR #7. `main` has Phases 0 through 2b.
