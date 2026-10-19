---
type: fact
description: Sean's personal GitHub account (snds) has had a payment method and an Actions budget since 2026-10-19, so private-repo CI keeps running past the free 2,000 minutes, up to the budget
created: 2026-10-19
confidence: high
relations: { relates-to: ["[[github-actions-private-repo-minutes]]"] }
---

## For future agent
- **TL;DR:** `snds` has a payment method and an Actions budget (added by Sean on 2026-10-19). Private-repo CI runs past the 2,000 free minutes a month and stops at the budget.
- **As of:** 2026-10 · **Status:** current

Before that date the account had no payment method. On 2026-10-19 GitHub refused every Synapse job for the rest of October, because the free minutes had run out. The budget's amount is in Sean's GitHub settings (Billing and licensing → Budgets and alerts), not here.

A budget isn't permission to spend. Private repos still follow the cadence in [[github-actions-private-repo-minutes]]: Linux on every push, macOS and Windows nightly when something changed.
