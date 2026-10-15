# SESSION-STATE — Lockdown

_Last updated: 2026-10-15 — Sean's decisions D1–D9 recorded (checkpoint)_

---

## Current state (rewritten atomically — no stale fields)

### 🤝 Live handoff (the baton)

- **TL;DR (for future agent)**: Lockdown is a planned cross-platform password manager, passkey provider, and authenticator meant to meet and beat 1Password, Bitwarden, Proton Pass, Vaultwarden, and Apple Passwords. Research is done and in the repo. Nothing built. Three decisions wait on Sean.
- **Current focus**: Sean decided (D1–D12, repo `docs/plan/decisions.md`): all three positioning layers; a Lockdown × Mailbird ecosystem that works alone; shared persona contract; enclave pairing; locked notes recoverable with the Lockdown kit; shared plugin doctrine; self-host bundle as value-add; vendor bridges to a maybe backlog; feature-complete v1. Next is the plan set.
- **Working set**: Repo `~/Projects/lockdown`: `docs/plan/decisions.md`, `docs/plan/00-ecosystem.md` (contract sketch), `docs/research/2026-10-15/` (brief, matrix, verification, report, seven reports). Readable copy: https://claude.ai/artifact/PT8FzNxTVLzrUr3AdVWHry.
- **Last action**: Recorded D1–D9 and the ecosystem sketch (repo `81d5c84`). Earlier: ran four parallel research passes, three gap sweeps, eight fact-check passes, a matrix and brief synthesis, and a critic pass. Built and published the report page. Pushed everything as the first commit on `main` (`e6d9248`). Scaffolded this project. By Claude Fable 5.1 · Claude Code (cloud) · vm.
- **Next action**: Write the plan set in `docs/plan/` the way Synapse did: big picture, model (incl. the shared identity schema), architecture, security, self-host bundle, roadmap re-estimated for a feature-complete v1 (D9). Start with the shared identity crate's format (D10–D12; it is built in Mailbird first). Then resolve the brief §7 blockers (Apple export-list rules, Android hybrid on real devices).
- **Open decisions**: (persona-schema owner resolved by D10: a shared Rust crate, Lockdown as reference implementation) team size and timeline under D9; the name (no trademark check); licence; whether the self-host bundle ships under one name; whether TV device-code activation is v1 or backlog.
- **Blocked on**: nothing.
- **In-flight / do-not-touch**: nothing. The research scratch files on the cloud VM are gone once the session ends; the repo holds the canonical copies.
- **Agent thread**: Claude Fable 5.1/Claude Code cloud (2026-10-15): research dossier, report page, repo first commit, project scaffold; next = Sean's three decisions.

### Environment
- **Context profile**: `personal-solo`
- **Machine**: cloud VM (`vm`, unknown host, most restrictive rules). The next session is likely a Mac.
- **Workspace root**: the checkout containing `AGENTS.md`
- **Project root**: `07-projects/28-lockdown/` (vault baton); research in the repo `~/Projects/lockdown`

### VCS state
- **Branch**: workspace `main` (vault docs only)
- **Repo**: `snds/lockdown` (private, `personal-solo`), branch `main` @ `e6d9248`
- **Uncommitted changes**: no
- **Test state at last check**: not applicable (no code)

### Active tooling / MCP bridges
- **Filesystem access**: native (this checkout)
- **Figma MCP**: not connected this session (proxy refused the tunnel)
- **Playwright**: local Chromium used for the report screenshots; not an MCP bridge

### Open work and paused threads
- **Currently in progress**: nothing
- **Pending questions**: team and timeline for a feature-complete v1
- **What's needed to resume**: read `docs/plan/decisions.md` and `00-ecosystem.md`, then start the plan set. The matrix is the feature backlog; under D9 treat every parity row as v1.

---

## Session history (append-only)

### 2026-10-15 — checkpoint (seeded)

**Focus this session**: deep competitive research on password managers and the vendor-login idea (Steam QR, Battle.net, Adobe).
**Machine**: cloud VM
**Stopped because**: research complete; decisions need Sean.

**Accomplishments**:
- Seven research reports, 45 fact-checked claims, a 201-feature matrix, an 11,600-word brief, and a published report page.
- Repo `snds/lockdown` initialised with the research as its first commit.
- Project folder seeded and registered in the workspace.

**Decisions made** (later the same day):
- D1–D9 in the repo decision log: all three positioning layers; ecosystem with Mailbird that works alone; vendor bridges parked; feature-complete v1.
- Earlier: none. The brief recommends: lead with breadth, prove with security, keep open source and free export as policy; Steam opt-in in v1.x; decline Battle.net, Adobe, Discord, and all vendor push emulation.

**Next resumption needs**:
- Sean's answers to the three questions. Then the plan set, modelled on Synapse's `docs/plan/`.

_Seeded by Claude Fable 5.1 on 2026-10-15. Initial state reflects the research dossier and the first repo commit._
