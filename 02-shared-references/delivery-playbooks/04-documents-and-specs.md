---
title: Documents & Specs — structure serves the second reader
status: canonical
date: 2026-07-09
tags: [documents, specs, reports, delivery]
---

# Documents and specs — structure serves the second reader

Fires when the deliverable is a spec, brief, report, decision record, or any prose document.
Naming, versioning, format selection (`.html` / `.md` / `.pdf` / `.docx`), and packaging live
in [[artifact-standards]] — this playbook adds the audience structure.

---

## Structure rules

- **Lead with the outcome.** The first paragraph answers "what is this and what should I do
  about it." Supporting detail follows for readers who want it.
- **Two-hop structure.** Sean's manager should be able to lift the opening section into their
  own read-out verbatim. For anything longer than two pages, open with a summary block written
  at the plain-english altitude ([[01-audience-contract]]).
- **The three altitudes map to document layers:** summary (plain english) → body (how it
  works, with diagrams per [[02-diagrams-and-flows]]) → appendix (full technical detail).
  Caveats, risks, and assumptions live in the summary, not the appendix.
- **Recommendations are flagged as recommendations,** with the evidence tier named per
  [[04-research-and-evidence-framework]] — expert judgment presented as measured fact is a
  trust failure.
- Design-system documents follow the canonical docs IA already established (get started /
  foundations / tokens / components / patterns) — don't invent a parallel structure.

## Voice

Per the profile lookup in [[01-audience-contract]]. The only engineer-voiced documents are
those living inside an engineering review surface (`centric-engineering` PRs); everything
else is designer-first.

## Pre-delivery checklist

0. Context profile resolved and cited? ([[00-context-profiles]] — always first)
1. Outcome in the first paragraph?
2. Summary liftable by the second reader verbatim?
3. Caveats at the top altitude, not the appendix?
4. Named and versioned per [[artifact-standards]]?
