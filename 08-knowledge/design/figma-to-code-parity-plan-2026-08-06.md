---
title: Figma → code parity plan (2026-08-06 session)
status: living
updated: 2026-08-06
figma_file: o6o1ZuGHxDow2vHLuYXT6X
related:
  - figma-ds-surface-authoring
  - density-radius-xxs-alignment
  - figma-component-token-axes
  - density-vertical-rhythm-audit
  - centric-ui-density-adoption
  - cross-surface-token-parity
codebases:
  - /Users/sean.sands/Projects/cpes-software/saas-plm-prototype
  - /Users/sean.sands/Projects/cpes-software/centric-ui
profile: employer / c8 — plan only; no auto-commit
implementation_started: 2026-08-06
prs:
  - https://github.com/cpes-software/saas-plm-prototype/pull/18
  - https://github.com/cpes-software/centric-ui/pull/225
---

# Figma → code parity plan — 2026-08-06

**Implementation note (2026-08-06 evening):** P0 control-radius SSOT (Figma `md` → code `rounded-md`) + field-adjacent overlays + `--radius-focus-*` calc twins landed on both interaction-token PRs above. Proto `design-system.rules.json` updated so `ds:check` enforces md. Toggle Group nest recipe deferred (toolbar-pill consumers).

Inventory of **Centric SaaS PLM DS** Figma work from the 2026-08-06 session (and durable
docs updated that day), compared to live Proto + centric-ui. Pure Figma construction
hacks are listed under **Non-goals** — do not port those as product CSS tokens.

**SSOT for what landed in Figma:** [[figma-ds-surface-authoring]], [[density-radius-xxs-alignment]],
[[density-vertical-rhythm-audit]] (Icon Button / adornment follow-ups).

**Code paths verified (read, not guessed):**

| Surface | Root |
|---|---|
| Proto | `cpes-software/saas-plm-prototype` — `src/styles/density.css`, `src/styles/index.css`, `src/app/components/ui/*` |
| centric-ui | `cpes-software/centric-ui` — `app/density.css`, `app/app.css`, `app/components/ui/*` |

Also present locally but **not** treated as primary targets: `cpes-software/centric-ui-main`
(parallel checkout), `c8-plm/CDS`, `design-system`. No Calendar / DayPicker package found in
either primary codebase.

---

## 1. Summary

| Class | Count (approx) | Meaning |
|---|---|---|
| **CODE-RELEVANT** | **14** | Token values, component CSS/behavior, density, radii, sizes, nest formulas |
| **FIGMA-ONLY / sync:ignore** | **9** | Construction spacers, precomputed ring radii, corner masks, locked anchors, stickersheet |
| **N/A in code today** | **2** | Calendar Day square; Carousel Icon Button (no primitive in either app) |
| **Already ALIGNED / MATCH** | **5** | Popover `sideOffset=4`; Slider track `rounded-full` (Proto); density control heights/px; Badge rounded→sm; dialog close uses `Button` icon size |

**Headline gap:** Figma default controls now bind **`control-radius/md`** (8 / 12 / 16).
Both codebases still use **`rounded-sm` → `--radius-sm`** (4 / 8 / 12) for Button / Input /
Select / Textarea. That is a one-rung softeness DEVIATE at every density — resolve before
bulk overlay/nest work, or overlays “matching the field” will be aimed at the wrong rung.

---

## 2. Inventory table

Statuses use [[cross-surface-token-parity]]: MATCH · ALIGNED · DEVIATE · FIGMA-ONLY / missing.

| Change | Figma status | Proto today | centric-ui today | Gap | Recommended action | Priority |
|---|---|---|---|---|---|---|
| **Default control radius** → Density `control-radius/md` (8/12/16); Size=sm → `sm` (4/8/12) | Landed 2026-08-06 | Button/Input/Select/Textarea `rounded-sm` (= `--radius-sm` 4/8/12) — `ui/button.tsx`, `ui/input.tsx`, `ui/select.tsx` | Same contract — `app/components/ui/button.tsx` (commented as DS standard), `input.tsx`, `select.tsx`, `textarea.tsx` | **DEVIATE** — Figma default = md rung; code default = sm rung | **Decide SSOT** (see Open Q1). If Figma wins: default controls → `rounded-md` (or `--control-radius` alias of `--radius-md`); Size=sm stays `rounded-sm`. If code wins: revert Figma defaults to `control-radius/sm`. | **P0** |
| **Focus ring nest** = body + 3px | Precomputed `focus-ring-radius/*` **[figma-only]**; docs recommend CSS calc | Global `:focus-visible` outline 2px / offset 2px, `border-radius: var(--radius-sm)` — `src/styles/index.css` (no outer nest calc) | Button `focus-visible:ring-3 ring-ring/50` — ring follows element radius, not `radius+3` | **DEVIATE** vs nested ideal; ring tokens themselves stay figma-only | Add `--focus-ring-offset: 3px` + `--radius-focus-sm/md: calc(var(--radius-*) + var(--focus-ring-offset))` in both `density.css`; apply to focus styles / box-shadow rings. Do **not** export Figma `focus-ring-radius/*` as named product tokens if calc twins exist. | **P1** |
| **Focus ring color** → `chrome/ring` (exceptions: destructive / Error) | Remapped Button/Badge modes | App-wide `--sem-ring` / `var(--color-ring)` — MATCH intent | `--sem-ring` + Button destructive → `ring-destructive/*` — MATCH intent | Mostly **MATCH**; audit leftover hue-matched status rings on ghosts if any | Spot-check Button/Badge focus styles; keep destructive exception | P2 |
| **Control density audit** (Button pad/gap, Input pad-x, OTP h, Select/Radio minH, Nav h, Badge pad-y) | Bound to Density | Densities in `density.css`; Button/Input consume `--density-control-*` | Same + adoption pass in [[centric-ui-density-adoption]] | Mostly **ALIGNED**; OTP/Radio primitives sparse | No bulk ticket; pick up when those primitives land | P3 |
| **Slider tracks** → `radius/full` | Landed | `ui/slider.tsx` Track/Indicator `rounded-full` | No slider primitive | Proto **MATCH**; centric N/A | None for Proto; if centric adds Slider, use `rounded-full` | — |
| **Pagination Focus variant** | Figma structure | No Pagination primitive | No Pagination primitive | N/A / FIGMA structure | Skip | — |
| **Calendar Day** square `control-height/md` + pad | Landed | **No** Calendar / DayPicker | **No** Calendar | missing | When DatePicker lands: day cells `size-(--density-control-h)` + light pad; shell pad from Density | P3 (blocked) |
| **Field-anchored overlay radii** → same rung as trigger (`control-radius/md`) | Calendar/Command/Dropdown/Context Menu → md | SelectContent `rounded-md`; Popover `rounded-lg`; Dropdown/Context `rounded-md` — `ui/select.tsx`, `popover.tsx`, `dropdown-menu.tsx`, `context-menu.tsx` | Select/Popover/Dropdown all `rounded-lg` — softer than field `rounded-sm` | **DEVIATE** — overlays ≠ trigger; Proto inconsistent (md vs lg) | After P0 radius decision: field-adjacent panels (Select, Combobox popover, Command, Dropdown, Context) → **same utility as trigger** (likely `rounded-md` if Figma md wins, or `rounded-sm` if code keeps sm). Keep Dialog/Sheet/Drawer on surface ladder (`rounded-lg` / `xl`). Tooltip stays tighter. | **P0** |
| **Popover gap 4px** (`popover/offset-y` = control-h + 4) | Token **[figma-only]**; intent = 4px under trigger | `sideOffset = 4` default — Popover/Select/Dropdown | Same `sideOffset = 4` | **ALIGNED** (mechanism differs) | Keep `sideOffset={4}`; do not add `popover/offset-y` CSS var | — |
| **`[popover-anchor]` / locked offset** | Construction | N/A (Positioner) | N/A | FIGMA-ONLY | Skip | — |
| **Toggle Group** shell `control-radius/md` + `control-height/md`; inset 2; item-radius = md−2 | Landed; position modes **[figma-only]** | `ui/toggle-group.tsx` unstyled flex; consumers e.g. MediaLibrary `rounded-sm` shell + `rounded-none` items — **no** 2px inset nest | No ToggleGroup; `button-group.tsx` joins corners to `rounded-*-lg` (surface, not nest formula) | **DEVIATE** | Proto: optional shell recipe — `h-(--density-control-h) rounded-md p-0.5 gap-0.5` + items `rounded-[calc(var(--radius-md)-2px)]` / first-last / middle `rounded-none`. centric: either adopt ToggleGroup or teach ButtonGroup the nest formula instead of `rounded-r-lg`. | **P1** |
| **Field adornment optical inset** — trailing Icon Button flush; text keeps `padding-x/input` | Standing rule §18 | Bare `<Input>` symmetric `px-(--density-control-px-input)`; no clear-affordance composite | Same; Select `pr-2` + chevron (not asymmetric clear well) | **DEVIATE** vs Figma composite Input | Add InputWithAdornments (or Input slots): `pl-(--density-control-px-input) pr-0`, trailing `Button size="icon-sm"` flush + optical end pad `gap`/`space-1.5`; Select chevron keep small trailing gap (`pr-1.5` / `gap-xs`) | **P1** |
| **Clear / dismiss Icon Button Size sm** (16px glyph in md field) | Landed | Dialog has no injected close; many `size="icon"` + `w-5 h-5` X; Sonner unstyled no dismiss control | Dialog/Sheet close `size="icon-sm"` — close to Figma sm; Alert has no dismiss slot; toast via Sonner | Partial | Standardize dismiss/clear on `icon-sm` (not `icon-xs`); bump tiny `size-3` clear glyphs in chips when they are real hit targets | **P2** |
| **Icon-only → Icon Button** (Carousel, Toast/Alert dismiss) | Landed in Figma | Pattern = `Button size="icon*"` (no separate IconButton wrapper) | Same (`size="icon"` / `icon-sm`) | ALIGNED intent if sizes match; Carousel N/A | Prefer `Button size="icon-sm"` for field/toast dismiss; document IconButton ≡ Button icon layout | P2 |
| **Dialog/Sheet close** → `control-height/md` | Density audit | No injected close | `icon-sm` (= sm ladder, not md) | **DEVIATE** vs Figma md | Confirm with Sean (surface-authoring also says dialog close may stay code-faithful per-component). If Figma md wins: `size="icon"` default. | P2 |
| **Badge Shape rounded** → `control-radius/sm` + focus-ring-sm; Pill full | Landed | `shape: chip` → `rounded-(--radius-chip)`; pill full — different chip ladder | `shape: rounded` → `rounded-sm`; pill `rounded-4xl` | Rounded **ALIGNED** to sm rung; chip ladder is intentional code nuance | No change unless unifying chip vs Badge/Shape | P3 |
| **COMPONENT_SET bounds / stickersheet fills** | Figma hygiene | N/A | N/A | FIGMA-ONLY | Skip | — |

---

## 3. Per-codebase work packages

Profile reminder: **employer / centric** — branch → PR → human review; **no auto-commit** from agents. Workspace docs OK.

### 3A. Shared decision (both codebases) — do first

1. **Control radius SSOT (P0)**  
   - **Options:** (A) Port Figma — default controls `rounded-md` / `--radius-md`; (B) Keep code — Figma rebinds defaults to `control-radius/sm`.  
   - **Acceptance:** Normal density default Input/Button measure equal in Figma stickersheet vs Storybook/Token Lab; overlay rule (§3B/3C) references the same rung.  
   - Update [[centric-ui-density-adoption]] “Control radius contract” + Proto Token Lab copy once decided.

2. **Focus nest calc twins (P1)**  
   - Add to both `density.css` (outside figma-only export):

```css
:root {
  --focus-ring-offset: 3px;
  --radius-focus-sm: calc(var(--radius-sm) + var(--focus-ring-offset));
  --radius-focus-md: calc(var(--radius-md) + var(--focus-ring-offset));
}
```

   - **Acceptance:** Focus ring outer corner reads nest-correct on Button/Input at C/N/S (±1px snap acceptable). Proto global outline may keep 2px stroke but should use focus radius token for `border-radius` on the outline path where feasible.

### 3B. Proto (`saas-plm-prototype`) backlog

| # | Package | Files (cite) | Acceptance |
|---|---|---|---|
| P0-1 | Apply control-radius decision to primitives | `ui/button.tsx`, `ui/input.tsx`, `ui/select.tsx`, `ui/textarea.tsx`, consumers overriding `rounded-*` | Default controls match chosen rung under `data-density` |
| P0-2 | Field-adjacent overlays match trigger | `ui/select.tsx` Content, `ui/popover.tsx`, `ui/dropdown-menu.tsx`, `ui/context-menu.tsx`, `ui/command.tsx` | Same `rounded-*` as SelectTrigger/Input; Dialog/Sheet unchanged as surfaces |
| P1-1 | Toggle Group nest recipe | `ui/toggle-group.tsx` (+ MediaLibrary / Token Lab consumers) | Shell = control height + control radius; 2px inset; end-cap radius = `calc(var(--radius-md) - 2px)` (or sm if SSOT stays sm); middle edges 0 |
| P1-2 | Input trailing clear optical inset | New composite or extend Input; `SingleSelect` / combobox triggers if they grow a clear | Clear `Button size="icon-sm"` flush to field edge; text-only fields keep full `--density-control-px-input` |
| P1-3 | Focus calc wiring | `src/styles/index.css` + `density.css` | Nested focus radius used; color stays `--sem-ring` |
| P2-1 | Dismiss / icon-only size pass | Dialog callers, Sonner if dismiss added, icon toolbars | Clear/dismiss → `icon-sm`; avoid 12px glyphs in ≥28px targets |
| P3-1 | Calendar (when built) | new `ui/calendar.tsx` | Day = square `--density-control-h`; panel radius = field rung |

### 3C. centric-ui backlog

| # | Package | Files (cite) | Acceptance |
|---|---|---|---|
| P0-1 | Apply control-radius decision | `app/components/ui/button.tsx`, `input.tsx`, `select.tsx`, `textarea.tsx`, SchemaForm widgets (already forced `rounded-sm` — re-check) | Same as Proto; no form widget reintroduces wrong rung |
| P0-2 | Field-adjacent overlays → trigger rung | `select.tsx` Content, `popover.tsx`, `dropdown-menu.tsx`, `command.tsx` | Drop `rounded-lg` on field panels if trigger is sm/md control; Dialog/Sheet/Alert stay surface `rounded-lg` |
| P1-1 | Toggle / ButtonGroup nest | `button-group.tsx` (today forces `rounded-*-lg`); add ToggleGroup if product needs segmented control | Nest formula matches Figma values; do not rely on Figma Item mode collection |
| P1-2 | Field adornment composite | Input + Select trigger; filter comboboxes | Trailing clear flush; Select chevron `pr` ≈ gap/xs (already `pr-2` — tune if needed) |
| P1-3 | Focus calc twins | `app/density.css` + Button/Input focus classes | `ring-3` corners use focus radius (box-shadow or outline) |
| P2-1 | Dialog/Sheet close size | `dialog.tsx` (`icon-sm`), `sheet.tsx` (`icon-sm`) | Match agreed close size (Figma md vs keep sm) |
| P2-2 | Alert dismiss (if product wants) | `alert.tsx` has no dismiss today | Optional `icon-sm` ghost; don’t invent if product omits |
| P3-1 | Calendar / Slider when added | — | Follow Proto recipes above |

### 3D. Shared tokens (optional naming cleanup)

If Option A (Figma md default) wins, consider explicit aliases in both density sheets:

```css
--control-radius: var(--radius-md);      /* default controls + field panels */
--control-radius-sm: var(--radius-sm);   /* Size=sm / Badge rounded / tabs */
```

Keeps Tailwind `rounded-sm` / `rounded-md` honest to the Radii ladder while documenting the **control** role. Not required if the team prefers utility discipline alone.

---

## 4. Explicit non-goals (do not port)

| Item | Why |
|---|---|
| `popover/offset-y` | Figma spacer = `control-height/md + 4`; code already uses `sideOffset={4}` |
| `focus-ring-radius/sm\|md`, `Button/Select/Badge … radiusRing` | Precomputed because Figma lacks calc — use CSS calc twins instead |
| `focus-ring-offset` as a **synced** design token | OK as local CSS var; do not require Figma→code sync pipeline |
| `Day/top-*` / `Day/bottom-*` (Calendar / Radii) | Per-corner range masks |
| `Toggle Group / Item` position mode collection | Figma mechanism for corner masks; port **values** (md−2, none), not the collection |
| `toggle-group/inset` as exported token | Literal `p-0.5` / `gap-0.5` (2px) is enough |
| `[popover-anchor]`, `[popover-offset]`, `[popover-pad-clear]`, locked layers | Absolute construction / selection hygiene |
| Pagination Focus variant merge | Component-set structure |
| Stickersheet white fills / text rebinds / COMPONENT_SET refits | Library hygiene |
| Carousel nav Icon Button | No Carousel primitive in Proto or centric-ui |

---

## 5. Open questions

1. **Control radius SSOT — Figma `control-radius/md` vs code `rounded-sm`?**  
   Session Figma work moved default Input/Button/Select to **md**. Code + [[centric-ui-density-adoption]] still document **sm** as the form-control contract. This blocks overlay parity tickets.

2. **Toggle Group `item-radius` in CSS:** confirm `calc(var(--radius-md) - 2px)` (6/10/14) vs snapping to nearest ladder rung. Figma uses exact md−2.

3. **Field clear optical inset — intentional product change for code?**  
   Figma now flushes trailing Icon Button clears. Code Inputs are symmetric. Confirm before changing SchemaForm / filter fields (hit-target and i18n clear affordances).

4. **Dialog/Sheet close size:** Figma Density audit → `control-height/md`; centric ships `icon-sm`. Surface-authoring historically prefers code-faithful per-component insets — which wins?

5. **Proto vs centric focus model:** Proto uses global outline; centric uses per-component `ring-3`. Nest calc should land in both without double-ringing Proto controls.

6. **Calendar:** no code surface yet — park Day square work until DatePicker exists.

---

## 6. Suggested first slice (top gaps)

Ordered for impact after the SSOT decision:

1. **P0 — Control radius SSOT** (Figma md vs code sm)  
2. **P0 — Field-adjacent overlay radii = trigger** (Select / Popover / Dropdown / Context / Command)  
3. **P1 — Focus ring nest calc** (`--focus-ring-offset` + `--radius-focus-*`)  
4. **P1 — Toggle Group / ButtonGroup nest** (height md + inset 2 + item-radius md−2)  
5. **P1 — Field trailing clear optical inset** + Clear `icon-sm`  
6. **P2 — Dialog/Sheet close size alignment**  
7. **P2 — Dismiss/icon-only size audit** (toast/alert/toolbars)  
8. **P3 — Calendar Day** when DatePicker lands  

---

## Provenance

- Session docs: `08-knowledge/design/figma-ds-surface-authoring.md` (updated 2026-08-06), `density-radius-xxs-alignment.md`, `density-vertical-rhythm-audit.md`, `figma-component-token-axes.md`
- Transcript seed: Cursor `88a67ad5-5ce5-4b22-aefb-de1ccb79c08e` (field adornment + Icon Button subagent)
- Code read: 2026-08-06 against local `cpes-software/saas-plm-prototype` + `cpes-software/centric-ui`
