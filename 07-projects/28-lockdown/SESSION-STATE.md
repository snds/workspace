# SESSION-STATE — Lockdown

_Last updated: 2026-10-16 — crate extracted (v0.1.0); Lockdown workspace scaffold in progress (checkpoint)_

---

## Current state (rewritten atomically — no stale fields)

### 🤝 Live handoff (the baton)

- **TL;DR (for future agent)**: Lockdown is a planned cross-platform password manager, passkey provider, and authenticator meant to meet and beat 1Password, Bitwarden, Proton Pass, Vaultwarden, and Apple Passwords. Research is done and in the repo. Nothing built. Three decisions wait on Sean.
- **Current focus**: **Plan set v0.1 is in the repo** (`docs/plan/00`–`06` + `decisions.md`, about 22k words). Identity crate format v1.1 is the keystone. Roadmap under D9: v1 = 122 features, ~155 person-months, recommended 10–12 engineers with a staged ramp, v1 in 15–18 months. Earlier today Sean decided (D1–D13, D14 confirmed by action, repo `docs/plan/decisions.md`): all three positioning layers; a Lockdown × Mailbird ecosystem that works alone; shared persona contract; enclave pairing; locked notes recoverable with the Lockdown kit; shared plugin doctrine; self-host bundle as value-add; vendor bridges to a maybe backlog; feature-complete v1. Next is the plan set.
- **Working set**: Repos `~/Projects/lockdown` (`docs/plan/` 00–07, decisions, Rust workspace) and `~/Projects/ecosystem-identity` (the shared crate), `docs/research/2026-10-15/` (brief, matrix, verification, report, seven reports). Readable copy: https://claude.ai/artifact/PT8FzNxTVLzrUr3AdVWHry.
- **Last action**: Recorded D1–D9 and the ecosystem sketch (repo `81d5c84`). Earlier: ran four parallel research passes, three gap sweeps, eight fact-check passes, a matrix and brief synthesis, and a critic pass. Built and published the report page. Pushed everything as the first commit on `main` (`e6d9248`). Scaffolded this project. By Claude Fable 5.1 · Claude Code (cloud) · vm.
- **Identity crate PR is up: `snds/Mailbird` #44** (branch `identity-crate`, `d2e7373`, +6,299 lines, 27 files; ADR-0049 Proposed). Spec §10 steps 1–2: records/envelopes (canonical CBOR, Ed25519, AAD-bound XChaCha20-Poly1305), Argon2id with a signed floor, HKDF AUK per 04-security §3, **hybrid X25519+ML-KEM-768 implemented** (X-Wing), the §5 store with a signed hash-chained manifest, create/attach/recover/adopt, recovery kit (Crockford base32), OPAQUE and keystores behind traits, JSON Schemas. Tests: 6 unit + 11 conformance + 2 schema pass; `pim-core` still 220/220. Eight deviations proposed as D18–D25 in `decisions.md`. CI running; this session watches the PR. **No merge without Sean.** Follow-ups: §10 step 3 (re-wrap the Phase 33 note-lock key), step 4 (handshake behind a test double).
- **PR #44 merged** (squash `e133551`, Sean: "Approved and merge. The deviations and gap look fine."). D18–D25 approved; D26 (accepted gap) and D27 (step division) recorded; spec is v1.3. **Step 3** (re-wrap the Phase 33 note-lock key as Mailbird's App Data Key) handed to the Mailbird session with precise intent (ADR-0050+, no self-merge). **Step 4** (local handshake behind a transport trait, Unix-socket first real transport, short authentication string, D26 enforcement) being built by this session on branch `identity-handshake`, crate-only; PR to follow.
- **Step 3 status (Mailbird session, 2026-10-16):** built on Mailbird branch `identity-notes-key` as Phase 39 / ADR-0050; PR after its browser regression. Uses the crate API only; on every passphrase unlock/change it opens-or-creates the identity and wraps `NotesKey` as an App Data Key under `personal`; `unlock_notes_with_identity` attaches (never creates) and searches app-data envelopes, which is how a kit-restored device with no local hint gets in; remembers the envelope and the last `Head` for rollback refusal; desktop only, `FileKeystore` at `<app data>/identity-device.key`. Its two API asks became D28 (app label in envelope + AAD) and D29 (retire envelope), added to the step-4 PR scope.
- **Step-4 PR is up: `snds/Mailbird` #46** (branch `identity-handshake`, `b4adaaf`, +4,259/−86, 25 files; ADR-0050 Proposed). Handshake behind `PeerTransport`/`PeerVerifier`/`ConfirmNewDevice` traits; protocol v1 with commit-then-reveal and a six-digit code; in-memory and Unix-socket transports; Linux process-identity verifier built, Apple/Windows declared. D26 closed (`Head.kdf`, `KdfLowered` error). D28 (app label in envelope + AAD) and D29 (retire with tombstone) delivered. Schemas regenerated. Tests: 12 unit + 13 conformance + 5 handshake + 3 kdf-rise + 2 schema; `pim-core` 220/220. D30–D33 proposed. CI running; this session watches it. No merge without Sean.
- **PR #46 merged by Sean** (`e7b0949`, 01:31 UTC). D28–D33 approved by that merge; spec v1.4. Crate steps 1, 2, 4 are on Mailbird main; step 3 is Mailbird PR #45 (Phase 39), which must rebase onto the new `wrap_app_key(persona, app, key)` signature and renumber its ADR to 0051 (0050 is now the handshake ADR on main).
- **What is left in the crate** (spec §10b): QR device enrolment, Apple/Windows/Android verifiers and transports, hardware keystores, OPAQUE client and key transparency (both need the Lockdown server), persona re-keying, extraction to its own repo (§10 step 5, when Lockdown consumes it).
- **Sean chose (a).** Crate extracted to **`snds/ecosystem-identity`** (D34). Its main is `96434d1`: extraction `41c80bc` + socket-path fallback + macOS fix (CI was red on macOS: `setsockopt` returns EINVAL after the peer hangs up, which a refused requester hit; `recv` now sets the timeout once) + macOS peer pid/image via `LOCAL_PEERPID`/`proc_pidpath`. CI green on ubuntu and macos. Tag `v0.1.0` is local only (the cloud git proxy refuses tag pushes); Sean pushes it from a Mac, then consumers move from `rev` to `tag`.
- **Mailbird swap PR is up: `snds/Mailbird` #47** (branch `identity-external`, `639f6df`): `crates/identity` removed, `pim-app` pins the crate at `96434d1` (dev-dep keeps `insecure-test-kdf`), two CI steps dropped, ADR-0049 and the architecture index say where it went. **Merged** on Sean's "merge any remaining open PRs" (squash → Mailbird main `480db92`). Mailbird is the first external consumer; the Mailbird session was told the root Cargo.toml is theirs again.
- **Lockdown Rust workspace is on `snds/lockdown` main** (`2da2aec`, `3c03e91`, `33013cf`, docs `865bdf4`; D35). Verified by this session: fmt clean, clippy clean under `-D warnings`, 66 tests pass, cargo-deny clean (agent run), employer-name grep clean. Real: `crypto` (AEAD with AAD, Argon2id via identity, HKDF, Ed25519, X-Wing, BLAKE3), `matcher` (PSL, 16 equivalent-domain groups, lookalikes, related origins, fill check), `codes` (HOTP/TOTP vectors, Steam 5-char, otpauth/steam URIs), `vault` (18 item kinds, per-field AEAD under the 8-field AAD, place-bound wrapped keys, signed hash-chained manifest with rollback refusal, purge), `cxf` (CXF 1.0 model, round trips, safe CSV). Skeletons with one real rule each: policy, approval, bridge-host, store, sync, ffi, wasm, cli, server. Map and next five steps: `docs/plan/07-workspace.md`. Note: commit `2da2aec` alone does not build; the tree builds from `3c03e91` on.
- **D36–D37 accepted by default; D38 recorded** (Sean: "no thoughts, not a security expert" → security-model details are the building session's call, plain-language line each, batched as audit items; Sean decides scope and anything user-visible). From the scaffold (`decisions.md`): version signatures exclude key envelopes so shredding keeps history; Lockdown-owned `WrappedKey` until identity gains `Purpose::{Vault,Item,Version,Attachment}` (additive crate proposal). Also noted: dependency direction is `crypto → identity`, reverse of the 03-architecture table.
- **Next action**: verify slice 1 when the agent reports (fmt, clippy, tests on both stores, cargo-deny, wall grep), record its decisions, then slice 2 = server first endpoints (OPAQUE, push with revision checks, manifest head acceptance) and the matcher WASM boundary in parallel. Sean: push the `v0.1.0` tag from a Mac. Reference list: the five steps in `07-workspace.md` §4 (store on SQLite behind the `Store` trait, OPAQUE login against the server bin, sync revisions over the server, the CLI as the first real shell, the identity crate proposal for vault purposes). In parallel: unicron PRs #2 and #3 await Sean (→0.2.0), then Mailbird moves off the submodule and Synapse adopts. Still open from before: staffing, name and trademark check, licence, audit budget, TV device-code flow in v1 or v1.x.
- **Open decisions**: staffing scenario (roadmap recommends 10–12 with a ramp; 6–8 means 20–24 months; 4–5 cannot deliver D9); ecosystem identifier name (App Group / package family) and whether Android apps share one signing key (01-identity §11); TV device-code flow in v1 or v1.x; developer-tools parity rows in v1 (+~10 PM) or v1.x; audit firm budget by month 6; team size and timeline under D9; the name (no trademark check); licence; whether the self-host bundle ships under one name; whether TV device-code activation is v1 or backlog.
- **Blocked on**: nothing. (Sean confirmed via the Mailbird session that Mailbird Phase 37, shared notes, waits for the identity crate: D12 sequencing accepted.)
- **In-flight / do-not-touch**: **Slice 1 is being built on `snds/lockdown` main by a Lockdown-session agent (Sean: "Go ahead", 2026-10-17):** SQLite `Store` + `Vault::load/save`, the identity adoption path (attach-not-create, App Data Key via `wrap_app_key(persona, "lockdown", …)`, Vault Key wrapped under it, second-process open through the identity root), the `lockdown` CLI (`init`/`add login`/`list`/`show`/`status`), `docs/plan/08-identity-proposal.md`, D39+ rows, 07-workspace §1/§4 updates. Until it reports: no other agent edits crates/store, crates/vault, bins/cli, or docs/plan in that repo. The research scratch files on the cloud VM are gone once the session ends; the repo holds the canonical copies.
- **Agent thread**: Claude Fable 5.1/Claude Code cloud (2026-10-15): research dossier, report page, repo first commit, project scaffold; next = Sean's three decisions.

### Environment
- **Context profile**: `personal-solo`
- **Machine**: cloud VM (`vm`, unknown host, most restrictive rules). The next session is likely a Mac.
- **Workspace root**: the checkout containing `AGENTS.md`
- **Project root**: `07-projects/28-lockdown/` (vault baton); research in the repo `~/Projects/lockdown`

### VCS state
- **Branch**: workspace `main` (vault docs only)
- **Repos**: `snds/lockdown` main @ `3081ba5`; `snds/ecosystem-identity` main @ `96434d1`; `snds/Mailbird` main @ `480db92` (#47 merged)
- **Uncommitted changes**: no
- **Test state at last check**: lockdown 66/66, clippy clean; ecosystem-identity 37 tests green on ubuntu + macos; Mailbird #47 CI green before merge

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
