# SESSION-STATE — Synapse

_Last updated: 2026-10-15 — Unicron move up for review: snds/synapse#1 (D90); then Stage 1 item 7_

---

## Current state (rewritten atomically — no stale fields)

### 🤝 Live handoff (the baton)

- **TL;DR (for future agent)**: Synapse (codename; was Switchyard) is a planned desktop workspace app with a tray service, for Mac and Windows. It makes an AI workspace visible and manageable over plain files, runs checks without an agent, creates and imports workspaces with scorecards, and walls personas. The credential router is its Personas & access module (`plan/access/`). Stage 1 (the engine) is built and scored; the desktop app already reads the real index.
- **Current focus**: **Stage 2 (app and tray):** `docs/stage-2/STAGE-2.md`, 17 items, exit tests S1–S14. Sean decided D91–D97 (2026-10-16). Sean's rule: build everything except the signing-dependent parts; those are tied in once he has an Apple team and a Windows signing route. Built: items 1–14 and 17 except the signed parts (the service, the local API on Mac, Linux and Windows, conformance, every screen, the lock's engine, Unicron 0.2, the Stage 2 scorecard). UI review round 1 is built (F1–F11). Left: Sean's look at round 1 and any round 2, and items 15–16 (Windows PC time, signing, release).
- **Working set**: Repo `~/Projects/synapse`: `crates/` (sy-model, sy-index, sy-route, sy-check, sy-write, sy CLI, sy-service, sy-os, sy-surface), `app/` and `app/src-tauri/` (sy-app), `docs/stage-2/STAGE-2.md` (progress notes per item), `docs/stage-2/security-review.md`, `scripts/` (e1-parity, scorecard, t3-check, surface-parity, name-ledger). Snapshots (read-only, local only): `~/Projects/synapse-sandbox/t1b-workspace@0f46578/` and `t1-workspace@4e2b6cf/`. Scorecards: `~/Projects/synapse-sandbox/scorecards/`. Readable plan copy (v2.12): https://claude.ai/artifact/VoPXvWfgPkc8ArsmtmESHt.
- **Last action**: 2026-10-18, **pane bars at one height (F12)** (repo `309a325`, CI green; snds/unicron#47 → ui 0.13.0): Sean's note that the Library's three bars differed. Every pane bar is one 48 px `PaneBar`, with a test; line tabs fill it through Unicron's new `TabsList size="fill"`; the graph's filters are one Filters menu so its toolbar fits one row at 1320 px. Also the **[Synapse Roadmap](https://claude.ai/artifact/Hi7e7nZvP19sL2DwW94JBp)** page (source: [roadmap.html](roadmap.html) beside this baton): every stage with its steps, what waits on Sean, what Claude builds next. Before that the same day: batons for every agent and D100 (repo `685c9dc`), in [history/2026-10.md](history/2026-10.md). By Claude Opus 5.5 · Claude Code · Work MBP.
- **Next action**: **Sean looks at round 1** (restart the dev server on 1430 to pick up Unicron 0.12 and three.js; in the browser, the palette's "Use worst-case sample content" shows the sheets at their extremes), then round 2 of feedback; **the hardware follow-up** (planned with Sean on 2026-10-17). Everything left in Stage 2, step by step with pass lines, is [stage-2-checklist.md](stage-2-checklist.md) beside this baton (the one copy; the repo's READMEs link it); its section 8 is what an agent can build without Sean (Health's tool buttons, a skill page, the app in Windows CI, an unsigned Mac bundle, the updater's wiring). Every screen is built: `npm run dev` in `app` shows them on sample data. Then S10's keyboard walk-through and S2's replay with Obsidian running. Waiting on Sean: an Apple team (try a free development team in Xcode first) for the Mac unlock, notifications and signing; a Windows signing route and Windows PC time (D72's Hello spike, item 15); Apple support (membership); YubiKey firmware version.
- **Naming rule (standing)**: Use "Synapse" for the app. Its one home is `brand/brand.json` in the repo (fact `n-v1jhd2e8.name`). Every other appearance is listed in `brand/name-ledger.json`. After adding the name anywhere (repo or vault), run `python3 scripts/name-ledger.py --vault ~/Projects/workspace` from the repo, then `--write` once reviewed. Identifiers never carry the name (D37): use the `sy` prefix.
- **Open decisions**: **Batons:** D98 and D100 are built. Five batons still need their own sessions to trim a Live handoff that a rule can't judge: 18-bootstrap-generator 40 KB, 28-lockdown 21 KB, 25-fontface 18 KB, 19-workspace-brain 15 KB, 24-mailbird 12.4 KB (the session card names them). Two employer batons on this machine have no Live handoff (`validate-batons.py` warns). The SessionStart hook's own fallback card (`.claude/hooks/dispatcher.py`) still parses only `## Session history`; hooks are write-protected from agents, so that one is Sean's. **Resume to the cloud** (`claude --cloud`) is built but untried, because a test starts a real cloud session: Sean to try it once. **Jira tickets** are listed as links only; reading them waits for Stage 4's credentials. Apple Developer Program (blocked; Sean emailed Apple support); the public name (trademark check not done); generator engine; plugin runtime; `python-cross-platform-gui` (spoke or project skill).
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

_Older entries are in [history/README.md](history/README.md), the long-term tier, by month; the app's Projects timeline joins them with this file._

- **2026-10-16** — Stage 2 items 5–14 built except the signing-dependent parts: conformance, every screen (Home, Projects, Health, Domains & skills, Library, graph, impact review, Agent apps, Settings), and the lock's engine. S3 and S5 pass. Sigma 3 chosen over the new Sigma 4. By Claude Opus 5.5 · Claude Code · Work MBP.

- **2026-10-15** — Sean approved D51 and D69–D74. Stage 0 item 10: name ledger as the first fact (`brand/`, `scripts/name-ledger.py`).
- **2026-10-15** — Sean chose to host the identity subdomain on his existing Cloudflare zone instead of snds.design (D75). Hosting rules proposed (D76). The host name is kept in the private repo, not here.
- **2026-10-16** — Sean ran `sy check` and `sy route` on the live workspace (expected output) and approved reinstalling `skills-ref`. E1 now covers it: T1b 510/510, T1 529/529; scorecard 8/8 (repo `3572111`).
- **2026-10-16** — Sean said go on Stage 2. Plan written; Sean chose a separate service process (D91), `sy-os` (D92), the key-guarding unlock (D93) and signing later (D94). Items 1 and 2 done (repo `ba924c6`). Found: the Mac unlock needs an Apple team.
