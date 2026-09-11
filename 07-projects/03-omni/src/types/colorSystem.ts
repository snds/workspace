// ── Radix 12-Step Color System Types ──────────────────────────────────────────

export type RadixStep = 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12;

export const RADIX_STEPS: RadixStep[] = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12];

/** Semantic groupings for Radix's 12-step scale */
export const RADIX_STEP_GROUPS = [
  { label: "Backgrounds", steps: [1, 2] as RadixStep[], description: "App backgrounds" },
  { label: "Interactive components", steps: [3, 4, 5] as RadixStep[], description: "Component backgrounds" },
  { label: "Borders and separators", steps: [6, 7, 8] as RadixStep[], description: "Border colors" },
  { label: "Solid colors", steps: [9, 10] as RadixStep[], description: "Solid backgrounds" },
  { label: "Accessible text", steps: [11, 12] as RadixStep[], description: "Text colors" },
] as const;

/** @deprecated Use RadixStep instead */
export type ColorShade = RadixStep;
/** @deprecated Use RADIX_STEPS instead */
export const COLOR_SHADES = RADIX_STEPS;

// ── Color Spaces & Code Formats ─────────────────────────────────────────────

export type ColorSpace = "srgb" | "display-p3" | "oklch" | "oklab" | "hsl" | "lch" | "lab";
export type CodeFormat = "hex" | "rgb" | "hsl" | "oklch" | "oklab" | "display-p3" | "lch" | "lab";

export const COLOR_SPACES: { value: ColorSpace; label: string; perceptual: boolean }[] = [
  { value: "oklch", label: "OKLCH", perceptual: true },
  { value: "oklab", label: "OKLab", perceptual: true },
  { value: "lch", label: "CIE LCH", perceptual: true },
  { value: "lab", label: "CIE Lab", perceptual: true },
  { value: "srgb", label: "sRGB", perceptual: false },
  { value: "display-p3", label: "Display P3", perceptual: false },
  { value: "hsl", label: "HSL", perceptual: false },
];

export const CODE_FORMATS: { value: CodeFormat; label: string; example: string }[] = [
  { value: "oklch", label: "oklch()", example: "oklch(0.58 0.22 284)" },
  { value: "hex", label: "Hex", example: "#7c6af7" },
  { value: "rgb", label: "rgb()", example: "rgb(124, 106, 247)" },
  { value: "hsl", label: "hsl()", example: "hsl(249, 89%, 69%)" },
  { value: "oklab", label: "oklab()", example: "oklab(0.58 0.07 -0.19)" },
  { value: "display-p3", label: "color(display-p3)", example: "color(display-p3 0.49 0.42 0.97)" },
  { value: "lch", label: "lch()", example: "lch(52 87 294)" },
  { value: "lab", label: "lab()", example: "lab(52 32 -72)" },
];

// ── Color Data ──────────────────────────────────────────────────────────────

export interface ColorShadeData {
  step: RadixStep;
  hex: string;
  hsl: string;
  representations?: Partial<Record<CodeFormat, string>>;
  contrastOnWhite: number;
  contrastOnBlack: number;
  wcagAA: boolean;
  wcagAAA: boolean;
}

export type ColorRole =
  | "brand-primary"
  | "brand-secondary"
  | "brand-accent"
  | "neutral"
  | "semantic-success"
  | "semantic-warning"
  | "semantic-error"
  | "semantic-info";

export interface ColorScaleVariant {
  steps: Partial<Record<RadixStep, ColorShadeData>>;
}

export interface ColorPalette {
  key: string;
  label: string;
  role: ColorRole;
  seedHex: string;
  light: ColorScaleVariant;
  dark: ColorScaleVariant;
  lightA: ColorScaleVariant;
  darkA: ColorScaleVariant;
}

export interface ColorReference {
  paletteKey: string;
  step: RadixStep;
}

// ── Semantic Tokens ─────────────────────────────────────────────────────────

export type SemanticCategory =
  | "background"
  | "foreground"
  | "border"
  | "interactive"
  | "status"
  | "data-visualization";

export interface SemanticToken {
  name: string;
  lightValue: ColorReference;
  darkValue: ColorReference;
  description: string;
  category: SemanticCategory;
}

export interface ColorMode {
  id: string;
  label: string;
  isDefault: boolean;
}

// ── Data Visualization Palette ──────────────────────────────────────────────

export interface DataVizColor {
  index: number;
  hex: string;
  label: string;
  wcagOnWhite: number;
  wcagOnBlack: number;
}

export interface DataVizPalette {
  mode: "auto" | "custom";
  colors: DataVizColor[];
}

// ── Brand Colors ────────────────────────────────────────────────────────────

export interface BrandColors {
  primary: string;
  secondary: string | null;
  accent: string | null;
}

// ── Color System ────────────────────────────────────────────────────────────

export interface ColorSystem {
  id: string;
  name: string;
  version: string;
  createdAt: string;
  updatedAt: string;
  palettes: Record<string, ColorPalette>;
  tokens: SemanticToken[];
  modes: ColorMode[];
  dataViz?: DataVizPalette;
  generationPrompt?: string;
  aiModel?: string;
}

/** Default semantic tokens applied to any generated color system */
export const DEFAULT_SEMANTIC_TOKENS: Omit<
  SemanticToken,
  "lightValue" | "darkValue"
>[] = [
  {
    name: "color.background.default",
    description: "Default page background",
    category: "background",
  },
  {
    name: "color.background.subtle",
    description: "Subtle background for panels and cards",
    category: "background",
  },
  {
    name: "color.foreground.default",
    description: "Default text color",
    category: "foreground",
  },
  {
    name: "color.foreground.subtle",
    description: "Secondary text color",
    category: "foreground",
  },
  {
    name: "color.border.default",
    description: "Default border color",
    category: "border",
  },
  {
    name: "color.interactive.primary",
    description: "Primary button and interactive element fill",
    category: "interactive",
  },
  {
    name: "color.interactive.primary.text",
    description: "Text on primary interactive elements",
    category: "interactive",
  },
  {
    name: "color.status.success",
    description: "Success state fill",
    category: "status",
  },
  {
    name: "color.status.warning",
    description: "Warning state fill",
    category: "status",
  },
  {
    name: "color.status.error",
    description: "Error state fill",
    category: "status",
  },
  {
    name: "color.status.info",
    description: "Info state fill",
    category: "status",
  },
];
