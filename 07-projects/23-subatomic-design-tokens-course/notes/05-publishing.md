---
title: Chapter 5 — Publishing A Token System
course: Subatomic — The Complete Guide To Design Tokens (Brad Frost & Ian Frost)
sections: ["Chapter 5 - Publishing A Token System"]
lessons: 20
status: noted
as-of: 2026-09-23
---

# Chapter 5 — Publishing A Token System

Original notes (not a transcript). Raw transcripts: `<Projects>/subatomic-design-tokens-course/transcripts/05-*`.
Lesson 204 ("Should You Publish Tier 1 Tokens?") ships a mislabelled transcript (a copy of 205); its notes
come from the Wistia caption in `captions/05-*`. Resource links: `files/05-*__notes.html`.
The authors frame this as a light chapter after the Chapter 4 marathon.

## A token system is a product — specifically a library

- Brad dislikes "digital product" as commodity language; his preferred frame is Warhol's Factory
  (tedious, exact work at scale producing creative output) rather than a can of soup.
- Installed software (their example: **Slack**) has a version number, a size, a shape, and named makers.
  Slack is cited for unusually crafted, personality-rich release notes. Versioning, changelogs, and
  release notes are deferred to later chapters.

| | End-user product | Library |
|---|---|---|
| Used by | Customers or internal staff through an interface | Other teams, to build *their* products |
| Nature | The thing people use | Infrastructure / a dependency |
| Release posture | Users mostly ride the latest version | Roll changes out carefully; resist changing things constantly |
| Framing | Project or product | Nathan Curtis: a design system is "a product serving products" |

The authors say this product-vs-library distinction was never explained to them; they learned it by
stumbling into it, and they think it is under-discussed.

## The publishing arc: source → library → consumers

| Stage | Figma | Code |
|---|---|---|
| **Source** (Ch 4 output) | The tokens source file | The tokens repo (JSON source + Style Dictionary) |
| **Library** (this chapter) | A **team library** of variables + relevant styles | Build → package → **publish** to a registry |
| **Consumption** (Ch 6) | Product designers enable the team library in their files | Developers install the package as a dependency and get CSS custom properties (or whatever format they need) |

## Makers vs. users

- **Makers** build and distribute the system; **users** pull it into their work. Different environment,
  skills, responsibilities, and details they sweat.
- Car metaphor: factory specialists vs. drivers who just want to get from A to B (with the Callahan Auto
  running gag from earlier videos: makers as the parts company, users as lovable, inept drivers).
- Many DS teams they've worked with don't grasp the distinction.

## User-centered design, pointed at the token system

- UCD principles (from Sepideh Yazdi's article; also IxDF on UCD): **user focus**, **involvement**
  (talk to them, get feedback), **usability** (easy, efficient, enjoyable), **iteration** (pixels are
  revisable).
- Two audiences: the end users of the org's sites/apps (indirect) and — the **primary** users of a
  token system — the designers and developers who consume it.
- So "good UX for a token system" means an exceptional **designer experience** and **developer
  experience**. The authors spell this out because it usually goes unsaid.

## Should you publish tier 1 tokens?

Metaphor: restaurant kitchen double doors. Tier 1 is the pantry behind the doors — ingredients for the
makers to wire up. Do you let diners walk into the kitchen and cook? Usually not, but there are valid
choose-your-own-adventure cases.

Concretely: in Figma, whether to tick the tier-1 collections in the publish dialog; in code, whether to
expose values like `ds-color-neutral-600` for direct use.

| Pros of publishing tier 1 | Cons |
|---|---|
| More ingredients, flexibility, autonomy for downstream teams | Users can do real damage — **accessibility** above all |
| Makers stop being a bottleneck; users can override, extend, compose | You depend on users knowing and doing the right thing |
| Suits wide-ranging, unknown product sets — **Material Design**, **Tailwind UI** ship smart-default palettes and leave assembly to you | Flexibility is traded against system quality and integrity |
| | More maintenance; future releases become unpredictable because they may collide with users' customizations |

Demo: the Frostd primary button rewired with tier-1 palette colors fails contrast everywhere (checked
with the Figma **Contrast** plugin) while technically still "using the token system." That is the trap.

**Recommendation:** default to *not* publishing tier 1. Do it only with clear, justifiable reasons
("unless you really know what you're doing"). If undecided, start unpublished — adding tier 1 later is
far easier than cleaning up after exposing it.

## Pre-publishing checklist

Treat the release like any product launch: due diligence first, in both design and code.

| # | Check | What it means | How they verify |
|---|---|---|---|
| 1 | **Mapped properly** | Hard to judge by squinting at a variables table or JSON; you need to see results | Pilot projects; a **playground** with every theme, all component variants, and a **kitchen-sink** component (all components and states on one page), plus a responsive-typography playground to flip modes. Doubles as the stakeholder "magic trick" demo. |
| 2 | **Design ↔ code aligned** | Shared tokens (e.g. colors) are exactly equal; known differences are intentional | Automation/sync helps; viewport vs. breakpoint need not be 1:1 (see Ch 4) |
| 3 | **Variables scoped** | Background tokens only on frames/shapes; content tokens only on text; and so on | Ch 4 scoping pass |
| 4 | **Hidden from publishing** | Only tokens meant for users leave the kitchen | Figma variable details panel → **Hide from publishing**; or prefix a collection name with `_` or `.` so it drops out of the publish list (demo: renaming the strawberry tier-1 collection with a leading `.` removed it). Tier-1 colors are already unscoped (Ch 4). Their demo files keep numbered names for teaching clarity. |
| 5 | **Yields accessible results** | Not "are these tokens accessible?" but "do they produce accessible UI?" — a token can pass alone yet fail in context | Contrast plugin across the playground/kitchen sink (sometimes drill into the selection); in code, the **Storybook accessibility addon** (violations / passes / incomplete; goes beyond contrast to functional issues). They say it belongs in every Storybook build. |
| 6 | **Builds cleanly** | JSON valid and wired; no console errors or warnings | Run the build for **every** output format |
| 7 | **Docs current** | Documentation reflects any renames or restructures | Manual review |

## Publishing in Figma

- Figma docs ("Publish a library"): available on all paid plans *at recording time* — they tell you to
  re-check, since plans change.
- Flow: main menu → **Libraries** → publish; the modal lists variable collections (tier 1/2/3), styles
  (typography), and any components.
- **Keep the token library separate from the component library.** Different products with different
  concerns, rhythms, and roadmaps; publish them as separate libraries that work together.
- Safety habit: **untick everything ticked by default**, then opt in deliberately — tier 2, tier 3,
  typography collections, and responsive + non-responsive text styles. Skip tier-1 theme collections
  (vanilla, strawberry, chocolate, dark chocolate) and the demo-page components.
- Label the publish (they used **v0.1 initial release**), publish.
- Consuming (preview of Ch 6): new file → Libraries → team panel → add the library → variables are
  available and theme switching works.

## Publishing in code

- The tokens repo holds source plus Style Dictionary output; the **package ships only what downstream
  developers need**.
- Their sequence (npm, monorepo):
  1. Set every `package.json` in the monorepo to the release version (0.1.0 in the demo).
  2. `npm run build` → a `dist` folder of Style Dictionary output only; source JSON is excluded as
     unnecessary downstream.
  3. Publish to the registry via their publish script; log into an npm account with publish rights.
  4. Cut a **GitHub release**: release branch, auto-generated notes from commits since the last release,
     a **tag** (important for tracking this and future versions), publish, merge to `main` so `main`
     carries the latest release.
- Public vs. private npm package depending on whether the org wants open installs (npm scoped-package
  docs; Benjamin Semah's freeCodeCamp step-by-step; GitHub Packages npm registry; GitHub "Managing
  releases").
- Doesn't have to be manual: e.g. a **GitHub Action** that builds `dist` and publishes on a button press.
- Consuming (preview of Ch 6): `npm install` the package, confirm it in `package.json`, import the
  strawberry theme tokens, style a `.rectangle` with the brand background token → it turns pink.

## Chapter homework

1. Get fluent with Figma team libraries.
2. Get fluent with package managers and how Style Dictionary builds a package for distribution.
3. Find out how **your org** distributes packages internally. npm was used because it's popular; orgs
   vary widely. Ask DevOps now for a package in the formats you need — in their experience this takes
   **weeks or months** at big orgs (hours or days if lucky).
4. Run the pre-publishing checklist against your own token system: what's missing, what needs
   ticking/unticking, is everything synced?

## For Sean

- The seven-item checklist is a ready-made **CI release gate**; almost every row maps to a detector
  (scope audit via Figma MCP `get_variable_defs`, Figma↔code value diff, warnings-as-errors build, axe
  in Storybook CI). Only "mapped properly" stays partly visual — the kitchen-sink/playground is where a
  human eyeballs it.
- Tier-1 privacy has **three independent layers** in a Figma + code pipeline: scoping (pickers),
  hide-from-publishing / `_`/`.` prefix (library), and package exports (code). Pick one Figma mechanism
  as canonical and lint for it, or the layers drift.
- "Yields accessible results" means contrast tests should run on **applied pairings per theme**
  (background × content as components use them), not on swatches. A generated pairing matrix from
  tier-2/tier-3 background/content tokens is the automatable version of their Contrast-plugin pass.
- Separate token and component libraries means **independent versioning**. The demo labels Figma v0.1
  and npm 0.1.0 in step; the course shows this but doesn't state it as a rule — worth deciding whether
  your pipeline enforces lockstep.
- The DevOps lead-time warning is the practical blocker: start registry/package provisioning before the
  system is "done."

## Mechanizable rules

1. The published Figma token library enables **no tier-1 collection** unless a documented exception
   flag exists for it (default: unpublished).
2. Every tier-1 variable is either marked hide-from-publishing or lives in a collection whose name starts
   with `_` or `.`.
3. Every tier-1 variable has an empty scope list.
4. Tier-2 `background` color variables are scoped only to frame/shape fills; tier-2 `content` color
   variables are scoped only to text (any other scope must be on a documented allowlist).
5. The token library's publish set contains **zero components**; components ship in a separate library.
6. No demo/playground-only components or collections appear in the published library.
7. For every token shared between Figma and code, resolved values match per theme/mode; mismatches are
   allowed only for names on the documented divergence list (e.g. viewport vs. breakpoint).
8. The token build exits 0 with **zero errors and zero warnings** for every configured output format.
9. The published package contains only build output (`dist`); no source token JSON appears in
   `npm pack --dry-run`.
10. All `package.json` files in the tokens monorepo carry the same release version before publish.
11. Every package publish has a matching git tag and GitHub release (notes generated from commits since
    the previous tag), and that release is merged into `main`.
12. Before publish, every theme's playground/kitchen-sink stories pass the Storybook a11y (axe) check
    with **zero color-contrast violations**.
13. A change that adds, renames, or removes a published token must include a documentation change in the
    same release.
14. The publish job (Figma library and npm package) is blocked unless rules 1–13 pass — the
    pre-publishing checklist as a required gate.
