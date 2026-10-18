---
type: decision
description: Every store of context has three tiers — current (read every session), recent (read when the question is about lately), long-term (queried on demand, never assumed empty). Batons split by month past 12 KB, with a linked history index; validate-batons.py holds every agent to it; the app fixes batons by itself when nothing is lost; project-recall.py searches one project's tiers.
created: 2026-10-18
confidence: high
relations:
  builds-on: ["[[decision-indexes-are-queried-not-read]]", "[[decision-externalize-everything-to-workspace]]"]
  relates-to: ["[[decision-session-status-card]]", "[[session-end]]", "[[workspace-ontology]]"]
---

## For future agent
- **TL;DR:** Context lives in three tiers. **Current** is what you read every session. **Recent**
  is what you read when the question is about lately. **Long-term** is queried on demand, never
  read whole and never assumed empty. Answer from current; go to recent for "last time" or "this
  week"; go to long-term for anything older, any "when", "why did we" or "what happened with", and
  before ever saying there's no record. One command searches a project's three tiers:
  `python3 09-tools/project-recall.py <project> "<words>"`.
- **As of:** 2026-10 · **Status:** current

## The tiers, store by store

| Store | Current | Recent | Long-term |
|---|---|---|---|
| A project's baton | its **Live handoff** (`SESSION-STATE.md`) | the baton's history section: its newest 5 entries | `history/YYYY-MM.md` beside it, through `history/README.md` (the index) |
| The session log | the head of `06-context/session-log.md` | the rest of `session-log.md` (bounded) and unfolded `06-context/sessions/` fragments | `06-context/session-log-archive.md` |
| Project context | the stubs in `06-context/project-context.md` | its Pending Items | `06-context/project-context-detail.md` |
| Durable facts | — | — | `06-context/memory/` (by its index), `08-knowledge/` (by its hints) |
| The record | — | — | `git log` (every baton commit, back to a project's first) |

## Decision — what we chose
- **Batons split by month past 12 KB** (Sean, 2026-10-18; the workspace app's D98). The workspace app's
  `batons.size` check flags a larger baton; its fix moves all but the newest 5 history entries,
  finished sections, and dated, finished Live handoff notes into `history/YYYY-MM.md`. Nothing is
  dropped. What a rule can't judge (a Live handoff grown into a log) is flagged for trimming.
- **Every split leaves links both ways.** The baton points to `history/README.md`; the index lists
  each month newest first with its entries; each month links back to the index and the baton.
  `09-tools/build-history-index.py` keeps every index current (run by the nightly rebuild, and
  `--check` fails when one is stale), so an index is never hand-maintained.
- **One command per project, not a global index.** `project-recall.py` reads one named project's
  three tiers. It doesn't add projects to `vault-retrieve.py`'s index, which keeps `07-projects/`
  out on purpose (employer projects stay out of any shared index).
- **The workspace app shows the same tiers.** Its Projects timeline labels every entry current,
  recent, long-term or record, and its resume prompt names the long-term index when there is one.
- **Every agent keeps the convention, app or no app** (Sean, 2026-10-18, after an adversarial
  review). `09-tools/validate-batons.py` runs in the harness, CI and the pre-commit lane: a stale
  index, a dangling pointer, or a tracked baton whose `history/` is git-ignored fails; size over
  12 KB warns, and so does the session-start card. `--lossless` proves a hand-made move kept every
  word. The template, `session-end` (Step 2.5), framework 08, the bootstrap and new-project skills
  and every adapter carry the rule. The workspace MCP server refuses hand edits to an index and
  says when a baton it wrote is over 12 KB.
- **Scoped batons count.** A `SESSION-STATE.md` deeper in a project (`docs/<thread>/`) is a baton
  with its own `history/`; every tool above and the app cover it.
- **The app fixes batons by itself** (the workspace app's D100). Its `batons.size` and
  `batons.index` fixes are written without review once the baton has been still for two minutes,
  and only when nothing is lost: every word of the baton and its month files is still there and
  the standing fields read the same. A fix that would lose anything waits for review. Each fix is
  kept as an applied proposal, so it can be undone, and the guard against fighting another writer
  applies.

## Consequences
- A session-start read stays small: the Live handoff and the session-log head, as before.
- "Is there anything about X?" is answered by querying the long-term tier, not by the absence of X
  in what was already read.
- A new store of context needs its three tiers named here before it grows.
