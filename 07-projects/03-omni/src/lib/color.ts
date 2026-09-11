/**
 * Color utility library for Omni.
 * WCAG contrast ratio calculation and hex/RGB conversion.
 */

// ── Hex parsing ────────────────────────────────────────────────────────────

export function hexToRgb(hex: string): [number, number, number] | null {
  const clean = hex.replace(/^#/, "");
  const full =
    clean.length === 3
      ? clean
          .split("")
          .map((c) => c + c)
          .join("")
      : clean;

  if (full.length !== 6) return null;

  const r = parseInt(full.slice(0, 2), 16);
  const g = parseInt(full.slice(2, 4), 16);
  const b = parseInt(full.slice(4, 6), 16);

  return [r, g, b];
}

export function rgbToHex(r: number, g: number, b: number): string {
  return (
    "#" +
    [r, g, b]
      .map((v) => Math.round(Math.max(0, Math.min(255, v))).toString(16).padStart(2, "0"))
      .join("")
  );
}

// ── WCAG contrast ──────────────────────────────────────────────────────────

/**
 * Relative luminance of a linearized RGB channel value.
 * Per WCAG 2.1 specification.
 */
function linearize(channel: number): number {
  const c = channel / 255;
  return c <= 0.04045 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
}

/**
 * Relative luminance of a hex color (0–1).
 */
export function relativeLuminance(hex: string): number {
  const rgb = hexToRgb(hex);
  if (!rgb) return 0;
  const [r, g, b] = rgb.map(linearize);
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}

/**
 * WCAG 2.1 contrast ratio between two hex colors.
 */
export function contrastRatio(hex1: string, hex2: string): number {
  const l1 = relativeLuminance(hex1);
  const l2 = relativeLuminance(hex2);
  const lighter = Math.max(l1, l2);
  const darker = Math.min(l1, l2);
  return (lighter + 0.05) / (darker + 0.05);
}

/**
 * Returns contrast ratios for a color against white and black.
 * Used to compute WCAG AA/AAA badges on color swatches.
 */
export function enrichColorSystem(hex: string): {
  onWhite: number;
  onBlack: number;
} {
  return {
    onWhite: parseFloat(contrastRatio(hex, "#ffffff").toFixed(2)),
    onBlack: parseFloat(contrastRatio(hex, "#000000").toFixed(2)),
  };
}

/**
 * Returns the best foreground color (black or white) for a given background.
 */
export function bestForeground(backgroundHex: string): "#ffffff" | "#000000" {
  const onWhite = contrastRatio(backgroundHex, "#ffffff");
  const onBlack = contrastRatio(backgroundHex, "#000000");
  return onBlack > onWhite ? "#000000" : "#ffffff";
}

// ── HSL helpers ────────────────────────────────────────────────────────────

export function hexToHsl(hex: string): [number, number, number] | null {
  const rgb = hexToRgb(hex);
  if (!rgb) return null;

  const r = rgb[0] / 255;
  const g = rgb[1] / 255;
  const b = rgb[2] / 255;

  const max = Math.max(r, g, b);
  const min = Math.min(r, g, b);
  const l = (max + min) / 2;
  let h = 0;
  let s = 0;

  if (max !== min) {
    const d = max - min;
    s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
    switch (max) {
      case r:
        h = ((g - b) / d + (g < b ? 6 : 0)) / 6;
        break;
      case g:
        h = ((b - r) / d + 2) / 6;
        break;
      case b:
        h = ((r - g) / d + 4) / 6;
        break;
    }
  }

  return [Math.round(h * 360), Math.round(s * 100), Math.round(l * 100)];
}

export function hslToHex(h: number, s: number, l: number): string {
  const sNorm = s / 100;
  const lNorm = l / 100;

  const c = (1 - Math.abs(2 * lNorm - 1)) * sNorm;
  const x = c * (1 - Math.abs(((h / 60) % 2) - 1));
  const m = lNorm - c / 2;

  let r = 0, g = 0, b = 0;
  if (h < 60) { r = c; g = x; b = 0; }
  else if (h < 120) { r = x; g = c; b = 0; }
  else if (h < 180) { r = 0; g = c; b = x; }
  else if (h < 240) { r = 0; g = x; b = c; }
  else if (h < 300) { r = x; g = 0; b = c; }
  else { r = c; g = 0; b = x; }

  return rgbToHex(
    Math.round((r + m) * 255),
    Math.round((g + m) * 255),
    Math.round((b + m) * 255)
  );
}

// ── Alpha derivation ──────────────────────────────────────────────────────

/**
 * Derives an rgba() string that, when composited on `background`, produces
 * `opaque`. This is how Radix Colors computes its alpha scale variants.
 */
export function deriveAlphaVariant(
  opaqueHex: string,
  backgroundHex: string
): string {
  const fg = hexToRgb(opaqueHex);
  const bg = hexToRgb(backgroundHex);
  if (!fg || !bg) return opaqueHex;

  // Find the optimal alpha — use the channel with the largest difference
  let bestAlpha = 1;
  for (let i = 0; i < 3; i++) {
    const diff = fg[i] - bg[i];
    if (Math.abs(diff) > 0.5) {
      // source channel = (result - bg * (1-a)) / a → rearranged from compositing formula
      // For the alpha that makes a pure-ish source: a = (result - bg) / (source - bg)
      // But we want to find source and alpha simultaneously.
      // Simpler: try alpha = |diff| / 255, then compute source
      const a = Math.abs(diff) / 255;
      if (a > 0 && a < bestAlpha) bestAlpha = a;
    }
  }

  // Binary search for the best alpha that minimizes RGB error
  let lo = 0.01, hi = 1;
  for (let iter = 0; iter < 20; iter++) {
    const mid = (lo + hi) / 2;
    // For each channel, compute what source RGB would be needed
    const sr = (fg[0] - bg[0] * (1 - mid)) / mid;
    const sg = (fg[1] - bg[1] * (1 - mid)) / mid;
    const sb = (fg[2] - bg[2] * (1 - mid)) / mid;
    if (sr >= 0 && sr <= 255 && sg >= 0 && sg <= 255 && sb >= 0 && sb <= 255) {
      hi = mid;
    } else {
      lo = mid;
    }
  }

  const alpha = Math.round(hi * 1000) / 1000;
  const sr = Math.round(Math.max(0, Math.min(255, (fg[0] - bg[0] * (1 - alpha)) / alpha)));
  const sg = Math.round(Math.max(0, Math.min(255, (fg[1] - bg[1] * (1 - alpha)) / alpha)));
  const sb = Math.round(Math.max(0, Math.min(255, (fg[2] - bg[2] * (1 - alpha)) / alpha)));

  return `rgba(${sr}, ${sg}, ${sb}, ${alpha})`;
}

// ── Color Vision Deficiency Simulation ────────────────────────────────────

/**
 * Simulates color vision deficiency using the Brettel/Viénot method.
 * Returns a hex string approximating how the color appears under CVD.
 */
export function simulateCVD(
  hex: string,
  type: "deutan" | "protan" | "tritan"
): string {
  const rgb = hexToRgb(hex);
  if (!rgb) return hex;

  // Linearize
  const lin = rgb.map((c) => {
    const v = c / 255;
    return v <= 0.04045 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4);
  });

  // Viénot simulation matrices (severity = 1.0 = full dichromacy)
  const matrices: Record<string, number[][]> = {
    deutan: [
      [0.367322, 0.860646, -0.227968],
      [0.280085, 0.672501, 0.047413],
      [-0.011820, 0.042940, 0.968881],
    ],
    protan: [
      [0.152286, 1.052583, -0.204868],
      [0.114503, 0.786281, 0.099216],
      [-0.003882, -0.048116, 1.051998],
    ],
    tritan: [
      [1.255528, -0.076749, -0.178779],
      [-0.078411, 0.930809, 0.147602],
      [0.004733, 0.691367, 0.303900],
    ],
  };

  const m = matrices[type];
  const r = m[0][0] * lin[0] + m[0][1] * lin[1] + m[0][2] * lin[2];
  const g = m[1][0] * lin[0] + m[1][1] * lin[1] + m[1][2] * lin[2];
  const b = m[2][0] * lin[0] + m[2][1] * lin[1] + m[2][2] * lin[2];

  // De-linearize
  const delinearize = (v: number) => {
    const clamped = Math.max(0, Math.min(1, v));
    return clamped <= 0.0031308
      ? clamped * 12.92
      : 1.055 * Math.pow(clamped, 1 / 2.4) - 0.055;
  };

  return rgbToHex(
    Math.round(delinearize(r) * 255),
    Math.round(delinearize(g) * 255),
    Math.round(delinearize(b) * 255)
  );
}

// ── Perceptual Color Difference (CIE ΔE2000) ─────────────────────────────

/**
 * Computes CIE ΔE2000 between two hex colors.
 * Values ≥ 15 indicate easily distinguishable colors.
 */
export function deltaE2000(hex1: string, hex2: string): number {
  const lab1 = hexToLabInternal(hex1);
  const lab2 = hexToLabInternal(hex2);
  if (!lab1 || !lab2) return 0;

  const [L1, a1, b1] = lab1;
  const [L2, a2, b2] = lab2;

  const kL = 1, kC = 1, kH = 1;
  const C1 = Math.sqrt(a1 * a1 + b1 * b1);
  const C2 = Math.sqrt(a2 * a2 + b2 * b2);
  const Cab = (C1 + C2) / 2;
  const Cab7 = Math.pow(Cab, 7);
  const G = 0.5 * (1 - Math.sqrt(Cab7 / (Cab7 + Math.pow(25, 7))));
  const ap1 = a1 * (1 + G);
  const ap2 = a2 * (1 + G);
  const Cp1 = Math.sqrt(ap1 * ap1 + b1 * b1);
  const Cp2 = Math.sqrt(ap2 * ap2 + b2 * b2);
  const hp1 = Math.atan2(b1, ap1) * (180 / Math.PI);
  const hp2 = Math.atan2(b2, ap2) * (180 / Math.PI);
  const h1 = hp1 >= 0 ? hp1 : hp1 + 360;
  const h2 = hp2 >= 0 ? hp2 : hp2 + 360;

  const dLp = L2 - L1;
  const dCp = Cp2 - Cp1;
  let dhp = 0;
  if (Cp1 * Cp2 !== 0) {
    const diff = h2 - h1;
    if (Math.abs(diff) <= 180) dhp = diff;
    else if (diff > 180) dhp = diff - 360;
    else dhp = diff + 360;
  }
  const dHp = 2 * Math.sqrt(Cp1 * Cp2) * Math.sin((dhp * Math.PI) / 360);

  const Lp = (L1 + L2) / 2;
  const Cp = (Cp1 + Cp2) / 2;
  let hp = 0;
  if (Cp1 * Cp2 !== 0) {
    if (Math.abs(h1 - h2) <= 180) hp = (h1 + h2) / 2;
    else if (h1 + h2 < 360) hp = (h1 + h2 + 360) / 2;
    else hp = (h1 + h2 - 360) / 2;
  }

  const T =
    1 -
    0.17 * Math.cos(((hp - 30) * Math.PI) / 180) +
    0.24 * Math.cos(((2 * hp) * Math.PI) / 180) +
    0.32 * Math.cos(((3 * hp + 6) * Math.PI) / 180) -
    0.20 * Math.cos(((4 * hp - 63) * Math.PI) / 180);

  const SL = 1 + (0.015 * (Lp - 50) ** 2) / Math.sqrt(20 + (Lp - 50) ** 2);
  const SC = 1 + 0.045 * Cp;
  const SH = 1 + 0.015 * Cp * T;

  const Cp7 = Math.pow(Cp, 7);
  const RT =
    -2 *
    Math.sqrt(Cp7 / (Cp7 + Math.pow(25, 7))) *
    Math.sin(((60 * Math.exp(-(((hp - 275) / 25) ** 2))) * Math.PI) / 180);

  return Math.sqrt(
    (dLp / (kL * SL)) ** 2 +
    (dCp / (kC * SC)) ** 2 +
    (dHp / (kH * SH)) ** 2 +
    RT * (dCp / (kC * SC)) * (dHp / (kH * SH))
  );
}

/** Internal: hex → CIE Lab for deltaE2000 */
function hexToLabInternal(hex: string): [number, number, number] | null {
  const rgb = hexToRgb(hex);
  if (!rgb) return null;

  // sRGB → linear RGB → XYZ D65
  const lin = rgb.map((c) => {
    const v = c / 255;
    return v <= 0.04045 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4);
  });

  const x = (0.4124564 * lin[0] + 0.3575761 * lin[1] + 0.1804375 * lin[2]) / 0.95047;
  const y = (0.2126729 * lin[0] + 0.7151522 * lin[1] + 0.0721750 * lin[2]) / 1.00000;
  const z = (0.0193339 * lin[0] + 0.1191920 * lin[1] + 0.9503041 * lin[2]) / 1.08883;

  const f = (t: number) =>
    t > 0.008856 ? Math.cbrt(t) : 7.787 * t + 16 / 116;

  const L = 116 * f(y) - 16;
  const a = 500 * (f(x) - f(y));
  const b = 200 * (f(y) - f(z));

  return [L, a, b];
}

// ── Validation ─────────────────────────────────────────────────────────────

export function isValidHex(hex: string): boolean {
  return /^#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$/.test(hex);
}

// ── Radix-Style Scale Generation ──────────────────────────────────────────

import { hexToOklch, oklchToHex } from "./colorSpaces";
import type { ColorScaleVariant, ColorShadeData, ColorPalette, RadixStep, DataVizColor } from "@/types/colorSystem";
import { RADIX_STEPS } from "@/types/colorSystem";

// Target OKLCH lightness for each step, by mode.
// These approximate Radix Colors' perceptual lightness ramps.
const DARK_L: Record<number, number> = {
  1: 0.14, 2: 0.17, 3: 0.20, 4: 0.23, 5: 0.26,
  6: 0.31, 7: 0.37, 8: 0.45, 9: 0, 10: 0, // seed-derived
  11: 0.75, 12: 0.90,
};
const LIGHT_L: Record<number, number> = {
  1: 0.99, 2: 0.97, 3: 0.94, 4: 0.91, 5: 0.88,
  6: 0.83, 7: 0.77, 8: 0.68, 9: 0, 10: 0,
  11: 0.40, 12: 0.25,
};

// Chroma multiplier relative to the seed (step 9). Tapers at extremes.
const CHROMA_MULT: Record<number, number> = {
  1: 0.04, 2: 0.07, 3: 0.12, 4: 0.16, 5: 0.20,
  6: 0.28, 7: 0.40, 8: 0.60, 9: 1.0, 10: 0.90,
  11: 0.45, 12: 0.15,
};

/**
 * Generates a 12-step Radix-style ColorScaleVariant from a seed hex.
 * The seed maps to step 9 (solid color). OKLCH is used for perceptual uniformity.
 */
export function generateRadixScale(
  seedHex: string,
  mode: "light" | "dark",
): ColorScaleVariant {
  const oklch = hexToOklch(seedHex);
  const seedL = oklch ? oklch[0] : 0.55;
  const seedC = oklch ? oklch[1] : 0.18;
  const seedH = oklch ? oklch[2] : 280;

  const targets = mode === "dark" ? DARK_L : LIGHT_L;

  const steps: Partial<Record<RadixStep, ColorShadeData>> = {};

  for (const step of RADIX_STEPS) {
    let L: number;
    if (step === 9) {
      L = seedL;
    } else if (step === 10) {
      L = mode === "dark"
        ? Math.min(seedL + 0.06, 0.75)
        : Math.max(seedL - 0.06, 0.20);
    } else {
      L = targets[step];
    }

    const C = seedC * CHROMA_MULT[step];
    const hex = oklchToHex(L, C, seedH);
    const contrasts = enrichColorSystem(hex);

    steps[step] = {
      step,
      hex,
      hsl: hex,
      contrastOnWhite: contrasts.onWhite,
      contrastOnBlack: contrasts.onBlack,
      wcagAA: contrasts.onWhite >= 4.5 || contrasts.onBlack >= 4.5,
      wcagAAA: contrasts.onWhite >= 7 || contrasts.onBlack >= 7,
    };
  }

  return { steps };
}

/**
 * Builds a full ColorPalette from a DataVizColor, generating 12-step scales
 * for light, dark, and their alpha variants.
 */
export function generateDataVizPalette(dvColor: DataVizColor): ColorPalette {
  const light = generateRadixScale(dvColor.hex, "light");
  const dark = generateRadixScale(dvColor.hex, "dark");

  const buildAlpha = (
    opaque: ColorScaleVariant,
    bg: string,
  ): ColorScaleVariant => {
    const alphaSteps: Partial<Record<RadixStep, ColorShadeData>> = {};
    for (const step of RADIX_STEPS) {
      const opaqueStep = opaque.steps[step];
      if (!opaqueStep) continue;
      const alphaStr = deriveAlphaVariant(opaqueStep.hex, bg);
      alphaSteps[step] = {
        step,
        hex: alphaStr,
        hsl: alphaStr,
        contrastOnWhite: 0,
        contrastOnBlack: 0,
        wcagAA: false,
        wcagAAA: false,
      };
    }
    return { steps: alphaSteps };
  };

  return {
    key: `dataviz-${dvColor.index}`,
    label: dvColor.label || `Series ${dvColor.index}`,
    role: "brand-primary",
    seedHex: dvColor.hex,
    light,
    dark,
    lightA: buildAlpha(light, "#ffffff"),
    darkA: buildAlpha(dark, "#111113"),
  };
}
