---
tags: [design-systems, color, radix, tailwind, apca, tokens]
created: 2026-06-02
updated: 2026-06-02
status: working
confidence: high
sources: [session-log 2026-06-02, centric-ui Radix palette re-architecture]
related_skills: [ds-advisor, design-engineer, figma-repo-sync-plugin]
related_projects: [centric-ui VMS DS, figma-repo-sync-plugin]
---

# Radix-derived color system — validated architecture

A reusable pattern for a token color foundation, validated on centric-ui (VMS DS).
Five decisions that work together:

## 1. Radix Colors as source of truth
Use the published Radix scales (values, 12-step context semantics, contrast) as the
primitive layer rather than deriving ramps from Tailwind. Tailwind 500 is a *lightness*
scale; Radix 1–12 is a *role* scale. Radix's step-9 solids are tuned so their on-color
text works (e.g. `green-9 #30a46c` carries white) — Tailwind's `green-500 #22c55e` does
not. Don't re-derive what Radix already solved.

## 2. Tailwind-name compatibility layer (so devs keep their classes)
Emit BOTH `--color-{hue}-{1..12}` (Radix step primitives, for the semantic layer to map
by role) AND `--color-{hue}-{50..950}` (Tailwind-shade aliases → the **nearest-OKLCh-L**
Radix step). Then `bg-green-500` resolves to the Radix-derived value that *looks like*
Tailwind green-500. Devs keep their mental model; the values are Radix.

## 3. APCA is GOVERNANCE, not a primitive mutator
APCA (the WCAG-3-draft perceptual contrast model) is the better legibility standard — but
enforcing it by *mutating primitives* (nudging a step's L until text passes) breaks Radix's
curated perceptual balance and muddies hues. Instead: trust Radix's values; apply APCA at
the **semantic-pairing / selection layer** (audit each fg/bg pairing, pick the step/text
color that passes). Mutate primitives ONLY for a custom scale you actually generate (the
brand). Standard scales: trusted + audited, never warped.

## 4. Brand-aware semantic hue assignment (collision avoidance)
A semantic context must never read as the brand. Rule (ported from the OMNI CDS engine):
if a role's default hue is within ~20° of the brand hue, shift it ~30° to the nearest
non-colliding scale. Brand = blue → `info` shifts blue→cyan/sky; `warning`→orange. The
brand owns its hue; success/warning/error/info take distinct alternates. Generalize as a
generative rule keyed on the brand hue, not hardcoded.

## 5. accent (hover) ≠ selected (active) — and the right Radix steps
shadcn's `accent` is **neutral** (a gray hover/highlight surface, ≈ Radix step 4), NOT
brand-derived — because it's applied to every hovered/highlighted item, so brand-tinting it
is noisy and conflates "hovering" with "selected." If you want brand emphasis on persistent
*selected/active* states (active nav item, current tab, selected row), add a SEPARATE token
at **Radix step 5** ("active/selected UI element background"), brand-hued, with step-11
brand text. Keep accent neutral (step 4 = hover); selected = brand (step 5).

## Bonus gotcha (Tailwind v4)
Bare `border-*` utilities default to `currentColor` (the dark text) in Tailwind v4 — no
gray default. Add the shadcn-standard `@layer base { * { border-color: var(--color-border) } }`
or dividers/footers render as the text color.

See memory `project_centric-ui-radix-palette`, `feedback_radix-step-apca-governs-color`.
