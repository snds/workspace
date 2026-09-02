---
tags: [design-systems, color, radix, tokens, interaction, states, figma, centric-ui]
created: 2026-07-31
updated: 2026-08-05
status: working
confidence: high
sources: [session 2026-07-31 Figma density/interaction work, Centric SaaS PLM DS o6o1ZuGHxDow2vHLuYXT6X]
related_skills: [ds-advisor, design-engineer, lead-ux-designer]
related_projects: [Centric SaaS PLM Design System, centric-ui]
relations:
  exemplifies:
    - "[[idempotent-design-decisions]]"
---

# Interaction state semantics — the overlay model

One mechanism for every hover/pressed/highlight surface in the system, replacing three
competing ad-hoc approaches. Validated in the Centric SaaS PLM Figma library 2026-07-31.

## The rule

**An interaction state is an alpha overlay composited over whatever the control already is —
never a substitute background colour.**

Base fill keeps its variant/status token. A dedicated `[state-layer]` node (or second fill)
paints an `interaction/*` token on top. The base never changes between Default and Hover.

Why this and not the alternatives:

| Approach | Why it loses |
|---|---|
| `background/hover` token per variant | N variants × 2 themes × status = explodes; still wrong when the control sits on a non-default parent |
| Derive from the parent surface | Figma can't express parent→child colour inheritance cleanly; breaks on `card`, `sidebar`, status fills |
| Swap to an opaque hover colour | Only correct on the one surface it was picked for |
| **Alpha overlay** | One small ladder, composites correctly over *any* parent, hue-agnostic |

## The token ladder

Lives in `Foundations / Semantics / Colors` (Light/Dark), aliasing Radix alpha primitives.
Radix A-steps mean the same *role* in every hue, so A4 = hover and A5 = pressed universally —
the same step→role logic as [[radix-derived-color-system]] §6.

| Token | Light | Dark | Use |
|---|---|---|---|
| `interaction/hover` | Zinc A4 | Zinc A4 | **Neutral** hover — Button `ghost/secondary`/`outline`/`secondary`, and **table cell** hover |
| `interaction/pressed` | Zinc A5 | Zinc A5 | Neutral pressed |
| `interaction/selected` | Blue A5 | Blue A5 | Persistent selected/active surface tint (brand). Replaces solid Blue/5 |
| `interaction/selected/foreground` | → `action/primary-text` (Blue/11) | → `action/primary-text` (Blue/11) | Brand **text** on selected washes — Radix text step, not `action/primary` (Blue/10 fill) |


| `interaction/solid/hover` | Black 10% | White 10% | On **solid** fills (primary, status solids). Darkens in Light, lightens in Dark — mirrors Radix 9→10 |
| `interaction/solid/pressed` | Black 20% | White 20% | On solid fills |
| `interaction/inverse/hover` | White 10% | White 10% | Control on a **coloured/dark parent**. Always lightens |
| `interaction/inverse/pressed` | White 20% | White 20% | ditto |
| `interaction/{primary,info,success,warning,caution,danger}/hover` | hue A4 | hue A4 | Hue-keyed tint for transparent/soft affordances |
| `interaction/{…}/pressed` | hue A5 | hue A5 | ditto |

Hue mapping (confirmed against the primitives): primary→Blue, info→Cyan, success→Green,
warning→Orange, caution→Yellow, danger→Red. Neutral→Zinc.

### Brand as the default hover/active voice (2026-07-31)

**Most** interactive chrome uses brand primary — not neutral Zinc — for hover and selected:

| Role | Background | Foreground |
|---|---|---|
| Hover (nav, menus, tabs, calendar, pagination, select highlight, table **row**) | `interaction/primary/hover` (Blue A4) | `action/primary-text` (Blue/11) |
| Selected / active | `interaction/selected` (Blue A5) | `interaction/selected/foreground` → `action/primary-text` (Blue/11) |

Semantic aliases updated so existing names keep working:

- `sidebar/selected`, `chrome/selected` → `interaction/selected`
- `sidebar/selected/foreground`, `chrome/selected/foreground` → `interaction/selected/foreground` → **`action/primary-text`** (Blue/11)
- `sidebar/accent` → `interaction/primary/hover`
- `sidebar/accent/foreground` → **`action/primary-text`** (Blue/11) — code `--sem-primary-text`; Figma must not stop at `action/primary` (Blue/10 fill)

**Stay neutral (Zinc):** Button `ghost/secondary` / `outline` / `secondary` overlays; table **cell**
hover. Status ghosts keep their hue family. Solid filled buttons keep Black/White solid overlays.

Verified on `_Sidebar/Menu Button` Selected: bg resolves to Blue A5 @ α≈0.24 (was opaque
`#cbe2ff`); fg resolves to `action/primary` `#0976e0`.

### Polarity rule (the only real decision)

- **Solid / light surfaces** → darken (Black overlay, or the hue's A-stack)
- **Dark / inverted / coloured parents** → lighten (White overlay)
- **Transparent over neutral chrome** → neutral Zinc A4/A5
- **Transparent over a status context** → that hue's A4/A5

## Two mechanics that will bite you

**1. Alpha must live in the token's colour value, never in paint opacity.**
Paint-level `opacity` is ignored on variable-bound fills at render
([[figma-ds-surface-authoring]] rule 17c). Radix A-steps store alpha *in the colour*, so they
work. Verified: a bound `interaction/hover` fill, a literal composite, and a literal rgba all
rendered pixel-identical at `#e8e8ec`.

**2. Set the state-layer node opacity to 1.**
The old Button state layer carried its alpha as *node* opacity (0.12 / 0.24 / 0.32) over a
fill bound to `foreground/default`. Node opacity does render — but it puts the alpha outside
the token system. Binding the fill to an `interaction/*` token and setting node opacity to 1
moves the whole value into tokens.

## Wiring in Figma

`Button / Variant` gained `overlay/hover` + `overlay/pressed`, resolved per mode to the right
family. State variants then bind the `[state-layer]` to those:

| Variant modes | family |
|---|---|
| `default`, `danger`, `info`, `success`, `warning`, `caution` (solid fills) | `solid` |
| `outline`, `secondary`, `ghost/secondary` | neutral |
| `link`, `ghost/primary` | `primary` (brand-tinted wash) |
| `destructive` (soft red bg), `ghost/danger` | `danger` |
| `ghost/info` · `ghost/success` · `ghost/warning` · `ghost/caution` | matching hue |
| `ghost/inverse` | `inverse` |

`State=Hover`/`Open` → `overlay/hover`; `State=Pressed` → `overlay/pressed`;
`State=Focus` → `overlay/hover` (the `[ring]` remains the actual focus indicator).
Icon Button inherits automatically — it nests a real Button instance.

### Foreground that changes on interaction

Most variants keep the same text/icon colour across states. Two need a colour *change*:

| Mode | Rest fg | Hover / Pressed fg | Overlay |
|---|---|---|---|
| `ghost/secondary` | `surface/foreground` | same | neutral |
| `ghost/primary` | `surface/foreground` | `action/primary` | `interaction/primary/*` |
| `link` | `action/primary` | same (already brand) | `interaction/primary/*` |

Implemented as `Button / Variant`.`foreground/hover` + `foreground/pressed` (seeded to equal
`foreground/default` on every mode; only `ghost/primary` elevates). Hover/Open/Pressed state
variants bind label + icon glyph fills to those tokens; Default/Focus/Disabled stay on
`foreground/default`.

Ghost modes are slash-grouped (`ghost/primary`, `ghost/secondary`, `ghost/info`, …) to match
variable-name nesting. Mode IDs are stable across renames — existing instance mode bindings hold.
`link` stays a separate variant (always-primary at rest ≠ ghost that becomes primary on hover).

**Verified pixel-exact** (server render, sampled at node bounds):

| Row | Hover rendered | Predicted |
|---|---|---|
| ghost | (232,232,236) | (232,232,236) |
| default | (8,106,201) | (8,106,202) |
| ghost/info | (202,241,246) | (202,241,246) |
| ghost/inverse | (34,132,227) | (34,132,227) |

## What was unified (2026-07-31)

Three mechanisms existed before this:

1. **`[state-layer]` node** bound to `foreground/default` at hardcoded node opacity — Button, `_Tabs/Trigger`
2. **Mode-driven `background` var** — `Select / Item` (Highlighted), `Table / Row` (Hover), `Sidebar / Menu Button` (Hover)
3. **Direct opaque fill** — `_Calendar/Day`, `_Menubar/Trigger`, `_NavMenu/Trigger`, `Toggle`, `_Menu/Item` row
   (`_Pagination/Item` now nests Button + `pagination` variant / primary overlays — no longer a direct fill)

All now resolve to `interaction/*`. Later the same day, **brand became the default hover/active
voice** (see § Brand as the default hover/active voice): nav/menu/tabs/calendar/pagination/select/
table-row hovers → `interaction/primary/hover` + `action/primary` fg; selected surfaces →
`interaction/selected` (Blue A5) instead of solid Blue/5.

**Stay neutral:** Button `ghost/secondary`/`outline`/`secondary`; table **cell** hover (Zinc).

**Deliberate exceptions** — not surface hovers: `_Resizable/Handle` and `_Slider/Thumb` (the hover
changes *the control itself*). Solid filled buttons keep Black/White solid overlays.

## Table cascade — the notable exception

Data tables break the "brand everywhere" rule because cells can carry **data-driven fills** that
must remain legible under row, column, and cell interaction.

Stack (bottom → top):

```
data fill (optional, per cell)
  └─ row hover/selected     → interaction/primary/*   (Blue A4 / A5)
  └─ column hover           → interaction/primary/*   (same brand voice; not yet wired)
  └─ cell hover             → interaction/hover       (Zinc A4 — neutral, sits on top)
```

Why zinc on the cell: a primary cell hover on top of a primary row hover just darkens brand-on-brand
with no new information. Neutral cell hover reads as "this cell" against "this row/column."
Because every layer is alpha, a custom-coloured cell still shows through — the overlays tint it
rather than replacing it. That is exactly why selected/hover must stay opacity treatments, not
solid Blue/5.

Wired today:

- `Table / Row` Hover → `interaction/primary/hover`; Selected → `chrome/selected` → `interaction/selected`
- `Table / Cell` collection created (`Default` / `Hover`); cell master fill bound to its
  `background` var (Default = transparent, Hover = `interaction/hover`)

Still open: column-hover surface (needs a column chrome component or absolute overlay); proving the
stack on a coloured-cell fixture; code-side `::before`/`::after` layering so CSS matches.

## centric-ui reconciliation plan

> Employer repo. Branch → PR → human engineer review. No self-merge, no direct push.
> Nothing from this workspace gets pasted into the repo; this is a plan, not content to copy.

The Radix alpha stacks already exist in the centric-ui foundation (every hue carries A1–A12
per [[radix-derived-color-system]]), so **no new primitives are needed**. The work is the
semantic layer plus the component mechanism.

**1. Semantic layer** — add the `interaction/*` tokens as CSS custom properties, mapped to the
same Radix A-steps and the Black/White overlay values. Naming should follow whatever the
`/`→nested-path convention resolves to at Style Dictionary export time.

**2. Component mechanism — this is the real change.** Current shadcn/Tailwind idiom is
`hover:bg-primary/90`, which *substitutes* a lower-opacity base colour. That is a different
model: it lightens toward whatever is behind, and it can't express "tint by the status hue."
Replace with a state layer:

```css
.btn { position: relative; isolation: isolate; }
.btn::after {
  content: ""; position: absolute; inset: 0;
  border-radius: inherit; pointer-events: none;
  background: transparent;
}
.btn:hover::after  { background: var(--interaction-hover); }
.btn:active::after { background: var(--interaction-pressed); }
```

with `--interaction-hover` re-pointed per variant (the CVA variant sets it). That mirrors the
Figma `[state-layer]` node 1:1. `box-shadow: inset 0 0 0 999px var(...)` is a viable
no-pseudo-element fallback.

**3. Audit `*/90`-style hover utilities** across components — each is a candidate for the same
replacement. Expect these in Button, Badge, menu/nav items, table rows, calendar days,
pagination.

**4. Ghost status + inverse variants** need to land alongside (see
[[density-vertical-rhythm-audit]]): `ghost-{info,success,warning,caution,danger}` and
`ghost/inverse`, foregrounds on `status/*/soft/foreground` not the solid step-9 hues.

**Contrast governance:** APCA (Lc) is primary, WCAG 2.x is fallback only. Overlay tokens are
non-text surfaces, but every foreground sitting *on* a tinted surface must be re-checked with
APCA — an A5 pressed tint moves the background enough to matter on the lighter hues (Yellow
A5 is α 0.56 in Light).

Related: [[radix-derived-color-system]] · [[figma-ds-surface-authoring]] ·
[[density-vertical-rhythm-audit]] · [[centric-plm-design-system]] ·
[[token-spec-page]] · [[cross-surface-token-parity]]

## Code sync (2026-08-05)

Both employer repos on `feat/interaction-overlay-tokens` (uncommitted; no auto-push):

| Binding | Target |
|---|---|
| `--sem-selected` | → `--sem-interaction-selected` → `--color-blueA-5` |
| `--sem-selected-foreground` | → `--sem-interaction-selected-foreground` → `--sem-primary` |
| `--sem-sidebar-accent` | → `--sem-interaction-primary-hover` → `--color-blueA-4` |
| `--sem-sidebar-accent-foreground` | → `--sem-primary` |
| `--sem-sidebar-selected` | interaction selected; fg → selected-foreground |
| Full `interaction/*` ladder | + caution*, border-subtle, surface-hover, destructive-subtle, transparent |
| Dark | solid overlays → whiteA; caution-foreground → yellow-1 |
| Sidebar selected/active | `sidebar-selected` (hover stays accent) |
| Utility | `.interaction-layer` ::after mirrors Figma state-layer |

Reference pages: centric-ui Storybook `Foundations/Interaction States`; prototype `/interaction-lab.html`.
