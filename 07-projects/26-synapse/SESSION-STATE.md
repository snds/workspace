# SESSION-STATE — Synapse

_Last updated: 2026-10-15 — Unicron move up for review: snds/synapse#1 (D90); then Stage 1 item 7_

---

## Current state (rewritten atomically — no stale fields)

### 🤝 Live handoff (the baton)

- **TL;DR (for future agent)**: Synapse (codename; was Switchyard) is a planned desktop workspace app with a tray service, for Mac and Windows. It makes an AI workspace visible and manageable over plain files, runs checks without an agent, creates and imports workspaces with scorecards, and walls personas. The credential router is its Personas & access module (`plan/access/`). Stage 1 (the engine) is built and scored; the desktop app already reads the real index.
- **Current focus**: **Stage 2 (app and tray):** `docs/stage-2/STAGE-2.md`, 17 items, exit tests S1–S14. Sean decided D91–D97 (2026-10-16). Sean's rule: build everything except the signing-dependent parts; those are tied in once he has an Apple team and a Windows signing route. Built: items 1–14 and 17 except the signed parts (the service, the local API on Mac, Linux and Windows, conformance, every screen, the lock's engine, Unicron 0.2, the Stage 2 scorecard). Left: Sean's UI feedback (item 1), and items 15–16 (Windows PC time, signing, release).
- **Working set**: Repo `~/Projects/synapse`: `crates/` (sy-model, sy-index, sy-route, sy-check, sy-write, sy CLI, sy-service, sy-os, sy-surface), `app/` and `app/src-tauri/` (sy-app), `docs/stage-2/STAGE-2.md` (progress notes per item), `docs/stage-2/security-review.md`, `scripts/` (e1-parity, scorecard, t3-check, surface-parity, name-ledger). Snapshots (read-only, local only): `~/Projects/synapse-sandbox/t1b-workspace@0f46578/` and `t1-workspace@4e2b6cf/`. Scorecards: `~/Projects/synapse-sandbox/scorecards/`. Readable plan copy (v2.12): https://claude.ai/artifact/VoPXvWfgPkc8ArsmtmESHt.
- **Last action**: 2026-10-16, Stage 2 (repo up to `8c93dc7`; details in `docs/stage-2/STAGE-2.md`):
  - **5, conformance:** fixes drafted when files change, saved for review; never fights another writer (a file undone twice in a minute is set aside).
  - **6–8, 13, 12:** Home, Projects, Health (waiting fixes, trend), Domains & skills with the load simulator (token cost matches the harness), Agent apps, Settings (region and formats, start at login, security).
  - **9, Library:** file tree, CodeMirror 6 editor with live preview, saving through the writer with a three-way merge, frontmatter as a form, outline, links, checks. S3: 23,237 live text files and 14 edge cases round-trip, 0 changed.
  - **10, graph:** Sigma 3 (Sigma 4's new style system can come later), regions by domain, clusters by area, spokes around hubs, filters, edge kinds by color and pattern, a list version. Live: 1,914 nodes, 5,050 edges, laid out in 13 ms.
  - **11, impact review:** a sheet from the Library; history mentions (sessions, archives, `## History`, pinned) listed and left alone (model §7.3). S5: 0 drift after applying.
  - **14, lock:** sealed proposals, the lock and its API, gated while locked; Touch ID and Hello wait for signing.
  - CI's Linux job ran out of disk building sy-app: fixed (line tables only, unused toolchains removed).
  - **17, scorecard:** `scripts/scorecard.py --stage 2`. On T1b: 9 of 13 pass (S3 0 bytes changed over 1,980 files; S4 121 ms; S9 82 MB, 0% CPU); 4 wait (Obsidian on Sean's Mac, an accessibility checker, the Windows PC, packaging). Saved in the sandbox's scorecards folder.
  - **1, Unicron 0.2:** `@unicron/ui` 0.2.0; icon-only buttons are `IconButton`s with tooltips; class overrides 18 → 4 (repo `8c93dc7`).
- **Earlier**: Stage 1 items 7–11, after the Unicron move merged (snds/synapse#1, D90 approved):
  - **7, facts engine:** markers, fact homes (JSON, frontmatter, baton bullets), slots, views, impact review; the name ledger runs in the engine (E7 identical).
  - **8, writer (`sy-write`):** strict UTF-8, BOM and line endings kept, D79 frontmatter edits, compare-and-swap, quiet period, atomic writes, undo. E6: 0 files changed outside an edit on T1.
  - **9, the `sy` CLI:** `sy route` matches `skill-loadset.py` byte for byte; `sy check --fix` (slots, views, retyped frontmatter values); `sy facts impact <fact> <new value>`; saved proposals with `sy propose`, `apply`, `undo`, `proposals`; `--json` everywhere.
  - **10, corpus and scorecards:** T1b pinned (workspace `0f46578`, after the fix-backs) with its routing oracle rebuilt; `scripts/e1-parity.py` (T1b 49/49, T1 68/68); `scripts/scorecard.py` (E1–E8); a seeded synthetic workspace with an answer key runs in CI (19/19 found, 0 extra).
  - **11, security review:** path escapes refused; files over 16 MB indexed by path only (a 200 MB file went from 4 s and a 97 MB index to 0.12 s and 64 KB); the index made readable by the user only.
  - Upstream asks filed: snds/unicron#6 (contrast), #7 (title-bar-aware dialog), #8 (`next-themes` example), snds/dsa#1 (release tarballs). The note for the Lockdown/Unicron session was handed to Sean.
  - 2026-10-16, Stage 2 (repo `e6272a8`…`ba924c6`): the plan; Stage 1 carry-overs (a timed-out tool stops with its whole process tree, minimal environment for scheduled runs, the index excluded from Time Machine); the Stage 2 security review (ten threats, three closed); targeted index updates now follow the walk's rules and never follow symlinks; `sy-service` (watcher, live index, scheduler with the X2 pause; a save is indexed in 124 ms).
  - 2026-10-16: `skills-ref` 0.1.0 reinstalled with Sean's OK (`~/Projects/synapse-sandbox/skills-ref-venv/`); E1 compares it in three stages (as found, D51 layout, planted): T1b 510/510, T1 529/529 (repo `c5ce087`, scorecard `3572111`).
  - By Claude Opus 5.5 · Claude Code · Work MBP.
- **Next action**: **Sean's UI feedback** (every screen is built: `npm run dev` in `app` shows them on sample data; the app itself on the live workspace). Then S10's automated accessibility checks (an accessibility checker in the app's tests needs Sean's OK to download), and S2's replay with Obsidian running. Waiting on Sean: an Apple team (try a free development team in Xcode first) for the Mac unlock, notifications and signing; a Windows signing route and Windows PC time (D72's Hello spike, item 15). Still waiting on: Apple support (membership), YubiKey firmware version.
- **Naming rule (standing)**: Use "Synapse" for the app. Its one home is `brand/brand.json` in the repo (fact `n-v1jhd2e8.name`). Every other appearance is listed in `brand/name-ledger.json`. After adding the name anywhere (repo or vault), run `python3 scripts/name-ledger.py --vault ~/Projects/workspace` from the repo, then `--write` once reviewed. Identifiers never carry the name (D37): use the `sy` prefix.
- **Open decisions**: Apple Developer Program (blocked; Sean emailed Apple support); the public name (trademark check not done); generator engine; plugin runtime; `python-cross-platform-gui` (spoke or project skill).
- **Blocked on**: nothing. Sensitive-data cleanup is deferred to after Stage 3 (D63, D65). Recommended now regardless: rotate the API key a memory note names, and review Drive link sharing.
- **In-flight / do-not-touch**: Scan output folder `~/Projects/synapse-sandbox/scan-t1@4e2b6cf-v1/` (local only; it holds employer terms). Probe results `~/Projects/synapse-sandbox/surface-probe-*.json` (local only; installed apps and versions). The T1 and T1b snapshots, their routing oracles and the scorecards folder stay local; the snapshots are read-only.
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

- **2026-10-16** — Stage 2 items 5–14 built except the signing-dependent parts: conformance, every screen (Home, Projects, Health, Domains & skills, Library, graph, impact review, Agent apps, Settings), and the lock's engine. S3 and S5 pass. Sigma 3 chosen over the new Sigma 4. By Claude Opus 5.5 · Claude Code · Work MBP.

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
- **2026-10-15** — Sean approved D88 and chose the shared Unicron design system. The Unicron move merged (snds/synapse#1); D90 approved. Upstream asks filed (snds/unicron#6–#8, snds/dsa#1).
- **2026-10-15** — Stage 1 items 7 (facts engine, E7), 8 (writer, E6) and 9 (the `sy` CLI: fixes, fact updates, saved proposals) done (repo `bb68a26`…`57da651`). CI green on all three platforms.
- **2026-10-15** — Stage 1 items 10 (T1b snapshot, E1 harness, scorecard, seeded corpus in CI) and 11 (security review, two fixes) done (repo `1d3230f`…`55e203b`). Scorecard on T1b: 8 of 8 exit tests pass.
- **2026-10-16** — Sean ran `sy check` and `sy route` on the live workspace (expected output) and approved reinstalling `skills-ref`. E1 now covers it: T1b 510/510, T1 529/529; scorecard 8/8 (repo `3572111`).
- **2026-10-16** — Sean said go on Stage 2. Plan written; Sean chose a separate service process (D91), `sy-os` (D92), the key-guarding unlock (D93) and signing later (D94). Items 1 and 2 done (repo `ba924c6`). Found: the Mac unlock needs an Apple team.
