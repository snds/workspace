---
name: research-synthesis
description: >
  Turns appraised sources into claims a reader can act on: each claim tied to the sources that
  support it, agreement counted only among independent sources, disagreements named rather than
  averaged, a framework #04 tier per decision-facing claim, and what evidence would change the
  answer. Use for evidence synthesis, conflicting evidence, stating confidence, or writing up a
  research finding.
aliases: [research-synthesis]
triggers: [evidence synthesis, conflicting evidence, state the confidence, how sure are we, weigh the evidence]
tier: spoke
domain: research
hub: lead-research
prerequisites: [lead-research]
defers_to: [framework-04]
spec_version: "2.2"
---

# Research Synthesis

Stages 7–8 of [[19-research-operating-model]]. The confidence language is #04's; this spoke adds
none.

## From sources to claims

1. **Extract** each source's claims in a table: claim, source, kind, date, strength.
2. **Cluster** claims that say the same thing; check the cluster's sources are independent
   ([[research-foundations]] §3). Echoes collapse to one.
3. **Weigh** each cluster: how many independent sources, how good, how recent, how big the effect.
4. **Name the disagreements:** which sources say otherwise, and what divides them (method, date,
   population, definition, interest).
5. **Write the claims** in plain sentences, each with its citations.

## State confidence

For each decision-facing claim, a #04 tier and one line of why:

- **Tier 1 · Evidenced:** three or more independent, appraised sources agree.
- **Tier 2 · Industry-supported:** documented practice, standards or published landscape.
- **Tier 3 · Single high-value:** one source whose weight is obvious.
- **Tier 4 · Expert judgment:** reasoned, not externally confirmed.
- **Tier 5 · Preference / untested.**

Then the finding's `confidence` (`high` / `medium` / `low`) follows #19 §5. Always add **would
change if:** the evidence that would move the tier. A finding that can't name one is a belief.

## Conflicting evidence

Don't average. Report the camps, then one of:

- **Resolvable:** the conflict comes from method, date or population; say which side the
  question's context favors.
- **Open:** the field disagrees; say so, with the best case on each side.
- **Artifact:** one side is weaker on appraisal; say why it carries less weight.

## Mistakes to avoid

- Vote counting: five weak studies outvoting one strong one.
- A confident summary of a D1 search.
- Dropping the inconvenient source instead of explaining it.
- Claims with no "would change if".

## Related
- hub → [[lead-research]]
- peer ↔ [[research-literature-review]] · [[research-retro]] · [[research-scoping]] · [[research-source-appraisal]]
