# SESSION-STATE — Synapse

_Last updated: 2026-10-14 — checkpoint (plan v2.4: accounts, linking and encryption)_

---

## Current state (rewritten atomically — no stale fields)

### 🤝 Live handoff (the baton)

- **TL;DR (for future agent)**: Synapse (codename; was Switchyard) is a planned desktop workspace app with a tray service, for Mac and Windows. It makes an AI workspace visible and manageable over plain files, runs checks without an agent, creates and imports workspaces with scorecards, and walls personas. The credential router is its Personas & access module (`plan/access/`). Planning only; nothing built.
- **Current focus**: Sean is reviewing the plan (v2.4). Wait for his feedback, then Stage 0 on his go.
- **Working set**: `07-projects/26-synapse/plan/*.md` and `plan/access/*.md` (source). `tools/build-plan-html.py` builds `05-artifacts/active/synapse-plan_v2.4_2026-10-14.html`, published at https://claude.ai/artifact/VoPXvWfgPkc8ArsmtmESHt.
- **Last action**: Plan v2.4: added 'Accounts, linking and encryption' to `plan/06-security.md`. It covers: no account for personal use; keys separate from identity; desktop unlock with Touch ID and Windows Hello, with three lock layers and timeout settings; QR or code linking; recovery passkey (PRF), then printed key, then optional passphrase; what syncs; vault encryption (disk, optional encrypted sync, opt-in `age` sealed notes); commercial SSO that never decrypts. Threaded through the model, architecture, app (journey 8), commercial path, roadmap, tests X8–X14 and D45–D50. Earlier: v2.3 Surface installer (D44). By Claude Opus 5.5 · Claude Code · Work MBP.
- **Next action**: Take Sean's notes on the plan. On his go, start Stage 0 (`plan/07-roadmap.md`): repo, sandbox snapshot, model v1, first deep scan and domain map, baselines, and spikes (including Touch ID/Hello unlock and passkey PRF).
- **Naming rule (standing)**: Use "Synapse" for the app from now on. Any new place the name appears (file, path, identifier, artifact title) must later be listed in the Stage 0 name ledger. User-facing text takes the name from one brand file. Internal identifiers use the neutral `sy` prefix. **No ledger scan has been run yet, by Sean's choice.** Places the name appears today: this folder's docs and paths, the build script's title, `.gitignore`, `06-context/project-registry.md`, `06-context/project-context.md`, and the published plan's title. The old name stays in decision rows D1–D36, this file's history, git history and the one-page proposal artifact, all as history.
- **Open decisions**: the public name (trademark check); frontmatter placement (leaning: under `metadata`, pending the Stage 0 check on lists); generator engine (recommended: Rust core with `wsx` as oracle); plugin runtime (recommended: MCP-server plugins); the domain map (after the first scan).
- **Blocked on**: Sean's review of the plan.
- **In-flight / do-not-touch**: none.
- **Agent thread**: Claude/Claude Code (2026-10-14): feasibility, then one-page proposal, then credential plan v1, then reframe to the workspace app (plan v2.0), then codename Synapse (plan v2.1).

### Environment
- **Context profile**: `personal-solo`
- **Machine**: Work MacBook Pro (planning only; the code will be personal, in `~/Projects/synapse`)
- **Workspace root**: the checkout containing `AGENTS.md`
- **Project root**: `07-projects/26-synapse/` (vault); repo not created

### VCS state
- **Branch**: workspace `main` (vault docs only)
- **Repo**: none yet

---

## History (append-only)

- **2026-10-14** — Project created. Feasibility review, then a one-page proposal (artifact `switchyard-proposal_v1.0`). Sean chose Vaultwarden on Unraid over 1Password, required Windows and both personal and employer identities, and set a product-grade security bar with an optional commercial path (GUI workspace generator over `wsx`). Plan set written in `plan/`.
- **2026-10-14** — Sean answered the three open questions: the Windows PC is personal-only; personas are user-defined, walled by app or by duplicate installs; employer IT allows it. He then reframed the product: logins are a symptom, and the real problem is that the workspace can't be seen or managed without heavy agent work. Switchyard became a desktop workspace app. The credential plan moved to `plan/access/` as the Personas & access module. Plan set v2.0 written: big picture, model, architecture, app, create and import, measurement, security, roadmap. Sean's domain idea led to a proposal to make Domain and Area first-class nodes.
- **2026-10-14** — Codename changed from Switchyard to Synapse (D37), and the folder renamed to `26-synapse`. The name must be tracked everywhere it appears so it can be swapped for branding or legal reasons. The name ledger and its check are now a Stage 0 deliverable; Sean asked for no scan yet. Paused so Sean can read the plan.
- **2026-10-14** — Sean asked for a way to update stale values once, like a design-system component, while keeping Markdown readable, staying standards-first, indexing reliably without agents, and handling languages and formats later. Plan v2.2 added facts (one source, many places), readable-without-Synapse, Agent Skills compliance, stable IDs, and stored-standard/shown-local values with region detected from OS settings (no prompts). D38–D43.
- **2026-10-14** — Sean asked to auto-place rules, skills and tools where each agent app reads them, using OS conventions and known locations. Plan v2.3 added the Surface installer (D44). He then asked about SSO, device linking like Signal, an encrypted credential fallback, and encrypting the vault. Claude gave its opinion; adding it to the plan is pending.
- **2026-10-14** — Sean chose passkeys for personal use and asked for Touch ID and Windows Hello unlock with timeout settings. Plan v2.4 added Accounts, linking and encryption (D45–D50).
