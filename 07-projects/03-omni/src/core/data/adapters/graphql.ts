// ─── GraphQL Adapter ─────────────────────────────────────────────────────────
// Helpers for creating GraphQL data sources and parsing introspection results.
// ──────────────────────────────────────────────────────────────────────────────

import type {
  DataSource,
  DataSchema,
  DataEndpoint,
  DataField,
} from "../types";

// ─── Source factory ──────────────────────────────────────────────────────────

/** Create a data source from a GraphQL endpoint */
export function createGraphQLSource(
  id: string,
  name: string,
  endpoint: string,
  authMethod?: DataSource["config"]["authMethod"],
): DataSource {
  return {
    id,
    name,
    type: "graphql",
    config: { baseUrl: endpoint, authMethod: authMethod ?? "none" },
    status: "disconnected",
  };
}

// ─── Introspection parser ────────────────────────────────────────────────────

/**
 * GraphQL introspection type as returned by `__schema { types { ... } }`.
 * This is a simplified subset — full introspection is much richer.
 */
interface IntrospectionType {
  name: string;
  kind: string;
  fields?: IntrospectionField[];
}

interface IntrospectionField {
  name: string;
  type: IntrospectionTypeRef;
  args?: IntrospectionArg[];
  description?: string;
}

interface IntrospectionTypeRef {
  kind: string;
  name?: string;
  ofType?: IntrospectionTypeRef;
}

interface IntrospectionArg {
  name: string;
  type: IntrospectionTypeRef;
  description?: string;
}

/**
 * Parse a GraphQL schema (introspection result) to extract available types
 * and fields.
 *
 * Expects the standard `{ __schema: { types: [...] } }` introspection format.
 * Extracts Query and Mutation root types and their fields as endpoints.
 */
export function parseGraphQLSchema(
  introspection: Record<string, unknown>,
): DataSchema {
  const endpoints: DataEndpoint[] = [];

  const schema = introspection.__schema as Record<string, unknown> | undefined;
  if (!schema) return { endpoints };

  const types = (schema.types ?? []) as IntrospectionType[];
  const typeMap = new Map<string, IntrospectionType>();
  for (const t of types) {
    typeMap.set(t.name, t);
  }

  // Find Query and Mutation root types
  const queryTypeName = (schema.queryType as Record<string, string>)?.name ?? "Query";
  const mutationTypeName = (schema.mutationType as Record<string, string>)?.name ?? "Mutation";

  const queryType = typeMap.get(queryTypeName);
  const mutationType = typeMap.get(mutationTypeName);

  if (queryType?.fields) {
    for (const field of queryType.fields) {
      endpoints.push(
        introspectionFieldToEndpoint(field, "GET", typeMap),
      );
    }
  }

  if (mutationType?.fields) {
    for (const field of mutationType.fields) {
      endpoints.push(
        introspectionFieldToEndpoint(field, "POST", typeMap),
      );
    }
  }

  return { endpoints };
}

/** Convert a single introspection field to a DataEndpoint */
function introspectionFieldToEndpoint(
  field: IntrospectionField,
  method: "GET" | "POST",
  typeMap: Map<string, IntrospectionType>,
): DataEndpoint {
  const returnType = unwrapType(field.type);
  const resolvedType = returnType.name
    ? typeMap.get(returnType.name)
    : undefined;

  const fields: DataField[] = resolvedType?.fields
    ? resolvedType.fields.map((f) => introspectionFieldToDataField(f, typeMap))
    : [];

  const params: DataField[] | undefined = field.args?.map((arg) => ({
    name: arg.name,
    type: mapGraphQLType(unwrapType(arg.type).name),
    description: arg.description,
  }));

  return {
    path: field.name,
    method,
    description: field.description,
    fields,
    params: params && params.length > 0 ? params : undefined,
  };
}

/** Convert an introspection field to a DataField */
function introspectionFieldToDataField(
  field: IntrospectionField,
  typeMap: Map<string, IntrospectionType>,
): DataField {
  const unwrapped = unwrapType(field.type);
  const type = mapGraphQLType(unwrapped.name);
  const isList = isListType(field.type);

  const resolvedType = unwrapped.name
    ? typeMap.get(unwrapped.name)
    : undefined;
  const children =
    type === "object" && resolvedType?.fields
      ? resolvedType.fields.map((f) =>
          introspectionFieldToDataField(f, typeMap),
        )
      : undefined;

  return {
    name: field.name,
    type: isList ? "array" : type,
    description: field.description,
    children,
  };
}

/** Unwrap NON_NULL and LIST wrappers to get the underlying named type */
function unwrapType(typeRef: IntrospectionTypeRef): IntrospectionTypeRef {
  if (
    typeRef.kind === "NON_NULL" ||
    typeRef.kind === "LIST"
  ) {
    return typeRef.ofType ? unwrapType(typeRef.ofType) : typeRef;
  }
  return typeRef;
}

/** Check if a type ref contains a LIST wrapper */
function isListType(typeRef: IntrospectionTypeRef): boolean {
  if (typeRef.kind === "LIST") return true;
  if (typeRef.ofType) return isListType(typeRef.ofType);
  return false;
}

/** Map GraphQL scalar names to DataField types */
function mapGraphQLType(
  name: string | undefined,
): DataField["type"] {
  switch (name) {
    case "String":
    case "ID":
      return "string";
    case "Int":
    case "Float":
      return "number";
    case "Boolean":
      return "boolean";
    case "DateTime":
    case "Date":
      return "date";
    default:
      // Named types (objects, enums, etc.) are treated as objects
      return "object";
  }
}
