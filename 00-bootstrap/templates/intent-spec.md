---
title: Intent spec
status: draft
created: YYYY-MM-DD
profile: personal-solo   # personal-solo | centric-engineering | centric-design
lane:                    # e.g. personal:SEA-NN — omit if not using Open Engine
northstar:               # path or URL — Figma / NORTHSTAR.md / contract
approval: pending        # pending | approved YYYY-MM-DD by <name> [note] | approved via PR <n> | waived (<reason>)
contract:                # paths every parallel implementor codes against; committed before fan-out (H9)
generated:               # globs any task may rewrite (registries, rendered files)
---

# Intent spec — <short outcome name>

## Outcome

What should exist, and where. Do not define success as "the agent finished."

## Northstar

Pointer to designed intent. Constraints that must not drift.

## Fidelity / acceptance checklist

- [ ] <item> -- measure: <command or artifact>
- [ ] <item> -- measure: python3 09-tools/<tool>.py --self-test -- signal: exit 0
- [ ] (human) <item> -- measure: human: <what a person does; never executed>

## Task graph

| id | role | skill / specialist | isolation | depends_on | status | writes | forbids | evidence |
|---|---|---|---|---|---|---|---|---|
| T0 | coordinator | intent-coordination | n/a | - | | docs/INTENT.md | | this spec approved |
| T1 | implementor | | worktree | T0 | | <path>, <dir>/**, <file>.json[<key.path>] | <glob> | |
| V1 | verifier | mission-fit + domain prove | read-only vs implementor tree | T1 | | none | | |

Parallel implementors in one wave must have disjoint `writes` (`intent-run gate` refuses overlaps);
check a branch with `intent-run scope --branch intent/T1`. Add an `enforce` column (`true`) only when
a task's pre-write report should fail `scope --check-path`.

## Waves

- Wave 1 (serial): …
- Wave 2 (parallel after V1): …

## Open decisions / blocked-on

-

## Changelog

- YYYY-MM-DD — created
