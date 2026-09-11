// ─── Data & Backend Integration — Barrel Export ──────────────────────────────
// Re-exports all data layer types, registry, adapters, and mock utilities.
// ──────────────────────────────────────────────────────────────────────────────

// Types
export type {
  DataSource,
  DataSourceType,
  DataSourceConnection,
  DataSchema,
  DataEndpoint,
  DataField,
  DataQuery,
  QueryResult,
  ComponentDataBinding,
} from "./types";

// Registry
export { DataSourceRegistry } from "./registry";

// Adapters
export {
  createRESTSource,
  parseOpenAPISchema,
  inferSchemaFromJSON,
} from "./adapters/rest";

export {
  createGraphQLSource,
  parseGraphQLSchema,
} from "./adapters/graphql";

export {
  createSupabaseSource,
  parseSupabaseTables,
} from "./adapters/supabase";
export type { SupabaseTable } from "./adapters/supabase";

// Mock data
export {
  generateMockData,
  createMockQueryResult,
} from "./mock";
