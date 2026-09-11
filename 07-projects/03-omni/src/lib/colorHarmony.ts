/**
 * Color harmony suggestions using OKLCH hue rotation.
 * Pure math — no AI calls, no side effects.
 */

import { hexToOklch, oklchToHex } from "./colorSpaces";
import { deltaE2000, isValidHex } from "./color";

// ── Types ────────────────────────────────────────────────────────────────

export type HarmonyMode =
  | "freeform"
  | "analogous"
  | "complementary"
  | "triadic"
  | "split-complementary"
  | "monochromatic";

export type HarmonyType =
  | "complementary"
  | "analogous-plus"
  | "analogous-minus"
  | "triadic-plus"
  | "triadic-minus"
  | "split-complementary-plus"
  | "split-complementary-minus";

export interface HarmonySuggestion {
  hex: string;
  harmonyType: HarmonyType;
  label: string;
  description: string;
  hueOffset: number;
}

// ── Harmony definitions ──────────────────────────────────────────────────

const HARMONIES: Record<HarmonyType, { offset: number; label: string; description: string }> = {
  "complementary":             { offset: 180,  label: "Complementary",       description: "Opposite on the color wheel \u2014 maximum contrast" },
  "analogous-plus":            { offset: 30,   label: "Analogous +30\u00b0", description: "Adjacent hue \u2014 visual harmony with subtle variation" },
  "analogous-minus":           { offset: -30,  label: "Analogous -30\u00b0", description: "Adjacent hue \u2014 visual harmony with subtle variation" },
  "triadic-plus":              { offset: 120,  label: "Triadic +120\u00b0",  description: "Evenly spaced triad \u2014 vibrant and balanced" },
  "triadic-minus":             { offset: -120, label: "Triadic -120\u00b0",  description: "Evenly spaced triad \u2014 vibrant and balanced" },
  "split-complementary-plus":  { offset: 150,  label: "Split-comp +150\u00b0", description: "Near-opposite \u2014 high contrast with more nuance" },
  "split-complementary-minus": { offset: -150, label: "Split-comp -150\u00b0", description: "Near-opposite \u2014 high contrast with more nuance" },
};

// ── Core ─────────────────────────────────────────────────────────────────

function rotateHue(hex: string, offset: number): string | null {
  const oklch = hexToOklch(hex);
  if (!oklch) return null;
  const [L, C, H] = oklch;
  const newH = ((H + offset) % 360 + 360) % 360;
  return oklchToHex(L, C, newH);
}

export function computeHarmonies(
  primaryHex: string,
  types: HarmonyType[],
): HarmonySuggestion[] {
  if (!isValidHex(primaryHex)) return [];

  const results: HarmonySuggestion[] = [];
  for (const type of types) {
    const def = HARMONIES[type];
    const hex = rotateHue(primaryHex, def.offset);
    if (!hex || !isValidHex(hex)) continue;

    // Skip if not perceptually distinct enough from the primary
    if (deltaE2000(primaryHex, hex) < 15) continue;

    results.push({
      hex,
      harmonyType: type,
      label: def.label,
      description: def.description,
      hueOffset: def.offset,
    });
  }
  return results;
}

// ── Convenience ──────────────────────────────────────────────────────────

export function suggestSecondary(primaryHex: string): HarmonySuggestion[] {
  return computeHarmonies(primaryHex, [
    "complementary",
    "split-complementary-plus",
    "split-complementary-minus",
  ]);
}

export function suggestAccent(primaryHex: string): HarmonySuggestion[] {
  return computeHarmonies(primaryHex, [
    "triadic-plus",
    "triadic-minus",
    "analogous-plus",
  ]);
}

// ── Harmony Mode Computation ─────────────────────────────────────────────

/**
 * Computes secondary and accent colors based on a harmony mode.
 * Returns null for slots that don't apply (e.g. monochromatic has no accent).
 */
export function computeHarmonyColors(
  primaryHex: string,
  mode: HarmonyMode,
): { secondary: string | null; accent: string | null } {
  if (!isValidHex(primaryHex) || mode === "freeform") {
    return { secondary: null, accent: null };
  }

  const oklch = hexToOklch(primaryHex);
  if (!oklch) return { secondary: null, accent: null };

  const [L, C, H] = oklch;

  switch (mode) {
    case "analogous":
      return {
        secondary: rotateHue(primaryHex, 30),
        accent: rotateHue(primaryHex, -30),
      };
    case "complementary":
      return {
        secondary: rotateHue(primaryHex, 180),
        accent: null,
      };
    case "triadic":
      return {
        secondary: rotateHue(primaryHex, 120),
        accent: rotateHue(primaryHex, -120),
      };
    case "split-complementary":
      return {
        secondary: rotateHue(primaryHex, 150),
        accent: rotateHue(primaryHex, -150),
      };
    case "monochromatic":
      return {
        secondary: oklchToHex(L, Math.max(0, C * 0.5), H),
        accent: oklchToHex(Math.min(1, L + 0.15), Math.max(0, C * 0.3), H),
      };
    default:
      return { secondary: null, accent: null };
  }
}
