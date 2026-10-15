# SESSION-STATE — Synapse

_Last updated: 2026-10-14 — Stage 0: first deep scan done; domain map awaiting Sean_

---

## Current state (rewritten atomically — no stale fields)

### 🤝 Live handoff (the baton)

- **TL;DR (for future agent)**: Synapse (codename; was Switchyard) is a planned desktop workspace app with a tray service, for Mac and Windows. It makes an AI workspace visible and manageable over plain files, runs checks without an agent, creates and imports workspaces with scorecards, and walls personas. The credential router is its Personas & access module (`plan/access/`). Planning only; nothing built.
- **Current focus**: **Stage 0: the first deep scan is done** (repo `0736a5e`). Sean reviews `docs/stage-0/domain-map-proposal-v1.md` (10 decisions) and `docs/stage-0/scan-v1-report.md`.
- **Working set**: Repo `~/Projects/synapse`: `docs/plan/`, `docs/stage-0/STAGE-0.md`, `scripts/`, `corpus/`. T1 snapshot: `~/Projects/synapse-sandbox/t1-workspace@4e2b6cf/` (read-only, local only). Readable copy: https://claude.ai/artifact/VoPXvWfgPkc8ArsmtmESHt.
- **Last action**: Added D67 (repo `8b782e3`), per Sean's condition on the domain map: domains organize and never wall off. A new on-demand `uses` edge, plus shared capability areas (vision → computer vision, quality → visual measurement), let any visual domain reach computer vision and vice versa. Model v1 §5.1, the schemas, and a new 'Crossing domains' section in the domain map. Before that: the first deep scan (730/730, 639 findings) and the domain map with 10 decisions. By Claude Opus 5.5 · Claude Code · Work MBP.
- **Next action**: After Sean's domain-map decisions: Stage 0 item 11 (refine the Create and Import diagrams from the scan), item 7 (surface catalog schema), item 4 (standards check), the name ledger as the first fact (item 10), then the spikes. Windows PC spikes need Sean.
- **Naming rule (standing)**: Use "Synapse" for the app from now on. Any new place the name appears (file, path, identifier, artifact title) must later be listed in the Stage 0 name ledger. User-facing text takes the name from one brand file. Internal identifiers use the neutral `sy` prefix. **No ledger scan has been run yet, by Sean's choice.** Places the name appears today: this folder's docs and paths, the build script's title, `.gitignore`, `06-context/project-registry.md`, `06-context/project-context.md`, and the published plan's title. The old name stays in decision rows D1–D36, this file's history, git history and the one-page proposal artifact, all as history.
- **Open decisions**: Sean's explicit OK on the 10 domain-map decisions, now that D67 meets his cross-domain condition; D51; the public name; generator engine; plugin runtime; Apple Developer Program membership.
- **Blocked on**: Sean's domain-map review. Not blocking Stage 0: the sensitive-data cleanup is deferred to after Stage 3 (D63, D65). Recommended now regardless: rotate the API key a memory note says still needs rotating, and review Google Drive link sharing for the personal files that note names.
- **In-flight / do-not-touch**: Scan output folder `~/Projects/synapse-sandbox/scan-t1@4e2b6cf-v1/` (local only; it holds employer terms). The T1 snapshot is read-only.
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
- **2026-10-14** — Stage 0 started. Sean declared the repo (`profile_resolve.py scan`). Repo `snds/synapse` created and pushed (`915b1c2`). The vault plan moved to the repo. Sean approved the `skills-ref` install and has a YubiKey. He'll set up DNS on Squarespace from instructions.
