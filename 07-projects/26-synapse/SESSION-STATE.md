# SESSION-STATE — Synapse

_Last updated: 2026-10-14 — Stage 0: model v1 draft done, awaiting Sean review_

---

## Current state (rewritten atomically — no stale fields)

### 🤝 Live handoff (the baton)

- **TL;DR (for future agent)**: Synapse (codename; was Switchyard) is a planned desktop workspace app with a tray service, for Mac and Windows. It makes an AI workspace visible and manageable over plain files, runs checks without an agent, creates and imports workspaces with scorecards, and walls personas. The credential router is its Personas & access module (`plan/access/`). Planning only; nothing built.
- **Current focus**: **Stage 0: model v1 draft is done and waiting for Sean's review** (repo `a2057a8`). D54–D62 are proposed.
- **Working set**: Repo `~/Projects/synapse`: `docs/plan/`, `docs/stage-0/STAGE-0.md`, `scripts/`, `corpus/`. T1 snapshot: `~/Projects/synapse-sandbox/t1-workspace@4e2b6cf/` (read-only, local only). Readable copy: https://claude.ai/artifact/VoPXvWfgPkc8ArsmtmESHt.
- **Last action**: Wrote workspace model v1: `docs/model/model-v1.md` (contract), 20 JSON Schemas with 24 examples (`scripts/check-schemas.py` passes), and the layout map for Sean's dialect (100% of T1 typed). `scripts/model-fit.py` shows the fit after the mechanical migration: skills 296/348, memory 43/47, knowledge 119/126, projects 10/12. Remaining failures are D53 or real defects listed in `docs/stage-0/model-fit-v0.md`. Aligned the plan (`sy:` markers, 8-character IDs, the vault's relation types). Raw fit results stay local (`~/Projects/synapse-sandbox/`) because some paths name the employer. D52 and D53 approved. By Claude Opus 5.5 · Claude Code · Work MBP.
- **Next action**: Sean reviews model v1 and D54–D62. In parallel: the routing oracle (item 8), then the scan protocol and first deep scan (item 9), the surface catalog schema (item 7), and the standards check (item 4).
- **Naming rule (standing)**: Use "Synapse" for the app from now on. Any new place the name appears (file, path, identifier, artifact title) must later be listed in the Stage 0 name ledger. User-facing text takes the name from one brand file. Internal identifiers use the neutral `sy` prefix. **No ledger scan has been run yet, by Sean's choice.** Places the name appears today: this folder's docs and paths, the build script's title, `.gitignore`, `06-context/project-registry.md`, `06-context/project-context.md`, and the published plan's title. The old name stays in decision rows D1–D36, this file's history, git history and the one-page proposal artifact, all as history.
- **Open decisions**: D54–D62 (model v1, proposed); D51; the public name; generator engine; plugin runtime; the domain map (after the first scan); Apple Developer Program membership.
- **Blocked on**: nothing for model v1. Sean's side: Cloudflare Pages plus a Squarespace CNAME for `id.snds.design` (instructions given 2026-10-14); his YubiKey's model (it needs FIDO2: YubiKey 5, Security Key or Bio series); the Windows PC later for the spikes.
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
- **2026-10-14** — Stage 0 started. Sean declared the repo (`profile_resolve.py scan`). Repo `snds/synapse` created and pushed (`915b1c2`). The vault plan moved to the repo. Sean approved the `skills-ref` install and has a YubiKey. He'll set up DNS on Squarespace from instructions.
