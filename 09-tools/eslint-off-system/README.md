# eslint-off-system

Reusable ESLint rules that make **off-system values inexpressible** in product
repos. Doctrine: [[llm-safe-design-system-expressiveness]] + [[agent-output-rails]].

This is **not** a vault-wide ESLint. Each product repo owns its config and
allowlists its token SSOTs. Copy or import these rules; do not invent a second
grammar here.

## Rules

| Rule | Blocks |
|---|---|
| `no-raw-hex` | Hex / rgb() / hsl() / oklch() color *literals* in JS/TS |
| `no-arbitrary-tailwind` | Tailwind arbitrary values (`bg-[#…]`, `p-[17px]`, `w-[123px]`) in `className` strings |

## Wire into a product repo

```js
// eslint.config.js
import js from '@eslint/js';
import tseslint from 'typescript-eslint';
import offSystem from '../path-to-workspace/09-tools/eslint-off-system/index.js';
// or: copy the folder into ./eslint/off-system and import from there

export default tseslint.config(
  js.configs.recommended,
  ...tseslint.configs.recommended,
  {
    files: ['src/**/*.{ts,tsx}'],
    plugins: { 'off-system': offSystem },
    rules: {
      'off-system/no-raw-hex': 'error',
      'off-system/no-arbitrary-tailwind': 'error',
    },
  },
  {
    // Token / palette SSOTs may declare hex once.
    files: ['src/constitution/tokens.ts', 'src/**/palette.ts'],
    rules: {
      'off-system/no-raw-hex': 'off',
    },
  },
);
```

Prefer reading hex from the token table (`TOKENS['frame.amber'].hex`) over
literals in components. CSS `var(--token)` is out of scope for these JS rules;
add Stylelint later if CSS debt matters.

## LCARS

`~/Projects/lcars-generative-interface` vendors a copy under `eslint/off-system/`
and allowlists `constitution/tokens.ts` + `catalog/system/live-t3.ts` (pack
palette). Schematics use `TOKENS[…].hex`.
