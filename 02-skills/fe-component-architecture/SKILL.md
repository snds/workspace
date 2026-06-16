---
name: fe-component-architecture
description: >
  Component API design, headless UI patterns, design system implementation, and
  composability at enterprise scale. Use this skill whenever the conversation
  touches: component API design, controlled vs. uncontrolled components, slot
  patterns, compound components, render props, polymorphic components, ref
  forwarding, useImperativeHandle, headless UI, Radix UI, Ark UI, Zag.js, React
  Aria, headless primitives, design system token consumption, CSS custom
  properties, variant systems, CVA, class-variance-authority, breaking changes
  in component APIs, codemods, deprecation cycles, composability patterns,
  context providers in compound components, merge refs, or any question about
  how to structure and expose component APIs in an enterprise design system
  context.
aliases: [fe-component-architecture]
tier: spoke
domain: engineering
hub: lead-frontend-engineer
prerequisites: [lead-frontend-engineer]
spec_version: "2.0"
---

# FE Component Architecture

Specialist lens for component API design, headless UI patterns, and design
system implementation. Part of the enterprise SaaS frontend engineering network.

---

## Domain Boundary

This skill owns **component structure and API decisions** — how components are
designed, composed, and exposed to consumers.

- **Framework-specific implementation details** → `fw-vue`, `fw-react`, `fw-angular`
- **Design system strategy and token architecture** → `ds-advisor`
- **Design/code bridge, Figma handoff** → `design-engineer`
- **Performance implications of component tree depth** → `fe-performance`
- **Accessibility logic within headless components** → `fe-accessibility`
- **Token storage (auth, not CSS)** → `be-auth-patterns`

---

## Component API Design Principles

### Controlled vs. Uncontrolled — When Each Is Appropriate

**Uncontrolled**: DOM manages its own state; consumer accesses via ref. Appropriate
for simple inputs where the parent doesn't need to drive state, and for performance-
critical cases where re-renders must be minimized (large forms, rich text editors).

**Controlled**: Consumer owns state; passes value + onChange. Appropriate when the
parent needs to react to or derive state from the component (conditional field
display, cross-field validation, form submission gating).

**Hybrid pattern** (the right default for library components): accept both `value`
(controlled) and `defaultValue` (uncontrolled). If `value` is provided, operate
controlled; otherwise manage internally. React's own inputs use this model.

```ts
// Hybrid pattern skeleton
function Select({ value, defaultValue, onChange, ...props }) {
  const [internalValue, setInternalValue] = useState(defaultValue ?? '');
  const isControlled = value !== undefined;
  const resolvedValue = isControlled ? value : internalValue;

  function handleChange(next: string) {
    if (!isControlled) setInternalValue(next);
    onChange?.(next);
  }
  // ...
}
```

**Anti-pattern**: switching between controlled and uncontrolled mid-lifecycle.
React will warn; behavior is undefined. Validate at mount in dev mode.

---

### Slot/Composition Patterns

**Prop drilling** fails past 2–3 levels and creates implicit coupling. Prefer
composition patterns that let consumers assemble components from parts.

**`children` (React) / default slot (Vue)**: Single-axis composition. Appropriate
when the compound component has one variable region.

**Named slots (Vue) / render props (React)**: Multi-axis composition. Use when
consumers need to customize multiple distinct regions (header, body, footer
of a data grid; trigger + content of a popover).

**Compound components**: Components that share state via context without
exposing it through props. The canonical pattern for Tabs, Accordion, Select,
RadioGroup.

```tsx
// Compound component context pattern
const TabsContext = createContext<TabsState | null>(null);

function Tabs({ children, defaultValue }) {
  const [active, setActive] = useState(defaultValue);
  return (
    <TabsContext.Provider value={{ active, setActive }}>
      {children}
    </TabsContext.Provider>
  );
}

function Tab({ value, children }) {
  const { active, setActive } = useContext(TabsContext)!;
  return (
    <button
      role="tab"
      aria-selected={active === value}
      onClick={() => setActive(value)}
    >
      {children}
    </button>
  );
}
```

**Anti-pattern**: boolean proliferation. `isLoading`, `isDisabled`, `isError`,
`isOpen`, `isSelected` on a single component is a sign the component is doing
too much. Prefer discriminated union variant props.

---

### Props Interface Design

**Required vs. optional**: required props should be the minimum contract. If a
consumer must provide a value for the component to be meaningful, it's required.
If there's a sensible default, it's optional. Avoid required props with narrow
"you'll almost always want X" defaults — that's just an optional prop with a
missing default.

**Discriminated unions for variant props** — prefer over boolean flags:

```ts
// Wrong: boolean proliferation
type BadButtonProps = {
  isPrimary?: boolean;
  isDestructive?: boolean;
  isGhost?: boolean;
  isLoading?: boolean;
};

// Right: discriminated union
type ButtonProps = {
  variant: 'primary' | 'secondary' | 'ghost' | 'destructive';
  state?: 'idle' | 'loading' | 'success' | 'error';
};
```

The discriminated form is exhaustively checkable, maps cleanly to DS variant
names, and eliminates impossible combinations (isPrimary + isDestructive = ???).

**Avoiding boolean proliferation**: if you have 3+ boolean props that affect the
same visual axis, you have an undeclared variant. Name it.

---

### Polymorphic Components (`as` Prop Pattern)

Allows the consumer to specify which HTML element or component the root renders as
without forking the component. Common in DS button, text, and link primitives.

Type-safe implementation in TypeScript requires generic constraints:

```tsx
type PolymorphicProps<C extends ElementType, Props = {}> = Props &
  Omit<ComponentPropsWithRef<C>, keyof Props> & {
    as?: C;
  };

function Text<C extends ElementType = 'span'>({
  as,
  children,
  ...props
}: PolymorphicProps<C, { children: ReactNode }>) {
  const Component = as ?? 'span';
  return <Component {...props}>{children}</Component>;
}
```

**Anti-pattern**: polymorphic + forwardRef simultaneously in older TypeScript is
notoriously painful. The cleanest solution is to use a wrapper ref prop
(`innerRef`) and document the constraint, or use the Radix `asChild` prop
pattern instead, which sidesteps the generic inference entirely.

---

### Ref Forwarding

When consumers need imperative access (programmatic focus, scroll, measurement),
`forwardRef` exposes the underlying DOM element. Use `useImperativeHandle` when
you want to expose a curated imperative API rather than the raw DOM element:

```tsx
const DataGrid = forwardRef<DataGridHandle, DataGridProps>((props, ref) => {
  const internalRef = useRef<HTMLDivElement>(null);

  useImperativeHandle(ref, () => ({
    scrollToRow: (index: number) => { /* ... */ },
    focusCell: (row: number, col: number) => { /* ... */ },
  }));

  return <div ref={internalRef} />;
});
```

**Contract**: `useImperativeHandle` should document every method it exposes.
Imperative APIs are hard to deprecate — keep them minimal and intentional.

---

## Headless UI Patterns

### Separation of Behavior from Presentation

Headless components own: keyboard interaction, ARIA roles/states, focus
management, and behavioral state machine. They render nothing or a neutral
wrapper. Consumers own: all visual styling.

This separation is why Radix UI, React Aria, and Ark UI are composable in DS
contexts — the DS provides the visual layer while the headless library provides
the interaction contract.

**When to use each:**

| Library | Best For | Tradeoff |
|---------|----------|----------|
| Radix UI (React) | Unstyled primitives, strong WAI-ARIA compliance, composable | React-only, primitives don't cover everything |
| React Aria (Adobe) | Comprehensive ARIA coverage, hooks-based, cross-platform | More verbose, heavier API surface |
| Ark UI / Zag.js | Framework-agnostic state machines (React/Vue/Solid) | Newer, smaller community, state machine mental model required |
| Headless UI (Tailwind Labs) | Simpler API, tight Tailwind integration | Limited component set |

**Ark UI specifics (relevant for Vue + React contexts)**: Zag.js state machines
drive the behavior layer. Each component exposes a machine context and a set
of props spreaders. The state machine model makes edge cases explicit — a
combobox open/close/selected transition is codified, not implicit.

### Building Headless Primitives

When existing libraries don't cover a primitive you need:

1. **Define the state machine**: what states can this component be in? What
   events transition between them? (Closed → Opening → Open → Closing → Closed)
2. **Define the keyboard interaction spec**: map every key to a state transition
   per the WAI-ARIA Authoring Practices Guide
3. **Define ARIA role mapping**: which element gets `role`, which gets `aria-*`
   attributes, which properties are static vs. dynamic
4. **Build the behavior hook**: encapsulates state machine + event handlers +
   ARIA attributes, returns prop spreaders
5. **Build the render component**: applies prop spreaders to DOM elements,
   forwards className/style, renders children

---

## Design System Implementation

### Token Consumption: CSS Custom Properties as the Boundary Layer

No hardcoded values in component code. Every color, spacing value, border-
radius, shadow, and typography property must reference a design token via
CSS custom property:

```css
/* Wrong */
.button { background-color: #0066cc; padding: 8px 16px; }

/* Right */
.button {
  background-color: var(--color-interactive-primary);
  padding: var(--spacing-2) var(--spacing-4);
}
```

This is the boundary that makes component theming, dark mode, and tenant
customization possible without forking component code. Route to `ds-advisor`
for token architecture strategy.

### Variant Systems: CVA Pattern

`class-variance-authority` (CVA) is the canonical solution for mapping prop
variants to class sets in Tailwind/utility-CSS contexts:

```ts
import { cva, type VariantProps } from 'class-variance-authority';

const button = cva(
  'inline-flex items-center font-medium transition-colors focus-visible:outline-none',
  {
    variants: {
      variant: {
        primary: 'bg-[var(--color-interactive-primary)] text-white',
        ghost: 'bg-transparent hover:bg-[var(--color-surface-hover)]',
      },
      size: {
        sm: 'h-8 px-3 text-sm',
        md: 'h-10 px-4 text-base',
      },
    },
    defaultVariants: {
      variant: 'primary',
      size: 'md',
    },
  }
);

type ButtonProps = VariantProps<typeof button> & { className?: string };
```

**Slot variants** (via `tailwind-variants` or CVA's `slots` API) for components
with multiple styled regions (trigger + content + arrow of a tooltip).

### Component as Design System Contract

The component's prop API must mirror the DS variant/state model. If the DS
defines a Button with variants `primary`, `secondary`, `ghost`, `destructive` —
the component's `variant` prop exposes exactly those values, not local synonyms.

Consumers reading the DS docs should be able to use the component without
translation. Naming divergence is a maintenance tax.

### Breaking Change Discipline

Enterprise DS components may have hundreds of consumers. Breaking changes require:

1. **Deprecation cycle**: mark old prop as `@deprecated` in JSDoc, add runtime
   warning in dev mode, document migration path
2. **Codemods**: provide an AST transform via jscodeshift or ts-morph for
   automated migration at scale
3. **Consumer impact analysis**: before finalizing any API change, grep or use
   the codemod in --dry-run mode to quantify affected files
4. **Minimum deprecation window**: for shared DS components, 2+ sprints between
   deprecation and removal

**Anti-pattern**: removing a prop without a deprecation cycle because "nobody
should be using this." They are.

---

## Composability Patterns

### Context Providers for Compound Component Trees

Compound components use a context provider at the root to share state without
prop drilling. Rules:

- The context shape is an internal implementation detail — don't export it
- Provide a `use[ComponentName]Context()` hook that throws a clear error when
  called outside the provider
- Keep context as lean as possible — only state that multiple children need

### Merge Refs Utility

When a component uses an internal ref and also forwards a ref to the consumer,
both must be applied. A merge-refs utility is required:

```ts
function mergeRefs<T>(...refs: Array<RefObject<T> | ForwardedRef<T> | null>) {
  return (node: T) => {
    refs.forEach(ref => {
      if (typeof ref === 'function') ref(node);
      else if (ref) (ref as MutableRefObject<T>).current = node;
    });
  };
}
```

This pattern appears in every non-trivial headless component that uses internal
focus management while also forwarding the ref to the consumer.

---

## Anti-Patterns Reference

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| Boolean proliferation | Impossible combinations, unmappable to DS | Discriminated union variant prop |
| Hardcoded token values | Breaks theming, dark mode, multi-tenant customization | CSS custom properties everywhere |
| Deep CSS selector overrides of DS internals | Breaks on DS updates, creates invisible coupling | Use headless layer or request DS variant |
| Uncontrolled-controlled switch | React warning, undefined behavior | Hybrid pattern with stable mode |
| Exporting raw context | Consumers bypass component API, coupling to implementation | Export hook with error guard only |
| Polymorphic + forwardRef in strict TypeScript | Inference breaks | Use `asChild` pattern or `innerRef` |
| Removing deprecated props immediately | Enterprise consumers can't move fast | 2-sprint minimum + codemod + runtime warning |

---

## Cross-Links

| Topic | Route to |
|-------|----------|
| Framework-specific slot/composition syntax | `fw-vue` (scoped slots), `fw-react` (render props), `fw-angular` (ng-content) |
| Token architecture and DS strategy | `ds-advisor` |
| Figma handoff, component-to-code mapping | `design-engineer` |
| ARIA within headless components | `fe-accessibility` |
| Performance impact of deep component trees | `fe-performance` |
| Token storage (auth flow, SPA OAuth) | `be-auth-patterns` |
