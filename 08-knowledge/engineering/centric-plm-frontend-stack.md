---
tags: [engineering, centric, frontend, typescript, react, npm, cds]
created: 2026-05-05
updated: 2026-05-05
status: stable
confidence: high
sources: [session-log 2026-05-05, 05-C8-PLM]
related_skills: [design-engineer, centric-ui-workflow]
related_projects: [05-C8-PLM]
---

# Centric PLM Frontend Stack — Engineering Quirks

Quirks and validated patterns for local development against `@centricsoftware/design-system` (CDS) as a `file:` linked package.

---

## `file:` link + @types/react version mismatch → TS2786

### Symptom
`TS2786: 'DataTable' cannot be used as a JSX component` when consuming CDS from a `file:../CDS` link.

### Root cause
CDS declares `@types/react@18.2.21` in its own `node_modules`. The consuming app had `@types/react@19.x`. npm `overrides` do **not** deduplicate `@types` inside a `file:` linked package's own node_modules — both versions coexist, and TypeScript picks up the mismatch when checking JSX element assignability.

The error is specifically `Type 'Element' is not assignable to type 'ReactNode | Promise<ReactNode>'` — React 19's `ReactNode` made `ReactPortal.children` required, which breaks components declared against React 18's `JSX.Element`.

### Fix
Pin the consuming app to the **same React version CDS targets** (`react@^18.3.1`, `@types/react@^18.3.x`). Do not rely on `overrides` to resolve this across a `file:` link boundary.

```json
{
  "dependencies": { "react": "^18.3.1", "react-dom": "^18.3.1" },
  "devDependencies": { "@types/react": "^18.3.12", "@types/react-dom": "^18.3.1" }
}
```

---

## CDS root `package.json` types field is wrong

CDS root `package.json` declares `"types": "./index.d.ts"` but that file does not exist at the repo root. The real typings are at `dist/index.d.ts`.

### Fix — tsconfig paths override

In the consuming app's `tsconfig.json`:

```json
{
  "compilerOptions": {
    "paths": {
      "@centricsoftware/design-system": ["../CDS/dist/index.d.ts"],
      "@centricsoftware/design-system/*": ["../CDS/dist/*"]
    }
  }
}
```

This is safe for local dev. Published tarball resolves correctly via `dist/package.json`.

---

## Circular type aliases in row types

### Symptom
`Type alias 'GridRow' circularly references itself` when using `type GridRow = DataTableRowType<GridRow> & { … }`.

### Fix
Use `interface` with `extends` instead:

```typescript
// Wrong — causes circular alias error
type GridRow = DataTableRowType<GridRow> & { id: string; … };

// Correct
interface GridRow extends DataTableRowType<GridRow> { id: string; … }
```

---

## Column renderer types exported from CDS

All TanStack types needed in consuming apps (`SortingState`, `ExpandedState`, `GroupingState`, `ColumnFiltersState`, `RowSelectionState`, `VisibilityState`) are **re-exported from `@centricsoftware/design-system`** and should be imported from there, not from `@tanstack/react-table` directly (which may not be hoisted into the app's `node_modules`).

---

## CDS DataTable API surface (TanStack Table 8)

Features available via `DataTable` props:

| Feature | Prop |
|---|---|
| Sorting | `enableSorting` + `sorting` / `onSortingChange` |
| Global + column filter | `enableFiltering` + `globalFilter` / `columnFilters` |
| Pagination | `enablePagination` + `pageSize` / `pageSizeOptions` |
| Row selection | `enableRowSelection` + `rowSelection` / `onRowSelectionChange` |
| Column visibility UI | `enableColumnVisibility` + `columnVisibility` / `onColumnVisibilityChange` |
| Column pinning | `columnPinning: { left: [], right: [] }` |
| Row pinning | `rowPinning: { top: [], bottom: [] }` |
| Grouping + aggregation | `grouping: GroupingConfig` (incl. `spanColumns`, `backgroundColor`) |
| Tree expand | `expandingConfig: ExpandingConfig` (incl. `stickyExpandedRows`) |
| Compare rows | `meta.compareCategory` + `meta.compareRow` + `cellsMeta[col].compareCategory` |
| Spans | `enableSpans` + `cellsMeta[col].rowSpan / colSpan` |
| Virtualization | `virtualization: { enabled, measureRows, overscan }` |
| Keyboard nav | `enableKeyboardNavigation` |
| Cell renderers | `meta.renderer: "text" | "link" | "linksList" | "richText"` |

**Not available:** column resize, built-in column DnD, built-in row DnD. Handle these at app state layer.
