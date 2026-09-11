// ─── Team Context Profile — Defaults & Presets ──────────────────────────────
// Sensible starting-point profiles for the most common modern stacks.

import type {
  TeamContextProfile,
  BreakpointConfig,
} from "./types";

// ─── Default breakpoints ─────────────────────────────────────────────────────

/** Tailwind-style responsive breakpoints. */
export const DEFAULT_BREAKPOINTS: BreakpointConfig[] = [
  { name: "sm", minWidth: 640 },
  { name: "md", minWidth: 768 },
  { name: "lg", minWidth: 1024 },
  { name: "xl", minWidth: 1280 },
  { name: "2xl", minWidth: 1536 },
];

// ─── Presets ─────────────────────────────────────────────────────────────────

/**
 * Partial profile presets keyed by a short identifier.
 *
 * Each preset provides sensible defaults for every field that is relevant
 * to its tier. Fields from higher tiers are still present but set to
 * neutral/"none" values so the profile remains structurally complete.
 */
export const CONTEXT_PRESETS: Record<string, Partial<TeamContextProfile>> = {
  // ── Next.js + shadcn/ui + Tailwind + Prisma + Vercel ──────────────────
  "next-shadcn": {
    name: "Next.js + shadcn/ui",
    tier: 2,

    // Tier 1
    framework: { id: "react", version: "19.x", metaFramework: "nextjs" },
    componentLibrary: { id: "shadcn", version: "latest" },
    iconLibrary: { id: "lucide" },
    styling: { approach: "tailwind", version: "4.x" },
    tokenOutput: { formats: ["css-vars", "tailwind-theme"], prefix: "--" },
    codePatterns: {
      naming: "camelCase",
      fileNaming: "kebab-case",
      componentFilePattern: "folder-with-index",
      testFramework: "vitest",
      testPattern: "co-located",
      linter: "eslint",
      formatter: "prettier",
    },
    breakpoints: DEFAULT_BREAKPOINTS,

    // Tier 2
    backend: {
      apiLayer: "trpc",
      serverFramework: "none",
      orm: "prisma",
      serverless: true,
    },
    database: { type: "postgres", provider: "neon" },
    auth: {
      provider: "clerk",
      flows: ["login", "signup", "oauth", "forgot-password"],
      rbac: false,
    },
    data: [],

    // Tier 3 — neutral defaults
    infra: {
      hosting: "vercel",
      environments: [
        { name: "development", variables: {} },
        { name: "staging", variables: {} },
        { name: "production", variables: {} },
      ],
      featureFlags: undefined,
      cicd: { provider: "vercel", autoDeployBranch: "main" },
      monitoring: "none",
    },
    i18n: {
      enabled: false,
      defaultLocale: "en",
      locales: ["en"],
      strategy: "key-based",
      managementTool: "none",
    },
  },

  // ── Next.js + MUI + Emotion + Prisma + Vercel ─────────────────────────
  "next-mui": {
    name: "Next.js + MUI",
    tier: 2,

    framework: { id: "react", version: "19.x", metaFramework: "nextjs" },
    componentLibrary: { id: "mui", version: "6.x" },
    iconLibrary: { id: "material-icons" },
    styling: { approach: "emotion" },
    tokenOutput: { formats: ["css-vars", "json-dtcg"], prefix: "--mui" },
    codePatterns: {
      naming: "camelCase",
      fileNaming: "PascalCase",
      componentFilePattern: "single-file",
      testFramework: "jest",
      testPattern: "separate-folder",
      linter: "eslint",
      formatter: "prettier",
    },
    breakpoints: DEFAULT_BREAKPOINTS,

    backend: {
      apiLayer: "rest",
      serverFramework: "express",
      orm: "prisma",
      serverless: false,
    },
    database: { type: "postgres", provider: "aws-rds" },
    auth: {
      provider: "auth0",
      flows: ["login", "signup", "oauth", "forgot-password"],
      rbac: true,
    },
    data: [],

    infra: {
      hosting: "vercel",
      environments: [
        { name: "development", variables: {} },
        { name: "staging", variables: {} },
        { name: "production", variables: {} },
      ],
      cicd: { provider: "github-actions", autoDeployBranch: "main" },
      monitoring: "sentry",
    },
    i18n: {
      enabled: false,
      defaultLocale: "en",
      locales: ["en"],
      strategy: "key-based",
      managementTool: "none",
    },
  },

  // ── Nuxt + Vuetify + SCSS ─────────────────────────────────────────────
  "vue-vuetify": {
    name: "Nuxt + Vuetify",
    tier: 1,

    framework: { id: "vue", version: "3.x", metaFramework: "nuxt" },
    componentLibrary: { id: "vuetify", version: "3.x" },
    iconLibrary: { id: "material-icons" },
    styling: { approach: "scss" },
    tokenOutput: { formats: ["scss", "css-vars"], prefix: "--v" },
    codePatterns: {
      naming: "camelCase",
      fileNaming: "PascalCase",
      componentFilePattern: "single-file",
      testFramework: "vitest",
      testPattern: "separate-folder",
      linter: "eslint",
      formatter: "prettier",
    },
    breakpoints: DEFAULT_BREAKPOINTS,

    backend: { apiLayer: "none" },
    database: { type: "none" },
    auth: { provider: "none", flows: [] },
    data: [],

    infra: {
      hosting: "netlify",
      environments: [
        { name: "development", variables: {} },
        { name: "production", variables: {} },
      ],
      cicd: { provider: "github-actions", autoDeployBranch: "main" },
      monitoring: "none",
    },
    i18n: {
      enabled: false,
      defaultLocale: "en",
      locales: ["en"],
      strategy: "key-based",
      managementTool: "none",
    },
  },

  // ── SvelteKit + Skeleton UI + Tailwind ────────────────────────────────
  "svelte-skeleton": {
    name: "SvelteKit + Skeleton",
    tier: 1,

    framework: { id: "svelte", version: "5.x", metaFramework: "sveltekit" },
    componentLibrary: { id: "custom" },
    iconLibrary: { id: "lucide" },
    styling: { approach: "tailwind", version: "4.x" },
    tokenOutput: { formats: ["css-vars", "tailwind-theme"], prefix: "--sk" },
    codePatterns: {
      naming: "camelCase",
      fileNaming: "kebab-case",
      componentFilePattern: "single-file",
      testFramework: "vitest",
      testPattern: "co-located",
      linter: "eslint",
      formatter: "prettier",
    },
    breakpoints: DEFAULT_BREAKPOINTS,

    backend: { apiLayer: "none" },
    database: { type: "none" },
    auth: { provider: "none", flows: [] },
    data: [],

    infra: {
      hosting: "vercel",
      environments: [
        { name: "development", variables: {} },
        { name: "production", variables: {} },
      ],
      cicd: { provider: "vercel", autoDeployBranch: "main" },
      monitoring: "none",
    },
    i18n: {
      enabled: false,
      defaultLocale: "en",
      locales: ["en"],
      strategy: "key-based",
      managementTool: "none",
    },
  },

  // ── React Native + NativeWind + Expo ──────────────────────────────────
  "react-native": {
    name: "React Native + Expo",
    tier: 1,

    framework: { id: "react-native", version: "0.76.x", metaFramework: "none" },
    componentLibrary: { id: "custom" },
    iconLibrary: { id: "phosphor" },
    styling: { approach: "tailwind", version: "4.x" },
    tokenOutput: { formats: ["json-dtcg", "swift", "kotlin"], prefix: "--rn" },
    codePatterns: {
      naming: "camelCase",
      fileNaming: "PascalCase",
      componentFilePattern: "folder-with-named",
      testFramework: "jest",
      testPattern: "separate-folder",
      linter: "eslint",
      formatter: "prettier",
    },
    breakpoints: [
      { name: "phone", minWidth: 0 },
      { name: "tablet", minWidth: 768 },
      { name: "desktop", minWidth: 1024 },
    ],

    backend: { apiLayer: "none" },
    database: { type: "none" },
    auth: { provider: "none", flows: [] },
    data: [],

    infra: {
      hosting: "aws",
      environments: [
        { name: "development", variables: {} },
        { name: "production", variables: {} },
      ],
      cicd: { provider: "github-actions" },
      monitoring: "none",
    },
    i18n: {
      enabled: false,
      defaultLocale: "en",
      locales: ["en"],
      strategy: "key-based",
      managementTool: "none",
    },
  },

  // ── Design Only (Tier 0) ──────────────────────────────────────────────
  "design-only": {
    name: "Design Only",
    tier: 0,

    framework: { id: "react", metaFramework: "none" },
    componentLibrary: { id: "none" },
    iconLibrary: { id: "lucide" },
    styling: { approach: "css-modules" },
    tokenOutput: { formats: ["json-dtcg", "css-vars"] },
    codePatterns: {
      naming: "camelCase",
      fileNaming: "kebab-case",
      componentFilePattern: "single-file",
      testFramework: "none",
      linter: "none",
      formatter: "none",
    },
    breakpoints: DEFAULT_BREAKPOINTS,

    backend: { apiLayer: "none" },
    database: { type: "none" },
    auth: { provider: "none", flows: [] },
    data: [],

    infra: {
      hosting: "vercel",
      environments: [],
      monitoring: "none",
    },
    i18n: {
      enabled: false,
      defaultLocale: "en",
      locales: ["en"],
      strategy: "key-based",
      managementTool: "none",
    },
  },
};

// ─── Factory ─────────────────────────────────────────────────────────────────

/**
 * Create a fully-populated `TeamContextProfile`, optionally seeded from a
 * named preset. Any fields the preset does not provide are filled with
 * neutral defaults.
 *
 * @param presetId - Key into `CONTEXT_PRESETS` (e.g. `"next-shadcn"`).
 *                   When omitted the "design-only" preset is used.
 */
export function createDefaultProfile(
  presetId?: string,
): TeamContextProfile {
  const preset = presetId
    ? CONTEXT_PRESETS[presetId] ?? CONTEXT_PRESETS["design-only"]
    : CONTEXT_PRESETS["design-only"];

  const base: TeamContextProfile = {
    name: "Untitled Profile",
    tier: 0,

    // Tier 1
    framework: { id: "react", metaFramework: "none" },
    componentLibrary: { id: "none" },
    iconLibrary: { id: "lucide" },
    styling: { approach: "css-modules" },
    tokenOutput: { formats: ["json-dtcg", "css-vars"] },
    codePatterns: {
      naming: "camelCase",
      fileNaming: "kebab-case",
      componentFilePattern: "single-file",
      testFramework: "none",
      linter: "none",
      formatter: "none",
    },
    breakpoints: DEFAULT_BREAKPOINTS,

    // Tier 2
    backend: { apiLayer: "none" },
    database: { type: "none" },
    auth: { provider: "none", flows: [] },
    data: [],

    // Tier 3
    infra: {
      hosting: "vercel",
      environments: [],
      monitoring: "none",
    },
    i18n: {
      enabled: false,
      defaultLocale: "en",
      locales: ["en"],
      strategy: "key-based",
      managementTool: "none",
    },
  };

  // Shallow-merge each field from the preset over the base
  return {
    ...base,
    ...preset,
  } as TeamContextProfile;
}
