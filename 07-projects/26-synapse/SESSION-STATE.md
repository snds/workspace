# SESSION-STATE — Synapse

_Last updated: 2026-10-14 — Stage 0: item 7 (surface catalog) done on Mac_

---

## Current state (rewritten atomically — no stale fields)

### 🤝 Live handoff (the baton)

- **TL;DR (for future agent)**: Synapse (codename; was Switchyard) is a planned desktop workspace app with a tray service, for Mac and Windows. It makes an AI workspace visible and manageable over plain files, runs checks without an agent, creates and imports workspaces with scorecards, and walls personas. The credential router is its Personas & access module (`plan/access/`). Planning only; nothing built.
- **Current focus**: **Stage 0.** Item 7 (surface catalog) is done on Mac (repo `fff32b5`); Windows verification waits for the PC spikes. Remaining: item 4 (standards check), item 10 (name ledger as the first fact), and the spikes.
- **Working set**: Repo `~/Projects/synapse`: `docs/plan/`, `docs/stage-0/STAGE-0.md`, `catalog/surfaces.json`, `schemas/v1/`, `scripts/`, `corpus/`. T1 snapshot: `~/Projects/synapse-sandbox/t1-workspace@4e2b6cf/` (read-only, local only). Readable copy (plan set v2.10): https://claude.ai/artifact/VoPXvWfgPkc8ArsmtmESHt.
- **Last action**: Stage 0 item 7. Wrote `catalog/surfaces.json`: 39 surfaces, 90 read locations, all 22 workspace surfaces mapped through a new `aliases` field (Grok Build, OpenCode, Goose and Amp added). Extended the schema additively. Wrote `scripts/surface-probe.py`: it checks existence and size only, never opens config files, keeps machine results in `~/Projects/synapse-sandbox/`, and is idempotent. 11 locations verified on macOS. The probe caught three catalog errors (Claude Code's Windows path, ChatGPT's data folder, Codex detection), all fixed. `check-schemas.py` now validates the catalog. Doc: `docs/stage-0/surface-catalog-v1.md`. By Claude Opus 5.5 · Claude Code · Work MBP.
- **Next action**: Stage 0 item 4: standards check (record current AGENTS.md, MCP and llms.txt versions, and what the model and catalog must follow). Then item 10 (name ledger), then the spikes. Tell Sean before the Windows PC spikes; one of them is a surface probe run with `--apply` (commit only `verified.windows`).
- **Naming rule (standing)**: Use "Synapse" for the app from now on. Any new place the name appears (file, path, identifier, artifact title) must later be listed in the Stage 0 name ledger. User-facing text takes the name from one brand file. Internal identifiers use the neutral `sy` prefix. **No ledger scan has been run yet, by Sean's choice.** Places the name appears today: this folder's docs and paths, the repo `snds/synapse` (docs, scripts, and the catalog's description and notes), the build script's title, `.gitignore`, `06-context/project-registry.md`, `06-context/project-context.md`, and the published plan's title. The old name stays in decision rows D1–D36, this file's history, git history and the one-page proposal artifact, all as history.
- **Open decisions**: D51; the public name; generator engine; plugin runtime; Apple Developer Program membership; `python-cross-platform-gui` (spoke or project skill).
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
- **Repo**: `snds/synapse` (public, `personal-solo`), branch `main`, latest `fff32b5`

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
