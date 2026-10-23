# SESSION-STATE — Synapse

_Last updated: 2026-10-23 — review context built into hub depth; D135 approved; D136 proposed_

---

## Current state (rewritten atomically — no stale fields)

### 🤝 Live handoff (the baton)

- **TL;DR (for future agent)**: Synapse (codename; was Switchyard) is a planned desktop workspace app with a tray service, for Mac and Windows. It makes an AI workspace visible and manageable over plain files, runs checks without an agent, creates and imports workspaces with scorecards, and walls personas. The credential router is its Personas & access module (`plan/access/`). Stage 1 (the engine) is built and scored; the desktop app already reads the real index.
- **Current focus**: **Stage 3 (import, create, measure)**, on Sean's go ("Continue with stage 3", 2026-10-18): `docs/stage-3/STAGE-3.md`, 16 items, exit tests C1–C12, threats U1–U9, decisions D101–D105 proceeding on their recommendations. Built: items 1–14 and 16. Two parts are left: item 9's library of finished skills to pull and adapt (needs Sean's input) and item 10's interview (waits for Stage 5's agent bridge). Item 15 waits for the Windows PC. The [Stage 3 scorecard](https://github.com/snds/synapse/blob/main/docs/stage-3/SCORECARD.md) on T1c: 6 of 12 pass; C3 fails on the source's own 52 over-long skill descriptions, which a copy keeps; C12 on the two open `wsx` promises; C8–C11 wait for agent runs on Sean's go or the live test signal. Stage 2's remaining steps run alongside: [stage-2-checklist.md](stage-2-checklist.md).
- **Working set**: Repo `~/Projects/synapse`: `crates/` (sy-model, sy-index, sy-route, sy-check, sy-write, sy CLI, sy-service, sy-os, sy-surface, sy-plan), `app/` and `app/src-tauri/` (sy-app), `docs/stage-2/STAGE-2.md` and `docs/stage-3/STAGE-3.md` (progress notes per item), each stage's `security-review.md`, `scripts/` (e1-parity, scorecard, t3-check, t2-check, t3-on-t2, template-check, surface-parity, name-ledger), `templates/create/` (Create's generic templates and pattern skills), `corpus/t2/` (ten `wsx`-made workspaces). Stage 3's pages: `docs/stage-3/SCORECARD.md`, `wsx-parity.md`, `scan-protocol-v2.md`. Snapshots (read-only, local only): `~/Projects/synapse-sandbox/t1c-workspace@2ff55d4/` (Stage 3's), `t1b-workspace@0f46578/` and `t1-workspace@4e2b6cf/`. Scorecards: `~/Projects/synapse-sandbox/scorecards/`. Readable plan copy (v2.12): https://claude.ai/artifact/VoPXvWfgPkc8ArsmtmESHt.
- **Last action**: 2026-10-23, Sean approved **D135** (hub depth is a report, never a gate or an automatic move) and asked that changes for review bring the lateral context they need, with the system judging when they need none. Built the first part in `sy routing hubs` ([plan 12](https://github.com/snds/synapse/blob/main/docs/plan/12-review-context.md), D136 proposed): each movable section carries a context (shared passages or subject, how many skills load the hub, files pointing at the section, governing decision notes) or a one-line "no context needed" with the reason. The rule is in the workspace's preferences (`04-preferences/user-preferences.md` → Changes for review), so every agent follows it. Sean then kept `figma`'s execution protocol and `lead-accessibility-architect`'s principles as they are. Earlier the same day: `sy routing hubs` itself and D133, both in snds/synapse#6 and snds/workspace#30. By Claude Opus 5.5 · Claude Code · cloud (remote session).
- **Next action**: **Sean:** review snds/synapse#6 and snds/workspace#30; confirm or change D136 (review context for every proposal: routing impact, dependents and recent edits next); whether short quoted asks become triggers; read [[intent-in-agentic-systems]]; say go to source the compiler's remaining design fills with `sy harness research`; give the first real research ask. Still open: snds/unicron#57 and its Version Packages PR; Stage H past H0 (`#ask-stage-h-go`) and D118–D123; D130–D132 and D134; the Touch ID route; Stage 4 (`#ask-stage-4-go`); agent runs (`#ask-deep-scan`); daily use (S1). **Claude:** drive #6 and #30 to green; review context on every `sy-write` proposal once D136 is confirmed; registry pulls when a session has network; roles from Create's profile once its skills carry a domain.
- **Naming rule (standing)**: Use "Synapse" for the app. Its one home is `brand/brand.json` in the repo (fact `n-v1jhd2e8.name`). Every other appearance is listed in `brand/name-ledger.json`. After adding the name anywhere (repo or vault), run `python3 scripts/name-ledger.py --vault ~/Projects/workspace` from the repo, then `--write` once reviewed. Identifiers never carry the name (D37): use the `sy` prefix.
- **Open decisions**: **Harnesses ([Stage H](https://github.com/snds/synapse/blob/main/docs/stage-h/STAGE-H.md), for Sean's go past H0):** Sean 2026-10-22 approved harnesses for all work (D115), reviewed agent proposals with §4.1 evidence (D116) and judges growing into counting, option D (D117). Proposed: role selectors (D118), one verdict vocabulary (D119), the CLI as the gate (D120), explore and ship modes (D121), a lettered Stage H (D122), where harnesses live (D123). Research supply on T1c now has a compiled fill (plan 10, for Sean's call). **Compiler (plan 10):** D124–D129 **approved by Sean 2026-10-22**. Research: [[domain-harness-architecture]]. **Stage 3:** fix-backs found for `wsx` (its conventions template's example links read as dangling; its registry's clock time); confirm or change D101–D105 (work proceeds on them); **D108, externals in the app** (proposed 2026-10-19, at Sean's ask through the REA session; **approved by Sean 2026-10-19**, and the workspace side, snds/workspace#24, is merged; built in Stage 4): the app drives the workspace's `externals.py --json` (vault PR snds/workspace#24) on the Integrations screen (Stage 4), each change reviewed first; six contract requests sent to that session (bind the apply to the reviewed pin, structured plan entries with the tracked change, a spec version, a write lock, self-test as JSON, a tool manifest); **project 18's archive** once every `wsx` promise is met (C12; Sean's word); a source that isn't a git repository has its git-ignored files snapshotted and scanned too (U5's open item); a **second roadmap page** was published by mistake (https://claude.ai/artifact/WtUJxDS3VVRYff15S53K5c): delete it on Sean's OK; **foundations across chains**: decided and built as D133 (2026-10-23). **Where updates are published** (new, 2026-10-18): the repo is private, so its releases can't serve the updater; a public releases repo, or a Cloudflare bucket or Pages site. **Batons:** D98 and D100 are built. Five batons still need their own sessions to trim a Live handoff that a rule can't judge: 18-bootstrap-generator 40 KB, 28-lockdown 21 KB, 25-fontface 18 KB, 19-workspace-brain 15 KB, 24-mailbird 12.4 KB (the session card names them). Two employer batons on this machine have no Live handoff (`validate-batons.py` warns). The SessionStart hook's own fallback card (`.claude/hooks/dispatcher.py`) still parses only `## Session history`; hooks are write-protected from agents, so that one is Sean's. **Resume to the cloud** (`claude --cloud`) is built but untried, because a test starts a real cloud session: Sean to try it once. **Jira tickets** are listed as links only; reading them waits for Stage 4's credentials. Apple Developer Program (blocked; Sean emailed Apple support); the public name (trademark check not done); generator engine; plugin runtime; `python-cross-platform-gui` (spoke or project skill).
- **Blocked on**: nothing. Sensitive-data cleanup is deferred to after Stage 3 (D63, D65). Recommended now regardless: rotate the API key a memory note names, and review Drive link sharing.
- **In-flight / do-not-touch**: Scan output folder `~/Projects/synapse-sandbox/scan-t1@4e2b6cf-v1/` (local only; it holds employer terms). Probe results `~/Projects/synapse-sandbox/surface-probe-*.json` (local only; installed apps and versions). The T1, T1b and T1c snapshots, their routing oracles, T1c's baseline and pre-pass, the scorecards folder and any scan folder stay local; the snapshots are read-only.
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

- **2026-10-23** — Hub depth made mechanical (`sy routing hubs`): the entry as it stood is in [history/2026-10.md](history/2026-10.md#2026-10-23-hub-depth-mechanical).

- **2026-10-23** — D133 built: the entry as it stood is in [history/2026-10.md](history/2026-10.md#2026-10-23-d133-built).

- **2026-10-23** — The routing suite and routing rules in every domain: the entry as it stood is in [history/2026-10.md](history/2026-10.md#2026-10-23-the-routing-suite-routing-rules-in-every-domain).

- **2026-10-22** — Design skills rearchitected (`ds` the one design-system hub, `dsci-`, UX duplicates folded): the entry as it stood is in [history/2026-10.md](history/2026-10.md#2026-10-22-design-skills-rearchitected).

- **2026-10-22** — The research network built; the design-skill question raised: the entry as it stood is in [history/2026-10.md](history/2026-10.md#2026-10-22-the-research-network-and-the-design-skill-question).

- **2026-10-22** — Compiler merged; item 21 built (snds/synapse#3): the entry as it stood is in [history/2026-10.md](history/2026-10.md#2026-10-22-item-21-accepting-supply-plans).

- **2026-10-22** — The harness compiler planned and built (items 18–20, snds/synapse#2): the entry as it stood is in [history/2026-10.md](history/2026-10.md#2026-10-22-the-harness-compiler-items-1820).

- **2026-10-22** — Stage H planned and H0 built: the entry as it stood is in [history/2026-10.md](history/2026-10.md#2026-10-22-stage-h-planned-and-h0-built).

- **2026-10-19 to 2026-10-20** — S10, the Mac app signed, item 14 built, S13 and S2 pass, icons fixed in WebKit: the Live handoff as it stood is in [history/2026-10.md](history/2026-10.md#2026-10-19-to-2026-10-20-s10-signing-item-14-s13-s2-icons).

- **2026-10-16** — Stage 2 items 5–14 built except the signing-dependent parts: conformance, every screen (Home, Projects, Health, Domains & skills, Library, graph, impact review, Agent apps, Settings), and the lock's engine. S3 and S5 pass. Sigma 3 chosen over the new Sigma 4. By Claude Opus 5.5 · Claude Code · Work MBP.

- **2026-10-15** — Sean approved D51 and D69–D74. Stage 0 item 10: name ledger as the first fact (`brand/`, `scripts/name-ledger.py`).
- **2026-10-15** — Sean chose to host the identity subdomain on his existing Cloudflare zone instead of snds.design (D75). Hosting rules proposed (D76). The host name is kept in the private repo, not here.
- **2026-10-16** — Sean ran `sy check` and `sy route` on the live workspace (expected output) and approved reinstalling `skills-ref`. E1 now covers it: T1b 510/510, T1 529/529; scorecard 8/8 (repo `3572111`).
- **2026-10-16** — Sean said go on Stage 2. Plan written; Sean chose a separate service process (D91), `sy-os` (D92), the key-guarding unlock (D93) and signing later (D94). Items 1 and 2 done (repo `ba924c6`). Found: the Mac unlock needs an Apple team.
