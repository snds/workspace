---
tags: [design-systems, figma, authoring, surfaces, tokens, transliteration, accessibility]
created: 2026-06-30
updated: 2026-08-06
status: stable
confidence: high
sources: [centric-ui Figma library authoring sessions 2026-06; density/overlay construction 2026-08; field adornment optical inset + Icon Button audit 2026-08-06; migrated from local memory ds-figma-surface-conventions / transliteration-focus-and-positioning / figma-use-linked-library-components]
related_skills: [figma-canvas-designer, design-engineer, ds-advisor, figma-plugin-dev]
related_projects: [centric-ui VMS DS, 02-centricPLM]
---

# Figma DS surface authoring — durable conventions

Durable layout/authoring decisions for design-system Figma libraries (validated on the
centric-ui library). They apply to **any** surface/overlay, not just the component that
first surfaced them, and hold regardless of the task. Three clusters: **surface/overlay
construction conventions**, the **build-from-real-components rule**, and the
**code→Figma transliteration judgment calls**.

## A. Build from real components — never hand-build approximations

**Rule.** Build every control by instancing a component from the file's linked/enabled
libraries — or by reusing/cloning an existing correct on-canvas instance — **not** by
drawing rounded-rects + text. Non-negotiable in a design-system-owned file.

**Why.** Hand-built approximations drift from the system, don't bind to variables/themes,
carry no states or variants, aren't maintainable, and read as obviously off to a DS author.
Real instances carry tokens, states, and variants for free and keep mockups system-true.

**How to apply.** Before drawing ANY control: (1) find the matching library component —
`search_design_system` by name, or read an existing instance's main component via
`getMainComponentAsync()`; (2) `await figma.importComponentByKeyAsync(key)` then
`.createInstance()`, OR `.clone()` an existing correct instance; (3) set variant / component
properties (`instance.setProperties({...})`, e.g. `isDisabled`, `State`, `Size`) and set
label text by loading the inner text layer's font then editing `.characters`. When no library
component exists, do NOT hand-build a one-off inline approximation — **generate a local
component / component set** (named `local/…`) for any element placed more than once or that
represents reusable page content (property rows, card headers, form-view bars, galleries).
Local components are worth creating even if never promoted. Reserve raw primitives (a lone
rectangle/text) for genuinely one-off, non-repeating decoration, labeled as placeholders.

**Props-first for every instance (hard requirement).** To change ANY aspect of an instance —
visibility of a part, an icon, a state, a label — FIRST look for a component property
(boolean / variant / instance-swap / text) that controls it: read `instance.componentProperties`
and set with `instance.setProperties({...})`. **If a property exists, it was designed for that
change — use it.** Manual overrides (`node.visible=false`, direct fills, nudging children) are
legitimate ONLY after confirming no property covers the need — never the first reach. When no
property exists for a change the design clearly requires (e.g. a `Select/Field` with no way to
hide its clear-✕), that's a **design-system gap**: do the minimal correct manual override —
toggle the part's **outermost container instance**, not just its inner glyph (hiding the glyph
leaves the wrapper occupying space) — AND record a backlog item / flag it to the DS owner so
the component gains the missing prop.

## B. Surface & overlay construction conventions

0. **Density-awareness is the default (STANDING RULE, Sean 2026-08-06).** When binding
   spacing, padding, gap, radius, height/width, or type on controls and their overlays, prefer
   **`Foundations / Semantics / Density`** tokens (`control-height/*`, `control-radius/*`,
   `padding-x/*`, `padding-y/*`, `gap/*`, `type-size/*`, `popover/offset-y`, …) over raw
   primitives or a Density-unaware Radii/Spacing alias — **especially when in doubt.** Control
   chrome must keep working under a Density-only mode pin (Compact/Normal/Spacious) without also
   pinning Radii. General surface radius (cards, dialogs) may still use the Radii ladder
   (`radius/xxs…4xl`); field-adjacent overlays follow Rule 10a. Figma-only construction tokens
   (focus-ring radii, `popover/offset-y`, Calendar Day corner masks) carry
   `[figma-only][sync:ignore]` in their descriptions — do not export them as product CSS.

1. **Separators are edge-to-edge by default.** A header/footer separator — or a border *used
   as* a separator — bleeds to the container's edge. Mechanism: the content **slot carries 0
   horizontal padding**; each content block carries its OWN side inset; separators/borders span
   full width. **BUT interactive rows (menu/list/option items) keep an internal horizontal
   inset** so their hover/selected highlight does NOT touch the container edge: build the item
   as a **full-width transparent wrapper** (separators bleed) with the **highlight/bg on an
   inset INNER frame**. Net: separators bleed full-width *and* the item state stays inset.

2. **Use spacing tokens — but don't snap blindly.** Prefer Density `padding-*` / `gap-*` on
   controls; fall back to semantic `space-*` where Density has no role token. Bind via
   `node.setBoundVariable('paddingLeft'|…|'itemSpacing'|'counterAxisSpacing', variable)`.
   Half-steps: `space-0-5`=2, `space-1-5`=6, `space-2-5`=10, `space-3-5`=14. Button Size modes
   resolve `paddingX`/`gap` through Density (`padding-x/sm|md`, `gap/sm`) — do not reintroduce
   raw 10/6 literals. Skip binding `0` and intentional negative item-spacing. Radii: controls →
   Density `control-radius/*`; general surfaces → density-modeled `radius/xxs…4xl` ladder.

3. **Popovers/dropdowns that are part of a parent component are absolutely positioned** so the
   open panel does NOT grow the parent's bounding box. Pair with a **BOOLEAN component property
   bound to a component-specific variable** to toggle visibility (open/closed).
   **Density-aware offset (2026-08-06):** Figma cannot bind absolute `y` or express
   `top:100% + gap`. Use absolute `[popover-anchor]` → in-flow `[popover-offset]` (height =
   Density `popover/offset-y` = `control-height/md + 4`) → panel. Keeps a constant **4px** gap
   under Compact/Normal/Spacious (`space-1`). Token is `[figma-only][sync:ignore]`; code uses
   `top:100%` + margin. Menubar adds `[popover-pad-clear]` (`Spacing/space-1`) above the offset
   when the bar pads the trigger. **Selection hygiene:** lock `[popover-offset]` /
   `[popover-pad-clear]` (`locked=true`); keep the panel frontmost under the anchor; put
   `[popover-anchor]` behind the field/trigger so deep-select prefers the control chrome.

4. **Icons must match their label — glyph AND color.** (a) *Glyph*: audit every popover/menu/
   list item — pick the semantically correct Material Symbol (the placeholder `more_horiz` on a
   "Share" item is wrong). (b) *Color*: an icon's fill must match its adjacent label's color so
   they read as one unit — bind the glyph fill to the same token as the label, never a raw color.
   The "inverted icons" bug was glyphs left at raw `Color/Base/White` on a light tint = invisible.

5. **No double padding from slotted content.** When a component consumes a parent that already
   provides inset (Popover content slot=10, Card/Dialog header inset), the slotted content must
   NOT re-add its own border/inset. **Popover-consumer pattern (Command/Combobox/Date Picker):**
   set the Popover **content slot L/R pad → 0**, let the slotted child own ALL inset, set the
   slot's direct children to `layoutSizingHorizontal=FILL`. Makes (a) the search/list **divider**
   (bottom-only stroke) bleed edge-to-edge; (b) the Calendar/Command FILL the popover so trigger
   field and popover share one width (Rule 9); (c) item-row highlights stay inset (Rule 1). A
   child re-drawing a full all-sides border inside an already-bordered Popover = double border →
   strip it. A *bottom-only* divider is fine and should bleed — don't mistake it for a double border.

6. **Slotted content fills or hugs per design intent.** Verify each slot's children — Command
   menu items FILL the menu width; chips/inline content HUG. Default: list/menu rows FILL.

7. **No empty frames used only for spacing.** Remove them (they don't exist in code). Hide first
   to confirm no gap regression, then adjust real spacing.

7a. **Clip-content cropping — a must-catch, with a known sizing gotcha.** Actively check every
   rendered layout for content cropped by an ancestor's `clipsContent` toggle (text cut mid-line,
   images sliced, values ending abruptly). Fix procedure: (1) disable the ancestor's clip so the true
   overflow is visible; (2) reassess the structural parameters causing it — hug/fill sizing on the
   element AND its ancestors, plus constraints — usually let the container/element hug (grow) so
   content fits, or adjust the pinning constraint; (3) OR apply intentional truncation/ellipsis if the
   layout's intent calls for it (dense grids, fixed-height cells where growth breaks rhythm). Choose by
   context: forms/descriptions/read views want grow+wrap; dense data grids may want truncation — never
   leave content silently sliced. **Gotcha:** calling `resize()` AFTER setting `counterAxisSizingMode =
   "AUTO"` (or HUG) resets height to FIXED → multi-line content then clips. Set sizing modes last, or
   re-assert HUG after resize.

7b. **Clip-content stays OFF by default — never enable it unless absolutely necessary (STANDING RULE,
   Sean 2026-06-30).** On every frame, component, and **component SET**, leave `clipsContent=false`.
   Clipping silently cuts off the exact things DS cells depend on overflowing: indicator/effect
   overlays, dropdowns/popovers, focus rings, drop shadows. **Critically, a component-SET frame with
   `clipsContent=true` does NOT auto-grow and HIDES any newly-added variant** (cost a real debugging
   cycle when a 4th `.cell/indicator` variant rendered invisibly until the set was resized). The only
   legitimate exceptions are narrow and deliberate: true image/media **CROP** frames, and intentional
   dense-grid truncation (Rule 7a step 3). Default construction = clip OFF; when building or auditing,
   treat any `clipsContent=true` as a smell to justify or clear. Sweep is cheap — recurse the tree and
   set `clipsContent=false` wherever true (skip genuine image-crop frames). This is the default-OFF
   companion to 7a's detect-and-fix procedure.

7c. **Indicators/badges that can land on a variable background need a contrast backing (halo).** A small
   status dot/ring (e.g. a cell corner indicator) reads fine on a plain/white cell but loses contrast on
   image thumbnails, hover tints, or colored chips (light-on-light, color-on-busy). Give the mark a white
   **halo backing disc** (mark + ~3–4px, placed *behind* it) plus a faint drop shadow (≈0.14 alpha, r1.5)
   — the avatar-status-dot pattern: near-invisible on white at real cell scale, legible on any surface.
   **Prefer ONE shared treatment** (refactor the indicator component) over forking an image-only variant —
   avoids divergence and covers tints/chips for free. Judge it at REAL cell scale, not a high-zoom preview
   (zoom exaggerates the halo/shadow). Validated on C8 cell corner indicators over refmap-image Filled photos.

8. **Oriented overlays (Tooltip, Hover Card) need a variant per required position** (Top/Right/
   Bottom/Left ± align). The **caret/arrow's halfway point must sit flush with the parent
   container's boundary** — use absolute positioning for the caret (Figma has no negative padding).

9. **Nested components get the right hug-vs-fill for their context.** A trigger Input FILLs its
   parent's width and its popover matches that SAME width (Date Picker: field + calendar popover
   are one width). Never leave a nested component at an arbitrary fixed size mismatching siblings.

10. **Corner-radius has two families.** *Control-family* (buttons, inputs, OTP slots, calendar
    day cells, pagination items, toggles, **field-adjacent panels**) → Density
    **`control-radius/sm|md`** (literals 4/8/12 and 8/12/16 across C/N/S — not Radii aliases).
    Default Input/Select/Button → **`control-radius/md`**; Size=sm / compact chrome →
    **`control-radius/sm`**. *Inset-row-highlight* (menu-item highlight, radio-row selection)
    stays a tighter inset radius (paired with Rule 1's inset wrapper). Bind via the four corner
    fields. Focus rings use `[figma-only]` `focus-ring-radius/*` (= control-radius + offset).

10a. **Field-anchored overlays match the trigger's control radius (STANDING RULE, 2026-08-06).**
    Any dropdown/popover/list/calendar that visually belongs to a parent field or control must
    use the **same Density `control-radius/*` rung as that trigger** — usually `md` next to
    Input / Select default / Popover / `_Select/Content`. Do **not** leave the panel on
    `control-radius/sm` (or a Radii `radius/*` alias) when the field is `md`; the mismatch reads
    as a broken nest. Validated fixes: Calendar, Command, Dropdown Menu, Context Menu →
    `control-radius/md` to align with Input/Popover/Select content. Tooltips stay `sm` (small
    floating chrome, not a field panel twin). Modals (Dialog/Drawer) stay on the Radii ladder
    (`radius/xl`, etc.) — not field-paired.

10b. **Toggle Group nests like a field next to Button/Input (2026-08-06).** Parent shell →
    Density **`control-radius/md`** + **`control-height/md`** (horizontal); inset/gap →
    `[figma-only]` `toggle-group/inset` (=2). Items use **`Toggle Group / Item`** modes
    (`standalone` | `h-*` | `v-*`) bound to `Item/top-*|bottom-*` — group end-caps resolve
    `toggle-group/item-radius` (= md−2 → 6/10/14 C/N/S), shared edges → `radius/none`.
    Standalone Toggle stamps mode `standalone` → still **`control-radius/sm`**. Slot consumers:
    set the Item mode on each Toggle instance (do not leave Auto).

11. **Input-trigger composites get a full State axis.** Any component whose trigger is an Input
    (Combobox, Date Picker, search fields) exposes `State=Default/Focus/Error/Disabled` as a
    variant axis driving the inner Input's state — not just an `Open` boolean. Body text is **14
    (`font-size-sm`)**, never 13; bind every non-icon text node's fontSize to a `font-size-*`
    token (exclude Material Symbols glyph nodes — their size is an icon dimension, not type).

12. **Variant architecture is MODE-FIRST (always, wherever possible).** Express a component's
    varying *primitives* — intent/tone colors, size, density — as variable **modes** on a
    component-scoped collection (`Button — Variant` has 11 intent modes; `Button — Sizes` has size
    modes), with parts bound to role tokens (`background/*`,`foreground/*`,`border/*`,`ring/*`;
    `height`,`paddingX`,`gap`,`radius`,`iconSize`) that resolve per mode. Litmus, in order: **a
    variable can carry it → mode+token; it's a part's presence → BOOLEAN (bound to `visible`); it's
    true structure or a non-bindable prop (e.g. link underline — `textDecoration` isn't
    variable-bindable) → physical VARIANT** (the only justified use). Never duplicate a mode system
    as physical variants — an intent×state Button is 7 state-variants × N intent-modes, NOT 42
    physical variants. Modes also give free light/dark/brand theming. If a collection needs more
    modes than allowed (Enterprise=40), split components into separate library files.

13. **TOTAL tokenization — bind every bindable value, including zeros and blanks.** No raw
    literals: fills, strokes, stroke-weight, corner radius, padding, gap/item-spacing, font
    size/line-height. Zeros/blanks are NOT exempt: pad/gap 0 → `space-0`, radius 0 → `radius-none`,
    stroke 0 → `border-width-0`, transparent fill/stroke → the **`transparent`** color token (a
    bound zero-alpha paint — primitive `Color/Base/Transparent` ← semantic `transparent`), **never**
    an empty paint array. If a parameter type lacks a 0/none/transparent helper, **CREATE it**
    (primitive value ← semantic alias) — never hardcode around a missing token. Sanctioned raw
    exceptions, *noted* not silently left: Figma SECTION chrome (bg/border) and deliberate negative
    overlaps (avatar group's −8 item-spacing).

14. **Floating elements are absolutely positioned at their logical location — never in-flow —
    even when toggled by a visibility boolean.** Anything that visually floats over/around its host
    — tooltips, value bubbles, focus rings, hover halos, carets/arrows, popover panels,
    status/notification badges, dropdown overlays — must be absolutely positioned (auto-layout
    parent → `layoutPositioning='ABSOLUTE'`; plain frame → out-of-flow x/y) at the spot it should
    logically live, with the right **constraints/pinnings**. The **host frame is sized to its
    *logical* element** and sets `clipsContent=false` so the float **overflows without inflating the
    host's bounding box / layout footprint**. Holds **even when the float is BOOLEAN-toggled** — a
    hidden in-flow float still reserves space; a shown one distorts the box. *(Concrete miss: a
    value-label tooltip added in-flow to a `_Slider/Thumb` made the component 28×44 instead of the
    16px handle, shifting the thumb on the track; fix = component sized to the 16×16 handle, with
    bubble + focus-ring + hover-halo absolute & overflowing under CENTER/MIN.)* **MANDATE (every
    absolute element): explicitly set `constraints` to match the layout context + intent — NEVER
    leave the default `{MIN,MIN}` / inherited.** Canonical mappings (C8 cell indicators): corner
    indicator → pin RIGHT+TOP `{horizontal:'MAX',vertical:'MIN'}`; left validation accent →
    `{horizontal:'MIN',vertical:'STRETCH'}` (hugs leading edge, grows with height); trailing inline
    icon (ƒx) → `{horizontal:'MAX',vertical:'CENTER'}`. A wrong/absent constraint silently drifts
    the element on resize — a corner badge left at `{MIN,MIN}` slides to mid-cell when the column
    widens.

15. **FILL absorbs surplus, never deficit — every FILL region carries an explicit `minWidth` equal
    to its content minimum (STANDING RULE, Sean 2026-07-06: "avoid such overlap at all costs").**
    A `layoutSizingHorizontal=FILL` child (spacer, flexible label region, space-between half) shrinks
    toward zero when its parent's fixed width leaves less room than the child's content needs; with
    `clipsContent=false` the content then silently overflows and **overlaps the adjacent sibling**
    (with clip ON it silently truncates — Rule 7a/7b). Auto-layout prevents sibling overlap only
    while every child's minimum is respected. Three obligations: (a) **authoring** — when building a
    component, set `minWidth` on every FILL region to its content minimum (for text anchors like a
    selection count, size to the max realistic string, e.g. "9,999 Selected"; anchors never
    truncate); (b) **consuming** — a FIXED resize of an instance must never go below
    Σ(children minimums + paddings + gaps); if the target width is smaller, **fold the content
    first, then shrink the frame** — the frame follows the content, never compresses it; (c)
    **detecting** — `minWidth` is NOT overridable on instance children, so a consumer cannot patch
    a library gap locally: sweep for it (`layoutGrow>0 || FILL` where content bbox > frame bbox →
    flag) and file the fix against the library component. *(Concrete miss: the CDS FloatingToolbar
    Figma component authors its `context` count region as bare FILL with no minWidth; fixed-width
    instances on the C8-99959 collapse board compressed it to 1–42px against 81px of text, sliding
    "12 Selected" under the controls frame — caught by Sean, fed into CDS-1247 as a component ask.)*

16. **In-flow boolean-toggled utility rows (icon clusters, trailing indicators) — HUG both axes,
    plus a row-level boolean.** When a component carries a cluster of boolean-toggled elements that
    must RESERVE SPACE dynamically (e.g. header sort/filter icons that shrink the label when shown),
    build it as an **in-flow auto-layout row** at the end of the content flow — NOT absolute — so a
    FILL sibling absorbs the space when icons appear (and End-aligned content abuts the icons instead
    of being overlapped). Three obligations: (a) the row is **HUG × HUG** so all-hidden children
    collapse it to zero — an in-flow row left at FIXED width renders a ghost gap when its children
    are off (⚠ gotcha: converting an ABSOLUTE frame to in-flow via `layoutPositioning='AUTO'`
    RETAINS its FIXED sizing — re-assert HUG after the conversion); (b) expose a **row-level boolean**
    (e.g. `Indicators`) bound to the row's own visibility, **DEFAULT OFF** — STANDING RULE (Sean,
    2026-07-07): *any frame whose children are all visibility-off must itself carry a boolean
    property, set off by default* — a hidden wrapper can never ghost, and one honest kill-switch
    beats N implicit ones. Consequence: demos/stickers that flip an inner boolean (e.g. `Sorted`)
    must also flip the wrapper boolean on. Exemption: load-bearing placeholder regions whose
    footprint IS the content (refmap image empty-state drop target renders its glyph and defines
    the hit area — evaluated and exempt); (c) after ANY `layoutMode` conversion on the component
    root, **re-assert every absolute overlay's geometry** (size to the variant + constraints
    STRETCH/STRETCH) — conversions silently distort absolute children (the header v2 `active-tint`
    rendered 3× cell height until re-asserted). Header-label typography note: header labels wrap to
    **max 3 lines** then ellipsis (`textTruncation='ENDING'`, `maxLines=3`) — longer attribute
    names shorten at the schema level. Validated on `cell/header (v2)`; all-cells audit 2026-07-07
    found no other violations (own-tree and instance-wrapper passes).

17. **Variables & modes — the mechanics that decide mode vs boolean vs physical (empirically
    verified 2026-07-07/09, C8 Tables).** (a) Per-instance mode flips re-resolve ONLY **color/paint
    bindings and visibility booleans** — both cross nested library-instance boundaries. STRING
    `fontStyle` bindings NEVER re-resolve inside instances (dead channel); enum props (text-align,
    auto-layout alignment) can't bind at all → structure/style/alignment = physical variants.
    (b) **Stamp the semantic default mode on every VARIANT ROOT** — never ship Auto: an unset
    instance resolves through its PLACEMENT chain to the collection's first mode (not the main's
    context); variant-root explicits mirror onto non-overridden instances, fresh and retroactively;
    set-frame explicits do NOT propagate. (c) **Paint-level `opacity` is IGNORED on variable-bound
    fills at render** — never build tints as bound-color-at-alpha; design real pale surface values/
    tokens. (d) **Test the override before filing a library ask**: nested text accepts
    `textAutoResize`/`layoutSizing FILL`/`textTruncation` overrides, and nested frames accept
    alignment-enum overrides — two assumed-locked walls broke under direct probes. (e) Verification
    bar for any mode/state surface: machine-vision permutation testing on rendered pixels (a
    checksum diff proved "working" what designers correctly saw as dead — the severity mode rendered
    0 px without its gating boolean).

18. **Field adornment optical edge inset (STANDING RULE, 2026-08-06).** Text/placeholder
    content keeps Density **`padding-x/input`**. Trailing **Icon Button** adornments (Combobox /
    Input clear) must **not** sit inside another full `padding-x/input` — ghost buttons read as
    their glyph, so the control chrome goes to the field edge and the glyph lands ~`iconOnlyPaddingX`
    in. Validated Input construction:
    - Root: `paddingLeft = padding-x/input`, `paddingRight = space/0`, `itemSpacing = space/2`,
      height → `control-height/md` FIXED. Clear Size → **sm** (32 / icon 16).
    - `[trailing-cluster]`: `[end-pad]` (width `space/1-5` = 6) + Clear, **−10** itemSpacing.
      Text-only right inset = gap 8 + end-pad 6 = **14** (`padding-x/input`). Trailing on: Clear
      flush to the field edge (glyph ~10px in). Negative spacing = sanctioned optical overlap
      (Rule 13 exception).
    - Leading bare icons stay at content inset (`padding-x/input`). Select chevron (no Icon Button
      chrome): `paddingLeft = padding-x/input`, `paddingRight = gap/xs`. Textarea: symmetric
      `padding-x/input`.

19. **Icon-only → Icon Button; icon size tracks control Size (STANDING RULE, 2026-08-06).**
    Any icon-only interactive control uses the library **`Icon Button`** (`350:2877`, wraps real
    `Button` + `Button / Layout = icon-only`), never a textless `Button` or a bare glyph with a
    hit target hacked via padding. Preserve Variant / Size / State when swapping. Icon glyph size
    comes from **`Button / Size`.`iconSize`** (xs=12 / sm=16 / default=20 / lg=20) — pick the Size
    mode so the glyph fills the optical weight of the surface (field clear / toast dismiss →
    **sm** in a `control-height/md` field; dialog/sheet close → **default**). Tiny 12px glyphs in
    ≥28px targets are a smell. Intentional bare exceptions: expanders/chevrons inside Select
    triggers, menu/command leading icons, status glyphs, decorative marks, pagination page
    **labeled** Buttons, ellipsis gap markers.

## C. Code→Figma transliteration judgment calls

1. **Focus states must use a focus token.** Use the `ring` (focus) color for the focus indicator
   — apply the system's standard focus treatment (border→`ring` + 3px `ring`/50 overlay) to every
   focusable control. Do this **even when the source Tailwind collapses to `focus:border-foreground`**
   (Input/Textarea did) — a foreground-darkened border is not a consistent or accessible focus
   indicator. *Why:* usability + accessibility consistency; focus must read as focus everywhere.
   This is the **one sanctioned deviation** from code-faithful transliteration.

2. **Otherwise favor code-faithful values over unifying.** When a value differs per component
   (Dialog close inset 8px vs Sheet 12px), keep the code's per-component value rather than unifying
   to one number. Deviate from code only for a clear a11y/consistency win (like #1), and log it.
   Always **visually assess and confirm** the rendered result matches the rule — measure the
   icon/control edges, screenshot. Verify by sight, not just by code.

---

**Why these are durable:** consistency across the whole library (not just dialogs); the Figma must
transliterate coded intent faithfully (token-driven spacing, correct icons, components that don't
distort their parents); these were repeated manual-build mistakes worth preventing.

**How to apply when building/auditing any surface:** (a) instance real components, props-first;
(b) set content slots to 0 L/R padding + bleed separators; (c) bind every gap/pad/radius to a token
(incl. zeros); (d) make in-parent popovers absolute + boolean-var visibility; (e) verify icon↔label;
(f) check double padding + correct slot fill/hug; (g) delete empty spacer frames; (h) give oriented
overlays position variants with boundary-flush carets; (i) make EVERY floating element absolute at
its logical spot with explicit constraints + `clipsContent=false`; (j) upgrade focus to the `ring`
token; (k) keep other values code-faithful and verify by sight; (l) field trailing Icon Buttons use
`gap/xs` edge inset (Rule 18), not `padding-x/input`; (m) icon-only actions → `Icon Button` with
Size-matched `iconSize` (Rule 19).

Related: [[radix-derived-color-system]] · [[figma-plugin-patterns]] · [[figma-cli-authoring]] ·
framework #05 §3a (full-result high-res review) · component & pattern framework #09.
