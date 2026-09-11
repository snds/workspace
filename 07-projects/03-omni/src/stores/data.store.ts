// ─── Data Store ──────────────────────────────────────────────────────────────
// Zustand store for managing data sources, queries, results, and component
// bindings. Wraps DataSourceRegistry with reactive state.
// ──────────────────────────────────────────────────────────────────────────────

import { create } from "zustand";
import { immer } from "zustand/middleware/immer";
import { devtools } from "zustand/middleware";
import { DataSourceRegistry } from "@/core/data/registry";
import type {
  DataSource,
  DataQuery,
  QueryResult,
  ComponentDataBinding,
} from "@/core/data/types";

// ─── State ───────────────────────────────────────────────────────────────────

interface DataState {
  /** Internal registry instance (not serialised) */
  registry: DataSourceRegistry;
  /** Component-to-data bindings */
  bindings: ComponentDataBinding[];
  /**
   * Monotonically incrementing revision counter.
   * Bumped on every mutation so selectors re-render.
   */
  _revision: number;
}

// ─── Actions ─────────────────────────────────────────────────────────────────

interface DataActions {
  // Sources
  addSource(source: DataSource): void;
  removeSource(id: string): void;
  updateSourceStatus(
    id: string,
    status: DataSource["status"],
    error?: string,
  ): void;

  // Queries
  addQuery(query: DataQuery): void;
  removeQuery(id: string): void;
  setQueryResult(queryId: string, result: Partial<QueryResult>): void;

  // Bindings
  addBinding(binding: ComponentDataBinding): void;
  removeBinding(nodeId: string, propName: string): void;
  getBindingsForNode(nodeId: string): ComponentDataBinding[];

  // Reads
  getAllSources(): DataSource[];
  getSource(id: string): DataSource | undefined;
  getQuery(id: string): DataQuery | undefined;
  getQueriesForSource(sourceId: string): DataQuery[];
  getQueryResult(queryId: string): QueryResult | undefined;
  getAvailableFields(sourceId: string): string[];
}

// ─── Store ───────────────────────────────────────────────────────────────────

export const useDataStore = create<DataState & DataActions>()(
  devtools(
    immer((set, get) => ({
      registry: new DataSourceRegistry(),
      bindings: [],
      _revision: 0,

      // ── Sources ────────────────────────────────────────────────────────

      addSource: (source) =>
        set((s) => {
          s.registry.register(source);
          s._revision++;
        }),

      removeSource: (id) =>
        set((s) => {
          s.registry.unregister(id);
          // Remove bindings referencing this source
          s.bindings = s.bindings.filter((b) => b.sourceId !== id);
          s._revision++;
        }),

      updateSourceStatus: (id, status, error) =>
        set((s) => {
          s.registry.setStatus(id, status, error);
          s._revision++;
        }),

      // ── Queries ────────────────────────────────────────────────────────

      addQuery: (query) =>
        set((s) => {
          s.registry.registerQuery(query);
          s._revision++;
        }),

      removeQuery: (id) =>
        set((s) => {
          s.registry.removeQuery(id);
          s._revision++;
        }),

      setQueryResult: (queryId, result) =>
        set((s) => {
          s.registry.setResult(queryId, result);
          s._revision++;
        }),

      // ── Bindings ───────────────────────────────────────────────────────

      addBinding: (binding) =>
        set((s) => {
          // Replace existing binding for the same node+prop
          const idx = s.bindings.findIndex(
            (b) =>
              b.nodeId === binding.nodeId &&
              b.propName === binding.propName,
          );
          if (idx >= 0) {
            s.bindings[idx] = binding;
          } else {
            s.bindings.push(binding);
          }
          s._revision++;
        }),

      removeBinding: (nodeId, propName) =>
        set((s) => {
          s.bindings = s.bindings.filter(
            (b) => !(b.nodeId === nodeId && b.propName === propName),
          );
          s._revision++;
        }),

      getBindingsForNode: (nodeId) =>
        get().bindings.filter((b) => b.nodeId === nodeId),

      // ── Reads ──────────────────────────────────────────────────────────

      getAllSources: () => get().registry.getAll(),

      getSource: (id) => get().registry.get(id),

      getQuery: (id) => get().registry.getQuery(id),

      getQueriesForSource: (sourceId) =>
        get().registry.getQueriesForSource(sourceId),

      getQueryResult: (queryId) => get().registry.getResult(queryId),

      getAvailableFields: (sourceId) =>
        get().registry.getAvailableFields(sourceId),
    })),
    { name: "DataStore" },
  ),
);
