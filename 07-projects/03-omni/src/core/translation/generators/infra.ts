// ─── AI Translation Engine — Infrastructure Generator ────────────────────────
// Template-based infrastructure configuration generation.
// Generates env files, CI/CD configs, Dockerfiles, and hosting configs.

import type { TeamContextProfile } from "@/core/context/types";
import type { GeneratedFile } from "../types";

// ─── Main entry point ───────────────────────────────────────────────────────

/**
 * Generate infrastructure configuration files.
 * Only generates when the team context has infra configuration (tier >= 3).
 */
export function generateInfraFiles(
  context: TeamContextProfile,
): GeneratedFile[] {
  const files: GeneratedFile[] = [];

  if (context.tier < 3) {
    return files;
  }

  // Environment files
  const envFiles = generateEnvFile(context);
  files.push(...envFiles);

  // CI/CD configuration
  if (context.infra.cicd && context.infra.cicd.provider !== "none") {
    const cicdFile = generateCICDConfig(context);
    if (cicdFile) files.push(cicdFile);
  }

  // Hosting-specific config
  const hostingFile = generateHostingConfig(context);
  if (hostingFile) files.push(hostingFile);

  // Docker (if not serverless / Vercel / Netlify)
  if (shouldGenerateDocker(context)) {
    const dockerFile = generateDockerfile(context);
    if (dockerFile) files.push(dockerFile);
  }

  // Feature flag setup
  if (context.infra.featureFlags) {
    const ffFile = generateFeatureFlagSetup(context);
    if (ffFile) files.push(ffFile);
  }

  // Monitoring setup
  if (context.infra.monitoring && context.infra.monitoring !== "none") {
    const monitoringFile = generateMonitoringSetup(context);
    if (monitoringFile) files.push(monitoringFile);
  }

  return files;
}

// ─── Environment files ──────────────────────────────────────────────────────

/**
 * Generate .env files for each environment.
 */
export function generateEnvFile(
  context: TeamContextProfile,
): GeneratedFile[] {
  const files: GeneratedFile[] = [];
  const { infra, auth, database } = context;

  // Common variables across all environments
  const commonVars: Record<string, string> = {};

  // Database URL
  if (database.type !== "none") {
    commonVars["DATABASE_URL"] = getDatabaseURLPlaceholder(database.type, database.provider);
  }

  // Auth variables
  if (auth.provider !== "none") {
    const authVars = getAuthEnvVars(auth.provider);
    Object.assign(commonVars, authVars);
  }

  // Feature flags
  if (infra.featureFlags) {
    commonVars[`${infra.featureFlags.provider.toUpperCase().replace(/-/g, "_")}_SDK_KEY`] = "your-sdk-key";
  }

  // Monitoring
  if (infra.monitoring && infra.monitoring !== "none") {
    commonVars[`${infra.monitoring.toUpperCase()}_DSN`] = "your-dsn";
  }

  // Generate .env.example with all variables
  const envExampleLines = Object.entries(commonVars)
    .map(([key, value]) => `${key}=${value}`)
    .join("\n");

  files.push({
    path: ".env.example",
    content: `# Environment variables\n# Copy this file to .env.local and fill in the values\n\n${envExampleLines}\n`,
    language: "plaintext",
    category: "config",
  });

  // Generate per-environment .env files
  for (const env of infra.environments) {
    const envVars = { ...commonVars, ...env.variables };
    const envLines = Object.entries(envVars)
      .map(([key, value]) => `${key}=${value}`)
      .join("\n");

    files.push({
      path: `.env.${env.name}`,
      content: `# ${env.name} environment\n\n${envLines}\n`,
      language: "plaintext",
      category: "config",
    });
  }

  return files;
}

// ─── CI/CD configuration ────────────────────────────────────────────────────

function generateCICDConfig(context: TeamContextProfile): GeneratedFile | null {
  const cicd = context.infra.cicd;
  if (!cicd) return null;

  switch (cicd.provider) {
    case "github-actions":
      return generateGitHubActions(context);
    case "gitlab-ci":
      return generateGitLabCI(context);
    default:
      return null;
  }
}

/**
 * Generate a GitHub Actions CI/CD workflow.
 */
export function generateGitHubActions(
  context: TeamContextProfile,
): GeneratedFile {
  const { framework, codePatterns, infra } = context;
  const deployBranch = infra.cicd?.autoDeployBranch ?? "main";
  const testCommand = codePatterns.testFramework && codePatterns.testFramework !== "none"
    ? `\n      - name: Run tests\n        run: npm test`
    : "";
  const lintCommand = codePatterns.linter && codePatterns.linter !== "none"
    ? `\n      - name: Lint\n        run: npm run lint`
    : "";

  const buildStep = framework.metaFramework === "nextjs"
    ? "npm run build"
    : framework.metaFramework === "nuxt"
      ? "npx nuxi build"
      : "npm run build";

  const content = `name: CI/CD

on:
  push:
    branches: [${deployBranch}]
  pull_request:
    branches: [${deployBranch}]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: "22"
          cache: "npm"

      - name: Install dependencies
        run: npm ci
${lintCommand}

      - name: Type check
        run: npx tsc --noEmit
${testCommand}

      - name: Build
        run: ${buildStep}
`;

  return {
    path: ".github/workflows/ci.yml",
    content,
    language: "yaml",
    category: "config",
  };
}

function generateGitLabCI(context: TeamContextProfile): GeneratedFile {
  const { codePatterns } = context;
  const testStage = codePatterns.testFramework && codePatterns.testFramework !== "none"
    ? `\ntest:\n  stage: test\n  script:\n    - npm test\n`
    : "";

  const content = `stages:
  - install
  - lint
  - test
  - build

install:
  stage: install
  script:
    - npm ci
  cache:
    paths:
      - node_modules/

lint:
  stage: lint
  script:
    - npm run lint
    - npx tsc --noEmit
${testStage}
build:
  stage: build
  script:
    - npm run build
`;

  return {
    path: ".gitlab-ci.yml",
    content,
    language: "yaml",
    category: "config",
  };
}

// ─── Hosting configuration ──────────────────────────────────────────────────

function generateHostingConfig(context: TeamContextProfile): GeneratedFile | null {
  switch (context.infra.hosting) {
    case "vercel":
      return generateVercelConfig(context);
    case "netlify":
      return generateNetlifyConfig(context);
    case "cloudflare":
      return generateCloudflareConfig();
    default:
      return null;
  }
}

/**
 * Generate a Vercel configuration file.
 */
export function generateVercelConfig(
  context: TeamContextProfile,
): GeneratedFile {
  const config: Record<string, unknown> = {
    $schema: "https://openapi.vercel.sh/vercel.json",
  };

  // Add framework-specific settings
  if (context.framework.metaFramework === "nextjs") {
    config.framework = "nextjs";
  } else if (context.framework.metaFramework === "nuxt") {
    config.framework = "nuxtjs";
  } else if (context.framework.metaFramework === "sveltekit") {
    config.framework = "sveltekit";
  }

  // Add environment variable references
  if (context.infra.environments.length > 0) {
    const envVars: Record<string, string>[] = [];
    for (const env of context.infra.environments) {
      for (const [key] of Object.entries(env.variables)) {
        envVars.push({
          key,
          value: `@${key.toLowerCase().replace(/_/g, "-")}`,
          target: [env.name === "production" ? "production" : env.name === "staging" ? "preview" : "development"] as unknown as string,
        });
      }
    }
    if (envVars.length > 0) {
      config.env = envVars;
    }
  }

  return {
    path: "vercel.json",
    content: JSON.stringify(config, null, 2) + "\n",
    language: "json",
    category: "config",
  };
}

function generateNetlifyConfig(context: TeamContextProfile): GeneratedFile {
  const buildCommand = context.framework.metaFramework === "nuxt"
    ? "npx nuxi build"
    : "npm run build";

  const publishDir = context.framework.metaFramework === "nextjs"
    ? ".next"
    : context.framework.metaFramework === "nuxt"
      ? ".output/public"
      : "dist";

  const content = `[build]
  command = "${buildCommand}"
  publish = "${publishDir}"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
`;

  return {
    path: "netlify.toml",
    content,
    language: "plaintext",
    category: "config",
  };
}

function generateCloudflareConfig(): GeneratedFile {
  return {
    path: "wrangler.toml",
    content: `name = "app"
main = "src/worker.ts"
compatibility_date = "2024-01-01"

[site]
bucket = "./dist"
`,
    language: "plaintext",
    category: "config",
  };
}

// ─── Docker ─────────────────────────────────────────────────────────────────

/**
 * Generate a basic multi-stage Dockerfile.
 */
export function generateDockerfile(
  context: TeamContextProfile,
): GeneratedFile {
  const buildCommand = context.framework.metaFramework === "nuxt"
    ? "npx nuxi build"
    : "npm run build";

  const content = `# ── Build stage ──────────────────────────────────────────────────────
FROM node:22-alpine AS builder

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN ${buildCommand}

# ── Production stage ─────────────────────────────────────────────────
FROM node:22-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production

# Copy only production dependencies
COPY package.json package-lock.json ./
RUN npm ci --omit=dev

# Copy build output
COPY --from=builder /app/dist ./dist

EXPOSE 3000

CMD ["node", "dist/server/index.js"]
`;

  return {
    path: "Dockerfile",
    content,
    language: "dockerfile",
    category: "config",
  };
}

// ─── Feature flags ──────────────────────────────────────────────────────────

function generateFeatureFlagSetup(
  context: TeamContextProfile,
): GeneratedFile | null {
  const ff = context.infra.featureFlags;
  if (!ff) return null;

  switch (ff.provider) {
    case "launchdarkly":
      return {
        path: "lib/feature-flags.ts",
        content: `import * as LaunchDarkly from "launchdarkly-js-client-sdk";

let ldClient: LaunchDarkly.LDClient | null = null;

export async function initFeatureFlags(userKey: string) {
  ldClient = LaunchDarkly.initialize(
    process.env.NEXT_PUBLIC_LAUNCHDARKLY_SDK_KEY!,
    { key: userKey },
  );

  await ldClient.waitForInitialization();
}

export function isFeatureEnabled(flagKey: string, defaultValue = false): boolean {
  if (!ldClient) return defaultValue;
  return ldClient.variation(flagKey, defaultValue);
}

export function useFeatureFlag(flagKey: string, defaultValue = false): boolean {
  // In a real app, this would be a React hook that subscribes to changes
  return isFeatureEnabled(flagKey, defaultValue);
}
`,
        language: "typescript",
        category: "frontend",
      };

    case "posthog":
      return {
        path: "lib/feature-flags.ts",
        content: `import posthog from "posthog-js";

export function initFeatureFlags() {
  posthog.init(process.env.NEXT_PUBLIC_POSTHOG_KEY!, {
    api_host: process.env.NEXT_PUBLIC_POSTHOG_HOST ?? "https://app.posthog.com",
  });
}

export function isFeatureEnabled(flagKey: string): boolean {
  return posthog.isFeatureEnabled(flagKey) ?? false;
}

export function useFeatureFlag(flagKey: string, defaultValue = false): boolean {
  return isFeatureEnabled(flagKey) || defaultValue;
}
`,
        language: "typescript",
        category: "frontend",
      };

    default:
      return {
        path: "lib/feature-flags.ts",
        content: `// Feature flag client for ${ff.provider}
// TODO: Install and configure the SDK

const flags: Record<string, boolean> = {};

export function isFeatureEnabled(flagKey: string, defaultValue = false): boolean {
  return flags[flagKey] ?? defaultValue;
}

export function useFeatureFlag(flagKey: string, defaultValue = false): boolean {
  return isFeatureEnabled(flagKey, defaultValue);
}
`,
        language: "typescript",
        category: "frontend",
      };
  }
}

// ─── Monitoring ─────────────────────────────────────────────────────────────

function generateMonitoringSetup(
  context: TeamContextProfile,
): GeneratedFile | null {
  switch (context.infra.monitoring) {
    case "sentry":
      return {
        path: "lib/monitoring.ts",
        content: `import * as Sentry from "@sentry/nextjs";

export function initMonitoring() {
  Sentry.init({
    dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
    tracesSampleRate: process.env.NODE_ENV === "production" ? 0.1 : 1.0,
    environment: process.env.NODE_ENV,
  });
}

export function captureError(error: Error, context?: Record<string, unknown>) {
  Sentry.captureException(error, { extra: context });
}

export function setUser(user: { id: string; email?: string }) {
  Sentry.setUser(user);
}
`,
        language: "typescript",
        category: "frontend",
      };

    case "posthog":
      return {
        path: "lib/monitoring.ts",
        content: `import posthog from "posthog-js";

export function initMonitoring() {
  posthog.init(process.env.NEXT_PUBLIC_POSTHOG_KEY!, {
    api_host: process.env.NEXT_PUBLIC_POSTHOG_HOST ?? "https://app.posthog.com",
    capture_pageview: true,
    capture_pageleave: true,
  });
}

export function trackEvent(event: string, properties?: Record<string, unknown>) {
  posthog.capture(event, properties);
}

export function setUser(user: { id: string; email?: string }) {
  posthog.identify(user.id, { email: user.email });
}
`,
        language: "typescript",
        category: "frontend",
      };

    default:
      return null;
  }
}

// ─── Helpers ────────────────────────────────────────────────────────────────

function shouldGenerateDocker(context: TeamContextProfile): boolean {
  const noDockerHosts = new Set(["vercel", "netlify", "cloudflare"]);
  return !noDockerHosts.has(context.infra.hosting);
}

function getDatabaseURLPlaceholder(type: string, provider?: string): string {
  switch (type) {
    case "postgres":
      return provider === "neon"
        ? "postgresql://user:password@ep-xxx.us-east-2.aws.neon.tech/dbname?sslmode=require"
        : "postgresql://user:password@localhost:5432/dbname";
    case "mysql":
      return "mysql://user:password@localhost:3306/dbname";
    case "sqlite":
      return "file:./dev.db";
    case "mongodb":
      return "mongodb://localhost:27017/dbname";
    case "supabase":
      return "postgresql://postgres:password@db.xxx.supabase.co:5432/postgres";
    default:
      return "your-database-url";
  }
}

function getAuthEnvVars(provider: string): Record<string, string> {
  switch (provider) {
    case "clerk":
      return {
        NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY: "pk_test_xxx",
        CLERK_SECRET_KEY: "sk_test_xxx",
      };
    case "auth0":
      return {
        AUTH0_DOMAIN: "your-tenant.auth0.com",
        AUTH0_CLIENT_ID: "your-client-id",
        AUTH0_CLIENT_SECRET: "your-client-secret",
        AUTH0_AUDIENCE: "your-api-audience",
      };
    case "supabase":
      return {
        NEXT_PUBLIC_SUPABASE_URL: "https://xxx.supabase.co",
        NEXT_PUBLIC_SUPABASE_ANON_KEY: "your-anon-key",
        SUPABASE_SERVICE_ROLE_KEY: "your-service-role-key",
      };
    case "firebase":
      return {
        NEXT_PUBLIC_FIREBASE_API_KEY: "your-api-key",
        NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN: "your-project.firebaseapp.com",
        NEXT_PUBLIC_FIREBASE_PROJECT_ID: "your-project-id",
      };
    case "nextauth":
      return {
        NEXTAUTH_URL: "http://localhost:3000",
        NEXTAUTH_SECRET: "your-secret-key",
      };
    default:
      return {};
  }
}
