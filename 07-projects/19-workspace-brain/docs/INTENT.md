---
title: Intent spec
status: active
created: 2026-09-04
profile: personal-solo
lane:
northstar: https://intentapp.dev
approval: approved 2026-09-04 by Sean
---

# Intent spec — living-spec runner + optional Intent app

## Outcome

A portable coordination kernel exists at `09-tools/intent-run.py` so agents follow a living spec (approval gate, waves, worktrees, checklist measures) without depending on the Intent GUI. On this Mac, Intent.app can be installed from GitHub releases when Sean wants the shell.

## Northstar

[intentapp.dev](https://intentapp.dev) protocol: coordinator spec, isolated implementors, independent verifier. Vault doctrine: [[17-intent-coordination-operating-model]].

## Fidelity / acceptance checklist

- [x] `intent-run.py doctor` exits 0 -- measure: python3 09-tools/intent-run.py doctor
- [x] `intent-run.py gate` on this spec exits 0 -- measure: python3 09-tools/intent-run.py gate --spec 07-projects/19-workspace-brain/docs/INTENT.md
- [x] Write-quality validator chain green -- measure: python3 09-tools/validate-integrity.py
- [x] Routing corpus includes living spec -- measure: python3 09-tools/evaluate-skill-routing.py --check

## Task graph

| id | role | skill / specialist | isolation | depends_on | status | evidence |
|---|---|---|---|---|---|---|
| T0 | coordinator | intent-coordination | n/a | - | verified | spec approved this session |
| T1 | implementor | intent-coordination | same-tree | T0 | verified | vault files + intent-run.py |
| V1 | verifier | mission-fit | read-only | T1 | verified | validator chain |

## Waves

- Wave 1: land doctrine + runner in this checkout (same-tree; not a parallel writer).
- Wave 2: optional `install-app` on Voyager-2.local.

## Open decisions / blocked-on

- Intent.app install is optional; runner is the portable contract.
- Do not auto-commit employer repos. This spec is `personal-solo`.

## Changelog

- 2026-09-04 — created and approved from Sean's integrate-or-script instruction
