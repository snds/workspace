---
title: Remediation fixture
kind: remediation
status: open
profile: personal-solo
approval: approved 2026-01-02 by Pat
---

# Remediation — synthetic widget repo

## Outcome

Every finding from the synthetic widget audit is RESOLVED with a closure, or DEFERRED with a revisit.

## Northstar

The synthetic audit report `widget-audit_v1.0_2026-01-01.md`.

## Recon

## Findings

| id | sev | status | origin | observed | expected | evidence | closure | closed_by | revisit | risk |
|---|---|---|---|---|---|---|---|---|---|---|
| F-001 | High | OPEN | widget-audit#A1 | the build script ignores lint errors | a lint error fails the build | scripts/build.sh:12 | C-001 | - | - | low |
| F-002 | Medium | RESOLVED | widget-audit#A2 | the README lacks setup steps | the README has setup steps | README.md | C-002 | abc1234 | - | |
| F-003 | minor | DEFERRED | recon | src/big.py is above the repo's p99 line count | split below p99 | the recon card | - | not worth it before v2 | on: the v2 branch opens | high |

### Closures

- C-001: measure: python3 09-tools/lint_gate.py --check
- C-002: judgment: Pat

## Preserve

| glob | why | until |
|---|---|---|
| migrations/** | applied migrations are history: never edit one | on: a squash release |

## Fidelity / acceptance checklist

- [ ] T1 lint gate -- measure: python3 09-tools/lint_gate.py --check

## Task graph

| id | role | skill / specialist | isolation | depends_on | status | writes | forbids | evidence |
|---|---|---|---|---|---|---|---|---|
| T0 | coordinator | intent-coordination | n/a | - | | docs/INTENT-remediation.md | | approved |
| T1 | implementor | | worktree | T0 | | scripts/build.sh, 09-tools/lint_gate.py | migrations/** | lint gate passes |

## Packets

### T1 — Make lint errors fail the build

- outcome: `scripts/build.sh` exits non-zero when lint reports an error.
- context: The build pipes lint output to a log and carries on.
- findings: F-001
- acceptance: a planted lint error makes the build exit 1; a clean tree exits 0
- last verified state: 1111111111111111111111111111111111111111
- non-goals: changing the lint rules themselves
- verification: `python3 09-tools/lint_gate.py --self-test`
- rollback: discard the branch; nothing else changes
- bail point: the fix needs a change under migrations/
- previous attempts: none

## Changelog

- 2026-01-02 — Pat: created
