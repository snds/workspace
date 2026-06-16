---
name: fe-data-visualization
description: >
  Rendering charts, tables, dashboards, and large datasets in enterprise SaaS
  frontends. Use this skill whenever the conversation touches: chart library
  selection, D3.js, Recharts, ECharts, Highcharts, Observable Plot, Victory,
  data tables, TanStack Table, table sorting, filtering, grouping, pagination,
  column resize, column reorder, inline editing, row selection, virtual
  scrolling, TanStack Virtual, vue-virtual-scroller, windowing, overscan,
  dynamic row height, infinite scroll with virtualization, canvas rendering,
  WebGL charts, deck.gl, dashboard composition, react-grid-layout, CSS Grid
  layout, widget loading states, skeleton screens per widget, error boundaries
  per widget, cross-filter interactions, brushing, linked views, data-dense
  UIs, or any question about rendering, performing, and composing data-heavy
  surfaces in an enterprise context.
aliases: [fe-data-visualization]
tier: spoke
domain: engineering
hub: lead-frontend-engineer
prerequisites: [lead-frontend-engineer]
spec_version: "2.0"
---

# FE Data Visualization

Specialist lens for charts, tables, dashboards, and large-dataset rendering.
Part of the enterprise SaaS frontend engineering network.

---

## Domain Boundary

This skill owns **rendering fidelity, performance, and composition** of data
surfaces.

- **What to visualize, data encoding, chart type decisions** → `ux-data-visualization` + `ds-executive-storytelling`
- **Performance at scale (bundle size, rendering strategies)** → `fe-performance`
- **Cross-filter state architecture, server state for widgets** → `fe-state-management`
- **API pagination contracts, filtering query design** → `be-api-design`

**Always agree on chart type and data encoding with UX and DS before starting
implementation.** Chart type is a design decision; rendering it is an engineering
one. Both must coordinate.

---

## Charting Library Decision Matrix

| Library | Bundle (gzipped) | Customization | Accessibility | TypeScript | SSR | Best For |
|---------|-----------------|---------------|---------------|------------|-----|---------|
| **D3.js** | ~80kb | Maximum | Manual | Community types | Yes (with care) | Bespoke branded charts, custom interactions |
| **Recharts** | ~120kb | Medium | Partial | Good | Yes | Mid-complexity React charts, rapid iteration |
| **ECharts** | ~180kb (tree-shakeable) | High | Partial | Official | Yes | Dashboard-heavy products, large feature set |
| **Highcharts** | ~200kb | High | Best-in-class | Official | Yes | Enterprise compliance story, accessibility VPAT |
| **Observable Plot** | ~60kb | Grammar-based | Good | Official | Yes | Modern API, D3-backed, growing enterprise adoption |
| **Victory** | ~180kb | Medium | Good | Official | Yes | Multi-platform (React + React Native) |
| **Nivo** | Varies (modular) | High | Partial | Official | Yes | React-first, responsive, good D3 surface area |

### Decision Framework

**Start with the compliance question**: does your enterprise procurement require
a VPAT for accessibility? Highcharts has the strongest accessibility story and
an explicit VPAT. Recharts and D3 require significant manual work to reach WCAG AA.

**Customization ceiling**: if your design system requires non-standard chart
aesthetics (custom colors, unusual label placement, animated transitions), check
the library's customization ceiling before committing. Recharts hits its ceiling
quickly; D3 has no ceiling but requires building everything manually.

**Bundle size in context**: all major charting libraries are large. The question
is whether they appear in the initial bundle (wrong) or lazy-loaded behind a
`React.lazy` / `defineAsyncComponent` boundary (right). A 200kb chart library
loaded asynchronously on a dashboard route is not a performance problem.

**ECharts in practice**: JSON-driven configuration model is powerful for
dashboard-heavy products but creates a type-safety challenge. The config objects
are deeply nested and hard to type precisely. Use the official TypeScript types
and avoid raw `any` config objects.

**D3.js in enterprise SaaS**: prefer D3 only when you need something the
declarative libraries can't do — custom force simulations, geographic
projections, custom brush interactions. D3's learning curve and verbosity are
real costs. Observable Plot is D3-backed with a much more ergonomic API and
covers most common chart types.

---

## Table Rendering for Enterprise Data

### TanStack Table (the default choice)

Headless, framework-agnostic, handles sorting/filtering/grouping/pagination/
row-selection/column-visibility with a single coherent API. It's the right choice
for any table beyond a simple static list.

**Column definitions:**

```ts
import { createColumnHelper } from '@tanstack/react-table';

const columnHelper = createColumnHelper<Product>();

const columns = [
  columnHelper.accessor('name', {
    header: 'Product Name',
    cell: info => <Link to={`/products/${info.row.original.id}`}>{info.getValue()}</Link>,
    sortingFn: 'alphanumeric',
    filterFn: 'includesString',
    size: 240,
    minSize: 120,
  }),
  columnHelper.accessor('status', {
    header: 'Status',
    cell: info => <StatusBadge value={info.getValue()} />,
    filterFn: 'equalsString',
    enableSorting: false,
  }),
];
```

**Server-side sorting/filtering/pagination**: set `manualSorting: true`,
`manualFiltering: true`, `manualPagination: true`. Connect TanStack Table's
`sorting`, `columnFilters`, and `pagination` state to TanStack Query query keys
so table state changes automatically trigger refetches.

**Row selection with indeterminate state:**

```ts
columnHelper.display({
  id: 'select',
  header: ({ table }) => (
    <Checkbox
      checked={table.getIsAllPageRowsSelected()}
      indeterminate={table.getIsSomePageRowsSelected()}
      onChange={table.getToggleAllPageRowsSelectedHandler()}
      aria-label="Select all"
    />
  ),
  cell: ({ row }) => (
    <Checkbox
      checked={row.getIsSelected()}
      disabled={!row.getCanSelect()}
      onChange={row.getToggleSelectedHandler()}
      aria-label={`Select row ${row.index + 1}`}
    />
  ),
})
```

### Virtualization: Required Above ~500 Rows

Rendering 1000+ DOM rows is a CLS and INP disaster. TanStack Virtual (formerly
react-virtual) handles windowing — renders only the rows in the viewport plus
an overscan buffer.

```tsx
import { useVirtualizer } from '@tanstack/react-virtual';

function VirtualTable({ rows }) {
  const parentRef = useRef<HTMLDivElement>(null);

  const rowVirtualizer = useVirtualizer({
    count: rows.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 48,  // estimated row height
    overscan: 10,            // rows rendered beyond viewport edges
  });

  return (
    <div ref={parentRef} style={{ height: '600px', overflow: 'auto' }}>
      <table>
        <tbody
          style={{ height: `${rowVirtualizer.getTotalSize()}px`, position: 'relative' }}
        >
          {rowVirtualizer.getVirtualItems().map(virtualRow => (
            <tr
              key={rows[virtualRow.index].id}
              style={{
                position: 'absolute',
                top: 0,
                transform: `translateY(${virtualRow.start}px)`,
                height: `${virtualRow.size}px`,
              }}
            >
              {/* cells */}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
```

**Dynamic row heights**: use `measureElement` callback instead of `estimateSize`
when row heights vary. The virtualizer measures each rendered row and recalculates
positions after measurement.

### Fixed Headers + Frozen Columns

Pure CSS approach for fixed headers: `position: sticky; top: 0` on `<thead>`.
Requires the scroll container to be the `<div>` wrapping the table, not `<body>`.

Frozen columns: `position: sticky; left: {offset}px` on each frozen cell.
Calculate the `left` value from accumulated column widths. Add a box-shadow
on the last frozen column to visually separate it from scrolling columns.

**Anti-pattern**: implementing frozen columns with two separate tables (one fixed,
one scrolling) and synchronizing scroll. This is fragile, causes accessibility
problems, and creates visual artifacts. Use sticky CSS.

### Inline Editing Pattern

Cell-level edit mode: clicking a cell switches it from a read view to an edit
control (input, select, datepicker). Design requirements:

1. **Single active edit** or **multi-active edit** — decide upfront. Single active
   is simpler; multi-active requires managing a Set of editing cell IDs.
2. **Save on blur** or **save on confirm** — save-on-blur is faster but risks
   accidental saves. For enterprise data, save on confirm (Enter key or explicit
   save button in the cell) is safer.
3. **Optimistic update**: apply the change to local state immediately, sync to
   server in background, rollback on error (see `fe-state-management`).
4. **Validation**: inline cell validation with clear error state — border color
   change + tooltip error message is the conventional pattern.

---

## Large Dataset Rendering

### Thresholds for Technology Choice

| Row Count | Strategy |
|-----------|---------|
| < 200 | Standard DOM rendering, no virtualization needed |
| 200–2000 | TanStack Virtual (DOM windowing) |
| 2000–10k | TanStack Virtual + aggressive memoization of row renders |
| 10k–100k | Consider canvas rendering (HTML5 Canvas) for the data body |
| 100k+ | WebGL rendering (deck.gl, regl) or server-side pagination required |

### Canvas Rendering for Data-Dense Tables

When DOM virtualization isn't enough (very high row counts, real-time streaming
data, 60fps interactions): render the data body on a `<canvas>` element, keep
only the interactive overlay (column headers, scrollbar, selected row highlight)
in the DOM.

Tradeoffs: accessibility requires a parallel accessible representation (usually
an ARIA live region or offscreen table for screen readers), text selection is
lost, custom tooltips must be implemented manually.

### WebGL for Data-Dense Visualizations

For scatter plots or heatmaps with 10k+ data points: the SVG/DOM rendering
model breaks down. Options:

- **deck.gl**: declarative WebGL layers. Scales to millions of data points.
  Strong for geographic and spatial data. React integration available.
- **regl**: functional WebGL. Lower-level, more control, steeper curve.
- **Vega-Lite + Vega**: grammar-of-graphics approach that can switch to Canvas
  rendering automatically above threshold.

In enterprise SaaS, WebGL is rarely necessary — if you're rendering 10k+ points
in a scatter, the visualization design is probably wrong (aggregation or
sampling should happen at the data layer). Route to `ds-executive-storytelling`
if the data density is a design question.

---

## Dashboard Composition

### Grid Layout

**CSS Grid** for static or responsive dashboards (layouts defined at build time).
Define named areas, let the browser handle placement.

**react-grid-layout** for draggable/resizable dashboards where users can
configure their own layout. Persisting layout: serialize to JSON, store in user
preferences (server-side for persistence across devices).

### Widget Loading States

Each widget must have its own loading, error, and empty state. A single top-level
spinner for a dashboard that loads 8 widgets is wrong — some widgets load in
200ms, some take 2s. Use per-widget `Suspense` boundaries (React) or Vue
`Suspense` to manage individual loading states.

**Skeleton screens**: skeleton dimensions must match the rendered widget's
dimensions. If the skeleton is a different size than the widget content,
it causes CLS. Design and engineering must agree on skeleton sizing.

### Error Boundaries Per Widget

Wrap each dashboard widget in an `ErrorBoundary`. A chart widget failing to
fetch should not unmount the entire dashboard. The error boundary renders a
degraded state: "This widget could not load — retry" with a retry button that
calls `queryClient.invalidateQueries` for that widget's data.

### Cross-Filter Interactions

When filtering one chart updates the data visible in others (linked views):

1. Store the active filter(s) in a shared state atom or store
2. Each widget's query key includes the shared filter state
3. When filter changes, TanStack Query refetches all affected queries in parallel
4. During refetch, show a loading overlay on the affected widgets (not full
   skeleton replacement — the current data remains visible while refetching)

**Brushing**: selection range drawn on one chart constrains data in others.
The brush state is URL-serializable for shareable filter states.

---

## Anti-Patterns Reference

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| Rendering 500+ rows without virtualization | INP and paint time regression, janky scroll | TanStack Virtual above 500 rows |
| Chart library in the initial bundle | Adds 100–200kb to first load | `React.lazy` / `defineAsyncComponent` on dashboard route |
| Two-table frozen column approach | Accessibility gaps, scroll sync fragility | `position: sticky` CSS |
| Single spinner for multi-widget dashboard | All widgets appear broken if one is slow | Per-widget Suspense + error boundaries |
| Skeleton with wrong dimensions | CLS when content loads | Agree on skeleton sizing with design; match content dimensions exactly |
| Array index as row key in virtual list | Scroll position jumps when data updates | Use stable data ID as key |
| D3.js for basic bar/line charts | High complexity cost for low customization need | Recharts or Observable Plot for standard chart types |

---

## Cross-Links

| Topic | Route to |
|-------|----------|
| What to visualize, data encoding, chart type | `ux-data-visualization` |
| Why to visualize it, executive/stakeholder framing | `ds-executive-storytelling` |
| Rendering performance at extreme scale | `fe-performance` |
| Cross-filter state, server state per widget | `fe-state-management` |
| Chart interaction event instrumentation | `ds-product-analytics` |
