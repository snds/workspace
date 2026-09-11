// ─── Mock Data Generator ─────────────────────────────────────────────────────
// Generates realistic preview data based on schema definitions.
// Used at design-time to populate bound components with sample content.
// ──────────────────────────────────────────────────────────────────────────────

import type { DataField, DataEndpoint, QueryResult } from "./types";

// ─── Public API ──────────────────────────────────────────────────────────────

/** Generate mock data based on a schema for design-time preview */
export function generateMockData(
  endpoint: DataEndpoint,
  count: number = 5,
): unknown {
  const items = Array.from({ length: count }, (_, i) =>
    generateMockObject(endpoint.fields, i),
  );
  return items;
}

/** Create a mock QueryResult from an endpoint */
export function createMockQueryResult(
  queryId: string,
  endpoint: DataEndpoint,
  count?: number,
): QueryResult {
  return {
    queryId,
    data: generateMockData(endpoint, count),
    loading: false,
    lastFetched: Date.now(),
  };
}

// ─── Object generation ───────────────────────────────────────────────────────

function generateMockObject(
  fields: DataField[],
  index: number,
): Record<string, unknown> {
  const obj: Record<string, unknown> = {};
  for (const field of fields) {
    obj[field.name] = generateMockValue(field, index);
  }
  return obj;
}

function generateMockValue(field: DataField, index: number): unknown {
  switch (field.type) {
    case "string":
      return generateMockString(field.name, index);
    case "number":
      return generateMockNumber(field.name, index);
    case "boolean":
      return index % 2 === 0;
    case "date":
      return new Date(Date.now() - index * 86400000).toISOString();
    case "array":
      return field.children
        ? Array.from({ length: 3 }, (_, i) =>
            generateMockObject(field.children!, i),
          )
        : [];
    case "object":
      return field.children
        ? generateMockObject(field.children, index)
        : {};
    default:
      return null;
  }
}

// ─── Contextual string generation ────────────────────────────────────────────

const NAMES = [
  "Alice Johnson",
  "Bob Smith",
  "Carol White",
  "David Brown",
  "Eve Davis",
];
const CITIES = ["New York", "San Francisco", "London", "Tokyo", "Berlin"];
const COUNTRIES = ["US", "US", "UK", "JP", "DE"];
const STATUSES = ["active", "pending", "inactive", "active", "pending"];
const COLORS = ["#3b82f6", "#ef4444", "#22c55e", "#f59e0b", "#8b5cf6"];

function generateMockString(fieldName: string, index: number): string {
  const name = fieldName.toLowerCase();

  if (name.includes("name") || name.includes("title"))
    return NAMES[index % NAMES.length];
  if (name.includes("email")) return `user${index + 1}@example.com`;
  if (name.includes("phone"))
    return `+1-555-${String(100 + index).padStart(3, "0")}-${String(1000 + index).padStart(4, "0")}`;
  if (name.includes("url") || name.includes("link"))
    return `https://example.com/item/${index + 1}`;
  if (name.includes("description") || name.includes("bio"))
    return `This is a sample description for item ${index + 1}.`;
  if (name.includes("id"))
    return `id-${String(index + 1).padStart(4, "0")}`;
  if (name.includes("status")) return STATUSES[index % STATUSES.length];
  if (name.includes("color") || name.includes("colour"))
    return COLORS[index % COLORS.length];
  if (name.includes("image") || name.includes("avatar"))
    return `https://picsum.photos/seed/${index}/200/200`;
  if (name.includes("address")) return `${100 + index} Main Street`;
  if (name.includes("city")) return CITIES[index % CITIES.length];
  if (name.includes("country"))
    return COUNTRIES[index % COUNTRIES.length];
  if (name.includes("tag") || name.includes("label"))
    return ["design", "frontend", "backend", "devops", "mobile"][
      index % 5
    ];

  return `${fieldName}-${index + 1}`;
}

function generateMockNumber(fieldName: string, index: number): number {
  const name = fieldName.toLowerCase();

  if (name.includes("price") || name.includes("amount"))
    return Math.round((9.99 + index * 10.5) * 100) / 100;
  if (name.includes("age")) return 25 + index * 5;
  if (name.includes("count") || name.includes("quantity"))
    return index * 3 + 1;
  if (name.includes("rating") || name.includes("score"))
    return Math.min(5, 3 + (index % 3));
  if (name.includes("percent") || name.includes("progress"))
    return Math.min(100, 20 + index * 18);

  return Math.floor(Math.random() * 1000) + index;
}
