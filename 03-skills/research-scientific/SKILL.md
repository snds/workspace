---
name: research-scientific
description: >
  Research in the natural and health sciences from the published record: reading study designs
  and their evidence level, effect sizes over p-values, replication and the replication crisis,
  preregistration and registered reports, preprints versus peer review, reporting guidelines
  (EQUATOR, CONSORT, PRISMA), and meta-analyses. Statistics and causal identification defer to
  framework #15. Use for "what does the science say", study design questions in a literature
  search, replication, or a meta-analysis.
aliases: [research-scientific]
triggers: [what does the science say, replication crisis, preregistration, meta-analysis, study design quality]
tier: spoke
domain: research
hub: lead-research
prerequisites: [lead-research]
defers_to: [framework-15]
related: [lead-data-scientist]
spec_version: "2.2"
---

# Research: Sciences

Method for the sciences. Statistics, power and causal inference belong to #15 and
[[lead-data-scientist]]; this spoke reads the literature they produce.

## Field profile

- **Publication bias:** positive results get published; null results sit in drawers. A literature
  looks stronger than the truth.
- **Replication:** large replication projects reproduced well under half of findings in some fields
  (Open Science Collaboration 2015, psychology). Treat a single unreplicated finding as Tier 3 at
  best.
- **Base rates:** Ioannidis (2005) showed why small studies of small effects in hot fields are
  mostly false. Start skeptical.
- **Preprints:** fast, unreviewed, sometimes later changed. Cite as preprints and check for a
  published version.

## Reading a study

1. **Design** first: randomized trial, cohort, case-control, cross-sectional, case report,
   simulation, lab study. Each has a ceiling on what it can claim.
2. **Size and effect:** sample size, effect size with its interval. A significant tiny effect is
   still tiny.
3. **Preregistration:** was the analysis planned before the data? Registered reports carry more
   weight.
4. **Reporting guideline:** does it follow its field's checklist (EQUATOR network: CONSORT for
   trials, STROBE for observational, PRISMA for reviews)? Missing items hide problems.
5. **Funding and interests:** declared, and who benefits.
6. **Replication and status:** later replications, corrections, retractions.

## Synthesizing many studies

Prefer an existing high-quality systematic review or meta-analysis over your own count. When none
exists, a D2 review with the strongest designs first; a D3 needs the Cochrane Handbook's methods and
GRADE for certainty. Heterogeneity (studies measuring different things) is a finding, not noise.

## Mistakes to avoid

- "A study found" as if one study settles anything.
- Mistaking statistical significance for importance.
- Citing the press release, not the paper.
- Missing a retraction or a failed replication.

## Sources
- Ioannidis, J. P. A. (2005). Why most published research findings are false. *PLOS Medicine*
  2(8), e124. doi:10.1371/journal.pmed.0020124. From training knowledge; not re-checked.
- Open Science Collaboration (2015). Estimating the reproducibility of psychological science.
  *Science* 349(6251), aac4716. doi:10.1126/science.aac4716. From training knowledge; not re-checked.
- Higgins, J. P. T., Thomas, J. et al., eds. (2024). *Cochrane Handbook*, version 6.5.
  www.cochrane.org/handbook. Checked by search 2026-10-22.
- EQUATOR Network. Reporting guidelines library. www.equator-network.org. From training knowledge.

## Related
- hub → [[lead-research]]
- peer ↔ [[research-mathematical]] · [[research-qualitative]]
