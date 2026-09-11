// ─── W3C Design Tokens Community Group (DTCG) Types ──────────────────────────
// Aligned with https://tr.designtokens.org/format/

export type DTCGType =
  | 'color'
  | 'dimension'
  | 'font-family'
  | 'font-weight'
  | 'font-style'
  | 'number'
  | 'string'
  | 'duration'
  | 'cubic-bezier'
  | 'shadow'
  | 'gradient'
  | 'typography'
  | 'transition';

/** Reference to another token using W3C {dot.path} syntax */
export type TokenReference = string; // e.g. "{color.brand.primary.500}"

export interface ShadowValue {
  color: string | TokenReference;
  offsetX: string;
  offsetY: string;
  blur: string;
  spread: string;
  inset?: boolean;
}

export type TokenValue = string | number | boolean | ShadowValue | ShadowValue[];

// ─── Omni-specific extensions (stored in $extensions per W3C spec) ────────────

export interface OmniExtensions {
  /** Per-mode value overrides, e.g. { dark: "{color.neutral.950}" } */
  "omni.mode"?: Record<string, TokenValue | TokenReference>;
  /** WCAG contrast data for color tokens */
  "omni.wcag"?: {
    contrastOnWhite: number;
    contrastOnBlack: number;
    aa: boolean;
    aaa: boolean;
  };
  /** For primitive palette tokens: which palette key this shade belongs to */
  "omni.paletteKey"?: string;
  /** For primitive palette tokens: step index (1–12, Radix step) */
  "omni.shade"?: number;
  /** For semantic color tokens: category (background, foreground, border, etc.) */
  "omni.category"?: string;
  /** System-seeded tokens: warn user before deleting */
  "omni.readonly"?: boolean;
}

// ─── Core W3C DTCG structures ─────────────────────────────────────────────────

/** A design token: has $value, may have $type, $description, $extensions */
export interface DesignToken {
  $value: TokenValue | TokenReference;
  $type?: DTCGType;
  $description?: string;
  $extensions?: OmniExtensions;
}

/**
 * A token group: any object without $value.
 * Groups organize tokens hierarchically. $type on a group is inherited by children.
 */
export interface TokenGroup {
  $type?: DTCGType;
  $description?: string;
  $extensions?: OmniExtensions;
  [key: string]: DesignToken | TokenGroup | DTCGType | string | OmniExtensions | undefined;
}

// ─── Type guards ──────────────────────────────────────────────────────────────

export function isDesignToken(node: object): node is DesignToken {
  return '$value' in node;
}

export function isTokenGroup(node: object): node is TokenGroup {
  return typeof node === 'object' && node !== null && !('$value' in node);
}

/** Checks if a value is a W3C token reference: "{dot.path}" */
export function isReference(v: unknown): v is TokenReference {
  return typeof v === 'string' && /^\{[^{}]+\}$/.test(v);
}

/** Extracts the dot-path from a reference string: "{color.brand.primary}" → "color.brand.primary" */
export function extractRefPath(ref: TokenReference): string {
  return ref.slice(1, -1);
}
