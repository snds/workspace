# SESSION-STATE — Lockdown

_Last updated: 2026-10-15 — seeded after the research dossier (checkpoint)_

---

## Current state (rewritten atomically — no stale fields)

### 🤝 Live handoff (the baton)

- **TL;DR (for future agent)**: Lockdown is a planned cross-platform password manager, passkey provider, and authenticator meant to meet and beat 1Password, Bitwarden, Proton Pass, Vaultwarden, and Apple Passwords. Research is done and in the repo. Nothing built. Three decisions wait on Sean.
- **Current focus**: Sean reads the brief and decides positioning, the Steam bridge, and team size.
- **Working set**: Repo `~/Projects/lockdown`: `docs/research/2026-10-15/` (brief, matrix, verification, report, seven reports). Readable copy: https://claude.ai/artifact/PT8FzNxTVLzrUr3AdVWHry.
- **Last action**: Ran four parallel research passes, three gap sweeps, eight fact-check passes, a matrix and brief synthesis, and a critic pass. Built and published the report page. Pushed everything as the first commit on `main` (`e6d9248`). Scaffolded this project. By Claude Fable 5.1 · Claude Code (cloud) · vm.
- **Next action**: Sean answers three questions. (1) Positioning: recommended "Every way you sign in. Locked down, even from us." (2) Steam bridge: ship opt-in in v1.x, or cut for zero legal risk. (3) Team size: the roadmap assumes 6 to 8 engineers and 12 to 18 months for v1. Then: write `docs/plan/` (decision log, model, architecture) the way Synapse did, and resolve the open questions in brief §7 that block a spec (Battle.net passkey date, Apple's export-list rules, Android hybrid on real devices).
- **Open decisions**: positioning (A, B, or C); Steam bridge yes or no; team size; the name (no trademark check); licence (OSI for apps, something that keeps self-hosting free for the server); whether to fold Synapse's Personas & access module into Lockdown or keep them separate.
- **Blocked on**: Sean's input on the three questions.
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
- **Pending questions**: the three decisions above
- **What's needed to resume**: read the brief's §1 and §2, then answer the three questions. The matrix is the feature backlog; filter by phase v1.

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

**Decisions made**:
- None by Sean yet. The brief recommends: lead with breadth, prove with security, keep open source and free export as policy; Steam opt-in in v1.x; decline Battle.net, Adobe, Discord, and all vendor push emulation.

**Next resumption needs**:
- Sean's answers to the three questions. Then the plan set, modelled on Synapse's `docs/plan/`.

_Seeded by Claude Fable 5.1 on 2026-10-15. Initial state reflects the research dossier and the first repo commit._
