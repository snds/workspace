---
title: Research Operating Model
tags: [framework, research, evidence, literature-review, research-methods, depth]
governs: [research]
created: 2026-10-22
updated: 2026-10-22
links:
  - "[[04-research-and-evidence-framework]]"
  - "[[15-analysis-operating-model]]"
  - "[[13-domain-rigor-stack]]"
  - "[[lead-research]]"
  - "[[research-foundations]]"
---

# Research Operating Model

*The L1 for research of any kind: a question answered from sources, in any field. It sits beside
[#04 Research and Evidence](04-research-and-evidence-framework.md), which says how sure a claim is
and how hard to push it, and [#15 Analysis](15-analysis-operating-model.md), which owns statistics
and causal claims. This framework says how the work runs, from the ask to the finished finding, and
how each piece of research leaves the workspace better at research.*

---

## The core conviction

**Research is answering a question from sources, at the depth the question deserves, and saying
honestly how sure the answer is. The depth is agreed before the search, not discovered after it.**

Two failures dominate. **Over-research:** a quick question turns into a survey nobody asked for.
**Under-research:** a decision rides on the first plausible page. Both come from skipping the
scoping step. A third failure is quieter: the work ends and nothing about *how* it went is kept, so
the next piece of research starts from zero.

---

## When this framework invokes

- Any ask to find out, look into, review the evidence on, or survey a topic, in any field.
- Any finding written into the vault (`08-knowledge/`), a decision record or a deliverable.
- Any claim in a deliverable that rests on outside sources.

Not this framework: user research with participants (interviews, usability tests, JTBD) runs on
[[ux-research-synthesis]] under [[lead-ux-designer]]; statistics, experiments and causal
identification run on #15. When either appears inside a research task, hand that part over and keep
the rest here.

---

## 1. The pipeline (ordered stages)

| # | Stage | What it produces | Owner skill |
|---|---|---|---|
| 1 | **Frame** | The question in one sentence, who it's for, and the decision or use it serves | [[research-scoping]] |
| 2 | **Scope the depth** | A depth tier (§2), its cost, and a proposal to go deeper or lighter, with why | [[research-scoping]] |
| 3 | **Profile the domain** | What makes this field hard (§3), which method spoke applies | [[research-scoping]] → a domain spoke |
| 4 | **Plan the search** | Sources to try, terms, inclusion rules, a stopping rule | [[research-literature-review]] |
| 5 | **Search and gather** | Candidate sources with provenance and dates | [[research-literature-review]] |
| 6 | **Appraise** | Each source's kind, reliability and date; weak or retracted ones out | [[research-source-appraisal]] |
| 7 | **Synthesize** | Claims, each tied to the sources that support it; disagreements named | [[research-synthesis]] |
| 8 | **State confidence** | A #04 tier per decision-facing claim; what would change it | [[research-synthesis]] |
| 9 | **Report** | The finding at the agreed depth, cited and dated | [[lead-research]] |
| 10 | **Retro** | What the approach taught: workspace improvements, recorded | [[research-retro]] |

Stages 1–3 always run, even for a quick answer; they can take one sentence each. Stages 4–8 scale
with the tier. Stage 10 always runs; it can be one line.

---

## 2. Depth tiers

Depth is a choice made with the person, not a mood. Name the tier, its rough cost, and what it can
and can't claim. The review types map to Grant and Booth's typology of 14 review types (2009).

| Tier | When | Search | Can claim | Can't claim |
|---|---|---|---|---|
| **D0 · Answer** | A fact, a definition, a known result | One or two authoritative sources | The fact, as of its source's date | That nothing contradicts it |
| **D1 · Brief** | Orient someone; a decision with low stakes | A handful of good sources, one pass | The main positions and the best-supported one | Completeness |
| **D2 · Review** | A decision with real stakes; a new area for the workspace | Planned search across source types, snowballing, appraisal | What the evidence says and how strongly | That no study was missed |
| **D3 · Systematic** | High stakes, contested or long-lived; a standard others will rely on | Protocol first, reproducible search, screening log, a PRISMA-style flow | What the full body of evidence supports | Anything outside the protocol's scope |
| **D4 · Original** | The answer isn't in the sources | Sources plus new work: an experiment, an analysis, a proof, archival digging | New knowledge, with its own method's limits | Generality beyond what was tested |

**Propose, don't just obey.** When the ask and its stakes disagree, say so before searching: *"You
asked for a quick look; this decides a platform choice for two years, so D2 is the honest tier. D1
gets you an orientation in a fraction of the time. Which?"* Lighter is a valid answer when the stakes
are low or time is short; then the report says what the lighter tier couldn't claim.

**Ask or proceed.** Proceed at the tier the ask implies when the proposal would change it by one tier
or less and the person isn't reachable mid-task; say which tier you used and why. Ask when the
proposal changes it by two tiers, or when D3 or D4 would spend real time or money.

---

## 3. Domain complexity profile

Every field has its own ways to be wrong. Profile the field before searching. The domain spokes
carry the method; this table is the triage.

| Field | What makes it hard | Method spoke |
|---|---|---|
| Natural and health sciences | Publication bias, replication failures, effect sizes lost in significance, preprints vs peer review | [[research-scientific]] (statistics defer to #15) |
| Mathematics | A result's status (proved, conjectured, refuted), notation drift, proofs that need checking, results rediscovered under other names | [[research-mathematical]] |
| History and the humanities | Primary vs secondary sources, survival bias in archives, anachronism, interpretation contested by school | [[research-historical]] |
| Computing and software | Fast decay, vendor claims, benchmarks that don't reproduce, docs that lag the code, versions | [[research-computing]] |
| Social and qualitative | Small samples read as general, method chosen after the fact, quotes without context | [[research-qualitative]] |
| Industry, markets, policy | Grey literature, marketing posing as evidence, paywalled data, interests behind every report | [[research-industry]] |

A question that spans fields gets the strictest profile of the fields it touches. A question about
people using this product goes to [[ux-research-synthesis]].

---

## 4. Done-gates

A finding is ready for review only when every one holds. The measurement path is
`python3 09-tools/research-check.py <finding.md>` (L3); the judged gates stay with the reviewer.

1. **Framed:** the question, its audience and its use are stated.
2. **Tiered:** the depth tier is named, with what it can't claim.
3. **Cited:** every claim from outside cites a source; every source has a title, a publisher or
   author, a date and a link or a findable identifier.
4. **Dated:** every claim that can go stale says *as of when* ([[dated-claims]]).
5. **Quoted lightly:** no quote over 15 words; the rest in the workspace's own words
   ([[quotes-and-copyright]]).
6. **Confident, honestly:** decision-facing claims carry a #04 tier; the knowledge entry's
   `confidence` field follows from it (§5).
7. **Supported (judged):** each claim is supported by the source it cites, as written.
8. **Retro'd:** stage 10 recorded at least one line, even "nothing to improve".

---

## 5. Confidence: one language

This framework adds no confidence language. **Decision-facing claims use #04's five tiers.** A
knowledge entry's `confidence` frontmatter is the summary of the tiers it rests on:

| #04 tier | Knowledge `confidence` |
|---|---|
| Tier 1 · Evidenced | `high` |
| Tier 2 · Industry-supported, Tier 3 · Single high-value | `medium` |
| Tier 4 · Expert judgment, Tier 5 · Preference | `low` |

A finding on outside sources reaches Tier 1 only when three or more independent, appraised sources
agree. "Independent" means they didn't copy each other: three articles citing one study are one
source.

---

## 6. Absolute bans

- **Citing what wasn't read.** A source known only from another source's summary is cited as such.
- **Uncited outside claims** in anything shipped or recorded.
- **Undated claims** about anything that changes: prices, versions, laws, rankings, people's roles.
- **Laundering the tier:** a D1 orientation reported with D3 confidence.
- **Fake independence:** three echoes of one source counted as three.
- **Long quotes** over 15 words, or close paraphrase that copies a source's structure.
- **Storing identifiable participant data** in the vault (the user-research rule holds here too).
- **Skipping the retro** because the research "went fine".

---

## 7. Research improves the workspace (stage 10)

The content of a finding goes where its subject lives. The *approach* goes to the workspace. After
every piece of research, [[research-retro]] asks what the method taught, not what the topic taught:

- A search path that worked (or failed) in a field → the domain spoke, as a proposed edit.
- A depth tier that was wrong → [[research-scoping]]'s calibration notes.
- A gate that missed a real problem, or fired on nothing → `research-check.py`'s fixtures, or a
  harness proposal for Synapse's `research.finding` (reviewed, D116).
- A gap the same way three times → a rule-of-three row
  (`python3 09-tools/rule_of_three.py add …`), then the smallest fix through [[self-improve]].

Insights about the workspace itself (a skill missing, a route that didn't fire, a check that should
exist) follow [[self-improve]]'s classes; research gives them evidence, never a shortcut past review.

---

## Relationship to other frameworks

- **#04** — confidence tiers and advocacy; this framework uses them and adds none.
- **#15** — statistics, experiments, causal claims; research hands those parts over.
- **#13** — this is research's L1; the instantiation map lists the cluster.
- **#06 / #11** — QA before delivery and the premortem for high-stakes findings still apply.
- **#08** — where findings and their retros are written.

## Skills that carry the mechanics

[[research-foundations]] → [[lead-research]] → [[research-scoping]], [[research-literature-review]],
[[research-source-appraisal]], [[research-synthesis]], [[research-scientific]],
[[research-mathematical]], [[research-historical]], [[research-computing]],
[[research-qualitative]], [[research-industry]], [[research-retro]].

## Sources

- Grant, M. J. and Booth, A. (2009). A typology of reviews: an analysis of 14 review types and
  associated methodologies. *Health Information and Libraries Journal* 26(2), 91–108.
  doi:10.1111/j.1471-1842.2009.00848.x. Checked by search 2026-10-22.
- Page, M. J. et al. (2021). The PRISMA 2020 statement: an updated guideline for reporting
  systematic reviews. *BMJ* 372, n71. doi:10.1136/bmj.n71. Checked by search 2026-10-22.
- Garritty, C. et al. (2021). Cochrane Rapid Reviews Methods Group offers evidence-informed guidance
  to conduct rapid reviews. *Journal of Clinical Epidemiology* 130, 13–22.
  doi:10.1016/j.jclinepi.2020.10.007. Checked by search 2026-10-22.

## Related

- [[04-research-and-evidence-framework]]
- [[15-analysis-operating-model]]
- [[13-domain-rigor-stack]]
- [[08-workspace-contribution-framework]]
- [[lead-research]]
- [[research-foundations]]
