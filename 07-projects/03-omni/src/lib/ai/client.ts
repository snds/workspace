import { platform } from "@/platform";
import {
  FRAMEWORK_ADVISOR_SYSTEM_PROMPT,
  TEAM_CONTEXT_ADVISOR_SYSTEM_PROMPT,
  COLOR_SYSTEM_GENERATION_PROMPT,
} from "./prompts";
import type { ChatMessage, TechStackRecommendation } from "@/types/onboarding";
import type { ColorSystem, ColorPalette, ColorShadeData, ColorScaleVariant, RadixStep, DataVizPalette, DataVizColor } from "@/types/colorSystem";
import { RADIX_STEPS } from "@/types/colorSystem";
import { enrichColorSystem, deriveAlphaVariant, contrastRatio } from "@/lib/color";

// ── Framework Advisor ──────────────────────────────────────────────────────

/**
 * Streams a framework advisor response.
 * Calls onChunk with each text delta as it arrives.
 */
export async function streamFrameworkAdvice(
  history: ChatMessage[],
  onChunk: (delta: string) => void
): Promise<void> {
  const messages = history.map((m) => ({ role: m.role, content: m.content }));

  for await (const chunk of platform.ai.streamMessage({
    systemPrompt: FRAMEWORK_ADVISOR_SYSTEM_PROMPT,
    messages,
    maxTokens: 1024,
  })) {
    onChunk(chunk);
  }
}

/**
 * Parses the recommendation JSON block from an AI response.
 * Returns null if no recommendation block is found.
 */
export function parseRecommendation(
  rawContent: string
): TechStackRecommendation | null {
  const match = rawContent.match(/```recommendation\n([\s\S]*?)\n```/);
  if (!match) return null;
  try {
    const parsed = JSON.parse(match[1]) as Omit<
      TechStackRecommendation,
      "confirmed"
    >;
    return { ...parsed, confirmed: false };
  } catch {
    return null;
  }
}

// ── Team Context Advisor ──────────────────────────────────────────────────

/**
 * Parsed team context recommendation from AI response.
 */
export interface TeamContextRecommendation {
  presetId: string;
  tier: number;
  framework: string;
  styling: string;
  componentLibrary: string;
  additionalNotes?: string;
  confirmed: boolean;
}

/**
 * Streams a team context advisor response.
 * Calls onChunk with each text delta as it arrives.
 */
export async function streamTeamContextAdvice(
  history: ChatMessage[],
  onChunk: (delta: string) => void,
): Promise<void> {
  const messages = history.map((m) => ({ role: m.role, content: m.content }));

  for await (const chunk of platform.ai.streamMessage({
    systemPrompt: TEAM_CONTEXT_ADVISOR_SYSTEM_PROMPT,
    messages,
    maxTokens: 1024,
  })) {
    onChunk(chunk);
  }
}

/**
 * Parses the team-context JSON block from an AI response.
 * Returns null if no team-context block is found.
 */
export function parseTeamContextRecommendation(
  rawContent: string,
): TeamContextRecommendation | null {
  const match = rawContent.match(/```team-context\n([\s\S]*?)\n```/);
  if (!match) return null;
  try {
    const parsed = JSON.parse(match[1]) as Omit<
      TeamContextRecommendation,
      "confirmed"
    >;
    return { ...parsed, confirmed: false };
  } catch {
    return null;
  }
}

// ── Color System Generator ─────────────────────────────────────────────────

interface SeedColors {
  primary: string;
  secondary?: string | null;
  accent?: string | null;
}

/**
 * Generates a complete Radix-style ColorSystem from seed hex colors using Claude.
 * Streams the response, parses light/dark variants, computes alpha variants.
 * Returns null on parse failure.
 */
export async function generateColorSystem(
  seeds: SeedColors,
  onProgress?: (partial: string) => void
): Promise<ColorSystem | null> {
  const userMessage = [
    `Generate a complete Radix Colors-style color system for the following seed colors:`,
    `Primary: ${seeds.primary}`,
    seeds.secondary ? `Secondary: ${seeds.secondary}` : null,
    seeds.accent ? `Accent: ${seeds.accent}` : null,
  ]
    .filter(Boolean)
    .join("\n");

  let fullResponse = "";

  for await (const chunk of platform.ai.streamMessage({
    systemPrompt: COLOR_SYSTEM_GENERATION_PROMPT,
    messages: [{ role: "user", content: userMessage }],
    maxTokens: 16384,
  })) {
    fullResponse += chunk;
    onProgress?.(fullResponse);
  }

  // Extract JSON robustly — AI may wrap in code fences or add surrounding text
  let json = fullResponse.trim();

  const fenceMatch = json.match(/```(?:json)?\s*\n([\s\S]*?)\n\s*```/);
  if (fenceMatch) {
    json = fenceMatch[1].trim();
  }

  if (!json.startsWith("{")) {
    const start = json.indexOf("{");
    const end = json.lastIndexOf("}");
    if (start !== -1 && end !== -1 && end > start) {
      json = json.slice(start, end + 1);
    }
  }

  try {
    const raw = JSON.parse(json) as RawResponse;
    return buildColorSystem(raw, seeds);
  } catch {
    console.error("[ColorSystem] Failed to parse JSON:", json.slice(0, 300));
    return null;
  }
}

// ── Internal helpers ───────────────────────────────────────────────────────

interface RawShade {
  hex: string;
  hsl: string;
}

interface RawPalette {
  key: string;
  label: string;
  role: ColorPalette["role"];
  seedHex: string;
  light: Record<string, RawShade>;
  dark: Record<string, RawShade>;
}

interface RawDataVizColor {
  hex: string;
  label: string;
}

interface RawResponse {
  palettes: Record<string, RawPalette>;
  dataViz?: RawDataVizColor[];
}

function buildScaleVariant(rawScale: Record<string, RawShade>): ColorScaleVariant {
  const steps: Partial<Record<RadixStep, ColorShadeData>> = {};
  for (const step of RADIX_STEPS) {
    const raw = rawScale[String(step)];
    if (!raw) continue;
    const contrasts = enrichColorSystem(raw.hex);
    steps[step] = {
      step,
      hex: raw.hex,
      hsl: raw.hsl,
      contrastOnWhite: contrasts.onWhite,
      contrastOnBlack: contrasts.onBlack,
      wcagAA: contrasts.onWhite >= 4.5 || contrasts.onBlack >= 4.5,
      wcagAAA: contrasts.onWhite >= 7 || contrasts.onBlack >= 7,
    };
  }
  return { steps };
}

function buildAlphaVariant(
  opaqueVariant: ColorScaleVariant,
  backgroundHex: string
): ColorScaleVariant {
  const steps: Partial<Record<RadixStep, ColorShadeData>> = {};
  for (const step of RADIX_STEPS) {
    const opaque = opaqueVariant.steps[step];
    if (!opaque) continue;
    const alphaStr = deriveAlphaVariant(opaque.hex, backgroundHex);
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

function buildDataVizPalette(raw: RawDataVizColor[]): DataVizPalette {
  const colors: DataVizColor[] = raw.map((c, i) => ({
    index: i + 1,
    hex: c.hex,
    label: c.label || `Series ${i + 1}`,
    wcagOnWhite: parseFloat(contrastRatio(c.hex, "#ffffff").toFixed(2)),
    wcagOnBlack: parseFloat(contrastRatio(c.hex, "#000000").toFixed(2)),
  }));
  return { mode: "auto", colors };
}

function buildColorSystem(
  raw: RawResponse,
  seeds: SeedColors
): ColorSystem {
  const palettes: Record<string, ColorPalette> = {};

  for (const [key, rawPalette] of Object.entries(raw.palettes)) {
    const light = buildScaleVariant(rawPalette.light ?? {});
    const dark = buildScaleVariant(rawPalette.dark ?? {});
    const lightA = buildAlphaVariant(light, "#ffffff");
    const darkA = buildAlphaVariant(dark, "#111113");

    palettes[key] = {
      key: rawPalette.key ?? key,
      label: rawPalette.label ?? key,
      role: rawPalette.role ?? "brand-primary",
      seedHex: rawPalette.seedHex ?? seeds.primary,
      light,
      dark,
      lightA,
      darkA,
    };
  }

  const dataViz = raw.dataViz?.length
    ? buildDataVizPalette(raw.dataViz)
    : undefined;

  const now = new Date().toISOString();
  return {
    id: `cs_${Date.now()}`,
    name: "My Design System",
    version: "1.0.0",
    createdAt: now,
    updatedAt: now,
    palettes,
    tokens: [],
    modes: [
      { id: "light", label: "Light", isDefault: true },
      { id: "dark", label: "Dark", isDefault: false },
    ],
    dataViz,
    aiModel: "claude-opus-4-6",
  };
}
