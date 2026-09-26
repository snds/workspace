# Task brief T1: Make lint errors fail the build

You are a coding agent working in the git repository `pat-sample/widget`. This brief is self-contained: everything you need is below, and nothing outside this repository is required. Work on a new branch from the default branch's current tip; never push to the default branch. The findings were verified at commit `1111111111111111111111111111111111111111`; if the tip has moved, confirm they still hold.

## Goal

`scripts/build.sh` exits non-zero when lint reports an error.

## Context

The build pipes lint output to a log and carries on.

## Findings to resolve

- F-001 (High): observed: the build script ignores lint errors · expected: a lint error fails the build · evidence: scripts/build.sh:12

## Scope

- May write: `scripts/build.sh`, `09-tools/lint_gate.py`
- Must not touch: `migrations/**`
- Preserve `migrations/**`: applied migrations are history: never edit one (until a squash release)

## Non-goals

- changing the lint rules themselves

## Acceptance

- a planted lint error makes the build exit 1; a clean tree exits 0
- F-001: a lint error fails the build

## Verify

Run each command from the repository root; every one must exit 0.

- `python3 09-tools/lint_gate.py --self-test`
- `python3 09-tools/lint_gate.py --check`

## Rollback

discard the branch; nothing else changes

## Bail point

Stop and report `blocked` (never a plausible substitute) when: the fix needs a change under migrations/

## Previous attempts

none

## Report back

Reply with the branch name, the commits, each Verify command with its exit code, and the finding ids you believe resolved. If you could not finish, say `blocked` and why.
