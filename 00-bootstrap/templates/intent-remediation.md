---
title: Remediation spec
kind: remediation
status: open             # open | closed (closed is refused while any finding is OPEN)
created: YYYY-MM-DD
profile: personal-solo   # personal-solo only; employer remediation stays on stdout (see intent-spec)
northstar:               # the audit report(s) this register carries
approval: pending        # pending | approved YYYY-MM-DD by <name> [note] | approved via PR <n> | waived (<reason>)
blocked_by:              # optional: another remediation spec that must not be Unfit or Blocked
---

# Remediation — <repo or scope>

## Outcome

Every finding is RESOLVED with a closure a verifier can re-run, DEFERRED with a reason and a revisit,
or OPEN with a packet.

## Northstar

Pointers to the dated reports. They are never edited; this register is the current state.

## Recon

Run `python3 09-tools/intent-run.py init --recon --repo <repo> --spec <this file>`; the card lands here.

## Findings

| id | sev | status | origin | observed | expected | evidence | closure | closed_by | revisit | risk |
|---|---|---|---|---|---|---|---|---|---|---|
| F-001 | High | OPEN | <report-slug>#<ID> | <what is true now> | <what should be true> | <path:line or command> | C-001 | - | - | low |

### Closures

- C-001: measure: python3 09-tools/<tool>.py --check

## Preserve

| glob | why | until |
|---|---|---|
| <path/**> | <why it must not change> | on: <trigger> |

## Fidelity / acceptance checklist

- [ ] The register is lint-clean -- measure: python3 09-tools/intent-run.py lint --spec <this file>
- [ ] RESOLVED closures still pass -- measure: python3 09-tools/intent-run.py lint --spec <this file> --run-closures

## Task graph

| id | role | skill / specialist | isolation | depends_on | status | writes | forbids | evidence |
|---|---|---|---|---|---|---|---|---|
| T0 | coordinator | intent-coordination | n/a | - | | <this file> | | this spec approved |
| T1 | implementor | | worktree | T0 | | <paths> | <globs> | |
| V1 | verifier | mission-fit | read-only vs implementor tree | T1 | | none | | `intent-run verdict --branch <b> --run` |

## Packets

### T1 — <title>

- outcome: <what should exist when the task is done>
- context: <why, in two sentences a cold agent can use>
- findings: F-001
- acceptance: <checkable>
- last verified state: <sha>
- non-goals: <what not to touch>
- verification: `python3 09-tools/<tool>.py --check`
- rollback: discard the branch
- bail point: <when to stop and report blocked>
- previous attempts: none

## Open decisions / blocked-on

-

## Changelog

- YYYY-MM-DD — created
