---
tags: [design-systems, tokens, lint, ci, llm, agentic, tailwind]
created: 2026-09-02
updated: 2026-09-03
status: working
confidence: medium
sources:
  - "Polar — Building an LLM safe design system (polar.sh/blog/orbit-llm-safe-design-system, 2026-06-16)"
  - "Polar ADR-0004 — Frontend UI is authored with Orbit Box and design tokens (handbook.polar.sh)"
related_skills: [design-engineer, ux-component-library, design-system-ops, ds-advisor, uid-color-for-ui]
related_projects: [19-workspace-brain, 20-lcars-generative-interface]
relations:
  builds-on:
    - "[[component-contracts-and-schemas]]"
    - "[[contracts-first-delivery]]"
    - "[[figma-tailwind-token-pipeline]]"
    - "[[radix-derived-color-system]]"
  relates-to:
    - "[[agentic-ds-context-model]]"
    - "[[ds-ops-governance-notes]]"
    - "[[agent-output-rails]]"
---

# LLM-safe design-system expressiveness

Testimony: Polar's Orbit post (2026-06-16) and ADR-0004. This note keeps the transferable law. It does not adopt StyleX, Polar's `Box`, or a ban on `<div>` as workspace doctrine.

## For future agent
- **TL;DR:** when an LLM authors UI, off-system values must be **inexpressible**, not discouraged. Docs and `CLAUDE.md` are probabilities. CI, types, and lint are the contract.
- **Key claims:**
  - *Timeless:* a design system is a set of **decisions**. `p-4` and `bg-gray-100` are values. `padding="m"` and `background-card` are decisions.
  - *Timeless:* anything written only in English will be weighed against training data and missed. Encode the decisions that matter as types + lint + CI.
  - *Timeless:* an escape hatch (raw `className`, arbitrary Tailwind, inline hex, `dark:` as a second pass) is a crack. Growing `eslint-disable` is a design-system bug.
  - *Dated 2026-06:* Polar implements this with StyleX + polymorphic `Box` + `light-dark()` + custom ESLint. Mechanism is theirs. Law is ours.
  - *Pointer:* token gaps are backloggable; a11y is not. A missing decision becomes a token, not a bypass.
- **As of:** 2026-09 · **Status:** current (LCARS ships `npm run lint` with off-system rules; centric-ui / Davinci still open)
- **Audience:** `for: agent`

---

## The problem that docs cannot fix

LLMs write CSS and Tailwind fluently. They do not know which gray is yours. `p-4`, `p-5`, `p-[17px]`, `bg-gray-100`, `bg-zinc-100`, `text-[#3b82f6]` all parse, all render, all pass ordinary lint. None of them is a syntax error. They are wrong in the way static analysis usually cannot see: they are off-system.

Putting "use our tokens" in `CLAUDE.md` raises the probability. It is not a guarantee. Across thousands of generations the misses pile up.

## The law

1. **Author in decisions, not values.** Intent names (`background-card`, spacing role `m`) are the vocabulary. Hex, raw px, and utility shades live behind those names.
2. **CI is the contract.** If a PR is green, it is safe to merge. If something off-system ships, that is a gap in the rules, not a failure of the author.
3. **Close the unconstrained path.** A typed primitive next to a raw `div` + `className` does nothing. The model will take the open door. One sanctioned layout/style primitive, or an equivalent lint that forbids raw layout utilities, hex, and arbitrary values.
4. **Theme in one pass.** Pair light and dark in the token (`light-dark()` or a single semantic that resolves per mode). Do not ask the model to remember a second `dark:` pass.
5. **Inventory escape hatches.** Treat `eslint-disable` growth as a system bug. A missing token is a backlog item against the system ([[ds-ops-governance-notes]]), not permission to bypass.

## What this workspace does *not* take from Polar

- StyleX as the required styling library. centric-ui and Davinci are Tailwind-shaped. Importing Polar's stack would be another system's conventions.
- A literal ban on `<div>`. Semantics stay. The workspace version is: one sanctioned primitive *or* lint that makes off-token layout/color inexpressible.
- Shipping `@polar-sh/orbit`. That package is Polar's product DS.

The product-repo move (centric-ui, Davinci), when wanted: a small ESLint set for off-token Tailwind, arbitrary values, and raw hex. That lives in the product repo, not this vault. Reusable rules: `09-tools/eslint-off-system/`. **LCARS** (2026-09-03): `npm run lint` with vendored `eslint/off-system` (`no-raw-hex`, `no-arbitrary-tailwind`); allowlists `constitution/tokens.ts` + `catalog/system/live-t3.ts`. Reusable rules: `09-tools/eslint-off-system/`. **LCARS** (2026-09-03): `npm run lint` with vendored `eslint/off-system` (`no-raw-hex`, `no-arbitrary-tailwind`); allowlists `constitution/tokens.ts` + `catalog/system/live-t3.ts`.

## Complements (do not collapse)

| Layer | Job |
|---|---|
| This note | Expressiveness: what an author (human or LLM) is allowed to say |
| [[component-contracts-and-schemas]] | Arbitration: what settles a disagreement without a human |
| [[contracts-first-delivery]] | Boundaries: empty vs broken, written before code |
| [[figma-tailwind-token-pipeline]] | One theme control point |
| [[radix-derived-color-system]] | Contrast as governance over semantics, not primitive mutation |

Docs remain testimony. Generated Figma extracts remain testimony. CI that refuses off-system values is a contract.

## Triggers

`llm-safe`, `inexpressible`, `off-system`, `CI is the contract`, `typed tokens`, `escape hatch`, `light-dark`, `no raw layout`, `Orbit`
