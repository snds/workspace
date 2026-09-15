---
title: Automation second wave — A4, A5, A9 applied; A8 still honestly blocked; two new candidates measured
version: "1.0"
date: 2026-09-15
surface: Claude Opus 5 + Claude Code (Mac desktop app)
sha: 6515bf9
status: applied — A4/A5/A9 landed and wired; A8 deferred with a stated unblock condition
companion: workspace-automation-review_v1.0_2026-09-11.md
---

# Automation second wave — 2026-09-15

Phase 6. Closes the remaining candidates from the 2026-09-11 review, and adds two the first
pass did not have the measurements to see.

**Evidence-grade legend:** `VERIFIED` · `INFERRED` — measured by the commands named inline
(`09-tools/workspace-harness.py`, `uvx ruff check`, `09-tools/validate-evidence-grades.py`),
not asserted.

---

## 1. Disposition of the open candidates

| # | Was | Now | Note |
|---|---|---|---|
| **A4** | nightly.sh wrapper, no cron | **applied** as `09-tools/nightly.py` | Python, not `.sh` — portable-first is an AGENTS core rule and the fleet has a Windows machine. Nothing is scheduled. |
| **A5** | ruff on `09-tools/` in CI | **applied** — `ruff.toml` + a CI job | Narrow ruleset (`E9`, `F`, `I`). 7 real hits, all auto-fixed. |
| **A8** | Figma bind probe | **still blocked** | Needs a real produce that cannot refuse `Color/*`. No such produce this session; manufacturing one would be theater. Unblock condition unchanged. |
| **A9** | analysis-report lint | **applied** as `09-tools/validate-evidence-grades.py` | 1 real violation found and fixed. |
| **A10 / R1–R3** | keep / refuse | unchanged | No reason to revisit. |

## 2. A5 — ruff, and why the ruleset is small

Default-ish ruff over `09-tools/` + `.claude/hooks/` returns **143 errors**; `--select E,F`
returns **402** (395 of them `E501` line-too-long). Both numbers are noise, and a lint that
reports 143 things is a lint everyone routes around.

`ruff.toml` selects `E9` (syntax/IO), `F` (pyflakes — undefined names, unused imports, dead
f-strings), `I` (import order). **7 errors, all auto-fixable**, all fixed. What is deliberately
excluded matters more than what is included:

| Excluded | Count | Why |
|---|---|---|
| `BLE001` blind-except | 40 | Fail-open is the contract — a hook must never block a session |
| `S110` / `S112` try-except-pass/continue | 12 | Same doctrine |
| `PLW1510` subprocess without `check` | 21 | These tools inspect `returncode` themselves, on purpose |
| `E501` line-too-long | 395 | Pure style |
| `EXE001` shebang-not-executable | 29 | Shebangs are decorative; everything runs as `python3 x.py` |
| `RUF100` unused-noqa | 9 | Misfires under a narrow select, flagging deliberate suppressions |

The rule is declared in-repo rather than as a CI flag, so a local run and CI agree.
It caught its author within the hour: two `F541`s in the new A9 lint.

## 3. A9 — a VERIFIED stamp must name what verified it

The vault already has the evidence-grade vocabulary. It is a good convention and it is the
kind that decays quietly: the grades keep appearing, the method that earned them stops being
written down, and a report reads as evidence while being narrative.

Any report using the vocabulary 3+ times must (1) declare the legend or link the standard and
(2) name a re-runnable detector. `03-skills/` is exempt — it *defines* the vocabulary.

Measured before building, which changed the design twice:

- 7 files use grades; 3 fully compliant. **One real violation**
  (`agent-load-miss-review.md`, 11 grades, no legend) — fixed.
- `--strict` adds the six pre-registration fields from [[experiment-validity-baseline]], but
  only for genuinely experiment-shaped documents, and only on **two distinct signals**. The
  first version fired on `process-rigor-gaps` because the word "experiment" appears there
  *as a trigger word in a routing table*. A lint that is wrong by construction is worse than
  no lint, so the gate got narrower rather than the finding getting waved through.

## 4. A4 — the recipe, executable

`nightly.py` is the recipe's steps in one command: `fold` → `rebuild` (mutating; build-related
before build-registry, because the registry hashes what build-related rewrites) → `verify`
(the harness, read-only) → `watch` (advisory) → `commit` (**opt-in**).

Guardrails carried over and enforced in code rather than in prose: report-don't-rewrite,
never invent skills, idempotent, and `--commit` stages an **allowlist** rather than `git add -A`
and refuses outright on a red tree. Nothing schedules it; adding a cron line here would be
enabling by stealth.

## 5. Two candidates the first review could not see

Both come from measurements that did not exist on 2026-09-11.

**C1 — cross-chain trigger collisions (applied).** 1,443 trigger terms; **92 claimed by more
than one skill**. 67 are benign — a foundation and its hub both claim `api contract`, and the
chain loads both anyway. **25 are cross-chain**: `mechanics` is claimed by `game-foundations`
*and* `science-foundations`, so one word drags two unrelated chains into context. Now a harness
check with a **ceiling of 25** rather than a fail-at-zero, because some are correct
(`color blindness` genuinely wants `a11y-visual` and `found-color`). The ceiling makes a new
one a reviewable diff instead of silent growth.

**C2 — `artifact-registry.md` is the largest recurring cost in the vault (queued, not built).**
Session-floor composition, measured:

| Tokens | File |
|---|---|
| **6,942** | `06-context/artifact-registry.md` |
| 7,691 | `AGENTS.md` |
| 2,331 | `04-preferences/user-preferences.md` |
| 1,538 | `CURSOR.md` (worst adapter) |
| 1,117 | `llms.txt` |
| 658 / 608 / 560 / 237 | role-and-context · CRITICAL_FACTS · project-context (head) · session-log (head) |

The single largest item after the contract itself is **a structural index of known files** —
precisely the shape of thing that should be *queried*, not ingested, and the contract currently
says to read it. That is the same mistake already fixed for `skills.registry.json` (→
`skill-loadset.py`) and `_INDEX.md` (→ `knowledge-hints` + the router parsing it server-side).

Deliberately **not** built this session: a retrieval CLI plus a read-order change is a real
piece of work, and starting it at the end of a long session is how half-finished layers get
left behind. Queued with the number attached so the next session starts from evidence.
Estimated saving ~6.9k tokens per session, ~28% of the 21.7k session floor.

## 6. State

15 → 19 harness gates. All green: quality 19/19, connections 8 checks / 0 defects, tokens under
every budget, 48/48 matcher cases, 14/14 trajectories, vault-health 0/0, ruff clean.

## 7. Next

1. **C2** — artifact-registry retrieval CLI + read-order change (~6.9k tokens/session).
2. **A8** — Figma bind probe, on the next produce that cannot refuse `Color/*`.
3. Watch the two graded counters: hub-prose spokes (140) and cross-chain collisions (25/25 —
   **at ceiling**, so the next addition fails CI and forces the conversation).
