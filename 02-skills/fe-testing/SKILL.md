---
name: fe-testing
description: >
  Component testing, visual regression, E2E testing, accessibility testing
  automation, and performance budgets in CI for enterprise SaaS frontends.
  Use this skill whenever the conversation touches: component testing, Testing
  Library, React Testing Library, Vue Test Utils, getByRole, getByLabelText,
  userEvent, fireEvent, waitFor, findBy, MSW, Mock Service Worker, visual
  regression, Chromatic, Percy, Playwright screenshots, toHaveScreenshot,
  E2E testing, Playwright, Cypress, Page Object Model, page.route, trace viewer,
  test parallelization, jest-axe, axe-core, Playwright accessibility, Storybook,
  CSF3, play functions, interaction tests, a11y addon, Storybook autodocs,
  Vitest, Jest, Lighthouse CI, bundlesize, size-limit, Web Vitals in CI,
  snapshot testing, or any question about testing strategy, test quality, or
  CI integration for a frontend application.
---

# FE Testing

Specialist lens for frontend testing strategy, component testing, visual
regression, E2E, and CI quality gates. Part of the enterprise SaaS frontend
engineering network.

---

## Domain Boundary

This skill owns **test strategy, test patterns, and CI quality gates**.

- **Accessibility implementation (ARIA, keyboard nav)** → `fe-accessibility`
- **Performance optimization (what causes issues)** → `fe-performance`
- **Storybook as design system documentation strategy** → `ux-design-systems`

---

## Testing Pyramid for Frontend

```
         ╔═══════════════╗
         ║    E2E Tests   ║  ← Few, slow, highest confidence
         ╠═══════════════╣
         ║Visual Regression║ ← Per component, per state
         ╠═══════════════╣
         ║Integration Tests║ ← Multi-component flows
         ╠═══════════════╣
         ║ Component Tests ║ ← Isolated behavior + DOM
         ╠═══════════════╣
         ║   Unit Tests   ║  ← Many, fast, pure functions
         ╚═══════════════╝
```

| Layer | Tools | Speed | Confidence | Best For |
|-------|-------|-------|-----------|---------|
| Unit | Vitest, Jest | ~ms | Medium | Pure functions, utilities, stores, derived state |
| Component | Vitest + Testing Library, Vue Test Utils | ~seconds | High | Component behavior, DOM interaction, form validation |
| Integration | Vitest + MSW | ~seconds | High | Multi-component flows, routing, API boundary |
| E2E | Playwright (preferred), Cypress | ~minutes | Highest | Critical user flows, auth, cross-page workflows |
| Visual regression | Chromatic, Playwright screenshots | ~minutes | High | Component visual states, design system compliance |

**The most common testing mistake in enterprise SaaS**: over-investing in E2E
tests at the expense of component tests. E2E tests are slow, flaky under CI
infrastructure variance, and hard to debug. A component test that covers the
same behavior runs 100x faster and pinpoints failures precisely.

Invest in the component and integration layers first.

---

## Component Testing with Testing Library

### Query Priority

Testing Library encourages testing what users experience, not implementation
details. Queries in priority order:

1. **`getByRole`** — most accessible query, matches ARIA roles:
   `getByRole('button', { name: 'Submit' })`
   `getByRole('combobox', { name: 'Status' })`
   `getByRole('row', { name: /Product A/ })`

2. **`getByLabelText`** — for form controls associated with labels:
   `getByLabelText('Email address')`

3. **`getByPlaceholderText`** — fallback when label isn't available

4. **`getByText`** — for non-interactive elements, links by text:
   `getByText('No results found')`

5. **`getByTestId`** — last resort when the element has no accessible
   semantic. Requires a `data-testid` attribute. Use sparingly — it's
   an implementation detail and doesn't reflect user experience.

**Anti-pattern**: `getByTestId` for everything. If you need a test ID to find
a button, the button probably lacks an accessible name and you've found a bug.

### User Event vs. fireEvent

`userEvent` from `@testing-library/user-event` simulates real browser events
including the full event sequence (pointerdown → mousedown → focus → pointerup
→mouseup → click → blur). `fireEvent` dispatches a single synthetic event.

Use `userEvent` for all user interactions. `fireEvent` is appropriate only for
programmatically firing events that don't have a user-event equivalent.

```ts
import userEvent from '@testing-library/user-event';

const user = userEvent.setup();  // v14+: setup() for configured instance

it('filters the list on input', async () => {
  render(<ProductFilter />);
  await user.type(screen.getByRole('textbox', { name: 'Search' }), 'Widget');
  await waitFor(() => {
    expect(screen.getByRole('row', { name: /Widget Pro/ })).toBeInTheDocument();
    expect(screen.queryByRole('row', { name: /Gadget/ })).not.toBeInTheDocument();
  });
});
```

### Async Assertions

Never use `setTimeout` or `sleep` in tests. Use `waitFor` (retries until
the assertion passes or times out) or `findBy*` queries (async versions that
wait for the element to appear):

```ts
// waitFor: for assertions that may take time to become true
await waitFor(() => expect(screen.getByText('Saved')).toBeInTheDocument());

// findBy*: for elements expected to appear asynchronously
const notification = await screen.findByRole('status', { name: /saved/i });
```

**`waitFor` pitfall**: wrapping multiple assertions in one `waitFor` — if the
first assertion passes but a later one fails and then passes, `waitFor` won't
retry correctly. One assertion per `waitFor`.

### MSW (Mock Service Worker)

MSW intercepts requests at the service worker / Node.js level, not at the module
level. This makes API mocking realistic — your `fetch` calls go through the
actual network stack (minus the real server).

```ts
import { http, HttpResponse } from 'msw';
import { setupServer } from 'msw/node';

const server = setupServer(
  http.get('/api/products', () => {
    return HttpResponse.json({
      items: [{ id: '1', name: 'Widget Pro', status: 'active' }],
      nextCursor: null,
    });
  }),
  http.get('/api/products/:id', ({ params }) => {
    return HttpResponse.json({ id: params.id, name: 'Widget Pro' });
  }),
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());  // clean per-test overrides
afterAll(() => server.close());

// Per-test override for error states
it('shows error state when fetch fails', async () => {
  server.use(
    http.get('/api/products', () => HttpResponse.error())
  );
  render(<ProductList />);
  await screen.findByText('Could not load products');
});
```

**Why MSW over module mocking**: module mocks require matching import paths
exactly, break on refactors, and don't test the actual fetch/error handling
logic. MSW mocks the network, so the actual API client code runs in tests.

### Testing Accessibility in Components

```ts
import { axe, toHaveNoViolations } from 'jest-axe';

expect.extend(toHaveNoViolations);

it('has no accessibility violations', async () => {
  const { container } = render(<ProductForm />);
  const results = await axe(container);
  expect(results).toHaveNoViolations();
});
```

Combine with specific accessibility assertions:

```ts
it('associates error message with input', () => {
  render(<ProductForm />);
  const input = screen.getByRole('textbox', { name: 'Product name' });
  expect(input).toHaveAttribute('aria-invalid', 'true');
  expect(input).toHaveAccessibleDescription('Name is required');
});
```

---

## Visual Regression Testing

### Chromatic (Storybook Integration)

Chromatic captures a screenshot of every story on every PR and compares to the
baseline. Reviewers approve or reject visual changes. Best-in-class workflow for
DS component development.

**Setup**: stories are the source of truth for component states. Every variant,
every interactive state, every loading/error state should be a story.

**Baseline management**: the "accepted" baseline advances when a reviewer
approves a change. Unapproved changes block the PR.

**Cost management**: use `disableSnapshot` for stories that are purely
documentation (no visual output) or stories that are flaky due to animation.

### Playwright Visual Comparison

For E2E-level visual regression (page-level screenshots, not per-component):

```ts
test('product list page matches snapshot', async ({ page }) => {
  await page.goto('/products');
  await page.waitForLoadState('networkidle');

  // Mask dynamic content (dates, IDs) to prevent false positives
  await expect(page).toHaveScreenshot('product-list.png', {
    mask: [page.locator('[data-testid="relative-date"]')],
    maxDiffPixels: 100,
  });
});
```

**Flakiness sources**: animations not completed, fonts loading asynchronously,
date/time values, external images. Fix by: disabling animations in test mode
(`prefers-reduced-motion: reduce`), using `page.waitForLoadState('networkidle')`,
and masking dynamic content.

---

## Playwright E2E

### Page Object Model

Decouples test logic from DOM selectors. When the DOM changes, only the Page
Object needs updating:

```ts
// page-objects/ProductsPage.ts
export class ProductsPage {
  constructor(private page: Page) {}

  async navigate() {
    await this.page.goto('/products');
    await this.page.waitForLoadState('networkidle');
  }

  async searchFor(query: string) {
    await this.page.getByRole('textbox', { name: 'Search products' }).fill(query);
    await this.page.keyboard.press('Enter');
  }

  async getVisibleProductNames(): Promise<string[]> {
    return this.page
      .getByRole('row')
      .filter({ hasNot: this.page.getByRole('columnheader') })
      .getByRole('cell', { name: /.+/ })
      .allTextContents();
  }

  getProductRow(name: string) {
    return this.page.getByRole('row', { name: new RegExp(name) });
  }
}

// test file
test('search filters product list', async ({ page }) => {
  const products = new ProductsPage(page);
  await products.navigate();
  await products.searchFor('Widget');
  const names = await products.getVisibleProductNames();
  expect(names.every(n => n.includes('Widget'))).toBe(true);
});
```

### Network Interception

```ts
test('shows error state when API is down', async ({ page }) => {
  await page.route('/api/products**', route => route.abort('failed'));
  await page.goto('/products');
  await expect(page.getByRole('alert')).toContainText('Could not load products');
});

// Fixture-based response
await page.route('/api/products', route => route.fulfill({
  status: 200,
  contentType: 'application/json',
  body: JSON.stringify(productsFixture),
}));
```

### Accessibility in E2E

```ts
import AxeBuilder from '@axe-core/playwright';

test('products page has no accessibility violations', async ({ page }) => {
  await page.goto('/products');
  const results = await new AxeBuilder({ page })
    .withTags(['wcag2a', 'wcag2aa', 'wcag21aa'])
    .analyze();
  expect(results.violations).toEqual([]);
});
```

### Parallelization and Isolation

Playwright runs tests in parallel by default across workers. Requirements for
parallelization:
- Tests must be independently runnable — no shared state between tests
- Each test provisions its own data or uses seeded fixtures
- Database/API state is reset between test runs (use `beforeEach` API calls or
  test-specific fixtures)

**Sharding in CI**: split the test suite across multiple CI workers:

```yaml
# GitHub Actions
strategy:
  matrix:
    shardIndex: [1, 2, 3, 4]
    shardTotal: [4]
steps:
  - run: npx playwright test --shard=${{ matrix.shardIndex }}/${{ matrix.shardTotal }}
```

### Trace Viewer

Playwright's trace viewer records every action, network request, and DOM snapshot.
Run with `--trace on` for flaky tests:

```bash
npx playwright test --trace on
npx playwright show-trace trace.zip
```

Invaluable for debugging CI failures that don't reproduce locally.

---

## Storybook as the Testing Hub

### Stories as the Source of Truth

Every component variant and state should have a story. This is the foundation
for:
- **Visual regression** (Chromatic)
- **Interaction testing** (play functions)
- **Accessibility checks** (a11y addon)
- **Documentation** (autodocs)

### CSF3 Interaction Tests (Play Functions)

```ts
// Button.stories.ts
import type { Meta, StoryObj } from '@storybook/react';
import { userEvent, within, expect } from '@storybook/test';

const meta: Meta<typeof Button> = { component: Button };
export default meta;

type Story = StoryObj<typeof Button>;

export const LoadingState: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const button = canvas.getByRole('button', { name: 'Submit' });

    await userEvent.click(button);

    await expect(button).toHaveAttribute('aria-busy', 'true');
    await expect(button).toBeDisabled();
  },
};
```

Play functions run in the browser, use the actual DOM, and can test real user
interactions. They run in Storybook's test runner (`@storybook/test-runner`)
and can be run in CI.

### a11y Addon

The Storybook a11y addon runs axe-core on every story automatically. Configure
per-story if a known violation is acceptable:

```ts
export const DisabledButton: Story = {
  parameters: {
    a11y: {
      config: {
        rules: [{ id: 'color-contrast', enabled: false }],  // document why
      },
    },
  },
};
```

---

## Performance Testing in CI

### Lighthouse CI

```yaml
# .lighthouserc.yml
ci:
  collect:
    url:
      - http://localhost:3000/products
      - http://localhost:3000/dashboard
  assert:
    assertions:
      'categories:performance': ['error', { minScore: 0.9 }]
      'first-contentful-paint': ['error', { maxNumericValue: 2000 }]
      'cumulative-layout-shift': ['error', { maxNumericValue: 0.1 }]
      'total-blocking-time': ['error', { maxNumericValue: 300 }]
```

### Bundle Size Budgets

`size-limit` enforces bundle size per chunk on PR. Fails the build when a PR
adds too much to the bundle:

```json
// .size-limit.json
[
  { "path": "dist/main.js", "limit": "150 kB" },
  { "path": "dist/vendors.js", "limit": "300 kB" }
]
```

---

## Anti-Patterns Reference

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| `getByTestId` for everything | Tests implementation, not user experience; doesn't catch accessibility issues | Use `getByRole` and semantic queries first |
| `fireEvent.click` instead of `userEvent.click` | Skips focus/blur events, misses real browser behavior | `userEvent.click` (or `userEvent.setup().click()`) |
| Arbitrary `setTimeout` in tests | Flaky under slow CI runners | `waitFor` or `findBy*` |
| Module mocking for API calls | Doesn't test actual fetch/error handling code | MSW for all API mocking |
| E2E tests for component-level behavior | Slow, brittle, disproportionate | Component tests for component logic; E2E for user flows |
| Visual regression without masking dynamic content | Flaky snapshots due to dates, IDs | Mask all dynamic content before snapshot |
| Skipping a11y testing in CI | Accessibility regressions ship undetected | jest-axe in component tests, axe-core in E2E |

---

## Cross-Links

| Topic | Route to |
|-------|----------|
| ARIA implementation patterns being tested | `fe-accessibility` |
| Performance budgets and what they measure | `fe-performance` |
| Storybook as design system documentation | `ux-design-systems` |
