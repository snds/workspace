# SESSION-STATE — Workspace Brain

_Last updated: 2026-07-29 17:05 PDT — Open Agent Engine COMPLETE: both lanes live, all four smoke tests passed, validators green_

---

## Current state (rewritten atomically — no stale fields)

### 🤝 Live handoff (the baton — any agent reads this FIRST, updates it on every handoff)

- **Current focus**: **Open Agent Engine — DONE.** Both lanes live and verified, all four smoke tests passed, detector reports `ok` on both, all five validators green. Remaining work is Sean-side Linear settings plus optional extras; nothing is half-built.
- **Working set** (uncommitted, 11 entries): `03-skills/open-agent-engine/SKILL.md` (new) · `00-bootstrap/doctor/linear-lanes.py` (new, untracked) · `06-context/open-engine/{README,personal}.md` (new) · `07-projects/02-centricPLM/open-engine.local.md` (new, **gitignored by design**) · edits to `02-shared-references/capability-registry.md`, `03-skills/workspace-bootstrap/SKILL.md`, `09-tools/build-local-skill-plugin.py`, `_SKILLS.md`, `.claude/hooks/dispatcher.py`, and this file.
- **Last action**: Closed out the punch list — fixed the detector's `PENDING` false positive (it matched the word in prose, including the config's own status banner, so a fully-provisioned `c8` reported `not-provisioned`; now matches the backticked field form only, with a regression test proving a real placeholder still trips it), cleared the stale c8 banner, and added the cross-lane id-collision rule to the skill. Verified via Linear that `personal:SEA-7` and `c8:SEA-5` both reached `Agent Done` — **all four smoke tests passed.** By Claude Opus 5 · Claude Code (VS Code extension) · Work MacBook Pro.
- **Next action**: commit the ritual-integration edits (below). Both earlier Sean-side follow-ups are **closed**: auto-close-stale-issues is OFF on both workspaces (done by Sean), and the scheduled runner is **decided against** — see Open decisions.
- **Open decisions**: none. Two settled 2026-07-29: (1) unattended scheduled runs AUTHORIZED via the `SEA-8` hold, relaxing nothing else — but left **unexercised**; (2) **no timer — the session boundary is the heartbeat.** A scheduled runner was scoped and rejected on three findings: cloud routines cannot reach Linear (no local `~/.mcp-auth`, and Linear is not a connected claude.ai connector); a local runner with full autonomy makes untrusted issue bodies an input to a process holding Bash + git, i.e. a prompt-injection path to a shell, sharpest on the `c8` lane whose board could one day be admin-controlled; and a timer only buys progress-while-absent, which is not how Sean works. Replaced by session-start read (report-only, silent when empty) + session-end filing. Rationale recorded in the personal lane config under "Unattended execution".
- **Blocked on**: nothing. (The Bash-tool `EACCES` failure that blocked the previous session is gone — git, validators, and `linear-lanes.py` all run.)
- **In-flight / do-not-touch**: the uncommitted working set. Do **not** `git add` the c8 lane config; it is gitignored deliberately (`git check-ignore -q 07-projects/02-centricPLM/open-engine.local.md`).
- **⚠️ Cross-lane hazard**: both lanes' teams are keyed `SEA`, so issue ids collide — `SEA-5` is hello-world on `personal` and the substance-refusal test on `c8`. Always qualify outside the tracker (`personal:SEA-5`, `c8:SEA-5`). **Now recorded in the skill** (Lanes → "Issue ids are not unique across lanes") as well as both lane configs.
- **⚠️ Isolation caveat**: connection-level isolation is real (each lane's auth context reaches one workspace only), but **runner-level isolation is not** — both servers are user-scoped, so every session on this machine can write to either. Acceptable with a human watching; **not** acceptable unattended. See the skill → Lanes.
- **Agent thread**: `Claude Opus 5 / Claude Code (VS Code) / Work MBP (2026-07-29): punch list closed, all 4 smoke tests passed, validators green; next = commit`.

### Environment
- **Context profile**: `personal-solo` for the workspace itself. The engine's `c8` lane declares `centric-engineering` and is **movement-only** — pointers, status, receipts; never substance.
- **Machine**: `CS-K746DRWXY1` (Work MacBook Pro, main)
- **OS context**: macOS (Darwin 25.5.0)
- **Workspace root**: `/Users/sean.sands/Projects/Workspace`
- **Project root**: `/Users/sean.sands/Projects/Workspace/07-projects/19-workspace-brain`

### VCS state
- **Branch**: `main` @ `d252cda`, in sync with `origin/main`
- **Committed + pushed 2026-07-29**: `8d42b36` (the engine — skill, lane index, personal config, detector, dispatcher wiring) and `d252cda` (the lane-isolation correction). The c8 lane config was correctly excluded from both — it stays gitignored.
- **Uncommitted**: the ritual-integration edits only — `CLAUDE.md` (engine line in the session-start ritual), `.claude/skills/session-end/SKILL.md` (Step 5.5), `03-skills/open-agent-engine/SKILL.md` (Ritual integration section), `06-context/open-engine/personal.md` (the no-timer decision), plus the regenerated registry and this file.
- **Note for concurrent sessions**: an earlier revision of this block reported 11 uncommitted entries at `c775341` and "nothing committed yet". That was accurate when written and is now superseded — verify against `git log` rather than this block if the two disagree.
- **Test state at last check (2026-07-29 17:05)**: all five green — `validate-integrity` 617 files · `validate-links` 253 skills · `validate-capabilities` 7 caps / 13 requirements · `validate-workspace` · `vault-health` 0 errors across 82 notes. `linear-lanes.py` compiles; both lanes report `ok`, `--check` exits 0.

### Open work and paused threads
- **Currently in progress**: nothing. Open Agent Engine is complete on both the workspace side and the Linear side, and now wired into the session rituals (session-start read, session-end filing).
- **The engine's next real test is its first ordinary session** — does the session-start line appear only when it should, and does `/session-end` file residue pointer-shaped rather than pasting prose into issues? Neither has run outside the session that built them.
- **The migration Sean deferred**: `project-context.md` carries **43 open items** (38 "Active"), some stamped as far back as early July and others un-stamped and older. That list is the queue this engine was built to replace, and moving it is the point at which the engine stops being scaffolding. Deliberately deferred until the ritual integration has proven itself over a week of real sessions. Not a bulk copy — most items _are_ substance, so each needs a pointer-shaped home first. Side benefit when it happens: it also fixes the ~21.6k-token session-start footprint already queued below.
- **Remaining `PENDING` fields**: none. Both lane configs fully provisioned.
- **Pending questions**: none.
- **Blocked on**: nothing.
- **Sean-side follow-ups** (not blocking): disable Linear auto-close-stale-issues on both workspaces; optionally build the lane-scoped scheduled runner.
- **Queued from the site review** (separate from Open Engine): trim the ~21.6k-token session-start footprint (`project-context.md` line 19 alone is ~1,490 tokens inside a head-60 read); add negative fixtures to the five validators; fold the seven-surface Agent Maintenance Loop into `/optimize`.
- **What's needed to resume**: read `03-skills/open-agent-engine/SKILL.md` → "Preflight", then `06-context/open-engine/README.md`, then the lane config. Run `python3 00-bootstrap/doctor/linear-lanes.py` for live state.

---

## Session history (append-only)

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
