---
name: research-computing
description: >
  Research in computing and software: weighing papers against official docs, source code,
  changelogs, issue trackers and standards (RFCs, W3C, WHATWG, Unicode); versions and how fast
  claims decay; benchmarks that do and don't reproduce; artifact evaluation; empirical software
  engineering standards; prior art and library comparisons. Use for technical research, a library
  or tool comparison, benchmark claims, prior art, or "does X support Y".
aliases: [research-computing]
triggers: [technical research, library comparison, benchmark claims, prior art search, does it support, empirical software engineering]
tier: spoke
domain: research
hub: lead-research
prerequisites: [lead-research]
related: [eng-foundations]
spec_version: "2.0"
---

# Research: Computing and Software

The field changes monthly, and the best evidence is often code, not prose.

## Field profile

- **Fast decay:** a claim about a tool is true for a version. Always record the version and date
  ([[dated-claims]]).
- **Docs lag code:** official docs describe intent; the source and the changelog describe reality.
- **Vendor benchmarks favor vendors.** Reproduce or find an independent one.
- **Blog posts copy each other:** check the date and whether it predates the version you use.

## The evidence ladder for "does X do Y"

1. **Run it** (a minimal test against the version you'll use): Tier 1 for that version.
2. **Source code and tests** at a tagged release.
3. **Changelog and release notes**; then **issues and pull requests** (open bugs, known limits).
4. **Official docs** for the version.
5. **Standards** where behavior is specified (IETF RFCs, W3C, WHATWG, Unicode): what *should*
   happen; implementations may differ.
6. **Papers** for algorithms and evaluations; **blog posts and Q&A** last, dated.

## Benchmarks

Ask: same hardware, same versions, same workload, warmed up, repeated, variance reported, code
published? ACM's artifact badges (available, functional, reproduced) signal how far a paper's
results were checked. Without published code and data, a benchmark is Tier 4.

## Empirical software engineering

For research *about* software practice (studies of teams, surveys, repository mining), the ACM
SIGSOFT Empirical Standards set per-method expectations, and snowballing guidelines cover the
literature search ([[research-literature-review]]).

## Prior art

Search patents (Google Patents), papers (DBLP, ACM DL, arXiv cs), and code (repository search) for
the idea under several names. Old mailing lists and RFCs often hold the first version of an idea.

## Mistakes to avoid

- A capability claim without a version.
- Trusting docs over a failing test.
- Comparing benchmarks run on different hardware.
- A three-year-old blog post as current practice.

## Sources
- Ralph, P. et al. (2020). Empirical Standards for Software Engineering Research. ACM SIGSOFT.
  arXiv:2010.03525 (v2 2021-03). Checked by search 2026-10-22.
- ACM. Artifact Review and Badging (current version). acm.org. From training knowledge.

## Related
- hub → [[lead-research]]
- peer ↔ [[research-industry]] · [[research-mathematical]]
