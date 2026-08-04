---
tags: [career, job-search, positioning, evidence, tooling]
created: 2026-08-03
updated: 2026-08-03
status: working
confidence: medium
sources: [03-skills/job-search-strategist/SKILL.md, 03-skills/job-application-optimizer/SKILL.md, 03-skills/career-ops-job-search/SKILL.md, 03-skills/product-foundations/SKILL.md, 06-context/role-and-context.md]
related_skills: [job-search-strategist, job-application-optimizer, career-ops-job-search, product-foundations, pm-metrics-analytics]
related_projects: []
relations:
  relates-to: ["[[experiment-validity-baseline]]", "[[workflow-patterns]]"]
---

# Career search: positioning decides the outcome, tooling only decides the throughput

## For future agent
- **TL;DR:** the workspace position on job-search work. Order is **strategy, then materials, then
  pipeline**, and it does not reverse. Automation raises throughput; it cannot substitute for a
  decided position, and applied first it industrializes the wrong application. The one hard rule:
  [[role-and-context]] is the only evidence base, and reframing is allowed while invention is not.
- **Key claims:**
  - *Timeless:* volume without positioning is noise. Tailoring a resume before the position is
    decided produces a well-formatted document aimed at nothing.
  - *Timeless:* an automated fit score ranks candidates for your attention, it does not decide. A
    stale profile or CV input produces grades that look rigorous and are not.
  - *Timeless:* keyword alignment that outruns the underlying evidence fails at the first competent
    interview, which is a worse outcome than not passing the filter.
  - *Pointer:* method depth is in the installed agent skills under `~/.agents/skills/`; the
    workspace wrappers own routing only.
- **As of:** 2026-08 · **Status:** current (doctrine at seed time; no outcome data yet, see below)

---

## Why this note exists

Three career skills were reachable from this workspace (a strategy skill, a materials skill, and an
automation pipeline) with no stated position on how they relate. The default failure is to start with
the tooling, because it is the most concrete, and to end up sending many well-formatted applications
built on an undecided position.

**Honest limitation:** this note is doctrine, not measurement. There is no outcome data here yet
(which framings converted, which channels produced replies). When there is, the claims below become
testable and the confidence should move in one direction or the other.

---

## A search is a positioning problem, which is why product-foundations is the prerequisite

The mapping from [[product-foundations]] is direct and worth making explicit, because it changes what
you do first:

| Product principle | Applied to a search |
|---|---|
| Jobs to be done | What progress is the hiring team trying to make? The posting is a symptom of it, not a description of it. |
| Evidence over opinion | Proof (artifacts, outcomes, specifics) beats claims. Confidence is a tier, so name it. |
| The four risks | Value (do they want this?), usability (is it legible on a resume?), feasibility (can you do it?), viability (does the comp and level work?). Most rejections are a value or level miss dressed up as a materials problem. |
| Prioritization under constraint | A pipeline with no "no" is just a list. Deciding what not to pursue is the strategy. |
| Outcomes over output | Applications sent is output. Conversations with decision-makers is the outcome. |

## Route order

1. **Position** ([[job-search-strategist]]). What value, to whom, with what proof. Also the decision
   to skip: a role that does not fit the position is a no, not a lower-priority yes.
2. **Materials** ([[job-application-optimizer]]). Select, order, and reframe real experience so the
   relevant part is legible to this specific reader.
3. **Pipeline** ([[career-ops-job-search]]). Scan, score, batch, track. Only worth standing up once
   1 and 2 are stable, because it multiplies whatever it is given.

Reversing the order is the characteristic failure. It is also the most tempting, because step 3
produces visible activity immediately.

## The evidence rule

[[role-and-context]] is the only source of truth for what Sean has actually done. Reframing means
selecting, sequencing, and re-describing that work for a reader. It does not mean inflating scope,
claiming tool exposure that is not there, or absorbing a posting's vocabulary into claims the work
does not support.

When a stated requirement genuinely is not present, the honest routes are: the adjacent framing (name
the closest real thing and the transfer), a skill-gap plan, or skip the role. Choosing a fourth
option makes the interview the place where it surfaces.

Practical form: when delivering tailored material, state which claims came from
[[role-and-context]] verbatim and which are reframings, so the reframings can be checked before they
are sent.

## Scoring models rank, they do not decide

The `career-ops` pipeline grades offers A-F from ten weighted dimensions. Two failure modes follow
directly, and both are versions of the general measurement problem in
[[experiment-validity-baseline]]:

- **The weights are assumptions, not facts.** They come from a config file. A B+ that matches the
  position can beat an A that does not, so read the dimension breakdown rather than the letter.
- **Garbage in, confident garbage out.** A stale profile or CV input yields grades with the full
  appearance of rigor. Verify both are current before trusting a batch run, and treat any grade
  produced without them as unscored.

## Separation and hygiene

- **Context profile `personal-solo`.** Career work is personal and stays out of employer
  repositories and anything Centric-scoped.
- Company-named research, comp figures, and application drafts do **not** go into tracked workspace
  files. `07-projects/` (gitignored) or `05-artifacts/`.
- The `career-ops` repository itself lives in the platform-relative `Projects` directory, never
  inside this portable workspace.
- Artifacts follow workspace naming (`context_descriptor_vN.N_YYYY-MM-DD.ext`) and are never
  overwritten. A variant per target role is how you later see which framing landed, which is the
  only way this note eventually gets real evidence behind it.
