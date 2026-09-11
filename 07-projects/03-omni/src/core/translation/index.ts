// ─── AI Translation Engine — Barrel Export ──────────────────────────────────
// Layer 3 of "Design Once, Output Anywhere":
// IR + Team Context -> Claude -> idiomatic full-stack code.

// Types
export type {
  TranslationRequest,
  TranslationResult,
  TranslationScope,
  GeneratedFile,
  FileCategory,
  ValidationResult,
  ValidationError,
  ValidationWarning,
} from "./types";

// Core service
export { translateToCode, parseTranslationResponse } from "./service";

// Prompt builders
export {
  buildTranslationPrompt,
  getFrameworkSection,
  getStylingSection,
  getComponentLibSection,
  getBackendSection,
  getOutputFormatInstructions,
} from "./prompts";

// Validation
export { validateGenerated } from "./validator";

// Generators
export { generateFrontendFiles } from "./generators/frontend";
export { generateBackendFiles } from "./generators/backend";
export { generateInfraFiles } from "./generators/infra";
