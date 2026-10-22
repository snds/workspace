---
name: research-mathematical
description: >
  Research in mathematics: establishing a result's status (proved, conjectured, refuted, open),
  finding whether something is already known under another name, searching zbMATH, MathSciNet,
  arXiv and the OEIS, reading and checking proofs, small-case computation as evidence, and formal
  verification in proof assistants. Use for "is this known", a theorem or proof search, checking a
  proof, or finding the original source of a result.
aliases: [research-mathematical]
triggers: [is this result known, proof check, theorem search, oeis, mathematical literature]
tier: spoke
domain: research
hub: lead-research
prerequisites: [lead-research]
related: [science-foundations]
spec_version: "2.0"
---

# Research: Mathematics

Mathematics has the strongest kind of evidence, a proof, and the subtlest ways to be wrong about
whether one exists.

## Field profile

- **Status is everything:** proved, proved under an assumption, conjectured, disproved, open.
  Popular sources blur these. State the status and who established it.
- **Names drift:** one result has several names and notations across fields and decades. Search by
  structure, not only by name.
- **Rediscovery is common:** "new" results are often old ones in another field's language.
- **Proofs can be wrong:** published proofs get corrected; long proofs may be accepted slowly.

## Finding whether it's known

1. **Compute small cases** and search the sequence or values in the OEIS; a match points to the
   literature.
2. **Search the reviews:** zbMATH Open (free) and MathSciNet index nearly all published mathematics
   with reviews; search by subject class (MSC) as well as words.
3. **Search preprints:** arXiv's math sections for recent work.
4. **Ask the formal libraries:** a result in Lean's mathlib (or another proof assistant's library)
   is checked by machine.
5. **Trace to the original:** cite where it was first proved, not only a textbook.

## Checking a proof

Pólya's questions still work: understand the problem, find the connection between data and
unknown, carry out the plan checking each step, look back. Then: test it on small cases; look for
the case it skips; check each cited lemma's hypotheses; read the reviews of the paper. For high
stakes, formal verification settles correctness, not significance.

## Evidence that isn't proof

Numerical evidence, heuristics and "it's true for the first billion cases" are Tier 3–4 for a
universal claim. Say so. Some famous conjectures held for enormous ranges and failed later.

## Mistakes to avoid

- Calling a conjecture a theorem because it's widely believed.
- Missing a result because it lives under another field's name.
- Trusting a proof's conclusion without checking its hypotheses fit your case.
- Citing a textbook as the origin of a result.

## Sources
- Pólya, G. (1945). *How to Solve It*. Princeton University Press. From training knowledge.
- zbMATH Open (zbmath.org) and the OEIS (oeis.org); the Lean mathlib community
  (leanprover-community.github.io). From training knowledge; access not re-checked.

## Related
- hub → [[lead-research]]
- peer ↔ [[research-computing]] · [[research-scientific]]
