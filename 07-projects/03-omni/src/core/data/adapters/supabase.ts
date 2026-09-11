// ─── Supabase Adapter ────────────────────────────────────────────────────────
// Helpers for creating Supabase data sources and parsing table definitions.
// ──────────────────────────────────────────────────────────────────────────────

import type {
  DataSource,
  DataSchema,
  DataEndpoint,
  DataField,
} from "../types";

// ─── Source factory ──────────────────────────────────────────────────────────

/** Create a Supabase data source */
export function createSupabaseSource(
  id: string,
  name: string,
  projectUrl: string,
): DataSource {
  return {
    id,
    name,
    type: "database",
    config: { baseUrl: projectUrl, authMethod: "api-key" },
    status: "disconnected",
  };
}

// ─── Table schema parser ─────────────────────────────────────────────────────

/** Definition of a Supabase table for schema parsing */
export interface SupabaseTable {
  name: string;
  columns: Array<{
    name: string;
    type: string;
    nullable: boolean;
    comment?: string;
  }>;
}

/** Parse Supabase table definitions to a DataSchema */
export function parseSupabaseTables(tables: SupabaseTable[]): DataSchema {
  const endpoints: DataEndpoint[] = tables.map((table) => ({
    path: table.name,
    description: `Supabase table: ${table.name}`,
    fields: table.columns.map(
      (col): DataField => ({
        name: col.name,
        type: mapSupabaseType(col.type),
        required: !col.nullable,
        description: col.comment ?? undefined,
      }),
    ),
  }));

  return { endpoints };
}

// ─── Type mapping ────────────────────────────────────────────────────────────

/** Map PostgreSQL types to DataField types */
function mapSupabaseType(pgType: string): DataField["type"] {
  // String types
  if (
    ["text", "varchar", "char", "uuid", "citext", "name"].includes(pgType)
  ) {
    return "string";
  }

  // Numeric types
  if (
    [
      "int2",
      "int4",
      "int8",
      "float4",
      "float8",
      "numeric",
      "decimal",
      "serial",
      "bigserial",
    ].includes(pgType)
  ) {
    return "number";
  }

  // Boolean
  if (pgType === "bool") return "boolean";

  // Date/time types
  if (
    ["timestamp", "timestamptz", "date", "time", "timetz", "interval"].includes(
      pgType,
    )
  ) {
    return "date";
  }

  // JSON types
  if (pgType === "jsonb" || pgType === "json") return "object";

  // Array notation (e.g. "_text" for text[])
  if (pgType.startsWith("_")) return "array";

  return "unknown";
}
