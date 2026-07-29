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
pass first — which it now has (2026-07-29). **No scheduled runner exists yet**; standing one up is
separate work, and `Automation state` stays `manual-required` until it does.

**⚠️ Identifier collision across lanes.** Both lanes' workspaces auto-created a team keyed `SEA`, so
issue ids are **not unique across lanes** — `SEA-5` is hello-world here and the substance-refusal test
on `c8`. Inside one tracker context disambiguates; anywhere else — session logs, handoff notes,
conversation — **qualify the id with its lane** (`personal:SEA-5`, `c8:SEA-5`).

## Optional standing skills

Directory issue: none (not used)
Subscribed: none

## Verification record

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
- [x] **Six statuses created (2026-07-29)** — `Standing` (backlog) · `Agent Todo` (unstarted) ·
      `Agent Working` (started) · `Agent Needs Input` (started) · `Agent Review` (started) ·
      `Agent Done` (**completed**, verified live: `completedAt` populates on transition). Created by
      hand in Linear → team `SEA` → Settings → Workflow → **Issue statuses**; the MCP has no
      status-creation operation. `Agent Review` is deliberately **not** completed — it means "done,
      but a human must judge", and a completed status would close the issue out of the human's view.
      **Sean renamed the five defaults rather than adding alongside** (`Todo`→`Agent Todo`,
      `In Progress`→`Agent Working`, `In Review`→`Agent Needs Input`, `Backlog`→`Standing`,
      `Done`→`Agent Done`) and added `Agent Review` new. Consequences, all accepted: this team now
      speaks only the engine's vocabulary, so ordinary personal work would have to borrow it; state
      *history* is relabelled retroactively (an issue created before the rename reads as having
      started in `Standing`); and `SEA-1`–`SEA-4`, Linear's onboarding seeds, now sit in `Agent Todo`
      — harmless, since the runner filters on label + title marker, and proven so during smoke test 1.
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
