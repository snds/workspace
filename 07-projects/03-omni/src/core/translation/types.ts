// ─── AI Translation Engine — Types ───────────────────────────────────────────
// Core types for Layer 3: IR + Team Context -> Claude -> idiomatic code.

import type { IRNode } from "@/core/ir/types";
import type { TeamContextProfile } from "@/core/context/types";

// ─── Translation scope ──────────────────────────────────────────────────────

/**
 * What kind of output to generate.
 *
 * | Scope         | Description                                  |
 * |---------------|----------------------------------------------|
 * | component     | Single component file(s)                     |
 * | page          | Full page with layout and routing             |
 * | full-stack    | Frontend + backend + data fetching            |
 * | tokens-only   | Just design tokens (CSS vars, theme, etc.)    |
 * | styles-only   | Just CSS / styling output                     |
 */
export type TranslationScope =
  | "component"
  | "page"
  | "full-stack"
  | "tokens-only"
  | "styles-only";

// ─── Translation request ────────────────────────────────────────────────────

/** Request to translate IR nodes to code. */
export interface TranslationRequest {
  /** The IR nodes to translate. */
  nodes: IRNode[];
  /** Team context defining the target stack. */
  context: TeamContextProfile;
  /** What to generate. */
  scope: TranslationScope;
  /** Additional instructions for the AI. */
  instructions?: string;
}

// ─── Translation result ─────────────────────────────────────────────────────

/** Result of a translation. */
export interface TranslationResult {
  /** Generated files. */
  files: GeneratedFile[];
  /** Any warnings or notes from the translation pipeline. */
  warnings?: string[];
  /** Token usage stats (when AI is used). */
  usage?: { inputTokens: number; outputTokens: number };
}

// ─── Generated file ─────────────────────────────────────────────────────────

/** Category of a generated file. */
export type FileCategory =
  | "frontend"
  | "backend"
  | "styling"
  | "config"
  | "test"
  | "types";

/** A single generated file. */
export interface GeneratedFile {
  /** Relative file path (e.g. "components/Button.tsx"). */
  path: string;
  /** File content. */
  content: string;
  /** Language for syntax highlighting. */
  language: string;
  /** Category of the generated file. */
  category: FileCategory;
}

// ─── Validation ─────────────────────────────────────────────────────────────

/** Validation result from the validation pipeline. */
export interface ValidationResult {
  valid: boolean;
  errors: ValidationError[];
  warnings: ValidationWarning[];
}

/** A validation error or warning for a specific file. */
export interface ValidationError {
  file: string;
  line?: number;
  message: string;
  severity: "error" | "warning";
}

/** A validation warning with an optional fix suggestion. */
export interface ValidationWarning {
  file: string;
  message: string;
  suggestion?: string;
}
