---
type: decision
description: Always print a numbered order of operations and the first later-breaker before executing multi-step or dual-repo work.
created: 2026-09-11
confidence: high
relations:
  builds-on: ["[[decision-cursor-prompt-route-hook]]"]
  relates-to: ["[[plan-ahead]]"]
---

## For future agent
- **TL;DR:** Sean asked the workspace to stay ahead of him on planning. Multi-step / dual-repo / consume work prints a numbered sequence and names the first later-breaker (local overlay ≠ CI cds `main`) **before** the first edit. Skill `03-skills/plan-ahead/SKILL.md`; Cursor agent `.cursor/agents/plan-ahead.md`.
- **As of:** 2026-09 · **Status:** current

## Context — what forced a choice
Proto #77 Pages failed on `@centric/ui/sonner` because the overlay had the export and cds `main` (after a squash) did not. Sean did not know Toaster and SplitDragHandle were the breakers until CI said so.

## Decision — what we chose
Make order-of-operations the default presentation. Route it into employer-repo chats via trigger-routes (`order of operations`, `cds then proto`, `pages build`, `follow up`, `re-export`). Keep the always-on reminder in AGENTS.md / brain.mdc to two lines.

## Rationale — why, and what we rejected
A pin check that allows overlay-ahead cannot catch this. A skill that only loads on "plan" is too late. Rejected stuffing a long checklist into always-on rules (token cost).

## Consequences — what this commits us to
Agents print the sequence first. Proto `cds-exports-check` is the mechanical gate. Consume of Toaster / SplitDragHandle / ChipMultiSelect still waits on cds #35 merge.
