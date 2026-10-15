# SESSION-STATE — Synapse

_Last updated: 2026-10-15 — review items merged; Stage 1 planned (D79, D80 proposed)_

---

## Current state (rewritten atomically — no stale fields)

### 🤝 Live handoff (the baton)

- **TL;DR (for future agent)**: Synapse (codename; was Switchyard) is a planned desktop workspace app with a tray service, for Mac and Windows. It makes an AI workspace visible and manageable over plain files, runs checks without an agent, creates and imports workspaces with scorecards, and walls personas. The credential router is its Personas & access module (`plan/access/`). Planning only; nothing built.
- **Current focus**: **Stage 1 planned** (`docs/stage-1/STAGE-1.md` in the repo, `0053f4c`): 11 work items, about 50 days, exit tests E1–E8. D79 and D80 await Sean. Stage 0 is done except three spikes waiting on the Windows PC or the Apple Developer membership.
- **Working set**: Repo `~/Projects/synapse`: `docs/plan/`, `docs/stage-0/STAGE-0.md`, `brand/`, `catalog/`, `schemas/v1/`, `scripts/`, `corpus/`. T1 snapshot: `~/Projects/synapse-sandbox/t1-workspace@4e2b6cf/` (read-only, local only). Readable copy (plan set v2.12): https://claude.ai/artifact/VoPXvWfgPkc8ArsmtmESHt.
- **Last action**: Sean approved D76–D78 and the fix-backs. Applied D77 to model §9.2 and D78 to `tool.schema.json` (repo `9eb3182`). Applied the workspace fix-backs (`110a7de`): `workspace_mcp.py` 1.1 is dual-era MCP (2026-07-28 plus the handshake versions up to 2025-11-25; self-test 45/45; both eras smoke-tested on the live vault); `llms.txt` follows llmstxt.org; 14 frontmatter values quoted. Gates: nightly rebuild OK, workspace-harness PASS. Wrote the Stage 1 plan. By Claude Opus 5.5 · Claude Code · Work MBP.
- **Next action**: Sean approves D79 (line-targeted frontmatter writes) and D80 (tool runner in core, no unreviewed third-party tools), then Stage 1 item 1: scaffold the Cargo workspace and macOS + Windows CI. Still waiting on: Apple support (membership), the Windows PC (tell Sean before starting), YubiKey firmware version.
- **Naming rule (standing)**: Use "Synapse" for the app. Its one home is `brand/brand.json` in the repo (fact `n-v1jhd2e8.name`). Every other appearance is listed in `brand/name-ledger.json`. After adding the name anywhere (repo or vault), run `python3 scripts/name-ledger.py --vault ~/Projects/workspace` from the repo, then `--write` once reviewed. Identifiers never carry the name (D37): use the `sy` prefix.
- **Open decisions**: D79, D80; Apple Developer Program (blocked: inactive membership; Sean emailed Apple support); the public name (trademark check not done); generator engine; plugin runtime; `python-cross-platform-gui` (spoke or project skill).
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
