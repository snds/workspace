---
tags: [context, critical, always-load]
created: 2026-07-23
status: active
---

# CRITICAL FACTS — read me first (always loaded)

_The handful of facts a session must never re-derive. Deliberately tiny (~a screenful)
so it's cheap to load every time; everything else is one hop away via the frameworks,
memory, and context files. Keep this current and prune ruthlessly — if it outgrows a
screen, it's doing too much and the overflow belongs in `memory/` or a framework._

## For future agent
- **TL;DR:** Sean Sands' portable, git-native design + engineering workspace. The git
  checkout is the source of truth; externalize everything durable here, never to local memory.
- **As of:** 2026-07 · **Status:** current

## The facts
- **Who:** Sean Sands (`hello@snds.design`) — designer + design engineer; employer = Centric (c8).
- **Workspace:** local `~/Projects/workspace` · remote `github.com/snds/workspace`. The **git
  checkout is the source of truth** (portable, not Google Drive; see [[decision-portable-workspace-refactor]]).
- **The three standing walls** (in force even before loading):
  1. Figma work uses **real library components**, never hand-built shapes.
  2. Durable context / learnings / decisions go to the **workspace**, never to local agent memory
     (see [[decision-externalize-everything-to-workspace]]).
  3. **Employer repos (`c8/*`) never receive personal-workspace content**, and workspace content
     is never pasted into employer surfaces.
- **Session start is mandatory:** read [[AGENTS]] read-order, emit the `workspace: LOADED` ritual
  token (machine-ABI; the SessionEnd audit greps for it), then the ✓ summary block.
- **Frameworks govern all work** (eleven, see [01-frameworks/00-README](../01-frameworks/00-README.md)).
  Framework **#06 QA pre-output gate is non-negotiable** for any audit/review/refine task.
- **Machine label** resolves from `hostname` at boot (table in [[CLAUDE]]); never ask, never carry forward.
- **Freshness:** treat every claim as **timeless / dated / pointer** (see
  [epistemic-standards](../02-shared-references/epistemic-standards.md) §2); `#stale` = re-check before trusting.
- **The legacy Drive workspace** (`claude-workspace-system`) is separate and untouched (see [[fact-workspace-repos]]).
