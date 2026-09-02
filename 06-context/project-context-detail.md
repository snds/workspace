# Project context — pending detail

_Long substance for pending items, graduated from `project-context.md` 2026-08-07 (harness-map rec #2). Stubs + `^pc-NN` anchors remain in [project-context.md](project-context.md) so Open Engine Linear pointers stay valid. Do not delete anchors._

## pc-01

- [ ] **SaaS PLM prototype — DataTable contract, then the TanStack replacement..** (Added 2026-07-28.) The hand-coded table in `cpes-software/saas-plm-prototype` is being replaced with TanStack Table. **Contract-first**: repo survey @ `6380a26` found **16 files rendering `<table>` across 11,784 lines** (not 5 components), `MaterialsTable` at 1,320 lines / 20+ props, five independent re-implementations of sort/filter/select/density/resize, **2 `aria-*` attributes and 0 roles/`tabIndex` in the six core table files**, no virtualization or pagination, and **zero table tests**. Plan + contract skeleton + gating criteria: `05-artifacts/active/saas-proto_datatable-contract-plan_v1.0_2026-07-28.md` (machine-local). **First three moves (do before any port):** (1) classify all 16 as component/recipe/snowflake/not-a-table — likely cuts scope by a third; (2) pin the 6 load-bearing behaviors with tests against the *current* implementation, because after the port "equivalent" stops being testable; (3) author `datatable.contract.yaml` resolving every feature's state `owner`. Durable model: [component-contract-schema.md](../02-shared-references/component-contract-schema.md) + [[component-contracts-and-schemas]] + framework #09 §5a. **Employer profile** — deliverables land in the employer repo (branch → PR → human review), never mirrored here. **Blue-sky stance (Sean, 2026-07-28):** this is new SaaS SMB work and must NOT be scoped from C8's legacy dgrid feature inventory — derive the feature list articulation-downward from the SaaS product's own UX source of truth (`saas-plm-analysis/knowledge-discovery` → `ux/flows`, `ui/specs`), the SMB user's jobs, and the lineage-neutral pattern canon ([[enterprise-saas-design-patterns]] + framework #09 §6/§7). The C8 dgrid→TanStack work stays **supplementary only** — pitfall ledger, effort calibration, and the eventual C8→SaaS parity horizon — consulted *after* the contract has a draft. Gate: every feature cites a user job, a UX spec, or a canon pattern; "C8 has it" is not provenance. **Growth horizon (Sean, 2026-07-28):** SMB is the entry point, **not the ceiling** — SaaS PLM will grow into enterprise, and SMBs commonly want enterprise practice because adopting it is how they grow. So **scope down, don't shape down**: SMB sets the *spec*, the enterprise horizon sets the *schema*, and the rule is **model the axis, ship one value on it** (declaring an axis is free; adding one later breaks every consumer). Highest-leverage axis on the table: `features.*.owner` — hardcoding `owner: table` makes saved views/deep links/persistence a rewrite of all 16 surfaces. Record decisions not to build (`enabled: false` + rationale) rather than omitting them, and **keep capability and entitlement orthogonal** — tier boundaries move (the Figma variable-mode-limits pattern), so packaging never goes in the component contract. Calibration: our verticals (fashion, consumer goods, food) adapt slower than design tooling — this is not a mandate to build enterprise features now, only that the architecture must never be what blocks the growth. **⚠️ REVIEWED + RE-SCOPED 2026-07-28** — implementation plan: `05-artifacts/active/saas-proto_datatable-implementation-plan_v1.0_2026-07-28.md` (machine-local). Live verification across three checkouts confirmed every survey number exactly (16 files / 11,784 lines / 2 aria / 0 role / 0 tabIndex / 21 props on `MaterialsTableProps` / 2 non-table tests), but found the premise stale: **`@centric/data-table` already ships in centric-ui `main`** — 201 files, ~19k lines, `@tanstack/react-table ^8.21.3` + `@tanstack/react-virtual ^3.13.23`, with `cellSelectionFeature`, grouping, computed columns, virtualization, pagination+loadMore and a real test suite. TanStack is absent from the *prototype*, not the *system*. And the prototype's own `MIGRATION-TO-CENTRIC-UI.md` §0 forbids build work landing there (*"the prototype is the spec, never the destination"*; rung 1 = reuse `@centric/data-table`, delete the proto's version). **Decision (Sean, 2026-07-28): "contract arbitrates, proto consolidates."** The contract lives in **centric-ui** beside `packages/data-table` (a contract the incumbent's CI can't enforce is a document, not a gate); `@centric/data-table` is signatory #1 and is *verified* against it, its gaps becoming its own backlog; the prototype consolidates 16 surfaces → **one local recipe** conforming to the contract's *presentation* clauses only and **never adopts TanStack** (mechanical tripwire: no `@tanstack/*` in the proto's `package.json`). Two corrections to the diagnosis: density is **already** centralized (`LandingToolbar` exports `Density`/`TABLE_CELL_Y`/`TABLE_HEAD_Y`/`DATA_TABLE_SHELL`, imported by 18 files) so only behavior state + cell rendering are duplicated; and a feature-density signal predicts **3–6 of the 16 are snowflakes/not-tables** (`ManageViews`, `SourcingPanel`, `MediaLibraryModal` lead). Two executional blockers the original plan missed: **there is no component-test harness** (Vitest 4 installed, but no jsdom/testing-library/config — Gate A's "pin 6 behaviors in a day" is really 2–3 days plus a CI decision, since `design-system.yml` deliberately installs nothing), and **the repo already has the enforcement architecture** the plan proposed to invent (`design-system.rules.json` + `ds-core.mjs` + `ds:check/fix/report/backlog` + pre-commit hook + CI backstop) — extend it for L1/L2 rather than standing up a parallel JSON-Schema runner. Gate 3 now applies to `@centric/data-table` exactly as to C8: *"the incumbent has it"* is not provenance. **Olga is a required signatory** (co-author of the prototype). Sequence: WP-0 align on destination (blocking, 1h) → WP-1 classify the 16 ∥ WP-2 harness → WP-3 pin 6 behaviors → WP-4 three-witness testimony → WP-5 author the contract → WP-6 L1/L2 in CI → WP-7 verify the incumbent ∥ WP-8 consolidate the proto. ~11–17 days; moves 1–3 pay off even if the contract idea is dropped. **🔄 REVERSED + BUILT 2026-07-30** — Sean overturned the "proto never adopts TanStack" call: the goal is **migratable parity** with centric-ui (same move as the shadcn/BaseUI alignment), so the prototype SHOULD run centric-ui's table as closely as possible. *"Either we consume what they have or we duplicate it — zero issue with the data table and its supporting dependencies being the few things our prototype depends on."* The `no @tanstack/*` tripwire is **void**. Decisive finding: `@centric/data-table` is **not standalone** — it reaches into its host app's `~/components/ui/*` + `~/lib/*` **41 times**, so consuming the table means adopting the foundation under it (proto had 8 of the 14 needed modules; centric-ui has 49 `ui/*` vs proto's 20). Prototype **stays a separate repo for now** (freedom over zero-drift; manual sync accepted until the eventual move into centric-ui — options weighed: design-only deploy inside the live app rejected, since it's SSR + blocked on the cloud-dev backend). **Built, on branch `feat/datatable-centric-ui-foundation`, UNCOMMITTED:** 6 primitives copied byte-identical; `@centric/data-table` copied in as a byte-identical local copy of upstream (166 files / 16,023 lines, tests excluded); a `~` → `src/app` alias + `#internal`/`@centric/data-table` aliases so copies need **zero edits** and re-sync is `cp`; deps added at centric-ui's exact versions; and `table-lab.html` — a standalone comparison page (Current vs centric, same Seasons data, per-panel error boundaries). `CENTRIC-UI-SYNC.md` records provenance + re-sync procedure. **Corrections to earlier claims:** lingui is **runtime-only** (no macros/plugin/catalogs — the earlier "heavy build-time system" claim was wrong); lucide 0.487→1.x is additive (**106 icons checked, 0 missing** — Sean called this); date-fns 3→4 fixed a *pre-existing* `@base-ui/react` peer break. **The load-bearing lesson: the build is not proof in this repo** — it passed green while the lab rendered blank (nuqs needs a framework adapter; `nuqs/adapters/react-router/v8` exists for the app proper). Only a real browser load caught it. **Upstream finding for centric-ui (recorded, not patched):** its own `FilterOptionSearchInput.tsx:36` uses `h-9 rounded-md`, off the centric control scale. **Progress 2026-07-30 (Layer A+B):** visual parity plan at `05-artifacts/active/saas-proto_datatable-visual-parity-plan_v1.0_2026-07-30.md`. Layer A (lab recipe) + Layer B (`LandingDataTable` in `src/app/features/landingDataTable/`, Seasons + Materials-subset lab subjects) complete. **Progress 2026-07-30 (density):** global Compact/Normal/Spacious density shipped in the prototype (header toggle, persisted, radius ladder + glyph/chip shape rules); card-grid selects default to circle. **Committed + PR open:** [saas-plm-prototype#13](https://github.com/cpes-software/saas-plm-prototype/pull/13) on `feat/global-density` — density-led PR that also includes the previously uncommitted DataTable foundation / token-lab / table-lab working tree. **Next:** Olga reviews #13; deepen Materials lab toward the full column set post-merge; revisit the contract as acceptance checklist; WP-0 memo drafted but **not sent**; lift density axis into centric-ui when ready (ROW_DENSITY sync logged as C14).

^pc-01

---

## pc-02

- [ ] **Silence the two recurring beacon-enroll NOTEs (Work MBP main, `CS-K746DRWXY1`)..** (Added 2026-07-28.) workspace-doctor's sweep flags `Projects/design-system` (**employer** — bitbucket/centricsoftware; must stay OUT per the standing rule) and `Projects/open-design` (non-personal org `github.com/nexu-io`; classify before any enrollment) as unenrolled on every run. Record both in `00-bootstrap/dist/beacon-repos.ignore.txt` as deliberate skips to quiet the NOTE — or enroll `open-design` if it's actually personal. A third flag, `Projects/workspace`, is a case-mismatch false positive (the repo flagging itself) and needs no action. Context: doctor on this machine is otherwise clean and the 13 historical MISSes were acked 2026-07-28 (ack-mark 08:34:56).

^pc-02

---

## pc-03

- [ ] **Machine-layer installs on remaining machines (FX-1/FX-14 carry-over)..** Run `00-bootstrap/doctor/workspace-doctor.sh` + retire Drive-era `~/.claude/hooks/*.sh` + registrations on: Work MBP (main, `CS-K746DRWXY1`), Work MBP (loaner, if kept), and the Windows Desktop (`Enterprise` — needs a Windows install route first: shims are bash/launchd; document the brain location in memory `fact-machine-layer-installs` at install time). Then run ONE verified post-migration Windows session end-to-end (none exists on record). **Work MBP session also includes:** Cursor User Rules + Perplexity Space beacon pastes + `--ack-chat` there (Sean's split, 2026-07-09). Added 2026-07-09 (fix session).

^pc-03

---

## pc-05

- [ ] **Employer design-system migration (cpes-software)..** (Added 2026-07-15; **unblocked 2026-07-20**.) Audit complete: a Figma-Make prototype mapped INTO the design system as a reuse-and-extend migration (most widgets land on components engineering already ships; little is genuinely net-new). Directionality (Sean): prototype = spec; all build work lands in the design system — reuse → extend → author net-new only if novel. Deliverables (migration plan + interactive gap map) and the review PR are tracked in the **employer repo** — not mirrored here (separation rule). ~~Held pending backend access provisioning~~ — **backend access landed 2026-07-20**; centric-ui now runs locally against the cloud dev backend (`PORT=3000 npm run dev -- --port 3000` from the `centric-ui-main` worktree; setup traps recorded in [[centric-ui-local-against-cloud-dev]]). **Gap report re-run 2026-07-21** against current `main` on both repos (Olga had moved the prototype onto real shadcn/Radix, invalidating the first audit's premise): plan + interactive gap map refreshed and a new per-unit detail appendix added, PR #1 updated in place, replied to her CHANGES_REQUESTED review. Verification finding worth remembering: report the stable mapped verdict, not the volatile confirmed/adjusted count ([[adversarial-verify-label-volatility]]). Next: on Olga's re-review sign-off, resume the build (quick-win reuses first).

^pc-05

---

## pc-06

- [ ] **centric-ui PR #179 — assign reviewers + settle the redirect-URI question..** (Added 2026-07-20.) Makes local-FE-against-cloud-dev work: routes record/schema-registry/workflow through `cloudOrLocalServiceProxy` (completing the pattern Alex Myronov introduced in #160 — natural reviewer), and corrects the API-key placement across `.env.example` / `.env.cloud.example` / `docs/local-setup.md`. **Item 3 needs a decision, not a review:** the VMS realm's `react` client accepts only `localhost:3000` while `vite.config.ts` defaults to 8082 and the example file said 5173 — either the realm allows 8082 or the examples say 3000. Deliberately not guessed; needs whoever owns the realm.

^pc-06

---

## pc-08

- [ ] **Purge two abandoned centric-ui SHAs carrying the personal email..** (Added 2026-07-20.) `ec04737` and `86651f0` were force-push-replaced within ~10 min, but GitHub keeps unreferenced commits reachable by direct URL until GC. Not in any branch, PR, or search result; the value is the public commit email, not a secret. Closing it out properly needs a GitHub Support request. Rule that prevents recurrence: [[feedback-credential-scoping]].

^pc-08

---

## pc-10

- [ ] **"Context is King" — workspace foundation refinements..** (Added 2026-07-09, Sean's directive.) Bring declared-context resolution to the foundation of *every working session*, not just the audience/evidence delivery layer. Candidate scope: session-start ritual surfaces the active context profile alongside machine/git; dispatcher hook resolves profile mechanically (repo remote, project declaration) and injects it; `SESSION-STATE.md` context fields populated across all 8 active projects; memory/knowledge entries carry context tags; skills receive the profile on load. Independent of — but informed by — the Audience & Evidence system shipped 2026-07-09: generalize from `02-shared-references/delivery-playbooks/00-context-profiles.md` (the profile model, resolution order, citing rule, fail-safe default).

^pc-10

---

## pc-11

- [ ] **C8/CDS semantic status-token gap (from the 2026-07-08 cell-validation session)..** C8 has no warning stroke/tint tokens; orange accent border used as the documented interim (Jabili directive). Flesh out status/context colors in the semantic token set — warning/error/info/success each need border + low-chroma tint-surface + on-tint text tokens. Verify the failing session didn't already file this; raise as a CDS ask if not. Added 2026-07-08.

^pc-11

---

## pc-12

- [ ] **Act on the 2026-07-08 workspace audit carry-forwards.** (see audit-log entry): (a) ~~APCA body-text floor~~ RESOLVED 2026-07-08 per Sean — the three values are a deliberate TIER, not a contradiction: `a11y-visual` = accessibility floor (bare minimum) · design-engineer table = working target ("happy middle") · [[radix-derived-color-system]] = Radix-scale-specific, scoped to Radix-derived palettes only; cross-linked tier notes added in all three files; (b) decide whether the remaining a11y/color skills get frontmatter `triggers:` (`ux-accessibility`, `fe-accessibility`, `visual-qa-accessibility`, `lead-accessibility-architect`, `gd-color-theory`, `infod-encoding-theory`) — deliberately deferred to avoid over-firing; (c) CVD prevalence numbers drift across 4 skills — align on one source; (d) `06-context/artifact-registry.md` hardcodes line-number tables for gitignored artifacts (unvalidatable mirror — regenerate or drop); (e) generalize the doctor's fossil check into a tracked `* 2.md` conflict-copy sweep — ~~one instance (`_archive/figma-plugin-patterns 2.md`, stale subset) removed 2026-07-23~~; the *doctor-sweep generalization* is still open; (f) ~~`08-knowledge/research/research/` double-nesting~~ RESOLVED 2026-07-23 — flattened to `research/`, `_INDEX.md` updated (Obsidian `[[wikilinks]]` unaffected — basename-resolved). Added 2026-07-08.

^pc-12

---

## pc-14

- [ ] **Load the evolved `ux-component-library` v2.1 on this + other machines..** The **Component & Pattern Framework (#09)** shipped 2026-06-18 — a 5-layer DS context system (framework hub + skill + `ux-components` MCP + `DESIGN.md` + `AGENTS.md`). New/changed: `01-frameworks/09-component-and-pattern-framework.md`, evolved skill + 3 references, `02-shared-references/ds-agents-binding.md`, and the A2UI canonical catalog (`02-shared-references/a2ui/`). The plugin cache still holds v0.2.0 — **restart Claude Code** or rerun `09-tools/build-local-skill-plugin.py` + `claude plugin install snds@snds-local`. C8 `DESIGN.md` + `AGENTS.md` written locally in `c8-plm/` (separate repo). Optional follow-ups: validate the A2UI catalog with A2UI's conformance tooling; build a CDS renderer mapping catalog variants → `--sem-*`; A/B-evaluate a C8 screen. See memory `decision-component-pattern-framework-system`.

^pc-14

---

## pc-15

- [ ] **C8 cell-indicators — Sean sign-offs to unblock propagation..** Pilot built + code-validated on the Figma `cell-indicators` branch (full state: `07-projects/02-centricPLM/context/cell-indicators-pilot.md`). Open decisions: (1) propagate lock+tint read-only (replace the `Cell Value` italic Read-only mode across the 26 cell sets); (2) enum-chip Computed keep/drop (KPI already stripped); (3) worst-case lock-density rule — always-lock vs tint-only vs density-adaptive (boards A/B side-by-side on the Cells page). Then: componentize the utility gutter + `cell/header` `Locked` prop; clean 005 icon board for the dot-vs-icon corner call. Added 2026-07-09.

^pc-15

---

## pc-17

- [ ] **figma-repo-sync-plugin finalization (code-grounded plan, 2026-06-22)..** Gold Figma library is DONE (hand-built via figma-cli); plugin must now *generate* to it, *enforce* it, and *converge* code↔Figma. Full plan + status: `07-projects/09-figma-repo-sync-plugin/next-steps-plan.md`. **Base is now `main`** — `feat/radix-color-system` is SUPERSEDED (the team re-landed radix work onto main via merged consolidate PRs #82/#83/#84; main has plugin @ 11.4.18 + radix tokens + tsconfig/eslint plugin-excludes). Foundational fixes done + rebased onto main: PRs **#116** (transparent token), **#117** (shared-plugin-data, stacked on #116), **#118** (Badge size/shape), **#119** (Alert); **#120 closed** (redundant). Company repo, no self-merge. **Next:** quick wins (ScrollArea placed=0; mode-first header comment) → Type→booleans lever + tokenization sweep + lint gate as ONE componentGenerator.ts pass, all on `main`. **Watch:** `caution` is open team PR **#87 → main** (Alert/Badge caution depends on it); cds→semantic usage migration is incomplete on main (~150 reintroduced refs → follow-up codemod). Biggest lever (narrowed) = Type icon-presence → boolean props on Button/Badge (keep State physical).

^pc-17

---

## pc-18

- [ ] **Publish the centric-ui Figma library.** ("Centric SaaS PLM — Design System", `o6o1ZuGHxDow2vHLuYXT6X`). Substantially reworked 2026-06-22: full typography style system (Body/UI categories + `Typography Roles` + 21 variable-bound styles, ~1,117 nodes remapped); comprehensive token binding across all pages + instances (+ `border-width-3`, line-height & paragraph-spacing tokens); mode-first refactors (Badge Size/Shape, Avatar/Badge Status); focus states (Sidebar/Tabs/NavMenu); Form Field boolean toggles + 14 instance rewires; all Additions tweaks; `_Slider/Thumb` subcomponent now consumed by the Slider; `_Avatar/Badge` icon → instance-swap; Avatar—Sizes dup-mode fix. **Manual step** (Plugin API can't publish): Figma → Assets panel → Publish, review the change list. Optional polish: relocate `_Slider/Thumb` into the Slider section; resolve the pre-existing `_Calendar/Day`↔`Calendar` 8px overlap (category relayout). New durable rule in knowledge `figma-ds-surface-authoring` (floating elements absolute → never inflate host bbox; migrated 2026-06-30). See session-log 2026-06-22. **Published earlier 2026-07-31; post-publish density/type/color changes now need another publish.** Added `Foundations / Semantics / Density` (modes Normal-default/Compact/Spacious; tokens aliasing Spacing/Radii/Typography) and applied it library-wide. Density and Colors are context axes: **components/subcomponents remain Auto** and inherit from app/chrome, page, feature, or audit shells; collection defaults remain Normal/Light. The initial explicit-Normal stamp was fully cleared and verified (zero context overrides remain). Also deleted redundant `Typography Roles`, rebound all 21 styles directly to semantics then to the full density type ladder, normalized component/semantic names, removed/cataloged CDS colors, and added `Calendar / Radii` + `Sidebar / Surface`. Technique captured in knowledge `centric-plm-design-system` and `figma-component-token-axes`. See session fragment `2026-07-31-work-figma-density`.

^pc-18

---

## pc-20

- [ ] **Install the `snds@snds-local` skill plugin on other machines..** Built 2026-06-02 on Work MBP (main). Exposes 18 curated `03-skills/` hubs as native `/snds:<name>` slash commands. Per machine: run `python3 08-tools/build-local-skill-plugin.py`, then `claude plugin marketplace add ~/.claude/local-plugins/snds-local` + `claude plugin install snds@snds-local`, then restart. (Plugin lives in `~/.claude`, not Drive-synced — only the generator script syncs.)

^pc-20

---

## pc-21

- [ ] **Refresh `05-artifacts/active/trigger-cheatsheet_v1.0_2026-06-01.html` to v1.1..** Flip `/ds`, `/figma`, `/motion`, `/type`, `/redesign` from "planned" → "live" (all built and observed on disk 2026-06-04 — six-hub set complete). Keep `/redesign`'s external-bridge tag. The full six-hub `/qa /ds /figma /motion /type /redesign` operation-grammar set is now live; cheatsheet is the public-facing reference.

^pc-21

---

## pc-22

- [ ] **Add `design-system-ops` to the semantic-overlap reconciliation..** Plugin observed active 2026-06-04 with 38 invocable commands (token-audit, drift-detection, component-audit, deprecation-process, governance-encoder, visual-report, etc.). Heavy semantic overlap with `/ds` + `ds-advisor` + `design-engineer` — fold into the description-contract pass (was 8–10 overlap zones; now ~9–11). Likely `/ds` (hub) routes TO design-system-ops commands (granular ops). Decide canonical owner per concern.

^pc-22

---

## pc-23

- [ ] **Document the now-complete six-hub operation-grammar surface..** Update `06-context/artifact-registry.md` (already done in this session's HEAD content) + decide whether workspace `CLAUDE.md` or the dispatcher needs a pointer. Six hubs: `/qa` JUDGES · `/ds` DECIDES · `design-engineer` / `/figma` AUTHOR · `/motion` IMPLEMENTS · `/redesign` CREATES. Next-step: test-drive against the Davinci Storybook QA audit (`/qa audit apps/docs --theme light --theme dark → /qa triage`) — validates the hubs on real work and closes the founding ask.

^pc-23

---

## pc-25

- [ ] **Act on Opus 4.7+ skill audit findings..** Report at `05-artifacts/active/skill-network-audit_opus-4.7_2026-04-21.md`. Five prioritized findings; the highest-leverage is extracting ~200 lines of design theory from `ds-advisor` and routing it to the Aesthetic Lens + Last-Mile Craft frameworks, plus resolving `ds-advisor` / `design-engineer` trigger overlap.

^pc-25

---

## pc-27

- [ ] **Data table cell anatomy + state matrix..** Text and numeric cell types first. Part of the PLM data table documentation project (90 tables audited). **Major progress 2026-07-07→09** (drag-to-fill/fill-range system, Align + Validation physical axes, header v2, DataTable keyboard docs, dense 24px study) — live state + node ids: `07-projects/02-centricPLM/context/cell-indicators-pilot.md`; interactive artifact (plan/matrix/playground) linked therein.

^pc-27

---

## pc-28

- [ ] **C8 cell system — rollout decisions for Sean (added 2026-07-09):.** CVD redundancy option (A leading glyph / B dashed warning border / C trailing glyph); entry-error border weight parity (1px vs 2px); Error+Focus severity-over-focus (003 ask); then scripted Validation-axis rollout (~25 sets, +~520 variants; refmap hits 105 — prune?); Cell Value modes verdict; afterwards Invalid-boolean instance migration + Cell Validation collection deprecation. Decision points staged in the artifact's plan view.

^pc-28

---

## pc-29

- [ ] **C8 cell system — follow-up builds (added 2026-07-09):.** re-run c8 legacy-indicator asset extraction (background agent lost at process exit) → before/after indicator boards per cell type; dense-24px 003 asks (TF wrapper structural trim, small checkbox box, Small chips + single-row truncation; 24 vs 26/28 pending team); map raw validation surfaces to CDS-WIP `interface/status/*` tokens when adopted.

^pc-29

---

## pc-34

- [ ] **Wire up production deployment for ds-docs..** Vercel suggested (Next.js auto-detect); set `NEXT_PUBLIC_STORYBOOK_URL` to the deployed Storybook URL so embeds work in prod. Also swap the 28 hardcoded `localhost:6006` Storybook links that [ds-docs#3](https://github.com/cpes-software/ds-docs/pull/3) ships (PageHero chips + home page) once the URL exists. Added 2026-07-07.

^pc-34

---

## pc-35

- [ ] **Section D — reference design-system deep reads..** Atlassian, Carbon, Salesforce Lightning, Workday Canvas, Adobe Spectrum, Polaris, Primer, Fluent 2. **Pre-step:** enumerate available MCPs / plugins / skills per DS before WebFetch fallback. **Priority targets** for closing the A18 task-center / queued-jobs-list gap not surfaced by Mobbin: GitHub Primer (Actions runs), Vercel (Deployments), Stripe (Export queue). Synthesis doc has the full pre-step enumeration plan.

^pc-35

---

## pc-39

- [ ] **Re-privatize the workspace-repo author email..** During the 2026-06-04 reconcile push, GitHub blocked the push because Personal MBP commits use `hello@snds.design` in plaintext metadata. Worked around by flipping the GitHub "Block command line pushes that expose my email" toggle OFF — Sean wants this re-enabled later. Long-term fix: set repo-local `user.email` on Personal MBP (and Windows) to `570874+snds@users.noreply.github.com` (the form Work MBP already uses), and migrate the deployed identity convention into `00-bootstrap/setup/gitconfig.personal.template` so it propagates per-machine. Auth scoping rule: **superseded on the Centric laptop as of 2026-07-20** — see memory [[feedback-credential-scoping]]. The old formulation ("Centric repos → Centric auth; ANY personal/workspace surface → personal `snds` auth, all devices") now holds only on non-Centric machines. On `CS-K746DRWXY1` every repo action uses the Centric account, *including* commits to `snds/workspace` (the Centric account is a contributor there). This pending item's remaining scope is therefore Personal MBP + Windows only.

^pc-39
