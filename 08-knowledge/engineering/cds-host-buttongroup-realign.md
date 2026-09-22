---
tags: [engineering, cds, centric-ui, button-group, federalization, consume]
created: 2026-09-18
updated: 2026-09-18
status: working
confidence: high
sources: [cds feat/shadcn-federalization ButtonGroup stories 2026-09-18, live centric-ui ViewHeaderActions, centric-ui-main ViewHeaderActions + local button-group.tsx, saas-plm-prototype SplitActionButton]
related_skills: [ds-advisor, design-engineer]
related_projects: [02-centricPLM, 19-workspace-brain]
relations:
  builds-on: ["[[cds-host-consume-order]]", "[[figma-to-code-parity-plan-2026-08-06]]"]
---

# Host ButtonGroup / split-CTA variances (cui federalization)

## For future agent
- **TL;DR:** CDS `ButtonGroup` is a join shell. Fill/outline/dark come from each child `Button` `variant`. Storybook Default using filled primary does **not** restyle hosts. Live `centric-ui` currently has **zero** `ButtonGroup` call sites. Older cui used a **dark split CTA**, not outline and not primary blue. Proto's joined control is a lateral (`SplitActionButton`), not `ButtonGroup`. Use this checklist when that team starts host federalization — do not copy CDS Default into toolbars.
- **Key claims:**
  - *Timeless:* `ButtonGroup` must not grow a variant that paints children. Hosts pass `variant` on every `Button`.
  - *Timeless:* Outline groups already share a hairline; `ButtonGroupSeparator` on outline **compounds**. ShadCN: separator is for non-outline variants.
  - *Dated 2026-09-18:* Live cui `ViewHeaderActions` is a single `variant="dark"` button. `centric-ui-main` still grouped that header with `ButtonGroup` + custom `CTA_CLASS` (neutral-900 / inverted dark) and a `rounded-md` override against L0 `rounded-lg`. Proto `button-group.tsx` is a dead local ShadCN copy; product uses `SplitActionButton` (`variant="dark"` + 1.6px `bg-background` divider).
- **Dated 2026-09-18 (sidebar):** CDS `SidebarTrigger` matches ShadCN: constant `left_panel_close` + RTL flip. Live cui `Header` used the old wrap extra (hamburger when closed, `md:hidden`). On pin, that header will show the panel glyph unless they compose a `menu` icon locally.
- **As of:** 2026-09-18 · **Status:** current · **Do not paste this file into employer repos**

---

## Why this exists

Instance-0 CDS federalization corrected Storybook so Default is filled and With Separator is not stacked on outline. Sean asked to keep the **host** deltas so cui re-alignment is deliberate, not accidental primary-blue.

Do **not** bump `cds.pin` from the federalization branch. Land CDS on `main` first ([[cds-host-consume-order]]).

## Inventory (2026-09-18)

| Surface | `ButtonGroup`? | What the UI actually is | Paint |
|---|---|---|---|
| Live `centric-ui` | No file, no imports | Collection header CTA only | `Button variant="dark"` + border class |
| `centric-ui-main` (older snapshot) | Local full copy (`app/components/ui/button-group.tsx`, not a CDS re-export) | Split header: primary action + chevron `DropdownMenu` | Custom `CTA_CLASS` (neutral-900 / inverted), **not** outline, **not** `variant="default"` |
| `saas-plm-prototype` | Local `src/app/components/ui/button-group.tsx`, **zero call sites** | `SplitActionButton` on where-used / assign | `variant="dark"` + custom 1.6px divider, capsule `rounded-md` |
| CDS Storybook (after 2026-09-18) | Yes | Default filled; With Separator filled+separator; Outline hairline join | Document compositions — not a host default |

### Live cui path

`app/features/views/components/ViewHeaderActions.tsx` — comment records that the ⋯ split menu moved to `ViewToolbar`. Remaining rule: **chevron on a dark CTA = choose which one**; **⋮ = other things about this page**.

### Older cui split (re-align target if it returns)

`ViewHeaderActions` wrapped two dark buttons in `ButtonGroup` and overrode group radius to `rounded-md` because L0 forces last-segment `rounded-r-lg` and Button base was `rounded-sm`. Size variants also had `in-data-[slot=button-group]:rounded-sm`. That radius fight is host overlay, not a CDS story bug.

## Re-align when cui federalizes

1. **Search** `ButtonGroup`, `button-group`, `SplitActionButton`, `role="group"` joined buttons before swapping modules.
2. **Chrome / toolbars** → `variant="outline"` (or `toolbar`) on every child. Do not use CDS Default (filled primary) as the copy-paste.
3. **Header / split CTA** → `variant="dark"` (or existing host CTA class) + separator or chevron slot. Do not restyle to primary blue.
4. **Separator** only between non-outline variants. Outline already has the join hairline.
5. Prefer `@centric/ui/button-group` wrap over keeping a local ShadCN fork. Do not `shadcn add` in the host.
6. If they still need `rounded-md` vs L0 `rounded-lg`, that is an extras/host overlay decision — record it; do not silently restyle L0.
7. Proto: delete or shim the unused local `button-group.tsx` when they consume CDS; keep `SplitActionButton` as an L2b lateral until a CDS split-button exists.
8. **SidebarTrigger:** hamburger is a cui mobile-header composition, not the CDS default. After pin, `Header` (`md:hidden` trigger) should pass a `menu` icon (or its own toggle button + `useSidebar()`) if they still want hamburger. Do not restore the morphing icon on the wrap.

## Out of scope

- Changing `Button` default variant.
- Adding a `ButtonGroup` CVA that sets child fill.
- Pin-bumping hosts from cds `feat/shadcn-federalization`.
