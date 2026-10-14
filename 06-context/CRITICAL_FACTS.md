---
tags: [context, critical, always-load]
created: 2026-07-23
status: active
---

# CRITICAL FACTS — read me first (first file in the AGENTS.md read order)

_The handful of facts a session must never re-derive. No hook injects it; every agent reads
it first ([[AGENTS]] → Canonical read order). Deliberately tiny (~a screenful) so it's cheap
to read every time; everything else is one hop away via the frameworks, memory, and context
files. Keep this current and prune ruthlessly — if it outgrows a screen, it's doing too much
and the overflow belongs in `memory/` or a framework._

## For future agent
- **TL;DR:** Sean Sands' portable, git-native design + engineering workspace. The git
  checkout is the source of truth; externalize everything durable here, never to local memory.
- **As of:** 2026-10-14 · **Status:** current

## The facts
- **Who:** Sean Sands (`hello@snds.design`) — designer + design engineer; employer = Centric (c8).
- **How to write to him — applies to EVERY reply, outranks other style notes.** Sean is ADHD
  and autistic. Plain language, one idea per sentence, answer first, no unexplained jargon.
  Keep the depth; change the packaging. Full rule: [[user-preferences]] → Response Style.
- **Commands for Sean:** run each one yourself first and fix what stops it. One block each:
  `cd /Users/sean.sands/Projects/<folder> && …`, absolute paths, never `~/`. Only when needed now.
  Full rule: [[user-preferences]] → Actions for me.
- **Workspace:** local `~/Projects/workspace` · remote `github.com/snds/workspace`. The **git
  checkout is the source of truth** (portable, not Google Drive; see [[decision-portable-workspace-refactor]]).
- **The three standing walls** (in force even before loading):
  1. Figma work uses **real library components**, never hand-built shapes.
  2. Durable context / learnings / decisions go to the **workspace**, never to local agent memory
     (see [[decision-externalize-everything-to-workspace]]).
  3. **Employer repos never receive personal-workspace content**, and workspace content
     is never pasted into employer surfaces. Every surface, Claude included, follows the device
     and the repo: Centric repos run under `centric-engineering` (branch → PR → human review) on the
     Work MBP; credentials stay scoped per repo ([[decision-claude-employer-surface]],
     [[feedback-credential-scoping]]).
- **Session start is mandatory:** emit `09-tools/session-status.py` (notices + all
  projects + pending). The ABI line `[workspace: LOADED · …]` is machine-ABI (SessionEnd audit).
  Do not shrink Active projects. Continuations skip the card.
- **Frameworks govern all work** (eighteen, see [01-frameworks/00-README](../01-frameworks/00-README.md)). #17 is living-spec agent coordination (`intent-run.py`). #18 is Frost/Southleft DS×AI.
  Framework **#06 QA pre-output gate is non-negotiable** for any audit/review/refine task.
- **Machine label** resolves from `hostname` at boot via `02-shared-references/devices.json`
  (`09-tools/profile_resolve.py` → `device_label`); never ask, never carry forward.
- **Freshness:** treat every claim as **timeless / dated / pointer** (see
  [epistemic-standards](../02-shared-references/epistemic-standards.md) §2); `#stale` = re-check before trusting.
- **The legacy Drive workspace** (`claude-workspace-system`) is separate and untouched (see [[fact-workspace-repos]]).
