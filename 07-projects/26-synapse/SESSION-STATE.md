# SESSION-STATE — Synapse

_Last updated: 2026-10-15 — Unicron move up for review: snds/synapse#1 (D90); then Stage 1 item 7_

---

## Current state (rewritten atomically — no stale fields)

### 🤝 Live handoff (the baton)

- **TL;DR (for future agent)**: Synapse (codename; was Switchyard) is a planned desktop workspace app with a tray service, for Mac and Windows. It makes an AI workspace visible and manageable over plain files, runs checks without an agent, creates and imports workspaces with scorecards, and walls personas. The credential router is its Personas & access module (`plan/access/`). Stage 1 (the engine) is being built, and the desktop app already reads the real index.
- **Current focus**: **Stage 1 (engine), app joins early (D85).** Items 1–4 and 6 are done; item 5 has 10 of 11 checks (the last, `names.ledger`, comes with item 7). Latest: the move onto Unicron, in review as PR snds/synapse#1 (branch `unicron`, `7d78d2f`; D90). Next: Sean's review of #1, then item 7.
- **Working set**: Repo `~/Projects/synapse`: `crates/` (sy-model, sy-index, sy CLI), `app/` (interface) and `app/src-tauri/` (sy-app), `docs/stage-1/STAGE-1.md`, `docs/plan/`, `brand/`, `catalog/`, `schemas/v1/`, `scripts/`. T1 snapshot: `~/Projects/synapse-sandbox/t1-workspace@4e2b6cf/` (read-only, local only). Readable copy (plan set v2.12): https://claude.ai/artifact/VoPXvWfgPkc8ArsmtmESHt.
- **Last action**: Stage 1 item 6, the tool runner (repo `4ca464a`):
  - `sy-check/tools`: reads `tool.json` manifests, fills `{params}`, enforces safety (writing runs need `--allow-write`; only the person's own workspaces, D80), runs with timeouts, collects exit code, text or JSON.
  - `sy tool list|run`, and `sy check --tools` (each checking tool's read-only, offline `check` run). New checks: `tools.manifest` (grouped before migration) and `tools.manifest-honesty`.
  - Ten manifests written beside their scripts in this vault's `09-tools/` (the spike's five + validate-integrity, validate-links, validate-workspace, check-secrets, build-local-skill-plugin); `.gitignore` now tracks `09-tools/*.tool.json`. Live: seven checking tools run in ~4 s, all pass.
  - Item 5 before it: 10 of 11 checks with parity (standards-lint on T1; both link/integrity validators, 39/39 planted). D88 approved; D89 replaces D87.
  - By Claude Opus 5.5 · Claude Code · Work MBP.
- **Next action**: **Sean reviews PR snds/synapse#1** (the Unicron move, D90 proposed); merge only on his word. What it does: `@unicron/ui` + `@unicron/tokens` 0.1.0 from release tarballs (exact pins, npm override; support window = current and previous minor); `app/src/app-extension.css` status roles from Unicron hue angles (measured 5.61:1+ light, 8.00:1+ dark); local shadcn copies, Emphasis Engine theme (D82, superseded) and IBM Plex removed; Badge/Kbd/Empty/ToggleGroup in place of hand-built pieces; `@snds/dsa` ratchet in CI (baseline 23 class overrides, 0 look-alikes; `dsa patterns`: 0 candidates of 48 compositions).
  - **Owed to the Lockdown/Unicron session** (`session_01DG9oy7EGG6unMww4vC7sSH`): the PR number (snds/synapse#1) and the first `dsa patterns` summary (0 candidates). This session had no tool to message it; Sean or a session with the remote-messaging tool should pass it on.
  - **Upstream asks to file once Sean agrees:** (1) Unicron core contrast: muted text 4.39/4.06:1 on sidebar/accent (light), focus ring at 50% 1.54:1 light / 1.88:1 dark, pressed toggle ~1.1:1 (corrected locally in the meantime); (2) a title-bar-aware dialog for desktop apps; (3) docs/05's `next-themes` example trips React 19's script warning; (4) `@snds/dsa` release tarballs so npm consumers don't need pnpm.
  - Then Stage 1 item 7 (facts engine, with `names.ledger`, E7). Take Sean's UI feedback when he's ready. Still waiting on: Apple support (membership), the Windows PC (tell Sean before starting), YubiKey firmware version.
- **Naming rule (standing)**: Use "Synapse" for the app. Its one home is `brand/brand.json` in the repo (fact `n-v1jhd2e8.name`). Every other appearance is listed in `brand/name-ledger.json`. After adding the name anywhere (repo or vault), run `python3 scripts/name-ledger.py --vault ~/Projects/workspace` from the repo, then `--write` once reviewed. Identifiers never carry the name (D37): use the `sy` prefix.
- **Open decisions**: Apple Developer Program (blocked; Sean emailed Apple support); the public name (trademark check not done); generator engine; plugin runtime; `python-cross-platform-gui` (spoke or project skill).
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
- **2026-10-15** — Sean approved D86. On the component registry he chose no shared registry: each project starts from shadcn and grows its own design system and components (D87, replacing D83; repo `c771964`).
- **2026-10-15** — App shell on the real index (`90f0b91`): Tauri crate `sy-app`, the `overview` command, router and query, live Home and Health, Synapse's own title bar, brand-named bundle. CI green on all three platforms.
- **2026-10-15** — Sean: "Looking great"; UI thoughts to come later, keep to the plan. Stage 1 item 4 done (`79b149d`): the router matches the oracle 5,488/5,488, 0.79 ms at most.
- **2026-10-15** — Stage 1 item 5: `sy-check` with 10 of 11 Rust checks and the ported link/integrity rules; parity with standards-lint (T1) and both validators (39/39 planted); Health runs the checks (`e1881d2`…`aa29f1d`). D88 proposed.
- **2026-10-15** — Merged a note from the 29-unicron cloud session saying D87 was reversed (Lockdown D14). Sean confirmed: D89 replaces D87, Synapse moves onto Unicron when it's ready. Sean approved D88 (`7f18260`).
- **2026-10-15** — Stage 1 item 6 done (`4ca464a`): the tool runner, `sy tool list|run`, `sy check --tools`; ten tool manifests added to this vault's `09-tools/`. The Lockdown/Unicron session asked for the Unicron move (D89) as the next Synapse item; recorded above.
- **2026-10-15** — Unicron move done on branch `unicron`, PR snds/synapse#1 (D90 proposed): Unicron 0.1.0 packages, the app's extension layer (measured contrast), primitives in place of hand-built pieces, dsa ratchet in CI. Awaiting Sean's review.
