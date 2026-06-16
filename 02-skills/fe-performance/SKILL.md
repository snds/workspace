---
name: fe-performance
description: >
  Core Web Vitals, bundle optimization, rendering strategy selection, and
  performance measurement for enterprise SaaS frontends. Use this skill whenever
  the conversation touches: Core Web Vitals, LCP, INP, CLS, TTFB, FID, bundle
  size, code splitting, tree shaking, lazy loading, dynamic imports, webpack-
  bundle-analyzer, source-map-explorer, SSR, CSR, SSG, streaming SSR, ISR,
  hydration, image optimization, WebP, AVIF, srcset, font performance, font-
  display, runtime performance, React DevTools Profiler, Vue DevTools performance,
  unnecessary re-renders, Lighthouse, Lighthouse CI, Web Vitals, performance
  budgets, bundlesize, size-limit, module federation, micro-frontend performance,
  barrel files, side effects, or any question about making an enterprise SaaS
  UI measurably faster under real user conditions.
---

# FE Performance

Specialist lens for frontend performance measurement, optimization, and rendering
strategy. Part of the enterprise SaaS frontend engineering network.

---

## Domain Boundary

This skill owns **technical performance measurement and optimization**.

- **Perceived performance UX** (skeleton screens, optimistic UI design) → `ux-performance-perception`
- **CDN strategy, cache headers, server response time** → `be-caching-performance`
- **Web Vitals as instrumented product analytics** → `ds-product-analytics`
- **Loading state taxonomy (what to show when)** → `fe-api-integration` + `ux-performance-perception`

---

## Core Web Vitals: What They Actually Measure

### LCP — Largest Contentful Paint

Measures: time until the **largest image or text block** visible in the viewport
has rendered. The "largest" element is re-evaluated as the page loads; it often
lands on a hero image, a large heading, or (in SaaS) a table or dashboard widget.

**What causes LCP to be slow:**
- The LCP element is in the DOM but its resource (image, font) loads late
- HTML is slow to arrive (high TTFB blocks everything)
- LCP image is not preloaded — browser discovers it late in the parse
- LCP element is rendered client-side only (CSR adds JS parse/execute cost)

**Optimization levers:**
- `<link rel="preload">` for the LCP image — must be in `<head>` before any scripts
- `fetchpriority="high"` on the LCP `<img>` — signals to the browser's preload scanner
- SSR or SSG to put the LCP element in initial HTML
- CDN for static assets — reduces physical distance latency
- Eliminate render-blocking resources above the LCP element

**Measuring**: Chrome DevTools Performance panel → "Timings" row. `web-vitals`
library reports LCP in field data. Target: <2.5s (good), 2.5–4s (needs
improvement), >4s (poor).

---

### INP — Interaction to Next Paint

Replaced FID in March 2024. Measures: the 98th percentile interaction-to-paint
latency across all interactions during a page visit. An interaction is click,
key press, or tap — it ends when the browser has committed a frame in response.

**What causes high INP:**
- Long tasks blocking the main thread during interaction (>50ms = long task)
- Synchronous DOM reads that force reflow during event handlers
- Expensive state updates that trigger deep re-renders
- Heavy third-party scripts competing for main thread time
- Unoptimized event handlers that do too much synchronous work

**Optimization levers:**
- Break up long tasks: `scheduler.yield()` (Chrome 115+), `setTimeout(fn, 0)`,
  `requestIdleCallback` for non-critical work
- React concurrent features: `useTransition` wraps non-urgent state updates,
  preventing them from blocking the interaction response
- `useDeferredValue` for expensive derived computations that don't need to
  block the primary UI update
- Memoization: `React.memo`, `useMemo`, `useCallback` — but profile first,
  memoization adds overhead when the equality check is expensive
- Virtual DOM libraries (Preact, Solid) don't inherently solve INP — the
  bottleneck is usually long tasks, not diffing

**Measuring**: Performance panel → "Long Tasks" (red chevrons). PerformanceObserver
with `{ type: 'event', buffered: true }` for local measurement. Target: <200ms (good).

---

### CLS — Cumulative Layout Shift

Measures: sum of all unexpected layout shift scores during the page's lifetime.
A shift score = impact_fraction × distance_fraction. Enterprise dashboards with
many independently-loading widgets are CLS magnets.

**Common causes:**
- Images or embeds without explicit `width`/`height` (or `aspect-ratio`) — browser
  doesn't reserve space, content jumps when resource loads
- Dynamic content injection above existing content (banners, notification bars,
  late-loading ads or chat widgets)
- Web fonts causing FOUT (Flash of Unstyled Text) that shifts surrounding text
- Skeleton screens with dimensions that don't match final content — a skeleton
  that's 48px tall replaced by content that's 64px tall causes CLS

**Fixes:**
- Always set `width` + `height` on images, even in responsive contexts (aspect-ratio
  is preserved by CSS)
- `font-display: optional` eliminates FOUT by not swapping if font isn't cached;
  `font-display: swap` is better for UX but causes CLS on uncached visits
- Reserve space for dynamic content via CSS `min-height` or skeleton components
  sized to match actual content dimensions
- `transform` animations don't cause CLS; `top`/`left`/`margin` animations do

**Measuring**: Chrome DevTools → Performance → "Layout Shift" records. Target: <0.1.

---

### TTFB — Time to First Byte

Measures: time until the browser receives the first byte of the HTML response.
High TTFB is the root cause of slow LCP on server-rendered pages.

**Optimization levers:**
- CDN edge caching for static or SSG pages
- Streaming SSR: flush initial HTML before data is fully fetched (React 18
  `renderToPipeableStream`, Next.js streaming, Nuxt streaming)
- Reduce origin server response time: connection pooling, query optimization,
  async rendering pipelines

---

## Rendering Strategies

| Strategy | When It Fits | Main Cost |
|----------|-------------|-----------|
| **CSR** (Client-Side Rendering) | Auth-gated SaaS apps, highly interactive, no SEO need | Full JS bundle cost before any content appears; LCP limited by JS execution |
| **SSR** (Server-Side Rendering) | SEO-critical pages, data-heavy initial render, TTFB-critical | Hydration cost; server under load for every request |
| **SSG** (Static Site Generation) | Content-stable pages (docs, marketing) | Rebuild required on content change; poor fit for personalized SaaS data |
| **Streaming SSR** | Data-heavy SaaS pages needing fast TTFB + good INP | Framework support required; async shell design complexity |
| **ISR** (Incremental Static Regeneration) | Semi-static content (product catalog, reports) | Stale data window acceptable; Next.js/Nuxt specific |

**For enterprise SaaS applications behind auth**: CSR is typically fine. The
"first paint" is a loading state or skeleton, not meaningful content. Optimize
for TTI (Time to Interactive) rather than LCP, and invest in SSR only where
cold load performance affects retention or contract compliance.

**Streaming SSR** is the right answer when you need SSR-class TTFB but have
async data fetching requirements. React 18 `<Suspense>` + `renderToPipeableStream`
lets you flush the shell immediately and stream content shells as they resolve.

---

## Bundle Optimization

### Code Splitting Strategies

**Route-based splitting** (always): each route gets its own chunk. Next.js and
Nuxt do this automatically. For manual Vite/webpack setups, `React.lazy` +
`<Suspense>` or Vue's `defineAsyncComponent` wraps route components.

**Component-level splitting**: for heavy components not needed on first render
(rich text editors, chart libraries, PDF viewers, code editors). Wrap in
`React.lazy` / `defineAsyncComponent` with a meaningful loading state.

**Vendor chunk strategy**: split vendor code from application code so that
framework updates (React, Vue, lodash) don't bust application code cache.
Vite does this automatically; webpack requires manual `splitChunks` config.

**Common mistake**: over-splitting into too many small chunks. Each additional
round-trip has latency cost. Chunks under ~15kb (gzipped) are usually not
worth splitting.

### Tree Shaking

Requires ESM (`import`/`export`), not CJS (`require`/`module.exports`). Tree
shaking is the bundler's ability to eliminate exports that are never imported.

**The barrel file problem**: `index.ts` re-exports that import everything from
every module (`export * from './Button'`, `export * from './Table'`, ...) force
the bundler to include every module in the graph even when only one is used.
This is the single most common cause of large bundles in design system consumers.

Fix: import directly from the module path (`import { Button } from 'ds/Button'`),
or ensure the DS package has proper `sideEffects: false` annotation and uses
named exports rather than barrel re-exports.

**`sideEffects` in package.json**: mark packages as side-effect-free to allow
tree shaking of unused modules. CSS imports are side effects — list them
explicitly: `"sideEffects": ["*.css", "*.scss"]`.

### Bundle Analysis

```bash
# Vite
vite build --mode analyze  # or use vite-plugin-visualizer

# webpack
webpack-bundle-analyzer stats.json
```

**What to look for:**
- Duplicated dependencies at different versions (lodash, moment, etc.)
- Heavy libraries included in full (lodash should be lodash-es with tree shaking)
- Unexpectedly large vendor chunks (moment.js at 67kb vs. date-fns at <5kb for the same features)
- Barrel imports pulling in the entire DS
- Test code or dev-only code included in production bundle

### Dynamic Imports

Use `import()` for non-critical code paths:

```ts
// Prefetch on hover (load before user clicks)
button.addEventListener('mouseenter', () => {
  import('./HeavyModal');
});

// Import on interaction
button.addEventListener('click', async () => {
  const { HeavyModal } = await import('./HeavyModal');
  // render
});
```

`<link rel="prefetch">` and `<link rel="preload">` as HTML hints for
critical next-page assets. Prefetch = low priority, future navigation.
Preload = high priority, current page.

---

## Image Optimization

- **Modern formats**: WebP (90%+ browser support), AVIF (better compression,
  growing support). Serve AVIF with WebP fallback via `<picture>`.
- **Responsive images**: `srcset` + `sizes` attributes for responsive serving.
  The browser chooses the smallest image that satisfies the display density.
- **LCP image**: never lazy-load it. Add `fetchpriority="high"` and preload it.
- **Below-fold images**: `loading="lazy"` prevents loading until the image is
  near the viewport.
- **Dimensions**: always set `width` + `height` to avoid CLS.

---

## Font Performance

- **`font-display: swap`**: shows fallback immediately, swaps when font loads.
  Best UX for visible text. Causes minor CLS on first visit — mitigate with
  `size-adjust` and `ascent-override` on the fallback font to match metrics.
- **`font-display: optional`**: only uses the font if it's cached. No FOUT, no
  CLS, but first-visit users may always see the fallback. Good choice for
  enterprise SaaS where users return daily.
- **Preload critical fonts**: `<link rel="preload" as="font">` for the primary
  UI font. Only preload what's used above the fold.
- **Subsetting**: for enterprise SaaS, Latin + any custom glyph range is
  usually sufficient. Removes unused character ranges from the font file.

---

## Runtime Performance

### What to Profile Before Optimizing

React DevTools Profiler → record an interaction → look for:
- Components that re-render without prop changes (missing `React.memo`)
- Components with large render time (expensive computation in render body)
- Components that re-render on every keystroke (missing `useMemo`/`useCallback`)

Vue DevTools → Performance tab → same analysis.

**Before adding `useMemo`**: confirm the computation is actually expensive. The
overhead of the memo check is real. `useMemo` for a string concatenation is
negative optimization.

### Avoiding Unnecessary Re-renders

Common causes:
- Anonymous function or object literals as props — new reference on every render
- Context value that is a new object literal every render (wrap in `useMemo`)
- State updates that trigger parent re-render, causing children to re-render
  unnecessarily (push state down or use `memo`)

---

## Performance Budgets in CI

**Lighthouse CI**: run Lighthouse against a staging URL on every PR, enforce
thresholds per route. Fail the build if LCP exceeds 3s or CLS exceeds 0.1.

**bundlesize / size-limit**: enforce bundle size budgets per chunk on PR. The
PR diff shows `+12kb` to the main bundle before it lands.

**Web Vitals in production**: `web-vitals` library reports field data from real
users. Send to your analytics stack. CrUX (Chrome UX Report) gives 28-day
rolling field data for public URLs.

---

## Anti-Patterns Reference

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| Barrel file re-exports in DS | Kills tree shaking, bloats every consumer | Direct imports or `sideEffects: false` + named exports |
| Lazy loading LCP image | LCP delayed until scroll trigger | Remove `loading="lazy"` on LCP element |
| Memoizing cheap computations | Overhead exceeds benefit | Profile first; memo only expensive derivations |
| Optimizing without measuring | Effort spent on non-bottlenecks | Profiler + Lighthouse before any perf work |
| SSR for auth-gated SaaS with no SEO need | Hydration cost without user-facing benefit | CSR + fast API responses + good skeleton screens |
| Images without dimensions | CLS on load | Always set width/height attributes |
| Moment.js in new code | 67kb minified, no tree shaking | date-fns (tree-shakeable) or Temporal polyfill |

---

## Cross-Links

| Topic | Route to |
|-------|----------|
| Perceived performance, skeleton screen design | `ux-performance-perception` |
| CDN headers, server response time, cache strategy | `be-caching-performance` |
| Web Vitals instrumentation as product analytics | `ds-product-analytics` |
| Loading state taxonomy (skeleton vs. spinner decisions) | `fe-api-integration` |
| Virtual scrolling for large datasets | `fe-data-visualization` |
