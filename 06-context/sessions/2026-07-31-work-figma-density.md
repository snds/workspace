### 2026-07-31 — Figma DS library: semantic density modes + collection cleanup

SessionID: 2026-07-31-work-figma-density
--- SESSION BLOCK ---
Date: 2026-07-31
Agent: Opus 4.8
Surface: Cursor
Machine: Work MacBook Pro (main, CS-K746DRWXY1)
Project(s): Centric SaaS PLM — Figma Design System library (file `o6o1ZuGHxDow2vHLuYXT6X`)
Summary: Refactored the near-publish Figma variable library in four moves. (1) Built a
  `Foundations / Semantics / Density` collection — modes Normal(default)/Compact/Spacious,
  23 tokens (control-height, padding-x/y, gap, control-radius, container/*) each aliasing the
  existing Spacing/Radii scale so **Normal == the current design pixel-for-pixel**. (2) Applied
  density across every page by rebinding structural props to density tokens (heights + radii via
  the Button/Select Size collections and blanket 8/12px radius; vertical padding + gaps + container
  insets 16/24 across Components, Base UI Additions, Features, Layout) — ~1,500 rebinds, all on
  non-instance nodes so instances inherit cleanly. An initial explicit-Normal stamp was later
  **reverted**: Density and Colors now remain Auto on components/subcomponents and inherit from
  app/chrome or audit shells; collection defaults remain Normal/Light. (3) Deleted the redundant
  `Typography Roles` collection — it was a pure 1:1 alias layer; rebound all 21 text styles' 126
  fields straight to `Foundations / Semantics / Typography`, no stray refs. (4) Normalized all 14
  component collection names to spaced `Component / Axis` (` — ` → ` / `, `Sizes` → `Size`).
  Verified: 0 em-dash collections, Roles gone, density resolves at all 3 modes, side-by-side
  screenshot of Button/Badge/Select/Input/Checkbox/Card confirms Compact/Normal/Spacious cascade.
Artifacts:
  - Figma file `o6o1ZuGHxDow2vHLuYXT6X` (Centric SaaS PLM - Design System) — variables/styles mutated in place
  - Knowledge updated: `08-knowledge/design/centric-plm-design-system.md` (density-via-modes + collapse patterns)
Decisions:
  - Density lives in the **semantic layer** as a mode-set collection, not per-component — components
    consume density tokens; the two axes (component Size × Density mode) compose independently.
  - Normal is the pinned default and is value-identical to the pre-refactor library (zero visual drift).
  - Horizontal *control* padding (8/10/12) stays fixed; only *container* insets (16/24) breathe on X.
  - An alias-only intermediate collection (Roles) is waste — bind styles/consumers to semantics directly.
  - Density/Colors are context axes: component roots and nested instances stay Auto; only app/chrome,
    page, feature, or audit shells set explicit modes. Collection defaults are Normal/Light.
Pending resolved:
  - Slash-group semantic scale names (Typography 29 + Spacing 36 + Radii 10 + Border Widths 6)
  - Semantic color category folders (`surface/` `action/` `status/` `chrome/` `sidebar/`) — 54 tokens
  - Cataloged + deleted 42 `cds/*` bridge tokens (zero Figma consumers); map at
    `08-knowledge/design/cds-to-radix-color-map.md` for centric-ui migration
  - `Calendar Day / Position` → `Calendar / Radii` with `Day/{corner}` vars + Title-Case modes;
    rebound `_Calendar/Day` corners (was dead wiring onto density-only radii)
  - Instance-vs-context method documented (`figma-component-token-axes`); density `control-font-size/*`;
    Button/Avatar Size `fontSize` wired through Size×Density; `Sidebar / Surface` pilot binds
    chrome fill/stroke + Menu Button focus ring (primary retained as capacity)
Pending added:
  - (Optional) Make Switch/Avatar/Badge Size collections density-aware for non-type dims (height already on Button).
  - centric-ui: retire CDS color usages using [[cds-to-radix-color-map]] → intent tokens (employer work).
  - Apply instance-vs-context recipe to remaining shells (Card/Popover → surface/* foregrounds).
  - Build Audit / Density Figma pages seeded from saas-plm-prototype (plan Part C).
Pending resolved:
  - Decisions: Figma Density Normal stays **32**; `line-height/relaxed` → **28**; baseline wrappers deferred
  - Full density type ladder (`type-size|leading|paragraph/*`); all 21 styles rebound; Button/Avatar Size×Density type wired
  - Cleared 2,387 direct explicit Density pins (plus inherited nested pins that disappeared with their
    masters) across Icons, Components, Additions, Features, and Layout; verified zero Density/Color
    context overrides remain. Auto inheritance test: Button resolved 28/12 Compact, 32/14 Normal,
    36/16 Spacious and inherited Dark/Light from its parent shell.
Pending resolved:
  - Vertical-rhythm audit + repair. Seed: `Example density` section `313:2782` (three Sidebar shells with
    explicit Compact/Normal/Spacious). Confirmed failure mode: horizontal AL + counter-axis CENTER +
    pad-Y bound to `space/0` + FIXED height with **no** Density-backed height → row frozen across modes.
    Centering alone carries no vertical rhythm. Audit + fixes: `08-knowledge/design/density-vertical-rhythm-audit.md`.
  - Repair recipe (repeatable): **HUG vertical + `padding-y/*` + `minHeight` → `control-height/*`**.
    Plain HUG+padding drifts off the control ladder at Spacious because the type ladder grows
    line-height 16/20/24 while `control-height/*` grows 28/32/36 (Menu Button hit 40 vs Select 36).
  - Fixed 9 masters (Compact/Normal/Spacious verified by temp three-mode test board, then deleted):
    `_Sidebar/Menu Button` 28/32/36 · Layout `Header` 40/48/56 · `_Table/Cell` + `_Table/Head` 32/40/48 ·
    `_Tabs/Trigger` 24/28/36 · `_Pagination/Item` 32/36/40 · `_Calendar/Day` 28/32/36 ·
    `_Dialog/Close` + `_Sheet/Close` 24/28/32. Button/Select already correct (28/32/36) — left as reference.
  - Only Normal-value drift: `_Tabs/Trigger` 26 → 28 (26 was off-ladder; 28 = `control-height/sm`).
Pending resolved:
  - Density `icon-size/*` ladder (xs/sm/md/lg → 12/16/20/24 Normal). Wired 4,244 icon masters'
    fontSize → `icon-size/md`; Button Size.iconSize → ladder; Menu Item → sm. Glyph **and box** now
    measure 16/20/24 (md) and 12/16/20 (sm) across Compact/Normal/Spacious.
  - Root blocker was **not** a Figma component-set limitation (earlier read was wrong): icon masters
    carried `min/maxWidth` + `min/maxHeight` pinned to 20, freezing the frame. Recipe per Sean:
    clear bound width/height, clear all four min/max, glyph TEXT → HUG/HUG, frame → HUG/HUG, and let
    `fontSize` → `icon-size/*` drive. Never re-bind frame width/height. Same unpin applied to 64
    consumer icon instances.
  - Gotcha: `Material Symbols Outlined` is missing in this agent environment (`hasMissingFont`), so
    plugin-side `node.width` reports stale 20×20. Verify icon sizing via server-rendered screenshot.
  - Button Size sm icon Normal 14→16; default binding corrected 16→20 to match prior render.
Icon consumer audit (434 instances across Components / Additions / Features / Layout):
  - Density-aware: 180 `icon-size/md` + 63 Button `iconSize` + 20 sm + 2 xs. **20×20 confirmed default**
    (all 4,244 masters bind `fontSize` → `icon-size/md`).
  - **171 density-blind literals** (14/16/18) from manual instance resizes. Figma stores a manual icon
    resize as a **0.8 scale override**, not a fontSize override — so it now *multiplies* the token:
    Sean's `more_vert` reads 12.8 / 16 / 19.2 (C/N/S) instead of 16 / 20 / 24.
  - **Hard blocker (corrected):** first read blamed the missing font — wrong. Control test: same
    `setBoundVariable('fontSize', …)` was dropped on `_Select/Item`'s **Inter** label (font loads fine,
    0 instances above). So **instance children reject fontSize variable binds, period**; paint writes
    on the same nodes succeed. Reinstalling Material Symbols does not unblock it — the bind must live
    on the main component. 145 of 156 rebinds were dropped this way, silently, no throw.
  - Font status: `Material Symbols Outlined` still not enumerated by Figma after Sean's Font Book
    reinstall (Rounded + Sharp are). Figma caches fonts at launch → needs an app restart. Only affects
    *measurement* trust, not the write path.
  - **Working fix path** (verified on `26:2177`): capture glyph fill + bound colour var →
    `instance.resetOverrides()` (clears the scale override) → re-apply via `setBoundVariableForPaint`.
    Step 2 silently reverts colour (`surface/muted/foreground` → `surface/foreground`); repaired.
    Blocks a blind sweep: reset returns every icon to the master's 20, which is wrong for the
    deliberately-small ones — those need a **Size variant on the icon component**.
  - Slot content is structurally locked: `insertChild` → negative index, `remove()` → "not allowed",
    `resetOverrides()` does not clear the inherited scale. Reach via **raw id** (`17:692`), not `I…;…`.
    Attempted Button swap for `UserIdentity` more_vert; it carried the 0.8 scale (72.8×25.6) — reverted clean.
  - Bare-icon vs icon-button classification recorded in the audit doc (~40 should become icon buttons;
    selects/tree chevrons/status glyphs/menu leading icons correctly stay bare).
Pending added:
  - **Needs Sean:** confirm Layout shell icon restore map (Business Objects→`business`, Team→`group`,
    Schema Registry→`schema`, …) — originals were not recoverable after the wipe.
  - Promote `UserIdentity` → `_Sidebar/User` (5 inline slot copies still).
  - Convert remaining interactive bare icons to Button + `Layout=icon-only` (Toast close, table row
    actions, widget overflow, etc.) — UserIdentity more_vert ×5 already done.
  - P2 sweep: Card / Dialog / Sheet / Empty State / Dropdown / Command / Menubar content slots still bind
    pad-Y to `space/*` instead of `padding-y/*` or `container/*` — inset is non-zero but density-blind.
  - Republish library after this structural round (adds to `^pc-18`).
Resolved this turn (fork):
  - **Regression:** blind `resetOverrides` wiped nested icon swaps → Layout Menu Buttons → `home`.
    Root cause confirmed: nested swaps without INSTANCE_SWAP are override-only.
  - Restored 40 Layout Menu Buttons via new `Icon` INSTANCE_SWAP (map above — Sean confirm).
  - Added INSTANCE_SWAP (+ exposed) on Menu Button, Button leading/trailing, Input, Select, Dialog/Sheet
    Close, Collapsible Trigger, Menu Item, Toast, Alert, Accordion Item, NavMenu Trigger.
  - `Icon / Size` live (default/xs/sm/lg/control); masters on `size`; Button icons → `control`.
  - `Button / Layout` (default / icon-only) + `iconOnlyPaddingX`; Button pad-X rebound to Layout.
  - UserIdentity more_vert → icon-only Button `More actions` (ghost/sm/icon-only/more_vert) ×5.
Icon Button + Menu Button round (Sean's direction):
  - Built **`Icon Button`** (`350:2877`) that *nests a real Button instance* rather than reimplementing it.
    1:1 by construction: inner Button FIXED width bound to `Button / Size`.`height` — the same token as
    height. `Button / Layout = icon-only` for padding; Variant/Size modes **cleared** so consumers drive
    them; `isExposedInstance = true` bubbles up `Leading icon instance` + `State` (icon exposed 2 levels).
    Verified square xs/sm/default/lg × Compact/Normal/Spacious (20 → 40).
  - UserIdentity ×5 swapped onto Icon Button (ghost/sm) — 24/28/32, the 0.8 scale drift finally gone.
  - **Menu Button colour bug (Sean spotted):** nav icon glyphs had drifted to `sidebar/foreground`
    (static) or a bare `foreground`, while labels used state-aware `Sidebar / Menu Button`.`foreground`
    → Selected went blue on text but stayed dark on the icon. Rebound 45 glyphs.
    Rule: a nested icon binds the *same* state variable as its sibling label.
  - **Icon semantics follow the label:** Dashboard → `dashboard` (`home` is only the master placeholder).
    10 swaps corrected. Cleared 4 stale `characters:"Search"` overrides on Documents rows — safe now that
    identity lives in the INSTANCE_SWAP prop rather than an override.
  - **Render caveat:** file data verified correct (masters *and* instances read `description` /
    `more_vert`, right codepoints, right mains) but server screenshots still show the old search / add
    glyphs. Missing `Material Symbols Outlined` means the app can't re-lay-out that text, so the
    rasterisation is stale. Swaps to *untouched* masters do render (dashboard appeared immediately).
    Figma still doesn't enumerate the font after the Font Book reinstall → **needs a Figma restart**.
Render lag resolved (Sean, after restart): Figma's renderer sometimes won't repaint a component
  until a user clicks *inside* it. He verified this — file data was correct all along, as the
  inspection said. One Compact menu item needed an instance reset + redo of overrides; rest updated.
  Standing lesson: when file data and a server screenshot disagree, trust the data and ask for a
  click/restart before re-editing. Do NOT "fix" a phantom.
Button ghost status + inverse (Sean's ask):
  - 6 new `Button / Variant` modes → 17 total: `ghost-{info,success,warning,caution,danger}` +
    `ghost-inverse`. Background + border transparent; only text/icon carry the status colour.
    `ghost-inverse` uses `action/primary/foreground` so a ghost on a filled surface reads light.
  - **Contrast catch:** first pass aliased the solid `status/*` hues (matching the existing
    `destructive` mode). Measured against `surface/background` — *all five* fail AA in Light, and
    `status/caution` (#ffe629) is 1.26:1, i.e. invisible. Rebound foregrounds to
    `status/*/soft/foreground` (4.51–5.21 Light, 8.95–14.14 Dark). Rings keep the solid hue —
    non-text UI component, 3:1 bar, saturated reads better. Verified by screenshot.
  - Existing `destructive` mode still carries the solid fg at 3.91 — flagged, untouched.
  - ~~Gap found: Hover pixel-identical to Default on every variant~~ **WRONG — my error.** The probe
    read only `fills` + a `/overlay|hover/i` name regex; the real node is `[state-layer]`, so it was
    missed. Hover always worked (foreground-tinted layer @0.12/0.24/0.32 node opacity).
    Lesson: a name-regex probe is not an inspection — enumerate children, read every paint.
Interaction semantics generalised (Sean's direction — overlays, not per-variant bg tokens):
  - 18 `interaction/*` tokens in Foundations/Semantics/Colors aliasing Radix **A4=hover / A5=pressed**
    per hue + Black/White overlay for solid/inverse. Hues: primary→Blue, info→Cyan, success→Green,
    warning→Orange, caution→Yellow, danger→Red, neutral→Zinc.
  - `Button / Variant` +`overlay/hover`/`overlay/pressed`, resolved per mode to the right family
    (solid | neutral | hue-keyed | inverse). Existing `[state-layer]` rebound to them at opacity 1,
    so alpha now lives in the token, not the node. Icon Button inherits (nests a real Button).
  - Alpha-in-token vs alpha-as-paint-opacity: authoring rule 17c only kills *paint* opacity on bound
    fills. Radix A-steps carry alpha in the colour value → they render. Proved it: bound fill,
    literal composite, and literal rgba all rasterised identically to `#e8e8ec`.
  - Verified pixel-exact by sampling the server PNG at node bounds (ghost 232,232,236 · default
    8,106,201 · ghost-info 202,241,246 · ghost-inverse 34,132,227) — all within 1/255 of prediction.
  - Unified 3 competing mechanisms → one: state-layer nodes (Button, Tabs), mode-driven `background`
    vars (Select Item, Table Row, Sidebar Menu Button), and direct opaque fills (Calendar Day,
    Pagination Item, Menubar/NavMenu Trigger, Toggle, Menu Item row).
  - Value shifts worth knowing: Table Row hover was Zinc **A2** (α0.02, below perceptual floor) → A4;
    Sidebar Menu Button hover was `sidebar/accent` → neutral alpha; Menu Item destructive highlight
    → `interaction/danger/hover`.
  - Left alone deliberately: Resizable Handle + Slider Thumb (hover changes the control, not a
    surface behind it) and all Selected/Active states (persistent state ≠ interaction feedback).
  - `surface/inverted/foreground` idea DROPPED — I'd oversold it. A fixed-polarity token can't work
    on *any* background; `ghost-inverse` stays an explicit consumer choice. Real options if ever
    needed: per-solid `on-*` pairings, or APCA-resolved contrast at runtime.
  - Docs: new [[interaction-state-semantics]] (architecture + centric-ui reconciliation plan).
Link + ghost/primary (Sean):
  - Link already had the state-layer; it was on *neutral* Zinc. Rebound `overlay/hover|pressed` for
    `link` → `interaction/primary/*` so brand links get a blue wash, not gray.
  - New `ghost/primary`: rest = `surface/foreground`; hover/pressed fg → `action/primary`; overlay →
    `interaction/primary/*`. Channel: `foreground/hover` + `foreground/pressed` on Button/Variant
    (seeded = default for every other mode; only ghost/primary elevates). Hover/Open/Pressed rebound
    label+icon to those tokens.
  - Verified: ghost/primary Default fg (41,45,49) → Hover (21,126,226); wash (213,239,255) matches
    link hover. ghost/secondary stays neutral wash (232,232,236).
  - Naming (Sean): slash-grouped all ghosts — `ghost` → `ghost/secondary`, `ghost-primary` →
    `ghost/primary`, and `ghost-{info,success,warning,caution,danger,inverse}` → `ghost/*`. Mode IDs
    stable; UserIdentity Icon Buttons still resolve on `ghost/secondary` (id `7:3`).
Brand as default hover/active voice (Sean):
  - Most chrome hovers → brand Blue A4 bg + `action/primary` fg. Selected → Blue A5 opacity (not
    solid Blue/5) + full brand fg. New tokens: `interaction/selected`, `interaction/selected/foreground`.
  - Rebound `sidebar/selected`, `chrome/selected` (+ fg) and `sidebar/accent` (+ fg) to those.
  - Sidebar Menu Button Selected resolves Blue A5 @α0.24 / fg `#0976e0` (was opaque `#cbe2ff` / Blue11).
  - Shifted to primary hover: Sidebar, Select Highlighted, Table Row, Tabs state-layers, Calendar Day,
    Pagination, Menubar/NavMenu Trigger, Toggle Off-Hover, Menu Item Default highlight.
  - Stay zinc: Button ghost/secondary·outline·secondary; **table cell** hover.
Table cascade exception (Sean — important):
  - Stack bottom→top: data fill → row primary overlay → column primary overlay → cell zinc overlay.
  - Why zinc on cell: primary-on-primary adds no info; neutral reads as "this cell." Alpha means
    coloured cells tint rather than get covered — the reason selected must stay opacity, not solid.
  - Scaffolded `Table / Cell` collection (Default transparent / Hover → `interaction/hover`); bound
    cell master. Column hover + coloured-cell fixture still open.
Avatar — regression I caused, plus a real gap (Sean: "circle gets very small, text breaches"):
  - ROOT CAUSE was mine, not a token gap. The earlier icon-unpinning sweep matched on
    "small + square + has a TEXT child" — `Avatar` (32x32, fallback initials "AB") fit that shape
    exactly, so 11 instances got flipped to HUG/HUG with their `width`/`height` binds cleared. The
    circle collapsed onto the glyph bbox: 19x20 Normal, 17x16 Compact, 22x24 Spacious — not even
    square, which is why initials touched the edge.
  - LESSON: never shape-match a structural sweep. "Square + small + text child" describes icons AND
    avatars AND badges AND count chips. Gate on master identity (component-set name / key), not
    geometry. Also: `resetOverrides()` and geometry sweeps are the two blast-radius tools here.
  - Fixed all 11 → FIXED/FIXED rebound to `Avatar / Size`.`size`. Verified 32x32 in all three density
    sidebars, initials centred. Masters already had primary+counter axis CENTER; untouched.
  - API notes: `set_minWidth` throws "cannot be overridden in an instance" — skip min/max on
    instances. Cross-page collect-then-write goes stale ("Node not found") on deep nested IDs, but
    the writes had actually landed; re-measure before assuming failure.
  - THE ACTUAL GAP (Sean picked both #1s — dedicated `avatar-size/*` + library-wide):
    Created `avatar-size/{sm,md,lg}` on Density (scopes WIDTH_HEIGHT), aliasing space/*:
    sm 24/20/28, md 32/28/36, lg **40/36/44** (preserves Normal 40; ±4 step; not control-height/lg).
    Rebound `Avatar / Size`.`size` sm→avatar-size/sm, md→…/md, lg→…/lg. Features 40×40 outlier →
    mode `lg` + bound. Live sidebars: Compact **28**, Normal **32**, Spacious **36**; glyph/circle
    ratio stable ~0.43–0.44 (was 0.375→0.50). Hover Card 48px = intentional `scaleFactor: 1.5`, leave.
    Write path this turn: figma-cli CDP (official `plugin-figma-figma` MCP not connected in Cursor).
Nested icon-only Button → Icon Button (Sean):
  - Census: 17 master-nested icon-only Buttons (Label=false) across Schema Action Buttons,
    Graph/Canvas/View toolbars, Header (+ theme-switcher xs×3). App Shell was instance-nested —
    inherits Header. UserIdentity already Icon Button.
  - Swapped all 17 → `Icon Button` (`350:2877`); preserved `ghost/secondary` + Size sm/xs + leading
    icon (all still placeholder `add` in these feature stubs).
  - Fixed Icon Button 1:1: inner Button width now binds to `Button / Size`.`height` (was hug; square
    only at md by luck). Cleared stale shell height/radius binds from swap. Result: sm 28², xs 24²,
    md 32²; density sidebars UserIdentity 28/32/36.
  - Re-census: **0** remaining nested icon-only Buttons on component masters.
Bare action icons → Icon Button (Sean):
  - ~47 master swaps: Input clear, Alert/Toast dismiss, Widget chrome (more/add/pin/close),
    Schema Palette add, Member/Relationship delete (`ghost/danger`), Documents Table
    download/delete + page chevrons, Inline Edit edit/confirm/cancel, Calendar month nav.
  - Gotchas: sibling variants can land as Icon Button with default `add` icon after first swap —
    re-set Leading to `close`. `scaleFactor` 0.8 on feature frames carries through swap — reset to 1
    or sizes read 0.8×. Outer HUG can stick at stale px after scale reset — resize to inner then HUG.
  - Skipped: Dialog/Sheet Close (already 28² wrappers), Pagination text+chevron pairs, disclosures,
    menu leadings, status glyphs, tiny decorative `open_in_new`.
Pagination → real Buttons + shared tokens (Sean):
  - Sean: Dialog close handled via parent subcomponent (leave alone). Pagination Prev/Next should be
    regular Buttons; Item should too, same token needs.
  - New `Pagination / Control` (single Value mode): background/default|active, foreground/*,
    border/default, overlay/hover|pressed → `interaction/primary/*`, radius → control-radius/sm,
    height → control-height/lg.
  - New Button / Variant mode **`pagination`**: outline-like rest (transparent bg + chrome border)
    but overlays alias Pagination / Control (primary hover/press — matches page-item chrome).
  - `_Pagination/Item` rebuilt: each State nests a real Button (square width=height @ lg).
    Default/Hover/Disabled → Variant=pagination; Active → Variant=default (solid primary).
  - Prev/Next frames → Button instances (pagination/lg, chevron leading/trailing, radius override
    to Pagination radius). Labels restored 1/2/3/8; item "1" Active.
INSTANCE_SWAP preferred lists cleared (Sean):
  - All 19 icon INSTANCE_SWAP props across 13 hosts (Button, Input, Select, Menu Button, Alert,
    Toast, Menu Item, etc.) — `preferredValues: []`. Re-census: 0 remaining. Swap UI no longer
    surfaces a Preferred shortlist.
Next:
  - Table column-hover surface + coloured-cell cascade proof
  - Optional: expose nested Button on `_Pagination/Item`; TEXT `Page` prop
  - centric-ui: `::after` state layer + interaction tokens; map former `ghost` → `ghost/secondary`;
    selected = primary A5 not solid. Employer repo → branch → PR → review.
  - Visual audit pages in Figma (prototype as capture seed only)
  - When Style Dictionary lands, map `/` → nested path; strip color category prefix for shadcn CSS
    (`action/primary` → `--primary`) or keep nested — decide at export time.
--- END SESSION BLOCK ---
