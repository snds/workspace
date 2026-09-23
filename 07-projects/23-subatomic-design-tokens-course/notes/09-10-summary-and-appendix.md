---
title: Course Summary + Appendix — Subatomic
course: Subatomic — The Complete Guide To Design Tokens (Brad Frost & Ian Frost)
sections: ["Course Summary", "Appendix and Resources"]
lessons: 7
status: noted
as-of: 2026-09-23
---

# Course Summary + Appendix

Original notes (not a transcript). Raw transcripts: `<Projects>/subatomic-design-tokens-course/transcripts/09-*`.
Lesson 369 ships a mislabelled transcript (a copy of 368); its notes come from the Wistia caption in
`captions/09-*`. The resource index below is generated from the course's "Links & Resources" page
(`files/10-*__notes.html`; machine copy `manifest/resources.json`).

## The authors' own recap, compressed

| Ch | The one idea to keep |
|---|---|
| 1 | Tokens make UI themeable for multi-all-the-things orgs; systems beat rebuilding every instance; tokens = aesthetics, components = structure/behaviour. |
| 2 | Three tiers (ingredients → jobs → rare component overrides); a theme = all three; colour + type carry the weight; composites travel together; start simple. |
| 3 | Names are the API; naming is hard because it is invented and subjective; co-create with devs; **structure beats specific words** — use an algorithm. |
| 4 | Build tiers in Figma (collections/modes) and code (Style Dictionary) in lockstep; each category has quirks (responsive type hardest); sync is a human process. |
| 5 | A token system is a **library**; tier 1 stays "behind the kitchen doors"; test before publishing; ship a Figma team library + a code package. |
| 6 | Spectrum of integration (reference → tokens → components); adopt at every ecosystem layer incl. recipes; makers must help users wield it. |
| 7 | Phases (MVP pilot → 1.0 → extend + support → optional self-service); a governance decision tree; "talk, talk, talk." |
| 8 | "Advanced" means *situational*, not technically harder: dark mode (user and/or OS), sub-brands/campaigns as partial overrides of a parent theme, white-label/CMS layers for non-designers, i18n tweaks to colour and type, rebrand strategy scaled to scope, and generative AI as an assistant whose output humans must still judge. |

## Closing stance

- The landscape keeps moving; concepts outlast tools.
- The course's through-line is cross-disciplinary empathy — designers understanding code, developers
  understanding Figma.
- Credits: Molly Hellmuth (UI Prep) built the Frostd Tokens Figma work; nods to Vitaly Friedman
  (Smashing), Christine Vallaure (Moonlearning), Matt D. Smith (Shift Nudge), Wes Bos.
- Remaining lessons are logistics (certificate, survey, where to follow the authors).

## For Sean

- The chapter-8 framing ("advanced = situational") is the right intake question for any new client or
  employer system: which advanced axes actually apply? It is step 1 of [[token-architecture]].
- The recap confirms the two load-bearing doctrines to carry into every token review: **tier 2 is the
  contract** and **structure/algorithm over word choice**.

## Resource index (from the course's Links & Resources page)

### Introduction

- [Atomic Design Book](https://atomicdesign.bradfrost.com/)

### Chapter 1: Core Concepts

- [Starbucks Creative Expression Color](https://creative.starbucks.com/color/)
- [Separation of Concerns Wikipedia](https://en.wikipedia.org/wiki/Separation_of_concerns)
- [CSS Zen Garden](https://csszengarden.com)
- [Every Windows 3.1 Theme](https://imgur.com/gallery/every-windows-3-1-theme-SsVYqM1#3FNW1hn)
- [Using Design Tokens with the Lightning Design System](https://www.youtube.com/watch?v=wDBEc3dJJV8)
- [Lightning Design System Design Tokens](https://www.lightningdesignsystem.com/design-tokens)
- [Material 2 Color Usage and Palettes](https://m2.material.io/design/color/the-color-system.html#color-usage-and-palettes)
- [W3C Design Tokens Community Group](https://www.w3.org/community/design-tokens/)
- [CSS Tricks: What are Design Tokens? by Robin Rendle](https://css-tricks.com/what-are-design-tokens/)
- [Style Dictionary](https://amzn.github.io/style-dictionary)
- [The Design System Ecosystem](https://bradfrost.com/blog/post/the-design-system-ecosystem/)

### Chapter 2: Foundations & Architecture

- [T-Mobile Brand Assets](https://tmap.t-mobile.com/portals/pro74u7a/EXTBrandPortal)
- [CSS Stats](https://cssstats.com/)
- [Material UI Colors](https://materialui.co/colors)
- [Adobe Color Wheel](https://color.adobe.com/create/color-wheel)
- [Interaction of Color by Josef Albers](https://interactionofcolor.com/)
- [Expressive Design Systems by Yesenia Perez Cruz](https://www.yeseniaperezcruz.com/expressive-design-systems)
- [Shopify Polaris Banner Component](https://polaris.shopify.com/components/feedback-indicators/banner)
- [Quickbooks Design System Color Palette](https://designsystem.quickbooks.com/foundations/color-palette/)
- [Using Color to Enhance Your Design by Kelley Gordon](https://www.nngroup.com/articles/color-enhance-design/)
- [WebAIM Contrast and Color Accessibility](https://webaim.org/articles/contrast/)
- [WebAIM Color Contrast Checker](https://webaim.org/resources/contrastchecker/)
- [Figma plugin for quick access to WCAG color contrast ratios](https://usecontrast.com/)
- [A Practical Guide to Designing For Colorblind People](https://www.smashingmagazine.com/2024/02/designing-for-colorblindness/)
- [Who Can Use: How Color Contrast Affects People With Visual Impairments](https://www.whocanuse.com)
- [Practical Accessibility](https://practical-accessibility.today)
- [Color in Design Systems by Nathan Curtis](https://medium.com/eightshapes-llc/color-in-design-systems-a1c80f65fa3)
- [Color within Constraints by Linzi Berry](https://medium.com/tap-to-dismiss/color-within-constraints-d6f777a3b72d)
- [Component Gallery](https://component.gallery)
- [Web Design is 95% Typography](https://ia.net/topics/the-web-is-all-about-typography-period)
- [Adobe Fonts Recommendations](https://fonts.adobe.com/recommendations)
- [Font Pair](https://www.fontpair.co/)
- [Monotype Font Pairing](https://www.monotype.com/font-pairing)
- [10 Tips on Typography in Web Design by Nick Babich](https://uxplanet.org/10-tips-on-typography-in-web-design-13a378f4aa0d)
- [Guide: How to Define & Use Typography in UX/UI Design](https://designlab.com/blog/what-is-typography-how-is-it-important-to-ux-ui-design)
- [WebAIM Typefaces and Fonts](https://webaim.org/techniques/fonts/)
- [Digital.gov Accessibility for Teams: Visual Design Typography](https://digital.gov/guides/accessibility-for-teams/visual-design/#typography)
- [Home Office Design System Layout and Typography Accessibility](https://design.homeoffice.gov.uk/accessibility/layout-typography)
- [W3C Community Group Composite Design Token](https://tr.designtokens.org/format/#composite-design-token)
- [Typography Systems in Figma](https://www.figma.com/best-practices/typography-systems-in-figma/typography-scales/)
- [Modular Scale](https://www.modularscale.com/)
- [Intro to The 8-Point Grid System by Elliot Dahl](https://medium.com/built-to-adapt/intro-to-the-8-point-grid-system-d2573cde8632)
- [Goodbye 8-Point Grid, Hello 4-Point Grid by Dries De Schepper](https://uxdesign.cc/goodbye-8-point-grid-hello-4-point-grid-1aa7f2159051)
- [Space in Design Systems by Nathan Curtis](https://medium.com/eightshapes-llc/space-in-design-systems-188bcbae0d62)
- [Including Animation In Your Design System by Val Head](https://www.smashingmagazine.com/2019/02/animation-design-system/)
- [Val Head books](https://valhead.com/books/)
- [Animation/Motion Design Tokens by Oscar Gonzalez](https://medium.com/@ogonzal87/animation-motion-design-tokens-8cf67ffa36e9)
- [Carbon Design System Motion](https://carbondesignsystem.com/elements/motion/overview)

### Chapter 3: Naming Conventions

- [API Wikipedia](https://en.wikipedia.org/wiki/API)
- [CSS Tricks: What are Design Tokens? by Robin Rendle](https://css-tricks.com/what-are-design-tokens/)
- [Figma: View and explore library analytics](https://help.figma.com/hc/en-us/articles/360039238353-View-and-explore-library-analytics)
- [Naming things is hard](https://www.karlton.org/2017/12/naming-things-hard/)
- [Design tokens are just meticulously debated variables.](https://www.linkedin.com/posts/tpitre_design-tokens-are-just-meticulously-debated-activity-7296201244245692416-3UjQ)
- [Creating Design Principles by Jared M. Spool](https://articles.centercentre.com/creating-design-principles/)
- [Design Principles: An open source collection of Design Principles and methods](https://principles.design)
- [Design Principles by Adactio](https://principles.adactio.com)
- [Merriam-Webster Dictionary Definition of Algorithm](https://www.merriam-webster.com/dictionary/algorithm)
- [Atlassian Design System Design Tokens](https://atlassian.design/tokens/design-tokens)
- [REI Cedar Design System Tokens](https://cedar.rei.com/tokens)
- [Pajamas Design System Reading design tokens](https://design.gitlab.com/product-foundations/design-tokens-reading)
- [Primer Design System Token Names](https://primer.style/foundations/primitives/token-names)
- [Adobe Spectrum Naming Structure](https://spectrum.adobe.com/page/design-tokens/)
- [Naming Tokens in Design Systems by Nathan Curtis](https://medium.com/eightshapes-llc/naming-tokens-in-design-systems-9e86c7444676)
- [Brad Frost Web Design token Architecture & Nomenclature FigJam](https://bit.ly/design-token-naming)
- [Naming colors in design systems by Jess Sattell](https://adobe.design/stories/design-for-scale/naming-colors-in-design-systems)

### Chapter 4: Building a Token System

- [Guide to variables in Figma](https://help.figma.com/hc/en-us/articles/15339657135383-Guide-to-variables-in-Figma)
- [Salesforce Theo](https://github.com/salesforce-ux/theo)
- [Diez: The Design Token Framework](https://diez.org/)
- [Style Dictionary](https://amzn.github.io/style-dictionary)
- [Figma plans and features](https://help.figma.com/hc/en-us/articles/360040328273-Figma-plans-and-features)
- [Visual Studio Code](https://code.visualstudio.com/)
- [Node.js](https://nodejs.org)
- [npm](https://www.npmjs.com/)
- [Style Dictionary NPM Package](https://www.npmjs.com/package/style-dictionary)
- [Sass](https://sass-lang.com/)
- [Sass NPM Package](https://www.npmjs.com/package/sass)
- [Storybook](https://storybook.js.org/)
- [Storybook NPM Package](https://www.npmjs.com/package/storybook)
- [Free Code Camp: Introduction to Git and GitHub](https://www.freecodecamp.org/news/introduction-to-git-and-github/)
- [Git](https://git-scm.com/)
- [GitHub](https://github.com/)
- [Figma: Overview of Variables, Collections, and Modes](https://help.figma.com/hc/en-us/articles/14506821864087-Overview-of-variables-collections-and-modes#h_01H9V3QSVH2T1EYNXP7RNXZ8MV)
- [Figma: Create and Manage Variables](https://help.figma.com/hc/en-us/articles/15145852043927-Create-and-manage-variables#h_01H32HZB74TE7MJXYBWEBBQWJV)
- [Px vs Rem Codepen by Brad Frost](https://codepen.io/bradfrost/pen/zxYwJRz)
- [Mozilla CSS Values and Units](https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Styling_basics/Values_and_units)
- [Modern Fluid Typography Using CSS Clamp by Adrian Bece](https://www.smashingmagazine.com/2022/01/modern-fluid-typography-css-clamp/)
- [line-height by Sara Cope](https://css-tricks.com/almanac/properties/l/line-height/)
- [Line height playground](https://aresluna.org/line-height-playground)
- [Figma: Create color, text, effect, and layout grid styles](https://help.figma.com/hc/en-us/articles/360038746534-Create-color-text-effect-and-layout-grid-styles)
- [Responsive Typography by Jason Pamental](https://www.oreilly.com/library/view/responsive-typography/9781491907085/)
- [Breakpoint example in Codepen by Brad Frost](https://codepen.io/bradfrost/pen/VYwMBEY?editors=1100)
- [Figma: Modes for variables](https://help.figma.com/hc/en-us/articles/15343816063383-Modes-for-variables)
- [Storybook addon-themes](https://storybook.js.org/addons/@storybook/addon-themes)
- [Design Tokens Manager Figma Plugin](https://www.figma.com/community/plugin/1263743870981744253/design-tokens-manager)
- [Tokens Studio](https://tokens.studio/)
- [Figma REST API](https://www.figma.com/developers/api)
- [Zeroheight Manage Design Tokens](https://zeroheight.com/help/article/manage-design-tokens/)
- [Supernova Design Tokens](https://www.supernova.io/design-tokens)
- [Knapsack Design Tokens Theming](https://www.knapsack.cloud/feature-listing/design-tokens-theming)

### Chapter 5: Publishing A Token System

- [A Design System isn't a Project. It's a Product, Serving Products. by Nathan Curtis](https://medium.com/eightshapes-llc/a-design-system-isn-t-a-project-it-s-a-product-serving-products-74dcfffef935)
- [Interaction Design Foundation: User Centered Design (UCD)](https://www.interaction-design.org/literature/topics/user-centered-design)
- [5 User centered design (UCD) principles you need to know. by Sepideh Yazdi](https://medium.com/@sepidy/5-user-centered-design-ucd-principles-you-need-to-know-f5508c7b8faf)
- [Figma: Hide styles, components, and variables when publishing](https://help.figma.com/hc/en-us/articles/360039238193-Hide-styles-components-and-variables-when-publishing)
- [Figma: Publish a library](https://help.figma.com/hc/en-us/articles/360025508373-Publish-a-library)
- [Creating and publishing scoped public packages](https://docs.npmjs.com/creating-and-publishing-scoped-public-packages)
- [How to Create and Publish an NPM Package - a Step-by-Step Guide by Benjamin Semah](https://www.freecodecamp.org/news/how-to-create-and-publish-your-first-npm-package/)
- [Working with the npm registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-npm-registry)
- [Managing releases in a repository](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository)

### Chapter 6: Adopting Design Tokens

- [Color Theming in WordPress](https://developer.wordpress.org/themes/global-settings-and-styles/settings/color)
- [Color Theming in Drupal](https://www.drupal.org/project/colorpalette)
- [The Design System Ecosystem](https://bradfrost.com/blog/post/the-design-system-ecosystem/)
- [Brad Frost Web Design token Architecture & Nomenclature FigJam](https://bit.ly/design-token-naming)
- [Integrating Design Tokens with Tailwind by Michael Mangialardi](https://www.michaelmang.dev/blog/integrating-design-tokens-with-tailwind)
- [Style Dictionary Defining Custom Transforms](https://styledictionary.com/reference/hooks/transforms/#defining-custom-transforms)
- [The Art of Design System Recipes](https://bradfrost.com/blog/post/the-art-of-design-system-recipes/)
- [Front-of-the-front-end and Back-of-the-front-end web development](https://bradfrost.com/blog/post/front-of-the-front-end-and-back-of-the-front-end-web-development/)

### Chapter 7: Maintaining & Evolving Token Systems

- [A Design System isn't a Project. It's a Product, Serving Products.](https://medium.com/eightshapes-llc/a-design-system-isn-t-a-project-it-s-a-product-serving-products-74dcfffef935)
- [Design System Pilot Project Exercise FigJam](https://www.figma.com/community/file/1440712042208446737)
- [Semantic Versioning](https://semver.org/)
- [Official Stick Reviews](https://www.instagram.com/officialstickreviews)
- [Git GUI Clients](https://git-scm.com/downloads/guis)
- [Atlassian Using Git Branches](https://www.atlassian.com/git/tutorials/using-branches)
- [Learn Git Branching game](https://learngitbranching.js.org/)
- [Branching in Figma](https://www.figma.com/best-practices/branching-in-figma/)
- [Figma Pricing](https://www.figma.com/pricing/)
- [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
- [Vanilla Pattern Workflow Diagram by Yaili de León Persson](https://coggle.it/diagram/V0hkiP976OIbGpy8/t/vanilla-pattern)
- [A Design System Governance Process](https://bradfrost.com/blog/post/a-design-system-governance-process/)
- [Design Token System Governance Process FigJam](https://www.figma.com/community/file/1493733526012952249/design-tokens-systems-governance-process)
- [Master Design System Governance With this One Weird Trick](https://bradfrost.com/blog/post/master-design-system-governance-with-this-one-weird-trick)
- [“The design system isn’t working for me!”](https://bradfrost.com/blog/post/design-system-governance-bugs-design-discrepancies-features-and-recipes/)

### Chapter 8: Advanced Design Tokens

- [Material Theme Builder](https://material-foundation.github.io/material-theme-builder)
- [InsuredMine Color Customization](https://www.insuredmine.com/knowledge-base/color-customization-throughout-the-portal/)
- [Color Customization in WordPress](https://developer.wordpress.org/themes/global-settings-and-styles/settings/color)
- [Color Customization in Drupal](https://www.drupal.org/project/colorpalette)
- [Pattern Variations by Brad Frost](https://bradfrost.com/blog/post/pattern-variations/)
- [Tools in the Basement by Brad Frost](https://bradfrost.com/blog/post/tools-in-the-basement/)
- [Designing for the World: An Introduction to Localization by Spotify Design](https://spotify.design/article/designing-for-the-world-an-introduction-to-localization)
- [Product Localization Tips and Tricks by UX Planet](https://uxplanet.org/product-localization-tips-and-tricks-7dc94b24bc5d)
- [Localization/Internationalization Codepen](https://codepen.io/bradfrost/pen/pvodVMB)
- [Making Logos by Jessica Hische](https://www.jessicahische.is/makinglogos)
- [Defining Fallbacks in the var() Function by MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_cascading_variables/Using_CSS_custom_properties#defining_fallbacks_in_the_var_function)
- [Figma AI](https://www.figma.com/ai)
- [Motiff](https://motiff.com)
- [Uizard](https://uizard.io)
- [Penpot](https://penpot.app)
- [GitHub Copilot](https://github.com/features/copilot)
- [Cursor](https://www.cursor.com)
- [Windsurf](https://windsurf.com/editor)
- [UXPin](https://www.uxpin.com/)
- [builder.io](https://www.builder.io)
- [Anima](https://www.animaapp.com/)
- [ChatGPT](https://chatgpt.com)
- [OpenAI](https://www.openai.com)
- [Claude](https://www.anthropic.com/claude)
- [Gemini](https://www.google.com/gemini)
- [Bolt](https://bolt.new)
- [The Future Is Built on Solid Foundations by Brad Frost](https://bradfrost.com/blog/post/the-future-is-built-on-solid-foundations/)
- [AI and Design Systems by Brad Frost](https://bradfrost.com/blog/post/ai-and-design-systems/)
- [First Came 'Spam'. Now, With A.I., We've Got 'Slop'](https://www.nytimes.com/2024/06/11/style/ai-search-slop.html)
- [Enshittification Wikipedia](https://en.wikipedia.org/wiki/Enshittification)
- [Death to Bullshit](https://deathtobullshit.com/)
- [Sturgeon's Law Wikipedia](https://en.wikipedia.org/wiki/Sturgeon%27s_law)

### More Resources From Brad & Ian

- [All Courses by Brad and Ian](https://bradfrost.com/courses/)
- [Sign up for our newsletter](https://bradfrost.com/newsletter/)
