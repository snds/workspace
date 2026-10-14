# SESSION-STATE — Synapse

_Last updated: 2026-10-14 — checkpoint (codename Synapse; paused for Sean's read)_

---

## Current state (rewritten atomically — no stale fields)

### 🤝 Live handoff (the baton)

- **TL;DR (for future agent)**: Synapse (codename; was Switchyard) is a planned desktop workspace app with a tray service, for Mac and Windows. It makes an AI workspace visible and manageable over plain files, runs checks without an agent, creates and imports workspaces with scorecards, and walls personas. The credential router is its Personas & access module (`plan/access/`). Planning only; nothing built.
- **Current focus**: **Paused.** Sean is reading the plan. Wait for his feedback before doing anything else.
- **Working set**: `07-projects/26-synapse/plan/*.md` and `plan/access/*.md` (source). `tools/build-plan-html.py` builds `05-artifacts/active/synapse-plan_v2.1_2026-10-14.html`, published at https://claude.ai/artifact/VoPXvWfgPkc8ArsmtmESHt.
- **Last action**: Renamed the codename Switchyard → Synapse (decision D37). Moved the folder `26-switchyard` → `26-synapse`. Swapped the name across the plan. Made the internal identifiers neutral (`sy`, `sy-access`, `git-credential-sy`, `sy://`, data folders `design.snds.sy` and `%LOCALAPPDATA%\snds\sy`). Repointed `.gitignore`, the project registry and project-context. Added the name ledger to the Stage 0 deliverables. By Claude Opus 5.5 · Claude Code · Work MBP.
- **Next action**: Take Sean's notes on the plan. Then, on his go, start Stage 0 (`plan/07-roadmap.md`).
- **Naming rule (standing)**: Use "Synapse" for the app from now on. Any new place the name appears (file, path, identifier, artifact title) must later be listed in the Stage 0 name ledger. User-facing text takes the name from one brand file. Internal identifiers use the neutral `sy` prefix. **No ledger scan has been run yet, by Sean's choice.** Places the name appears today: this folder's docs and paths, the build script's title, `.gitignore`, `06-context/project-registry.md`, `06-context/project-context.md`, and the published plan's title. The old name stays in decision rows D1–D36, this file's history, git history and the one-page proposal artifact, all as history.
- **Open decisions**: the public name (trademark check); frontmatter placement against the Agent Skills spec; generator engine (recommended: Rust core with `wsx` as oracle); plugin runtime (recommended: MCP-server plugins); the domain map (after the first scan).
- **Blocked on**: Sean's read of the plan.
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
