# Project Context — Sean Sands
_Authoritative source: this file (06-context/project-context.md)_
_Written by any agent — the git checkout is the source of truth._
_Last updated: 2026-07-23_

> **Platform note (2026-06-16):** the workspace itself was refactored to be portable, git-native, and
> LLM/surface/device-agnostic, then consolidated onto `main` at `github.com/snds/workspace` (16-PR stack,
> all five validators green). The git checkout — not Google Drive — is now the source
> of truth. Day-to-day contribution rules live in [01-frameworks/08-workspace-contribution-framework.md](01-frameworks/08-workspace-contribution-framework.md) + [AGENTS.md](../AGENTS.md). See memory `decision-portable-workspace-refactor`. The project pending items below are unchanged.

---

## Pending Items

_Triaged 2026-04-27 into three buckets: **Active** (next actions), **Deferred** (resurface on context match), **Recently resolved** (prune at next /optimize)._

### Active (next actions)

- [ ] **Machine-layer installs on remaining machines (FX-1/FX-14 carry-over).** Run `00-bootstrap/doctor/workspace-doctor.sh` + retire Drive-era `~/.claude/hooks/*.sh` + registrations on: Work MBP (main, `CS-K746DRWXY1`), Work MBP (loaner, if kept), and the Windows Desktop (`Enterprise` — needs a Windows install route first: shims are bash/launchd; document the brain location in memory `fact-machine-layer-installs` at install time). Then run ONE verified post-migration Windows session end-to-end (none exists on record). **Work MBP session also includes:** Cursor User Rules + Perplexity Space beacon pastes + `--ack-chat` there (Sean's split, 2026-07-09). Added 2026-07-09 (fix session).
- [ ] **Extract a tool-neutral trigger-routes reference (FX-8 deferred half).** Consider `02-shared-references/trigger-routes.md` consumed by both the dispatcher and AGENTS.md so non-Claude agents get the curated routes without reading Python. Deferred from the fix session: the single-source rule had just consolidated authority in the dispatcher; don't churn it twice in one day. Added 2026-07-09 (fix session).
- [ ] **Employer design-system migration (cpes-software).** (Added 2026-07-15; **unblocked 2026-07-20**.) Audit complete: a Figma-Make prototype mapped INTO the design system as a reuse-and-extend migration (most widgets land on components engineering already ships; little is genuinely net-new). Directionality (Sean): prototype = spec; all build work lands in the design system — reuse → extend → author net-new only if novel. Deliverables (migration plan + interactive gap map) and the review PR are tracked in the **employer repo** — not mirrored here (separation rule). ~~Held pending backend access provisioning~~ — **backend access landed 2026-07-20**; centric-ui now runs locally against the cloud dev backend (`PORT=3000 npm run dev -- --port 3000` from the `centric-ui-main` worktree; setup traps recorded in [[centric-ui-local-against-cloud-dev]]). **Gap report re-run 2026-07-21** against current `main` on both repos (Olga had moved the prototype onto real shadcn/Radix, invalidating the first audit's premise): plan + interactive gap map refreshed and a new per-unit detail appendix added, PR #1 updated in place, replied to her CHANGES_REQUESTED review. Verification finding worth remembering: report the stable mapped verdict, not the volatile confirmed/adjusted count ([[adversarial-verify-label-volatility]]). Next: on Olga's re-review sign-off, resume the build (quick-win reuses first).
- [ ] **centric-ui PR #179 — assign reviewers + settle the redirect-URI question.** (Added 2026-07-20.) Makes local-FE-against-cloud-dev work: routes record/schema-registry/workflow through `cloudOrLocalServiceProxy` (completing the pattern Alex Myronov introduced in #160 — natural reviewer), and corrects the API-key placement across `.env.example` / `.env.cloud.example` / `docs/local-setup.md`. **Item 3 needs a decision, not a review:** the VMS realm's `react` client accepts only `localhost:3000` while `vite.config.ts` defaults to 8082 and the example file said 5173 — either the realm allows 8082 or the examples say 3000. Deliberately not guessed; needs whoever owns the realm.
- [ ] **BE ask: `workflow-service` has no cloud dev hostname.** (Added 2026-07-20.) `workflow-service.internal.app.dev.centricsoftware.io` does not resolve (DNS/HTTP 000, vs 401 for services that exist). Workflow features can't work against cloud dev until BE exposes it or supplies the real host. Not a local config problem.
- [ ] **Purge two abandoned centric-ui SHAs carrying the personal email.** (Added 2026-07-20.) `ec04737` and `86651f0` were force-push-replaced within ~10 min, but GitHub keeps unreferenced commits reachable by direct URL until GC. Not in any branch, PR, or search result; the value is the public commit email, not a secret. Closing it out properly needs a GitHub Support request. Rule that prevents recurrence: [[feedback-credential-scoping]].
- [ ] **SSH to github.com:22 timing out on the Centric laptop.** (Added 2026-07-20.) Persisted all session; every push went over HTTPS instead. Likely corporate egress filtering. Fix if it recurs: point `Host github.com` and `Host github-work` at `ssh.github.com` port 443 in `~/.ssh/config`.
- [ ] **"Context is King" — workspace foundation refinements.** (Added 2026-07-09, Sean's directive.) Bring declared-context resolution to the foundation of *every working session*, not just the audience/evidence delivery layer. Candidate scope: session-start ritual surfaces the active context profile alongside machine/git; dispatcher hook resolves profile mechanically (repo remote, project declaration) and injects it; `SESSION-STATE.md` context fields populated across all 8 active projects; memory/knowledge entries carry context tags; skills receive the profile on load. Independent of — but informed by — the Audience & Evidence system shipped 2026-07-09: generalize from `02-shared-references/delivery-playbooks/00-context-profiles.md` (the profile model, resolution order, citing rule, fail-safe default).
- [ ] **C8/CDS semantic status-token gap (from the 2026-07-08 cell-validation session).** C8 has no warning stroke/tint tokens; orange accent border used as the documented interim (Jabili directive). Flesh out status/context colors in the semantic token set — warning/error/info/success each need border + low-chroma tint-surface + on-tint text tokens. Verify the failing session didn't already file this; raise as a CDS ask if not. Added 2026-07-08.
- [ ] **Act on the 2026-07-08 workspace audit carry-forwards** (see audit-log entry): (a) ~~APCA body-text floor~~ RESOLVED 2026-07-08 per Sean — the three values are a deliberate TIER, not a contradiction: `a11y-visual` = accessibility floor (bare minimum) · design-engineer table = working target ("happy middle") · [[radix-derived-color-system]] = Radix-scale-specific, scoped to Radix-derived palettes only; cross-linked tier notes added in all three files; (b) decide whether the remaining a11y/color skills get frontmatter `triggers:` (`ux-accessibility`, `fe-accessibility`, `visual-qa-accessibility`, `lead-accessibility-architect`, `gd-color-theory`, `infod-encoding-theory`) — deliberately deferred to avoid over-firing; (c) CVD prevalence numbers drift across 4 skills — align on one source; (d) `06-context/artifact-registry.md` hardcodes line-number tables for gitignored artifacts (unvalidatable mirror — regenerate or drop); (e) generalize the doctor's fossil check into a tracked `* 2.md` conflict-copy sweep — ~~one instance (`_archive/figma-plugin-patterns 2.md`, stale subset) removed 2026-07-23~~; the *doctor-sweep generalization* is still open; (f) ~~`08-knowledge/research/research/` double-nesting~~ RESOLVED 2026-07-23 — flattened to `research/`, `_INDEX.md` updated (Obsidian `[[wikilinks]]` unaffected — basename-resolved). Added 2026-07-08.
- [ ] **Paste the workspace beacon: Cursor User Rules + Perplexity Space (Work MBP).** Rides the Work MBP doctor-install session — those tools live/are used there; its doctor nags until `--ack-chat` on that machine. (claude.ai preferences + "Workspace" project: DONE on Personal MBP 2026-07-09, acked — doctor verified clean.) Added 2026-07-06; split 2026-07-09.
- [ ] **Load the evolved `ux-component-library` v2.1 on this + other machines.** The **Component & Pattern Framework (#09)** shipped 2026-06-18 — a 5-layer DS context system (framework hub + skill + `ux-components` MCP + `DESIGN.md` + `AGENTS.md`). New/changed: `01-frameworks/09-component-and-pattern-framework.md`, evolved skill + 3 references, `02-shared-references/ds-agents-binding.md`, and the A2UI canonical catalog (`02-shared-references/a2ui/`). The plugin cache still holds v0.2.0 — **restart Claude Code** or rerun `09-tools/build-local-skill-plugin.py` + `claude plugin install snds@snds-local`. C8 `DESIGN.md` + `AGENTS.md` written locally in `c8-plm/` (separate repo). Optional follow-ups: validate the A2UI catalog with A2UI's conformance tooling; build a CDS renderer mapping catalog variants → `--sem-*`; A/B-evaluate a C8 screen. See memory `decision-component-pattern-framework-system`.
- [ ] **C8 cell-indicators — Sean sign-offs to unblock propagation.** Pilot built + code-validated on the Figma `cell-indicators` branch (full state: `07-projects/02-centricPLM/context/cell-indicators-pilot.md`). Open decisions: (1) propagate lock+tint read-only (replace the `Cell Value` italic Read-only mode across the 26 cell sets); (2) enum-chip Computed keep/drop (KPI already stripped); (3) worst-case lock-density rule — always-lock vs tint-only vs density-adaptive (boards A/B side-by-side on the Cells page). Then: componentize the utility gutter + `cell/header` `Locked` prop; clean 005 icon board for the dot-vs-icon corner call. Added 2026-07-09.
- [ ] **Review + merge the 4 centric-ui Radix color-system PRs (#64–67).** Based off the dev branch `feat/figma-repo-sync-plugin`. Merge order: **#64 tokens → #65 components → #67 harness** (consume the new tokens); **#66 generator** independent. Working basis = local combined branch `feat/radix-color-system`.
- [ ] **figma-repo-sync-plugin finalization (code-grounded plan, 2026-06-22).** Gold Figma library is DONE (hand-built via figma-cli); plugin must now *generate* to it, *enforce* it, and *converge* code↔Figma. Full plan + status: `07-projects/09-figma-repo-sync-plugin/next-steps-plan.md`. **Base is now `main`** — `feat/radix-color-system` is SUPERSEDED (the team re-landed radix work onto main via merged consolidate PRs #82/#83/#84; main has plugin @ 11.4.18 + radix tokens + tsconfig/eslint plugin-excludes). Foundational fixes done + rebased onto main: PRs **#116** (transparent token), **#117** (shared-plugin-data, stacked on #116), **#118** (Badge size/shape), **#119** (Alert); **#120 closed** (redundant). Company repo, no self-merge. **Next:** quick wins (ScrollArea placed=0; mode-first header comment) → Type→booleans lever + tokenization sweep + lint gate as ONE componentGenerator.ts pass, all on `main`. **Watch:** `caution` is open team PR **#87 → main** (Alert/Badge caution depends on it); cds→semantic usage migration is incomplete on main (~150 reintroduced refs → follow-up codemod). Biggest lever (narrowed) = Type icon-presence → boolean props on Button/Badge (keep State physical).
- [ ] **Publish the centric-ui Figma library** ("Centric SaaS PLM — Design System", `o6o1ZuGHxDow2vHLuYXT6X`). Substantially reworked 2026-06-22: full typography style system (Body/UI categories + `Typography Roles` + 21 variable-bound styles, ~1,117 nodes remapped); comprehensive token binding across all pages + instances (+ `border-width-3`, line-height & paragraph-spacing tokens); mode-first refactors (Badge Size/Shape, Avatar/Badge Status); focus states (Sidebar/Tabs/NavMenu); Form Field boolean toggles + 14 instance rewires; all Additions tweaks; `_Slider/Thumb` subcomponent now consumed by the Slider; `_Avatar/Badge` icon → instance-swap; Avatar—Sizes dup-mode fix. **Manual step** (Plugin API can't publish): Figma → Assets panel → Publish, review the change list. Optional polish: relocate `_Slider/Thumb` into the Slider section; resolve the pre-existing `_Calendar/Day`↔`Calendar` 8px overlap (category relayout). New durable rule in knowledge `figma-ds-surface-authoring` (floating elements absolute → never inflate host bbox; migrated 2026-06-30). See session-log 2026-06-22.
- [ ] **REVOKE the Figma PAT** pasted during the 2026-06-04 session (Figma → Settings → Personal access tokens). It was used read-only for an attempted Variables API call (lacked the Enterprise `file_variables:read` scope) and shared in plaintext.
- [ ] **Install the `snds@snds-local` skill plugin on other machines.** Built 2026-06-02 on Work MBP (main). Exposes 18 curated `03-skills/` hubs as native `/snds:<name>` slash commands. Per machine: run `python3 08-tools/build-local-skill-plugin.py`, then `claude plugin marketplace add ~/.claude/local-plugins/snds-local` + `claude plugin install snds@snds-local`, then restart. (Plugin lives in `~/.claude`, not Drive-synced — only the generator script syncs.)
- [ ] **Refresh `05-artifacts/active/trigger-cheatsheet_v1.0_2026-06-01.html` to v1.1.** Flip `/ds`, `/figma`, `/motion`, `/type`, `/redesign` from "planned" → "live" (all built and observed on disk 2026-06-04 — six-hub set complete). Keep `/redesign`'s external-bridge tag. The full six-hub `/qa /ds /figma /motion /type /redesign` operation-grammar set is now live; cheatsheet is the public-facing reference.
- [ ] **Add `design-system-ops` to the semantic-overlap reconciliation.** Plugin observed active 2026-06-04 with 38 invocable commands (token-audit, drift-detection, component-audit, deprecation-process, governance-encoder, visual-report, etc.). Heavy semantic overlap with `/ds` + `ds-advisor` + `design-engineer` — fold into the description-contract pass (was 8–10 overlap zones; now ~9–11). Likely `/ds` (hub) routes TO design-system-ops commands (granular ops). Decide canonical owner per concern.
- [ ] **Document the now-complete six-hub operation-grammar surface.** Update `06-context/artifact-registry.md` (already done in this session's HEAD content) + decide whether workspace `CLAUDE.md` or the dispatcher needs a pointer. Six hubs: `/qa` JUDGES · `/ds` DECIDES · `design-engineer` / `/figma` AUTHOR · `/motion` IMPLEMENTS · `/redesign` CREATES. Next-step: test-drive against the Davinci Storybook QA audit (`/qa audit apps/docs --theme light --theme dark → /qa triage`) — validates the hubs on real work and closes the founding ask.
- [ ] **Seed `07-projects/04-claude-figma-plugin/SESSION-STATE.md`.** Active project; bring it up to parity with the four seeded on 2026-04-21. Remaining seeds (03-omni, 12-MCS, 15-DavinciRemake) are deferred until those projects are next touched.
- [ ] **Act on Opus 4.7+ skill audit findings.** Report at `05-artifacts/active/skill-network-audit_opus-4.7_2026-04-21.md`. Five prioritized findings; the highest-leverage is extracting ~200 lines of design theory from `ds-advisor` and routing it to the Aesthetic Lens + Last-Mile Craft frameworks, plus resolving `ds-advisor` / `design-engineer` trigger overlap.
- [ ] **Add framework-layer pointers to key skills.** The six highest-leverage skills (`workspace-bootstrap`, `ds-advisor`, `design-engineer`, `figma-canvas-designer`, `variable-icon-font-architect`, `lead-art-director`) should reference the relevant frameworks on demand. Pattern documented in the audit report. Bundle with the audit-findings session.
- [ ] **Data table cell anatomy + state matrix.** Text and numeric cell types first. Part of the PLM data table documentation project (90 tables audited). **Major progress 2026-07-07→09** (drag-to-fill/fill-range system, Align + Validation physical axes, header v2, DataTable keyboard docs, dense 24px study) — live state + node ids: `07-projects/02-centricPLM/context/cell-indicators-pilot.md`; interactive artifact (plan/matrix/playground) linked therein.
- [ ] **C8 cell system — rollout decisions for Sean (added 2026-07-09):** CVD redundancy option (A leading glyph / B dashed warning border / C trailing glyph); entry-error border weight parity (1px vs 2px); Error+Focus severity-over-focus (003 ask); then scripted Validation-axis rollout (~25 sets, +~520 variants; refmap hits 105 — prune?); Cell Value modes verdict; afterwards Invalid-boolean instance migration + Cell Validation collection deprecation. Decision points staged in the artifact's plan view.
- [ ] **C8 cell system — follow-up builds (added 2026-07-09):** re-run c8 legacy-indicator asset extraction (background agent lost at process exit) → before/after indicator boards per cell type; dense-24px 003 asks (TF wrapper structural trim, small checkbox box, Small chips + single-row truncation; 24 vs 26/28 pending team); map raw validation surfaces to CDS-WIP `interface/status/*` tokens when adopted.
- [ ] **Component Set Manager — bulk export finalization + filename template UI.** Figma plugin.
- [ ] **Open centric-ui PR #2 (component stories).** 22 component + 3 feature stories staged; held until [centric-ui#34](https://github.com/cpes-software/centric-ui/pull/34) merges so the PR diff is clean.
- [ ] **Mark `lint, types, build` as required status check on ds-docs `main`.** CI is green on [ds-docs#1](https://github.com/cpes-software/ds-docs/pull/1); update branch protection via `gh api repos/cpes-software/ds-docs/branches/main/protection` once that PR merges.
- [ ] **Add `.github/CODEOWNERS` to ds-docs.** Sean to provide the reviewer-per-path list; Claude opens a follow-up PR.
- [ ] **Wire up production deployment for ds-docs.** Vercel suggested (Next.js auto-detect); set `NEXT_PUBLIC_STORYBOOK_URL` to the deployed Storybook URL so embeds work in prod. Also swap the 28 hardcoded `localhost:6006` Storybook links that [ds-docs#3](https://github.com/cpes-software/ds-docs/pull/3) ships (PageHero chips + home page) once the URL exists. Added 2026-07-07.
- [ ] **Section D — reference design-system deep reads.** Atlassian, Carbon, Salesforce Lightning, Workday Canvas, Adobe Spectrum, Polaris, Primer, Fluent 2. **Pre-step:** enumerate available MCPs / plugins / skills per DS before WebFetch fallback. **Priority targets** for closing the A18 task-center / queued-jobs-list gap not surfaced by Mobbin: GitHub Primer (Actions runs), Vercel (Deployments), Stripe (Export queue). Synthesis doc has the full pre-step enumeration plan.
- [ ] **Section B audit (18 adjacent enterprise SaaS patterns).** Defer until Section A graduations stabilize. Most B-patterns reuse Section A primitives, lower-urgency than Section D.
- [ ] **28 individual pattern entries pending graduation at `08-knowledge/design/{slug}.md`.** Graduate one-by-one as Centric work creates demand; the master entry already references their target paths and serves as their parent until materialized.
- [ ] **Stream C re-audit scheduled ~2027-Q3** (12-18 months). Emerging patterns C4 NL-workflow / C5 canvases / C7 true-merge will mature significantly.

### Deferred (resurface on context match)

- [ ] **Re-privatize the workspace-repo author email.** During the 2026-06-04 reconcile push, GitHub blocked the push because Personal MBP commits use `hello@snds.design` in plaintext metadata. Worked around by flipping the GitHub "Block command line pushes that expose my email" toggle OFF — Sean wants this re-enabled later. Long-term fix: set repo-local `user.email` on Personal MBP (and Windows) to `570874+snds@users.noreply.github.com` (the form Work MBP already uses), and migrate the deployed identity convention into `00-bootstrap/setup/gitconfig.personal.template` so it propagates per-machine. Auth scoping rule: **superseded on the Centric laptop as of 2026-07-20** — see memory [[feedback-credential-scoping]]. The old formulation ("Centric repos → Centric auth; ANY personal/workspace surface → personal `snds` auth, all devices") now holds only on non-Centric machines. On `CS-K746DRWXY1` every repo action uses the Centric account, *including* commits to `snds/workspace` (the Centric account is a contributor there). This pending item's remaining scope is therefore Personal MBP + Windows only.
- [ ] **Populate `team-practices-and-decisions.md`.** Fills in passively as decisions surface; not a discrete task. Scaffold lives at `01-frameworks/team-practices-and-decisions.md`.
- [ ] **TanStack Table inline editing reference implementation.** Live artifact for design-dev handoff. No recent traction; resurface when handoff need arises.
- [ ] **Greenfield PLM SaaS redesign architecture exploration.** Vite/React SPA + TanStack Query stack; monorepo direction. Exploratory; no near-term deadline.
- [ ] **Seed SESSION-STATE.md for 03-omni, 12-MCS, 15-DavinciRemake.** Pre-seed deferred — create on demand when each project is next active.



---

## Active Projects

### Claude Workspace Infrastructure
**Status:** Active — knowledge vault layer live (2026-04-29)
**Summary:** Multi-session workspace with cross-device context sync via Obsidian + Git. Workspace root is **also an Obsidian vault and a Claude Code working directory** — three consumers reading the same filesystem. Hooks-based hands-off session lifecycle (SessionStart loads context, SessionEnd commits + pushes). Five frameworks (2026-04-21) + SESSION-STATE per-project template. 194-skill hub/spoke network (2026-04-28). 08-knowledge/ vault layer with three-tier surfacing system (2026-04-29).

**Layered additions across recent cycles:**
- **2026-04-25 (topology cleanup):** Restored deployed-vs-project distinction. The integration's deployed files (CLAUDE.md, dotfiles, MOCs, `.claude/`, `.obsidian/`) live at workspace root where the consuming tools expect them. Installer + Obsidian templates + integration architecture doc consolidated into existing `00-bootstrap/`. Project workspace `07-projects/00-obsidian/` now holds SESSION-STATE.md + README.md only — design history, not deployment. `.gitignore` rewritten to track only the system layer + the 00-obsidian project. Dispatcher's session-end commit simplified to `git add -A` (gitignore is now the source of truth).
- **2026-04-23 (Obsidian + Claude Code):** `CLAUDE.md`, `.claude/` (settings.json + hooks/dispatcher.py + 5 slash-command skills), `.obsidian/` (plugins, hotkeys, graph, templates), root MOCs (`_HOME`, `_PROJECTS`, `_SKILLS`, `_FRAMEWORKS`, `_CONTEXT`), `.gitignore` scoped to system layer, installer (Python stdlib-only + double-clickable wrappers + one-liner fetchers), `OBSIDIAN-SETUP.md` architecture doc. Windows hostname `Enterprise` registered in workspace-bootstrap.
- **2026-04-21 (Framework layer):** `01-frameworks/` folder with five framework docs + README + team-practices scaffold + session-state template. `workspace-bootstrap` extended with framework awareness + SESSION-STATE.md loading + Write 5 at session end. Opus 4.7+ skill audit report delivered.

**Project folder:** `07-projects/00-obsidian/` — populated 2026-04-25 with SESSION-STATE.md + README.md.

**Git remote:** `https://github.com/snds/workspace` (private). Initialized 2026-04-25; first commit pushed to `main` 2026-04-25.

**Next:** Smoke-test installer on Mac. Decide Python binary strategy. Then act on 2026-04-21 audit findings and seed remaining SESSION-STATE files.

---

### CentricSymbols Variable Icon Font System
**Status:** Active development
**Summary:** Variable icon font pipeline for Centric's design system. v0.3 architecture spec active. Four variable axes (wght, FILL, GRAD, opsz). COLRv1 for per-path opacity. Hybrid Figma plugin + local FastAPI/PyInstaller server as delivery. Seven-skill hub/spoke network (`variable-icon-font-architect` hub with 7 spokes: icon design, vector construction, pipeline engineering, 4 math skills).

**Key decisions:**
- Figma is authoring environment for default masters only (wght=400, FILL=0, opsz=24).
- Weight extremes derived algorithmically via inner boundary offset.
- Round join required for variable-font point topology compatibility.

**Next:** [Sean's call — decisions pending on GRAD axis derivation approach per SESSION-STATE.]

---

### Centric VMS Design System (`centric-ui` + `ds-docs`)
**Status:** Active — four PRs in flight (2026-07-07)
**Summary:** React 19 / Vite 7 / Tailwind 4 / shadcn-style component library for the Centric VMS platform. Repo: [cpes-software/centric-ui](https://github.com/cpes-software/centric-ui) (private). 2026-04-29: scaffolded Storybook 10 with foundation stories and split component stories into a separate PR. Stood up [cpes-software/ds-docs](https://github.com/cpes-software/ds-docs) (private, Next.js + Fumadocs) as the curated narrative layer; embeds Storybook stories via custom `<StorybookEmbed>` MDX block. Seeded with 8 foundations + 22 components (Design / Code tabs) + 4 patterns. Persistent design/code mode toggle + native foundation layouts + token-level dogfooding.

**Live PRs:**
- [centric-ui #34](https://github.com/cpes-software/centric-ui/pull/34) — Storybook setup + foundation stories. Awaiting review.
- [ds-docs #1](https://github.com/cpes-software/ds-docs/pull/1) — LICENSE + CI workflow. CI green; awaiting merge.
- [ds-docs #2](https://github.com/cpes-software/ds-docs/pull/2) — security deps: next 16.2.4→16.2.10 (13 GHSAs), postcss override, npm audit clean. Stacked on #1; opened 2026-07-07.
- [ds-docs #3](https://github.com/cpes-software/ds-docs/pull/3) — changelog hub + PageHero/KeyFacts/UseCases blocks + content sweep (the formerly-uncommitted local WIP, fixed forward to green CI). Stacked on #1; opened 2026-07-07.

**Branch protection on ds-docs `main`:** require PR + 1 review + linear history + conversation resolution; force-push and deletion blocked; admin bypass enabled.

**Stack quirks worth remembering:**
- ESLint pinned to `^9.39.3` (10.x breaks `eslint-config-next@16` — still unresolved upstream, vercel/next.js#91702).
- next hard-pins its nested `postcss` to 8.4.31 even at 16.2.10 → `overrides.next.postcss ^8.5.10` in package.json clears the audit; remove when next bumps its pin. npm quirk: overrides don't retro-apply to existing lockfile entries — delete the nested entry from package-lock + node_modules, then reinstall.
- ContentTabs uses `@radix-ui/react-tabs` directly (Fumadocs's wrapper omits `value`/`onValueChange`).
- DocMode uses `useSyncExternalStore` (avoids `setState`-in-`useEffect`).
- Storybook iframe theme sync via `preview-head.html` URL-globals parser + dark-mode body bg override (centric-ui's `@theme inline` bakes light values for CDS gray utilities, so dark mode only works through `--sem-*`).

**Admin tasks** (CODEOWNERS, required status check, deployment) are tracked as Pending Items in this file — migrated out of Claude Code local memory 2026-06-30; see memory `decision-externalize-everything-to-workspace`.

**2026-06-02 — Radix-derived color system:** re-architected the centric-ui color foundation onto **Radix Colors as source of truth** (values, 12-step context semantics, contrast) with a Tailwind-class compatibility layer (nearest-OKLCh-L aliases), APCA-as-governance (selection/audit, not primitive mutation), centric-blue replacing Radix blue, and brand-aware semantic hue assignment (info→cyan, warning→orange — no semantic context collides with the brand; collision rule ported from OMNI). New `--sem-selected` (Radix step 5) for active/selected vs neutral `accent` (hover). Built a Palette Review Storybook harness (25 components, before/after × light/dark, flagging) to drive the review. Shipped as 4 PRs (#64–67). Details in memory `project_centric-ui-radix-palette`; generator lives at `~/projects/cpes-software/centric-ui/scripts/generate-color-palette/`.

**Next:** Sean assigns reviewers on ds-docs #2 + #3 (2026-07-07). ds-docs merge order **#1 → #2 → #3** (CI only triggers on PRs targeting main, so #2/#3 checks appear after #1 merges and GitHub retargets them). After ds-docs#1 merges → mark CI status check required. After centric-ui#34 merges → open the centric-ui PR with the staged component stories. Review/merge the Radix color-system PRs #64–67 (tokens→components→harness).

---

### Centric 8 PLM Design System (`cds-docs`)
**Status:** Active — scaffold complete, content sprint pending
**Project root:** `~/projects/c8-plm/` (outside Drive — see stub at [07-projects/05-C8-PLM/README.md](../07-projects/05-C8-PLM/README.md))
**Summary:** Fumadocs documentation site for the **Centric Design System (CDS)** that powers the **Centric 8 PLM** monolith — `@centricsoftware/design-system` v1.3.0-develop-13 on Bitbucket (`centricsoftware/design-system`). Parallels the VMS-side `cpes-software/ds-docs` site that shipped 2026-04-29; same scaffold (Next.js 16 + Fumadocs + Tailwind 4 + custom MDX blocks + DocMode toggle), retargeted at C8's design system.

**2026-04-30 milestone:** Scaffold spun up at `~/projects/c8-plm/cds-docs/`. 8 foundation MDX with real ported content (colors, typography, icons, sizes, validation, z-index, theme — sourced from `CDS/src/stories/*.mdx`). 59 component stubs in atomic IA (19 atoms + 18 molecules + 22 organisms — mirrors `CDS/src/components/{atoms,molecules,organisms}/`). `npm run lint`, `types:check`, `build` all green; build emits 222 static pages.

**Stack quirks worth remembering:**
- Next.js + Turbopack rejects symlinks that resolve outside the project root (`Symlink [project]/node_modules is invalid`). `node_modules` and `.next/` must live inside the project tree. Drive sync of those dirs is incompatible with the build pipeline — hence the project is at `~/projects/c8-plm/`, not in Drive.
- Same ESLint pin as VMS ds-docs: `^9.39.3` (10.x breaks `eslint-config-next@16`).
- Component IA differs from VMS: atoms/molecules/organisms (mirrors CDS source layout), not the functional primitives/inputs/layout/overlays/feedback grouping VMS uses.
- CDS itself uses **system fonts** (`-apple-system, BlinkMacSystemFont, ...`) and **Material Symbols** for icons — different from VMS's Inter Variable + Lucide. The docs site chrome still uses Lucide; only documented foundations reflect CDS's system.

**No GitHub repo / no CI / no deployment yet** — building in isolation until write access to `centricsoftware/design-system` is granted on Bitbucket.

**Next:** Decide content-fill order for the 59 component stubs (suggestion: most-used first — Buttons, Inputs, Select, Tabs, Modal, DataTable, Card, Tooltip, Icon, Text — then sweep the rest). Add `metadataBase` to layout to silence the build warning about social-card image URLs.

---

### Centric PLM Design System Work
**Status:** Active — multi-thread
**Summary:** Cross-framework DS strategy for Centric PLM serving fashion, food, and product verticals. Primary threads:
- Data table documentation (90+ tables audited, Dojo/dgrid legacy → TanStack Table modern).
- Token architecture across frameworks (Vue primary, React/Angular adapters).
- Cross-framework DS strategy (Ark UI recommended as headless foundation).
- Greenfield PLM SaaS redesign architecture exploration.

**Active Figma files:**
- Core Design System (file key: `sgsaBIZBVNjuoBDTwqZlhd`)
- Components (file key: `pyYokK7ajFtPgeQAKfjIZd`)
- Research FigJam: `RWJnQG5MLStvN7JfEllnWZ`
- Visual research board: `PuCufvvSxifLafOxHwQeMp`

**Next:** Data table cell anatomy + state matrix. Component spec work.

---

### SaaS PLM Knowledge Base (`knowledge-discovery`)
**Status:** Active — reference / consumed (cloned 2026-07-20)
**Repo:** [saas-plm-analysis/knowledge-discovery](https://github.com/saas-plm-analysis/knowledge-discovery) (private, org-owned)
**Local path:** `<Projects>/saas-plm-analysis/knowledge-discovery` — outside this workspace per the "codebases live in Projects" core rule. Full detail in memory [[reference-saas-plm-knowledge-discovery]].
**Summary:** Centric's cross-role knowledge base for the new SaaS PLM platform — legacy C8 domain
extraction mapped to target SaaS configuration, plus PM requirements, UX research, UI specs, engineering
architecture, ADRs, and a machine-consumed `ai-knowledge/` layer (patterns, legacy→new mappings, golden
examples, decision log). Agent-aware: its own `AGENTS.md` domain taxonomy, an `INDEX.md` in each of 62
directories (open the local INDEX before loading leaf files — the repo's own rule), 8 `.cursor/rules`, and
4 `.cursor/skills`.

**Why it matters here:** it is the employer-side domain source of truth that sits underneath the
`centric-ui` / VMS design-system work. `ui/design-system/` and `ux/` overlap Sean's DS threads directly —
cross-read them, never copy content across the personal/employer boundary in either direction.

**Next:** [Set when first substantively used — likely cross-reading `ui/specs` + `ux/flows` against the
centric-ui component work, and the `ai-knowledge/mappings` layer against the C8→SaaS migration threads.]

---

### Centric UX Research (Multi-Vertical)
**Status:** Active — research / analysis
**Summary:** User research across Fashion, Food, and Product Engineering verticals to derive scalable workflow models. FigJam boards and enterprise persona sets as recent deliverables.

**Operating layer:** Research and Evidence Framework (04) is the primary lens. Median persona test applied per vertical (don't collapse across verticals).

**Next:** [Captured per SESSION-STATE when project resumes.]

---

### Legion (Game Project)
**Status:** Active — V1 prototype + standalone repo
**Summary:** Interstellar hard sci-fi game inspired by The Bobiverse. Factory management × 4X strategy × RTS × narrative core. Tech stack: Three.js + WebGPU (TypeScript + GLSL).
**Code home:** `/Users/snds/Projects/Legion` → `https://github.com/snds/legion` (private). Extracted from workspace on 2026-05-11; design refs (Reference/, Screenshots/, Video/, Visual-Development/, docs/) remain in workspace at `07-projects/13-legion/` alongside SESSION-STATE.md.

**Skill set (12 skills):** `legion-project` (foundation) + `lead-game-designer` / `lead-art-director` / `lead-game-developer` (hubs) + `threejs-materials-master` / `glsl-shader-architect` / `threejs-vfx-atmosphere` / `webgpu-advanced-rendering` + the 2026-07-22 hero-body spokes `realtime-render-performance` / `planetary-terrain-lod` / `atmospheric-scattering-and-clouds` / `stellar-and-relativistic-hero-bodies` (specialty spokes). Also leans on `game-scale-traversal`, `vfx-volumetrics`, `vfx-particle-systems`, `sci-astro-objects`.

**V1 Systems (minimum viable):** Exploration, factory building, resource economy, RTS combat, Bob clone mechanics, tutorial flow.

**Visualization state (as of 2026-05-12):** 9-tier zoom hierarchy (surface→galaxy) with Powers-of-10-style seamless sector→arm→galaxy fades. Galaxy disc is now a SINGLE volumetric raymarch (one BoxGeometry, 24-step Beer-Lambert integration) replacing the previous 9-disc+8-dust stack — looks correct from any angle including edge-on, dust actually occludes light from behind through line-of-sight extinction, 1 draw call instead of 17. Per-particle stellar size/color (Planckian, ~160K stars), real-Milky-Way structural fidelity: 4 arms emerging from bar tips, ~13.4° pitch, ±1kpc galactic warp, LMC/SMC at sky-correct positions, Sgr dSph tidal stream. Cinematic flight-path camera mode (shift+dblclick triggers a Bezier-arced traversal with ease-in-out cubic timing) + velocity-aware micro-streaks on stars (gated below 6000 WU/s — subtle/minor per design). Per-object camera scale at close tiers, full hover+select+dblclick model.

**Planet-renderer state (as of 2026-07-22):** Planet material hardened end-to-end (PRs #163–#184, all merged + deployed to Pages). Living weather (CPU cyclone lifecycle, ocean-gated, bounded shear); biome/climate as signed additive moisture field + Earth-MAT temperature; Earth-calibrated dark biome palette; settlement-realistic night lights (habitability field); ice/snow overlays with uneven cap margins; storm lightning; systemic World dials (offset/manual-edit-preserving) over the raw sliders; bake parity via one finishHeight() path. Stars-through-planets bug fixed (ledger A-06). Full detail + carry-forward in SESSION-STATE.md.

**Next:** ✅ **Delivered 2026-07-22** — the adversarially-checked performance/fidelity skills landed: 4 new hero-body spokes + a **project-wide performance doctrine** (60 FPS floor, uncapped by default, optional user frame cap, input latency co-equal) + the [[legion-hero-body-rendering-research]] master dossier + [[legion-planet-surface-rendering]] hard-won patterns. **Now:** implement against `src/render/` — reconcile `planetary-terrain-lod` with the existing quadtree renderer; wire `realtime-render-performance`'s frame-cap setting + input-latency pipeline into the engine loop; then profile/optimize the planet material at close zoom. (Longer arc still: galaxy-scale viz → system-scale gameplay per V1 scope; procedural-worlds `feat/worlds-star` S1 baton also still open — see SESSION-STATE 2026-07-11 block.)

---

### Figma Plugin Development
**Status:** Multi-plugin — active
**Summary:** Several plugins under active development:
- **Claude AI Agent Plugin** — embedding Claude as autonomous design collaborator with Figma scene graph access. Phase 2 library intelligence + variable tools complete. Rate limit mitigation (compressed tool schemas ~78%, 8-message sliding window, capped tool results), stop button via AbortController, resizable window, inline markdown rendering live.
- **Component Set Manager** — batch property rename + bulk variant export with configurable filename templates.
- **figma-repo-sync-plugin** (`~/projects/cpes-software/centric-ui/figma-repo-sync-plugin/`) — TypeScript plugin that generates Figma components from shadcn / Tailwind / CVA React source. Branched at `feat/figma-repo-sync-plugin` off `main` in `cpes-software/centric-ui` (Draft PR for FYI visibility). Bundles 4 + 5 (A–F) + 7 + 7.1–7.8 + 8 + 9 + 10A.1 + 10B.1 + 11.1 shipped (2026-05-11..05-12). **2026-05-13 audit-driven bundle**: 10A.2 (Phase 1 fixture-fallback unblock for Form/Sidebar/Sheet/NativeDialog when story 404s or parses empty; Phase 2.1 Input/Textarea placeholder injection at walker + single-component dispatch; Phase 3b EmptyState slot-default wiring from synthetic compound-style fixture children + conditional auto-visible when inner slot has a default) + 10B.1.1 (list-container dedup exemption for TabsList/TableRow/SelectGroup/AvatarGroup/SidebarMenu + Tabs master-assembly dedup; Phase 3a.1 inferLayoutMode conditional-class filter + `<tr>` HORIZONTAL tag default + TabsList componentName override for cnExtractor cva-unwrap gap) — promoted 9 of 11 ❌ from the 2026-05-12 audit to ✅. 374/374 tests passing. Build 420.3kb. **Still ❌**: ScrollArea (Phase 3c — story rich=13 wins but its `<div>` wrapper child gets filtered by PascalCase tag check), Avatar (size-full → Figma fill-parent layout-sizing translation). **Still ⚠**: Dialog `.DialogContent` 108×845 narrow column (Bundle 10B.2 partial-slot architecture), Badge `secondary` token cascade gap, Tabs/Table/EmptyState per-instance content overrides (Phase 4 `componentProperties` work — every TabsTrigger currently says "List view", every TableHead "Name", every EmptyState action button "Button"). **2026-05-23 (Bundle 11.3.70, 445 tests, ~570kb):** the `(?)`-binding regression is CLOSED (Phase 0 black-default kill in resolveVariableRGBAAtMode + page-level/Badge-glyph Colors mode pinning + authoritative scanner proving residual 3 `(?)` are cosmetic multi-value CVA tokens). **State-representation pattern landed on Button + Badge** (per `07-projects/09-figma-repo-sync-plugin/docs/2026-05-23-state-representation-decision-tree.md`): grouped `<slot>/<state>` variable naming (explicit `default`); physical State axis with foreground-tinted state-layer overlays (hover 12/focus 24/pressed 32%), focus ring + error (border+ring) overlays, disabled 50%; per-component state derivation. **Button Type expansion**: None/Leading/Trailing/Both + Icon with size-responsive icon-side padding. Footer de-clip + variantChild idempotency fix. Phase 1: TOKEN_PALETTE derived from COLOR_TOKENS (single source) with documented palette-generator migration seam. **Decision**: Figma state-as-modes is valid; physical for the smaller axis (states), modes for variant; opacity can't be mode-driven → normalized state-layer (Decision B). **Pending**: regen-verify on 11.3.70; Phases 2–3 (parser/binder unification, deferred); palette-generator migration (pending engineer alignment + non-breaking path); engineer-doc for the `default` naming affordance.

**Project folder:** `07-projects/04-claude-figma-plugin/`

**Next:** Bulk export finalization → filename template UI.

**figma-repo-sync-plugin — known non-issues (do NOT iterate on these until engineering follows up):**
- **NativeDialog** — not a shadcn primitive (404s on shadcn docs and on the project's storybook branch). Likely a Centric-specific use of the HTML `<dialog>` element or a dev-side helper component. As of Phase 1 (b93c76c) the master now picks up the dialog category fixture (richness=17), so visually it shows "Are you absolutely sure?" + Cancel + Continue like the regular Dialog. Leave as-is in the generated library; we'll only refine if engineering raises a follow-up about whether this primitive should ship at all.

---

### Omni — Design-to-Production Platform
**Status:** Exploratory architecture
**Summary:** Seed product for a computational design system — canvas editor + headless component library + IDE/CLI + visual logic builder + intermediate representation (IR). Framework-agnostic (Mitosis/Radix approach).

**Hub skill:** `omni-project`

**Next:** [Captured per SESSION-STATE when project resumes.]

---

### AI-Powered Design Assessment — Exploratory
**Status:** Research / exploratory
**Summary:** Bridging visual audit (component assessment) and code generation tools for enterprise PLM. Goal: reduce manual transcription between design tools and dev handoff. Connects to the `visual-qa-toolkit` skill (instrumented-perception layer, now built) and `native-visual-eval` (native-resolution precondition, framework #10).

**Next:** Apply the visual-QA stack (`native-visual-eval` → `visual-qa-toolkit` → `lead-visual-qa`) against a real PLM component-assessment pass.

---

### Workspace Brain
**Status:** Active
**Summary:** Standing home for sessions whose subject is the workspace itself (validation, fix, migration, infrastructure). Established 2026-07-09 per the workspace-work project-home rule in framework #08 (FX-13); git-tracked for cross-machine continuity.
**Folder:** `07-projects/19-workspace-brain/`
**Triggers:** workspace brain, workspace fix, workspace validation
**Next:** Complete the FX-1..FX-14 fix session (Phases E–F), then re-run the validation harness and compare scorecards.

---

### Portable Bootstrap Generator (`wsx`)
**Status:** Active — validated, colleague-ready
**Summary:** Scripted + LLM-enhanced generator that scaffolds a portable, git-native, token-frugal workspace-brain for any user, on any surface, BYO-tokens (no API key, no model calls — runs on the user's own agent/MCP/local-LLM; `wsx scan` detects the stack and gates with a surface recommendation if none found). Stub-free `wsx` CLI (14 commands); the Resolver is a composite builder (fuses the person's judgment with distilled industry-leading references, cited author-voice, never copied); per-domain expertise calibration (each emitted skill written at its own domain's altitude); conflict-free session fragments + union-merge + idempotent compaction for multi-device safety. `VALIDATION.md` is the colleague-facing proofboard.
**Folder:** `07-projects/18-bootstrap-generator/` — **git-tracked** (whitelisted in `.gitignore`); first non-Drive-coupled, version-controlled project. Eventual destination (SPEC §9): standalone `wsx` CLI repo, extractable from this folder's history.
**Triggers:** bootstrap generator, wsx, workspace generator, portable workspace
**Next:** Optional polish — deeper `wsx doctor` self-heal for generated workspaces (re-emit stale adapters, verify `.gitattributes`); a registry search/discovery index layer; externalize the embedded scaffold templates. Or drive the generator through a real colleague test. Distribution zips ready in `dist/` (gitignored; regen via `package.py`).

---

### CDS Figma–Code Audit
**Status:** Active — audit complete + verified (2026-05-04); acting on gaps blocked on Sean
**Summary:** Prop-parity audit between the Centric Design System (CDS) Figma libraries and the shipped `@centricsoftware/design-system` code (v1.3.0-develop-13), surfacing where Figma and code diverge. Full audit + v1.1 prop-parity artifact written and visually verified. Codebases: `~/projects/c8-plm/cds-docs/` (Fumadocs docs, port 3001) + `~/projects/c8-plm/CDS/` (DS source + dist). All 4 CDS Figma library files read via Figma MCP.
**Folder:** `07-projects/16-CDS Figma-Code Audit/` (definitive final state: `audit_prop-parity_v1.1_2026-05-04.md`)
**Next (blocked on Sean's call — docs acknowledgment vs. CDS source PR):** act on 🔴 gaps (Button `tertiarySubtle`, Accordion `size`/`disabled`, Progress Indicator, Chip status variants, Spinner linear); 🟠 Text gaps (italic variants, Hyperlink Extra Small, UI-size naming); deep-read the Custom Icons page in 005-Iconography.

---

## Design System — Current State

**System:** Centric PLM internal DS
**Maturity:** Mid-stage — audit complete, triage and spec work in progress
**Active concerns:**
- Data table component coverage (primary current focus)
- Token migration between Figma DS versions
- Cross-framework component parity (Vue primary)
- Component deprecation communication to engineering
- Cross-framework strategy: Ark UI as candidate headless foundation

---

## Migration Note — 2026-04-21

On 2026-04-21 a framework layer was added to the workspace. Five top-level operating frameworks now live at `01-frameworks/` in the workspace root:

1. Aesthetic Lens (`01-aesthetic-lens.md`) — philosophical ground
2. UI/UX Operational Framework (`02-ui-ux-operational-framework.md`) — operational decisions
3. Collaboration and Critique Framework (`03-collaboration-and-critique-framework.md`) — conduct
4. Research and Evidence Framework (`04-research-and-evidence-framework.md`) — epistemology
5. Last-Mile Craft Framework (`05-last-mile-craft-framework.md`) — finishing discipline

Orientation + compressed summaries at `01-frameworks/00-README.md`. These frameworks sit above any project-specific skill or context. They inform design, collaboration, research, and craft decisions across every project in the workspace.

The `workspace-bootstrap` skill has been extended to be aware of the frameworks folder (silent note at boot if missing) and to load per-project `SESSION-STATE.md` files (operational state continuity between sessions). `_session-state-template.md` in the frameworks folder is the spec for those files.

The stale `workspace-bootstrap-updated` skill directory has been renamed to `_deprecated_workspace-bootstrap-updated_2026-04-21` pending Sean's removal.

A skill audit report (`05-artifacts/active/skill-network-audit_opus-4.7_2026-04-21.md`) identified five prioritized opportunities for aligning the skill network with the new framework layer. None of the recommendations have been executed yet — the report is a deliverable, not an action log.

---

## Artifact Naming Convention

```
context_descriptor_vN.N_YYYY-MM-DD.ext
```
- Never overwrite — increment version
- Minor bump = iterative changes
- Major bump = structural changes
