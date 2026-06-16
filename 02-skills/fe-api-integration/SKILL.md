---
name: fe-api-integration
description: >
  REST and GraphQL client patterns, real-time communication (WebSocket, SSE),
  pagination, error handling, loading state taxonomy, and Suspense integration
  for enterprise SaaS frontends. Use this skill whenever the conversation
  touches: REST client, fetch wrapper, axios, ky, request interceptors, response
  interceptors, auth header injection, typed fetch, Zod runtime validation,
  retry logic, exponential backoff, GraphQL, Apollo Client, URQL, normalized
  cache, field policies, reactive variables, fragment composition, fragment
  masking, optimistic response, WebSocket, reconnection logic, heartbeat,
  Server-Sent Events, SSE, EventSource, GraphQL subscriptions, graphql-ws, long
  polling, cursor pagination, offset pagination, IntersectionObserver, loading
  state, skeleton screen, error boundary, empty state, zero state, React
  Suspense, Vue Suspense, or any question about how a frontend application
  fetches, streams, and handles data from backend APIs.
aliases: [fe-api-integration]
tier: spoke
domain: engineering
hub: lead-frontend-engineer
prerequisites: [lead-frontend-engineer]
spec_version: "2.0"
---

# FE API Integration

Specialist lens for REST/GraphQL client patterns, real-time communication, and
data lifecycle management. Part of the enterprise SaaS frontend engineering
network.

---

## Domain Boundary

This skill owns **client-side data fetching, transport, and data lifecycle**.

- **State management patterns above the fetch layer** → `fe-state-management`
- **API contract design, pagination contracts, error envelopes** → `be-api-design`
- **WebSocket/SSE server implementation** → `be-integration-patterns`
- **Loading state UX, skeleton screen design** → `ux-performance-perception`
- **ML prediction API specifics** → `ds-ml-engineering`

---

## REST Client Patterns

### Abstraction Layer (Always)

Never call `fetch` or `axios` directly in component code or query functions.
A thin abstraction layer always pays off:

- Centralizes base URL, auth header injection, and default headers
- Provides a single place to add request/response interceptors
- Enables mocking in tests without patching globals
- Allows swapping the underlying HTTP client without touching call sites

```ts
// api-client.ts
const client = ky.create({
  prefixUrl: import.meta.env.VITE_API_BASE_URL,
  hooks: {
    beforeRequest: [
      request => {
        const token = tokenStore.getAccessToken();
        if (token) request.headers.set('Authorization', `Bearer ${token}`);
      },
    ],
    afterResponse: [
      async (request, options, response) => {
        if (response.status === 401) {
          await tokenStore.refresh();
          return ky(request);  // retry with new token
        }
      },
    ],
  },
  timeout: 30_000,
});
```

**`ky` vs `axios`**: `ky` is ESM-native, smaller, and has a cleaner API. Axios
is more established and has broader ecosystem support. Both are valid. Avoid
wrapping bare `fetch` — retry logic, timeout, and error handling are non-trivial
to implement correctly.

### TypeScript: Zod Runtime Validation at the Boundary

Never trust API responses. Validate and transform at the API boundary:

```ts
import { z } from 'zod';

const UserSchema = z.object({
  id: z.string().uuid(),
  name: z.string(),
  email: z.string().email(),
  role: z.enum(['admin', 'editor', 'viewer']),
  createdAt: z.string().datetime().transform(s => new Date(s)),
});

type User = z.infer<typeof UserSchema>;

async function getUser(id: string): Promise<User> {
  const raw = await client.get(`users/${id}`).json();
  return UserSchema.parse(raw);  // throws ZodError if shape is wrong
}
```

Why: API contracts drift, backends can return unexpected shapes, and TypeScript
types are erased at runtime. Zod catches schema violations as early as possible
(at the API boundary) rather than as mysterious undefined errors deep in the UI.

**In production**: use `safeParse` and handle `ZodError` gracefully — log the
validation failure to your error tracker with the raw response body.

### Error Handling: Distinguish All Error Classes

```ts
async function apiRequest<T>(requestFn: () => Promise<T>): Promise<T> {
  try {
    return await requestFn();
  } catch (error) {
    if (error instanceof TypeError) {
      // Network error (offline, DNS failure, CORS)
      throw new NetworkError('Could not reach the server');
    }
    if (error instanceof HTTPError) {
      const status = error.response.status;
      if (status === 401) throw new AuthError('Session expired');
      if (status === 403) throw new PermissionError('Access denied');
      if (status === 404) throw new NotFoundError('Resource not found');
      if (status === 422) {
        const body = await error.response.json();
        throw new ValidationError('Invalid request', body.errors);
      }
      if (status >= 500) throw new ServerError(`Server error: ${status}`);
    }
    if (error instanceof ZodError) {
      throw new ParseError('Unexpected API response shape', error);
    }
    throw error;
  }
}
```

**Never retry 4xx errors** (except 429 with Retry-After header). Retrying a 422
will always fail. Retrying a 400 wastes bandwidth and can cause duplicate mutations
if the idempotency key wasn't designed correctly.

### Retry Logic

```ts
import { HTTPError } from 'ky';

const client = ky.create({
  retry: {
    limit: 3,
    methods: ['get'],  // never retry mutations automatically
    statusCodes: [429, 503],  // only these status codes
    backoffLimit: 30_000,
    delay: (attemptCount) => 0.3 * 2 ** (attemptCount - 1) * 1000,  // exponential backoff
  },
  hooks: {
    afterResponse: [
      (request, options, response) => {
        if (response.status === 429) {
          const retryAfter = response.headers.get('Retry-After');
          // ky will use delay fn; you can also parse Retry-After header
        }
      },
    ],
  },
});
```

---

## GraphQL Client Patterns

### Apollo Client: Normalized Cache

Apollo's normalized cache stores entities by `__typename + id`, enabling
automatic cache updates when the same entity appears in multiple queries.

**Cache-and-network fetch policy**: for data that must be fresh but can show
stale data while loading:

```ts
const { data, loading } = useQuery(GET_PRODUCTS, {
  fetchPolicy: 'cache-and-network',  // show cached immediately, fetch in background
  nextFetchPolicy: 'cache-first',    // subsequent fetches use cache unless invalidated
});
```

**Field policies** for non-normalized data (pagination merge):

```ts
const cache = new InMemoryCache({
  typePolicies: {
    Query: {
      fields: {
        products: relayStylePagination(['filter', 'sort']),  // Apollo helper for Relay pagination
      },
    },
  },
});
```

### URQL: When to Use Over Apollo

URQL is lighter (~40kb vs Apollo's ~90kb), has a simpler mental model, and uses
an "exchanges" pipeline for extensibility. Prefer URQL when:
- The GraphQL usage is relatively straightforward (no complex cache manipulation)
- Bundle size is a significant concern
- The team finds Apollo's normalized cache model confusing

### Query Colocation (Relay Principle)

Components should declare the data they need. Don't hoist all queries to a parent
and thread props down — it creates hidden data coupling and makes components
impossible to reuse in different contexts.

```tsx
// Each component declares its own fragment
const PRODUCT_CARD_FRAGMENT = gql`
  fragment ProductCard on Product {
    id
    name
    status
    thumbnailUrl
  }
`;

function ProductCard({ product }: { product: ProductCardFragment }) {
  // component only uses what it declared
}
```

### Fragment Masking

In typed GraphQL setups (gql.tada, GraphQL Code Generator), fragments mask their
fields so parent components can't accidentally access fields they didn't declare.
This enforces the colocation contract at compile time.

### Optimistic Response in Mutations

```ts
const [updateStatus] = useMutation(UPDATE_PRODUCT_STATUS, {
  optimisticResponse: {
    updateProduct: {
      __typename: 'Product',
      id: productId,
      status: newStatus,  // the expected result
    },
  },
  update(cache, { data }) {
    // normalize into cache — Apollo uses __typename + id to match existing entries
  },
});
```

---

## Real-Time Patterns

### WebSocket

Full-duplex, long-lived connection. The right choice when the client also
sends data to the server in real time (collaborative editing, live cursors,
bidirectional game state).

**Reconnection logic is mandatory.** WebSocket connections drop — on mobile
network switches, corporate proxy timeouts, and server restarts. Without
reconnection logic, the user silently stops receiving updates.

```ts
class ReconnectingWebSocket {
  private ws: WebSocket | null = null;
  private reconnectDelay = 1000;
  private maxDelay = 30_000;

  connect(url: string) {
    this.ws = new WebSocket(url);
    this.ws.onclose = () => {
      setTimeout(() => {
        this.reconnectDelay = Math.min(this.reconnectDelay * 2, this.maxDelay);
        this.connect(url);
      }, this.reconnectDelay);
    };
    this.ws.onmessage = (event) => {
      this.reconnectDelay = 1000;  // reset on successful message
      this.handleMessage(JSON.parse(event.data));
    };
  }

  sendHeartbeat() {
    setInterval(() => this.ws?.send(JSON.stringify({ type: 'ping' })), 30_000);
  }
}
```

**Reconnection UX**: show a "Reconnecting..." indicator when the connection is
lost. Show a "Reconnected — catching up..." indicator when it restores. Fetch
any missed events on reconnect.

### Server-Sent Events (SSE)

Unidirectional (server → client only), HTTP/1.1 compatible, simpler than
WebSocket for push-only scenarios (notifications, live status updates, progress
streaming for long jobs):

```ts
const source = new EventSource('/api/events', {
  withCredentials: true,
});

source.addEventListener('notification', (event) => {
  const data = JSON.parse(event.data);
  // handle
});

source.onerror = () => {
  // EventSource reconnects automatically — but you may want to track state
  setConnectionState('reconnecting');
};
```

**SSE vs. WebSocket decision**: use SSE when the client only receives, not sends.
SSE is simpler, works over HTTP/2 multiplexing without connection limits, and
requires no special server infrastructure. Use WebSocket when bidirectional
communication is needed.

### GraphQL Subscriptions

Over WebSocket via `graphql-ws` protocol. Apollo Client and URQL both support
subscription over WebSocket link:

```ts
const wsLink = new GraphQLWsLink(
  createClient({
    url: 'wss://api.example.com/graphql',
    connectionParams: () => ({ authToken: getToken() }),
  })
);

// Split link: subscriptions over WS, queries/mutations over HTTP
const splitLink = split(
  ({ query }) => {
    const def = getMainDefinition(query);
    return def.kind === 'OperationDefinition' && def.operation === 'subscription';
  },
  wsLink,
  httpLink,
);
```

### Long Polling (Fallback)

When WebSocket is blocked by corporate proxies (more common in enterprise SaaS
than in consumer apps): long polling is a reliable fallback. The server holds
the request open until data is available or a timeout expires, then the client
immediately sends the next request.

---

## Pagination Patterns (Client Side)

### Cursor Pagination (Prefer This)

Stable under concurrent mutations — inserting or deleting a row doesn't shift
the page boundary. The server contract uses `endCursor` / `hasNextPage` (Relay
spec) or `nextCursor` / `prevCursor` (custom).

```ts
const { data, fetchNextPage, hasNextPage } = useInfiniteQuery({
  queryKey: ['products', filters],
  queryFn: ({ pageParam = null }) =>
    api.getProducts({ cursor: pageParam, ...filters }),
  getNextPageParam: (lastPage) => lastPage.nextCursor ?? undefined,
  initialPageParam: null,
});
```

### Offset Pagination

Simpler but produces inconsistent results under concurrent mutation (inserting
a row on page 1 pushes page 2's first item to page 1's last item on next load).
Acceptable for read-heavy, low-mutation data (reports, audit logs).

### Infinite Scroll with Virtualization

Combine TanStack Query `useInfiniteQuery` with TanStack Virtual: the virtualizer
windows the existing rows, and an `IntersectionObserver` on the last row triggers
`fetchNextPage`. The virtualizer must handle the growing `flatMap` of all pages.

Route to `fe-data-visualization` for the virtualization implementation details.

---

## Loading and Error States

### Loading State Taxonomy

| State | Description | UI Pattern |
|-------|------------|------------|
| **Initial load** | No data in cache; fetching for the first time | Skeleton screen (preferred) or spinner |
| **Background refresh** | Stale data visible; fetching updated version | Subtle loading indicator (top bar, icon pulse) |
| **Optimistic update** | Change applied speculatively; awaiting confirmation | No indicator (assume success) |
| **Mutation in flight** | Form submitted; waiting for response | Button disabled + spinner in button |
| **Paginating** | More data being loaded for infinite scroll | Spinner below the list |

**Skeleton vs. spinner decision**: skeletons reduce CLS and feel faster because
they reserve space and communicate the content structure. Use skeletons for
initial load of content areas. Use spinners for mutations and background refreshes.

Route to `ux-performance-perception` for the UX design of each state.

### Error Boundary Placement Strategy

Coarse-grained error boundaries (around route-level components) are the safety
net. Fine-grained boundaries (around individual widgets or data sections) allow
partial degradation — a failing chart doesn't unmount the entire page.

**Placement rule**: every independently-loaded section of UI should have its
own error boundary. On a dashboard: one per widget.

### Empty vs. Zero States

- **Empty state**: no data exists. Show a call-to-action: "No products yet — add
  your first product."
- **Zero state**: data exists but the current filters return nothing. Show a filter
  context: "No results for 'status: archived' — clear filter."
- **Error state**: data fetch failed. Show retry and support context.

Never render the same empty state for all three — they communicate different
things to the user.

### Suspense Integration

React Suspense + TanStack Query (with `suspense: true` option) or Apollo Client
(with `useSuspenseQuery`) allows the component to suspend while loading, and
the nearest `Suspense` boundary renders the fallback.

**When Suspense simplifies code**: eliminates `if (isLoading) return <Skeleton>`
guards inside every component. The component always receives resolved data.

**When Suspense complicates code**: waterfall fetches (parent suspends before
child's query is known), Suspense boundaries that are too coarse, interaction
with error boundaries requires careful co-placement.

---

## Anti-Patterns Reference

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| Direct `fetch` calls in components | No retry, no auth injection, hard to mock | Abstraction layer with interceptors |
| No runtime validation (TypeScript types only) | Silent incorrect data when API shape drifts | Zod parse at API boundary |
| Retrying 4xx errors | Repeats invalid requests, can cause duplicates | Only retry 429/503/network errors |
| WebSocket without reconnection logic | Silently stops receiving updates | Exponential backoff reconnection + reconnect UX |
| Same empty state for empty vs. zero vs. error | Confuses user about what action to take | Three distinct states with different messages and CTAs |
| Coarse-grained error boundary | One widget failure unmounts entire page | Per-widget error boundaries |
| Loading state flash (spinner visible for <100ms) | Jarring, worse than no indicator | Delay showing loading indicator by 200ms with CSS transition |

---

## Cross-Links

| Topic | Route to |
|-------|----------|
| State management above the fetch layer | `fe-state-management` |
| API contract, error envelope, versioning | `be-api-design` |
| WebSocket/SSE server implementation | `be-integration-patterns` |
| Loading state UX design, skeleton screens | `ux-performance-perception` |
| ML prediction endpoints, streaming inference | `ds-ml-engineering` |
