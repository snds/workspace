---
name: ux-information-architecture
description: >
  Information architecture, navigation system design, and wayfinding for complex enterprise
  applications. Use this skill when working on: navigation structure decisions (sidebar vs.
  top nav vs. hybrid), multi-level hierarchies, role-based access and what different users
  see, multi-product suites and cross-app navigation, breadcrumb and wayfinding design,
  content organization for large feature sets, mental model research and validation (card
  sorting, tree testing), progressive disclosure in navigation, empty states as IA failures,
  and "where does this feature/item live in the product?" questions. Also trigger on:
  "how should I organize the navigation", "is this IA too deep", "users can't find X",
  "should this be a tab or a page", "how do I handle multi-role navigation", or any
  question about the structural organization of a complex product.
---

# UX — Information Architecture

Spoke skill in the `lead-ux-designer` network. Owns navigation system design, IA
structure decisions, wayfinding, and mental model validation for enterprise SaaS.

Does not own: interaction design within a section (→ `ux-interaction-design`),
research method selection for non-IA problems (→ `ux-research-synthesis`), backend
data hierarchy that constrains IA (→ `be-data-modeling`, but surface the constraint here).

---

## Enterprise IA Challenges

Enterprise applications fail on IA in predictable ways. Before proposing a navigation
structure, diagnose which of these is the actual problem.

**Deep feature sets with unclear hierarchy.** Enterprise products accumulate features.
After 5 years, a navigation has 12 top-level items and 3 levels of sub-navigation, each
maintained by a different team. The fix is a principled IA audit against user task
frequency — not adding a search box to compensate for undiscoverable structure.

**Multi-role access.** The admin who configures the system and the end user who operates
it have fundamentally different mental models and task frequencies. A navigation that
exposes all admin functions to end users is not "flexible" — it is overwhelming. A
navigation that hides admin functions from admins is a support ticket. Role-based
navigation filtering is a requirement, not a feature.

**Multi-product suites.** When users navigate between Product A and Product B (same
platform, different apps), the cross-product navigation layer must be designed explicitly.
Session context (which product am I in?), shared elements (user account, notifications),
and product-switching affordances are all IA decisions. Ignoring them creates an experience
where users don't know where they are.

**Vertical-specific terminology.** In PLM, "part" means something specific. In finance,
"account" means something specific. Navigation labels borrowed from generic UX patterns
often fail in domain-specific enterprise contexts because they don't match the user's
mental model. Always validate navigation labels with real domain users.

---

## Navigation Patterns — Selection Criteria

Don't choose a navigation pattern because it's popular. Choose it because it fits the
structural properties of the content. Each pattern makes different tradeoffs.

### Flat navigation (top nav / horizontal)

Best for: ≤7 top-level items, equal-weight sections, broad-and-shallow structures,
marketing sites, and products where users need to switch top-level contexts frequently.

Fails when: the product has more than 7 meaningful top-level sections, when sections have
deep sub-navigation, or when the product is primarily used in a single section per session
(the persistent tab bar costs screen height for no switching benefit).

Enterprise fit: **limited.** Most enterprise products are too deep for flat navigation.
Top nav is appropriate for the primary app-level navigation in a multi-product suite
(the "which product" layer), not for feature-level navigation within a product.

### Hierarchical navigation (sidebar)

Best for: deep structures with 3+ levels, role-based filtering, collapsible sections,
products where users dwell within a section (the sidebar stays visible, reinforcing location).

Variants: persistent visible sidebar (best for frequent navigation), collapsible sidebar
(good when the content area needs full width), icon-only rail (for secondary navigation
or when spatial memory can substitute for labels).

Fails when: the sidebar becomes a list of 40 items with no grouping — this is an IA
failure, not a sidebar failure. Hierarchical nav requires principled grouping.

Enterprise fit: **dominant.** Most enterprise SaaS products use a left sidebar. The
pattern is so established that deviation requires a strong reason.

### Hub-and-spoke

Structure: a dashboard or landing view (hub) with navigation to detail/task pages (spokes).
Users return to the hub between tasks. The hub is the "home base."

Best for: products where the primary use case is "check status → act on something →
return to overview." Separates overview from task completion. Works well for dashboard-
first products where the overview is genuinely useful, not just a placeholder.

Fails when: the hub becomes a required intermediate step between every action — this
creates navigation overhead. If users spend 90% of their time in the spokes, the hub
is friction, not orientation.

Enterprise fit: **strong** for analytics and operational products. Weak for configuration
or data management products where users are "inside" a record, not surveying a landscape.

### Mega menu

Best for: large flat taxonomies where discoverability matters more than depth —
typically content-heavy products with many peer-level categories (e-commerce, documentation
portals, reference databases).

Fails in task-oriented enterprise products: the mega menu works because users are
browsing. Enterprise users are executing tasks — they know where they're going. Mega
menus add pointer area without adding navigational clarity for expert users.

Enterprise fit: **limited.** Appropriate for enterprise documentation portals or large
content libraries. Rarely appropriate for operational products.

### Contextual navigation

Breadcrumbs, tabs within a page, step indicators for multi-step flows, related content
links. These are not primary navigation — they are orientation aids within a primary
navigation pattern.

**Breadcrumbs**: hierarchical path (Home > Products > Product A > Edit), not history.
This distinction is critical: history breadcrumbs ("you came from...") create confusion
in apps where the same object can be reached via multiple paths. Hierarchical breadcrumbs
show location in the content structure, not navigation history.

**Tabs within a page**: appropriate when a single record or object has multiple
organizational views (Details, Related Items, History, Activity). Not appropriate
for switching between top-level application sections — that's what the sidebar is for.

**Step indicators**: for multi-step tasks where the step sequence is fixed and
meaningful. The step indicator must show current step, completed steps, and remaining
steps. It must not be used for workflows that aren't genuinely sequential.

---

## Information Hierarchy Principles

### Primary/secondary/tertiary action hierarchy

Never more than one primary action per screen. The primary action is the one most
users need to take most of the time. Secondary actions are available but visually
subordinate. Tertiary actions (destructive, rarely used, admin-only) are present
but require deliberate discovery.

Anti-pattern: every action in a table row is a primary button. This is not flexibility —
it is refusal to make a design decision.

### Progressive disclosure

Show the minimum until the user demonstrates intent to go deeper. In navigation, this
means: don't expand all sub-navigation on load — let users expand the section they
need. In forms, don't show all fields at once when most users only need 5 of 20. In
record views, surface key fields above the fold; collapse secondary fields into tabs or
expandable sections.

Progressive disclosure is not the same as hiding things. The depth must be reachable
and the path to it must be obvious. "Hidden" behind a disclosure means "visible when
triggered." "Missing" means the user can't find it regardless.

### Chunking: Miller's Law applied

Seven plus or minus two is not a rule about navigation items — it is a model of working
memory load. The practical implication: when a navigation section has more than ~7 items,
group them. When a form has more than ~7 fields in a single section, chunk them with
labeled section dividers. When a table has more than ~7 columns visible at once, consider
whether all columns are necessary or whether some should be secondary/optional.

The grouping structure must reflect actual conceptual relationships, not arbitrary
counts. Seven items that naturally belong together are fine. Seven arbitrary items
grouped to hit the number is not.

### Spatial memory

Users learn where things are. The first few sessions with a product are about learning;
subsequent sessions rely on spatial memory to reduce navigation overhead. Don't move
navigation items without a strong reason. Don't reorganize the sidebar between releases
unless the IA is genuinely broken. The cost of a nav reorganization is paid by every
existing user who must re-learn where things are.

When a navigation reorganization is necessary: communicate it explicitly (in-product
notice, not just release notes), consider providing a "where did X go?" lookup for a
transition period, and accept that user satisfaction metrics will temporarily drop.

---

## Card Sorting and Tree Testing in Enterprise Contexts

These are the two most-used IA validation methods. They answer different questions and
should not be substituted for each other.

### Open card sort

When to use: discovering the user's mental model of a domain they're already familiar
with. Best at the beginning of a new product area or when redesigning an existing
navigation that you suspect doesn't match how users think.

How it works: users group unlabeled cards (each representing a feature or content type)
into categories they name themselves. The categories reveal the user's mental model, not
the designer's.

Enterprise-specific challenge: domain experts have strong, specific mental models.
An engineer using a PLM tool thinks about "parts" and "configurations" and "change
orders" — not "items" and "records" and "workflows." Open card sort in enterprise
reveals the domain vocabulary that navigation labels must match.

Failure mode: running an open card sort with only 5 participants and treating the output
as definitive IA structure. Card sorting is generative — it surfaces hypotheses, not
architecture. Validate with tree testing.

### Closed card sort

When to use: validating whether a proposed IA structure matches user expectations.
After you've drafted a navigation structure, before you build it.

How it works: users sort labeled items into a predefined set of categories. Measures
fit between the proposed structure and user expectations. High agreement = good fit.
Low agreement = the structure doesn't match the mental model.

### Tree testing

When to use: testing the findability of specific content within a proposed navigation
structure. The most reliable pre-build IA validation method.

How it works: users are given tasks ("find the setting that controls X") and navigate
a text-only tree structure (no visual design, no icons). Measures: success rate,
directness (did they go straight there or backtrack), and time. The absence of visual
design is the point — it isolates IA findability from visual design quality.

Run tree testing before major nav redesigns. Run it with a minimum of 20 participants
per task (tree testing is quantitative — small samples are misleading).

Enterprise participant mix: include admin users, power users, and occasional users
separately. Their task sets differ. Their mental models differ. Aggregating them
obscures real role-based IA differences.

---

## Wayfinding in Complex Apps

### Breadcrumbs: hierarchical, not historical

The breadcrumb shows the user's location in the content hierarchy, not the path they
took to get there. This matters because: (1) in enterprise apps, the same record can
be reached via search, navigation, deep link, or related item — history breadcrumbs
would differ across these paths; (2) hierarchical breadcrumbs tell the user where they
are in the structure, which is actionable — they can click up to the parent level.

Format: Home > [Section] > [Subsection] > [Current Item]. The current item is not
a link (you're already there). All parents are links.

Long breadcrumbs: truncate the middle, not the ends. Show the root and the current
item; collapse the middle path with an ellipsis + expandable.

### "You are here" clarity

Active state in navigation must be unambiguous. The current page's link in the sidebar
must look distinctly different from the hover state and the default state. Page titles
must mirror the navigation label — if the sidebar says "Product Configurations" and
the page title says "Config Management," users are disoriented.

Page title is the highest-priority location signal. It must be: visible on load,
specific (not "Dashboard" — "Product Configurations"), and consistent with the
navigation label that led here.

### Empty states as IA failures

If a user arrives at a section of the product and the content is empty, their experience
of that empty state is determined by the IA — did they find the right place to
accomplish their goal, or are they lost?

A good empty state: tells the user what this section is for, tells them why it's
empty, and gives them a clear path to either populate it or go elsewhere. An empty
state that just shows a graphic and "No items yet" has failed to answer the most
important question: "Am I in the right place?"

An empty state with a broken IA is an empty state that says "No items" when the
user expected to find items that are actually elsewhere in the navigation. That's
not an empty state — that's a findability failure.

---

## Anti-Patterns

**The "everything important" nav.** Adding every high-priority feature to the top-level
navigation produces a navigation with 15 items, each claiming equal importance. Priority
must be expressed in hierarchy, not omission. Secondary features belong in sub-navigation,
settings, or contextual panels.

**Organizational structure mirrored in navigation.** The product team is organized by
"Catalog," "Orders," and "Reporting" — so the navigation is organized by "Catalog,"
"Orders," and "Reporting." Users don't care about the team structure. They care about
their tasks. Task-based IA beats org-chart IA.

**Navigation as search compensation.** Adding a global search to compensate for a
broken navigation is not an IA solution — it's a coping mechanism. Search is a
complement to navigation, not a replacement. Users who can't find what they need
via navigation don't automatically succeed via search.

**Consistent navigation for inconsistent content.** Some enterprise products have
sections with fundamentally different workflows (configuration vs. operation vs.
reporting). Forcing them into the same navigation pattern creates cognitive mismatch.
It is acceptable to have different navigation behaviors for different sections if
those sections genuinely require different navigation patterns.

---

## Cross-Links

- `ux-interaction-design` — flow design within a section; form patterns; multi-step workflows
- `ux-research-synthesis` — mental model research methods; participant recruitment for IA research
- `ux-accessibility` — keyboard navigation order; focus management at navigation level; skip links
- `be-data-modeling` — data hierarchy constraints that shape IA decisions (what can be grouped with what)
- `ds-product-analytics` — funnel drop-off, nav path analysis, time-to-task to validate IA decisions
- `pm-discovery-research` — IA decisions informed by user mental models; coordinate on research inputs

---

## References

- Abby Covert — How to Make Sense of Any Mess
- Peter Morville, Louis Rosenfeld — Information Architecture for the Web and Beyond
- Optimal Workshop (tree testing + card sort tooling): https://www.optimalworkshop.com/
- Nielsen Norman Group — Navigation IA articles: https://www.nngroup.com/topic/ia/
