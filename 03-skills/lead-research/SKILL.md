---
name: lead-research
description: >
  Leads research in any field: takes a question, works out how deep it deserves, proposes more or
  less depth with reasons, profiles the field's pitfalls (science, mathematics, history,
  computing, qualitative and social, industry and markets), runs the search, appraises sources,
  synthesizes with a stated confidence tier, cites and dates every claim, and ends with a retro that
  feeds what the approach taught back into the workspace. Hub for the research network under
  framework #19. Use for "research this", a literature review, "what does the evidence say",
  deep research, or a research finding to write up. User research with participants routes to
  ux-research-synthesis; statistics and experiments to lead-data-scientist.
aliases: [lead-research]
triggers: [research this, literature review, what does the evidence say, research finding, deep research, research question, evidence review]
tier: hub
domain: research
area: research
prerequisites: [research-foundations]
related: [ux-research-synthesis, ia-research-methods, pm-discovery-research, lead-data-scientist, self-improve]
rigor_role: command-hub
defers_to: [framework-04, framework-15, framework-19]
spec_version: "2.2"
---

# Lead Research

**Hub** for research in any field. Owns the execution protocol, the depth call and the done-gates
([[19-research-operating-model]]). Spokes own method depth. Confidence language is #04's; statistics
are #15's. Load [[research-foundations]] first.

## Execution protocol (the verbs)

Run these in order. Stages 1–3 and 10 always run; for a D0 answer each can be one sentence.

1. **Frame** — restate the question as claims that could be wrong; name who it's for and what it
   serves. → [[research-scoping]]
2. **Scope** — pick a depth tier (D0–D4); give its cost and what it can't claim; **propose more or
   less depth** when the ask and the stakes disagree. Ask before moving two tiers or spending real
   time. → [[research-scoping]]
3. **Profile** — name the field's pitfalls and load its method spoke (below).
4. **Plan** — sources, terms, inclusion rules, a stopping rule. → [[research-literature-review]]
5. **Search** — gather with provenance and dates. → [[research-literature-review]]
6. **Appraise** — kind, reliability, date, independence; drop the weak. → [[research-source-appraisal]]
7. **Synthesize** — claims tied to sources; disagreements named. → [[research-synthesis]]
8. **State confidence** — a #04 tier per decision-facing claim. → [[research-synthesis]]
9. **Report** — at the agreed depth, in the shape below.
10. **Retro** — what the approach taught the workspace. → [[research-retro]]

## Spokes

| Spoke | Load when |
|---|---|
| [[research-scoping]] | Every ask, first: framing, depth tiers, the propose-more-or-less call, domain profiling |
| [[research-literature-review]] | D1 and up: planning and running the search, snowballing, review types, PRISMA-style logs |
| [[research-source-appraisal]] | Judging any source: lateral reading, provenance, retractions, preprints, independence |
| [[research-synthesis]] | Turning sources into claims: conflicting evidence, confidence tiers, what would change the answer |
| [[research-scientific]] | Natural and health sciences: study designs, replication, effect sizes, preregistration |
| [[research-mathematical]] | Mathematics: a result's status, finding known results, checking proofs, formal verification |
| [[research-historical]] | History and the humanities: archives, source criticism, historiography, anachronism |
| [[research-computing]] | Computing and software: papers vs docs vs code, benchmarks, versions, standards, prior art |
| [[research-qualitative]] | Qualitative and social research from sources: interviews, thematic analysis, reporting standards |
| [[research-industry]] | Industry, markets, policy: grey literature, vendor claims, landscape scans |
| [[research-retro]] | Every finish: the approach's lessons into the workspace |

Load one domain spoke, two when the question spans fields; never all of them. Elsewhere:
participant research → [[ux-research-synthesis]]; IA methods → [[ia-research-methods]]; product
discovery → [[pm-discovery-research]]; statistics → [[lead-data-scientist]].

## The report

```markdown
# <the question, as asked>

**Answer.** <two or three sentences, the claim and its tier>
**Depth.** D<n> · <what this tier can't claim> · as of <YYYY-MM-DD>
**Confidence.** <#04 tier> — <why, in one line> — would change if <evidence>

## Findings
<claim> [1][2]. <claim> [3].

## Where sources disagree
<the camps, what divides them>

## Method
<what was searched, how sources were chosen, what was left out>

## Sources
1. <Author or publisher>. (<year>). <Title>. <Where>. <link or identifier>. Accessed <date>.

## Retro
<one line or more: what the approach taught; where it was recorded>
```

## Done-gates and measurement

The gates are #19 §4. Measure before calling a finding done:

`python3 09-tools/research-check.py <finding.md>` — checks the shape: depth and confidence stated,
every source dated and identified, numbered citations resolve to sources, quotes within 15 words, a
retro present. `--self-test` runs its planted fixtures. Whether each claim is *supported* by what
it cites is judged, not measured: the reviewer reads the passage.

## Absolute bans

Citing what wasn't read · uncited outside claims · undated claims about things that change · a D1
reported with D3 confidence · echoes counted as independent · quotes over 15 words · participant
data in the vault · skipping the retro. (#19 §6.)

## Contrast

**Bad.** *"Studies show dark mode reduces eye strain."* No source, no date, no tier; "studies"
could be one blog post.

**Good.** *"Evidence that dark mode reduces eye strain is weak (Tier 4): the two controlled studies
found (2019, 2022) measured reading speed, not strain, and disagree [1][2]. As of 2026-10. Would
change with a study measuring strain directly."*

**Why.** The good version can be checked, shows its depth, and says what would move it.

## Related
- foundation → [[research-foundations]]
- spoke → [[research-computing]] · [[research-historical]] · [[research-industry]] · [[research-literature-review]] · [[research-mathematical]] · [[research-qualitative]] · [[research-retro]] · [[research-scientific]] · [[research-scoping]] · [[research-source-appraisal]] · [[research-synthesis]]
- peer ↔ [[ux-research-synthesis]]
