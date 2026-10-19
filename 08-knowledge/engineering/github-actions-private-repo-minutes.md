---
tags: [github, github-actions, ci, billing, engineering]
created: 2026-10-19
updated: 2026-10-19
status: stable
confidence: high
sources: [Synapse CI runs 2026-10-15 to 2026-10-19 and its decision D106 (snds/synapse), GitHub Docs read 2026-10-19 — Product usage included with each plan, GitHub Actions billing, Actions runner pricing]
related_skills: [devops-ci-cd, devops-cost-optimization]
related_projects: [26-synapse]
---

# GitHub Actions on Sean's private repos: the free minutes run out fast

**The rule.** A private repo under Sean's personal GitHub account (`snds`) runs its Linux checks on every push and pull request. Its macOS and Windows jobs run less often:

- nightly, and only when the default branch has a commit the last nightly didn't test;
- on a version tag (`v*`);
- on "Run workflow" (`workflow_dispatch`).

Public repos don't need this. Their standard runners are free.

## Why

- **The allowance.** GitHub Free includes 2,000 Actions minutes a month for private repos, and 500 MB of storage. Artifacts and Packages share that storage. The count resets on the 1st of the month.
- **macOS and Windows minutes weigh more.** A macOS minute counts about 10 Linux minutes, and a Windows minute about 2. GitHub's current pages no longer print these weightings. But they match the prices (Linux $0.006 a minute, Windows $0.010, macOS $0.062, as of 2026), and they match what we measured.
- **Rounding.** Each job is rounded up to a whole minute, so many short jobs cost more than they look.
- **Larger runners** (4 cores and up) never use the included minutes.
- **What happened.** In October 2026, Synapse ran Linux checks plus macOS and Windows tests on every push.
  - That used about 1,850 weighted minutes in four days (October 15–19).
  - About three quarters of it was macOS and Windows.
  - GitHub then refused every job until Sean added a payment method.
- **With the rule,** a Synapse push costs about 5 minutes and a nightly about 30.

## How to tell the minutes ran out

- **Every job fails in 2–5 seconds** without starting.
- **The run's annotation** says "recent account payments have failed or your spending limit needs to be increased". That's GitHub's stock wording. It shows up when the free minutes are used up and nothing covers more: no payment method, or a budget with no room left. It doesn't mean a payment failed. Don't repeat it to Sean as "fix your billing" without checking.
- **There's no alert on the account or in the Actions tab.** Read the annotation with `gh run view <run id>`.

## Where to look

- **Sean, on github.com:** profile picture → Settings → Billing and licensing.
  - **Usage** shows minutes by repo.
  - **Budgets and alerts** caps spending; "stop usage when budget limit is reached" keeps the cap hard.
  - **Payment information** holds the card.
- **An agent can't read billing.** The billing API needs the `user` scope, and the `gh` token on Sean's Macs doesn't have it. Don't widen the token for this. Count from the runs instead:
  1. List the month's runs: `gh api --paginate "repos/<owner>/<repo>/actions/runs?created=>=YYYY-MM-01&per_page=100"`.
  2. Fetch each run's jobs: `repos/<owner>/<repo>/actions/runs/<id>/jobs`.
  3. Skip jobs with no `runner_name`, which never started.
  4. Round each job's time from `started_at` to `completed_at` up to a minute.
  5. Weight macOS ×10 and Windows ×2.

## The pattern

A cheap Linux job decides whether the nightly has anything new. The macOS and Windows jobs depend on it. `!cancelled()` lets them run on a tag or a manual run, when the gate itself is skipped.

```yaml
on:
  push: { branches: [main], tags: ["v*"] }
  pull_request:
  schedule: [{ cron: "17 10 * * *" }]
  workflow_dispatch:

concurrency:
  # The event in the group, so a push doesn't cancel the nightly.
  group: ci-${{ github.event_name }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  checks:                      # Linux, every push and pull request
    if: github.event_name != 'schedule'
    runs-on: ubuntu-latest
  changed:                     # the nightly's gate
    if: github.event_name == 'schedule'
    runs-on: ubuntu-latest
    permissions: { actions: read }
    outputs: { run: "${{ steps.compare.outputs.run }}" }
    steps:
      - id: compare
        env: { GH_TOKEN: "${{ github.token }}" }
        run: |
          last=$(gh run list -R "$GITHUB_REPOSITORY" -w ci.yml -e schedule -s completed -L 20 \
            --json headSha,conclusion --jq '[.[] | select(.conclusion == "success" or .conclusion == "failure")][0].headSha // ""')
          if [ "$last" = "$GITHUB_SHA" ]; then echo "run=false" >> "$GITHUB_OUTPUT"; else echo "run=true" >> "$GITHUB_OUTPUT"; fi
  test:                        # macOS and Windows
    needs: changed
    if: >-
      !cancelled() && (github.event_name == 'workflow_dispatch'
      || startsWith(github.ref, 'refs/tags/v')
      || needs.changed.outputs.run == 'true')
```

The working copy is Synapse's `.github/workflows/ci.yml` (D106).

## What this doesn't cover

- **Employer repos.** Their billing and CI rules are the employer's. Change an employer repo's CI cadence only by a PR for its engineers to review.
- **Public repos.** Standard runners are free, so testing every system on every push is fine there.

## Related

- Account state: [[fact-github-actions-billing]] (a payment method and an Actions budget since 2026-10-19).
- Method: [[devops-cost-optimization]] (runner costs, self-hosted break-even), [[devops-ci-cd]].
