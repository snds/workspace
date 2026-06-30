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

## 6. Applying it — role → Radix step → use-class (the application layer)

When a color looks wrong or fails contrast, **diagnose by role → Radix step → use-class → pick
the token at that step in the element's own hue stack.** Never nudge a hand-authored hex. The
centric-ui foundation is a full **Radix 12-step** system (every hue — Zinc/neutral, Blue/primary,
Red, Green, Orange, Cyan, Yellow — has steps 1–12 in Light+Dark, plus alpha `A{n}` stacks).

**Contrast standard: APCA (Lc) is PRIMARY; WCAG 2.x AA is the FALLBACK** only when an APCA target
can't be met. Evaluate every text/icon-on-surface pair with APCA's polarity-aware Lc (rough use
targets: ~Lc 90 body, 75 content, 60 large/headline, 45 large-bold + non-text/UI, 30 spot/disabled)
— not WCAG ratios. APCA is directional: dark-on-light ≠ light-on-dark; pick the foreground polarity
yielding the higher |Lc|.

**Step → role → use-class:**
- **1–2** app/subtle backgrounds (FILL only): `background`=Zinc1, `card`/`popover`=white→Zinc2.
- **3** component surface (FILL): `muted`/`secondary`=Zinc3; soft status bg = hue3.
- **4** hover surface (FILL): `accent`=Zinc4 (neutral hover, NOT brand).
- **5** active/selected surface (FILL): `selected`=Blue5 (tinted, never the solid).
- **6–8** borders/separators (BORDER/RING only, never a fill): `border`=Zinc6 (subtle), `input`=Zinc7
  (**control border — THE INPUT TRAP: `input` is the input's border, never its fill; an input's fill
  is `card`/`background`**), Zinc8 = hover/high-contrast edge.
- **9–10** solids (FILL of CTAs/status/toggles + focus-ring stroke): `primary`=Blue10, `ring`=Blue9,
  `destructive`=Red9, `success`=Green9, `warning`=Orange9, `info`=Cyan9, `caution`=Yellow9.
- **11** secondary text (TEXT): `muted-foreground`=Zinc11.
- **12** primary text (TEXT): `foreground`=Zinc12.

**Use-class gate (catches most bugs):** fills come from steps 1–5 and 9–10; borders/rings from 6–8
(focus ring = step-9 accent stroke); text from 11–12. A token used outside its class IS the bug
(e.g. a Select painted with `input`/Zinc7 = a step-7 border token used as a fill → swap fill to
`card`, keep Zinc7 as the 1px edge).

**On-solid foreground is CONTRAST-DRIVEN (APCA Lc), not fixed-white** (the `*-foreground` token):
for each step-9 solid, choose white vs the hue's dark step (12 light / 1 dark) by whichever yields
the higher APCA Lc. Bright 9s (Yellow→`caution`, Orange→`warning`, Cyan→`info`) tend to need dark;
dark 9s (Blue/Red/Green) keep white. **Re-derive per hue with APCA — don't assume.**

**Soft variants** = step-3 tint surface + step-11 text by default (`destructive-soft-foreground`=Red11);
bump text to 12 only where APCA on that hue's 11-over-3 misses. Text on tinted surfaces (steps 2–5,
e.g. `selected`=Blue5): verify with APCA, 11→12 only where required.

**Dark mode:** re-resolve by STEP, not hex; keep alpha tokens alpha (`border-subtle`=ZincA4 — never
flatten); preserve elevation order bg < card < popover per mode.

**Known/by-design:** steps 6–7 borders are intentionally subtle (step 8 for a hard edge); the
resting `input` border is flagged for a deliberate decision (subtle aesthetic vs APCA/WCAG-1.4.11
non-text target). **NOTE — a 2026-06 WCAG-ratio pass that pushed `warning-/info-foreground` to dark
and `*-soft-foreground`/`selected-foreground` to step 12 was REVERTED at Sean's request; originals
restored (foregrounds=`inverted`/white, soft=step 11, selected=Blue 11). Any future corrections must
be re-derived under APCA-primary, WCAG-fallback.**

This application layer is the operational complement to decision §3 (APCA as governance): §3 says
*don't mutate primitives*; this section says *how to select the right token at the semantic layer*.

Related: [[figma-ds-surface-authoring]] · [[enterprise-saas-design-patterns]]. (Migrated from local
memory `radix-context-step-color-rules`; supersedes the old `feedback_radix-step-apca-governs-color`.)
