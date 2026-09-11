// ─── REST API Adapter ────────────────────────────────────────────────────────
// Helpers for creating REST data sources and parsing OpenAPI schemas.
// ──────────────────────────────────────────────────────────────────────────────

import type {
  DataSource,
  DataSchema,
  DataEndpoint,
  DataField,
} from "../types";

// ─── Source factory ──────────────────────────────────────────────────────────

/** Create a data source from a REST API base URL */
export function createRESTSource(
  id: string,
  name: string,
  baseUrl: string,
  authMethod?: DataSource["config"]["authMethod"],
): DataSource {
  return {
    id,
    name,
    type: "rest-api",
    config: { baseUrl, authMethod: authMethod ?? "none" },
    status: "disconnected",
  };
}

// ─── OpenAPI parser ──────────────────────────────────────────────────────────

/**
 * Parse an OpenAPI/Swagger schema to extract available endpoints and fields.
 *
 * This is a simplified parser covering common patterns — not full OpenAPI 3.x
 * compliance. It walks `paths` -> operations -> `responses` -> `200` ->
 * `content` -> `application/json` -> `schema` and resolves `$ref` pointers
 * against `#/components/schemas`.
 */
export function parseOpenAPISchema(
  spec: Record<string, unknown>,
): DataSchema {
  const endpoints: DataEndpoint[] = [];
  const paths = (spec.paths ?? {}) as Record<string, Record<string, unknown>>;
  const schemas = ((spec.components as Record<string, unknown>)?.schemas ??
    {}) as Record<string, unknown>;

  const httpMethods = ["get", "post", "put", "patch", "delete"] as const;

  for (const [path, pathItem] of Object.entries(paths)) {
    for (const method of httpMethods) {
      const operation = pathItem[method] as
        | Record<string, unknown>
        | undefined;
      if (!operation) continue;

      // Extract response schema from 200 response
      const responses = operation.responses as
        | Record<string, unknown>
        | undefined;
      const successResponse = (responses?.["200"] ??
        responses?.["201"]) as Record<string, unknown> | undefined;
      const content = successResponse?.content as
        | Record<string, unknown>
        | undefined;
      const jsonContent = content?.["application/json"] as
        | Record<string, unknown>
        | undefined;
      const responseSchema = jsonContent?.schema as
        | Record<string, unknown>
        | undefined;

      const fields = responseSchema
        ? resolveSchemaFields(responseSchema, schemas)
        : [];

      // Extract parameters
      const rawParams = (operation.parameters ?? []) as Array<
        Record<string, unknown>
      >;
      const params: DataField[] = rawParams.map((p) => ({
        name: p.name as string,
        type: mapOpenAPIType(
          (p.schema as Record<string, unknown>)?.type as string,
        ),
        required: (p.required as boolean) ?? false,
        description: p.description as string | undefined,
      }));

      endpoints.push({
        path,
        method: method.toUpperCase() as DataEndpoint["method"],
        description: (operation.summary ?? operation.description) as
          | string
          | undefined,
        fields,
        params: params.length > 0 ? params : undefined,
      });
    }
  }

  return { endpoints };
}

/** Resolve a JSON Schema object into DataField[] with $ref support */
function resolveSchemaFields(
  schema: Record<string, unknown>,
  definitions: Record<string, unknown>,
): DataField[] {
  // Handle $ref
  if (schema.$ref) {
    const refPath = (schema.$ref as string).replace(
      "#/components/schemas/",
      "",
    );
    const resolved = definitions[refPath] as
      | Record<string, unknown>
      | undefined;
    if (resolved) return resolveSchemaFields(resolved, definitions);
    return [];
  }

  // Handle array type
  if (schema.type === "array") {
    const items = schema.items as Record<string, unknown> | undefined;
    const children = items
      ? resolveSchemaFields(items, definitions)
      : [];
    return [{ name: "items", type: "array", children }];
  }

  // Handle object type (or implicit object with properties)
  const properties = (schema.properties ?? {}) as Record<
    string,
    Record<string, unknown>
  >;
  const required = (schema.required ?? []) as string[];

  return Object.entries(properties).map(([name, propSchema]) => {
    const type = mapOpenAPIType(propSchema.type as string);
    const children =
      type === "object" || type === "array"
        ? resolveSchemaFields(propSchema, definitions)
        : undefined;

    return {
      name,
      type,
      required: required.includes(name),
      description: propSchema.description as string | undefined,
      children,
    };
  });
}

// ─── JSON schema inference ───────────────────────────────────────────────────

/** Infer schema from a sample JSON response */
export function inferSchemaFromJSON(
  data: unknown,
  endpointPath: string,
): DataEndpoint {
  const fields = inferFields(data);
  return { path: endpointPath, method: "GET", fields };
}

function inferFields(data: unknown): DataField[] {
  if (data === null || data === undefined) return [];

  if (Array.isArray(data)) {
    if (data.length === 0)
      return [{ name: "items", type: "array" }];
    return [
      { name: "items", type: "array", children: inferFields(data[0]) },
    ];
  }

  if (typeof data === "object") {
    return Object.entries(data as Record<string, unknown>).map(
      ([key, value]) => {
        const type = inferFieldType(value);
        return {
          name: key,
          type,
          children: type === "object" ? inferFields(value) : undefined,
        };
      },
    );
  }

  return [];
}

function inferFieldType(value: unknown): DataField["type"] {
  if (value === null || value === undefined) return "unknown";
  if (typeof value === "string") {
    // Check for date-like strings
    if (/^\d{4}-\d{2}-\d{2}/.test(value)) return "date";
    return "string";
  }
  if (typeof value === "number") return "number";
  if (typeof value === "boolean") return "boolean";
  if (Array.isArray(value)) return "array";
  if (typeof value === "object") return "object";
  return "unknown";
}

// ─── Helpers ─────────────────────────────────────────────────────────────────

function mapOpenAPIType(type: string | undefined): DataField["type"] {
  switch (type) {
    case "string":
      return "string";
    case "integer":
    case "number":
      return "number";
    case "boolean":
      return "boolean";
    case "array":
      return "array";
    case "object":
      return "object";
    default:
      return "unknown";
  }
}
