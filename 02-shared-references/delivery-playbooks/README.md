---
title: Delivery Playbooks — Context, Audience, Medium, Evidence
status: canonical
date: 2026-07-09
tags: [delivery, audience, context, evidence, playbook]
---

# Delivery Playbooks — context, audience, medium, evidence

Standards governing **how work is delivered** — whose work it is, who reads it, what form it
takes, and how it gets proven — as distinct from what gets built. Sibling to
[[artifact-standards]] (naming, versioning, packaging) and consumed by the pre-output gate in
[[06-qa-operating-model]].

**Founding failure (the anti-example these playbooks exist to prevent):** asked for workflow
diagrams for the Media Sentinel project, Claude delivered an engineering-voiced HTML page —
wrong audience, wrong medium, wrong vocabulary. If Sean has to explain the explanation to his
manager, the explanation failed.

---

## The one rule above the others: context is king

Nothing in this directory fires correctly until the **context profile** is resolved — who owns
the work, who reviews it, what Claude is allowed to do with it. Profiles are *declared facts*,
never per-task guesses. Resolve the profile first ([[00-context-profiles]]), then derive
audience, medium, and evidence from it.

---

## Load order

1. **[[00-context-profiles]]** — resolve whose work this is and who reviews it. Always first.
2. **[[01-audience-contract]]** — derive the reader, voice, and explanation altitude.
3. **The medium playbook the request's own words imply:**
   - [[02-diagrams-and-flows]] — workflow / flow / journey / "how does it work" requests
   - [[03-data-and-charts]] — data, results, comparisons, metrics
   - [[04-documents-and-specs]] — specs, briefs, reports, decision records
4. **[[05-validation-harness]]** — for any code-heavy or back-of-house work: the Proofboard
   standard (how Sean verifies the work without reading code).

---

## The pre-delivery gate (four questions, in order)

Run before any artifact, explanation, diagram, or deliverable ships. This gate extends the
critical-eye pre-output gate in [[06-qa-operating-model]] §4.

1. **Context check.** Whose work is this, and who reviews it? Which profile is in force — and
   have I cited it? (Wrong answer here poisons every question below.)
2. **Audience check.** Who reads this — and who do *they* read it out to? Default: a Staff/Lead
   UX designer reporting to design leadership.
3. **Translation check.** Could the reader forward this without translating it? Any unavoidable
   technical term defined in one plain line at first use?
4. **Medium check.** Is the medium what the request's own words imply? A diagram request is
   satisfiable only by a diagram. A "show me it works" request is satisfiable only by
   something visual and runnable, not by test output.

If any check fails, the deliverable isn't ready.

---

## File map

| File | Owns |
|---|---|
| [[00-context-profiles]] | Who owns/reviews the work; repo conduct; identity; IP boundaries |
| [[01-audience-contract]] | Reader, voice, jargon rule, the three-altitude explanation model |
| [[02-diagrams-and-flows]] | Flow diagrams and system pictures — notation, medium, quality bar |
| [[03-data-and-charts]] | Chart and data delivery — routes to the `dataviz` standard |
| [[04-documents-and-specs]] | Document mediums — routes to [[artifact-standards]] |
| [[05-validation-harness]] | The Proofboard: visual, non-destructive verification for code-heavy work |

---

## Enforcement surfaces

A playbook that never loads is shelfware. These are the places that make it fire:

- **Prompt triggers** — `.claude/hooks/dispatcher.py` `TRIGGER_WORDS` surfaces this directory
  when a prompt contains diagram/flow/walkthrough/proofboard/playbook-class words.
- **Pre-output gate** — [[06-qa-operating-model]] §4 carries a context-and-medium check that
  points here.
- **SESSION-STATE** — each project declares its `Context profile` in the Environment block
  ([[_session-state-template|template]]), so the profile travels across sessions and machines.
- **Preferences** — `04-preferences/user-preferences.md` names this directory as the
  operationalization of "target audience: UX/product designer."

## Changing these playbooks

Per [[08-workspace-contribution-framework]]: additive edits, never delete (archive with
provenance), and profile facts change only on Sean's explicit word.
