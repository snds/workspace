---
tags: [harness, agents, zero-vector, investiture, methodology, drift-control, research-synthesis]
created: 2026-09-22
updated: 2026-09-22
status: working
confidence: medium
sources:
  - "zerovector.design — /, /start, /approach, /philosophy, /for-builders, /investiture, /investiture/skills, /investiture/changelog, robots.txt, llms.txt, sitemap.xml (read 2026-09-22)"
  - "open.zerovector.design — /, /learn (read 2026-09-22)"
  - "herelabrador.ai (read 2026-09-22; pre-beta)"
  - "github.com/erikaflowers/{investiture,openvector,zerovector} @ main (read 2026-09-22; no LICENSE file)"
  - "Erika Flowers, 'The 20 Rules for AI-First Design' (2026-02-03) and 'Zero Stage to Orbit' (2026-02-21), eflowers.substack.com"
  - "07-projects/19-workspace-brain/notes/zero-vector-harness-plan_2026-09-22.md"
related_skills: [harness-map, close-out, intent-coordination, plan-ahead, mission-fit, self-improve]
related_projects: [19-workspace-brain, 18-bootstrap-generator]
relations:
  relates-to:
    - "[[nate-jones-harness-enrichments]]"
    - "[[agentic-ds-context-model]]"
    - "[[agentic-error-correction-foundations]]"
    - "[[agent-output-rails]]"
---

# Zero-Vector Design: methodology, tooling, training, and what transfers

## For future agent

- **TL;DR:** Zero-Vector (ZV) is Erika Flowers' design-led build methodology. Its core claim is that
  the distance between intent and working product should be zero. The mechanism is one person
  running agents across research, framing, building, testing, and shipping. The transferable
  value is in a handful of **patterns**: project intent doctrine, spec-lint plus drift audit,
  finding ledger with closure, self-contained phase packets, role charters with owned paths, and
  research records with provenance. The tooling itself is prompt-only and drifts. Its own repos
  show the failure to design against, **"done but not closed"**. Steal the method, not the tool.
- **Key claims:**
  - Almost every ZV mechanism is a slash command an LLM runs on request. There are no hooks, no
    CI, and no schema validators; the control panel's health checks are stubs. (dated 2026-09-22)
  - The site's own repo runs the Investiture audit chain. It produced a strong audit and a phased
    remediation, most of which was carried out. The closure step never ran, so stale
    MANIFEST/AUDIT/REMEDIATION files still steer agents. (dated 2026-09-22)
  - Drift concentrates in places no check covers. `llms.txt` lists a different set of seven
    principles from the live site. Marketing says 60+ lessons; there are 40. The tutor's system
    prompt disagrees with the curriculum manifest at every level. (dated 2026-09-22)
  - The workspace already does the deterministic half better: generated registry, validators,
    reachability, token budgets, persisted baton, context profiles. The gaps ZV exposes are at
    **project** level, not vault level. (dated 2026-09-22)
  - None of the three repos has a LICENSE file, despite claims of MIT and CC BY-SA. Adopt ideas
    clean-room; never vendor their SKILL.md text, schemas, or templates. (dated 2026-09-22)
- **As of:** 2026-09 · **Status:** working · **Audience:** `for: agent`

---

## 1. What ZV is

A methodology, an open-source ecosystem, and a movement, all authored by Erika Flowers. It is
opinionated about approach and agnostic about tools (in practice, Claude Code-centric).

- **Seven principles** (live-site set): Work in the Medium · Boundaryless by Nature · The Medium
  is the Message · The Purpose of a System is What It Does (Beer's POSIWID) · Design and Build are
  the Same Act · Dissolve the Hyperspecialization · Venture Past the Possible. On top sits a
  "Principle Zero": build from what's around you.
- **Eight-phase pipeline**, each phase shown twice, as the timeless practice and "the ZV way":
  problem framing → market research → customer research → JTBD → ideation → prototyping (the
  prototype *is* the product) → validation → build + ship. The loop claim is that validation
  feeds back into the problem brief and the JTBD.
- **Operator model**, from "Zero Stage to Orbit": the pipeline is a multi-stage rocket whose
  stages mostly exist to carry translation overhead. ZV removes the launch: one operator plus a
  named agent crew (strategist, frontend, backend, researcher, and others) in one continuous loop.
- **Positioning:** the methodology sits beneath Double Diamond, Lean, and Agile. It says *why*
  decisions get made, not *how* the process runs.

## 2. Tooling

**Investiture** (scaffold plus skill chain, v1.5, 2026-04-12):
- **Doctrine files** have a declared reading order: `VECTOR.md` (why: audience, problem, knowns,
  unknowns, stage, assumptions, definition of done), then `CLAUDE.md` (contributor onboarding),
  then `ARCHITECTURE.md` (where things go). A `/vector/` tree holds research, decisions (ADRs),
  and audits.
- **Doctrine chain:** `backfill` bootstraps the doctrine from a survey of the codebase. It tiers
  evidence (config beats code, code beats naming) and leaves `[OPERATOR: …]` markers where a
  human must decide. `doctrine` lints the spec: completeness, contradictions across documents,
  and declared structure vs. what's on disk. Its drift verdict is "update one of them".
  `architecture` enforces only the rules the project itself declared.
- **Audit chain:** `preflight` (a quick reconnaissance card) → `manifest` (an inventory that
  describes but never judges) → `repo-audit` (eight vectors, severity levels, mandatory
  commendations) → `remediate` (self-contained phase prompts ordered by risk, each with
  non-goals, verification, rollback, and bail points) → `verify-remediation` (tri-state ledger
  RESOLVED/DEFERRED/OPEN, then a go/no-go on resuming).
- **Optional skills:** crew (a manifest for multi-agent sprints: owned paths, inputs and outputs,
  do-not-touch lines, critical path), handoff (views of state per role), validate, interview, and
  synthesize (pre-registered signals, then two-gate propose → diff → apply), brief
  (Known/Bet/Disproven), adr, changelog.
- **Six research schemas** (persona, JTBD, assumption, interview, competitive, blue ocean) with
  prefixed IDs and a draft/confirmed/invalidated status. They are permissive and have no typed
  cross-references.
- **Update CLI** with ownership classes (replace/merge/preserve/createIfMissing). It pulls an
  unpinned branch head, keeps no hashes, and overwrites local skill edits.
- **Verified mechanical defects:** a preflight size check that can never fire. A personalization
  script that silently does nothing because its placeholders no longer exist. Producer and
  consumer skills that disagree on AUDIT format and on where REMEDIATION.md lives. A remediate
  skill told to commit with no shell tool. Two frontmatter dialects.

**Labrador** (pre-beta, no public repo): middleware that assembles four context layers per turn
(cartridges, knowledge base with pinning, memories, and documents that can be promoted into the
knowledge base). A per-response **context sparkline** shows which sources contributed and their
token counts, under a fixed 40k budget filled by relevance. The transferable part is that receipt,
not the pgvector store; dense retrieval stays deferred in this workspace.

## 3. Training (The Open Vector)

- Free. **6 levels / 40 lessons / 11 approach guides**: Orientation → Foundation → The Medium →
  The Pipeline → Orchestration → Auteur. Content is markdown plus a manifest; sign-in only
  tracks progress.
- **Pedagogy:** concept lessons are kept separate from numbered "IKEA-instruction" runbooks with
  copyable templates. Knowledge checks are unscored (13 of 40 lessons have them; none in L04–L05).
  Your work is the credential. The capstone counts as done when a live URL reaches another person.
- **Most harness-relevant content (L04 Orchestration plus the approach guides):**
  - A briefing file needs identity, stack, conventions, an architecture map, and rules with
    reasons; keep it under about 200 lines. The lessons treat stale briefings as "confident
    wrongness".
  - Crew charters: lens, owned and forbidden paths, duties. Start with a builder, add a reviewer,
    add a planner only on evidence.
  - Work contract-first in parallel, and default to sequential.
  - Four gate types, selected by the type of change.
  - A fresh-context, read-only reviewer.
  - Staged prompts that open with the last verified state.
  - A three-section status ledger (Done / In Progress / Next).
  - Evolve your checklist by what it actually caught.
  - A gap interview at session end ("what would have helped at the start?").
  - Rule of three before extracting a framework; principles, then patterns, then primitives.
- The Claude-powered tutor runs on a hand-written system prompt listing lesson titles, with no
  retrieval. It has drifted from the manifest at every level.

## 4. What the dogfood shows

| Worked | Failed |
|---|---|
| AUDIT.md with stable IDs, file:line evidence, "conditional CRITICAL" plus a named manual check, commendations | Closure never ran: no statuses, REMEDIATION.md left in place, MANIFEST.md months stale and still in the reading order |
| REMEDIATION.md phases: self-contained, risk-ordered, rollback, bail points, preserve-list, named human decision gates | The Phase 6 output fails Phase 6's own "every path exists" check (the checklist was read, not run) |
| CLAUDE.md as a map (stack, prohibitions, reading order) | Name overload drives drift: three different sets of "Seven Principles", three meanings of "Investiture", CLAUDE.md described as both persona and onboarding |
| Content-as-data layer | New pages bypass it (no lint); facts restated per module with different values |

Pattern: **audits are events, not gates.** Nothing triggers them, and their scope misses
machine entry points (llms.txt), generated inventories, and restated facts.

## 5. Transferable patterns (clean-room) → where they land

The full mapping, with homes, detectors, and waves, is in the harness plan:
[zero-vector-harness-plan](../../07-projects/19-workspace-brain/notes/zero-vector-harness-plan_2026-09-22.md).
The high-leverage set:

1. **Project intent declaration** (problem, audience, knowns, unknowns, stage, out-of-scope,
   seeded assumptions), bounded to one screen and placed so it doesn't duplicate intent-spec,
   NORTHSTAR, or SESSION-STATE.
2. **Spec-lint plus declared-vs-reality drift** for project doctrine. The verdict is "update one
   of them"; severity scales with project stage.
3. **Finding ledger** with stable IDs and tri-state status. Closure is triggered by a gate, not by
   memory. Plans are archived, never deleted.
4. **Self-contained phase packets** with non-goals, verification, rollback, and bail points,
   ordered by severity within risk band.
5. **Role charters as data** with owned path globs, plus a check that the diff stays inside
   declared scope, extending intent-spec task rows.
6. **Research records** with provenance status kept separate from epistemic status (#04
   vocabulary), typed references, and invalidation cascades.
7. **Machine entry points generated from or validated against the canonical source.** Our own
   `llms.txt` is subject to this too.
8. **Artifact lifecycle class plus freshness stamp** (current-state / snapshot / append-only /
   ephemeral).
9. **Commendations → preserve-list** with an expiry, so product pivots re-baseline it.
10. **Gap interview at session end**, routed through self-improve.

## 6. Do not import

- Prompt-only "enforcement", and audit skills that auto-commit. Profiles decide conduct:
  employer repos are branch → PR → human review.
- The "zero handoff / solo auteur" ideology over employer governance. Handoffs also carry
  distributed scepticism; adversarial verification and independent measurement stay primary.
- Framing design systems as "translation overhead". Adopt ZV's mechanisms, not its view of DS
  roles.
- Verbatim template defaults (stack opinions injected into every project), hand-maintained
  summaries, and copy-based distribution without hashes.
- Any ZV text, schema, or template, verbatim (no license).

## 7. Access notes (2026-09-22)

`robots.txt` allows all crawlers and points to `llms.txt`. There was no CAPTCHA, bot wall, or
AI-crawler block on any ZV property or on Substack. The only guard seen is a per-IP rate limit on
ZV's own Claude chat endpoint.
