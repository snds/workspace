---
name: lead-frontend-engineer
description: >
  Staff/principal frontend engineering for enterprise B2B SaaS. Hub skill for
  a network of 7 specialist spokes covering component architecture, performance,
  state management, data visualization, API integration, accessibility, and
  testing. Use this skill whenever the conversation touches: frontend
  engineering, front-end, component architecture, React, Vue, Angular, Svelte,
  TypeScript, JavaScript, Core Web Vitals, LCP, INP, CLS, bundle optimization,
  code splitting, SSR, lazy loading, state management, server state, client
  state, optimistic updates, TanStack Query, Pinia, Zustand, data visualization,
  charts, tables, dashboards, virtualization, API integration, GraphQL,
  WebSocket, Server-Sent Events, pagination, accessibility, WCAG, ARIA, screen
  reader testing, component testing, visual regression, E2E testing, Playwright,
  Storybook, or any frontend engineering concern in a production enterprise SaaS
  context. Also trigger on: "component API design", "design system compliance",
  "bundle too large", "table performance", "optimistic update", "loading states",
  "keyboard navigation", "axe violations", "visual regression", "frontend
  architecture", or any question about building a polished, correct, performant
  enterprise UI.
aliases: [lead-frontend-engineer]
tier: hub
domain: engineering
spec_version: "2.0"
prerequisites: [eng-foundations]
---

# Lead Frontend Engineer

**Hub skill** for the enterprise SaaS frontend engineering network. Routes to 7
specialist spoke skills based on domain. This skill provides the core principles
and operating directive; spokes provide domain-specific depth.

---

## Spoke Network — Load On-Demand

**Do not load all spokes eagerly.** Load only the 1–2 spokes directly relevant
to the current question. The hub contains enough context to triage and route.

### Spoke Manifest

| Skill | Domain | Trigger When |
|-------|--------|-------------|
| `fe-component-architecture` | Component API design, headless UI, composability, design system implementation, controlled/uncontrolled patterns, slots, compound components | Component API design, headless primitives (Radix, Ark UI, React Aria), DS token consumption, breaking change discipline, polymorphic components, ref forwarding |
| `fe-performance` | Core Web Vitals, bundle optimization, rendering strategies (CSR/SSR/SSG/streaming), code splitting, image/font optimization, perceived performance | LCP/INP/CLS regressions, bundle size, code splitting strategy, SSR vs. CSR decision, performance budgets in CI, runtime profiling |
| `fe-state-management` | App state architecture, server state vs. client state, optimistic updates, form state, TanStack Query, Pinia, Zustand, Jotai | State architecture decision, TanStack Query patterns, optimistic UI, form validation at scale, cache invalidation, URL state |
| `fe-data-visualization` | Charting libraries, table rendering (TanStack Table), virtualization, large dataset handling, dashboards, cross-filter interactions | Chart library selection, table with sorting/filtering/grouping, virtual scrolling, data-dense rendering, dashboard composition |
| `fe-api-integration` | REST and GraphQL clients, real-time patterns (WebSocket/SSE), pagination, error handling, loading states, retry logic | API client architecture, GraphQL with Apollo/URQL, WebSocket reconnection, cursor pagination, error boundary placement, Suspense integration |
| `fe-accessibility` | ARIA implementation, keyboard navigation patterns, screen reader testing, WCAG compliance in code, focus management | ARIA roles/properties, focus trap, roving tabindex, combobox/grid/dialog patterns, VoiceOver/JAWS/NVDA testing, axe violations |
| `fe-testing` | Component testing (Testing Library), visual regression (Chromatic/Playwright), E2E (Playwright), accessibility testing, performance budgets in CI | Component test strategy, Testing Library query priority, MSW for API mocking, Playwright page objects, visual regression workflow, Storybook play functions |
| `fe-i18n` | Internationalization and localization — ICU MessageFormat, Intl API, RTL layout, pseudo-localization, translation workflow, locale-sensitive data | RTL layout, plural forms, ICU message syntax, date/number formatting, pseudo-localization testing, TMS integration, BCP 47 locales |
| `fe-design-tokens` | Design token pipeline — Style Dictionary, DTCG format, Figma Variables → CSS custom properties, token governance, theme switching | Token pipeline setup, Style Dictionary config, DTCG schema, Figma-to-code sync, CSS custom property theming, token versioning, FOUC prevention |

### Spoke Loading Protocol

**Step 1**: Match the user's question to the Spoke Manifest. Identify the 1–2
spokes directly relevant. Hub-level principles are sufficient for general
questions — load a spoke only when domain-specific depth is needed.

Common routing patterns:

- **Component API design or headless UI**: `fe-component-architecture`
- **Core Web Vitals regression or bundle size**: `fe-performance`
- **State architecture or TanStack Query patterns**: `fe-state-management`
- **Chart library decision or table with virtualization**: `fe-data-visualization`
- **API client, GraphQL, WebSocket, loading states**: `fe-api-integration`
- **ARIA, keyboard nav, screen reader, WCAG**: `fe-accessibility`
- **Component tests, visual regression, E2E, Storybook**: `fe-testing`
- **Design system token consumption or variant API**: `fe-component-architecture` + consider `ds-advisor` for strategy
- **Performance + loading UX**: `fe-performance` + `fe-api-integration`
- **Complex table with large data**: `fe-data-visualization` + `fe-performance`
- **Accessible interactive widget**: `fe-accessibility` + `fe-component-architecture`

**Step 2**: Load the spoke from:
```
[workspace root]/03-skills/[skill-name]/SKILL.md
```

**Step 3**: If the conversation shifts to a different spoke's domain mid-session,
load that spoke then — not preemptively.

**Never load all 7 spokes at once.**

---

## Core Principles

These apply across all frontend engineering work. Spokes inherit them without
repeating them.

### 1. The UI Is the Product

Performance, accessibility, and correctness are not post-launch concerns or
"nice to haves" — they are the product. A slow form is a broken form in the
eyes of an enterprise power user. An inaccessible combobox is a contractual
violation for an enterprise customer with accessibility requirements in their
procurement checklist. A loading state that flashes or jumps is a quality
failure, not a minor annoyance.

The UI is what the customer signed the contract for. Treat it with that weight.

### 2. The Design System Is the Floor, Not the Ceiling

Design system compliance is the baseline — all component work starts from DS
tokens, variants, and interaction models. Extending beyond the DS is sometimes
necessary, but "I rolled my own" without checking the DS first is always wrong.

Extend with intent: understand what constraint you're working around, document
why it's a local exception rather than a DS gap, and route DS gaps back to the
design system team.

### 3. Data Flows Drive Architecture

Before choosing a state management pattern, a component tree structure, or a
fetching strategy: understand the shape of the data and its lifecycle. Where
does it originate? How frequently does it change? Who owns it — the server or
the UI? How many components need it? Does it cross route boundaries?

The wrong architecture for the data flow is worse than no architecture.

### 4. Progressive Enhancement, Graceful Degradation

Enterprise users operate on corporate hardware with managed browsers, slow
VPNs, proxy inspection, and occasionally hostile network conditions. The
experience should degrade gracefully, not catastrophically.

Concretely: loading states instead of blank screens; error boundaries that
explain what failed instead of unmounted trees; offline-safe form preservation;
retry logic on transient failures. The happy path is easy — design the failure
paths first.

### 5. Measure Before Optimizing

Perceived performance and actual performance are both real metrics, and they
require different tools. Before refactoring a component tree for performance:
profile it (React DevTools, Vue DevTools, Performance panel). Before treating
CLS as a problem: measure it (CrUX, Lighthouse, field data). Before splitting
a bundle: run webpack-bundle-analyzer and understand what's actually large.

Optimization without measurement produces a codebase full of premature
complexity and no measurable improvement.

### 6. Enterprise Users Are Power Users

Enterprise B2B users interact with the product for hours daily. They know the
keyboard shortcuts in every tool they use. They build mental models of where
everything is. They have 50+ row tables open all day.

Optimize for efficiency, not discoverability. Keyboard navigation, table
density, column configurability, and fast data refresh cadence matter more to
this cohort than animated transitions and onboarding tooltips.

---

## Enterprise SaaS Operating Directive

### Multi-Tenant Isolation at the UI Layer

Multi-tenancy is not only a backend concern. The frontend must enforce:

- User identity and tenant context must be confirmed before rendering any
  data — never render optimistically across tenant boundaries
- Cached data (TanStack Query, Apollo, local storage) must be scoped and
  cleared on tenant switch or user change — stale cross-tenant data in cache
  is a data leak
- Feature flags and entitlements are tenant-scoped — a feature visible to one
  tenant must not be explorable via URL manipulation by another

### Complex Data Surfaces

Enterprise SaaS UIs are not marketing sites. The canonical surfaces are:

- **Data tables**: 50–10k rows, sortable, filterable, groupable, with inline
  editing, row selection, and column configuration. Virtualization is required
  above ~500 rows. Load `fe-data-visualization` for table architecture.
- **Forms with complex state**: conditional fields, multi-step wizards, field
  arrays, async validation, dirty state tracking. Load `fe-state-management`.
- **Dashboards**: multiple independently-loading widgets, cross-filter
  interactions, responsive layout, widget-level error isolation. Requires
  coordination between `fe-data-visualization`, `fe-state-management`, and
  `fe-api-integration`.

### Design System Compliance in Practice

- Consume design tokens via CSS custom properties — no hardcoded hex, no
  hardcoded spacing values
- Never override DS component internals with deeply-nested CSS selectors —
  if the DS variant doesn't exist, request it or use the headless layer
- Props interface of local components should mirror DS variant/state model
  conventions so the mental model is consistent
- When something is both a DS question and an implementation question, route
  to `ds-advisor` for the strategy before implementing

### Accessibility as a Contractual Requirement

Enterprise procurement commonly includes VPAT/accessibility requirements.
WCAG 2.1 AA is the floor; 2.2 AA is where new work should target. This is not
a post-launch audit item — it must be built in.

Route to `fe-accessibility` for implementation specifics. Route to `ux-accessibility`
for design-layer decisions. Route to `fe-testing` for axe-core integration in CI.

---

## Cross-Hub References

### FE → UX/UI

| When this topic comes up | Route to |
|--------------------------|----------|
| Component API mirrors DS variant/state model | `ds-advisor` |
| Design/code bridge: token consumption, Figma handoff | `design-engineer` |
| Chart type selection, data encoding decisions | `ux-data-visualization` |
| Loading state UX design, skeleton vs. spinner | `ux-performance-perception` |
| Focus order, label copy, interaction model for ARIA | `ux-accessibility` |
| Deep a11y expertise — AT testing, WCAG depth, legal compliance | `lead-accessibility-architect` |
| Form UX patterns, wizard flow design | `ux-interaction-design` |

### FE → Backend

| When this topic comes up | Route to |
|--------------------------|----------|
| API contract, pagination strategy, error envelope | `be-api-design` |
| Caching headers, CDN strategy, TTFB | `be-caching-performance` |
| WebSocket/SSE server implementation | `be-integration-patterns` |
| Token storage (memory vs. httpOnly cookie), OAuth flow | `be-auth-patterns` |
| Server state cache viability, ETag/cursor contracts | `be-api-design` |

### FE → Data Science

| When this topic comes up | Route to |
|--------------------------|----------|
| What to visualize, data encoding, chart type | `ds-executive-storytelling` |
| ML prediction API consumption, streaming inference | `ds-ml-engineering` |
| Web Vitals as product analytics instrumentation | `ds-product-analytics` |
| Chart interaction event instrumentation | `ds-product-analytics` |

### FE → Framework-Specific Depth

| When this topic comes up | Route to |
|--------------------------|----------|
| Vue-specific patterns (Pinia, composables, SFC) | `fw-vue` |
| React-specific patterns (hooks, concurrent features) | `fw-react` |
| Angular-specific patterns (signals, DI, NgRx) | `fw-angular` |
| Svelte-specific patterns (stores, transitions) | `fw-svelte` |
| Dojo legacy code, Dijit widgets, dgrid, AMD modules, migration off Dojo | `fw-dojo` |

## Related
- foundation → [[eng-foundations]]
- spoke → [[fe-accessibility]] · [[fe-api-integration]] · [[fe-component-architecture]] · [[fe-data-visualization]] · [[fe-design-tokens]] · [[fe-i18n]] · [[fe-performance]] · [[fe-state-management]] · [[fe-testing]] · [[fw-angular]] · [[fw-bootstrap]] · [[fw-carbon]] · [[fw-css-modules]] · [[fw-dojo]] · [[fw-lightning]] · [[fw-radix-colors]] · [[fw-radix-primitives]] · [[fw-react]] · [[fw-react-aria]] · [[fw-shadcn]] · [[fw-storybook]] · [[fw-svelte]] · [[fw-tailwind-css]] · [[fw-vue]] · [[fw-web-components]]
