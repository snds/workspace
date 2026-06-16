---
name: fe-state-management
description: >
  Application state architecture, server state vs. client state, optimistic
  updates, form state, and cache management for enterprise SaaS frontends.
  Use this skill whenever the conversation touches: state management, server
  state, client state, URL state, form state, TanStack Query, React Query,
  Vue Query, SWR, Apollo Client, Pinia, Zustand, Redux Toolkit, Jotai, stale-
  while-revalidate, optimistic updates, cache invalidation, query keys, mutations,
  dependent queries, infinite queries, prefetching, form validation, Zod, Yup,
  React Hook Form, VeeValidate, dirty state tracking, unsaved changes, wizard
  forms, multi-step forms, dynamic field arrays, atom-based state, or any
  question about how to architect and manage state in an enterprise SaaS
  frontend application.
aliases: [fe-state-management]
tier: spoke
domain: engineering
hub: lead-frontend-engineer
prerequisites: [lead-frontend-engineer]
spec_version: "2.0"
---

# FE State Management

Specialist lens for application state architecture, server state management,
and form state at enterprise scale. Part of the enterprise SaaS frontend
engineering network.

---

## Domain Boundary

This skill owns **state architecture decisions and patterns**.

- **Data fetching layer (clients, interceptors, error handling)** → `fe-api-integration`
- **API contracts, pagination, caching headers** → `be-api-design`
- **Form UX patterns, wizard interaction design** → `ux-interaction-design`
- **Framework-specific store patterns** → `fw-vue` (Pinia deep dive), `fw-react` (hooks patterns)

---

## State Categorization — The Most Important Architectural Decision

Before choosing any state management library or pattern, categorize the state.
The wrong category-to-tool mapping is the most common cause of overcomplicated
frontend state architecture.

| Category | Characteristics | Right Tool |
|----------|----------------|------------|
| **Server state** | Async, potentially stale, owned by the server | TanStack Query, SWR, Apollo, Vue Query |
| **Client state** | Synchronous, owned by the UI, no server round-trip | Pinia, Zustand, Jotai, useState, useReducer |
| **URL state** | Shareable, persistent across navigation, bookmarkable | Router query params, `useSearchParams` |
| **Form state** | Uncontrolled DOM values, validation, submit lifecycle | React Hook Form, VeeValidate, Formik |

**The critical mistake**: using Redux, Pinia, or Zustand to cache server data.
This forces you to re-implement stale detection, background refresh, cache
invalidation, loading states, error states, and optimistic updates — all of
which TanStack Query gives you for free.

Server state belongs in TanStack Query (or equivalent). Client state belongs in
a client state library. Never conflate them.

---

## Server State: TanStack Query / Vue Query

### Query Keys as a Cache Coordinate System

The query key is the cache address. Design it deliberately:

```ts
// Key structure: [entity, filters/params]
['users']                              // all users
['users', { status: 'active' }]       // filtered subset
['users', userId]                     // single user
['users', userId, 'permissions']      // related entity
```

**Rules:**
- Keys must be serializable (no functions, no class instances)
- Keys must be complete — if the query depends on a filter param, include it in
  the key. A key that doesn't include its dependencies produces stale data bugs.
- Centralize key definitions in a queryKey factory to prevent typos and enable
  easy invalidation of related queries:

```ts
const userKeys = {
  all: ['users'] as const,
  lists: () => [...userKeys.all, 'list'] as const,
  list: (filters: UserFilters) => [...userKeys.lists(), filters] as const,
  detail: (id: string) => [...userKeys.all, id] as const,
};
```

### Stale-While-Revalidate Behavior

TanStack Query returns cached data immediately (stale) and fetches fresh data in
the background. Configure `staleTime` to match your data's volatility:

- `staleTime: 0` (default): data is always considered stale; refetch in background
  on every mount and window focus. Right for real-time data (notifications, live status).
- `staleTime: 5 * 60 * 1000`: data is fresh for 5 minutes. Right for user profile,
  config data that doesn't change frequently.
- `staleTime: Infinity`: never auto-refetch. Right for truly static reference data.

`gcTime` (formerly `cacheTime`): how long unused data stays in cache after the
last observer unmounts. Set generously (default 5 min) — the memory cost is low
and it enables instant navigation to previously-viewed data.

### Mutations with Optimistic Updates

```ts
const mutation = useMutation({
  mutationFn: (update: UserUpdate) => api.updateUser(userId, update),

  onMutate: async (update) => {
    // Cancel in-flight queries to prevent race conditions
    await queryClient.cancelQueries({ queryKey: userKeys.detail(userId) });

    // Snapshot the previous value
    const previous = queryClient.getQueryData(userKeys.detail(userId));

    // Optimistically update the cache
    queryClient.setQueryData(userKeys.detail(userId), old => ({
      ...old,
      ...update,
    }));

    // Return context for rollback
    return { previous };
  },

  onError: (err, update, context) => {
    // Rollback on error
    queryClient.setQueryData(userKeys.detail(userId), context?.previous);
    toast.error('Update failed — changes reverted');
  },

  onSettled: () => {
    // Always re-sync with server after mutation settles
    queryClient.invalidateQueries({ queryKey: userKeys.detail(userId) });
  },
});
```

### Dependent and Parallel Queries

**Dependent query**: only runs when a prerequisite value is available.

```ts
const { data: user } = useQuery({ queryKey: ['user', userId], ... });

const { data: permissions } = useQuery({
  queryKey: ['permissions', user?.orgId],
  enabled: !!user?.orgId,  // don't fire until user is loaded
});
```

**Parallel queries**: fire independently. `useQueries` for dynamic arrays of
parallel queries (e.g., load N widget configs simultaneously on a dashboard).

### Infinite Queries

For cursor-based pagination with "load more" UX:

```ts
const { data, fetchNextPage, hasNextPage } = useInfiniteQuery({
  queryKey: ['items', filters],
  queryFn: ({ pageParam }) => api.getItems({ cursor: pageParam, ...filters }),
  getNextPageParam: (lastPage) => lastPage.nextCursor ?? undefined,
  initialPageParam: null,
});
```

Combine with `IntersectionObserver` to trigger `fetchNextPage` when the sentinel
element enters the viewport. Combine with TanStack Virtual for virtualized
infinite scroll (see `fe-data-visualization`).

### Prefetching

```ts
// Prefetch on hover — load before user navigates
<Link onMouseEnter={() => queryClient.prefetchQuery({ queryKey: ..., queryFn: ... })}>
```

At the router level (React Router loaders, TanStack Router loaders, Nuxt route
middleware): prefetch the data that the next route needs before navigation commits.
This eliminates loading states for predictable navigation patterns.

---

## Client State Architecture

### Pinia (Vue)

The canonical Vue 3 state store. Composition API style is strongly preferred
over Options API style for new code:

```ts
export const useUserStore = defineStore('user', () => {
  const currentUser = ref<User | null>(null);
  const isAuthenticated = computed(() => !!currentUser.value);

  async function loadUser(id: string) {
    currentUser.value = await api.getUser(id);
  }

  return { currentUser, isAuthenticated, loadUser };
});
```

**`storeToRefs`**: required to destructure reactive refs from a store without
losing reactivity. Direct destructuring breaks the reactive binding.

```ts
// Wrong: breaks reactivity
const { currentUser } = useUserStore();

// Right
const store = useUserStore();
const { currentUser } = storeToRefs(store);
const { loadUser } = store; // actions can be destructured directly
```

**Anti-pattern**: putting server data in Pinia. If you're writing `isLoading`,
`isError`, `error`, and `data` properties in a Pinia store alongside fetch logic,
you're reimplementing Vue Query. Use Vue Query for server state.

### Zustand (React)

Minimal React store. The slice pattern for splitting large stores:

```ts
const useStore = create<StoreState>()(
  devtools(
    persist(
      immer((...args) => ({
        ...createUserSlice(...args),
        ...createUISlice(...args),
      })),
      { name: 'app-store' }
    )
  )
);
```

**Shallow equality**: Zustand's default equality check is reference equality.
Use `useShallow` or `shallow` from `zustand/shallow` when selecting objects or
arrays to prevent unnecessary re-renders:

```ts
const { user, settings } = useStore(useShallow(state => ({
  user: state.user,
  settings: state.settings,
})));
```

### Jotai (React)

Atomic state model — state is split into small atoms, derived atoms compose them.
Wins when you have many independent state atoms across a large component tree
(each component subscribes to exactly what it needs, no over-subscription):

```ts
const filterAtom = atom<string>('');
const sortAtom = atom<SortConfig>({ field: 'name', direction: 'asc' });

// Derived async atom (runs query when deps change)
const filteredItemsAtom = atom(async (get) => {
  const filter = get(filterAtom);
  const sort = get(sortAtom);
  return api.getItems({ filter, sort });
});
```

**When to use Jotai over Zustand**: when components across the tree need isolated
subscriptions to different state atoms and global store subscription would cause
excessive re-renders. For typical enterprise SaaS app state (current user, app
config, selected entity), Zustand or Pinia is simpler.

### When Global State Is the Wrong Answer

State that only one component needs → `useState` inside that component.
State that two sibling components need → lift to nearest common ancestor.
State that a subtree needs → Context + `useReducer` within that subtree.
State that the whole app needs → global store.

Reaching for global state too early creates invisible coupling and makes
components impossible to test in isolation.

---

## Optimistic Updates

### Speculative UI Pattern

Render the expected result immediately on user action, then reconcile with the
server response. Makes the UI feel instantaneous for common mutation paths.

**When speculative UI is appropriate:**
- High confidence the operation will succeed (e.g., toggling a feature flag)
- Low cost of a brief incorrect state (e.g., a task checkbox)
- Server response latency is user-noticeable (>200ms)

**When speculative UI is risky:**
- Operation may be rejected by business logic (quota exceeded, permission denied)
- Conflict with other users' concurrent changes is likely
- Operation is irreversible (deletion, financial transaction)

### Rollback Strategy

Always preserve the previous state before applying the optimistic update (see
`onMutate` pattern above). On error, restore it, and show clear feedback: "Your
changes couldn't be saved — please try again" not a silent silent revert.

### Conflict Resolution

For enterprise SaaS: **server wins**. The server's state is canonical. On
optimistic update failure, the client reverts to the server's returned state.
Last-write-wins (merging client + server) is usually wrong — it can silently
discard a concurrent change from another user.

---

## Form State at Enterprise Scale

### Tool Selection

| Scenario | Right Tool |
|----------|-----------|
| React forms with complex validation | React Hook Form (performance-first, uncontrolled) |
| Vue forms | VeeValidate (Vue 3 Composition API, Zod integration) |
| Schema-driven validation | Zod (TypeScript-first, composable, excellent error messages) |
| Legacy or controlled forms with extensive logic | Formik (stable, more verbose) |

### Zod Schema Binding

Define validation in Zod; bind to the form library's resolver:

```ts
const schema = z.object({
  name: z.string().min(1, 'Name is required').max(255),
  email: z.string().email('Must be a valid email'),
  role: z.enum(['admin', 'editor', 'viewer']),
  // async validation via .refine
  slug: z.string().refine(
    async (val) => !(await api.slugExists(val)),
    'This slug is already taken'
  ),
});

// React Hook Form
const { register, handleSubmit, formState: { errors } } = useForm({
  resolver: zodResolver(schema),
});
```

### Complex Form Patterns

**Wizard/multi-step**: maintain form state across steps with a single
`useForm` instance. Only validate the current step's fields on "Next";
validate all fields on final submit. Store the partial form state in URL
params if users might navigate away and return.

**Conditional fields**: register/unregister fields based on other field values.
React Hook Form's `watch` + conditional rendering. Important: unregistered
fields must be cleared or their values will persist invisibly.

**Dynamic field arrays**: React Hook Form's `useFieldArray`, VeeValidate's
`useFieldArray`. Each array entry gets its own index-based key; avoid using
array index as React key if items can be reordered.

### Dirty State Tracking

Track unsaved changes to prevent accidental data loss:

- `formState.isDirty` (React Hook Form) — true if any field value differs from `defaultValues`
- Prompt the user before navigation if the form is dirty (router `beforeEach`/`useBlocker`)
- Enterprise SaaS pattern: **warn on navigation + autosave draft**. Show a
  "Unsaved changes" indicator. Save a draft copy on `onChange` debounce (500ms).
  The primary "Save" action is still explicit and confirmed.

---

## Anti-Patterns Reference

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| Server data in Redux/Pinia/Zustand | Manual re-implementation of TanStack Query's features | Move server data to TanStack Query; keep global store for client-only state |
| Query key missing a dependency | Stale data when dependency changes | Audit keys: every variable the query depends on must be in the key |
| Optimistic update without rollback | Silent incorrect state on failure | Always preserve previous state in `onMutate`, restore in `onError` |
| Global state for component-local state | Invisible coupling, untestable components | Push state down to the component that owns it |
| Fetching in a Pinia/Zustand action without error state | Unhandled errors silently swallowed | Use TanStack Query for the fetch; store only truly global client state |
| Array index as form field array key | Broken focus, incorrect validation mapping on reorder | Use stable ID from data as key |
| Validating all steps on "Next" | Poor UX — errors in future steps confuse users | Validate only current step's schema slice on Next |

---

## Cross-Links

| Topic | Route to |
|-------|----------|
| Data fetching layer, API client, error handling | `fe-api-integration` |
| API contracts, cursor pagination, caching headers | `be-api-design` |
| Form UX design, wizard flow | `ux-interaction-design` |
| Vue-specific Pinia patterns and composables | `fw-vue` |
| React-specific hooks and concurrent patterns | `fw-react` |

## Related
- hub → [[lead-frontend-engineer]]
