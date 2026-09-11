// ─── Data Source Registry ────────────────────────────────────────────────────
// Central registry for managing data sources, queries, and their results.
// Used by the Zustand store and adapters to coordinate data flow.
// ──────────────────────────────────────────────────────────────────────────────

import type {
  DataSource,
  DataQuery,
  QueryResult,
  DataSchema,
  DataField,
} from "./types";

/** Registry for managing data sources and their connections */
export class DataSourceRegistry {
  private sources: Map<string, DataSource> = new Map();
  private queries: Map<string, DataQuery> = new Map();
  private results: Map<string, QueryResult> = new Map();

  // ─── Data Sources ────────────────────────────────────────────────────────

  /** Register a data source */
  register(source: DataSource): void {
    this.sources.set(source.id, source);
  }

  /** Remove a data source and its associated queries/results */
  unregister(id: string): void {
    this.sources.delete(id);

    // Clean up associated queries and results
    for (const [queryId, query] of this.queries) {
      if (query.sourceId === id) {
        this.queries.delete(queryId);
        this.results.delete(queryId);
      }
    }
  }

  /** Get a data source by ID */
  get(id: string): DataSource | undefined {
    return this.sources.get(id);
  }

  /** Get all registered data sources */
  getAll(): DataSource[] {
    return Array.from(this.sources.values());
  }

  /** Update a data source's status */
  setStatus(
    id: string,
    status: DataSource["status"],
    error?: string,
  ): void {
    const source = this.sources.get(id);
    if (!source) return;

    source.status = status;
    source.error = error;
    this.sources.set(id, source);
  }

  /** Set the schema for a data source */
  setSchema(id: string, schema: DataSchema): void {
    const source = this.sources.get(id);
    if (!source) return;

    source.schema = schema;
    this.sources.set(id, source);
  }

  // ─── Queries ─────────────────────────────────────────────────────────────

  /** Register a query */
  registerQuery(query: DataQuery): void {
    this.queries.set(query.id, query);
  }

  /** Remove a query and its result */
  removeQuery(id: string): void {
    this.queries.delete(id);
    this.results.delete(id);
  }

  /** Get a query by ID */
  getQuery(id: string): DataQuery | undefined {
    return this.queries.get(id);
  }

  /** Get all queries for a data source */
  getQueriesForSource(sourceId: string): DataQuery[] {
    return Array.from(this.queries.values()).filter(
      (q) => q.sourceId === sourceId,
    );
  }

  // ─── Results ─────────────────────────────────────────────────────────────

  /** Set query result (used by mock or real execution) */
  setResult(queryId: string, result: Partial<QueryResult>): void {
    const existing = this.results.get(queryId);
    this.results.set(queryId, {
      queryId,
      data: result.data ?? existing?.data ?? null,
      loading: result.loading ?? false,
      error: result.error,
      lastFetched: result.lastFetched ?? existing?.lastFetched,
    });
  }

  /** Get query result */
  getResult(queryId: string): QueryResult | undefined {
    return this.results.get(queryId);
  }

  // ─── Field introspection ─────────────────────────────────────────────────

  /** Get all available fields from a data source (flattened dot-paths) */
  getAvailableFields(sourceId: string): string[] {
    const source = this.sources.get(sourceId);
    if (!source?.schema) return [];

    const paths: string[] = [];
    for (const endpoint of source.schema.endpoints) {
      flattenFields(endpoint.fields, endpoint.path, paths);
    }
    return paths;
  }
}

// ─── Helpers ─────────────────────────────────────────────────────────────────

/** Recursively flatten nested fields into dot-notation paths */
function flattenFields(
  fields: DataField[],
  prefix: string,
  out: string[],
): void {
  for (const field of fields) {
    const path = `${prefix}.${field.name}`;
    out.push(path);
    if (field.children) {
      flattenFields(field.children, path, out);
    }
  }
}
