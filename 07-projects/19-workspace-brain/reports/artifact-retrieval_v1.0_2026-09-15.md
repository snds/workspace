---
title: C2 — the artifact registry moves behind a CLI; session floor down 32%
version: "1.0"
date: 2026-09-15
surface: Claude Opus 5 + Claude Code (Mac desktop app)
sha: 69e52ae
status: applied — session floor 21,697 → 14,778; budget lowered to lock it
companion: automation-second-wave_v1.0_2026-09-15.md
---

# Artifact retrieval v1.0 — 2026-09-15

**Evidence-grade legend:** `VERIFIED` · `INFERRED` — every number below is measured by
`09-tools/workspace-harness.py --tokens`, re-runnable, not asserted.

`06-context/artifact-registry.md` cost **6,942 tokens** and CLAUDE.md read-order item 4 told
every agent to read it. It is a structural index of known files — the exact shape of thing
that should be queried. This is the same mistake already fixed twice in this workspace
(`skills.registry.json` → `skill-loadset.py`; `08-knowledge/_INDEX.md` → knowledge-hints plus
the router parsing the index server-side), left standing in a third place.

---

## 1. What it cost, and what it costs now

| Call | Tokens |
|---|---|
| read the file (the old read-order item 4) | **6,942** |
| `--list` — every group and entry name | 575 |
| `--path 07-projects` | 513 |
| `artifact-find.py "session state"` | 514 |
| `artifact-find.py "lcars"` | **100** |

Even the broadest call is a **92% reduction**; a real lookup is 99%.

| Measure | Before | After |
|---|---|---|
| session floor | 21,697 | **14,778** (−6,919, −31.9%) |
| worst-case legal request | 62,110 | **55,191** |
| banned-ingest multiple | 1.4× | 1.6× (the legal path got cheaper, so skipping routing costs relatively more) |

## 2. `09-tools/artifact-find.py`

Positional terms search name / path / group / purpose, scored so a name hit outranks a
prose hit. `--path` filters by folder fragment, `--list` prints the whole map at 575 tokens,
`--json` for machines, `--limit` to widen.

A no-match prints where to go instead (`vault-retrieve.py` for content) rather than an empty
result — the registry indexes known artifacts, not everything, and a bare "no results" invites
the agent to conclude nothing exists.

**`--check` is half the tool.** A retrieval layer is only as good as the structure it reads.
If entries drift out of the `- **Purpose**:` / `- **Last modified**:` shape, queries begin
missing *silently* — strictly worse than the whole-file read it replaced, because the failure
is invisible. So the thing that queries the file also polices it: every entry parseable, a
purpose to match on, a `YYYY-MM-DD` to age against, no duplicate names. Live: **36 entries,
all complete.**

The check runs in CI and in `/session-end` step 4, immediately after the step that *writes*
to the registry — which is where format drift would be introduced.

## 3. Locking the saving

A saving that can be silently undone is a saving you will pay for twice. Three things hold it:

1. **`session_floor` budget lowered 25,000 → 17,000.** Reverting the read order costs
   14,778 + 6,942 = **21,720**, which now fails CI.
2. **A harness self-test assertion** that the ceiling actually sits in that gap —
   `reverted > BUDGETS["session_floor"] >= measured`. Verified non-vacuous: raising the
   ceiling to 99,000 makes the self-test fail.
3. **The `avoided_by_retrieval` line** in the token report, so the 6,942 stays visible as a
   thing being *avoided* rather than disappearing from the accounting entirely. A saving you
   stop measuring is a saving you stop having.

## 4. Contract changes

Four files: `CLAUDE.md` read-order item 4 (read → query, with the commands), `AGENTS.md`
read-order item 9 (one terse clause — it is auto-loaded), `_CONTEXT.md` navigation table, and
`/optimize` step 7, where a whole-file read is left **correct and annotated as such**: a full
audit is the one caller that legitimately needs every entry.

Writing to the registry at session-end is unchanged. The index still has to be current; only
the reading moved.

## 5. What this does not do

It does not shrink the registry, and it should not — the file is the source of truth and
`/optimize` reads it whole on purpose. It does not touch the next two largest floor items
(`AGENTS.md` at 7,691 and `user-preferences.md` at 2,331); both are genuinely always-on
content rather than indexes, so the same trick does not apply and pretending otherwise would
just move cost somewhere unmeasured.

And it cannot make an agent obey the new read order. The budget catches a reverted *contract*;
it cannot catch a model that ingests the file anyway. That is the same limit as everywhere
else here — injection is not compliance.

## 6. State

21 harness gates green · connections 8/8 · every token budget met · 48/48 matcher cases ·
14/14 trajectories · vault-health 0/0 · ruff clean · registry 36/36 entries queryable.
