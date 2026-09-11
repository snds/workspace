// ─── Team Context Profile — Types ────────────────────────────────────────────
// Full-stack team context that drives code generation, token output, and
// component scaffolding. Organised into four progressive usage tiers.

// ─── Usage Tier ──────────────────────────────────────────────────────────────

/**
 * Which usage tier is active. Each tier is a superset of the previous:
 *
 * | Tier | Scope                         |
 * |------|-------------------------------|
 * | 0    | Design Only                   |
 * | 1    | Design + Frontend             |
 * | 2    | Design + Full-Stack           |
 * | 3    | Design + Full-Stack + Prod    |
 */
export type UsageTier = 0 | 1 | 2 | 3;

// ─── Top-Level Profile ───────────────────────────────────────────────────────

/** The root team context profile that configures every layer of code gen. */
export interface TeamContextProfile {
  /** Display name for this profile (e.g. "Acme Corp — Web App"). */
  name: string;

  /** Active usage tier. */
  tier: UsageTier;

  // ── Tier 0: Design Only ──────────────────────────────────────────────────
  // (always available — no additional configuration needed)

  // ── Tier 1: Design + Frontend ────────────────────────────────────────────

  /** Frontend framework and meta-framework selection. */
  framework: FrameworkConfig;

  /** Component library / design-system base. */
  componentLibrary: ComponentLibConfig;

  /** Icon library preference. */
  iconLibrary: IconLibConfig;

  /** CSS / styling approach. */
  styling: StylingConfig;

  /** Which token output formats to generate. */
  tokenOutput: TokenOutputConfig;

  /** Naming, file structure, and tooling conventions. */
  codePatterns: CodePatternsConfig;

  /** Responsive breakpoints. */
  breakpoints: BreakpointConfig[];

  // ── Tier 2: Design + Full-Stack ──────────────────────────────────────────

  /** Backend API and server framework config. */
  backend: BackendConfig;

  /** Database type and provider. */
  database: DatabaseConfig;

  /** Authentication provider and flows. */
  auth: AuthConfig;

  /** External data sources the app consumes. */
  data: DataSourceConfig[];

  // ── Tier 3: Design + Full-Stack + Production ─────────────────────────────

  /** Hosting, CI/CD, monitoring, and feature flags. */
  infra: InfraConfig;

  /** Internationalisation settings. */
  i18n: I18nConfig;
}

// ─── Tier 1 Sub-Configs ──────────────────────────────────────────────────────

/** Frontend framework selection. */
export interface FrameworkConfig {
  /** Framework identifier. */
  id:
    | "react"
    | "vue"
    | "svelte"
    | "angular"
    | "react-native"
    | "flutter"
    | "solid"
    | "qwik";
  /** Specific version constraint (e.g. "19.x"). */
  version?: string;
  /** Meta-framework layered on top (e.g. Next.js, Nuxt). */
  metaFramework?:
    | "nextjs"
    | "remix"
    | "nuxt"
    | "sveltekit"
    | "astro"
    | "none";
}

/** Component library / UI kit selection. */
export interface ComponentLibConfig {
  /** Library identifier. */
  id:
    | "shadcn"
    | "mui"
    | "chakra"
    | "ant-design"
    | "radix"
    | "headless-ui"
    | "vuetify"
    | "custom"
    | "none";
  /** Specific version constraint. */
  version?: string;
}

/** Icon library selection. */
export interface IconLibConfig {
  /** Library identifier. */
  id:
    | "lucide"
    | "phosphor"
    | "heroicons"
    | "material-icons"
    | "tabler"
    | "feather"
    | "carbon"
    | "iconify"
    | "custom";
  /**
   * Override the default semantic-to-icon mapping.
   * Key = semantic name (e.g. "close", "search"), value = icon name.
   */
  semanticMappingOverrides?: Record<string, string>;
}

/** CSS / styling approach. */
export interface StylingConfig {
  /** Primary styling strategy. */
  approach:
    | "tailwind"
    | "css-modules"
    | "styled-components"
    | "emotion"
    | "vanilla-extract"
    | "scss"
    | "css-in-js"
    | "uno-css";
  /** Specific version constraint. */
  version?: string;
}

/** Token output format configuration. */
export interface TokenOutputConfig {
  /** Formats to generate on each export. */
  formats: (
    | "css-vars"
    | "tailwind-theme"
    | "scss"
    | "json-dtcg"
    | "swift"
    | "kotlin"
    | "flutter-dart"
  )[];
  /** Prefix applied to generated names (e.g. `"--omni"`). */
  prefix?: string;
}

/** Code style and tooling conventions. */
export interface CodePatternsConfig {
  /** Variable / property naming convention. */
  naming: "camelCase" | "PascalCase" | "kebab-case" | "snake_case";
  /** File naming convention. */
  fileNaming: "camelCase" | "PascalCase" | "kebab-case";
  /** How component files are structured on disk. */
  componentFilePattern:
    | "single-file"
    | "folder-with-index"
    | "folder-with-named";
  /** Test runner / framework. */
  testFramework?:
    | "vitest"
    | "jest"
    | "testing-library"
    | "playwright"
    | "cypress"
    | "none";
  /** Where test files live relative to source. */
  testPattern?: "co-located" | "separate-folder";
  /** Linter. */
  linter?: "eslint" | "biome" | "oxlint" | "none";
  /** Formatter. */
  formatter?: "prettier" | "biome" | "dprint" | "none";
}

/** A single responsive breakpoint definition. */
export interface BreakpointConfig {
  /** Breakpoint name (e.g. "sm", "md"). */
  name: string;
  /** Minimum viewport width in pixels. */
  minWidth: number;
}

// ─── Tier 2 Sub-Configs ──────────────────────────────────────────────────────

/** Backend API layer and server framework. */
export interface BackendConfig {
  /** API paradigm. */
  apiLayer: "rest" | "graphql" | "trpc" | "grpc" | "none";
  /** Path to an API schema file (e.g. OpenAPI spec, GraphQL SDL). */
  apiSchemaPath?: string;
  /** Server-side framework. */
  serverFramework?:
    | "express"
    | "fastify"
    | "hono"
    | "django"
    | "rails"
    | "spring"
    | "laravel"
    | "phoenix"
    | "none";
  /** ORM / query builder. */
  orm?:
    | "prisma"
    | "drizzle"
    | "typeorm"
    | "sqlalchemy"
    | "sequelize"
    | "none";
  /** Whether the backend runs as serverless functions. */
  serverless?: boolean;
}

/** Database type and hosting provider. */
export interface DatabaseConfig {
  /** Database engine. */
  type:
    | "postgres"
    | "mysql"
    | "sqlite"
    | "mongodb"
    | "supabase"
    | "firebase"
    | "dynamodb"
    | "none";
  /** Managed hosting provider. */
  provider?:
    | "supabase"
    | "planetscale"
    | "neon"
    | "railway"
    | "aws-rds"
    | "self-hosted";
  /** Path to the database schema file. */
  schemaPath?: string;
}

/** Authentication provider and supported flows. */
export interface AuthConfig {
  /** Auth provider. */
  provider:
    | "clerk"
    | "auth0"
    | "supabase"
    | "firebase"
    | "nextauth"
    | "lucia"
    | "custom"
    | "none";
  /** Enabled authentication flows. */
  flows: (
    | "login"
    | "signup"
    | "forgot-password"
    | "magic-link"
    | "oauth"
    | "passkey"
  )[];
  /** Whether role-based access control is enabled. */
  rbac?: boolean;
}

/** An external data source the app consumes. */
export interface DataSourceConfig {
  /** Unique identifier for this source. */
  id: string;
  /** Human-readable label. */
  name: string;
  /** Source type / protocol. */
  type:
    | "rest-api"
    | "graphql"
    | "database"
    | "websocket"
    | "storage"
    | "realtime";
  /** Base URL (for network sources). */
  baseUrl?: string;
  /** Path to a schema or type definition. */
  schemaPath?: string;
  /** How requests are authenticated. */
  authMethod?: "bearer" | "api-key" | "oauth" | "cookie" | "none";
}

// ─── Tier 3 Sub-Configs ──────────────────────────────────────────────────────

/** Infrastructure, deployment, and observability. */
export interface InfraConfig {
  /** Primary hosting platform. */
  hosting:
    | "vercel"
    | "netlify"
    | "aws"
    | "azure"
    | "gcp"
    | "railway"
    | "fly-io"
    | "cloudflare"
    | "self-hosted";
  /** Deployment environments (dev, staging, prod, etc.). */
  environments: EnvironmentConfig[];
  /** Feature flag provider. */
  featureFlags?: FeatureFlagConfig;
  /** CI / CD pipeline. */
  cicd?: CICDConfig;
  /** Error / performance monitoring. */
  monitoring?:
    | "sentry"
    | "datadog"
    | "posthog"
    | "logrocket"
    | "none";
}

/** A single deployment environment. */
export interface EnvironmentConfig {
  /** Environment name (e.g. "development", "staging", "production"). */
  name: string;
  /** Environment-specific variables (keys only — values are placeholders). */
  variables: Record<string, string>;
}

/** Feature flag provider configuration. */
export interface FeatureFlagConfig {
  /** Provider. */
  provider:
    | "launchdarkly"
    | "statsig"
    | "posthog"
    | "flagsmith"
    | "unleash"
    | "custom";
  /** Client-side SDK key (stored securely at runtime). */
  sdkKey?: string;
}

/** CI / CD pipeline configuration. */
export interface CICDConfig {
  /** CI/CD platform. */
  provider:
    | "github-actions"
    | "gitlab-ci"
    | "circle-ci"
    | "jenkins"
    | "vercel"
    | "none";
  /** Branch that triggers automatic deploys. */
  autoDeployBranch?: string;
}

/** Internationalisation configuration. */
export interface I18nConfig {
  /** Whether i18n is enabled. */
  enabled: boolean;
  /** Default / fallback locale (BCP-47). */
  defaultLocale: string;
  /** All supported locales. */
  locales: string[];
  /** Translation string strategy. */
  strategy: "key-based" | "default-language" | "icu-messages";
  /** Translation management platform. */
  managementTool?: "crowdin" | "lokalise" | "phrase" | "none";
}
