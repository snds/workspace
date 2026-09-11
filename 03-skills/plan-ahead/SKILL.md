---
name: plan-ahead
description: >
  Print a numbered order of operations and name the first later-breaker BEFORE
  writing code. Use on multi-step work, dual-repo consume (cds then proto),
  follow-ups after a squash-merge, Pages / CI vs local overlay, "what's the
  sequence?", "don't get ahead of me", PR pairs, or any ask that can succeed
  locally and fail in CI. The workspace should be ahead of Sean on planning —
  he should never learn the breaker from a red Pages job. Pair with
  failure-mode-premortem for visual techniques; this skill is the sequence and
  CI-contract half.
aliases: [plan-ahead, order-of-operations, cds-then-proto]
triggers: [order of operations, cds then proto, consume cds, pages build, follow up, overlay vs main, first breaker, dual repo, squash leftover, re-export]
tier: cross-cutting
domain: workspace
related: [workspace-bootstrap, failure-mode-premortem]
surfaces: ["*"]
spec_version: "2.2"
---

# Plan Ahead

Print the sequence before executing. Name what can fail *later* while the local tree looks green.

## Purpose

Sean reviews as a designer. A local overlay symlink, a squash that dropped a follow-up commit, or
an `@centric/ui/X` import whose `exports["./X"]` exists only on the worktree will pass Vite and fail
Pages. This skill makes the agent surface that **before** the first file edit.

## When to use

- Dual-repo work (cds + saas-plm-prototype)
- Consume / re-export / "follow up" after a cds PR
- Pages, GitHub Actions, or "CI is green locally"
- Any multi-step plan with an order that can be inverted

## When NOT to use

- Single-file copy or a question with no write
- Visual technique premortem → [[failure-mode-premortem]]
- Session handshake → [[workspace-bootstrap]]

## Behavior

Before the first edit, print:

1. **Goal** in one line
2. **Numbered order of operations** (what must land *before* the next step)
3. **What CI actually vendors** vs what this laptop is linked to
4. **Squash leftovers** — commits that sat on a feature branch after a squash-merge
5. **First breaker** — the one thing that will fail later if we invert the order
6. **Do not start** any proto `export * from "@centric/ui/X"` until cds `main` exports `./X`

Then execute in that order. If a step is blocked (open cds PR, waiting on merge), stop and say so.

## Dual-repo (cds + proto)

| Step | Who | Why |
|---|---|---|
| 1 | cds PR onto `main` | Pages clones cds `main`, not the overlay worktree |
| 2 | Confirm `packages/ui/package.json` `exports` on `main` | Subpath imports need `./name`, not just a file on disk |
| 3 | Proto consume / re-export | Only after (2) |
| 4 | Proto `npm run build` (includes `cds-exports-check`) | Local overlay can no longer hide a missing `main` export |

`ds-pin` treating overlay-ahead as a *note* is correct for co-dev. It is **not** a Pages contract.
The Pages contract is: every `@centric/ui/<subpath>` import exists on cds `origin/main`.

## First breaker (learned 2026-09-11)

Toaster (`./sonner`) and `SplitDragHandle` were on the overlay after cds #34 squash-merged without
them. Proto imported `@centric/ui/sonner`. Local Vite succeeded. Pages failed. Knowledge:
[[cds-host-consume-order]].

## Related
- peer ↔ [[workspace-bootstrap]]
- peer ↔ [[failure-mode-premortem]]
