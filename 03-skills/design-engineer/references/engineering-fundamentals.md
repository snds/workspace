# Software Engineering Fundamentals

Foundational principles that inform the developer side of every design-engineer
decision. Load this spoke when reasoning about code architecture, maintainability,
developer experience, or when the developer lens needs to weigh in on a design
choice with engineering consequences.

This is not a coding tutorial. It's a reference for the repeatable thinking
patterns that distinguish production-quality engineering from "it works on my
machine." Written for a design-minded reader who needs to understand *why*
developers make the choices they do — and when those choices should influence
design decisions.

---

## Table of Contents

1. Separation of concerns — the organizing principle
2. Abstraction — managing complexity through layers
3. DRY, KISS, YAGNI — the tension between principles
4. Component architecture — from code's perspective
5. State management — where behavior lives
6. API design — the contract between systems
7. Developer experience — the human side of code
8. Testing — confidence as a system property
9. Performance — constraints that shape design
10. Applying engineering thinking to design decisions

---

## 1. Separation of Concerns

The single most important principle in software architecture. Every module,
function, file, and layer should have one clear responsibility.

**What it means:** Structure (HTML) is separate from presentation (CSS) is
separate from behavior (JS). Data fetching is separate from data display.
Business logic is separate from UI logic.

**Why designers should care:** When a component mixes concerns (a button that
knows about the API endpoint it calls, or a form field that validates AND
displays AND submits), changes in one area break another. This is why
developers resist "just add a prop for that" — each prop that mixes concerns
makes the component harder to change safely.

**DS application:** A well-separated design system has layers: tokens (values)
→ styles (visual rules) → components (structure) → patterns (composition).
Each layer changes independently. When a token value changes, styles update
automatically. When a component's structure changes, its token consumption
shouldn't need to change. This mirrors the 3-tier token model directly.

---

## 2. Abstraction

Hiding complexity behind a simpler interface. Every layer in a system is an
abstraction over the layer beneath it.

### The abstraction ladder

```
User sees:        A dropdown menu
Designer sees:    Trigger + popover + list items + states
Developer sees:   Event listeners + DOM positioning + keyboard
                  handlers + focus traps + ARIA attributes +
                  scroll containment + z-index management
Browser sees:     DOM nodes + CSSOM + paint operations
```

Each layer hides the complexity below it. Good abstractions are "leaky" only
when they need to be — the designer shouldn't need to think about focus traps,
and the developer shouldn't need to think about token tier mapping.

**Why designers should care:** When a component API is "too complex" from a
developer's perspective, it's usually because the abstraction is leaking —
internal complexity is being exposed to consumers. The same principle applies
in Figma: if using a component instance requires understanding its internal
layer structure, the abstraction has failed.

**DS application:** Tokens abstract raw values. Components abstract combinations
of tokens. Patterns abstract compositions of components. Each layer should be
usable without understanding the layer below it. A developer consuming a
Button component shouldn't need to know which tokens it uses internally —
they set props, and the component handles the rest.

---

## 3. DRY, KISS, YAGNI

Three principles that are often in tension with each other.

### DRY — Don't Repeat Yourself

Every piece of knowledge should have a single, authoritative representation.
Duplication means that changes must be made in multiple places, and one will
inevitably be missed.

**DS application:** This is *the* argument for design tokens and shared
components. A color defined in one place (the token) and consumed everywhere
means one change propagates globally. A component defined once and instanced
300 times means one fix fixes all 300.

**The trap:** Over-DRYing creates inappropriate coupling. Two components that
happen to share a padding value today don't necessarily need to share a token
— they might diverge tomorrow. DRY applies to knowledge, not coincidence.

### KISS — Keep It Simple, Stupid

The simplest solution that meets requirements is the best solution. Complexity
is a cost, not a feature.

**DS application:** A component with 47 props "for flexibility" violates KISS.
A token system with 400 semantic aliases for 50 primitives violates KISS. The
simplest component API that covers real use cases — not hypothetical ones — is
the right API.

### YAGNI — You Aren't Gonna Need It

Don't build for requirements that don't exist yet. Premature abstraction is as
dangerous as premature optimization.

**DS application:** Don't create a "density mode" token collection before a
single product has asked for density variants. Don't add a "size: tiny" variant
because someone might want it someday. Build for now, design for extensibility,
but don't build the extensions until they're needed.

**The tension:** DRY says "don't duplicate." YAGNI says "don't abstract prematurely."
The resolution: extract shared abstractions when you see the pattern repeat in
practice (the "rule of three"), not when you imagine it might repeat in theory.

---

## 4. Component Architecture — From Code's Perspective

### Composition over inheritance

Modern frontend frameworks prefer composing small components together rather
than extending base classes. A Card component renders Header, Body, and Footer
as children — it doesn't inherit from a "BaseCard" class.

**Why this matters for Figma:** This is exactly how Figma slots work. A Card
component with slots for header, body, and footer mirrors the React pattern
of `<Card><CardHeader/><CardBody/><CardFooter/></Card>`. When Figma component
architecture mirrors code component architecture, handoff friction drops.

### Props as the public API

A component's props are its contract with the outside world. Everything else
is internal implementation.

**Good prop design:**
- Minimal surface area — fewer props = easier to use correctly
- Predictable — same input always produces same output
- Composable — children/slots for flexible content, not config props
- Typed — TypeScript interfaces catch misuse at build time, not runtime

**Bad prop design (and the design equivalent):**
- `variant="primary-large-with-icon-left-disabled"` — combinatorial naming
  (Figma equivalent: deeply nested variant names)
- 30 boolean props — cognitive overload
  (Figma equivalent: 30 component properties on one component)
- Props that conflict with each other — `isDisabled` + `isLoading` + `isActive`
  all true simultaneously with no defined behavior

### The component tree

Components form a tree. Parent components pass data down (props) and receive
events up (callbacks). Each component owns its internal state and delegates
what it doesn't own.

```
App
├── Layout
│   ├── Navigation
│   │   ├── NavItem (active)
│   │   └── NavItem
│   └── Content
│       ├── PageHeader
│       └── DataTable
│           ├── TableHeader
│           ├── TableRow
│           │   ├── Cell (text)
│           │   ├── Cell (badge)
│           │   └── Cell (action)
│           └── Pagination
```

This maps 1:1 to Figma's layer tree. When the code tree and the Figma tree
don't match, handoff breaks.

---

## 5. State Management

State is any data that changes over time and affects what the user sees.

### Types of state

**UI state:** What's open, closed, focused, hovered, selected. Lives in the
component that owns the interaction. A dropdown's open/closed state belongs
to the dropdown, not to a global store.

**Application state:** User session, current route, feature flags. Shared
across many components. Lives in a state management layer (Redux, Zustand,
Pinia, Context).

**Server state:** Data fetched from an API. Has its own lifecycle: loading,
success, error, stale. Libraries like TanStack Query manage this separately
from UI state.

**Why designers should care:** When a designer specifies "this table shows
loading, then data, then error if the fetch fails" — they're describing a
state machine. Developers implement state machines. The more precisely a
designer defines the states and transitions, the more accurately the
developer can implement them. Ambiguous states create bugs.

### State machines

Every interactive component is a state machine. A Button has states:
default → hover → active → focus → disabled. Transitions between states
are triggered by events (mouseenter, mousedown, keypress, prop change).

**DS application:** The variant/state matrix in a Figma component set IS a
state machine definition. When that matrix is complete and the transitions
are documented, the developer has an implementation spec. When states are
missing ("what happens if the button is both loading and disabled?"), the
developer has to guess — and guesses create inconsistency.

---

## 6. API Design

An API is any interface between two systems — not just REST endpoints, but
component props, function signatures, event contracts, and token naming
conventions.

### Principles of good API design

**Consistency:** Same patterns everywhere. If one component uses `size="sm"`
and another uses `size="small"`, the API is inconsistent. If one token uses
dot notation and another uses slashes, the naming convention is inconsistent.

**Discoverability:** A developer should be able to guess the API from
conventions. If `Button` has a `variant` prop, `Badge` should too. If
`color.background.primary` exists, `color.background.secondary` should
exist at the same path.

**Backwards compatibility:** Changing an API breaks every consumer. New
features are additive (new optional props, new token values). Removals and
renames are breaking changes that require migration paths.

**DS application:** Token naming is an API. Component prop names are an API.
Variant values are an API. Every naming decision in a design system is an
API design decision — and API decisions are expensive to change later.

---

## 7. Developer Experience (DX)

DX is to developers what UX is to end users. A system with good DX is
easy to learn, hard to misuse, and fast to work with.

### What good DX looks like

**Clear error messages:** When something goes wrong, the error says what
happened, why, and how to fix it. "Invalid prop" is bad DX. "Button: 'size'
must be 'sm', 'md', or 'lg'. Received 'small'." is good DX.

**Sensible defaults:** Components work without configuration. A Button with
zero props renders a usable default button. A token system with a single mode
works before dark mode is configured.

**Progressive disclosure:** Simple things are simple. Complex things are
possible. A developer can use a Button in 10 seconds. If they need to
customize the loading spinner, that path exists but doesn't clutter the
basic use case.

**Documentation that matches reality:** Storybook stories, README files,
and inline JSDoc that reflect the actual current API — not a version from
six months ago. Outdated docs are worse than no docs.

**DS application:** Every design system artifact has a developer consumer.
Token files need clear naming. Components need typed props with JSDoc.
Migration guides need to accompany breaking changes. The design system
team's "product" is the system itself, and developers are the users.

---

## 8. Testing

Testing is how developers build confidence that code works correctly and
continues to work as changes are made.

### The testing pyramid

**Unit tests (base):** Test individual functions and components in isolation.
Fast, cheap, numerous. "Does this function format a date correctly?"

**Integration tests (middle):** Test how components work together. "Does the
form submit the right data when the user fills in fields and clicks submit?"

**End-to-end tests (top):** Test the full application from the user's
perspective. Slow, expensive, fewer. "Can a user log in, navigate to
settings, and change their password?"

### Visual regression testing

Critical for design systems. Tools like Chromatic capture screenshots of
every component state and compare them against baselines. Any pixel-level
change is flagged for review.

**Why designers should care:** Visual regression testing is the mechanism
that prevents "we shipped a padding change and it broke 47 other components."
It's the engineering equivalent of Figma's library update preview — but
automated and enforced in CI.

### Accessibility testing

Automated tools (axe-core, jest-axe) catch approximately 30-40% of WCAG
issues — missing alt text, broken ARIA attributes, color contrast failures.
The remaining 60-70% requires manual testing with screen readers and keyboard
navigation. Both are necessary; neither alone is sufficient.

---

## 9. Performance

Performance constraints shape design decisions. These are the most common
boundaries designers should understand.

### Bundle size

Every component, library, and asset adds to the JavaScript bundle users
download. A 500KB component library is a real cost — especially on mobile
networks. Component libraries that support tree-shaking (importing only
what you use) mitigate this.

**DS application:** A design system that publishes 200 components as a
single package forces every consumer to download all 200. A system with
per-component imports lets teams take only what they need.

### Render performance

Browsers repaint the screen when the DOM changes. Complex components with
deep nesting, many DOM nodes, or frequent re-renders can cause visible
jank — especially in data-heavy views like tables with hundreds of rows.

**DS application:** A data table component that renders 1,000 rows into the
DOM will be slow. Virtual scrolling (rendering only visible rows) is an
engineering solution to a design + data scale problem. Designers specifying
"infinite scroll" need to understand that this requires virtual rendering
to perform acceptably.

### Animation performance

Browsers can animate `transform` and `opacity` on the GPU — these are
"cheap" animations. Animating `width`, `height`, `top`, `left`, `margin`,
or `padding` triggers layout recalculation — these are "expensive."

**DS application:** Motion tokens should prefer transform-based animations
(translate, scale, rotate) over layout-based ones. A sidebar that animates
its width causes the entire page to reflow on every frame. A sidebar that
translates off-screen is smooth.

---

## 10. Applying Engineering Thinking to Design Decisions

### When evaluating a component from the code perspective

1. **Separation of concerns:** Does this component do one thing? Or is it
   a Swiss Army knife that handles layout, data fetching, and business logic?
2. **API surface:** How many props does this need? Could composition (slots/
   children) replace configuration (boolean props)?
3. **State completeness:** Are all states defined? What happens in edge cases
   (empty data, error, loading, offline)?
4. **Naming consistency:** Do prop names, variant values, and token references
   follow the same conventions as the rest of the system?
5. **Backwards compatibility:** Will this change break existing consumers?
   What's the migration path?

### When the developer lens should push back on design

- "This animation triggers layout recalculation on every frame — can we
  achieve the same effect with transforms?"
- "This component would need 14 boolean props to cover all these toggles —
  can we use composition instead?"
- "These three components share identical behavior but have different prop
  names — can we align the API?"
- "This state isn't defined in the spec — what should happen when the data
  fetch fails while the modal is open?"
- "Adding this variant creates a breaking change for every existing consumer
  — is the improvement worth the migration cost?"

### When the developer lens should defer to design

- Visual weight, optical alignment, and perceptual spacing — math isn't
  always right. Trust the designer's eye when values are "close enough"
  mathematically but visually wrong.
- Content hierarchy and reading order — these are UX decisions informed by
  user research, not engineering constraints.
- Color and typography choices — unless they violate accessibility minimums,
  these are design calls.
- Motion and interaction feel — "does this transition feel right?" is a
  design question. "Can this transition perform well?" is an engineering
  question. Both need answers.
