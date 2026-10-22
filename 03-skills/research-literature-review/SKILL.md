---
name: research-literature-review
description: >
  Plans and runs the search for D1 to D3 research: choosing the review type (narrative, scoping,
  rapid, systematic), building search terms and sources, inclusion and exclusion rules, backward
  and forward snowballing, a stopping rule, and a search log or PRISMA-style flow that lets
  someone repeat it. Use for a systematic review, a scoping review, a search strategy, snowballing,
  or "what has been written about this".
aliases: [research-literature-review]
triggers: [systematic review, scoping review, search strategy, snowballing, prisma, what has been written about]
tier: spoke
domain: research
hub: lead-research
prerequisites: [lead-research]
spec_version: "2.0"
---

# Research Literature Review

Stages 4–5 of [[19-research-operating-model]]: plan the search, then run it so it could be run again.

## Choose the review type

From Grant and Booth's typology (2009), the ones that matter most:

| Type | Tier | Shape | Use when |
|---|---|---|---|
| Narrative / literature review | D1 | Expert selection, no protocol | Orientation; the reader trusts your judgment |
| Rapid review | D1–D2 | Systematic steps, deliberately cut (one database, one screener) | A decision is due; say which steps were cut (Garritty et al. 2021) |
| Scoping review | D2 | Maps what exists, doesn't judge effect | A new area: what's been studied, how, where the gaps are (PRISMA-ScR) |
| Systematic review | D3 | Protocol, full search, dual screening, appraisal | High stakes; others will rely on it (Cochrane Handbook; PRISMA 2020) |
| Umbrella review | D3 | A review of reviews | Many reviews exist and disagree |

## Plan the search

1. **Concepts:** break the question into two to four concepts (for health questions PICO:
   population, intervention, comparison, outcome; elsewhere: subject, context, outcome).
2. **Terms:** for each concept, synonyms, field jargon, older names, spellings. A search that misses
   the field's own word misses the field.
3. **Sources:** at least two kinds: an index for the field (below), a general scholarly index, and
   for D2+ grey literature ([[research-industry]]).
4. **Rules:** inclusion and exclusion written before reading: dates, languages, study types,
   publication status.
5. **Stopping rule:** when new sources stop adding claims (saturation), or a fixed budget. Write it
   down so "I stopped" means something.

| Field | Where to search first |
|---|---|
| Health and life sciences | PubMed, Cochrane Library |
| Sciences broadly | Google Scholar, Semantic Scholar, OpenAlex, arXiv for preprints |
| Mathematics | zbMATH Open, MathSciNet, arXiv (math), OEIS for sequences |
| Computing | ACM Digital Library, IEEE Xplore, DBLP, arXiv (cs), project docs and repos |
| History, humanities | JSTOR, library catalogs, archives' finding aids, digitized collections |
| Social sciences | SSRN, discipline databases, OpenAlex |
| Industry, policy | Standards bodies, regulators, analyst and NGO reports, filings |

## Snowball

From the best few sources: **backward** (their references) and **forward** (who cites them).
Wohlin's snowballing guideline (2014) is the standard in software engineering and works anywhere.
Two rounds usually saturate a D2.

## Keep a log

For D2: terms, sources, dates searched, hit counts, what was kept and why. For D3: a PRISMA 2020
flow (identified → screened → eligible → included, with reasons at each cut). The log is what makes
"no evidence found" a finding instead of a shrug.

## Mistakes to avoid

- One database, one phrasing, and calling it a review.
- Writing inclusion rules after seeing which sources agree with you.
- Forgetting preprints in fast fields, or trusting them as if reviewed.
- No stopping rule, so the search ends when patience does.

## Sources
- Grant, M. J. and Booth, A. (2009). A typology of reviews. *Health Information and Libraries
  Journal* 26(2), 91–108. doi:10.1111/j.1471-1842.2009.00848.x. Checked by search 2026-10-22.
- Page, M. J. et al. (2021). The PRISMA 2020 statement. *BMJ* 372, n71. doi:10.1136/bmj.n71.
  Checked by search 2026-10-22.
- Higgins, J. P. T., Thomas, J. et al., eds. (2024). *Cochrane Handbook for Systematic Reviews of
  Interventions*, version 6.5. www.cochrane.org/handbook. Checked by search 2026-10-22.
- Garritty, C. et al. (2021). Cochrane Rapid Reviews Methods Group guidance. *Journal of Clinical
  Epidemiology* 130, 13–22. doi:10.1016/j.jclinepi.2020.10.007. Checked by search 2026-10-22.
- Wohlin, C. (2014). Guidelines for snowballing in systematic literature studies and a replication
  in software engineering. *EASE '14*, ACM. doi:10.1145/2601248.2601268. Checked by search 2026-10-22.

## Related
- hub → [[lead-research]]
- peer ↔ [[research-scoping]] · [[research-source-appraisal]] · [[research-synthesis]]
