// ─── W3C DTCG Migration Utilities ────────────────────────────────────────────
// Converts existing ColorSystem + static token arrays into DTCG-aligned entries.

import type { ColorSystem } from "@/types/colorSystem";
import type { DesignToken, TokenGroup, ShadowValue } from "@/types/tokens";
import {
  TYPOGRAPHY_TOKENS,
  SPACING_TOKENS,
  BORDER_TOKENS,
  EFFECT_TOKENS,
} from "./staticTokens";

// ─── ColorSystem → DTCG entries ───────────────────────────────────────────────

/**
 * Converts a ColorSystem's palettes and semantic tokens into a flat DTCG entry map.
 * Palette steps become "color.{paletteKey}.{step}" tokens (light variant by default).
 * Dark variant steps are embedded as mode overrides.
 * Semantic tokens become "color.{tokenName}" tokens with mode overrides.
 */
export function colorSystemToTokenEntries(cs: ColorSystem): Record<string, DesignToken> {
  const entries: Record<string, DesignToken> = {};

  // ── Primitive palette steps ────────────────────────────────────────────────
  for (const palette of Object.values(cs.palettes)) {
    for (const [stepStr, stepData] of Object.entries(palette.light.steps)) {
      if (!stepData) continue;
      const path = `color.${palette.key}.${stepStr}`;

      // Find the dark variant for this step
      const darkStep = palette.dark.steps[Number(stepStr) as 1|2|3|4|5|6|7|8|9|10|11|12];

      entries[path] = {
        $value: stepData.hex,
        $type: "color",
        $extensions: {
          "omni.paletteKey": palette.key,
          "omni.shade": stepData.step,
          "omni.wcag": {
            contrastOnWhite: stepData.contrastOnWhite,
            contrastOnBlack: stepData.contrastOnBlack,
            aa: stepData.wcagAA,
            aaa: stepData.wcagAAA,
          },
          ...(darkStep ? { "omni.mode": { dark: darkStep.hex } } : {}),
          "omni.readonly": true,
        },
      };
    }
  }

  // ── Semantic tokens ─────────────────────────────────────────────────────────
  for (const token of cs.tokens) {
    const lightPalette = cs.palettes[token.lightValue.paletteKey];
    const darkPalette = cs.palettes[token.darkValue.paletteKey];

    const lightRef = lightPalette
      ? `{color.${token.lightValue.paletteKey}.${token.lightValue.step}}`
      : token.lightValue.paletteKey;
    const darkRef = darkPalette
      ? `{color.${token.darkValue.paletteKey}.${token.darkValue.step}}`
      : token.darkValue.paletteKey;

    entries[token.name] = {
      $value: lightRef,
      $type: "color",
      $description: token.description,
      $extensions: {
        "omni.mode": { dark: darkRef },
        "omni.category": token.category,
      },
    };
  }

  return entries;
}

// ─── Static tokens → DTCG entries ────────────────────────────────────────────

/** Parse a CSS box-shadow shorthand string into a ShadowValue (best-effort) */
function parseShadow(css: string): ShadowValue {
  if (css === "none") {
    return { color: "transparent", offsetX: "0", offsetY: "0", blur: "0", spread: "0" };
  }
  const inset = css.startsWith("inset ");
  const rest = inset ? css.slice(6) : css;
  // Only handle first shadow layer; split on comma but not inside rgb()
  const layer = rest.split(/,(?![^(]*\))/)[0]?.trim() ?? rest;
  const parts = layer.split(/\s+/);
  // parts: [offsetX, offsetY, blur?, spread?, color...]
  // color is typically the last part(s) containing rgb(...)
  const colorStart = parts.findIndex((p) => p.startsWith("rgb") || p.startsWith("#"));
  const dims = colorStart >= 0 ? parts.slice(0, colorStart) : parts.slice(0, -1);
  const color = colorStart >= 0 ? parts.slice(colorStart).join(" ") : parts[parts.length - 1] ?? "#000";
  return {
    color,
    offsetX: dims[0] ?? "0",
    offsetY: dims[1] ?? "0",
    blur: dims[2] ?? "0",
    spread: dims[3] ?? "0",
    inset,
  };
}

/**
 * Converts all static token arrays into DTCG-aligned flat entries.
 * All static tokens are marked as omni.readonly to warn before deletion.
 */
export function staticTokensToEntries(): Record<string, DesignToken> {
  const entries: Record<string, DesignToken> = {};

  // ── Typography ──────────────────────────────────────────────────────────────
  for (const [groupLabel, tokens] of Object.entries(TYPOGRAPHY_TOKENS)) {
    for (const token of tokens) {
      let $type: DesignToken["$type"];
      let $value: DesignToken["$value"];

      if (groupLabel === "Font Family") {
        $type = "font-family";
        $value = token.fullValue;
      } else if (groupLabel === "Font Size") {
        $type = "dimension";
        $value = token.shortValue; // "14px"
      } else if (groupLabel === "Font Weight") {
        $type = "font-weight";
        $value = token.meta ?? Number(token.shortValue);
      } else if (groupLabel === "Line Height") {
        $type = "number";
        $value = token.meta ?? Number(token.shortValue);
      } else if (groupLabel === "Letter Spacing") {
        $type = "dimension";
        $value = token.shortValue; // "-0.05em"
      } else {
        $type = "string";
        $value = token.fullValue;
      }

      entries[token.name] = {
        $value,
        $type,
        $description: token.description,
        $extensions: { "omni.readonly": true },
      };
    }
  }

  // ── Spacing ─────────────────────────────────────────────────────────────────
  for (const token of SPACING_TOKENS) {
    entries[token.name] = {
      $value: token.shortValue, // "16px"
      $type: "dimension",
      $extensions: { "omni.readonly": true },
    };
  }

  // ── Border ──────────────────────────────────────────────────────────────────
  for (const tokens of Object.values(BORDER_TOKENS)) {
    for (const token of tokens) {
      entries[token.name] = {
        $value: token.shortValue, // "4px", "9999px"
        $type: "dimension",
        $extensions: { "omni.readonly": true },
      };
    }
  }

  // ── Effects ─────────────────────────────────────────────────────────────────
  for (const [groupLabel, tokens] of Object.entries(EFFECT_TOKENS)) {
    for (const token of tokens) {
      if (groupLabel === "Shadow") {
        entries[token.name] = {
          $value: token.fullValue === "none"
            ? { color: "transparent", offsetX: "0", offsetY: "0", blur: "0", spread: "0" }
            : parseShadow(token.fullValue.split(", ")[0] ?? token.fullValue),
          $type: "shadow",
          $extensions: { "omni.readonly": true },
        };
      } else if (groupLabel === "Blur") {
        entries[token.name] = {
          $value: token.shortValue === "0" ? "0px" : token.shortValue,
          $type: "dimension",
          $extensions: { "omni.readonly": true },
        };
      } else if (groupLabel === "Opacity") {
        entries[token.name] = {
          $value: token.meta ?? Number(token.fullValue),
          $type: "number",
          $extensions: { "omni.readonly": true },
        };
      }
    }
  }

  return entries;
}

// ─── Tree builder ─────────────────────────────────────────────────────────────

/**
 * Build a W3C DTCG-compliant nested TokenGroup tree from a flat entries map.
 * Used for export and for tree-based UI rendering.
 */
export function buildTree(entries: Record<string, DesignToken>): TokenGroup {
  const root: TokenGroup = {};

  // Sort so shorter paths come first — ensures parent groups exist before children
  const sortedPaths = Object.keys(entries).sort((a, b) => a.localeCompare(b, undefined, { numeric: true }));

  for (const path of sortedPaths) {
    const token = entries[path]!;
    const segments = path.split(".");
    let node: Record<string, unknown> = root;

    for (let i = 0; i < segments.length - 1; i++) {
      const seg = segments[i]!;
      const existing = node[seg];
      // If missing or is already a frozen DesignToken (path conflict), replace with a fresh group
      if (!existing || typeof existing !== "object" || "$value" in (existing as object)) {
        node[seg] = {};
      }
      node = node[seg] as Record<string, unknown>;
    }

    const leaf = segments[segments.length - 1]!;
    // Spread-copy the token so it's a fresh extensible object (immer freezes store objects)
    node[leaf] = { ...token };
  }

  return root as TokenGroup;
}

// ─── W3C DTCG JSON export ─────────────────────────────────────────────────────

/**
 * Serializes the flat entries map to a valid W3C DTCG JSON string.
 * Strips omni.* extensions for clean export, keeping $value/$type/$description.
 */
export function exportDTCGJson(entries: Record<string, DesignToken>): string {
  // Build tree and strip Omni-specific extensions before export
  const cleanEntries: Record<string, DesignToken> = {};
  for (const [path, token] of Object.entries(entries)) {
    cleanEntries[path] = {
      $value: token.$value,
      ...(token.$type && { $type: token.$type }),
      ...(token.$description && { $description: token.$description }),
    };
  }
  return JSON.stringify(buildTree(cleanEntries), null, 2);
}

// ─── DTCG JSON import ─────────────────────────────────────────────────────────

/**
 * Parses a W3C DTCG JSON object into a flat entries map.
 * Groups (objects without $value) are traversed recursively.
 * The prefix is the accumulated dot-path from the root.
 */
export function parseDTCGTree(
  node: Record<string, unknown>,
  prefix = "",
  inheritedType?: DesignToken["$type"],
): Record<string, DesignToken> {
  const entries: Record<string, DesignToken> = {};
  const groupType = (node["$type"] as DesignToken["$type"]) ?? inheritedType;

  for (const [key, value] of Object.entries(node)) {
    if (key.startsWith("$")) continue; // skip reserved keys at group level
    const path = prefix ? `${prefix}.${key}` : key;

    if (typeof value === "object" && value !== null) {
      if ("$value" in value) {
        // It's a token
        const tokenNode = value as Record<string, unknown>;
        const token: DesignToken = {
          $value: tokenNode["$value"] as DesignToken["$value"],
        };
        const tokenType = (tokenNode["$type"] as DesignToken["$type"]) ?? groupType;
        if (tokenType) token.$type = tokenType;
        if (tokenNode["$description"]) token.$description = String(tokenNode["$description"]);
        entries[path] = token;
      } else {
        // It's a group — recurse
        Object.assign(
          entries,
          parseDTCGTree(value as Record<string, unknown>, path, groupType),
        );
      }
    }
  }

  return entries;
}

// ─── Count helpers ────────────────────────────────────────────────────────────

/** Count how many token entries fall under a given path prefix */
export function countUnderPrefix(entries: Record<string, DesignToken>, prefix: string): number {
  return Object.keys(entries).filter(
    (k) => k === prefix || k.startsWith(prefix + "."),
  ).length;
}

/** Get all immediate child keys of a path prefix in the flat entries */
export function getChildKeys(entries: Record<string, DesignToken>, prefix: string): string[] {
  const seen = new Set<string>();
  const offset = prefix ? prefix.length + 1 : 0;
  for (const key of Object.keys(entries)) {
    if (!prefix || key.startsWith(prefix + ".") || key === prefix) {
      const rest = key.slice(offset);
      const child = rest.split(".")[0];
      if (child) seen.add(child);
    }
  }
  return [...seen].sort();
}

/** Check if a path is a token (has a direct entry) or a group (has children but no direct entry) */
export function pathIsToken(entries: Record<string, DesignToken>, path: string): boolean {
  return path in entries;
}

export function pathIsGroup(entries: Record<string, DesignToken>, path: string): boolean {
  return Object.keys(entries).some((k) => k.startsWith(path + "."));
}
