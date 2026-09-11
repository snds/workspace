import { nanoid } from "nanoid";
import type {
  ColorRole,
  RadixStep,
  ColorShadeData,
  ColorScaleVariant,
  ColorSystem,
} from "@/types/colorSystem";
import { RADIX_STEPS, DEFAULT_SEMANTIC_TOKENS } from "@/types/colorSystem";
import { enrichColorSystem, deriveAlphaVariant } from "@/lib/color";

// ─── Preset types ──────────────────────────────────────────────────────────────

interface PresetPalette {
  key: string;
  label: string;
  role: ColorRole;
  seedHex: string;
  light: Partial<Record<RadixStep, string>>;
  dark: Partial<Record<RadixStep, string>>;
}

export interface DesignSystemPreset {
  id: string;
  name: string;
  tagline: string;
  previewColors: string[]; // 3 hex swatches shown on the card
  palettes: PresetPalette[];
}

// ─── Helpers ───────────────────────────────────────────────────────────────────

function makeStep(hex: string, step: RadixStep): ColorShadeData {
  const contrasts = enrichColorSystem(hex);
  return {
    step,
    hex,
    hsl: hex,
    contrastOnWhite: contrasts.onWhite,
    contrastOnBlack: contrasts.onBlack,
    wcagAA: contrasts.onWhite >= 4.5 || contrasts.onBlack >= 4.5,
    wcagAAA: contrasts.onWhite >= 7 || contrasts.onBlack >= 7,
  };
}

function buildVariant(scale: Partial<Record<RadixStep, string>>): ColorScaleVariant {
  const steps: Partial<Record<RadixStep, ColorShadeData>> = {};
  for (const step of RADIX_STEPS) {
    const hex = scale[step];
    if (hex) steps[step] = makeStep(hex, step);
  }
  return { steps };
}

function buildAlpha(opaque: ColorScaleVariant, bgHex: string): ColorScaleVariant {
  const steps: Partial<Record<RadixStep, ColorShadeData>> = {};
  for (const step of RADIX_STEPS) {
    const src = opaque.steps[step];
    if (!src) continue;
    const alphaStr = deriveAlphaVariant(src.hex, bgHex);
    steps[step] = {
      step,
      hex: alphaStr,
      hsl: alphaStr,
      contrastOnWhite: 0,
      contrastOnBlack: 0,
      wcagAA: false,
      wcagAAA: false,
    };
  }
  return { steps };
}

// ─── Preset definitions ────────────────────────────────────────────────────────

export const DESIGN_SYSTEM_PRESETS: DesignSystemPreset[] = [
  {
    id: "shadcn",
    name: "shadcn/ui",
    tagline: "Zinc neutral + Violet accent — the default shadcn palette",
    previewColors: ["#8b5cf6", "#a78bfa", "#71717a"],
    palettes: [
      {
        key: "primary",
        label: "Violet",
        role: "brand-primary",
        seedHex: "#8b5cf6",
        light: {
          1: "#fdfcfe", 2: "#faf8ff", 3: "#f5f3ff", 4: "#ede9fe",
          5: "#ddd6fe", 6: "#c4b5fd", 7: "#a78bfa", 8: "#8b5cf6",
          9: "#8b5cf6", 10: "#7c3aed", 11: "#6d28d9", 12: "#2e1065",
        },
        dark: {
          1: "#14121f", 2: "#1b1525", 3: "#291f43", 4: "#33255b",
          5: "#3c2e69", 6: "#473876", 7: "#56468b", 8: "#6958ad",
          9: "#8b5cf6", 10: "#a78bfa", 11: "#c4b5fd", 12: "#ede9fe",
        },
      },
      {
        key: "neutral",
        label: "Zinc",
        role: "neutral",
        seedHex: "#71717a",
        light: {
          1: "#fafafa", 2: "#f4f4f5", 3: "#e4e4e7", 4: "#d4d4d8",
          5: "#c4c4c9", 6: "#b4b4ba", 7: "#a1a1aa", 8: "#71717a",
          9: "#71717a", 10: "#52525b", 11: "#3f3f46", 12: "#09090b",
        },
        dark: {
          1: "#09090b", 2: "#18181b", 3: "#27272a", 4: "#303033",
          5: "#3f3f46", 6: "#4a4a52", 7: "#52525b", 8: "#71717a",
          9: "#71717a", 10: "#a1a1aa", 11: "#d4d4d8", 12: "#fafafa",
        },
      },
    ],
  },
  {
    id: "radix",
    name: "Radix Themes",
    tagline: "Violet + Mauve — Radix UI's default accessible color scales",
    previewColors: ["#6e56cf", "#9e8cfc", "#8b8792"],
    palettes: [
      {
        key: "primary",
        label: "Violet",
        role: "brand-primary",
        seedHex: "#6e56cf",
        light: {
          1: "#fdfcfe", 2: "#faf8ff", 3: "#f4f0fe", 4: "#ebe4ff",
          5: "#e1d9ff", 6: "#d4cafe", 7: "#c2b5f5", 8: "#aa99ec",
          9: "#6e56cf", 10: "#654dc4", 11: "#6550b9", 12: "#2f265f",
        },
        dark: {
          1: "#14121f", 2: "#1b1525", 3: "#291f43", 4: "#33255b",
          5: "#3c2e69", 6: "#473876", 7: "#56468b", 8: "#6958ad",
          9: "#6e56cf", 10: "#7d66f0", 11: "#baa7ff", 12: "#e2ddfe",
        },
      },
      {
        key: "neutral",
        label: "Mauve",
        role: "neutral",
        seedHex: "#8b8792",
        light: {
          1: "#fdfcfd", 2: "#faf9fb", 3: "#f2eff3", 4: "#eae7ec",
          5: "#e3dfe6", 6: "#ddd8e0", 7: "#c8c4cc", 8: "#b9b5bd",
          9: "#8b8792", 10: "#807c87", 11: "#736f7a", 12: "#2b2533",
        },
        dark: {
          1: "#121113", 2: "#1a191b", 3: "#232225", 4: "#2b292d",
          5: "#323035", 6: "#3c393f", 7: "#49474e", 8: "#625f69",
          9: "#8b8792", 10: "#9f9ba6", 11: "#c5c2cb", 12: "#eeedf0",
        },
      },
    ],
  },
  {
    id: "tailwind",
    name: "Tailwind CSS",
    tagline: "Blue + Slate — Tailwind's default utility-first palette",
    previewColors: ["#3b82f6", "#93c5fd", "#64748b"],
    palettes: [
      {
        key: "primary",
        label: "Blue",
        role: "brand-primary",
        seedHex: "#3b82f6",
        light: {
          1: "#fafcff", 2: "#eff6ff", 3: "#dbeafe", 4: "#bfdbfe",
          5: "#93c5fd", 6: "#60a5fa", 7: "#3b82f6", 8: "#2563eb",
          9: "#3b82f6", 10: "#2563eb", 11: "#1d4ed8", 12: "#172554",
        },
        dark: {
          1: "#0b1120", 2: "#0f1729", 3: "#152244", 4: "#1a2e5a",
          5: "#1e3a6e", 6: "#244a85", 7: "#2d5fa3", 8: "#3978cc",
          9: "#3b82f6", 10: "#60a5fa", 11: "#93c5fd", 12: "#eff6ff",
        },
      },
      {
        key: "neutral",
        label: "Slate",
        role: "neutral",
        seedHex: "#64748b",
        light: {
          1: "#f8fafc", 2: "#f1f5f9", 3: "#e2e8f0", 4: "#cbd5e1",
          5: "#b0bac8", 6: "#94a3b8", 7: "#64748b", 8: "#475569",
          9: "#64748b", 10: "#475569", 11: "#334155", 12: "#020617",
        },
        dark: {
          1: "#020617", 2: "#0f172a", 3: "#1e293b", 4: "#273548",
          5: "#334155", 6: "#3e4d63", 7: "#475569", 8: "#64748b",
          9: "#64748b", 10: "#94a3b8", 11: "#cbd5e1", 12: "#f8fafc",
        },
      },
    ],
  },
  {
    id: "antd",
    name: "Ant Design",
    tagline: "Enterprise Blue — Ant Design 5's canonical color system",
    previewColors: ["#1677ff", "#69b1ff", "#595959"],
    palettes: [
      {
        key: "primary",
        label: "Blue",
        role: "brand-primary",
        seedHex: "#1677ff",
        light: {
          1: "#f0f7ff", 2: "#e6f4ff", 3: "#bae0ff", 4: "#91caff",
          5: "#69b1ff", 6: "#4096ff", 7: "#1677ff", 8: "#0958d9",
          9: "#1677ff", 10: "#0958d9", 11: "#003eb3", 12: "#000d33",
        },
        dark: {
          1: "#060e1a", 2: "#0a1628", 3: "#0f2240", 4: "#142f5a",
          5: "#1a3c74", 6: "#204f95", 7: "#2868b8", 8: "#3580dc",
          9: "#1677ff", 10: "#4096ff", 11: "#69b1ff", 12: "#e6f4ff",
        },
      },
      {
        key: "neutral",
        label: "Gray",
        role: "neutral",
        seedHex: "#595959",
        light: {
          1: "#ffffff", 2: "#fafafa", 3: "#f5f5f5", 4: "#f0f0f0",
          5: "#d9d9d9", 6: "#bfbfbf", 7: "#8c8c8c", 8: "#595959",
          9: "#595959", 10: "#434343", 11: "#262626", 12: "#141414",
        },
        dark: {
          1: "#0a0a0a", 2: "#141414", 3: "#1f1f1f", 4: "#2a2a2a",
          5: "#353535", 6: "#434343", 7: "#595959", 8: "#8c8c8c",
          9: "#595959", 10: "#8c8c8c", 11: "#bfbfbf", 12: "#fafafa",
        },
      },
    ],
  },
  {
    id: "material3",
    name: "Material Design 3",
    tagline: "Material You — Google's dynamic, accessible tonal system",
    previewColors: ["#6750A4", "#b69df8", "#79747e"],
    palettes: [
      {
        key: "primary",
        label: "Purple",
        role: "brand-primary",
        seedHex: "#6750A4",
        light: {
          1: "#fffbfe", 2: "#f6edff", 3: "#e8def8", 4: "#d0bcff",
          5: "#b69df8", 6: "#9a82db", 7: "#7f67be", 8: "#6750a4",
          9: "#6750a4", 10: "#4f378b", 11: "#381e72", 12: "#12003a",
        },
        dark: {
          1: "#0e0b14", 2: "#1d1a25", 3: "#2d2640", 4: "#3a3058",
          5: "#483d6e", 6: "#574c85", 7: "#675e99", 8: "#7a71b0",
          9: "#6750a4", 10: "#9a82db", 11: "#d0bcff", 12: "#f6edff",
        },
      },
      {
        key: "neutral",
        label: "Neutral",
        role: "neutral",
        seedHex: "#79747e",
        light: {
          1: "#fffbfe", 2: "#f7f2fa", 3: "#e6e1e5", 4: "#d5d0d5",
          5: "#cac4d0", 6: "#aeaaae", 7: "#938f99", 8: "#79747e",
          9: "#79747e", 10: "#605d67", 11: "#49454e", 12: "#0f0e12",
        },
        dark: {
          1: "#0f0e12", 2: "#1c1b1f", 3: "#2a282e", 4: "#36343a",
          5: "#49454e", 6: "#565259", 7: "#605d67", 8: "#79747e",
          9: "#79747e", 10: "#938f99", 11: "#cac4d0", 12: "#f7f2fa",
        },
      },
    ],
  },
  {
    id: "bootstrap",
    name: "Bootstrap 5",
    tagline: "Classic Blue — Bootstrap's familiar web-native palette",
    previewColors: ["#0d6efd", "#6ea8fe", "#6c757d"],
    palettes: [
      {
        key: "primary",
        label: "Blue",
        role: "brand-primary",
        seedHex: "#0d6efd",
        light: {
          1: "#f0f5ff", 2: "#e7f1ff", 3: "#cfe2ff", 4: "#9ec5fe",
          5: "#6ea8fe", 6: "#3d8bfd", 7: "#0d6efd", 8: "#0a58ca",
          9: "#0d6efd", 10: "#0a58ca", 11: "#084298", 12: "#010b1a",
        },
        dark: {
          1: "#050d1a", 2: "#0a1628", 3: "#0f2340", 4: "#14305a",
          5: "#1a3e74", 6: "#204f95", 7: "#2a63b8", 8: "#357bde",
          9: "#0d6efd", 10: "#3d8bfd", 11: "#6ea8fe", 12: "#e7f1ff",
        },
      },
      {
        key: "neutral",
        label: "Gray",
        role: "neutral",
        seedHex: "#6c757d",
        light: {
          1: "#f8f9fa", 2: "#e9ecef", 3: "#dee2e6", 4: "#ced4da",
          5: "#bcc3ca", 6: "#adb5bd", 7: "#6c757d", 8: "#495057",
          9: "#6c757d", 10: "#495057", 11: "#343a40", 12: "#0a0d0f",
        },
        dark: {
          1: "#0a0d0f", 2: "#161b21", 3: "#212529", 4: "#2a3036",
          5: "#343a40", 6: "#42484f", 7: "#495057", 8: "#6c757d",
          9: "#6c757d", 10: "#adb5bd", 11: "#ced4da", 12: "#f8f9fa",
        },
      },
    ],
  },
];

// ─── Convert preset → ColorSystem ─────────────────────────────────────────────

export function makeColorSystem(preset: DesignSystemPreset): ColorSystem {
  const now = new Date().toISOString();

  const palettes: ColorSystem["palettes"] = {};
  for (const p of preset.palettes) {
    const light = buildVariant(p.light);
    const dark = buildVariant(p.dark);
    const lightA = buildAlpha(light, "#ffffff");
    const darkA = buildAlpha(dark, "#111113");

    palettes[p.key] = {
      key: p.key,
      label: p.label,
      role: p.role,
      seedHex: p.seedHex,
      light,
      dark,
      lightA,
      darkA,
    };
  }

  // Wire semantic tokens to primary + neutral palettes
  const primaryKey =
    preset.palettes.find((p) => p.role.startsWith("brand-primary"))?.key ?? "primary";
  const neutralKey =
    preset.palettes.find((p) => p.role === "neutral")?.key ?? "neutral";

  const tokens: ColorSystem["tokens"] = DEFAULT_SEMANTIC_TOKENS.map((stub) => {
    let lightRef = { paletteKey: neutralKey, step: 2 as RadixStep };
    let darkRef = { paletteKey: neutralKey, step: 11 as RadixStep };

    if (stub.category === "background") {
      lightRef = { paletteKey: neutralKey, step: 1 };
      darkRef = { paletteKey: neutralKey, step: 1 };
    } else if (stub.category === "foreground") {
      lightRef = { paletteKey: neutralKey, step: 12 };
      darkRef = { paletteKey: neutralKey, step: 12 };
    } else if (stub.category === "border") {
      lightRef = { paletteKey: neutralKey, step: 7 };
      darkRef = { paletteKey: neutralKey, step: 7 };
    } else if (stub.category === "interactive") {
      lightRef = { paletteKey: primaryKey, step: 9 };
      darkRef = { paletteKey: primaryKey, step: 9 };
    } else if (stub.category === "status") {
      lightRef = { paletteKey: primaryKey, step: 9 };
      darkRef = { paletteKey: primaryKey, step: 9 };
    }

    return { ...stub, lightValue: lightRef, darkValue: darkRef };
  });

  return {
    id: nanoid(),
    name: preset.name,
    version: "1.0.0",
    createdAt: now,
    updatedAt: now,
    palettes,
    tokens,
    modes: [
      { id: "light", label: "Light", isDefault: true },
      { id: "dark", label: "Dark", isDefault: false },
    ],
  };
}
