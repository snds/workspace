---
title: Chapter 4 — Building a Token System
course: Subatomic — The Complete Guide To Design Tokens (Brad Frost & Ian Frost)
sections: ["Chapter 4: Building a Token System"]
lessons: 89
status: noted
as-of: 2026-09-23
---

# Chapter 4 — Building a Token System

Original notes (not a transcript). Raw transcripts: `<Projects>/subatomic-design-tokens-course/transcripts/04-*`.
Demo repos (zips) and Figma/FigJam links: `<Projects>/subatomic-design-tokens-course/files/04-*`.

## The demo: "Frostd Tokens"

A fictional ice-cream company with three products that span the product-family axis: a **marketing
home page**, a **utilitarian checkout flow**, and an **enterprise dashboard**. Four themes flow through
the *same* component set: `vanilla` (unbranded internal base — never shipped), `strawberry`,
`chocolate`, `dark-chocolate` (dark mode of chocolate). Built in Figma (with Molly Hellmuth) and in
code (Style Dictionary + Sass + Storybook); code can do things Figma can't (swapping hero imagery,
`position: sticky`, true responsiveness).

Cross-disciplinary framing is deliberate: Brad plays designer, Ian plays developer, **each step is done
in Figma and code side by side** — designers should watch the code parts and vice versa.

## Five-step build

1. **Choose tools.** Figma Variables (native; Tokens Studio, Supernova, Knapsack, zeroheight etc. orbit
   it). Code: Style Dictionary (they used Salesforce Theo before; Diez exists). Check Figma plan limits
   on modes/collections before designing the architecture around them.
2. **Environment.** Figma edit access (Dev Mode hides the local-variables panel). Code: editor, Node/npm,
   `style-dictionary` (devDependency — build-time only), `sass` (dependency — ships), Storybook
   (devDependency), git + GitHub. Start from `style-dictionary init basic`, strip to one platform (CSS
   custom properties) and one token, prove the build.
3. **MVP architecture** — one colour through all three tiers in both environments.
4. **Build out a full theme** — colour, typography, spacing, border, shadow, animation, z-index.
5. **Duplicate the theme** into a second one (appended below).

## MVP in both environments (mirror structure exactly)

| Step | Figma | Code (Style Dictionary JSON) |
|---|---|---|
| Tier 1 | Collection **"Tier 1"**; `color/brand/pink` (slashes = groups) | `tier-1-definitions/` → `color.brand.pink` |
| Tier 2 | Collection **"Tier 2"**; `color/content/brand` aliases tier 1 | `tier-2-usage/` → `color.content.brand = {color.brand.pink}` |
| Tier 3 | Collection **"Tier 3"**; `button/color/content` aliases tier 2 (or 1) — here the top group separates *components* | `tier-3-components/button.json` |
| Namespace | — | `prefix: "ds"` in platform config |
| Tier identifier | — | custom **name transform**: add `theme-` when the token's source file is in tier-2/3 dirs, never to tier 1 (config moves to JS to allow custom transforms) |

Result: `--ds-color-brand-pink` (tier 1), `--ds-theme-color-content-brand`, `--ds-theme-button-color-content`.

**Collections = tiers** in Figma and **directories = tiers** in code: the tier is structural, not just a
naming convention, which makes the prefix transform (and any audit) mechanical.

Wiring: a heading binds to tier 2 directly; the button binds to its tier-3 tokens (fill, stroke, text).
In code, Dev Mode's generated CSS shows the variable names — which match except for the `ds-theme-` prefix.

### Scoping Figma variables (designer UX)

- Un-scope **all tier-1 variables** (untick every scope) so consumers never see raw ingredients in pickers.
- Scope tier-2 colour by property: `content` → text (+ shape where needed); `background` → frame/shape
  fills; `border` → strokes (+ effects). Now the fill picker only offers backgrounds, the stroke picker
  only borders — fewer mistakes, less sifting.
- **Do scoping once the categories settle**, typically right before publishing the library.

## Building a full theme

### Colour

- Tier 1 grows categories: brand (pink, cream…), utility (blue/green/yellow/red), neutral, transparent
  (backdrops), data-viz. Categories are optional affordances.
- Tier 2 roles are identified **through a pilot project**, not in the abstract: `default`,
  `default-hover`, `subtle`, `knockout`, `brand`, `brand-hover`, `disabled` × background/content/border.
- Tier 3 for buttons expands to variants × states (`default|hover|active|disabled` under
  primary/secondary/tertiary), plus form controls, links, focus rings. They admit this "should make you
  feel a little uneasy" — justified for heavily-variable, multi-theme components only.

### Typography — the hardest part of the course

- **Tier 1**: families, sizes (on the grid), weights, line-heights, letter-spacing, transforms.
- **Relative units.** Figma is pixel-only; browsers support absolute and relative units (%, em/rem, ch,
  ex, viewport and container units, `lh`). Pixel font sizes **ignore the user's browser font-size
  preference** — an accessibility failure. House rule: **relative units almost everywhere in CSS;
  `rem` for font size** (it converts cleanly from Figma px at a 16px root). Fluid type via `clamp()`
  is possible in code and impossible in Figma — a reason to kill the waterfall.
- **Line-height**: best practice on the web is **unitless** (`1.5`); Figma variables can't hold
  percentage line-heights, so teams store px or omit line-height in Figma. A known parity gap.
- **Tier 2**: `typography/{role}/{variant}` groups each holding the full property set: display,
  headline, title, label, body, meta — plus `…-mobile` siblings for large type.
- **Responsive typography** — the system absorbs the complexity so consumers get it free:
  - Model: two composite sets (`display-default` large, `display-default-mobile` small) that the
    consumer sees as **one** token.
  - **Figma**: a dedicated **viewport collection** (modes `large`/`medium`/`small`, each with a label and
    width) and a **design-only "viewport typography" collection** whose modes remap size/line-height/
    letter-spacing per viewport (modes can't be multiplied across collections — strawberry × large isn't
    expressible — hence the separate collection). Text styles bind to it; artboards get a variable
    mode. One-time setup per type style; then dragging text between artboards reflows automatically.
    One breakpoint is often enough.
  - **Code**: media queries; code usually has **more breakpoints than Figma has viewports** (they're
    different concepts). Mobile-first mixin in Sass: small values by default, larger inside the
    `min-width` query.
- **Bundle composites for consumers**: Sass mixins (`ds-theme-typography-display-default`), utility
  classes, or similar. **No component in the system should contain a stray `font-size`/`font-weight`** —
  all typography comes from composite bundles (prevents missed letter-spacing, typo'd names).

### Spacing

- Tier 1 `spacing/0,4,8,12,16…`. Components may use it directly.
- Ian's code alternative: a Sass `size(n)` function (8px × n, emitted in rem) for height/width/margin/
  padding — spacing tokens exported per value get unwieldy.
- Tier 2 only for jobs like `section-break`, which can itself be responsive (same viewport trick).

### Border

- Keep **border tokens separate from spacing** even when values overlap (you may want a 3px border
  width but never a 3px space). Tier 2: `border-radius-{none|sm|md|lg}`, `border-width-*`, often one
  default plus modifiers — maybe just one theme radius.

### Shadow

- Composite; tier 1 co-locates x/y/blur/spread/color per size (redundant but works). Tier 2 bundles
  them; Figma gets an **effect style** (`box-shadow-small`); code gets a custom Style Dictionary transform
  that **emits one `box-shadow` value** per composite so components set one property. (File renamed
  `box-shadow` at tier 2 to dodge Style Dictionary name collisions with tier 1.)

### Animation

- Code-only (Figma can store but not use them). Tier 1 durations + easings; the animated property is
  left to the component. Tier 2 named effects (`fade-quick`, `fade-long`, `move-quick`, `move-long`).
  Applied through `transition` on e.g. a button hover scale.

### z-index

- Code-only. A 100-step ramp (tooltips low, modals high) so developers stop inventing arbitrary
  numbers; used directly by components.

## For Sean

- "Tier = collection = directory" is the strongest mechanical hook in the course: an audit can derive
  tier from file location and never guess. `token-audit.py --config` supports `tier_prefixes` for this.
- The **no stray font-size/weight in component CSS** rule is directly lintable (extend TA015-style scan).
- Figma scoping is a checklist item for any Figma variables work: tier 1 unscoped, tier-2 colour
  scoped by property — verifiable through the Figma MCP (`get_variable_defs` exposes scopes).
- rem-for-type + unitless line-height is a code-side rule that conflicts with Figma's px model; record
  the conversion (px ÷ 16) as a pipeline transform, never a manual step.

## Documenting the theme

Before extending, **document the theme visually** in Figma: pages for tier-1 ramps (brand, neutral,
utility, transparent, data-viz), tier-2 roles grouped by background/content/border, tier-3 component
tokens, the type scale and tier-2 type roles (with the responsive large/small side-by-side), border
widths/radii, shadows, spacing grid, viewports. Then show it **wired to pilot screens** (home, checkout,
dashboard) in Figma and Storybook.

## Step 5 — adding a second theme (chocolate)

Two goals, both required: ship a real new design language **and validate the architecture** holds for
*any* further theme.

| | Figma | Code |
|---|---|---|
| Tier 1 per theme | Rename collection `Strawberry Tier 1`; add `Chocolate Tier 1`; paste, rename ramps (pink → brown), replace values | Duplicate the `strawberry/` directory as `chocolate/`; replace values |
| Tier 2 / Tier 3 | **Modes** (columns) in the shared Tier 2 and Tier 3 collections: `strawberry`, `chocolate` | Remap aliases in the theme's tier-2/tier-3 files |
| The work | **Remapping only** — the structure and semantics already exist | Same |

"Hard to build once, cheap to extend": new themes are a mapping exercise, not new architecture.

### Core tokens (shared across themes)

Cloning surfaces values that never change per theme (white is white). Put them in a **core** collection /
`core/` directory, delete them from each theme, move shared Sass (typography mixins) into core too.

Candidates (org-dependent — ask "truly universal or brand-specific?"):
- neutral palette (unless brands need their own greys) · utility/status colours (esp. contrast-tuned
  yellow) · transparent/backdrop colours · data-viz colours · a parent-brand colour shared by sub-brands
  (Nasdaq, Marriott) · tier-1 type scale · the 4/8pt spacing grid · animation · z-index.

**Create the core collection as soon as the second theme starts** — refactoring shared values out later
is the expensive path.

### Theme switching — "the magic trick"

- Figma: **Apply variable mode** on the page or on a wrapping frame — set both the Tier 2 and Tier 3
  collection modes, switch strawberry ↔ chocolate live.
- Code: Storybook themes add-on (toggle → dropdown beyond two themes).
- This demo is what makes the ROI visible to skeptics and leadership — use it deliberately.

### The vanilla theme (architecture x-ray)

- An **internal, unshipped** theme — usually plain and boring, sometimes deliberately garish — whose
  only job is to exercise the architecture and host system-level conversations away from any brand's
  politics.
- The second theme will expose weak points: incomplete sets, excess tokens, values that belong in core
  (or back out of it). That churn is expected.
- **By theme 2–4 the architecture should be stable** — no major surgery after the first couple. If it
  keeps changing, the architecture isn't done.
- Final demo: four modes (vanilla, strawberry, chocolate, dark-chocolate) in Figma and code; the
  mechanism scales to dozens of themes (they joke: don't do 2,000).

## Synchronization & automation (the most-asked question)

Framing first:
- Getting a token system off the ground behaves **more like a project than a product** — it stabilizes
  and changes far less than the component library or product work.
- **Tools don't fix people/process problems.** Teams on fire ask "which plugin?" when the fix is roles
  and process.

### Token czars

- **Two stewards: one owns the Figma library, one owns the code** (sometimes one person). Every
  request/change goes through them; requesters don't need to understand the system or open PRs.
- Justification: tokens are more niche, specialized, and stable than component work; many cooks =
  naming chaos. Keep collaboration tight, the group small.

### The sync spectrum

| Approach | Example | Pros | Cons |
|---|---|---|---|
| **Fully manual** | Designer edits Figma variables; dev mirrors in JSON by hand (the whole chapter) | Forces collaboration; close to the metal; no vendor lock-in | Disconnected, tedious, typos and mis-copied hex values |
| **Mostly manual** | *Design Tokens Manager* plugin exports JSON zip → a small build script reshapes it for Style Dictionary | Lightweight, free, low lock-in, kills copy-paste errors | Still a hand-off; syntax mismatch needs reshaping; room for error |
| **Mostly automated** | *Tokens Studio* (predates Figma Variables) pushing to a Git repo → PR | Feature-rich, configurable, repo-integrated | Black box without plugin access; "false collaboration" (design pushes, dev surprised); paid; format quirks (e.g. font weights exported as px → extra transforms); uneven application bugs in their experience |
| **Other** | Figma REST API (Enterprise) — Nate Baldwin's Adobe write-up; zeroheight, Supernova, Knapsack token managers | Pipeline-grade integration | Figma variables can't be written back from those tools (Figma stays the origin); plan/price gates |
| **Fully automated** | — | — | **Doesn't exist.** Static vector tool ≠ runtime; desire for it is often a desire not to talk to each other |

Landscape moves fast — re-evaluate tools at decision time. **Success = cross-disciplinary collaboration
and communication** ("if there's one thing you take from this course").

## Chapter homework

- Stand up the provided Figma + code assets as a boilerplate/reference — **not** production-ready.
- Your system is yours: modify or discard anything that doesn't fit.
- Designers: master variables, collections, modes. Developers: JSON, Style Dictionary, custom
  properties, Sass, Storybook. Evaluate sync tools (if any) against your org's needs. Collaborate.

## For Sean (sync + themes)

- Theme-API parity is now a gate: `token-audit.py --themes` fails when one theme lacks a tier-2/3 token
  the others expose — the mechanical version of "the second theme exposes weak points."
- A **vanilla theme** should exist in any multi-brand system Sean designs; it doubles as the fixture
  for audits and visual regression.
- The sync spectrum maps onto the existing Figma↔code pipeline doctrine: the workspace pipeline sits at
  "mostly automated" (variables → DTCG → Style Dictionary → PR). The course's warning — the tool can hide
  a missing conversation — is the reason the PR must be reviewed by the other discipline's czar.
- "Token czars" = named owners per side; route token change requests to them rather than open contribution.
