// ─── Repo Analysis — Pattern Matchers ────────────────────────────────────────
// Lookup tables that map package.json dependencies, config file names, and
// other signals to TeamContextProfile sub-config values.

import type {
  FrameworkConfig,
  StylingConfig,
  BackendConfig,
  InfraConfig,
} from "@/core/context/types";

// ─── Framework Patterns ──────────────────────────────────────────────────────
// Maps a dependency name found in package.json to the corresponding
// FrameworkConfig. Checked in order — first match wins.

export const FRAMEWORK_PATTERNS: Record<string, FrameworkConfig> = {
  next: { id: "react", metaFramework: "nextjs" },
  "react-native": { id: "react-native", metaFramework: "none" },
  react: { id: "react", metaFramework: "none" },
  nuxt: { id: "vue", metaFramework: "nuxt" },
  vue: { id: "vue", metaFramework: "none" },
  svelte: { id: "svelte", metaFramework: "none" },
  "@sveltejs/kit": { id: "svelte", metaFramework: "sveltekit" },
  "@angular/core": { id: "angular", metaFramework: "none" },
  "solid-js": { id: "solid", metaFramework: "none" },
  "@builder.io/qwik": { id: "qwik", metaFramework: "none" },
};

/** Ordered list of dependency names to check (order matters for priority). */
export const FRAMEWORK_DETECT_ORDER: string[] = [
  "next",
  "@sveltejs/kit",
  "nuxt",
  "react-native",
  "react",
  "vue",
  "svelte",
  "@angular/core",
  "solid-js",
  "@builder.io/qwik",
];

// ─── Component Library Patterns ──────────────────────────────────────────────

export const COMPONENT_LIB_PATTERNS: Record<string, string> = {
  "@radix-ui/react-dialog": "shadcn",
  "@mui/material": "mui",
  "@chakra-ui/react": "chakra",
  "antd": "ant-design",
  "@headlessui/react": "headless-ui",
  "vuetify": "vuetify",
};

// ─── Icon Library Patterns ───────────────────────────────────────────────────

export const ICON_LIB_PATTERNS: Record<string, string> = {
  "lucide-react": "lucide",
  "lucide-vue-next": "lucide",
  "@phosphor-icons/react": "phosphor",
  "@heroicons/react": "heroicons",
  "@mui/icons-material": "material-icons",
  "@tabler/icons-react": "tabler",
  "feather-icons": "feather",
  "@iconify/react": "iconify",
  "@carbon/icons-react": "carbon",
};

// ─── Styling Patterns ────────────────────────────────────────────────────────

export const STYLING_PATTERNS: Record<string, StylingConfig["approach"]> = {
  tailwindcss: "tailwind",
  "styled-components": "styled-components",
  "@emotion/react": "emotion",
  "@vanilla-extract/css": "vanilla-extract",
  sass: "scss",
  "unocss": "uno-css",
};

// ─── ORM Patterns ────────────────────────────────────────────────────────────

export const ORM_PATTERNS: Record<string, NonNullable<BackendConfig["orm"]>> = {
  prisma: "prisma",
  "@prisma/client": "prisma",
  drizzle: "drizzle",
  "drizzle-orm": "drizzle",
  typeorm: "typeorm",
  sequelize: "sequelize",
};

// ─── API Layer Patterns ──────────────────────────────────────────────────────

export const API_LAYER_PATTERNS: Record<string, BackendConfig["apiLayer"]> = {
  "@trpc/server": "trpc",
  "@trpc/client": "trpc",
  graphql: "graphql",
  "@apollo/server": "graphql",
  "@apollo/client": "graphql",
};

// ─── Server Framework Patterns ───────────────────────────────────────────────

export const SERVER_FRAMEWORK_PATTERNS: Record<
  string,
  NonNullable<BackendConfig["serverFramework"]>
> = {
  express: "express",
  fastify: "fastify",
  hono: "hono",
};

// ─── Database Patterns ───────────────────────────────────────────────────────

export const DATABASE_PATTERNS: Record<string, string> = {
  "@supabase/supabase-js": "supabase",
  firebase: "firebase",
  "firebase-admin": "firebase",
  pg: "postgres",
  mysql2: "mysql",
  "better-sqlite3": "sqlite",
  mongodb: "mongodb",
  mongoose: "mongodb",
};

// ─── Auth Patterns ───────────────────────────────────────────────────────────

export const AUTH_PATTERNS: Record<string, string> = {
  "@clerk/nextjs": "clerk",
  "@clerk/clerk-react": "clerk",
  "auth0": "auth0",
  "@auth0/nextjs-auth0": "auth0",
  "next-auth": "nextauth",
  "@supabase/auth-helpers-nextjs": "supabase",
  lucia: "lucia",
};

// ─── Hosting / Config File Patterns ──────────────────────────────────────────
// Maps the existence of certain files to hosting platform.

export const HOSTING_FILE_PATTERNS: Record<
  string,
  InfraConfig["hosting"]
> = {
  "vercel.json": "vercel",
  ".vercel": "vercel",
  "netlify.toml": "netlify",
  "fly.toml": "fly-io",
  "railway.json": "railway",
  "wrangler.toml": "cloudflare",
};

// ─── CI/CD File Patterns ─────────────────────────────────────────────────────

export const CICD_FILE_PATTERNS: Record<string, string> = {
  ".github/workflows": "github-actions",
  ".gitlab-ci.yml": "gitlab-ci",
  ".circleci": "circle-ci",
  "Jenkinsfile": "jenkins",
};

// ─── Linter / Formatter Patterns ─────────────────────────────────────────────

export const LINTER_PATTERNS: Record<string, string> = {
  eslint: "eslint",
  "@biomejs/biome": "biome",
  "biome": "biome",
  oxlint: "oxlint",
};

export const FORMATTER_PATTERNS: Record<string, string> = {
  prettier: "prettier",
  "@biomejs/biome": "biome",
  dprint: "dprint",
};

// ─── Test Framework Patterns ─────────────────────────────────────────────────

export const TEST_FRAMEWORK_PATTERNS: Record<string, string> = {
  vitest: "vitest",
  jest: "jest",
  "@testing-library/react": "testing-library",
  "@playwright/test": "playwright",
  cypress: "cypress",
};
