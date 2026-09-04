---
type: decision
description: Multi-agent work uses a living intent spec; Intent the Mac app is optional tooling, not the contract
created: 2026-09-04
confidence: high
relations:
  builds-on:
    - "[[decision-externalize-everything-to-workspace]]"
    - "[[decision-portable-workspace-refactor]]"
  exemplifies:
    - "[[17-intent-coordination-operating-model]]"
---

## For future agent
- **TL;DR:** Designed-intent coordination is framework #17 + [[intent-coordination]]. The Intent app is optional. Specs are files. Open Engine stays movement-only.
- **As of:** 2026-09 · **Status:** current

## Context — what forced a choice

Sean asked to review intentapp.dev and make large-scale agent coordination the standard so outcomes stay close to designed intent. The workspace already had queues (Open Engine), done-checks (mission-fit), continuity (Live handoff), and domain prove-gates, but multi-agent work still defaulted to chat threads.

## Decision — what we chose

Adopt Intent's **protocol** (living spec, approve, isolated implementors, independent verifier) as portable doctrine. Do not require Augment's app, credits, or Context Engine. Do not replace Open Engine, skills, or validators.

## Rationale — why, and what we rejected

Portable-first forbids a macOS-only shell as law. A second queue would fork substance. Chat-as-spec is how intent drifts across agents. Mapping onto files + git + existing skills keeps one contract.

Rejected: vendor lock as standard; cloning the Intent UI into the vault; always-on load of the new skill (token cost).

## Consequences — what this commits us to

- Multi-agent / parallel work writes `docs/INTENT.md` (or equivalent) in the owning tree.
- Live handoff points at that spec.
- Verifiers use evidence, not the implementor's story.
- Employer profile still blocks auto-commit and self-merge.
