---
title: Idempotent Design Decisions
spec_version: "1.0"
status: canonical
tags: [shared-reference, design-systems, ontology, apca, state-overlay, elevation]
created: 2026-09-01
updated: 2026-09-01
links:
  - "[[workspace-ontology]]"
  - "[[09-component-and-pattern-framework]]"
  - "[[ds-agents-binding]]"
  - "[[radix-derived-color-system]]"
  - "[[interaction-state-semantics]]"
  - "[[figma-shadow-modes]]"
  - "[[agentic-ds-context-model]]"
---

# Idempotent design decisions

Standing **design methods**, not style values. They apply to every system this workspace
touches. They do **not** import another system's tokens, hex, radii, or typefaces into a
target DS. When a target system lacks a token the method needs, derive minimally inside
that system's own grammar and backlog the gap. Token gaps are backloggable; a11y
compliance is not.

## For future agent
- **TL;DR:** Three method decisions travel with every DS job: Radix-shaped APCA color
  governance, overlay emphasis (not baked fills), and one-light elevation. Values stay
  in the target system. Depth lives in the knowledge entries this file points at.
- **Key claims:**
  - These are ontology-level *methods*. A project's `DESIGN.md` owns look. (timeless)
  - APCA governs pairings; it must not mutate a curated primitive scale. (timeless)
  - Interaction and emphasis are composited modifiers over the existing fill. (timeless)
  - Elevation is one implied light: geometry by step, opacity by theme. (timeless)
- **As of:** 2026-09 · **Status:** current
- **Audience:** `for: all`

---

## What belongs here

| This file | Not this file |
|---|---|
| Method that stays true if the brand, framework, or repo changes | A hex, a radius, a typeface, a product hue |
| How to select / composite / light | What Blue-10 is in C8 or any other library |
| Pointers to validated knowledge | A second copy of those entries |

Routing: durable standard → this file. Validated how-to → `08-knowledge/design/`.
Project look → that project's `DESIGN.md`. See [[workspace-ontology]].

---

## 1. Radix-shaped color, APCA as governance

**Decision.** When a system uses (or is being given) a 12-step role scale, treat the
scale as a *role* ladder, not a lightness ladder. Contrast is decided at the
**semantic pairing** layer. Do not warp trusted primitives to chase a ratio.

**Must**
- Reason in a perceptual space (OKLCH), then export to the target format.
- Diagnose a bad color by role → step → use-class (fill / border / text), then pick
  the token in that element's own hue stack. Never nudge a hand-authored hex.
- APCA (Lc) is the primary pairing test. WCAG 2.2 AA is the legal fallback when an
  APCA target cannot be met. Polarity is directional: dark-on-light ≠ light-on-dark.
- Brand owns its hue. Status roles (success / warning / error / info) must not
  collide with brand; shift the colliding role, not the brand.
- Hover-accent ≠ selected. Hover is a transient overlay. Selected is a persistent
  role, often brand-hued, never the same token as hover.

**Must not**
- Mutate a curated primitive scale (Radix or a Radix-derived ramp) so a pairing
  "passes."
- Copy another system's hex or step numbers into a target DS that does not use
  that scale. Import the method; derive tokens inside the target.
- Treat Tailwind 500-as-midpoint as equivalent to a 12-step role scale.

**Use-class (the bug catcher).** Fills live on the low and solid steps; borders/rings
on the mid edge steps; text on the high steps. A token used outside its class *is*
the defect (example: an input fill painted with a border-step token).

Depth: [[radix-derived-color-system]] · [[found-color]] · [[a11y-visual]] ·
[[uid-color-for-ui]]. Machine view: DSDS shared `shared-color-governance`.

## 2. Overlay emphasis (solid, wash, gradient, or other modifier)

**Decision.** Interaction and emphasis are **composited modifiers** over whatever the
control already is. The base fill keeps its variant / status token. Hover, pressed,
selected, and emphasis (solid dim, tint wash, inverse lift, or a gradient/other
modifier) paint on top. The base does not swap to a new baked color per state.

**Must**
- One small overlay ladder, hue-agnostic enough to composite over any parent.
- Separate concerns: interaction enum (`rest | hover | active | focus`) vs
  `disabled` / `readonly` booleans vs `validation` vs `selected`. Do not cram
  them into one state enum.
- Solid fills use a polarity-aware modifier (darken on light solids, lighten on
  dark solids). Soft / ghost / chrome uses a wash. Inverse parents always lighten.
- If the target system has no overlay tokens, derive a minimal ladder in *its*
  token grammar and backlog promotion. Do not import another library's alpha
  tokens by name.

**Must not**
- Author `background/hover` per variant × theme × status (combinatorial explosion,
  still wrong on a non-default parent).
- Swap the base to an opaque hover color picked for one surface.
- Treat gradient or other emphasis as a second visual language. It is still a
  modifier of the existing fill, governed by the same pairing rules.

Depth: [[interaction-state-semantics]] · framework #09 §8c state layers / §8d
state modeling. Machine view: DSDS shared `shared-overlay-emphasis`.

## 3. One-light elevation

**Decision.** Elevation is a **realistic light model**, not decoration. One implied
key light (top-down unless the product explicitly authors otherwise). Geometry
(offset, blur, spread) is the elevation step. Opacity is a theme axis. They are
not the same token.

**Must**
- Keep a single light direction across the system. Larger / blurrier / slightly
  lower offset = higher.
- Bind geometry and color/opacity separately so Light/Dark (or any theme) can
  retune opacity without rewriting elevation steps.
- On dark surfaces, shadows vanish. Pair the shadow ladder with a tonal lift
  (surface lightness increase) when the theme needs it. Framework #09 §8c: pick
  shadow, tonal, or both *as a system stance*, then stay consistent.
- One effect style (or one token family) with modes beats N named shadow styles
  that duplicate the same light.

**Must not**
- Bake theme opacity into the geometry token (forces a restyle per theme).
- Use colored or multi-direction shadows as default elevation (that is illustration,
  not UI light).
- Deepen shadows as the only dark-mode elevation strategy.
- Copy another product's drop-1/2/3 values into a target DS. Import the method;
  set geometry/opacity in that system's tokens.

Depth: [[figma-shadow-modes]] (one instance of the method) · framework #09 §8c
Elevation / depth · [[uid-color-for-ui]] dark-mode tonal lift. Machine view:
DSDS shared `shared-one-light-elevation`.

---

## How a target system applies this

1. Load this file (method) + the target `DESIGN.md` / token source (values).
2. If a needed token is missing, derive the smallest overlay / pairing / elevation
   step inside the target grammar and record the gap.
3. Never paste C8, Radix hex, or any other library's values into a foreign system
   to "make it match."
4. A11y pairing must pass now (APCA primary, WCAG fallback). Token completeness
   can wait on a backlog item.

## Related

- [[workspace-ontology]] — routing: method here, values in the target system
- [[ds-agents-binding]] — always-on compression of these three
- [[agentic-ds-context-model]] — three-graph + DSDS projection
- [[09-component-and-pattern-framework]] — §8c dimensions these decisions lock
