---
tags: [knowledge-vault, engineering, agent-ops, mcp, security]
created: 2026-07-30
updated: 2026-07-30
status: working
confidence: high
sources: [session 2026-07-29/30 — Open Agent Engine build, two isolated Linear lanes]
related_skills: [open-agent-engine, workspace-bootstrap]
related_projects: [19-workspace-brain]
---

# Boundaries in a multi-tenant agent work queue

Seven constraints found by building a two-lane agent task queue (one personal, one employer) on a
hosted tracker, each caught by testing against reality rather than reasoning about it. All are
tracker-agnostic and transport-agnostic — none is specific to Linear or to Claude Code, though both
supplied the evidence.

## 1. Connection isolation is not runner isolation

Per-tenant credentials genuinely scope *reads*: a connection authenticated to tenant A cannot see
tenant B. That much is structural. But a **runner** is isolated only if tenant A's server is the
*only* one bound to its process. Register both tenants at **user scope** — the normal desktop setup —
and every session on that machine holds write access to both. The wall is then the agent's judgment,
not the tool layer.

Tolerable with a human watching; **not** tolerable unattended. Any scheduled or headless runner must
be launched with only its own tenant's server present (Claude Code: `--strict-mcp-config` plus a
one-server `--mcp-config`). Verified 2026-07-29: both servers connected in one session, each with its
own auth directory, both writable.

**The general form:** credential scoping and process scoping are different guarantees. Documentation
that conflates them will overstate safety in exactly the case that matters. See [[claude-code-mcp-scope]].

## 2. Identity cannot be verified read-only on an empty tenant

Registration is not authentication, and authentication is not *pointing at the right tenant*. A
connection that OAuth'd into the wrong workspace passes every file-based check and then writes to the
wrong board.

But on a **fresh, empty tenant there may be nothing readable that identifies it.** On Linear the org
slug appears only on object URLs (issues, projects, documents, comments) — `get_user`, `get_team`,
and `list_teams` all omit it, and the server publishes no MCP resources. Zero objects, zero proof.

So identity verification degrades to a **first-write gate**: create the cheapest, most disposable
object you can, read its returned URL, assert the tenant, and only then perform a second write. Which
makes the first write of a tenant's life a deliberate act, not an incidental one.

What *can* be proven read-only: **distinctness**. Where user records are per-tenant (Linear's are),
the same human returning two different user ids proves two different tenants — no write needed. Prove
what you can cheaply; gate the rest.

## 3. Never rely on a tracker's create-default

A default status is a property of the board, not of your intent, and it drifts. Observed: renaming a
team's default `Backlog` to `Standing` silently made `Standing` the create-default, so any issue
created without an explicit state landed outside the claimable pool — invisible to every future run,
with nothing in the loop to flag it. Set the state explicitly on every create.

Corollary worth keeping: **leaving the inert status as the default is the safer choice.** A
half-written issue that sits idle beats one a runner can claim mid-authoring.

## 4. Entity ids collide across tenants

Team/project keys are per-tenant, so two tenants can — and here do — mint the same key. `SEA-5` was a
smoke test on one lane and an unrelated task on the other. A bare id is unambiguous **only inside the
connection that resolved it**; everywhere else (logs, handoff notes, commit messages, conversation)
it must be qualified `tenant:ID`.

The danger is not confusion, it is **mis-resolution**: resolving a bare id against whichever
connection happens to be at hand is a cross-tenant read, and on a write it is a boundary breach. Adopt
a qualified-id convention on day one; retrofitting it means auditing every reference already written.

## 5. A movement-only queue makes deletion structurally impossible

If the queue may hold only *pointers* — never briefs, decisions, or rationale — then migrating a
backlog into it cannot be a content transfer. Each item's issue points at an anchor in the source
document, and **deleting the anchored text orphans the issue.**

This is the useful part: the source becomes the substance store and the queue carries movement, so the
"don't delete the original" discipline stops depending on anyone remembering it. The architecture
enforces it. Shrinking the source later is a separate migration — graduate an item's substance to its
own artifact, repoint the issue, *then* remove.

The inverse is the failure mode to fear: a queue that accumulates content becomes a second source of
truth, and the two drift silently.

## 6. Cloud-scheduled agents cannot reach locally-authenticated tools

Hosted/cloud schedulers run with no local filesystem, no local environment, and no local credential
store. Their tool access comes only from connectors registered with the hosting platform. If the
queue's transport is a locally-OAuth'd MCP server, **a cloud schedule cannot run it at all** — not a
degraded path, an impossibility.

And where the hosted platform *does* offer a connector, it is typically one shared auth context, which
cannot express two isolated tenants. Scheduling and isolation pull against each other; decide which
you need before building either.

## 7. Untrusted input plus autonomy equals remote execution

Issue bodies are untrusted data. An unattended runner that reads an issue and executes the work it
describes — holding a shell and repository access — converts "anyone who can write to that board" into
"anyone who can run commands on that machine". On a tenant an employer or third party could one day
administer, that is a prompt-injection path to code execution on a personal device.

The mitigation is not better prompting. It is either keeping a human in the loop at the moment of
execution, or reducing the runner's tool surface so that reading the board cannot cause execution
(move-work-only: tracker writes, no shell, no VCS). **Autonomy and untrusted input are safe in
isolation and dangerous only together** — which is why the combination is easy to arrive at by
accident, one reasonable decision at a time.

## The pattern behind all seven

Every one of these was found by **doing the thing and reading what came back** — creating an object
and inspecting its URL, listing servers in a live session, watching a rename move a default. None was
visible from the documentation, and several contradicted a design document written hours earlier by
the same author. A boundary nobody has watched fail is not a boundary yet.

## Related

- skill → [[open-agent-engine]]
- MCP scope behaviour → [[claude-code-mcp-scope]]
- credential handling → [[feedback-credential-scoping]]
- fenced-layer failures → [[silent-degradation-in-fenced-layers]]
