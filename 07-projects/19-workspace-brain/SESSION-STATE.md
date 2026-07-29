# SESSION-STATE — Workspace Brain

_Last updated: 2026-07-29 — Open Agent Engine: stage-2 identity verification PASSED (no writes); boards not yet provisioned_

---

## Current state (rewritten atomically — no stale fields)

### 🤝 Live handoff (the baton — any agent reads this FIRST, updates it on every handoff)

- **Current focus**: **Open Agent Engine** — a work-movement layer (queue / claim lock / status ledger / receipts) on Linear, adapted from Nate B. Jones' Open Engine. Workspace side is COMPLETE and validated. Paused mid-build at the session boundary.
- **Working set** (uncommitted, 10 changes): `03-skills/open-agent-engine/SKILL.md` (new) · `00-bootstrap/doctor/linear-lanes.py` (new, untracked) · `06-context/open-engine/{README,personal}.md` (new) · `07-projects/02-centricPLM/open-engine.local.md` (new, **gitignored by design**) · edits to `02-shared-references/capability-registry.md`, `03-skills/workspace-bootstrap/SKILL.md`, `09-tools/build-local-skill-plugin.py`, `_SKILLS.md`, `.claude/hooks/dispatcher.py`.
- **Last action**: **Both lanes live; all four smoke tests run; three passed and one is deliberately parked.** Stage 2 passed on both (account + distinctness proved read-only; workspace slug proved by the first-write gate on each lane, since no Linear MCP read exposes an org slug). Boards built on both: project, `agent-instructions` label, ledger + first `AGENT STATUS`. Sean created the six statuses by hand on both. Results: **test 1 hello-world PASSED** (`personal:SEA-5`) · **test 3 human-hold PASSED** (`personal:SEA-8`, answered in the agent thread) · **test 4 substance refusal PASSED** (`c8:SEA-5` — refused, held, zero paraphrase written) · **test 2 blocked-resume MID-FLIGHT** (`personal:SEA-7`, deliberately left blocked). By Claude Opus 5 · Claude Code (VS Code extension) · Work MacBook Pro.
- **Next action**: three things, none blocking each other. (1) **`personal:SEA-7`** needs Sean to comment *on the issue* (`manual only` / `scheduled`) — it is NOT to be closed from a chat answer, because where the answer arrives is the thing the test measures. (2) **`c8:SEA-5`** is held awaiting a venue decision (pointer-only / write it in the owning repo / close). (3) **Commit the working set** — blocked on the Bash tool, see below. Then optionally: stand up the scheduled runner (now authorized), and turn off Linear's auto-close-stale-issues (6mo → Canceled) which would eventually cancel a dormant ledger.
- **Open decisions**: unattended scheduled runs **AUTHORIZED** by Sean 2026-07-29 for both lanes, granted via the `SEA-8` human hold. Relaxes nothing else — profile, ask-first list, and one-issue-per-run all still hold. No scheduled runner exists yet.
- **Blocked on**: **the Bash tool is failing** — `EACCES: permission denied, mkdir '/private/tmp/claude-502/.../tasks'`. This blocks git (commit/push), the five validators, and `linear-lanes.py`. Validators were all green at their last run, *before* the final round of lane-config edits; those edits touch only `06-context/` and a gitignored file, so no registry rebuild is owed — but **re-run the five validators before committing**. Fix: restart the session, or repair permissions on that scratch dir.
- **In-flight / do-not-touch**: the uncommitted working set (11 entries at last check, plus later edits to `06-context/open-engine/personal.md`). Do **not** `git add` the c8 lane config; it is gitignored deliberately (verify with `git check-ignore -q 07-projects/02-centricPLM/open-engine.local.md`).
- **⚠️ Cross-lane hazard**: both lanes' teams are keyed `SEA`, so **issue ids are not unique across lanes** — `SEA-5` is hello-world on `personal` and the substance-refusal test on `c8`. Always qualify ids with the lane outside the tracker (`personal:SEA-5`, `c8:SEA-5`). Recorded in both lane configs; **still owed a line in the skill** (deferred only because editing `SKILL.md` requires a registry rebuild, which needs Bash).
- **Agent thread**: `Claude Opus 5 / Claude Code (VS Code) / Work MBP (2026-07-29): both lanes provisioned + verified, 3 of 4 smoke tests passed; next = SEA-7 answer on-issue, c8:SEA-5 venue call, commit once Bash is back`.

### Environment
- **Context profile**: `personal-solo` for the workspace itself. The engine's `c8` lane declares `centric-engineering` and is **movement-only** — pointers, status, receipts; never substance.
- **Machine**: `CS-K746DRWXY1` (Work MacBook Pro, main)
- **OS context**: macOS (Darwin 25.5.0)
- **Workspace root**: `/Users/sean.sands/Projects/Workspace`
- **Project root**: `/Users/sean.sands/Projects/Workspace/07-projects/19-workspace-brain`

### VCS state
- **Branch**: `main` @ `c775341`
- **Uncommitted changes**: 10 (see Working set). Nothing committed this session.
- **Test state at last check**: all four validators green (`validate-integrity` 617 files / `validate-links` 253 skills / `validate-capabilities` 7 caps, 13 requirements / `validate-workspace`). `dispatcher.py` and `linear-lanes.py` both compile. Detector negative test passed (planted an unexpected employer lane on a personal-machine evaluation → reported `unexpected`, exit 1, fixture removed).

### Open work and paused threads
- **Currently in progress**: Open Agent Engine — workspace side done, Linear side not started.
- **Remaining `PENDING` fields** (all require a live Linear connection): `personal` — team, project, ledger issue id, optional-skill directory id. `c8` — same four.
- **Pending questions**: none.
- **Blocked on**: nothing post-restart.
- **What's needed to resume**: read `03-skills/open-agent-engine/SKILL.md` → "Preflight", then `06-context/open-engine/README.md` (lane index + canonical machine→lane manifest), then each lane config. Run `python3 00-bootstrap/doctor/linear-lanes.py` for live stage-1 state. The personal lane's target workspace is declared in its own tracked config; **the c8 lane's target is declared only in its machine-local config** — deliberately not repeated in tracked files, which is the movement-only rule applied to our own artifacts.

---

## Session history (append-only)

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
- Unrelated but queued from the site review: trim the ~21.6k-token session-start footprint (`project-context.md` line 19 alone is ~1,490 tokens inside a head-60 read), add negative fixtures to the five validators, and fold the seven-surface maintenance loop into `/optimize`.

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
