import { DESIGN_SYSTEM_PRESETS, type DesignSystemPreset } from "@/features/tokens/presets";

export interface DesignSystemTemplate {
  id: string;
  name: string;
  tagline: string;
  previewColors: string[];
  category: "popular" | "enterprise" | "minimal";
  features: string[];
  sourcePreset: DesignSystemPreset | null;
}

function fromPreset(
  preset: DesignSystemPreset,
  category: DesignSystemTemplate["category"],
  features: string[],
): DesignSystemTemplate {
  return {
    id: preset.id,
    name: preset.name,
    tagline: preset.tagline,
    previewColors: preset.previewColors,
    category,
    features,
    sourcePreset: preset,
  };
}

const presetMap = Object.fromEntries(DESIGN_SYSTEM_PRESETS.map((p) => [p.id, p]));

export const DESIGN_SYSTEM_TEMPLATES: DesignSystemTemplate[] = [
  fromPreset(presetMap["shadcn"], "popular", ["Zinc neutral", "Violet accent", "Tailwind-ready"]),
  fromPreset(presetMap["radix"], "popular", ["Accessible", "12-step scale", "Dark mode"]),
  fromPreset(presetMap["tailwind"], "popular", ["Utility-first", "Slate neutral", "JIT-ready"]),
  fromPreset(presetMap["material3"], "popular", ["Material You", "Tonal palettes", "Dynamic color"]),
  fromPreset(presetMap["antd"], "enterprise", ["Enterprise blue", "Ant Design 5", "Token system"]),
  fromPreset(presetMap["bootstrap"], "popular", ["Classic web", "Blue primary", "Gray neutral"]),

  // Templates without full preset data yet
  {
    id: "untitled-ui",
    name: "Untitled UI",
    tagline: "Modern SaaS design system with clean, minimal aesthetics",
    previewColors: ["#7F56D9", "#9E77ED", "#667085"],
    category: "popular",
    features: ["SaaS-ready", "Clean neutral", "Figma-native"],
    sourcePreset: null,
  },
  {
    id: "carbon",
    name: "IBM Carbon",
    tagline: "IBM's open-source design system for digital products",
    previewColors: ["#0f62fe", "#4589ff", "#6f6f6f"],
    category: "enterprise",
    features: ["Accessibility-first", "Enterprise", "Data-dense"],
    sourcePreset: null,
  },
  {
    id: "lightning",
    name: "Salesforce Lightning",
    tagline: "Enterprise design system for the Salesforce ecosystem",
    previewColors: ["#0176d3", "#57a3e8", "#706e6b"],
    category: "enterprise",
    features: ["CRM-focused", "Enterprise", "Mobile-ready"],
    sourcePreset: null,
  },
  {
    id: "atlassian",
    name: "Atlassian Design",
    tagline: "Atlassian's design system for team collaboration tools",
    previewColors: ["#0052CC", "#4C9AFF", "#6B778C"],
    category: "enterprise",
    features: ["Collaboration", "Enterprise", "Dark mode"],
    sourcePreset: null,
  },
];
