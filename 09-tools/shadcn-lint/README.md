# shadcn-lint — independent design-system lint service

Agent-facing Tailwind / shadcn lint for **product repos**. Doctrine:
[[llm-safe-design-system-expressiveness]] + [[shadcn-lint-token-tiers]] +
[[decision-shadcn-lint-independent-service]].

This folder is **not** part of the vault toolset. Do not import it from
`workspace-harness.py`, `validate-integrity.py`, or vault GitHub Actions.
`09-tools/eslint-off-system/` stays the hex/arbitrary gate for non-shadcn
packs (LCARS). shadcn-bound apps use this service instead of folding the
two together.

Upstream: [@shadcn/lint](https://github.com/shadcn-ui/lint) (`@shadcn/lint`
on npm). shadcn/ui is **not** required. Tailwind v4 is.

## First breaker (do not invert)

Upstream SETUP.md says: install the plugin, **enable no new rules**, prove
config loads. On our stack that is a false green.

CDS `packages/tokens/semantic.css` declares `--color-cds-blue-500` (and the
rest of the cds-* ramp) in `@theme inline`. Stock `shadcn/no-raw-colors`
treats those as legal theme tokens. `bg-cds-blue-500` therefore passes
until `ds-lint/no-tier-leakage` is on.

`lint:ds` is **`eslint.ds.config.mjs`** plus a **host** file
(`hosts/cds.config.mjs`, `hosts/centric-ui.config.mjs`,
`hosts/proto.config.mjs`) — both plugins, overlay at `error`,
`settings.shadcn.ui` = `@centric/ui`. Do not ship `design-system.lint.json`
through Oxlint `extends` as the only gate. Oxlint cannot load this overlay
today (JS plugin API is alpha and this overlay is an ESLint plugin).

**Enforcement:** CDS published packages (`packages/ui`, `packages/data-table`)
must be at baseline 0. centric-ui and proto run the same overlay at error and
**ratchet** `baseline.json` so existing app-level palette debt cannot grow.
Do not warn-only the overlay.

Theme reset (`@theme { --color-*: initial }`, semantics only) is a **later
product-CSS PR**. Overlay-first. The reset would also drop `bg-cds-*`
utilities that Storybook/docs still use.

## What each layer does

| Layer | Job | Where it runs |
|---|---|---|
| `@shadcn/lint` | `no-restyle`, `no-raw-colors`, `no-arbitrary-values`, `no-inline-styles`, `no-unknown-classes`, `require-static-classes`. Reads the product theme + components. Agent-shaped errors. | Product repo ESLint (`lint:ds`) |
| `design-system.lint.json` | Shared shadcn rule policy + component-directory overrides. Not sufficient alone. | Imported by `eslint.ds.config.mjs` |
| `eslint.ds.config.mjs` | Canonical entry: both plugins + overlay required. | Product `lint:ds` script |
| `ds-lint/no-tier-leakage` | Overlay. Flags Radix steps, shade aliases, `bg-white` / `text-black`, and **`bg-cds-*`**. | Same ESLint run |
| `probe.py` | Matcher + wiring self-test (policy cannot weaken overlay / `no-raw-colors` to warn or off, including ESLint `["error", opts]` tuples; config must set overlay to `error`). | `python3 09-tools/shadcn-lint/probe.py --self-test` — **not** a vault CI gate |

## Install in a product repo

Context profile first: employer repos are `centric-engineering` (branch →
PR, no auto-commit, no vault paste of substance). Personal packs
(`personal-solo`) may copy this folder.

1. Install the upstream plugin. ESLint is the CI-stable runner.

```bash
npm install -D @shadcn/lint eslint @typescript-eslint/parser
```

2. Copy this whole directory to `eslint/ds-lint/` (or another vendored
   path). Do not symlink this workspace into an employer repo.

3. Point `lint:ds` at the host config via `ratchet.mjs`. Keep
   `ds-lint/no-tier-leakage` at `error`. Do not turn `shadcn/no-raw-colors`
   off in `components/ui` overrides.

```json
{
  "scripts": {
    "lint:ds": "node eslint/ds-lint/ratchet.mjs --config eslint/ds-lint/hosts/cds.config.mjs"
  }
}
```

Mint a consumer baseline once, then commit it:

```bash
node eslint/ds-lint/ratchet.mjs --config eslint/ds-lint/hosts/centric-ui.config.mjs --write-baseline
```

Start shadcn restyle/arbitrary rules at `warn` + `--max-warnings` if the
tree is dirty. The overlay and `no-raw-colors` stay `error` from day one —
a warn-only overlay is the same false-green.

4. Agent instruction in the **product** `AGENTS.md` / `CLAUDE.md`:

```md
After making UI changes, run `npm run lint:ds` and fix all errors.
```

5. Host-install gotchas (proven on the 2026-09-15 PRs):

- Install `@typescript-eslint/parser` as a **direct** devDependency. The
  overlay imports it; knip reports it unlisted if it is only nested under
  `typescript-eslint`.
- If the host runs knip, add `eslint/ds-lint/**/*.{js,mjs}` to both `entry`
  and `project`. Listing `@shadcn/lint` in `ignoreDependencies` is the wrong
  fix — the config really uses it.
- Proto (and any repo whose `preinstall` needs a sibling cds) must CI with
  `npm ci --ignore-scripts` for the lint:ds job. Do not leave `vendor/cds`
  as a symlink to a dirty sibling checkout when running local hooks.
  Regenerating `package-lock.json` without a real `vendor/cds` drops
  `@centric/tokens` transitive deps (Material Symbols font) and Pages
  `npm ci` then cannot resolve `icons.css`.
- CDS published packages stay baseline 0. Consumers freeze today's count
  with `--write-baseline` and ratchet; do not boil the ocean in the install
  PR.

## Theme surgery (later, product CSS)

Belt after the overlay. Do not put this reset in the vault.

```css
@theme {
  --color-*: initial;
  --color-primary: var(--sem-primary);
  --color-primary-foreground: var(--sem-primary-foreground);
}
:root {
  --color-blue-10: /* radix primitive, no utility */;
}
```

## What this is not

- Not a substitute for `09-tools/eslint-off-system/` in LCARS.
- Not a vault markdown linter.
- Not permission to paste employer token files into this workspace.
- Not a fork of `@shadcn/lint`. Overlay + policy only.
- Not complete if only Oxlint loads `@shadcn/lint`.

## Self-test (overlay spec + wiring)

```
python3 09-tools/shadcn-lint/probe.py --self-test
python3 09-tools/shadcn-lint/probe.py --classes "bg-primary bg-cds-blue-500"
```
