---
type: decision
description: @shadcn/lint is a product-repo design-system lint service, independent of vault validators and of eslint-off-system; token-tier overlay lives beside it, not inside either.
created: 2026-09-15
confidence: high
relations:
  builds-on: ["[[decision-lint-narrow-or-not-at-all]]", "[[llm-safe-design-system-expressiveness]]"]
  relates-to: ["[[shadcn-lint-token-tiers]]", "[[agent-output-rails]]", "[[figma-tailwind-token-pipeline]]"]
---

## For future agent
- **TL;DR:** Do not fold `@shadcn/lint` into `workspace-harness.py`, `validate-integrity.py`, or
  `09-tools/eslint-off-system/`. Product repos run `npm run lint:ds` via host configs
  (`hosts/cds.config.mjs`, `hosts/centric-ui.config.mjs`, `hosts/proto.config.mjs`) wrapping
  `eslint.ds.config.mjs`. Wave 1 errors are `no-raw-colors` + `ds-lint/no-tier-leakage` only.
  CDS published packages are baseline 0. cui/proto ratchet existing debt. Overlay-first;
  theme reset later. Oxlint-only is not a complete gate.
- **As of:** 2026-09 · **Status:** current

## Context — what forced a choice
We already have two lint families: vault graph validators (narrow, markdown, CI-gated) and
`eslint-off-system` (hex + arbitrary utilities for packs like LCARS). shadcn-bound apps need a
third thing — a theme-aware, agent-shaped linter that knows components, variants, and `@theme`.
[shadcn-ui/lint](https://github.com/shadcn-ui/lint) is that engine. Merging it into either
existing family would either (a) make vault CI depend on Node + a product theme, or (b) pretend
regex hex rules can replace theme discovery.

Our Tailwind mapping made a second problem: primitives, shade aliases, and CDS
`--color-cds-*` back-compat names are real `@theme` (or `@theme inline`) tokens so
utilities exist. Proven on cds `packages/tokens/semantic.css`: `--color-cds-blue-500`
is declared there. Upstream `no-raw-colors` then treats `bg-cds-blue-500` as on-system.
Following upstream SETUP.md ("enable no new rules") ships that false-green.

## Decision — what we chose
Stand up `09-tools/shadcn-lint/` as its own service. Canonical entry is
`eslint.ds.config.mjs` plus a per-repo host file. Wave 1 CI errors are
`shadcn/no-raw-colors` and `ds-lint/no-tier-leakage` (restyle/arbitrary/inline
are off until a later PR). CDS published packages must stay at baseline 0.
centric-ui and proto freeze today's count in `baseline.json`. Overlay-first;
`@theme { --color-*: initial }` is a later product-CSS PR. ESLint is the
CI-stable runner. Oxlint-only is incomplete. Close-out keeps an honest SKIP to
product `lint:ds`.

## Rationale — why, and what we rejected
Rejected: adding `@shadcn/lint` to the write-quality gate list (wrong corpus). Rejected: extending
`eslint-off-system` with restyle/theme rules (no component or `@theme` reader; different job).
Rejected: relying on `no-raw-colors` `deny` patterns (declared tokens stay legal). Rejected:
forking `@shadcn/lint` (policy + overlay is enough; upstream stays an npm bump). Rejected:
following upstream SETUP "no new rules" (false-green on `bg-cds-blue-500`). Rejected:
theme-reset in the same PR as the linter (breaks remaining `bg-cds-*` in docs).

## Consequences — what this commits us to
Product install is a per-repo PR (employer: `centric-engineering`). Until a repo copies the
folder and runs `lint:ds` **with** `eslint.ds.config.mjs`, the overlay is unenforced there.
Adopting `design-system.lint.json` alone is the skip path this decision forbids.

Install PRs (2026-09-15): cds [#41](https://github.com/cpes-software/cds/pull/41)
merged (packages baseline 0), proto [#81](https://github.com/cpes-software/saas-plm-prototype/pull/81)
merged (ratchet 5410). centric-ui [#398](https://github.com/cpes-software/centric-ui/pull/398)
open (ratchet 988; do not agent-merge). Proto CI lint:ds job uses
`npm ci --ignore-scripts`. Knip hosts must list `eslint/ds-lint/**/*.{js,mjs}`
as entry and `@typescript-eslint/parser` as a direct dep.
