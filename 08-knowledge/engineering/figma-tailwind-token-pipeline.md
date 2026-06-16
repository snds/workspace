---
tags: [engineering, design-tokens, figma, tailwind, css-cascade]
created: 2026-06-04
updated: 2026-06-04
status: stable
confidence: high
sources: [session-log 2026-06-04, figma-repo-sync-plugin]
related_skills: [figma-plugin-dev, design-engineer]
related_projects: [figma-repo-sync-plugin, centric-ui]
---

# Figma + Tailwind design-token pipeline — hard-won mechanics

Generalizable facts discovered building the figma-repo-sync-plugin's generator-driven
Radix→Figma token migration (2026-06-04). Project-specific detail lives in memory
`project_figma-repo-sync-token-architecture`; these are the cross-project constraints.

## 1. Tailwind v4: an unlayered `:root` overrides `@layer theme` — swap a palette without touching utilities
Tailwind v4 emits its default theme as `@layer theme { :root { --color-blue-500: … } }` and
generates utilities that **reference the var**: `.bg-blue-500 { background: var(--color-blue-500) }`.
CSS cascade rule: **unlayered declarations beat layered ones**, regardless of source order. So a
later, unlayered `:root { --color-blue-500: <radix> }` (e.g. an `@import`ed generated palette)
**overrides the value** and every `bg-blue-500` renders the new color — *no `@theme` edit, no
utility regeneration*. This is how you re-base an entire palette (Tailwind shades → Radix) while
keeping all dev classes working. **Verify the real output** by compiling with the project's own
engine (`@tailwindcss/node` `compile(css,{base}).build([candidates])`) and inspecting which
`--color-*` declaration wins + that utilities use `var()`. Note: `bg-x/opacity` compiles to
`color-mix(in oklab, var(--color-x) N%, transparent)` — so opacity composites the overridden
(Radix) value too. Corollary: custom props in plain `:root` (not `@theme`) set CSS variables but
do **not** generate utilities — so `bg-blue-9` (a non-default name) won't exist as a class unless
added to `@theme`; `bg-blue-500` works only because Tailwind's default theme already declares it.

## 2. Figma `Variable.consumers` is unreliable for usage audits
`variable.consumers` returns **0 even for variables genuinely bound by nodes** inside
component/instance trees (observed across an entire 1300-var file where a parallel node-walk found
769 bound paints). Do **not** judge "is this token used/orphan" by `consumers`. Reliable signals:
- **alias-reference** (walk every variable's `valuesByMode`, collect `VARIABLE_ALIAS` target ids) —
  trustworthy; this is how to tell whether a *primitive* is referenced by a *semantic*.
- **node-walk** of `boundVariables` on scene nodes — what the binding-diag scanner does for paints.
So: primitive orphan-analysis (usage flows through alias-refs) is trustworthy; semantic/component-
token orphan-analysis via `consumers` is not (they're node-bound, which `consumers` misses).

## 3. Two scopes: CSS = full dev compat, Figma = design surface only
Keep the **complete** token set in CSS (every Tailwind class must resolve — shades 50–950, alpha,
all hue families) but **materialize only the design-surface subset as Figma variables**. Shades and
per-hue alpha are dev-compat / `/opacity` concerns → CSS + a parse-time palette map, but NOT Figma
variables (designers pick steps + semantics, never `blue/500` or `blueA/9`). A raw shade class that
*does* appear in generated output should bind to its nearest **step** variable (shade→step map),
not a literal — keeps the artifact fully variable-bound without materializing shades.

## 4. One theme-control point beats two
Semantics must be theme-bearing anyway (surface tokens like `background` point at *different*
primitives per theme: white↔zinc-1, not the same primitive flipping). Given that, keep **primitives
flat/theme-agnostic** (name-encode light/dark as distinct constants in a single-mode collection)
rather than giving primitives their own Light/Dark modes. Two theme-bearing collections means a
node needs *both* collections' modes aligned to theme correctly → the multi-mode-resolution
fragility behind most `(?)` / pin-failure pain. Flat primitives → theme is controlled in exactly
one place (the semantics collection).

## 5. Idempotent self-healing migration patterns
- **Retire legacy collections by NAME, not by plugin-marker** — collections created by a different
  code path (e.g. a runtime sync) may lack your marker and never get cleaned otherwise.
- **`sweepUnseeded`**: after seeding, remove collection vars NOT seeded this run AND with no
  consumers — clears foreign-named / dropped / renamed cruft *inside* a kept collection without a
  manual delete. Bound vars are never removed (regen re-aliases first).
- **Resolve split-brain on clash**: when both a legacy and canonical collection exist with bindings,
  prefer the one with bindings (rename it in / retire the empty dup); recreate + auto-rebind on regen.
- **O(n) upsert at scale**: a per-variable linear scan of `collection.variableIds` is O(n²) and
  *hangs* at ~1700 vars (~1.5M `getVariableById` calls). Build a `{key→Variable}` index once.
