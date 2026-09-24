# SESSION-STATE — Workspace Brain

_Last updated: 2026-09-23 — Zero-Vector wave 0 published; D5, F-14 and D6 landed; CI fix committed; cds #50 still waiting on Sean_

---

## Current state (rewritten atomically — no stale fields)

### 🤝 Live handoff (the baton — any agent reads this FIRST, updates it on every handoff)

- **Current focus**: cds [#50](https://github.com/cpes-software/cds/pull/50) on `feat/instance-0-thin-child-lockstep` @ `a346322`. CodeQL and CI green. Waiting on Sean to review.
- **Parallel thread (2026-09-22): Zero-Vector harness plan v1.1, WAVE 0 APPROVED (LLM-inclusive caveat).**
  - Plan: `notes/zero-vector-harness-plan_2026-09-22.md` (v1.1 summary). Full v1.1 detail and surface research are held locally at `.claude/state/held/` (Work MBP; not committed while the vault is public, ^pc-47).
  - Decisions are recorded in [[decision-llm-inclusive-harness]], [[decision-project-intent-in-repo]] and [[feedback-credential-scoping]].
  - **Wave 0 status (2026-09-23): published.** Waves A and B reached `main` at `ec77eda`. Sean then fast-forwarded `main` to the verified fix round (head `7fefad5`) and pushed it. That round holds 23 fixes, including the walls F-01/F-02 blockers, plus the harness environment notes.
  - **Verification at `bd8274d`:** harness 35/36 gates with the real git; the 36th (profile_resolve) is 340/340 outside the sandbox. Under Claude Code's Bash sandbox, 3 gates go red for environmental reasons (xcrun cache, `ps` denied); the harness now prints an environment note naming them.
  - **Done after publish (2026-09-23):** D5 landed in `6d30676` (exact, case-insensitive domain match; 351/351 resolver checks outside the sandbox; three reviewers found no defects). Decisions recorded here, in ^pc-45, the plan note, `surfaces.json` and the held spec. The ten merged intent worktrees were removed; their branches stay. The T10/T11 findings register is saved in held (`wave0-verification/`).
  - **F-14 and D6 landed (2026-09-23).** Gap detail follows repo visibility ([[decision-public-residual-detail]]). The public identity row states ten gaps at class level (H17-R1 to H17-R10) plus WALL-C1; the recipes and machine posture are in held (`h17-residual-register_2026-09-23.md`, `machine-posture_2026-09-23.md`). Four review rounds found new bypass shapes each time, so H17-R10 is an umbrella: the local layers are seatbelts against ordinary pushes, and the barriers are server-side protection and review. The classifier now labels single overlay-entry overrides, the `+=` form, `--no-verify` abbreviations and include/alias keys; the doctor's check mode audits URL rewrites (report-only). CI fix for the two red gates is in `6c5a909`.
  - **Next action (agent):** after the push, confirm CI is green on `main`. Then rerun the three-lens verification on current `main` (the walls lens asked for it before the v5 overlay install), fix anything it finds, run verify, and tick the machine gates.
  - **Human steps later (words only until ready):** pin install, per-surface probes (Claude Code, Cursor, Codex, VS Code), Personal MBP identity checks, v5 overlay install, one vetted prune with the sandbox off. The Cursor card on this Mac needs the Cursor shim reinstalled to get `--family cursor`; the G3b `--install-shims` run does that (L-12).
  - **Sean's decisions (2026-09-23):** walls F-11: the heal path gets pinned in wave 1, and until then it is a declared residual. Tests F-07: the floor keeps blocking the vetted employer prune when `ps` is denied; that one command runs with the sandbox off. D5: the employer email domain is `centricsoftware.com`; Sean will say if the employer changes. D7: the three H25 items move to wave 1 with H23, H4 and H15. Walls F-14: gap detail follows the repo's visibility; in this public vault a gap is written at class level with a stable ID, and the recipe and machine posture stay held ([[decision-public-residual-detail]]). D6: approved; `00-context-profiles.md` says "cited by the agent". The work email address in three tracked files is handled with wave 1 (H25 scrub, ^pc-47).
  - **Claude sessions must not open employer repos.** Employer mapping and recon run in Cursor/Codex.
- **Working set**: `/Users/sean.sands/Projects/cpes-software/cds`. Do not edit cds from a centric-ui-rooted chat.
- **Last action (2026-09-21):** Alex rejected the peer explanation on centric-ui [#413](https://github.com/cpes-software/centric-ui/pull/413). Removed `input-otp` and `react-day-picker` from the host (`022c468`) and replied on both threads. npm still installs them as required peers of `@centric/ui`; hiding that install is a CDS change, not started. Cursor Grok 4.7 · Cursor · Work MBP. cds #50 remains green at `a346322`.
- **Unattended runner — decided 2026-09-15: not building it.** Not a pending task. The safety gate
  (`check-unattended-runner-gate.py`) stays and is silent when idle. See [[decision-no-unattended-runner]].
- **Next action:** Sean reviews cds #50. Alex has the correction on cui #413 (`022c468`). Do not agent-merge. Do not bump a host `cds.pin`. Do not re-add widget libraries to the host to silence an unmet peer.
- **Open decisions:** Theme reset stays a later product-CSS PR. Restyle/arbitrary/inline shadcn rules stay off until a later wave. Proto #84 and cui #398 were last noted 2026-09-18 as human-merge; not re-checked this session.
- **Blocked on:** Sean review of cds #50. For the ZV plan: nothing blocks the agent steps. Sean decided the last three items on 2026-09-23: the loaner is retired from `devices.json` (D9), probe records are public evidence under F-14 exception 1, and no per-use approval on the employer credential (H17-R10). CI is green on `e360aa3`. The human steps above wait on the re-verification.
- **In-flight / do-not-touch:** do **not** `git add` the c8 lane config. **Do not delete anchored `^pc-NN` stubs** from `project-context.md`. Do not auto-commit or merge employer repos. Do not commit the untracked `canvases/` in the cds checkout. Do not bump cui `cds.pin`.
- **Agent thread**: `… → Cursor Grok 4.7 / Cursor / Work MBP (2026-09-21): cds #50 CodeQL green → Cursor Grok 4.7 / Cursor / Work MBP (2026-09-21): cui #413 peer replies → Cursor Grok 4.7 / Cursor / Work MBP (2026-09-21): cui #413 drop widget deps → Claude Opus 5.5 / Claude Code / Work MBP (2026-09-22): Zero-Vector research + harness plan + X1 heal → Claude Opus 5.5 / Claude Code / Work MBP (2026-09-23): wave 0 A+B, fix round, harness environment notes → Claude Opus 5.5 / Claude Code / Work MBP (2026-09-23): D5, decisions recorded, worktrees removed → Claude Opus 5.5 / Claude Code / Work MBP (2026-09-23): F-14 and D6 applied, uncommitted`.

### Environment
- **Context profile**: `personal-solo` for the workspace itself. The engine's `c8` lane declares `centric-engineering` and is **movement-only** — pointers, status, receipts; never substance.
- **Machine**: Work MacBook Pro (`CS-K746DRWXY1`) this session; Personal MBP remains the other primary.
- **OS context**: macOS (Darwin 27.0.0)
- **Workspace root**: resolve via nearest `AGENTS.md` (this checkout)
- **Project root**: `07-projects/19-workspace-brain`

### VCS state
- **Branch**: `main` plus this session-end commit
- **Uncommitted at baton write**: session fragment + this SESSION-STATE rewrite (folded into session-log at end)
- **Test state at last check (2026-09-02):** `vqa doctor` core ok; FLIP/DreamSim/OCR/gltf-validator/VGGT degraded honestly. `vqa calibrate` **48/48** (`vqa/1.1`). LCARS `S-SYS47-01` v4 `vqa prove` 16/16 measured. Doctor personal lane `ok` on this Cursor.

### Open work and paused threads
- **Currently in progress**: error-correction items 1–5 landed; watch for skip-after-close.
- **Paused (unchanged)**: Open Agent Engine ritual integration still wants an ordinary-session proof; dense Layer-2 retrieval stays deferred ([[decision-defer-dense-vault-retrieval]]).
- **The engine passed its first real verification (2026-09-15).** A label-filtered `list_issues` on the personal lane returned 30 issues; all **23** anchor→issue mappings in `open-engine/personal.md` resolve — **zero orphaned pointers**. The other 7 are engine infra (`SEA-5`/`6`/`7`/`8`) plus three created after the migration. Remaining untested: whether `/session-end` files residue pointer-shaped rather than pasting prose.
- **The migration is DONE — this entry was stale (corrected 2026-09-15).** It happened 2026-07-30 (43 anchored items, 38 with issues across both lanes; personal lane 23, c8 15 machine-local) and the substance graduated to `project-context-detail.md` 2026-08-07. `project-context.md` is now **93 lines / 12.4 KB**, already pointer-shaped, and costs **560 tokens** at session start (head-30) — not the ~61 KB this entry implied. The five unmigrated items are refusals on purpose, not backlog: three are `c8` with no valid pointer, two are lane-ambiguous, and guessing a lane on a movement-only boundary is the one thing the skill forbids. The 21.6k session-start footprint was fixed separately by C2 (`artifact-find.py`), not by this.
- **Remaining `PENDING` fields**: none. Both lane configs fully provisioned.
- **Pending questions**: none.
- **Blocked on**: nothing for the error-correction P-items. Open Engine itself is unblocked.
- **Sean-side follow-ups** (not blocking): disable Linear auto-close-stale-issues on both workspaces; optionally build the lane-scoped scheduled runner.
- **Queued from the site review** (separate from Open Engine): trim the ~21.6k-token session-start footprint (`project-context.md` line 19 alone is ~1,490 tokens inside a head-60 read). Negative fixtures and `/optimize` seven-surface loop landed 2026-08-26.
- **What's needed to resume**: error-correction → read `notes/error-correction-research_2026-08-26.md` + the knowledge entry. Engine → `03-skills/open-agent-engine/SKILL.md` Preflight, then `06-context/open-engine/README.md`. Run `python3 00-bootstrap/doctor/linear-lanes.py` for live lane state.

---

## Session history (append-only)

### 2026-09-21 — cui #413 drop widget deps

**Focus this session**: Take Alex's encapsulation note on centric-ui #413 and correct the host.
**Machine**: Work MacBook Pro (`CS-K746DRWXY1`) · Cursor Grok 4.7 · Cursor
**Stopped because**: correction pushed and replied; session still open.

**Accomplishments**:
- Removed `input-otp` and `react-day-picker` in `022c468`; replied on both threads
- Encoded the boundary in the workspace (foundations, #14, #18, ds-advisor, fe-component-architecture, knowledge)

**Next**: Sean reviews cds #50. CDS-side peer hide is not started. Do not bump `cds.pin`.

### 2026-09-21 — cui #413 peer replies

**Focus this session**: Answer Alex on centric-ui #413 about `input-otp` and `react-day-picker`.
**Machine**: Work MacBook Pro (`CS-K746DRWXY1`) · Cursor Grok 4.7 · Cursor
**Stopped because**: Sean asked to end session.

**Accomplishments**:
- Replies posted on [#413](https://github.com/cpes-software/centric-ui/pull/413) discussion threads

**Next**: Sean reviews cds #50. Do not agent-merge.

### 2026-09-21 — cds #50 CodeQL green

**Focus this session**: Clear the remaining CodeQL failure on cds #50.
**Machine**: Work MacBook Pro (`CS-K746DRWXY1`) · Cursor Grok 4.7 · Cursor
**Stopped because**: Sean asked to end session.

**Accomplishments**:
- Linear CSS scans pushed as `a346322` on `feat/instance-0-thin-child-lockstep`
- CodeQL and CI green on [#50](https://github.com/cpes-software/cds/pull/50)

**Next**: Sean reviews #50. Do not agent-merge.

### 2026-09-18 — CDS ShadCN federalization instance 0 (local)

**Focus this session**: Federalize CDS on bumpable ShadCN; keep local; resume in CDS-rooted chat.
**Machine**: Work MacBook Pro (`CS-K746DRWXY1`) · Cursor Grok 4.6 · Cursor
**Stopped because**: Sean asked to end session.

**Accomplishments**:
- Local wrap merge on cds `feat/shadcn-federalization` @ `5b21ec9` (10 ahead of origin)
- Stock L0 + extras + ShadCN stories: Button, Input, Badge
- Remaining modules thin-wrapped (CDS-as-L0, not stock yet)
- Resumption prompt for a CDS-folder chat

**Next**: Open Cursor on `/Users/sean.sands/Projects/cpes-software/cds`. Restore stock per remaining module. No push until review.

### 2026-09-17 — Phosphor consume (cds #46 / proto #84)

**Focus this session**: Dual-set Icon on cds, then proto consume + lint-ds CI.
**Machine**: Work MacBook Pro (`CS-K746DRWXY1`) · Cursor Grok 4.6 · Cursor
**Stopped because**: Sean asked to end session.

**Accomplishments**:
- cds #46 on `main` (Phosphor renderer + `IconSetProvider`)
- proto #84 merge-ready: header toggle, Vite 8 CSR resolve, semantic tokens for lint-ds
- Harvested later-breakers into [[cds-host-consume-order]]

**Next**: Sean merge proto #84 if wanted. Do not agent-merge.

### 2026-09-17 — late close: cui PR 312 quality gate

**Focus this session**: Close an Aug 18 thread on cui #312 Quality gate (knip unused optional peer).
**Machine**: Work MacBook Pro (`CS-K746DRWXY1`) · Cursor Grok 4.6 · Cursor
**Stopped because**: Sean asked to end session.

**Accomplishments**:
- Confirmed knip `unused` was a real fail (`@xyflow/react` optional + FlowCanvas import)
- Read-back: #312 MERGED 2026-08-18 with Quality gate still red

**Next**: None. Live handoff current focus stays lint:ds / cui #398.

### 2026-09-17 — leftover cds consume closed (#77 / #78)

**Focus this session**: Close the Sep 11 leftover consume thread after cds #35 and proto #78 merged.
**Machine**: Work MacBook Pro (`CS-K746DRWXY1`) · Cursor Grok 4.6 · Cursor
**Stopped because**: Sean asked to end session.

**Accomplishments**:
- Proto #77 host chrome + #78 leftover consume on `main` (`adac92b`)
- `cds-exports-check` gates `@centric/ui/<subpath>` against cds `origin/main`
- Workspace [[plan-ahead]] + [[cds-host-consume-order]] already on vault `main`

**Next**: centric-ui host-chrome consume only if named. Live handoff current focus stays lint:ds / cui #398.

### 2026-09-15 — portable session-status card closed; doctor MISSes acked

**Focus this session**: Close the leftover 2026-09-11 Cursor thread; ack bootstrap MISSes.
**Machine**: Work MacBook Pro (`CS-K746DRWXY1`) · Cursor Grok 4.6 · Cursor
**Stopped because**: Sean asked to acknowledge the misses and end session.

**Accomplishments**:
- Portable boot card shipped earlier as `46d207a` (`session-status.py` + Cursor `sessionStart` hook)
- `workspace-doctor.sh --ack` on this machine; session-status notices = 0
- Layer 0 `make sure` is not produce

**Next**: New Cursor session on this machine should show 0 MISS notices. Live handoff current focus stays with later 2026-09-15 work (cui #398 / lint:ds).

### 2026-09-15 — vault CI green after Layer-0 brain-root fix (session-end)

**Focus this session**: Confirm workspace CI; session-end after canonical-docs housekeeping + Actions trajectory self-test fix.
**Machine**: Work MacBook Pro (`CS-K746DRWXY1`) · Cursor Grok 4.6 · Cursor
**Stopped because**: Sean asked to end session.

**Accomplishments**:
- Housekeeping `c69baef` (canonical-docs-voice title-description + YAML block-list triggers)
- Layer-0 handback routes no longer name gitignored inbox (`2214bbd`)
- `resolve_brain_root` uses CLAUDE_PROJECT_DIR + cwd (`9178aaf`); workspace-integrity green

**Next**: Human review of cui #398; after merge remove `centric-ui-lint-ds`.

### 2026-09-03 — ATSMATRIX GitHub org review (session-end)

**Focus this session**: Assess anyel1to/ATSMATRIX public repos for workspace usefulness.
**Machine**: Personal MacBook Pro (`Voyager-2.local`) · Cursor Grok 4.6 · Cursor
**Stopped because**: Sean agreed skip and asked to end session.

**Accomplishments**:
- Read all 11 public repo trees plus implementation (not README-only)
- Verdict: none useful to adopt; RING doc is the only writing worth a glance
- No clone, skill, knowledge entry, or Open Engine issue

**Next**: LCARS live-primitive visual review in a separate session.

### 2026-09-02 — Open Engine enroll + visual-qa prove + branch prune (session-end)

**Focus this session**: Fix Open Engine on this Cursor; load matching domain pack; prove path not Legion work; land vqa relative-output patch; prune merged personal branches.
**Machine**: Personal MacBook Pro (`Voyager-2.local`) · Cursor Grok 4.6 · Cursor
**Stopped because**: Sean asked to end session.

**Accomplishments**:
- Cursor `linear-personal` enrolled; Stage 2 identity matches `snds` / `hello@snds.design`; lane file operational
- `vqa calibrate` 48/48 after relative `--output` fix (`7a40df5`); LCARS v4 16/16 measured
- Merged leftover branches pruned on workspace / davinci / legion / LCARS
- First Cursor ledger heartbeat: `sean-cursor` on `personal:SEA-6`

**Next resumption needs**:
- Pick new work. Optional Davinci unique branches + Legion `feat/scale-unification`

### 2026-09-02 — Legion Continuum + PR #17 + copilot skip (session-end)

**Focus this session**: Land remaining Legion Continuum WIP; resolve then merge workspace PR #17; skip vendored Copilot example wikilinks in integrity.
**Machine**: Personal MacBook Pro (`Voyager-2.local`) · Cursor Grok 4.6 · Cursor
**Stopped because**: Sean asked to end session.

**Accomplishments**:
- Legion `064e363` + canvases `4bee94c` on `origin/main`; `refs/` and `.tmp-*` gitignored
- PR #17 merged (`9221e54`): §8e + QA defaults #6 and #7
- Integrity `copilot/` skip (`b62058d`); vault notes still gated

**Next resumption needs**:
- Open Engine personal lane still not-registered on this machine
- Domain pack / `ds-source-watch --fetch` / `vqa prove` when Sean wants real work

### 2026-09-02 — session-end

**Focus this session**: Close the prove-engine merge thread; persist DSDS constitution + ds-source-watch.
**Machine**: Personal MacBook Pro (`Voyager-2.local`) · Cursor Grok 4.6 · Cursor
**Stopped because**: Sean asked to end session.

**Accomplishments**:
- Prove-engine vqa/1.1 + play-prove + LCARS residuals merged to origin/main (`0f4228a`)
- DSDS constitution + idempotent method decisions + source-watch skill/script persisted
- Looney Tunes 2026-08-26 fragment folded into session-log

**Next resumption needs**:
- `python3 09-tools/ds-source-watch.py --fetch` when Sean wants the first snapshot judged

### 2026-08-28 — checkpoint (prove engine vqa/1.1)

**Focus this session**: Course corrections 1–12 from perception-critique-stack; `/optimize`; commit and merge.
**Machine**: Personal MacBook Pro (`Voyager-2.local`) · Cursor Grok 4.6 · Cursor
**Stopped because**: merge landed; session-end deferred to 2026-09-02.

**Accomplishments**:
- Prove engine altitudes A–G, FLIP, fail-closed mesh/geometry, play-prove, named uncued residuals
- Calibrate 48/48; merge commit `0f4228a` on `main`

**Next resumption needs**:
- Visual work uses `vqa prove`; LCARS residuals still unmeasured

### 2026-08-26 — checkpoint (error-correction items 1–5)

**Focus this session**: Land honesty-check, embedded prove/validate, negative fixtures, observable routing skips, and `/optimize` as system ECC.
**Machine**: Personal MacBook Pro (`Voyager-2.local`) · Cursor Grok 4.6 · Cursor
**Stopped because**: items 1–5 implemented; next is ordinary-work watch, not more protocol.

**Accomplishments**:
- #06 detector check + report Detector line; 00-README compressed gate list
- Literal prove embedded in `visual-reference-replication` + `lead-visual-qa`; vault writes embed validators in AGENTS/#08
- `09-tools/test-validators.py` + CI `validator-fixtures.yml`
- Dispatcher routing-coverage note when Layer 0 under-fires on a real prompt
- `/optimize` Step 1.6 seven-surface maintenance loop

**Next resumption needs**:
- Watch skip-after-close. Commit reliability files separately from LCARS dirt.

### 2026-08-26 — checkpoint (error-correction research)

**Focus this session**: Broad→narrow research on error correction, looping structures, and foundations that reduce unexpected LLM results, mapped onto this workspace.
**Machine**: Personal MacBook Pro (`Voyager-2.local`) · Cursor Grok 4.6 · Cursor
**Stopped because**: dossier landed; next step is Sean's pick, not more survey.

**Accomplishments**:
- Field map by *signal source* (self-critique vs tool/environment vs independent-model vs sampling vs human)
- Honesty bound: surprises cannot be fully removed; they can be detectable, non-silent, non-repeatable
- Workstream detector registry against existing gates
- Durable entry: `08-knowledge/research/agentic-error-correction-foundations.md`

**Next resumption needs**:
- Sean picks from `notes/error-correction-research_2026-08-26.md`

### 2026-08-05 — checkpoint (Layer-1 vault retrieve)

**Focus this session**: Enrich workspace tooling with Layer-1 RAG (lexical FTS) + wire dispatcher fallback.
**Machine**: Personal MacBook Pro (`Voyager-2.local`) · Cursor Grok 4.5 · Cursor
**Stopped because**: Sean ended session after feature commit.

**Accomplishments**:
- `09-tools/vault-retrieve.py` — stdlib FTS5 index/query, graph expand, `--cached` hot path
- Dispatcher: SessionStart rebuild; UserPromptSubmit lexical fallback when Layer 0 < 2 unique targets (cap 2)
- Docs: ontology, vault-graph-conventions, infrastructure, README, CURSOR.md
- Feature committed as `55b9f2a`

**Next resumption needs**:
- Live Claude Code smoke of the fallback; optional golden-set before dense Layer 2

### 2026-07-29 17:05 — checkpoint (Open Agent Engine complete)

**Focus this session**: Close the Open Engine punch list after the boards were built in a parallel session.
**Machine**: Work MacBook Pro (`CS-K746DRWXY1`) · Claude Opus 5 · Claude Code (VS Code extension)
**Stopped because**: work complete; awaiting commit.

**Accomplishments**:
- Verified against Linear (not the baton) that `personal:SEA-7` blocked-resume and `c8:SEA-5` substance-refusal both reached `Agent Done` with clean state histories — **all four smoke tests passed on both lanes.**
- Fixed a detector false positive: `provisioned` matched the bare word `PENDING` anywhere in a lane config, including the config's own status banner, so a fully-provisioned `c8` reported `not-provisioned`. Now matches the backticked field form. Regression-tested by planting a real `` `PENDING` `` field (tripped correctly) and restoring.
- Cleared the stale `PENDING SETUP` banner in the c8 config.
- Added the cross-lane id-collision rule to the skill — the item the previous session deferred when Bash was unavailable.
- Re-ran the full chain: `build-related` → `build-registry` → four validators + `vault-health`. All green.

**Durable lessons (candidates for `08-knowledge/`)**:
- A substring check against prose is not a field check. The detector's own documentation contained the token it was scanning for — self-referential false positive.
- Connection isolation ≠ runner isolation. Per-workspace MCP auth genuinely scopes reads, but user-scope registration binds every session to every lane. Unattended runners need process-level scoping, not just credential scoping.
- Team keys are per-workspace, so issue ids collide across trackers. Any multi-tracker system needs a lane-qualified id convention from day one.

**Next resumption needs**:
- Commit. Then the two Sean-side Linear settings, and the queued site-review items.


### 2026-07-29 08:42 — checkpoint (Open Agent Engine)

**Focus this session**: Review Nate B. Jones' Unlock AI site in full, then adopt Open Engine as a workspace-governed skill with two isolated Linear lanes.
**Machine**: Work MacBook Pro (`CS-K746DRWXY1`) · Claude Opus 5 · Claude Code (VS Code extension)
**Stopped because**: Claude Code restart required — MCP servers bind at session start, and both Linear servers were registered mid-session.

**Accomplishments**:
- Read the full site: 20 guides (incl. the unlisted `/guides/cut-token-waste`), all 41 Open Skills across 8 categories, 10 runbooks, the Open Engine spec, benchmarks, and the Image Arena.
- Authored `open-agent-engine` as a `cross-cutting` skill — procedure only. Lanes, transport contract (MCP → GraphQL → human), six statuses, routing contract, receipts, 10-step queue run, boundaries, failure modes, provenance.
- Established the **procedure / instance-facts split**: the skill holds the method; per-lane configs hold the bindings. Tracked lanes in `06-context/open-engine/`; employer lanes beside their project as `open-engine.local.md`, gitignored. *Governed by the workspace ≠ committed to the workspace.*
- Added the `linear-mcp` capability (`fallback: degrade` — MCP is a preferred transport, not a hard dependency; four operations, three transports, so it is not Claude-specific).
- Built `00-bootstrap/doctor/linear-lanes.py` — deterministic lane preflight (no network, no credentials read). Wired into `dispatcher.py` session-start Notices: 80 ms, silent when healthy.
- Declared machine→lane expectations canonically in the lane index (same fenced-json pattern as `capability-registry.md`); an undeclared hostname is itself a finding.
- Upgraded stage-2 preflight to three checks — workspace, **account**, and **distinctness** — after Sean chose separate identities per lane.

**Decisions**:
- Two Linear lanes, not one shared workspace. Isolation is structural: Linear scopes one MCP connection to one workspace, so per-lane `MCP_REMOTE_CONFIG_DIR` auth contexts make cross-lane reads impossible rather than merely forbidden.
- The `c8` lane is **movement-only** — pointers, status, receipts; never briefs, decisions, diffs, or client detail. A task that cannot be described without substance is a `HUMAN HOLD`, not a paraphrase.
- c8 Linear workspace created under the Centric Google account (2026-07-29). Rationale + accepted consequences in the machine-local c8 config.
- Tracker is a lane-level choice: if Centric never sanctions Linear, the lane repoints at GitHub Issues with one field edit and no skill change.

**Bugs found and fixed (both caught by testing against reality, not assumption)**:
- `validate-integrity` resolves wikilinks against *git-tracked* files, so a brand-new skill is unaddressable until `git add -N`. Applies to every future new skill.
- The detector's auth check missed `mcp-remote`'s nested `mcp-remote-<version>/` store and reported authenticated lanes as `not-authed`. Fixed to recurse and to look for `*_tokens.json` specifically — which yielded a new `auth-incomplete` state (verifier present, no token = an abandoned OAuth flow that looks finished to a human).
- Also noted: `build-related.py` does not propagate reciprocal `## Related` edges into the counterpart file; `validate-links` reads the block, not frontmatter, so the counterpart line must be added by hand.

**Next resumption needs**:
- Stage 2 identity verification **before any write**, then boards, ledgers, and the four smoke tests (hello-world, blocked-resume, human-hold, plus substance-refusal on c8).
- Unrelated but queued from the site review: trim the ~21.6k-token session-start footprint (`project-context.md` line 19 alone is ~1,490 tokens inside a head-60 read). Negative fixtures and `/optimize` seven-surface loop landed 2026-08-26.

### 2026-07-09 16:00 — checkpoint

**Focus this session**: Apply FX-1..FX-14 from the validation report under the fix-session prompt's guardrails.
**Machine**: Personal MacBook Pro
**Stopped because**: (in progress)

**Accomplishments**:
- Phase A: v2 machine layer installed (doctor), Drive-era shims retired, brain-path fixed, memory fact written.
- Phase B: dispatcher tiered emit + audit carrier + SESSION-BLOCK parser + report triggers, evidence green.
- Phase C: 10 triggers narrowed at sources, 4 drifted triggers declared, registry rebuilt, mirror tables reconciled, single-source rule added.
- Phase D: Proofboard amendments, AGENTS.md read-order additions, 3 ontology rows, workspace-work project-home rule, this project scaffolded.

**Next resumption needs**:
- Phases E–F per the fix prompt; then `/session-end` and a validation-harness re-run (pending item).

---

_Seeded by Claude Fable 5 on 2026-07-09 during the fix session (FX-13). Initial state reflects the live fix-session progress._
