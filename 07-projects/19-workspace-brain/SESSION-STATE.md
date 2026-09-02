# SESSION-STATE — Workspace Brain

_Last updated: 2026-09-02 — session-end: Open Engine enroll, visual-qa prove, branch prune_

---

## Current state (rewritten atomically — no stale fields)

### 🤝 Live handoff (the baton — any agent reads this FIRST, updates it on every handoff)

- **TL;DR (for future agent)**: Open Engine personal lane is `ok` on this Cursor (`linear-personal` → `hello@snds.design` / `linear.app/snds`). Visual-qa prove path ran: `vqa calibrate` 48/48 (`vqa/1.1`); relative `--output` double-join fixed (`7a40df5`); LCARS S-SYS47-01 v4 16/16 measured with 4 named uncued residuals. Merged leftover branches pruned on personal `snds/*` clones. Legion Continuum remains `snds/legion` `064e363`. Do not register `linear-c8` here.
- **Current focus**: Session closing. No substantive Legion work this thread.
- **Working set**: [[open-agent-engine]]; [[visual-prove-engine]]; [[dc-visual-qa.yaml]].
- **Last action (2026-09-02):** Session-end after Open Engine enroll + vqa prove + branch prune. Cursor Grok 4.6 / Cursor / Personal MBP.
- **Unattended runner — hard gate exists; no timer.** Still authorized-but-unbuilt.
- **Next action:** Pick new work. Optional: Davinci leftover unique branches; Legion `feat/scale-unification`.
- **Open decisions:** Product/data/security constitutions still `mapped` only. YAML still hand-authored.
- **Blocked on:** Machine-local homes for `^pc-07` / `^pc-11`; lane ambiguity on `^pc-30` / `^pc-41`.
- **In-flight / do-not-touch:** do **not** `git add` the c8 lane config. **Do not delete anchored `^pc-NN` stubs.** Copilot pack is tracked (`copilot/` + relative `.claude` wrappers); do not convert wrappers back to absolute paths.
- **Agent thread**: `… → (2026-09-02): Legion Continuum + PR #17 + copilot skip` → `(2026-09-02): Open Engine enroll + visual-qa prove + branch prune`.

### Environment
- **Context profile**: `personal-solo` for the workspace itself. The engine's `c8` lane declares `centric-engineering` and is **movement-only** — pointers, status, receipts; never substance.
- **Machine**: Personal MacBook Pro (`Voyager-2.local`) this session; Work MBP remains the other primary.
- **OS context**: macOS (Darwin 25.5.0)
- **Workspace root**: resolve via nearest `AGENTS.md` (this checkout)
- **Project root**: `07-projects/19-workspace-brain`

### VCS state
- **Branch**: `main` @ session-end commit (this fragment)
- **Uncommitted at baton write**: session fragment + this baton only
- **Test state at last check (2026-09-02):** `vqa doctor` core ok; FLIP/DreamSim/OCR/gltf-validator/VGGT degraded honestly. `vqa calibrate` **48/48** (`vqa/1.1`). LCARS `S-SYS47-01` v4 `vqa prove` 16/16 measured. Doctor personal lane `ok` on this Cursor.

### Open work and paused threads
- **Currently in progress**: error-correction items 1–5 landed; watch for skip-after-close.
- **Paused (unchanged)**: Open Agent Engine ritual integration still wants an ordinary-session proof; dense Layer-2 retrieval stays deferred ([[decision-defer-dense-vault-retrieval]]).
- **The engine's next real test is its first ordinary session** — does the session-start line appear only when it should, and does `/session-end` file residue pointer-shaped rather than pasting prose into issues? Neither has run outside the session that built them.
- **The migration Sean deferred**: `project-context.md` carries **43 open items** (38 "Active"), some stamped as far back as early July and others un-stamped and older. That list is the queue this engine was built to replace, and moving it is the point at which the engine stops being scaffolding. Deliberately deferred until the ritual integration has proven itself over a week of real sessions. Not a bulk copy — most items _are_ substance, so each needs a pointer-shaped home first. Side benefit when it happens: it also fixes the ~21.6k-token session-start footprint already queued below.
- **Remaining `PENDING` fields**: none. Both lane configs fully provisioned.
- **Pending questions**: none.
- **Blocked on**: nothing for the error-correction P-items. Open Engine itself is unblocked.
- **Sean-side follow-ups** (not blocking): disable Linear auto-close-stale-issues on both workspaces; optionally build the lane-scoped scheduled runner.
- **Queued from the site review** (separate from Open Engine): trim the ~21.6k-token session-start footprint (`project-context.md` line 19 alone is ~1,490 tokens inside a head-60 read). Negative fixtures and `/optimize` seven-surface loop landed 2026-08-26.
- **What's needed to resume**: error-correction → read `notes/error-correction-research_2026-08-26.md` + the knowledge entry. Engine → `03-skills/open-agent-engine/SKILL.md` Preflight, then `06-context/open-engine/README.md`. Run `python3 00-bootstrap/doctor/linear-lanes.py` for live lane state.

---

## Session history (append-only)

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
