---
type: decision
description: Why framework #18 (Design Systems × AI) exists beside #09, with an ai-design-systems spoke
created: 2026-09-11
confidence: high
relations:
  builds-on: ["[[decision-component-pattern-framework-system]]"]
  exemplifies: ["[[ai-and-design-systems]]"]
---

## For future agent

- **TL;DR:** #09 owns component intent/schema; #18 owns how AI attaches to a living design system. Procedure is the `ai-design-systems` spoke under `ds-advisor`, not a new hub.
- **As of:** 2026-09 · **Status:** current

## Context — what forced a choice

Sean completed Brad Frost / Southleft *AI and Design Systems* (notes in `07-projects/22-ai-design-systems-course/`). The vault already held Atomic Design as a mapping inside #09, contracts/testimony, A2UI, and Curtis ops notes — but it did not have an **operating model** for mortar, steel curtain, context-based drafts, agent users, or sell→pilot→rollout→govern. Dumping that into `ds-advisor` (already huge) or into #09 (wrong question) would either bloat or misplace it. Sean's explicit signal: Frost's models are paramount to how he has worked for eight years; the course should structure the workspace, not sit as a project souvenir.

## Decision — what we chose

1. **New L1 framework #18** — Design Systems × AI Operating Model — consumed by ds-advisor, design-engineer, design-system-ops, generation, a11y/QA gates.
2. **Spoke `ai-design-systems`** under `ds-advisor` (not a hub) — verb grammar inspect/ready/draft/rails/agents/gen-ui/adopt.
3. **Knowledge entry** [[ai-and-design-systems]] for provenance; weave terse Frost canon into `ds-advisor` and bans into generation/ops/engineer rather than forking principles.
4. **Do not** add this doctrine to `AGENTS.md` (token frugality). Route via trigger-routes + skill triggers + the "design system" curated load.

Rejected: stuffing #09; a second DS hub; knowledge-only (would not fire on work).

## Rationale — why, and what we rejected

#09 answers "what is each component for." The course answers "what is the system, and how may AI touch it." Three-plus consumers earned a framework (#08 rule). A spoke keeps load-chain intact (`design-foundations → ds-advisor → ai-design-systems`) without an orphan hub.

## Consequences — what this commits us to

- DS+AI tasks load #18 + the spoke; component-choice tasks still load #09 first.
- `ds-generation-pipeline` must refuse "generate a DS from scratch" when a system exists.
- Official Figma MCP vs Console MCP stays a named distinction.
- Course notes remain the project archive; durable claims live here, not in SESSION-STATE.
