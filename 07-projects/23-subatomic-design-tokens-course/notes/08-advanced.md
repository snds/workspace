---
title: Chapter 8 — Advanced Design Tokens
course: Subatomic — The Complete Guide To Design Tokens (Brad Frost & Ian Frost)
sections: ["Chapter 8 - Advanced Design Tokens"]
lessons: 44
status: noted
as-of: 2026-09-23
---

# Chapter 8 — Advanced Design Tokens

Original notes (not a transcript). Raw transcripts: `<Projects>/subatomic-design-tokens-course/transcripts/08-*`.
Sources: 44 items (positions 321–364). 42 have transcripts. **Item 322** ("Fall 2025 Update: Figma
Extended Collections") is an HTML-only lesson, taken from `files/08-*/322-*__notes.html`. **Item 358**
("Using AI to Adopt Tokens in Existing Application") has no transcript, so it comes from its Wistia
caption (`captions/08-*/358-*.txt`). The chapter slide PDF (≈204 MB) was too large to render here.
**Discrepancy:** lesson 8.13 promises that the next video is a ~15–20 min recording of the pre-order
community Q&A on internationalization (writing modes, font loading, logical properties, screen-reader
dialects; raised by Omar from Egypt). The item that follows (336) is instead **"Dimitri's Token
Architecture Demo"**, a different guest demo from a community session. Its caption matches its
transcript, so the swap is in the course, not in the download. The i18n Q&A recording isn't in the
material.

Framing: "advanced" means **optional, not harder**. Something that is a nice-to-have for one org can be
another org's core use case. Most of these cases are **subsets or extensions** of work already done,
and each one usually touches only a **few token properties** (only colour, only typography, sometimes
a single property). So the extra effort is well below the cost of standing up the architecture.

| Use case | Properties it usually touches | Mechanism (code) | Mechanism (Figma) | Who customizes |
|---|---|---|---|---|
| Knockout / inverted | colour (tier-2 roles) | None. It's already in the parent theme | None | System makers |
| Dark mode (user or system) | **colour + box-shadow only** | Skinny override theme loaded after the parent | New sibling **mode** in the tier-2/3 collections | System makers |
| Sub-brand | Cosmetic: colour, maybe font family, maybe radius | Override theme loaded after the parent brand | Sibling mode that "inherits" the parent's values | System makers |
| White label / CMS | Colour, overwhelmingly. Maybe radius | Translation layer plus config, settings panel or CMS | Little role (client mock-ups only) | **Auxiliary users** |
| Product families | None. You pick different components, variants and tokens | Same system | Same system | Product teams |
| i18n / l10n | Colour, typography, spacing/density | Small tweaks, plus native web features | — | System makers |
| Redesign / refresh / rebrand | From one value up to every category | In the existing theme, a new theme, or a replatform | New theme | System makers + product teams |
| Campaigns | A couple of brand colours | An appended override, **scoped to a page section** | — | Marketing + makers |

## Fall 2025 update: Figma Extended Collections (HTML-only item)

- Figma announced **Extended Collections** at **Schema 2025**. An author builds a **parent collection**
  and **extends** it to create an instance for each brand. Designers then **override only the variables
  that differ** in that extended collection. The note quotes Figma's help article and links a YouTube
  demo (from ~12:46).
- The authors' view: Extended Collections suit **building on a theme and tweaking only what's needed**.
  They say many of this chapter's cases, naming **dark mode and white labeling**, would benefit from
  the feature.
- **Plan gate:** at the time of the note it was **Enterprise-only**. So the chapter's videos, which use
  sibling modes, still apply to non-Enterprise teams. If you have the feature, mentally translate the
  videos' sibling-mode steps into extensions. The note gives no more detail than that. It doesn't say
  whether the brand axis, the mode axis, or both should use extension.

## Dark mode

### Three flavours (refresher from Chapter 1)

| Flavour | Example | How it's handled | Dedicated theme? |
|---|---|---|---|
| **Knockout / inverted** | `color.content.knockout` sitting on `color.background.brand` | Tier-2 roles **inside the same theme** | **No.** The authors say much of what people call "dark mode" is really this |
| **User-selected** | GitHub (light/dark, with contrast variants inside each), **Piccalilli** (Andy Bell / Set Studio) toggle | Swap the root theme class, e.g. `theme-chocolate` → `theme-dark-chocolate` | Yes |
| **System setting** ("dark mode proper") | Dave Rupert's site | `prefers-color-scheme` media query conditionally loads the dark token set. React Native: the `useColorScheme` hook picks light or dark tokens | Yes |

The user-selected and system flavours use the **same mechanics**. The only difference is **where the
switch lives**: in the UI, in the OS, or both (a media query default plus a user override).

### Should you build it at all?

They point to an article asking whether your product really needs a dark mode, and weigh it up:

| Pros | Cons |
|---|---|
| Less eye strain and headaches *for some users* | *Some* users report **more** eye strain. Results are contextual and subjective |
| Battery savings (dark pixels draw less power) | **ROI is uncertain**, so measure it |
| Honours the user's OS preference | **Every design, build, QA and maintenance task doubles.** Each new token or component has to work in both modes |
| The trend and cool-kids factor since ~2019, when iOS and Android shipped OS dark mode. The authors say that's a fine reason | — |

Good justifications they name: software people use eight hours a day, or loud user demand. Their advice
is to go in knowing the ongoing cost.

### Mechanics (Frostd: `chocolate` → `dark-chocolate`, built through the homepage)

- **Scope: colour and box-shadow only.** Typography, border width and radius, and animation stay the
  same. Keep the dark theme **skinny**.
- **Figma:** in the **tier-2** collection, add a mode with "+" or duplicate the chocolate mode. Remap
  `background.default` to dark brown and content to light cream. Brand content, which failed contrast,
  becomes gold. Then **duplicate the mode in the tier-3 collection too** and remap the button tokens.
  The result is two side-by-side designs, each strong on its own. Neither is the lesser
  version. The authors call the colour work an art form.
- **Figma org choices:** in practice, especially with many brands and theming categories, they **add
  the dark theme as a sibling mode** next to the others. That sometimes means duplicating the whole
  light theme to change a handful of values. They say **you could instead create a separate collection
  as another dimension**, like the Ch4 viewport-typography collection, which would be leaner. They don't
  demo it.
- **Code is simpler:** the dark theme file holds **only the overrides**: define the dark colours, remap
  them, adjust the shadows. At runtime the **parent (`chocolate`) always loads as the base** and
  `dark-chocolate` overrides only what differs.
- **Validate in real screens.** Use pilot-project screens plus the kitchen-sink component playground.
  "Doing this stuff in isolation simply doesn't work" (8.02). The failure to watch for is dark text on a
  dark background.

### What the chapter says about theme vs mode (the open question)

- **Chapter 8 does not model dark mode as an axis orthogonal to brand.** Dark mode is a **dedicated
  child theme of one brand**. `dark-chocolate` inherits from `chocolate` and overrides colour and
  shadow. In code it's an override layer on the parent. In Figma it's a **sibling mode column** in the
  same tier-2/3 collections as the brand themes. The summary (8.42) describes dark mode as a possible
  dedicated theme, switched by the user or by the system.
- The chapter **mentions** a separate-collection "dimension" as a Figma option but doesn't recommend it.
  It also notes that Figma sibling modes can mean full duplication, while code overrides stay skinny.
- The AI section repeats the same pattern: the AI dark-mode demo generates a **`dark strawberry`**
  theme, one dark theme per brand.
- The Extended Collections note says dark mode would benefit from extension but doesn't say how.
- The course gets closest to orthogonality in **Dimitri's guest demo**, where light / dark / dimmed /
  high-contrast are **computed presets per brand**. That is guest material, not the course's own advice.
- Conclusion: the course's **theme list flattens brand × mode**. Keeping them orthogonal (Curtis) is
  not contradicted, just not practised here.

## Sub-brands

- Example: **Verywell → Verywell Fit / Verywell Mind** (from Ch1). Tie-in: the Ch1 **brand relationship
  spectrum**. The relationship between parent and sub-brand determines the architecture.

| Relationship | Strategy |
|---|---|
| Effectively a distinct brand | Stand it up as its **own theme** |
| True parent-child: the parent anchors the visual language and the child tweaks a few things | **Child override theme** on top of the parent |
| The child overrides so much it feels like **fighting** the parent instead of extending it | Promote it to a **standalone theme** |

- **Override only cosmetic properties:** colour, sometimes font face, sometimes border radius. **Don't
  override font size, spacing or sizing.** Structural differences cause maintenance headaches.
- Frostd demo: **Frostd Dawgs** (pup cups). Add an orange tier-1 palette, create a **`Strawberry Dawgs`
  mode inheriting from `strawberry`**, and remap the strawberry references to orange in tiers 2 and 3.
  In code, define only the overrides, load `strawberry` first, and let the cascade apply the sub-brand
  on top.
- **Governance cost:** children depend on the parent, so **every parent change propagates to all child
  themes**. The parent carries more responsibility.

## White labeling and CMS implementation

- Examples: **Blend** (mortgage-application SaaS whose bank customers re-skin it with their own logo
  and colours), **Material Design 3** (generated palettes, added **~7–8 years** into Material's life),
  **InsuredMine** (a colour-theme settings page). Many general-purpose design systems fit this pattern:
  a base, with some parts locked and some customizable.
- **Timing:** add it **after v1**, not while you're bootstrapping. If it's your core business (like
  Blend), do it in **phase 3**. Otherwise it can come later still. Wait until the system has
  settled.
- **Auxiliary users:** a third role alongside makers and users. Usually marketers or brand people who
  sit near design and development but lack UI expertise. Make it easy for them and limit the damage
  they can do (the *Home Alone 2* burglars).

| Customization surface | Their take |
|---|---|
| **Colour** | Overwhelmingly the main, and most obvious, case |
| Border radius and other "safe" properties | Possible |
| **Font family** | Gnarly: licensing issues, and changed line wrapping can break layouts |
| Anything that changes the **box model** | Avoid |

- **Translation layer:** put a thin layer in front of the three-tier system. Don't expose
  `color-background-brand-subtle`. Expose names like **`primary` / `secondary`**, in the auxiliary
  users' own vocabulary ("brand primary" if that's what brand people say). White-label names **needn't,
  and probably shouldn't, match** the internal token names. **Never surface the entire token system.**
- **Start from the vanilla base** so defaults don't clash with what customers can change, and show
  where each option lands in the UI.

| Delivery model | Notes |
|---|---|
| Vendor-managed config (**white glove**) | A JSON or settings file in the codebase, deployed into the client's environment. Stays locked down |
| Settings / preferences panel | Users change values, save, and see the result |
| **CMS** integration | Surface a *subset* of tokens in WordPress, Drupal, etc. |
| Figma | The "sad Keanu" slide. Only for mocking up a client preview. This is an **implementation** problem |

- **Risk:** user-controlled values threaten accessibility and quality (white text on a light-yellow
  background). Mitigate with **education, documentation and tooling**.

## Multiple product families

- They've already shown this: the Frostd marketing homepage and the data-heavy dashboard share one
  system. Teams often argue that their business units (staplers vs paper) are too different. That's
  true for the business, but it doesn't matter for UI. Components are **boxes** (U-Haul boxes work for an office move
  or a house move).
- Kinds of variation Brad lists: **content** (different content through the same card), **structural**
  (text / text+icon / icon-only button), **stylistic** (zebra-striped or dense tables), **behavioural**
  (dismissible or persistent alert). He notes the list isn't exhaustive.

| | "Sites" (marketing / informational) | "Apps" (capital-E enterprise) |
|---|---|---|
| Type | Large, e.g. `display-large` | Smaller |
| Components | Heroes, cards, features: chunky | Tables, charts, forms: utilitarian and transactional |
| Density | More whitespace, jumbo CTAs | Denser. Smaller component variants |

- These are **stereotypes with heavy crossover**. Buttons are still buttons. Hence **one toolset** (the
  "tools in the basement": most jobs use the hammer and drill, and some need the orbital sander).
- **Separate site and app themes** that control sizing and density are technically possible, but the
  authors **haven't seen it on a client project**. If you change the type scale or sizing constants
  per theme, **re-QA both**.

## Internationalization and localization

- The authors call it a huge topic and hand off to a **Spotify Design** article on the layers of
  localization, plus a second tips article. What tokens can do:

| Lever | Why |
|---|---|
| **Colour** | Cultural meaning differs (red means different things in different places) |
| **Typography** | Languages, **writing modes**, character-based scripts, loading different fonts |
| **Spacing / density** | Whitespace reads as pleasing in some cultures and as an anti-pattern in others |
| (content length) | German and Dutch strings run longer than English |

- **Practical tip:** find a **sensible middle ground** for font size and spacing. Aim for **tweaks, not a
  full theme per country**, and avoid wild swings between locales.
- **Lean on the web platform:** fluid layout, natural wrapping, **CSS logical properties**, writing
  modes, responsive design. The authors say it was built with the world in mind.

## Guest demo: Dimitri's token architecture (item 336, community session)

Not course doctrine. It's a guest showing his own system, and Brad reacts to it.

- **Per-component config files** (style at the base, plus "roles" = variants) feed a
  **platform-agnostic engine** that generates CSS (`gen.css`). Swift and Kotlin generation is planned.
  No hand-written `error-background` tokens: components have **background / foreground / border**
  relationships that are **calculated**, using **APCA** contrast so they can't become inaccessible.
  He likens it to **Donnie D'Amato's *mise-en-mode***.
- **Brand config = OKLCH hue + chroma per intent.** **Lightness is derived** from the configured
  contrast targets. Button parameters: alpha (how much colour sits on the surface), lightness shift,
  foreground contrast, chroma.
- **No density, contrast, mode or size tokens.** Presets per brand: light, dark, **dimmed**, high
  contrast, dark high contrast. Component size = density + scaling relative to the parent. Sliders
  control base `rem` and spacing (for accessibility), surface **elevation steps**, and **colour-vision-
  deficiency** simulation with a severity setting. Themes can nest ("themes in themes").
- **Agentic brand ingestion:** **Firecrawl** scraped DraftKings. An agent with brand- and content-
  scraping skills extracted colours, converted them to OKLCH and wrote the brand config. No colour ramps or
  type scales were authored.
- Stated goal: tie it to **generative UI**, e.g. asking for a UI for an Asian market, for a CVD user,
  in Arabic, and having it adapt.
- Brad's takeaways: the **system's parameters matter more than specific values**. AI lets people reach
  a sophisticated system through their own mental model (hand it a brand hex like BE6700 and ask it to
  fit the system) without an airplane manual. What you need is **fluency in web materials**
  (`clamp()`, colour spaces, variable fonts), not every inner detail.

## Redesigns, refreshes and rebrands

| Scale | Examples they cite | Token response |
|---|---|---|
| **Tiny tweak** | Nudging a hex; making brand blue more accessible; adding a purple where there was only blue; Jessica's logo-legibility tweaks | Do it **inside the existing theme** |
| **Refresh** | New typeface + new brand colours; Verizon keeping its logo but adding highlighter yellow | Likely a **new theme** |
| **Radical redesign / rebrand** | united.com (purple buttons, new DS); About.com → **Dotdash** (now Dotdash Meredith); Cigna + **Evernorth**; **Nasdaq** acquisitions (keep the acquired UI or fold it in?) | A **new theme across every category**. At total-transformation scale, anything goes: replatforming, new stacks, systems merging |

### Adopting it into existing software: the fallback switch

Product teams rarely welcome a rebrand mandate "from on high". The authors' goal is **laparoscopic
surgery, not a teardown**, plus a service mindset: use the rebrand to advance the product team's own
goals.

1. Import the token system and the redesign theme.
2. Wire the product to tokens with **CSS custom properties that carry fallbacks**:
   `var(--token, <legacy value>)`.
3. **Comment out or remove the redesign theme import.** The hooks exist, but the legacy fallbacks
   render, so the UI looks identical. You can **ship this safely**.
4. Test and QA until you get the green light, then **re-import the theme**, and the token values take
   over.
5. Once the launch is stable, **delete the fallbacks**.

| Starting point | Approach | Cost |
|---|---|---|
| **No system** (hard-coded values) | Replace literals with `var(--ds-token, #legacy)` | Touches each style |
| **Existing Sass variables**, option A | Per component: `var(--ds-token, $brand-purple)` | Works, but touches the **whole component codebase** |
| **Existing Sass variables**, option B | Wire the token **into the Sass variable definition** (`$primary: var(--ds-token, purple)`) and let the Sass variables spread it. They did this at **Caterpillar** with `Cat Yellow` | Rest of the codebase untouched |
| **Already token-powered** | Add the new theme, keep it commented out until launch, then uncomment | Easiest |

## Campaigns

- Short-lived, bespoke designs with a job and an end date, such as a **holiday** red and green for the
  Frostd homepage. The process is shortcut. Load the core theme, **append** `holiday-red` and
  `holiday-green`, and remap `background-brand` / `content-brand`. **Overrides and bespoke one-offs
  are acceptable here**, because the design is deliberately specific and temporary.
- **Themes can be scoped to part of a page.** A `.holiday-theme` class (on a wrapper div or on the hero
  itself) overrides the custom properties only inside it. The rest of the page stays `strawberry`. You
  can also show `vanilla`, `chocolate` and `strawberry` together, for example on a parent company's site.
- Campaigns get less rigour and less QA (sometimes they appear only on the homepage). For **recurring
  holidays**, keep the tokens "in the attic" to reuse next year.

## AI and design tokens

### Framing

- LLMs are **language** models, and tokens are the org's **shared language and the API between tools**.
  The authors call that a natural fit. Their stance throughout is **simultaneous curiosity and
  skepticism**. They aim to spark ideas, not give answers, and they expect the videos to date
  quickly. (Recorded about 1–2 weeks before a Figma Config.)
- "AI is part of our design system toolkit" and design systems are part of the AI toolkit. The DS
  supplies the **constraints and infrastructure** that make generative output trustworthy: you tell the
  model how things are done here and have it generate new work with those conventions.

### Tool landscape (as recorded)

| Category | Named |
|---|---|
| Design tools | **Figma AI** (First Draft, rename layers, sample data, prototyping); **Motiff**; **Uizard**; **Penpot** (open source, which had just shipped native design tokens) |
| Dev IDEs | **GitHub Copilot**, **Cursor** (used throughout the course), **Windsurf**. The authors warn to watch what they do under the hood |
| Design↔code sync | **UXPin**, **Builder.io** (has token features), **Anima**; "Hoobastank AI" is a joke site Claude generated |
| Base models | GPT, **Claude**, Gemini, Copilot. Talking to the models directly gets you a long way |
| Scaffolding | **bolt.new** |

### Use cases, mapped to the course's phases

| Phase / task | Demo | What worked | Limits the authors flag |
|---|---|---|---|
| **Naming: extract** | View-source CSS from the **Jane Goodall Institute** site → ChatGPT asked for a token taxonomy → text tree → distil into a naming algorithm using the Ch3 anatomy slide as reference | Gets a draft nomenclature and structure quickly | Early clustering was off; it takes iteration |
| **Naming: arbitrate** | Asked to settle `default` vs `initial` → rationale, recommends `default`. Then asked for other states | Pros and cons as fodder to reach consensus | **It doesn't decide for you.** The state list conflated concepts |
| **Environment setup** | bolt.new: Style Dictionary + vanilla/chocolate/strawberry/dark-chocolate → a running reference site with a theme switcher in minutes | Speed | Without context it builds generic output (a custom site instead of Storybook, unknown conventions). **Feed it your nomenclature, taxonomy and sample theme** |
| **MVP from brand guidelines** | Spotify guidelines link → Claude → colour, type and spacing tokens (Sass, RN) | A first draft from vague guidelines | Likely invented values |
| **MVP from an image** | ESPN screenshot → tokens → re-mapped to a sample CSS file's format → dropped into Frostd | Forced into your architecture quickly | Accuracy unknown until you check |
| **MVP from an existing product** | **Radiooooo**: CSS Stats → screenshot of background colours → Claude lists and **dedupes** them → map to the tier-1 JSON format → then tier 2 → **Cursor** scaffolds a `radio` theme, registers it in the Storybook switcher and adds a build script | Scaffolds a whole new theme end to end | Not one-shot. Manual fixes needed (e.g. `base` → `brand`) |
| **Colour ramps** | Coolors palette → 100–900 ramps | Fills gaps in vague guidelines | Accessibility unverified |
| **Figma → code** | **Screenshot of the Figma variables panel** → JSON per theme | Works on the second prompt | **The first pass hard-coded hex and dropped aliasing.** Needed a re-prompt for reference notation. Doesn't replace Tokens Studio or the Figma API |
| **Testing** | Theme CSS plus a planted `vanilla-wrong` (content-default white on background-default white) → asked for an accessibility test | Caught the invisible-text error | **Not** a substitute for user testing or proper a11y tooling |
| **New component** | Cursor asked for a toast mirroring alert's structure and variants | Followed conventions (`ds-c-toast`); states wired to tokens | You still have to accept and review the diff |
| **Adopt in an existing app** *(caption source)* | Next.js + **MUI** page → Cursor told to apply the strawberry theme, with tokens as context | Maps components to token custom properties; eases product-team fear | This demo was a radical visual change. It can also just wire things up |
| **Translate formats** | Any output format from the JSON source; **glue code** for brittle legacy apps | They use it a lot for glue | Style Dictionary is **not** obsolete |
| **Dark mode** | Generate `dark strawberry` from `strawberry` | Got there eventually | Several iterations, and it skipped tiers 2/3 at first. **Copy-paste would have been faster**, so know when to use it |

### Principles (8.40)

| Principle | Meaning |
|---|---|
| **Respect** | Use people's time and talent well. Automate drudgery (nobody should hand-convert a variables table to JSON), but protect people's humanity and livelihoods |
| **Org-specific solutions** | Tools must go **with the grain** of the org's culture and conventions (the reason orgs don't all run on Wix) |
| **Security and privacy** | A high bar. Don't upload user data to ChatGPT. Where the AI runs matters |
| **Humans own input and output** | Garbage in, garbage out. Humans control inputs and can modify, extend and fix outputs. The authors call this a duty |
| **Predictability and reliability** | Tokens are critical infrastructure |
| **Enhancement, not replacement** | Honour the hard-won human consensus and tool decisions |

### Our role (8.41)

- "AI vs humans" is a false dichotomy, even if it feels existential to people whose craft was drawing
  or coding rectangles.
- Watch out for **AI slop** and **enshittification** (Cory Doctorow, 2022). Brad also cites his 2013
  *Death to Bullshit* talk and **Sturgeon's law** (90% of everything is crap). Easy production floods the
  zone, so the human job is the **harder filtering work**: making sure output is sound, accessible,
  follows web principles and is good for people. His closing message: you won't be replaced by AI,
  though parts of the job may be encroached on.

## Chapter homework

From the chapter summary (8.42):

1. **Audit your org's advanced use cases.** Dark mode? Sub-brands? White labeling? Decide which matter
   most and start those conversations.
2. **Identify the hard parts** blocking them, and tackle those head-on.
3. **Map your org's AI adoption:** policies, which tools are **sanctioned**, and which would be hard to
   introduce.
4. Keep exploring the AI landscape with curiosity and skepticism, looking for ways to make token work
   better and faster.

## For Sean

- **Resolve theme vs mode in your favour, knowingly.** The course flattens brand × mode into a theme
  list (`chocolate`, `dark-chocolate`, `dark strawberry`). That's workable for four themes but
  multiplies with N brands. Keep Curtis's orthogonality in the *model*: in Style Dictionary, build a
  `brand/*` × `mode/*` matrix of override layers; in Figma with Enterprise, use a parent collection with
  light/dark **modes**, **extended** per brand. *My synthesis.* The course's Extended Collections note
  doesn't prescribe this split, so verify how extended collections inherit modes before committing.
- **The Figma/code asymmetry is the real cost.** Code dark and sub-brand themes are skinny overrides,
  but Figma sibling modes (without Extended Collections) are **full copies**, so drift hides in the
  unchanged values. Generate the Figma mode from the code override (or diff them) instead of
  maintaining both by hand.
- **Treat "skinny" as a lintable contract.** Dark mode: colour and shadow only. Sub-brand: cosmetic only.
  White label: an allowlist. Make those category limits checks in the build, not guidance in docs.
- **White label is a public API.** Version the auxiliary-user vocabulary (`primary`/`secondary`)
  separately, map it through a declared translation table, and run contrast checks at save time.
  That's the "tooling" the authors gesture at.
- **The fallback switch is the cleanest rebrand migration pattern in the course.** Pair `var(--t,
  legacy)` with a feature-flagged theme import, and track remaining fallbacks as burn-down debt after
  launch. At Caterpillar they wired tokens into the Sass variable definitions, which reaches a legacy
  estate with the smallest diff.
- **For agents in the pipeline:** the course's clearest AI failure mode is **losing aliasing**
  (screenshot → hard-coded hex) and skipping tiers. Gate every agent-generated token PR on a
  reference-integrity check and the name linter. Dimitri's parametric OKLCH/APCA engine (config →
  computed tokens, agent-scraped brands) suggests agents should edit **parameters**, not values.

## Mechanizable rules

1. A dark-mode theme (code override file or Figma mode) may only set values for **colour and
   box-shadow** tokens. Any override of typography, spacing, sizing, border width/radius, animation or
   z-index fails the build.
2. Every override theme (dark, sub-brand, campaign) defines **only token names that already exist in its
   declared parent theme**, and its output is loaded after the parent. An unknown token name, or a
   missing `parent` declaration, fails.
3. A **sub-brand** theme may override only cosmetic categories (colour, font-family, border-radius).
   Overrides of font-size, line-height, spacing or sizing tokens fail.
4. If a child theme overrides more than an org-set share of its parent's tokens, CI flags it for
   promotion to a standalone theme. *The course gives no threshold.*
5. Any change to a parent theme triggers visual regression and contrast checks on **every descendant
   theme** (dark, sub-brand, campaign) across the component playground and pilot screens.
6. For every theme, each content/background tier-2 pairing (e.g. `content-default` on
   `background-default`, `content-knockout` on `background-brand`) passes a contrast check. At minimum,
   identical resolved values fail. The course gives no ratio, so use WCAG.
7. If the product supports system dark mode, the CSS output contains a
   `@media (prefers-color-scheme: dark)` block applying the dark overrides. If it supports a user toggle,
   each theme is emitted under a **class selector** (e.g. `.theme-dark-chocolate`) that works on the
   root or on any subtree.
8. In Figma, every theme mode in the tier-2 collection has a same-named mode in the tier-3 collection,
   and every Figma theme mode has a same-named code theme output (and vice versa).
9. White-label / CMS customization exposes only an **allowlisted set of keys**, colour by default and
   optionally border-radius. No exposed key may map to spacing, sizing, font-size, line-height or
   font-family tokens.
10. Every exposed white-label key is defined in a **translation map** to ≥1 internal token. Internal
    token names (e.g. `color-background-brand-subtle`) never appear as exposed keys.
11. White-label customization starts from the **vanilla** (unbranded) theme as its default base.
12. User-supplied white-label colour values are contrast-validated against their paired content colours
    at save/deploy time, and a failing pair is rejected or warned on.
13. The white-label customization feature may not ship while the token package version is `<1.0.0`.
14. During a rebrand transition, each token reference in legacy code carries a legacy fallback
    (`var(--token, <legacy>)`). After launch, a report counts the remaining fallbacks as debt, down to
    zero.
15. Campaign tokens live in a separate namespace/directory. Core theme source never imports them, and
    campaign themes are applied only through a scoped class selector. Recurring campaign themes are
    archived, not deleted.
16. Locale overrides may touch only colour, typography and spacing/density tokens. A per-locale theme
    that overrides more than an org-set number of tokens is flagged. *No threshold is given.*
17. Stylesheets use **CSS logical properties**. A stylelint rule rejects physical
    `margin-left`/`padding-right`/`left`/`right` etc. where a logical equivalent exists.
18. In any token file (including AI-generated ones), tier-2 and tier-3 values must be **references/
    aliases**, never raw literals. The alias-integrity check fails on a hex or dimension literal above
    tier 1.
19. AI-generated tokens, themes and components pass the same name linter, alias-integrity, contrast and
    visual-regression gates as human work. A human reviewer's approval is required before merge.
20. Component styles, including AI-generated ones, reference token custom properties for colour,
    background and border (no raw hex) and use the system's class prefix (e.g. `ds-c-`).
21. AI tooling that receives code or token source must appear on the org's sanctioned-tool allowlist. A
    CI or pre-commit check blocks configs pointing at unsanctioned endpoints.
