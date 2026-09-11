/**
 * Color space conversion utilities for Omni.
 * Pure math — sRGB hex ↔ OKLCH, OKLab, CIE Lab, CIE LCH, Display P3, HSL.
 */

import { hexToRgb, rgbToHex, hexToHsl } from "./color";
import type { CodeFormat } from "@/types/colorSystem";

// ── Linear sRGB helpers ───────────────────────────────────────────────────

function srgbToLinear(c: number): number {
  return c <= 0.04045 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
}

function linearToSrgb(c: number): number {
  const clamped = Math.max(0, Math.min(1, c));
  return clamped <= 0.0031308
    ? clamped * 12.92
    : 1.055 * Math.pow(clamped, 1 / 2.4) - 0.055;
}

function hexToLinearRgb(hex: string): [number, number, number] | null {
  const rgb = hexToRgb(hex);
  if (!rgb) return null;
  return [srgbToLinear(rgb[0] / 255), srgbToLinear(rgb[1] / 255), srgbToLinear(rgb[2] / 255)];
}

// ── XYZ D65 ───────────────────────────────────────────────────────────────

function linearRgbToXyz(r: number, g: number, b: number): [number, number, number] {
  return [
    0.4124564 * r + 0.3575761 * g + 0.1804375 * b,
    0.2126729 * r + 0.7151522 * g + 0.0721750 * b,
    0.0193339 * r + 0.1191920 * g + 0.9503041 * b,
  ];
}

// ── CIE Lab ───────────────────────────────────────────────────────────────

const D65 = [0.95047, 1.00000, 1.08883];

function xyzToLab(x: number, y: number, z: number): [number, number, number] {
  const f = (t: number) => t > 0.008856 ? Math.cbrt(t) : 7.787 * t + 16 / 116;
  const fx = f(x / D65[0]);
  const fy = f(y / D65[1]);
  const fz = f(z / D65[2]);
  return [116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz)];
}

// ── CIE LCH ──────────────────────────────────────────────────────────────

function labToLch(L: number, a: number, b: number): [number, number, number] {
  const C = Math.sqrt(a * a + b * b);
  let H = Math.atan2(b, a) * (180 / Math.PI);
  if (H < 0) H += 360;
  return [L, C, H];
}

// ── OKLab ─────────────────────────────────────────────────────────────────

function linearRgbToOklab(r: number, g: number, b: number): [number, number, number] {
  const l = Math.cbrt(0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b);
  const m = Math.cbrt(0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b);
  const s = Math.cbrt(0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b);
  return [
    0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s,
    1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s,
    0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s,
  ];
}

function oklabToLinearRgb(L: number, a: number, b: number): [number, number, number] {
  const l = (L + 0.3963377774 * a + 0.2158037573 * b) ** 3;
  const m = (L - 0.1055613458 * a - 0.0638541728 * b) ** 3;
  const s = (L - 0.0894841775 * a - 1.2914855480 * b) ** 3;
  return [
    4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
    -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
    -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s,
  ];
}

// ── OKLCH ─────────────────────────────────────────────────────────────────

function oklabToOklch(L: number, a: number, b: number): [number, number, number] {
  const C = Math.sqrt(a * a + b * b);
  let H = Math.atan2(b, a) * (180 / Math.PI);
  if (H < 0) H += 360;
  return [L, C, H];
}

function oklchToOklab(L: number, C: number, H: number): [number, number, number] {
  const rad = H * (Math.PI / 180);
  return [L, C * Math.cos(rad), C * Math.sin(rad)];
}

// ── Display P3 ────────────────────────────────────────────────────────────

function xyzToP3Linear(x: number, y: number, z: number): [number, number, number] {
  return [
    2.4934969119 * x - 0.9313836179 * y - 0.4027107845 * z,
    -0.8294889696 * x + 1.7626640603 * y + 0.0236246858 * z,
    0.0358458302 * x - 0.0761723893 * y + 0.9568845240 * z,
  ];
}

// ── Public conversion functions ───────────────────────────────────────────

export function hexToOklch(hex: string): [number, number, number] | null {
  const lin = hexToLinearRgb(hex);
  if (!lin) return null;
  const [L, a, b] = linearRgbToOklab(...lin);
  return oklabToOklch(L, a, b);
}

export function oklchToHex(L: number, C: number, H: number): string {
  const [oL, oa, ob] = oklchToOklab(L, C, H);
  const [r, g, b] = oklabToLinearRgb(oL, oa, ob);
  return rgbToHex(
    Math.round(linearToSrgb(r) * 255),
    Math.round(linearToSrgb(g) * 255),
    Math.round(linearToSrgb(b) * 255)
  );
}

export function hexToOklab(hex: string): [number, number, number] | null {
  const lin = hexToLinearRgb(hex);
  if (!lin) return null;
  return linearRgbToOklab(...lin);
}

export function hexToLab(hex: string): [number, number, number] | null {
  const lin = hexToLinearRgb(hex);
  if (!lin) return null;
  const xyz = linearRgbToXyz(...lin);
  return xyzToLab(...xyz);
}

export function hexToLch(hex: string): [number, number, number] | null {
  const lab = hexToLab(hex);
  if (!lab) return null;
  return labToLch(...lab);
}

export function hexToP3(hex: string): [number, number, number] | null {
  const lin = hexToLinearRgb(hex);
  if (!lin) return null;
  const xyz = linearRgbToXyz(...lin);
  const p3Lin = xyzToP3Linear(...xyz);
  // Apply P3 transfer function (same gamma as sRGB for simplicity)
  return p3Lin.map((c) => linearToSrgb(c)) as [number, number, number];
}

// ── Format a hex color into any CodeFormat ────────────────────────────────

export function formatColor(hex: string, format: CodeFormat): string {
  switch (format) {
    case "hex":
      return hex;

    case "rgb": {
      const rgb = hexToRgb(hex);
      if (!rgb) return hex;
      return `rgb(${rgb[0]}, ${rgb[1]}, ${rgb[2]})`;
    }

    case "hsl": {
      const hsl = hexToHsl(hex);
      if (!hsl) return hex;
      return `hsl(${hsl[0]}, ${hsl[1]}%, ${hsl[2]}%)`;
    }

    case "oklch": {
      const oklch = hexToOklch(hex);
      if (!oklch) return hex;
      return `oklch(${oklch[0].toFixed(3)} ${oklch[1].toFixed(3)} ${oklch[2].toFixed(1)})`;
    }

    case "oklab": {
      const oklab = hexToOklab(hex);
      if (!oklab) return hex;
      return `oklab(${oklab[0].toFixed(3)} ${oklab[1].toFixed(4)} ${oklab[2].toFixed(4)})`;
    }

    case "lab": {
      const lab = hexToLab(hex);
      if (!lab) return hex;
      return `lab(${lab[0].toFixed(1)} ${lab[1].toFixed(1)} ${lab[2].toFixed(1)})`;
    }

    case "lch": {
      const lch = hexToLch(hex);
      if (!lch) return hex;
      return `lch(${lch[0].toFixed(1)} ${lch[1].toFixed(1)} ${lch[2].toFixed(1)})`;
    }

    case "display-p3": {
      const p3 = hexToP3(hex);
      if (!p3) return hex;
      return `color(display-p3 ${p3[0].toFixed(4)} ${p3[1].toFixed(4)} ${p3[2].toFixed(4)})`;
    }

    default:
      return hex;
  }
}

/** Compute all code format representations for a hex color */
export function computeAllRepresentations(hex: string): Partial<Record<CodeFormat, string>> {
  const result: Partial<Record<CodeFormat, string>> = {};
  const formats: CodeFormat[] = ["hex", "rgb", "hsl", "oklch", "oklab", "lab", "lch", "display-p3"];
  for (const fmt of formats) {
    result[fmt] = formatColor(hex, fmt);
  }
  return result;
}
