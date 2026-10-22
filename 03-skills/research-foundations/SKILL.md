---
name: research-foundations
description: >
  Context-free first principles of research in any field: what a claim is, what counts as a
  source, how evidence differs from assertion, independence, base rates, falsifiability,
  provenance and dating. Load before the research hub or any research spoke. The ideas that
  framework #04's tiers, framework #15's validity gates and every domain's method assume.
aliases: [research-foundations]
triggers: [research methodology, epistemics, what counts as evidence, primary vs secondary source, evidence hierarchy]
tier: foundation
domain: research
surfaces: ["*"]
related: [data-foundations, product-foundations, science-foundations]
spec_version: "2.0"
---

# Research Foundations

The handful of ideas every research method rests on, in every field. Each domain spoke applies
them; none restates them. The confidence language is framework #04's; the operating model is #19.

## The ideas

**1. A claim is a sentence that could be wrong.** "The API returns JSON" can be checked; "the API
is good" can't until "good" is defined. Before searching, turn the ask into claims that evidence
could support or refute. A question with no possible wrong answer isn't ready for research.

**2. A source is a chain, not a point.** Every source got its claim from somewhere: an observation,
an experiment, a document, another source. Primary sources stand at the start of the chain
(the dataset, the archive letter, the proof, the code); secondary sources interpret primaries;
tertiary sources summarize secondaries. Cite as close to the start as you actually read, and say
which link you read.

**3. Independence is what makes agreement count.** Three sources agreeing is strong only if they
reached the claim separately. Ten news stories quoting one press release are one source. Trace
agreement back to its roots before counting it ([[04-research-and-evidence-framework]]'s rule of
threes depends on this).

**4. Base rates come first.** How often is a claim like this true? Most new findings in noisy
fields don't replicate; most vendor benchmarks favor the vendor; most "first" claims in history
have precedents. Start from the base rate and let the specific evidence move you.

**5. Absence of evidence is weak evidence of absence, and only after a real search.** "I found
nothing" means something only when the search could have found it. Say what was searched.

**6. Everything has a date.** A claim is true *as of* something: when it was observed, published or
last checked. Facts about the world drift; principles drift slower. Record which kind a claim is
([[dated-claims]]).

**7. Strength and confidence are different questions.** How big is the effect, and how sure are we
it's real? A tiny, certain effect and a large, uncertain one call for different decisions. Report
both.

**8. Disagreement is data.** When good sources disagree, the disagreement is part of the finding.
Name the camps, what divides them, and what evidence would settle it. Don't average them away.

## Mistakes to avoid

- Searching before the question can be wrong.
- Citing the summary as if you'd read the original.
- Counting echoes as independent confirmation.
- Reporting "no evidence" after a search that couldn't have found any.
- Recording a claim with no date.

## Related
- applies-in ← [[lead-research]]
