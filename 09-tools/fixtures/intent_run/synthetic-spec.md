---
title: Synthetic wave fixture   # a recorded comment
status: active
created: 2026-01-01
profile: personal-solo # c
lane:
northstar: notes/northstar.md
approval: "approved 2026-01-01 by Fixture — chat 'go' (synthetic; parentheses stay)"
wave: 0
blocked_by: x#F-003
---

# Intent spec — synthetic wave fixture

Synthetic fixture for `intent-run.py --self-test`. It mirrors the features a wave spec uses:
`path[a, b]` write selectors, `@Tn` references, brace globs, `human:` measures, a measure followed
by `-- signal:`, an escaped pipe in a cell, a HELD named set, and an approval with parentheses.
Every path and name here is invented.

## Outcome

Two tools and one table exist on `main`, merged by the integrator.

## Interface contracts

- **HELD:**
  - `held/**`;
  - `secrets/policy.json` (rows: coordinator only);
  - the body of `mem/rule.md`;
  - `gen/registry.json`. It changes only through generators run by the integrator.

## Fidelity / acceptance checklist

- [ ] tool self-test -- measure: python3 09-tools/tool.py --self-test -- signal: exit 0
- [ ] (human) reviewer signs off -- measure: human: the reviewer records the sign-off in the handoff
- [ ] merges stay in scope -- measure: python3 09-tools/intent-run.py scope-audit --spec held/INTENT-fixture.md --wave-merges

## Task graph

| id | role | skill / specialist | isolation | depends_on | status | writes | forbids | evidence |
|---|---|---|---|---|---|---|---|---|
| T0 | coordinator | coordination | n/a | - | | held/INTENT-fixture.md | all paths outside own writes | approval line |
| T1 | implementor | alpha (foo\|bar) | worktree | T0 | | tools/alpha.py, data/table.json[rows.*.cov.A1, outputs], fixtures/alpha/** | all paths outside own writes, HELD | self-test log |
| T2 | implementor | beta | worktree | T0 | | tools/beta.py, docs/{one,two}.md, notes/beta.md[Section] | all paths outside own writes, HELD | self-test log |
| T9a | implementor | integrator | worktree | T1, T2 | | tools/test-validators.py, .gitignore, mem/**, gen/registry.json | task-owned files change only through merges | merge shas |
| T9b | implementor | integrator | worktree | T9a | | @T9a | as T9a | merge sha |
| T3 | implementor | fix round | worktree | T9b | | @T1, @T2 | all paths outside the owning task's writes | finding per commit |
| V1 | verifier | review | read-only | T3 | | none | everything | findings register |

## Waves

- Wave A: T1 and T2 in parallel; T9a merges both.

## Changelog

- 2026-01-01 — created (synthetic)
