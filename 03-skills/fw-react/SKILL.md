---
name: fw-react
description: >
  React framework patterns for design system implementation — hooks architecture,
  component composition patterns, concurrent features, server state management with
  TanStack Query, performance optimization, TypeScript prop patterns, and cross-framework
  alignment. Use this skill whenever the conversation involves React components in a
  design system context, React 18/19 concurrent features, hooks (useState, useEffect,
  useReducer, useContext, useMemo, useCallback, useRef), compound components, Radix
  Primitives integration, CVA/cva variant patterns, or ensuring parity between React
  and Vue/Angular/Svelte DS implementations. If the user mentions "React", "JSX",
  "hooks", "Suspense", "useTransition", "RSC", "TanStack Query", or is working on a
  DS that targets React — use this skill.
pinned_version: "19.1.0"
pinned_date: "2026-04-22"
changelog_url: "https://github.com/facebook/react/releases"
aliases: [fw-react]
tier: spoke
domain: engineering
hub: lead-frontend-engineer
prerequisites: [lead-frontend-engineer]
spec_version: "2.0"
---

# React — Framework Skill

## Version Check (run on every load)

1. Web search for `React latest release`.
2. Compare against `pinned_version: 19.1.0`.
3. Flag if newer stable version. Proceed with current knowledge.

---

## React 19 / Concurrent Features

### useTransition — non-urgent state updates

```typescript
const [isPending, startTransition] = useTransition();

// Mark a state update as non-urgent — React yields to higher-priority renders
function handleSearch(query: string) {
  startTransition(() => {
    setSearchResults(expensiveFilter(query));
  });
}

// isPending is true while the transition is in-flight — use for loading indicators
```

Mental model: `startTransition` tells React "this update is okay to interrupt." Use for any state update that drives a slow render (filtering large lists, tab switches, page transitions). Do NOT use for inputs — those must feel instant.

### useDeferredValue — defer a derived value

```typescript
const deferredQuery = useDeferredValue(query);
// deferredQuery lags behind query during typing — prevents every keystroke from triggering expensive work
const results = useMemo(() => expensiveFilter(deferredQuery), [deferredQuery]);
```

`useDeferredValue` vs `useTransition`: use `useTransition` when you own the state setter; use `useDeferredValue` when you receive a value from a parent and can't wrap the setter.

### Suspense + lazy — code splitting

```typescript
const HeavyPanel = lazy(() => import('./HeavyPanel'));

function App() {
  return (
    <Suspense fallback={<Skeleton />}>
      <HeavyPanel />
    </Suspense>
  );
}
```

Suspense also integrates with data fetching via TanStack Query's `suspense: true` option and React Server Components streaming.

### React 19: `use()` hook

```typescript
// Unwrap a promise or context directly in render (React 19+)
const data = use(dataPromise);
const theme = use(ThemeContext); // replaces useContext in most cases
```

`use()` can be called conditionally — unlike all other hooks. Enables reading async resources in the component body when wrapped in Suspense.

---

## Hooks Architecture

### useState — local ephemeral state

```typescript
const [count, setCount] = useState(0);
const [user, setUser] = useState<User | null>(null);

// Functional update — always use when next state depends on previous
setCount(prev => prev + 1);

// Lazy initializer — for expensive initial computation only
const [data] = useState(() => JSON.parse(localStorage.getItem('data') ?? '[]'));
```

Failure mode: calling `setState` in render. If you derive a value from state, use `useMemo` or derive inline — never sync state to state.

### useEffect — synchronizing with external systems

```typescript
useEffect(() => {
  const sub = eventSource.subscribe(handler);
  return () => sub.unsubscribe(); // cleanup is mandatory for subscriptions
}, [handler]);
```

Mental model: `useEffect` synchronizes React state with something outside React (DOM APIs, WebSockets, analytics, third-party libraries). It is NOT a lifecycle hook. If you're using it to derive state, you don't need it — compute inline or with `useMemo`.

Common failure modes:
- Missing dependencies (stale closure) — ESLint `exhaustive-deps` catches these
- Infinite loop via object/array literals in deps (`{}` is a new reference every render)
- Fetching data in `useEffect` — use TanStack Query instead

### useReducer — complex local state machines

```typescript
type Action =
  | { type: 'increment' }
  | { type: 'set'; payload: number };

function reducer(state: number, action: Action): number {
  switch (action.type) {
    case 'increment': return state + 1;
    case 'set': return action.payload;
    default: return state;
  }
}

const [count, dispatch] = useReducer(reducer, 0);
dispatch({ type: 'increment' });
```

Use `useReducer` over `useState` when: multiple sub-values update together, next state depends on multiple pieces of current state, or the update logic is testable in isolation.

### useContext — consuming context

```typescript
const ThemeContext = createContext<Theme>(defaultTheme);

// Provider
<ThemeContext.Provider value={theme}>
  <App />
</ThemeContext.Provider>

// Consumer
const theme = useContext(ThemeContext);
```

`useContext` re-renders the consumer whenever the context value changes (by reference). Memoize the value object or split contexts by update frequency to avoid unnecessary re-renders.

### useRef — mutable values that don't trigger re-render

```typescript
// DOM access
const inputRef = useRef<HTMLInputElement>(null);
useEffect(() => { inputRef.current?.focus(); }, []);
<input ref={inputRef} />

// Mutable value that persists across renders (timer ids, previous values, abort controllers)
const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
```

### useMemo — memoize expensive computations

```typescript
const sortedItems = useMemo(
  () => [...items].sort(compareFn),
  [items, compareFn]
);
```

The common mistake: wrapping everything in `useMemo` as a premature optimization. `useMemo` itself has a cost. Use it only when: (1) the computation is measurably slow (profile first), or (2) you need referential stability for a dependency array or context value. Do not use `useMemo` for primitive values or simple object literals passed as JSX props — React.memo on the child is the correct tool.

### useCallback — stable function references

```typescript
const handleClick = useCallback((id: string) => {
  dispatch({ type: 'select', payload: id });
}, [dispatch]); // dispatch from useReducer is stable — safe dep
```

Only needed when the function is: (1) a dependency of another hook, or (2) a prop to a `React.memo`-wrapped child. Like `useMemo`, do not wrap every function by default.

---

## Component Patterns

### Compound components — DS-first pattern

```typescript
// Context-driven compound component (Radix-style)
const AccordionContext = createContext<AccordionContextValue>(null!);

function Accordion({ children, defaultOpen }: AccordionProps) {
  const [openItem, setOpenItem] = useState(defaultOpen ?? null);
  return (
    <AccordionContext.Provider value={{ openItem, setOpenItem }}>
      <div className="accordion">{children}</div>
    </AccordionContext.Provider>
  );
}

function AccordionItem({ value, children }: AccordionItemProps) {
  const { openItem, setOpenItem } = useContext(AccordionContext);
  const isOpen = openItem === value;
  return (
    <div data-state={isOpen ? 'open' : 'closed'}>
      {children}
    </div>
  );
}

// Attach as static properties for ergonomic API
Accordion.Item = AccordionItem;
Accordion.Trigger = AccordionTrigger;
Accordion.Content = AccordionContent;
```

### forwardRef — exposing DOM refs

```typescript
const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ className, ...props }, ref) => (
    <input ref={ref} className={cn('input', className)} {...props} />
  )
);
Input.displayName = 'Input';
```

React 19: `ref` is now a regular prop — `forwardRef` is no longer required in React 19 projects. Use `forwardRef` only when targeting React 18 compatibility.

### Controlled vs. uncontrolled

```typescript
// Controlled — parent owns state
<Input value={value} onChange={e => setValue(e.target.value)} />

// Uncontrolled — component owns state (defaultValue)
<Input defaultValue="initial" ref={inputRef} />

// DS pattern: support both via the "open-closed" pattern
function useControllableState<T>({ value, defaultValue, onChange }: ...) {
  const [internalValue, setInternalValue] = useState(defaultValue);
  const isControlled = value !== undefined;
  return [
    isControlled ? value : internalValue,
    (next: T) => {
      if (!isControlled) setInternalValue(next);
      onChange?.(next);
    },
  ] as const;
}
```

---

## State Management Decision Matrix

| Scope | Tool | When |
|---|---|---|
| Component-local UI state | `useState` / `useReducer` | Toggle open, input value, hover |
| Shared UI state (module) | `useContext` + `useReducer` | Theme, auth user, modal stack |
| Server/async state | TanStack Query | API data, mutations, cache |
| App-level complex state | Zustand or Redux Toolkit | Shopping cart, complex forms, undo |
| Atomic derived state | Jotai | Fine-grained reactivity, derived atoms |

Rule of thumb: push state as low as possible, lift only when required. Context is not a performance-free global store — it causes re-renders. Zustand/Jotai do not (selectors only subscribe to slices).

---

## TanStack Query (React Query) — Server State

```typescript
// Query — read
const { data, isPending, error } = useQuery({
  queryKey: ['products', filters],
  queryFn: () => fetchProducts(filters),
  staleTime: 1000 * 60 * 5, // 5 min — don't refetch if fresh
});

// Mutation — write + optimistic update
const mutation = useMutation({
  mutationFn: updateProduct,
  onMutate: async (updated) => {
    await queryClient.cancelQueries({ queryKey: ['products'] });
    const previous = queryClient.getQueryData(['products']);
    queryClient.setQueryData(['products'], (old) => /* optimistic update */);
    return { previous }; // rollback context
  },
  onError: (err, _vars, context) => {
    queryClient.setQueryData(['products'], context?.previous);
  },
  onSettled: () => {
    queryClient.invalidateQueries({ queryKey: ['products'] });
  },
});
```

Key mental model: TanStack Query is a server state cache, not a data fetching library. `queryKey` is the cache key — structure it as `[resource, ...filters]` so invalidation is precise.

---

## Performance

### React.memo — prevent child re-renders

```typescript
const ProductCard = memo(function ProductCard({ product, onSelect }: Props) {
  return <div onClick={() => onSelect(product.id)}>{product.name}</div>;
});
```

`memo` does a shallow comparison of props. It helps when: the parent re-renders frequently and the child is expensive to render. It hurts when: props change on every render anyway (defeats the memo) or the component is trivially cheap.

### Virtual DOM reconciliation — what to know

React's reconciler matches elements by type and key. Key rules:
- Always provide stable `key` on list items — use IDs, never array indices for dynamic lists
- Changing a component's type (e.g., `div` → `span`) unmounts and remounts — avoid in hot paths
- Sibling elements with the same type at the same position share state — use `key` to reset

### Profiler — finding actual bottlenecks

Use React DevTools Profiler before optimizing. Common sources of slow renders:
1. Context value changing on every render (wrap in `useMemo`)
2. Expensive render functions without memoization
3. Too many components in a single Suspense boundary
4. Unkeyed dynamic lists causing full reconciliation

### Concurrent rendering — priority lanes

React 18+ schedules renders in priority lanes. `startTransition` moves work to the "transition" lane (interruptible). Input events are in the "sync" lane (never interrupted). Understanding this explains why `startTransition` makes UIs feel more responsive: React can abandon and restart the transition render if a higher-priority update (typing) comes in.

---

## Design System Integration

### Token consumption patterns

```typescript
// Option 1: CSS Modules (co-located, scoped, zero runtime)
import styles from './Button.module.css';
// Button.module.css: .root { background: var(--color-primary); }
<button className={styles.root} />

// Option 2: Utility classes (Tailwind)
<button className="bg-[--color-primary] px-[--spacing-md]" />

// Option 3: CSS-in-JS (runtime, avoid in DS — poor SSR + perf)
// Only if the project is already committed to a CSS-in-JS library
```

For DS libraries: CSS Modules or CSS custom properties are preferred. CSS-in-JS adds runtime cost and SSR complexity that library consumers inherit.

### Radix Primitives pattern

```typescript
import * as Dialog from '@radix-ui/react-dialog';

// Radix provides accessible behavior, you own all styles
export function Modal({ open, onOpenChange, children, trigger }: ModalProps) {
  return (
    <Dialog.Root open={open} onOpenChange={onOpenChange}>
      <Dialog.Trigger asChild>{trigger}</Dialog.Trigger>
      <Dialog.Portal>
        <Dialog.Overlay className={styles.overlay} />
        <Dialog.Content className={styles.content}>
          {children}
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
```

`asChild` merges Radix's behavior props onto your element — use it to avoid extra DOM nodes.

### CVA — compound component variants

```typescript
import { cva, type VariantProps } from 'class-variance-authority';

const button = cva('btn', {
  variants: {
    variant: {
      primary: 'btn--primary',
      secondary: 'btn--secondary',
      ghost: 'btn--ghost',
    },
    size: {
      sm: 'btn--sm',
      md: 'btn--md',
      lg: 'btn--lg',
    },
  },
  defaultVariants: { variant: 'primary', size: 'md' },
  compoundVariants: [
    { variant: 'primary', size: 'lg', class: 'btn--primary-lg' },
  ],
});

interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof button> {}

export function Button({ variant, size, className, ...props }: ButtonProps) {
  return <button className={button({ variant, size, className })} {...props} />;
}
```

---

## TypeScript with React

### Component prop typing

```typescript
// Extend native element props for primitive DS components
interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost';
  isLoading?: boolean;
}

// Discriminated union props — when a prop changes the shape of the API
type CardProps =
  | { href: string; onClick?: never }   // link card
  | { href?: never; onClick: () => void }; // button card

// Generic components
function Select<T extends { id: string; label: string }>({
  options,
  value,
  onChange,
}: {
  options: T[];
  value: T | null;
  onChange: (item: T) => void;
}) { ... }
```

### Event handler types

```typescript
// Synthetic event handlers
onChange: React.ChangeEventHandler<HTMLInputElement>;   // e.target.value
onClick: React.MouseEventHandler<HTMLButtonElement>;
onKeyDown: React.KeyboardEventHandler<HTMLElement>;

// Custom handler (no event object)
onSelect: (id: string) => void;
```

---

## Testing (React Testing Library)

### Philosophy — test behavior, not implementation

```typescript
// BAD: testing implementation details
expect(wrapper.state('isOpen')).toBe(true);
expect(component.find('Button').props().onClick).toBeCalled();

// GOOD: testing what the user sees and does
const { getByRole, findByText } = render(<Dropdown label="Sort" options={opts} />);
await userEvent.click(getByRole('button', { name: 'Sort' }));
expect(await findByText('Newest first')).toBeInTheDocument();
```

Query priority (RTL's recommended order): `getByRole` > `getByLabelText` > `getByPlaceholderText` > `getByText` > `getByTestId`. Never query by class name or component name.

### Testing async state

```typescript
// Async state with TanStack Query
const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });

function renderWithQuery(ui: React.ReactElement) {
  return render(
    <QueryClientProvider client={queryClient}>{ui}</QueryClientProvider>
  );
}

test('shows products after load', async () => {
  server.use(http.get('/api/products', () => HttpResponse.json(mockProducts)));
  renderWithQuery(<ProductList />);
  expect(await screen.findByText('Product A')).toBeInTheDocument();
});
```

### Testing custom hooks

```typescript
import { renderHook, act } from '@testing-library/react';

test('useCounter increments', () => {
  const { result } = renderHook(() => useCounter(0));
  act(() => result.current.increment());
  expect(result.current.count).toBe(1);
});
```

---

## React ↔ Vue / Angular / Svelte Parity

| React | Vue | Angular | Svelte 5 | Notes |
|---|---|---|---|---|
| `props` | `defineProps()` | `input()` signal | `$props()` | TS generics in all |
| `children` | Default `<slot />` | `<ng-content />` | `children` snippet | |
| Named slots | Named `<slot name="x">` | `select="[slot=x]"` | Named snippets | |
| `useState` | `ref()` | `signal()` | `$state()` | |
| `useMemo` | `computed()` | `computed()` | `$derived()` | |
| `useEffect` | `watchEffect()` | `effect()` | `$effect()` | |
| `useContext` | `inject()` | `inject()` token | `getContext()` | |
| `forwardRef` | `defineExpose()` | `viewChild()` | `bind:ref` | React 19: just `ref` prop |
| `React.memo` | (auto) | `OnPush` | (auto) | Vue/Svelte skip by default |

Key API differences:
- React is explicit about memoization (opt-in); Vue and Svelte are reactive by default
- Angular's DI system is the most formal — injection tokens replace all context patterns
- Svelte compiles away the reactivity runtime; React ships ~45KB runtime
- React's `key` prop controls reconciliation identity — Vue and Angular have equivalent `key`/`trackBy`

---

## Design-Engineer Integration

Spoke of `design-engineer` and `lead-frontend-engineer`. React DS components should:
1. Consume tokens exclusively via CSS custom properties — never hardcode colors or spacing
2. Use Radix Primitives for accessibility-critical interactive components
3. Use CVA for variant management — keeps class logic declarative and type-safe
4. Support both controlled and uncontrolled usage via `useControllableState`
5. Export TypeScript types alongside components — consumers depend on them
6. Test with React Testing Library against ARIA roles, not implementation details

## Related
- hub → [[lead-frontend-engineer]]
