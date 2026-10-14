---
title: Synapse — Measurement
type: plan
project: 26-synapse
status: draft
updated: 2026-10-14
---

# Measurement

**TL;DR:** Every run of Create, Import or the scanner produces a scorecard. Release gates are numbers, not impressions. The test set starts with a pinned snapshot of your workspace, the north star. It also includes generated workspaces, deliberately broken copies with an answer key, and workspaces in other formats. The gates below are starting points. Stage 0's first scan sets the real baselines.

## What we measure

| # | Metric | The question it answers | How it's measured | Starting gate |
|---|---|---|---|---|
| 1 | **Coverage** | Did every file land somewhere? | Files mapped, or excluded with a written reason, ÷ all files | 100% accounted for; at least 99% mapped for your workspace |
| 2 | **Edge fidelity** | Were the relationships kept? | Precision and recall of edges (frontmatter edges, wikilinks, load chains), source against output | Recall: at least 99% for hard edges, 97% for soft |
| 3 | **Structural validity** | Does the output pass every check? | All model checks plus your existing validators | 0 errors |
| 4 | **Routing equivalence** | Does the same request load the same skills? | A fixed set of requests: every trigger phrase, requests mined from your session logs, and hand-written edge cases. Ordered load sets compared. | At least 95% exact. Foundations-first holds 100% of the time. |
| 5 | **Close-out equivalence** | Do the same lenses run after work? | Lens sets per request, compared | At least 95% |
| 6 | **Token cost** | Is it cheaper or the same? | Session floor, median and 95th-percentile load set, worst case, against your current budgets | No regression above 5% |
| 7 | **Determinism** | Same input, same output? | Run twice and compare, ignoring timestamps | 100% identical |
| 8 | **Idempotence** | Is the output already clean? | Import the output again and count new proposals | 0 |
| 9 | **Scanner recall and precision** | Does the scan find real problems and avoid false ones? | Seeded broken copies with an answer key | Recall at least 90%, precision at least 80% |
| 10 | **Scan stability** | Does the scan give the same answer twice? | Overlap of findings across two runs on the same snapshot | At least 90% |
| 11 | **Agent dependence** | Are plain rules catching more over time? | Share of findings caught by deterministic checks | Rises every release |
| 12 | **Task equivalence** | Can the output do the same work? | A fixed set of real tasks run by an agent against source and output, graded by a rubric with your spot checks | Equal or better on at least 90% of tasks. Run per release, not per commit. |
| 13 | **Review load** | How much does a person have to check? | Proposals per 100 files and the share you accept | Tracked; acceptance should rise |

## Test workspaces (the corpus)

| Set | What it is | Where it runs |
|---|---|---|
| **T1: Your workspace** | A snapshot at a pinned commit, in a sandbox folder. Employer project notes stay inside it and never enter any shared corpus. | Your Mac only, on demand and before each release |
| **T2: Generated workspaces** | About 10 profiles, including `wsx`'s "Priya Nair" persona, a work-only engineer, a personal-only hobbyist, and a mixed user with three personas | CI on every change |
| **T3: Seeded breakage** | Copies of T1 and T2 with scripted damage: a hub edge removed, a knowledge entry orphaned, a skill duplicated, a wrong tier, a stale date, employer text in a personal area, a load-chain cycle, a missing tool manifest. Each carries an answer key. | CI. T1-based copies stay local. |
| **T4: Other formats** | A plain Obsidian vault, a repo with only `AGENTS.md`, a Cursor rules repo, a Claude Code skills folder, an old flat `wsx` workspace | CI |

## The scorecard

- **Saved as JSON per run,** plus a readable page.
- **Shown in the app** under Health → Create and import, with trends across runs.
- **Every failed gate links to its evidence:** the files, edges or requests that differed.

```text
sy score <source> <output>        compare an import or generation with its source
sy score --corpus T2,T3,T4        run the CI corpus
sy score --corpus T1              your snapshot, local only
```

## What we reuse

| Existing piece | Used for |
|---|---|
| `evaluate-skill-routing.py` | Routing equivalence, metric 4 |
| `evaluate-surface-trajectories.py` | Per-app behaviour checks |
| `test-validators.py` | Proving each check catches what it should |
| `workspace-harness.py` token lane | Token cost, metric 6 |
| `wsx` `VALIDATION.md` contracts | The first T2 profiles and their expected results |

## Rules for the gates

- **Gates only go up** after a baseline is set. Lowering one needs a written decision in the [decision log](decisions.md).
- **A release can't ship** with a failed gate on T2, T3 or T4. T1 failures block until you have reviewed them.
- **Every miss becomes a test.** A scanner miss found later is added to T3 with its answer.
