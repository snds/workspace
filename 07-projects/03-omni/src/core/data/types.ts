// ─── Data & Backend Integration — Type System ─────────────────────────────────
// Types for connecting UI components to real data sources, APIs, and databases
// using a proxy-and-query model.
// ──────────────────────────────────────────────────────────────────────────────

// ─── Data Source ─────────────────────────────────────────────────────────────

/** A configured data source that components can bind to */
export interface DataSource {
  /** Unique identifier */
  id: string;
  /** Display name */
  name: string;
  /** Type of data source */
  type: DataSourceType;
  /** Connection configuration */
  config: DataSourceConnection;
  /** Schema describing available fields */
  schema?: DataSchema;
  /** Current connection status */
  status: "disconnected" | "connecting" | "connected" | "error";
  /** Error message if status is "error" */
  error?: string;
}

export type DataSourceType =
  | "rest-api"
  | "graphql"
  | "database"
  | "websocket"
  | "storage"
  | "mock";

export interface DataSourceConnection {
  baseUrl?: string;
  authMethod?: "bearer" | "api-key" | "oauth" | "cookie" | "none";
  headers?: Record<string, string>;
  /** Credential key stored in OS keychain (never exposed to browser) */
  credentialKey?: string;
}

// ─── Schema ──────────────────────────────────────────────────────────────────

/** Schema describing the structure of available data */
export interface DataSchema {
  /** Available endpoints/tables/collections */
  endpoints: DataEndpoint[];
}

export interface DataEndpoint {
  /** Endpoint path or table name */
  path: string;
  /** HTTP method (for REST) */
  method?: "GET" | "POST" | "PUT" | "PATCH" | "DELETE";
  /** Description */
  description?: string;
  /** Response fields */
  fields: DataField[];
  /** Required parameters */
  params?: DataField[];
}

export interface DataField {
  /** Field name/path */
  name: string;
  /** Field type */
  type:
    | "string"
    | "number"
    | "boolean"
    | "object"
    | "array"
    | "date"
    | "unknown";
  /** Whether this field is required */
  required?: boolean;
  /** Description */
  description?: string;
  /** Nested fields (for object/array types) */
  children?: DataField[];
}

// ─── Query ───────────────────────────────────────────────────────────────────

/** A query to execute against a data source */
export interface DataQuery {
  /** Unique query identifier */
  id: string;
  /** Display name */
  name: string;
  /** Data source to query */
  sourceId: string;
  /** Endpoint/path to query */
  endpoint: string;
  /** Method (for REST) */
  method?: string;
  /** Query parameters */
  params?: Record<string, unknown>;
  /** Request body */
  body?: unknown;
  /** Transform expression to apply to the response */
  transform?: string;
}

/** Result of a query execution */
export interface QueryResult {
  /** The query that produced this result */
  queryId: string;
  /** Response data */
  data: unknown;
  /** Whether the query is currently loading */
  loading: boolean;
  /** Error message if query failed */
  error?: string;
  /** Timestamp of last successful fetch */
  lastFetched?: number;
}

// ─── Component Binding ───────────────────────────────────────────────────────

/** Binding from a component prop to a data source field */
export interface ComponentDataBinding {
  /** The component node ID */
  nodeId: string;
  /** The prop being bound */
  propName: string;
  /** The data source ID */
  sourceId: string;
  /** The field path in the response (dot notation) */
  fieldPath: string;
  /** Optional transform expression */
  transform?: string;
}
