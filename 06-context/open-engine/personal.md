---
tags: [context, open-engine, agent-ops, lane]
created: 2026-07-29
status: provisioning
aliases: [open-engine-personal]
---

# Open Agent Engine — lane `personal`

Instance config for the personal-solo lane. Procedure lives in [[open-agent-engine]] — do not restate
it here. This file answers only *which instance*.

> **Status: PROVISIONING (2026-07-29).** Stage-2 identity verification passed and the board is built
> — team, project, label, ledger, and the first `AGENT STATUS` comment all exist. **One blocking
> human step remains: the six engine statuses.** The Linear MCP exposes no status-creation operation
> (`list_issue_statuses` / `get_issue_status` only), so they must be created in Linear's team
> settings by hand. Until they exist, no queue run is valid and the smoke tests cannot execute — the
> runner must refuse to run.

## Binding

| Field | Value |
|---|---|
| Engine version | v1 |
| Tracker | Linear |
| Workspace | `snds` — <https://linear.app/snds/> |
| Account | personal (`hello@snds.design`) — **must not** be the Centric Google account |
| Team | `Sean Sands` · key `SEA` · `87d16edc-8626-4d1b-93ed-6ae0e74487df` |
| Project | `Personal Agent Engine` · `6a2d5795-105a-40ae-8f79-369744f82672` |
| Label | `agent-instructions` · `dbe5a1fa-21a7-4d27-a022-7583d03e5f33` (workspace-level) |
| Statuses | created 2026-07-29 — six engine statuses live; `Agent Done` verified in the completed category (`completedAt` populates) |
| Default status for new issues | `Standing` — **always set `state` explicitly when creating a task issue.** Sean renamed the team's defaults rather than adding alongside, so the old `Backlog · Default` became `Standing`. An issue created without an explicit state lands in `Standing` and is never claimable. Leaving the default here is deliberate: a half-written issue sitting inert is safer than one a runner can claim mid-authoring. |
| Status ledger issue | `SEA-6` |
| Transport | MCP preferred; HTTP/GraphQL fallback — see [[open-agent-engine]] → Transport |
| MCP server | `linear-personal` (user scope) |
| MCP auth dir | `~/.mcp-auth/linear-personal` |
| Context profile | `personal-solo` |
| Movement-only | **no** — this lane may carry substance |

## Agent codes

One stable code per runtime. The runner identifies its own runtime and picks the matching code.

| Runtime | Agent code |
|---|---|
| Claude Code | `sean-claude` |
| Cursor | `sean-cursor` |

Machines are *not* part of the agent code — the ledger's `Last heartbeat` and the session block's
machine stamp already carry that, and per-machine codes would fragment the claim lock.

## Allowed sources

- This workspace checkout (read + write, per `personal-solo`).
- Personal repos under the `Projects` directory on this machine.
- Public web.

Not in scope for this lane: anything under an employer remote. Those route to `c8`.

## Boundaries

- `personal-solo` profile: direct commits and the session-end commit are expected. Still no force
  pushes to `main`, and no history rewrites on pushed branches.
- Ask before: publishing, posting publicly, emailing, deploying, changing billing or credentials, or
  deleting anything not covered by the archive protocol.
- Never write employer content here. If a task turns out to be employer-scoped, leave
  `AGENT HUMAN HOLD` and ask — do not re-file it across lanes unilaterally.

## Unattended execution

**Authorized 2026-07-29** by Sean, in the operator's agent thread, via the `HUMAN HOLD` on `SEA-8`.
A scheduled runner may claim and execute `Agent Todo` issues on this lane with no human present.

It relaxes nothing else: the `personal-solo` profile, the ask-first list (publish · post · email ·
deploy · credentials · billing · deletion outside the archive protocol), and one-task-issue-per-run
all still hold. **An unattended run is not a broader-permission run.**

The same grant covers the `c8` lane, with the standing recommendation that its substance-refusal test
pass first — which it now has (2026-07-29).

**Decision 2026-07-29: no timer. The session boundary is the heartbeat.** A scheduled runner was
scoped and rejected on three findings, in order of weight:

1. **Cloud routines cannot reach Linear.** They run with no local files, no local env, and no
   `~/.mcp-auth`; their only MCP comes from claude.ai connectors, and Linear is not among the
   connected ones. A cloud routine was never an option.
2. **A local runner with full autonomy is a prompt-injection path to a shell.** Issue bodies are
   untrusted input by this engine's own rule, and an unattended process reading them while holding
   Bash and git turns "anyone who can write to that board" into "anyone who can run commands on this
   laptop". Acute on the `c8` lane, whose workspace could one day be administered by a Centric tenant.
3. **A timer buys nothing here.** Its only value is progressing work while the human is away; Sean
   works interactively as the sole human on the main runtime, so hourly runs would mostly burn tokens
   confirming an empty queue.

What replaced it: the engine reads at **session start** (report-only, silent when empty) and files
residue at **session end**. The human is present exactly when a hold can be answered, so unattended
execution is not needed to make holds resolvable. Wired into `CLAUDE.md`'s session-start ritual and
`/session-end` Step 5.5; procedure in [[open-agent-engine]] → Ritual integration.

**Hard gate before any future timer (2026-08-07 harness-map #6):**
`python3 09-tools/check-unattended-runner-gate.py --require` with
`UNATTENDED_RUNNER=1`, `OPEN_ENGINE_TOOLS`, `OPEN_ENGINE_DISALLOWED_TOOLS` (must deny
Bash/Edit/Write/Agent/CronCreate), and `OPEN_ENGINE_STRICT_MCP=1`. Exit 1 → do not launch.

**The authorization above stays on record**, unexercised. If a real need for unattended progress
appears (most likely cross-machine handoff), it can be switched on without re-litigating — but it
**must** be lane-scoped (`--strict-mcp-config` + a one-server `--mcp-config`), and finding 2 should be
re-read first. `Automation` reads `session rituals`, not `manual` and not `scheduled`.

**⚠️ Identifier collision across lanes.** Both lanes' workspaces auto-created a team keyed `SEA`, so
issue ids are **not unique across lanes** — `SEA-5` is hello-world here and the substance-refusal test
on `c8`. Inside one tracker context disambiguates; anywhere else — session logs, handoff notes,
conversation — **qualify the id with its lane** (`personal:SEA-5`, `c8:SEA-5`).

## Migrated items — project-context.md → this lane (2026-07-30)

23 items migrated from `06-context/project-context.md` → Pending Items. **Nothing was deleted there
and nothing may be**: each issue's only pointer is its anchor, so removing the anchored text would
orphan the issue. `project-context.md` is now the substance store for these.

| Anchor | Issue | Item |
|---|---|---|
| `^pc-02` | `personal:SEA-9` | Silence the two beacon-enroll NOTEs |
| `^pc-03` | `personal:SEA-10` | Machine-layer installs on remaining machines |
| `^pc-04` | `personal:SEA-11` | Tool-neutral trigger-routes reference — **closed 2026-08-05** (accepted; substance already Done in vault) |
| `^pc-09` | `personal:SEA-12` | SSH to github.com:22 timing out |
| `^pc-10` | `personal:SEA-13` | "Context is King" foundation refinements |
| `^pc-12` | `personal:SEA-14` | 2026-07-08 audit carry-forwards (b–e) |
| `^pc-13` | `personal:SEA-15` | Beacon paste — Cursor + Perplexity |
| `^pc-14` | `personal:SEA-16` | Load ux-component-library v2.1 |
| `^pc-19` | `personal:SEA-17` | REVOKE the Figma PAT (Urgent) |
| `^pc-20` | `personal:SEA-18` | Install the snds@snds-local plugin |
| `^pc-21` | `personal:SEA-19` | Refresh the trigger cheatsheet |
| `^pc-22` | `personal:SEA-20` | design-system-ops overlap reconciliation |
| `^pc-23` | `personal:SEA-21` | Document the six-hub grammar |
| `^pc-24` | `personal:SEA-22` | Seed SESSION-STATE for 04-claude-figma-plugin |
| `^pc-25` | `personal:SEA-23` | Opus 4.7+ skill-audit findings |
| `^pc-26` | `personal:SEA-24` | Framework pointers in six skills |
| `^pc-35` | `personal:SEA-25` | Section D reference DS deep reads |
| `^pc-36` | `personal:SEA-26` | Section B audit (18 patterns) |
| `^pc-37` | `personal:SEA-27` | Graduate 28 pattern entries |
| `^pc-38` | `personal:SEA-28` | Stream C re-audit (due 2027-07-01) |
| `^pc-39` | `personal:SEA-29` | Re-privatize workspace-repo author email |
| `^pc-40` | `personal:SEA-30` | Populate team-practices-and-decisions |
| `^pc-43` | `personal:SEA-31` | Seed SESSION-STATE for 03/12/15 |

**The collision hazard, live:** `personal:SEA-9` is the beacon-NOTE item; `c8:SEA-9` is a centric-ui
PR. Same bare id, different lanes, different work. This table is why every id above is qualified.

**Not migrated, and why** — 5 items remain only in `project-context.md`:

| Anchor | Reason |
|---|---|
| `^pc-07` | `c8`, no valid pointer. Its substance is an internal hostname + a DNS finding; putting either on the employer board is exactly the infra detail movement-only forbids. Needs a machine-local home first. |
| `^pc-11` | `c8`, no valid pointer. Reasoning plus a named colleague's directive exist only in `project-context.md`, and neither may be written to that board. |
| `^pc-30` | **Lane ambiguous.** 103 characters with no indication whether the plugin is Sean's own or employer tooling. Guessing the lane on a movement-only boundary is the one thing the skill says never to do. |
| `^pc-41` | Lane ambiguous *and* no pointer. |
| `^pc-42` | `c8`, no valid pointer — exploratory, no artifact to reference. |

## Optional standing skills

Directory issue: none (not used)
Subscribed: none

## Verification record

**Stage 2 — workspace identity, 2026-09-02 (Cursor Grok 4.6 · Cursor · Personal MBP `Voyager-2.local`).**

| Check | Evidence | Verdict |
|---|---|---|
| Account | `get_user("me")` → `hello@snds.design`, user `92d3f2ac…`, admin | ✅ matches the declared `Account` |
| Distinctness | this machine expects `personal` only — `linear-c8` is not registered (correct). User/team ids match the 2026-07-29 Work MBP record | ✅ no second lane to collapse into |
| Workspace | `get_workspace` → `https://linear.app/snds` (slug `snds`) | ✅ matches; Linear now exposes the slug on a read, so no first-write gate was needed |

**Transport this session.** Cursor `~/.cursor/mcp.json` server `linear-personal` via mcp-remote; tokens in `~/.mcp-auth/linear-personal`. Doctor: `ok`. Query verified: `list_issue_statuses` (seven engine statuses live; board label `Some Day`) + `list_issues` Agent Todo.

**Stage 2 — workspace identity, 2026-07-29 (Claude Opus 5 · Claude Code · Work MBP `CS-K746DRWXY1`).**

| Check | Evidence | Verdict |
|---|---|---|
| Account | `get_user("me")` → `hello@snds.design`, user `92d3f2ac…`, admin | ✅ matches the declared `Account` |
| Distinctness | this lane user `92d3f2ac…` / team `87d16edc…`; the other lane returns a different user id **and** a different team id. Linear user records are per-workspace, so this proves two different orgs | ✅ lanes cannot collapse onto one destination |
| Workspace | first created object returned `https://linear.app/snds/issue/SEA-5/…` | ✅ slug `snds` matches |

**Why the slug needed a write.** No Linear MCP read exposes the org slug — `get_user`, `get_team`,
and `list_teams` all omit it; the slug-bearing `url` exists only on projects, issues, documents, and
comments; and the server publishes no MCP resources. On an empty board the check is therefore only
answerable by creating something. The skill's stage-2 section carries this as the first-write gate.

**Transport.** All four required operations verified live: query (`list_issues`), create
(`save_issue`), update incl. status-write (`save_issue` Backlog → Todo on `SEA-5`), and comment
(`save_comment` on `SEA-6`).

## Setup checklist

- [x] Linear workspace created (2026-07-29)
- [x] **Seven statuses (2026-07-29 + `Someday` 2026-08-05)** — `Standing` (backlog) · `Someday`
      (deferred, not claimable; board may read `Some day`) · `Agent Todo` (unstarted) ·
      `Agent Working` (started) · `Agent Needs Input` (started) · `Agent Review` (started) ·
      `Agent Done` (**completed**, verified live: `completedAt` populates on transition). Created by
      hand in Linear → team `SEA` → Settings → Workflow → **Issue statuses**; the MCP has no
      status-creation operation. `Agent Review` is deliberately **not** completed — it means "done,
      but a human must judge", and a completed status would close the issue out of the human's view.
      `Someday` is also not completed (parking lot). **Sean renamed the five defaults rather than
      adding alongside** (`Todo`→`Agent Todo`, `In Progress`→`Agent Working`,
      `In Review`→`Agent Needs Input`, `Backlog`→`Standing`, `Done`→`Agent Done`), added
      `Agent Review` new (2026-07-29), then added `Someday` / `Some day` on both lane boards
      (2026-08-05 — closes `personal:SEA-32`). Consequences, all accepted: this team now speaks only
      the engine's vocabulary, so ordinary personal work would have to borrow it; state *history* is
      relabelled retroactively (an issue created before the rename reads as having started in
      `Standing`); and `SEA-1`–`SEA-4`, Linear's onboarding seeds, now sit in `Agent Todo` — harmless,
      since the runner filters on label + title marker, and proven so during smoke test 1.
- [x] `agent-instructions` label created and applied to a test issue (`SEA-5`, `SEA-6`)
- [x] Team + project created; ids recorded above — **deviation:** the lane originally suggested a
      dedicated `Agent Engine` team, but the MCP cannot create teams either. The workspace's default
      `Sean Sands` / `SEA` team is used instead. Harmless while this workspace hosts nothing else; if
      it ever does, move the engine to its own team and update the ids above.
- [x] MCP server `linear-personal` registered at user scope and authenticated
- [x] Read / comment / status-write verified on a throwaway issue (see Verification record)
- [x] Ledger issue created (`SEA-6`); id recorded above; first `AGENT STATUS` comment posted
- [x] **Smoke test 1 — hello-world: PASSED** (`SEA-5`, 2026-07-29). Full run: ledger heartbeat →
      claim → re-read → work → `AGENT DONE` → `Agent Done`. Proved four things beyond the happy path:
      the in-place ledger edit keeps one comment id (`createdAt` unchanged across three updates, so no
      heartbeat clutter); the label + title-marker filter correctly skipped `SEA-1`–`SEA-4` sitting in
      the same status; `completedAt` populated, so `Agent Done` really is in the completed category;
      and the run stopped after exactly one task issue.
- [ ] Smoke test 2 — blocked-resume. **Mid-flight:** `SEA-7` claimed and left `AGENT BLOCKED` in
      `Agent Needs Input`, ledger `blocked SEA-7`. Waiting on an answer **on the issue**. Resume leg
      (`UNBLOCKED` → `RESUMED` → `DONE`) still unproven.
- [ ] Smoke test 3 — human-hold. **Mid-flight:** `SEA-8` claimed and left `AGENT HUMAN HOLD` in
      `Agent Needs Input`, ledger `holding SEA-8`. Waiting on an answer **in the agent thread**.
      Resume leg (`HUMAN ANSWERED` → `RESUMED` → `DONE`) still unproven.
- [ ] Optional-skill directory check summarizes without installing

**Housekeeping:** Linear seeded the workspace with four onboarding issues (`SEA-1`–`SEA-4`:
"Get familiar with Linear", "Connect your tools", "Import your data", "Set up your teams"). They are
unlabelled and outside the project, so the runner's filter ignores them — delete at leisure.

## Related
- skill → [[open-agent-engine]]
- index → [README](README.md)
