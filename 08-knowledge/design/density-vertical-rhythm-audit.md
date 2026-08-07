# Density vertical-rhythm audit — center + no pad-Y

_Status: audit findings · 2026-07-31 · file `o6o1ZuGHxDow2vHLuYXT6X`_
_Seed layout: Example density `313:2782` (Spacious / Normal / Compact Sidebar shells)_

## Pattern (failure mode)

Horizontal auto-layout + `counterAxisAlignItems: CENTER` + **paddingTop/Bottom = 0** (often bound to `space/0`) + either:

1. **FIXED** height with **no** binding that resolves to Density (`control-height/*`), or
2. **HUG** with no density pad-Y on self or an inner wrapper

Centering then only vertically centers fixed content; density mode changes do not grow/shrink the hit area.

**Healthy controls** (Button, Select) use the same pad-Y=0 + center pattern but bind **height** → Size axis → `control-height/md` (Density). That path works.

**Healthy nested pattern** (`_Menu/Item`): outer pad-Y=0, but inner `row` binds `padding-y/sm` (Density) + HUG → row height tracks density.

## Example density shells (`313:2782`)

| Slot | Compact | Normal | Spacious | Density-aware? |
|------|---------|--------|----------|----------------|
| `_Sidebar/Menu Button` height | **32** | **32** | **32** | **No** — FIXED 32, pad-Y `space/0`, no height bind |
| `_Sidebar/Header` | 44 | 48 | 52 | Yes — content slot `padding-y/md` |
| Group / Footer `gap` | 2 | 4 | 6 | Yes — `gap/xs` |
| Select (footer) | 28 | 32 | 36 | Yes — Size → `control-height/md` |
| UserIdentity pad-Y | 8 | 8 | 8 | Partial — static `space/2`; height still shifts via type/avatar |

## Layout page

| Master | Issue |
|--------|--------|
| **Header** `16:678` | FIXED **48**, pad-Y unbound 0, center. Horizontal inset uses `container/card-padding` (ok). Shell height does **not** follow density; children Buttons do via `control-height`. Risk: Spacious buttons (36) can feel tight / overflow visually inside 48. |
| **Page Layout** | PageHeader + content slot already use Density container tokens — good. |
| **App Shell** | Structure only; inherits chrome — no extra row freeze found at root. |

Sidebar masters live on **Components**, not Layout: `Sidebar`, `_Sidebar/Header|Group|Footer|Menu Button`.

## Library — prioritize fix

### P0 — same failure as Menu Button (interactive rows, frozen)

| Component | Structure | Suggested fix |
|-----------|-----------|---------------|
| **`_Sidebar/Menu Button`** | FIXED 32, pad-Y 0, no height bind | Prefer: height → `control-height/md` **or** HUG + `padding-y/sm` (match `_Menu/Item` row). Apply all State variants. |
| **`_Table/Cell`**, **`_Table/Head`** | FIXED 40, pad-Y 0 | Bind height to denser row token (new `control-height`/`row-height` or pad-Y + HUG). |
| **`_Tabs/Trigger`** | FIXED 26, pad-Y 0 | Height or pad-Y → Density. |
| **`_Pagination/Item`** | FIXED 36, pad-Y 0 | Height → `control-height/md` (or sm). |
| **`_Calendar/Day`** | FIXED 32, pad-Y 0 | Height → Density (or Size axis aliased). |
| **`_Dialog/Close`**, **`_Sheet/Close`** | FIXED 28, pad-Y 0 | Height → `control-height/sm`. |
| **Layout `Header`** | FIXED 48, pad-Y 0 | HUG + `padding-y/md` **or** minHeight/height → density chrome token. |

### P1 — works via nest / size axis; polish only

| Component | Notes |
|-----------|--------|
| Button / Select | pad-Y 0 + center is fine; height aliases Density. |
| `_Menu/Item` | Outer 0; inner `row` has `padding-y/sm` — **reference pattern**. |
| `_Sidebar/Header|Group|Footer` wrappers | Outer 0 + center; **content SLOT** already on `padding-y/md`. |
| Avatar | Size axis (`sm/md/lg`) aliases Density `avatar-size/*` (24/20/28 · 32/28/36 · 40/36/44). Circle + glyph scale together. |

### P2 — static semantic pad on slots (not zero, but not Density)

Card / Dialog / Sheet / Empty State / Dropdown / Command / Menubar content slots often bind pad-Y to `space/*` or `Spacing/space-*` instead of `padding-y/*` or `container/*`. They do change absolute inset but **not** with Density mode. Retarget when those surfaces should breathe with density.

## Fixes applied — 2026-07-31

Recipe used (repeatable): **HUG vertical + `padding-y/*` + `minHeight` → `control-height/*`**.
`minHeight` pins the component to the control ladder; HUG + pad-Y prevents clipping when the density
type ladder outgrows that floor.

Measured across all three modes (Compact / Normal / Spacious):

| Component | Change | Compact | Normal | Spacious |
|-----------|--------|---------|--------|----------|
| `_Sidebar/Menu Button` (4 states) | `padding-y/xs` + minH `control-height/md` | 28 | **32** | 36 |
| Layout `Header` | HUG + `padding-y/sm` (spacer neutralized to 1px) | 40 | **48** | 56 |
| `_Table/Cell` | HUG + `padding-y/lg` | 32 | **40** | 48 |
| `_Table/Head` | HUG + `padding-y/lg` | 32 | **40** | 48 |
| `_Tabs/Trigger` (10 variants) | `padding-y/xs` + minH `control-height/sm` | 24 | **28** ⚠ | 36 |
| `_Pagination/Item` (4 states) | `padding-y/xs` + minH & width `control-height/lg` | 32 | **36** | 40 |
| `_Calendar/Day` (7 states) | `padding-y/xs` + minH `control-height/md` | 28 | **32** | 36 |
| `_Dialog/Close` | `padding-y/xs` + minH & width `control-height/sm` | 24 | **28** | 32 |
| `_Sheet/Close` | `padding-y/xs` + minH & width `control-height/sm` | 24 | **28** | 32 |
| Button / Select (unchanged reference) | — | 28 | 32 | 36 |

⚠ **Only Normal-value change:** `_Tabs/Trigger` 26 → **28**. 26 was off the control ladder; 28 = `control-height/sm`.

### Why `minHeight` and not plain HUG

First pass used HUG + `padding-y/sm` on Menu Button. Normal stayed 32, but **Spacious hit 40** while
Select next to it stayed 36 — because the density *type* ladder grows line-height 16 → 20 → 24 while
`control-height/*` grows 28 → 32 → 36. Pure padding sizing therefore drifts off the control ladder at
Spacious. `minHeight` + light `padding-y/xs` keeps both: ladder-exact at every mode, clip-safe if type
or label grows.

### Known follow-ups (not changed)

- Layout `Header` `spacer` frame was FILL-vertical (blocked HUG); set to FIXED 1px. Purely structural.
- P2 static-pad slots (Card / Dialog / Sheet / Empty State / menu surfaces) still bind `space/*`
  rather than `padding-y/*` or `container/*`.

## Icon-size density ladder — 2026-07-31

Material Symbols here are **TEXT glyphs**, one component per icon with a Filled variant (Figma does
not expose all variable-font axes to the API, so the styles are separate variants).

**The size lever is glyph `fontSize`; the bounding box must be free to follow it.** Icon masters were
authored with `minWidth/maxWidth/minHeight/maxHeight` all pinned to 20, which froze the frame no
matter what `fontSize` resolved to. The working recipe:

1. Clear any bound `width`/`height` on the icon frame
2. Clear **all four** min/max constraints (this is the actual blocker)
3. Glyph TEXT → HUG / HUG
4. Icon frame → HUG / HUG
5. Glyph `fontSize` → `icon-size/*`

Do **not** bind frame width/height — that re-pins the box. Rule of thumb for md: icon =
control-height − 12 (6px air each side).

> **Local-environment caveat:** if `Material Symbols Outlined` is not installed locally, text metrics
> are frozen (`hasMissingFont: true`) and plugin-side measurements will report a stale 20×20 even
> when the wiring is correct. Verify with a **server-rendered screenshot**, not `node.width`.

### Tokens (`Foundations / Semantics / Density`)

| Token | Compact | Normal | Spacious | Role |
|-------|---------|--------|----------|------|
| `icon-size/xs` | 12 | **12** | 14 | Button Size=xs |
| `icon-size/sm` | 12 | **16** | 20 | Menu Item; Button Size=sm |
| `icon-size/md` | 16 | **20** | 24 | Default control icons |
| `icon-size/lg` | 20 | **24** | 28 | Large controls |
| `avatar-size/sm` | 20 | **24** | 28 | Avatar Size=sm (= control-height/xs) |
| `avatar-size/md` | 28 | **32** | 36 | Avatar Size=md (= control-height/md) |
| `avatar-size/lg` | 36 | **40** | 44 | Avatar Size=lg — dedicated (not control-height/lg) |

Scopes: `WIDTH_HEIGHT` + `FONT_SIZE`. Values alias semantic `space/*`.

### Wiring

- **4,244** Icons-page masters: min/max cleared, frame + glyph HUG, `fontSize` → `icon-size/md`
- **64** consumer icon instances (Button leading/trailing, Menu Button, Select, Close): size binds and
  min/max cleared, set to HUG so they inherit the master's hug
- `Button / Size`.`iconSize` → `icon-size/xs|sm|md|md` (Size × Density)
- Button Leading/Trailing nested `fontSize` → Size `iconSize`
- `_Menu/Item` icons → `icon-size/sm`

### Result (glyph + box, C / N / S)

Menu Button, Select, Close, Button default: **16 / 20 / 24**. Menu Item: **12 / 16 / 20**.
Verified by server-rendered screenshot of a temp three-mode board (since deleted).

### Normal drifts

- Button Size **sm** icon 14 → **16**
- Button Size **default** binding was `space/4` (16) but rendered 20; now `icon-size/md` = **20**

## Icon usage audit — consumers, not masters — 2026-07-31

Scope: every instance on `Components`, `Components · Base UI Additions`, `Features`, `Layout` whose
first TEXT child uses a Material Symbols family. **434 icon instances.**

| Sizing source | Count | Meaning |
|---------------|-------|---------|
| `icon-size/md` | 180 | Default 20 (16 / 20 / 24) — density-aware |
| Button `iconSize` | 63 | Size × Density via `Button / Size` — density-aware |
| `icon-size/sm` | 20 | Deliberate inline/dense — density-aware |
| `icon-size/xs` | 2 | Micro (`open_in_new`) — density-aware |
| **Literal px** | **171** | **Density-blind** — hard-coded 14 / 16 / 18 from manual resize |

**20×20 is the default**: all 4,244 Icons-page masters bind glyph `fontSize` → `icon-size/md`.
Off-scale consumers are instance-level resizes, not a master problem.

### Off-ladder mechanism (the `more_vert` 16 → 13 case)

`UserIdentity` in the Sidebar footer is **not a component** — it is authored inline in 5 separate
Sidebar slot instances. Its `more_vert` was manually resized 20 → 16, which Figma stores as a **0.8
scale override**, not a fontSize override. Once the master became density-aware, that 0.8 multiplied
the token instead of replacing it: Compact 16 × 0.8 = **12.8**, Normal **16**, Spacious 24 × 0.8 = **19.2**.

Any manually resized icon behaves this way. The ladder is correct; the override rides on top of it.

### Blocker — `fontSize` binds do not stick on instance children

**This is an API constraint, not a font problem.** Proven by control test:

| Node | Font | Loads? | `setBoundVariable('fontSize')` |
|------|------|--------|-------------------------------|
| `16:691`, `26:2177`, `56:2055`, `17:955` (icons, 0 instances above) | Material Symbols Outlined | no | **dropped** |
| `13:98` `_Select/Item` label (0 instances above) | **Inter** | **yes** | **dropped** |
| Same nodes, `node.fills = …` | either | — | **works** |

The call returns without throwing and the read-back is unchanged. It fails with a fully-loaded font,
so reinstalling Material Symbols does **not** unblock it. Instance children accept paint writes but
not `fontSize` variable binds — the bind has to live on the main component.

Separately, `Material Symbols Outlined` is still invisible to Figma here (only `Material Symbols
Rounded` and `Material Symbols Sharp` enumerate, even after a Font Book reinstall — Figma caches its
font list at launch, so it needs a restart). While it is missing, `node.fontSize` / `node.width` on
icon text are **stale local artifacts** — verify with a server-rendered screenshot, not `node.width`.

### `Icon / Size` collection (architecture)

`VariableCollectionId:339:25` · variable `size` (`VariableID:339:26`) · modes
**default / xs / sm / lg / control**.

| Mode | Resolves to |
|------|-------------|
| `default` | Density `icon-size/md` (16/20/24) |
| `xs` / `sm` / `lg` | matching `icon-size/*` |
| `control` | `Button / Size`.`iconSize` (Size × Density) |

All **4,244** icon masters bind glyph `fontSize` → `Icon / Size`.`size`. Instances pick size via
**explicit mode**, not instance-level fontSize binds (those don't stick). Button nested icons use
`control`; Menu/Select items use `sm`.

### CRITICAL — nested icons need `INSTANCE_SWAP` props

Manual nested-instance swaps (Figma's default swap UI on an exposed child) store the choice as a
**component-swap override**. `resetOverrides()` destroys that identity — the instance falls back to
the master's default icon.

**Regression 2026-07-31:** a blind `resetOverrides` sweep on consumer icons wiped Sidebar Menu Button
icon swaps across density shells (`313:2782`); nearly every row reverted to `home`.

**Rule:** any parent that nests a swappable icon must have:

1. An **`INSTANCE_SWAP`** component property linked via `componentPropertyReferences.mainComponent`
2. The nested icon **`isExposedInstance = true`** so the property surfaces in the instance panel

Do **not** rely on bare nested swaps for icon identity. Do **not** run blind `resetOverrides` on
instances that still lack INSTANCE_SWAP for their icons.

#### INSTANCE_SWAP props added this session

| Host | Props |
|------|-------|
| `_Sidebar/Menu Button` | `Icon` |
| `Button` | `Leading icon instance`, `Trailing icon instance` (BOOLEAN show/hide kept) |
| `Input` | `Leading icon instance`, `Trailing icon instance` |
| `Select` | `Icon` |
| `_Dialog/Close`, `_Sheet/Close` | `Icon` |
| `_Collapsible/Trigger` | `Icon` |
| `_Menu/Item` | `Leading icon instance`, `Check icon instance`, `Submenu icon instance` |
| `Toast` | `Status icon instance`, `Close icon instance` |
| `Alert` | `Icon instance`, `Dismiss icon instance` |
| `_Accordion/Item`, `_NavMenu/Trigger` | `Icon` |

`_Avatar/Badge` already had `Icon` — reference pattern.

### Layout shell icon restore — corrected map

Restored **via the `Icon` INSTANCE_SWAP** so future resets can't destroy identity.

| Label | Icon | Outlined variant |
|-------|------|------------------|
| Dashboard | `dashboard` | `6:2010` |
| Business Objects | `business` | `6:4463` |
| Team | `group` | `7:4105` |
| Schema Registry | `schema` | `6:6806` |
| Documents | `description` | `6:2065` |
| Settings | `settings` | `6:3080` |
| Get Help | `help` | `6:2335` |
| Search | `search` | `6:3050` |

**Icon semantics follow the label.** `home` is only the Menu Button master's placeholder — Dashboard
must use `dashboard`, which exists in the library. Keep `home` as the master default.

### Nested icon colour binds to the state variable, not the surface variable

Sidebar nav icons had drifted onto `sidebar/foreground` (static) or a bare `foreground`, while the
sibling label sat on `Sidebar / Menu Button`.`foreground` — which is state-aware. Selected therefore
went blue on the text but stayed dark on the icon. All 45 glyphs rebound to
`Sidebar / Menu Button`.`foreground`.

**2026-08-05 — idle icons match label, not muted.** Default/Focus icon layers still bind
`foreground-muted`, but that token’s **Default** mode now aliases `surface/foreground` (same as
`foreground` Default). Hover/Selected variants bind `foreground` directly. Code mirrors this:
centric-ui dropped `[&>svg]:text-sidebar-accent-foreground` on `SidebarMenuSubButton`; prototype
nav icons inherit the button’s `text-sidebar-foreground` / selected / hover classes (no
`text-muted-foreground`).

**Rule:** a nested icon's fill binds to the *same* state-aware variable as its sibling label.

Because identity now lives in the INSTANCE_SWAP property, `resetOverrides()` on an icon instance is
**safe** — it clears stale `characters` / `fills` / scale without changing which icon it is. That is
how a stale `characters: "Search"` override on 4 Documents rows was cleared.

### `resetOverrides` — still valid, but scoped

Clears scale overrides + paint; **also clears component-swap overrides** unless those swaps live in
INSTANCE_SWAP properties. Capture paint → reset → restore paint. Never sweep hosts that only have
nested-swap overrides.

### Slot content is structurally locked

Slot-authored content: `insertChild` / `remove()` blocked; `swapComponent()` works. Reach via **raw
id** (`17:705`), not only the `I…;…` proxy path.

### `Icon Button` — a real component that *wraps* Button

`Icon Button` (`350:2877`, Components ▸ Button section) **contains a real Button instance**. Nothing
about fills, radii, states or variants is reimplemented.

| Aspect | How |
|--------|-----|
| 1:1 square | inner Button `layoutSizingHorizontal = FIXED` + `width` bound to **`Button / Size`.`height`** (`VariableID:7:4857`) — same token as height, so square by construction at every size and density |
| Icon centred | inner Button is already `CENTER` on both axes |
| Padding | inner Button pinned to `Button / Layout` = **`icon-only`** → `paddingX` resolves to `iconOnlyPaddingX` |
| Variant / Size | explicit modes **cleared** on the inner Button so the consumer drives them from the Icon Button instance |
| Props | inner Button `isExposedInstance = true` → `Leading icon instance` (INSTANCE_SWAP), `State` etc. bubble up; the nested icon is exposed two levels deep |

Verified square across the whole matrix:

| Size | Compact | Normal | Spacious |
|------|---------|--------|----------|
| xs | 20 | 24 | 28 |
| sm | 24 | 28 | 32 |
| default | 28 | **32** | 36 |
| lg | 32 | 36 | 40 |

`Button / Layout` (`VariableCollectionId:345:2837`) modes **default / icon-only** stay as the
underlying token: `paddingX` → `Button / Size`.`paddingX` or `iconOnlyPaddingX`.

### UserIdentity `more_vert` → Icon Button

All 5 Layout copies are now **Icon Button** instances named `More actions` (ghost / sm, `more_vert`
via the exposed Leading INSTANCE_SWAP) — 24 / 28 / 32 square, scale drift gone. Still authored inline
in slots; promote to `_Sidebar/User` so the affordance isn't duplicated five times.

### Render caveat — stale rasterisation while the icon font is missing

With `Material Symbols Outlined` absent, the desktop app cannot re-lay-out icon text, so **server
screenshots keep the pre-change glyph even when the file data is correct**. Confirmed: masters *and*
instances read `description` / `more_vert` (correct codepoints, correct main components), yet renders
still showed the old search / add glyphs. Component *swaps to untouched masters* do render (the
`dashboard` fix appeared immediately). Restart Figma after installing the font, then re-verify — do
not "fix" what the data already says is right.

### Bare icon vs icon button — remaining

**Done:** UserIdentity more_vert ×5; nested icon-only `Button`s in Schema Action Buttons (4),
Graph Controls Toolbar (5), Canvas Toolbar (3), View Toolbar (1), Header (4: 1×sm + 3×xs theme
switcher). App Shell inherited Header. All `ghost/secondary`, square via width→`Button / Size.height`.

**Icon Button fix (2026-08-03):** master now binds inner Button **width** to the same `height`
token (was hug-content — square only by coincidence at md). Cleared stale height/radius binds left
on shells after `swapComponent`.

**Bare action icons → Icon Button (2026-08-03):** ~47 swaps on component masters. Preserved icon
identity; `ghost/danger` for deletes; `ghost/secondary` otherwise; xs for dismiss/clear/compact,
sm for row/toolbar. Reset `scaleFactor` 0.8→1 on swap (carried from scaled feature frames).

**Follow-up (2026-08-06):** Field clear / Toast+Alert dismiss bumped **xs→sm** (16px glyph in 32
surface). Carousel prev/next swapped from bare chevrons → Icon Button sm. Canonical rules now in
[[figma-ds-surface-authoring]] §§18–19 (field adornment `gap/xs` edge + icon-only → Icon Button).

| Host | Icons | Notes |
|------|-------|-------|
| Input (×4 states) | close | Clear — xs |
| Alert (×6) / Toast (×5) | close | Dismiss — xs; status `info` left bare |
| Widget Card / Section / Picker / Editable Frame | more_horiz, add, push_pin, close | Chrome actions |
| Schema Palette | add ×3 | Checks left as selection indicators |
| Member Detail / Relationship | delete | `ghost/danger`; tiny `open_in_new` left |
| Documents Table | download+delete ×4 rows, chevrons | Row + page nav |
| Inline Edit Field | edit, check, close | Confirm/cancel |
| Calendar Single+Range | chevron_left/right | Month nav |

**Left alone (intentional):**
- `_Dialog/Close` / `_Sheet/Close` — Sean handles via parent subcomponent
- Pagination ellipsis `more_horiz` — decorative gap marker (not a control)
- Breadcrumb separators, tree/collapsible disclosures, menu/command leading icons, checkbox/
  select checks, Alert/Toast status glyphs, `drag_indicator`

**Pagination → Buttons (2026-08-03):** Prev/Next and `_Pagination/Item` are real `Button`
instances. Shared `Pagination / Control` tokens + Button / Variant mode `pagination` (primary
hover overlays; radius `control-radius/sm`). Active page uses Variant=`default` (solid primary).

**Correctly bare:** Select/Combobox/NavMenu expanders, tree disclosure, breadcrumb separators,
status glyphs, input `search`, menu leading icons, decorative file/stat glyphs, `drag_indicator`.

## Button ghost status + inverse variants — 2026-07-31

`Button / Variant` (`VariableCollectionId:7:4851`) gained 6 modes — 17 total:

| Mode | background | foreground (text + icon) | ring |
|------|-----------|--------------------------|------|
| `ghost/info` | transparent | `status/info/soft/foreground` | `status/info` |
| `ghost/success` | transparent | `status/success/soft/foreground` | `status/success` |
| `ghost/warning` | transparent | `status/warning/soft/foreground` | `status/warning` |
| `ghost/caution` | transparent | `status/caution/soft/foreground` | `status/caution` |
| `ghost/danger` | transparent | `status/destructive/soft/foreground` | `status/destructive` |
| `ghost/inverse` | transparent | `action/primary/foreground` | `action/primary/foreground` |
| `ghost/primary` | transparent | rest=`surface/foreground`; hover/pressed=`action/primary` | `chrome/ring` |
| `ghost/secondary` | transparent | `surface/foreground` | `chrome/ring` |

`border/default` is transparent on all. Works on both Button and `Icon Button`. Ghost modes are
slash-grouped (`ghost/primary`, `ghost/secondary`, `ghost/info`, …). `ghost/secondary` is the
renamed former bare `ghost`.

### Why `soft/foreground` and not the solid status hue

The solid `status/*` tokens are **fill** colours — every one fails WCAG AA for text on
`surface/background` in Light mode. Measured:

| Token | Light contrast | `…/soft/foreground` |
|-------|----------------|---------------------|
| `status/info` #00a2c7 | 3.00 ✗ | #107d98 → **4.76** ✓ |
| `status/success` #30a46c | 3.16 ✗ | #218358 → **4.72** ✓ |
| `status/warning` #f76b15 | 2.97 ✗ | #cc4e00 → **4.51** ✓ |
| `status/caution` #ffe629 | **1.26** ✗✗ | #9e6c00 → **4.57** ✓ |
| `status/destructive` #e5484d | 3.91 ✗ | #ce2c31 → **5.21** ✓ |

Dark mode passes comfortably either way (8.95–14.91). Rings keep the solid hue — a focus ring is a
non-text UI component, where 3:1 is the bar and the saturated hue reads better.

> Pre-existing, unchanged: the `destructive` mode still uses solid `status/destructive` as its
> foreground (3.91 on white). Worth revisiting on its own.

### Hover states — CORRECTED, then generalised

**An earlier entry here claimed Hover was pixel-identical to Default on every variant. That was
wrong.** The check inspected only `fills` and matched child names against `/overlay|hover/i`; the
real node is named `[state-layer]`, so it was missed. Hover always worked.

What actually existed: a Material-style `[state-layer]` rectangle on Hover/Focus/Pressed/Open, fill
bound to that variant's `foreground/default`, alpha carried as **node opacity** (0.12 / 0.24 / 0.32).
Self-adapting (ghost tints dark, solid tints white) but with the alpha outside the token system.

Superseded 2026-07-31 by the overlay model — the `[state-layer]` now binds `interaction/*` tokens at
node opacity 1. Full architecture: [[interaction-state-semantics]].

**Lesson:** a name-regex probe is not an inspection. Enumerate children and read every paint before
declaring something missing.

## COMPONENT_SET bounds after density growth — 2026-08-06

Variant **components** may HUG correctly while the parent **COMPONENT_SET** stays FIXED/`layoutMode: NONE` and clips (`clipsContent` + height < max child bottom). Density-taller children (e.g. Calendar after Day square fix) overflow the set chrome even when variants themselves are fine.

**Fix at set level** (match Button-style sets: no auto-layout on the set): `resizeWithoutConstraints` to `contentExtent + existing pad` (usually `min child x/y`), clear leftover `minHeight`/`maxHeight` with `null`, prefer `clipsContent = false` once fitted. Do **not** hug Icon Button / focus-ring overflows (~2–4px intentional). Stickersheet Compact calendars at ~270 vs Normal master ~300 are density-mode, not a set bug.

Applied: Calendar `64:3184` 660×326→674×380; also Carousel, Date Picker, `_Tabs/Trigger` width, Toggle width.

## Recommended repair rules

1. **Row / nav / cell / day / page-control:** either bind **height** to `control-height/*`, or switch to **HUG** and bind **pad-Y** to `padding-y/*` (inner wrapper ok, as Menu Item).
2. Do **not** rely on CENTER alone for vertical rhythm under Density.
3. Keep Button-style pad-Y=0 only when height is Density-backed.
4. Leave explicit Density mode on **app/chrome** frames (like Example density); keep component masters on Auto.
5. After density child growth, **refit COMPONENT_SET bounds** (see above) — variant HUG alone does not expand the set frame.

## Related

- [figma-component-token-axes.md](figma-component-token-axes.md) — instance vs context axes
- [centric-plm-design-system.md](centric-plm-design-system.md) — density collection notes
