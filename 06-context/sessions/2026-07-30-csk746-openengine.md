### 2026-07-30 — Open Agent Engine: provisioned, smoke-tested, wired to the rituals, backlog migrated

SessionID: 2026-07-30-csk746-openengine

--- SESSION BLOCK ---
Date: 2026-07-30
Agent: Claude Opus 5
Machine: Work MacBook Pro (`CS-K746DRWXY1`)
Surface: Cursor (Claude Code extension)
Project(s): 19-workspace-brain — Open Agent Engine (both lanes); 06-context backlog migration
Artifacts:
  - 08-knowledge/engineering/agent-work-queue-boundaries.md — seven tracker-agnostic boundary
    constraints found by testing, not reasoning
Decisions:
  - Stage-2 identity verification passed on both lanes; the workspace-slug check degrades to a
    first-write gate, because no Linear read exposes an org slug on an empty board
  - Six engine statuses created by hand (Sean) — the MCP has no status-creation or team-creation op
  - Unattended scheduled runs AUTHORIZED via the `personal:SEA-8` human hold, then deliberately
    NOT exercised
  - **No timer — the session boundary is the heartbeat.** Cloud routines cannot reach Linear at all;
    a local runner with full autonomy makes untrusted issue bodies a path to a shell; and a timer
    only buys progress-while-absent, which is not how Sean works
  - Migration is pointer-shaped, so items CANNOT be deleted from project-context.md — the
    architecture enforces Sean's "don't remove until validated" instead of discipline doing it
  - Employer-lane issues carry no path into this repo; resolution goes through a machine-local table
Pending added:
  - `personal:SEA-32` — the six statuses have no "someday" bucket and the claim rule is
    priority-blind; harmless while runs are human-triggered, real the moment anything is unattended
  - 5 items could not be migrated (`^pc-07`, `^pc-11`, `^pc-30`, `^pc-41`, `^pc-42`) — two need a
    machine-local home before they can be filed without writing substance to the employer board;
    two are lane-ambiguous; one has nothing to point at
Pending resolved:
  - `^pc-04` trigger-routes reference — delivered by a concurrent Cursor session; `personal:SEA-11`
    moved to `Agent Review` (not Done) because the work is still uncommitted
  - `^pc-13` beacon paste — Cursor User Rules done, Perplexity Space still open; issue stays open
Project status changes:
  - Open Agent Engine: build → live on both lanes, all four smoke tests passed
Deferred commits:
  - A concurrent Cursor session's work (~20 modified + ~10 untracked: Cursor rules/hooks,
    trigger-routes system, workspace-doctor, AGENTS.md, .gitignore, archive move) is uncommitted and
    was deliberately NOT swept into this session's commits — see the orphaned-changes audit
Next:
  - Commit the concurrent Cursor session's work under its own attribution, then close
    `personal:SEA-11`
  - Decide `personal:SEA-32` (seventh status vs priority-aware claim rule)
  - Give `^pc-07` / `^pc-11` machine-local homes so they can be filed; resolve the lane ambiguity
    on `^pc-30` / `^pc-41`
  - First ordinary session is the real test of the ritual integration — does the engine line appear
    only when it should, and does `/session-end` file residue pointer-shaped?
--- END BLOCK ---
