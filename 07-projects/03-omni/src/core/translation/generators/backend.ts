// ─── AI Translation Engine — Backend Generator ──────────────────────────────
// Template-based backend code generation from IR nodes with data bindings.
// Generates API routes, data fetching hooks, and auth middleware.

import type { TeamContextProfile } from "@/core/context/types";
import type { IRNode, DataBinding } from "@/core/ir/types";
import type { GeneratedFile } from "../types";

// ─── Main entry point ───────────────────────────────────────────────────────

/**
 * Generate backend files from IR nodes with data bindings.
 * Only generates when the team context has backend configuration (tier >= 2).
 */
export function generateBackendFiles(
  nodes: IRNode[],
  context: TeamContextProfile,
): GeneratedFile[] {
  const files: GeneratedFile[] = [];

  if (context.tier < 2 || context.backend.apiLayer === "none") {
    return files;
  }

  // Collect all unique data bindings from the IR nodes
  const bindings = collectDataBindings(nodes);

  if (bindings.length === 0) {
    return files;
  }

  // Group bindings by source
  const sourceGroups = groupBindingsBySource(bindings);

  // Generate API routes for each data source
  for (const [sourceId, sourceBindings] of Object.entries(sourceGroups)) {
    const routeFile = generateAPIRoute(sourceId, sourceBindings, context);
    if (routeFile) files.push(routeFile);
  }

  // Generate data fetching hooks/utilities
  for (const [sourceId, sourceBindings] of Object.entries(sourceGroups)) {
    const fetcherFile = generateDataFetcher(sourceId, sourceBindings, context);
    if (fetcherFile) files.push(fetcherFile);
  }

  // Generate auth middleware if auth is configured
  if (context.auth.provider !== "none") {
    const authFile = generateAuthMiddleware(context);
    if (authFile) files.push(authFile);
  }

  return files;
}

// ─── API route generator ────────────────────────────────────────────────────

/**
 * Creates API route files based on the server framework.
 */
export function generateAPIRoute(
  sourceId: string,
  bindings: DataBinding[],
  context: TeamContextProfile,
): GeneratedFile | null {
  const { backend, framework } = context;
  const resourceName = sourceId.toLowerCase();
  const fields = bindings.map((b) => b.fieldPath.split(".").pop() ?? b.fieldPath);

  // Next.js App Router route handler
  if (framework.metaFramework === "nextjs") {
    return generateNextjsRoute(resourceName, fields, context);
  }

  // Express route
  if (backend.serverFramework === "express") {
    return generateExpressRoute(resourceName, fields, context);
  }

  // Fastify route
  if (backend.serverFramework === "fastify") {
    return generateFastifyRoute(resourceName, fields, context);
  }

  // Hono route
  if (backend.serverFramework === "hono") {
    return generateHonoRoute(resourceName, fields, context);
  }

  // Fallback: generic API route
  return {
    path: `api/${resourceName}/route.ts`,
    content: generateGenericRoute(resourceName, fields),
    language: "typescript",
    category: "backend",
  };
}

function generateNextjsRoute(
  resourceName: string,
  fields: string[],
  context: TeamContextProfile,
): GeneratedFile {
  const hasAuth = context.auth.provider !== "none";
  const hasOrm = context.backend.orm && context.backend.orm !== "none";

  let content = `import { NextRequest, NextResponse } from "next/server";\n`;

  if (hasAuth) {
    content += `import { auth } from "@/lib/auth";\n`;
  }

  if (hasOrm) {
    content += `import { db } from "@/lib/db";\n`;
  }

  content += `
export async function GET(request: NextRequest) {
${hasAuth ? "  const session = await auth();\n  if (!session) {\n    return NextResponse.json({ error: \"Unauthorized\" }, { status: 401 });\n  }\n" : ""}
  try {
${hasOrm ? `    const data = await db.${resourceName}.findMany({\n      select: {\n${fields.map((f) => `        ${f}: true,`).join("\n")}\n      },\n    });\n` : `    // TODO: Implement data fetching for ${resourceName}\n    const data: { ${fields.map((f) => `${f}: string`).join("; ")} }[] = [];\n`}
    return NextResponse.json({ data });
  } catch (error) {
    console.error("[${resourceName}] GET error:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 },
    );
  }
}

export async function POST(request: NextRequest) {
${hasAuth ? "  const session = await auth();\n  if (!session) {\n    return NextResponse.json({ error: \"Unauthorized\" }, { status: 401 });\n  }\n" : ""}
  try {
    const body = await request.json();

${hasOrm ? `    const created = await db.${resourceName}.create({\n      data: body,\n    });\n` : `    // TODO: Implement data creation for ${resourceName}\n    const created = { id: crypto.randomUUID(), ...body };\n`}
    return NextResponse.json({ data: created }, { status: 201 });
  } catch (error) {
    console.error("[${resourceName}] POST error:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 },
    );
  }
}
`;

  return {
    path: `app/api/${resourceName}/route.ts`,
    content,
    language: "typescript",
    category: "backend",
  };
}

function generateExpressRoute(
  resourceName: string,
  fields: string[],
  context: TeamContextProfile,
): GeneratedFile {
  const hasOrm = context.backend.orm && context.backend.orm !== "none";

  let content = `import { Router } from "express";\n`;

  if (hasOrm) {
    content += `import { db } from "../lib/db";\n`;
  }

  content += `
const router = Router();

// GET /${resourceName}
router.get("/", async (req, res) => {
  try {
${hasOrm ? `    const data = await db.${resourceName}.findMany({\n      select: {\n${fields.map((f) => `        ${f}: true,`).join("\n")}\n      },\n    });\n` : `    // TODO: Implement data fetching for ${resourceName}\n    const data: { ${fields.map((f) => `${f}: string`).join("; ")} }[] = [];\n`}
    res.json({ data });
  } catch (error) {
    console.error("[${resourceName}] GET error:", error);
    res.status(500).json({ error: "Internal server error" });
  }
});

// POST /${resourceName}
router.post("/", async (req, res) => {
  try {
    const body = req.body;

${hasOrm ? `    const created = await db.${resourceName}.create({\n      data: body,\n    });\n` : `    // TODO: Implement data creation for ${resourceName}\n    const created = { id: crypto.randomUUID(), ...body };\n`}
    res.status(201).json({ data: created });
  } catch (error) {
    console.error("[${resourceName}] POST error:", error);
    res.status(500).json({ error: "Internal server error" });
  }
});

// GET /${resourceName}/:id
router.get("/:id", async (req, res) => {
  try {
    const { id } = req.params;

${hasOrm ? `    const item = await db.${resourceName}.findUnique({\n      where: { id },\n    });\n` : `    // TODO: Implement data fetching for ${resourceName} by ID\n    const item = null;\n`}
    if (!item) {
      return res.status(404).json({ error: "Not found" });
    }

    res.json({ data: item });
  } catch (error) {
    console.error("[${resourceName}] GET :id error:", error);
    res.status(500).json({ error: "Internal server error" });
  }
});

export default router;
`;

  return {
    path: `server/routes/${resourceName}.ts`,
    content,
    language: "typescript",
    category: "backend",
  };
}

function generateFastifyRoute(
  resourceName: string,
  fields: string[],
  context: TeamContextProfile,
): GeneratedFile {
  const hasOrm = context.backend.orm && context.backend.orm !== "none";

  let content = `import type { FastifyInstance } from "fastify";\n`;

  if (hasOrm) {
    content += `import { db } from "../lib/db";\n`;
  }

  content += `
export default async function ${resourceName}Routes(app: FastifyInstance) {
  // GET /${resourceName}
  app.get("/", async (request, reply) => {
    try {
${hasOrm ? `      const data = await db.${resourceName}.findMany({\n        select: {\n${fields.map((f) => `          ${f}: true,`).join("\n")}\n        },\n      });\n` : `      // TODO: Implement data fetching for ${resourceName}\n      const data: { ${fields.map((f) => `${f}: string`).join("; ")} }[] = [];\n`}
      return { data };
    } catch (error) {
      request.log.error(error, "[${resourceName}] GET error");
      return reply.status(500).send({ error: "Internal server error" });
    }
  });

  // POST /${resourceName}
  app.post("/", async (request, reply) => {
    try {
      const body = request.body;

${hasOrm ? `      const created = await db.${resourceName}.create({\n        data: body as Record<string, unknown>,\n      });\n` : `      // TODO: Implement data creation for ${resourceName}\n      const created = { id: crypto.randomUUID(), ...(body as Record<string, unknown>) };\n`}
      return reply.status(201).send({ data: created });
    } catch (error) {
      request.log.error(error, "[${resourceName}] POST error");
      return reply.status(500).send({ error: "Internal server error" });
    }
  });
}
`;

  return {
    path: `server/routes/${resourceName}.ts`,
    content,
    language: "typescript",
    category: "backend",
  };
}

function generateHonoRoute(
  resourceName: string,
  fields: string[],
  context: TeamContextProfile,
): GeneratedFile {
  const hasOrm = context.backend.orm && context.backend.orm !== "none";

  let content = `import { Hono } from "hono";\n`;

  if (hasOrm) {
    content += `import { db } from "../lib/db";\n`;
  }

  content += `
const app = new Hono();

// GET /${resourceName}
app.get("/", async (c) => {
  try {
${hasOrm ? `    const data = await db.${resourceName}.findMany({\n      select: {\n${fields.map((f) => `        ${f}: true,`).join("\n")}\n      },\n    });\n` : `    // TODO: Implement data fetching for ${resourceName}\n    const data: { ${fields.map((f) => `${f}: string`).join("; ")} }[] = [];\n`}
    return c.json({ data });
  } catch (error) {
    console.error("[${resourceName}] GET error:", error);
    return c.json({ error: "Internal server error" }, 500);
  }
});

// POST /${resourceName}
app.post("/", async (c) => {
  try {
    const body = await c.req.json();

${hasOrm ? `    const created = await db.${resourceName}.create({\n      data: body,\n    });\n` : `    // TODO: Implement data creation for ${resourceName}\n    const created = { id: crypto.randomUUID(), ...body };\n`}
    return c.json({ data: created }, 201);
  } catch (error) {
    console.error("[${resourceName}] POST error:", error);
    return c.json({ error: "Internal server error" }, 500);
  }
});

export default app;
`;

  return {
    path: `server/routes/${resourceName}.ts`,
    content,
    language: "typescript",
    category: "backend",
  };
}

function generateGenericRoute(resourceName: string, fields: string[]): string {
  return `// API route for ${resourceName}
// TODO: Implement with your preferred server framework

export interface ${toPascalCase(resourceName)}Record {
${fields.map((f) => `  ${f}: string;`).join("\n")}
}

export async function get${toPascalCase(resourceName)}(): Promise<${toPascalCase(resourceName)}Record[]> {
  // TODO: Implement data fetching
  return [];
}

export async function create${toPascalCase(resourceName)}(
  data: Omit<${toPascalCase(resourceName)}Record, "id">,
): Promise<${toPascalCase(resourceName)}Record> {
  // TODO: Implement data creation
  return { ...data } as ${toPascalCase(resourceName)}Record;
}
`;
}

// ─── Data fetcher generator ─────────────────────────────────────────────────

/**
 * Creates data fetching hooks (React Query, SWR, etc.)
 */
export function generateDataFetcher(
  sourceId: string,
  bindings: DataBinding[],
  context: TeamContextProfile,
): GeneratedFile | null {
  const { framework, backend } = context;
  const resourceName = sourceId.toLowerCase();
  const typeName = toPascalCase(sourceId);
  const fields = bindings.map((b) => b.fieldPath.split(".").pop() ?? b.fieldPath);

  // React with tRPC
  if (framework.id === "react" && backend.apiLayer === "trpc") {
    return generateTRPCHook(resourceName, typeName, fields);
  }

  // React with REST (React Query)
  if (framework.id === "react") {
    return generateReactQueryHook(resourceName, typeName, fields, context);
  }

  // Vue (with composable)
  if (framework.id === "vue") {
    return generateVueComposable(resourceName, typeName, fields, context);
  }

  // Svelte (with store)
  if (framework.id === "svelte") {
    return generateSvelteStore(resourceName, typeName, fields);
  }

  return null;
}

function generateTRPCHook(
  resourceName: string,
  typeName: string,
  fields: string[],
): GeneratedFile {
  const content = `import { api } from "@/lib/trpc";

export interface ${typeName}Data {
${fields.map((f) => `  ${f}: string;`).join("\n")}
}

/** Fetch all ${resourceName} records */
export function use${typeName}List() {
  return api.${resourceName}.list.useQuery();
}

/** Fetch a single ${resourceName} by ID */
export function use${typeName}(id: string) {
  return api.${resourceName}.byId.useQuery({ id });
}

/** Create a new ${resourceName} */
export function useCreate${typeName}() {
  const utils = api.useUtils();

  return api.${resourceName}.create.useMutation({
    onSuccess: () => {
      utils.${resourceName}.list.invalidate();
    },
  });
}
`;

  return {
    path: `hooks/use-${resourceName}.ts`,
    content,
    language: "typescript",
    category: "frontend",
  };
}

function generateReactQueryHook(
  resourceName: string,
  typeName: string,
  fields: string[],
  context: TeamContextProfile,
): GeneratedFile {
  const apiBase = context.framework.metaFramework === "nextjs"
    ? `/api/${resourceName}`
    : `${getAPIBaseURL(context)}/${resourceName}`;

  const content = `import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";

export interface ${typeName}Data {
${fields.map((f) => `  ${f}: string;`).join("\n")}
}

const ${resourceName.toUpperCase()}_QUERY_KEY = ["${resourceName}"] as const;

/** Fetch all ${resourceName} records */
export function use${typeName}List() {
  return useQuery({
    queryKey: ${resourceName.toUpperCase()}_QUERY_KEY,
    queryFn: async (): Promise<${typeName}Data[]> => {
      const res = await fetch("${apiBase}");
      if (!res.ok) throw new Error("Failed to fetch ${resourceName}");
      const json = await res.json();
      return json.data;
    },
  });
}

/** Fetch a single ${resourceName} by ID */
export function use${typeName}(id: string) {
  return useQuery({
    queryKey: [...${resourceName.toUpperCase()}_QUERY_KEY, id],
    queryFn: async (): Promise<${typeName}Data> => {
      const res = await fetch(\`${apiBase}/\${id}\`);
      if (!res.ok) throw new Error("Failed to fetch ${resourceName}");
      const json = await res.json();
      return json.data;
    },
    enabled: Boolean(id),
  });
}

/** Create a new ${resourceName} */
export function useCreate${typeName}() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: Omit<${typeName}Data, "id">) => {
      const res = await fetch("${apiBase}", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
      if (!res.ok) throw new Error("Failed to create ${resourceName}");
      const json = await res.json();
      return json.data as ${typeName}Data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ${resourceName.toUpperCase()}_QUERY_KEY });
    },
  });
}
`;

  return {
    path: `hooks/use-${resourceName}.ts`,
    content,
    language: "typescript",
    category: "frontend",
  };
}

function generateVueComposable(
  resourceName: string,
  typeName: string,
  fields: string[],
  context: TeamContextProfile,
): GeneratedFile {
  const isNuxt = context.framework.metaFramework === "nuxt";

  const content = isNuxt
    ? `export interface ${typeName}Data {
${fields.map((f) => `  ${f}: string;`).join("\n")}
}

/** Fetch all ${resourceName} records */
export function use${typeName}List() {
  return useFetch<{ data: ${typeName}Data[] }>("/api/${resourceName}");
}

/** Fetch a single ${resourceName} by ID */
export function use${typeName}(id: string) {
  return useFetch<{ data: ${typeName}Data }>(\`/api/${resourceName}/\${id}\`);
}
`
    : `import { ref, onMounted } from "vue";

export interface ${typeName}Data {
${fields.map((f) => `  ${f}: string;`).join("\n")}
}

/** Fetch all ${resourceName} records */
export function use${typeName}List() {
  const data = ref<${typeName}Data[]>([]);
  const isLoading = ref(true);
  const error = ref<Error | null>(null);

  onMounted(async () => {
    try {
      const res = await fetch("/api/${resourceName}");
      if (!res.ok) throw new Error("Failed to fetch ${resourceName}");
      const json = await res.json();
      data.value = json.data;
    } catch (e) {
      error.value = e instanceof Error ? e : new Error(String(e));
    } finally {
      isLoading.value = false;
    }
  });

  return { data, isLoading, error };
}
`;

  return {
    path: `composables/use-${resourceName}.ts`,
    content,
    language: "typescript",
    category: "frontend",
  };
}

function generateSvelteStore(
  resourceName: string,
  typeName: string,
  fields: string[],
): GeneratedFile {
  const content = `export interface ${typeName}Data {
${fields.map((f) => `  ${f}: string;`).join("\n")}
}

/** Fetch all ${resourceName} records */
export async function fetch${typeName}List(): Promise<${typeName}Data[]> {
  const res = await fetch("/api/${resourceName}");
  if (!res.ok) throw new Error("Failed to fetch ${resourceName}");
  const json = await res.json();
  return json.data;
}

/** Fetch a single ${resourceName} by ID */
export async function fetch${typeName}(id: string): Promise<${typeName}Data> {
  const res = await fetch(\`/api/${resourceName}/\${id}\`);
  if (!res.ok) throw new Error("Failed to fetch ${resourceName}");
  const json = await res.json();
  return json.data;
}

/** Create a new ${resourceName} */
export async function create${typeName}(
  data: Omit<${typeName}Data, "id">,
): Promise<${typeName}Data> {
  const res = await fetch("/api/${resourceName}", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Failed to create ${resourceName}");
  const json = await res.json();
  return json.data;
}
`;

  return {
    path: `lib/api/${resourceName}.ts`,
    content,
    language: "typescript",
    category: "frontend",
  };
}

// ─── Auth middleware generator ───────────────────────────────────────────────

/**
 * Creates auth middleware based on the auth provider.
 */
export function generateAuthMiddleware(
  context: TeamContextProfile,
): GeneratedFile | null {
  const { auth, framework } = context;

  if (auth.provider === "none") return null;

  switch (auth.provider) {
    case "clerk":
      return generateClerkAuth(framework.metaFramework ?? "none");
    case "nextauth":
      return generateNextAuth();
    case "supabase":
      return generateSupabaseAuth(framework.metaFramework ?? "none");
    case "auth0":
      return generateAuth0Middleware();
    default:
      return generateGenericAuthMiddleware(auth.provider);
  }
}

function generateClerkAuth(metaFramework: string): GeneratedFile {
  if (metaFramework === "nextjs") {
    return {
      path: "middleware.ts",
      content: `import { clerkMiddleware, createRouteMatcher } from "@clerk/nextjs/server";

const isProtectedRoute = createRouteMatcher(["/dashboard(.*)", "/api(.*)"]);

export default clerkMiddleware(async (auth, req) => {
  if (isProtectedRoute(req)) {
    await auth.protect();
  }
});

export const config = {
  matcher: ["/((?!.*\\\\..*|_next).*)", "/", "/(api|trpc)(.*)"],
};
`,
      language: "typescript",
      category: "backend",
    };
  }

  return {
    path: "server/middleware/auth.ts",
    content: `// Clerk auth middleware
// See: https://clerk.com/docs

export function requireAuth() {
  // TODO: Implement Clerk auth middleware for your server framework
  return async (req: Request, next: () => Promise<Response>) => {
    // Validate the session token
    return next();
  };
}
`,
    language: "typescript",
    category: "backend",
  };
}

function generateNextAuth(): GeneratedFile {
  return {
    path: "lib/auth.ts",
    content: `import NextAuth from "next-auth";

export const { handlers, auth, signIn, signOut } = NextAuth({
  providers: [
    // TODO: Configure your auth providers
  ],
  callbacks: {
    async session({ session, token }) {
      // Attach user ID to session
      if (token.sub) {
        session.user.id = token.sub;
      }
      return session;
    },
  },
});
`,
    language: "typescript",
    category: "backend",
  };
}

function generateSupabaseAuth(metaFramework: string): GeneratedFile {
  if (metaFramework === "nextjs") {
    return {
      path: "lib/supabase/middleware.ts",
      content: `import { createServerClient } from "@supabase/ssr";
import { NextResponse, type NextRequest } from "next/server";

export async function updateSession(request: NextRequest) {
  let supabaseResponse = NextResponse.next({ request });

  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() {
          return request.cookies.getAll();
        },
        setAll(cookiesToSet) {
          for (const { name, value } of cookiesToSet) {
            request.cookies.set(name, value);
          }
          supabaseResponse = NextResponse.next({ request });
          for (const { name, value, options } of cookiesToSet) {
            supabaseResponse.cookies.set(name, value, options);
          }
        },
      },
    },
  );

  await supabase.auth.getUser();

  return supabaseResponse;
}
`,
      language: "typescript",
      category: "backend",
    };
  }

  return {
    path: "lib/supabase/client.ts",
    content: `import { createClient } from "@supabase/supabase-js";

export const supabase = createClient(
  process.env.SUPABASE_URL!,
  process.env.SUPABASE_ANON_KEY!,
);
`,
    language: "typescript",
    category: "backend",
  };
}

function generateAuth0Middleware(): GeneratedFile {
  return {
    path: "server/middleware/auth.ts",
    content: `// Auth0 middleware
// See: https://auth0.com/docs

import { expressjwt, type GetVerificationKey } from "express-jwt";
import { expressJwtSecret } from "jwks-rsa";

const AUTH0_DOMAIN = process.env.AUTH0_DOMAIN!;
const AUTH0_AUDIENCE = process.env.AUTH0_AUDIENCE!;

export const requireAuth = expressjwt({
  secret: expressJwtSecret({
    cache: true,
    rateLimit: true,
    jwksRequestsPerMinute: 5,
    jwksUri: \`https://\${AUTH0_DOMAIN}/.well-known/jwks.json\`,
  }) as GetVerificationKey,
  audience: AUTH0_AUDIENCE,
  issuer: \`https://\${AUTH0_DOMAIN}/\`,
  algorithms: ["RS256"],
});
`,
    language: "typescript",
    category: "backend",
  };
}

function generateGenericAuthMiddleware(provider: string): GeneratedFile {
  return {
    path: "server/middleware/auth.ts",
    content: `// Auth middleware for ${provider}
// TODO: Implement authentication middleware

export interface AuthUser {
  id: string;
  email: string;
  roles?: string[];
}

export function requireAuth() {
  return async (req: Request, next: () => Promise<Response>) => {
    // TODO: Validate auth token and attach user to request
    return next();
  };
}

export function requireRole(role: string) {
  return async (req: Request, next: () => Promise<Response>) => {
    // TODO: Check if user has the required role
    return next();
  };
}
`,
    language: "typescript",
    category: "backend",
  };
}

// ─── Helpers ────────────────────────────────────────────────────────────────

function collectDataBindings(nodes: IRNode[]): DataBinding[] {
  const bindings: DataBinding[] = [];

  for (const node of nodes) {
    if (node.dataBindings) {
      bindings.push(...node.dataBindings);
    }
  }

  return bindings;
}

function groupBindingsBySource(
  bindings: DataBinding[],
): Record<string, DataBinding[]> {
  const groups: Record<string, DataBinding[]> = {};

  for (const binding of bindings) {
    if (!groups[binding.sourceId]) {
      groups[binding.sourceId] = [];
    }
    groups[binding.sourceId].push(binding);
  }

  return groups;
}

function getAPIBaseURL(context: TeamContextProfile): string {
  const dataSource = context.data.find((d) => d.baseUrl);
  return dataSource?.baseUrl ?? "/api";
}

function toPascalCase(str: string): string {
  return str
    .replace(/[^a-zA-Z0-9]/g, " ")
    .split(" ")
    .filter(Boolean)
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join("");
}
