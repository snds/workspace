---
title: Chapter 6 — Adopting Design Tokens
course: Subatomic — The Complete Guide To Design Tokens (Brad Frost & Ian Frost)
sections: ["Chapter 6 - Adopting Design Tokens"]
lessons: 71
status: noted
as-of: 2026-09-23
---

# Chapter 6 — Adopting Design Tokens

Original notes (not a transcript). Raw transcripts: `<Projects>/subatomic-design-tokens-course/transcripts/06-*`.
Sources: 70 transcripts, plus the Wistia caption for lesson 242 (default colour in code), which has no
transcript. Lesson 278 is a download-only lesson (demo code) and has no video.

## Framing: token adoption is "design system adoption light"

- Adopting a component library means dealing with tech stacks, backend integration and legacy systems.
  Adopting tokens can mean shipping a list of variables. In the authors' experience, tokens are **more
  flexible and portable** than components, so they are easier to adopt.
- Adoption is not a yes/no question. It is a **spectrum** you can use deliberately, meeting each team
  where it is.

## The spectrum of integration

| Level | What the consumer does | Examples | Payoff / caveat |
|---|---|---|---|
| **1 — Reference** | Reads the token docs and copies values by hand into tools that can't import a package | Mailchimp brand kit (colours, type, buttons; no JSON import); CMS theme colours: WordPress, Drupal (colour-palette module), AEM, Contentful | Valid, and **"not a failure"**, as long as whoever manages the tool knows the system exists, checks the docs and hears about changes. Usually maintained by hand. |
| **2 — Consume the token library** | Subscribes to the Figma team library and installs the tokens package from npm | Covered in Ch5 | A real connection. Changes roll out and fewer things slip through the cracks. |
| **3 — Consume the component library** | Uses DS components that are already wired to tokens | Drop a Material button into a blank Figma file, or import an MUI `Button`: radius, colour and type arrive without extra work | Highest integration. Designers never touch the right sidebar, and code gets HTML/behaviour as well. |

- The spectrum is a **roadmap**: reference now, import tokens on the next pass, replace old components
  when the time is right. Share it with consuming teams explicitly.

## Who uses tokens

| User | Notes |
|---|---|
| **You (the DS team)** | Makers who are also consumers: you wire tokens into the core component library and help product teams. |
| **Other product teams** | Colleagues plus third parties such as agencies, consultants and offshore dev teams. Anyone building digital product for the org counts. Expertise and proximity vary widely, so **don't assume people will just get it**. |
| **Devs on many stacks** | Web frameworks, CMSs, SwiftUI, Jetpack Compose, Flutter, Ionic, Electron, React Native, native desktop, and odder things. |
| **Auxiliary users** | Marketers and content editors in a CMS or email tool (Weebly, WordPress). They usually see a **subset** of tokens with limited customisation and use them to build branded pages or campaigns. |
| **Stakeholders** | CMOs, brand managers, agencies. They don't use tokens directly but care about the result. |

**Nobody cares about design tokens.** People are busy with sprints, PI planning, rebrands and
re-platforming. The DS team's job is to explain what tokens do for them, then roll up its sleeves and
help them ship with tokens.

## Adopting at every layer of the ecosystem

Uses the layer cake from Ch1 (Brad's "The Design System Ecosystem" post). In the door metaphor, tokens
are the paint and the hardware finish (matte-black hinges), and components are the frame's structure
and function. Your org may lack some layers, and that's fine.

| Layer | What lives there | How tokens arrive | Owner |
|---|---|---|---|
| **Core DS** | Token library + universal components | Wired directly into components (most of this chapter) | DS team |
| **Technology-specific** | Platform flavours where core components can't travel | Style Dictionary platform builds | Platform implementers, working with the DS team |
| **Recipes** | Product-specific compositions (often tied to one theme) | Through core components, plus direct token use in bespoke parts | Product teams, with DS guidance |
| **Smart components** | Components wrapped in logic; skinned third-party libraries | Wrap tokenised components; map the library's styling hooks to tokens | Built in-house or brought in from vendors |
| **Product** | "Special snowflakes" (one-off bespoke UI) | Tokens used directly | Individual product designers and developers |

## Core layer: prerequisites

- **Figma:** the *component library file* is the product here. It subscribes to the tokens team library,
  which makes variables and styles available, lets you map to tier 2, and turns on theme switching. The
  authors say this core-library-subscribes-to-token-library setup is what they have seen work.
- **Code:** source lives in the tokens repo. `npm run build` produces a package containing only the files
  downstream teams need. Publish it to npm, then consumers `npm install` it at a specific version.
  **Check `package.json`** to confirm the right version landed, then import a theme (strawberry) and use
  a token (`background-brand`).
- The component library installs the **same** tokens package and publishes its own package with tokens
  already wired into its CSS. Product teams install both packages.

## Existing components: the "Indiana Jones swap"

Replace hard-coded values with tokens. Users should see **no difference**, but every theming capability
becomes available under the hood.

| Step (text field demo) | Figma | Code |
|---|---|---|
| Spacing / gap / padding | 8pt spacing variables | Spacing token or the Sass `size()` function (`size(1)` = 8px, `size(0.5)` = 4px; the file must be imported) |
| Label type | `label default` text style | Typography mixin (import the typography-usage SCSS); **delete** the loose font properties |
| Text colour | `content default` | `--ds-theme-color-content-default`. **Add the `ds-theme` prefix**, which Dev Mode omits |
| Input fill / border | Colour variables | **Tier-3 form tokens** (form background default, form border colour), radius small, border-width small (1px) |
| Input text / placeholder / helper | body default; `content subtle`; body small + content subtle | Same, via mixins |
| Radius | Bound even though nothing changes yet (it will change per theme) | Same |
| Motion | Not available in Figma | **Animation tokens** for hover transitions: code-only |

Workflow: turn on Dev Mode and work top-down from the outermost element.

### Best practices (existing components)

- **Don't bulk-paste Dev Mode output.** Pick token values one at a time and place them deliberately.
- **Follow each environment's conventions**: text styles in Figma, mixins in code. Watch breakpoints,
  z-index and spacing, which behave differently in the two environments.
- **Visual parity:** before and after should be nearly identical, and any change should be deliberate.
  Use visual-regression tooling (Chromatic or similar) to compare.
- **Show the magic trick** (below). The authors call this possibly the biggest piece of advice.

### Showing the magic trick

A swap that changes nothing visible looks to the stakeholders funding it like the team is standing
still. Put before and after side by side in a playground (the course sample lets you drag a component across
themed artboards). A **dark chocolate** theme makes it obvious that the old component couldn't do dark
mode or other type families. **Share early, share often.**

## New components

Two routes: build with hard-coded values and then do the swap, **or** apply tokens as you build (the
demo route, which gets faster once the language is second nature).

- **Figma (badge):** `label small` text, spacing tokens for padding and gap, `background knockout`
  paired with `content knockout` so the two move together, a radius token, then make it a component and
  switch themes. Add variants `success`, `error` and `warning` bound to utility tokens.
- **Code:** component classes use a `dsc-` prefix (`.dsc-badge`, `.dsc-badge--success`), and tokens
  use `ds-theme-`. The badge uses inline-flex with a gap (ready for future icons) and radius *large* for
  the pill shape. The success variant actually uses **utility success knockout** for a darker green.
  There is one Storybook story per variant, each with a modifier class.
- **Magic trick:** utility colours were kept **the same across themes** on purpose, so the shifts are
  small (radius and so on), but you still check every theme.

### Best practices (new components)

- Designers and developers **learn the token language by doing**; the authors call it "Duolingo for
  your token system language", and it takes a few components. That's why creators must sweat the naming:
  fluent users compose with tokens directly instead of making a second pass to systematise.
- Same caution about Dev Mode copy-paste, and the same attention to environment conventions.
- **Test theming while you build**, keeping other themes in view. Building for one theme with blinders on means
  things break once other themes are applied. Light theme-switching during construction cuts bugs and
  QA work.

## Applying the nomenclature: colour

The shared language has to mean the same thing to everyone ("background subtle default"). Your
vocabulary may differ from theirs, even radically, as long as it is shared. The Ch3 naming FigJam is
linked (`bit.ly/design-token-naming`).

| Intention / variant | Demo | Notes |
|---|---|---|
| **default** | Box (a generic card): content, background and border default + border width | Also the page/body defaults. Code: `theme-color-background-default`, content default, border-width small, `color-border-default` |
| **brand** | Badge `brand` variant: background, border and content brand | Code: the text colour sits on the **base class** so it cascades to all variants, and the brand modifier overrides it. Shows the most obvious change on theme switch |
| **accent** | Ulta Beauty's DS **"Palette"**: `brand-1` to `brand-6` | Interchangeable **siblings** doing the same job, none preferred. Also appears as primary/secondary |
| **disabled** | Text field disabled variant: content, background and border disabled | Technically a state, but **promoted to an intention** so every variant doesn't need its own grey. Code adds a modifier class **and the native `disabled` attribute** so the field can't be used |
| **utility** | Toast: info (the default), error, warning, success: background, content and border utility-* + radius medium | Status styling is **defined once** and reused by alerts, toasts and badges. Code variants are a find-and-replace |
| **knockout** (inverted / reversed / flipped) | Promo block: background knockout **requires** content knockout (also content brand knockout) | Background and content always travel as a pair. Other systems name this `on-default` / `on-brand` / `on-dark`: same job, different words. Expect to need it |
| **subtle / strong** | Ulta: `background default subtle` (light grey block on white); brand-01 is desaturated, with `strong` and `extra-strong` variants | Dials for turning a colour down or up. Works for utility too: a subtle pink default error alert and a strong variant that shouts |
| **tier 3** | Link: default, hover, active, visited | Themes differ (brand colour vs interactive blue). **Disabled falls back to tier-2 `content disabled`** rather than getting its own tier-3 token |

Link in code: states use **browser pseudo-classes, not modifier classes**, which you verify with
DevTools state toggles. Disabled uses a modifier class (`.dsc-link--disabled`) that groups
hover/active/default together to `content disabled`, plus `cursor: not-allowed`.

## Applying the nomenclature: typography

Tier-2 roles are borrowed largely from Material. Figma **text styles** and Sass **mixins** carry the
composite (family, size, line height) as one unit, which is far more ergonomic than binding each
property separately.

| Role | Use | Demo |
|---|---|---|
| **display** | Large, high-impact: hero titles, short bold statements, big stats (e.g. a 64% conversion rate). Mostly marketing sites; rare in utilitarian apps | Hero → `display default` |
| **headline** | Medium, page-level hierarchy: page titles, section headers ("Our Story") | Feature block (Bootsy the dog) → `headline large` |
| **title** | Smaller, functional, often component-level: card titles, subtitles | Product card → `title default` |
| **body** | The default and fallback: passages, descriptions, fine print. Makes the most use of t-shirt sizes | Modal → `body default`; feature list → `body large` (emphasis, lead paragraph); footer copyright → `body small` (legal text) |
| **label** | Form fields, messaging (badges), sometimes navigation. Legibility first | Text field → `label default`; **buttons use label** (short CTAs don't wrap); large button → `label large` + bigger padding (`size(3) size(2)`); small text field → `label small` + 4px block padding |
| **tier 3** | When button type needs to diverge from other form controls | Figma: detach the label style and map to a tier-3 button typography token. Code: add the token to JSON, build, create a `button-default` mixin, swap it in. The authors say button-specific type is legitimate |

- **Responsive type** was baked in during Ch4, so it just works. In Figma, a hero moved into a mobile
  viewport reflows (with some auto-layout quirks). In code, the mixins contain the media queries that
  shrink size and line height. A per-theme **responsive typography playground** serves as both a demo
  and a test.

## Border, shadow, animation (code)

Toast redesign: radius tokens; a border on **inline-start only** at border-width extra-large; a box
shadow matched to Figma (they deliberately try the wrong one first); keyframe animation using `move
quick` + `animation ease` tokens, then swapped to `duration long` because the first felt too fast.
Motion doesn't exist in Figma, so **timing is agreed with design** rather than read off the file.

## Token-powered components (level 3)

Components go through the same **build, publish, consume** cycle as tokens. In Figma, publish the team
library with components included (in practice a separate component-library file). A new file then
subscribes, drags in an instance from Assets, and gets theme switching (apply variable mode) with no
right-sidebar work. That is where the efficiency pays off.

## Technology-specific layer

Reasons core components can't always be consumed include **tech-stack mismatch**. Web components travel
to JS frameworks and CMSs, but not everywhere. Tokens still reach every platform: JSON → Style
Dictionary → per-platform formats. In their Bon Jovi joke, only the names change: the **structure
stays the same**, and the differences are mostly casing and syntax.

### CSS and CSS frameworks

- CSS is the common denominator: every web framework ends up as CSS in the browser, so custom properties
  reach all of them.
- For Tailwind, Bootstrap or Material you integrate tokens into the framework's config (they point to
  Michael Mangialardi's Tailwind article).
- **Use adoption as a moment to re-evaluate the framework.** Teams often reach for these tools as a
  stopgap when they have no token system. Utility classes such as `color-blue` in markup **couple
  the value to where it's applied**, which works against multi-theme and multi-brand support. The
  authors hedge: the tools exist for good reasons and many people like them; the point is to ask what
  jobs they still do.

### Platforms (all from one Style Dictionary config)

| Platform | Output | Naming | Delivery | Theme switch |
|---|---|---|---|---|
| **Web** | CSS custom properties (also Sass/Less variables, CSS-in-JS, TS, JSON) | kebab-case `--ds-theme-…` | npm | Storybook themes |
| **iOS (Swift)** | A generated Swift file | camelCase, same segments (`…ButtonColorContentDisabled`) | **Not npm**: copy manually or by script | Swap in another theme's Swift file |
| **Android** | `colors.xml` + `dimens.xml` (Android dimension units) | snake_case | Not npm; import the XML files | Swap the XML files per theme |
| **React Native** | JS variables (hex colours, numeric dimensions) | PascalCase, per the lesson | **Same npm package** as web | Change the import path (strawberry → dark chocolate) and swap images |
| **Other** | **Custom transforms** | Whatever the target needs | Varies | — |

- The native apps use **tier-2/tier-3 tokens** (tier-1 spacing such as `spacing-12`/`16` used directly),
  so swapping the theme file re-themes the app with no code changes.
- "Other" examples: United check-in kiosks and SeaTac displays, FAA constraints for in-flight displays,
  wearables, medical devices, point-of-sale, digital signage, Cosmopolitan (Las Vegas) slot-machine
  screens, the NASDAQ Times Square ticker.
- Lesson 278 resource: a demo branch where the **Design Tokens Manager** Figma plugin exports tokens,
  a script copies them from `~/Downloads/design-tokens` into the package, Style Dictionary builds them,
  and React Native tokens come out as well. It is for course use only and not redistributable.

### Best practices (tech-specific)

- One JSON source of truth, with Style Dictionary platforms and transforms (custom ones when needed).
- Each platform has its own package or module system, or falls back to a manual step.
- **Platform conventions may override the system, and that's fine.** Defer to Apple's HIG or Material
  for Android where it makes sense (nav bars, tabs). Users live in their OS and expect native behaviour;
  system designers' obsession with consistency has to give way here.
- **Work with the platform implementers** to learn the platform's quirks and agree where the token
  system stops and platform conventions take over.

## Recipes

- **Definition:** product-specific compositions that sit on top of the core DS. The core holds what is
  universally applicable (badges, buttons, form fields, cards, alerts). Material works as Google's core,
  and products add recipes on top: the Docs toolbar, a Gmail message row, a Drive file row, the search
  bar, the YouTube share bar, Calendar's new-event form.
- **Metaphor:** core components are pantry staples (flour, sugar, eggs). Recipes combine them, sometimes
  with **secret ingredients** from outside the cookbook.
- **Three forms:** pure DS composition (following the cookbook exactly), fully custom, or, most often, a mix.
- **Architecture:** the recipe layer consumes tokens (for bespoke UI) **and** components.

### In Figma

The tokens library and components library feed product teams, who build recipes and **publish a recipe
team library**. A feature designer subscribes to all three. Demo: a generic **card** with header, body
and footer zones (slots in code) is published. Its instance gets restyled with tokens, and a core
**button** is swapped into a slot using instance swap. When the card changes (border token, shadow),
every instance picks up the change: shared structure with room for expression.

- Recipes are **often single-theme** (the YouTube team doesn't worry about Maps), but not always:
  Frostd's blog card and an internal customer card with spend data are multi-theme. The custom
  **Starburst badge** is bespoke but still token-wired.

### In code

A product repo pulls in the tokens package, the components package, and recipe packages if recipes are
managed that way. Recipes can also live in the product repo; the authors have seen both and call
neither wrong. The concepts don't depend on framework. The blog card composes a `ds-card` web component (header, unnamed default,
and footer slots), a primary `ds-button`, and Starburst CSS bound to tokens. Consumers just write
`<blog-card>` and pass in data.

### Best practices (recipes)

- **Default to existing DS components** before inventing custom ones, even custom ones wired to tokens.
- **Product teams own recipes**; the DS team helps architect and guide them.
- Recipes are a **test bed** that keeps validating the token system and steers DS work.
- The authors say recipes are one of the biggest lightbulb moments for clients: they allow the right amount of
  expression while respecting the core.
- Onboarding matters here: "it's all the hard human work".

## Smart components

- **Front of the front end** (HTML, CSS, presentational JS, accessibility, cross-browser; the people
  who build the DS component library) vs **back of the front end** (routing, cache invalidation, state,
  APIs and data, DevOps; the people who own the product codebase). Brad hints at a future course on this.
- A smart component **wraps a presentation-only DS component in logic** so developers can drop it in:
  form submission and validation, payments, typeahead, API-bound components, complex data tables and
  product grids, analytics, CMS-ready components.
- At the extreme it is effectively its own app (United's seat selector) and is tightly coupled to the
  backend, so it **doesn't belong in the core DS**. Advanced tables (drag, filter, sort, expand) live in
  framework territory; whole products exist for them, such as **AG Grid**.
- They can be built in-house or be org-specific skins of third-party libraries. Demo: AG Grid themed by
  **attaching to its styling hooks** and wiring them to tokens.

## Product layer

- The special snowflakes. (Wilson Bentley spent his career photographing snowflakes.) Some bespoke UI
  doesn't even belong in recipes.
- If the lower layers do their job, products find most of what they need there. There should not be a
  flood of snowflakes, but there won't be zero either. **Bespoke components should still be wired to tokens**
  in both design and code.
- The chapter's running theme: the layers are confusing. Product people may not know the difference
  between core and recipes, or what tokens are at all. The DS team supplies **education, visibility and
  support**.

## Chapter homework

1. For each product in your ecosystem, decide how it can adopt tokens: can this SaaS tool use tokens
   directly, or only reference them? Can the product consume the token library, or the components?
2. As you apply your token language, **watch for confusion**, especially early on.
3. Go through each ecosystem layer and discuss how tokens enter and are used there.
4. As a system team, decide how you will onboard, educate, guide and support consuming teams (Ch7 covers
   people and process).

## For Sean

- **Treat the integration spectrum as a consumer registry.** Tag every team, framework and tool as
  reference, tokens or components, each with a next step. Levels 2–3 can be verified automatically
  (dependency scans for the tokens and component packages, Figma library analytics). Level-1 consumers
  (CMS, email, SaaS) get nothing automatically, so each needs a named contact and a change feed.
- **The swap needs a theme-matrix visual-regression gate.** Zero diff on the reference theme proves the
  swap is safe; diffs on the other themes show what it unlocks. Generate before/after theme captures in
  the PR so every swap comes with its own magic-trick evidence.
- **The Dev Mode warning matters more with AI/MCP codegen** (my extension of the course's point): design
  output shows unprefixed variable names and individual typography properties. Generators should emit
  `--ds-theme-*` names and typography mixins, never paste literal output.
- **Multi-framework delivery:** the course's answer is custom properties as the web common denominator
  and Style Dictionary outputs with identical structure. It leaves native *distribution* open (manual or
  script). A real channel, such as a versioned SPM/Gradle artifact, is my suggestion, not theirs.
- **CSS frameworks:** if Tailwind or similar stays, expose only semantic tier-2/3 tokens in its config
  so markup can't bind raw palette values. This is my inference from their argument that such classes
  couple value to application.
- **Recipes as audit targets:** product teams own them, but raw values in recipe or product code are
  the cheapest signal of token gaps. That makes recipes the "test bed" the course describes.

## Mechanizable rules

1. Component styles contain no literal colour, spacing, radius, border, shadow or motion values; only token references (Figma: bound library variables).
2. Typography is applied as a composite: library text styles in Figma, mixins in code; no loose `font-*`/`line-height`.
3. Token names in code carry the global prefix (`--ds-theme-*`); unprefixed names pasted from Dev Mode fail.
4. A `*-knockout` background requires a `*-knockout` content colour on the same component.
5. Interactive states use pseudo-classes (`:hover`/`:active`/`:visited`) with state tokens, not modifier classes.
6. Disabled styling uses tier-2 `*-disabled` tokens for every state; form controls also set the native `disabled` attribute.
7. Every component story renders under every theme in CI.
8. A token-swap PR on an existing component shows zero visual-regression diff on the reference theme unless labelled deliberate.
9. Each consumer's declared integration level (reference/tokens/components) matches its dependency scan; the tokens package version is pinned.
10. All Style Dictionary platform outputs expose the same token set after case normalisation.
11. App code on every platform uses tier-2/3 tokens (tier-1 spacing excepted), so a theme-file swap needs no code change.
12. Values copied by hand at reference level (e.g. a WordPress `theme.json` palette) are diffed against the current token build.
13. Themed codebases flag utility classes that encode raw palette values in markup.
14. Recipes, third-party skins (e.g. AG Grid overrides) and bespoke product components obey rule 1.
