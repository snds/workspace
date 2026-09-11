// ─── Token Tier Classification ───────────────────────────────────────────────
// Classifies design tokens into primitive / semantic / component tiers and
// validates that cross-tier references follow the correct direction.

import type { DesignToken, TokenReference } from "@/types/tokens";
import { isReference, extractRefPath } from "@/types/tokens";

// ─── Types ───────────────────────────────────────────────────────────────────

/** The three conceptual tiers of a design-token hierarchy. */
export type TokenTier = "primitive" | "semantic" | "component";

/** A single tier-reference violation returned by `validateTierReferences`. */
export interface ValidationError {
  /** Dot-path of the offending token */
  path: string;
  /** Tier of the offending token */
  tier: TokenTier;
  /** Human-readable explanation of the violation */
  message: string;
}

// ─── Primitive path prefixes ─────────────────────────────────────────────────

const PRIMITIVE_PREFIXES = [
  "spacing.",
  "sizing.",
  "radius.",
  "font.",
] as const;

// ─── Semantic path prefixes ──────────────────────────────────────────────────

const SEMANTIC_PREFIXES = [
  "color.semantic.",
  "text.",
  "background.",
  "border.",
  "surface.",
  "foreground.",
  "accent.",
] as const;

// ─── Component scope keywords ────────────────────────────────────────────────

const COMPONENT_SCOPES = [
  "button.",
  "card.",
  "input.",
  "badge.",
  "dialog.",
  "modal.",
  "select.",
  "checkbox.",
  "radio.",
  "switch.",
  "toggle.",
  "tooltip.",
  "popover.",
  "dropdown.",
  "avatar.",
  "alert.",
  "toast.",
  "tab.",
  "table.",
  "navigation.",
  "sidebar.",
  "header.",
  "footer.",
] as const;

// ─── Classification ─────────────────────────────────────────────────────────

/**
 * Classify a single token into one of the three tiers based on its dot-path
 * and its extension metadata.
 *
 * Classification rules (evaluated in order):
 * 1. **Component** — path contains a known component scope keyword.
 * 2. **Primitive** — path starts with a raw-value prefix *or* it is a `color.*`
 *    token carrying the `omni.shade` extension (palette swatch).
 * 3. **Semantic** — path starts with a semantic prefix *or* the token carries
 *    the `omni.category` extension.
 * 4. **Fallback** — if the `$value` is a reference the token is at least
 *    "semantic"; otherwise it falls back to "primitive".
 */
export function classifyTier(path: string, token: DesignToken): TokenTier {
  // 1. Component — path contains a component scope
  if (COMPONENT_SCOPES.some((scope) => path.includes(scope))) {
    return "component";
  }

  // 2. Primitive — raw-value palette or base scale
  const isPrimitivePath = PRIMITIVE_PREFIXES.some((p) => path.startsWith(p));
  const isPaletteColor =
    path.startsWith("color.") &&
    token.$extensions?.["omni.shade"] !== undefined;

  if (isPrimitivePath || isPaletteColor) {
    return "primitive";
  }

  // 3. Semantic — named-role token or category-tagged
  const isSemanticPath = SEMANTIC_PREFIXES.some((p) => path.startsWith(p));
  const hasCategory = token.$extensions?.["omni.category"] !== undefined;

  if (isSemanticPath || hasCategory) {
    return "semantic";
  }

  // 4. Fallback: reference depth heuristic
  if (isReference(token.$value)) {
    return "semantic";
  }

  return "primitive";
}

// ─── Validation ──────────────────────────────────────────────────────────────

/**
 * Validate that cross-tier token references flow in the correct direction:
 *
 * - **Primitive** tokens must NOT reference other tokens.
 * - **Semantic** tokens should only reference **primitive** tokens.
 * - **Component** tokens may reference **semantic** or **primitive** tokens.
 *
 * @returns An array of `ValidationError` objects for every violation found.
 *          An empty array means the token set is valid.
 */
export function validateTierReferences(
  entries: Record<string, DesignToken>,
): ValidationError[] {
  const errors: ValidationError[] = [];

  // Pre-compute tier lookup so we don't re-classify on every reference check
  const tierOf = new Map<string, TokenTier>();
  for (const [path, token] of Object.entries(entries)) {
    tierOf.set(path, classifyTier(path, token));
  }

  for (const [path, token] of Object.entries(entries)) {
    const tier = tierOf.get(path)!;

    // Collect all references embedded in the token (direct + mode overrides)
    const refs: string[] = [];
    if (isReference(token.$value)) {
      refs.push(extractRefPath(token.$value as TokenReference));
    }
    if (token.$extensions?.["omni.mode"]) {
      for (const modeVal of Object.values(token.$extensions["omni.mode"])) {
        if (isReference(modeVal)) {
          refs.push(extractRefPath(modeVal as TokenReference));
        }
      }
    }

    for (const refPath of refs) {
      const refTier = tierOf.get(refPath);

      if (tier === "primitive") {
        errors.push({
          path,
          tier,
          message: `Primitive token "${path}" must not reference other tokens, but references "{${refPath}}".`,
        });
      } else if (tier === "semantic") {
        if (refTier && refTier !== "primitive") {
          errors.push({
            path,
            tier,
            message: `Semantic token "${path}" should only reference primitive tokens, but references "${refPath}" which is "${refTier}".`,
          });
        }
      } else if (tier === "component") {
        if (refTier && refTier === "component") {
          errors.push({
            path,
            tier,
            message: `Component token "${path}" should not reference other component tokens, but references "${refPath}".`,
          });
        }
      }
    }
  }

  return errors;
}

// ─── Grouping ────────────────────────────────────────────────────────────────

/**
 * Group every token path in `entries` by its tier.
 *
 * @returns A record keyed by `TokenTier` whose values are arrays of dot-paths.
 */
export function getTokensByTier(
  entries: Record<string, DesignToken>,
): Record<TokenTier, string[]> {
  const result: Record<TokenTier, string[]> = {
    primitive: [],
    semantic: [],
    component: [],
  };

  for (const [path, token] of Object.entries(entries)) {
    const tier = classifyTier(path, token);
    result[tier].push(path);
  }

  return result;
}
