---
title: Chapter 7 — Maintaining & Evolving Token Systems
course: Subatomic — The Complete Guide To Design Tokens (Brad Frost & Ian Frost)
sections: ["Chapter 7 - Maintaining & Evolving Token Systems"]
lessons: 31
status: noted
as-of: 2026-09-23
---

# Chapter 7 — Maintaining & Evolving Token Systems

Original notes (not a transcript). Raw transcripts: `<Projects>/subatomic-design-tokens-course/transcripts/07-*`.
Sources: 31 transcripts (lessons 290–320). All are distinct, so no caption substitution was needed.
Resource links: `files/07-*__notes.html`. The chapter slide PDF (249 pages) could not be rendered here,
so the governance workflow below is taken from the narration of lesson 7.26.

Framing: Chapters 4–6 covered the mechanics. This chapter covers the people. The authors argue that a
system can have every asset and every doc and still fail if the relationships and human processes are
weak.

## A token system is a product with a roadmap

Nathan Curtis (again): a design system is a product that serves other products. So it has a lifecycle,
which the authors split into four phases. Phase 4 is optional.

| Phase | Name | Goal | Exit state | Maker posture |
|---|---|---|---|---|
| **1** | Foundation + initial pilot | An MVP architecture, validated by building and shipping a real product. It may be only a screen or three, but it has to be **in production**. | Architecture in place; a **0.x** library published in Figma and as a package; one pilot consuming it in production | Makers and users work as **one team** |
| **2** | Verify via additional pilot(s) | Reach a **v1** architecture, validated in another production product. This is where the ROI starts to show. | **1.0** released; the first pilot migrated onto it | Still one joint team per pilot |
| **3** | Evolve & extend | Cover more use cases (modes, product families, platforms) and build the processes to maintain the system long term | Ongoing. For **most orgs this is the final form** | Makers become **maintainers**; a dedicated DS team; governance formalized; customer support |
| **4** *(optional)* | Self-service | Non-system people create their own themes | A wizard plus a czar review gate | Czars act as gatekeepers, not producers |

## Phase 1 — Foundation and the first pilot

### Team: roles, not headcount

| Side | Role | Owns |
|---|---|---|
| Maker | **Token czar, design** | Keeper of the Figma token library; ultimately responsible for it (per the course, likely *you*) |
| Maker | **Token czar, code** | Keeper of the code tokens |
| Maker | DS design owner / architect | The design side of the whole DS effort: tokens, components, everything else |
| Maker | DS technical architect | Tech stack, architecture, naming conventions |
| Maker *(optional)* | Extra designers, developers, a project manager | Production help |
| User | **Product team**: PO, PM, designers, developers, QA, content… | Building and shipping the product (homepage, checkout, PDP, however the org slices its teams) |

- The czar and architect roles are often the same person. The authors stress they are describing
  **roles**, not people.
- Warning about too many cooks: the MVP team should be **small, scrappy, smart and autonomous**. Don't
  bring dozens of people to it.

### The virtuous cycle, and atomic design as the through-line

- The system shapes what products can build, and the products shape what goes into the system. This
  loop has to exist **from day one**. The authors have seen many teams build a system on their own and
  then wonder why no product uses it well.
- Atomic design is the tool for showing that loop: atoms → molecules → organisms → templates → pages.
  Their worked example is Instagram's app broken into icons, images and text nodes. Tokens are the
  **subatomic** layer below atoms. Wiring tokens into the atomic stack shows the path from tokens to
  real screens and back. The authors call it a **continuum, not a step-by-step process**. (They sell a
  separate atomic design course.)

### Pilot projects: go for the quick win

- Systems people want to power the whole landscape at once. The answer is: not yet. Start with a small
  win the team can celebrate.
- Dan Mall's analogy: a product pilot works like a TV pilot. It tests the concept before you invest in
  the whole series, and it battle-tests design and code.

**Pilot selection criteria**

| Criterion | Good sign | Bad sign |
|---|---|---|
| **Timing** | Committed work that **hasn't started yet** (the sweet spot) | Already underway (the train has left the station), or hypothetical |
| **Yield** | Produces the components and tokens the architecture needs | Yields little reusable system |
| **Scope** | Achievable fast; possibly a *slice* of a big app | Redesigning the whole flagship enterprise app |
| **Technical feasibility & independence** | A streamlined front end and token layer | Backend quicksand. *Hedge:* big refactors or overhauls are sometimes exactly the right moment |
| **People** | Enthusiastic, eager, willing guinea pigs who will cheer afterwards | The most skeptical team. You'll spend your time persuading them instead of building |
| **Showcase** | A win you can hold up to the rest of the org | — |

**Examples from their consulting work**

- **United Airlines, Atmos DS:** a lift-and-shift of the existing *My Trips* page into the new look and a
  new tech stack, with no new design work. It yielded core components (tabs, data tables, accordions)
  that were later rolled out across united.com.
- **Caterpillar, Blocks DS:** Blocks already existed in several formats. The authors added a token
  system plus web components and validated them on **parts.cat.com**, a heavy-machinery parts
  e-commerce site.

**MVP discipline:** don't build the most feature-rich door. Build for the use cases in front of the
product team. Teams that open the floodgates too early get pulled in many directions, burn out, and
never finish the foundation.

### Finding pilots

- Product teams won't wait in the station until the system is ready. Accept that some work will slip
  through the cracks. You can adopt incrementally later.
- Ask what is happening across the org and which effort you can attach to. Frame it both ways: how can
  makers speed up users, and how can users help build the MVP?
- Pilots won't fall into your lap. **Go out, sell, and offer your services.** Screen candidates against
  the criteria, then agree a plan of attack and timing with them.
- Resource: Brad's **"Design System Pilot Project Exercise" FigJam**, for identifying and scoring
  candidates, adding notes, next steps, and people to talk to.

### Starting points differ

- It might be a fresh Lego kit with numbered bags, or it might be Legos all over the floor: broken,
  half-built and patched systems plus work already in flight.
- Choosing between **extending an existing system, starting over, or cherry-picking** from the old one
  is a judgment call; the authors say there is no right or wrong answer. Makers and users make the call
  **together**, and they also settle roles: who does what, where, and when.

### Maker ↔ user collaboration

- **Do actual work together.** Meetings and planning sessions don't count. The authors say this happens
  far too rarely.
- Prefer ongoing, ambient contact: quick video calls, shared videos and assets, comments on each
  other's work. Everyone should be in the mix, not just the system designer and the product designer.
- The **product team shares its context** (the nuances of the product). The **makers share systems
  thinking**. Compromise, leave your ego at the door, and keep a shared vision.
- Division of labour: makers build the token architecture and plumbing. Users implement it *on top of*
  their real work: screens, flows, personas, caching, validation, routing.
- Frostd example: the new strawberry product launch needs a homepage, which becomes pilot #1.
- **Early on, work in the same file.** The czars edit variables while the product designer mocks up
  comps elsewhere in the same Figma file. Fast, scrappy and co-located beats separate and formal at
  this stage.
- **Think globally, act locally.** You ship for one use case (the strawberry landing page), but you keep
  asking how each token or component would scale. Everything beyond the pilot is hypothetical.

### Phase 1 best practices

- **Build the vanilla theme anyway.** It gives an x-ray view of the architecture even when only one
  theme ships.
- Think ahead to known future themes (chocolate) but don't build them yet.
- **Early: maximize collaboration** (shared environment). **Once things settle: split** into separate
  source files and environments and stand up the Chapter 5/6 pipeline.
- Publish a **0.1 (0.x)** release. The leading zero signals the system is still in flight and not yet stable. The pilot team pulls
  the team library into production files and the package into production code.
- Token work runs on its **own track**. It can be done or settled while backend integration and the
  rest of the product work continue.

## Phase 2 — Verify with another pilot, reach 1.0

### Semantic versioning

SemVer is long-standing developer practice. The authors note designers have only started to need it in
the last couple of years.

| Part | Meaning | Token-system example / note |
|---|---|---|
| **Patch** (x.y.**Z**) | Bug fixes or optimizations, nothing breaking | *In the authors' experience,* patches are uncommon for token systems. They matter more for components with moving parts (accordions, modals) |
| **Minor** (x.**Y**.z) | New features, new tokens, non-breaking tweaks | Adding tertiary button tokens. It's additive because they didn't exist before |
| **Major** (**X**.y.z) | Breaking changes that need consumers' attention | Renaming `primary`/`secondary` to new language because people found it confusing |
| **0.x** | Emerging. Expect bugs | The phase 1 release |
| **1.0** | Stable. You should be able to pull it in without it breaking | Goal of phase 2 |

### Libraries must be stable, so branch

- Scenario: pilot #2 is the chocolate site's **checkout flow** (for the demo, Frostd runs separate
  strawberry and chocolate sites). v0.1 has no chocolate theme yet.
- Anti-pattern: someone (the authors say, a little sheepishly, usually designers) edits the main library
  file directly and breaks pilot #1 without warning. Brad's gags: *Cousin Eddie* makes the mess and
  *Patrick* is the confused victim.
- Principle: **products need stable libraries.** Frequent changes, and breaking changes above all, frustrate
  adopters and **erode trust**. Make progress in a careful, deliberate, controlled way.
- Model: **`main` = the latest stable release**. A **`develop`** branch (a common name; there are many
  conventions) is where work moves forward, with feature branches off it.

| | Code | Figma |
|---|---|---|
| Main | The tokens repo's `main` (holds v0.1) | The token source file (holds v0.1) |
| Branch | `git checkout -b feature/create-chocolate-theme` (`git branch` creates but doesn't switch; `git switch` is the newer equivalent) | Figma's **branching** feature. *At recording time* it was limited to Organization/Enterprise plans, so check current pricing |
| No-feature fallback | — | **Duplicate the token library file**, work there, then bring the changes back into main. The authors admit it's not ideal, but it works |
| Tools | CLI, or a GUI such as **Git Tower** (Brad and Ian both use it). Learn from Atlassian's branching tutorial and the *Learn Git Branching* game | — |

Because Figma branching is weaker than git, the authors stress **coordinating new token work and
library releases between design and code**.

### Doing the work, and the changelog

- Repeat the phase 1 loop: atomic design, pilot screens, wiring, and switching between chocolate,
  strawberry and vanilla to check both the system and the product requirements.
- Most work is **additive**, but this is **the moment to fix brittle, badly named or wrongly structured
  parts** of the MVP. Only one product consumes it, and updating one product beats updating 12 or 20
  later. Don't dodge hard calls.
- Keep a **changelog** (they recommend *Keep a Changelog*): a record of what each release added,
  removed or modified. Their example:
  - **v0.1:** initial architecture, strawberry theme, vanilla theme.
  - **v1.0:** chocolate theme, tertiary button tokens, a tweak to strawberry brand pink (possibly
    feedback from pilot #1).
- It becomes more valuable as the library supports more products.

### Release 1.0, then migrate pilot #1

1. Publish 1.0 using the Chapter 5 process. Pilot #2 consumes it using the Chapter 6 process.
2. Now two versions are in production (pilot #1 on 0.1, pilot #2 on 1.0). The authors call this a
   pivotal moment.
3. **Move pilot #1 onto 1.0 right away.** The effort depends on what changed between versions. Hopefully
   it's mostly additive, but breaking changes are possible.
4. Handle breaking changes through collaboration. The makers reach out, list what changed and what the
   team must do, and guide them through it (white-glove treatment). **Rip the band-aid off.** Otherwise
   workarounds build up around 0.x's weak spots.
5. In the **0.x days, changes can be fast and loose.** Iterating on the architecture is natural. Make
   architectural changes sooner rather than later.

### Coordinated versions for tokens and components

- The token system and the component system are separate products, but the authors recommend
  **releasing them together under the same version number**. Cut a release of both even if one hasn't
  changed. If tokens are at 1.3, components are at 1.3.
- Why: reliability and maintainability. With per-package or per-component versions (accordion on one
  number, button on another, icons on a third) it's hard to say which combinations work together.
  Matching versions state that tokens 1.3 and components 1.3 are compatible.
- *Hedge:* they call it partly an art form that depends on context. It is their recommendation after
  seeing it done many ways.

### Choosing the second pilot

- Use the phase 1 criteria, plus:
  - **Timing:** it should follow **hot on the heels** of pilot #1. Don't start the first two at the same
    time, and don't leave a long gap. Stack quick wins.
  - **Advance the core use case.** If the system exists for multi-brand, pilot #2 should add a brand
    theme. Prioritize that over dark mode or multi-platform.
- Reaching 1.0 may take **one, two or three** pilots in phase 2.
- 1.0 means **stable, not perfect or comprehensive**: no major bugs, experimental features or rough
  edges when a team pulls in the library or package. Nathan Curtis: "a 1.0 designation comes with
  commitment". Your freewheeling days are over. Celebrate the milestone.

## Phase 3 — Extend, and switch to service

### Third pilot: widen the scope

- Now that 1.0 is solid, you can take on a use case the system hasn't covered yet. More brand themes are
  also fine.
- Frostd example: a **dark chocolate enterprise customer dashboard**. It covers two use cases at once:
  color modes (dark mode) and a new product family (an enterprise app next to the marketing homepage).
- Good news: you're over the hump. Extending the system is quirky (covered in Chapter 8), but the
  authors say it usually takes much less effort than standing up the architecture did.
- The long-term aim is for the token system and DS to power the org's whole digital landscape.

### Shifting roles: from making to maintaining and serving

- Makers and users now **separate into distinct roles**. Makers become **makers and maintainers** of
  infrastructure that at least two production products depend on.
- Recommendation: a **core design system team, including the token czars**, should be in place by now,
  or close to it.
- A **cross-fade** happens that catches many teams off guard. Production work shrinks and support/service
  work grows. Designers and developers who are used to making things feel lost. (Brad's gags: a
  *Talladega Nights* clip about not knowing what to do with your hands, then Steve Ballmer's
  "developers" chant as the model of enthusiasm for your users.)
- Brad draws on 12 years of doing this work full time. The job is really **helping people**: making
  other designers' and developers' work less frustrating, slow and tedious. He calls it deeply
  satisfying, and the new skills are worth building. Their success is your success.

### Governance: the gist

- Lineage: **Yaili de León Persson's** *Vanilla* pattern decision tree at **Canonical** (Brad believes she
  is now at GitHub). Brad iterated on it for years in a component-focused form. For this course they made
  a **token-specific** governance diagram, the **"Design Tokens Systems Governance Process" FigJam**,
  free to adapt.
- The gist: teams use the system. When something doesn't fit, **they talk** with the czars. Together
  they decide whether new work is needed and who does it. If it's token-system work, it ships in a new
  release and the team pulls it in.

### Governance workflow, in full (lesson 7.26)

1. **Use.** The product team designs and builds with the token system. The brand, visual, UX and
   accessibility practices baked into it are what attract teams.
2. **Check.** Do the tokens work, look right and pass accessibility? **Yes** → wire them up, ship, and
   move on. That's the promise working.
3. **No / not sure / confused** → the product team and the czars **talk**.
   - Prerequisite: product teams must **know the czars exist and how to reach them**. Many orgs have a
     system that product teams can't see. Make the contact route "abundantly, obnoxiously clear".
   - Be proactive. Don't assume silence means success. Check in with teams you know are using the
     system.
4. **Conversation.** The team explains what they're trying to do: unsure which token to wire, or
   unclear on the difference between *subtle* and *strong*.
   - **Education outcome:** usually the system is fine and the team just needs a nudge toward the right
     token (language is arbitrary; see Chapter 3). Brad says this is where *millions* get saved, because
     no tickets or workflow are needed. Afterwards, **revisit the docs** so the next person doesn't have
     to ask.
5. **If both sides agree new work is needed**, classify it:

   | Nature | Examples | Route |
   |---|---|---|
   | **Bug in the token library** | Incorrect mapping; Figma library ≠ code library; accessibility issues; inconsistent names; missing or incomplete docs | **Five-alarm fire.** Drop everything, top of the backlog, fix and release. Bugs left sitting erode trust |
   | **New or modified token** | The team can't find what it needs, or thinks an existing token is wrong | Q1: **core system, or recipe/product layer?** Temporary or campaign work (e.g. a **Valentine's Day theme**) belongs at the recipe/product layer. The team uses overrides and owns it in their backlog. Q2 (core only): **can it land before the product's deadline without lowering system quality?** **No** → the team proceeds locally, it goes on the token backlog, and the czars follow up later. **Yes** (common for small tweaks such as a wrong hex value; tier-1 values can be handled more loosely because they aren't shipped) → squeeze it in, track it on the token backlog, and release |
   | **Visual discrepancy** | A developer files an urgent bug because the build doesn't match the comp | Q1: **is the mismatch between the Figma token library and the code token library?** → then it's a token bug (fast path). *In the authors' experience* it's usually **product-level**. Q2: **is the deviation deliberate and justifiable?** **No** (e.g. a designer detached instances to make purple buttons because they like purple) → the product team updates the design to conform. **Yes** (e.g. purple buttons in an **A/B test**) → the team ships it, and the czars log it for research and follow-up. If it converts, it may justify evolving the theme |

6. **System work.** Make the additions and changes in Figma variables *and* in code.
7. **Test.** This is core infrastructure. Wire the change into the DS component library and any relevant
   recipe or product libraries. Check that it works, looks right and is accessible. Check responsive
   behaviour where relevant. Run **visual regression** (e.g. **Chromatic**), add **stories** for the
   component states, and do **code review and design review**. This can be light for a hex tweak.
8. **Validate with the requesting team** that the change is what they asked for. Iterate until they agree.
9. **Document.** Update the Figma library, **Storybook** and the reference website.
10. **Release.** Merge `develop` → `main`, merge the Figma branch or duplicate file into the main file,
    **bump the version**, update the **changelog**, and **announce** it on the appropriate Slack/Teams
    channels.
11. **Adopt.** The product team pulls the new version, wires it up and checks it. **Broken** → the bug
    path. **Works** → launch.

**Scale reassurance:** about a third of the workflow is a few minutes of Slack/Teams chat or a quick
call. The whole thing takes **hours to a day or two**, not months. Product teams **don't need to learn
the workflow**. They only need to know where to go (the friendly neighbourhood token czars).
Brad's "one weird trick" is **just talk**. Related articles: *A Design System Governance Process*,
*Master Design System Governance With This One Weird Trick*, and *"The design system isn't working for
me!"* (bugs, design discrepancies, features, recipes).

### Phase 3 best practices

- Establish a dedicated systems team if you haven't already. Multiple production products now rely on
  the system.
- Lean into the **customer-support model** alongside production work. Brad's point: you are more than a
  drawer of rectangles.
- **Formalize governance** so everyone knows what happens with bugs, questions and change requests. Take
  the template and adapt it.
- **For most orgs, phase 3 is the final form.** Typical examples: a handful of themes, a couple of brands
  each with dark mode, marketing plus enterprise products, several JS frameworks, plus iOS and Android.

## Phase 4 (optional) — Self-service theming

- **Who needs it:** very large multi-brand orgs where one pilot after another can't scale and czars would
  be up all night producing themes. Examples: **Unilever**, **Comcast** (a client of theirs; many brands
  and verticals), and **Pfizer** (hundreds of brands).
- **The idea:** a sturdy phase 1–3 architecture turns theming into the Chapter 2 mix-and-match game, a
  fill-in-the-blanks, Mad Libs-style exercise driven by brand guidelines (colors, typography…).
- **Interface:** no JSON, and often not even Figma, for non-technical users. The authors have helped
  orgs build **theme wizards**: a Clippy-style guide or a CMS-like, paint-by-numbers form, plus a
  **playground** that previews the theme on real UI so the author isn't working blind. They skip the
  technical details.
- **Flow:**
  1. A brand manager, agency partner, product owner or similar (non-designer, non-developer, but fluent
     in the brand) uses the wizard.
  2. The output is a **draft theme**.
  3. The **token czars review it** for accessibility, brand fit and sturdiness, going back and forth as
     needed.
  4. Once it satisfies the czars, **they bring it into the system**.
- **Principle:** theme *creation* is democratized, but *integrity* is not. The czars remain the
  gatekeepers and stay responsible.

## Chapter homework

1. Which phase is your org at: 1, 2, 3, or something else?
2. What do you need to reach the next phase? Which **products** (pilot opportunities) and which
   **people** (enthusiastic partners) can get you there?
3. Take the governance diagram and **rip it up and adapt it** to your org's people, tools and processes.
4. Reflect on how much you can help other people, both as a systems person and in general. The authors
   say practitioners underrate what they know.

## For Sean

- **This settles the Chapter 5 open question on lockstep versioning.** The authors do recommend
  coordinated version numbers for tokens and components, cutting both even when one is unchanged. In a
  Figma + npm pipeline that means three artifacts carry the same version: the Figma library publish
  label, the tokens package, and the components package. Decide once and enforce it in CI, or the
  compatibility promise is empty.
- **The governance tree maps directly onto an issue template.** Intake type (question / new-or-modified
  token / visual discrepancy / bug) plus two required branch fields decide the route: *layer*
  (core vs recipe/product) and *discrepancy source* (Figma-lib↔code-lib vs product-level, and if
  product-level, the justification). The czar's triage becomes filling fields, not tribal knowledge.
- **The SemVer bump can mostly be computed from a token diff**: removed or renamed published token →
  major; added → minor. The course is silent on *value* changes (its v1.0 changelog includes a brand-pink
  tweak without calling it breaking). My suggestion: treat tier-2/3 value changes as minor only with a
  visual-regression artifact attached, and leave tier-1-only changes to czar judgment.
- **The Figma branching gap is the weak link in PR review.** Without Org/Enterprise branching the Figma
  "branch" is a duplicate file with no diff. Make the **code PR the merge point of record**: the
  Figma-side change is exported and diffed in the same PR, then the library publish happens only after
  merge, labelled with the PR's release version.
- **The phase framing gives a hiring and staffing argument.** Phase 3 needs a dedicated team whose job is
  mostly service (answering, educating, triaging), not production. Plan czar capacity around support
  load and docs updates driven by questions, not just new tokens.
- **Classify discrepancy tickets before touching the system.** An automated Figma↔code value diff
  answers Q1 of the discrepancy branch instantly. Anything that diff doesn't flag is a product-level
  question, not a token bug.

## Mechanizable rules

1. Every token release (npm package tag and Figma library publish description) carries a SemVer
   `MAJOR.MINOR.PATCH` version, and the two match for the same release.
2. The tokens package and the components package are published with **identical version numbers**. A
   release of either bumps and publishes both, even if one has no changes.
3. At ≥1.0.0, a release that removes or renames any published token must bump MAJOR. A release that adds
   published tokens must bump at least MINOR. A PATCH release may not add, remove or rename published
   tokens.
4. `1.0.0` may not be tagged until at least two distinct production consumers are recorded against the
   system (phase 2 exit). Before that, versions stay `0.x`.
5. The release job fails if `CHANGELOG.md` has no entry under the version being published. Entries use
   Keep a Changelog sections (Added / Changed / Removed / Fixed).
6. Every MAJOR release includes migration notes (what changed + consumer action). CI opens a migration
   issue for each registered consumer still pinned to an older major.
7. `main` is branch-protected. It only receives merges from `develop`/release branches at release time,
   and `main` HEAD always equals the latest release tag. Feature work happens on `feature/*` branches.
8. Token source directories have CODEOWNERS entries for the design token czar and the code token czar.
   Merges require approval from both (design review + code review).
9. A token-change PR cannot merge unless: visual regression (e.g. Chromatic) ran against the component
   library in every theme with diffs approved; stories exist for affected component states; the
   accessibility check passes; and a requester sign-off link is present.
10. A token-change PR that adds, renames or changes a published token also updates the docs surfaces
    (Figma library docs, Storybook, reference site) in the same release.
11. Each release triggers an automated announcement to the designated Slack/Teams channel, containing
    the version and its changelog entry.
12. The governance issue template requires a type from {question, new/modified token, visual discrepancy,
    bug}. *New/modified token* requires a `layer` field {core, recipe/product}. *Visual discrepancy*
    requires a `source` field {Figma-lib vs code-lib, product-level} and, if product-level, a
    `justification` field.
13. Issues typed or labelled *token bug* (incorrect mapping, Figma↔code mismatch, accessibility failure,
    inconsistent naming, missing docs) are auto-assigned top priority and tracked against an
    org-defined SLA. The course gives no number.
14. Any Figma↔code resolved-value mismatch found by the sync diff automatically opens a *token bug*
    issue.
15. Requests with `layer: recipe/product` (e.g. campaign or holiday themes) may not modify core token
    source directories.
16. Issues closed as *question/education* require either a linked documentation change or an explicit
    "docs already cover this" flag.
17. The token package README / docs site contains a support section naming the czars and a contact
    channel. A docs check fails if it's missing.
18. Any new theme, including self-service or wizard-generated drafts, merges only with czar approval and
    a passing contrast/accessibility check across the playground.
19. The pilot-candidate intake form requires a score for each criterion: timing (committed but not
    started), token/component yield, scope, technical feasibility, and team enthusiasm.
