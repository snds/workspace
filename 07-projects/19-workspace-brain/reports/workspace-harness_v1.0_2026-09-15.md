---
title: Workspace harness — adversarial review of the first-wave pass, and the detector that replaces re-reviewing it
version: "1.0"
date: 2026-09-15
surface: Claude Opus 5 + Claude Code (Mac desktop app)
sha: 64797a7
status: applied — all three lanes green; CI extended; 16 defects found, 16 fixed
companion: workspace-automation-review_v1.0_2026-09-11.md
---

# Workspace harness v1.0 — 2026-09-15

Second opinion on the 2026-09-11 first-wave automation pass (A1/A2/A3/A6/A7), run against
the live tree rather than against the report that described it. **The pass was directionally
right and left the repository failing its own gates.** Both CI failures were introduced by
the work that added the gates.

The durable output is not this report. It is `09-tools/workspace-harness.py`, which asks the
two questions the existing validators structurally cannot: *can a cold agent on another
surface reach this?* and *what does reaching it cost?* Those are where Cursor kept missing
skills, so they now have a detector instead of a review.

---

## 1. What the review found (all fixed this session)

Ordered by severity. Every row was found by running something, not by reading.

| # | Defect | Evidence | Fix |
|---|---|---|---|
| **1** | **`main` was CI-red.** `validate-workspace.py` exit 1 — `08-knowledge/design/plain-language.md` added 2026-09-14, never indexed. Write-quality gate 3 (cross-link continuity), committed. | `validate-workspace.py` | Indexed with a full `Triggers:` list |
| **2** | **`test-validators.py` was CI-red — a clock bomb.** `test_stamp_age_parses_heading_and_yaml` hardcoded `date: 2026-09-11` and asserted age ≤ 1. Green the day it was written, red every day after. A detector that fails with the calendar rather than with defects. | `AssertionError: 4 not less than or equal to 1` | Dates computed relative to `today`; asserts the parser, not the calendar |
| **3** | **`vault-health.py` could not resolve any note→skill edge.** It keyed the link index on file *stem*; every skill is `<name>/SKILL.md`, so every skill indexed as `"skill"`. Three real edges read as dangling; every other note→skill edge was unverifiable. `validate-integrity.py` already had the dir-name rule — the two resolvers disagreed. | 3 dangling typed edges | `link_name()` mirrors `validate-integrity`; 0 errors |
| **4** | **Four Layer-0 routes pointed at a file that does not exist.** `diagram`, `flowchart`, `how does it work`, `show me the steps` all named a bare `00-context-profiles.md`. The schema validator checks *shape*, so nothing noticed the path. | 4/354 targets missing | Full paths |
| **5** | **A canonical doc nothing could reach.** `02-shared-references/model-routing.md` — `status: canonical`, zero inbound links, zero routes. Findable only by already knowing it existed. | 1 orphan | Reciprocal link from the ontology **plus** four routes; a backlink alone does not make a doc findable |
| **6** | **Ten knowledge entries were indexed but unroutable.** In `_INDEX.md`, no `Triggers:` list, no hint, no `trigger_words` — reachable only by ingesting the index the contract forbids ingesting. | 10/86 entries | `Triggers:` lists added |
| **7** | **`github-guardrails` was reachable by nothing.** `tier: cross-cutting` with no `triggers`; registry CI requires triggers only of hubs and foundations, so it slipped the gate. Its own description says to load it before any Git action. | 1/300 skills | Nine triggers; routing corpus still 48/48 |
| **8** | **`vault-health.py` ran in no gate.** Not in CI, not in the AGENTS.md chain. Its errors were invisible — which is why #3 sat unnoticed. | absent from all workflows | Added to CI and to the enforcement chain |

Two observations worth keeping separate from the list:

- Failures #1, #2 and #8 share one cause: **the pass that installs a gate is the pass least
  able to check it.** Same-model critique is not a detector — already doctrine here
  ([[agentic-error-correction-foundations]]) — and this is the same fact one layer up.
- Failures #4, #5, #6 and #7 share the other: **the validators all verify that a file is
  well-formed; none verified that anything can reach it.** Well-formed and unreachable is the
  exact shape of "Cursor didn't find the skill."

## 2. The harness

`09-tools/workspace-harness.py` — stdlib-only, read-only, deterministic. No network, no
clock dependence, no LLM judgment anywhere in the pass/fail path.

**quality** — runs the documented enforcement chain as subprocesses in AGENTS.md order and
aggregates exit codes. Reimplements nothing; `--check` modes keep it read-only. If a tool
owns a rule, the harness runs that tool.

**connections** — the graph checks nothing else performs:

| Check | Question |
|---|---|
| `layer0-targets` | Does every path a Layer-0 route names exist? (caught #4) |
| `skill-reachability` | Own triggers, or an ancestor in some chain, or a named route? `related` does not count — the contract says it never auto-loads. (caught #7) |
| `hub-edges` | Is the hub's chain an ordered **subsequence** of the spoke's, and does the hub load first? |
| `skill-files` | Does every registry path resolve? |
| `knowledge-routability` | Hint, `_INDEX` `Triggers:`, or `trigger_words`? (caught #6) |
| `index-link-resolution` | Does each `_INDEX` wikilink resolve the way `prompt_route.py` resolves it — `glob("*/<name>.md")`, one level only? |
| `named-detectors` | Does every CLI the contract names as a gate exist? A gate whose binary is gone fails open. |

Two modelling corrections the vault itself forced, both worth recording because the naive
version of each would have made the harness useless:

- **Reachability is three grades, not two.** First run flagged 141 spokes. They are the known
  silent-trigger population and their hub's `SKILL.md` names them, so an agent that opened the
  hub still finds them. Graded `hub-prose` and *reported*; failing 141 every run trains
  everyone to ignore the harness. Hard failures: 1.
- **The chain invariant is subsequence, not prefix, and not the tier enum.** First run flagged
  20 spokes for "hub is tier spoke" — but sub-spokes are legitimate here
  (`threejs-vfx-atmosphere` parents two vfx spokes) and a child may inject its own prerequisite
  ahead of its hub. What must hold is that the parent's order survives inside the child's chain.
  Hard failures after the correction: 0.

**tokens** — prices the traversal, five tiers. `bytes/4`, the vault's own convention
(`compact-sessions.py`), exact if `tiktoken` is ever importable. It is an estimate and every
report says so; the gate is on *relative regression*, which the heuristic tracks faithfully.

| Tier | Measured 2026-09-15 | Budget |
|---|---|---|
| contract floor — `llms.txt` + `AGENTS.md` + worst adapter | 10,305 | 11,800 |
| session floor — + the CLAUDE.md context read order | 21,656 | 25,000 |
| load set p50 / p95 / max | 7,877 / 12,261 / 20,057 | p95 ≤ 14,500 |
| worst-case legal request | 62,069 | 72,000 |
| banned ingest if routing is skipped | 87,154 | — |

The session floor independently reproduces the ~21.6k figure already recorded in
`SESSION-STATE.md` from a different method, which is the only evidence available that the
estimator is not inventing numbers.

The last row is the point of the routing layer: **skipping it costs 1.4× the worst
*compliant* request**, and that is the cheap comparison — against the p50 request it is 11×.

`BUDGETS` is a regression gate. Raising a ceiling is a deliberate, reviewable diff, never a
side effect of the report going red.

**`--self-test`** proves each check can fail on planted defects. A detector that only ever
passes is decor — the standing rule here, and the harness is not exempt from it.

## 3. Attach points (so it is not another unused script)

The first-wave decision memo already names the failure mode: *scripts the next agent never
runs are theater.* Five attachments:

1. **CI** — `workspace-integrity.yml` runs `--self-test` then `--connections --tokens`. The
   quality lane is deliberately **not** run in CI; those jobs already exist and double-running
   them buys nothing.
2. **`vault-health.py` joins the same workflow** — the gap that hid #3.
3. **AGENTS.md enforcement chain** — one clause at the end, terse by the auto-load rule.
4. **`close-out-dispatch.py`** — new `self-improve` row: `--self-test`, `--connections --tokens`,
   `vault-health`. Vault-edit prompts previously fell back to `qa`, whose detectors cannot see
   a skill that became unreachable or a traversal that got more expensive. `self-improve` gains
   `rigor_role: command-hub`, which is what obliges it to name a detector at all.
5. **Layer 0** — seven routes (`workspace harness`, `traversal cost`, `token budget`,
   `reachability`, …) so an agent that never reads this report still finds the command.

## 4. Honest scope — what this pass did not cover

Against the six-phase prompt: phases 1–3 are done for the *structural* layer (map → extend →
sequence → fix → green). Phase 4 gained one mechanism (the harness is what makes
`self-improve` measurable rather than aspirational) but the broader self-improvement question
is untouched. Phases 5–6 are **not** done:

- **Phase 5 (cross-LLM reliability)** — the harness proves the graph is *traversable*; it does
  not prove a given model *traverses* it. That needs per-surface trajectory fixtures, not a
  static check. The one honest claim available today: every route now resolves, every skill and
  knowledge entry is reachable by a machine path, and the cost of doing it right is 1.4× cheaper
  than doing it wrong.
- **Phase 6 (further automation)** — A4/A5/A8/A9 from the automation review remain open, and
  this session added no new candidates to that list.
- **Not attempted:** Figma construction rigor (A8 still waits for a produce that cannot refuse
  `Color/*`), and any visual-QA question. Nothing here touches the visual lane.

## 5. Next

1. A8 Figma bind probe, on the next produce that cannot refuse `Color/*`.
2. Per-surface routing trajectories (phase 5) — the Cursor-misses-a-skill claim deserves a
   fixture, not a memory.
3. Watch the `hub-prose` count (currently 141). It is graded, not failed, on purpose; if it
   grows, the silent-spoke problem is growing with it.
