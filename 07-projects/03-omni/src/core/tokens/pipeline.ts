// ─── Multi-Format Token Pipeline ─────────────────────────────────────────────
// Exports a flat record of DesignTokens into various platform-native formats.
// Handles reference resolution, mode overrides, and tier filtering.

import type { DesignToken, TokenValue, TokenReference } from "@/types/tokens";
import { isReference, extractRefPath } from "@/types/tokens";
import type { TokenTier } from "./tiers";
import { classifyTier } from "./tiers";

// ─── Public types ────────────────────────────────────────────────────────────

/** Supported output formats for the token pipeline. */
export type TokenOutputFormat =
  | "css-vars"
  | "tailwind-theme"
  | "scss"
  | "json-dtcg"
  | "swift"
  | "kotlin"
  | "flutter-dart";

/** Options passed to `TokenPipeline.export()`. */
export interface TokenPipelineOptions {
  /** Target output format. */
  format: TokenOutputFormat;
  /** Optional prefix for generated names (e.g. `"--omni"` for CSS vars). */
  prefix?: string;
  /** When `true`, emit token `$description` as comments. */
  includeDescriptions?: boolean;
  /** Only include tokens belonging to these tiers (default: all). */
  tiers?: TokenTier[];
  /** Resolve mode-specific values instead of default `$value`. */
  mode?: string;
}

/** The result of a single export run. */
export interface PipelineResult {
  /** The format that was used. */
  format: TokenOutputFormat;
  /** The generated file content. */
  content: string;
  /** A suggested filename for the output. */
  filename: string;
}

// ─── Helpers ─────────────────────────────────────────────────────────────────

/** Convert a dot-path to a CSS-custom-property-style kebab name. */
function toKebab(path: string): string {
  return path.replace(/\./g, "-");
}

/** Convert a dot-path to a camelCase identifier. */
function toCamel(path: string): string {
  const parts = path.split(".");
  return parts
    .map((p, i) => (i === 0 ? p : p.charAt(0).toUpperCase() + p.slice(1)))
    .join("");
}

/** Convert a dot-path to PascalCase. */
function toPascal(path: string): string {
  return path
    .split(".")
    .map((p) => p.charAt(0).toUpperCase() + p.slice(1))
    .join("");
}

/** Convert a dot-path to snake_case. */
export function toSnake(path: string): string {
  return path.replace(/\./g, "_");
}

/** Stringify a resolved value for use in generated code. */
function stringifyValue(val: TokenValue): string {
  if (typeof val === "string") return val;
  if (typeof val === "number") return String(val);
  if (typeof val === "boolean") return String(val);

  // Shadow value(s)
  if (Array.isArray(val)) {
    return val
      .map(
        (s) =>
          `${s.inset ? "inset " : ""}${s.offsetX} ${s.offsetY} ${s.blur} ${s.spread} ${s.color}`,
      )
      .join(", ");
  }

  // Single shadow
  if (typeof val === "object" && val !== null && "offsetX" in val) {
    const s = val;
    return `${s.inset ? "inset " : ""}${s.offsetX} ${s.offsetY} ${s.blur} ${s.spread} ${s.color}`;
  }

  return String(val);
}

// ─── Pipeline ────────────────────────────────────────────────────────────────

/**
 * `TokenPipeline` takes a flat record of `DesignToken` entries (keyed by
 * dot-path) and exports them into one of several platform formats.
 *
 * @example
 * ```ts
 * const pipeline = new TokenPipeline(myTokens);
 * const result = pipeline.export({ format: "css-vars", prefix: "--omni" });
 * console.log(result.content);
 * ```
 */
export class TokenPipeline {
  private entries: Record<string, DesignToken>;

  constructor(entries: Record<string, DesignToken>) {
    this.entries = entries;
  }

  // ── Public API ───────────────────────────────────────────────────────────

  /** Export tokens in the requested format. */
  export(options: TokenPipelineOptions): PipelineResult {
    const filtered = this.filterByTiers(options.tiers);
    const resolved = this.resolveAll(filtered, options.mode);

    switch (options.format) {
      case "css-vars":
        return this.toCSSVars(resolved, options);
      case "tailwind-theme":
        return this.toTailwindTheme(resolved, options);
      case "scss":
        return this.toSCSS(resolved, options);
      case "json-dtcg":
        return this.toJSONDTCG(filtered, options);
      case "swift":
        return this.toSwift(resolved, options);
      case "kotlin":
        return this.toKotlin(resolved, options);
      case "flutter-dart":
        return this.toFlutterDart(resolved, options);
    }
  }

  // ── Filtering & resolution ───────────────────────────────────────────────

  /**
   * Return only those entries whose tier is in the allowed set.
   * If `tiers` is undefined, all entries are returned.
   */
  private filterByTiers(
    tiers?: TokenTier[],
  ): Record<string, DesignToken> {
    if (!tiers || tiers.length === 0) return { ...this.entries };

    const result: Record<string, DesignToken> = {};
    for (const [path, token] of Object.entries(this.entries)) {
      if (tiers.includes(classifyTier(path, token))) {
        result[path] = token;
      }
    }
    return result;
  }

  /**
   * Resolve all references in the given entries to concrete values.
   * Returns a map of `path -> resolved TokenValue`.
   *
   * If `mode` is provided and the token has a matching `omni.mode` override
   * that value (or its resolved reference) is used instead of `$value`.
   */
  private resolveAll(
    entries: Record<string, DesignToken>,
    mode?: string,
  ): Map<string, { value: TokenValue; token: DesignToken }> {
    const resolved = new Map<string, { value: TokenValue; token: DesignToken }>();

    const resolve = (
      val: TokenValue | TokenReference,
      visited: Set<string>,
    ): TokenValue => {
      if (!isReference(val)) return val as TokenValue;

      const refPath = extractRefPath(val as TokenReference);
      if (visited.has(refPath)) return val as TokenValue; // circular — bail
      visited.add(refPath);

      const refToken = this.entries[refPath];
      if (!refToken) return val as TokenValue; // unresolved reference

      const refRaw =
        mode && refToken.$extensions?.["omni.mode"]?.[mode] !== undefined
          ? refToken.$extensions["omni.mode"][mode]
          : refToken.$value;

      return resolve(refRaw, visited);
    };

    for (const [path, token] of Object.entries(entries)) {
      const raw =
        mode && token.$extensions?.["omni.mode"]?.[mode] !== undefined
          ? token.$extensions["omni.mode"][mode]
          : token.$value;

      resolved.set(path, {
        value: resolve(raw, new Set([path])),
        token,
      });
    }

    return resolved;
  }

  // ── Format: CSS Custom Properties ────────────────────────────────────────

  private toCSSVars(
    resolved: Map<string, { value: TokenValue; token: DesignToken }>,
    options: TokenPipelineOptions,
  ): PipelineResult {
    const prefix = options.prefix ?? "--";
    const lines: string[] = [":root {"];

    for (const [path, { value, token }] of resolved) {
      if (options.includeDescriptions && token.$description) {
        lines.push(`  /* ${token.$description} */`);
      }
      const name = `${prefix}-${toKebab(path)}`;
      lines.push(`  ${name}: ${stringifyValue(value)};`);
    }

    lines.push("}");

    return {
      format: "css-vars",
      content: lines.join("\n"),
      filename: "tokens.css",
    };
  }

  // ── Format: Tailwind v4 @theme ───────────────────────────────────────────

  private toTailwindTheme(
    resolved: Map<string, { value: TokenValue; token: DesignToken }>,
    options: TokenPipelineOptions,
  ): PipelineResult {
    const prefix = options.prefix ?? "--";
    const lines: string[] = ["@theme {"];

    for (const [path, { value, token }] of resolved) {
      if (options.includeDescriptions && token.$description) {
        lines.push(`  /* ${token.$description} */`);
      }
      const name = `${prefix}-${toKebab(path)}`;
      lines.push(`  ${name}: ${stringifyValue(value)};`);
    }

    lines.push("}");

    return {
      format: "tailwind-theme",
      content: lines.join("\n"),
      filename: "tokens.theme.css",
    };
  }

  // ── Format: SCSS variables ───────────────────────────────────────────────

  private toSCSS(
    resolved: Map<string, { value: TokenValue; token: DesignToken }>,
    options: TokenPipelineOptions,
  ): PipelineResult {
    const prefix = options.prefix ? `${options.prefix}-` : "";
    const lines: string[] = [
      "// ─── Generated Design Tokens ─────────────────────────────────────────────",
      "// Do not edit manually — regenerate via the Omni token pipeline.",
      "",
    ];

    for (const [path, { value, token }] of resolved) {
      if (options.includeDescriptions && token.$description) {
        lines.push(`// ${token.$description}`);
      }
      const name = `$${prefix}${toKebab(path)}`;
      lines.push(`${name}: ${stringifyValue(value)};`);
    }

    return {
      format: "scss",
      content: lines.join("\n"),
      filename: "_tokens.scss",
    };
  }

  // ── Format: W3C DTCG JSON ────────────────────────────────────────────────

  private toJSONDTCG(
    entries: Record<string, DesignToken>,
    options: TokenPipelineOptions,
  ): PipelineResult {
    // Build nested JSON structure from dot-paths
    const root: Record<string, unknown> = {};

    for (const [path, token] of Object.entries(entries)) {
      const parts = path.split(".");
      let cursor: Record<string, unknown> = root;

      for (let i = 0; i < parts.length - 1; i++) {
        if (!(parts[i] in cursor) || typeof cursor[parts[i]] !== "object") {
          cursor[parts[i]] = {};
        }
        cursor = cursor[parts[i]] as Record<string, unknown>;
      }

      const leaf: Record<string, unknown> = {
        $value: token.$value,
      };
      if (token.$type) leaf.$type = token.$type;
      if (options.includeDescriptions && token.$description) {
        leaf.$description = token.$description;
      }
      if (token.$extensions) leaf.$extensions = token.$extensions;

      cursor[parts[parts.length - 1]] = leaf;
    }

    return {
      format: "json-dtcg",
      content: JSON.stringify(root, null, 2),
      filename: "tokens.json",
    };
  }

  // ── Format: Swift ────────────────────────────────────────────────────────

  private toSwift(
    resolved: Map<string, { value: TokenValue; token: DesignToken }>,
    options: TokenPipelineOptions,
  ): PipelineResult {
    const lines: string[] = [
      "// ─── Generated Design Tokens ───────────────────────────────────────────",
      "// Do not edit manually — regenerate via the Omni token pipeline.",
      "",
      "import SwiftUI",
      "",
      "enum OmniTokens {",
    ];

    for (const [path, { value, token }] of resolved) {
      if (options.includeDescriptions && token.$description) {
        lines.push(`    /// ${token.$description}`);
      }

      const name = toCamel(path);
      const strVal = stringifyValue(value);

      if (token.$type === "color") {
        // Attempt hex parsing for Color literal
        const hex = parseHexColor(strVal);
        if (hex) {
          lines.push(
            `    static let ${name} = Color(red: ${hex.r}, green: ${hex.g}, blue: ${hex.b}, opacity: ${hex.a})`,
          );
        } else {
          lines.push(`    // "${path}" — non-hex color: ${strVal}`);
        }
      } else if (
        token.$type === "dimension" ||
        token.$type === "number"
      ) {
        const num = parseFloat(strVal);
        lines.push(
          `    static let ${name}: CGFloat = ${isNaN(num) ? `/* ${strVal} */ 0` : num}`,
        );
      } else if (token.$type === "font-family") {
        lines.push(`    static let ${name} = "${strVal}"`);
      } else {
        lines.push(`    static let ${name} = "${strVal}"`);
      }
    }

    lines.push("}");

    return {
      format: "swift",
      content: lines.join("\n"),
      filename: "OmniTokens.swift",
    };
  }

  // ── Format: Kotlin ───────────────────────────────────────────────────────

  private toKotlin(
    resolved: Map<string, { value: TokenValue; token: DesignToken }>,
    options: TokenPipelineOptions,
  ): PipelineResult {
    const lines: string[] = [
      "// ─── Generated Design Tokens ───────────────────────────────────────────",
      "// Do not edit manually — regenerate via the Omni token pipeline.",
      "",
      "package com.omni.tokens",
      "",
      "import androidx.compose.ui.graphics.Color",
      "import androidx.compose.ui.unit.dp",
      "import androidx.compose.ui.unit.sp",
      "",
      "object OmniTokens {",
    ];

    for (const [path, { value, token }] of resolved) {
      if (options.includeDescriptions && token.$description) {
        lines.push(`    /** ${token.$description} */`);
      }

      const name = toPascal(path);
      const strVal = stringifyValue(value);

      if (token.$type === "color") {
        const hex = strVal.replace("#", "").toUpperCase();
        const padded = hex.length === 6 ? `FF${hex}` : hex;
        lines.push(`    val ${name} = Color(0x${padded})`);
      } else if (token.$type === "dimension") {
        const num = parseFloat(strVal);
        if (!isNaN(num)) {
          const unit = strVal.includes("rem") || strVal.includes("em") ? "sp" : "dp";
          lines.push(`    val ${name} = ${num}.${unit}`);
        } else {
          lines.push(`    // "${path}" — unparseable dimension: ${strVal}`);
        }
      } else if (token.$type === "number") {
        lines.push(`    val ${name} = ${strVal}`);
      } else {
        lines.push(`    val ${name} = "${strVal}"`);
      }
    }

    lines.push("}");

    return {
      format: "kotlin",
      content: lines.join("\n"),
      filename: "OmniTokens.kt",
    };
  }

  // ── Format: Flutter / Dart ───────────────────────────────────────────────

  private toFlutterDart(
    resolved: Map<string, { value: TokenValue; token: DesignToken }>,
    options: TokenPipelineOptions,
  ): PipelineResult {
    const lines: string[] = [
      "// ─── Generated Design Tokens ───────────────────────────────────────────",
      "// Do not edit manually — regenerate via the Omni token pipeline.",
      "",
      "import 'package:flutter/material.dart';",
      "",
      "class OmniTokens {",
      "  OmniTokens._(); // prevent instantiation",
      "",
    ];

    for (const [path, { value, token }] of resolved) {
      if (options.includeDescriptions && token.$description) {
        lines.push(`  /// ${token.$description}`);
      }

      const name = toCamel(path);
      const strVal = stringifyValue(value);

      if (token.$type === "color") {
        const hex = strVal.replace("#", "").toUpperCase();
        const padded = hex.length === 6 ? `FF${hex}` : hex;
        lines.push(
          `  static const ${name} = Color(0x${padded});`,
        );
      } else if (token.$type === "dimension" || token.$type === "number") {
        const num = parseFloat(strVal);
        lines.push(
          `  static const ${name} = ${isNaN(num) ? `/* ${strVal} */ 0.0` : `${num}`};`,
        );
      } else if (token.$type === "font-family") {
        lines.push(`  static const ${name} = '${strVal}';`);
      } else {
        lines.push(`  static const ${name} = '${strVal}';`);
      }
    }

    lines.push("}");

    return {
      format: "flutter-dart",
      content: lines.join("\n"),
      filename: "omni_tokens.dart",
    };
  }
}

// ─── Internal colour parsing ─────────────────────────────────────────────────

interface ParsedColor {
  r: number;
  g: number;
  b: number;
  a: number;
}

/**
 * Parse a hex colour string (#RGB, #RRGGBB, #RRGGBBAA) into normalised
 * 0-1 channel values suitable for Swift `Color()` literals.
 */
function parseHexColor(hex: string): ParsedColor | null {
  const raw = hex.replace("#", "");
  let r: number, g: number, b: number, a: number;

  if (raw.length === 3) {
    r = parseInt(raw[0] + raw[0], 16) / 255;
    g = parseInt(raw[1] + raw[1], 16) / 255;
    b = parseInt(raw[2] + raw[2], 16) / 255;
    a = 1;
  } else if (raw.length === 6) {
    r = parseInt(raw.slice(0, 2), 16) / 255;
    g = parseInt(raw.slice(2, 4), 16) / 255;
    b = parseInt(raw.slice(4, 6), 16) / 255;
    a = 1;
  } else if (raw.length === 8) {
    r = parseInt(raw.slice(0, 2), 16) / 255;
    g = parseInt(raw.slice(2, 4), 16) / 255;
    b = parseInt(raw.slice(4, 6), 16) / 255;
    a = parseInt(raw.slice(6, 8), 16) / 255;
  } else {
    return null;
  }

  if ([r, g, b, a].some(isNaN)) return null;

  return {
    r: Math.round(r * 1000) / 1000,
    g: Math.round(g * 1000) / 1000,
    b: Math.round(b * 1000) / 1000,
    a: Math.round(a * 1000) / 1000,
  };
}
