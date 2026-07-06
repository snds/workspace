# Team Practices and Decisions

_Location: `01-frameworks/team-practices-and-decisions.md`_
_Maintainer: Sean Sands_
_Last updated: 2026-07-05_

A layered reference for code-level craft and design-engineering conventions, organized so that *which* team I'm on and *when* a practice was adopted are both surfaceable. Read by the Last-Mile Craft Framework (section: Code-level craft) as the authoritative source for team-specific conventions that override or extend the general best-practices baseline.

This is a living document. Unlike the five frameworks, it changes frequently — when team composition shifts, when a convention gets revisited, when historical context becomes newly relevant.

---

## How this document is organized

Four layers, structured by *whose rules apply and when*:

1. **Active layer — current team non-negotiables.** What my current team has explicitly decided. Authoritative for current work. Overrides baseline when they differ.
2. **Best practices baseline.** The portable, team-agnostic defaults — what "good" looks like absent team context. The fallback when no active-layer override exists.
3. **Historical archive.** Previous teams' conventions, scoped by team and date range. Not binding on current work, but useful for context when reading old code, migrating, or understanding why existing patterns exist.
4. **Cross-team patterns.** Conventions that have proven durable across multiple teams — candidates for the baseline if they show up in enough places, but tracked separately until then.

Loading order for the LLM: active layer first (it's the authoritative overlay), baseline second (fills gaps), historical third (context only), cross-team fourth (signal).

---

## 1. Active layer — current team non-negotiables

_Team: [current team name]. Effective from: [YYYY-MM-DD]. Active maintainer: Sean._

### Component API

- [e.g. "All new components use shadcn/ui + Radix UI Primitives as the headless foundation."]
- [e.g. "Variant props use string unions, not enums."]
- [Fill in as conventions get adopted.]

### Token usage

- [e.g. "Tokens consumed through CSS custom properties, not theme objects."]
- [e.g. "No raw hex values anywhere in component styles — violations fail PR review."]

### Accessibility

- [e.g. "Focus-visible styling required on every interactive component."]
- [e.g. "ARIA attributes mandatory in the component itself; consumer props can't be the only way to enable them."]

### Documentation

- [e.g. "Every component ships with Storybook stories for each state and variant combination that isn't combinatorial-explosion territory."]
- [e.g. "Component description fields in Figma must match the README description in the code package."]

### Build / versioning

- [e.g. "Semver applied strictly. Breaking changes require a migration note in CHANGELOG."]
- [e.g. "No mixing of `npm`/`yarn`/`pnpm` across packages in the monorepo."]

### Review / process

- [e.g. "Design review before any PR that changes visual output ships."]
- [e.g. "Accessibility review before any PR that changes interaction behavior ships."]
- [e.g. "Tickets link to design intent (Figma frame URL) and acceptance criteria."]

### Testing

- [e.g. "Behavioral tests required on every component. Visual regression required on every exported component."]

### What this team has decided is NOT a concern

_Legitimate non-goals to prevent scope creep._

- [e.g. "We don't support IE11. Don't write polyfills for it."]
- [e.g. "We don't optimize for sub-16ms render on low-end mobile in this product context."]

---

## 2. Best practices baseline

The portable default for design-engineered work. Applies absent active-layer override. These are the general-industry best practices the Last-Mile Craft Framework references when no team-specific guidance exists.

### Component API

- Props are the public API. Minimize the surface: prefer composition (children, render props) over configuration (dozens of boolean props).
- TypeScript types export-able. JSDoc on non-obvious props.
- Figma component properties ↔ React props 1:1 where possible.
- Variant names and values consistent across the library.
- No variants for state where tokens can express the change via modes.

### Architecture / extending upstream

_Stack-agnostic. Applies to any language, framework, or vendor — the mechanism matters, not the tools._

- Separation of concerns is the default, not the exception. Before editing, ask **which layer owns this concern.** Behavior, appearance, and product ergonomics are three different owners; a change belongs to exactly one of them.
- When building on third-party or generated code, keep a **regenerable boundary**: the upstream/vendored layer stays unmodified so updates flow in cleanly. Customization lives in adjacent layers, never in the layer you don't own.
- Three roles, non-overlapping:
  - **Upstream / base** — owns behavior and structure. Regenerable; never hand-edited.
  - **Presentation / theme** — owns appearance. Applied through the upstream layer's stable extension points (variables, slots, hooks, data contracts), never by editing it.
  - **Composition / wrapper** — owns product ergonomics: new capabilities, defaults, and the consumer-facing API. Additive; composes the base, never edits it. Consumers depend on this layer, not the base.
- Route by owner: appearance tweak → presentation; new capability/variant/prop → composition; behavior bug → fix upstream or regenerate, don't patch the base.
- Protect the seam with a **divergence check** (regenerate-and-diff, or equivalent) so the boundary can't silently rot. A failure means "this change is in the wrong layer," not "silence the check."
- Prefer this to the alternatives: **forking** upstream accrues permanent merge debt; **override stacks** (specificity hacks, monkey-patches) break the moment upstream internals shift. Abstraction at stable contracts is what lets the system scale and absorb improvements without rework.

### Token usage

- Three-tier model: global → semantic → component.
- Semantic tokens used where semantics live. Components don't reach past semantic into global except for documented exceptions.
- No raw values at the component authoring layer.
- Exceptions documented explicitly, not tolerated silently.

### Iconography

- Default to **Google Material Symbols** for app/product UI icons — never hand-roll SVG icon paths for standard iconography. (Bespoke variable-icon-font work — e.g. CentricSymbols — is a distinct craft exercise, not the default for app product work; see Last-Mile Craft Framework §Icon and imagery systems.)
- **Self-host** the variable font (bundle it into the build; no runtime CDN) so the surface works offline. Expose **one** reusable `Icon` component that owns the variable axes (`opsz`, `wght`, `FILL`, `GRAD`), tracks optical size to the rendered size, and inherits `currentColor`; consumers reach for symbols by name.
- Icon-to-text alignment (cap height, x-height, baseline) is explicit, per the craft framework.
- Hit targets ≥ 24×24px (WCAG 2.2 minimum); ≥ 44×44px for touch-primary contexts.
- Focus indicators visible and distinct from hover.
- Focus order logical. Keyboard navigation complete.
- Screen reader experience authored, not default.
- Cognitive accessibility considered — plain language, predictable patterns, recoverable errors.

### Documentation

- Every component has a description, a usage note, and a "when not to use" note.
- Usage examples cover common cases, not every possible state.
- Component documentation serves designers and developers equally.

### Build / versioning

- Semver applied honestly. Breaking changes trigger major bump.
- Public API stable. Internal utilities stay internal.
- Build is tree-shakable and predictable.
- No magic numbers, no hardcoded URLs in library code.

### Review / process

- Atomic commits. Clear messages. Reviewable diffs.
- Tickets have scope, acceptance criteria, and design intent.
- No TODO hacks in production code. No commented-out blocks.

### Repository & release hygiene

Applies to **every session tied to a git repo** and any work that touches code.
Operating model is solo-maintainer: Sean + Claude, with Claude maintaining the repo
through prompt confirmations. Because there are no other collaborators, `main` is kept
continuously clean rather than via long-lived branches.

- **Nothing falls behind `main`.** Start work from an up-to-date `main`. If the working
  branch is behind, reconcile (rebase or merge `main` in) *before* continuing — don't
  build on a stale base.
- **End-of-session ritual (substantial sessions).** When a substantial piece of work is
  done: commit (atomic, conventional message + the agreed co-author trailer) → push →
  open/refresh the PR into `main` → run the collision check → **merge to `main` after a
  single confirmation** (the same confirm-gate as deploy). Don't strand substantial work
  on a branch; `main` is the source of truth.
- **Collision check before merging.** Trial-merge for conflicts (`git merge-tree`),
  scan other open branches for anything behind `main` or colliding, and **surface every
  issue that needs human intervention** rather than papering over it.
- **Deploy / publish is gated.** Any outward-facing deploy or publish requires explicit
  per-instance confirmation from Sean — never automatic. Deploy from an allow-listed
  branch (typically `main`, post-merge), and verify the published result.
- **Branch janitorial.** After a merge, note branches that are now subsumed or have
  fallen behind, and flag stale/divergent branches for rebase-or-close.

### Testing

- Behavioral tests over implementation tests.
- Visual regression for exported components.
- Accessibility tests (axe-core or equivalent) in CI for exported components.

---

## 3. Historical archive

Previous teams' conventions. Not binding. Read when:

- Working in older parts of the codebase that still follow old conventions.
- Migrating something from an old pattern to the current one.
- Understanding why a pattern exists the way it does.

### Centric PLM — legacy Dojo/dgrid era

_Team: Centric Software PLM legacy. Effective: pre-2023. Archived._

- Data tables implemented in Dojo/dgrid. Custom declarative column config.
- Inline editing opt-in per cell, not per table.
- Row identity tracked by explicit ID, not position.
- Styling via component-scoped Less, not tokens.

_Relevance today: any legacy surface still running this stack reflects these conventions. New work migrates off them per the active layer._

### [Previous team name] — [era]

_Team: [name]. Effective: [date range]. Archived._

- [Practice 1]
- [Practice 2]

_Relevance today: [when this context matters]._

---

## 4. Cross-team patterns

Conventions Sean has seen succeed across multiple teams. Not binding on current work, but signal that a pattern is durable. Candidates for the baseline if they accumulate enough evidence.

- **States expressed via variable modes, not variants** — durable across every design system team that's adopted Figma variables. Reduces combinatorial variant explosion; maps cleanly to CSS pseudo-classes.
- **Semantic token tier as the component-consumption layer** — consistent across every mature DS (Material, Carbon, Polaris, Fluent, Spectrum, Primer). Components should read from semantic, not global.
- **Preferred instances on slots** — consistently valuable wherever slot-based composition is used in Figma. Reduces the cognitive load of "which component goes here?"
- **Destructive operations require explicit confirmation** — design system governance across teams consistently benefits from preserving identity of existing artifacts over recreating them.
- [Add more as patterns surface.]

---

## Maintenance

- This document is Sean's to edit. Claude can propose changes but doesn't merge them unilaterally.
- **When to update the active layer:** a team decision gets explicit agreement (architecture review, design system council, team lead signoff). Undocumented decisions aren't decisions — they're habits.
- **When to move a cross-team pattern to the baseline:** seen in 3+ teams as a working convention. Move with a note on which teams validated it.
- **When to archive the active layer:** when the team composition or scope shifts such that the current rules no longer apply. Archive with date range and team name; start a new active layer.
- **Rule of thumb for granularity:** if a practice would go into a PR review comment multiple times, it belongs here. One-off feedback doesn't.

---

## Integration with the five frameworks

- **Last-Mile Craft Framework** (05) references this document as the authoritative source for team-specific code-level craft conventions that override or extend the general best-practices baseline.
- **Collaboration and Critique Framework** (03) references this document indirectly — the shared archive of disagreements and outcomes may feed into updating the active layer when a prediction plays out and a team convention needs to change.
- **Research and Evidence Framework** (04) is how active-layer decisions get justified when they're not obvious — tier-named evidence for why a convention was adopted.

When a team-specific convention is adopted or retired, the relevant framework's operating habits may need to update. That flag belongs at the top of this document when editing.

---

_Last reviewed: [YYYY-MM-DD]. Next planned review: [YYYY-MM-DD or "on team change"]._
