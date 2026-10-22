---
title: Citing sources in research findings
tags: [research, citations, sources, evidence, provenance]
triggers: [citations, citing sources, sources, evidence, reference list]
created: 2026-10-22
updated: 2026-10-22
status: working
confidence: high
sources: [Booth et al., The Craft of Research (4th ed., 2016); Chicago Manual of Style (18th ed., 2024)]
related_skills: [lead-research, research-source-appraisal, research-synthesis]
related_projects: [26-synapse]
---

# Citing sources in research findings

## For future agent
- **TL;DR:** Cite every claim from outside, as close to its origin as you actually read, with
  enough to find it again: who, when, what, where, and the identifier. Say how you checked it. A
  bare URL is not a citation ([[epistemic-standards]] §2).
- **As of:** 2026-10 · **Status:** timeless principle; the format details below are a house style.

## The rule

1. **Every outside claim cites.** In-line numbers `[1]` pointing to a numbered `## Sources` list.
   `09-tools/research-check.py` checks every number resolves.
2. **Cite what you read.** Read the summary, not the paper? Cite the summary, and the paper "as
   cited in" it.
3. **Enough to find it again:** author or publisher · year · title · where (journal, site,
   archive) · identifier (DOI, arXiv id, ISBN, URL, archive reference) · version for software and
   standards.
4. **Say how it was checked:** `Checked by search <date>`, `Opened <date>`, or `From training
   knowledge; not re-checked`. Honesty about access is part of the citation; an agent that couldn't
   open a page says so.
5. **One claim, the right source.** The source must support the sentence as written (judged at
   review, #19 §4 gate 7).

## The house format

```
1. <Author(s) or publisher>. (<year>). <Title>. <Where>. <identifier>. <how checked, date>.
```

Archives: repository, collection, box/folder, item, date. Software: project, version or tag, file
or section, date. Standards: body, number, version, status (draft or final), date.

## What a citation can't fix

A citation shows where a claim came from, not that the claim is right. Appraise first
([[research-source-appraisal]]); count independent sources only ([[research-foundations]] §3).

## Sources
1. Booth, W. C., Colomb, G. G., Williams, J. M., Bizup, J. and FitzGerald, W. T. (2016). *The
   Craft of Research*, 4th ed. University of Chicago Press. Checked by search 2026-10-22.
2. *The Chicago Manual of Style*, 18th ed. (2024-09). University of Chicago Press. Checked by
   search 2026-10-22.

## Related
- [[19-research-operating-model]] · [[lead-research]] · [[dated-claims]] · [[quotes-and-copyright]]
