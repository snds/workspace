---
type: fact
description: The two workspace git repos and which one is canonical going forward
created: 2026-06-16
confidence: high
---

There are two workspace repositories, with **no shared git history**:

- `github.com/snds/workspace` — **the new canonical, portable workspace** (this checkout). Git is the
  source of truth; no Google Drive or Desktop Commander coupling.
- `github.com/snds/claude-workspace-system` — the **legacy** Drive-based original, backed by the local
  gitdir `~/.git-stores/claude-workspace-system`. Left untouched by the refactor.

This copy was detached from the shared legacy gitdir and re-initialized as an independent repo, so commits
here never affect the legacy original. Work going forward happens in `snds/workspace`. See
[[decision-portable-workspace-refactor]] for the rationale.
