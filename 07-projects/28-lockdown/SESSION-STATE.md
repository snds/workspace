# SESSION-STATE — Lockdown

_Last updated: 2026-10-16 — PR #44 merged; step 3 to Mailbird, step 4 in progress (checkpoint)_

---

## Current state (rewritten atomically — no stale fields)

### 🤝 Live handoff (the baton)

- **TL;DR (for future agent)**: Lockdown is a planned cross-platform password manager, passkey provider, and authenticator meant to meet and beat 1Password, Bitwarden, Proton Pass, Vaultwarden, and Apple Passwords. Research is done and in the repo. Nothing built. Three decisions wait on Sean.
- **Current focus**: **Plan set v0.1 is in the repo** (`docs/plan/00`–`06` + `decisions.md`, about 22k words). Identity crate format v1.1 is the keystone. Roadmap under D9: v1 = 122 features, ~155 person-months, recommended 10–12 engineers with a staged ramp, v1 in 15–18 months. Earlier today Sean decided (D1–D13, D14 confirmed by action, repo `docs/plan/decisions.md`): all three positioning layers; a Lockdown × Mailbird ecosystem that works alone; shared persona contract; enclave pairing; locked notes recoverable with the Lockdown kit; shared plugin doctrine; self-host bundle as value-add; vendor bridges to a maybe backlog; feature-complete v1. Next is the plan set.
- **Working set**: Repo `~/Projects/lockdown`: `docs/plan/` (00–06, decisions), `docs/research/2026-10-15/` (brief, matrix, verification, report, seven reports). Readable copy: https://claude.ai/artifact/PT8FzNxTVLzrUr3AdVWHry.
- **Last action**: Recorded D1–D9 and the ecosystem sketch (repo `81d5c84`). Earlier: ran four parallel research passes, three gap sweeps, eight fact-check passes, a matrix and brief synthesis, and a critic pass. Built and published the report page. Pushed everything as the first commit on `main` (`e6d9248`). Scaffolded this project. By Claude Fable 5.1 · Claude Code (cloud) · vm.
- **Identity crate PR is up: `snds/Mailbird` #44** (branch `identity-crate`, `d2e7373`, +6,299 lines, 27 files; ADR-0049 Proposed). Spec §10 steps 1–2: records/envelopes (canonical CBOR, Ed25519, AAD-bound XChaCha20-Poly1305), Argon2id with a signed floor, HKDF AUK per 04-security §3, **hybrid X25519+ML-KEM-768 implemented** (X-Wing), the §5 store with a signed hash-chained manifest, create/attach/recover/adopt, recovery kit (Crockford base32), OPAQUE and keystores behind traits, JSON Schemas. Tests: 6 unit + 11 conformance + 2 schema pass; `pim-core` still 220/220. Eight deviations proposed as D18–D25 in `decisions.md`. CI running; this session watches the PR. **No merge without Sean.** Follow-ups: §10 step 3 (re-wrap the Phase 33 note-lock key), step 4 (handshake behind a test double).
- **PR #44 merged** (squash `e133551`, Sean: "Approved and merge. The deviations and gap look fine."). D18–D25 approved; D26 (accepted gap) and D27 (step division) recorded; spec is v1.3. **Step 3** (re-wrap the Phase 33 note-lock key as Mailbird's App Data Key) handed to the Mailbird session with precise intent (ADR-0050+, no self-merge). **Step 4** (local handshake behind a transport trait, Unix-socket first real transport, short authentication string, D26 enforcement) being built by this session on branch `identity-handshake`, crate-only; PR to follow.
- **Next action**: watch the step-4 PR to green; Sean reviews it and Mailbird's step-3 PR; then step 3 (note-lock re-wrap) and step 4 (handshake behind a test double). In parallel, Sean reads `00-big-picture.md`, `01-identity.md` §0 and §11, and `06-roadmap.md` §3 (staffing), and answers the open questions below. Then: hand `01-identity.md` §10 to the Mailbird session as the build order for the identity crate; open the trademark check on the names; resolve the brief §7 blockers (Apple export-list rules, Android hybrid on real devices).
- **Open decisions**: staffing scenario (roadmap recommends 10–12 with a ramp; 6–8 means 20–24 months; 4–5 cannot deliver D9); ecosystem identifier name (App Group / package family) and whether Android apps share one signing key (01-identity §11); TV device-code flow in v1 or v1.x; developer-tools parity rows in v1 (+~10 PM) or v1.x; audit firm budget by month 6; team size and timeline under D9; the name (no trademark check); licence; whether the self-host bundle ships under one name; whether TV device-code activation is v1 or backlog.
- **Blocked on**: nothing. (Sean confirmed via the Mailbird session that Mailbird Phase 37, shared notes, waits for the identity crate: D12 sequencing accepted.)
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
