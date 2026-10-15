# SESSION-STATE — Synapse

_Last updated: 2026-10-15 — Stage 1 items 1–3 done, CI green; D86 proposed_

---

## Current state (rewritten atomically — no stale fields)

### 🤝 Live handoff (the baton)

- **TL;DR (for future agent)**: Synapse (codename; was Switchyard) is a planned desktop workspace app with a tray service, for Mac and Windows. It makes an AI workspace visible and manageable over plain files, runs checks without an agent, creates and imports workspaces with scorecards, and walls personas. The credential router is its Personas & access module (`plan/access/`). Planning only; nothing built.
- **Current focus**: **Stage 1 (engine), app joins early (D85).** Items 1–3 are done, with CI green on Linux, macOS and Windows (repo `4ba93e6`). Next: the app shell on the real index, then item 4 (router).
- **Working set**: Repo `~/Projects/synapse`: `docs/plan/`, `docs/stage-0/STAGE-0.md`, `brand/`, `catalog/`, `schemas/v1/`, `scripts/`, `corpus/`. T1 snapshot: `~/Projects/synapse-sandbox/t1-workspace@4e2b6cf/` (read-only, local only). Readable copy (plan set v2.12): https://claude.ai/artifact/VoPXvWfgPkc8ArsmtmESHt.
- **Last action**: Stage 1 item 3: `sy-index` (parser and SQLite index in the app's data folder, incremental by size, modified time and hash, moves by ID, invalid YAML recorded as an issue) and `sy index`. T1: full index 0.83–0.94 s, 100% of 2,161 accounted for, matching Stage 0. Live workspace: 1,900 files, 100%, no-change refresh 0.13 s. Found that `07-projects/03-omni` is a nested git repository (987 files): it's now recorded as a boundary and never indexed (D86, proposed). Earlier: the Emphasis Engine accent was already fixed upstream; Synapse's theme was regenerated with the engine's accessibility switches on. By Claude Opus 5.5 · Claude Code · Work MBP.
- **Next action**: Sean approves D86 and decides where the shared component registry lives (D83). Then the app shell on the real index: Tauri 2 wrapper, TanStack Router, Home and Health from `sy-index`. Then item 4 (router). Still waiting on: Apple support (membership), the Windows PC (tell Sean before starting), YubiKey firmware version.
- **Naming rule (standing)**: Use "Synapse" for the app. Its one home is `brand/brand.json` in the repo (fact `n-v1jhd2e8.name`). Every other appearance is listed in `brand/name-ledger.json`. After adding the name anywhere (repo or vault), run `python3 scripts/name-ledger.py --vault ~/Projects/workspace` from the repo, then `--write` once reviewed. Identifiers never carry the name (D37): use the `sy` prefix.
- **Open decisions**: D86 (nested repositories are boundaries); where the shared shadcn registry lives (D83); Apple Developer Program (blocked; Sean emailed Apple support); the public name (trademark check not done); generator engine; plugin runtime; `python-cross-platform-gui` (spoke or project skill).
- **Blocked on**: nothing. Sensitive-data cleanup is deferred to after Stage 3 (D63, D65). Recommended now regardless: rotate the API key a memory note names, and review Drive link sharing.
- **In-flight / do-not-touch**: Scan output folder `~/Projects/synapse-sandbox/scan-t1@4e2b6cf-v1/` (local only; it holds employer terms). Probe results `~/Projects/synapse-sandbox/surface-probe-*.json` (local only; installed apps and versions). The T1 snapshot is read-only.
- **Agent thread**: Claude/Claude Code (2026-10-14): feasibility, then one-page proposal, then credential plan v1, then reframe to the workspace app (plan v2.0), then codename Synapse (plan v2.1).

### Environment
- **Context profile**: `personal-solo`
- **Machine**: Work MacBook Pro (planning only; the code will be personal, in `~/Projects/synapse`)
- **Workspace root**: the checkout containing `AGENTS.md`
- **Project root**: `07-projects/26-synapse/` (vault baton); code and plan in the repo `~/Projects/synapse`

### VCS state
- **Branch**: workspace `main` (vault docs only)
- **Repo**: `snds/synapse` (private, `personal-solo`), branch `main`

---

## History (append-only)

- **2026-10-14** — Project created. Feasibility review, then a one-page proposal (artifact `switchyard-proposal_v1.0`). Sean chose Vaultwarden on Unraid over 1Password, required Windows and both personal and employer identities, and set a product-grade security bar with an optional commercial path (GUI workspace generator over `wsx`). Plan set written in `plan/`.
- **2026-10-14** — Sean answered the three open questions: the Windows PC is personal-only; personas are user-defined, walled by app or by duplicate installs; employer IT allows it. He then reframed the product: logins are a symptom, and the real problem is that the workspace can't be seen or managed without heavy agent work. Switchyard became a desktop workspace app. The credential plan moved to `plan/access/` as the Personas & access module. Plan set v2.0 written: big picture, model, architecture, app, create and import, measurement, security, roadmap. Sean's domain idea led to a proposal to make Domain and Area first-class nodes.
- **2026-10-14** — Codename changed from Switchyard to Synapse (D37), and the folder renamed to `26-synapse`. The name must be tracked everywhere it appears so it can be swapped for branding or legal reasons. The name ledger and its check are now a Stage 0 deliverable; Sean asked for no scan yet. Paused so Sean can read the plan.
- **2026-10-14** — Sean asked for a way to update stale values once, like a design-system component, while keeping Markdown readable, staying standards-first, indexing reliably without agents, and handling languages and formats later. Plan v2.2 added facts (one source, many places), readable-without-Synapse, Agent Skills compliance, stable IDs, and stored-standard/shown-local values with region detected from OS settings (no prompts). D38–D43.
- **2026-10-14** — Sean asked to auto-place rules, skills and tools where each agent app reads them, using OS conventions and known locations. Plan v2.3 added the Surface installer (D44). He then asked about SSO, device linking like Signal, an encrypted credential fallback, and encrypting the vault. Claude gave its opinion; adding it to the plan is pending.
- **2026-10-14** — Sean chose passkeys for personal use and asked for Touch ID and Windows Hello unlock with timeout settings. Plan v2.4 added Accounts, linking and encryption (D45–D50).
- **2026-10-14** — Stage 0 started. Sean declared the repo (`profile_resolve.py scan`). Repo `snds/synapse` created and pushed (`915b1c2`). The vault plan moved to the repo. Sean approved the `skills-ref` install and has a YubiKey. He'll set up DNS on Squarespace from instructions.
- **2026-10-14** — Stage 0 continued: skills-ref check (D52, D53), model v1 (D54–D62), routing oracle, scan protocol and first deep scan (730/730 files, 639 findings), build in public with sealed facts later (D63–D65), domain map approved (D66–D68), item 11 diagrams. Then item 7: surface catalog v1 with 39 surfaces, verified on macOS by an existence-only probe (repo `fff32b5`).
- **2026-10-14** — Stage 0 item 4: standards check v1 (29 standards in `catalog/standards.json`), `standards-lint.py`, D69–D74 proposed (repo `92597dd`).
- **2026-10-15** — Sean approved D51 and D69–D74. Stage 0 item 10: name ledger as the first fact (`brand/`, `scripts/name-ledger.py`).
- **2026-10-15** — Sean chose to host the identity subdomain on his existing Cloudflare zone instead of snds.design (D75). Hosting rules proposed (D76). The host name is kept in the private repo, not here.
- **2026-10-15** — Identity host live: Sean set up Cloudflare Pages and an Access Bypass policy; checked from outside (200, no login in front).
- **2026-10-15** — Apple Developer Program: account page shows the free tier; enroll is blocked ("already associated with the Account Holder of a membership"). Sean to check the Developer app, email, or Apple support.
- **2026-10-15** — Searched Gmail for Apple Developer Program mail (with Sean's go): none found. Recommended Apple support.
- **2026-10-15** — Stage 0 spikes on Mac: 5 of 8 pass (repo `291fd5e`). D77 and D78 proposed. Sean emailed Apple support about the membership.
- **2026-10-15** — Sean approved D76–D78 and the fix-backs ("merge and continue"). Applied them (repo `9eb3182`, workspace `110a7de`). Stage 1 planned (`0053f4c`); D79, D80 proposed.
- **2026-10-15** — Sean approved D79 and D80. Discussed the app's front end (same base as Fontface and Mailbird, plus router, query cache, Emphasis Engine theme).
- **2026-10-15** — Sean approved D81–D84. UI prototype built and checked (`8e0b8e2`).
- **2026-10-15** — D85: engine first, app joins early. Stage 1 item 1 done (`4f1eebb`), CI green on Linux, macOS and Windows.
- **2026-10-15** — Stage 1 item 2 done (`e9426ff`), CI green on all three platforms.
- **2026-10-15** — Emphasis Engine dark-accent bug: already fixed upstream (parity output); a separate session added a guard test (emphasis-engine `d527149`). Synapse's theme regenerated through Vite's loader with all four accessibility switches on; stopgap removed (repo `7df7347`).
- **2026-10-15** — Stage 1 item 3 done (`4ba93e6`), CI green on all three platforms. D86 proposed.
