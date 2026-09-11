// ─── Production Infrastructure — Barrel Export ─────────────────────────────────
// Re-exports all infrastructure types, utilities, and generators.
// ──────────────────────────────────────────────────────────────────────────────

export type {
  Environment,
  EnvironmentVariable,
  FeatureFlag,
  ABTest,
  ABTestVariant,
  DeployTarget,
} from "./types";

export {
  DEFAULT_ENVIRONMENTS,
  createEnvVar,
  generateEnvFile,
  validateEnvironment,
} from "./environments";

export {
  createFeatureFlag,
  resolveFlagValue,
  createABTest,
  generateFlagCheckCode,
  generateABTestCode,
} from "./featureFlags";

export { generateCICDConfig } from "./cicd";
