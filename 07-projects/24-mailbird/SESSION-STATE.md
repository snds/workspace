# SESSION-STATE — Mailbird, working name (24-mailbird)

_Last updated: 2026-10-13 — checkpoint (Phase 0 foundation pushed, PR #1 open)_

---

## Current state (rewritten atomically — no stale fields)

### 🤝 Live handoff (the baton — any agent reads this FIRST)

- **TL;DR (for future agent)**: An open-source, ad-free PIM "super app" with mail, calendar,
  contacts, and notes. It is mobile-first and runs on the web plus Tauri shells. The code is in
  `snds/Mailbird`, and its docs/ folder holds the research, license audit, architecture, and ADRs.
- **Current focus**: Phase 0 foundation, in review as PR #1 (`foundation` → `main`).
- **Working set**: `apps/web/src/{app,components,features,styles}`, `tools/shadcn-material/`,
  `crates/core/`, `apps/web/src-tauri/`, `docs/`.
- **Last action**: Scaffolded the monorepo and shipped the adaptive shell with 4 verticals on mock
  data. Added the 3-tier tokens, the shadcn → Material Symbols transform, the Tauri 2 shell, the
  Rust capability matrix, and CI. All local checks pass. By Claude Opus 5.5 · Claude Code (cloud) ·
  no local device.
- **Next action**: Merge PR #1, then start Phase 1, the mail MVP:
  1. IMAP/SMTP + JMAP adapters in `pim-core`.
  2. SQLite store + Tantivy search.
  3. Unified inbox, composer, undo send, and snooze.
- **Open decisions**: (1) the product name, which collides with Mailbird, Inc. (ADR-0006);
  (2) the Tauri mobile spike vs Capacitor (ADR-0002); (3) when to subset the Material Symbols font
  (about 5.4 MB, ADR-0003); (4) whether to keep Apache-2.0 for the repo license.
- **Blocked on**: nothing.
- **In-flight / do-not-touch**: none.
- **Agent thread**: Claude Opus 5.5 / Claude Code cloud (2026-10-13): competitive and protocol
  research, OSS license audit, scaffold, and PR #1.

### Environment
- **Context profile**: `personal-solo` + `visibility: public`.
- **Code repo**: `github.com/snds/Mailbird` (default branch `main`).
- **Gotcha**: the shadcn registry host may be blocked by cloud network policy. Components come from
  a shadcn-ui/ui git clone through `tools/shadcn-material/transform.mjs`.

### VCS state
- `main`: initial commit (README, LICENSE, NOTICE, .gitignore).
- `foundation`: the Phase 0 work, in PR #1.
